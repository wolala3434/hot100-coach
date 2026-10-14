"""把「已练过」的题生成 Anki 卡组（.apkg，双击导入 Anki）。

卡片设计（间隔重复友好，复习 = 从零重写）:
  正面：题号 + 标题 + 难度 + 标签 + 原题链接
  背面：你的笔记 + 代码随想录/labuladong 本地参考 + 复习标准

用法:
  python scripts/make_anki.py                 # 导出所有 done/review 题
  python scripts/make_anki.py --all           # 导出全部 100 题
  python scripts/make_anki.py --ids 1 15 42   # 只导出指定题号
  python scripts/make_anki.py -o my.apkg      # 指定输出文件
"""

import argparse
import glob
import json
import os
import re
import sys

import _workspace

try:
    import genanki
except ImportError:
    sys.exit("缺少依赖，请先运行: python -m pip install genanki")

DECK_ID = 2026101301
MODEL_ID = 2026101303  # v2：正面带完整题面

MODEL = genanki.Model(
    MODEL_ID,
    "LeetCode Hot100 v2",
    fields=[{"name": "Front"}, {"name": "Desc"}, {"name": "Back"}, {"name": "Topic"},
            {"name": "Difficulty"}, {"name": "Slug"}],
    templates=[{
        "name": "刷题复习卡",
        "qfmt": """
<div class="lc-card">
  <div class="lc-topic">{{Topic}} · {{Difficulty}}</div>
  <div class="lc-title">{{Front}}</div>
  <div class="lc-desc">{{Desc}}</div>
  <div class="lc-hint">先自己重写一遍：写出核心思路 → 关键边界 → 复杂度，再翻面。</div>
</div>
""",
        "afmt": """
<div class="lc-card">
  <div class="lc-topic">{{Topic}} · {{Difficulty}}</div>
  <div class="lc-title">{{Front}}</div>
  <div class="lc-desc">{{Desc}}</div>
  <hr>
  <div class="lc-back">{{Back}}</div>
</div>
""",
    }],
    css="""
.lc-card { font-family: -apple-system, "Segoe UI", Roboto, "PingFang SC", sans-serif;
  font-size: 18px; line-height: 1.7; color: #1f2328; max-width: 720px; }
.lc-topic { font-size: 13px; color: #6b7280; letter-spacing: .5px; margin-bottom: 6px; }
.lc-title { font-size: 22px; font-weight: 600; margin: 8px 0 12px; }
.lc-desc { font-size: 15px; color: #374151; background: #f9fafb; border-radius: 8px;
  padding: 10px 14px; margin: 8px 0; }
.lc-desc pre { white-space: pre-wrap; margin: 8px 0; font-size: 13px; background: #f3f4f6;
  padding: 8px; border-radius: 6px; }
.lc-desc code { background: #eef0f2; padding: 1px 5px; border-radius: 4px; font-size: 13px; }
.lc-desc img { max-width: 100%; }
.lc-hint { font-size: 14px; color: #9ca3af; font-style: italic; margin-top: 14px;
  border-left: 3px solid #e5e7eb; padding-left: 10px; }
.lc-back { font-size: 16px; }
.lc-back code { background: #f6f8fa; padding: 1px 5px; border-radius: 4px; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 14px 0; }
.neutral { color: #9ca3af; }
""",
)


def clean_html(html):
    """清洗力扣题面 HTML：去脚本/样式，压空白，适配 Anki。"""
    if not html:
        return ""
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    html = html.replace("&nbsp;", " ")
    # 题面约束文本里的裸 <（如 "<= nums.length"、"< people.length"）不是标签，
    # genanki 会警告 invalid HTML tags，转义为 &lt; 避免污染/丢失
    html = re.sub(r"<(?![a-zA-Z/!])", "&lt;", html)
    return html.strip()


