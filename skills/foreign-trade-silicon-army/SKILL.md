---
name: foreign-trade-silicon-army
description: 外贸硅基军团 - 执行型AI Agent军团，外贸出海全自动。包含建站Agent、流量Agent、转化Agent，支持WordPress/Shopify自动建站、GEO优化、多渠道获客与转化。基于 Salesforce Agentforce Atlas 推理引擎，多智能体协同(MAS)架构。
version: 2.0.0
author: Silicon Army Team
homepage: https://github.com/silicon-army/foreign-trade-silicon-army

metadata:
  hermes:
    category: business-automation
    tags:
      - foreign-trade
      - ai-agent
      - seo
      - geo
      - multi-agent
      - atlas-reasoning
      - mas-system
      - grounding-check
      - wordpress
      - shopify
      - multi-channel
    runtime_version: "2.0"
    min_hermes_version: "1.0.0"

required_environment_variables:
  - name: WORDPRESS_SITE_URL
    description: WordPress站点URL，如 https://example.com
    required: false
  - name: WORDPRESS_USERNAME
    description: WordPress用户名（用于App Password认证）
    required: false
  - name: WORDPRESS_APP_PASSWORD
    description: WordPress应用专用密码
    required: false
  - name: SHOPIFY_DOMAIN
    description: Shopify店铺域名，如 my-store.myshopify.com
    required: false
  - name: SHOPIFY_ACCESS_TOKEN
    description: Shopify Admin API访问令牌
    required: false
  - name: OPENAI_API_KEY
    description: OpenAI API密钥（用于GEO优化和内容生成）
    required: false
  - name: DEEPSEEK_API_KEY
    description: DeepSeek API密钥（用于Atlas推理引擎）
    required: false
  - name: REDIS_URL
    description: Redis连接URL（用于任务队列）
    required: false
    default: "redis://localhost:6379/0"
  - name: DATABASE_URL
    description: PostgreSQL数据库连接字符串
    required: false
    default: "postgresql://user:pass@localhost:5432/silicon_army"
  # ───────────────────────────────────────────────────────────────────────────
  # P0 模块环境变量（v2.0 新增）
  # ───────────────────────────────────────────────────────────────────────────
  - name: WHATSAPP_PHONE_NUMBER_ID
    description: WhatsApp Business 虚拟号码 ID（Meta Graph API）
    required: false
  - name: WHATSAPP_ACCESS_TOKEN
    description: WhatsApp Business 长期 Access Token
    required: false
  - name: WHATSAPP_APP_SECRET
    description: Facebook App Secret（用于 Webhook 签名验证）
    required: false
  - name: WHATSAPP_WABA_ID
    description: WhatsApp Business Account ID
    required: false
  - name: WHATSAPP_WEBHOOK_VERIFY_TOKEN
    description: Webhook 验证 Token（自定义）
    required: false
  - name: WHATSAPP_CATALOG_ID
    description: WhatsApp 产品目录 ID（用于产品目录消息）
    required: false
  - name: TRANSLATION_PROVIDER
    description: 翻译服务提供商（deepseek | deepl | google | baidu | mock）
    required: false
    default: "deepseek"
  - name: TRANSLATION_API_KEY
    description: 翻译 API Key（如 DeepL / 百度翻译 Key）
    required: false
  - name: DEEPSEEK_API_KEY
    description: DeepSeek API Key（用于Atlas推理、翻译、AI客服及所有P1模块）
    required: false
  - name: OPENAI_API_KEY
    description: OpenAI API Key（Atlas推理引擎备选）
    required: false
  # ───────────────────────────────────────────────────────────────────────────
  # P1 模块环境变量（v2.0 新增）
  # ───────────────────────────────────────────────────────────────────────────
  - name: HUNTER_API_KEY
    description: Hunter.io API Key（潜客邮箱挖掘）
    required: false
  - name: CLEARBIT_API_KEY
    description: Clearbit API Key（公司信息查询）
    required: false
  - name: VISION_API_KEY
    description: 多模态视觉API Key（供应链图片分析）
    required: false
  - name: CRM_PLATFORM
    description: CRM平台类型（salesforce | hubspot | zoho | fenxiang | custom）
    required: false
  # Salesforce
  - name: SF_INSTANCE_URL
    description: Salesforce实例URL（如 https://xxx.salesforce.com）
    required: false
  - name: SF_CLIENT_ID
    description: Salesforce Connected App Client ID
    required: false
  - name: SF_CLIENT_SECRET
    description: Salesforce Connected App Client Secret
    required: false
  - name: SF_USERNAME
    description: Salesforce用户名
    required: false
  - name: SF_PASSWORD
    description: Salesforce密码
    required: false
  - name: SF_SECURITY_TOKEN
    description: Salesforce安全令牌
    required: false
  # HubSpot
  - name: HUBSPOT_ACCESS_TOKEN
    description: HubSpot Private App Access Token
    required: false
  # 纷享销客
  - name: FX_API_URL
    description: 纷享销客API地址
    required: false
  - name: FX_APP_ID
    description: 纷享销客 App ID
    required: false
  - name: FX_APP_SECRET
    description: 纷享销客 App Secret
    required: false
  - name: FX_CORP_ID
    description: 纷享销客企业 ID
    required: false
  - name: FX_PERMANENT_CODE
    description: 纷享销客永久授权码
    required: false
  # 自定义 Webhook
  - name: CRM_WEBHOOK_URL
    description: 自定义CRM Webhook地址
    required: false
  - name: CRM_WEBHOOK_AUTH
    description: Webhook认证头（如 Bearer token）
    required: false

