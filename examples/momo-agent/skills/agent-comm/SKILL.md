---
name: agent-comm
description: |
  跨 Agent 通信。发消息、查状态、读历史。
  触发: "发给trader"、"查agent状态"、"让scout查"。
---

# Agent Communication

## Session Key 格式

```
agent:{agent_id}:{channel}:{peer_kind}:{peer_id}
```

示例：`agent:coder:feishu:group:oc_你的群聊ID`

通过 `sessions_list` 获取实际 key。

## 工具

### sessions_list — 列出活跃 session

```
sessions_list(limit=10, messageLimit=1)
```

### sessions_send — 发消息给 agent

```
sessions_send(sessionKey="agent:coder:...", message="...", timeoutSeconds=10)
```

- 必须用 sessionKey（不是 agentId）
- Agent 在自己的 workspace 和模型下运行

### sessions_history — 读历史

```
sessions_history(sessionKey="agent:coder:...", limit=5)
```

## 常用场景

**派发任务：** sessions_list → sessions_send(timeout=10) → 回复用户

**检查进度：** sessions_history(limit=3) → 看最新消息

**多 agent 协作：** A 的结果 → 作为上下文发给 B

## 注意

- 查 agent 状态只需 `sessions_history limit=3`，不拉全量
- 网关重启后检查正在执行的 agent 是否中断
