#!/usr/bin/env python3
"""
亚马逊运营任务编排器 - Level 2
Amazon Ops Task Orchestrator

功能：
- orchestrate: 运营任务编排（Listing/广告/库存/评论/Rufus 5模块）
- dependencies: 依赖关系分析
- critical-path: 关键路径计算

Author: Amazon Ops Team
Version: 1.0.0
"""

import sys
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque


class TaskModule(Enum):
    """任务模块"""
    LISTING = "listing"          # Listing优化
    ADVERTISING = "advertising"  # 广告投放
    INVENTORY = "inventory"      # 库存管理
    REVIEWS = "reviews"          # 评价管理
    RUFUS = "rufus"              # Rufus优化


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "待处理"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    BLOCKED = "被阻塞"
    SKIPPED = "已跳过"


@dataclass
class OpsTask:
    """运营任务"""
    id: str
    module: TaskModule
    name: str
    description: str
    duration_hours: float
    dependencies: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None  # 可并行执行的分组
    priority: int = 3  # 1-5, 1最高
    status: TaskStatus = TaskStatus.PENDING
    owner: str = ""  # 负责人
    estimated_cost: float = 0  # 预估成本(元)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyNode:
    """依赖图节点"""
    task_id: str
    task_name: str
    module: str
    incoming: List[str] = field(default_factory=list)
    outgoing: List[str] = field(default_factory=list)
    level: int = 0  # 在依赖链中的层级


@dataclass
class ScheduleResult:
    """排程结果"""
    total_duration: float  # 总工期(小时)
    schedule: List[Dict[str, Any]]  # 详细排程
    critical_path: List[str]  # 关键路径任务ID
    parallel_batches: List[List[str]]  # 可并行批次


