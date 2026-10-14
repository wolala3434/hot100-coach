"""初始化 Hot100 刷题工作区。

在当前目录创建一个 hot100/ 工作区，克隆题解仓库，拉取官方题单并生成刷题路线。

用法:
  python scripts/setup.py                            # 在当前目录创建 ./hot100
  python scripts/setup.py --workspace D:/algo/hot100 # 指定工作区路径
  python scripts/setup.py --skip-clone               # 已有题解仓库时跳过克隆
  python scripts/setup.py --proxy http://127.0.0.1:7890
"""

import argparse
import os
import subprocess
import sys

REPOS = {
    "leetcode-master": "https://github.com/youngyangyang04/leetcode-master.git",  # 代码随想录
    "labuladong-algo": "https://github.com/labuladong/fucking-algorithm.git",     # labuladong 算法小抄
}

# GitHub 直连失败时尝试的镜像加速（前缀 + 原 URL）
MIRRORS = [
    "https://ghfast.top/",
    "https://ghproxy.net/",
    "https://gh-proxy.com/",
]


def sh(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def ensure_genanki():
    try:
        import genanki  # noqa: F401
        print("genanki 已安装")
    except ImportError:
        sh([sys.executable, "-m", "pip", "install", "genanki"])


def clone(name, url, vendor, proxy=None):
    dest = os.path.join(vendor, name)
    if os.path.isdir(dest):
        print(f"已存在，跳过克隆: {dest}")
        return
    env = dict(os.environ)
    if proxy:
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
    for u in [url] + [m + url for m in MIRRORS]:
        try:
            subprocess.run(["git", "clone", "--depth", "1", u, dest],
                           check=True, env=env, capture_output=True, text=True)
            print(f"克隆成功: {u}")
            return
        except subprocess.CalledProcessError:
            print(f"克隆失败，换源重试: {u}")
    sys.exit(f"克隆 {name} 失败。请检查网络，或用 --proxy 指定代理后重试。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=None, help="工作区路径，默认 ./hot100")
    ap.add_argument("--skip-clone", action="store_true", help="跳过克隆题解仓库")
    ap.add_argument("--proxy", default=None, help="HTTP 代理，如 http://127.0.0.1:7890")
    args = ap.parse_args()

    ws = os.path.abspath(args.workspace or os.path.join(os.getcwd(), "hot100"))
    for d in ("data", "route", "solutions", "anki", "vendor"):
        os.makedirs(os.path.join(ws, d), exist_ok=True)

    ensure_genanki()

    vendor = os.path.join(ws, "vendor")
    if not args.skip_clone:
        for name, url in REPOS.items():
            clone(name, url, vendor, args.proxy)

    here = os.path.dirname(os.path.abspath(__file__))
    env = dict(os.environ)
    if args.proxy:
        env["HTTP_PROXY"] = args.proxy
        env["HTTPS_PROXY"] = args.proxy

    sh([sys.executable, os.path.join(here, "fetch_hot100.py"), "--workspace", ws], env=env)
    sh([sys.executable, os.path.join(here, "build_route.py"), "--workspace", ws], env=env)

    print("\n工作区就绪:", ws)
    print("下一步: 打开 route/hot100-route.md 按专题顺序开始刷题")


if __name__ == "__main__":
    main()
