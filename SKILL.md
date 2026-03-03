---
name: feishu-multi-agent
description: |
  飞书多 Agent 系统搭建指南。当用户要求创建新的功能 Agent、配置飞书群聊绑定、
  搭建多 Agent 协作系统时激活此 skill。
  触发词：创建 agent、新建 agent、添加 agent、create agent、多 agent、飞书绑定。
---

# 飞书多 Agent 系统

## 你要做什么

帮用户搭建「一个飞书 Bot → 多个独立 AI Agent」的系统。每个 Agent 绑定一个飞书群聊，互相独立，可以通信。

## 读取顺序（严格按顺序）

**第一步：理解架构**
```
read("INDEX.md")       # 文档索引
read("01-architecture.md")  # 架构设计
```
读完你会知道：binding、session、agent 间通信的概念。

**第二步：收集用户信息**
```
read("10-setup-wizard.md")
read("examples/PLACEHOLDERS.md")
```
读完按 Phase 1 的问卷向用户收集信息。`PLACEHOLDERS.md` 列出了所有需要用户提供的字段。不要跳过任何问题。

**第三步：执行创建**
用户回答完问题后，运行创建脚本：
```
read("scripts/create_agent.py")
exec("python3 scripts/create_agent.py --agent-id xxx --role xxx ...")
```

**第四步：按需深入**
- 用户问飞书权限 → `read("02-feishu-setup.md")`
- 用户问 Agent 绑定 → `read("03-agent-binding.md")`
- 用户问 Agent 通信 → `read("04-agent-communication.md")`
- 用户问飞书文档 → `read("05-feishu-doc.md")`
- 用户问群聊管理 → `read("06-feishu-chat-management.md")`
- 用户问消息格式 → `read("07-feishu-message-format.md")`
- 用户问 skill 组织 → `read("08-skill-organization.md")`
- 用户问最佳实践 → `read("09-best-practices.md")`

## ⚠️ 关键注意事项

1. **不要一次读所有文件** — 按需读取，节省上下文
2. **不要跳过信息收集** — 缺少 app_id/open_id 后面全部会失败
3. **修改 openclaw.json 必须包含所有 Agent** — agents.list 是整体替换，遗漏 = 丢失
4. **创建群聊后必须注册** — 加 binding + groups 配置 + 重启 gateway
5. **Bot 创建的文档必须授权** — 否则用户看不到
