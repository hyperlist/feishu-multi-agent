---
name: git-workflow
description: |
  Git 工作流规范。管理分支、commit、PR 的标准流程。
  用户发送 /git 或涉及版本控制操作时触发。
---

# Git Workflow

## 触发

- `/git status` — 项目 git 状态摘要
- `/git save` — 自动 add + commit 当前改动
- 涉及 git 操作的自然语言请求

## 分支规范

```
main/master     ← 生产分支，禁止直推
feat/xxx        ← 功能开发
fix/xxx         ← Bug 修复
refactor/xxx    ← 重构
```

## Commit 规范

```bash
feat: 新功能描述
fix: 修复描述
refactor: 重构描述
docs: 文档更新
test: 测试相关
chore: 构建/工具链
```

- 一个功能点一个 commit
- 未 push 时善用 `git commit --amend`
- commit message 用英文，简洁明确

## /git status 输出

```bash
# 执行这些命令，汇总成简报
git branch --show-current
git log --oneline -5
git status --short
git stash list
```

输出格式：
```
📊 Git Status: {项目名}
分支: feat/xxx
最近提交:
  1. abc1234 feat: ...
  2. def5678 fix: ...
未提交改动: 3 files (2M, 1D)
```

## /git save 流程

```bash
git add -A
git diff --cached --stat  # 确认改动
git commit -m "feat: 自动生成的描述"
```

- 根据 diff 内容自动生成 commit message
- 不自动 push（需用户明确要求）

## PR 流程

```bash
git checkout -b feat/描述
# ... 开发 ...
git push origin feat/描述
gh pr create --title "feat: 描述" --body "..."
# 等用户确认后 merge
```

## 安全检查（push 前）

```bash
# 检查是否包含敏感信息
git diff --cached | grep -i "password\|secret\|api_key\|token" || echo "✅ 无敏感信息"
```
