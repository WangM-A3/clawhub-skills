#!/bin/bash
# ClawHub技能重新发布脚本
# 用法: bash clawhub-resubmit.sh

# ClawHub Token (已配置)
CLAWHUB_TOKEN="clh_RwU-WFhmb3TcVec2kx_plKLzvg4FG7iCP4JgPvpi6lk"

echo "======================================"
echo "ClawHub技能重新发布"
echo "======================================"

# 1. OpenClaw Enterprise
echo ""
echo "[1/3] 正在重新发布 OpenClaw Enterprise..."
cd ./skills/openclaw-enterprise
npx clawhub@latest publish \
  --token "$CLAWHUB_TOKEN" \
  --slug "openclaw-enterprise"

# 2. GEO AgentOps
echo ""
echo "[2/3] 正在重新发布 GEO AgentOps..."
cd ../geo-agentops
npx clawhub@latest publish \
  --token "$CLAWHUB_TOKEN" \
  --slug "geo-agentops"

# 3. Industrial Silicon Army
echo ""
echo "[3/3] 正在重新发布 Industrial Silicon Army..."
cd ../industrial-silicon-army
npx clawhub@latest publish \
  --token "$CLAWHUB_TOKEN" \
  --slug "industrial-silicon-army"

echo ""
echo "======================================"
echo "发布完成！"
echo "请访问 https://clawhub.ai/developer 检查审核状态"
echo "======================================"
