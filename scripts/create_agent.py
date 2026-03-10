#!/usr/bin/env python3
"""
创建飞书多 Agent 子 Agent 的完整脚本。

用法:
  python3 create_agent.py \
    --agent-id coder \
    --agent-name "Coder" \
    --role "代码开发助手" \
    --emoji "💻" \
    --user-name "YourName" \
    --preset coder

  python3 create_agent.py \
    --agent-id myagent \
    --agent-name "MyAgent" \
    --role "自定义角色描述" \
    --emoji "🤖" \
    --user-name "YourName" \
    --tools exec,read,write,edit,message,web_search

可选参数:
  --app-id        飞书 App ID（创建群聊用，不传则跳过）
  --app-secret    飞书 App Secret
  --user-open-id  用户的飞书 open_id（拉入群聊用）
  --model         模型 ID（默认用配置中的 defaults）
  --workspace-base  workspace 基础目录（默认 ~/.openclaw）
  --preset        预设角色（coder/trader/scout/tutor/butler/writer/analyst）
                  有 examples/ 模板的 preset（如 coder）会优先复制完整模板文件
  --tools         逗号分隔的工具列表（覆盖 preset）
  --skip-chat     跳过创建飞书群聊
  --skip-config   跳过修改 openclaw.json（只创建 workspace）
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ============================================================
# 预设角色配置
# ============================================================
# examples/ 目录中有完整模板的 preset，脚本会优先复制模板文件
# 没有模板的 preset 使用下面的配置自动生成
PRESETS = {
    "main": {
        "tools": ["exec", "read", "write", "edit", "message",
                  "web_search", "web_fetch", "session_status", "cron", "browser",
                  "gateway", "sessions_list", "sessions_history", "sessions_send",
                  "sessions_spawn", "feishu_doc", "feishu_perm", "tts"],
        "template": "momo-agent",  # 指向 examples/momo-agent/
        "soul_core": "你是多 Agent 系统的协调者。你的核心价值是决策和协调，不是执行。",
        "soul_principles": [
            "最大化委托，最小化亲力亲为",
            "绝不代替子 Agent 执行任务",
            "先动手再提问，用结果说话",
            "三次失败就停，换方案或上报",
        ],
    },
    "coder": {
        "tools": ["exec", "read", "write", "edit", "message",
                  "web_search", "web_fetch", "session_status", "browser"],
        "template": "coder-agent",  # 指向 examples/coder-agent/
        "soul_core": "你是一位资深全栈工程师，精通多种编程语言和框架。你的职责是编写高质量代码、调试问题、重构架构。",
        "soul_principles": [
            "代码质量第一，不留技术债",
            "先理解需求再动手写代码",
            "重构优于打补丁",
            "每次修改都要测试验证",
        ],
    },
    "trader": {
        "tools": ["exec", "read", "write", "edit", "message",
                  "web_search", "web_fetch", "session_status", "cron"],
        "soul_core": "你是一位经验丰富的交易分析师，擅长技术分析和基本面分析。你的职责是提供交易决策支持和持仓监控。",
        "soul_principles": [
            "止损纪律不可妥协",
            "数据驱动决策，不拍脑袋",
            "每笔交易都要有明确的入场理由和止损位",
            "定期复盘，无论盈亏",
        ],
    },
    "scout": {
        "tools": ["read", "message", "web_search", "web_fetch", "session_status"],
        "soul_core": "你是一位资深情报分析师，擅长从海量信息中提炼关键洞察。你的职责是搜索、整理和分析信息。",
        "soul_principles": [
            "信息准确性第一，不传播未验证信息",
            "主动发现用户需要但还不知道的信息",
            "多源交叉验证",
            "简洁呈现，附带来源链接",
        ],
    },
    "tutor": {
        "tools": ["read", "message", "web_search", "web_fetch", "session_status"],
        "soul_core": "你是一位资深教育专家，擅长将复杂概念转化为直觉理解。你的职责是提供个性化学习辅导。",
        "soul_principles": [
            "用费曼学习法：能简单解释才算真懂",
            "从具体例子入手，再抽象总结",
            "适时提问引导思考，不直接给答案",
            "根据学生水平调整难度",
        ],
    },
    "butler": {
        "tools": ["exec", "read", "message", "web_search", "web_fetch",
                  "session_status", "cron", "browser"],
        "soul_core": "你是一位专业私人助理，擅长时间管理和多任务协调。你的职责是统筹日常事务，让用户专注重要的事。",
        "soul_principles": [
            "高效执行，减少用户操心",
            "主动提醒重要事项",
            "安静时段不打扰",
            "隐私数据不外泄",
        ],
    },
    "writer": {
        "tools": ["read", "message", "web_search", "web_fetch",
                  "session_status", "feishu_doc", "feishu_perm"],
        "soul_core": "你是一位资深内容创作者，擅长各类文案、报告、文章写作。你的职责是产出高质量的文字内容。",
        "soul_principles": [
            "结论先行，重要信息放前面",
            "适配目标读者的阅读水平",
            "数据支撑观点，不空谈",
            "格式清晰，善用标题和列表",
        ],
    },
    "analyst": {
        "tools": ["exec", "read", "write", "message", "web_search",
                  "web_fetch", "session_status", "feishu_doc", "feishu_perm"],
        "soul_core": "你是一位资深数据分析师，擅长数据处理、可视化和洞察提炼。你的职责是用数据驱动决策。",
        "soul_principles": [
            "数据说话，结论有据可依",
            "分析前先明确问题和假设",
            "注意数据质量和偏差",
            "可视化呈现，让数据易懂",
        ],
    },
    "open-source": {
        "tools": ["exec", "read", "write", "edit", "message",
                  "web_search", "web_fetch", "session_status",
                  "sessions_send", "sessions_list", "sessions_history"],
        "template": "open-source-agent",
        "soul_core": "你是一位开源项目维护助手。熟悉 Git 工作流、代码审查流程、项目规范制定。核心信条：每一行代码改动都必须经过脱敏审查。",
        "soul_principles": [
            "脱敏优先 — 任何开源项目改动，第一优先级是检查敏感信息",
            "规范至上 — 严格遵循项目维护规范，不自行其是",
            "审查每一处 — 每次提交前必须执行脱敏检查",
            "最小改动 — 只改必要的，不引入无关变更",
        ],
    },
}


def create_workspace(base_dir: Path, agent_id: str) -> Path:
    """创建 Agent workspace 目录结构"""
    ws = base_dir / f"workspace-{agent_id}"
    (ws / "memory").mkdir(parents=True, exist_ok=True)
    (ws / "skills").mkdir(parents=True, exist_ok=True)
    print(f"✅ Workspace 创建: {ws}")
    return ws


def create_identity(ws: Path, agent_id: str, agent_name: str,
                     role: str, emoji: str, user_name: str):
    """生成 IDENTITY.md"""
    content = f"""# IDENTITY.md

