---
name: project-switcher
description: |
  多项目管理和目录切换。用户发送 /repo 时列出项目，选择后切换工作目录。
  适用于 coder agent 同时维护多个代码仓库的场景。
---

# Project Switcher

## 触发

- `/repo` — 列出所有注册的项目
- `/repo <名称或编号>` — 切换到指定项目

## 工作流程

1. 读取 `config/projects.json` 获取项目列表
2. 用户选择后，记录当前项目到 `.current_project`
3. 后续所有文件操作在该项目目录下执行

## 配置

编辑 `config/projects.json` 注册项目：

```json
{
  "projects": [
    {
      "name": "my-app",
      "path": "/path/to/my-app",
      "description": "主项目",
      "language": "Python",
      "git": "git@github.com:user/my-app.git"
    }
  ]
}
```

## 脚本

- `scripts/list_projects.py` — 列出项目
- `scripts/switch_project.py` — 切换项目 + 记录历史

## 注意

- 切换项目后建议开启新 session（避免上下文混淆）
- 无配置文件时自动扫描 workspace 子目录
