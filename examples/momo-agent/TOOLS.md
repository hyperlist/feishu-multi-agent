# TOOLS.md - MOMO (协调者 Agent)

> 部署后根据实际环境填写

## 环境

- **OS:** macOS / Linux
- **Python:** 3.x

## 多 Agent 系统

| Agent | 群聊 ID | 用途 |
|-------|---------|------|
| momo | — | 协调者 |
| coder | `oc_你的群聊ID` | 开发助手 |
| trader | `oc_你的群聊ID` | 交易助手 |
| scout | `oc_你的群聊ID` | 情报助手 |
| tutor | `oc_你的群聊ID` | 学习助手 |
| butler | `oc_你的群聊ID` | 生活助手 |

## 工具权限矩阵

| 工具 | momo | coder | trader | scout | tutor | butler |
|------|------|-------|--------|-------|-------|--------|
| exec | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| read/write/edit | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| message | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| web_search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cron | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| browser | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| sessions_* | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| gateway | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

> 设计原则：gateway/sessions 仅 main 可用；coder 专注编码；scout/tutor 只读

## 定时任务

| 任务 | Agent | 时间 | 说明 |
|------|-------|------|------|
| 心跳 | momo | 每 30min | 批量检查 |
| 示例 cron | — | — | 按需添加 |

---

_环境变了就更新这里。_
