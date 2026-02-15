#!/bin/bash
# Agent Lightning 环境配置脚本
# 用于设置项目所需的环境变量和激活虚拟环境

# 设置agentlightning代码位置
export AGL_HOME=~/gaokewoo/agent-lightning

# 切换到项目目录
cd $AGL_HOME

# 激活uv虚拟环境
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "✓ UV虚拟环境已激活"
else
    echo "⚠ 虚拟环境不存在，请先运行: uv sync"
fi

# 设置deepseek环境变量，运行APO case时需要
export OPENAI_API_KEY="YOUR_DEEPSEEK_KEY"
export OPENAI_BASE_URL="https://api.deepseek.com"
echo "✓ DeepSeek API环境变量已设置"

# 设置huggingface mirror，运行spider case时需要
export HF_ENDPOINT=https://hf-mirror.com
echo "✓ HuggingFace镜像已设置: $HF_ENDPOINT"

# 设置wandb，运行spider case时需要
export WANDB_API_KEY=YOUR_WANDB_KEY
echo "✓ W&B API Key已设置"

# 显示当前环境状态
echo ""
echo "========================================="
echo "Agent Lightning 环境已配置完成"
echo "========================================="
echo "项目目录: $AGL_HOME"
echo "Python: $(which python)"
echo "OPENAI_BASE_URL: $OPENAI_BASE_URL"
echo "HF_ENDPOINT: $HF_ENDPOINT"
echo "========================================="
