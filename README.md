# 🦞 飞书多 Agent 协作方案

> 基于 [OpenClaw](https://github.com/openclaw/openclaw) 的飞书多 Agent 系统设计与实现。

## 这个项目做什么？

用**一个飞书 Bot**驱动**多个独立 AI Agent**。每个 Agent 绑定一个飞书群聊，拥有独立的身份、记忆、工具权限，并且 Agent 之间可以互相通信协作。

```
                    飞书 Bot（一个应用）
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     群聊「开发」   群聊「交易」   群聊「情报」
          │              │              │
      Coder Agent   Trader Agent   Scout Agent
     (写代码)      (盯盘分析)    (搜索资讯)
```

### 核心能力

- 🤖 **一 Bot 多 Agent** — 一个飞书应用，多个独立 AI 助手
- 💬 **群聊隔离** — 每个 Agent 一个专属群聊，互不干扰
- 📡 **Agent 间通信** — Agent 之间可以互相发消息、派任务
- 📝 **飞书文档** — Agent 可以创建和编辑飞书文档
- 🔐 **权限隔离** — 每个 Agent 有独立的工具白名单
- 🕐 **定时任务** — 心跳监控、定时推送、自动巡检

## 快速开始

> 假设你已安装 OpenClaw 并完成基础配置（模型、Gateway）。本指南只涉及**飞书多 Agent** 部分。

### Step 1：创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/app)，创建「企业自建应用」
2. 记录 **App ID**（`cli_xxx`）和 **App Secret**
3. 添加「机器人」能力（应用能力 → 添加能力 → 机器人）

### Step 2：申请飞书权限

在「权限管理」中按需申请（管理员审批后生效）：

**基础权限（必须）：**

| 权限 | 用途 |
|------|------|
| `im:message` | 接收消息 |
| `im:message:send_as_bot` | Bot 发送消息 |

**群聊管理（多 Agent 必须）：**

| 权限 | 用途 |
|------|------|
| `im:chat` | 读取群信息 |
| `im:chat:create` | 创建群聊 |
| `im:chat:update` | 修改群名/描述 |
| `im:chat.members:write_only` | 添加/移除群成员 |

**文档能力（按需）：**

| 权限 | 用途 |
|------|------|
| `docs:doc` | 读取文档 |
| `docs:doc:create` | 创建文档 |
| `drive:drive` | 云空间操作 |
| `drive:permission:member:create` | 文档权限管理 |

**事件订阅（必须）：**
- 添加 `im.message.receive_v1`（接收消息回调）
- 连接方式选择 **长连接（WebSocket）**

完成后发布应用版本。

详细配置见 [02-feishu-setup.md](02-feishu-setup.md)。

### Step 3：启用飞书插件

在 `openclaw.json` 中添加飞书插件和渠道配置：

```json
{
  "plugins": {
    "allow": ["feishu"],
    "entries": { "feishu": { "enabled": true } }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "dmPolicy": "allowlist",
      "accounts": {
        "default": {
          "appId": "<YOUR_APP_ID>",
          "appSecret": "<YOUR_APP_SECRET>",
          "botName": "your-bot-name"
        }
      },
      "dm": {
        "allowFrom": ["ou_<YOUR_OPEN_ID>"]
      }
    }
  }
}
```

> **如何获取 open_id？** 启动 Gateway 后给 Bot 发一条私信，在日志中可以看到发送者的 open_id（格式 `ou_xxx`）。

### Step 4：配置 Binding 和验证

添加路由绑定，将你的私信绑定到 main Agent：

```json
{
  "bindings": [
    {
      "agentId": "main",
      "match": {
        "channel": "feishu",
        "peer": { "kind": "dm", "id": "ou_<YOUR_OPEN_ID>" }
      }
    }
  ]
}
```

重启 Gateway，在飞书中给 Bot 发消息，收到回复即表示单 Agent 跑通。

### Step 5：扩展为多 Agent

**方式 A：脚本自动创建**

```bash
python3 scripts/create_agent.py \
  --agent-id coder \
  --agent-name "Coder" \
  --preset coder \
  --app-id "<YOUR_APP_ID>" \
  --app-secret "<YOUR_APP_SECRET>" \
  --user-open-id "ou_<YOUR_OPEN_ID>"
```

脚本自动完成：创建工作目录 → 生成身份文件 → 调飞书 API 建群 → 更新配置。

**方式 B：手动添加**

见 [03-agent-binding.md](03-agent-binding.md)。

### Step 6：开启 Agent 间通信（可选）

```json
{
  "tools": {
    "agentToAgent": { "enabled": true }
  }
}
```

在需要通信的 Agent 的 `tools.allow` 中加入 `sessions_send`、`sessions_list`。

详细用法见 [04-agent-communication.md](04-agent-communication.md)。

### 遇到问题？

查看 [11-troubleshooting.md](11-troubleshooting.md) — 覆盖 9 类常见问题和排查流程。

## ⚠️ 安全注意事项

- **`dm.allowFrom` 必须配置** — 不设白名单意味着任何人私信 Bot 都会触发 Agent
- **`appSecret` 不要提交到 Git** — 建议用环境变量或 secret manager
- **`agents.list` 修改是整体替换** — 漏掉现有 Agent 会导致配置丢失，务必备份
- **修改配置前先备份** — `cp openclaw.json openclaw.json.bak`
- **群聊 `groupAllowFrom: "*"`** 表示群内所有人的消息都会被处理，确认这是你想要的
- Bot 创建的文档**只有 Bot 自己能看** — 需要主动调用权限 API 授予用户访问权

## 项目结构

```
feishu-multi-agent/
│
├── README.md                 ← 你正在看的文件
├── INDEX.md                  ← AI 文档索引
├── SKILL.md                  ← OpenClaw Skill 入口
│
├── 01 ~ 10 文档              ← 详细设计文档（AI + 人类可读）
│   ├── 01-architecture.md        架构设计
│   ├── 02-feishu-setup.md        飞书应用配置
│   ├── 03-agent-binding.md       Agent 绑定与路由
│   ├── 04-agent-communication.md Agent 间通信
│   ├── 05-feishu-doc.md          飞书文档读写
│   ├── 06-feishu-chat-management.md 群聊管理
│   ├── 07-feishu-message-format.md  消息格式规范
│   ├── 08-skill-organization.md  Skill 目录组织
│   ├── 09-best-practices.md      最佳实践
│   ├── 10-setup-wizard.md        配置引导（AI 引导用户搭建）
│   └── 11-troubleshooting.md     故障排查指南
│
├── scripts/
│   └── create_agent.py       ← 一键创建子 Agent
│
├── examples/
│   ├── openclaw-config.json  ← 示例配置（脱敏）
│   ├── agent-soul-template.md
│   └── agent-identity-template.md
│
└── skills/                   ← 可复用的 Agent Skills
    ├── agent-comm/               跨 Agent 通信
    ├── delegate-agent/           任务委派
    ├── feishu-chat/              飞书群聊管理
    └── feishu-doc-writer/        飞书文档写作
```

## 架构原理

### Binding（路由绑定）

OpenClaw 的核心机制：**一条 binding = 一条路由规则**。

```json
{
  "agentId": "coder",
  "match": {
    "channel": "feishu",
    "peer": { "kind": "group", "id": "oc_群聊ID" }
  }
}
```

意思是：来自这个群聊的消息 → 全部交给 coder agent 处理。

### Session（会话隔离）

每个 Agent + 群聊组合形成独立会话：
- 独立的对话上下文
- 独立的工作目录
- 独立的模型和工具

### Agent 间通信

Agent 通过 `sessions_send` 工具互相发消息：

```
用户 → main: "让 coder 修一下这个 bug"
        │
        └─→ sessions_send → coder
                              │
                          修复代码
                              │
                          ←── 返回结果
        │
用户 ← main: "coder 已修复，改了 3 个文件"
```

## 预设角色

| 角色 | 工具权限 | 适合场景 |
|------|---------|---------|
| **coder** | 代码执行、文件读写、浏览器 | 开发、调试、重构 |
| **trader** | 代码执行、文件读写、定时任务 | 交易分析、持仓监控 |
| **scout** | 只读、网页搜索 | 信息搜索、市场情报 |
| **tutor** | 只读、网页搜索 | 学习辅导、知识问答 |
| **butler** | 代码执行、定时任务、浏览器 | 日程、提醒、生活管理 |
| **writer** | 飞书文档读写 | 文案、报告、内容创作 |
| **analyst** | 代码执行、文件读写、飞书文档 | 数据分析、报告生成 |

当然也可以完全自定义。

## 踩坑提醒

> 这些是实战中趟过的坑，每一条都有血泪教训。

### 🚨 配置修改必须包含所有 Agent

`agents.list` 是**整体替换**，不是追加。只传新 Agent 会导致其他 Agent 全部丢失。

### 🚨 飞书不支持 Markdown 表格

飞书文档 API 传入表格语法会返回 400。用列表替代。

### 🚨 Bot 创建的文档只有 Bot 能看

必须手动调用权限 API 授予用户访问权限。

### 🚨 跨租户 open_id 不通用

同一个人在不同飞书租户有不同的 open_id。

更多踩坑记录见 [09-best-practices.md](09-best-practices.md)。

## 飞书权限清单

根据你的需求申请：

| 功能 | 需要的权限 |
|------|-----------|
| 基础消息 | `im:message:send_as_bot` `im:message` `im:message:readonly` |
| 群聊管理 | `im:chat:create` `im:chat:update` `im:chat.members:write_only` |
| 文档读写 | `docs:doc` `docs:doc:create` `drive:drive` |
| 权限管理 | `drive:permission:member:create` |

## 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) — AI Agent 运行时
- [飞书开放平台](https://open.feishu.cn/) — 消息、文档、群聊 API

## License

MIT
