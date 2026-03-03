# 🦞 飞书多 Agent 协作方案

> 基于 [OpenClaw](https://github.com/openclaw/openclaw) 的飞书多 Agent 系统设计与实现。

## 🎯 项目原则

**这个项目是为 AI 写的，也是由 AI 维护的。**

你可以直接将这个仓库喂给 OpenClaw（小龙虾 🦞），它会自动理解架构并帮你创建多 Agent 系统。人类不需要逐行阅读——让你的 AI 读。

### 💬 试试对你的 AI 说

```
读一下 INDEX.md，了解这个项目的结构
```

```
帮我部署一个 MOMO 协调者 Agent 和一个 Coder Agent
```

```
按照 10-setup-wizard.md 引导我完成飞书多 Agent 系统搭建
```

```
读一下 examples/coder-agent/，帮我创建一个开发助手
```

- **AI-first 文档**：结构化的提示词工程，而非给人看的散文
- **模型一致性**：明确的代码和 checklist 代替模糊描述，减少不同模型的理解偏差
- **自维护**：由 Agent 维护的项目，脚本化操作代替手动配置
- **强制脱敏**：所有示例经过脱敏处理，不含真实身份信息

## 这个项目做什么？

用**一个飞书 Bot** 驱动**多个独立 AI Agent**。每个 Agent 绑定一个飞书群聊，拥有独立的身份、记忆、工具权限，Agent 之间可以互相通信协作。

```
                    飞书 Bot（一个应用）
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     群聊「开发」   群聊「交易」   群聊「情报」
          │              │              │
      Coder Agent   Trader Agent   Scout Agent
```

### 核心能力

- 🤖 **一 Bot 多 Agent** — 一个飞书应用，多个独立 AI 助手
- 💬 **群聊隔离** — 每个 Agent 专属群聊，独立上下文
- 📡 **Agent 间通信** — 异步派任务、跨 Agent 协作
- 📝 **飞书文档** — 创建和编辑飞书文档（支持 MD 导入）
- 🔐 **权限隔离** — 每个 Agent 独立工具白名单
- 🕐 **定时任务** — 心跳监控、定时推送

## 快速开始

> 假设已安装 OpenClaw 并完成基础配置。

### Step 1：创建飞书应用

1. [飞书开放平台](https://open.feishu.cn/app) → 创建企业自建应用
2. 记录 **App ID** 和 **App Secret**
3. 添加「机器人」能力
4. 申请权限（见下方权限清单）
5. 事件订阅：`im.message.receive_v1`，连接方式选 **WebSocket**
6. 发布应用版本

详细配置见 [02-feishu-setup.md](02-feishu-setup.md)。

### Step 2：配置 OpenClaw

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "accounts": {
        "default": {
          "appId": "<YOUR_APP_ID>",
          "appSecret": "<YOUR_APP_SECRET>"
        }
      },
      "dm": { "allowFrom": ["ou_<YOUR_OPEN_ID>"] }
    }
  },
  "bindings": [{
    "agentId": "main",
    "match": { "channel": "feishu", "peer": { "kind": "dm", "id": "ou_<YOUR_OPEN_ID>" } }
  }]
}
```

重启 Gateway，给 Bot 发消息验证。

### Step 3：扩展为多 Agent

**脚本自动创建：**
```bash
python3 scripts/create_agent.py \
  --agent-id coder --preset coder \
  --app-id "<APP_ID>" --app-secret "<APP_SECRET>" \
  --user-open-id "ou_<YOUR_OPEN_ID>"
```

自动完成：创建工作目录 → 生成身份文件 → 建群 → 更新配置。

手动方式见 [03-agent-binding.md](03-agent-binding.md)。

## 架构原理

### Binding（路由）

一条 binding = 一条路由规则：
```json
{ "agentId": "coder", "match": { "channel": "feishu", "peer": { "kind": "group", "id": "oc_xxx" } } }
```
来自该群聊的消息 → 全部交给 coder 处理。

### Session（会话隔离）

每个 Agent + 群聊组合 = 独立会话（独立上下文、工作目录、模型、工具）。

### Agent 间通信

通过 `sessions_send` 异步委派，详见 [04-agent-communication.md](04-agent-communication.md)。

## 命名建议

协调者 Agent 推荐以 **MOMO** 命名（如 `momo`），功能 Agent 按职责正常命名（`coder`、`trader`、`scout` 等）。系统支持多个 MOMO 实例（peer 关系）。

这不是强制要求，只是一个小小的偏好建议 🦞

## 预设角色

| 角色 | 模板 | 工具权限 | 适合场景 |
|------|------|---------|---------|
| **momo** | `momo-agent` | 协调权限（sessions_*, gateway） | 协调者（支持多实例 peer） |
| **coder** | `coder-agent` | 代码执行、文件读写 | 开发、调试 |
| **trader** | — | 代码执行、定时任务 | 交易分析 |
| **scout** | — | 只读、网页搜索 | 信息搜索 |
| **tutor** | — | 只读、网页搜索 | 学习辅导 |
| **butler** | — | 代码执行、定时任务、浏览器 | 日程、生活 |

> 有模板的 preset（main/coder）使用 `create_agent.py --preset` 时会自动复制 `examples/` 中的完整配置文件。

## 飞书权限清单

| 功能 | 权限 |
|------|------|
| 基础消息 | `im:message` `im:message:send_as_bot` |
| 群聊管理 | `im:chat:create` `im:chat:update` `im:chat.members:write_only` |
| 文档读写 | `docs:doc` `docs:doc:create` `drive:drive` |
| 权限管理 | `drive:permission:member:create` |

## ⚠️ 安全注意

- `dm.allowFrom` 必须配置白名单
- `appSecret` 不要提交到 Git
- `agents.list` 修改是**整体替换**，漏掉 Agent 会丢失配置
- Bot 创建的文档只有 Bot 能看，需调用权限 API 授权

## 项目结构

```
feishu-multi-agent/
├── README.md                  本文件
├── INDEX.md                   AI 文档索引
├── 01~11 *.md                 详细设计文档
├── scripts/create_agent.py    一键创建功能 Agent
├── examples/                  配置模板、Agent 模板
└── skills/                    可复用 Agent Skills
    ├── agent-comm/            跨 Agent 通信
    ├── delegate-agent/        任务委派
    ├── feishu-chat/           群聊管理
    ├── feishu-doc-writer/     文档写作
    └── maintenance/           项目维护
```

## 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) — AI Agent 运行时
- [飞书开放平台](https://open.feishu.cn/) — 消息、文档、群聊 API

## License

MIT
