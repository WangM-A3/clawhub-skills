# 云旅技能安全扫描排查报告

**生成时间**：2026年4月30日  
**检查技能数量**：8个  

---

## 一、扫描状态汇总表

| 技能Slug | 技能名称 | VirusTotal | ClawScan | Static Analysis | 状态 |
|----------|----------|------------|----------|-----------------|------|
| yunlv-guangjiao | 广交会客户挖掘 | Pending | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-customs-scout | 海关数据智能获客 | Pending | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-linkedin-outreach | LinkedIn开发信生成 | Pending | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-email-writer | 多语言邮件撰写 | Pending | **Benign** ✅ | Benign ✅ | **通过** |
| yunlv-product-desc | 产品差异化描述生成 | Pending | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-price-monitor | 竞品价格监控 | Pending | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-compliance-check | 进出口合规检查 | **Benign** ✅ | Suspicious ⚠️ | Benign ✅ | 需修复 |
| yunlv-contract-draft | 外贸合同智能起草 | **Benign** ✅ | **Benign** ✅ | Benign ✅ | **通过** |

**汇总**：2个技能通过 ✅，6个技能需修复 ⚠️

---

## 二、Suspicious原因分析

### 核心问题：元数据不一致 (Metadata Inconsistency)

ClawScan对6个Suspicious技能的审查发现了一个**共同的核心问题**：

> **注册表顶层元数据显示 `required_env: none` 和 `required_binaries: none`，但 `clawhub.yaml` 和 `SKILL.md` 中明确声明了 `TRADEGPT_API_KEY` 和 `python3/curl` 作为必需项。**

这种内部不一致性让ClawScan怀疑：
1. 注册表元数据可能是过时的
2. 或者技能运行时确实会访问未声明的凭证/端点

### 各技能详细分析

#### 1. yunlv-guangjiao (ClawScan置信度: Medium)
**Suspicious原因**：
- `required_env` 声明不一致
- SKILL.md中包含"信任约束"（如"API密钥不写入日志"、"禁止抓取第三方网站"），但这些无法从仅指令技能中强制执行
- 声明调用外部API (api.yunlvai.com) 和广交会官方数据

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | ⚠️ Concern | 功能合理但元数据不一致 |
| Instruction Scope | 📝 Note | 指令范围符合功能 |
| Install Mechanism | ✅ OK | 仅指令技能，无安装风险 |
| Credentials | ⚠️ Concern | API密钥声明不一致 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

#### 2. yunlv-customs-scout (ClawScan置信度: High)
**Suspicious原因**：
- 注册表元数据显示无需凭证，但clawhub.yaml声明需要 `TRADEGPT_API_KEY`
- 声称调用两个API端点（api.yunlvai.com, data.yunlvai.com），但第二个API的凭证未明确声明
- 涉及自动化触达（邮件/WhatsApp/LinkedIn），存在隐私合规风险

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | ⚠️ Concern | 高置信度：数据源声明不完整 |
| Instruction Scope | 📝 Note | 包含敏感联系数据传输 |
| Install Mechanism | ✅ OK | 仅指令技能 |
| Credentials | ⚠️ Concern | 高置信度：凭证声明不完整 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

#### 3. yunlv-linkedin-outreach (ClawScan置信度: Medium)
**Suspicious原因**：
- 可选声明 `LINKEDIN_SESSION_TOKEN`，但顶层元数据未声明
- "自动发送"功能需要授权，但OAuth流程描述模糊
- LinkedIn session token的使用和存储方式不明确

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | ⚠️ Concern | LinkedIn token声明不一致 |
| Instruction Scope | ⚠️ Concern | OAuth/session token获取和存储流程不清晰 |
| Install Mechanism | ✅ OK | 仅指令技能 |
| Credentials | ⚠️ Concern | LinkedIn token风险高 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

