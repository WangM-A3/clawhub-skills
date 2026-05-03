# 外贸硅基军团 🌏

> 外贸出海AI Agent军团 — 建站 × 流量 × 转化，全自动闭环
> Powered by **Salesforce Agentforce Atlas 推理引擎**，多智能体协同(MAS)架构

[![Version](https://img.shields.io/badge/version-2.5.0-green.svg)](package.json)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-8%2B-orange.svg)](#)
[![GEO](https://img.shields.io/badge/GEO-Optimized-purple.svg)](#)

---

## 💡 一句话价值主张

**外贸出海，从建站到获客，一个Agent军团全搞定。** AI自动建站、GEO优化抢滩AI答案页、多渠道精准获客（WhatsApp/LinkedIn/Email），询盘成本从$1.20→$0.04。

---

## ⚡ 效果数据

| 指标 | 数据 |
|------|------|
| 询盘成本 | **$0.04**（vs Google Ads $1.20）|
| 询盘增长 | **+127%** |
| 月均AI渠道询盘 | **580条** |
| 建站周期 | **从数周→数小时** |
| 内容发布 | 多平台同步，一键完成 |
| 见效周期 | 1-2个月 |

---

## 🎯 三大Agent模块

```
┌──────────────────────────────────────────────────────┐
│              外贸硅基军团 v2.5.0                      │
├──────────────┬─────────────────┬────────────────────┤
│  🏗️ 建站Agent │  📢 流量Agent    │  💰 转化Agent       │
│              │                 │                    │
│ · WordPress  │ · GEO内容生成    │ · WhatsApp获客     │
│ · Shopify    │ · 多平台分发     │ · Email营销        │
│ · 页面SEO    │ · AI引用监测     │ · LinkedIn触达     │
│ · 移动适配   │ · 竞品分析       │ · 询盘管理         │
└──────────────┴─────────────────┴────────────────────┘
```

### 🏗️ 建站Agent（2个）
| Agent | 职能 | 核心能力 |
|-------|------|---------|
| 🌐 WordPress建站Agent | 独立站搭建/优化 | 主题选型、页面SEO、性能优化 |
| 🛍️ Shopify建站Agent | 电商独立站 | 商品同步、支付配置、物流对接 |

### 📢 流量Agent（4个）
| Agent | 职能 | 核心能力 |
|-------|------|---------|
| 📡 Topic Planner | 每周选题库 | 行业热点、关键词挖掘、内容日历 |
| 🔥 Headline Generator | 爆款标题生成 | 10个高点击率标题，A/B测试支持 |
| 📝 GEO Article | GEO文章生成 | 1200词完整文章，AI引用优化 |
| ❓ FAQ Generator | FAQ内容生成 | 8组AI可引用Q&A，Schema标记 |

### 💰 转化Agent（4个）
| Agent | 职能 | 核心能力 |
|-------|------|---------|
| 💬 WhatsApp获客Agent | WhatsApp触达 | 虚拟号管理、自动回复、目录推送 |
| 📧 Email营销Agent | 邮件自动化 | 模板定制、发送优化、打开率追踪 |
| 💼 LinkedIn触达Agent | B2B社媒获客 | 精准拓客、互动自动化 |
| 📊 询盘管理Agent | 询盘全流程 | 自动分配、跟进提醒、数据分析 |

---

## 🔧 技术架构

- **推理引擎**: Salesforce Agentforce Atlas（场景耦合模式）
- **多Agent架构**: MAS (Multi-Agent System)，并行协作
- **内容引擎**: GEO优化，覆盖 DeepSeek/Kimi/ChatGPT/Claude/Gemini/Perplexity
- **CMS集成**: WordPress REST API + Shopify Admin API
- **消息中枢**: WhatsApp Business API（Meta Graph API）
- **部署**: Docker Compose，30分钟启动

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Docker & Docker Compose
- WordPress站点（可选）/ Shopify店铺（可选）

### 安装
```bash
git clone https://github.com/silicon-army/foreign-trade-silicon-army.git
cd foreign-trade-silicon-army
pip install -r requirements.txt
docker compose up -d
```

### 配置
设置环境变量（参考 `.env.example`）:
```bash
WORDPRESS_SITE_URL=https://your-domain.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
OPENAI_API_KEY=sk-xxxx
DEEPSEEK_API_KEY=sk-xxxx
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_ACCESS_TOKEN=your_token
```

### 第一个任务
```python
from silicon_army import AgentArmy

army = AgentArmy(
    wordpress_url="https://your-domain.com",
    deepseek_api_key="sk-xxxx"
)

# 让Agent自动完成建站+GEO+获客
result = army.execute("""
    帮我创建一个关于工业阀门产品的外贸独立站，
    包含5个GEO优化的产品页面，
    并生成第一批LinkedIn推广内容
""")
```

---

## 🆚 竞品对比

| 能力 | 外贸硅基军团 | 传统建站公司 | 单一AI工具 |
|------|------------|-----------|-----------|
| 建站 | AI自动，小时级 | 数周，人工 | 仅文案 |
| GEO优化 | 6大AI平台全覆盖 | 无 | 仅Google SEO |
| 多渠道获客 | WhatsApp+Email+LinkedIn | 无 | 仅邮件 |
| 多Agent协作 | ✅ MAS架构，并行执行 | ❌ 单点 | ❌ 单一助手 |
| 实施成本 | **$199/月起** | $5,000-50,000 | $20-100/月 |
| 询盘成本 | **$0.04/条** | $0.80-2.00/条 | $0.50-1.00/条 |

---

## 💰 定价方案

| 方案 | 价格 | 核心权益 |
|------|------|---------|
| 🥉 Starter | $199/月 | 建站Agent + 2个流量Agent |
| 🥇 Professional | $499/月 | 全部8个Agent + WhatsApp获客 |
| 🏢 Enterprise | $999/月 | 全功能 + 私有部署 + 定制开发 |

---

## 📦 目录结构

```
foreign-trade-silicon-army/
├── agents/                    # 8个专业Agent实现
│   ├── builder/              # 建站Agent
│   ├── traffic/              # 流量Agent
│   └── conversion/           # 转化Agent
├── atlas/                    # Atlas推理引擎
├── cms/                      # WordPress/Shopify连接器
├── geo/                      # GEO优化模块
├── whatsapp/                 # WhatsApp集成
├── api_server.py             # FastAPI服务
├── requirements.txt
└── docker-compose.yml
```

---

## 📖 更多资源

- 📘 [SKILL.md](SKILL.md) — 完整技能文档
- 🐙 [GitHub](https://github.com/silicon-army/foreign-trade-silicon-army) — 源码
- 📧 [support@silicon-army.dev](mailto:support@silicon-army.dev)

---

*© 2024 Silicon Army Team. Apache 2.0 Licensed.*
