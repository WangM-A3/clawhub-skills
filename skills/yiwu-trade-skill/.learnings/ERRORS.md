# Errors | 操作失败与异常记录

> 义乌.Skill 自进化机制核心文件
> 记录报关失败、物流异常、支付风险等实战中的错误案例

**异常类型**: customs_failure | logistics_failure | payment_risk | compliance_violation | system_error

---

## 异常记录规范

| 异常类型 | 说明 | 优先级 |
|----------|------|--------|
| customs_failure | 报关/清关失败 | high |
| logistics_failure | 物流延误/丢件/破损 | high |
| payment_risk | 支付诈骗/拒付/账期风险 | critical |
| compliance_violation | 违规操作/政策红线 | critical |
| system_error | 系统/工具/API故障 | medium |

---

## 示例条目

### [ERR-YYYYMMDD-001] customs_clearance_failed

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: compliance

### Summary
报关低报货值导致海关查验，延误出运5天

### Details
**错误场景**：
- 实际货值$15,000，申报$8,000（低报46%）
- 被海关布控查验
- 要求提供采购发票、付款凭证
- 补缴关税+滞纳金

**根因分析**：
- 客户要求降低关税成本
- 未意识到低报的法律风险
- 1039政策"免征不退"不等于"可低报"

### Correct Approach
- 1039模式：如实申报，免征增值税，但需缴纳关税
- 货值申报不低于实际成交价70%
- 提供完整采购凭证链

### Suggested Action
在合规红线清单中强调：低报瞒报货值是严重违规

### Metadata
- Source: error
- Related Files: references/compliance_guide.md
- Tags: 海关查验, 低报风险, 1039合规
- Resolution: 已向用户说明1039政策正确理解方式

---

### [ERR-YYYYMMDD-002] logistics_delay

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: logistics

### Summary
圣诞旺季海运延误，欧洲客户错过销售窗口

### Details
**错误场景**：
- 10月出货，走海运（预计30天）
- 遭遇港口拥堵+圣诞旺季塞港
- 实际到港：1月15日
- 客户错过圣诞+新年销售季

**根因分析**：
- 未考虑旺季物流时效波动
- 旺季海运时效可能延长50%-100%
- 缺乏备选物流方案

### Correct Approach
- 圣诞/新年订单：最晚9月中旬出货
- 旺季建议提前30-45天预订舱位
- 高价值订单考虑海运+空运组合

### Suggested Action
在物流调度模块增加"旺季物流时效预警"章节

### Metadata
- Source: error
- Related Files: references/logistics_guide.md
- Tags: 物流延误, 旺季预警, 欧洲物流
- Resolution: 建议客户增加空运备货方案

---

### [ERR-YYYYMMDD-003] payment_scam_attempt

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: critical
**Status**: blocked

### Summary
尼日利亚客户伪造水单，试图骗取货物

### Details
**诈骗手法**：
- 初次合作，客户爽快接受报价
- 预付30%定金后，发来水单截图
- 水单显示金额正确，但附言信息异常
- 银行查询：实际未到账

**识别特征**：
- 水单抬头与付款账户不一致
- 金额精确到分（小数点后两位）
- 催促发货时间与水单时间矛盾

### Correct Approach
- 坚持原则：银行到账通知为准，不以水单为据
- 核对水单与付款账户信息一致性
- 大额订单建议视频核实付款账户

### Suggested Action
在支付结算模块完善"支付风控信号"清单

### Metadata
- Source: error
- Related Files: references/payment_guide.md
- Tags: 支付诈骗, 水单造假, 尼日利亚风险
- Resolution: 拦截成功，货物未发出

---

### [ERR-YYYYMMDD-004] compliance_risk_self_check

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: critical
**Status**: resolved

### Summary
1039主体注册地址与实际经营地不符，可能影响后续核销

### Details
**风险点**：
- 个体工商户注册地址：某小区住宅
- 实际经营地：国际商贸城档口
- 可能导致银行开户审核不通过
- 后续出口核销可能受限

**根因分析**：
- 注册时代理机构未告知地址要求
- 未了解1039对经营地址的特殊要求

### Correct Approach
- 注册地址需与实际经营地址一致或符合政策要求
- 咨询当地商务局或1039服务窗口
- 保留租赁合同、档口协议等经营证明

### Suggested Action
在起盘SOP中增加1039主体注册地址要求说明

### Metadata
- Source: error
- Related Files: references/startup_guide.md
- Tags: 1039注册, 合规风险, 主体资质

---

### [ERR-YYYYMMDD-005] supplier_quality_issue

**Logged**: 2026-04-26T12:00:00+08:00
**Priority**: high
**Status**: resolved

### Summary
供应商以次充好，出货后发现不良率高达25%

### Details
**问题场景**：
- 样品确认OK（不良率<1%）
- 大货到仓后发现不良率25%
- 供应商推脱责任
- 客户要求索赔

**根因分析**：
- 未进行出货前第三方验货
- 未在合同中明确质量条款
- 付款节点控制不当

### Correct Approach
- 大货出货前必须抽检（5%-10%）
- 合同明确质量标准、不良率上限、赔偿条款
- 付款与验货结果挂钩（验货合格后付尾款）

### Suggested Action
在供应链模块完善质检SOP和合同模板

### Metadata
- Source: error
- Related Files: references/quality_control.md
- Tags: 质量事故, 供应商风险, 质检缺失

---

## 错误预防机制

### 高频错误预警
| 错误类型 | 预防措施 | 检查清单 |
|----------|----------|----------|
| 报关低报 | 货值真实性核查 | 发票+付款凭证+流水一致 |
| 物流延误 | 预留buffer时间 | 旺季提前30天预订 |
| 支付诈骗 | 银行到账为准 | 水单≠到账 |
| 质量事故 | 出货前验货 | 抽检报告留存 |

### 错误复盘机制
1. 发生错误后24小时内记录
2. 分析根因（5Why分析法）
3. 制定预防措施
4. 更新对应SOP文档
5. 定期回顾，避免同类问题重复发生

---
