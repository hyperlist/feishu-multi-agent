# 08 - Skill 目录组织

## 概述

OpenClaw 的 Skill 系统让 Agent 学会特定能力。合理组织 Skill 目录可以避免重复、方便维护。

## Skill 扫描路径

OpenClaw 按以下顺序扫描 Skill：

1. **Agent 自己的 workspace** — `~/.openclaw/workspace-{agent}/skills/`
2. **全局 skills 目录** — `~/.openclaw/skills/`
3. **内置 skills** — `/usr/local/lib/node_modules/openclaw/skills/`
4. **额外目录** — 通过 `skills.load.extraDirs` 配置

## 推荐的目录结构

```
~/.openclaw/
├── skills/                          # 全局共享 skills（所有 Agent 可见）
│   ├── feishu-doc-writer/           # 飞书文档写作
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── feishu-message-format.md
│   │       └── perm-fallback.md
│   ├── feishu-chat/                 # 飞书群聊管理
│   │   └── SKILL.md
│   └── model-tester/                # 模型对比测试
│       ├── SKILL.md
│       └── scripts/
│           └── run_test.sh
│
├── workspace-momo/                  # 协调者 agent (MOMO) workspace
│   └── skills/
│       ├── agent-comm/              # 跨 Agent 通信（仅 main 和需要通信的 Agent）
│       │   └── SKILL.md
│       └── delegate-coder/          # 任务委派（仅 main）
│           └── SKILL.md
│
├── workspace-coder/                 # coder agent workspace
│   └── skills/
│       └── project-switcher/        # 项目切换（仅 coder）
│           └── SKILL.md
│
├── workspace-butler/                # butler agent workspace
│   └── skills/
│       ├── apple-notes/             # Apple Notes（仅 butler）
│       └── apple-reminders/         # Apple Reminders（仅 butler）
│
└── workspace-assistant/            # 用户B的专属 agent workspace
    └── skills/
        └── agent-comm/              # 跨 Agent 通信（复制一份）
            └── SKILL.md
```

## 分类原则

### 全局 skills（`~/.openclaw/skills/`）

所有 Agent 都可能用到的通用能力：

- 飞书文档读写（feishu-doc-writer）
- 飞书群聊管理（feishu-chat）
- 模型测试工具（model-tester）
- 消息格式参考（作为 skill 的 references）

### Agent 专属 skills（`workspace-{agent}/skills/`）

只有特定 Agent 需要的能力：

- `delegate-coder` — 仅协调者用（委派编码任务）
- `project-switcher` — 仅 coder 用（切换项目目录）
- `apple-notes` / `apple-reminders` — 仅 butler 用（macOS 专属）
- `agent-comm` — 仅需要跨 Agent 通信的 Agent

### 判断标准

问自己：**这个 Skill 是否需要限制哪些 Agent 可以看到？**

- 如果任何 Agent 都可以用 → 全局
- 如果只有特定 Agent 需要 → 放对应 workspace
- 如果涉及安全/权限（如 gateway 操作）→ 放协调者 workspace

## 公共文件共享

### ❌ 旧方式：手动复制到每个 workspace

```
workspace-coder/references/feishu-message-format.md    # 副本1
workspace-trader/references/feishu-message-format.md   # 副本2
workspace-scout/references/feishu-message-format.md    # 副本3
...
```

改一处要改 N 处，容易遗漏。

### ✅ 新方式：放在全局 Skill 的 references 中

```
~/.openclaw/skills/feishu-doc-writer/references/feishu-message-format.md
```

所有 Agent 加载 feishu-doc-writer skill 时自动看到这个文件。

## Skill 文件结构

每个 Skill 的标准结构：

```
skill-name/
├── SKILL.md           # 必须：Skill 定义和使用说明
├── scripts/           # 可选：辅助脚本
│   └── helper.sh
├── references/        # 可选：参考文档
│   └── format-guide.md
└── config/            # 可选：配置文件
    └── defaults.json
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 一句话描述，用于自动匹配
---

# Skill 标题

## 使用说明
...

## 工作流程
...
```

`description` 字段很重要：OpenClaw 用它来判断何时自动加载这个 Skill。
