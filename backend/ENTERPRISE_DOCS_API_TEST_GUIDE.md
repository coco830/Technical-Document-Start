# 企业文档生成API测试指南

## 概述

本指南说明如何测试新实现的企业文档生成API端点 `POST /api/enterprise/{id}/generate-docs`。

## 前提条件

1. 确保后端服务正在运行：
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. 确保数据库中存在测试用户和企业数据。如果没有，可以使用以下脚本创建：
   ```bash
   cd backend
   python create_test_user.py
   ```

## 测试方法

### 方法1：使用简单测试脚本

我们提供了一个简单的测试脚本 `test_enterprise_docs_api.py`，它会自动完成以下步骤：

1. 登录获取访问令牌
2. 获取企业信息列表
3. 选择第一个企业进行文档生成测试
4. 显示生成结果并保存第一个文档到文件

运行测试脚本：
```bash
cd backend
python test_enterprise_docs_api.py
```

### 方法2：使用pytest运行完整测试套件

运行完整的单元测试：
```bash
cd backend
pytest test_enterprise_document_generation.py -v
```

### 方法3：手动使用curl或API客户端

1. 首先登录获取访问令牌：
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=test@example.com&password=testpassword"
   ```

2. 使用获取的令牌测试文档生成API：
   ```bash
   curl -X POST "http://localhost:8000/api/enterprise/1/generate-docs" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "basic_info": {
            "company_name": "测试企业",
            "risk_level": "一般"
          },
          "production_process": {
            "products": [
              {
                "product_name": "测试产品",
                "product_type": "主产品",
                "design_capacity": "1000吨/年",
                "actual_output": "800吨/年"
              }
            ]
          },
          "environment_info": {
            "nearby_receivers": [
              {
                "receiver_type": "水体",
                "name": "测试河流",
                "direction": "东",
                "distance_m": 500,
                "population_or_scale": "小型河流"
              }
            ]
          },
          "emergency_resources": {
            "contact_list_internal": [
              {
                "role": "应急指挥",
                "name": "张三",
                "department": "管理部",
                "mobile": "13800138000"
              }
            ],
            "emergency_materials": [
              {
                "material_name": "灭火器",
                "unit": "个",
                "quantity": 10,
                "purpose": "消防",
                "storage_location": "仓库",
                "keeper": "保管员"
              }
            ]
          }
        }'
   ```

## 预期结果

成功的API响应应该如下格式：

```json
{
    "success": true,
    "message": "文档生成成功",
    "data": {
        "tabs": [
            {
                "id": "risk_report",
                "title": "环境风险评估报告",
                "content": "<html>...</html>",
                "word_count": 11829
            },
            {
                "id": "emergency_plan",
                "title": "突发环境事件应急预案",
                "content": "<html>...</html>",
                "word_count": 27033
            },
            {
                "id": "resource_report",
                "title": "应急资源调查报告",
                "content": "<html>...</html>",
                "word_count": 6463
            }
        ],
        "enterprise_info": {
            "id": 1,
            "name": "测试企业",
            "generated_at": "2024-01-01T12:00:00Z"
        }
    },
    "errors": []
}
```

## 故障排除

### 问题1：登录失败
- 确保测试用户存在
- 检查用户名和密码是否正确

### 问题2：企业信息不存在
- 确保数据库中存在企业信息
- 检查企业ID是否正确

### 问题3：文档生成失败
- 检查模板文件是否存在
- 查看后端日志获取详细错误信息
- 确保请求数据格式正确

### 问题4：无法连接到服务器
- 确保后端服务正在运行
- 检查端口是否正确（默认8000）
- 确认防火墙设置

## 文件结构

测试过程中会创建以下文件：

- `test_enterprise_docs_api.py`: 简单的API测试脚本
- `test_enterprise_document_generation.py`: 完整的单元测试
- `test_output/`: 测试输出目录，保存生成的HTML文档

## 注意事项

1. 测试脚本会自动创建 `test_output` 目录（如果不存在）
2. 生成的HTML文档包含完整的样式，可以直接在浏览器中打开查看
3. 测试过程中会打印详细的日志信息，便于调试