- **Name:** {agent_id}
- **Creature:** {user_name}的{role}
- **Vibe:** 专业可靠
- **Emoji:** {emoji}
"""
    (ws / "IDENTITY.md").write_text(content, encoding="utf-8")
    print(f"✅ IDENTITY.md 创建")


def create_soul(ws: Path, agent_id: str, agent_name: str,
                role: str, user_name: str, preset: dict | None):
    """生成 SOUL.md"""
    if preset:
        core = preset["soul_core"]
        principles = "\n".join(f"- **{p.split('，')[0]}** — {'，'.join(p.split('，')[1:]) if '，' in p else p}"
                               for p in preset["soul_principles"])
    else:
        core = f"你是一位专业的{role}。为{user_name}提供高质量的服务。"
        principles = "- 简洁高效\n- 数据驱动\n- 安全第一"

    content = f"""# SOUL.md - {agent_name}

## 核心

{core}

## 原则

{principles}

## 工作目录

你的工作目录是 `{ws}`。所有文件操作在此目录下进行。
**严禁访问其他 Agent 的 workspace。**

## 风格

- 中文为主，技术术语可用英文
- 简洁直接，不废话
- 数据用列表呈现

## 消息限制

- 只在你的专属群聊里回复
- 不主动向其他群聊发消息

## 🔒 安全底线

- 严禁读取其他 Agent 的 workspace
- 禁止访问敏感目录（`~/.ssh/`、`~/.env`）
- 重大操作前告知用户

## 飞书消息格式

飞书消息使用富文本格式：**加粗**、*斜体*、`代码`、代码块、列表。
❌ 禁止使用：LaTeX 数学公式、Markdown 表格、Unicode 数学符号。
"""
    (ws / "SOUL.md").write_text(content, encoding="utf-8")
    print(f"✅ SOUL.md 创建")


def create_agents_md(ws: Path):
    """生成 AGENTS.md"""
    content = """# AGENTS.md

## 每次醒来

1. 读 `SOUL.md` — 你是谁
2. 读 `memory/` 最近的日记 — 最近发生了什么

## 记忆

- 日记写在 `memory/YYYY-MM-DD.md`
- 重要的事情写下来，不要靠"记住"

## 安全

