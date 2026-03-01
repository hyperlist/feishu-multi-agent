# 03 - Agent 绑定与路由

## 核心概念

OpenClaw 通过 `bindings` 配置将飞书的群聊/私信路由到不同的 Agent。

**一条 binding = 一条路由规则：** "来自这个群聊的消息 → 发给这个 Agent 处理"

## 配置结构

### Agent 定义

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "your-model-id",
        "fallbacks": []
      },
      "workspace": "/path/to/default/workspace"
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "/home/user/.openclaw/workspace",
        "model": {
          "primary": "your-model-id",
          "fallbacks": ["fallback-model-id"]
        },
        "heartbeat": {
          "every": "30m",
          "target": "last"
        }
      },
      {
        "id": "coder",
        "name": "Coder",
        "workspace": "/home/user/.openclaw/workspace-coder",
        "model": {
          "primary": "your-model-id",
          "fallbacks": ["fallback-model-id"]
        },
        "tools": {
          "allow": ["exec", "read", "write", "edit", "message", "web_search", "web_fetch", "session_status"]
        }
      }
    ]
  }
}
```

### Binding 定义

```json
{
  "bindings": [
    {
      "agentId": "coder",
      "match": {
        "channel": "feishu",
        "accountId": "default",
        "peer": {
          "kind": "group",
          "id": "oc_你的群聊ID"
        }
      }
    },
    {
      "agentId": "main",
      "match": {
        "channel": "feishu",
        "accountId": "default",
        "peer": {
          "kind": "dm",
          "id": "ou_你的open_id"
        }
      }
    }
  ]
}
```

## Binding 类型

### 群聊绑定

```json
{
  "agentId": "trader",
  "match": {
    "channel": "feishu",
    "accountId": "default",
    "peer": { "kind": "group", "id": "oc_群聊ID" }
  }
}
```

一个群聊只能绑定一个 Agent。消息进入该群 → 路由到对应 Agent。

### DM 绑定

```json
{
  "agentId": "main",
  "match": {
    "channel": "feishu",
    "accountId": "default",
    "peer": { "kind": "dm", "id": "ou_用户open_id" }
  }
}
```

不同用户的私信可以路由到不同 Agent。

## Agent 配置详解

### Workspace

每个 Agent 有独立的工作目录：

```
~/.openclaw/
├── workspace/          # main agent
├── workspace-coder/    # coder agent
├── workspace-trader/   # trader agent
└── workspace-scout/    # scout agent
```

Workspace 中的关键文件：
- `SOUL.md` — Agent 的身份、性格、规则
- `IDENTITY.md` — Agent 的名字、代号
- `AGENTS.md` — 工作流程指引
- `HEARTBEAT.md` — 心跳检查清单
- `memory/` — 日记文件
- `skills/` — Agent 专属 Skill

### 模型配置

```json
{
  "model": {
    "primary": "provider/model-id",
    "fallbacks": ["fallback-provider/model-id"]
  }
}
```

主模型不可用时自动切换到 fallback。

### 工具权限

```json
{
  "tools": {
    "allow": ["read", "message", "web_search"],
    "deny": ["exec", "write", "gateway"]
  }
}
```

- `allow` 和 `deny` 二选一即可
- 不设置时继承默认权限（全部开放）

### 心跳

```json
{
  "heartbeat": {
    "every": "30m",
    "target": "last",
    "activeHours": {
      "start": "09:00",
      "end": "22:00"
    }
  }
}
```

定期触发 Agent，用于主动检查、监控、清理等。

## 新增 Agent 流程

### Step 1: 创建 Workspace

```bash
mkdir -p ~/.openclaw/workspace-newagent
```

### Step 2: 创建身份文件

```bash
# IDENTITY.md
cat > ~/.openclaw/workspace-newagent/IDENTITY.md << 'EOF'
# IDENTITY.md
- **Name:** newagent
- **Creature:** 你的XX助手
- **Emoji:** 🤖
EOF

# SOUL.md
cat > ~/.openclaw/workspace-newagent/SOUL.md << 'EOF'
# SOUL.md - NewAgent

## 核心
你是一位XXX专家。你的职责是...

## 原则
- ...

## 风格
- 中文为主
- 简洁直接
EOF
```

### Step 3: 创建飞书群聊

在飞书中创建群，拉入 Bot，记录群聊 ID（`oc_xxx`）。

### Step 4: 更新配置

在 `openclaw.json` 中添加 Agent 和 Binding：

```json
// agents.list 中添加
{
  "id": "newagent",
  "name": "NewAgent",
  "workspace": "/home/user/.openclaw/workspace-newagent",
  "model": { "primary": "your-model-id" },
  "tools": { "allow": ["read", "message", "web_search"] }
}

// bindings 中添加
{
  "agentId": "newagent",
  "match": {
    "channel": "feishu",
    "accountId": "default",
    "peer": { "kind": "group", "id": "oc_新群聊ID" }
  }
}
```

### Step 5: 重启 Gateway

```bash
openclaw gateway restart
```

⚠️ **重要**：修改 `agents.list` 时必须包含**所有**现有 Agent。`config.patch` 的 `agents.list` 是**整体替换**，遗漏任何 Agent 会导致其配置丢失。

## 常见错误

### ❌ config.patch 丢失 Agent

```json
// 错误示例：只包含新 Agent，丢失了其他所有 Agent
{
  "agents": {
    "list": [
      { "id": "newagent", ... }
    ]
  }
}
```

**正确做法**：先 `gateway config.get` 获取完整配置，修改后通过 `config.apply` 写入完整配置。

### ❌ 跨租户 open_id 混用

不同飞书租户中同一用户的 `open_id` 不同。确保 binding 和 allowFrom 中的 open_id 匹配正确的租户。
