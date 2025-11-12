# AI 服务集成指南

本文档说明了如何配置和使用集成了真实 OpenAI API 的 AI 服务。

## 功能概述

新的 AI 服务包含以下功能：

1. **真实 OpenAI API 集成** - 支持使用真实的 OpenAI API 进行内容生成
2. **API 密钥验证** - 验证 API 密钥的有效性和格式
3. **智能降级策略** - 当 API 不可用时自动降级到模拟生成
4. **重试机制** - 支持指数退避的重试策略
5. **使用量统计** - 跟踪全局和用户级别的使用量
6. **使用限制** - 支持全局和用户每日使用限制
7. **错误处理** - 完善的错误处理和日志记录

## 配置说明

### 1. 环境变量配置

在 `backend/.env` 文件中添加以下配置：

```bash
# OpenAI API配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4

# AI使用限制配置
AI_DAILY_LIMIT=100
AI_USER_DAILY_LIMIT=10
AI_REQUEST_TIMEOUT=30
AI_MAX_RETRIES=3
```

### 2. 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `OPENAI_BASE_URL` | OpenAI API 基础 URL | `https://api.openai.com/v1` |
| `AI_MODEL` | 使用的 AI 模型 | `gpt-4` |
| `AI_DAILY_LIMIT` | 全局每日使用限制 | `100` |
| `AI_USER_DAILY_LIMIT` | 用户每日使用限制 | `10` |
| `AI_REQUEST_TIMEOUT` | API 请求超时时间（秒） | `30` |
| `AI_MAX_RETRIES` | 最大重试次数 | `3` |

## 使用方法

### 1. 基本使用

```python
from app.services.ai_service import get_ai_service

# 获取 AI 服务实例
ai_service = get_ai_service()

# 生成内容
prompt = "请生成一个关于企业安全生产管理的章节内容"
config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
}

# 带用户 ID 的生成（用于使用量统计）
result = ai_service.generate(prompt, config, user_id="user_123")
```

### 2. 检查服务可用性

```python
# 检查 AI 服务是否可用
if ai_service.is_available():
    print("AI 服务可用")
else:
    print("AI 服务不可用，将使用模拟生成")
```

### 3. 获取使用量统计

```python
# 获取用户使用量
user_usage = ai_service.get_user_usage("user_123")
print(f"用户今日使用量: {user_usage['today']}")
print(f"用户剩余可用次数: {user_usage['remaining']}")

# 获取全局统计
global_stats = ai_service.get_usage_stats()
print(f"全局使用统计: {global_stats}")
```

## API 端点

### 1. 生成内容

```
POST /api/ai/generate
```

请求体：
```json
{
    "template_id": "emergency_plan",
    "section_id": "basic_principles",
    "data": {
        "company_name": "示例公司",
        "industry": "制造业"
    }
}
```

### 2. 获取使用量统计

```
GET /api/ai/usage/stats
```

响应：
```json
{
    "success": true,
    "user_usage": {
        "today": 5,
        "remaining": 5,
        "limit": 10
    },
    "global_stats": {
        "daily_limit": 100,
        "user_daily_limit": 10,
        "usage": {
            "2023-12-01": {
                "total": 25,
                "users": {
                    "user_123": 5,
                    "user_456": 3
                }
            }
        }
    },
    "service_available": true
}
```

## 错误处理和降级策略

### 1. 自动降级

当出现以下情况时，系统会自动降级到模拟生成：

- 未配置 API 密钥
- API 密钥无效
- API 调用失败（网络错误、认证失败等）
- 达到使用限制

### 2. 重试机制

- 支持指数退避重试（2, 4, 8 秒）
- 针对不同错误类型采用不同等待时间
- 速率限制错误等待 60 秒
- 超时错误等待 5 秒

### 3. 错误类型处理

| 错误类型 | 处理方式 |
|----------|----------|
| 认证失败 | 立即失败，不重试 |
| 速率限制 | 等待 60 秒后重试 |
| 超时错误 | 等待 5 秒后重试 |
| 其他错误 | 指数退避重试 |

## 测试

### 1. 运行测试脚本

```bash
cd backend
python test_ai_service.py
```

测试脚本会验证以下功能：

- 服务可用性检查
- API 密钥验证
- 内容生成（真实 API 和模拟）
- 使用量统计
- 使用限制
- 错误处理

### 2. 手动测试

1. **无 API 密钥测试**：
   - 注释掉 `OPENAI_API_KEY` 配置
   - 验证系统使用模拟生成

2. **无效 API 密钥测试**：
   - 设置错误的 API 密钥
   - 验证系统检测到无效密钥

3. **使用限制测试**：
   - 设置较低的 `AI_USER_DAILY_LIMIT`
   - 连续生成直到触发限制
   - 验证系统降级到模拟生成

## 生产环境注意事项

### 1. 安全性

- 确保 API 密钥安全存储
- 使用环境变量或密钥管理服务
- 定期轮换 API 密钥

### 2. 监控

- 监控 API 使用量和成本
- 设置使用量告警
- 记录错误日志

### 3. 性能优化

- 考虑使用 Redis 存储使用量统计
- 实现异步 API 调用
- 添加请求缓存

### 4. 扩展性

- 支持多个 AI 提供商
- 实现负载均衡
- 添加 A/B 测试功能

## 故障排除

### 1. 常见问题

**问题：API 调用失败**
- 检查 API 密钥是否正确
- 验证网络连接
- 确认 API 配额

**问题：使用量统计不准确**
- 检查时区设置
- 确认日期重置逻辑
- 验证用户 ID 传递

**问题：降级策略不工作**
- 检查错误处理逻辑
- 验证模拟生成函数
- 确认日志记录

### 2. 调试方法

1. 启用详细日志：
   ```python
   logging.getLogger('app.services.ai_service').setLevel(logging.DEBUG)
   ```

2. 检查环境变量：
   ```python
   import os
   print(f"API Key: {os.getenv('OPENAI_API_KEY')}")
   ```

3. 验证 API 连接：
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="your-key")
   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hello"}],
       max_tokens=10
   )
   ```

## 更新日志

### v1.0.0 (2023-12-01)

- 集成真实 OpenAI API
- 添加使用量统计和限制
- 实现智能降级策略
- 添加重试机制
- 完善错误处理
- 添加使用量统计 API 端点