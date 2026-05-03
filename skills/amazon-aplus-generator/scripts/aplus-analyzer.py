#!/usr/bin/env python3
"""
亚马逊A+内容分析器 - Level 2
Amazon A+ Content Analyzer

功能：
- score: A+内容评分（品牌故事/产品细节/场景图/对比表/FAQ 5维）
- recommend: 模块推荐
- gap-analysis: 内容差距分析

Author: Amazon A+ Team
Version: 1.0.0
"""

import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ContentLevel(Enum):
    """内容等级"""
    PREMIUM = "Premium A+"
    STANDARD = "Standard A+"
    BASIC = "Basic A+"
    NONE = "无A+内容"


@dataclass
class ModuleScore:
    """模块评分"""
    module: str
    score: float  # 0-100
    status: str  # present, missing, partial
    quality_factors: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class APlusReport:
    """A+报告"""
    overall_score: float
    content_level: ContentLevel
    module_scores: List[ModuleScore]
    recommended_modules: List[Dict]
    gaps: List[Dict]
    priority_improvements: List[str]


class APlusAnalyzer:
    """A+内容分析器"""
    
    MODULES = [
        {"id": "brand_story", "name": "品牌故事", "weight": 0.20, "essential": True},
        {"id": "product_detail", "name": "产品细节", "weight": 0.25, "essential": True},
        {"id": "lifestyle", "name": "生活方式图", "weight": 0.15, "essential": False},
        {"id": "comparison", "name": "对比图表", "weight": 0.15, "essential": False},
        {"id": "faq", "name": "FAQ问答", "weight": 0.10, "essential": False},
        {"id": "infographic", "name": "信息图", "weight": 0.10, "essential": False},
        {"id": "video", "name": "品牌视频", "weight": 0.05, "essential": False}
    ]
    
    # 评分标准
    QUALITY_CRITERIA = {
        "brand_story": {
            "brand_values": 25,
            "history": 20,
            "mission": 20,
            "visuals": 25,
            "consistency": 10
        },
        "product_detail": {
            "feature_list": 20,
            "specifications": 25,
            "benefits": 25,
            "usability": 15,
            "clarity": 15
        },
        "lifestyle": {
            "scene_diversity": 30,
            "emotional_appeal": 25,
            "product_integration": 25,
            "image_quality": 20
        },
        "comparison": {
            "competitor_count": 20,
            "feature_comparison": 30,
            "clarity": 25,
            "visual_design": 25
        },
        "faq": {
            "question_count": 25,
            "relevance": 30,
            "coverage": 25,
            "helpfulness": 20
        }
    }
    
    def __init__(self):
        self.current_report: Optional[APlusReport] = None
    
    def assess_module(self, module_id: str, content: Dict[str, Any]) -> ModuleScore:
        """
        评估单个模块
        
        Args:
            module_id: 模块ID
            content: 模块内容
        
        Returns:
            模块评分
        """
        module_info = next((m for m in self.MODULES if m["id"] == module_id), None)
        if not module_info:
            return ModuleScore(module=module_id, score=0, status="missing")
        
        module_name = module_info["name"]
        
        if not content or not content.get("present", False):
            return ModuleScore(
                module=module_name,
                score=0,
                status="missing",
                suggestions=[f"建议添加{module_name}模块以提升转化"]
            )
        
        # 计算模块得分
        criteria = self.QUALITY_CRITERIA.get(module_id, {})
        quality_factors = {}
        total_score = 0
        
        for factor, weight in criteria.items():
            factor_value = content.get(factor, content.get(f"{factor}_score", 0))
            if isinstance(factor_value, dict):
                factor_score = factor_value.get("score", 0)
            else:
                factor_score = factor_value
            
            factor_score = min(100, max(0, factor_score))
            quality_factors[factor] = {
                "score": factor_score,
                "weight": weight,
                "weighted_score": factor_score * weight / 100
            }
            total_score += factor_score * weight / 100
        
        # 检查完整性
        is_complete = content.get("complete", True)
        status = "present" if is_complete else "partial"
        
        # 如果不完整，降低分数
        if not is_complete:
            total_score *= 0.7
        
        # 生成建议
        suggestions = self._generate_module_suggestions(module_id, quality_factors, total_score)
        
        return ModuleScore(
            module=module_name,
            score=round(total_score, 1),
            status=status,
            quality_factors=quality_factors,
            suggestions=suggestions
        )
    
    def _generate_module_suggestions(self, module_id: str, 
                                     factors: Dict,
                                     score: float) -> List[str]:
        """生成模块改进建议"""
        suggestions = []
        
        if score < 60:
            # 找出最弱的因素
            weak_factors = sorted(factors.items(), key=lambda x: x[1]["score"])[:2]
            for factor, data in weak_factors:
                if data["score"] < 50:
                    suggestions.append(f"改进{factor}展示：当前仅{data['score']}分")
        
        if module_id == "brand_story":
            if score < 70:
                suggestions.append("品牌故事应包含使命、价值观和独特性")
                suggestions.append("使用高质量品牌视觉素材")
        elif module_id == "product_detail":
            if score < 70:
                suggestions.append("清晰展示产品核心卖点和规格参数")
                suggestions.append("使用信息图解释复杂功能")
        elif module_id == "lifestyle":
            if score < 70:
                suggestions.append("展示多种真实使用场景")
                suggestions.append("平衡产品展示与情感诉求")
        elif module_id == "comparison":
            if score < 70:
                suggestions.append("与主要同行进行功能对比")
                suggestions.append("使用清晰的对比表格格式")
        elif module_id == "faq":
            if score < 70:
                suggestions.append("覆盖用户常见问题")
                suggestions.append("提供有价值的答案，不只是简单回复")
        
        return suggestions[:3]
    
    def calculate_overall_score(self, module_scores: List[ModuleScore]) -> float:
        """计算综合评分"""
        total = 0
        for module in self.MODULES:
            module_id = module["id"]
            weight = module["weight"]
            
            score_entry = next((ms for ms in module_scores if ms.module == module["name"]), None)
            
            if score_entry:
                total += score_entry.score * weight
            else:
                # 未使用的模块不计分
                pass
        
        return round(total, 1)
    
    def determine_content_level(self, overall_score: float,
                                module_scores: List[ModuleScore]) -> ContentLevel:
        """确定内容等级"""
        # 检查essential模块
        essential_missing = any(
            ms.status == "missing" and 
            next((m for m in self.MODULES if m["name"] == ms.module), {}).get("essential", False)
            for ms in module_scores
        )
        
        if overall_score >= 85 and not essential_missing:
            return ContentLevel.PREMIUM
        elif overall_score >= 60:
            return ContentLevel.STANDARD
        elif overall_score >= 30:
            return ContentLevel.BASIC
        else:
            return ContentLevel.NONE
    
    def score(self, content_data: Dict[str, Any]) -> APlusReport:
        """
        执行完整评分
        
        Args:
            content_data: A+内容数据
        
        Returns:
            评分报告
        """
        module_scores = []
        
        for module in self.MODULES:
            module_content = content_data.get(module["id"], {})
            ms = self.assess_module(module["id"], module_content)
            module_scores.append(ms)
        
        overall_score = self.calculate_overall_score(module_scores)
        content_level = self.determine_content_level(overall_score, module_scores)
        
        # 生成模块推荐
        recommended_modules = self._recommend_modules(module_scores)
        
        # 生成差距分析
        gaps = self._analyze_gaps(module_scores)
        
        # 优先改进项
        priority_improvements = self._get_priority_improvements(module_scores)
        
        self.current_report = APlusReport(
            overall_score=overall_score,
            content_level=content_level,
            module_scores=module_scores,
            recommended_modules=recommended_modules,
            gaps=gaps,
            priority_improvements=priority_improvements
        )
        
        return self.current_report
    
    def _recommend_modules(self, module_scores: List[ModuleScore]) -> List[Dict]:
        """推荐模块"""
        recommendations = []
        
        # 缺失的模块
        for ms in module_scores:
            if ms.status == "missing":
                module_info = next((m for m in self.MODULES if m["name"] == ms.module), {})
                recommendations.append({
                    "module": ms.module,
                    "action": "add",
                    "priority": "high" if module_info.get("essential", False) else "medium",
                    "reason": f"{ms.module}缺失，影响整体表现"
                })
        
        # 需要改进的模块
        for ms in module_scores:
            if ms.status == "present" and ms.score < 70:
                recommendations.append({
                    "module": ms.module,
                    "action": "improve",
                    "priority": "medium",
                    "reason": f"{ms.module}评分{ms.score}分，有提升空间"
                })
        
        return recommendations[:6]
    
    def _analyze_gaps(self, module_scores: List[ModuleScore]) -> List[Dict]:
        """分析内容差距"""
        gaps = []
        
        for ms in module_scores:
            if ms.status == "missing":
                gaps.append({
                    "type": "missing_module",
                    "module": ms.module,
                    "impact": "high" if ms.score == 0 else "medium",
                    "description": f"{ms.module}完全缺失"
                })
            elif ms.score < 60:
                gaps.append({
                    "type": "low_quality",
                    "module": ms.module,
                    "impact": "medium",
                    "description": f"{ms.module}质量较低({ms.score}分)"
                })
        
        return gaps
    
    def _get_priority_improvements(self, module_scores: List[ModuleScore]) -> List[str]:
        """获取优先改进项"""
        improvements = []
        
        # 按分数排序
        sorted_scores = sorted(module_scores, key=lambda x: x.score)
        
        for ms in sorted_scores[:3]:
            if ms.score < 75:
                improvements.extend(ms.suggestions[:2])
        
        return improvements[:5]
    
    def recommend_modules(self) -> List[Dict]:
        """获取模块推荐（基于当前报告）"""
        if not self.current_report:
            return []
        return self.current_report.recommended_modules
    
    def analyze_gap(self, target_level: ContentLevel = None) -> List[Dict]:
        """分析达成目标需要的改进"""
        if not self.current_report:
            return []
        
        if target_level is None:
            # 默认目标是Standard A+
            target_level = ContentLevel.STANDARD
        
        current = self.current_report
        gaps = []
        
        # 需要的分数
        target_scores = {
            ContentLevel.BASIC: 30,
            ContentLevel.STANDARD: 60,
            ContentLevel.PREMIUM: 85
        }
        
        target = target_scores.get(target_level, 60)
        
        if current.overall_score >= target:
            gaps.append({
                "status": "achieved",
                "message": f"已达到{target_level.value}水平"
            })
        else:
            gap = target - current.overall_score
            gaps.append({
                "status": "gap",
                "current": current.overall_score,
                "target": target,
                "gap": gap,
                "message": f"距{target_level.value}还差{gap:.1f}分"
            })
        
        # 具体改进项
        for ms in current.module_scores:
            if ms.score < 70:
                module_info = next((m for m in self.MODULES if m["name"] == ms.module), {})
                gaps.append({
                    "module": ms.module,
                    "current_score": ms.score,
                    "target_score": 70,
                    "gap": 70 - ms.score,
                    "suggestions": ms.suggestions
                })
        
        return gaps
    
    def format_report(self, report: APlusReport) -> str:
        """格式化报告"""
        output = []
        output.append("=" * 70)
        output.append("亚马逊A+内容评分报告")
        output.append("=" * 70)
        
        output.append(f"\n【综合评分】{report.overall_score}分")
        output.append(f"【内容等级】{report.content_level.value}")
        
        output.append(f"\n【各模块评分】")
        for ms in report.module_scores:
            status_icon = "✅" if ms.status == "present" else "❌" if ms.status == "missing" else "⚠️"
            bar = "█" * int(ms.score/5) + "░" * (20 - int(ms.score/5))
            output.append(f"\n  {status_icon} {ms.module}: [{bar}] {ms.score}分")
            
            if ms.quality_factors:
                for factor, data in list(ms.quality_factors.items())[:3]:
                    output.append(f"      {factor}: {data['score']:.0f}分")
        
        if report.recommended_modules:
            output.append(f"\n【模块推荐】")
            for rec in report.recommended_modules[:4]:
                action = "添加" if rec["action"] == "add" else "改进"
                output.append(f"  → {action}{rec['module']} (优先级: {rec['priority']})")
        
        output.append("\n" + "=" * 70)
        return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python aplus-analyzer.py <command> [args]")
        print("命令:")
        print("  score         - A+内容评分")
        print("  recommend    - 模块推荐")
        print("  gap-analysis - 差距分析")
        return
    
    command = sys.argv[1]
    analyzer = APlusAnalyzer()
    
    # 示例数据
    sample_content = {
        "brand_story": {
            "present": True,
            "complete": True,
            "brand_values": 75,
            "history": 60,
            "mission": 70,
            "visuals": 80,
            "consistency": 75
        },
        "product_detail": {
            "present": True,
            "complete": True,
            "feature_list": 85,
            "specifications": 80,
            "benefits": 75,
            "usability": 70,
            "clarity": 80
        },
        "lifestyle": {
            "present": True,
            "complete": True,
            "scene_diversity": 65,
            "emotional_appeal": 70,
            "product_integration": 60,
            "image_quality": 75
        },
        "comparison": {
            "present": False
        },
        "faq": {
            "present": True,
            "complete": False,
            "question_count": 50,
            "relevance": 60,
            "coverage": 55,
            "helpfulness": 65
        },
        "infographic": {
            "present": True,
            "complete": True,
            "clarity": 75,
            "design": 80,
            "info_density": 70
        }
    }
    
    if command == "score":
        report = analyzer.score(sample_content)
        print(analyzer.format_report(report))
        
    elif command == "recommend":
        analyzer.score(sample_content)
        recommendations = analyzer.recommend_modules()
        
        print("=" * 70)
        print("A+模块推荐")
        print("=" * 70)
        
        for rec in recommendations:
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡"
            print(f"\n{priority_icon} {rec['module']}")
            print(f"   操作: {'添加' if rec['action'] == 'add' else '改进'}")
            print(f"   原因: {rec['reason']}")
    
    elif command == "gap-analysis":
        analyzer.score(sample_content)
        gaps = analyzer.analyze_gap()
        
        print("=" * 70)
        print("A+内容差距分析")
        print("=" * 70)
        
        for gap in gaps:
            if gap.get("status"):
                print(f"\n{gap['message']}")
                if "gap" in gap:
                    print(f"  当前: {gap['current']}分")
                    print(f"  目标: {gap['target']}分")
                    print(f"  差距: {gap['gap']}分")
            else:
                print(f"\n📊 {gap['module']}")
                print(f"   当前: {gap['current_score']}分 → 目标: {gap['target_score']}分")
                print(f"   差距: {gap['gap']}分")
                if gap.get("suggestions"):
                    for sug in gap["suggestions"][:2]:
                        print(f"   → {sug}")
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
