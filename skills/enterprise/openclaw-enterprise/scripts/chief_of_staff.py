#!/usr/bin/env python3
"""OpenClaw Enterprise - 幕僚长调度器"""

import os
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

# ============================================================
# 路径验证模块 - 防止越权访问
# ============================================================
class PathValidator:
    """路径访问验证器，确保文件操作在允许范围内"""
    
    ALLOWED_READ_DIRS = [
        "./data/openclaw-enterprise/",
        "./skills/openclaw-enterprise/scripts/",
        "./skills/openclaw-enterprise/templates/",
        "./skills/openclaw-enterprise/references/",
    ]
    ALLOWED_WRITE_DIRS = [
        "./data/openclaw-enterprise/output/",
        "./data/openclaw-enterprise/logs/",
    ]
    DENY_PATHS = [
        "/etc/", "/root/", "/home/", "/var/", "/.ssh/",
        "/usr/bin/", "/usr/sbin/", "/bin/", "/sbin/",
    ]
    
    @classmethod
    def validate_path(cls, path: str, require_write: bool = False) -> bool:
        """验证路径是否在允许范围内"""
        resolved = Path(path).resolve()
        
        # 检查禁止访问的路径
        for deny in cls.DENY_PATHS:
            if str(resolved).startswith(deny):
                return False
        
        # 检查允许的目录
        allowed = cls.ALLOWED_WRITE_DIRS if require_write else cls.ALLOWED_READ_DIRS + cls.ALLOWED_WRITE_DIRS
        for allowed_dir in allowed:
            allowed_resolved = Path(allowed_dir).resolve()
            try:
                resolved.relative_to(allowed_resolved)
                return True
            except ValueError:
                continue
        
        return False
    
    @classmethod
    def safe_read(cls, path: str) -> Optional[str]:
        """安全读取文件"""
        if cls.validate_path(path, require_write=False):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return None
        return None
    
    @classmethod
    def safe_write(cls, path: str, content: str) -> bool:
        """安全写入文件"""
        if cls.validate_path(path, require_write=True):
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception:
                return False
        return False


@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    instruction: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Dict] = None

@dataclass
class AgentDefinition:
    name: str
    category: str
    keywords: List[str]
    description: str
    capabilities: List[str]

class ChiefOfStaff:
    """幕僚长 - 负责理解用户意图、调度Agent、聚合结果"""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.agents: Dict[str, AgentDefinition] = {}
        self.task_history: List[AgentTask] = []
        self._load_agents()
    
    def _load_agents(self):
        """加载所有Agent定义"""
        agents_config = [
            ("原料采购Agent", "procurement", ["原料", "供应商", "行情", "比价", "采购"], "负责采购方案建议、行情参考、比价规划", ["供应商推荐参考", "行情分析建议"]),
            ("仓储管理Agent", "procurement", ["库存", "库位", "仓储", "备货"], "负责库存规划建议、库位优化方案", ["库存规划提示", "库位优化参考"]),
            ("物流调度Agent", "procurement", ["物流", "车队", "运输", "发货"], "负责车队匹配建议、路线规划参考", ["车队调度参考", "路线优化建议"]),
            ("生产调度Agent", "production", ["排产", "工单", "交期", "产能"], "负责排产建议、工单管理参考", ["智能排产建议", "工单管理参考"]),
            ("质量检测Agent", "production", ["质量", "检测", "合格率", "质检"], "负责质量检测建议、合格率参考", ["质量检测建议", "合格率参考"]),
            ("报价Agent", "sales", ["报价", "价格", "定价", "询价"], "负责快速报价建议、成本计算参考", ["快速报价建议", "成本计算参考"]),
            ("订单履约Agent", "sales", ["订单", "发货", "履约", "跟踪"], "负责订单协调建议、异常处理方案", ["订单协调建议", "异常处理方案"]),
            ("客户管理Agent", "sales", ["客户", "跟进", "复购", "CRM"], "负责客户管理建议、复购参考", ["客户分级建议", "复购分析参考"]),
            ("成本核算Agent", "finance", ["成本", "毛利", "利润", "核算"], "负责成本核算建议、毛利分析参考", ["成本核算建议", "毛利分析参考"]),
            ("风险预警Agent", "finance", ["风控", "预警", "信用", "风险"], "负责风险预防建议、信用评估参考", ["信用评估建议", "风险预防提示"]),
            ("数据分析Agent", "operations", ["数据", "报表", "月报", "分析"], "负责数据分析建议、报表生成参考", ["数据汇总建议", "报表生成参考"]),
            ("报告生成Agent", "operations", ["报告", "会议", "文档", "纪要"], "负责报告生成建议、文档撰写参考", ["文档生成建议", "会议纪要参考"]),
            ("客服支持Agent", "operations", ["售后", "投诉", "客服", "支持"], "负责客服支持建议、问题处理方案", ["问题解答建议", "投诉处理方案"]),
        ]
        
        for name, cat, kw, desc, caps in agents_config:
            self.agents[name] = AgentDefinition(name=name, category=cat, keywords=kw, description=desc, capabilities=caps)
    
    def route_task(self, user_input: str) -> List[str]:
        """路由任务到合适的Agent"""
        matched = []
        for name, agent in self.agents.items():
            for kw in agent.keywords:
                if kw in user_input and name not in matched:
                    matched.append(name)
                    break
        return matched if matched else ["数据分析Agent"]
    
    async def dispatch_to_agent(self, agent_name: str, task: AgentTask) -> Dict:
        """分发任务到Agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        # 模拟执行（真实环境需要API Key）
        return {
            "agent": agent_name,
            "category": agent.category,
            "task": task.instruction,
            "status": "completed",
            "message": f"{agent_name}已生成建议方案",
            "capabilities": agent.capabilities
        }
    
    async def process_request(self, user_input: str) -> Dict:
        """处理用户请求"""
        matched = self.route_task(user_input)
        
        tasks = [AgentTask(
            task_id=f"task_{i}_{datetime.now().strftime('%H%M%S')}",
            agent_name=agent,
            instruction=user_input
        ) for i, agent in enumerate(matched[:3])]
        
        results = await asyncio.gather(*[
            self.dispatch_to_agent(agent, task)
            for agent, task in [(t.agent_name, t) for t in tasks]
        ])
        
        return {
            "chief_of_staff": "ChiefOfStaff",
            "user_input": user_input,
            "matched_agents": matched,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

async def ask_chief(user_input: str) -> Dict:
    chief = ChiefOfStaff()
    return await chief.process_request(user_input)

if __name__ == "__main__":
    import sys
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "帮我规划库存方案"
    result = asyncio.run(ask_chief(user_input))
    print(json.dumps(result, ensure_ascii=False, indent=2))
