---
name: feishu-doc-writer
description: |
  Feishu document writing skill. Handles known API pitfalls (block ordering, unsupported formats).
  Activate when writing content into Feishu docs or creating structured documents.
---

# Feishu Document Writer

## ⭐ 推荐：MD 导入 API（长文档首选）

飞书原生 MD 解析，**支持表格**，无 block 乱序。

**流程：** 本地写 .md → 上传素材 → 创建导入任务 → 轮询结果 → 加权限

```python
# Step 1: 上传
POST /drive/v1/medias/upload_all  → file_token

# Step 2: 导入
POST /drive/v1/import_tasks
  body: { file_extension: "md", file_token, type: "docx",
          file_name: "标题", point: {mount_type: 1, mount_key: ""} }
  → ticket

# Step 3: 轮询
GET /drive/v1/import_tasks/{ticket}  → doc_token, url

# Step 4: 加权限
POST /drive/v1/permissions/{doc_token}/members?type=docx
  body: { member_type: "openid", member_id: "ou_xxx", perm: "full_access" }
```

完整 Python 脚本：[references/md-import.py](references/md-import.py)

```bash
# 用法
python3 references/md-import.py report.md "报告标题"
# 或设置环境变量
FEISHU_APP_ID=cli_xxx FEISHU_APP_SECRET=xxx python3 references/md-import.py report.md "标题"
```

## 备选：feishu_doc 工具（短文档/追加）

### 约束
- **无 Markdown 表格**（返回 400）— 用列表替代
- **逐章节 append** — 每次 1 个 heading + 内容，保证顺序
- **创建后必须加权限** — Bot 创建的文档默认只有 Bot 能看

### 工作流
```
1. feishu_doc create → doc_token
2. feishu_perm add → 授权用户
3. feishu_doc append × N → 逐章节写入
```

### 表格替代方案
```markdown
**模型 A — ✅ 通过**
- Token 消耗: 46,817
- 评价: 稳定可靠
```

## 方案选择

| 场景 | 方案 |
|------|------|
| 长文档 / 含表格 / 严格顺序 | ⭐ MD 导入 |
| 短文档 / 追加 / 修改已有文档 | feishu_doc |
| 替换整篇 | feishu_doc write（单次调用无乱序） |

## 报告类文档结构

1. **背景** — 为什么做、测什么
2. **结果总览** — 结论前置（✅/❌），每个对象核心数据
3. **问题详析** — 现象 + 原始证据（代码块）+ 因果链
4. **最终结论** — 一句话 + 建议

**原则：** 章节自包含、结论前置、必须附原始证据、因果链完整。

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 400 on append | Markdown 表格 | 用 MD 导入或列表替代 |
| Block 乱序 | 多次 append | 用 MD 导入 |
| 403 | 权限不足 | 检查 `docx:document` scope |
| 99992402 on import | 缺 point 字段 | 加 `point: {mount_type:1, mount_key:""}` |

详细消息格式规范见 `references/feishu-message-format.md`。
