# 企业文档生成API实现

## 概述

本实现添加了一个新的API端点 `POST /api/enterprise/{id}/generate-docs`，允许前端通过企业ID生成三个应急预案文档：

1. 环境风险评估报告
2. 突发环境事件应急预案
3. 应急资源调查报告

## 实现文件

### 核心实现文件

1. **`backend/app/schemas/enterprise.py`**
   - 添加了 `EnterpriseDataRequest`、`DocumentData` 和 `DocumentGenerationResponse` 模型
   - 定义了API请求和响应的数据结构

2. **`backend/app/routes/enterprise.py`**
   - 添加了 `convert_enterprise_to_emergency_plan_format()` 函数，将企业数据转换为文档生成所需的格式
   - 添加了 `count_words()` 函数，统计HTML内容的字数
   - 实现了 `generate_enterprise_docs()` API端点

### 测试文件

1. **`backend/test_enterprise_document_generation.py`**
   - 完整的pytest测试套件
   - 测试各种场景：成功、失败、权限验证等

2. **`backend/test_enterprise_docs_api.py`**
   - 简单的API测试脚本
   - 可以直接运行，模拟完整的API调用流程

3. **`backend/test_api_quickstart.sh`**
   - 快速启动脚本
   - 自动设置环境并运行测试

### 文档文件

1. **`backend/ENTERPRISE_DOCS_API_TEST_GUIDE.md`**
   - 详细的测试指南
   - 包含多种测试方法和故障排除

## API使用方法

### 请求格式

```http
POST /api/enterprise/{enterprise_id}/generate-docs
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "basic_info": {
    "company_name": "企业名称",
    "risk_level": "一般"
  },
  "production_process": {
    "products": [...]
  },
  "environment_info": {
    "nearby_receivers": [...]
  },
  "compliance_info": {
    "eia": {...}
  },
  "emergency_resources": {
    "contact_list_internal": [...],
    "emergency_materials": [...]
  },
  "additional_data": {
    "custom_field": "自定义值"
  }
}
```

### 响应格式

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
      "id": 123,
      "name": "企业名称",
      "generated_at": "2024-01-01T12:00:00Z"
    }
  },
  "errors": []
}
```

## 快速测试

### 方法1：使用快速启动脚本

```bash
cd backend
./test_api_quickstart.sh
```

### 方法2：手动测试

1. 启动后端服务：
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. 在另一个终端运行测试脚本：
   ```bash
   cd backend
   python test_enterprise_docs_api.py
   ```

### 方法3：运行pytest测试

```bash
cd backend
pytest test_enterprise_document_generation.py -v
```

## 技术特点

1. **数据转换**：将企业信息模型转换为符合emergency_plan.json结构的数据格式
2. **数据合并**：支持前端提交的表单数据与数据库信息合并
3. **错误处理**：完整的错误处理和用户友好的错误消息
4. **权限验证**：使用现有的认证和权限系统
5. **字数统计**：自动统计生成文档的字数
6. **模板缓存**：利用现有的模板缓存机制提高性能

## 依赖关系

- 依赖现有的 `DocumentGenerator` 服务
- 使用现有的企业信息模型 (`EnterpriseInfo`)
- 集成现有的认证系统 (`get_current_user`)
- 使用现有的错误处理机制 (`handle_error`)

## 注意事项

1. 确保数据库中存在测试用户和企业数据
2. 确保模板文件存在于 `backend/app/prompts/templates/` 目录
3. 生成的HTML包含完整的CSS样式，可以直接在浏览器中查看
4. API支持部分数据更新，前端可以只提交需要覆盖的字段

## 故障排除

1. **企业不存在**：检查企业ID是否正确，确保企业属于当前用户
2. **模板加载失败**：检查模板文件是否存在，查看后端日志获取详细错误
3. **权限错误**：确保用户已登录，访问令牌有效
4. **数据格式错误**：检查请求数据是否符合JSON格式

## 扩展性

该实现具有良好的扩展性：

1. 可以轻松添加新的文档类型
2. 支持自定义数据字段
3. 可以集成到前端的工作流中
4. 支持异步处理（如果需要）

## 总结

本实现提供了一个完整的企业文档生成API，支持前端通过企业ID生成三个应急预案文档。API设计遵循RESTful原则，具有良好的错误处理和权限验证，同时提供了完整的测试套件和文档。