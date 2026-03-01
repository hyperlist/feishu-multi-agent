# 10 - 配置引导：从零搭建飞书多 Agent 系统

> **目标读者**：主 Agent（AI）。读完这份文档后，你可以引导用户完成整套系统搭建。

---

## 总流程（5 步）

```
Step 1: 向用户收集信息（飞书凭证、想要的 Agent）
Step 2: 引导用户申请飞书权限
Step 3: 运行脚本创建子 Agent（workspace + 身份文件 + 飞书群 + 配置）
Step 4: 重启 Gateway
Step 5: 在每个群聊中发测试消息，确认 Agent 正常工作
```

---

## Step 1: 收集信息

**向用户发送以下问题，等用户全部回答后再继续。不要跳过。**

```
我来帮你搭建飞书多 Agent 系统。请回答以下问题：

1. 飞书应用凭证
   - App ID: ?
   - App Secret: ?
   - Bot 名称: ?（如 clawd）

2. 你的飞书 open_id: ?
   （不知道？先给 Bot 发一条私信，我帮你从日志找）

3. 你想创建哪些 Agent？可以选预设或自定义：
   预设: coder / trader / scout / tutor / butler / writer / analyst
   自定义: 告诉我名称和一句话描述

4. 需要以下功能吗？（y/n）
   - Agent 间互相通信
   - Agent 读写飞书文档
   - Agent 创建/管理飞书群聊
   - 定时任务（心跳、定时推送）
   - 网页搜索
```

**检查点**：确认拿到了 App ID、App Secret、open_id、至少一个 Agent 名称。缺少任何一项都不要继续。

---

## Step 2: 引导申请飞书权限

根据用户选择的功能，告诉用户需要申请哪些权限。

### 必选权限（所有场景）

```
im:message:send_as_bot    — 发送消息
im:message               — 接收消息  
im:message:readonly       — 读取消息
```

### 群聊管理（用户选了"管理飞书群聊"）

```
im:chat                  — 获取群信息
im:chat:create           — 创建群聊
im:chat:update           — 修改群信息
im:chat.members:write_only — 管理群成员
```

### 文档读写（用户选了"读写飞书文档"）

```
docs:doc                 — 读写文档
docs:doc:create          — 创建文档
drive:drive              — 云盘操作
drive:permission:member:create — 文档权限管理
```

**告诉用户**：
```
请到 https://open.feishu.cn → 你的应用 → 权限管理，申请以上权限。
企业应用还需要管理员审批。全部通过后告诉我。
```

**检查点**：用户确认权限已申请通过。

---

## Step 3: 创建子 Agent

**对用户选择的每个 Agent，运行创建脚本。**

### 方式一：使用脚本（推荐）

脚本位置：`scripts/create_agent.py`

```bash
# 示例：创建 coder agent（使用预设）
python3 scripts/create_agent.py \
  --agent-id coder \
  --agent-name "Coder" \
  --role "代码开发助手" \
  --emoji "💻" \
  --user-name "用户名" \
  --preset coder \
  --app-id "cli_xxx" \
  --app-secret "xxx" \
  --user-open-id "ou_xxx"

# 示例：创建自定义 agent
python3 scripts/create_agent.py \
  --agent-id myagent \
  --agent-name "MyAgent" \
  --role "数据分析助手" \
  --emoji "📊" \
  --user-name "用户名" \
  --tools "exec,read,write,message,web_search,web_fetch,session_status" \
  --app-id "cli_xxx" \
  --app-secret "xxx" \
  --user-open-id "ou_xxx"
```

脚本会自动：
1. 创建 workspace 目录（`~/.openclaw/workspace-{agent_id}/`）
2. 生成 IDENTITY.md、SOUL.md、AGENTS.md
3. 调用飞书 API 创建群聊并拉入用户
4. 更新 openclaw.json（添加 agent + binding + groups）
5. 备份原配置到 `.json.bak`

### 方式二：手动创建（脚本无法运行时）

如果脚本运行失败，按以下步骤手动操作：

#### 2a. 创建目录

```bash
mkdir -p ~/.openclaw/workspace-{agent_id}/{memory,skills}
```

