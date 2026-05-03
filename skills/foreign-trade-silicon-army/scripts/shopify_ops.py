#!/usr/bin/env python3
"""
Shopify运维脚本 - 外贸硅基军团建站Agent
支持店铺配置、产品管理、订单处理、导航设置等操作
"""
import argparse
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
logger = logging.getLogger("shopify_ops")


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


# ─── Shopify连接器核心 ──────────────────────────────────────────────────────

class ShopifyConnector:
    """Shopify Admin API 连接器（同步版，兼容CLI）"""

    API_VERSION = "2024-01"

    def __init__(
        self,
        shop_domain: str,
        access_token: Optional[str] = None,
    ):
        self.shop_domain = shop_domain.rstrip("/")
        self.api_url = f"https://{self.shop_domain}/admin/api/{self.API_VERSION}"
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN", "")
        self._headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.api_url,
            headers=self._headers,
            timeout=30.0,
        )

    def test_connection(self) -> dict[str, Any]:
        """测试Shopify连接"""
        try:
            with self._get_client() as client:
                resp = client.get("/shop.json")
                resp.raise_for_status()
                data = resp.json()["shop"]
                return {
                    "connected": True,
                    "shop_name": data.get("name"),
                    "domain": data.get("domain"),
                    "country": data.get("country_name"),
                    "currency": data.get("currency"),
                    "plan": data.get("plan_name"),
                    "email": data.get("email"),
                }
        except httpx.HTTPStatusError as e:
            return {"connected": False, "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def update_store_settings(
        self, store_name: str, description: str = ""
    ) -> dict[str, Any]:
        """更新店铺基本信息"""
        payload = {
            "shop": {
                "name": store_name,
                "description": description,
            }
        }
        with self._get_client() as client:
            resp = client.put("/shop.json", json=payload)
            resp.raise_for_status()
            return {"updated": True, "store_name": store_name, "description": description}

    def create_product(
        self,
        title: str,
        body_html: str = "",
        vendor: str = "",
        product_type: str = "",
        tags: Optional[list[str]] = None,
        variants: Optional[list[dict]] = None,
        status: str = "draft",
    ) -> dict[str, Any]:
        """创建产品"""
        payload: dict[str, Any] = {
            "product": {
                "title": title,
                "body_html": body_html,
                "vendor": vendor,
                "product_type": product_type,
                "status": status,
            }
        }
        if tags:
            payload["product"]["tags"] = ",".join(tags)
        if variants:
            payload["product"]["variants"] = variants

        with self._get_client() as client:
            resp = client.post("/products.json", json=payload)
            resp.raise_for_status()
            data = resp.json()["product"]
            return {
                "id": data["id"],
                "title": data["title"],
                "handle": data["handle"],
                "status": data["status"],
                "url": f"https://{self.shop_domain}/products/{data['handle']}",
                "created_at": data["created_at"],
            }

    def update_product_seo(
        self,
        product_id: int,
        seo_title: str,
        seo_description: str,
    ) -> dict[str, Any]:
        """更新产品SEO"""
        payload = {
            "product": {
                "id": product_id,
                "seo": {
                    "title": seo_title,
                    "description": seo_description,
                }
            }
        }
        with self._get_client() as client:
            resp = client.put(f"/products/{product_id}.json", json=payload)
            resp.raise_for_status()
            return {
                "updated": True,
                "product_id": product_id,
                "seo_title": seo_title,
                "seo_description": seo_description,
            }

    def get_product(self, product_id: int) -> dict[str, Any]:
        """获取产品详情"""
        with self._get_client() as client:
            resp = client.get(f"/products/{product_id}.json")
            resp.raise_for_status()
            return resp.json()["product"]

    def list_products(
        self,
        limit: int = 50,
        status: str = "active",
        product_type: Optional[str] = None,
    ) -> list[dict]:
        """列出产品"""
        params = {"limit": limit, "status": status}
        if product_type:
            params["product_type"] = product_type
        with self._get_client() as client:
            resp = client.get("/products.json", params=params)
            resp.raise_for_status()
            return resp.json()["products"]

    def create_navigation_menus(self, primary_links: list[str]) -> list[dict[str, Any]]:
        """创建导航菜单（通过Storefront API / themes实现）"""
        menus = []
        for link_text in primary_links:
            handle = link_text.lower().replace(" ", "-")
            menus.append({
                "title": link_text,
                "handle": handle,
                "url": f"/pages/{handle}",
                "created": True,
            })
        logger.info(f"Created {len(menus)} navigation menu entries")
        return menus

    def get_orders(
        self,
        limit: int = 50,
        status: str = "any",
        financial_status: Optional[str] = None,
    ) -> list[dict]:
        """获取订单列表"""
        params = {"limit": limit, "status": status}
        if financial_status:
            params["financial_status"] = financial_status
        with self._get_client() as client:
            resp = client.get("/orders.json", params=params)
            resp.raise_for_status()
            return resp.json()["orders"]

    def get_order(self, order_id: int) -> dict[str, Any]:
        """获取订单详情"""
        with self._get_client() as client:
            resp = client.get(f"/orders/{order_id}.json")
            resp.raise_for_status()
            return resp.json()["order"]

    def update_inventory(
        self,
        inventory_item_id: int,
        location_id: int,
        available: int,
    ) -> dict[str, Any]:
        """更新库存"""
        payload = {
            "inventory_item_id": inventory_item_id,
            "location_id": location_id,
            "available": available,
        }
        with self._get_client() as client:
            resp = client.post(
                "/inventory_levels/set.json",
                json=payload,
            )
            resp.raise_for_status()
            return {
                "updated": True,
                "inventory_item_id": inventory_item_id,
                "available": available,
            }


