"""暴力对拍模板：用朴素解做黄金标准，随机小数据压测用户解。

用法：
    1. 把 solve 换成用户的函数，brute 写成朴素版
    2. python 本文件
"""

import importlib.util
import random
import sys


def load_solution(path, func_name):
    spec = importlib.util.spec_from_file_location("sol", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, func_name)


def brute(inp):
    """黄金标准：怎么直接怎么写，不在乎复杂度。"""
    raise NotImplementedError("按题目写一个朴素解")


def gen_case():
    """生成一组随机小数据：值域收窄、长度短，让边界高频出现。"""
    n = random.randint(0, 10)
    return [random.randint(-5, 5) for _ in range(n)]


def main():
    solution_path = sys.argv[1]          # 用户解法文件路径
    func_name = sys.argv[2]              # 函数名
    trials = int(sys.argv[3]) if len(sys.argv) > 3 else 2000

    solve = load_solution(solution_path, func_name)
    random.seed(42)

    bad = 0
    for _ in range(trials):
        case = gen_case()
        got = solve(case.copy() if hasattr(case, "copy") else case)
        exp = brute(case.copy() if hasattr(case, "copy") else case)
        if got != exp:
            bad += 1
            if bad <= 5:
                print(f"不一致: input={case!r} got={got} exp={exp}")
    print(f"对拍 {trials - bad}/{trials} 一致（不一致 {bad}）")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
