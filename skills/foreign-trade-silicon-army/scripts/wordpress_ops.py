#!/usr/bin/env python3
"""
WordPress运维脚本 - 外贸硅基军团建站Agent
支持页面创建、文章发布、SEO配置、图片上传等操作
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("wordpress_ops")


# ─── 数据模型 ───────────────────────────────────────────────────────────────

@dataclass
class TaskResult:
    task_id: str
    agent: str = "build"
    status: str = "success"
    result: Optional[dict] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["metadata"] = self.metadata or {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
        }
        return d


# ─── WordPress连接器核心 ────────────────────────────────────────────────────

class WordPressConnector:
    """WordPress REST API 连接器（同步版，兼容CLI）"""

    def __init__(
        self,
        site_url: str,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
    ):
        self.site_url = site_url.rstrip("/")
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = username or os.getenv("WORDPRESS_USERNAME", "")
        self.app_password = app_password or os.getenv("WORDPRESS_APP_PASSWORD", "")
        self._auth: Optional[httpx.BasicAuth] = None
        if self.username and self.app_password:
            self._auth = httpx.BasicAuth(self.username, self.app_password)

    def _get_client(self) -> httpx.Client:
        kwargs: dict[str, Any] = {"base_url": self.api_url, "timeout": 30.0}
        if self._auth:
            kwargs["auth"] = self._auth
        return httpx.Client(**kwargs)

    def test_connection(self) -> dict[str, Any]:
        """测试WordPress连接"""
        try:
            with self._get_client() as client:
                resp = client.get("/")
                resp.raise_for_status()
                data = resp.json()
                return {
                    "connected": True,
                    "site_name": data.get("name"),
                    "site_description": data.get("description"),
                    "version": data.get("version"),
                    "site_url": self.site_url,
                    "rest_base": data.get("rest_url"),
                }
        except httpx.HTTPStatusError as e:
            return {"connected": False, "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def create_page(
        self,
        title: str,
        content: str = "",
        status: str = "draft",
        parent_id: Optional[int] = None,
        template: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建页面"""
        payload: dict[str, Any] = {
            "title": title,
            "content": content,
            "status": status,
        }
        if parent_id:
            payload["parent"] = parent_id
        if template:
            payload["template"] = template

        with self._get_client() as client:
            resp = client.post("/pages", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {
                "id": data["id"],
                "title": data["title"]["rendered"],
                "slug": data["slug"],
                "url": data["link"],
                "status": data["status"],
                "created": data["date"],
            }

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "draft",
        categories: Optional[list[int]] = None,
        tags: Optional[list[int]] = None,
        featured_media: Optional[int] = None,
        excerpt: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建文章"""
        payload: dict[str, Any] = {
            "title": title,
            "content": content,
            "status": status,
        }
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
        if featured_media:
            payload["featured_media"] = featured_media
        if excerpt:
            payload["excerpt"] = excerpt

        with self._get_client() as client:
            resp = client.post("/posts", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {
                "id": data["id"],
                "title": data["title"]["rendered"],
                "slug": data["slug"],
                "url": data["link"],
                "status": data["status"],
                "created": data["date"],
            }

    def update_seo(
        self,
        post_id: int,
        meta_title: str,
        meta_description: str,
        focus_keywords: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """更新SEO元数据（Yoast SEO插件格式）"""
        payload = {
            "meta": {
                "title": meta_title,
                "description": meta_description,
                "focuskw": focus_keywords[0] if focus_keywords else "",
            }
        }
        with self._get_client() as client:
            resp = client.post(f"/posts/{post_id}", json=payload)
            resp.raise_for_status()
            return {
                "updated": True,
                "post_id": post_id,
                "meta_title": meta_title,
                "meta_description": meta_description,
            }

    def upload_media(
        self,
        file_path: str,
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> dict[str, Any]:
        """上传媒体文件"""
        import mimetypes
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, mime_type)}
            data = {"title": title or filename}
            if alt_text:
                data["alt_text"] = alt_text

            with self._get_client() as client:
                resp = client.post("/media", files=files, data=data)
                resp.raise_for_status()
                media = resp.json()
                return {
                    "id": media["id"],
                    "url": media["source_url"],
                    "filename": media["slug"],
                    "mime_type": media["mime_type"],
                    "alt_text": media.get("alt_text", ""),
                }

    def get_post(self, post_id: int) -> dict[str, Any]:
        """获取文章详情"""
        with self._get_client() as client:
            resp = client.get(f"/posts/{post_id}")
            resp.raise_for_status()
            return resp.json()

    def update_post_status(self, post_id: int, status: str) -> dict[str, Any]:
        """更新文章发布状态"""
        with self._get_client() as client:
            resp = client.post(f"/posts/{post_id}", json={"status": status})
            resp.raise_for_status()
            return {"updated": True, "post_id": post_id, "status": status}

    def list_posts(self, per_page: int = 10, status: str = "publish") -> list[dict]:
        """列出文章"""
        with self._get_client() as client:
            resp = client.get("/posts", params={"per_page": per_page, "status": status})
            resp.raise_for_status()
            return resp.json()


# ─── CLI入口 ───────────────────────────────────────────────────────────────

def run_test(site_url: str, username: str, app_password: str) -> TaskResult:
    """执行连接测试"""
    connector = WordPressConnector(site_url, username, app_password)
    status = connector.test_connection()
    if status.get("connected"):
        logger.info(f"✅ WordPress连接成功: {status['site_name']} v{status['version']}")
        return TaskResult(
            task_id=f"wp_test_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="success",
            result=status,
        )
    else:
        logger.error(f"❌ WordPress连接失败: {status.get('error')}")
        return TaskResult(
            task_id=f"wp_test_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="failed",
            error=status.get("error", "Unknown error"),
        )


def run_create_page(
    site_url: str, username: str, app_password: str,
    title: str, content: str = "", status: str = "draft",
) -> TaskResult:
    """创建页面"""
    connector = WordPressConnector(site_url, username, app_password)
    try:
        result = connector.create_page(title, content, status)
        logger.info(f"✅ 页面创建成功: {result['url']}")
        return TaskResult(
            task_id=f"wp_page_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="success",
            result=result,
        )
    except Exception as e:
        logger.error(f"❌ 页面创建失败: {e}")
        return TaskResult(
            task_id=f"wp_page_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="failed",
            error=str(e),
        )


def run_create_post(
    site_url: str, username: str, app_password: str,
    title: str, content: str, status: str = "draft",
) -> TaskResult:
    """创建文章"""
    connector = WordPressConnector(site_url, username, app_password)
    try:
        result = connector.create_post(title, content, status)
        logger.info(f"✅ 文章创建成功: {result['url']}")
        return TaskResult(
            task_id=f"wp_post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="success",
            result=result,
        )
    except Exception as e:
        logger.error(f"❌ 文章创建失败: {e}")
        return TaskResult(
            task_id=f"wp_post_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="failed",
            error=str(e),
        )


def run_update_seo(
    site_url: str, username: str, app_password: str,
    post_id: int, meta_title: str, meta_description: str,
    focus_keywords: Optional[list[str]] = None,
) -> TaskResult:
    """更新SEO"""
    connector = WordPressConnector(site_url, username, app_password)
    try:
        result = connector.update_seo(post_id, meta_title, meta_description, focus_keywords)
        logger.info(f"✅ SEO更新成功: post_id={post_id}")
        return TaskResult(
            task_id=f"wp_seo_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="success",
            result=result,
        )
    except Exception as e:
        logger.error(f"❌ SEO更新失败: {e}")
        return TaskResult(
            task_id=f"wp_seo_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            agent="build",
            status="failed",
            error=str(e),
        )


def main():
    parser = argparse.ArgumentParser(description="外贸硅基军团 - WordPress运维脚本")
    parser.add_argument("--action", required=True,
                        choices=["test", "create_page", "create_post", "update_seo", "upload_media", "list"],
                        help="执行的操作")
    parser.add_argument("--site-url", default=os.getenv("WORDPRESS_SITE_URL", ""),
                        help="WordPress站点URL")
    parser.add_argument("--username", default=os.getenv("WORDPRESS_USERNAME", ""),
                        help="WordPress用户名")
    parser.add_argument("--app-password", default=os.getenv("WORDPRESS_APP_PASSWORD", ""),
                        help="WordPress应用密码")
    parser.add_argument("--title", help="页面/文章标题")
    parser.add_argument("--content", default="", help="页面/文章内容（支持HTML）")
    parser.add_argument("--status", default="draft", choices=["draft", "publish", "pending", "private"],
                        help="发布状态")
    parser.add_argument("--post-id", type=int, help="文章ID（用于SEO更新）")
    parser.add_argument("--meta-title", help="SEO标题")
    parser.add_argument("--meta-description", help="SEO描述")
    parser.add_argument("--focus-keywords", help="焦点关键词（逗号分隔）")
    parser.add_argument("--file-path", help="上传文件路径")
    parser.add_argument("--output-json", action="store_true", help="JSON格式输出结果")

    args = parser.parse_args()

    # 验证必填参数
    if args.action == "test" and not args.site_url:
        logger.error("错误: --site-url 为必填参数（或设置 WORDPRESS_SITE_URL 环境变量）")
        sys.exit(1)

    task_result: Optional[TaskResult] = None

    if args.action == "test":
        task_result = run_test(args.site_url, args.username, args.app_password)

    elif args.action == "create_page":
        if not args.title:
            logger.error("错误: --title 为必填参数")
            sys.exit(1)
        task_result = run_create_page(
            args.site_url, args.username, args.app_password,
            args.title, args.content, args.status,
        )

    elif args.action == "create_post":
        if not args.title or not args.content:
            logger.error("错误: --title 和 --content 为必填参数")
            sys.exit(1)
        task_result = run_create_post(
            args.site_url, args.username, args.app_password,
            args.title, args.content, args.status,
        )

    elif args.action == "update_seo":
        if not args.post_id or not args.meta_title:
            logger.error("错误: --post-id 和 --meta-title 为必填参数")
            sys.exit(1)
        keywords = [k.strip() for k in args.focus_keywords.split(",")] if args.focus_keywords else None
        task_result = run_update_seo(
            args.site_url, args.username, args.app_password,
            args.post_id, args.meta_title, args.meta_description or "",
            keywords,
        )

    elif args.action == "upload_media":
        if not args.file_path:
            logger.error("错误: --file-path 为必填参数")
            sys.exit(1)
        connector = WordPressConnector(args.site_url, args.username, args.app_password)
        try:
            result = connector.upload_media(args.file_path)
            task_result = TaskResult(
                task_id=f"wp_media_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                agent="build", status="success", result=result,
            )
        except Exception as e:
            task_result = TaskResult(
                task_id=f"wp_media_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                agent="build", status="failed", error=str(e),
            )

    elif args.action == "list":
        connector = WordPressConnector(args.site_url, args.username, args.app_password)
        try:
            posts = connector.list_posts(per_page=20)
            task_result = TaskResult(
                task_id=f"wp_list_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                agent="build", status="success",
                result={"posts": posts, "count": len(posts)},
            )
        except Exception as e:
            task_result = TaskResult(
                task_id=f"wp_list_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                agent="build", status="failed", error=str(e),
            )

    # 输出结果
    if args.output_json:
        print(json.dumps(task_result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(task_result.to_dict(), ensure_ascii=False))

    # 以状态码退出
    sys.exit(0 if task_result.status == "success" else 1)


if __name__ == "__main__":
    main()
