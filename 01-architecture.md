# 01 - 整体架构设计

## 核心思路

**一个飞书 Bot，多个 AI Agent，通过群聊隔离。**

```
飞书 Bot (一个应用)
    │
    ├── 群聊 A → Agent: trader (交易助手)
    ├── 群聊 B → Agent: coder  (开发助手)
    ├── 群聊 C → Agent: scout  (情报助手)
    ├── 群聊 D → Agent: tutor  (学习助手)
    ├── 群聊 E → Agent: butler (生活助手)
    │
    ├── DM 用户 A → Agent: main   (主助手)
    └── DM 用户 B → Agent: user-assistant  (用户B的专属助手)
```

## 关键概念

### 1. Binding（绑定）

OpenClaw 的 `bindings` 配置决定了**哪个群聊/DM → 路由到哪个 Agent**。每条 binding 包含：

- `agentId`: 目标 Agent 的 ID
- `match.channel`: 消息来源渠道（`feishu`）
- `match.peer.kind`: `group`（群聊）或 `dm`（私信）
- `match.peer.id`: 群聊 ID 或用户 open_id

### 2. Session（会话）

每个 Agent + 群聊/DM 组合形成一个独立 Session，有独立的：
- 上下文（对话历史）
- 工作目录（workspace）
- 模型配置
- 工具权限

Session Key 格式：`agent:{agent_id}:{channel}:{peer_kind}:{peer_id}`

### 3. Agent 间通信

Agent 之间通过 `sessions_send` 工具通信：

```
Agent A (trader) ──sessions_send──► Agent B (coder)
                                        │
                                    处理任务
                                        │
                                    返回结果
```

### 4. 工具权限隔离

每个 Agent 可以配置独立的工具白名单/黑名单：

- 主 Agent: 拥有所有权限（gateway、browser、cron...）
- 只读 Agent（如 scout）: 仅 read、web_search、message
- 编码 Agent（如 coder）: exec、read、write、edit
- 跨 Agent 通信: sessions_list、sessions_history、sessions_send

## 架构优势

| 特性 | 说明 |
|------|------|
| **隔离性** | 每个 Agent 有独立 workspace、session、权限 |
| **可扩展** | 新增 Agent 只需：创建 workspace → 建群 → 加 binding |
| **灵活路由** | 群聊绑定 + DM 路由 + 跨 Agent 通信 |
| **统一入口** | 用户只需跟一个 Bot 对话 |
| **安全可控** | 工具权限按 Agent 粒度控制 |

## 数据流

```
用户在飞书群聊发消息
    │
    ▼
OpenClaw Gateway (WebSocket 长连接)
    │
    ├─ 匹配 binding → 路由到对应 Agent
    │
    ▼
Agent 处理（读 SOUL.md → 调用工具 → 生成回复）
    │
    ├─ 需要其他 Agent 协助？ → sessions_send
    │
    ▼
回复发送到原群聊/DM
```

## 推荐的 Agent 分工

| Agent | 职责 | 模型建议 | 工具权限 |
|-------|------|---------|---------|
| main | 主控调度、系统管理 | 最强模型 | 全部 |
| coder | 代码开发、调试 | 代码能力强的模型 | exec, read, write, edit |
| trader | 交易分析、监控 | 通用模型 | exec, read, write, cron |
| scout | 信息搜索、情报 | 通用模型 | read, web_search (只读) |
| tutor | 学习辅导 | 通用模型 | read, web_search (只读) |
| butler | 生活管理 | 通用模型 | exec, read, cron, browser |

> 实际 Agent 数量和分工根据需求调整，以上仅为参考。
