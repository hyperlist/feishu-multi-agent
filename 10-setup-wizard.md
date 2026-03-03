# 10 - 配置引导：从零搭建飞书多 Agent 系统

> **目标读者**：主 Agent（AI），引导用户完成系统搭建。

## 总流程

```
1. 收集信息（凭证、Agent 列表）
2. 引导申请飞书权限
3. 脚本创建子 Agent（workspace + 身份文件 + 飞书群 + 配置）
4. 确认 → 重启 Gateway
5. 验证 → 更新文档
```

---

## Step 1: 收集信息

向用户确认以下信息（缺少任何一项不继续）：

1. **飞书凭证**：App ID、App Secret、Bot 名称
2. **用户 open_id**（不知道则先给 Bot 发私信，从日志获取）
3. **Agent 列表**：预设（coder/trader/scout/tutor/butler）或自定义
4. **功能需求**：Agent 间通信、飞书文档、群聊管理、定时任务、搜索

## Step 2: 申请飞书权限

根据功能需求告知用户需要的权限：

**必选：** `im:message` `im:message:send_as_bot` `im:message:readonly`
**群聊：** `im:chat` `im:chat:create` `im:chat:update` `im:chat.members:write_only`
**文档：** `docs:doc` `docs:doc:create` `drive:drive` `drive:permission:member:create`

事件订阅：`im.message.receive_v1`，连接方式 **WebSocket**。

## Step 3: 创建子 Agent

### 脚本创建（推荐）

```bash
python3 scripts/create_agent.py \
  --agent-id coder --agent-name "Coder" --preset coder \
  --app-id "cli_xxx" --app-secret "xxx" --user-open-id "ou_xxx"
```

自动完成：创建 workspace → 复制/生成身份文件 → 飞书建群 → 更新配置 → 备份。

> 💡 有 `examples/` 模板的 preset（如 coder）会自动复制完整的 SOUL.md、AGENTS.md 等文件，开箱即用。

### 手动创建（备选）

1. `mkdir -p ~/.openclaw/workspace-{id}/{memory,skills}`
2. 创建 IDENTITY.md、SOUL.md（用 `examples/` 模板）
3. 飞书 API 建群（见 [06-feishu-chat-management.md](06-feishu-chat-management.md)）
4. Python 读取 openclaw.json → 追加 agent + binding + group → 写回

⚠️ `agents.list` 是整体替换，必须用 Python 追加，不要手动拼 JSON。

## Step 4: 确认 + 重启

**重启前与用户确认**（会中断当前所有会话）：

```
配置就绪，重启 Gateway 使新 Agent 生效。
重启会中断当前会话，需要几秒恢复。确认？(y/n)
```

```bash
openclaw gateway restart
```

## Step 5: 验证 + 更新文档

在每个新群聊发送 `你好，请告诉我你是谁`，确认 Agent 正常响应。

更新：
1. 主 Agent 的 TOOLS.md（agent 列表 + 权限矩阵）
2. 新 Agent 的 workspace 文档（SOUL.md/AGENTS.md/USER.md）
3. 复制必要 skills 到新 Agent workspace
4. Git 提交

---

## 预设角色

| 预设 | 工具权限 | 场景 |
|------|---------|------|
| coder | exec, read, write, edit, browser | 开发、调试 |
| trader | exec, read, write, edit, cron | 交易、监控 |
| scout | read, web_search（只读） | 搜索、情报 |
| tutor | read, web_search（只读） | 学习辅导 |
| butler | exec, read, cron, browser | 日程、生活 |

所有预设自动包含：`message`, `web_fetch`, `session_status`。

## 跨 Agent 通信（可选）

给需要通信的 Agent 添加 `sessions_list`, `sessions_history`, `sessions_send`，并放置 `agent-comm` skill。

详见 [04-agent-communication.md](04-agent-communication.md)。