supported_platforms:
  - linux
  - macos

installation:
  runtime: python3.10+
  dependencies:
    - httpx>=0.26.0
    - pydantic>=2.5.0
    - python-dotenv>=1.0.0
  verify_command: python scripts/wordpress_ops.py --test


# ============================================================================
# v2.0 核心能力：Atlas 推理引擎 + MAS 多智能体协同
# ============================================================================

capabilities:

  # ───────────────────────────────────────────────────────────────────────────
  # Atlas 推理引擎（核心新能力）
  # ───────────────────────────────────────────────────────────────────────────
  - name: atlas_reasoning_engine
    description: |
      基于 Salesforce Agentforce Atlas 推理引擎的 Plan-Evaluate-Refine-Retrieve 推理循环。
      自动分析用户意图，生成多步骤执行计划，评估最优动作，支持失败重试与策略优化。
    triggers:
      - "帮我分析..."
      - "制定一个方案"
      - "告诉我应该怎么做"
      - "流程是什么"
      - "step by step"
    files:
      - cloudbase/core/reasoning-engine.js
    architecture:
      phases:
        - Plan: 意图拆解 + 实体提取 + 知识检索 → 生成执行计划
        - Evaluate: 评估动作选择、依赖关系、是否需要审批
        - Execute: 串行/并行执行，支持重试与部分回滚
        - Retrieve: KnowForce 知识中台检索（组织知识 + 个人知识）
        - Refine: 失败后降级优化，重构后续步骤

  - name: mas_multi_agent
    description: |
      多智能体协同（MAS）系统，支持三种协作模式：
      - 并行协作：多个Agent同时处理不同子任务
      - 层级协作：主Agent协调子Agent依次执行
      - 监管模式：关键操作（如报价/发送邮件）需人工审批后执行
    triggers:
      - "需要多个Agent协作"
      - "同步处理这些任务"
      - "这些一起做"
    files:
      - cloudbase/core/reasoning-engine.js  # MASOrchestrator
    agent_manifest:
      - SiteAgent: 建站专家（SEO/Listing/内容）
      - TrafficAgent: 流量专家（Google/Meta/TikTok/LinkedIn）
      - ConversionAgent: 转化专家（邮件/报价/话术/跟进）

  - name: grounding_check
    description: |
      Grounding Check 响应验证机制，确保Agent响应基于真实数据。
      包含三大检查：幻觉检测（绝对化声明/无来源数据）、完整性验证（意图覆盖率）、
      知识溯源（来源标注覆盖率）。
    triggers:
      - "确认这个建议有依据"
      - "数据可靠吗"
      - "这个数据哪来的"
    files:
      - cloudbase/core/grounding-check.js

  - name: agent_script_dsl
    description: |
      Agent Script DSL 声明式逻辑编排，支持：
      - 变量系统：{{variable}} 模板变量
      - 条件分支：if/elif/else 逻辑判断
      - 话题切换：topic 定义与自动切换规则
      - 动作链：多步 action 链式调用
      - SSE输出：流式输出中间结果
    triggers:
      - "用脚本执行"
      - "topic:"
      - "action:"
    files:
      - cloudbase/core/agent-script.js

  - name: knowforce_knowledge
    description: |
      KnowForce 知识中台集成（Marketingforce AI-Agentforce 3.0 启发）。
      双轨道知识管理：组织知识图谱（企业共享知识）+ 个人知识（个人经验积累）。
      自动检索相关知识注入推理过程，提升响应准确度。
    triggers:
      - "基于我们的知识库"
      - "结合历史经验"
      - "参考公司案例"
    features:
      - 语义级知识萃取
      - 知识新鲜度过滤（默认30天内）
      - 知识关联图谱
      - 响应时自动引用来源

  # ───────────────────────────────────────────────────────────────────────────
  # 建站 Agent 能力
  # ───────────────────────────────────────────────────────────────────────────
  - name: build_site
    description: WordPress/Shopify自动建站，Atlas推理增强
    triggers:
      - "帮我建站"
      - "创建一个新的独立站"
      - "build a new website"
      - "帮我搭建网站"
    atlas_enhanced: true

  - name: seo_optimize
    description: SEO关键词布局与优化，Atlas多步骤推理诊断
    triggers:
      - "SEO优化"
      - "优化网站排名"
      - "optimize SEO"
      - "帮我诊断网站SEO"
    atlas_enhanced: true
    reasoning_steps:
      - fetchSeoData: 抓取SEO数据
      - analyzeSeoMetrics: 分析SEO指标
      - generateSeoReport: 生成诊断报告

  - name: keyword_research
    description: 关键词研究，竞品分析和关键词矩阵构建
    triggers:
      - "关键词研究"
      - "关键词布局"
      - "keyword research"
    atlas_enhanced: true

  - name: listing_optimize
    description: Amazon/独立站 Listing 创作与优化，含 Grounding Check
    triggers:
      - "优化Listing"
      - "详情页优化"
      - "产品描述"
    atlas_enhanced: true
    grounding_required: true

  - name: geo_optimize
    description: GEO（生成式引擎优化）优化，AI搜索呈现优化
    triggers:
      - "GEO优化"
      - "AI搜索优化"
      - "优化在ChatGPT中的呈现"
      - "生成式引擎优化"

  # ───────────────────────────────────────────────────────────────────────────
  # 流量 Agent 能力
  # ───────────────────────────────────────────────────────────────────────────
  - name: google_ads
    description: Google Ads 策略（搜索/展示/购物），Atlas推理编排
    triggers:
      - "Google Ads"
      - "Google广告"
      - "SEM投放"
    atlas_enhanced: true
    mas_parallel: true

  - name: meta_ads
    description: Meta (Facebook/Instagram) 广告，受众分层与创意策略
    triggers:
      - "Facebook广告"
      - "Meta Ads"
      - "Instagram广告"

  - name: tiktok_ads
    description: TikTok Ads 创意制作与投放策略
    triggers:
      - "TikTok广告"
      - "Tk Ads"

  - name: linkedin_b2b
    description: LinkedIn B2B 广告与内容运营，决策者触达
    triggers:
      - "LinkedIn广告"
      - "领英开发"

  - name: remarketing
    description: 全渠道再营销策略，漏斗分层与创意匹配
    triggers:
      - "再营销"
      - "Remarketing"
      - "Retargeting"

  - name: content_publish
    description: 多平台内容自动发布与社媒运营策略
    triggers:
      - "发布内容"
      - "社媒发布"
      - "publish to social media"
    mas_parallel: true

  - name: audience_research
    description: 目标受众分析与画像构建，海关数据应用
    triggers:
      - "受众分析"
      - "客户画像"
      - "audience research"

  - name: budget_plan
    description: 广告预算分配与优化策略
    triggers:
      - "预算规划"
      - "预算分配"
      - "广告预算"

  # ───────────────────────────────────────────────────────────────────────────
  # 转化 Agent 能力
  # ───────────────────────────────────────────────────────────────────────────
  - name: email_sequence
    description: 开发信/跟进信/催单邮件序列，KnowForce + Grounding
    triggers:
      - "开发信"
      - "邮件序列"
      - "cold email"
      - "跟进邮件"
    atlas_enhanced: true
    grounding_required: true
    reasoning_steps:
      - researchRecipient: 调研收件人背景
      - generateEmailDraft: 生成邮件草稿
      - personalizeTemplate: 个性化模板
      - validateEmailContent: 合规检查

  - name: quotation
    description: 报价策略（FOB/CIF/EXW），KnowForce历史定价检索
    triggers:
      - "报价"
      - "FOB价格"
      - "价目表"
      - "quote"
    atlas_enhanced: true
    grounding_required: true
    approval_required: true  # 报价需审批

  - name: sales_script
    description: WhatsApp/Email/LinkedIn 多渠道销售话术
    triggers:
      - "话术"
      - "销售脚本"
      - "WhatsApp话术"
    atlas_enhanced: true

  - name: lead_capture
    description: 精准获客与线索管理
    triggers:
      - "获取客户"
      - "挖掘潜在客户"
      - "lead generation"

  - name: multi_channel_inbox
    description: 多渠道消息聚合与自动回复
    triggers:
      - "聚合消息"
      - "多渠道收件箱"
      - "multi-channel inbox"

  - name: negotiation
    description: 议价与成交推进，Atlas推理决策树
    triggers:
      - "议价"
      - "谈判"
      - "客户嫌贵"

  - name: ab_test
    description: A/B 测试设计与统计显著性分析
    triggers:
      - "A/B测试"
      - "ab test"

  - name: customer_research
    description: 客户背调（海关数据/LinkedIn/社媒）
    triggers:
      - "客户背调"
      - "海关数据"
      - "客户调查"

  - name: follow_up
    description: 询盘跟进策略与漏斗管理
    triggers:
      - "跟进策略"
      - "询盘跟进"


  # ───────────────────────────────────────────────────────────────────────────
  # P0 能力：WhatsApp Business API（对标 SaleSmartly · 98%开放率）
  # ───────────────────────────────────────────────────────────────────────────
  - name: whatsapp_business_api
    description: |
      WhatsApp Business API 集成，支持：
      • 文本/图片/文档/语音/视频消息发送
      • 模板消息（Template Messages）— 提升98%开放率
      • 交互式按钮消息（Interactive Button）
      • 列表消息（List Message）— 适用于产品目录/订单查询
      • Webhook 事件处理（消息接收/状态回调/表情反应）
      • 联系人管理与标签
      • 消息状态追踪（sent → delivered → read → failed）
      • 批量群发
    triggers:
      - "whatsapp"
      - "WhatsApp Business"
      - "wa消息"
      - "wa客户"
      - "wa群发"
      - "what's app"
    files:
      - cloudbase/modules/whatsapp-integration.js
    metrics:
      delivery_rate: "> 99%"
      avg_response_time: "< 2s"
      open_rate: "> 98%"


  # ───────────────────────────────────────────────────────────────────────────
  # P0 能力：134语言实时翻译（对标 SaleSmartly）
  # ───────────────────────────────────────────────────────────────────────────
  - name: multilingual_translation
    description: |
      支持134种语言的实时翻译，核心能力：
      • 外贸专业术语库（FOB/CIF/L/C/MOQ/HS Code等中英双语）
      • 翻译记忆库（TM）— 提高术语一致性，减少重复翻译成本
      • 上下文感知翻译 — 保留商业语义，提升专业度
      • 语言自动检测（字符集分析 + AI检测）
      • 批量翻译接口（支持并发控制）
      • 自定义术语管理
      • 支持 DeepSeek / DeepL / Google Translate / 百度翻译等多种后端
    triggers:
      - "翻译"
      - "多语言"
      - "134语言"
      - "translator"
      - "中译英"
      - "英译中"
      - "小语种"
      - "开发信翻译"
    files:
      - cloudbase/modules/multilingual-translator.js
    metrics:
      language_count: 134
      translation_accuracy: "> 95%"
      avg_latency: "< 500ms"


  # ───────────────────────────────────────────────────────────────────────────
  # P0 能力：AI客服（对标 Instadesk · 80%自动化）
  # ───────────────────────────────────────────────────────────────────────────
  - name: ai_customer_service
    description: |
      AI 客服模块，实现 80% 自动化率，核心能力：
      • 智能意图识别（20+ 意图类型，外贸场景扩展）
      • 情感分析（5级评分，自动检测紧急升级信号）
      • 自动回复生成（基于知识库RAG + DeepSeek AI）
      • 工单自动创建/分配（SLA计时 / 优先级路由）
      • 多轮对话管理（槽位填充 / 上下文继承）
      • 人工接管触发（情感触发 / 意图触发 / SLA违规 / 次数上限）
      • 知识库检索（RAG，支持自定义文档）
      • 服务质量评分（CSAT 1-5分）
    triggers:
      - "客服"
      - "工单"
      - "投诉"
      - "售后"
      - "ticket"
      - "robot response"
      - "ai 回复"
      - "转人工"
      - "chatbot"
    files:
      - cloudbase/modules/ai-customer-service.js
    metrics:
      automation_rate: "> 80%"
      intent_accuracy: "> 90%"
      customer_satisfaction: "> 4.5/5"


  # ───────────────────────────────────────────────────────────────────────────
  # P1 能力：HS编码智能查询（对标 EximGPT · OKKI）
  # ───────────────────────────────────────────────────────────────────────────
  - name: hs_code_query
    description: |
      HS编码智能查询与关税税率模块，对标 EximGPT RaaS（按效果付费）和 OKKI 65万次/年高频刚需：
      • HS Code 智能查询（模糊匹配 / 关键词搜索 / AI归类建议）
      • 关税税率查询（目标国家 / FTA优惠税率 / MFN税率）
      • 进出口管制检测（许可证 / 禁止进出口 / 配额管理）
      • 产品归类建议（多方案排序 + 置信度评分）
      • 历史申报记录关联（同类商品参考）
      • 批量查询接口（并发控制）
      支持数据源：WCO / 中国海关 / USITC / EU TARIC
    triggers:
      - "HS编码"
      - "hs code"
      - "关税税率"
      - "产品归类"
      - "tariff"
      - "duty rate"
      - "import duty"
      - "export control"
      - "许可证"
    files:
      - cloudbase/modules/hs-code-query.js
    metrics:
      search_accuracy: "> 90%"
      duty_rate_coverage: "覆盖180+国家/地区"
      response_latency: "< 2s"


  # ───────────────────────────────────────────────────────────────────────────
  # P1 能力：谈单节点AI预警（对标 OKKI · 65万次/年预警系统）
  # ───────────────────────────────────────────────────────────────────────────
  - name: deal_stage_monitor
    description: |
      谈单节点AI预警系统，对标 OKKI 65万次/年谈单预警能力：
      • 谈单阶段识别（询盘→报价→样品→谈判→合同→成交/流失）
      • 关键节点监测（超时提醒 / 风险预警 / 最佳跟进窗口）
      • 自动跟进建议（基于阶段 + 客户画像 + AI生成）
      • 成交概率预测（机器学习评分模型，多维度因子）
      • 多渠道预警推送（WhatsApp / Email / Webhook）
      • 批量监控（定时任务，每日/每周报告）
      • 与 WhatsApp/P0模块协同（自动推送预警通知）
    triggers:
      - "谈单"
      - "跟进"
      - "成交概率"
      - "预警"
      - "谈单节点"
      - "deal stage"
      - "follow up"
      - "win probability"
      - "alert"
    files:
      - cloudbase/modules/deal-stage-monitor.js
    metrics:
      alert_accuracy: "> 85%"
      win_prob_accuracy: "> 78%"
      overdue_detection: "100%"


  # ───────────────────────────────────────────────────────────────────────────
  # P1 能力：潜客智能推荐（对标 OKKI潜客背调 · 遨虾供应链匹配）
  # ───────────────────────────────────────────────────────────────────────────
  - name: lead_recommendation
    description: |
      潜客智能推荐系统，对标 OKKI潜客背调和遨虾供应链匹配：
      • 多维度潜客画像（公司规模 / 行业 / 采购行为 / 决策链）
      • 智能匹配算法（产品需求 / 地域 / 采购量级 / 合作意向）
      • 潜客评分排序（综合评分 + 多维度子评分）
      • 推荐理由生成（AI生成个性化推荐语）
      • 转化追踪（跟进状态 / 转化漏斗 / ROI计算）
      • 外部数据集成（Hunter.io邮箱挖掘 / Clearbit公司数据 / LinkedIn）
      • 每日潜客推送（定时任务，按评分优先级排序）
    triggers:
      - "潜客"
      - "客户推荐"
      - "新客户"
      - "采购商"
      - "客户背调"
      - "leads"
      - "prospect"
      - "lead score"
      - "客户画像"
    files:
      - cloudbase/modules/lead-recommendation.js
    metrics:
      match_accuracy: "> 80%"
      lead_quality: "A/B/C/D四级分类"
      roi_tracking: "端到端"


  # ───────────────────────────────────────────────────────────────────────────
  # P1 能力：CRM多平台连接器（对标 OKKI阿里巴巴生态集成）
  # ───────────────────────────────────────────────────────────────────────────
  - name: crm_connector
    description: |
      CRM多平台连接器，对标 OKKI 阿里巴巴生态集成：
      • 支持主流CRM：Salesforce / HubSpot / Zoho / 纷享销客 / 自定义Webhook
      • 双向数据同步（Contacts / Deals / Tasks）
      • 联系人去重（多维度匹配：姓名+邮箱 / 公司+职位）
      • 交易记录关联（Orders / Invoices / Shipments）
      • 自定义字段映射（JSON Schema灵活配置）
      • 冲突解决策略（Last-Write-Wins / 优先级 / 手动确认）
      • Webhook事件订阅（实时同步，触发业务自动化）
      • 同步队列管理（失败重试 / 状态追踪）
    triggers:
      - "CRM"
      - "salesforce"
      - "hubspot"
      - "纷享销客"
      - "CRM同步"
      - "联系人同步"
      - "contact sync"
    files:
      - cloudbase/modules/crm-connector.js
    metrics:
      platform_support: "5+平台"
      sync_latency: "< 5s"
      deduplication_accuracy: "> 95%"


  # ───────────────────────────────────────────────────────────────────────────
  # P1 能力：供应链智能匹配（对标遨虾"所见即可卖"）
  # ───────────────────────────────────────────────────────────────────────────
  - name: supply_chain_matcher
    description: |
      供应链智能匹配系统，对标遨虾"所见即可卖"端到端链路：
      • 图像特征提取（视觉识别 → HS编码推断 → 供应商匹配）
      • 供应商能力匹配（产能 / MOQ / 交期 / 认证 / 价格）
      • 最优供应商推荐（综合评分 + 排序算法）
      • 采购决策辅助（风险评估 / 成本分析 / 交付评估）
      • 批量供应商对比（多维度评分矩阵）
      • 最优采购方案生成（单源 / 双源分散 / 成本最优组合）
      • AI采购建议（供应商核心优势 + 谈判建议）
      • 贸易战规避建议（越南/印度替代供应商推荐）
    triggers:
      - "供应链"
      - "供应商"
      - "匹配"
      - "采购"
      - "MOQ"
      - "交期"
      - "product matching"
      - "supplier"
      - "supply chain"
      - "procurement"
      - "图片找供应商"
      - "所见即可卖"
    files:
      - cloudbase/modules/supply-chain-matcher.js
    metrics:
      match_accuracy: "> 85%"
      supplier_coverage: "覆盖全球主要供应商"
      price_optimal: "AI优化方案"


