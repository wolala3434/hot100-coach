"""登记刷题进度 / 笔记 / 错题。

用法（在包含工作区的目录下运行，或设 HOT100_HOME）:
  python scripts/track.py done 1                  # 标记第 1 题已完成
  python scripts/track.py review 15               # 标记为「待复习」（错题）
  python scripts/track.py reset 1                 # 重置为 todo
  python scripts/track.py note 1 "哈希一次遍历，注意先查后存"
  python scripts/track.py list done               # 列出所有已完成题
  python scripts/track.py stat                    # 查看整体进度
"""

import argparse
import json
import os
import sys
from datetime import datetime

import _workspace

ICON = {"todo": "⬜", "done": "✅", "review": "🔁"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["done", "review", "reset", "note", "list", "stat"])
    ap.add_argument("target", nargs="?", help="题号，或 list 时的状态")
    ap.add_argument("text", nargs="?", help="note 时的笔记内容")
    ap.add_argument("--workspace", default=None, help="工作区路径")
    args = ap.parse_args()

    ws = _workspace.resolve(args.workspace)
    progress_path = os.path.join(ws, "progress.json")
    with open(progress_path, encoding="utf-8") as f:
        d = json.load(f)
    problems = d["problems"]

    def save():
        d["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    if args.action == "stat":
        cnt = {"todo": 0, "done": 0, "review": 0}
        by_topic = {}
        for rec in problems.values():
            st = rec.get("status", "todo")
            cnt[st] = cnt.get(st, 0) + 1
            t = rec.get("topic", "其他")
            by_topic.setdefault(t, {"todo": 0, "done": 0, "review": 0})
            by_topic[t][st] += 1
        total = len(problems)
        done = cnt["done"]
        print(f"总进度: {done}/{total} 已完成  ({done * 100 // total}%)  待复习 {cnt['review']}")
        print("-" * 46)
        for t, c in by_topic.items():
            n = c["todo"] + c["done"] + c["review"]
            bar = "█" * c["done"] + "▓" * c["review"] + "░" * (n - c["done"] - c["review"])
            print(f"  {t:<12} {c['done']:>2}/{n:<2} {bar}")
        return

    if args.action == "list":
        status = args.target or "done"
        rows = sorted((r for r in problems.values() if r.get("status") == status),
                      key=lambda r: r["id"])
        print(f"{ICON.get(status, '')} {status} ({len(rows)}):")
        for r in rows:
            print(f"  {r['id']:>3}. {r['title']} [{r.get('topic', '')}]")
        return

    if not args.target:
        sys.exit("需要题号，例如: track.py done 1")
    key = str(int(args.target))
    if key not in problems:
        sys.exit(f"题号 {key} 不在 Hot100 清单中")
    rec = problems[key]

    if args.action == "note":
        rec["notes"] = args.text or ""
        save()
        print(f"已记录第 {key} 题笔记：《{rec['title']}》")
        return

    rec["status"] = {"done": "done", "review": "review", "reset": "todo"}[args.action]
    if args.action == "done":
        rec["attempts"] = rec.get("attempts", 0) + 1
    save()
    print(f"{ICON[rec['status']]} 第 {key} 题《{rec['title']}》-> {rec['status']}")


if __name__ == "__main__":
    main()
