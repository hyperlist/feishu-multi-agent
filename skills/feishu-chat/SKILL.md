---
name: feishu-chat
description: |
  飞书群聊管理：创建群、添加/移除成员、修改群信息。
  需要 exec 权限执行 curl 命令。
---

# 飞书群聊管理

通过飞书 Open API 管理群聊。需要 `exec` 权限。

## 前置条件

- 飞书应用已开通 `im:chat:create`、`im:chat:update`、`im:chat.members:write_only` 权限
- 准备好 `app_id` 和 `app_secret`

## 获取 Token

每次操作前先获取 tenant_access_token（有效期 2 小时）：

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
  -d '{"name": "群名称", "chat_mode": "group", "chat_type": "private"}'
```

返回 `data.chat_id`（如 `oc_xxx`）。

### 添加成员

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_list": ["ou_用户open_id"]}'
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

## 踩坑经验

1. **Bot 自动为群主** — 创建时不指定 `owner_id`，Bot 自动成为群主
2. **不能直接加 Bot 不可见的用户** — 创建后通过 members API 可以加
3. **跨租户 open_id 不通用** — 不同飞书租户中同一用户的 open_id 不同
4. **创建后需注册** — 在 openclaw.json 添加 binding + groups 配置后重启
5. **Token 有效期 2 小时** — 长时间操作需重新获取