# ============================================================================
# 技术架构（v2.0）
# ============================================================================

architecture:

  # ─── Atlas 推理引擎 ───
  atlas_engine:
    description: |
      Salesforce Agentforce Atlas 架构实现，5阶段推理循环
    file: cloudbase/core/reasoning-engine.js
    classes:
      - AtlasReasoningEngine: 核心推理引擎
      - MASOrchestrator: 多智能体协同调度器
      - PlanStep: 执行计划步骤
    exports:
      - AtlasReasoningEngine
      - MASOrchestrator
      - StepStatus
      - PlanStatus

  # ─── Agent Script DSL ───
  agent_script:
    description: 声明式Agent逻辑编排
    file: cloudbase/core/agent-script.js
    classes:
      - AgentScriptParser: DSL解析与执行器
      - TopicManager: 话题切换管理器
    syntax:
      - variable: "variable: varname = value"
      - topic: "topic: topic_name"
      - action: "action: methodName with: {param1: value}"
      - conditional: "if: {{customer.is_vip}} then: escalate_to_human"
      - goto: "goto: billing_inquiry"
      - output: "say: 欢迎词内容"

  # ─── Grounding Check ───
  grounding:
    description: 响应接地验证与幻觉检测
    file: cloudbase/core/grounding-check.js
    checks:
      - hallucination: 绝对化声明、无来源数据、虚构引用检测
      - completeness: 意图覆盖率、内容长度、结构完整性
      - knowledge_trace: 知识溯源、来源标注覆盖率
    severity_levels:
      - high: 高严重性，立即标记，可能触发FAIL
      - medium: 中等严重性，建议修正
      - low: 低严重性，可自动修复

  # ─── 三大专业Agent ───
  agents:
    site_agent:
      file: cloudbase/army/site-agent.js
      parent_file: cloudbase/agent.js
      capabilities:
        - seo_optimize
        - keyword_research
        - listing_optimize
        - geo_optimize
      atlas_integration: true
      grounding_integration: true

    traffic_agent:
      file: cloudbase/army/traffic-agent.js
      parent_file: cloudbase/agent.js
      capabilities:
        - google_ads
        - meta_ads
        - tiktok_ads
        - linkedin_b2b
        - remarketing
        - content_publish
        - audience_research
        - budget_plan
      atlas_integration: true
      mas_integration: true

    conversion_agent:
      file: cloudbase/army/conversion-agent.js
      parent_file: cloudbase/agent.js
      capabilities:
        - email_sequence
        - quotation
        - sales_script
        - follow_up
        - negotiation
        - customer_research
        - ab_test
        - landing_page
      atlas_integration: true
      grounding_integration: true
      knowforce_integration: true

    # ───────────────────────────────────────────────────────────────────────────
    # P0 模块（v2.0 新增）
    # ───────────────────────────────────────────────────────────────────────────
    whatsapp_integration:
      file: cloudbase/modules/whatsapp-integration.js
      parent_file: cloudbase/agent.js
      classes:
        - WhatsAppBusinessAPI: Meta Graph API 客户端
        - WhatsAppAgent: 高级对话封装
      trigger: _handleP0Module._P0WhatsApp
      capabilities:
        - whatsapp_business_api
      metrics:
        delivery_rate: "> 99%"
        open_rate: "> 98%"

    multilingual_translator:
      file: cloudbase/modules/multilingual-translator.js
      parent_file: cloudbase/agent.js
      classes:
        - MultilingualTranslator: 核心翻译引擎
        - MultilingualConversationHelper: 多语言对话助手
      trigger: _handleP0Module._P0Translator
      capabilities:
        - multilingual_translation
      metrics:
        language_count: 134
        accuracy: "> 95%"

    ai_customer_service:
      file: cloudbase/modules/ai-customer-service.js
      parent_file: cloudbase/agent.js
      classes:
        - AICustomerService: 核心客服引擎
        - IntentRecognizer: 意图识别器
        - SentimentAnalyzer: 情感分析器
        - KnowledgeBaseRetriever: 知识库检索器
      trigger: _handleP0Module._P0AICustomerService
      capabilities:
        - ai_customer_service
      metrics:
        automation_rate: "> 80%"
        intent_accuracy: "> 90%"

  # ─── 主入口 ───
  main:
    file: cloudbase/agent.js
    class: ForeignTradeArmy
    export: exports.main


