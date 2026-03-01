# Permission Fallback (when feishu_perm tool is disabled)

When `feishu_perm` tool is not enabled in config (`channels.feishu.tools.perm: true`), use direct API calls.

## Step 1: Get Tenant Access Token

```bash
curl -s 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
```

Extract `tenant_access_token` from response.

Note: App ID is in TOOLS.md. App Secret is in environment or OpenClaw config — check `gateway config.get` for `channels.feishu.appSecret`.

## Step 2: Add Collaborator

```bash
curl -s 'https://open.feishu.cn/open-apis/drive/v1/permissions/<DOC_TOKEN>/members?type=docx' \
  -H "Authorization: Bearer <TENANT_ACCESS_TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{
    "member_type": "openid",
    "member_id": "<OPEN_ID>",
    "perm": "full_access"
  }'
```

Replace:
- `<DOC_TOKEN>` — document token
- `<TENANT_ACCESS_TOKEN>` — from step 1
- `<OPEN_ID>` — user's open_id (e.g. `ou_xxxx`)

## Permission Levels
- `view` — read only
- `edit` — can edit
- `full_access` — can manage (edit + share + delete)

## Better Solution

Enable the tool in config to avoid manual curl:

```yaml
channels:
  feishu:
    tools:
      perm: true
```

Then use `feishu_perm` tool directly.
