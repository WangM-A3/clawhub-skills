---
name: datacrawl-debug
description: >-
  Use when user needs to crawl web data, debug scraping code, clean crawled data, or iterate on scraping strategies.
  Use when generating web scraping code from URL and field descriptions.
  Use when diagnosing crawling errors like 403, timeout, selector failures, encoding issues.
  Use when cleaning, deduplicating, normalizing, and formatting scraped data.
  Use when optimizing crawl strategies based on run history analysis.
  Use when user mentions "数据抓取", "爬虫", "爬虫调试", "数据清洗", "抓取代码", "反爬", "scraping", "crawling", "data extraction", "debug crawler".
homepage: https://yunlvai.com
license: MIT-0
version: 1.0.0
progressive:
  layers:
    - name: metadata
      tokens: 200
      loaded: startup
      description: "技能基础配置、5大核心模块、适用场景"
    - name: instructions
      tokens: 4500
      loaded: trigger
      description: "数据抓取全流程：配置生成→代码生成→调试修复→数据清洗→迭代优化"
    - name: resources
      tokens: variable
      loaded: on-demand
      description: "错误模式库、代码模板、清洗规则、评分算法"
  resource_paths:
    - references/crawl_best_practices.md
    - references/anti_detection_guide.md
    - references/data_quality_checklist.md
metadata:
  datacrawl:
    core_modules:
      - CrawlEngine: "抓取配置生成+HTML解析器"
      - CodeGenerator: "3模式代码自动生成(requests_bs4/playwright/api_client)"
      - DebugRunner: "8类错误模式库+诊断+修复建议"
      - DataCleaner: "文本清洗+类型标准化+多格式输出"
      - IterateOptimizer: "运行历史分析+配置自动改进"
    enemy: "反爬封杀和数据混乱"
    memory_hook: "抓得到·修得好·洗得净·跑得稳"
---

# DataCrawl Debug — 数据抓取全流程工具

> 抓得到·修得好·洗得净·跑得稳

## 核心定位

数据抓取的"急诊室+健身房"——出了问题来急诊（DebugRunner），日常训练来健身（IterateOptimizer），全程配营养师（DataCleaner）。

## 5大核心模块

### 1. CrawlEngine — 抓取配置生成 + 结果解析
```
scripts/crawl-engine.py config --url URL --fields 字段1 字段2 --mode static|dynamic|api
scripts/crawl-engine.py extract --html "HTML内容" --fields 字段1 字段2
```
- 站点类型自动识别（电商/B2B/社媒/内容/政府/开发者）
- 3种模式工具推荐 + CSS/XPath选择器建议
- HTML结构化提取（文本/链接/图片/表格/列表）

### 2. CodeGenerator — 抓取代码自动生成
```
scripts/code-generator.py --name 项目名 --url URL --fields 字段1 字段2 --mode requests_bs4|playwright|api_client
```
- 3种模板自动选择：静态页面/动态渲染/API接口
- 生成完整可运行代码 + 依赖安装 + 使用步骤

### 3. DebugRunner — 代码调试与修复
```
scripts/debug-runner.py --error "错误信息"
```
- 8类错误模式库：connection/http_error/timeout/selector_error/encoding/json_parse/selenium_playwright/rate_limit
- HTTP子类型精准诊断（403反爬/429限流/503服务不可用等各有方案）
- 代码片段扫描（缺异常处理/超时/延迟/UA自动检测）

### 4. DataCleaner — 数据清洗格式化
```
scripts/data-cleaner.py clean --input 数据 --remove-html --remove-duplicates
scripts/data-cleaner.py normalize --input 数据 --schema 类型定义
scripts/data-cleaner.py format --input 数据 --format json|csv|jsonl --fields 字段列表
```

### 5. IterateOptimizer — 自我迭代优化
```
scripts/iterate-optimizer.py analyze --input 运行历史.json
scripts/iterate-optimizer.py improve --config 当前配置 --analysis 分析结果
```
- 成功率趋势 / 错误聚类 / 字段覆盖率 / 优化建议
- 自动调整延迟/超时/重试/模式切换

## 实战案例：小红书外贸博主抓取

内置 `scripts/xhs-foreign-trade-processor.py`：
- 5维粉丝质量评分（互动率/收藏比/评论活跃/粉丝规模/外贸相关度）
- S/A/B/C/D 5级分层
- 粉丝画像推断（工厂主/跨境卖家/SOHO/公司经营者/新手）
- Playwright执行配置生成
- 批量数据处理（去重+外贸筛选+评分+画像）

### 常见脚本问题诊断
原脚本用requests直连API → 必403。正确方案：
1. 用Playwright打开小红书网页版
2. 手动登录后保存Cookie
3. 通过搜索页面而非API提取数据
4. 用本技能的评分模型替代简单加权

## 使用流程

1. **配置**: `crawl-engine.py config` → 了解目标站点+推荐方案
2. **生成代码**: `code-generator.py` → 获得起始代码模板
3. **调试**: 遇错 → `debug-runner.py` → 秒级诊断
4. **清洗**: `data-cleaner.py` → 去重+标准化+格式化
5. **迭代**: `iterate-optimizer.py` → 基于运行数据持续改进
