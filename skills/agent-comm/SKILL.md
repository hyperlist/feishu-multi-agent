---
name: agent-comm
description: 跨 Agent 通信。当用户说"问XX"、"让XX做"、"发给XX"、"check agent status"时使用。
---

# Agent Communication

通过 sessions_send、sessions_list、sessions_history 实现跨 Agent 通信。

## Session Key 格式

每个 Agent Session 有唯一 key：

```
agent:{agent_id}:{channel}:{peer_kind}:{peer_id}
```

示例：
- `agent:trader:feishu:group:oc_xxx`
- `agent:scout:feishu:group:oc_yyy`

**不要硬编码 sessionKey**，用 `sessions_list` 动态查找。

## 工具

### sessions_list

列出活跃 session，找到目标 Agent 的 sessionKey。

```
sessions_list(limit=10, messageLimit=0)
```

### sessions_send

向另一个 Agent 发送消息，等待回复。

```
sessions_send(sessionKey="agent:coder:feishu:group:oc_xxx", message="你的任务描述")
```

- 成功时返回 `status: "ok"` 和 `reply`
- 超时时返回 `status: "timeout"`

### sessions_history

获取某个 Session 的对话历史。

```
sessions_history(sessionKey="agent:coder:feishu:group:oc_xxx", limit=5)
```

## 工作流程

1. 用户说「问 coder 这个 bug 怎么回事」
2. `sessions_list` → 找到 coder 的 sessionKey
3. `sessions_send(sessionKey, message="这个bug怎么回事: ...")` → 等待回复
4. 将 coder 的回复转发给用户

## 注意事项

- 避免循环调用（A→B→A）
- 超时不代表失败，目标 Agent 可能仍在处理
- 不要在消息中泄露其他 Agent workspace 的敏感信息
