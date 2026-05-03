# Feature Requests | 功能建议与需求扩展

> 义乌.Skill 自进化机制核心文件
> 记录用户需求的实战功能扩展建议

**需求类型**: tool_request | content_request | integration_request | workflow_request

---

## 需求记录规范

| 需求类型 | 说明 | 处理优先级 |
|----------|------|------------|
| tool_request | 工具/计算器类需求 | P1 |
| content_request | 内容/知识库扩展 | P2 |
| integration_request | 系统对接需求 | P2 |
| workflow_request | SOP流程优化 | P3 |

---

## 示例条目

### [REQ-YYYYMMDD-001] tool_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P1
**Status**: pending
**Category**: finance

### Summary
自动报价计算器：一键计算FOB/CIF/DDP价格

### Details
**用户场景**：
- 客户询价时，需要快速计算各种贸易术语下的报价
- 当前需要手动计算：成本+运费+保险+关税+利润
- 希望有输入采购价、目的港、货量，自动输出报价

**功能需求**：
- 支持FOB/CIF/DDP/EXW四种报价方式
- 内置主要目的港运费查询（义新欧/海运/空运）
- 关税自动估算（基于HS编码）
- 利润率滑块调节
- 一键生成报价单（PDF/Excel）

### Suggested Implementation
```javascript
// 伪代码示例
function calculatePrice(cost, destination, volume, tradeTerm, profitMargin) {
  const freight = getFreight(destination, volume);
  const insurance = cost * 0.001; // 货值0.1%
  const duty = calculateDuty(cost, destination.HSCode);
  const total = tradeTerm === 'FOB' ? cost : 
                tradeTerm === 'CIF' ? cost + freight + insurance :
                cost + freight + insurance + duty;
  return total / (1 - profitMargin);
}
```

### Metadata
- Source: user_feedback
- Related Files: scripts/price_calculator.py
- Tags: 报价工具, 成本核算, FOB/CIF/DDP
- Frequency: 高频需求（>5次）

---

### [REQ-YYYYMMDD-002] content_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P2
**Status**: pending
**Category**: sales

### Summary
TikTok Shop开店指南：小商品出海新渠道

### Details
**背景**：
- TikTok Shop在东南亚、欧美快速增长
- 义乌小商品适合短视频电商（低价、视觉化）
- 用户询问如何从传统B2B转型到TikTok电商

**内容需求**：
- TikTok Shop入驻条件与流程
- 义乌货盘选择建议（适合TikTok的品类）
- 物流方案（TikTok官方仓 vs 海外仓 vs 专线）
- 选品策略（爆款逻辑、季节性备货）
- 视频内容制作指南
- 直播带货SOP

### Suggested Implementation
新增文档：`references/tiktok_shop_guide.md`

### Metadata
- Source: user_feedback
- Tags: TikTok Shop, 跨境电商, 选品策略
- Frequency: 中频需求（3-5次）

---

### [REQ-YYYYMMDD-003] tool_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P1
**Status**: pending
**Category**: logistics

### Summary
物流方案智能匹配器：输入目的地+货值+紧急度，自动推荐最优方案

### Details
**用户场景**：
- 新手外贸人不清楚如何选择物流
- 需要综合考虑时效、成本、货值、安全性
- 希望系统自动给出推荐方案及理由

**功能需求**：
- 输入：目的地、货值、重量体积、紧急度
- 输出：推荐方案（Top3）+ 详细对比
- 包含：时效、费用、风险提示、注意事项
- 支持一键比价（多家货代）

### Suggested Implementation
参考SKILL.md中的"物流方案匹配矩阵"，扩展为智能工具

### Metadata
- Source: user_feedback
- Related Files: references/logistics_guide.md
- Tags: 物流方案, 智能推荐, 新手友好

---

### [REQ-YYYYMMDD-004] integration_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P2
**Status**: pending
**Category**: data

### Summary
与Chinagoods平台API对接：订单自动同步

### Details
**用户场景**：
- Chinagoods平台订单需要手动同步
- 订单管理、发货跟踪、财务核对繁琐
- 希望与现有ERP/CRM系统打通

**技术需求**：
- Chinagoods开放平台API接入
- 订单自动同步到本地系统
- 物流单号自动回填
- 收汇状态自动更新

### Suggested Implementation
- 文档化Chinagoods API接入流程
- 提供订单同步SOP
- 如有开放API，集成到技能体系中

### Metadata
- Source: user_feedback
- Tags: Chinagoods, API对接, 自动化

---

### [REQ-YYYYMMDD-005] workflow_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P3
**Status**: pending
**Category**: compliance

### Summary
1039合规自查清单自动化：定期提醒+一键生成报告

### Details
**用户场景**：
- 1039合规要求复杂，容易遗漏
- 季度/年度审计需要准备大量材料
- 希望有清单化工具降低合规风险

**功能需求**：
- 合规检查清单（日常）
- 预警提醒（证件到期、额度预警等）
- 一键生成合规报告（PDF）
- 历史记录存档

### Suggested Implementation
扩展 `references/compliance_guide.md` 中的自查清单为可交互工具

### Metadata
- Source: user_feedback
- Related Files: references/compliance_guide.md
- Tags: 1039合规, 合规工具, 自动化

---

### [REQ-YYYYMMDD-006] content_request

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: P2
**Status**: pending
**Category**: sales

### Summary
亚马逊FBA入门指南：义乌卖家如何切入亚马逊

### Details
**背景**：
- 亚马逊FBA是B2C出海重要渠道
- 义乌卖家有供应链优势（轻小件、FBA友好）
- 用户希望了解从0到1切入亚马逊的路径

**内容需求**：
- 亚马逊FBA入驻流程（北美站/欧洲站）
- 选品策略（义乌优势品类）
- FBA费用计算器
- Listing优化指南
- 仓储物流（FBA vs 海外仓）
- 税务合规（VAT/EIN）

### Suggested Implementation
新增文档：`references/amazon_fba_guide.md`

### Metadata
- Source: user_feedback
- Tags: 亚马逊FBA, 跨境电商, B2C

---

## 需求优先级评估

### 评估维度
| 维度 | 说明 | 权重 |
|------|------|------|
| Frequency | 需求出现频次 | 30% |
| Impact | 对业务的提升幅度 | 40% |
| Effort | 实现难度 | 30% |

### 优先级矩阵
| 频次 | 影响大 | 影响中 | 影响小 |
|------|--------|--------|--------|
| 高频 | **P0-紧急** | P1-重要 | P2-普通 |
| 中频 | P1-重要 | P2-普通 | P3-可选 |
| 低频 | P2-普通 | P3-可选 | 暂缓 |

### 需求路线图
| 季度 | 计划实现 | 状态 |
|------|----------|------|
| Q2 2026 | 报价计算器 | 待开发 |
| Q2 2026 | TikTok Shop指南 | 待开发 |
| Q3 2026 | 物流智能匹配器 | 规划中 |
| Q3 2026 | 亚马逊FBA指南 | 规划中 |

---
