#!/usr/bin/env python3
"""
Binding 配置管理工具

专门用于管理 OpenClaw 中的 binding 配置，解决各种场景下的 binding 问题。

用法:
  # 列出所有 binding
  python3 manage_binding.py --list

  # 添加群聊 binding
  python3 manage_binding.py --add coder oc_xxx

  # 添加私信 binding
  python3 manage_binding.py --add main ou_xxx --kind dm

  # 多账号场景：指定 accountId
  python3 manage_binding.py --add coder oc_xxx --account work

  # 移除 binding
  python3 manage_binding.py --remove oc_xxx

  # 移除某个 agent 的所有 binding
  python3 manage_binding.py --remove-by-agent coder

  # 验证 binding 配置
  python3 manage_binding.py --validate

  # 导出 binding 配置
  python3 manage_binding.py --export

  # 导入 binding 配置
  python3 manage_binding.py --import bindings.json

  # 修复常见问题
  python3 manage_binding.py --fix-missing-accountId

  # 应用修改并重启
  python3 manage_binding.py --add coder oc_xxx --apply --restart
"""

import json
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
BACKUP_DIR = os.path.expanduser("~/.openclaw/config-backups")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(config, reason="manual"):
    """安全写入配置"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"binding_{ts}.json")
    shutil.copy2(CONFIG_PATH, backup_path)
    print(f"📦 备份: {backup_path}")

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ 配置已写入 ({reason})")
    return True


def list_bindings(config, verbose=False):
    """列出所有 binding"""
    bindings = config.get("bindings", [])
    agent_ids = {a["id"] for a in config.get("agents", {}).get("list", [])}
    
    print(f"\n{'Agent':<12} {'Channel':<8} {'Account':<10} {'Kind':<6} {'Peer ID':<35} {'Status'}")
    print("-" * 90)
    
    for i, binding in enumerate(bindings):
        agent_id = binding.get("agentId", "-")
        match = binding.get("match", {})
        channel = match.get("channel", "-")
        account_id = match.get("accountId", "⚠️ missing")
        peer = match.get("peer", {})
        peer_kind = peer.get("kind", "-")
        peer_id = peer.get("id", "-")
        
        # 检查状态
        if agent_id not in agent_ids:
            status = "❌ agent不存在"
        elif not account_id:
            status = "⚠️ 缺accountId"
        else:
            status = "✅"
        
        if len(peer_id) > 32:
            peer_id = peer_id[:29] + "..."
        
        print(f"{agent_id:<12} {channel:<8} {account_id:<10} {peer_kind:<6} {peer_id:<35} {status}")
    
    print(f"\n总计: {len(bindings)} bindings, {len(agent_ids)} agents")
    return bindings


def add_binding(config, agent_id, peer_id, peer_kind="group", account_id="default"):
    """添加 binding"""
    # 验证 agent 存在
    agent_ids = {a["id"] for a in config.get("agents", {}).get("list", [])}
    if agent_id not in agent_ids:
        print(f"❌ agent '{agent_id}' 不存在")
        print(f"   现有 agents: {', '.join(sorted(agent_ids))}")
        return config
    
    # 验证 peer_kind
    if peer_kind not in ["group", "dm"]:
        print(f"❌ peer_kind 必须是 'group' 或 'dm'")
        return config
    
    # 验证 peer_id 格式
    if peer_kind == "group" and not peer_id.startswith("oc_"):
        print(f"⚠️ 群聊 ID 应以 'oc_' 开头: {peer_id}")
    elif peer_kind == "dm" and not peer_id.startswith("ou_"):
        print(f"⚠️ 用户 ID 应以 'ou_' 开头: {peer_id}")
    
    # 检查是否已存在相同 binding
    for binding in config.get("bindings", []):
        match = binding.get("match", {})
        if (match.get("peer", {}).get("id") == peer_id and 
            match.get("peer", {}).get("kind") == peer_kind):
            existing_agent = binding.get("agentId")
            print(f"⚠️ Binding 已存在: {existing_agent} → {peer_kind}:{peer_id}")
            return config
    
    # 添加 binding
    binding = {
        "agentId": agent_id,
        "match": {
            "channel": "feishu",
            "accountId": account_id,
            "peer": {
                "kind": peer_kind,
                "id": peer_id
            }
        }
    }
    config.setdefault("bindings", []).append(binding)
    print(f"✅ Binding 已添加: {agent_id} → {peer_kind}:{peer_id} (account: {account_id})")
    
    # 自动管理 groups 配置（仅群聊）
    if peer_kind == "group":
        if "channels" not in config:
            config["channels"] = {}
        if "feishu" not in config["channels"]:
            config["channels"]["feishu"] = {}
        if "groups" not in config["channels"]["feishu"]:
            config["channels"]["feishu"]["groups"] = {}
        
        if peer_id not in config["channels"]["feishu"]["groups"]:
            config["channels"]["feishu"]["groups"][peer_id] = {
                "enabled": True,
                "requireMention": False
            }
            print(f"✅ Groups 配置已添加: {peer_id}")
    
    return config


def remove_binding(config, peer_id_or_pattern):
    """移除 binding"""
    original = config.get("bindings", [])
    new_bindings = []
    removed_count = 0
    
    for binding in original:
        peer_id = binding.get("match", {}).get("peer", {}).get("id", "")
        agent_id = binding.get("agentId", "")
        
        if peer_id == peer_id_or_pattern or peer_id_or_pattern in peer_id:
            print(f"❌ 已移除: {agent_id} → {binding.get('match', {}).get('peer', {}).get('kind')}:{peer_id}")
            removed_count += 1
        else:
            new_bindings.append(binding)
    
    config["bindings"] = new_bindings
    
    if removed_count == 0:
        print(f"⚠️ 未找到匹配的 binding: {peer_id_or_pattern}")
    else:
        print(f"✅ 共移除 {removed_count} 个 binding")
    
    return config


def remove_by_agent(config, agent_id):
    """移除某个 agent 的所有 binding"""
    original = config.get("bindings", [])
    new_bindings = []
    removed_count = 0
    
    for binding in original:
        if binding.get("agentId") == agent_id:
            peer_id = binding.get("match", {}).get("peer", {}).get("id", "")
            peer_kind = binding.get("match", {}).get("peer", {}).get("kind", "")
            print(f"❌ 已移除: {agent_id} → {peer_kind}:{peer_id}")
            removed_count += 1
        else:
            new_bindings.append(binding)
    
    config["bindings"] = new_bindings
    
    if removed_count == 0:
        print(f"⚠️ Agent '{agent_id}' 没有绑定任何群聊或私信")
    else:
        print(f"✅ 共移除 {removed_count} 个 binding")
    
    return config


def validate_bindings(config):
    """验证 binding 配置"""
    errors = []
    warnings = []
    
    agent_ids = {a["id"] for a in config.get("agents", {}).get("list", [])}
    bindings = config.get("bindings", [])
    
    # 检查 bindings 是否存在
    if not bindings:
        warnings.append("bindings 为空")
    
    # 检查每个 binding
    for i, binding in enumerate(bindings):
        idx = i + 1
        agent_id = binding.get("agentId")
        
        # 检查 agentId
        if agent_id not in agent_ids:
            errors.append(f"binding #{idx}: agentId '{agent_id}' 不存在")
        
        # 检查 match
        match = binding.get("match", {})
        if not match:
            errors.append(f"binding #{idx}: 缺少 match 字段")
            continue
        
        # 检查 channel
        if match.get("channel") != "feishu":
            errors.append(f"binding #{idx}: channel 必须是 'feishu'")
        
        # 检查 accountId
        account_id = match.get("accountId")
        if not account_id:
            errors.append(f"binding #{idx}: 缺少 accountId 字段")
        
        # 检查 peer
        peer = match.get("peer", {})
        if not peer:
            errors.append(f"binding #{idx}: 缺少 peer 字段")
            continue
        
        peer_kind = peer.get("kind")
        peer_id = peer.get("id")
        
        if peer_kind not in ["group", "dm"]:
            errors.append(f"binding #{idx}: peer.kind 必须是 'group' 或 'dm'")
        
        if not peer_id:
            errors.append(f"binding #{idx}: peer.id 不能为空")
        
        # 警告：peer_id 格式
        if peer_kind == "group" and peer_id and not peer_id.startswith("oc_"):
            warnings.append(f"binding #{idx}: 群聊 ID 通常以 'oc_' 开头")
        elif peer_kind == "dm" and peer_id and not peer_id.startswith("ou_"):
            warnings.append(f"binding #{idx}: 用户 ID 通常以 'ou_' 开头")
    
    # 检查重复 binding
    peer_ids = set()
    for binding in bindings:
        peer_id = binding.get("match", {}).get("peer", {}).get("id")
        if peer_id:
            if peer_id in peer_ids:
                errors.append(f"重复的 peer.id: {peer_id}")
            peer_ids.add(peer_id)
    
    # 输出结果
    print("\n" + "=" * 50)
    print("Binding 验证结果")
    print("=" * 50)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for e in errors:
            print(f"   - {e}")
    
    if warnings:
        print(f"\n⚠️ 发现 {len(warnings)} 个警告:")
        for w in warnings:
            print(f"   - {w}")
    
    if not errors and not warnings:
        print("\n✅ 所有 binding 配置正确")
    
    return len(errors) == 0


def fix_missing_account_id(config):
    """修复缺少 accountId 的 binding"""
    fixed = 0
    for binding in config.get("bindings", []):
        match = binding.get("match", {})
        if "accountId" not in match or not match.get("accountId"):
            match["accountId"] = "default"
            agent_id = binding.get("agentId", "unknown")
            peer_id = match.get("peer", {}).get("id", "unknown")
            print(f"✅ 已修复: {agent_id} → peer:{peer_id} (accountId = 'default')")
            fixed += 1
    
    if fixed > 0:
        print(f"\n✅ 共修复 {fixed} 个缺少 accountId 的 binding")
    else:
        print("\n⚠️ 没有需要修复的 binding")
    
    return config


def export_bindings(config, output_file):
    """导出 binding 配置"""
    bindings = config.get("bindings", [])
    with open(output_file, "w") as f:
        json.dump(bindings, f, indent=2, ensure_ascii=False)
    print(f"✅ 已导出 {len(bindings)} 个 binding 到: {output_file}")


def import_bindings(config, input_file, merge=False):
    """导入 binding 配置"""
    with open(input_file) as f:
        new_bindings = json.load(f)
    
    if not isinstance(new_bindings, list):
        print("❌ 导入文件格式错误，应为 JSON 数组")
        return config
    
    if merge:
        # 合并：追加新 binding，跳过重复
        existing_peers = {
            (b.get("match", {}).get("peer", {}).get("kind"),
             b.get("match", {}).get("peer", {}).get("id"))
            for b in config.get("bindings", [])
        }
        
        added = 0
        for binding in new_bindings:
            peer = binding.get("match", {}).get("peer", {})
            key = (peer.get("kind"), peer.get("id"))
            if key not in existing_peers:
                config.setdefault("bindings", []).append(binding)
                added += 1
        
        print(f"✅ 合并完成: 新增 {added} 个 binding")
    else:
        # 替换
        config["bindings"] = new_bindings
        print(f"✅ 替换完成: {len(new_bindings)} 个 binding")
    
    return config


def main():
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw Binding 配置管理工具")
    parser.add_argument("--list", action="store_true", help="列出所有 binding")
    parser.add_argument("--add", nargs=2, metavar=("AGENT_ID", "PEER_ID"), help="添加 binding")
    parser.add_argument("--remove", metavar="PEER_ID", help="移除 binding")
    parser.add_argument("--remove-by-agent", metavar="AGENT_ID", help="移除 agent 的所有 binding")
    parser.add_argument("--kind", choices=["group", "dm"], default="group", help="binding 类型")
    parser.add_argument("--account", default="default", help="accountId")
    parser.add_argument("--validate", action="store_true", help="验证 binding 配置")
    parser.add_argument("--fix-missing-accountId", action="store_true", help="修复缺少 accountId 的 binding")
    parser.add_argument("--export", metavar="FILE", help="导出 binding 到文件")
    parser.add_argument("--import", dest="import_file", metavar="FILE", help="从文件导入 binding")
    parser.add_argument("--merge", action="store_true", help="与现有 binding 合并（仅与 --import 一起使用）")
    parser.add_argument("--apply", action="store_true", help="应用修改")
    parser.add_argument("--restart", action="store_true", help="应用后重启 gateway")
    
    args = parser.parse_args()
    
    # 检查配置文件
    if not Path(CONFIG_PATH).exists():
        print(f"❌ 配置文件不存在: {CONFIG_PATH}")
        return
    
    config = load_config()
    modified = False
    
    if args.list:
        list_bindings(config)
        return
    
    if args.validate:
        validate_bindings(config)
        return
    
    if args.fix_missing_account_id:
        config = fix_missing_account_id(config)
        modified = True
    
    if args.add:
        agent_id, peer_id = args.add
        config = add_binding(config, agent_id, peer_id, args.kind, args.account)
        modified = True
    
    if args.remove:
        config = remove_binding(config, args.remove)
        modified = True
    
    if args.remove_by_agent:
        config = remove_by_agent(config, args.remove_by_agent)
        modified = True
    
    if args.export:
        bindings = config.get("bindings", [])
        with open(args.export, "w") as f:
            json.dump(bindings, f, indent=2, ensure_ascii=False)
        print(f"✅ 已导出 {len(bindings)} 个 binding 到: {args.export}")
        return
    
    if args.import_file:
        config = import_bindings(config, args.import_file, args.merge)
        modified = True
    
    if modified and args.apply:
        reason = "binding管理"
        if save_config(config, reason):
            if args.restart:
                print("🔄 重启 gateway...")
                os.system("openclaw gateway restart")
        return
    
    if modified and not args.apply:
        print("\n⚠️ 预览模式，加 --apply 写入，加 --apply --restart 写入并重启")
    
    if not any([args.list, args.add, args.remove, args.remove_by_agent,
                args.validate, args.fix_missing_accountId, args.export, args.import_file]):
        parser.print_help()


if __name__ == "__main__":
    main()
