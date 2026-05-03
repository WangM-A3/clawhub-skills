---
name: industrial-silicon-army
description: "产业互联网硅基军团 - 面向制造业的Multi-Agent运营系统，涵盖采购/生产/销售/研发/合规全链路"
metadata:
  openclaw:
    requires: ["python3", "pip", "httpx"]
    emoji: "🏭"
    version: "1.0.0"
    author: "LookingPlas × 云旅智能体超市"
    category: "industrial-ai"
    tags: ["industrial", "manufacturing", "erp", "scm", "plastics", "multi-agent"]
pricing:
  basic:
    price: 299
    currency: CNY
    period: month
    features: ["10个专业Agent", "采购/生产/销售", "基础数据看板"]
  professional:
    price: 999
    currency: CNY
    period: month
    features: ["全部20个Agent", "全链路覆盖", "API集成", "SLA 99.5%"]
  enterprise:
    price: 9999
    currency: CNY
    period: month
    features: ["私有部署", "行业定制", "源码交付", "专属顾问"]
---

# 产业互联网硅基军团 SKILL.md

## 一、系统定位

面向制造业的产业互联网AI运营平台，模拟一个完整的制造业中层管理团队。

**LookingPlas**（塑化行业）为核心行业，后续可扩展至模具/化工/电子/汽车零部件。

## 二、团队架构

### 幕僚长（ChiefOfStaff）
- 任务分发、调度、结果整合
- 支持自然语言查询全链路数据
- 主动预警异常

### 核心执行Agent（20个）

#### 采购与供应链（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 原料采购Agent | 供应商匹配/行情分析/下单 | 1688/阿里巴巴比价 |
| 仓储管理Agent | 库存预警/库位优化 | 实时库存 + 安全库存 |
| 物流调度Agent | 车队匹配/路线优化 | 降低物流成本 |
| 供应商管理Agent | 评级/风控/合同 | 供应商KPI |

#### 生产与研发（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 生产调度Agent | 排产/工单管理 | 交期承诺 |
| 配方研发Agent | 新材料/替代料 | 成本优化 |
| 质量检测Agent | 来料/过程/成品 | 合标率 |
| 设备维护Agent | 预测性维护 | 减少停机 |

#### 销售与市场（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 报价Agent | 快速响应/成本叠加 | 提升响应速度 |
| 订单履约Agent | 订单跟踪/异常处理 | 客户满意度 |
| 客户管理Agent | 客户分级/跟进 | 复购率 |
| 竞品监控Agent | 市场价格/替代品 | 定价决策 |

#### 财务与合规（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 成本核算Agent | 实际成本/标准成本 | 毛利分析 |
| 合规审查Agent | 环保/安全/税务 | 减少处罚 |
| 风险预警Agent | 客户信用/材料波动 | 降低坏账 |
| 政策解读Agent | 行业政策/补贴 | 争取优惠 |

#### 通用运营（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 数据分析Agent | 经营日报/月报 | BI报表 |
| 报告生成Agent | 会议纪要/汇报材料 | 减少文山 |
| 项目管理Agent | 里程碑/风险/进度 | 交付透明 |
| 客服支持Agent | 售后/投诉/FAQ | 响应<4h |

## 三、行业Know-How（塑化行业）

### 核心业务流程
```
原料采购 → 来料检测 → 生产排产 → 质量控制 → 成品入库
    ↓                                           ↓
客户询价 ← 报价响应 ← 订单评审 ← 交期确认   物流发货
```

### 关键KPI
| 指标 | 目标 |
|------|------|
| 原料库存周转 | ≥12次/年 |
| 来料合格率 | ≥98% |
| 交期达成率 | ≥95% |
| 产品合格率 | ≥99.5% |
| 毛利率 | ≥20% |
| 客户复购率 | ≥60% |

## 四、技术实现

### 架构
- ChiefOfStaff = LangGraph 状态机
- 各Agent = Python async 函数
- API层 = FastAPI
- 数据源 = ERP/MES/WMS/CRM API

### 关键词路由表
| 关键词 | Agent |
|--------|-------|
| 原料/供应商/行情/比价 | 原料采购Agent |
| 库存/库位/周转 | 仓储管理Agent |
| 排产/工单/交期 | 生产调度Agent |
| 配方/新材料/成本 | 配方研发Agent |
| 质量/检测/合格率 | 质量检测Agent |
| 设备/维修/停机 | 设备维护Agent |
| 报价/价格/成本 | 报价Agent |
| 订单/发货/交期 | 订单履约Agent |
| 客户/跟进/复购 | 客户管理Agent |
| 竞品/市场/定价 | 竞品监控Agent |
| 成本/毛利/利润 | 成本核算Agent |
| 合规/环保/安全 | 合规审查Agent |
| 风控/预警/呆账 | 风险预警Agent |
| 政策/补贴/税务 | 政策解读Agent |
| 数据/报表/月报 | 数据分析Agent |
| 报告/会议/文档 | 报告生成Agent |
| 项目/里程碑/进度 | 项目管理Agent |
| 售后/投诉/客服 | 客服支持Agent |
