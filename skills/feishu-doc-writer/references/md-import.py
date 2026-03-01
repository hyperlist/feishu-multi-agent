#!/usr/bin/env python3
"""
飞书 MD 导入脚本 — 将本地 .md 文件导入为飞书文档

用法:
    python3 md-import.py <md_file> <doc_title> [folder_token]

依赖: requests

流程: 上传素材 → 创建导入任务 → 轮询结果 → 输出文档链接
"""

import requests, json, time, os, sys


def get_token(app_id: str, app_secret: str) -> str:
    """获取 tenant_access_token"""
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret}
    ).json()
    token = resp.get("tenant_access_token")
    if not token:
        raise RuntimeError(f"获取 token 失败: {resp}")
    return token


def upload_md(headers: dict, md_file: str) -> str:
    """上传 MD 文件到飞书素材库，返回 file_token"""
    with open(md_file, "rb") as f:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all",
            headers=headers,
            data={
                "file_name": os.path.basename(md_file),
                "parent_type": "explorer",
                "parent_node": "",
                "size": str(os.path.getsize(md_file)),
            },
            files={"file": (os.path.basename(md_file), f, "text/markdown")}
        ).json()
    file_token = resp.get("data", {}).get("file_token")
    if not file_token:
        raise RuntimeError(f"上传失败: {resp}")
    return file_token


def import_md(headers: dict, file_token: str, title: str, folder_token: str = "") -> dict:
    """创建导入任务，轮询直到完成，返回 {token, url}"""
    resp = requests.post(
        "https://open.feishu.cn/open-apis/drive/v1/import_tasks",
        headers={**headers, "Content-Type": "application/json"},
        json={
            "file_extension": "md",
            "file_token": file_token,
            "type": "docx",
            "file_name": title,
            "point": {"mount_type": 1, "mount_key": folder_token}
        }
    ).json()
    ticket = resp.get("data", {}).get("ticket")
    if not ticket:
        raise RuntimeError(f"创建导入任务失败: {resp}")

    for _ in range(20):
        time.sleep(2)
        check = requests.get(
            f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}",
            headers=headers
        ).json()
        result = check.get("data", {}).get("result", {})
        if result.get("token"):
            return result
    raise TimeoutError("导入任务超时")


def grant_permission(headers: dict, doc_token: str, user_open_id: str):
    """授予用户文档管理权限"""
    requests.post(
        f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/members?type=docx",
        headers={**headers, "Content-Type": "application/json"},
        json={
            "member_type": "openid",
            "member_id": user_open_id,
            "perm": "full_access"
        }
    )


def main():
    if len(sys.argv) < 3:
        print("用法: python3 md-import.py <md_file> <doc_title> [folder_token]")
        print()
        print("环境变量:")
        print("  FEISHU_APP_ID       飞书应用 App ID")
        print("  FEISHU_APP_SECRET   飞书应用 App Secret")
        print("  FEISHU_USER_OPENID  用户 open_id (可选，用于自动授权)")
        sys.exit(1)

    md_file = sys.argv[1]
    title = sys.argv[2]
    folder_token = sys.argv[3] if len(sys.argv) > 3 else ""

    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    user_open_id = os.environ.get("FEISHU_USER_OPENID", "")

    if not app_id or not app_secret:
        # 尝试从 openclaw.json 读取
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(config_path):
            config = json.load(open(config_path))
            feishu = config.get("channels", {}).get("feishu", {})
            accounts = feishu.get("accounts", {})
            for acc in accounts.values():
                if isinstance(acc, dict) and acc.get("appId"):
                    app_id = acc["appId"]
                    app_secret = acc["appSecret"]
                    break
        if not app_id:
            print("错误: 需要 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")
            sys.exit(1)

    token = get_token(app_id, app_secret)
    headers = {"Authorization": f"Bearer {token}"}

    print(f"上传 {md_file}...")
    file_token = upload_md(headers, md_file)

    print(f"导入为飞书文档...")
    result = import_md(headers, file_token, title, folder_token)
    doc_token = result["token"]
    url = result.get("url", f"https://feishu.cn/docx/{doc_token}")

    if user_open_id:
        grant_permission(headers, doc_token, user_open_id)
        print(f"已授权 {user_open_id}")

    print(f"✅ {url}")
    print(f"   doc_token: {doc_token}")


if __name__ == "__main__":
    main()
