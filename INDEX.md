# 飞书多 Agent 协作方案

基于 OpenClaw 的飞书多 Agent 系统设计与实现指南。

## 这是什么

一套完整的方案，让你用**飞书群聊**作为多个 AI Agent 的独立通信频道，实现：

- 🤖 **一个飞书 Bot → 多个独立 Agent**（每个群聊绑定一个 Agent）
- 📡 **Agent 间通信**（Agent A 可以给 Agent B 发消息、查状态）
- 📝 **飞书文档读写**（通过 API 创建/编辑飞书文档）
- 💬 **飞书群聊管理**（创建群、拉人、改名）
- 🎯 **DM 路由**（不同用户私信 Bot → 路由到不同 Agent）

## 适合谁

- 使用 OpenClaw 的开发者
- 想用飞书作为 AI Agent 交互界面的团队
- 需要多 Agent 协作系统的个人

## 目录结构

```
feishu-multi-agent/
├── README.md                     # 本文件
├── 01-architecture.md            # 整体架构设计
├── 02-feishu-setup.md            # 飞书应用配置
├── 03-agent-binding.md           # Agent 绑定与路由
├── 04-agent-communication.md     # Agent 间通信
├── 05-feishu-doc.md              # 飞书文档读写
├── 06-feishu-chat-management.md  # 飞书群聊管理
├── 07-feishu-message-format.md   # 飞书消息格式规范
├── 08-skill-organization.md      # Skill 目录组织
├── 09-best-practices.md          # 最佳实践与踩坑记录
├── 10-setup-wizard.md            # 配置引导（权限申请 + 自动创建功能 Agent）
├── 11-troubleshooting.md         # 故障排查指南
├── scripts/
│   └── create_agent.py           # 一键创建功能 Agent 脚本
├── examples/
│   ├── openclaw-config.json      # 示例配置（脱敏）
│   ├── agent-soul-template.md    # Agent SOUL.md 模板
│   └── agent-identity-template.md # Agent IDENTITY.md 模板
├── SKILL.md                      # OpenClaw Skill 入口（自动加载）
└── skills/
    ├── agent-comm/SKILL.md       # 跨 Agent 通信 Skill
    ├── feishu-chat/SKILL.md      # 飞书群聊管理 Skill
    ├── feishu-doc-writer/        # 飞书文档写作 Skill
    │   ├── SKILL.md
    │   └── references/
    │       ├── feishu-message-format.md
    │       └── perm-fallback.md
    └── delegate-agent/SKILL.md   # 任务委派 Skill（通用化版本）
```

## 快速开始

1. 阅读 [01-architecture.md](01-architecture.md) 了解整体设计
2. 按 [10-setup-wizard.md](10-setup-wizard.md) 的引导流程，收集信息、申请权限、创建 Agent
3. 或手动操作：[02-feishu-setup.md](02-feishu-setup.md) → [03-agent-binding.md](03-agent-binding.md)
4. 按需阅读其他章节

## 前置条件

- [OpenClaw](https://github.com/openclaw/openclaw) 已安装
- 飞书开放平台账号（个人版或企业版均可）
- macOS / Linux 环境
