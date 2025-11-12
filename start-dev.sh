#!/bin/bash

# 悦恩人机共写平台 - 开发环境启动脚本

echo "🌿 悦恩人机共写平台 - 启动开发环境"
echo "=================================="

# 检查是否在项目根目录
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend
if [ -d ".venv" ]; then
    source .venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✅ 后端启动成功 (PID: $BACKEND_PID) - http://localhost:8000"
else
    echo "⚠️  警告: 后端虚拟环境不存在，请先运行: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
fi

cd ..

# 等待后端启动
sleep 2

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
if [ -d "node_modules" ]; then
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ 前端启动成功 (PID: $FRONTEND_PID) - http://localhost:3000"
else
    echo "⚠️  警告: 前端依赖未安装，请先运行: cd frontend && npm install"
fi

cd ..

echo ""
echo "🚀 开发环境已启动！"
echo "=================================="
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
wait
