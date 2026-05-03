# ClawScan Suspicious 状态排查报告

**报告日期**：2026-05-06
**排查技能**：openclaw-enterprise、industrial-silicon-army、geo-agentops

---

## 一、ClawScan 检测机制说明

### 1.1 双层检测架构

ClawHub 采用 **VirusTotal + Code Insight** 双层安全扫描体系：

| 检测层 | 来源 | 判定结果 | 当前状态 |
|--------|------|----------|----------|
| **静态扫描** | VirusTotal 全球威胁情报库 | Benign | ✅ 3个技能均通过 |
| **行为分析** | OpenClaw LLM Code Insight | Suspicious | ❌ 3个技能均触发 |

### 1.2 ClawScan Suspicious 触发机制

根据 GitHub Issue #1645 的官方回复，**Suspicious 标记来自 ClawHub LLM Review**，而非恶意软件检测。LLM 会分析技能的以下维度：

| 检测维度 | 风险指标 |
|----------|----------|
| **权限范围** | 是否声明明确的存储根路径 |
| **删除操作** | 是否有删除前的确认机制 |
| **文件访问** | 是否限定在特定目录内操作 |
| **数据处理** | 如何选择和处理"相关"文件 |
| **隐私声明** | 是否有数据保留/隐私行为文档 |
| **外部依赖** | 是否有可信的第三方来源声明 |

### 1.3 Suspicious vs Benign 的本质区别

```
Benign = 代码本身无恶意 + 行为描述清晰 + 权限边界明确
Suspicious = 代码无恶意 + 但 LLM 对行为边界存在疑虑
```

---

## 二、3个技能疑似触发点分析

### 2.1 openclaw-enterprise

| 疑似触发点 | 严重程度 | 具体位置 | 问题描述 |
|------------|----------|----------|----------|
| **多API密钥组合** | 中 | clawhub.yaml | 同时请求 OPENAI_API_KEY + ANTHROPIC_API_KEY + OPENCLAW_API_KEY |
| **敏感系统集成** | 中 | SKILL.md L277-283 | 声称支持 ERP/MES/WMS/CRM 深度集成 |
| **多Agent并发执行** | 低 | scripts/chief_of_staff.py | asyncio.gather 并发调度多个Agent |
| **权限边界未声明** | 中 | SKILL.md | 未明确说明幕僚长可访问哪些数据目录 |
| **自动调度能力** | 低 | SKILL.md L60-67 | 任务自动路由机制可能被误读为"自动执行高危操作" |

**修复建议**：
```yaml
# 在 clawhub.yaml 中增加安全声明
security:
  data_scope: "仅处理用户明确授权的业务数据"
  storage_root: "~/.openclaw/enterprise/"
  delete_confirmation: true
  permissions:
    - "read: 用户指定的企业数据"
    - "write: 技能私有目录"
    - "no_system_access: 不访问系统关键路径"
```

### 2.2 industrial-silicon-army

| 疑似触发点 | 严重程度 | 具体位置 | 问题描述 |
|------------|----------|----------|----------|
| **第三方平台集成** | 中 | clawhub.yaml L33-34 | 集成 1688 API（阿里巴巴采购平台） |
| **行业敏感数据** | 中 | SKILL.md | 涉及供应商评级、客户信用、税务数据 |
| **外部数据源引用** | 低 | industrial_agents.py L73-78 | 包含供应商具体名称和价格数据 |
| **多API密钥请求** | 低 | clawhub.yaml L19-22 | OPENAI_API_KEY + LOOKINGPLAS_API_KEY |
| **自动采购建议** | 中 | SKILL.md | 提供"采购建议"可能被解读为"自动下单" |

**修复建议**：
```yaml
# 在 clawhub.yaml 中增加数据处理声明
data_handling:
  storage_scope: "仅用于本地报价计算，不存储外部敏感信息"
  retention_policy: "会话结束自动清除"
  third_party_data: "仅用于数据聚合，不缓存原始凭证"
  automation_level: "仅提供建议，人工确认后执行"
```

### 2.3 geo-agentops

| 疑似触发点 | 严重程度 | 具体位置 | 问题描述 |
|------------|----------|----------|----------|
| **社交媒体API** | 高 | clawhub.yaml L27-32 | LinkedIn + Twitter/X API 集成 |
| **多平台发布能力** | 中 | SKILL.md L129-132 | "一键发布到 LinkedIn、Twitter/X、Reddit" |
| **AI引用追踪** | 中 | SKILL.md L131 | 监控 ChatGPT/Claude/Gemini/Perplexity 引用 |
| **竞品分析功能** | 低 | SKILL.md L132 | 声称可追踪竞争对手在AI搜索中的表现 |
| **Perplexity API** | 低 | clawhub.yaml L24-26 | 实时AI搜索数据获取 |

**修复建议**：
```yaml
# 在 clawhub.yaml 中增加平台授权声明
platform_authorization:
  linkedin: "需用户自行OAuth授权，仅发布用户内容"
  twitter: "需用户自行OAuth授权，仅发布用户内容"
  perplexity: "仅用于公开数据聚合，不访问私密对话"
  
# 增加使用边界说明
usage_constraints:
  - "所有社交媒体操作需用户显式确认"
  - "不自动关注/添加陌生用户"
  - "不批量发送私信"
  - "引用追踪仅监控公开可见内容"
```

