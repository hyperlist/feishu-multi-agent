# 11 — 故障排查指南

## 快速诊断流程

```
Agent 不响应？
├── 1. openclaw status → Gateway 是否运行？
├── 2. 飞书 WebSocket 是否连接？（看日志 feishu ws connected）
├── 3. 消息是否匹配 binding？（检查 peer kind/id）
├── 4. allowFrom 是否包含发送者 open_id？
├── 5. Agent 是否有未完成的上一轮对话？（并发限制）
└── 6. 模型 API 是否可用？（检查 provider 连通性）
```

## 常见问题

### 1. Bot 收不到消息

**症状：** 飞书发消息给 Bot，无任何反应

**排查：**
```bash
# 检查 Gateway 状态
openclaw status

# 检查飞书连接日志
openclaw logs | grep -i "feishu\|websocket"
```

**常见原因：**
- WebSocket 未连接 → 检查 `appId` 和 `appSecret` 是否正确
- Bot 未开启「接收消息」权限 → 飞书开放平台 → 事件订阅
- 群聊中未 @ Bot 且 `requireMention: true` → 改为 `false` 或在群配置中覆盖

### 2. 消息到了但 Agent 不回复

**症状：** 日志显示收到消息，但 Agent 无响应

**排查：**
```bash
# 查看 binding 匹配情况
openclaw logs | grep "binding\|match\|route"
```

**常见原因：**
- **binding 不匹配：** `peer.kind` 错了（`dm` vs `group`），或 `peer.id` 写错
- **allowFrom 拦截：** 发送者 open_id 不在 `allowFrom` 列表中
- **并发限制：** Agent 正在处理上一条消息，新消息排队中（检查 `maxConcurrent`）
- **DM 策略：** `dmPolicy: "allowlist"` 但发送者不在白名单

### 3. Agent 回复到错误的群聊

**症状：** 在群 A 发消息，回复出现在群 B

**原因：** 多个 binding 的 match 条件有重叠

**修复：** 确保每个群聊 ID 只出现在一个 binding 中：
```json
{
  "agentId": "coder",
  "match": {
    "channel": "feishu",
    "peer": { "kind": "group", "id": "oc_CODER_CHAT_ID" }
  }
}
```

### 4. 飞书 API 权限错误

**常见错误码：**

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 99991668 | 无权限访问 | 飞书开放平台 → 权限管理 → 申请对应权限 |
| 99991672 | token 过期 | OpenClaw 自动刷新，重启 Gateway 即可 |
| 99991663 | 操作频率限制 | 降低请求频率，添加重试间隔 |
| 99991401 | Bot 不在群里 | 先将 Bot 加入群聊 |
| 230001 | 文档 token 无效 | 检查 doc_token 是否正确（从 URL /docx/XXX 提取） |
| 99991400 | 参数错误 | 检查请求体格式，特别是 receive_id_type |

### 5. 文档操作失败

**症状：** `feishu_doc` 写入返回 400 或权限错误

**排查清单：**
- Bot 是否有 `docx:document:*` 权限？
- 文档是否由 Bot 创建（或已添加 Bot 为协作者）？
- Markdown 内容是否包含不支持的格式？

**已知限制：**
- 飞书 API **不支持 Markdown 表格**（返回 400）→ 用结构化列表替代
- 单次 append 内容不宜过长 → 分段写入
- 文档 block 有排序问题 → 按顺序逐个 append

### 6. 跨 Agent 通信失败

**症状：** `sessions_send` 返回错误或目标 Agent 未收到

**排查：**
```bash
# 列出所有活跃 session
sessions_list(limit=20)
```

**常见原因：**
- **sessionKey 格式错误：** 正确格式为 `agent:<id>:feishu:group:oc_xxx`
- **目标 Agent 没有活跃 session：** 需要先在对应群聊中触发一次对话
- **agentToAgent 未开启：** 检查 `tools.agentToAgent.enabled: true`
- **Agent 无 sessions_send 权限：** 检查 `tools.allow` 列表

### 7. Gateway 配置错误导致启动失败

**症状：** `openclaw gateway start` 失败

**排查：**
```bash
# 验证 JSON 格式
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json')); print('✅ JSON valid')"

# 检查关键字段
python3 -c "
import json
c = json.load(open('$HOME/.openclaw/openclaw.json'))
assert 'agents' in c and 'list' in c['agents'], 'agents.list missing'
assert 'bindings' in c, 'bindings missing'
assert 'channels' in c, 'channels missing'
print(f'✅ agents: {len(c[\"agents\"][\"list\"])} | bindings: {len(c[\"bindings\"])}')
"
```

**预防措施：**
- 修改前备份：`cp openclaw.json openclaw.json.bak`
- 用 `config.apply` 而非手动编辑（自动做 JSON Schema 验证）
- `config.patch` 对数组字段是**整体替换**，必须包含所有元素

### 8. 心跳不工作

**症状：** Agent 不执行定期检查

**排查：**
- 检查 `heartbeat.every` 配置（如 `"30m"`）
- 检查 `heartbeat.activeHours`（是否在活跃时间段外）
- 检查 `heartbeat.target`（`"last"` 需要有最近活跃的 session）
- Agent 是否繁忙（并发处理中跳过心跳）

### 9. 模型 API 连接问题

**症状：** Agent 回复超时或返回错误

**排查：**
```bash
# 测试模型连通性
curl -s -o /dev/null -w "%{http_code}" \
  -H "x-api-key: YOUR_KEY" \
  YOUR_BASE_URL/v1/models
```

**应对：**
- 配置 `model.fallbacks` 作为备用模型
- 检查 API Key 是否过期
- 检查 baseUrl 协议是否匹配（anthropic-messages vs openai-chat）

## 日志关键词速查

| 关键词 | 含义 |
|--------|------|
| `ws connected` | WebSocket 连接成功 |
| `ws disconnected` | WebSocket 断开，自动重连 |
| `binding matched` | 消息匹配到 Agent |
| `no binding` | 消息未匹配任何 Agent |
| `allowFrom rejected` | 发送者不在白名单 |
| `rate limited` | 触发频率限制 |
| `compaction` | 会话上下文压缩 |
| `heartbeat` | 心跳轮询 |

## 紧急恢复

如果 Gateway 完全无法启动：

```bash
# 1. 恢复备份配置
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# 2. 或最小化配置启动（仅保留一个 Agent）
# 手动编辑 openclaw.json，只保留 main agent + 一个 binding

# 3. 重启
openclaw gateway restart
```
