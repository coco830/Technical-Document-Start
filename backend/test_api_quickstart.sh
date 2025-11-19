#!/bin/bash

# 企业文档生成API快速测试脚本

echo "=== 企业文档生成API快速测试 ==="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查是否在backend目录
if [[ ! -f "app/main.py" ]]; then
    echo "❌ 请在backend目录下运行此脚本"
    exit 1
fi

# 安装依赖（如果需要）
if [[ ! -d ".venv" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

echo "📦 激活虚拟环境..."
source .venv/bin/activate

echo "📦 安装依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 检查后端服务是否运行
echo "🔍 检查后端服务..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务正在运行"
else
    echo "❌ 后端服务未运行，正在启动..."
    echo "请在另一个终端运行以下命令："
    echo "cd $(pwd) && source .venv/bin/activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "等待服务启动..."
    sleep 5
    
    # 再次检查
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ 后端服务启动失败，请手动启动后端服务"
        exit 1
    fi
fi

# 创建测试输出目录
mkdir -p test_output

# 运行测试脚本
echo "🧪 运行API测试..."
python test_enterprise_docs_api.py

echo ""
echo "✅ 测试完成！"
echo "📁 生成的文档保存在 test_output/ 目录中"