class AmazonOpsOrchestrator:
    """亚马逊运营任务编排器"""
    
    # 模块间依赖关系
    MODULE_DEPENDENCIES = {
        TaskModule.LISTING: [],  # Listing无前置依赖
        TaskModule.ADVERTISING: [TaskModule.LISTING],  # 广告依赖Listing
        TaskModule.INVENTORY: [TaskModule.LISTING],    # 库存依赖Listing
        TaskModule.REVIEWS: [TaskModule.LISTING],      # 评价依赖Listing
        TaskModule.RUFUS: [TaskModule.LISTING, TaskModule.REVIEWS]  # Rufus依赖Listing和评价
    }
    
    def __init__(self):
        self.tasks: Dict[str, OpsTask] = {}
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.current_schedule: Optional[ScheduleResult] = None
    
    def add_task(self, task: OpsTask) -> bool:
        """添加任务"""
        if task.id in self.tasks:
            return False
        self.tasks[task.id] = task
        return True
    
    def add_tasks_from_template(self, asin: str, phase: str = "new") -> List[OpsTask]:
        """
        从模板添加任务
        
        Args:
            asin: ASIN标识
            phase: 阶段 (new/regular/prime_day)
        
        Returns:
            添加的任务列表
        """
        tasks = []
        
        if phase == "new":
            tasks = self._generate_new_product_tasks(asin)
        elif phase == "regular":
            tasks = self._generate_regular_ops_tasks(asin)
        elif phase == "prime_day":
            tasks = self._generate_prime_day_tasks(asin)
        
        for task in tasks:
            self.add_task(task)
        
        return tasks
    
    def _generate_new_product_tasks(self, asin: str) -> List[OpsTask]:
        """生成新品推广任务"""
        return [
            OpsTask(
                id=f"{asin}-listing-001",
                module=TaskModule.LISTING,
                name="关键词调研",
                description="进行关键词调研和竞争分析",
                duration_hours=4,
                priority=1,
                estimated_cost=200
            ),
            OpsTask(
                id=f"{asin}-listing-002",
                module=TaskModule.LISTING,
                name="标题优化",
                description="撰写优化标题，包含核心关键词",
                duration_hours=2,
                dependencies=[f"{asin}-listing-001"],
                priority=1,
                estimated_cost=100
            ),
            OpsTask(
                id=f"{asin}-listing-003",
                module=TaskModule.LISTING,
                name="图片优化",
                description="优化主图和辅图",
                duration_hours=6,
                dependencies=[f"{asin}-listing-001"],
                priority=2,
                estimated_cost=500
            ),
            OpsTask(
                id=f"{asin}-listing-004",
                module=TaskModule.LISTING,
                name="A+内容",
                description="创建A+内容",
                duration_hours=4,
                dependencies=[f"{asin}-listing-003"],
                priority=3,
                estimated_cost=300
            ),
            OpsTask(
                id=f"{asin}-inventory-001",
                module=TaskModule.INVENTORY,
                name="FBA入库计划",
                description="制定FBA入库计划",
                duration_hours=2,
                dependencies=[f"{asin}-listing-002"],
                priority=1,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-inventory-002",
                module=TaskModule.INVENTORY,
                name="库存关注设置",
                description="设置库存提醒",
                duration_hours=1,
                dependencies=[f"{asin}-inventory-001"],
                priority=2,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-ads-001",
                module=TaskModule.ADVERTISING,
                name="广告结构设计",
                description="设计广告活动结构",
                duration_hours=3,
                dependencies=[f"{asin}-listing-002"],
                priority=1,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-ads-002",
                module=TaskModule.ADVERTISING,
                name="自动广告启动",
                description="启动自动广告",
                duration_hours=1,
                dependencies=[f"{asin}-ads-001", f"{asin}-inventory-001"],
                priority=2,
                estimated_cost=1000
            ),
            OpsTask(
                id=f"{asin}-reviews-001",
                module=TaskModule.REVIEWS,
                name="VINE计划申请",
                description="申请VINE计划",
                duration_hours=1,
                dependencies=[f"{asin}-inventory-001"],
                priority=1,
                estimated_cost=200
            ),
            OpsTask(
                id=f"{asin}-reviews-002",
                module=TaskModule.REVIEWS,
                name="评论关注",
                description="设置评论关注",
                duration_hours=1,
                dependencies=[f"{asin}-reviews-001"],
                priority=2,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-rufus-001",
                module=TaskModule.RUFUS,
                name="Rufus优化",
                description="优化Rufus问答内容",
                duration_hours=3,
                dependencies=[f"{asin}-reviews-001"],
                priority=2,
                estimated_cost=0
            )
        ]
    
    def _generate_regular_ops_tasks(self, asin: str) -> List[OpsTask]:
        """生成日常运营任务"""
        return [
            OpsTask(
                id=f"{asin}-listing-weekly",
                module=TaskModule.LISTING,
                name="周度Listing检查",
                description="检查Listing表现",
                duration_hours=1,
                priority=2,
                estimated_cost=50
            ),
            OpsTask(
                id=f"{asin}-ads-daily",
                module=TaskModule.ADVERTISING,
                name="日度广告优化",
                description="广告数据分析与优化",
                duration_hours=2,
                priority=1,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-inventory-weekly",
                module=TaskModule.INVENTORY,
                name="周度库存盘点",
                description="库存盘点与补货计划",
                duration_hours=1,
                priority=1,
                estimated_cost=0
            ),
            OpsTask(
                id=f"{asin}-reviews-weekly",
                module=TaskModule.REVIEWS,
                name="周度评价分析",
                description="分析评价变化",
                duration_hours=1,
                priority=2,
                estimated_cost=0
            )
        ]
    
    def _generate_prime_day_tasks(self, asin: str) -> List[OpsTask]:
        """生成Prime Day任务"""
        return [
            OpsTask(
                id=f"{asin}-pd-inventory",
                module=TaskModule.INVENTORY,
                name="Prime Day备货",
                description="Prime Day备货计划",
                duration_hours=4,
                priority=1,
                estimated_cost=5000
            ),
            OpsTask(
                id=f"{asin}-pd-ads-prep",
                module=TaskModule.ADVERTISING,
                name="广告预热",
                description="Prime Day前广告预热",
                duration_hours=8,
                priority=1,
                estimated_cost=3000
            ),
            OpsTask(
                id=f"{asin}-pd-ads-live",
                module=TaskModule.ADVERTISING,
                name="活动期间广告调整",
                description="实时调整广告出价",
                duration_hours=12,
                priority=1,
                estimated_cost=5000
            ),
            OpsTask(
                id=f"{asin}-pd-reviews",
                module=TaskModule.REVIEWS,
                name="活动后评价跟进",
                description="活动后评价管理",
                duration_hours=4,
                dependencies=[f"{asin}-pd-ads-live"],
                priority=2,
                estimated_cost=0
            )
        ]
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        分析任务依赖关系
        
        Returns:
            依赖分析结果
        """
        # 构建依赖图
        graph = {}
        
        for task_id, task in self.tasks.items():
            graph[task_id] = DependencyNode(
                task_id=task_id,
                task_name=task.name,
                module=task.module.value,
                incoming=[dep for dep in task.dependencies if dep in self.tasks],
                outgoing=[]
            )
        
        # 构建反向依赖
        for task_id, node in graph.items():
            for dep in node.incoming:
                if dep in graph:
                    graph[dep].outgoing.append(task_id)
        
        # 计算层级
        self._calculate_levels(graph)
        
        self.dependency_graph = graph
        
        # 分析结果
        result = {
            "total_tasks": len(self.tasks),
            "modules": {},
            "parallel_groups": [],
            "bottlenecks": []
        }
        
        # 按模块统计
        module_counts = defaultdict(int)
        for task in self.tasks.values():
            module_counts[task.module.value] += 1
        result["modules"] = dict(module_counts)
        
        # 找出可并行的任务组
        parallel_groups = self._find_parallel_groups(graph)
        result["parallel_groups"] = [
            {"group_id": i, "tasks": g}
            for i, g in enumerate(parallel_groups, 1)
        ]
        
        # 找出瓶颈任务
        bottlenecks = self._find_bottlenecks(graph)
        result["bottlenecks"] = [
            {
                "task_id": b["task_id"],
                "task_name": b["task_name"],
                "reason": b["reason"]
            }
            for b in bottlenecks
        ]
        
        return result
    
    def _calculate_levels(self, graph: Dict[str, DependencyNode]) -> None:
        """计算任务层级"""
        # 找到入度为0的节点（起始节点）
        visited = set()
        levels = {}
        
        def dfs(node_id: str, level: int):
            if node_id in visited:
                return
            visited.add(node_id)
            levels[node_id] = max(levels.get(node_id, 0), level)
            
            if node_id in graph:
                for next_id in graph[node_id].outgoing:
                    dfs(next_id, level + 1)
        
        for node_id in graph:
            if not graph[node_id].incoming:
                dfs(node_id, 0)
        
        for node_id, level in levels.items():
            if node_id in graph:
                graph[node_id].level = level
    
    def _find_parallel_groups(self, graph: Dict[str, DependencyNode]) -> List[List[str]]:
        """找出可并行执行的任务组"""
        if not graph:
            return []
        
        # 按层级分组
        level_groups = defaultdict(list)
        for node_id, node in graph.items():
            level_groups[node.level].append(node_id)
        
        # 每层内的任务可以并行
        return [sorted(group) for group in level_groups.values() if group]
    
    def _find_bottlenecks(self, graph: Dict[str, DependencyNode]) -> List[Dict]:
        """找出瓶颈任务"""
        bottlenecks = []
        
        for node_id, node in graph.items():
            # 出度大于2意味着是重要分发点
            if len(node.outgoing) >= 3:
                bottlenecks.append({
                    "task_id": node_id,
                    "task_name": node.task_name,
                    "reason": f"影响{len(node.outgoing)}个后续任务"
                })
            
            # 链路过长的最后一个节点
            if not node.outgoing and len(graph) > 5:
                # 检查是否在关键路径上
                pass
        
        return bottlenecks[:5]
    
    def calculate_critical_path(self) -> List[str]:
        """
        计算关键路径
        
        Returns:
            关键路径任务ID列表
        """
        if not self.tasks:
            return []
        
        # 构建DAG
        dag = defaultdict(list)
        in_degree = defaultdict(int)
        
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                dag[dep].append(task_id)
                in_degree[task_id] += 1
        
        # 拓扑排序并计算最长路径
        dist = {task_id: 0.0 for task_id in self.tasks}
        parent = {task_id: None for task_id in self.tasks}
        
        # Kahn算法变体
        queue = deque([tid for tid in self.tasks if in_degree[tid] == 0])
        
        while queue:
            curr = queue.popleft()
            
            for next_id in dag[curr]:
                task_duration = self.tasks[next_id].duration_hours
                if dist[curr] + task_duration > dist[next_id]:
                    dist[next_id] = dist[curr] + task_duration
                    parent[next_id] = curr
                
                in_degree[next_id] -= 1
                if in_degree[next_id] == 0:
                    queue.append(next_id)
        
        # 找到最长路径终点
        end_node = max(dist, key=dist.get)
        
        # 回溯关键路径
        critical_path = []
        curr = end_node
        while curr is not None:
            critical_path.insert(0, curr)
            curr = parent[curr]
        
        return critical_path
    
    def orchestrate(self, task_ids: List[str] = None) -> ScheduleResult:
        """
        编排任务执行顺序
        
        Args:
            task_ids: 指定任务ID列表，None则编排全部
        
        Returns:
            排程结果
        """
        if task_ids is None:
            task_ids = list(self.tasks.keys())
        
        # 分析依赖
        dep_result = self.analyze_dependencies()
        critical_path = self.calculate_critical_path()
        
        # 构建排程
        schedule = []
        current_time = 0
        
        # 按层级组织
        level_groups = defaultdict(list)
        for task_id in task_ids:
            if task_id in self.dependency_graph:
                level = self.dependency_graph[task_id].level
                level_groups[level].append(task_id)
        
        # 生成排程
        for level in sorted(level_groups.keys()):
            tasks_in_level = level_groups[level]
            
            # 计算该批次开始时间
            if level == 0:
                start_time = 0
            else:
                # 取所有前置任务的完成时间
                max_end = 0
                for task_id in tasks_in_level:
                    task = self.tasks[task_id]
                    for dep_id in task.dependencies:
                        if dep_id in self.tasks:
                            dep_task = self.tasks[dep_id]
                            # 假设前置任务在之前的某批次完成
                            pass
                start_time = max_end
            
            for task_id in sorted(tasks_in_level, key=lambda x: self.tasks[x].priority):
                task = self.tasks[task_id]
                is_critical = task_id in critical_path
                
                schedule.append({
                    "task_id": task_id,
                    "task_name": task.name,
                    "module": task.module.value,
                    "start_hour": start_time,
                    "end_hour": start_time + task.duration_hours,
                    "duration_hours": task.duration_hours,
                    "priority": task.priority,
                    "is_critical": is_critical,
                    "parallel_with": [t for t in tasks_in_level if t != task_id]
                })
        
        # 计算总工期
        total_duration = max((s["end_hour"] for s in schedule), default=0)
        
        # 批次信息
        parallel_batches = [
            {"batch": i+1, "tasks": g}
            for i, g in enumerate(self._find_parallel_groups(self.dependency_graph))
        ]
        
        self.current_schedule = ScheduleResult(
            total_duration=total_duration,
            schedule=schedule,
            critical_path=critical_path,
            parallel_batches=parallel_batches
        )
        
        return self.current_schedule
    
    def get_module_summary(self) -> Dict[str, Any]:
        """获取模块汇总"""
        summary = {}
        
        for module in TaskModule:
            module_tasks = [t for t in self.tasks.values() if t.module == module]
            
            if module_tasks:
                summary[module.value] = {
                    "task_count": len(module_tasks),
                    "total_hours": sum(t.duration_hours for t in module_tasks),
                    "total_cost": sum(t.estimated_cost for t in module_tasks),
                    "priority_tasks": [
                        {"id": t.id, "name": t.name, "priority": t.priority}
                        for t in sorted(module_tasks, key=lambda x: x.priority)[:3]
                    ]
                }
        
        return summary


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python ops-orchestrator.py <command> [args]")
        print("命令:")
        print("  orchestrate      - 编排任务")
        print("  dependencies    - 分析依赖关系")
        print("  critical-path   - 计算关键路径")
        return
    
    command = sys.argv[1]
    orchestrator = AmazonOpsOrchestrator()
    
    # 添加示例任务
    asin = "B08N5WRWNW"
    tasks = orchestrator.add_tasks_from_template(asin, "new")
    
    print(f"已添加 {len(tasks)} 个任务\n")
    
    if command == "orchestrate":
        result = orchestrator.orchestrate()
        
        print("=" * 70)
        print("任务编排结果")
        print("=" * 70)
        print(f"\n总工期: {result.total_duration} 小时 ({result.total_duration/8:.1f} 工作日)")
        
        print(f"\n【关键路径】")
        for task_id in result.critical_path:
            task = orchestrator.tasks.get(task_id)
            if task:
                print(f"  → {task.name}")
        
        print(f"\n【执行排程】")
        for s in result.schedule[:10]:  # 只显示前10个
            critical_mark = "🔥" if s["is_critical"] else "  "
            print(f"{critical_mark} {s['start_hour']:.0f}h-{s['end_hour']:.0f}h | {s['module']:12} | {s['task_name']}")
        
        if len(result.schedule) > 10:
            print(f"  ... 还有 {len(result.schedule)-10} 个任务")
        
        print(f"\n【并行批次】")
        for batch in result.parallel_batches[:5]:
            print(f"  批次{batch['batch']}: {', '.join(batch['tasks'][:3])}...")
    
    elif command == "dependencies":
        result = orchestrator.analyze_dependencies()
        
        print("=" * 70)
        print("依赖关系分析")
        print("=" * 70)
        
        print(f"\n【任务统计】")
        print(f"  总任务数: {result['total_tasks']}")
        
        print(f"\n【各模块任务数】")
        for module, count in result['modules'].items():
            print(f"  {module}: {count}个")
        
        print(f"\n【可并行任务组】")
        for group in result['parallel_groups'][:5]:
            print(f"  组{group['group_id']}: {', '.join(group['tasks'][:4])}")
        
        print(f"\n【瓶颈任务】")
        for bn in result['bottlenecks']:
            print(f"  ⚠ {bn['task_name']} - {bn['reason']}")
    
    elif command == "critical-path":
        critical_path = orchestrator.calculate_critical_path()
        
        print("=" * 70)
        print("关键路径分析")
        print("=" * 70)
        
        print(f"\n关键路径 ({len(critical_path)} 个任务):")
        
        total_hours = 0
        for i, task_id in enumerate(critical_path, 1):
            task = orchestrator.tasks.get(task_id)
            if task:
                total_hours += task.duration_hours
                print(f"  {i}. {task.name}")
                print(f"     模块: {task.module.value} | 时长: {task.duration_hours}h | 优先级: {task.priority}")
        
        print(f"\n关键路径总时长: {total_hours}h ({total_hours/8:.1f} 工作日)")
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
