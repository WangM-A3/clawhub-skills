#!/usr/bin/env python3
"""
义乌发展经验分析引擎
根据县域现状，匹配适用的义乌经验，生成发展建议
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CountyProfile:
    """县域发展画像"""
    name: str
    population: float  # 万人
    gdp: float  # 亿元
    main_industries: List[str]  # 主导产业
    resources: List[str]  # 资源禀赋
    location: str  # 地理位置（内陆/沿海/沿边）
    market_scale: str  # 市场规模（无/小/中/大）
    digital_level: str  # 数字化水平（低/中/高）
    pain_points: List[str]  # 发展痛点

@dataclass
class YiwuPrinciple:
    """义乌发展原则"""
    name: str
    description: str
    applicability: Dict[str, List[str]]  # 适用条件
    priority: int  # 优先级权重
    actions: List[str]  # 行动建议

# 六大原则定义
PRINCIPLES = [
    YiwuPrinciple(
        name="兴商建市",
        description="市场是根与魂，坚持一条发展主线不动摇",
        applicability={
            "market_scale": ["无", "小"],
            "resources": ["农业资源", "特色产品"]
        },
        priority=10,
        actions=[
            "建设专业市场（从农贸市场、特色产品市场起步）",
            "降低市场准入门槛，鼓励农民经商",
            "专业化分区，便于采购商货比三家",
            "配套物流、仓储、金融服务"
        ]
    ),
    YiwuPrinciple(
        name="政府与市场协同",
        description="群众推着政府走，政府领着百姓跑",
        applicability={
            "location": ["内陆", "沿海", "沿边"],
            "digital_level": ["低", "中"]
        },
        priority=9,
        actions=[
            "梳理政府权力清单，明确'做什么不做什么'",
            "建立'企业点单、政府接单'服务机制",
            "扩大县级经济管理权限（争取试点）",
            "打造营商环境评价指标体系"
        ]
    ),
    YiwuPrinciple(
        name="无中生有",
        description="资源匮乏也能做枢纽，借力外部资源",
        applicability={
            "location": ["内陆"],
            "resources": ["资源匮乏"]
        },
        priority=8,
        actions=[
            "对接国家战略（一带一路、双循环）",
            "打通物流通道（铁路、公路、港口合作）",
            "建设数字化平台，弥补区位劣势",
            "发展跨境电商，直连全球市场"
        ]
    ),
    YiwuPrinciple(
        name="贸工联动",
        description="市场带动工业，工业支撑市场",
        applicability={
            "market_scale": ["中", "大"],
            "main_industries": ["制造业", "加工业"]
        },
        priority=7,
        actions=[
            "引导'前店后厂'模式，市场牵引生产",
            "培育产业集群，形成配套圈",
            "推动传统制造业智能化升级",
            "引进新兴产业，优化产业结构"
        ]
    ),
    YiwuPrinciple(
        name="改革创新",
        description="改革是最亮底色，制度突破释放活力",
        applicability={
            "pain_points": ["体制束缚", "审批繁琐", "政策限制"]
        },
        priority=6,
        actions=[
            "争取改革试点（国家级、省级）",
            "简化行政审批，推行'一网通办'",
            "创新贸易监管模式（市场采购贸易等）",
            "建立容错机制，鼓励先行先试"
        ]
    ),
    YiwuPrinciple(
        name="数字化升级",
        description="AI重塑贸易，数字科技赋能发展",
        applicability={
            "digital_level": ["中", "高"],
            "market_scale": ["中", "大"]
        },
        priority=5,
        actions=[
            "建设数字贸易平台",
            "推广AI应用（多语种客服、智能设计）",
            "发展直播电商、跨境电商",
            "建设智慧物流体系"
        ]
    )
]

def analyze_county(profile: CountyProfile) -> Dict:
    """
    分析县域发展现状，匹配义乌经验
    """
    results = []
    
    for principle in PRINCIPLES:
        score = 0
        matched_conditions = []
        
        # 检查适用条件
        for condition, values in principle.applicability.items():
            profile_value = getattr(profile, condition, None)
            if profile_value:
                if isinstance(profile_value, list):
                    if any(v in values for v in profile_value):
                        score += 1
                        matched_conditions.append(f"{condition}: {profile_value}")
                elif profile_value in values:
                    score += 1
                    matched_conditions.append(f"{condition}: {profile_value}")
        
        if score > 0:
            results.append({
                "principle": principle.name,
                "description": principle.description,
                "match_score": score,
                "matched_conditions": matched_conditions,
                "priority": principle.priority,
                "actions": principle.actions
            })
    
    # 按优先级和匹配分数排序
    results.sort(key=lambda x: (x["priority"], x["match_score"]), reverse=True)
    
    return {
        "county_name": profile.name,
        "analysis_time": "2026-04-25",
        "matched_principles": results,
        "recommendation_count": len(results)
    }

def generate_action_plan(profile: CountyProfile, analysis: Dict) -> str:
    """
    生成行动计划
    """
    plan = f"""# {profile.name}县域发展行动计划

## 一、现状诊断

### 资源禀赋
- 人口：{profile.population}万人
- GDP：{profile.gdp}亿元
- 主导产业：{', '.join(profile.main_industries)}
- 地理位置：{profile.location}
- 市场规模：{profile.market_scale}
- 数字化水平：{profile.digital_level}

### 发展痛点
"""
    for pain in profile.pain_points:
        plan += f"- {pain}\n"
    
    plan += "\n## 二、对标义乌经验\n\n"
    
    for i, item in enumerate(analysis["matched_principles"], 1):
        plan += f"""### {i}. {item['principle']}（匹配度：{'★' * item['match_score']}）

{item['description']}

**适用条件匹配**：
"""
        for cond in item['matched_conditions']:
            plan += f"- {cond}\n"
        
        plan += "\n**行动建议**：\n"
        for action in item['actions']:
            plan += f"- {action}\n"
        plan += "\n"
    
    plan += """## 三、实施路径

### 短期（1年内）
- 完成发展诊断，明确主攻方向
- 启动1-2个重点项目
- 建立工作机制

### 中期（3年内）
- 形成初步产业集聚
- 数字化平台上线运行
- 改革试点取得突破

### 长期（5年内）
- 产业生态基本成型
- 市场影响力显著提升
- 可复制经验形成

## 四、风险提示

1. **因地制宜**：义乌经验不能照搬，需结合本地实际
2. **久久为功**：县域发展是长期工程，不能急功近利
3. **政府与市场双轮驱动**：缺一不可
4. **避免同质化**：走差异化发展道路

---
*本计划基于义乌发展经验分析生成，仅供参考*
"""
    return plan

# 示例使用
if __name__ == "__main__":
    # 示例县域
    example = CountyProfile(
        name="XX县",
        population=30,
        gdp=50,
        main_industries=["农业", "粮食加工"],
        resources=["农业资源", "特色农产品"],
        location="内陆",
        market_scale="小",
        digital_level="低",
        pain_points=["产业链短", "附加值低", "人才外流", "缺乏龙头市场"]
    )
    
    analysis = analyze_county(example)
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    plan = generate_action_plan(example, analysis)
    print("\n" + "="*50 + "\n")
    print(plan)
