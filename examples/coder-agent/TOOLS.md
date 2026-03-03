# TOOLS.md - Coder Agent

> 部署后根据实际环境填写

## 环境

- **OS:** macOS / Linux
- **Python:** 3.x
- **Node:** vXX.x
- **包管理:** pip / npm / brew

## 工作目录

主工作区：`~/.openclaw/workspace-coder/`

## 代码仓库

| 项目 | 路径 | 说明 |
|------|------|------|
| my-project | `~/projects/my-project` | 示例，替换为实际项目 |

## 多 Agent 协作

| Agent | 群聊 ID | 关系 |
|-------|---------|------|
| momo | — | 协调者（派发任务给你） |
| coder | `oc_你的群聊ID` | 本 agent |

## 注意事项

- Git commit 后不 push，除非明确要求
- 跨 workspace 访问需要在 SOUL.md 中明确授权

---

_环境变了就更新这里。_