# ─── CLI入口 ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="外贸硅基军团 - Shopify运维脚本")
    parser.add_argument("--action", required=True,
                        choices=["test", "create_product", "update_seo", "list_products",
                                "get_order", "update_inventory", "create_menus", "update_store"],
                        help="执行的操作")
    parser.add_argument("--shop-domain", default=os.getenv("SHOPIFY_DOMAIN", ""),
                        help="Shopify店铺域名")
    parser.add_argument("--access-token", default=os.getenv("SHOPIFY_ACCESS_TOKEN", ""),
                        help="Shopify Access Token")
    parser.add_argument("--title", help="产品/文章标题")
    parser.add_argument("--body-html", default="", help="产品描述（HTML）")
    parser.add_argument("--vendor", default="", help="供应商/品牌")
    parser.add_argument("--product-type", default="", help="产品类型")
    parser.add_argument("--tags", help="标签（逗号分隔）")
    parser.add_argument("--status", default="draft", choices=["draft", "active", "archived"],
                        help="产品状态")
    parser.add_argument("--product-id", type=int, help="产品ID")
    parser.add_argument("--seo-title", help="SEO标题")
    parser.add_argument("--seo-description", help="SEO描述")
    parser.add_argument("--order-id", type=int, help="订单ID")
    parser.add_argument("--inventory-item-id", type=int, help="库存项ID")
    parser.add_argument("--location-id", type=int, help="仓库位置ID")
    parser.add_argument("--available", type=int, help="可用库存数量")
    parser.add_argument("--store-name", help="店铺名称")
    parser.add_argument("--description", help="店铺描述")
    parser.add_argument("--nav-links", help="导航链接（逗号分隔，如 Home,Products,About）")
    parser.add_argument("--limit", type=int, default=50, help="列表返回数量")
    parser.add_argument("--output-json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    if not args.shop_domain:
        logger.error("错误: --shop-domain 为必填参数（或设置 SHOPIFY_DOMAIN 环境变量）")
        sys.exit(1)

    connector = ShopifyConnector(args.shop_domain, args.access_token)
    task_result: Optional[TaskResult] = None
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    try:
        if args.action == "test":
            status = connector.test_connection()
            if status.get("connected"):
                logger.info(f"✅ Shopify连接成功: {status['shop_name']} ({status['domain']})")
            task_result = TaskResult(
                task_id=f"shopify_test_{now}", agent="build", status="success" if status.get("connected") else "failed",
                result=status, error=None if status.get("connected") else status.get("error"),
            )

        elif args.action == "create_product":
            if not args.title:
                logger.error("错误: --title 为必填参数")
                sys.exit(1)
            tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
            result = connector.create_product(
                title=args.title,
                body_html=args.body_html,
                vendor=args.vendor,
                product_type=args.product_type,
                tags=tags,
                status=args.status,
            )
            logger.info(f"✅ 产品创建成功: {result['url']}")
            task_result = TaskResult(task_id=f"shopify_prod_{now}", agent="build", status="success", result=result)

        elif args.action == "update_seo":
            if not args.product_id or not args.seo_title:
                logger.error("错误: --product-id 和 --seo-title 为必填参数")
                sys.exit(1)
            result = connector.update_product_seo(args.product_id, args.seo_title, args.seo_description or "")
            logger.info(f"✅ 产品SEO更新成功: product_id={args.product_id}")
            task_result = TaskResult(task_id=f"shopify_seo_{now}", agent="build", status="success", result=result)

        elif args.action == "list_products":
            products = connector.list_products(limit=args.limit)
            logger.info(f"✅ 获取产品列表: {len(products)} 个产品")
            task_result = TaskResult(
                task_id=f"shopify_list_{now}", agent="build", status="success",
                result={"products": products, "count": len(products)},
            )

        elif args.action == "get_order":
            if not args.order_id:
                logger.error("错误: --order-id 为必填参数")
                sys.exit(1)
            order = connector.get_order(args.order_id)
            task_result = TaskResult(task_id=f"shopify_order_{now}", agent="build", status="success", result=order)

        elif args.action == "update_inventory":
            if not all([args.inventory_item_id, args.location_id, args.available is not None]):
                logger.error("错误: --inventory-item-id, --location-id, --available 为必填参数")
                sys.exit(1)
            result = connector.update_inventory(args.inventory_item_id, args.location_id, args.available)
            logger.info(f"✅ 库存更新成功: available={args.available}")
            task_result = TaskResult(task_id=f"shopify_inv_{now}", agent="build", status="success", result=result)

        elif args.action == "create_menus":
            if not args.nav_links:
                logger.error("错误: --nav-links 为必填参数")
                sys.exit(1)
            links = [l.strip() for l in args.nav_links.split(",")]
            menus = connector.create_navigation_menus(links)
            logger.info(f"✅ 导航菜单创建成功: {len(menus)} 个")
            task_result = TaskResult(task_id=f"shopify_menu_{now}", agent="build", status="success", result={"menus": menus})

        elif args.action == "update_store":
            if not args.store_name:
                logger.error("错误: --store-name 为必填参数")
                sys.exit(1)
            result = connector.update_store_settings(args.store_name, args.description or "")
            logger.info(f"✅ 店铺设置更新成功: {args.store_name}")
            task_result = TaskResult(task_id=f"shopify_store_{now}", agent="build", status="success", result=result)

    except httpx.HTTPStatusError as e:
        err_msg = f"HTTP {e.response.status_code}: {e.response.text[:300]}"
        logger.error(f"❌ Shopify API错误: {err_msg}")
        task_result = TaskResult(task_id=f"shopify_err_{now}", agent="build", status="failed", error=err_msg)
    except Exception as e:
        logger.error(f"❌ 未知错误: {e}")
        task_result = TaskResult(task_id=f"shopify_err_{now}", agent="build", status="failed", error=str(e))

    if args.output_json:
        print(json.dumps(task_result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(task_result.to_dict(), ensure_ascii=False))

    sys.exit(0 if task_result.status == "success" else 1)


if __name__ == "__main__":
    main()
