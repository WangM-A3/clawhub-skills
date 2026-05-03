"""
OpenClaw Enterprise — 多 Agent 协作工作流示例
================================================

演示场景：市场调研 → 数据分析 → 内容创作 → 图表设计 → PPT 演示

Pipeline:
  ResearchAgent ──► AnalystAgent ──► WriterAgent ──► DesignerAgent ──► PresentAgent
       │                 │               │                │               │
       ▼                 ▼               ▼                ▼               ▼
   原始数据          洞察报告        文案报告         图表/数据可视化    最终PPT

核心概念：
- ChiefAgent（幕僚长）：负责任务拆解、调度、汇总、质量控制
- AgentRegistry：Agent 注册表，维护 Agent 与能力类型的映射
- Scheduler：任务调度器，支持顺序/并行/自适应三种模式
- StateGraph：LangGraph 状态图，驱动整个工作流

依赖：
    pip install langchain-openai langgraph pydantic

运行：
    python examples/multi_agent_workflow.py

本示例使用模拟 Agent 函数。实际接入时，只需将模拟函数替换为真实 Agent 实例
（如 ResearchAgent、ContentAgent 等）即可。
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────────────
# 1. 状态与数据类型
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# 1. 状态与数据类型
# ─────────────────────────────────────────────────────────────────────────────

# 优先尝试从 OpenClaw Enterprise 包导入；若未安装则使用内嵌的最小定义
try:
    import sys
    _src_root = str(__file__.rsplit("/examples", 1)[0])
    if _src_root not in sys.path:
        sys.path.insert(0, _src_root)

    from projects.openclaw_enterprise.src.chief.state import (
        AgentType,
        ChiefState,
        TaskPriority,
        TaskStatus,
    )
except ImportError:
    # 内嵌最小状态定义，确保示例可独立运行
    class AgentType:
        RESEARCHER    = "researcher"
        DATA_ANALYST  = "data_analyst"
        CONTENT_WRITER = "content_writer"
    class TaskStatus:
        PENDING    = "pending"
        COMPLETED  = "completed"
        FAILED     = "failed"
    TaskPriority = None   # type: ignore[assignment, misc]
    ChiefState   = None   # type: ignore[assignment, misc]

# 扩展的消息类型，用于 Agent 间数据传递
@dataclass
class AgentMessage:
    """Agent 间的消息信封"""
    msg_id: str
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    references: List[str] = field(default_factory=list)  # 引用上游 msg_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "references": self.references,
        }


@dataclass
class WorkflowResult:
    """完整工作流执行结果"""
    session_id: str
    total_duration_seconds: float
    stages_completed: List[str]
    agent_outputs: Dict[str, Any]
    final_deliverable: Optional[Dict[str, Any]]
    quality_score: float
    errors: List[str]


# ─────────────────────────────────────────────────────────────────────────────
# 2. 模拟执行 Agent（实际使用时替换为真实 Agent 实例）
# ─────────────────────────────────────────────────────────────────────────────

async def run_research_agent(task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    ResearchAgent — 收集市场数据

    职责：
    - 确定调研范围和关键词
    - 调用搜索工具（web_search / news_api）获取原始数据
    - 去重、清洗、摘要整理

    Args:
        task: 子任务描述，期望包含 {"topic": "...", "depth": "brief|detailed" }
        context: 共享上下文，ChiefAgent 在启动时传入

    Returns:
        {
            "findings": [...],      # 核心发现列表
            "sources": [...],       # 信息来源
            "data_points": {...},   # 关键数据点（供 Analyst 使用）
            "summary": "..."        # 一句话摘要
        }
    """
    topic = task.get("description", "AI 行业趋势")
    depth = task.get("depth", "detailed")

    print(f"  [ResearchAgent] 开始调研: {topic} (depth={depth})")

    # ── 模拟 API 调用延迟 ──
    await asyncio.sleep(1.5)

    # ── 模拟搜索结果 ──
    findings = [
        f"2024-2025 年 {topic} 市场规模年复合增长率约 28%",
        "头部厂商（OpenAI/Anthropic/Google）市场份额超过 65%",
        "企业级 AI 应用渗透率从 12% 提升至 34%",
        "开源模型（Llama/Mistral）降低了中小企业的使用门槛",
    ]
    sources = [
        "Gartner AI Market Report 2025",
        "IDC China AI Tracker Q1 2025",
        "麦肯锡《AI 全球影响报告》",
    ]
    data_points = {
        "market_size_2024_b": 184,          # 十亿美元
        "market_size_2025_b": 236,
        "growth_rate": 0.28,
        "enterprise_adoption_rate": 0.34,
        "top3_vendor_share": 0.65,
    }

    print(f"  [ResearchAgent] ✓ 完成，收集到 {len(findings)} 条核心发现")

    return {
        "findings": findings,
        "sources": sources,
        "data_points": data_points,
        "summary": f"{topic}市场正处于高速增长期，企业采纳率持续攀升。",
    }


