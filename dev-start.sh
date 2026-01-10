#!/bin/bash

# 开发环境启动脚本
# 同时启动后端 Flask 和前端 Vue 3 应用

echo "=========================================="
echo "股票异动监控系统 - 开发环境启动"
echo "=========================================="
echo ""

# 检查 Python 是否安装
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python，请先安装 Python 3.12+"
    exit 1
fi

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo "❌ 错误: 未找到 pnpm，请先安装 pnpm"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "🚀 启动后端服务 (Flask)..."
echo "   地址: http://127.0.0.1:5000"
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端服务 (Vue 3)..."
echo "   地址: http://127.0.0.1:3000"
cd frontend
pnpm dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ 开发服务已启动"
echo "=========================================="
echo ""
echo "后端进程 ID: $BACKEND_PID"
echo "前端进程 ID: $FRONTEND_PID"
echo ""
echo "访问地址: http://127.0.0.1:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待进程
wait

