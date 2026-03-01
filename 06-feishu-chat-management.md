# 06 - 飞书群聊管理

## 概述

通过飞书 Open API 管理群聊：创建群、添加/移除成员、修改群信息。

## 前置条件

- 飞书应用已开通权限：`im:chat:create`、`im:chat:update`、`im:chat.members:write_only`
- 准备好应用的 `app_id` 和 `app_secret`

## 获取 Token

每次操作前先获取 `tenant_access_token`（有效期 2 小时）：

```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<YOUR_APP_ID>","app_secret":"<YOUR_APP_SECRET>"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")
echo $TOKEN
```

## 操作

### 创建群聊

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/chats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agent-群名称",
    "chat_mode": "group",
    "chat_type": "private"
  }'
```

返回 `data.chat_id`（格式：`oc_xxx`）。

### 添加成员

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_list": ["ou_用户open_id_1", "ou_用户open_id_2"]}'
```

### 移除成员

```bash
curl -s -X DELETE "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_list": ["ou_用户open_id"]}'
```

### 修改群信息

```bash
curl -s -X PUT "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "新群名", "description": "群描述"}'
```

### 获取群信息 / 成员

```bash
# 群信息
curl -s "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}" \
  -H "Authorization: Bearer $TOKEN"

# 群成员
curl -s "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members" \
  -H "Authorization: Bearer $TOKEN"
```

## 常见错误

### 错误 232024：用户不在应用可见范围

```
{"code":232024,"msg":"Users do not have the visibility of the app, or the operator does not have collaboration permissions with the target users."}
```

**原因**：用户没有授权应用查看其信息，或不在应用的可用成员列表里。

**解决方案**（按推荐顺序）：
1. **先让用户给机器人发私信** — 建立关系后自动授权
2. **让管理员添加** — 如果是企业版，需要管理员在管理后台添加

**注意**：只有企业版应用可以添加跨企业的用户；个人版应用只能添加同一企业的用户。

### 错误 10014：app secret invalid

凭证错误，检查 app_id 和 app_secret。

## 创建群后注册到 OpenClaw

创建群聊后，需要在 `openclaw.json` 中注册：

### 1. 添加群聊配置

```json
{
  "channels": {
    "feishu": {
      "groups": {
        "oc_新群聊ID": {
          "enabled": true,
          "requireMention": false,
          "groupAllowFrom": "*"
        }
      }
    }
  }
}
```

### 2. 添加 Binding

```json
{
  "bindings": [
    {
      "agentId": "newagent",
      "match": {
        "channel": "feishu",
        "accountId": "default",
        "peer": { "kind": "group", "id": "oc_新群聊ID" }
      }
    }
  ]
}
```

### 3. 重启 Gateway

```bash
openclaw gateway restart
```

## 踩坑经验

1. **Bot 自动为群主** — 创建群聊时不指定 `owner_id`，Bot 自动成为群主
2. **不能直接加 Bot 不可见的用户** — 创建时不能指定未知用户，但创建后通过 members API 可以加
3. **跨租户 open_id 不通用** — 不同飞书租户中同一用户的 `open_id` 不同
4. **群聊注册后才能监听** — 只是创建群不够，必须在配置中添加 binding + groups 并重启
5. **Token 有效期 2 小时** — 长时间操作需要重新获取
6. **API 返回 `code=0` 表示成功** — 非 0 都是错误，看 `msg` 字段
