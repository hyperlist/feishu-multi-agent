# 09 - 最佳实践与踩坑记录

## 配置管理

### ⚠️ config.patch 的 agents.list 是整体替换

这是最常见的致命错误。`config.patch` 修改 `agents.list` 时会**替换整个数组**，不是追加。

```
❌ 错误：只传入新 Agent
config.patch(raw={"agents":{"list":[{"id":"newagent",...}]}})
→ 其他所有 Agent 配置丢失！

✅ 正确：传入完整列表
1. gateway config.get → 获取完整配置
2. 修改需要改的字段
3. config.apply → 写入完整配置
```

### 配置变更安全流程

```bash
# 1. 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 2. 用 Python 生成新配置（不要手动拼 JSON）
python3 << 'EOF'
import json
with open('~/.openclaw/openclaw.json') as f:
    config = json.load(f)
# 修改字段...
with open('/tmp/openclaw_new.json', 'w') as f:
    json.dump(config, f, indent=2)
EOF

# 3. 验证 JSON 格式
python3 -c "import json; json.load(open('/tmp/openclaw_new.json')); print('✅ valid')"

# 4. 验证关键字段
python3 -c "
import json
c = json.load(open('/tmp/openclaw_new.json'))
assert 'agents' in c and 'list' in c['agents'], 'agents.list 缺失'
assert 'bindings' in c, 'bindings 缺失'
print(f'✅ agents: {len(c[\"agents\"][\"list\"])} | bindings: {len(c[\"bindings\"])}')
"

# 5. 通过 config.apply 写入（会自动做 schema 验证 + 重启）
```

### 绝对禁止

- ❌ 直接往 openclaw.json 写非 JSON 内容
- ❌ 不验证就重启 gateway
- ❌ config.patch 只传部分 agents.list

## Agent 设计

### SOUL.md 要点

1. **身份明确** — 第一行说清楚"你是谁"，避免 Agent 混淆身份
2. **权限边界** — 明确列出可以做什么、不可以做什么
3. **通信指引** — 如果有跨 Agent 通信能力，说明何时使用、如何使用
4. **格式规范** — 特别是飞书消息格式，不支持 LaTeX/表格

### 避免身份混淆

如果你有多个相似的 Agent（如 assistant-a 和 assistant-b），在 SOUL.md 开头强调区分：

```markdown
> ⚠️ 你叫 **assistant-b**，不是 assistant-a。assistant-a 是用户A的助手，你是用户B的助手。
```

### 工具权限最小化

不要给 Agent 不需要的权限：

```
scout（搜索型）: read, web_search, message     ✅ 最小权限
scout（搜索型）: 全部权限                      ❌ 过度授权
```

### 任务委派原则

主 Agent 应该**委派而非亲力亲为**：

```
用户请求编码任务 → 发给 coder（不是自己写）
coder 出错 → 优化 coder 的提示词 → 重新派发
coder 反复出错（3次+）→ 才考虑自己做
```

## 飞书相关

### 消息格式

- 不用 LaTeX，用 `**粗体**` + `代码块`
- 不用 Markdown 表格，用列表
- 彩色文本：`<font color='red'>重点</font>`
- 数学公式：`E(X) = sum(xi * P(xi))`

### 文档 API

- 每次 append 只写一个 section（保证顺序）
- Bot 创建的文档必须手动授权给用户
- 权限降级：`full_access` → `edit` → `view`

### 群聊管理

- Bot 创建群后自动成为群主
- 创建群后还需要在配置中注册 binding + groups
- Token 有效期 2 小时

## 模型选择

### 测试方法

用同一个任务在不同模型上跑，比较：
- 工具调用准确率
- 输出质量
- 是否有结构性 bug（循环、格式错误）

### 常见问题

- 有些模型会在工具调用时出现格式泄漏（tool call 内容混入 thinking block）
- 首次启动时模型可能"犯迷糊"，清空 session 重试
- 编码任务对模型要求更高，选代码能力强的模型

## 心跳机制

### heartbeat vs cron

| 场景 | 用 heartbeat | 用 cron |
|------|------------|---------|
| 批量检查（邮件+日历+通知） | ✅ | ❌ |
| 精确定时（每天9:00） | ❌ | ✅ |
| 需要对话上下文 | ✅ | ❌ |
| 独立执行（不影响主会话） | ❌ | ✅ |
| 一次性提醒 | ❌ | ✅ |

### 心跳活跃时间

交易类 Agent 只在交易时段需要心跳：

```json
{
  "heartbeat": {
    "every": "60m",
    "activeHours": { "start": "09:25", "end": "15:05" }
  }
}
```

## 安全

1. **身份信息脱敏** — 开源分享时替换 open_id、app_secret、API key
2. **DM 白名单** — 限制谁可以私信 Bot
3. **workspace 隔离** — Agent 不应读取其他 Agent 的 workspace
4. **外部操作确认** — 发消息、发邮件等操作需要用户确认
5. **config 备份** — 每次修改配置前备份
