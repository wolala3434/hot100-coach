# hot100-coach

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)

**给 AI 编程助手装一个 LeetCode Hot 100 刷题教练：一句话出题 → 图解讲模板 → 你写核心代码 → 对拍揪出隐蔽 bug → 自动导卡进 Anki。**

> 按代码随想录专题顺序出题 → labuladong 思维模板讲解 → 带 TODO 的代码骨架 → 本地判题 + 暴力对拍 → 登记进度 → 生成 Anki 卡组。

把「刷题」从「看题解抄一遍」变成「有教练盯着的刻意练习」。

## 效果预览

```
你  > 刷题
AI  > 【数组 + 双指针 3/13】283. 移动零（简单）
      给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
      示例：输入 [0,1,0,3,12] → 输出 [1,3,12,0,0]
      约束：1 <= nums.length <= 10^4 ...
      （快慢指针图解）
      核心模板：慢指针指向「已处理的非零序列末尾」，快指针找非零值。
      骨架已生成 solutions/0283_move_zeroes.py，TODO 留给你。

你  > 我写完了
AI  > 本地 8 个用例通过；随机对拍 1000 组：通过。
      已登记 done，Anki 卡片已导出（正面含完整题面）。
```

## 为什么做这个

刷 Hot 100 常见的三个坑：

1. **顺序乱** —— 官方题单不分专题，刷起来没有连贯性
2. **看会≠写对** —— 看完题解觉得懂了，自己写一堆隐蔽 bug（比如三数之和的 `i+=1` 去重失效）
3. **忘得快** —— 刷完不复习，一周后白刷

这个 skill 对应三件武器：**专题路线 + 对拍判题 + Anki 间隔重复**。

## 它怎么工作

```
你: 刷题
AI: 按专题路线出下一题（完整题面：描述+约束+示例）+ 讲思维模板 + 出图解
AI: 生成带 TODO 的代码骨架（docstring 内含完整题面 + 边界测试用例）
你: 自己写核心逻辑
AI: 本地跑测试 + 暴力对拍（朴素解做黄金标准，随机对拍上千组）
AI: 有 bug 指根因，没 bug 登记进度、生成 Anki 卡（卡片正面含完整题面）
你: 睡前在 Anki 里过一遍今天的卡
```

## 安装

```powershell
# 1. 克隆本仓库
git clone https://github.com/wolala3434/hot100-coach.git

# 2. 初始化工作区（在你想刷题的目录下执行）
cd hot100-coach
python scripts/setup.py
```

setup.py 会在当前目录创建 `hot100/` 工作区：克隆题解仓库（代码随想录 + labuladong，自动换镜像源）、拉取官方 Hot100 题单、生成刷题路线和进度台账。

**Trae 用户**：把本仓库的 `SKILL.md` 所在目录复制到 `~/.trae-cn/skills/hot100-coach/`，重启后说「刷题」即可触发。
**Claude Code 用户**：`claude skill install <本仓库路径>`，或把目录复制到 `~/.claude/skills/`。

## 可选：MCP 增强

在 MCP 配置中加入（可选，不配也能用）：

```json
{
  "mcpServers": {
    "algo-coach": {
      "command": "npx",
      "args": ["-y", "algo-coach-mcp@latest"]
    },
    "leetcode": {
      "command": "npx",
      "args": ["-y", "@jinzcdev/leetcode-mcp-server", "--site", "cn"]
    }
  }
}
```

- `algo-coach`：出题、理论讲解、参考解
- `leetcode`：拉题、看提交记录、自动写笔记（加 `--session <LEETCODE_SESSION>` 解锁登录态）

## 每日使用

```powershell
cd hot100                      # 进入工作区

# 刷题中（对 AI 说）：刷题 / 提示 / 答案 / 下一题 / 进度

# 刷完一题后（AI 会自动做，也可手动）：
python ../hot100-coach/scripts/track.py done 283          # 登记通关
python ../hot100-coach/scripts/track.py note 283 "..."    # 记一行笔记
python ../hot100-coach/scripts/make_anki.py               # 重导 Anki 卡组
python ../hot100-coach/scripts/track.py stat              # 看进度条
```

## 目录结构

```
hot100-coach/                  ← 本仓库（skill 本体）
├── SKILL.md                   教练主流程（AI 读）
├── README.md                  你正在看的这个
├── scripts/
│   ├── setup.py               初始化工作区 + 克隆题解仓库
│   ├── fetch_hot100.py        拉取官方 Hot100 题单
│   ├── build_route.py         生成专题路线 + 进度台账
│   ├── track.py               进度/错题/笔记登记
│   └── make_anki.py           生成 Anki .apkg 卡组
├── references/
│   ├── topics.md              专题顺序 × labuladong 模板映射
│   └── judging.md             判题方法论（对拍为什么必须做）
└── assets/
    ├── solution_template.py          题目骨架模板
    └── differential_test_template.py 对拍模板

hot100/                        ← 你的工作区（setup 后生成）
├── route/hot100-route.md      刷题路线（按专题排序）
├── progress.json              进度台账
├── solutions/                 你的代码
├── anki/                      生成的卡组
└── vendor/                    题解仓库（代码随想录 + labuladong）
```

## 依赖

- Python 3.8+
- `genanki`（`pip install genanki`，setup.py 会自动装）
- Anki 桌面端（导卡用，去 [ankiweb.net](https://apps.ankiweb.net/) 下载）

## License

MIT
