# hot100-coach 🏋️

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)

**给你的 AI 编程助手请一位「刷题私教」——LeetCode Hot 100 专项训练营，一句话开练。**

出题按代码随想录的专题顺序走 🗺️，讲解套 labuladong 的思维模板 🧠，核心代码留给你自己写 ✍️，写完先用暴力解对拍上千组抓 bug 🔬，过了就生成 Anki 卡片帮你对抗遗忘 📇。

一句话：**把「看题解抄一遍」变成「有教练盯着的刻意练习」。**

## 🎬 效果预览

```
你  > 刷题
AI  > 【数组 + 双指针 3/13】283. 移动零（简单）
      给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
      示例：输入 [0,1,0,3,12] → 输出 [1,3,12,0,0]
      约束：1 <= nums.length <= 10^4 ...
      （快慢指针图解 🎨）
      核心模板：慢指针指向「已处理的非零序列末尾」，快指针找非零值。
      骨架已生成 solutions/0283_move_zeroes.py，TODO 留给你。

你  > 我写完了
AI  > 本地 8 个用例 ✅；随机对拍 1000 组 ✅。
      已登记 done，Anki 卡片已导出（正面含完整题面）。晚上记得复习 🌙
```

## 😮‍💨 为什么做这个

刷 Hot 100 的人，大概率踩过这三个坑：

1. **顺序乱** 🤯 —— 官方题单不分专题，东一榔头西一棒子，刚学会的双指针转头就忘
2. **看会 ≠ 写对** 🪤 —— 题解看得频频点头，自己一写全是隐蔽 bug（比如三数之和里 `i+=1` 导致去重失效，示例全绿也照样错）
3. **忘得快** 🫠 —— 刷完不复习，一周后跟没刷过一样

这个 skill 就是三味解药：**专题路线 + 对拍判题 + Anki 间隔重复**。

## 🔄 它是怎么工作的

```
你: 刷题
AI: 按专题路线出下一题（完整题面：描述 + 约束 + 示例）+ 讲思维模板 + 画图解
AI: 生成带 TODO 的代码骨架（docstring 里有完整题面和边界用例）
你: 自己动手写核心逻辑（这一步谁也替不了你 💪）
AI: 本地跑测试 + 暴力对拍（拿朴素解当黄金标准，随机对拍上千组）
AI: 有 bug 指出根因，没 bug 登记进度、生成 Anki 卡（卡片正面就是完整题面）
你: 睡前在 Anki 里过一遍今天的卡，记忆加固 ✅
```

## 🚀 安装

```powershell
# 1. 克隆本仓库
git clone https://github.com/wolala3434/hot100-coach.git

# 2. 初始化工作区（在你想刷题的目录下执行）
cd hot100-coach
python scripts/setup.py
```

`setup.py` 会一口气帮你搞定：创建 `hot100/` 工作区、克隆题解仓库（代码随想录 + labuladong，连不上 GitHub 会自动换镜像源 🪄）、拉取官方 Hot100 题单、生成专题路线和进度台账。

**Trae 用户**：把本仓库复制到 `~/.trae-cn/skills/hot100-coach/`，重启后对 AI 说一句「刷题」就开练。

**Claude Code 用户**：`claude skill install <本仓库路径>`，或者直接把目录丢进 `~/.claude/skills/`。

## 🔌 可选：MCP 增强

不配也能用，配了体验更好：

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

- `algo-coach`：出题、讲理论、给参考解 🎓
- `leetcode`：拉题、查提交记录、自动写笔记（加 `--session <LEETCODE_SESSION>` 解锁登录态）🔑

## 📅 每天怎么用

```powershell
cd hot100                      # 进入工作区

# 刷题中，对 AI 说的咒语只有几句：
#   刷题 / 提示 / 答案 / 下一题 / 进度

# 刷完一题后的收尾（AI 会自动做，也可以手动来）：
python ../hot100-coach/scripts/track.py done 283          # ✅ 登记通关
python ../hot100-coach/scripts/track.py note 283 "..."    # 📝 记一行笔记
python ../hot100-coach/scripts/make_anki.py               # 📇 重导 Anki 卡组
python ../hot100-coach/scripts/track.py stat              # 📊 看看进度条爬到哪了
```

## 🗂️ 目录结构

```
hot100-coach/                  ← 本仓库（skill 本体）
├── SKILL.md                   教练主流程（AI 读的，你不用管）
├── README.md                  你正在看的这个 👀
├── scripts/
│   ├── setup.py               初始化工作区 + 克隆题解仓库
│   ├── fetch_hot100.py        拉取官方 Hot100 题单（含完整题面）
│   ├── build_route.py         生成专题路线 + 进度台账
│   ├── track.py               进度 / 错题 / 笔记登记
│   └── make_anki.py           生成 Anki .apkg 卡组
├── references/
│   ├── topics.md              专题顺序 × labuladong 模板映射
│   └── judging.md             判题方法论（为什么对拍非做不可）
└── assets/
    ├── solution_template.py          题目骨架模板
    └── differential_test_template.py 对拍模板

hot100/                        ← 你的工作区（setup 之后自动生成）
├── route/hot100-route.md      刷题路线（按专题排好序）
├── progress.json              进度台账
├── solutions/                 你写的代码都在这
├── anki/                      生成的卡组
└── vendor/                    题解仓库（代码随想录 + labuladong）
```

## 🧰 依赖

- Python 3.8+
- `genanki`（跑 `pip install genanki`，其实 setup.py 会顺手帮你装好）
- Anki 桌面端（导卡用，去 [ankiweb.net](https://apps.ankiweb.net/) 下载）

## 📄 License

MIT —— 随便用，改完欢迎回来 PR 🙌
