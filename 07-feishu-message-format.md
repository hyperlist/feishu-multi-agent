# 飞书消息支持的格式参考

> 来源：飞书开放平台官方文档（2025-04-08 更新）

## 飞书消息 Markdown 支持的语法

### 文本格式
- **加粗**：`**粗体**` 或 `__粗体__`
- *斜体*：`*斜体*`
- ~~删除线~~：`~~删除线~~`
- 换行：`\n`

### 彩色文本
```
<font color='red'>红色文本</font>
<font color='green'>绿色文本</font>
<font color='grey'>灰色文本</font>
```
支持的 color 值：red、green、grey、default，以及颜色枚举值。

### 链接
- 文字链接：`[显示文本](https://url)`
- 超链接：`<a href='https://url'></a>`

### 列表（飞书 7.6+）
```
- 无序列表1
    - 子项（4 空格缩进）
- 无序列表2

1. 有序列表1
    1. 子项（4 空格缩进）
2. 有序列表2
```

### 代码块（飞书 7.6+）
````
```python
def hello():
    print("Hello!")
```
````
支持语言高亮：python、json、go、javascript、typescript、sql、bash、cpp 等。

### 其他
- 分割线：`---`（需单独一行）
- 图片：`![hover_text](image_key)`
- 飞书表情：`:OK:` `:THUMBSUP:` `:DONE:` 等
- 标签：`<text_tag color='blue'>标签文本</text_tag>`
- @用户：`<at id=open_id></at>`
- @所有人：`<at id=all></at>`

## 不支持的格式

- ❌ LaTeX 数学公式（`$...$`、`\frac{}{}`）
- ❌ Markdown 表格（`| col | col |`）— 飞书文档 API 返回 400
- ❌ HTML 标签（除飞书专有标签外）
- ❌ Unicode 数学符号（∑、∫、√、∈ 等可能显示异常）
- ❌ 上标/下标 Unicode（x₁、x² 等部分设备无法显示）

## 特殊字符转义

如果文本包含 Markdown 特殊字符，需要 HTML 转义：

- `*` → `&#42;`
- `~` → `&sim;`
- `>` → `&#62;`
- `<` → `&#60;`
- `[` → `&#91;`
- `]` → `&#93;`
- `` ` `` → `&#96;`

## 数学公式最佳实践

飞书不支持 LaTeX，数学内容推荐这样处理：

**简单公式** — 用文本 + 加粗：
```
**期望** E(X) = x1*P(x1) + x2*P(x2) + ... + xn*P(xn)
```

**复杂公式** — 用代码块：
````
```
E(X)   = sum_{i=1}^{n} x_i * P(x_i)
Var(X) = E(X^2) - [E(X)]^2
P(A|B) = P(B|A) * P(A) / P(B)
```
````

**重点标记** — 用彩色文本：
```
<font color='red'>核心公式：P(A|B) = P(B|A) * P(A) / P(B)</font>
```