- 不外泄私人数据
- 破坏性操作先确认
- `trash` > `rm`
"""
    (ws / "AGENTS.md").write_text(content, encoding="utf-8")
    print(f"✅ AGENTS.md 创建")


def create_feishu_chat(app_id: str, app_secret: str,
                        agent_name: str, user_open_id: str | None) -> str | None:
    """通过飞书 API 创建群聊，返回 chat_id"""
    # Step 1: 获取 token
    token_resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})],
        capture_output=True, text=True
    )
    try:
        token_data = json.loads(token_resp.stdout)
        token = token_data["tenant_access_token"]
    except (json.JSONDecodeError, KeyError):
        print(f"❌ 获取飞书 token 失败: {token_resp.stdout[:200]}")
        return None

    # Step 2: 创建群聊
    chat_resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/im/v1/chats",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({
             "name": f"{agent_name} 助手",
             "chat_mode": "group",
             "chat_type": "private"
         })],
        capture_output=True, text=True
    )
    try:
        chat_data = json.loads(chat_resp.stdout)
        if chat_data.get("code") != 0:
            print(f"❌ 创建群聊失败: {chat_data.get('msg', 'unknown error')}")
            return None
        chat_id = chat_data["data"]["chat_id"]
        print(f"✅ 飞书群聊创建: {chat_id}")
    except (json.JSONDecodeError, KeyError):
        print(f"❌ 解析群聊响应失败: {chat_resp.stdout[:200]}")
        return None

    # Step 3: 添加用户到群
    if user_open_id:
        add_resp = subprocess.run(
            ["curl", "-s", "-X", "POST",
             f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"id_list": [user_open_id]})],
            capture_output=True, text=True
        )
        try:
            add_data = json.loads(add_resp.stdout)
            if add_data.get("code") == 0:
                print(f"✅ 用户 {user_open_id} 已加入群聊")
            else:
                print(f"⚠️ 添加用户失败: {add_data.get('msg')}")
        except json.JSONDecodeError:
            print(f"⚠️ 解析添加成员响应失败")

    return chat_id


def update_openclaw_config(config_path: Path, agent_id: str, agent_name: str,
                            workspace: Path, chat_id: str | None,
                            tools: list[str], model: str | None,
                            account_id: str = "default"):
    """更新 openclaw.json，添加新 Agent 和 Binding
    
    Args:
        config_path: 配置文件路径
        agent_id: Agent ID
        agent_name: Agent 显示名称
        workspace: Workspace 路径
        chat_id: 飞书群聊 ID（可选）
        tools: 工具权限列表
        model: 模型 ID（可选）
        account_id: 飞书账号 ID（默认 "default"）
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 初始化必要字段
    if "agents" not in config:
        config["agents"] = {"list": []}
    if "bindings" not in config:
        config["bindings"] = []
    if "channels" not in config:
        config["channels"] = {}
    if "feishu" not in config["channels"]:
        config["channels"]["feishu"] = {}

    # 检查是否已存在
    existing_ids = [a["id"] for a in config["agents"]["list"]]
    if agent_id in existing_ids:
        print(f"⚠️ Agent '{agent_id}' 已存在于配置中，跳过")
        return

    # 构造 Agent 配置
    agent_config = {
        "id": agent_id,
        "name": agent_name,
        "workspace": str(workspace),
    }
    if model:
        agent_config["model"] = {"primary": model}
    if tools:
        agent_config["tools"] = {"allow": tools}

    config["agents"]["list"].append(agent_config)
    print(f"✅ Agent '{agent_id}' 已添加到 agents.list（共 {len(config['agents']['list'])} 个）")

    # 添加 Binding
    if chat_id:
        # 检查是否已存在相同 binding
        existing_binding = False
        for binding in config["bindings"]:
            match = binding.get("match", {})
            if match.get("peer", {}).get("id") == chat_id:
                existing_binding = True
                print(f"⚠️ Binding 已存在: {binding.get('agentId')} → group:{chat_id}")
                break
        
        if not existing_binding:
            binding = {
                "agentId": agent_id,
                "match": {
                    "channel": "feishu",
                    "accountId": account_id,
                    "peer": {"kind": "group", "id": chat_id}
                }
            }
            config["bindings"].append(binding)
            print(f"✅ Binding 已添加: {agent_id} → group:{chat_id}")

        # 添加 groups 配置
        if "groups" not in config["channels"]["feishu"]:
            config["channels"]["feishu"]["groups"] = {}
        
        if chat_id not in config["channels"]["feishu"]["groups"]:
            config["channels"]["feishu"]["groups"][chat_id] = {
                "enabled": True,
                "requireMention": False
            }
            print(f"✅ 群聊配置已添加: {chat_id}")
        else:
            print(f"⚠️ 群聊配置已存在: {chat_id}")

    # 验证
    if len(config["agents"]["list"]) < 1:
        print("❌ agents.list 为空！")
        return
    if "bindings" not in config:
        print("❌ bindings 缺失！")
        return

    # 备份并写入
    backup_path = config_path.with_suffix(".json.bak")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(json.loads(config_path.read_text()), f, indent=2, ensure_ascii=False)
    print(f"✅ 配置备份: {backup_path}")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ 配置写入: {config_path}")
    print(f"⚡ 请运行 'openclaw gateway restart' 使配置生效")


