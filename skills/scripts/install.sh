#!/bin/bash
# OpenClaw Enterprise 技能安装脚本

set -e

echo "🦞 OpenClaw Enterprise 技能安装"
echo "=================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 Python 3.8+"
    exit 1
fi

# 检查 pip
if ! command -v pip &> /dev/null; then
    echo "❌ 需要安装 pip"
    exit 1
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  未设置 OPENAI_API_KEY 环境变量"
    echo "   请运行: export OPENAI_API_KEY='your-key'"
fi

# 安装依赖
echo "📦 安装依赖..."
pip install -q langchain langgraph openai fastapi uvicorn pydantic redis psycopg2-binary

# 创建配置目录
echo "📁 创建配置目录..."
mkdir -p ~/.openclaw/{config,data,logs}

# 复制技能文件
echo "📋 安装技能文件..."
SKILL_DIR="$HOME/.openclaw/skills/openclaw-enterprise"
mkdir -p "$SKILL_DIR"
cp -r . "$SKILL_DIR/"

echo ""
echo "✅ 安装完成!"
echo ""
echo "🚀 快速启动:"
echo "   cd $SKILL_DIR"
echo "   python api_server.py"
echo ""
echo "📖 文档: https://openclaw-ai.com/docs"