---

## 三、通用修复建议

### 3.1 SKILL.md 文档增强

在 SKILL.md 末尾添加 **"Security & Privacy"** 章节：

```markdown
## Security & Privacy

### 数据处理原则
- ✅ 技能仅处理用户明确授权的数据
- ✅ 所有外部操作需用户确认后执行
- ✅ 不访问系统关键目录（/etc, /root, ~/.ssh 等）
- ✅ 敏感操作（删除、修改）默认禁用，需显式开启

### 存储范围
- **存储根目录**：`~/.openclaw/skills/{skill-name}/`
- **数据保留**：会话结束后自动清除
- **日志策略**：仅保留执行摘要，不保留原始输入

### 第三方服务
| 服务 | 用途 | 数据传输 |
|------|------|----------|
| OpenAI API | LLM调用 | 仅发送脱敏后的业务指令 |
| Anthropic API | 内容生成 | 仅发送脱敏后的业务指令 |
| 其他API | 数据聚合 | 不缓存原始凭证 |
```

### 3.2 clawhub.yaml 增强

添加 `security` 和 `permissions` 声明：

```yaml
# 安全配置
security:
  # 数据处理边界
  read_scope:
    - "~/.openclaw/skills/{skill-name}/data/"
    - "用户明确指定的业务数据"
  write_scope:
    - "~/.openclaw/skills/{skill-name}/output/"
  no_access:
    - "~/.ssh/"
    - "/etc/"
    - "~/.aws/"
  
  # 操作保护
  require_confirmation:
    - delete_files
    - external_api_calls
    - social_media_posts
  
  # 隐私声明
  privacy:
    no_telemetry: true
    no_analytics: true
    data_retention: "session_only"
```

### 3.3 Python 脚本安全加固

在脚本中添加路径验证：

```python
import os
from pathlib import Path

# 定义安全边界
ALLOWED_ROOTS = [
    os.path.expanduser("~/.openclaw/skills/{skill-name}/"),
    os.getcwd()
]

def safe_path(path: str) -> bool:
    """验证路径在允许范围内"""
    try:
        resolved = Path(path).resolve()
        return any(str(resolved).startswith(root) for root in ALLOWED_ROOTS)
    except:
        return False
```

---

## 四、申诉流程

### 4.1 官方申诉路径

1. **GitHub Issue**：在 [openclaw/clawhub](https://github.com/openclaw/clawhub/issues) 创建新 Issue
2. **模板内容**：
   ```markdown
   ## Skill Information
   - Skill Name: {skill-name}
   - Version: {version}
   - GitHub Issue Link: {本Issue链接}
   
   ## Security Scan Status
   - VirusTotal: Benign ✅
   - ClawScan OpenClaw: Suspicious ❌
   
   ## Clarification
   [请详细说明技能的实际用途、权限边界、数据处理方式]
   
   ## Mitigation Steps Taken
   - [ ] 已在 SKILL.md 添加 Security & Privacy 章节
   - [ ] 已在 clawhub.yaml 添加 security 配置
   - [ ] 已限制文件访问范围
   - [ ] 已添加删除确认机制
   - [ ] 其他措施...
   ```

### 4.2 申诉注意事项

| 注意事项 | 说明 |
|----------|------|
| **提供 VirusTotal 链接** | 证明代码本身无恶意 |
| **详细说明业务场景** | 让 LLM 理解技能的真实用途 |
| **强调用户控制权** | 突出"人工确认"、"用户显式授权" |
| **提供修复证据** | 展示已添加的安全声明 |
| **引用官方文档** | 如 GitHub Issue #1645 的修复建议 |

---

## 五、总结

### 5.1 根因分析

| 技能 | 主要触发原因 | 修复优先级 |
|------|-------------|------------|
| openclaw-enterprise | 多API密钥 + 自动化调度 + 权限边界模糊 | 高 |
| industrial-silicon-army | 第三方平台集成 + 敏感数据处理 + 采购建议 | 高 |
| geo-agentops | 社交媒体API + 多平台发布 + 引用追踪 | 高 |

### 5.2 行动计划

| 步骤 | 行动项 | 负责 |
|------|--------|------|
| 1 | 在 SKILL.md 末尾添加 Security & Privacy 章节 | 技能开发者 |
| 2 | 在 clawhub.yaml 添加 security 配置块 | 技能开发者 |
| 3 | 更新 Python 脚本添加路径验证 | 技能开发者 |
| 4 | 在 GitHub 创建申诉 Issue | 技能开发者 |
| 5 | 等待 ClawHub 团队重新审查 | ClawHub 团队 |

### 5.3 参考资料

- GitHub Issue: [my skill got flagged when its safe #1645](https://github.com/openclaw/clawhub/issues/1645)
- ClawHub 官方文档：安全扫描机制
- OpenClaw 官方博客：与 VirusTotal 的安全合作

---

**报告完成时间**：2026-05-06
**排查人员**：ClawScan Analysis Agent
