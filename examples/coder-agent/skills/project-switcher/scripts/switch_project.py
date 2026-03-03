#!/usr/bin/env python3
"""切换当前项目并记录历史"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "projects.json"


def load_projects():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f).get("projects", [])
    return []


def find_project(identifier: str, projects: list) -> dict | None:
    """按编号或名称查找项目"""
    if identifier.isdigit():
        idx = int(identifier) - 1
        if 0 <= idx < len(projects):
            return projects[idx]
    else:
        for p in projects:
            if p["name"] == identifier:
                return p
    return None


def switch(identifier: str, state_dir: str = "."):
    projects = load_projects()
    project = find_project(identifier, projects)

    if not project:
        print(f"❌ 项目 '{identifier}' 不存在")
        print("运行 list_projects.py 查看可用项目")
        return False

    # 记录当前项目
    state_file = os.path.join(state_dir, ".current_project")
    with open(state_file, "w") as f:
        f.write(project["path"])

    # 记录历史
    history_file = os.path.join(state_dir, ".session_history.json")
    history = {}
    if os.path.exists(history_file):
        with open(history_file) as f:
            history = json.load(f)

    name = project["name"]
    if name not in history:
        history[name] = {"path": project["path"], "sessions": []}
    history[name]["sessions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    history[name]["sessions"] = history[name]["sessions"][-10:]

    with open(history_file, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"✅ 已切换到：{name}")
    print(f"   路径: {project['path']}")
    print()
    print("━" * 40)
    print("🔄 建议开启新 session 继续开发")
    print("━" * 40)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        state_file = ".current_project"
        if os.path.exists(state_file):
            print(f"当前项目：{open(state_file).read().strip()}")
        else:
            print("未选择项目，运行: python3 switch_project.py <名称或编号>")
        sys.exit(0)

    switch(sys.argv[1])