# ============================================================================
# 对比说明：v1.0 vs v2.0
# ============================================================================

upgrade_notes:
  v2_0_new_features:
    - name: Atlas Reasoning Engine
      source: Salesforce Agentforce Atlas
      benefit: 复杂任务自动多步骤规划，失败自动重试与降级
    - name: MAS 多智能体协同
      source: Marketingforce MAS体系
      benefit: 三大Agent并行协作，效率提升
    - name: Grounding Check
      source: Salesforce Agentforce Grounding Check
      benefit: 防止幻觉，提升响应可信度
    - name: KnowForce 知识中台
      source: Marketingforce KnowForce
      benefit: 企业知识复用，提升专业度
    - name: Agent Script DSL
      source: Salesforce Agent Script
      benefit: 支持声明式逻辑编排，可定制Agent行为
    - name: 监管模式
      source: MAS Supervised Mode
      benefit: 关键操作需人工审批，降低风险
    # ───────────────────────────────────────────────────────────────────────────
    # P0 新增能力（v2.0 P0优先级）
    # ───────────────────────────────────────────────────────────────────────────
    - name: WhatsApp Business API集成
      source: 对标 SaleSmartly
      benefit: Meta官方认证，消息送达率>99%，支持98%开放率
    - name: 134语言实时翻译
      source: 对标 SaleSmartly
      benefit: 外贸专业术语库，翻译记忆库，批量翻译
    - name: AI客服模块
      source: 对标 Instadesk
      benefit: 80%自动化率，意图识别>90%，情感分析自动升级