def main():
    parser = argparse.ArgumentParser(description="创建飞书多 Agent 子 Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID（英文小写，如 coder）")
    parser.add_argument("--agent-name", help="Agent 显示名称（如 Coder），默认取 agent-id 首字母大写")
    parser.add_argument("--role", required=True, help="角色描述（如 '代码开发助手'）")
    parser.add_argument("--emoji", default="🤖", help="Agent emoji")
    parser.add_argument("--user-name", required=True, help="用户名称")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="预设角色")
    parser.add_argument("--tools", help="逗号分隔的工具列表（覆盖 preset）")
    parser.add_argument("--model", help="模型 ID")
    parser.add_argument("--app-id", help="飞书 App ID")
    parser.add_argument("--app-secret", help="飞书 App Secret")
    parser.add_argument("--user-open-id", help="用户飞书 open_id")
    parser.add_argument("--account-id", default="default", help="飞书账号 ID（多账号场景使用）")
    parser.add_argument("--workspace-base", default=os.path.expanduser("~/.openclaw"),
                        help="workspace 基础目录")
    parser.add_argument("--skip-chat", action="store_true", help="跳过创建飞书群聊")
    parser.add_argument("--skip-config", action="store_true", help="跳过修改 openclaw.json")
    args = parser.parse_args()

    base_dir = Path(args.workspace_base)
    agent_name = args.agent_name or args.agent_id.capitalize()
    preset = PRESETS.get(args.preset) if args.preset else None

    # 解析工具列表
    if args.tools:
        tools = [t.strip() for t in args.tools.split(",")]
    elif preset:
        tools = preset["tools"]
    else:
        tools = ["read", "message", "web_search", "web_fetch", "session_status"]

    print(f"\n{'='*50}")
    print(f"创建 Agent: {agent_name} ({args.agent_id})")
    print(f"角色: {args.role}")
    print(f"工具: {', '.join(tools)}")
    print(f"{'='*50}\n")

    # Step 1: 创建 Workspace
    ws = create_workspace(base_dir, args.agent_id)

    # Step 2: 创建身份文件
    # 如果 preset 有 template，优先从 examples/ 复制完整模板
    template_dir = None
    if preset and preset.get("template"):
        # 查找 examples/ 目录（相对于脚本位置）
        script_dir = Path(__file__).resolve().parent
        template_dir = script_dir.parent / "examples" / preset["template"]
        if not template_dir.exists():
            template_dir = None  # 找不到就 fallback 到自动生成

    if template_dir:
        # 复制模板文件（不覆盖已存在的文件）
        copied = []
        for src_file in template_dir.iterdir():
            if src_file.is_file() and src_file.suffix == ".md":
                dst_file = ws / src_file.name
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                    copied.append(src_file.name)
        print(f"✅ 从模板 {preset['template']} 复制: {', '.join(copied) or '(已存在，跳过)'}")
    else:
        create_identity(ws, args.agent_id, agent_name, args.role, args.emoji, args.user_name)
        create_soul(ws, args.agent_id, agent_name, args.role, args.user_name, preset)
        create_agents_md(ws)

    # Step 3: 创建飞书群聊
    chat_id = None
    if not args.skip_chat and args.app_id and args.app_secret:
        chat_id = create_feishu_chat(args.app_id, args.app_secret,
                                      agent_name, args.user_open_id)
    elif not args.skip_chat:
        print("⚠️ 未提供 --app-id 和 --app-secret，跳过创建飞书群聊")
        print("   你可以手动创建群聊，然后把 chat_id 填入 openclaw.json")

    # Step 4: 更新 OpenClaw 配置
    if not args.skip_config:
        config_path = base_dir / "openclaw.json"
        if config_path.exists():
            update_openclaw_config(config_path, args.agent_id, agent_name,
                                    ws, chat_id, tools, args.model, args.account_id)
        else:
            print(f"⚠️ 配置文件不存在: {config_path}")
            print("   请先安装并初始化 OpenClaw")

    # 汇总
    print(f"\n{'='*50}")
    print(f"✅ Agent '{args.agent_id}' 创建完成！")
    print(f"")
    print(f"Workspace: {ws}")
    if chat_id:
        print(f"群聊 ID:   {chat_id}")
    print(f"")
    print(f"下一步:")
    if not args.skip_config:
        print(f"  1. openclaw gateway restart")
        print(f"  2. 在飞书群聊中发送一条消息测试")
    else:
        print(f"  1. 将 Agent 配置添加到 openclaw.json")
        print(f"  2. openclaw gateway restart")
        print(f"  3. 在飞书群聊中发送一条消息测试")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
