"""定位 Hot100 工作区。

优先级：--workspace 参数 > HOT100_HOME 环境变量 > 从当前目录向上找 progress.json。
"""

import os
import sys


def resolve(ws=None):
    if ws:
        ws = os.path.abspath(ws)
        if not os.path.isdir(ws):
            sys.exit(f"工作区不存在：{ws}")
        return ws

    env = os.environ.get("HOT100_HOME")
    if env and os.path.isdir(env):
        return env

    cwd = os.path.abspath(os.getcwd())
    p = cwd
    while True:
        if os.path.isfile(os.path.join(p, "progress.json")) and \
                os.path.isfile(os.path.join(p, "data", "hot100.json")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent

    for name in ("hot100", "leetcode-hot100"):
        cand = os.path.join(cwd, name)
        if os.path.isfile(os.path.join(cand, "progress.json")):
            return cand

    sys.exit(
        "找不到 Hot100 工作区。\n"
        "  初始化: python scripts/setup.py\n"
        "  或 cd 到已有工作区目录再运行。"
    )
