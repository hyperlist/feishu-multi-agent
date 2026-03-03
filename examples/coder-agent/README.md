# Coder Agent - 开箱即用的开发助手

## 快速部署

```bash
# 1. 复制到 workspace
cp -r examples/coder-agent ~/.openclaw/workspace-coder

# 2. 创建记忆目录
mkdir -p ~/.openclaw/workspace-coder/memory

# 3. 编辑 TOOLS.md — 填入实际的项目路径和环境信息
# 4. 编辑 USER.md — 填入你的信息

# 5. 在 openclaw.json 中添加 agent（或使用 create_agent.py）
python3 scripts/create_agent.py \
  --agent-id coder --agent-name "Coder" --preset coder \
  --app-id "cli_xxx" --app-secret "xxx" --user-open-id "ou_xxx"

# 6. 重启
openclaw gateway restart
```

## 文件说明

| 文件 | 用途 | 部署时修改 |
|------|------|-----------|
| SOUL.md | 行为定义、开发规范、代码风格 | 按需调整 |
| AGENTS.md | 职责、工具权限、安全规范 | 按需调整 |
| TOOLS.md | 环境信息（路径、仓库、Agent 列表） | **必须填写** |
| USER.md | 用户偏好 | **必须填写** |
| IDENTITY.md | 身份标识 | 可选修改 |

## 权限配置

```json
{
  "id": "coder",
  "name": "Coder",
  "workspace": "~/.openclaw/workspace-coder",
  "tools": {
    "allow": [
      "exec", "read", "write", "edit",
      "message", "web_search", "web_fetch", "session_status",
      "feishu_doc", "feishu_perm"
    ]
  }
}
```

## 核心能力

- **直接写文件** — 不给代码片段，直接在 workspace 创建/修改
- **自动测试** — 写完跑 pytest 验证
- **Git 规范** — 小步 commit，不擅自 push
- **大文件安全** — >100 行用 edit 不用 write
- **错误恢复** — 失败 2 次自动换方案

## 使用示例

在群聊中：

> 帮我写一个 Python CLI，读取 CSV 统计每列空值数量，支持 --output json

Coder 会自动：读需求 → 写代码 → 跑测试 → 回复结果
