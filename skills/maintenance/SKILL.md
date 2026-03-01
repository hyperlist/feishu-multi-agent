# Maintenance Skill

飞书多 Agent 项目维护指南 - 仅供维护 feishu-multi-agent 项目时使用。

## 用途

本文档指导如何维护和更新 feishu-multi-agent 开源项目本身。

**何时使用此 skill**：
- 添加新 Agent 示例到项目
- 修改项目配置格式
- 更新项目文档
- 发布新版本

**何时不使用**：普通用户部署多 Agent 系统时不需要阅读此文档。

## 核心原则

1. **强制脱敏** - 所有提交必须脱敏，禁止含个人信息/TOKEN
2. **一致性优先** - 用代码代替模糊指令
3. **可验证性** - 所有更新必须通过自动化检查

## 参考文档

- [项目维护指南](./references/project-maintenance.md)

## 快速命令

```bash
# 提交前脱敏检查
python3 scripts/check_sensitive.py

# 验证配置
python3 scripts/validate_config.py

# 创建新 Agent 示例
python3 scripts/create_agent.py --agent-id xxx --preset coder
```
