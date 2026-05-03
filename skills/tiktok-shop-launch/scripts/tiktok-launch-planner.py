#!/usr/bin/env python3
"""
TikTok Shop开店准备度评估器 - Level 2
TikTok Shop Launch Readiness Planner

功能：
- readiness: 开店准备度评分（资质/选品/内容/物流/客服 5维）
- checklist: 入驻清单生成
- cold-start: 冷启动策略

Author: TikTok Shop Team
Version: 1.0.0
"""

import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ReadinessLevel(Enum):
    """准备度等级"""
    READY = "准备就绪"
    MOSTLY_READY = "基本就绪"
    PARTIALLY_READY = "部分就绪"
    NOT_READY = "未准备充分"
    NOT_STARTED = "未开始"


@dataclass
class DimensionReadiness:
    """维度准备度"""
    dimension: str
    score: float  # 0-100
    level: ReadinessLevel
    completed_items: List[str] = field(default_factory=list)
    pending_items: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReadinessReport:
    """准备度报告"""
    overall_score: float
    overall_level: ReadinessLevel
    dimensions: List[DimensionReadiness]
    checklist: List[Dict]
    estimated_launch_date: str
    blockers_summary: List[str]


class TikTokLaunchPlanner:
    """TikTok Shop开店准备度规划器"""
    
    DIMENSIONS = [
        {"id": "qualification", "name": "资质认证", "weight": 0.25},
        {"id": "product", "name": "选品规划", "weight": 0.25},
        {"id": "content", "name": "内容创作", "weight": 0.20},
        {"id": "logistics", "name": "物流配送", "weight": 0.15},
        {"id": "customer_service", "name": "客服体系", "weight": 0.15}
    ]
    
    # 各维度检查项
    CHECKLIST_TEMPLATES = {
        "qualification": [
            {"id": "q1", "item": "营业执照（真实在营）", "required": True},
            {"id": "q2", "item": "法人身份证信息", "required": True},
            {"id": "q3", "item": "银行账户信息", "required": True},
            {"id": "q4", "item": "品牌授权书（如适用）", "required": False},
            {"id": "q5", "item": "产品合规认证", "required": True},
            {"id": "q6", "item": "税务登记证明", "required": True},
            {"id": "q7", "item": "店铺命名符合规范", "required": True}
        ],
        "product": [
            {"id": "p1", "item": "确定目标品类", "required": True},
            {"id": "p2", "item": "完成选品调研", "required": True},
            {"id": "p3", "item": "确定SKU结构", "required": True},
            {"id": "p4", "item": "完成产品定价", "required": True},
            {"id": "p5", "item": "准备产品图片（白底+场景图）", "required": True},
            {"id": "p6", "item": "编写产品描述", "required": True},
            {"id": "p7", "item": "准备库存", "required": True}
        ],
        "content": [
            {"id": "c1", "item": "账号基础设置完成", "required": True},
            {"id": "c2", "item": "账号定位明确", "required": True},
            {"id": "c3", "item": "准备内容素材库（≥20条）", "required": True},
            {"id": "c4", "item": "达人合作资源", "required": False},
            {"id": "c5", "item": "直播脚本模板", "required": True},
            {"id": "c6", "item": "短视频剪辑工具", "required": True},
            {"id": "c7", "item": "账号人设打造", "required": False}
        ],
        "logistics": [
            {"id": "l1", "item": "仓储解决方案确定", "required": True},
            {"id": "l2", "item": "物流服务商对接", "required": True},
            {"id": "l3", "item": "发货时效承诺设定", "required": True},
            {"id": "l4", "item": "退换货政策制定", "required": True},
            {"id": "l5", "item": "打包材料准备", "required": True}
        ],
        "customer_service": [
            {"id": "cs1", "item": "客服团队/工具就位", "required": True},
            {"id": "cs2", "item": "FAQ常见问题准备", "required": True},
            {"id": "cs3", "item": "话术脚本制定", "required": True},
            {"id": "cs4", "item": "自动回复设置", "required": True},
            {"id": "cs5", "item": "差评处理预案", "required": True}
        ]
    }
    
    # 市场特定配置
    MARKET_CONFIG = {
        "美区": {
            "registration_time": "7-14天",
            "min_investment": 50000,
            "key_requirements": ["美国本土资质", "SSN或EIN", "仓储在美"]
        },
        "东南亚": {
            "registration_time": "3-7天",
            "min_investment": 20000,
            "key_requirements": ["当地营业执照", "银行账户", "本地仓或云仓"]
        },
        "英国": {
            "registration_time": "5-10天",
            "min_investment": 40000,
            "key_requirements": ["UK资质", "VAT号", "合规产品"]
        }
    }
    
    def __init__(self):
        self.current_report: Optional[ReadinessReport] = None
    
    def assess_readiness(self, market: str, status: Dict[str, List[str]]) -> ReadinessReport:
        """
        评估准备度
        
        Args:
            market: 目标市场
            status: 各维度完成项（item_id列表）
        
        Returns:
            准备度报告
        """
        dimensions = []
        all_checklist = []
        
        for dim_config in self.DIMENSIONS:
            dim_id = dim_config["id"]
            dim_name = dim_config["name"]
            
            # 获取检查项
            template = self.CHECKLIST_TEMPLATES.get(dim_id, [])
            completed = status.get(dim_id, [])
            
            # 计算完成情况
            total_items = len(template)
            required_items = [t for t in template if t["required"]]
            completed_required = [t for t in required_items if t["id"] in completed]
            
            # 计算分数
            if total_items == 0:
                score = 50
            else:
                # 必选项占70%，可选项占30%
                required_score = len(completed_required) / len(required_items) * 70 if required_items else 70
                optional_items = [t for t in template if not t["required"]]
                completed_optional = [t for t in optional_items if t["id"] in completed]
                optional_score = len(completed_optional) / len(optional_items) * 30 if optional_items else 30
                score = required_score + optional_score
            
            # 找出未完成项和阻碍项
            pending_items = [t for t in template if t["id"] not in completed]
            blockers = [t["item"] for t in pending_items if t["required"]]
            
            # 确定等级
            level = self._get_readiness_level(score)
            
            # 生成建议
            recommendations = self._generate_recommendations(dim_id, score, completed, template)
            
            dimensions.append(DimensionReadiness(
                dimension=dim_name,
                score=round(score, 1),
                level=level,
                completed_items=[t["item"] for t in template if t["id"] in completed],
                pending_items=[t["item"] for t in pending_items],
                blockers=blockers,
                recommendations=recommendations
            ))
            
            # 收集检查项
            for t in template:
                all_checklist.append({
                    "dimension": dim_name,
                    "id": t["id"],
                    "item": t["item"],
                    "required": t["required"],
                    "status": "completed" if t["id"] in completed else "pending",
                    "priority": "high" if t["required"] else "normal"
                })
        
        # 计算总分
        overall_score = sum(
            d.score * next((dim["weight"] for dim in self.DIMENSIONS if dim["name"] == d.dimension), 0.2)
            for d in dimensions
        )
        overall_level = self._get_readiness_level(overall_score)
        
        # 估算上线日期
        estimated_launch = self._estimate_launch_date(market, overall_score, dimensions)
        
        # 汇总阻碍项
        blockers_summary = []
        for dim in dimensions:
            blockers_summary.extend(dim.blockers)
        
        self.current_report = ReadinessReport(
            overall_score=round(overall_score, 1),
            overall_level=overall_level,
            dimensions=dimensions,
            checklist=sorted(all_checklist, key=lambda x: (0 if x["required"] else 1, x["dimension"])),
            estimated_launch_date=estimated_launch,
            blockers_summary=blockers_summary[:10]
        )
        
        return self.current_report
    
    def _get_readiness_level(self, score: float) -> ReadinessLevel:
        """获取准备度等级"""
        if score >= 90:
            return ReadinessLevel.READY
        elif score >= 75:
            return ReadinessLevel.MOSTLY_READY
        elif score >= 50:
            return ReadinessLevel.PARTIALLY_READY
        elif score >= 25:
            return ReadinessLevel.NOT_READY
        else:
            return ReadinessLevel.NOT_STARTED
    
    def _generate_recommendations(self, dim_id: str, score: float,
                                  completed: List[str],
                                  template: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if score < 75:
            pending_required = [t for t in template if t["required"] and t["id"] not in completed]
            if pending_required:
                recommendations.append(f"优先完成{pending_required[0]['item']}")
        
        if dim_id == "qualification":
            if score < 75:
                recommendations.append("确保所有资质文件清晰有效")
        elif dim_id == "product":
            if score < 75:
                recommendations.append("选品是核心，建议深入调研后再推进")
        elif dim_id == "content":
            if score < 75:
                recommendations.append("内容储备至少20条再开始推广")
        elif dim_id == "logistics":
            if score < 75:
                recommendations.append("发货时效直接影响评分，需重点关注")
        elif dim_id == "customer_service":
            if score < 75:
                recommendations.append("差评处理预案是重中之重")
        
        return recommendations[:2]
    
    def _estimate_launch_date(self, market: str, score: float,
                              dimensions: List[DimensionReadiness]) -> str:
        """估算上线日期"""
        # 获取市场配置
        market_cfg = self.MARKET_CONFIG.get(market, self.MARKET_CONFIG["东南亚"])
        
        if score >= 90:
            return "预计3-5个工作日可完成入驻"
        elif score >= 75:
            return "预计1-2周可完成准备"
        elif score >= 50:
            blockers = len([d for d in dimensions if d.level in [ReadinessLevel.NOT_READY, ReadinessLevel.NOT_STARTED]])
            return f"预计{bockers * 2 + 2}周可完成准备"
        else:
            return "建议先完成基础准备再申请入驻"
    
    def generate_checklist(self, dimension: str = None) -> List[Dict]:
        """生成检查清单"""
        if not self.current_report:
            return []
        
        if dimension:
            return [c for c in self.current_report.checklist if c["dimension"] == dimension]
        
        return self.current_report.checklist
    
    def generate_cold_start_strategy(self, market: str) -> Dict[str, Any]:
        """生成冷启动策略"""
        if not self.current_report:
            return {"error": "请先执行准备度评估"}
        
        score = self.current_report.overall_score
        low_dims = [d.dimension for d in self.current_report.dimensions if d.score < 70]
        
        # 基础冷启动策略
        strategy = {
            "market": market,
            "timeline": self._get_cold_start_timeline(score),
            "phases": [],
            "key_metrics": [],
            "budget_allocation": {}
        }
        
        # 阶段一：账号冷启动（1-2周）
        strategy["phases"].append({
            "phase": "1-账号冷启动",
            "duration": "1-2周",
            "focus": "账号基础建设",
            "tasks": [
                "完善账号主页信息",
                "发布10-20条预热内容",
                "互动增加初始粉丝",
                "研究对标账号"
            ],
            "kpis": ["粉丝数≥1000", "视频播放≥5000"]
        })
        
        # 阶段二：内容测试期（3-4周）
        strategy["phases"].append({
            "phase": "2.内容测试期",
            "duration": "3-4周",
            "focus": "找到爆款内容模式",
            "tasks": [
                "测试不同内容形式",
                "分析数据找到最佳内容",
                "建立内容素材库",
                "尝试直播测试"
            ],
            "kpis": ["找到≥3种高效内容形式", "单视频播放≥10万"]
        })
        
        # 阶段三：带货爬坡期（5-8周）
        strategy["phases"].append({
            "phase": "3.带货爬坡期",
            "duration": "4-6周",
            "focus": "提升带货能力",
            "tasks": [
                "稳定日播/周播频率",
                "与达人合作带货",
                "优化商品卡转化",
                "积累店铺评分"
            ],
            "kpis": ["日均订单≥50", "店铺评分≥4.5"]
        })
        
        # 关键指标
        strategy["key_metrics"] = [
            {"metric": "视频完播率", "target": "≥30%", "importance": "high"},
            {"metric": "粉丝转化率", "target": "≥5%", "importance": "high"},
            {"metric": "带货转化率", "target": "≥2%", "importance": "high"},
            {"metric": "店铺评分", "target": "≥4.5", "importance": "medium"}
        ]
        
        # 预算分配
        strategy["budget_allocation"] = {
            "冷启动期": {"广告投放": "30%", "内容制作": "40%", "达人合作": "20%", "其他": "10%"},
            "成长期": {"广告投放": "40%", "内容制作": "20%", "达人合作": "30%", "其他": "10%"},
            "稳定期": {"广告投放": "50%", "内容制作": "15%", "达人合作": "25%", "其他": "10%"}
        }
        
        return strategy
    
    def _get_cold_start_timeline(self, score: float) -> str:
        """获取冷启动时间线"""
        if score >= 90:
            return "约4-6周达到稳定出单"
        elif score >= 75:
            return "约6-8周达到稳定出单"
        else:
            return "建议先完善准备工作"
    
    def format_report(self, report: ReadinessReport) -> str:
        """格式化报告"""
        output = []
        output.append("=" * 70)
        output.append("TikTok Shop开店准备度评估")
        output.append("=" * 70)
        
        output.append(f"\n【综合评分】{report.overall_score}分 ({report.overall_level.value})")
        output.append(f"【预计上线】{report.estimated_launch_date}")
        
        output.append(f"\n【各维度准备度】")
        for dim in report.dimensions:
            level_icon = "✅" if dim.level == ReadinessLevel.READY else "🔄" if dim.level == ReadinessLevel.MOSTLY_READY else "⚠️"
            bar = "█" * int(dim.score/5) + "░" * (20 - int(dim.score/5))
            output.append(f"\n  {level_icon} {dim.dimension}: [{bar}] {dim.score}分")
            if dim.recommendations:
                output.append(f"     建议: {dim.recommendations[0]}")
        
        if report.blockers_summary:
            output.append(f"\n【待完成关键项】")
            for blocker in report.blockers_summary[:5]:
                output.append(f"  ⚠️ {blocker}")
        
        output.append("\n" + "=" * 70)
        return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python tiktok-launch-planner.py <command> [args]")
        print("命令:")
        print("  readiness    - 开店准备度评分")
        print("  checklist    - 生成入驻清单")
        print("  cold-start   - 冷启动策略")
        return
    
    command = sys.argv[1]
    planner = TikTokLaunchPlanner()
    
    # 示例状态数据
    sample_status = {
        "qualification": ["q1", "q2", "q3", "q5"],  # 已完成部分
        "product": ["p1", "p2", "p3", "p4", "p5"],   # 选品基本完成
        "content": ["c1", "c2", "c3"],               # 内容部分完成
        "logistics": ["l1", "l2"],                   # 物流部分完成
        "customer_service": ["cs1", "cs3"]           # 客服部分完成
    }
    
    if command == "readiness":
        report = planner.assess_readiness("美区", sample_status)
        print(planner.format_report(report))
        
    elif command == "checklist":
        planner.assess_readiness("美区", sample_status)
        checklist = planner.generate_checklist()
        
        print("=" * 70)
        print("入驻检查清单")
        print("=" * 70)
        
        current_dim = ""
        for item in checklist:
            if item["dimension"] != current_dim:
                current_dim = item["dimension"]
                print(f"\n【{current_dim}】")
            
            status_icon = "✅" if item["status"] == "completed" else "☐"
            priority_mark = " *" if item["required"] else ""
            print(f"  {status_icon} {item['item']}{priority_mark}")
    
    elif command == "cold-start":
        planner.assess_readiness("美区", sample_status)
        strategy = planner.generate_cold_start_strategy("美区")
        
        print("=" * 70)
        print("冷启动策略")
        print("=" * 70)
        print(f"\n目标市场: {strategy['market']}")
        print(f"预计周期: {strategy['timeline']}")
        
        for phase in strategy["phases"]:
            print(f"\n📌 {phase['phase']} ({phase['duration']})")
            print(f"   重点: {phase['focus']}")
            print("   任务:")
            for task in phase["tasks"]:
                print(f"     • {task}")
            print("   KPI:")
            for kpi in phase["kpis"]:
                print(f"     ✓ {kpi}")
        
        print(f"\n💰 预算分配（冷启动期）")
        for cat, ratio in strategy["budget_allocation"]["冷启动期"].items():
            print(f"   {cat}: {ratio}")
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
