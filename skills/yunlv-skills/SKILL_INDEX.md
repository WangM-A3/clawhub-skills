# 云旅AI外贸技能市场 - 技能总览索引

> 首批8个P0优先级技能 | 覆盖客户开发、沟通转化、数据分析、合规风控四大类

---

## 📦 技能包信息

| 属性 | 值 |
|------|------|
| 技能包名称 | 云旅AI外贸技能包（yunlv-skills） |
| 版本 | 1.0.0 |
| 开发者 | 云旅AI团队 |
| 官方网站 | https://yunlvai.com |
| 许可协议 | MIT-0 |
| 定价模式 | Freemium（基础免费，高级付费订阅） |

---

## 🗂️ 技能目录结构

```
yunlv-skills/
├── SKILL_INDEX.md                    # 本文件 - 技能总览
├── SKILL_GUANGJIAOFAI.md            # 技能1：广交会客户挖掘
├── SKILL_CUSTOMS_SCOUT.md           # 技能2：海关数据智能获客
├── SKILL_LINKEDIN_OUTREACH.md       # 技能3：LinkedIn开发信生成
├── SKILL_EMAIL_WRITER.md            # 技能4：多语言邮件撰写
├── SKILL_PRODUCT_DESC.md            # 技能5：产品差异化描述生成
├── SKILL_PRICE_MONITOR.md           # 技能6：竞品价格监控
├── SKILL_COMPLIANCE_CHECK.md        # 技能7：进出口合规检查
├── SKILL_CONTRACT_DRAFT.md          # 技能8：外贸合同智能起草
└── references/                       # 参考文档库
    ├── canton_fair_categories.md     # 广交会展品分类表
    ├── linkedin_message_templates.md # LinkedIn话术模板库
    ├── contract_type_templates.md    # 合同类型模板
    ├── certification_requirements.md # 认证要求清单
    ├── data_filter_rules.md          # 数据过滤规则（规划中）
    ├── customer_scoring_model.md     # 客户评分模型（规划中）
    ├── outreach_templates.md          # 开发信模板（规划中）
    ├── followup_strategy.md          # 展会跟进策略（规划中）
    ├── industry_hooks_library.md      # 行业钩子库（规划中）
    ├── followup_sequence_templates.md # 跟进序列模板（规划中）
    ├── industry_vocabulary.md         # 行业产品词库（规划中）
    ├── differentiation_templates.md   # 差异化话术模板（规划中）
    ├── platform_guide.md              # 平台适配指南（规划中）
    ├── competitor_list_template.md    # 竞品监控模板（规划中）
    ├── price_analysis_report.md       # 价格分析报告模板（规划中）
    ├── pricing_strategy_guide.md      # 定价策略指南（规划中）
    ├── sanctions_screening.md         # 制裁名单筛查指南（规划中）
    ├── compliance_report_template.md   # 合规报告模板（规划中）
    ├── international_commercial_law.md # 国际商法参考（规划中）
    ├── clause_risk_checklist.md       # 条款风险清单（规划中）
    ├── email_type_templates.md         # 邮件类型模板（规划中）
    ├── multi_language_guide.md         # 多语言邮件指南（规划中）
    ├── email_sequence_templates.md     # 邮件序列模板（规划中）
    └── (更多参考文件持续补充中)
```

---

## 🎯 技能速查表

### 按类别分类

| 类别 | 技能名称 | 编号 | 核心场景 |
|------|---------|------|----------|
| **客户开发** | 广交会客户挖掘 | SKILL_GUANGJIAOFAI | 展会数据挖掘、展商联系 |
| **客户开发** | 海关数据智能获客 | SKILL_CUSTOMS_SCOUT | 进出口数据、竞品客户 |
| **客户开发** | LinkedIn开发信生成 | SKILL_LINKEDIN_OUTREACH | 社媒触达、决策人挖掘 |
| **客户开发** | 产品差异化描述生成 | SKILL_PRODUCT_DESC | B2B内容创作、产品详情 |
| **沟通转化** | 多语言邮件撰写 | SKILL_EMAIL_WRITER | 开发信、询盘回复、报价 |
| **数据分析** | 竞品价格监控 | SKILL_PRICE_MONITOR | 价格趋势、竞争情报 |
| **合规风控** | 进出口合规检查 | SKILL_COMPLIANCE_CHECK | 认证、关税、制裁筛查 |
| **合规风控** | 外贸合同智能起草 | SKILL_CONTRACT_DRAFT | PI、合同、NDA |

