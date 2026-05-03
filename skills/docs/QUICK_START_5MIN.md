# OpenClaw Enterprise 5分钟快速上手

> 让你在 5 分钟内跑通第一个 Agent，感受多 Agent 协作的强大。

---

## ⏱️ 时间分配

| 步骤 | 内容 | 预计时间 |
|------|------|----------|
| 1 | 安装依赖 | 1 分钟 |
| 2 | 配置 API Key | 1 分钟 |
| 3 | 运行第一个 Agent | 3 分钟 |

---

## 1️⃣ 安装（1分钟）

### 方式一：从技能包安装（推荐）

```bash
clawhub install WangM-A3/openclaw-enterprise-skill
```

### 方式二：从源码安装

```bash
cd projects/openclaw-enterprise
pip install -r requirements.txt
```

**需要的环境：**
- Python 3.8+
- pip
- curl（用于健康检查）

---

## 2️⃣ 配置（1分钟）

### 复制环境变量模板

```bash
cp .env.example .env
```

### 编辑 `.env`，填入你的密钥

```bash
# 必需
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 可选（使用外部数据库时）
DATABASE_URL=postgresql://user:pass@localhost/openclaw
```

> 💡 如果还没有 API Key，前往 [platform.openai.com](https://platform.openai.com) 申请。

---

## 3️⃣ 运行第一个 Agent（3分钟）

创建一个文件 `first_agent.py`：

```python
import asyncio
from langchain_openai import ChatOpenAI
from src.chief import ChiefAgent
from src.chief.state import AgentType

async def main():
    # Step 1: 初始化 LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    # Step 2: 初始化幕僚长（所有任务的统一入口）
    chief = ChiefAgent(llm=llm)

    # Step 3: 注册一个自定义执行 Agent
    async def hello_agent(task, context):
        """打招呼 Agent"""
        return {
            "message": f"你好！我是 {task['description']}，任务已完成！",
            "status": "done"
        }

    chief.register_agent(AgentType.GENERAL_ASSISTANT, hello_agent)

    # Step 4: 让幕僚长调度执行任务
    result = await chief.execute(
        query="帮我打个招呼，介绍自己是助手",
        user_id="quickstart_user"
    )

    # Step 5: 查看结果
    print("=" * 50)
    print("🎉 执行完成！")
    print("=" * 50)
    print(f"✅ 成功: {result['success']}")
    print(f"📋 子任务: {result['tasks']['completed']}/{result['tasks']['total']} 完成")
    print(f"⭐ 质量评分: {result['quality_score']}")
    print(f"⏱️  执行耗时: {result['execution_time']:.2f}秒")
    print(f"\n📝 响应内容:\n{result['response']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行

```bash
python first_agent.py
```

**期望输出：**

```
==================================================
🎉 执行完成！
==================================================
✅ 成功: True
📋 子任务: 1/1 完成
⭐ 质量评分: 0.95
⏱️  执行耗时: 1.23秒

📝 响应内容:
你好！我是 助手，任务已完成！
```

---

## 🔧 多 Agent 协作示例

幕僚长的核心能力：**一个请求 → 自动拆解 → 并行调度多个专业 Agent**

```python
import asyncio
from langchain_openai import ChatOpenAI
from src.chief import ChiefAgent
from src.chief.state import AgentType

async def main():
    llm = ChatOpenAI(model="gpt-4o")
    chief = ChiefAgent(llm=llm, config={"max_concurrent": 3})

    # 注册内容创作 Agent
    async def content_writer(task, context):
        await asyncio.sleep(0.5)  # 模拟处理
        return {"article": f"关于「{task['description']}」的文章已完成", "words": 1200}

    # 注册数据分析 Agent
    async def data_analyst(task, context):
        await asyncio.sleep(0.8)
        return {"insights": ["洞察1：增长显著", "洞察2：转化率提升"]}

    chief.register_agent(AgentType.CONTENT_WRITER, content_writer)
    chief.register_agent(AgentType.DATA_ANALYST, data_analyst)

    # 复杂任务：一个请求触发多个 Agent 并行工作
    result = await chief.execute(
        query="帮我写一篇关于AI行业趋势的文章，同时分析相关数据",
        user_id="user_001",
        context={"industry": "AI", "deadline": "2026-04-15"}
    )

    print(f"成功: {result['success']}, "
          f"质量: {result['quality_score']}, "
          f"耗时: {result['execution_time']:.1f}秒")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧠幕僚长做了什么？

```
你: "帮我写文章 + 分析数据"
         │
         ▼
┌─────────────────────────┐
│      幕僚长 Agent        │
│  - 理解用户意图          │
│  - 拆解为子任务          │
│  - 选择合适的执行 Agent  │
└────────┬────────────────┘
         │ 并行调度
    ┌────┴────┐
    ▼         ▼
ContentWriter  DataAnalyst
  (写文章)     (分析数据)
    │         │
    └────┬────┘
         ▼
┌─────────────────────────┐
│      结果整合            │
│  - 汇总各 Agent 产出     │
│  - 质量评分             │
│  - 返回统一响应          │
└─────────────────────────┘
```

---

## 下一步

- 📖 **[完整文档](docs/)** — 深入了解所有 Agent 能力
- 🧑‍💻 **[Chief Agent 指南](docs/chief_agent_readme.md)** — 幕僚长完整 API
- 🚀 **[幕僚长快速启动](docs/QUICKSTART.md)** — 详细示例（10分钟版）
- ⚙️ **[部署指南](DEPLOYMENT.md)** — 生产环境部署
- 🔧 **[运维手册](docs/ops_guide.md)** — 监控、日志、告警

---

## 💡 常见问题

**Q: 报 `ModuleNotFoundError`？**
```bash
pip install -r requirements.txt
```

**Q: 报 `OPENAI_API_KEY` 错误？**
```bash
export OPENAI_API_KEY=sk-your-key
```

**Q: 想换模型？**
```python
llm = ChatOpenAI(model="gpt-4o-mini")  # 更便宜
llm = ChatOpenAI(model="gpt-4")        # 效果更好
```
