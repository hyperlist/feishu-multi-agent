---
name: delegate-agent
description: Delegate tasks to agents asynchronously. Triggers on "让XX做", "delegate to", "assign to", "派发", "布置任务".
---

# Delegate to Agent — 异步任务派发

## 核心原则

1. **异步不阻塞** — 派发后立刻回复用户，绝不同步等待
2. **绝不代替功能 Agent 执行** — 包括编码、搜索、分析、验证
3. **Agent 自验** — 验收命令写在 brief 里，Agent 自己跑
4. **失败不接手** — 优化提示词重新派发，不自己做

## 派发流程

```
1. 拆解任务 → 结构化 brief
2. sessions_list(limit=20) → 找到目标 sessionKey
3. sessions_send(sessionKey=..., message=brief, timeoutSeconds=10)
   - 收到回复 → 秒完成
   - 超时 → 正常，Agent 在后台工作
4. 立刻回复用户"已派发给 XX"
5. 心跳时 sessions_history(sessionKey=..., limit=3) 跟进
```

## 任务 Brief 模板

```
## 任务：[一句话描述]

### 背景
[上下文]

### 工作目录
[绝对路径]

### 需求
1. [具体要求]

### 技术约束
- [约束条件]

### 不要修改的文件
[受保护文件列表]

### 验收标准
- [ ] [测试命令 + 预期结果]

### 验证要求
完成后必须：运行验收命令 → 附完整输出 → 标注 ✅/❌
```

## Agent 路由

| 任务类型 | Agent |
|---------|-------|
| 编码/调试/重构 | coder |
| 信息搜索/分析 | scout |
| 交易/数据策略 | trader |
| 日程/提醒/生活 | butler |
| 学习/辅导 | tutor |
| Gateway/配置 | main（自己做） |

## 禁止事项

- ❌ `timeoutSeconds > 30`
- ❌ 等 Agent 完成再回复用户
- ❌ 自己跑命令验证 Agent 的工作
- ❌ Agent 失败后自己接手

## 失败处理

1. `sessions_history` 诊断卡点
2. 拆分任务 / 补充上下文 / 修改 SOUL.md
3. 重新派发
4. 3 次失败 → 汇报用户
