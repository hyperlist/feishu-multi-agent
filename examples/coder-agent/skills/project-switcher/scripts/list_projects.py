#!/usr/bin/env python3
"""列出已注册的项目"""
import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "projects.json"


def load_projects():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f).get("projects", [])
    return []


def list_projects(workspace: str = ""):
    """优先从配置读取，否则扫描 workspace 子目录"""
    projects = load_projects()
    if not projects and workspace and os.path.isdir(workspace):
        projects = [
            {"name": d, "path": os.path.join(workspace, d), "description": "", "language": ""}
            for d in sorted(os.listdir(workspace))
            if os.path.isdir(os.path.join(workspace, d)) and not d.startswith(".")
        ]
    return projects


if __name__ == "__main__":
    projects = list_projects()
    if not projects:
        print("未找到任何项目，请编辑 config/projects.json")
    else:
        print("可用项目：")
        for i, p in enumerate(projects, 1):
            desc = f" — {p['description']}" if p.get("description") else ""
            lang = f" [{p['language']}]" if p.get("language") else ""
            print(f"  {i}. {p['name']}{lang}{desc}")
