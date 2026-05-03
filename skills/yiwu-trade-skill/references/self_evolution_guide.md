# 义乌.Skill 自进化机制集成指南

> 本指南基于 [self-improving-agent](https://github.com/peterskoett/self-improving-agent) 设计理念，针对义乌外贸场景定制

---

## 一、机制概述

### 什么是自进化机制？
自进化机制是义乌.Skill的持续学习与优化系统，通过记录、分类、晋升三个核心流程，实现技能的自我迭代与升级。

### 核心价值
- **错误不重犯**：同类错误记录在案，形成预防机制
- **经验可传承**：最佳实践从个人经验变为可复制方法论
- **需求驱动进化**：用户需求直接推动功能迭代

### 自进化闭环
```
用户反馈 → 记录学习 → 分类归档 → 高频晋升 → SKILL升级
    ↑                                                        ↓
    └──────────────── 持续优化 ←─────────────────────────────┘
```

---

## 二、文件结构

```
./skills/yiwu-trade-skill/
└── .learnings/                    # 自进化核心目录
    ├── LEARNINGS.md              # 学习记录（洞察/纠正/最佳实践）
    ├── ERRORS.md                 # 错误记录（失败/异常/风险）
    └── FEATURE_REQUESTS.md       # 需求记录（功能/内容/集成）
```

---

## 三、学习记录规范

### 何时记录学习？

| 场景 | 触发条件 | 记录位置 | 分类标签 |
|------|----------|----------|----------|
| 用户纠正 | "不对，应该是..."、"实际上..." | LEARNINGS.md | `correction` |
| 更优方案发现 | 找到更高效的流程或方法 | LEARNINGS.md | `best_practice` |
| 行业洞察 | 汇率变化、政策更新、市场趋势 | LEARNINGS.md | `insight` |
| 知识盲区 | 发现自己不了解的内容 | LEARNINGS.md | `knowledge_gap` |
| 操作失败 | 命令/流程/工具执行失败 | ERRORS.md | - |
| 支付/物流异常 | 诈骗/延误/破损/清关失败 | ERRORS.md | - |
| 用户建议 | "能不能加个..."、"建议增加..." | FEATURE_REQUESTS.md | - |

### 记录格式要求

#### LEARNINGS.md 条目模板
```markdown
### [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601时间戳
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: sourcing | logistics | payment | compliance | sales | finance

### Summary
一行描述：学到了什么

### Details
完整上下文：
- 发生了什么
- 之前怎么做的
- 正确做法是什么

### Suggested Action
具体改进建议

### Metadata
- Source: conversation | error | user_feedback
- Related Files: 相关文件路径
- Tags: 标签1, 标签2
- See Also: 关联条目（如有）
```

#### ERRORS.md 条目模板
```markdown
### [ERR-YYYYMMDD-XXX] error_type

**Logged**: ISO-8601时间戳
**Priority**: high
**Status**: pending | resolved | blocked
**Area**: customs | logistics | payment | compliance

### Summary
错误概述

### Details
**错误场景**：
- 具体描述

**根因分析**：
- 为什么会发生

### Correct Approach
正确做法

### Suggested Action
预防措施

### Metadata
- Source: error
- Related Files: 相关文件
- Resolution: 处理结果
```

---

## 四、学习晋升机制

### 晋升标准

当同一领域的学习记录达到以下条件时，启动晋升流程：

| 条件 | 晋升目标 | 操作 |
|------|----------|------|
| 同领域3次+通用性高 | 完善SOP | 更新对应模块文档 |
| 同领域5次+实践验证 | 独立文档 | 创建新参考指南 |
| 高优先级×5次 | 紧急迭代 | 版本升级优先处理 |

### 晋升流程

```
1. 发现高频学习条目（同一 Pattern-Key 出现3次+）
   ↓
2. 评估通用性和实践价值
   ↓
3. 制定晋升方案（合并/扩展/新建文档）
   ↓
4. 更新 SKILL.md 或新建 reference 文档
   ↓
5. 标记原条目状态为 "promoted"
   ↓
6. 记录晋升日志（LEARNINGS.md 底部表格）
```

### 晋升决策树

```
学习条目出现
    │
    ├── 是否高频？（同一 Pattern-Key ≥3次）
    │   │
    │   ├── YES → 是否通用性强？
    │   │   │
    │   │   ├── YES → 晋升到 SKILL.md 或 reference
    │   │   │
    │   │   └── NO → 保留在 .learnings
    │   │
    │   └── NO → 评估单次价值
    │       │
    │       ├── 价值高 → 保留，标记关注
    │       └── 价值低 → 保留供参考
    │
    └── 是否高优先级（critical/high）？
        │
        └── YES → 优先处理，48小时内评估
```

---

## 五、版本升级机制

### 升级触发条件

| 触发条件 | 升级优先级 |
|----------|------------|
| 重大功能新增（工具/模块） | P0 → 主版本升级 |
| 核心流程优化（影响>50%用户） | P1 → 次版本升级 |
| 内容补充（知识库扩展） | P2 → 补丁版本 |
| Bug修复（错误记录修复） | P3 → 热修复 |

### 版本号规范
- 主版本：重大架构变更或功能新增
- 次版本：流程优化、内容扩展
- 补丁：勘误、小幅优化

### 升级记录格式
```markdown
## 版本历史

| 版本 | 日期 | 更新内容 | 触发来源 |
|------|------|----------|----------|
| 2.3.0 | YYYY-MM-DD | 自进化机制集成 | .learnings 晋升 |
| 2.2.0 | 2026-04-26 | 竞品Copy升级... | 用户需求 |
```

---

## 六、集成检查清单

### 首次使用初始化
- [ ] `.learnings/` 目录已创建
- [ ] `LEARNINGS.md` 已初始化（含模板）
- [ ] `ERRORS.md` 已初始化（含模板）
- [ ] `FEATURE_REQUESTS.md` 已初始化（含模板）
- [ ] SKILL.md 已添加自进化机制引用

### 日常使用规范
- [ ] 遇到错误时立即记录到 ERRORS.md
- [ ] 用户纠正时记录到 LEARNINGS.md（correction）
- [ ] 发现最佳实践时记录到 LEARNINGS.md（best_practice）
- [ ] 用户建议功能时记录到 FEATURE_REQUESTS.md
- [ ] 定期回顾学习记录（建议每周）

### 定期维护
- [ ] 月度：回顾高频模式，评估晋升需求
- [ ] 季度：版本升级评估，更新SKILL.md
- [ ] 年度：全面复盘，优化自进化流程

---

## 七、常见问题

### Q: 什么时候应该记录？
A: 保守原则——宁可多记，不要遗漏。即使不确定是否有价值，也可以先记录，后续再评估。

### Q: 什么样的条目值得晋升？
A: 满足以下条件之一：
- 同一 Pattern-Key 出现 3 次以上
- 能显著提升效率或降低风险
- 具有跨场景通用性

### Q: 记录时要注意什么？
A:
- 不记录敏感信息（密码、密钥、客户隐私）
- 保持简洁，用结构化格式
- 包含足够的上下文以便后续理解

### Q: 如果记录冲突怎么办？
A: 同一问题有不同观点时，保留多个视角，标记为 "debate"，后续通过实践验证。

---

## 八、参考资源

- **self-improving-agent**: https://github.com/peterskoett/self-improving-agent
- **义乌.Skill 核心文档**: `./SKILL.md`
- **合规指南**: `./references/compliance_guide.md`
- **物流指南**: `./references/logistics_guide.md`
- **支付指南**: `./references/payment_guide.md`

---

*本指南随技能版本持续更新，最后更新：v2.3.0*