#### 4. yunlv-product-desc (ClawScan置信度: Medium)
**Suspicious原因**：
- 注册表显示无环境变量，但技能文件声明需要 `TRADEGPT_API_KEY`
- python3声明为必需二进制文件，但无安装步骤或代码文件
- 涉及竞品文本处理，需明确数据传输范围

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | 📝 Note | 功能合理但元数据不一致 |
| Instruction Scope | ✅ OK | 指令范围清晰 |
| Install Mechanism | ✅ OK | 仅指令技能 |
| Credentials | ⚠️ Concern | API密钥声明不一致 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

#### 5. yunlv-price-monitor (ClawScan置信度: Medium)
**Suspicious原因**：
- 邮件和WhatsApp预警功能需要凭证，但未声明
- 声明两个API端点，但第二个(data.yunlvai.com)的凭证未明确
- 可能涉及第三方网站爬取，法律合规性需确认

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | 📝 Note | 功能合理但元数据不一致 |
| Instruction Scope | 📝 Note | 预警渠道凭证未声明 |
| Install Mechanism | ✅ OK | 仅指令技能 |
| Credentials | ⚠️ Concern | 多API凭证声明不完整 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

#### 6. yunlv-compliance-check (ClawScan置信度: Medium)
**Suspicious原因**：
- 传输PII和出口管制敏感信息到外部API，隐私风险
- python3/curl声明为必需但无安装步骤
- 制裁名单筛查涉及敏感数据处理

**风险维度**：
| 维度 | 评级 | 说明 |
|------|------|------|
| Purpose & Capability | 📝 Note | 功能合理但元数据不一致 |
| Instruction Scope | 📝 Note | 涉及PII和敏感数据传输 |
| Install Mechanism | ✅ OK | 仅指令技能 |
| Credentials | ⚠️ Concern | API密钥声明不一致 |
| Persistence & Privilege | ✅ OK | 无持久化特权请求 |

---

## 三、对比分析：为什么 yunlv-email-writer 和 yunlv-contract-draft 通过？

| 技能 | ClawScan结果 | 关键差异 |
|------|--------------|----------|
| yunlv-email-writer | **Benign** | 声明`EMAIL_API_KEY`作为额外环境变量；SMTP/Email API标注为"用户自配置" |
| yunlv-contract-draft | **Benign** | 功能单一（合同生成），不涉及自动化触达或外部数据爬取 |
| Suspicious技能 | **Suspicious** | 涉及自动化触达、外部数据爬取、多个API调用 |

**通过的技能特点**：
1. 数据流透明（明确声明用户自配置的服务）
2. 功能边界清晰（不涉及第三方网站爬取）
3. 无复杂的自动化触达流程

---

## 四、修复建议

### 建议1：解决元数据不一致（高优先级）

**问题**：注册表顶层元数据显示 `required_env: none`，与实际技能文件不符。

**解决方案**：在clawhub.yaml中确保以下字段清晰声明：

```yaml
name: yunlv-xxx
required_env:
  - TRADEGPT_API_KEY  # 主API密钥
optional_env:
  - LINKEDIN_SESSION_TOKEN  # 可选凭证（如适用）
required_bins:
  - python3  # 仅在实际需要时声明
  - curl
```

### 建议2：移除或明确化"信任约束"（高优先级）

**问题**：SKILL.md中包含无法强制执行的承诺（如"API密钥不写入日志"）。

**解决方案A - 移除承诺性语句**：
```markdown
# 修改前（有问题）
- API密钥不写入日志（承诺但无法验证）

# 修改后（推荐）
- 数据处理：所有查询条件和中间数据仅在本地处理
- 日志策略：查看 `./data/yunlv-skills/xxx/logs/` 了解日志内容
```

**解决方案B - 明确可验证的行为**：
```markdown
### 数据保护措施
- 敏感凭证通过环境变量传递，不硬编码
- 日志文件位于 `./data/yunlv-skills/xxx/logs/`（用户可自行检查）
- 联系数据导出需用户明确授权
```

