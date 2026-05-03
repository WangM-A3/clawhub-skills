# OpenClaw Enterprise 快速参考

## Agent 能力速查

| Agent | 触发词 | 典型任务 |
|-------|--------|----------|
| DataAnalyst | 分析、数据、报表 | 销售分析、用户洞察 |
| ContentWriter | 写、撰写、文案 | 文章、邮件、报告 |
| Researcher | 调研、搜索、查 | 市场调研、竞品分析 |
| Developer | 开发、编码、实现 | 功能开发、Bug修复 |
| Designer | 设计、UI、视觉 | 海报、原型、配色 |
| Planner | 计划、规划、安排 | 项目排期、旅行计划 |
| Troubleshooter | 问题、排查、故障 | 系统诊断、错误分析 |
| Marketer | 营销、推广、增长 | 活动策划、增长方案 |
| Financier | 财务、预算、成本 | 成本分析、预算规划 |
| LegalAdvisor | 合规、法律、风险 | 合同审查、风险评估 |
| HRManager | 招聘、团队、人力 | 岗位描述、培训方案 |
| Operations | 运营、流程、优化 | 流程改进、效率提升 |
| Innovator | 创新、创意、头脑风暴 | 新产品构思、方案设计 |

## API 快速调用

### Python
```python
import requests

# 基础对话
resp = requests.post("http://localhost:8080/chat", json={
    "user_id": "user123",
    "message": "帮我分析Q3销售数据"
})
print(resp.json()["response"])

# 异步任务
resp = requests.post("http://localhost:8080/task", json={
    "user_id": "user123",
    "task_type": "analysis",
    "parameters": {"data_source": "sales_q3.csv"}
})
task_id = resp.json()["task_id"]

# 查询结果
resp = requests.get(f"http://localhost:8080/task/{task_id}")
print(resp.json())
```

### cURL
```bash
# 对话
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","message":"分析销售数据"}'

# 查看Agent列表
curl http://localhost:8080/agents

# 查询消耗
curl http://localhost:8080/costs?user_id=user123
```

## 配置模板

### agents.yaml
```yaml
chief_of_staff:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4000
  system_prompt: |
    你是幕僚长，负责理解用户需求并调度合适的执行Agent。

executors:
  data_analyst:
    model: "gpt-3.5-turbo"
    temperature: 0.3
    tools: ["pandas", "matplotlib"]
  
  content_writer:
    model: "gpt-4"
    temperature: 0.8
```

### memory.yaml
```yaml
short_term:
  type: "buffer"
  max_tokens: 2000

long_term:
  type: "vector"
  backend: "pinecone"
  index: "openclaw-memories"
```

## 错误码

| 码 | 含义 | 处理建议 |
|----|------|----------|
| 400 | 请求格式错误 | 检查JSON格式 |
| 401 | 认证失败 | 检查API Key |
| 429 | 请求过快 | 降低调用频率 |
| 500 | 服务内部错误 | 查看日志排查 |
| 503 | 服务不可用 | 等待后重试 |

## 监控指标

```bash
# 健康检查
curl http://localhost:8080/health

# Prometheus 指标
curl http://localhost:8080/metrics
```

关键指标:
- `openclaw_requests_total` - 总请求数
- `openclaw_tokens_used` - Token消耗
- `openclaw_latency_seconds` - 响应延迟
- `openclaw_agents_active` - 活跃Agent数
