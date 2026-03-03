# MOMO - 协调者 Agent

多 Agent 系统的**协调者**。MOMO 不执行具体任务，而是将任务分发给专业子 Agent 并跟进结果。

系统中可以有多个 MOMO 实例（peer 关系），各自绑定不同用户或场景。

## 核心职责

- **任务调度** — 理解用户需求，拆解并派发给合适的子 Agent
- **进度跟进** — 通过心跳和 sessions_history 监控子 Agent 状态
- **系统运维** — 管理 Gateway 配置、cron 任务、Agent 健康度
- **记忆维护** — 记录决策和经验，维护长期记忆

## 快速部署

```bash
# 1. 复制到 workspace
cp -r examples/momo-agent ~/.openclaw/workspace-momo

# 2. 创建记忆目录
mkdir -p ~/.openclaw/workspace-momo/memory

# 3. 编辑 TOOLS.md — 填入实际的 Agent 列表和群聊 ID
# 4. 编辑 USER.md — 填入用户信息

# 5. 在 openclaw.json 中添加 agent 配置
# 6. 重启 Gateway
```

## 文件说明

| 文件 | 用途 | 部署时修改 |
|------|------|-----------|
| SOUL.md | 协调原则、任务下发规则、安全边界 | 按需调整 |
| AGENTS.md | 记忆规范、安全规则、Git 规范 | 按需调整 |
| TOOLS.md | Agent 列表、权限矩阵、定时任务 | **必须填写** |
| USER.md | 用户偏好 | **必须填写** |
| HEARTBEAT.md | 心跳检查项 | 按需调整 |
| IDENTITY.md | 身份标识 | 可选修改 |

## 内置 Skills

| Skill | 用途 |
|-------|------|
| **delegate-agent** | 异步任务派发（10s 超时 + 心跳跟进） |
| **agent-comm** | 跨 Agent 通信（sessions_send/list/history） |

## 权限配置

```json
{
  "id": "main",
  "name": "MOMO",
  "workspace": "~/.openclaw/workspace-momo",
  "tools": {
    "allow": [
      "exec", "read", "write", "edit",
      "message", "web_search", "web_fetch", "session_status",
      "cron", "browser", "gateway",
      "sessions_list", "sessions_history", "sessions_send", "sessions_spawn",
      "feishu_doc", "feishu_perm", "feishu_wiki", "feishu_drive",
      "tts", "canvas", "nodes"
    ]
  }
}
```

## 架构关系

```
  MOMO-A (用户A)    MOMO-B (用户B)     ← peer 协调者
   ┌──┼──┐          ┌──┼──┐
 coder scout      trader butler        ← 功能 Agent
```

- 多个 MOMO 实例之间是 **peer 关系**，彼此平等
- 每个 MOMO 拥有 sessions_* 权限，可协调子 Agent
- MOMO 只协调，不执行具体任务
- 子 Agent 失败 → MOMO 优化提示词重新派发，**不接手**
