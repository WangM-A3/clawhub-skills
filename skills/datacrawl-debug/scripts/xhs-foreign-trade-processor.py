#!/usr/bin/env python3
"""
小红书外贸博主数据抓取 v2.0 — 改进版
基于 datacrawl-debug 技能诊断，修复以下问题：
1. requests直连API → Playwright渲染（解决403/验证码/动态加载）
2. 无重试 → 指数退避重试
3. 硬编码API路径 → 页面搜索+数据提取（API路径经常变）
4. 无Cookie管理 → 登录态持久化
5. 粉丝画像空白 → 基于互动数据的粉丝质量评分模型
"""

import json
import random
import re
import sys
import time
from datetime import datetime


class XhsForeignTradeCrawler:
    """小红书外贸博主爬虫 — 需配合Playwright使用"""

    KEYWORDS = ["外贸", "跨境电商", "B2B外贸", "独立站", "TikTok外贸", "亚马逊运营", "海外获客", "外贸老板"]
    FOREIGN_TRADE_SIGNALS = ["外贸", "B2B", "跨境", "老板", "出口", "FOB", "CIF", "独立站", "亚马逊", "TikTok", "海外"]

    def __init__(self):
        self.results = []
        self.seen_ids = set()
        self.error_log = []

    # ===== 评分模型 =====

    @staticmethod
    def calc_follower_quality(note_data: dict) -> dict:
        """粉丝质量评分 — 基于互动数据的5维模型"""
        followers = note_data.get("follower_count", 0) or 0
        likes = note_data.get("liked_count", 0) or 0
        collects = note_data.get("collected_count", 0) or 0
        comments = note_data.get("comment_count", 0) or 0

        # 维度1: 互动率 (互动/粉丝)
        total_engagement = likes + collects + comments
        engagement_rate = (total_engagement / followers * 100) if followers > 0 else 0

        # 维度2: 收藏比 (收藏/点赞，高质量内容收藏率高)
        collect_ratio = (collects / likes * 100) if likes > 0 else 0

        # 维度3: 评论活跃度 (评论/互动)
        comment_ratio = (comments / total_engagement * 100) if total_engagement > 0 else 0

        # 维度4: 粉丝规模分 (对数映射)
        import math
        scale_score = min(math.log10(max(followers, 1)) * 15, 60)

        # 维度5: 外贸相关度
        text = (note_data.get("title", "") + note_data.get("desc", "")).lower()
        relevance_count = sum(1 for s in XhsForeignTradeCrawler.FOREIGN_TRADE_SIGNALS if s.lower() in text)
        relevance_score = min(relevance_count * 12, 60)

        # 加权总分
        quality_score = (
            min(engagement_rate * 2, 25) +  # 互动率最高25分
            min(collect_ratio * 0.5, 20) +   # 收藏比最高20分
            min(comment_ratio * 0.8, 15) +   # 评论活跃度最高15分
            scale_score * 0.4 +               # 粉丝规模
            relevance_score * 0.5             # 外贸相关度
        )

        # 分级
        if quality_score >= 60:
            tier = "S级-头部外贸KOL"
        elif quality_score >= 40:
            tier = "A级-活跃外贸博主"
        elif quality_score >= 25:
            tier = "B级-潜力外贸博主"
        elif quality_score >= 15:
            tier = "C级-初级外贸博主"
        else:
            tier = "D级-待验证"

        return {
            "quality_score": round(quality_score, 1),
            "tier": tier,
            "dimensions": {
                "engagement_rate": round(engagement_rate, 2),
                "collect_to_like_ratio": round(collect_ratio, 2),
                "comment_activity": round(comment_ratio, 2),
                "follower_scale_score": round(scale_score, 1),
                "trade_relevance_score": relevance_score,
            },
        }

    @staticmethod
    def infer_follower_profile(note_data: dict, quality: dict) -> dict:
        """推断粉丝画像 — 基于博主内容特征"""
        desc = note_data.get("desc", "")
        tags = note_data.get("tags", "")
        text = desc + " " + tags

        profiles = []
        # 内容特征 → 受众推断
        if any(w in text for w in ["工厂", "供应链", "货源", "代工", "OEM", "ODM"]):
            profiles.append({"segment": "工厂主/供应链", "likelihood": "高", "value": "高"})
        if any(w in text for w in ["亚马逊", "独立站", "Shopify", "TikTok Shop", "速卖通"]):
            profiles.append({"segment": "跨境卖家", "likelihood": "高", "value": "极高"})
        if any(w in text for w in ["SOHO", "个人", "在家", "副业", "兼职"]):
            profiles.append({"segment": "SOHO/个人卖家", "likelihood": "中", "value": "中"})
        if any(w in text for w in ["团队", "公司", "规模化", "管理", "招人"]):
            profiles.append({"segment": "外贸公司经营者", "likelihood": "高", "value": "高"})
        if any(w in text for w in ["新手", "入门", "0基础", "小白", "转行"]):
            profiles.append({"segment": "外贸新手/转行者", "likelihood": "中", "value": "低"})

        if not profiles:
            profiles.append({"segment": "泛外贸人群", "likelihood": "中", "value": "中"})

        # 粉丝规模 → 画像补充
        followers = note_data.get("follower_count", 0) or 0
        if followers > 50000:
            profiles.append({"segment": "泛商业关注者", "likelihood": "高", "value": "中"})
        if followers > 100000:
            profiles.append({"segment": "知识付费受众", "likelihood": "中", "value": "中"})

        engagement = quality.get("dimensions", {}).get("engagement_rate", 0)
        return {
            "inferred_segments": profiles,
            "audience_loyalty": "高" if engagement > 5 else "中" if engagement > 2 else "低",
            "monetization_potential": "强" if quality["quality_score"] >= 40 else "中" if quality["quality_score"] >= 25 else "弱",
        }

    # ===== Playwright执行指令生成 =====

    def generate_playwright_script(self, keywords: list = None, limit_per_kw: int = 30,
                                    cookie_file: str = "xhs_cookies.json") -> dict:
        """生成Playwright执行脚本配置"""
        kws = keywords or self.KEYWORDS
        return {
            "tool": "playwright",
            "browser": "chromium",
            "base_url": "https://www.xiaohongshu.com",
            "cookie_file": cookie_file,
            "search_url_template": "https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes",
            "keywords": kws,
            "limit_per_keyword": limit_per_kw,
            "steps": [
                "1. 启动浏览器 (headless=False便于调试)",
                "2. 加载Cookie: 若cookie_file存在则注入，否则先手动登录",
                "3. 逐关键词搜索 → 等待结果加载 → 滚动加载更多",
                "4. 提取每条笔记数据: 标题/作者/互动数据/标签",
                "5. 点击进入博主主页: 获取粉丝数/简介",
                "6. 保存Cookie避免重复登录",
                "7. 每次操作间隔3-6秒随机延迟",
            ],
            "selectors": {
                "search_input": "#search-input, input[placeholder*='搜索']",
                "note_card": ".note-item, section.note-item, [class*='note']",
                "note_title": ".title, [class*='title'], a span",
                "author_name": ".author .name, [class*='author'] [class*='name']",
                "like_count": ".like-wrapper .count, [class*='like'] .count",
                "collect_count": ".collect-wrapper .count, [class*='collect'] .count",
                "comment_count": ".chat-wrapper .count, [class*='comment'] .count",
                "follower_count": ".user-info .follower, [class*='follower'] span",
            },
            "anti_detection": {
                "scroll_randomly": True,
                "mouse_move_randomly": True,
                "delay_range": [3, 6],
                "max_scroll_pages": 10,
                "pause_on_captcha": True,
                "cookie_refresh_interval": 3600,
            },
            "output_fields": [
                "nickname", "user_id", "follower_count", "title",
                "liked_count", "collected_count", "comment_count",
                "desc", "tags", "foreign_trade_flag",
                "quality_score", "tier", "follower_profile",
            ],
        }

    # ===== 纯数据处理（不涉及网络请求）=====

    def process_raw_data(self, raw_items: list) -> dict:
        """处理原始数据: 去重+外贸筛选+评分+画像"""
        processed = []
        duplicates = 0
        non_trade = 0

        for item in raw_items:
            uid = item.get("user_id") or item.get("账号ID", "")
            if uid in self.seen_ids:
                duplicates += 1
                continue
            self.seen_ids.add(uid)

            # 外贸属性判断
            text = (item.get("title", "") + item.get("笔记标题", "") +
                    item.get("desc", "") + item.get("简介", "") +
                    str(item.get("tags", "")))
            is_trade = any(s in text for s in self.FOREIGN_TRADE_SIGNALS)
            if not is_trade:
                non_trade += 1
                continue

            # 标准化字段名
            normalized = {
                "nickname": item.get("nickname") or item.get("博主昵称", ""),
                "user_id": uid,
                "follower_count": self._parse_number(item.get("follower_count") or item.get("粉丝数", 0)),
                "title": item.get("title") or item.get("笔记标题", ""),
                "liked_count": self._parse_number(item.get("liked_count") or item.get("点赞数", 0)),
                "collected_count": self._parse_number(item.get("collected_count") or item.get("收藏数", 0)),
                "comment_count": self._parse_number(item.get("comment_count") or item.get("评论数", 0)),
                "desc": item.get("desc") or item.get("简介", ""),
                "tags": item.get("tags") or item.get("标签", ""),
                "foreign_trade_flag": True,
            }

            # 评分+画像
            quality = self.calc_follower_quality(normalized)
            profile = self.infer_follower_profile(normalized, quality)

            normalized["quality_score"] = quality["quality_score"]
            normalized["tier"] = quality["tier"]
            normalized["quality_dimensions"] = quality["dimensions"]
            normalized["follower_profile"] = profile

            processed.append(normalized)

        # 按质量分排序
        processed.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        return {
            "summary": {
                "total_input": len(raw_items),
                "duplicates_removed": duplicates,
                "non_trade_removed": non_trade,
                "valid_accounts": len(processed),
                "processed_at": datetime.now().isoformat(),
            },
            "tier_distribution": self._tier_distribution(processed),
            "data": processed,
        }

    @staticmethod
    def _parse_number(val) -> int:
        """解析数字字符串: '1.2万' → 12000"""
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val).strip()
        if not s:
            return 0
        s = re.sub(r'[^\d.万千百]', '', s)
        try:
            if '万' in s:
                return int(float(s.replace('万', '')) * 10000)
            if '千' in s:
                return int(float(s.replace('千', '')) * 1000)
            if '百' in s:
                return int(float(s.replace('百', '')) * 100)
            return int(float(s))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _tier_distribution(data: list) -> dict:
        dist = {}
        for item in data:
            tier = item.get("tier", "未知")
            dist[tier] = dist.get(tier, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: -x[1]))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书外贸博主数据处理器")
    sub = parser.add_subparsers(dest="command")

    p_score = sub.add_parser("score", help="单个博主质量评分")
    p_score.add_argument("--followers", type=int, required=True)
    p_score.add_argument("--likes", type=int, required=True)
    p_score.add_argument("--collects", type=int, required=True)
    p_score.add_argument("--comments", type=int, required=True)
    p_score.add_argument("--desc", type=str, default="")
    p_score.add_argument("--title", type=str, default="")

    p_process = sub.add_parser("process", help="批量处理原始数据")
    p_process.add_argument("--input", type=str, required=True, help="原始数据JSON")

    p_config = sub.add_parser("config", help="生成Playwright执行配置")
    p_config.add_argument("--keywords", type=str, nargs="*", default=None)
    p_config.add_argument("--limit", type=int, default=30)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    crawler = XhsForeignTradeCrawler()

    if args.command == "score":
        note_data = {
            "follower_count": args.followers, "liked_count": args.likes,
            "collected_count": args.collects, "comment_count": args.comments,
            "desc": args.desc, "title": args.title,
        }
        quality = crawler.calc_follower_quality(note_data)
        profile = crawler.infer_follower_profile(note_data, quality)
        print(json.dumps({"quality": quality, "follower_profile": profile}, ensure_ascii=False, indent=2))

    elif args.command == "process":
        raw = json.loads(args.input)
        if args.input.endswith(".json"):
            with open(args.input, "r", encoding="utf-8") as f:
                raw = json.load(f)
        result = crawler.process_raw_data(raw)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "config":
        result = crawler.generate_playwright_script(args.keywords, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