### 按关键词快速定位

| 关键词 | 对应技能 |
|--------|----------|
| 广交会/展会/摊位 | SKILL_GUANGJIAOFAI |
| 海关/进出口/竞品客户 | SKILL_CUSTOMS_SCOUT |
| LinkedIn/领英/社媒 | SKILL_LINKEDIN_OUTREACH |
| 邮件/开发信/询盘 | SKILL_EMAIL_WRITER |
| 产品描述/差异化/卖点 | SKILL_PRODUCT_DESC |
| 价格/竞品/监控 | SKILL_PRICE_MONITOR |
| 合规/认证/制裁/关税 | SKILL_COMPLIANCE_CHECK |
| 合同/PI/起草/审核 | SKILL_CONTRACT_DRAFT |

---

## 🔗 技能联动场景

云旅AI技能的最大价值在于多技能联动，覆盖外贸全链路：

### 场景1：新客户全链路开发
```
① CUSTOMS_SCOUT（挖掘目标采购商）
   → ② LINKEDIN_OUTREACH（找到决策人LinkedIn）
   → ③ EMAIL_WRITER（生成个性化开发信）
   → ④ COMPLIANCE_CHECK（签约前合规筛查）
   → ⑤ CONTRACT_DRAFT（起草PI/合同）
```

### 场景2：展会全流程覆盖
```
① GUANGJIAOFAI（展会前预热目标客户）
   → ② CUSTOMS_SCOUT（评估展会上发现的客户）
   → ③ EMAIL_WRITER（展会后发送跟进邮件）
   → ④ COMPLIANCE_CHECK（重要客户合规筛查）
   → ⑤ CONTRACT_DRAFT（展会现场签PI）
```

### 场景3：产品全平台发布
```
① PRICE_MONITOR（分析市场价格区间）
   → ② PRODUCT_DESC（生成差异化产品描述）
   → ③ EMAIL_WRITER（向现有客户推送新品）
   → ④ CONTRACT_DRAFT（起草新品订单合同）
```

---

## 📋 首批15个技能路线图（扩展计划）

### P0（已完成）- 首批8个技能
1. ✅ SKILL_GUANGJIAOFAI - 广交会客户挖掘
2. ✅ SKILL_CUSTOMS_SCOUT - 海关数据智能获客
3. ✅ SKILL_LINKEDIN_OUTREACH - LinkedIn开发信生成
4. ✅ SKILL_EMAIL_WRITER - 多语言邮件撰写
5. ✅ SKILL_PRODUCT_DESC - 产品差异化描述生成
6. ✅ SKILL_PRICE_MONITOR - 竞品价格监控
7. ✅ SKILL_COMPLIANCE_CHECK - 进出口合规检查
8. ✅ SKILL_CONTRACT_DRAFT - 外贸合同智能起草

### P1（规划中）- 下一批7个技能
9. 🔄 SKILL_WHATSAPP_OUTREACH - WhatsApp客户触达
10. 🔄 SKILL_TRADE_SHOW_INTEL - 全球展会情报
11. 🔄 SKILL_CUSTOMER_CRM - 客户关系管理
12. 🔄 SKILL_MARKET_ANALYSIS - 目标市场分析
13. 🔄 SKILL_INCOTERMS_GUIDE - Incoterms运用指南
14. 🔄 SKILL_PAYMENT_TERMS - 付款方式选择
15. 🔄 SKILL_SHIPMENT_TRACKER - 货运追踪管理

---

## 📌 版本说明

### v1.0.0 (2025-04)
- 首批8个P0技能发布
- 覆盖客户开发、沟通转化、数据分析、合规风控四大类
- 所有技能支持中文/英文触发词
- 所有技能包含Security & Privacy章节
- 所有技能包含Common Rationalizations章节

---

*本技能包由云旅AI团队开发维护，版本持续迭代更新中。*
