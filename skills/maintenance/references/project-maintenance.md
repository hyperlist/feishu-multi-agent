# 项目自身更新指南

> 本文档指导如何维护和更新 feishu-multi-agent 项目本身。
> **核心原则**：确保所有模型（AI Agent）在维护项目时表现一致，用代码代替模糊指令。

## 更新原则

### 1. 强制脱敏 🔒

**所有提交（commit）前必须完成脱敏检查**，禁止包含：

- ❌ 个人身份信息（姓名、open_id、user_id）
- ❌ 敏感路径（`/Users/真实用户名/`、`/home/真实用户名/`）
- ❌ TOKEN / API Key / Secret（即使是示例也要用占位符）
- ❌ 内部群聊 ID（oc_xxx）
- ❌ 服务器 IP、内网域名

**脱敏检查脚本**（必须运行）：
```bash
# 提交前自动检查
python3 scripts/check_sensitive.py

# 手动扫描
python3 scripts/check_sensitive.py --path . --strict
```

**脱敏示例**：
```python
# ❌ 错误
"workspace": "/Users/username/.openclaw/workspace-coder"
"appSecret": "cli_xxxxxxxxxxxxxxxx"
"chat_id": "oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ✅ 正确
"workspace": "/path/to/.openclaw/workspace-coder"
"appSecret": "__OPENCLAW_REDACTED__"
"chat_id": "oc_xxxxxxxxxxxxxxxx"
```

### 2. 一致性优先

所有文档、脚本、示例必须遵循统一规范，避免不同模型产生不同理解：

- **使用明确路径**：不要用"examples目录"，用 `examples/`
- **使用明确命令**：不要用"运行脚本"，用 `python3 scripts/create_agent.py ...`
- **使用确定性格式**：JSON 字段必须完整，不要省略可选字段

### 2. 代码优于自然语言

当指令可能产生歧义时，优先使用代码/脚本：

| 模糊指令 ❌ | 明确代码 ✅ |
|------------|-----------|
| "添加到 agents.list" | `config['agents']['list'].append({"id": "xxx", ...})` |
| "更新群聊配置" | `config['channels']['feishu']['groups'][chat_id] = {"enabled": True}` |
| "修改模型配置" | 见下方 Python 脚本 |

### 3. 可验证性

所有更新必须通过自动化检查：

```bash
# 更新后运行验证
python3 scripts/validate_config.py
```

## 更新类型与流程

### 类型 A：添加新 Agent 示例

**场景**：新增一个预设角色（如 designer、researcher）

**步骤**：

1. **创建示例目录**（使用脚本，不手动）
   ```bash
   python3 scripts/add_agent_example.py \
     --agent-id designer \
     --agent-name "Designer" \
     --category examples
   ```

2. **编辑模板文件**（使用 edit 工具，不手动写）
   - `examples/designer-agent/SOUL.md` — 角色定义
   - `examples/designer-agent/AGENTS.md` — 职责说明
   - `examples/designer-agent/TOOLS.md` — 环境模板
   - `examples/designer-agent/README.md` — 使用说明

3. **更新索引**（必须自动化）
   ```python
   # scripts/update_index.py
   import re

   def add_to_index(agent_id, agent_name):
       with open('INDEX.md', 'r') as f:
           content = f.read()
       
       # 找到 examples/ 部分，插入新行
       pattern = r'(examples/\n)(.*?)(skills/)'
       new_entry = f"├── examples/{agent_id}-agent/          # {agent_name} 示例\n"
       content = re.sub(pattern, r'\1' + new_entry + r'\3', content)
       
       with open('INDEX.md', 'w') as f:
           f.write(content)
   ```

4. **更新预设列表**（修改 PRESETS 常量）
   ```python
   # scripts/create_agent.py
   PRESETS["designer"] = {
       "tools": ["read", "write", "message", "web_search"],
       "soul_core": "你是一位资深设计师...",
       "soul_principles": [...]
   }
   ```

5. **运行验证**
   ```bash
   python3 scripts/validate_examples.py --check-designer
   ```

### 类型 B：修改配置格式

**场景**：openclaw.json 结构变更

**步骤**：

1. **编写迁移脚本**（强制）
   ```python
   # scripts/migrate_config_v2.py
   import json
   from pathlib import Path

   def migrate_v1_to_v2(config_path: Path):
       with open(config_path) as f:
           config = json.load(f)
       
       # 版本检查
       if config.get('version', '1.0').startswith('2.'):
           return  # 已是最新
       
       # 执行迁移
       for agent in config['agents']['list']:
           if 'tools' in agent and isinstance(agent['tools'], list):
               # v1: tools 是列表 → v2: tools 是对象
               agent['tools'] = {'allow': agent['tools']}
       
       config['version'] = '2.0'
       
       # 备份 + 写入
       backup_path = config_path.with_suffix('.json.v1.bak')
       config_path.rename(backup_path)
       with open(config_path, 'w') as f:
           json.dump(config, f, indent=2)
       
       print(f"✅ 迁移完成: {config_path}")
       print(f"📦 备份位置: {backup_path}")
   ```

