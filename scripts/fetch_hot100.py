"""从力扣中国站拉取官方 Hot100 题单（题号/标题/难度/标签/完整题面），写入 data/hot100.json。

用法:
  python scripts/fetch_hot100.py                      # 写入 ./hot100/data/
  python scripts/fetch_hot100.py --workspace ./hot100
  python scripts/fetch_hot100.py --proxy http://127.0.0.1:7890
  python scripts/fetch_hot100.py --skip-content       # 只拉题单不拉题面（快）

说明:
  - 走 leetcode.cn 公开 GraphQL 接口，无需登录。
  - 默认拉取每题的完整中文题面（含示例/约束，HTML 格式），供出题展示和 Anki 卡片使用；
    题面较大且逐题请求，约需 1-2 分钟。--skip-content 可跳过。
  - 默认遵循系统环境变量代理；也可 --proxy 显式指定。
"""

import argparse
import json
import os
import time
import urllib.request

LIST_QUERY = '''query favoriteQuestionList($favoriteSlug: String!, $filter: FavoriteQuestionFilterInput, $limit: Int, $skip: Int, $version: String) {
  favoriteQuestionList(favoriteSlug: $favoriteSlug, filter: $filter, limit: $limit, skip: $skip, version: $version) {
    totalLength
    questions { questionFrontendId titleSlug title translatedTitle difficulty topicTags { slug nameTranslated } }
  }
}'''

CONTENT_QUERY = '''query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) { questionFrontendId translatedContent }
}'''


def build_opener(proxy=None):
    if proxy:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener()  # 默认尊重 HTTP_PROXY/HTTPS_PROXY 环境变量


def post_graphql(opener, query, variables, referer):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://leetcode.cn/graphql/", data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Origin": "https://leetcode.cn",
        })
    with opener.open(req, timeout=60) as r:
        return json.load(r)


def fetch_list(opener):
    all_q, skip = [], 0
    while True:
        d = post_graphql(
            opener, LIST_QUERY,
            {"favoriteSlug": "2cktkvj", "filter": {}, "limit": 100, "skip": skip, "version": None},
            "https://leetcode.cn/problem-list/2cktkvj/")
        lst = d["data"]["favoriteQuestionList"]
        total, qs = lst["totalLength"], lst["questions"]
        all_q.extend(qs)
        skip += len(qs)
        print(f"题单 {len(all_q)}/{total}")
        if skip >= total or not qs:
            break
    return all_q


def fetch_contents(opener, problems):
    """逐题拉取中文题面（HTML），失败留空、可断点续传。"""
    ok = 0
    for i, q in enumerate(problems, 1):
        slug = q["titleSlug"]
        if q.get("contentHtml"):
            ok += 1
            continue
        try:
            d = post_graphql(opener, CONTENT_QUERY, {"titleSlug": slug},
                             f"https://leetcode.cn/problems/{slug}/")
            q["contentHtml"] = (d["data"]["question"] or {}).get("translatedContent") or ""
            ok += 1
        except Exception as e:
            q["contentHtml"] = ""
            print(f"  [warn] {slug} 题面拉取失败: {e}")
        if i % 20 == 0 or i == len(problems):
            print(f"题面 {i}/{len(problems)}")
        time.sleep(0.15)  # 轻微限速，避免触发风控
    print(f"题面完成 {ok}/{len(problems)}")


def main():
    import _workspace

    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--skip-content", action="store_true", help="不拉题面，只拉题单")
    args = ap.parse_args()

    ws = _workspace.resolve(args.workspace)
    opener = build_opener(args.proxy)

    all_q = fetch_list(opener)

    # 若已有缓存，优先复用已有题面
    cache_path = os.path.join(ws, "data", "hot100.json")
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cache = {q["titleSlug"]: q.get("contentHtml") for q in json.load(f)}
        for q in all_q:
            if cache.get(q["titleSlug"]):
                q["contentHtml"] = cache[q["titleSlug"]]

    if not args.skip_content:
        fetch_contents(opener, all_q)

    os.makedirs(os.path.join(ws, "data"), exist_ok=True)
    out = os.path.join(ws, "data", "hot100.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)

    slugs = [q["titleSlug"] for q in all_q]
    with open(os.path.join(ws, "data", "hot100_slugs.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(slugs))

    with_content = sum(1 for q in all_q if q.get("contentHtml"))
    print(f"题单: {len(all_q)} 题（含题面 {with_content}）-> {out}")


if __name__ == "__main__":
    main()
