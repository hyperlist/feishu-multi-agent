---
name: delegate-agent
description: Delegate tasks to sub-agents asynchronously. Use when user says "让XX做", "delegate to", "assign to", or when a task should be handed off to a sub-agent. Triggers on "派发", "布置任务", "让XX做", "delegate to", "assign to".
---

# Delegate to Agent — 异步任务派发

将任务派发给子 Agent，异步跟进结果。适用于所有子 Agent。

## 核心原则

1. **绝不代替子 Agent 执行任务** — 包括编码、搜索、分析、验证
2. **异步不阻塞** — 派发后立刻回复用户，不同步等待
3. **结果由 Agent 自验** — 验收命令写在任务里，Agent 自己跑
4. **失败不接手** — 失败了优化提示词重新派发，不自己做

## 派发流程（5 步，必须严格执行）

### Step 1: 拆解任务

将用户需求拆解为结构化任务 brief（格式见下方模板）。

### Step 2: 查找 Session Key

```
sessions_list(limit=20)
```

找到目标 Agent 的 sessionKey，格式：`agent:<id>:feishu:group:oc_<chat_id>`

### Step 3: 异步派发

```
sessions_send(sessionKey=<key>, message=<brief>, timeoutSeconds=30)
```

**必须用 30 秒短超时。** 不管是否收到回复。

- 收到回复 → Agent 秒完成，直接汇报
- 超时（status=timeout） → 正常，Agent 在后台工作

### Step 4: 立刻回复用户

不等结果，立刻告诉用户任务已派发：

- "已派发给 coder，预计 10 分钟完成"
- "scout 正在搜索，稍后汇报"

**绝不同步等待 Agent 完成再回复用户。**

### Step 5: 异步跟进

在下次心跳时检查 Agent 是否完成：

```
sessions_history(sessionKey=<key>, limit=3)
```

- Agent 完成 → 汇报给用户
- Agent 未完成 → 继续等下次心跳
- Agent 失败 → 走失败处理流程

可在 HEARTBEAT.md 中记录待检查任务：
```markdown
## 待检查任务
- [ ] coder: 重构量化系统架构 (派发: 18:22)
```

## 任务 Brief 模板

```
## 任务：[一句话描述]

### 背景
[为什么需要做这个，上下文信息]

### 工作目录
[绝对路径]

### 现有文件结构
[ls/tree output — 帮 Agent 理解项目]

### 需求
1. [具体要求，带验收标准]
2. [另一个要求]

### 技术约束
- [语言/框架约束]
- [依赖限制]

### 不要修改的文件
[明确列出受保护文件]

### 验收标准
- [ ] [测试命令 + 预期结果]
- [ ] [另一个测试]

### 验证要求（必须由你完成）
开发完成后，你必须：
1. 运行上面每一条验收命令
2. 在回复中附上完整的命令输出
3. 如果任何测试失败，自行修复后重新测试
4. 最终回复中标注每条验收标准的通过状态（✅/❌）

### 注意事项
- [已知坑点]
```

### 不同 Agent 的 Brief 侧重

| Agent | Brief 重点 | 验收方式 |
|-------|-----------|---------|
| coder | 文件结构、代码规范、编译/测试命令 | 自己跑测试、附输出 |
| trader | 数据源、风控规则、输出格式 | 自己跑策略验证 |
| scout | 搜索关键词、输出模板、来源要求 | 自己检查信息覆盖度 |
| tutor | 知识领域、难度要求、格式规范 | 自己检查准确性 |
| butler | 操作步骤、确认要求、安全约束 | 自己验证操作结果 |

## Agent 路由参考

| 任务类型 | 推荐 Agent |
|---------|-----------|
| 编码/调试/重构 | coder |
| 信息搜索/市场分析 | scout |
| 数据分析/交易策略 | trader |
| 日程/提醒/生活管理 | butler |
| 学习/辅导/知识推送 | tutor |
| 系统管理/Gateway/配置 | main（自己做） |

## 禁止事项

- ❌ `timeoutSeconds > 30`（会阻塞自己等待 Agent）
- ❌ 自己 exec 跑命令验证 Agent 的工作
- ❌ 自己读 Agent 写的代码/文件做 review
- ❌ 自己修改 Agent workspace 里的文件
- ❌ Agent 失败后自己接手执行
- ❌ 同步等待完成后才回复用户

## 失败处理流程

Agent 失败时**不要自己接手**：

1. **诊断**：`sessions_history` 查看卡在哪里
2. **优化**：
   - 任务太复杂 → 拆分成 2-3 个小任务
   - 缺少上下文 → 补充文件结构/完整内容
   - Agent 理解偏差 → 修改 Agent 的 SOUL.md 加入约束
3. **重新派发**：用优化后的 brief 重新发送
4. **反复失败（3 次+）**：汇报用户，建议：
   - 换模型
   - 拆分为更小的子任务
   - 用户自己处理

## 最佳实践

1. **任务 brief 越详细，Agent 表现越好** — 提供完整文件结构、现有代码引用、明确的验收命令
2. **"不要修改"比"修改这些"更重要** — 明确列出受保护文件，防止 Agent 破坏已有代码
3. **验收标准必须可执行** — 写成具体命令 + 预期输出，不要模糊描述
4. **一次一个大任务** — 不要同时给一个 Agent 派多个无关任务
5. **失败是优化 Agent 的机会** — 每次失败记录原因，更新 Agent 的 SOUL.md 或任务模板
