#!/bin/bash

# 启动脚本 - 悦恩人机共写平台

echo "🚀 启动悦恩人机共写平台..."

# 进入项目目录
cd "$(dirname "$0")"

# 启动后端
echo "📦 启动后端服务..."
cd backend
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "✅ 后端启动成功 (PID: $BACKEND_PID) - http://localhost:8000"
else
    echo "⚠️  警告: 后端虚拟环境不存在，请先运行: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
if [ -d "node_modules" ]; then
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ 前端启动成功 (PID: $FRONTEND_PID) - http://localhost:3000"
else
    echo "⚠️  警告: 前端依赖未安装，请先运行: cd frontend && npm install"
    exit 1
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

# 等待任意服务退出
wait $BACKEND_PID $FRONTEND_PID
