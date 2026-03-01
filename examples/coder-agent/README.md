# Coder Agent - 开发助手

飞书多 Agent 系统中的 **Coder** 角色模板。

## 用途

专门负责代码开发、代码审查、架构设计和技术方案支持的 Agent。

## 核心能力

- **代码开发** — 接收需求后直接写代码交付
- **代码审查** — Review 代码质量、找 bug、提改进建议
- **架构设计** — 模块划分、接口设计、重构方案
- **Bug 排查** — 读日志、复现问题、定位修复
- **测试验证** — 写完跑测试，确保功能可用

## 文件说明

| 文件 | 用途 |
|------|------|
| `SOUL.md` | Agent 的核心行为定义、开发规范、代码风格 |
| `AGENTS.md` | 职责说明、工具权限、工作流程 |
| `TOOLS.md` | 环境特有信息（路径、仓库、群聊等），需根据实际部署填写 |

## 部署步骤

1. 复制本目录到目标 workspace：`cp -r examples/coder-agent /path/to/your/workspace-coder/`
2. 编辑 `TOOLS.md`，填入实际的：
   - 工作目录路径
   - 代码仓库信息
   - 飞书群聊 ID
3. 在 `openclaw.json` 中添加 agent 配置（参考 `03-agent-binding.md`）
4. 重启 Gateway：`openclaw gateway restart`

## 使用示例

用户在群聊中 @Coder：

> @Coder 帮我写一个 Python 脚本，读取 CSV 文件并统计每列的空值数量

Coder 会：
1. 确认需求（如有不清楚的地方会提问）
2. 在工作区创建脚本文件
3. 运行测试验证
4. 在群聊中回复结果

## 权限建议

```json
{
  "tools": {
    "allow": [
      "exec",
      "read",
      "write",
      "edit",
      "message",
      "web_search",
      "web_fetch",
      "session_status",
      "feishu_doc",
      "feishu_perm"
    ]
  }
}
```

## 与其他 Agent 协作

- 接收 **Main** 指派的开发任务
- 为 **Scout** 提供技术实现支持
- 协助 **Trader** 开发量化策略
- 为 **Tutor** 准备技术教程代码