async def run_analyst_agent(task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    AnalystAgent — 分析数据，生成洞察

    职责：
    - 解读原始数据，识别趋势和模式
    - 生成结构化洞察（SWOT、波特五力等框架可选）
    - 准备供可视化使用的数据结构

    注意：
        Analyst 的输入来自 ResearchAgent 的输出，通过 context["upstream"] 传入。
        这是 Agent 间消息传递的核心机制。

    Args:
        task: 子任务描述
        context: 包含 "upstream" → {"research": AgentMessage }

    Returns:
        {
            "insights": [...],
            "charts": [{"type": "...", "data": {...}}, ...],
            "recommendations": [...],
            "confidence": 0.85
        }
    """
    topic = task.get("description", "AI 行业分析")

    # ── 接收上游 Research 数据 ──
    upstream: Optional[Dict] = context.get("upstream", {})
    research_data = upstream.get("research", {}).get("content", {})
    data_points = research_data.get("data_points", {})

    print(f"  [AnalystAgent] 收到上游数据: {len(data_points)} 个数据点，开始分析…")

    await asyncio.sleep(2.0)

    # ── 生成洞察 ──
    growth = data_points.get("growth_rate", 0.28)
    adoption = data_points.get("enterprise_adoption_rate", 0.34)
    market_2025 = data_points.get("market_size_2025_b", 236)

    insights = [
        f"行业 CAGR 达 {growth*100:.0f}%，处于高速扩张阶段",
        f"企业采纳率 {adoption*100:.0f}% 表明 B2B 市场已跨越鸿沟",
        f"2025 年市场规模预计达 {market_2025}B 美元，头部效应明显",
        "开源生态崛起将重塑竞争格局，中小厂商机会窗口开启",
    ]
    recommendations = [
        "优先布局企业级 AI SaaS 产品",
        "关注开源模型与闭源模型的混合架构路线",
        "聚焦金融、医疗、制造三大高价值垂直赛道",
    ]
    confidence = 0.88

    # ── 准备图表数据（供 Designer 使用）────────────
    charts = [
        {
            "type": "line",
            "title": "AI 市场增长趋势",
            "xlabel": "年份",
            "ylabel": "市场规模（十亿美元）",
            "series": {
                "市场规模": [120, 148, 184, 236, 298],
                "增长率(%)": [0, 23, 24, 28, 26],
            },
            "labels": ["2022", "2023", "2024", "2025E", "2026E"],
        },
        {
            "type": "bar",
            "title": "各厂商市场份额",
            "xlabel": "厂商",
            "ylabel": "份额（%）",
            "series": {
                "厂商": ["OpenAI", "Google", "Anthropic", "其他"],
                "份额": [35, 18, 12, 35],
            },
            "labels": None,
        },
    ]

    print(f"  [AnalystAgent] ✓ 生成 {len(insights)} 条洞察、{len(charts)} 个图表方案")

    return {
        "insights": insights,
        "charts": charts,
        "recommendations": recommendations,
        "confidence": confidence,
        "executive_summary": f"AI 市场 {market_2025}B 美元规模，CAGR {growth*100:.0f}%，B2B 是下一个主战场。",
    }


async def run_writer_agent(task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    WriterAgent — 撰写报告

    职责：
    - 基于上游洞察撰写结构化报告
    - 适配不同受众（投资人/管理层/业务方）调整语气和深度
    - 生成 Markdown 格式正文（可直接转为 PPT）

    输入：
        context["upstream"]["analyst"] 包含洞察和摘要

    Returns:
        {
            "sections": [...],     # 报告各章节
            "word_count": int,
            "markdown": "..."      # 完整 Markdown 正文
        }
    """
    audience = task.get("audience", "管理层")
    topic = task.get("description", "AI 行业调研报告")

    upstream: Dict = context.get("upstream", {})
    analyst_data = upstream.get("analyst", {}).get("content", {})
    research_data = upstream.get("research", {}).get("content", {})

    print(f"  [WriterAgent] 开始撰写 {audience} 版报告…")

    await asyncio.sleep(1.8)

    sections = [
        {
            "title": "一、行业概览",
            "level": 1,
            "content": analyst_data.get("executive_summary", "行业快速增长。"),
        },
        {
            "title": "二、核心发现",
            "level": 1,
            "content": "\n".join(f"- {s}" for s in analyst_data.get("insights", [])),
        },
        {
            "title": "三、数据支撑",
            "level": 1,
            "content": (
                f"2025 年市场规模预计达 {research_data.get('data_points', {}).get('market_size_2025_b', 'N/A')}B 美元，"
                f"CAGR {research_data.get('data_points', {}).get('growth_rate', 0)*100:.0f}%，"
                f"企业采纳率 {research_data.get('data_points', {}).get('enterprise_adoption_rate', 0)*100:.0f}%。"
            ),
        },
        {
            "title": "四、战略建议",
            "level": 1,
            "content": "\n".join(f"- {r}" for r in analyst_data.get("recommendations", [])),
        },
    ]

    markdown = f"# {topic}\n\n*报告日期：{datetime.now().strftime('%Y-%m-%d')}*\n\n"
    for sec in sections:
        markdown += f"## {sec['title']}\n{sec['content']}\n\n"

    word_count = sum(len(s["content"].split()) for s in sections)

    print(f"  [WriterAgent] ✓ 完成，{word_count} 字")

    return {
        "sections": sections,
        "word_count": word_count,
        "markdown": markdown,
        "audience": audience,
    }


async def run_designer_agent(task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    DesignerAgent — 生成图表和可视化

    职责：
    - 将上游图表数据转化为可视化（调用 echart skill）
    - 导出图片或 SVG，供 PPT 使用

    输入：
        context["upstream"]["analyst"] 包含 charts 数据

    Returns:
        {
            "charts": [{"name": "...", "path": "...", "url": "..."}, ...],
            "design_notes": "..."
        }

    Note:
        实际调用 echart skill：
            from skills.echart import generate_chart
            chart_path = await generate_chart(chart_data)
    """
    upstream: Dict = context.get("upstream", {})
    analyst_data = upstream.get("analyst", {}).get("content", {})
    charts_spec = analyst_data.get("charts", [])

    print(f"  [DesignerAgent] 开始生成 {len(charts_spec)} 张图表…")

    await asyncio.sleep(2.2)

    # 模拟图表生成（真实场景调用 echart skill）
    generated_charts = []
    for i, spec in enumerate(charts_spec):
        chart_id = f"chart_{i+1}_{spec['type']}"
        generated_charts.append({
            "name": spec["title"],
            "type": spec["type"],
            "chart_id": chart_id,
            "path": f"outputs/{chart_id}.png",          # 本地路径（示例）
            "url": f"https://assets.example.com/{chart_id}.png",  # 线上 URL（示例）
            "spec": spec,
        })

    design_notes = (
        "配色方案：主色 #1A73E8（科技蓝），辅色 #34A853（增长绿），"
        "强调色 #EA4335（警示红）。字体：标题思源黑体，正文 Arial。"
    )

    print(f"  [DesignerAgent] ✓ 生成 {len(generated_charts)} 张图表")

    return {
        "charts": generated_charts,
        "design_notes": design_notes,
    }


async def run_present_agent(task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    PresentAgent — 制作 PPT

    职责：
    - 将 Markdown 报告和图表合并为 PPT
    - 调用 create-ppt skill 输出 .pptx 文件

    输入：
        context["upstream"]["writer"]  → Markdown 正文
        context["upstream"]["designer"] → 图表列表

    Returns:
        {
            "pptx_path": "...",      # 本地 .pptx 文件路径
            "slide_count": int,
            "slides": [{"title": "...", "content": "..."}, ...]
        }

    Note:
        实际调用 create-ppt skill：
            from skills.create_ppt import build_presentation
            pptx_path = await build_presentation(slides=slide_list, theme="modern")
    """
    upstream: Dict = context.get("upstream", {})
    writer_data = upstream.get("writer", {}).get("content", {})
    designer_data = upstream.get("designer", {}).get("content", {})

    markdown_body = writer_data.get("markdown", "")
    charts = designer_data.get("charts", [])

    print(f"  [PresentAgent] 开始组装 PPT ({len(charts)} 张图表)…")

    await asyncio.sleep(1.5)

    # 模拟 PPT 生成
    slides = [
        {"title": "封面", "type": "cover", "content": "AI 行业调研报告"},
        {"title": "行业概览", "type": "content", "content": writer_data.get("sections", [{}])[0].get("content", "")},
        {"title": "核心发现", "type": "content", "content": writer_data.get("sections", [{}])[1].get("content", "")},
        {"title": "市场增长趋势", "type": "chart", "content": charts[0].get("name", "") if len(charts) > 0 else ""},
        {"title": "厂商市场份额", "type": "chart", "content": charts[1].get("name", "") if len(charts) > 1 else ""},
        {"title": "战略建议", "type": "content", "content": writer_data.get("sections", [{}])[3].get("content", "")},
        {"title": "谢谢", "type": "ending", "content": ""},
    ]

    pptx_path = "outputs/multi_agent_report.pptx"

    print(f"  [PresentAgent] ✓ 生成 PPT：{len(slides)} 页 → {pptx_path}")

    return {
        "pptx_path": pptx_path,
        "slide_count": len(slides),
        "slides": slides,
        "charts_embedded": [c["name"] for c in charts],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. 消息总线（Agent 间通信）
# ─────────────────────────────────────────────────────────────────────────────

class MessageBus:
    """
    轻量消息总线，维护 Agent 间消息记录。

    工作方式：
    - 每条消息携带 msg_id 和 references（引用上游 msg_id）
    - 各 Agent 通过 context["upstream"] 访问上游消息
    - ChiefAgent 维护全局消息日志（便于审计和回放）
    """

    def __init__(self):
        self._messages: Dict[str, AgentMessage] = {}
        self._inbox: Dict[str, List[str]] = {}  # agent_name → [msg_id, ...]

    def send(
        self,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
        references: Optional[List[str]] = None,
    ) -> AgentMessage:
        """发送消息，返回 AgentMessage 对象。"""
        msg = AgentMessage(
            msg_id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            references=references or [],
        )
        self._messages[msg.msg_id] = msg
        self._inbox.setdefault(to_agent, []).append(msg.msg_id)
        return msg

    def fetch_upstream(self, agent_name: str) -> Dict[str, AgentMessage]:
        """获取某 Agent 的全部上游消息（去重，保留最新）。"""
        msg_ids = self._inbox.get(agent_name, [])
        upstream: Dict[str, AgentMessage] = {}
        for mid in msg_ids:
            msg = self._messages.get(mid)
            if msg:
                upstream[msg.from_agent] = msg
        return upstream

    def history(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._messages.values()]


# ─────────────────────────────────────────────────────────────────────────────
# 4. 工作流编排器（Orchestrator）
# ─────────────────────────────────────────────────────────────────────────────

class WorkflowOrchestrator:
    """
    工作流编排器

    封装完整的 5 步工作流：
        Research → Analyst → Writer → Designer → Present

    关键设计：
    - 串行依赖链：每步等待上游完成后开始（保证数据一致性）
    - 并行化潜力：Writer 和 Designer 可以在 Analyst 完成后并行执行
        （当前示例采用顺序执行以保证可读性）
    - 消息总线：所有 Agent 输出通过 MessageBus 共享
    - ChiefAgent 集成：在真实环境中，Orchestrator 的大部分逻辑由
        ChiefAgent 的 StateGraph 自动处理
    """

    # Agent 名称常量
    RESEARCH  = "ResearchAgent"
    ANALYST   = "AnalystAgent"
    WRITER    = "WriterAgent"
    DESIGNER  = "DesignerAgent"
    PRESENT   = "PresentAgent"

    # Agent 能力到函数的映射
    AGENT_FUNCS: Dict[str, Callable] = {
        RESEARCH:  run_research_agent,
        ANALYST:   run_analyst_agent,
        WRITER:    run_writer_agent,
        DESIGNER:  run_designer_agent,
        PRESENT:   run_present_agent,
    }

    # Agent 执行顺序（与依赖顺序一致）
    PIPELINE = [RESEARCH, ANALYST, WRITER, DESIGNER, PRESENT]

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.bus = MessageBus()
        self.session_id = str(uuid.uuid4())[:8]
        self._agent_outputs: Dict[str, Any] = {}
        self._errors: List[str] = []

    # ── 核心流程 ────────────────────────────────────────────────────────────

    async def run(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        执行完整工作流。

        Args:
            user_query: 用户的原始请求（自然语言）
            context: 额外上下文（行业、时间范围、受众等）

        Returns:
            WorkflowResult，包含所有 Agent 输出和最终交付物
        """
        start = time.monotonic()
        print(f"\n{'='*60}")
        print(f"  Multi-Agent Workflow 启动 | session={self.session_id}")
        print(f"  用户请求: {user_query}")
        print(f"{'='*60}\n")

        context = context or {}
        completed_stages: List[str] = []

        # ── Stage 1: Research ───────────────────────────────────────────────
        print(f"\n▶ Stage 1/5: {self.RESEARCH}")
        research_task = {
            "description": user_query,
            "depth": context.get("depth", "detailed"),
        }
        try:
            research_out = await self._run_agent(
                self.RESEARCH, research_task,
                upstream=self.bus.fetch_upstream(self.RESEARCH),
            )
            self._agent_outputs[self.RESEARCH] = research_out
            completed_stages.append(self.RESEARCH)
        except Exception as e:
            self._errors.append(f"{self.RESEARCH}: {e}")
            raise

        # ── Stage 2: Analyst ────────────────────────────────────────────────
        print(f"\n▶ Stage 2/5: {self.ANALYST}")
        analyst_task = {
            "description": user_query,
            "framework": context.get("framework", "standard"),
        }
        try:
            analyst_out = await self._run_agent(
                self.ANALYST, analyst_task,
                upstream=self.bus.fetch_upstream(self.ANALYST),
            )
            self._agent_outputs[self.ANALYST] = analyst_out
            completed_stages.append(self.ANALYST)
        except Exception as e:
            self._errors.append(f"{self.ANALYST}: {e}")
            raise

        # ── Stages 3-4: Writer & Designer（可并行，但这里顺序演示）───────────
        # Analyst 完成后，Writer 和 Designer 可同时开始
        print(f"\n▶ Stage 3/5: {self.WRITER}")
        writer_task = {
            "description": user_query,
            "audience": context.get("audience", "管理层"),
        }
        try:
            writer_out = await self._run_agent(
                self.WRITER, writer_task,
                upstream=self.bus.fetch_upstream(self.WRITER),
            )
            self._agent_outputs[self.WRITER] = writer_out
            completed_stages.append(self.WRITER)
        except Exception as e:
            self._errors.append(f"{self.WRITER}: {e}")
            raise

        print(f"\n▶ Stage 4/5: {self.DESIGNER}")
        designer_task = {"description": user_query, "style": context.get("style", "modern")}
        try:
            designer_out = await self._run_agent(
                self.DESIGNER, designer_task,
                upstream=self.bus.fetch_upstream(self.DESIGNER),
            )
            self._agent_outputs[self.DESIGNER] = designer_out
            completed_stages.append(self.DESIGNER)
        except Exception as e:
            self._errors.append(f"{self.DESIGNER}: {e}")
            raise

        # ── Stage 5: Present ─────────────────────────────────────────────────
        print(f"\n▶ Stage 5/5: {self.PRESENT}")
        present_task = {
            "description": user_query,
            "format": context.get("format", "pptx"),
        }
        try:
            present_out = await self._run_agent(
                self.PRESENT, present_task,
                upstream=self.bus.fetch_upstream(self.PRESENT),
            )
            self._agent_outputs[self.PRESENT] = present_out
            completed_stages.append(self.PRESENT)
        except Exception as e:
            self._errors.append(f"{self.PRESENT}: {e}")
            raise

        # ── 完成 ─────────────────────────────────────────────────────────────
        duration = time.monotonic() - start
        quality = self._estimate_quality()

        result = WorkflowResult(
            session_id=self.session_id,
            total_duration_seconds=round(duration, 2),
            stages_completed=completed_stages,
            agent_outputs=self._agent_outputs,
            final_deliverable=self._agent_outputs.get(self.PRESENT),
            quality_score=quality,
            errors=self._errors,
        )

        self._print_summary(result)
        return result

    # ── Agent 执行封装 ───────────────────────────────────────────────────────

    async def _run_agent(
        self,
        agent_name: str,
        task: Dict[str, Any],
        upstream: Optional[Dict[str, AgentMessage]] = None,
    ) -> Dict[str, Any]:
        """
        单个 Agent 执行逻辑。

        步骤：
        1. 准备 context（含 upstream 消息）
        2. 调用注册的 Agent 函数
        3. 将结果写入 MessageBus
        """
        upstream_dict = {k: v.to_dict() for k, v in (upstream or {}).items()}
        exec_context = {
            "session_id": self.session_id,
            "user_query": task.get("description", ""),
            "upstream": upstream_dict,
        }

        func = self.AGENT_FUNCS.get(agent_name)
        if not func:
            raise ValueError(f"Unknown agent: {agent_name}")

        result = await func(task, exec_context)

        # 将结果写入总线，通知下游 Agent
        for downstream in self._get_downstream(agent_name):
            self.bus.send(
                from_agent=agent_name,
                to_agent=downstream,
                content=result,
                references=[upstream_dict.get(a, {}).get("msg_id") for a in upstream_dict],
            )

        return result

    def _get_downstream(self, agent_name: str) -> List[str]:
        """获取某 Agent 的下游 Agent 列表。"""
        idx = self.PIPELINE.index(agent_name)
        return self.PIPELINE[idx + 1:]

    # ── 辅助方法 ─────────────────────────────────────────────────────────────

    def _estimate_quality(self) -> float:
        """基于完成率和错误数估算质量分（0-1）。"""
        if not self._agent_outputs:
            return 0.0
        penalty = len(self._errors) * 0.1
        return max(0.0, min(1.0, 1.0 - penalty))

    def _print_summary(self, result: WorkflowResult) -> None:
        print(f"\n{'='*60}")
        print(f"  Multi-Agent Workflow 完成")
        print(f"{'='*60}")
        print(f"  session_id    : {result.session_id}")
        print(f"  总耗时        : {result.total_duration_seconds}s")
        print(f"  完成阶段     : {' → '.join(result.stages_completed)}")
        print(f"  质量评分      : {result.quality_score:.2f}")
        if result.final_deliverable:
            pptx = result.final_deliverable.get("pptx_path", "N/A")
            slides = result.final_deliverable.get("slide_count", 0)
            print(f"  最终交付物    : {pptx} ({slides} 页)")
        if result.errors:
            print(f"  ⚠ 错误       : {result.errors}")
        print(f"{'='*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ChiefAgent 集成（可选 — 演示如何与 ChiefAgent 一起使用）
# ─────────────────────────────────────────────────────────────────────────────

async def run_with_chief_agent(user_query: str, context: Optional[Dict[str, Any]] = None):
    """
    演示如何将 Orchestrator 嵌入 ChiefAgent 工作流。

    在真实 OpenClaw Enterprise 环境中：
    - ChiefAgent 使用 LangGraph StateGraph 自动完成意图识别、任务拆解、
      调度执行、结果汇总、质量检查
    - Orchestrator 可以作为 ChiefAgent 的一个 TaskExecutor 实现，
      或者直接注册为 SpecialTask 类型

    关键流程（ChiefAgent 内部）：
        understand  →  plan  →  schedule  →  aggregate  →  check_quality  →  deliver

    意图映射：
        "帮我做一份市场调研 PPT"  →  IntentCategory.CONTENT_CREATION + 多步任务
        → 自动拆解为 [Research, Analyst, Writer, Designer, Present]
        → 通过 Scheduler 并行/顺序调度
        → 汇总所有输出 → QualityChecker 评估 → 交付

    本函数演示了手动调用路径，真实场景 ChiefAgent 会自动完成。
    """
    try:
        from projects.openclaw_enterprise.src.chief import ChiefAgent
        from langchain_openai import ChatOpenAI
        _HAS_CHIEF = True
    except ImportError:
        _HAS_CHIEF = False
        ChiefAgent = None   # type: ignore[assignment, misc]
        ChatOpenAI = None   # type: ignore[assignment, misc]

    # ── 初始化 LLM（生产环境请使用真实 API Key）────────────
    # llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    # ── 初始化幕僚长 ─────────────────────────────────────
    # chief = ChiefAgent(
    #     llm=llm,
    #     config={"max_concurrent": 5, "timeout": 600},
    # )

    # ── 注册执行 Agent ────────────────────────────────────
    # chief.scheduler.register_agent(AgentType.RESEARCHER, run_research_agent)
    # chief.scheduler.register_agent(AgentType.DATA_ANALYST,  run_analyst_agent)
    # chief.scheduler.register_agent(AgentType.CONTENT_WRITER, run_writer_agent)
    # chief.scheduler.register_agent("designer", run_designer_agent)
    # chief.scheduler.register_agent("presenter", run_present_agent)

    # ── 执行（真实场景）───────────────────────────────────
    # result = await chief.execute(
    #     query=user_query,
    #     context=context or {},
    #     user_id="demo_user",
    # )
    # return result

    # ── 降级：直接使用 Orchestrator ───────────────────────
    print("[ChiefAgent] 降级使用 Orchestrator（请配置 LLM 以启用完整 ChiefAgent）")
    orch = WorkflowOrchestrator()
    return await orch.run(user_query, context)


# ─────────────────────────────────────────────────────────────────────────────
# 6. 入口
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    """
    主入口 — 执行多 Agent 协作工作流示例

    场景：用户请求一份"2025年AI行业调研报告（管理层版）"

    预期输出：
        1. ResearchAgent：收集行业数据
        2. AnalystAgent：生成洞察和图表数据
        3. WriterAgent：撰写 Markdown 报告
        4. DesignerAgent：生成可视化图表
        5. PresentAgent：组装为 .pptx 文件
    """
    user_query = "帮我完成一份2025年AI行业市场调研报告，要求有数据图表，最终生成PPT供管理层汇报使用。"

    context = {
        "audience": "管理层",   # 决定报告语气和深度
        "depth": "detailed",    # 调研深度
        "style": "modern",      # 设计风格
        "framework": "standard",  # 分析框架
    }

    # ── 方式 A：直接使用 Orchestrator（推荐用于独立演示）───
    print("\n>>> 方式 A：使用 WorkflowOrchestrator")
    orch = WorkflowOrchestrator(max_concurrent=3)
    result = await orch.run(user_query, context)

    # ── 方式 B：通过 ChiefAgent 调度（生产环境）────────────
    print("\n>>> 方式 B：通过 ChiefAgent 调度（演示用）")
    result_chief = await run_with_chief_agent(user_query, context)

    # ── 输出最终报告摘要 ───────────────────────────────────
    if result.final_deliverable:
        print(f"最终 PPT: {result.final_deliverable.get('pptx_path')}")
        print(f"总页数  : {result.final_deliverable.get('slide_count')}")
        print(f"嵌入图表: {result.final_deliverable.get('charts_embedded')}")

    writer_out = result.agent_outputs.get("WriterAgent", {})
    if writer_out.get("markdown"):
        print(f"\n报告预览（前 300 字）：")
        print("-" * 40)
        print(writer_out["markdown"][:300])
        print("-" * 40)

    print("\n✅ 多 Agent 协作工作流示例执行完毕！")


if __name__ == "__main__":
    asyncio.run(main())
