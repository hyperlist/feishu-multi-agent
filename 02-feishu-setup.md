# 02 - 飞书应用配置

## 创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn/)
2. 创建「企业自建应用」
3. 记下 `App ID` 和 `App Secret`

## 必需权限

在「权限管理」中申请以下权限：

### 消息相关
- `im:message:send_as_bot` — 发送消息
- `im:message` — 接收消息
- `im:message:readonly` — 读取消息

### 群聊管理（可选）
- `im:chat` — 获取群信息
- `im:chat:create` — 创建群聊
- `im:chat:update` — 修改群信息
- `im:chat.members:write_only` — 管理群成员

### 文档相关（可选）
- `docs:doc` — 读写文档
- `docs:doc:create` — 创建文档
- `drive:drive` — 云盘操作
- `wiki:wiki` — 知识库操作

### 通讯录（可选）
- `contact:user.base:readonly` — 获取用户基本信息

## 开启 Bot 能力

1. 应用详情 → 「添加应用能力」→ 「机器人」
2. 设置 Bot 名称（如 `clawd`）

## 事件订阅

OpenClaw 使用 **WebSocket 长连接** 模式，不需要配置回调 URL。

在「事件订阅」中启用以下事件：
- `im.message.receive_v1` — 接收消息

## OpenClaw Gateway 配置

### Gateway 基础配置

```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "<生成一个随机 token，如 openssl rand -hex 24>"
    }
  }
}
```

| 参数 | 说明 |
|------|------|
| `port` | Gateway 监听端口，默认 18789 |
| `mode` | `local` 本地模式 |
| `bind` | `loopback` 只监听 127.0.0.1；`0.0.0.0` 监听所有接口 |
| `auth.mode` | `token` 需要 token 认证；`none` 无认证（不推荐） |
| `auth.token` | Gateway API 访问令牌 |

### 必须开启的全局配置

```json
{
  "tools": {
    "agentToAgent": {
      "enabled": true
    },
    "web": {
      "search": {
        "enabled": true,
        "provider": "brave",
        "apiKey": "<YOUR_BRAVE_API_KEY>"
      }
    }
  },
  "messages": {
    "ackReactionScope": "group-mentions"
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true
  },
  "skills": {
    "install": {
      "nodeManager": "pnpm"
    }
  },
  "plugins": {
    "allow": ["feishu"],
    "entries": {
      "feishu": { "enabled": true }
    }
  }
}
```

| 配置 | 说明 | 必须？ |
|------|------|--------|
| `tools.agentToAgent.enabled` | 开启 Agent 间通信 | 多 Agent 系统必须 |
| `tools.web.search` | 网页搜索能力 | 按需 |
| `messages.ackReactionScope` | 消息确认 emoji 反应范围 | 推荐 |
| `commands.native` | 内置命令（/status 等） | 推荐 auto |
| `commands.restart` | 允许通过命令重启 | 推荐 |
| `plugins.allow` | 启用飞书插件 | 必须 |
| `channels.feishu.tools.perm` | 启用 feishu_perm 工具 | 需要文档权限管理时必须 |

### 飞书渠道配置

在 `openclaw.json` 中配置飞书渠道：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "accounts": {
        "default": {
          "appId": "<你的 App ID>",
          "appSecret": "<你的 App Secret>",
          "botName": "clawd"
        }
      },
      "dmPolicy": "allowlist",
      "groupPolicy": "open",
      "requireMention": false,
      "allowFrom": [
        "<你的 open_id>"
      ],
      "dm": {
        "allowFrom": [
          "<你的 open_id>"
        ]
      }
    }
  },
  "plugins": {
    "allow": ["feishu"],
    "entries": {
      "feishu": { "enabled": true }
    }
  }
}
```

### 关键参数说明

| 参数 | 说明 |
|------|------|
| `connectionMode` | 固定 `websocket`，飞书 WebSocket 长连接 |
| `dmPolicy` | `allowlist` 表示只允许白名单用户私信 |
| `groupPolicy` | `open` 表示群聊开放接收消息 |
| `requireMention` | `false` 时不需要 @Bot 也能响应 |
| `allowFrom` | 全局允许的用户 open_id 列表 |
| `dm.allowFrom` | 允许私信的用户 open_id 列表 |

## 获取 open_id

1. 在飞书中给 Bot 发一条私信
2. 查看 OpenClaw 日志，找到消息中的 `sender.open_id`
3. 或通过飞书 API 查询：
   ```bash
   # 先获取 tenant_access_token
   TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
     -H "Content-Type: application/json" \
     -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' \
     | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")
   ```

## 多账号模式（可选）

如果需要同时连接多个飞书租户：

```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "default": {
          "appId": "<企业版 App ID>",
          "appSecret": "<企业版 Secret>",
          "botName": "clawd"
        },
        "personal": {
          "appId": "<个人版 App ID>",
          "appSecret": "<个人版 Secret>",
          "botName": "clawd"
        }
      }
    }
  }
}
```

⚠️ **注意**：不同租户的 `open_id` 不通用，同一个人在不同租户有不同的 open_id。

## 创建群聊

为每个 Agent 创建独立群聊：

1. 在飞书中手动创建群，把 Bot 拉进去
2. 或通过 API 创建（参考 [06-feishu-chat-management.md](06-feishu-chat-management.md)）

获取群聊 ID：
- 在群聊中发一条消息，查看 OpenClaw 日志中的 `chat_id`（格式：`oc_xxx`）

## 群聊安全控制

可以按群聊设置消息来源白名单：

```json
{
  "channels": {
    "feishu": {
      "groups": {
        "oc_群聊ID": {
          "enabled": true,
          "requireMention": false,
          "groupAllowFrom": "*"
        }
      }
    }
  }
}
```

- `groupAllowFrom: "*"` — 群里所有人都能触发 Agent
- `groupAllowFrom: ["open_id_1", "open_id_2"]` — 只有指定用户能触发
- 不设置时继承全局 `groupAllowFrom`
