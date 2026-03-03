---
name: delegate-agent
description: |
  异步任务派发。将任务委托给子 Agent，不阻塞等待。
  触发: "让coder做"、"派发给trader"、"delegate to scout"。
---

# Delegate to Agent — 异步任务派发

## 核心原则

1. **绝不代替子 Agent 执行** — 包括编码、搜索、分析
2. **异步不阻塞** — 派发后立刻回复用户
3. **结果由 Agent 自验** — 验收命令写在 brief 里
4. **失败不接手** — 优化提示词重新派发

## 派发流程

```
1. 拆解需求 → 结构化 brief
2. sessions_list → 找 sessionKey
3. sessions_send(timeoutSeconds=10) → 异步发送
4. 立刻回复用户 → "已派发给 coder"
5. 心跳时 sessions_history(limit=3) → 检查进度
```

## Brief 模板

```markdown
## 任务：[标题]

### 背景
[为什么需要]

### 工作目录
[绝对路径]

### 需求
1. [具体需求]
2. [...]

### 验收标准
- [ ] [测试命令和预期结果]

### 验证要求（由你完成）
完成后运行验收命令，附上输出，标注 ✅/❌。
```

## 失败处理

1. `sessions_history` 看卡在哪里
2. 任务太复杂 → 拆小；缺上下文 → 补充
3. 重新派发（优化后的 brief）
4. **3 次失败 → 汇报用户**

## 禁止

- ❌ timeoutSeconds > 10（阻塞等待）
- ❌ 自己跑测试验证 agent 的工作
- ❌ 自己修改 agent workspace 的文件
- ❌ agent 失败后自己接手
