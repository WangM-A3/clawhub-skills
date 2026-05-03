#!/bin/bash
# OpenClaw Enterprise 快速启动脚本

set -e

SKILL_DIR="$HOME/.openclaw/skills/openclaw-enterprise"

# 检查是否已安装
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 技能未安装，请先运行 ./scripts/install.sh"
    exit 1
fi

cd "$SKILL_DIR"

# 解析参数
MODE=${1:-"api"}
PORT=${2:-8080}

case "$MODE" in
    api)
        echo "🚀 启动 API 服务 (端口 $PORT)..."
        python3 api_server.py --port "$PORT"
        ;;
    wechat)
        echo "🚀 启动微信网关 (端口 8081)..."
        python3 wechat_server.py
        ;;
    test)
        echo "🧪 运行测试..."
        python3 -m pytest tests/ -v
        ;;
    help|*)
        echo "OpenClaw Enterprise 启动脚本"
        echo ""
        echo "用法: ./run.sh [模式] [端口]"
        echo ""
        echo "模式:"
        echo "  api     启动 API 服务 (默认)"
        echo "  wechat  启动微信网关"
        echo "  test    运行测试套件"
        echo "  help    显示帮助"
        echo ""
        echo "示例:"
        echo "  ./run.sh api 8080"
        echo "  ./run.sh wechat"
        ;;
esac
