# 04 - Agent 间通信

## 概述

Agent 之间可以通过 `sessions_send`、`sessions_list`、`sessions_history` 三个工具实现跨 Agent 通信。

## 工具说明

### sessions_list

列出所有活跃的 Agent Session。

```
sessions_list(limit=10, messageLimit=1)
```

返回每个 Session 的 key、状态、最近消息等。

### sessions_send

向另一个 Agent 的 Session 发送消息。

```
sessions_send(sessionKey="agent:coder:feishu:group:oc_xxx", message="请帮我检查代码")
```

目标 Agent 会收到消息并处理，返回结果。

### sessions_history

获取某个 Session 的对话历史。

```
sessions_history(sessionKey="agent:coder:feishu:group:oc_xxx", limit=5)
```

## Session Key 格式

```
agent:{agent_id}:{channel}:{peer_kind}:{peer_id}
```

示例：
- `agent:trader:feishu:group:oc_abc123` — trader 在飞书群聊的 session
- `agent:user-assistant:feishu:dm:ou_xyz789` — user-assistant 处理用户私信的 session
- `agent:coder:main` — coder 的主 session

## 通信模式

### 模式一：主 Agent 异步委派任务（推荐模式）

```
用户 → main Agent: "帮我写个 Python 脚本"
         │
         ├── Step 1: 判断编码任务 → 拆解为任务 brief
         ├── Step 2: sessions_send → coder Agent（30秒超时）
         ├── Step 3: 立即回复用户"任务已派发，稍后汇报"
         │          （用户感知：秒回）
         │
         ├── Step 4: coder 后台执行任务（可能 10-30 分钟）
         │          （主 Agent 可以处理其他请求）
         │
         ▼
    下次心跳时检查 → 获取结果 → 汇总回复用户
```

**异步优势**：
- 用户立即得到响应
- 主 Agent 不阻塞，继续工作
- 容错性好，子 Agent 超时不影响主流程
- 可并发派发多个任务

### 模式二：同步委派（不推荐）

```
用户 → main Agent: "帮我写个 Python 脚本"
         │
         ├── sessions_send → coder Agent（120秒超时）
         │                   （主 Agent 阻塞等待）
         │
         ├── coder 执行任务
         ├── 返回结果
         │
         ▼
    main Agent 汇总回复用户（用户等待 2 分钟+）
```

**问题**：用户体验差，主 Agent 资源浪费。

### 模式二：Agent 主动求助（异步）

```
trader Agent: 需要搜索某只股票的新闻
         │
         ├── 自己没有 web_search 权限
         │
         ├── sessions_send → scout Agent（30秒超时）
         │                   （trader 不阻塞等待）
         │
         ├── 继续其他工作
         │
         ▼
    稍后通过 sessions_history 获取结果
```

**异步要点**：
- 发送请求后继续工作，不阻塞
- 后续通过历史记录获取结果
- 避免链式阻塞（A 等 B，B 等 C）

### 模式三：用户指令转发（异步）

```
用户 → user-assistant: "问 trader 今天的持仓情况"
         │
         ├── 识别到"问 trader"
         │
         ├── sessions_send → trader Agent（30秒超时）
         │                   （user-assistant 立即回复用户"已询问"）
         │
         ├── trader 后台查询持仓
         │
         ▼
    user-assistant 稍后获取结果 → 转发给用户
```

## 异步通信最佳实践

### 1. 超时设置
- **30 秒黄金法则**：所有 `sessions_send` 使用 `timeoutSeconds=30`
- **为什么**：避免主 Agent 阻塞，用户立即得到响应
- **预期行为**：超时是正常的，表示子 Agent 在后台工作

### 2. 任务派发流程
1. **拆解任务**：结构化 brief，包含验收标准
2. **异步发送**：30 秒超时，不等待结果
3. **立即回复**：告知用户"任务已派发，稍后汇报"
4. **心跳跟进**：每 30-60 分钟检查进度

### 3. 错误处理
- **超时不是错误**：预期行为，子 Agent 在后台工作
- **真正的错误**：sessionKey 错误、Agent 不在线、权限不足
- **重试策略**：同一任务最多尝试 3 次，然后拆分或换方案

### 4. 用户体验
- **派发即反馈**：用户立即得到确认，建立信任
- **进度透明**：定期汇报进度（"正在处理，已完成 50%"）
- **结果通知**：任务完成后主动通知

### 5. 系统设计
- **避免链式阻塞**：A → B → C 的链式调用要异步
- **资源隔离**：每个 Agent 独立工作，不共享状态
- **容错设计**：单个 Agent 失败不影响整体系统

## 权限控制

**不是所有 Agent 都应该有通信能力。** 推荐配置：

| Agent | 是否需要通信 | 理由 |
|-------|------------|------|
| main | ✅ | 主控调度，需要委派任务 |
| coder | ✅ | 可能需要查询其他 Agent 状态 |
| trader | ❌ | 专注交易，不需要主动通信 |
| scout | ❌ | 只读型，被动响应 |
| tutor | ❌ | 专注教学，不需要通信 |

在 Agent 的 `tools.allow` 中添加：
```json
"sessions_list", "sessions_history", "sessions_send"
```

## Skill: agent-comm

创建一个 Skill 来指导 Agent 如何使用通信工具：

```markdown
# skills/agent-comm/SKILL.md

---
name: agent-comm
description: 跨 Agent 通信。当用户说"问XX"、"让XX做"、"发给XX"时使用。
---

# Agent Communication

## Session Key 查找

1. 使用 `sessions_list` 查找目标 Agent 的 sessionKey
2. 格式：`agent:{id}:{channel}:{peer_kind}:{peer_id}`

## 发送消息

```
sessions_send(sessionKey="...", message="你的消息")
```

## 可用 Agent
- **trader** — 交易分析
- **coder** — 代码开发
- **scout** — 信息搜索
- **tutor** — 学习辅导
- **butler** — 生活管理
```

## SOUL.md 中的通信指引

在需要通信能力的 Agent 的 SOUL.md 中添加：

```markdown
## 🤝 跨 Agent 通信

你可以与其他 Agent 通信协作。当用户说「问 trader」「让 coder 看看」时，
使用 `sessions_send` 发送消息给对应 Agent。

**使用方式：**
1. 先用 `sessions_list` 查找目标 Agent 的 sessionKey
2. 用 `sessions_send(sessionKey=..., message=...)` 发送任务
3. 用 `sessions_history(sessionKey=...)` 查看回复
```

## 注意事项

1. **超时处理**：`sessions_send` 默认有超时，目标 Agent 未响应会返回 `timeout`
2. **Session 查找**：使用 `sessions_list` 而不是硬编码 sessionKey，因为 session 可能重建
3. **循环通信**：避免 A→B→A 的循环调用
4. **安全**：通信内容不应包含其他 Agent workspace 中的敏感信息
