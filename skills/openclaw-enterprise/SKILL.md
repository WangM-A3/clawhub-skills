---
name: openclaw-enterprise
description: >-
  Use when user needs enterprise multi-agent collaboration system.
  Use when orchestrating 1 ChiefOfStaff + multiple specialized AI agents.
  Use when assisting cross-department workflow planning (procurement/sales/finance/HR).
  Use when setting up AI team coordination or workflow planning.
  Use when user mentions "幕僚长", "AI团队", "运营规划", "数字员工", "多Agent协作".
homepage: https://openclaw.ai
license: MIT-0
version: 1.2.6
progressive:
  layers:
    - name: metadata
      tokens: 200
      loaded: startup
      description: "技能基础配置、Agent列表、定价信息"
    - name: instructions
      tokens: 5000
      loaded: trigger
      description: "系统定位、团队架构、技术实现、部署方式"
    - name: resources
      tokens: variable
      loaded: on-demand
      description: "关键词路由表、工作流模板、配置指南"
  resource_paths:
    - scripts/*.py
    - templates/*.md
    - references/routing_tables/
metadata:
  openclaw:
    homepage: https://openclaw.ai
    primaryEnv: OPENAI_API_KEY
    requires:
      env:
        - OPENAI_API_KEY
      bins:
        - python3
        - pip
        - curl
    third_party:
      - name: GitHub
        domain: github.com
        purpose: "开源社区协作，源码托管"
        verify_url: https://github.com/openclaw
    apis:
      - name: OpenAI API
        domain: api.openai.com
        purpose: "LLM大语言模型调用，用于Agent推理和内容生成"
        auth:
          type: Bearer Token
          env_var: OPENAI_API_KEY
      - name: Anthropic API
        domain: api.anthropic.com
        purpose: "Claude大语言模型调用，用于高级推理和内容生成"
        auth:
          type: Bearer Token
          env_var: ANTHROPIC_API_KEY
          optional: true
          note: "可选，配置后启用Claude增强推理能力"
    emoji: "🏢"
    version: "1.2.6"
    author: "OpenClaw AI Team"
    category: "enterprise-ai"
    tags: ["multi-agent", "enterprise", "collaboration", "workflow", "planning", "运营自动化", "AI团队"]
pricing:
  basic:
    price: 999
    currency: CNY
    period: month
    features: ["1个幕僚长+5个专业Agent", "基础工作流", "10个并发用户"]
  professional:
    price: 3999
    currency: CNY
    period: month
    features: ["1个幕僚长+20个专业Agent", "全链路覆盖", "流程协同", "50个并发用户", "SLA 99.5%"]
  enterprise:
    price: 29999
    currency: CNY
    period: month
    features: ["私有部署", "行业定制", "源码交付", "无限并发", "专属顾问"]
triggers:
  - "多Agent协作"
  - "运营自动化"
  - "企业AI团队"
  - "幕僚长调度"
  - "AI工作流"
  - "智能运营"
  - "团队协作"
  - "流程规划"
  - "企业智能化"
  - "数字员工"
  - "AI助手团队"
---

# 企业多Agent协作系统：1个幕僚长+20个专业Agent辅助运营决策

还在为团队协作效率低、跨部门沟通成本高而头疼？
OpenClaw Enterprise用1个幕僚长+20个专业AI Agent，帮你把运营规划效率提升到新高度。

## 【能做什么】

- **智能规划**：幕僚长自动理解需求，生成各专业领域协作方案
- **全链路覆盖**：采购/生产/销售/财务/人事/合规，20个专业Agent各展所长
- **7×24在线**：AI永不疲劳，节假日、深夜均可正常运转
- **自然语言交互**：用日常语言调度整个AI团队，无需学习命令行

## 【效果数据】

- 规划响应时间：从天级→分钟级
- 运营规划效率：80%重复规划工作由AI辅助完成
- 团队效能：提升10倍

## 【安装】

```bash
# 通过ClawHub CLI安装
openclaw skills install openclaw-enterprise
```

适合中大型企业、电商平台、运营团队转型。

---

## 一、系统定位

OpenClaw Enterprise 是一个企业级多Agent协作规划系统，用AI模拟完整的中层管理团队。
1个幕僚长（ChiefOfStaff）负责统筹协调，20个专业Agent负责方案生成，覆盖企业运营全链路。

## 二、团队架构

### 幕僚长（ChiefOfStaff）
- 任务分发、调度、方案整合
- 支持自然语言生成交互建议
- 主动提示风险和优化方向
- 支持多Agent并行执行与结果聚合

### 核心执行Agent（20个）

#### 采购与供应链（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 原料采购Agent | 采购方案建议/行情参考/采购规划辅助 | 比价分析 |
| 仓储管理Agent | 库存规划建议/仓储优化方案 | 安全库存规划 |
| 物流调度Agent | 车队匹配/路线优化建议 | 降低物流成本 |
| 供应商管理Agent | 评级/风控/合同建议 | 供应商KPI评估 |

#### 生产与研发（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 生产调度Agent | 排产/工单管理建议 | 交期规划参考 |
| 配方研发Agent | 新材料/替代料推荐 | 成本优化参考 |
| 质量检测Agent | 来料/过程/成品方案 | 合标率建议 |
| 设备维护Agent | 预测性维护规划 | 减少停机建议 |

#### 销售与市场（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 报价Agent | 快速响应/成本叠加建议 | 提升响应速度 |
| 订单履约Agent | 订单跟踪/异常处理建议 | 客户满意度参考 |
| 客户管理Agent | 客户分级/跟进方案 | 复购率提升参考 |
| 竞品监控Agent | 市场趋势分析/定价策略建议 | 定价决策辅助 |

#### 财务与合规（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 成本核算Agent | 实际成本/标准成本分析 | 毛利分析参考 |
| 合规审查Agent | 环保/安全/税务方案 | 减少处罚建议 |
| 风险预警Agent | 客户信用/材料波动分析 | 降低坏账建议 |
| 政策解读Agent | 行业政策/补贴解读 | 争取优惠参考 |

#### 通用运营（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 数据分析Agent | 经营日报/月报建议 | BI报表参考 |
| 报告生成Agent | 会议纪要/汇报材料生成 | 减少文山会海 |
| 项目管理Agent | 里程碑/风险/进度规划 | 交付透明参考 |
| 客服支持Agent | 售后/投诉/FAQ方案 | 响应<4h参考 |

## 三、技术实现

### 架构
- ChiefOfStaff = LangGraph 状态机
- 各Agent = Python async 函数
- API层 = FastAPI
- 业务信息参考来源 = ERP/MES/WMS/CRM

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

## 四、部署方式

### SaaS版（开箱即用）
- 直接使用API服务，无需部署
- 按月订阅，按需扩展

### 私有部署版
- 部署到客户自有服务器
- 支持企业业务流程协同
- 行业定制开发

### API接入
- RESTful API
- Webhook事件通知
- 支持Python/Node.js/Java SDK

---

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "ChiefOfStaff replaces managers" | ChiefOfStaff orchestrates agents; human managers handle exceptions and strategy |
| "More agents = better results" | Quality of orchestration matters more than agent count |
| "One workflow fits all departments" | Each department has unique processes requiring customization |
| "AI never makes mistakes" | Agents can hallucinate; verification and guardrails are essential |
| "Deploy and forget" | Continuous monitoring and tuning required for optimal performance |

## Verification

After completing openclaw-enterprise workflow:
- [ ] 确认幕僚长正确理解用户意图（检查任务解析结果）
- [ ] 验证Agent路由准确率≥92%（对照路由表抽样检查）
- [ ] 多Agent并发任务无死锁或状态冲突
- [ ] 跨部门工作流数据传递完整无误
- [ ] 执行结果符合预期SLA（响应时间、准确率）
- [ ] 异常情况已触发预警并记录日志
- [ ] 最终输出格式符合业务规范要求
- [ ] ChiefOfStaff汇总报告逻辑自洽、信息完整


---

## 五、Security & Privacy

### 存储根路径
```
./data/openclaw-enterprise/
├── agents/          # Agent配置和状态
├── workflows/       # 工作流模板和执行记录
├── outputs/         # 生成的文件和报告
└── logs/            # 运行日志
```

### 数据处理原则
- **本地优先**：所有业务数据仅在本地处理，不上传到第三方服务器
- **敏感数据保护**：API密钥、密码、业务机密数据不写入日志或输出文件
- **最小化留存**：执行完成后清理中间临时文件，仅保留必要结果

### 权限边界声明
- ✅ **允许**：读取 `./data/openclaw-enterprise/` 目录下的配置文件和模板
- ✅ **允许**：写入 `./data/openclaw-enterprise/output/` 目录生成的文件
- ✅ **允许**：读取技能目录下的 `scripts/`、`templates/`、`references/` 资源
- ❌ **禁止**：访问系统关键目录（如 `/etc/`, `/root/`, `~/.ssh/`）
- ❌ **禁止**：修改系统文件或配置文件
- ❌ **禁止**：访问用户其他敏感目录（如 `/home/`, `/var/`）

### API密钥管理策略
- **加密存储**：API密钥存储在环境变量或加密的配置文件（如 `.env`）
- **最小权限**：仅申请执行任务所需的最小API权限
- **不外泄**：密钥不写入日志、不在输出中暴露、不发送给第三方
- **定期轮换**：建议定期更换API密钥

### 多Agent调度安全
- **并发限制**：单次任务最多调度5个Agent，防止资源耗尽
- **操作确认**：涉及数据修改的操作需用户确认
- **操作日志**：所有Agent操作记录完整日志，支持审计