### 建议3：明确API调用和数据流（中优先级）

**问题**：多个API端点的凭证声明不完整。

**解决方案**：在clawhub.yaml中完整声明所有API：
```yaml
apis:
  - name: 云旅AI MatchGPT API
    url: https://api.yunlvai.com
    purpose: 数据查询与智能匹配
    auth: Bearer Token (TRADEGPT_API_KEY)
  - name: 海关价格数据
    url: https://data.yunlvai.com
    purpose: 价格数据查询
    auth: Bearer Token (同TRADEGPT_API_KEY)  # 明确使用同一密钥
  - name: Email发送
    url: (用户自配置SMTP服务器)
    purpose: 预警通知发送
    auth: 用户自配置  # 明确是用户配置的服务
```

### 建议4：细化LinkedIn技能授权流程（中优先级）

**问题**：yunlv-linkedin-outreach的session token使用不透明。

**解决方案**：
```markdown
### LinkedIn授权方式
1. **推荐**：使用OAuth 2.0授权（可撤销、可限定权限）
2. **备选**：Session Token（需用户自行获取，风险自担）

### 数据存储
- LinkedIn档案数据：存储在 `./data/yunlv-skills/linkedinOutreach/profiles/`
- 用户可随时删除本地数据
- 不在第三方服务器存储档案副本
```

### 建议5：添加合规性声明（低优先级）

**问题**：合规检查技能涉及PII和敏感数据传输。

**解决方案**：在SKILL.md中添加明确的数据处理声明：
```markdown
## 数据处理声明

- **传输数据**：提交的筛查信息（公司名、地址、法人等）将发送至 api.yunlvai.com
- **数据保留**：API方保留数据的期限请参阅 https://yunlvai.com/privacy
- **用户责任**：确保提交的数据符合GDPR/CAN-SPAM及贵司数据政策
- **建议**：高敏感筛查建议在提交前进行脱敏处理
```

---

## 五、修复后的重新发布步骤

### 步骤1：本地修复文件

```bash
# 1. 修复clawhub.yaml中的元数据不一致
# 2. 修改SKILL.md中的信任约束表述
# 3. 添加数据处理声明
```

### 步骤2：验证文件一致性

```bash
# 检查clawhub.yaml中的required_env/required_bins
# 确保与SKILL.md中的描述一致
```

### 步骤3：重新上传到ClawHub

```bash
# 重新打包并上传（使用clawhub CLI）
clawhub skill publish ./skills/yunlv-skills/skill_xxx
```

### 步骤4：触发重新扫描（已完成）

已成功提交6个Suspicious技能的重新扫描请求：

```
✔ yunlv-guangjiao - 重新扫描请求已提交
✔ yunlv-customs-scout - 重新扫描请求已提交
✔ yunlv-linkedin-outreach - 重新扫描请求已提交
✔ yunlv-product-desc - 重新扫描请求已提交
✔ yunlv-price-monitor - 重新扫描请求已提交
✔ yunlv-compliance-check - 重新扫描请求已提交
```

### 步骤5：等待扫描结果

重新扫描通常需要 **5-30分钟**。建议：
1. 等待扫描完成后再次检查ClawHub页面
2. 查看Security Scans区域的更新状态
3. 如仍为Suspicious，根据新的Guidance进行调整

---

## 六、附录：ClawScan审查维度说明

| 维度 | 说明 |
|------|------|
| Purpose & Capability | 技能声明的功能与实际能力是否匹配 |
| Instruction Scope | 指令范围是否清晰、有无越界风险 |
| Install Mechanism | 安装机制是否安全 |
| Credentials | 凭证声明是否完整、必要 |
| Persistence & Privilege | 是否请求持久化特权 |

---

**报告完成**

*如需进一步的技术细节或修复协助，请联系云旅AI团队。*
