"""生成 Hot100 专题刷题路线（代码随想录顺序），并初始化进度台账。

输入:
  data/hot100.json                          官方 Hot100 题单
  vendor/leetcode-master/problems/*.md      代码随想录本地题解
  vendor/labuladong-algo/**                 labuladong 思维模板

输出:
  route/hot100-route.md    按代码随想录专题顺序编排的路线
  progress.json            进度台账（已存在则不覆盖）

用法:
  python scripts/build_route.py --workspace ./hot100
"""

import argparse
import glob
import json
import os
import re

import _workspace

# 代码随想录 Hot100 专题顺序（数组 → 二分 → 链表 → 哈希 → 字符串 → 栈 → 二叉树 → 回溯 → 贪心 → DP → 图）
TOPIC_ORDER = [
    "数组 + 双指针", "二分查找", "链表", "哈希表", "字符串", "栈",
    "二叉树", "回溯", "贪心", "动态规划", "图论", "其他",
]

# 代码随想录 Hot100 官方路线（programmercarl.com/hot100）显式题号映射，优先于标签推断
CS_HOT100_MAP = {
    283: "数组 + 双指针", 11: "数组 + 双指针", 15: "数组 + 双指针", 42: "数组 + 双指针",
    3: "数组 + 双指针", 438: "数组 + 双指针",
    33: "二分查找", 34: "二分查找", 74: "二分查找",
    206: "链表", 21: "链表", 19: "链表", 24: "链表", 141: "链表", 142: "链表", 160: "链表",
    1: "哈希表", 49: "哈希表", 128: "哈希表",
    5: "字符串", 76: "字符串", 560: "字符串",
    20: "栈", 22: "栈", 155: "栈", 739: "栈", 84: "栈",
    94: "二叉树", 104: "二叉树", 102: "二叉树", 226: "二叉树", 101: "二叉树",
    543: "二叉树", 105: "二叉树",
    77: "回溯", 78: "回溯", 46: "回溯", 39: "回溯",
    56: "贪心",
    70: "动态规划", 53: "动态规划", 198: "动态规划", 62: "动态规划",
    300: "动态规划", 322: "动态规划", 1143: "动态规划",
    200: "图论", 207: "图论", 994: "图论",
}

# 兜底用的标签 → 专题（按特异性从高到低，避免 array 吞掉一切）
TAG_TOPIC = [
    ("回溯", ["backtracking"]),
    ("动态规划", ["dynamic-programming", "memoization"]),
    ("图论", ["graph", "breadth-first-search", "union-find", "topological-sort",
            "shortest-path", "minimum-spanning-tree"]),
    ("二叉树", ["binary-tree", "binary-search-tree", "tree"]),
    ("链表", ["linked-list"]),
    ("哈希表", ["hash-table"]),
    ("栈", ["stack", "monotonic-stack", "queue", "design"]),
    ("字符串", ["string", "trie"]),
    ("贪心", ["greedy"]),
    ("二分查找", ["binary-search"]),
    ("数组 + 双指针", ["array", "two-pointers", "sliding-window", "prefix-sum",
                  "sorting", "matrix", "simulation", "binary-indexed-tree", "segment-tree",
                  "recursion", "divide-and-conquer", "depth-first-search"]),
]

# labuladong 思维模板 → 专题
LABU_MAP = {
    "数组 + 双指针": ["算法思维系列/双指针技巧.md", "算法思维系列/前缀和技巧.md",
                 "算法思维系列/差分技巧.md", "算法思维系列/滑动窗口技巧进阶.md"],
    "二分查找": ["算法思维系列/二分查找详解.md", "高频面试系列/二分运用.md"],
    "链表": ["数据结构系列/递归反转链表的一部分.md", "高频面试系列/k个一组反转链表.md",
           "高频面试系列/判断回文链表.md", "高频面试系列/LRU算法.md"],
    "哈希表": [],
    "字符串": [],
    "栈": ["数据结构系列/单调栈.md", "数据结构系列/单调队列.md",
          "数据结构系列/队列实现栈栈实现队列.md"],
    "二叉树": ["数据结构系列/二叉树总结.md", "数据结构系列/二叉树系列1.md",
            "数据结构系列/二叉树系列2.md", "数据结构系列/BST1.md", "数据结构系列/BST2.md"],
    "回溯": ["算法思维系列/回溯算法详解修订版.md", "高频面试系列/子集排列组合.md"],
    "贪心": ["动态规划系列/贪心算法之区间调度问题.md"],
    "动态规划": ["动态规划系列/动态规划详解进阶.md", "动态规划系列/背包问题.md",
             "动态规划系列/子序列问题模板.md", "动态规划系列/团灭股票问题.md",
             "动态规划系列/状态压缩技巧.md"],
    "图论": ["算法思维系列/BFS框架.md", "数据结构系列/图.md", "数据结构系列/拓扑排序.md"],
    "其他": ["算法思维系列/常用的位操作.md"],
}


