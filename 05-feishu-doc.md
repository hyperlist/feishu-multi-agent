# 05 - 飞书文档读写

## 概述

OpenClaw 内置 `feishu_doc` 工具，可以创建、读取、编辑飞书文档。适合 Agent 自动生成报告、记录分析结果等。

## 工具 API

### 创建文档

```
feishu_doc(action="create", title="文档标题", folder_token="可选的目标文件夹")
```

返回 `doc_token`，后续操作都需要它。

### 读取文档

```
feishu_doc(action="read", doc_token="xxx")
```

### 追加内容

```
feishu_doc(action="append", doc_token="xxx", content="## 标题\n\n正文内容...")
```

### 覆盖写入

```
feishu_doc(action="write", doc_token="xxx", content="完整的新内容...")
```

## ⚠️ 关键坑点

### 1. 不支持 Markdown 表格

飞书 API **不支持 Markdown 表格语法**，会返回 400 错误。

```markdown
❌ 错误写法：
| 列1 | 列2 |
|-----|-----|
| a   | b   |

✅ 正确写法（用列表替代）：
- **列1:** a | **列2:** b
- **列1:** c | **列2:** d
```

### 2. 批量追加顺序随机

一次 append 包含多个 block 时，**顺序可能被打乱**。

```
❌ 错误：一次 append 5 个 section
✅ 正确：每次 append 1 个 section（标题+正文），保证顺序
```

### 3. 权限问题

Bot 创建的文档**只有 Bot 自己能看到**。必须手动授权：

```
feishu_perm(action="add", token="doc_token", type="docx",
            member_id="用户open_id", member_type="openid", perm="full_access")
```

### 4. 权限回退

如果 `feishu_perm` 返回权限错误（如 `lark_perm_not_allow_edit_meta`），
尝试降级权限：`full_access` → `edit` → `view`。

## 文档写作 Workflow

```
1. feishu_doc(action="create", title="报告标题")
   → 获取 doc_token

2. feishu_perm(action="add", token=doc_token, type="docx",
               member_id="用户open_id", member_type="openid", perm="full_access")
   → 授予用户权限

3. 逐节追加内容：
   feishu_doc(action="append", doc_token=doc_token, content="## 第一节\n\n内容...")
   feishu_doc(action="append", doc_token=doc_token, content="## 第二节\n\n内容...")
   feishu_doc(action="append", doc_token=doc_token, content="## 第三节\n\n内容...")

4. 返回文档链接给用户
```

## 报告文档模板

推荐的报告结构（结论先行）：

```markdown
## 1. 背景
简述项目背景、动机

## 2. 结论概述
最终结论放最前面，一眼能看到

## 3. 详细分析
### 3.1 方案A
- 优点
- 缺点
- 原始证据/截图

### 3.2 方案B
...

## 4. 最终建议
具体操作建议
```

### 写作原则

1. **结论先行** — 核心结论放第二节，不要让读者翻到最后才知道结果
2. **原始证据必须** — 每个结论必须附带原始输出/数据支撑
3. **完整因果链** — 问题→原因→证据→影响→结论，缺一不可
4. **列表替代表格** — 飞书 API 不支持表格，用结构化列表代替

## 消息格式规范

飞书消息中支持的富文本格式：

### ✅ 支持的格式
- `**粗体**` → **粗体**
- `*斜体*` → *斜体*
- `` `代码` `` → `代码`
- `~~删除线~~` → ~~删除线~~
- `[链接](url)` → 链接
- `> 引用`
- 无序列表（`-`）和有序列表（`1.`）
- 代码块（``` ）

### ❌ 不支持的格式
- LaTeX 数学公式（`$...$`、`\frac{}{}`）
- Markdown 表格
- Unicode 数学符号（∑、∫、√）
- HTML 标签

数学公式替代方案：
```
❌ $f(x) = \frac{1}{n}\sum_{i=1}^{n}x_i$
✅ **f(x) = (1/n) × Σ(xi)**, i 从 1 到 n
```