2. **更新文档中的示例配置**
   ```bash
   python3 scripts/sync_examples.py
   ```

3. **版本标记**
   ```bash
   git tag -a v2.0 -m "配置格式 v2.0: tools 字段结构调整"
   ```

### 类型 C：更新文档内容

**场景**：修正文档错误、更新说明

**步骤**：

1. **定位所有相关位置**
   ```bash
   grep -r "旧内容" --include="*.md" .
   ```

2. **批量替换**（使用脚本，不手动）
   ```python
   # scripts/replace_in_docs.py
   import re
   from pathlib import Path

   def replace_in_docs(old: str, new: str):
       for md_file in Path('.').rglob('*.md'):
           content = md_file.read_text()
           if old in content:
               content = content.replace(old, new)
               md_file.write_text(content)
               print(f"✅ {md_file}")
   ```

3. **验证一致性**
   ```bash
   python3 scripts/check_consistency.py
   ```

## 自动化脚本规范

所有脚本必须：

1. **有明确的输入输出**
   ```python
   def main(agent_id: str, workspace_base: Path) -> Path:
       """返回创建的 workspace 路径"""
       ...
   ```

2. **有幂等性**（多次运行结果一致）
   ```python
   # 检查是否存在，避免重复创建
   if workspace.exists():
       print(f"⚠️ {workspace} 已存在，跳过")
       return workspace
   ```

3. **有详细日志**
   ```python
   print(f"✅ 创建: {file_path}")
   print(f"⚠️ 跳过: {file_path} (已存在)")
   print(f"❌ 失败: {reason}")
   ```

4. **有验证步骤**
   ```python
   assert workspace.exists(), f"Workspace 创建失败"
   assert (workspace / "SOUL.md").exists(), "SOUL.md 缺失"
   ```

## 模型一致性保障

为确保不同 AI 模型更新项目时表现一致：

### 1. 强制使用脚本

文档中必须明确：

> **不要手动操作**，使用脚本：
> ```bash
> python3 scripts/xxx.py --param value
> ```

### 2. 提供完整代码示例

不要描述"怎么改"，直接给代码：

```python
# 正确做法 ✅
with open('openclaw.json') as f:
    config = json.load(f)
config['agents']['list'].append({
    "id": "new_agent",
    "name": "New Agent",
    "workspace": "/path/to/workspace-new_agent"
})
with open('openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

# 错误做法 ❌
# "在 agents.list 里添加新 agent"
```

### 3. 约定式提交

所有变更必须使用约定式提交格式：

```bash
# Agent 相关
git commit -m "feat(agent): 添加 designer 预设"
git commit -m "fix(coder): 修正 SOUL.md 中的路径描述"

# 脚本相关
git commit -m "feat(script): 添加 validate_config.py"
git commit -m "fix(script): 修复 migrate_config_v2 的备份逻辑"

# 文档相关
git commit -m "docs: 更新 10-setup-wizard.md 中的重启说明"
git commit -m "docs(contributing): 添加自身更新指南"
```

## 更新 Checklist

任何更新必须完成以下检查：

```markdown
- [ ] 脚本可执行且幂等
- [ ] 文档已同步更新
- [ ] 示例配置已同步
- [ ] 索引已更新（INDEX.md）
- [ ] 验证脚本通过
- [ ] Git 提交符合规范
- [ ] 无敏感信息泄露
```

## 脚本清单

| 脚本 | 用途 | 调用方式 |
|------|------|---------|
| `create_agent.py` | 创建子 Agent | `python3 scripts/create_agent.py --agent-id xxx ...` |
| `add_agent_example.py` | 添加示例 Agent | `python3 scripts/add_agent_example.py --agent-id xxx` |
| `migrate_config_v2.py` | 配置格式迁移 | `python3 scripts/migrate_config_v2.py --config path` |
| `validate_config.py` | 验证配置完整性 | `python3 scripts/validate_config.py` |
| `validate_examples.py` | 验证示例完整性 | `python3 scripts/validate_examples.py` |
| `sync_examples.py` | 同步示例配置 | `python3 scripts/sync_examples.py` |
| `replace_in_docs.py` | 批量替换文档内容 | `python3 scripts/replace_in_docs.py --old "x" --new "y"` |
| `check_consistency.py` | 检查文档一致性 | `python3 scripts/check_consistency.py` |

---

**维护者注意**：更新本文档时，遵循本文档自身的规范。