def build_cs_index(ws):
    idx = {}
    cs_md = os.path.join(ws, "vendor", "leetcode-master", "problems")
    if os.path.isdir(cs_md):
        for p in glob.glob(os.path.join(cs_md, "*.md")):
            m = re.match(r"^(\d+)\.", os.path.basename(p))
            if m:
                idx[int(m.group(1))] = os.path.basename(p)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="导出全部 100 题")
    ap.add_argument("--ids", nargs="*", type=int, help="只导出指定题号")
    ap.add_argument("-o", "--output", default=None, help="输出 .apkg 路径")
    ap.add_argument("--workspace", default=None, help="工作区路径")
    args = ap.parse_args()

    ws = _workspace.resolve(args.workspace)

    with open(os.path.join(ws, "data", "hot100.json"), encoding="utf-8") as f:
        problems = json.load(f)
    cs_index = build_cs_index(ws)
    labu_root = os.path.join(ws, "vendor", "labuladong-algo")
    labu_dirs = [os.path.join(labu_root, d) for d in
                 ("算法思维系列", "数据结构系列", "动态规划系列", "高频面试系列")
                 if os.path.isdir(os.path.join(labu_root, d))]

    prog_path = os.path.join(ws, "progress.json")
    prog = {"problems": {}}
    if os.path.exists(prog_path):
        with open(prog_path, encoding="utf-8") as f:
            prog = json.load(f)

    selected = []
    for p in problems:
        qid = int(p["questionFrontendId"])
        if args.ids:
            if qid in args.ids:
                selected.append(p)
        elif args.all:
            selected.append(p)
        else:
            st = prog.get("problems", {}).get(str(qid), {}).get("status", "todo")
            if st in ("done", "review"):
                selected.append(p)

    if not selected:
        print("没有可导出的题目。用 --all 导出全量，或先用 track.py 把题目标为 done。")
        return

    diff_cn = {"EASY": "简单", "MEDIUM": "中等", "HARD": "困难"}
    deck = genanki.Deck(DECK_ID, "LeetCode Hot100")
    for p in selected:
        qid = int(p["questionFrontendId"])
        title = p["translatedTitle"]
        diff = diff_cn.get(p["difficulty"], p["difficulty"])
        tags_cn = "、".join(t.get("nameTranslated", t["slug"]) for t in p.get("topicTags", []))
        slug = p["titleSlug"]
        rec = prog.get("problems", {}).get(str(qid), {})
        topic = rec.get("topic", "")
        user_note = (rec.get("notes") or "").strip()

        front = f"{qid}. {title}"
        desc = clean_html(p.get("contentHtml", ""))
        if not desc:
            desc = ('<div class="neutral">题面未缓存——'
                    f'<a href="https://leetcode.cn/problems/{slug}/">点这里看原题</a>，'
                    '或运行 fetch_hot100.py 补齐题面。</div>')
        back = [
            f'<div class="neutral">标签：{tags_cn}</div>',
            f'<div class="neutral">题目：<a href="https://leetcode.cn/problems/{slug}/">leetcode.cn/problems/{slug}</a></div>',
        ]
        if user_note:
            back.append(f"<div><b>我的解法/易错点：</b><br>{user_note}</div>")
        else:
            back.append('<div class="neutral">（翻面后补充「核心思路 / 边界 / 复杂度」三行，下次复习更有效）</div>')
        if qid in cs_index:
            back.append(f'<div>参考（代码随想录）：<code>vendor/leetcode-master/problems/{cs_index[qid]}</code></div>')
        if labu_dirs:
            back.append('<div>思维模板（labuladong）：' +
                        "、".join(f"<code>{os.path.basename(d)}</code>" for d in labu_dirs) + "</div>")
        back.append('<div class="lc-hint">复习标准：能不看题解、15 分钟内独立写出正确且复杂度达标的解法，才算过关。</div>')

        tags = ["leetcode", "hot100", "Hot100::" + diff]
        if topic:
            tags.append("Hot100::" + topic.replace(" + ", "-").replace(" ", "-"))
        deck.add_note(genanki.Note(
            model=MODEL,
            fields=[front, desc, "<br>".join(back), topic or "Hot100", diff, slug],
            tags=tags,
        ))

    out = args.output or os.path.join(ws, "anki", "hot100.apkg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    genanki.Package(deck).write_to_file(out)
    print(f"导出 {len(selected)} 张卡片 -> {out}")
    print("打开 Anki → 文件 → 导入 → 选择该 .apkg 即可。")


if __name__ == "__main__":
    main()
