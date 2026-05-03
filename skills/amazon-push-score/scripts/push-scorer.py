#!/usr/bin/env python3
"""
亚马逊推广效果评分器 - Level 2
Amazon Push Score Calculator

功能：
- score: 推广效果评分（曝光/点击/转化/ROI/复购 5维）
- strategy: 推广策略建议
- budget-optimize: 预算分配优化

Author: Amazon Push Score Team
Version: 1.0.0
"""

import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ScoreLevel(Enum):
    """评分等级"""
    EXCELLENT = "优秀"    # 90-100
    GOOD = "良好"         # 75-89
    AVERAGE = "一般"      # 60-74
    POOR = "较差"         # 40-59
    VERY_POOR = "很差"    # 0-39


@dataclass
class DimensionScore:
    """维度评分"""
    dimension: str
    score: float
    weight: float
    level: ScoreLevel
    metrics: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class PushScoreReport:
    """推送分报告"""
    overall_score: float
    overall_level: ScoreLevel
    dimensions: List[DimensionScore]
    traffic_pool: str  # 流量池等级
    priority_actions: List[str]
    budget_recommendations: Dict[str, Any]


class PushScoreCalculator:
    """推广效果评分器"""
    
    # 各维度权重
    DIMENSION_WEIGHTS = {
        "曝光": 0.25,
        "点击": 0.20,
        "转化": 0.25,
        "ROI": 0.20,
        "复购": 0.10
    }
    
    # 流量池等级划分
    TRAFFIC_POOL_THRESHOLDS = {
        "冷启动池": 40,
        "潜力池": 60,
        "增长池": 75,
        "主力池": 85,
        "爆款池": 95
    }
    
    # 评分基准（行业平均水平）
    BENCHMARKS = {
        "曝光": {
            "impressions": 10000,  # 日均曝光
            "impression_share": 0.15  # 展示份额
        },
        "点击": {
            "ctr": 0.005,  # 点击率 0.5%
            "click_rank": 5000  # 点击排名
        },
        "转化": {
            "cvr": 0.10,  # 转化率 10%
            "conversion_rank": 1000  # 转化排名
        },
        "ROI": {
            "acos": 0.25,  # ACOS 25%
            "roas": 4.0  # ROAS 4x
        },
        "复购": {
            "repurchase_rate": 0.05,  # 复购率 5%
            "review_score": 4.3  # 评分
        }
    }
    
    def __init__(self):
        self.current_report: Optional[PushScoreReport] = None
    
    def calculate_dimension_score(self, dimension: str, 
                                  metrics: Dict[str, float]) -> DimensionScore:
        """
        计算单维度评分
        
        Args:
            dimension: 维度名称
            metrics: 指标数据
        
        Returns:
            维度评分结果
        """
        benchmark = self.BENCHMARKS.get(dimension, {})
        score = 50  # 基础分
        level_metrics = {}
        suggestions = []
        
        if dimension == "曝光":
            score, level_metrics, suggestions = self._calc_exposure_score(metrics, benchmark)
        elif dimension == "点击":
            score, level_metrics, suggestions = self._calc_click_score(metrics, benchmark)
        elif dimension == "转化":
            score, level_metrics, suggestions = self._calc_conversion_score(metrics, benchmark)
        elif dimension == "ROI":
            score, level_metrics, suggestions = self._calc_roi_score(metrics, benchmark)
        elif dimension == "复购":
            score, level_metrics, suggestions = self._calc_repurchase_score(metrics, benchmark)
        
        level = self._get_score_level(score)
        
        return DimensionScore(
            dimension=dimension,
            score=round(score, 1),
            weight=self.DIMENSION_WEIGHTS[dimension],
            level=level,
            metrics=level_metrics,
            suggestions=suggestions
        )
    
    def _calc_exposure_score(self, metrics: Dict, benchmark: Dict) -> Tuple[float, Dict, List[str]]:
        """计算曝光维度评分"""
        impressions = metrics.get("impressions", 0)
        benchmark_impressions = benchmark.get("impressions", 10000)
        impression_share = metrics.get("impression_share", 0)
        benchmark_share = benchmark.get("impression_share", 0.15)
        
        # 曝光量得分
        if impressions >= benchmark_impressions * 3:
            volume_score = 100
        elif impressions >= benchmark_impressions:
            volume_score = 70 + 30 * (impressions / (benchmark_impressions * 3))
        elif impressions >= benchmark_impressions * 0.5:
            volume_score = 50 + 20 * (impressions / benchmark_impressions)
        else:
            volume_score = max(10, 50 * (impressions / (benchmark_impressions * 0.5)))
        
        # 展示份额得分
        if impression_share >= benchmark_share * 2:
            share_score = 100
        elif impression_share >= benchmark_share:
            share_score = 75 + 25 * (impression_share / (benchmark_share * 2))
        else:
            share_score = max(20, 75 * (impression_share / benchmark_share))
        
        score = volume_score * 0.6 + share_score * 0.4
        
        level_metrics = {
            "日均曝光": f"{impressions:,}",
            "基准曝光": f"{benchmark_impressions:,}",
            "曝光达标率": f"{impressions/benchmark_impressions*100:.1f}%",
            "展示份额": f"{impression_share*100:.2f}%" if impression_share else "N/A"
        }
        
        suggestions = []
        if volume_score < 60:
            suggestions.append("提升关键词竞价以增加曝光量")
            suggestions.append("扩展关键词覆盖面")
        if share_score < 60:
            suggestions.append("优化listing质量分提升展示份额")
        
        return score, level_metrics, suggestions
    
    def _calc_click_score(self, metrics: Dict, benchmark: Dict) -> Tuple[float, Dict, List[str]]:
        """计算点击维度评分"""
        ctr = metrics.get("ctr", 0)
        benchmark_ctr = benchmark.get("ctr", 0.005)
        clicks = metrics.get("clicks", 0)
        
        # CTR得分
        if ctr >= benchmark_ctr * 2:
            ctr_score = 100
        elif ctr >= benchmark_ctr:
            ctr_score = 70 + 30 * (ctr / (benchmark_ctr * 2))
        elif ctr >= benchmark_ctr * 0.5:
            ctr_score = 50 + 20 * (ctr / benchmark_ctr)
        else:
            ctr_score = max(10, 50 * (ctr / (benchmark_ctr * 0.5)))
        
        # 点击量得分
        min_clicks = 50  # 最低点击量
        if clicks >= 200:
            clicks_score = 100
        elif clicks >= min_clicks:
            clicks_score = 50 + 50 * (clicks - min_clicks) / (200 - min_clicks)
        else:
            clicks_score = max(10, 50 * clicks / min_clicks)
        
        score = ctr_score * 0.7 + clicks_score * 0.3
        
        level_metrics = {
            "点击率": f"{ctr*100:.2f}%" if ctr else "N/A",
            "基准CTR": f"{benchmark_ctr*100:.2f}%",
            "CTR达标率": f"{ctr/benchmark_ctr*100:.1f}%" if ctr else "N/A",
            "点击量": f"{clicks:,}" if clicks else "N/A"
        }
        
        suggestions = []
        if ctr_score < 60:
            suggestions.append("优化主图以提升点击率")
            suggestions.append("检查标题是否有吸引力")
        if clicks_score < 60:
            suggestions.append("增加曝光同时注重精准度")
        
        return score, level_metrics, suggestions
    
    def _calc_conversion_score(self, metrics: Dict, benchmark: Dict) -> Tuple[float, Dict, List[str]]:
        """计算转化维度评分"""
        cvr = metrics.get("cvr", 0)
        benchmark_cvr = benchmark.get("cvr", 0.10)
        orders = metrics.get("orders", 0)
        
        # CVR得分
        if cvr >= benchmark_cvr * 1.5:
            cvr_score = 100
        elif cvr >= benchmark_cvr:
            cvr_score = 75 + 25 * (cvr / (benchmark_cvr * 1.5))
        elif cvr >= benchmark_cvr * 0.7:
            cvr_score = 50 + 25 * (cvr / benchmark_cvr)
        else:
            cvr_score = max(15, 50 * (cvr / (benchmark_cvr * 0.7)))
        
        # 订单量得分
        min_orders = 5
        if orders >= 50:
            orders_score = 100
        elif orders >= min_orders:
            orders_score = 50 + 50 * (orders - min_orders) / (50 - min_orders)
        else:
            orders_score = max(10, 50 * orders / min_orders)
        
        score = cvr_score * 0.7 + orders_score * 0.3
        
        level_metrics = {
            "转化率": f"{cvr*100:.2f}%" if cvr else "N/A",
            "基准CVR": f"{benchmark_cvr*100:.2f}%",
            "CVR达标率": f"{cvr/benchmark_cvr*100:.1f}%" if cvr else "N/A",
            "订单量": f"{orders}" if orders else "N/A"
        }
        
        suggestions = []
        if cvr_score < 60:
            suggestions.append("优化listing详情内容")
            suggestions.append("检查价格竞争力")
            suggestions.append("分析评价情况")
        
        return score, level_metrics, suggestions
    
    def _calc_roi_score(self, metrics: Dict, benchmark: Dict) -> Tuple[float, Dict, List[str]]:
        """计算ROI维度评分"""
        acos = metrics.get("acos", 1.0)  # 默认100% ACOS
        roas = metrics.get("roas", 0)
        benchmark_acos = benchmark.get("acos", 0.25)
        benchmark_roas = benchmark.get("roas", 4.0)
        
        # ACOS得分（越低越好）
        if acos <= benchmark_acos * 0.5:
            acos_score = 100
        elif acos <= benchmark_acos:
            acos_score = 75 + 25 * (1 - acos/benchmark_acos) / 0.5
        elif acos <= benchmark_acos * 1.5:
            acos_score = 50 + 25 * (1 - (acos - benchmark_acos) / (benchmark_acos * 0.5))
        else:
            acos_score = max(10, 50 * benchmark_acos / acos)
        
        # ROAS得分（越高越好）
        if roas >= benchmark_roas * 2:
            roas_score = 100
        elif roas >= benchmark_roas:
            roas_score = 70 + 30 * (roas - benchmark_roas) / benchmark_roas
        elif roas >= benchmark_roas * 0.5:
            roas_score = 40 + 30 * (roas - benchmark_roas * 0.5) / (benchmark_roas * 0.5)
        else:
            roas_score = max(10, 40 * roas / (benchmark_roas * 0.5))
        
        score = acos_score * 0.5 + roas_score * 0.5
        
        level_metrics = {
            "ACOS": f"{acos*100:.1f}%" if acos else "N/A",
            "基准ACOS": f"{benchmark_acos*100:.1f}%",
            "ROAS": f"{roas:.2f}x" if roas else "N/A",
            "基准ROAS": f"{benchmark_roas:.2f}x"
        }
        
        suggestions = []
        if acos > benchmark_acos * 1.2:
            suggestions.append("优化关键词精准度降低ACOS")
            suggestions.append("调整投放策略聚焦高效词")
        if roas < benchmark_roas * 0.8:
            suggestions.append("重新审视出价策略")
        
        return score, level_metrics, suggestions
    
    def _calc_repurchase_score(self, metrics: Dict, benchmark: Dict) -> Tuple[float, Dict, List[str]]:
        """计算复购维度评分"""
        repurchase_rate = metrics.get("repurchase_rate", 0)
        benchmark_rate = benchmark.get("repurchase_rate", 0.05)
        review_score = metrics.get("review_score", 0)
        benchmark_review = benchmark.get("review_score", 4.3)
        review_count = metrics.get("review_count", 0)
        
        # 复购率得分
        if repurchase_rate >= benchmark_rate * 2:
            rate_score = 100
        elif repurchase_rate >= benchmark_rate:
            rate_score = 75 + 25 * (repurchase_rate / (benchmark_rate * 2))
        elif repurchase_rate >= benchmark_rate * 0.5:
            rate_score = 50 + 25 * (repurchase_rate / benchmark_rate)
        else:
            rate_score = max(15, 50 * repurchase_rate / (benchmark_rate * 0.5))
        
        # 评分得分
        if review_score >= 4.8:
            review_score_level = 100
        elif review_score >= 4.5:
            review_score_level = 85 + 15 * (review_score - 4.5) / 0.3
        elif review_score >= 4.0:
            review_score_level = 60 + 25 * (review_score - 4.0) / 0.5
        else:
            review_score_level = max(20, 60 * review_score / 4.0)
        
        # 评论数量权重
        count_factor = min(1.0, review_count / 100)
        
        score = rate_score * 0.5 + review_score_level * 0.4 + count_factor * 10
        
        level_metrics = {
            "复购率": f"{repurchase_rate*100:.2f}%" if repurchase_rate else "N/A",
            "基准复购率": f"{benchmark_rate*100:.2f}%",
            "星级评分": f"{review_score:.1f}" if review_score else "N/A",
            "评论数量": f"{review_count:,}" if review_count else "N/A"
        }
        
        suggestions = []
        if review_score < 4.3:
            suggestions.append("关注并回复负面评价")
            suggestions.append("优化产品品质减少差评")
        if repurchase_rate < benchmark_rate * 0.7:
            suggestions.append("考虑设置会员权益提升复购")
        
        return score, level_metrics, suggestions
    
    def _get_score_level(self, score: float) -> ScoreLevel:
        """获取评分等级"""
        if score >= 90:
            return ScoreLevel.EXCELLENT
        elif score >= 75:
            return ScoreLevel.GOOD
        elif score >= 60:
            return ScoreLevel.AVERAGE
        elif score >= 40:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR
    
    def calculate_overall_score(self, dimension_scores: List[DimensionScore]) -> float:
        """计算综合评分"""
        total = 0
        for ds in dimension_scores:
            total += ds.score * ds.weight
        return round(total, 1)
    
    def determine_traffic_pool(self, score: float) -> str:
        """确定流量池等级"""
        if score >= self.TRAFFIC_POOL_THRESHOLDS["爆款池"]:
            return "爆款池"
        elif score >= self.TRAFFIC_POOL_THRESHOLDS["主力池"]:
            return "主力池"
        elif score >= self.TRAFFIC_POOL_THRESHOLDS["增长池"]:
            return "增长池"
        elif score >= self.TRAFFIC_POOL_THRESHOLDS["潜力池"]:
            return "潜力池"
        else:
            return "冷启动池"
    
    def score(self, metrics: Dict[str, Any]) -> PushScoreReport:
        """
        执行完整评分
        
        Args:
            metrics: 推广指标数据
        
        Returns:
            评分报告
        """
        dimension_scores = []
        
        for dimension in self.DIMENSION_WEIGHTS.keys():
            dim_metrics = metrics.get(dimension, {})
            ds = self.calculate_dimension_score(dimension, dim_metrics)
            dimension_scores.append(ds)
        
        overall_score = self.calculate_overall_score(dimension_scores)
        overall_level = self._get_score_level(overall_score)
        traffic_pool = self.determine_traffic_pool(overall_score)
        
        # 生成优先行动
        priority_actions = self._generate_priority_actions(dimension_scores)
        
        # 预算建议
        budget_recommendations = self._generate_budget_recommendations(dimension_scores, metrics)
        
        self.current_report = PushScoreReport(
            overall_score=overall_score,
            overall_level=overall_level,
            dimensions=dimension_scores,
            traffic_pool=traffic_pool,
            priority_actions=priority_actions,
            budget_recommendations=budget_recommendations
        )
        
        return self.current_report
    
    def _generate_priority_actions(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """生成优先行动"""
        # 按分数排序，找出最弱的维度
        sorted_dims = sorted(dimension_scores, key=lambda x: x.score)
        
        actions = []
        for dim in sorted_dims[:3]:
            if dim.score < 75:
                for suggestion in dim.suggestions[:2]:
                    if suggestion not in actions:
                        actions.append(suggestion)
        
        return actions[:5]
    
    def _generate_budget_recommendations(self, dimension_scores: List[DimensionScore],
                                        metrics: Dict) -> Dict[str, Any]:
        """生成预算建议"""
        # 找出需要投入的维度
        low_dims = [d for d in dimension_scores if d.score < 70]
        
        if not low_dims:
            return {
                "action": "维持",
                "message": "当前各维度表现良好，保持现有预算分配",
                "suggestions": ["保持当前投放策略", "关注日常数据关注"]
            }
        
        # 计算推荐预算调整
        total_budget = metrics.get("total_budget", 10000)
        
        recommendations = {
            "action": "优化调整",
            "current_budget": total_budget,
            "suggestions": []
        }
        
        for dim in low_dims[:2]:
            if dim.dimension == "曝光":
                recommendations["suggestions"].append(
                    f"增加{dim.weight*100:.0f}%预算用于提升曝光"
                )
            elif dim.dimension == "点击":
                recommendations["suggestions"].append(
                    "优化创意素材提升点击率"
                )
            elif dim.dimension == "转化":
                recommendations["suggestions"].append(
                    "优化落地页和促销策略"
                )
            elif dim.dimension == "ROI":
                recommendations["suggestions"].append(
                    "调整关键词出价优化ROI"
                )
        
        return recommendations
    
    def suggest_strategy(self) -> Dict[str, Any]:
        """生成推广策略建议"""
        if not self.current_report:
            return {"error": "请先执行评分"}
        
        report = self.current_report
        
        # 基于流量池和短板生成策略
        strategies = {
            "冷启动池": {
                "focus": "破冰",
                "tactics": ["提升曝光量", "积累基础数据", "优化基础指标"]
            },
            "潜力池": {
                "focus": "突破",
                "tactics": ["优化点击率", "提升转化效率", "精准关键词"]
            },
            "增长池": {
                "focus": "扩张",
                "tactics": ["扩大投放规模", "拓展关键词", "多广告类型"]
            },
            "主力池": {
                "focus": "优化",
                "tactics": ["精细化运营", "提升ROI", "稳定排名"]
            },
            "爆款池": {
                "focus": "防守",
                "tactics": ["维护排名", "关注同行", "持续优化"]
            }
        }
        
        strategy = strategies.get(report.traffic_pool, strategies["潜力池"])
        
        # 添加针对性建议
        low_dims = [d.dimension for d in report.dimensions if d.score < 70]
        
        return {
            "traffic_pool": report.traffic_pool,
            "overall_strategy": strategy["focus"],
            "core_tactics": strategy["tactics"],
            "focus_areas": low_dims,
            "action_plan": report.priority_actions
        }
    
    def optimize_budget(self, total_budget: float = None) -> Dict[str, Any]:
        """优化预算分配"""
        if not self.current_report:
            return {"error": "请先执行评分"}
        
        report = self.current_report
        
        if total_budget is None:
            total_budget = report.budget_recommendations.get("current_budget", 10000)
        
        # 基于各维度评分计算权重
        dim_weights = []
        for dim in report.dimensions:
            # 分数越低，分配越高
            if dim.score < 40:
                adjusted_weight = dim.weight * 2
            elif dim.score < 60:
                adjusted_weight = dim.weight * 1.5
            elif dim.score < 80:
                adjusted_weight = dim.weight * 1.0
            else:
                adjusted_weight = dim.weight * 0.8
            dim_weights.append((dim.dimension, dim.weight, dim.score, adjusted_weight))
        
        # 归一化
        total_adjusted = sum(w[3] for w in dim_weights)
        allocations = []
        
        for dim, orig_w, score, adj_w in dim_weights:
            budget = total_budget * (adj_w / total_adjusted)
            allocations.append({
                "dimension": dim,
                "original_weight": f"{orig_w*100:.0f}%",
                "current_score": score,
                "recommended_budget": round(budget, 2),
                "recommended_ratio": f"{adj_w/total_adjusted*100:.1f}%"
            })
        
        return {
            "total_budget": total_budget,
            "allocations": allocations,
            "summary": "预算向低分维度倾斜，提升整体表现"
        }
    
    def format_report(self, report: PushScoreReport) -> str:
        """格式化报告输出"""
        output = []
        output.append("=" * 70)
        output.append("亚马逊推广效果评分报告")
        output.append("=" * 70)
        
        output.append(f"\n【综合评分】{report.overall_score}分 ({report.overall_level.value})")
        output.append(f"【流量池】{report.traffic_pool}")
        
        output.append(f"\n【各维度评分】")
        for dim in report.dimensions:
            bar = "█" * int(dim.score/5) + "░" * (20 - int(dim.score/5))
            output.append(f"\n  {dim.dimension}: [{bar}] {dim.score}分 ({dim.level.value})")
            output.append(f"    权重: {dim.weight*100:.0f}%")
            for key, val in list(dim.metrics.items())[:2]:
                output.append(f"    {key}: {val}")
        
        output.append(f"\n【优先行动】")
        for action in report.priority_actions[:5]:
            output.append(f"  → {action}")
        
        output.append("\n" + "=" * 70)
        return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python push-scorer.py <command> [args]")
        print("命令:")
        print("  score            - 推广效果评分")
        print("  strategy         - 推广策略建议")
        print("  budget-optimize  - 预算分配优化")
        return
    
    command = sys.argv[1]
    calculator = PushScoreCalculator()
    
    # 示例数据
    sample_metrics = {
        "曝光": {
            "impressions": 15000,
            "impression_share": 0.18
        },
        "点击": {
            "ctr": 0.006,
            "clicks": 90
        },
        "转化": {
            "cvr": 0.12,
            "orders": 11
        },
        "ROI": {
            "acos": 0.28,
            "roas": 3.5
        },
        "复购": {
            "repurchase_rate": 0.04,
            "review_score": 4.2,
            "review_count": 50
        },
        "total_budget": 10000
    }
    
    if command == "score":
        report = calculator.score(sample_metrics)
        print(calculator.format_report(report))
        
    elif command == "strategy":
        calculator.score(sample_metrics)
        strategy = calculator.suggest_strategy()
        
        print("=" * 70)
        print("推广策略建议")
        print("=" * 70)
        print(f"\n当前流量池: {strategy['traffic_pool']}")
        print(f"核心策略: {strategy['overall_strategy']}")
        print(f"\n核心战术:")
        for tactic in strategy['core_tactics']:
            print(f"  • {tactic}")
        print(f"\n重点提升维度: {', '.join(strategy['focus_areas'])}")
        print(f"\n行动计划:")
        for action in strategy['action_plan']:
            print(f"  → {action}")
    
    elif command == "budget-optimize":
        calculator.score(sample_metrics)
        result = calculator.optimize_budget(10000)
        
        print("=" * 70)
        print("预算分配优化")
        print("=" * 70)
        print(f"\n总预算: ¥{result['total_budget']:,.2f}")
        print(f"\n优化方案:")
        for alloc in result['allocations']:
            print(f"\n  {alloc['dimension']}")
            print(f"    原权重: {alloc['original_weight']}")
            print(f"    当前评分: {alloc['current_score']}分")
            print(f"    建议预算: ¥{alloc['recommended_budget']:,.2f} ({alloc['recommended_ratio']})")
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