def build_cs_index(ws):
    """代码随想录本地题解：题号 -> 文件名"""
    idx = {}
    cs_md = os.path.join(ws, "vendor", "leetcode-master", "problems")
    if os.path.isdir(cs_md):
        for p in glob.glob(os.path.join(cs_md, "*.md")):
            m = re.match(r"^(\d+)\.", os.path.basename(p))
            if m:
                idx[int(m.group(1))] = os.path.basename(p)
    return idx


def assign_topic(qid, tags):
    if qid in CS_HOT100_MAP:
        return CS_HOT100_MAP[qid]
    tags = set(tags)
    for topic, slugs in TAG_TOPIC:
        if tags & set(slugs):
            return topic
    return "其他"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=None)
    args = ap.parse_args()
    ws = _workspace.resolve(args.workspace)

    data_path = os.path.join(ws, "data", "hot100.json")
    with open(data_path, encoding="utf-8") as f:
        problems = json.load(f)

    cs_index = build_cs_index(ws)
    grouped = {}
    for p in problems:
        qid = int(p["questionFrontendId"])
        tags = [t["slug"] for t in p.get("topicTags", [])]
        grouped.setdefault(assign_topic(qid, tags), []).append((p, tags))

    lines = [
        "# LeetCode Hot 100 刷题路线（代码随想录顺序）\n",
        "> 顺序编排：数组 → 链表 → 哈希 → 字符串 → 栈 → 二叉树 → 回溯 → 贪心 → 动态规划 → 图论",
        "> 每题配「代码随想录本地题解」+「labuladong 思维模板」；刷完一题用 scripts/track.py 登记。\n",
        f"共 {len(problems)} 题。\n",
    ]

    progress = {}
    diff_cn = {"EASY": "简单", "MEDIUM": "中等", "HARD": "困难"}
    for topic in TOPIC_ORDER:
        items = grouped.get(topic)
        if not items:
            continue
        lines.append(f"\n## {topic}（{len(items)} 题）\n")
        labu_files = LABU_MAP.get(topic, [])
        if labu_files:
            lines.append("**先读思维模板（labuladong）**：")
            for lf in labu_files:
                lines.append(f"- [ ] `vendor/labuladong-algo/{lf}`")
            lines.append("")
        lines.append("| # | 题目 | 难度 | 核心标签 | 代码随想录题解 | 状态 |")
        lines.append("|---|---|---|---|---|---|")
        items.sort(key=lambda x: ("EASY", "MEDIUM", "HARD").index(x[0]["difficulty"])
                   if x[0]["difficulty"] in ("EASY", "MEDIUM", "HARD") else 3)
        for p, tags in items:
            qid = int(p["questionFrontendId"])
            title = p["translatedTitle"]
            diff = diff_cn.get(p["difficulty"], p["difficulty"])
            tag_cn = "、".join(t.get("nameTranslated", t["slug"]) for t in p.get("topicTags", [])[:3])
            slug = p["titleSlug"]
            if qid in cs_index:
                cs_link = f"[本地题解](../vendor/leetcode-master/problems/{cs_index[qid]})"
            else:
                cs_link = "[代码随想录](https://programmercarl.com/hot100/)"
            lc_link = f"[力扣](https://leetcode.cn/problems/{slug}/)"
            lines.append(f"| {qid} | {title}（{lc_link}） | {diff} | {tag_cn} | {cs_link} | ⬜ |")
            progress[str(qid)] = {
                "id": qid, "slug": slug, "title": title, "titleEn": p["title"],
                "difficulty": p["difficulty"], "topic": topic,
                "status": "todo", "attempts": 0, "notes": "",
            }

    os.makedirs(os.path.join(ws, "route"), exist_ok=True)
    route_path = os.path.join(ws, "route", "hot100-route.md")
    with open(route_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    progress_path = os.path.join(ws, "progress.json")
    if not os.path.exists(progress_path):
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump({"updated": "", "problems": progress}, f, ensure_ascii=False, indent=2)

    print("route ->", route_path)
    print("progress ->", progress_path)
    for topic in TOPIC_ORDER:
        if grouped.get(topic):
            print(f"  {topic}: {len(grouped[topic])}")


if __name__ == "__main__":
    main()
