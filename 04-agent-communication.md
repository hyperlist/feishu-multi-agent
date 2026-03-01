# 04 - Agent 间通信

## 工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `sessions_list` | 列出活跃 Session | `sessions_list(limit=10)` |
| `sessions_send` | 向 Agent 发消息 | `sessions_send(sessionKey="...", message="...")` |
| `sessions_history` | 获取历史记录 | `sessions_history(sessionKey="...", limit=5)` |

## Session Key 格式

```
agent:{agent_id}:{channel}:{peer_kind}:{peer_id}
```

示例：
- `agent:coder:feishu:group:oc_xxx` — coder 的飞书群聊 session
- `agent:main:feishu:dm:ou_xxx` — main 的私信 session

## 异步委派（推荐模式）

```
用户 → main: "帮我写个脚本"
  │
  ├─ 拆解任务 brief
  ├─ sessions_send → coder（10-30s 超时）
  ├─ 立即回复用户"已派发"     ← 用户感知：秒回
  │
  └─ 心跳时 sessions_history → 获取结果 → 汇总回复
```

**关键原则：**
- **超时 10-30 秒**：避免主 Agent 阻塞
- **超时是正常的**：表示子 Agent 在后台工作
- **立即回复用户**：不等结果
- **心跳跟进**：定期检查进度

> ❌ 同步等待（120s+ 超时）会阻塞主 Agent、浪费资源、用户体验差。

## 权限控制

不是所有 Agent 都需要通信能力：

| Agent | 通信 | 理由 |
|-------|------|------|
| main | ✅ | 主控调度 |
| coder | 可选 | 可能需要查询其他 Agent |
| trader/scout/tutor | ❌ | 专注本职，被动响应 |

在 `tools.allow` 中添加：`sessions_list`, `sessions_history`, `sessions_send`

## SOUL.md 通信指引模板

在需要通信的 Agent 的 SOUL.md 中添加：

```markdown
## 跨 Agent 通信
1. `sessions_list` 查找目标 sessionKey
2. `sessions_send(sessionKey=..., message=...)` 发送
3. `sessions_history(sessionKey=...)` 查看回复
```

## 注意事项

- **避免链式阻塞**：A→B→C 的调用都要异步
- **避免循环通信**：A→B→A 会死循环
- **不要硬编码 sessionKey**：session 可能重建，用 `sessions_list` 查找
- **通信内容不含敏感信息**：不跨 workspace 传递私密数据
