# OpenClaw Enterprise 技能发布指南

## 📦 技能包结构

已创建完整的技能包：
```
skills/openclaw-enterprise/
├── SKILL.md              # 技能定义（核心）
├── README.md             # 说明文档
├── clawhub.yaml          # 发布配置
├── scripts/
│   ├── install.sh        # 安装脚本
│   └── run.sh            # 启动脚本
└── references/
    └── QUICKSTART.md     # 快速参考
```

## 🚀 发布到 ClawHub

### 方法1: CLI 发布（推荐）

```bash
# 1. 安装 ClawHub CLI
pip install clawhub-cli

# 2. 登录
clawhub login

# 3. 进入技能目录
cd skills/openclaw-enterprise

# 4. 验证技能包
clawhub validate

# 5. 发布
clawhub publish
```

### 方法2: Web 界面发布

1. 访问 https://clawhub.ai/developer
2. 创建新技能
3. 上传技能包 ZIP 文件
4. 填写发布信息
5. 提交审核

## 🦞 发布到 QBotClaw

QBotClaw 完全兼容 OpenClaw 技能格式：

### 方法1: 通过 ClawHub 同步
发布到 ClawHub 后，技能会自动同步到 QBotClaw 技能广场。

### 方法2: 直接提交
```bash
# 使用 QBotClaw CLI
qbot skill publish --source skills/openclaw-enterprise
```

### 方法3: 技能广场提交
1. 访问 QQ浏览器龙虾技能广场
2. 注册开发者账号
3. 提交技能审核
4. 等待审核通过

## ✅ 发布前检查清单

- [ ] SKILL.md 元数据完整
- [ ] README.md 说明清晰
- [ ] 安装脚本可运行
- [ ] 环境变量要求说明
- [ ] 依赖版本明确
- [ ] 示例代码可执行

## 📋 审核标准

ClawHub/QBotClaw 审核要点：

1. **功能完整性** - 技能能正常工作
2. **文档质量** - 说明清晰易懂
3. **安全性** - 无恶意代码
4. **合规性** - 符合平台规范
5. **用户体验** - 安装使用便捷

## 🔗 发布后

### 获取安装链接
```
https://clawhub.ai/skills/openclaw-enterprise
```

### 用户安装方式
```bash
# ClawHub
clawhub install openclaw-enterprise

# QBotClaw
/install https://clawhub.ai/skills/openclaw-enterprise
```

### 更新版本
```bash
# 修改 clawhub.yaml 中的版本号
version: 1.0.1

# 重新发布
clawhub publish
```

## 📊 统计数据

发布后可在开发者后台查看：
- 安装量
- 使用频率
- 用户评分
- 问题反馈

---

**发布平台**: ClawHub / QBotClaw  
**技术支持**: https://openclaw-ai.com/support