#### 2b. 创建 IDENTITY.md

```bash
cat > ~/.openclaw/workspace-{agent_id}/IDENTITY.md << 'EOF'
# IDENTITY.md
- **Name:** {agent_id}
- **Creature:** {用户名}的{角色描述}
- **Emoji:** {emoji}
EOF
```

#### 2c. 创建 SOUL.md

使用 `examples/agent-soul-template.md` 作为模板，替换所有 `{占位符}`。

#### 2d. 创建飞书群聊

```bash
# 获取 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"APP_ID","app_secret":"APP_SECRET"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")

# 创建群
CHAT_ID=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/chats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"AgentName 助手","chat_mode":"group","chat_type":"private"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['chat_id'])")

# 拉用户进群
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/chats/${CHAT_ID}/members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_list":["USER_OPEN_ID"]}'

echo "群聊 ID: $CHAT_ID"
```

#### 2e. 更新 openclaw.json

⚠️ **关键**：必须用 Python 读取完整配置 → 追加 → 写回。不要手动拼 JSON。

```python
import json

with open('/path/to/.openclaw/openclaw.json') as f:
    config = json.load(f)

# 添加 Agent（追加到 list，不要替换 list）
config['agents']['list'].append({
    "id": "agent_id",
    "name": "AgentName",
    "workspace": "/path/to/workspace-agent_id",
    "tools": {"allow": ["read", "message", "web_search", "web_fetch", "session_status"]}
})

# 添加 Binding
config['bindings'].append({
    "agentId": "agent_id",
    "match": {"channel": "feishu", "accountId": "default",
              "peer": {"kind": "group", "id": "oc_CHAT_ID"}}
})

# 添加群聊配置
config['channels']['feishu']['groups']['oc_CHAT_ID'] = {
    "enabled": True, "requireMention": False
}

# 验证
print(f"Agents: {len(config['agents']['list'])}")
print(f"Bindings: {len(config['bindings'])}")

# 写入
with open('/path/to/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

**检查点**：每个 Agent 都有 workspace、身份文件、群聊 ID、配置条目。

---

## Step 4: 重启 Gateway

```bash
openclaw gateway restart
```

或者通过 gateway 工具：
```
gateway(action="restart")
```

**检查点**：重启成功，无报错。

---

## Step 5: 验证

在每个新创建的群聊中发送一条测试消息：

```
你好，请告诉我你是谁
```

验证项：
- ✅ Agent 正常回复
- ✅ 回复中的身份与 SOUL.md 一致
- ✅ 使用正确的语言和风格

如果 Agent 没有响应：
1. 检查 binding 中的 chat_id 是否正确
2. 检查 groups 配置中是否注册了该群聊
3. 查看 OpenClaw 日志：`openclaw status`

---

## 预设角色参考

| 预设 | 工具权限 | 适用场景 |
|------|---------|---------|
| coder | exec, read, write, edit, browser | 代码开发、调试 |
| trader | exec, read, write, edit, cron | 交易分析、监控 |
| scout | read, web_search（只读） | 信息搜索、情报 |
| tutor | read, web_search（只读） | 学习辅导 |
| butler | exec, read, cron, browser | 日程、提醒、生活 |
| writer | read, feishu_doc, feishu_perm | 文案、报告 |
| analyst | exec, read, write, feishu_doc | 数据分析 |

所有预设都自动包含：`message`, `web_fetch`, `session_status`。

---

## 跨 Agent 通信设置（可选）

如果用户需要 Agent 间通信：

1. 给需要通信的 Agent 添加工具权限：
   ```json
   "sessions_list", "sessions_history", "sessions_send"
   ```

2. 在这些 Agent 的 workspace 中放置 `agent-comm` skill：
   ```bash
   cp -r skills/agent-comm ~/.openclaw/workspace-{agent_id}/skills/
   ```

3. 在 SOUL.md 中添加通信指引（参考 `04-agent-communication.md`）

**注意**：不是所有 Agent 都需要通信能力。只给 main 和需要主动联系其他 Agent 的 Agent 开放。
