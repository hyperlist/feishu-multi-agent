---
name: feishu-doc-writer
description: |
  Stable Feishu document writing skill with battle-tested patterns for creating well-structured documents.
  Activate when user asks to write content into a Feishu doc, create a report/article in Feishu, or generate structured Feishu documents with headings, lists, and formatted text.
  Handles known API pitfalls (block ordering, unsupported formats) automatically.
---

# Feishu Document Writer

Reliable patterns for writing structured Feishu documents via `feishu_doc` tool.

## Critical Constraints

1. **No markdown tables** — `feishu_doc` append/write returns 400 for markdown table syntax. Use bullet lists or key-value pairs instead.
2. **Incremental append for ordering** — Batch block creation randomizes order. Always append in small chunks (1-3 logical sections per call) to guarantee sequence.
3. **One heading + its content per append** — Keep each append as one heading plus its body. This ensures the heading always appears before its content.

## Writing Workflow

### New Document

```
1. feishu_doc action=create title="文档标题" [folder_token=xxx]
   → get doc_token from response
2. feishu_perm action=add token=<doc_token> type=docx member_id=<user_open_id> member_type=openid perm=full_access
   → 必须将用户加为管理员，否则用户无法访问机器人创建的文档
3. For each section:
     feishu_doc action=append doc_token=xxx content="## Section Title\n\nSection body..."
```

### Append to Existing Document

```
1. feishu_doc action=read doc_token=xxx  → verify current content
2. For each section to add:
     feishu_doc action=append doc_token=xxx content="..."
```

### Replace Entire Document

```
feishu_doc action=write doc_token=xxx content="# Title\n\nFull markdown content"
```

⚠️ Single write call is fine for full replacement — ordering is preserved within one call's content. The ordering issue only affects multiple sequential block-creation calls.

## Formatting Rules

### Supported
- `#` / `##` / `###` headings
- `**bold**`, `*italic*`, `~~strikethrough~~`
- Bullet lists (`- item`) and numbered lists (`1. item`)
- Code blocks (triple backtick)
- Blockquotes (`>`)
- Links `[text](url)`
- Images `![alt](url)` — auto-uploaded to Feishu

### Not Supported
- Markdown tables (`| col | col |` → returns 400)
- HTML tags

### Table Alternatives

Instead of markdown tables, use these patterns:

**Key-value style:**
```markdown
- **股票**: 特变电工(sh600089)
- **买入价**: 29.85 元
- **当前价**: 30.58 元
- **浮盈**: +2.46%
```

**Structured list style:**
```markdown
**模型 A — Apple**
- 执行时间: 10 分钟
- Token 消耗: 46,817
- 评价: 报告质量最高

**模型 B — Lemon**
- 执行时间: 5 分钟
- Token 消耗: 37,228
- 评价: 成本效率最优
```

## Append Chunking Strategy

For a document with N sections, append N times (one per section):

```
# Bad — all sections in one append (may work but risky for large docs)
feishu_doc append content="## S1\n...\n## S2\n...\n## S3\n..."

# Good — one section per append (guaranteed order)
feishu_doc append content="## S1\nContent for section 1..."
feishu_doc append content="## S2\nContent for section 2..."
feishu_doc append content="## S3\nContent for section 3..."
```

For very short sections (a heading + 1-2 lines), combining 2-3 is safe. For longer sections (10+ lines each), always one per append.

## 文档结构规范（Battle-tested）

以下结构模式经过实战验证，产出的文档质量高、可读性好。

### 报告类文档模板

适用于：测试报告、对比分析、技术评估等。

**标准章节结构：**
1. **背景/场景** — 为什么做、怎么做、测什么
2. **结果总览** — 每个被测对象的核心结论（用结构化列表，不用表格）
3. **问题原始上下文** — 有问题的对象单独展开，包含现象描述、原始输出样例、因果链分析
4. **最终结论/决定** — 一句话结论 + 推荐排序

### 内容写作原则

1. **每个章节自包含** — 读者跳到任何一章都能理解，不依赖上下文
2. **结论前置** — 每个被测对象先给结论（✅/❌），再展开细节
3. **原始证据必须附** — 问题描述必须包含原始输出样例（用代码块），不能只写"出了问题"
4. **因果链要完整** — 不只描述现象，要分析 现象 → 原因 → 影响 → 结论
5. **用列表代替表格** — 飞书不支持 markdown 表格，用加粗标题 + 缩进列表替代

### 结构化列表风格（替代表格）

```markdown
**Apple — ✅ 9/9 通过**
- 完成度：9/9
- 输出质量：⭐⭐⭐⭐⭐
- 特点：一次通过，输出简洁结构化，工具调用精准无冗余
- 结论：稳定可靠，所有类型编码任务均适用

**Orange — ❌ 失败**
- 完成度：0/9
- 输出质量：无法产出有效结果
- 问题：文本无限循环 + tool call 泄漏进 thinking block
- 结论：多步工具调用场景存在结构性缺陷
```

### 问题分析章节模板

每个问题按以下结构展开：

```markdown
### 问题 N：[问题名称]

**频率：** 高/中/低

**现象描述：** 一段话说清楚发生了什么。

**原始输出样例：**
（代码块，贴真实输出片段）

**影响：** 这个问题导致了什么后果。

**因果链：**（如果涉及多步因果）
1. 步骤 A 发生
2. 导致步骤 B
3. 最终结果 C
```

### 补充测试/修正结论

如果后续有补充测试，新增章节而非修改原文：

```markdown
## N+1. 补充测试：[说明]（时间）

[测试结果]

### 结论修正
[基于新数据修正之前的结论]
```

这样保留了完整的测试时间线，读者能看到认知演进过程。

## Permissions

机器人创建的文档默认只有机器人自己能访问。**每次创建新文档后必须立即将用户加为管理员**，否则用户打不开。

```
feishu_perm action=add token=<doc_token> type=docx member_id=<user_open_id> member_type=openid perm=full_access
```

`feishu_perm` 工具已在 config 中启用（`channels.feishu.tools.perm: true`），可直接调用。

如果工具不可用，使用 curl fallback，见 `references/perm-fallback.md`。

## 飞书消息格式参考

详见 `references/feishu-message-format.md`，包含飞书消息支持的完整 Markdown 语法列表、不支持的格式、特殊字符转义、数学公式处理最佳实践。

所有 agent 在生成飞书消息内容时都应参考此文件。

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 400 on append/write | Markdown tables in content | Replace tables with bullet lists |
| Blocks appear out of order | Too many blocks in one append | Split into smaller appends |
| 403 on doc operations | Missing doc permissions | Check app has `docx:document` scope |
| Empty read result | Doc is a wiki page | Use `feishu_wiki get` first to get the real doc_token |
