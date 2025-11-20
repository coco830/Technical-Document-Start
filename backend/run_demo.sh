#!/bin/bash

# 端到端Demo运行脚本
# 用于生成企业文档的完整演示

echo "=========================================="
echo "企业文档生成Demo - 运行脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否在backend目录
if [ ! -f "sample_enterprise.json" ]; then
    echo "错误：请在backend目录下运行此脚本"
    exit 1
fi

# 设置Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "开始运行Demo..."
echo "企业数据文件：sample_enterprise.json"
echo "输出目录：test_output/"
echo ""

# 运行Demo脚本
python3 demo_generate_documents.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Demo执行成功！"
    echo "=========================================="
    echo "生成的文件："
    ls -la test_output/*demo.*
    echo ""
    echo "可以使用以下命令查看生成的文档："
    echo "  - 风险评估报告：test_output/risk_assessment_demo.html"
    echo "  - 应急预案：test_output/emergency_plan_demo.html"
    echo "  - 应急资源调查报告：test_output/resource_report_demo.html"
    echo "  - AI段落信息：test_output/ai_sections_demo.json"
    echo ""
    echo "使用浏览器打开HTML文件即可查看生成的文档"
else
    echo ""
    echo "=========================================="
    echo "Demo执行失败！"
    echo "=========================================="
    echo "请检查错误信息并重试"
    exit 1
fi