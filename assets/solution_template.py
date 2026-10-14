"""{题号}. {中文名} ({难度})

专题: {专题}    标签: {标签}
链接: https://leetcode.cn/problems/{slug}/

题目:
    {题目描述}

示例:
    {示例}

约束: {约束}

核心思路 ({算法标签}):
    {一两句话核心思路}

提示(labuladong 思维模板):
    - {对应的模板文件路径}
"""

from typing import List


def {function_name}(...):
    # TODO: 在这里实现核心逻辑
    pass


if __name__ == "__main__":
    cases = [
        # (输入, 期望输出) —— 至少包含：题目示例 + 空/单元素 + 重复值 + 极值
        (..., ...),
    ]
    passed = 0
    for i, (inp, expected) in enumerate(cases, 1):
        got = {function_name}(inp)
        ok = got == expected
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(f"Case {i}: {status} | got: {got} | expected: {expected}")
    print(f"\n通过 {passed}/{len(cases)}")
