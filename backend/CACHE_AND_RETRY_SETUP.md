# 缓存降级与重试机制 - 使用指南

版本：v1.0
日期：2025-11-04

---

## 📋 功能概述

本次更新实现了：

1. **缓存自动降级**：Redis → 内存缓存
   - 优先使用 Redis（如果配置了 `REDIS_URL`）
   - 如果 Redis 不可用，自动降级到内存缓存
   - 对业务代码完全透明

2. **AI API 重试机制**
   - 自动重试 3 次（可配置）
   - 指数退避策略（2秒、4秒、8秒）
   - 30 秒超时控制

3. **缓存统计**
   - 缓存命中率
   - 请求次数统计
   - 错误次数统计

---

## 🚀 快速开始

### 方案 1：仅使用内存缓存（无需 Redis）

**适用场景**：开发测试、单机部署

```bash
# 1. 不配置 REDIS_URL
# .env 文件中不设置 REDIS_URL 即可

# 2. 启动服务
cd backend
python -m uvicorn app.main:app --reload
```

系统会自动使用内存缓存：
```
缓存服务已启动，使用内存缓存后端（降级模式）
```

---

### 方案 2：使用 Redis 缓存（推荐生产环境）

**适用场景**：生产部署、多实例负载均衡

#### 步骤 1：安装 Redis

**Docker 方式（推荐）**：
```bash
docker run -d \
  --name yueen-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**或本地安装**：
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows（使用 WSL）
sudo apt-get install redis-server
```

#### 步骤 2：安装 Python Redis 客户端

```bash
cd backend
pip install redis==5.0.1
```

或取消注释 `requirements.txt` 中的：
```
redis==5.0.1
```

#### 步骤 3：配置环境变量

在 `.env` 文件中添加：
```bash
REDIS_URL=redis://localhost:6379/0
```

如果 Redis 有密码：
```bash
REDIS_URL=redis://:your-password@localhost:6379/0
```

#### 步骤 4：启动服务

```bash
python -m uvicorn app.main:app --reload
```

系统会自动使用 Redis：
```
成功连接到 Redis: redis://localhost:6379/0
缓存服务已启动，使用 Redis 后端
```

---

## 🤖 配置 AI 模型

### 方案 1：使用模拟生成（默认）

**适用场景**：开发测试、演示

无需任何配置，系统会自动使用模拟生成。

---

### 方案 2：接入 OpenAI API

#### 步骤 1：安装 OpenAI SDK

```bash
pip install openai==1.12.0
```

或取消注释 `requirements.txt` 中的：
```
openai==1.12.0
```

#### 步骤 2：配置环境变量

在 `.env` 文件中添加：
```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
AI_MODEL=gpt-4  # 可选
```

#### 步骤 3：重启服务

```bash
python -m uvicorn app.main:app --reload
```

系统会自动使用 OpenAI API：
```
AI 服务已启动，使用模型: gpt-4
```

---

### 方案 3：使用国内 AI 服务

#### 通义千问（阿里云）

```bash
# .env
OPENAI_API_KEY=sk-your-dashscope-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-max
```

#### API2D（OpenAI 镜像）

```bash
# .env
OPENAI_API_KEY=fk-your-api2d-key
OPENAI_BASE_URL=https://api.api2d.net/v1
AI_MODEL=gpt-4
```

---

## 📊 API 使用示例

### 1. 生成内容

```bash
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "template_id": "emergency_plan",
    "section_id": "2",
    "data": {
      "enterprise_info": {
        "enterprise_name": "测试企业",
        "industry_type": "化工制造",
        "address": "北京市朝阳区",
        "main_products": "化工产品",
        "employees_count": 100
      }
    }
  }'
```

**响应**：
```json
{
  "success": true,
  "content": "生成的内容...",
  "section_title": "企业概况",
  "cached": false
}
```

第二次调用相同参数会返回缓存：
```json
{
  "cached": true
}
```

---

### 2. 查看缓存统计

```bash
curl -X GET http://localhost:8000/api/ai/cache/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**：
```json
{
  "success": true,
  "stats": {
    "hits": 15,
    "misses": 5,
    "sets": 5,
    "errors": 0,
    "total_requests": 20,
    "hit_rate": "75.00%"
  }
}
```

---

### 3. 清除缓存

```bash
curl -X DELETE http://localhost:8000/api/ai/cache \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔄 缓存降级流程

系统启动时的自动选择流程：

```
启动服务
    ↓
检查 REDIS_URL 环境变量
    ↓
是否配置？
    ├─ 是 → 尝试连接 Redis
    │         ↓
    │      连接成功？
    │         ├─ 是 → 使用 Redis 缓存 ✅
    │         └─ 否 → 降级到内存缓存 ⚠️
    │
    └─ 否 → 使用内存缓存 ℹ️
```

---

## 🔁 重试机制说明

AI API 调用失败时的重试流程：

```
调用 AI API
    ↓
成功？
    ├─ 是 → 返回结果 ✅
    └─ 否 → 重试 1（等待 2 秒）
              ↓
          成功？
              ├─ 是 → 返回结果 ✅
              └─ 否 → 重试 2（等待 4 秒）
                        ↓
                    成功？
                        ├─ 是 → 返回结果 ✅
                        └─ 否 → 重试 3（等待 8 秒）
                                  ↓
                              成功？
                                  ├─ 是 → 返回结果 ✅
                                  └─ 否 → 抛出异常 ❌
```

**重试参数**：
- 最大重试次数：3 次
- 退避策略：指数退避（2ⁿ 秒）
- 单次超时：30 秒
- 总耗时：最多约 75 秒

---

## 📈 性能对比

| 指标 | 内存缓存 | Redis 缓存 |
|------|---------|-----------|
| 读取速度 | ~0.001ms | ~1ms |
| 写入速度 | ~0.001ms | ~1ms |
| 持久化 | ❌ 重启丢失 | ✅ 持久保存 |
| 分布式 | ❌ 单机 | ✅ 多实例共享 |
| 内存占用 | 进程内存 | 独立进程 |
| 适用场景 | 开发测试 | 生产环境 |

---

## 🧪 测试降级功能

### 测试 1：从 Redis 降级到内存

```bash
# 1. 启动服务（配置了 REDIS_URL）
python -m uvicorn app.main:app --reload

# 2. 观察日志
# ✅ 成功连接到 Redis: redis://localhost:6379/0
# ✅ 缓存服务已启动，使用 Redis 后端

# 3. 停止 Redis
docker stop yueen-redis

# 4. 重启服务
# ⚠️ Redis 不可用，降级到内存缓存
# ℹ️ 缓存服务已启动，使用内存缓存后端（降级模式）
```

---

### 测试 2：从模拟生成切换到真实 AI

```bash
# 1. 不配置 OPENAI_API_KEY，启动服务
python -m uvicorn app.main:app --reload

# 2. 调用生成 API
# 返回模拟内容：【这是 AI 生成的模拟内容】

# 3. 配置 .env 添加 OPENAI_API_KEY

# 4. 重启服务
# ✅ AI 服务已启动，使用模型: gpt-4

# 5. 再次调用
# 返回真实 AI 生成的内容
```

---

## 🐛 常见问题

### Q1: Redis 连接失败怎么办？

**现象**：
```
Redis 不可用，降级到内存缓存: Connection refused
```

**解决**：
1. 检查 Redis 是否启动：`docker ps` 或 `redis-cli ping`
2. 检查 REDIS_URL 配置是否正确
3. 检查防火墙是否阻止端口 6379

**临时方案**：
系统已自动降级到内存缓存，可以正常使用

---

### Q2: OpenAI API 调用失败？

**现象**：
```
AI 生成失败: RateLimitError
```

**解决**：
1. 检查 API Key 是否正确
2. 检查账户余额
3. 检查是否超过速率限制

**临时方案**：
注释掉 `.env` 中的 `OPENAI_API_KEY`，使用模拟生成

---

### Q3: 缓存命中率低？

**现象**：
```json
{
  "hit_rate": "10.00%"
}
```

**原因**：
- 数据变化频繁
- 缓存 TTL 太短
- 请求参数每次都不同

**优化**：
1. 增加缓存 TTL（在 `registry.yaml` 中配置）
2. 标准化输入数据
3. 使用更稳定的数据源

---

## 📚 架构说明

### 缓存服务架构

```
CacheService (统一接口)
    ↓
CacheBackend (抽象基类)
    ↓
├─ RedisCacheBackend (Redis 实现)
└─ MemoryCacheBackend (内存实现)
```

### AI 服务架构

```
AIService
    ↓
├─ generate() (生成内容)
│     ↓
│   ├─ _call_openai_with_retry() (真实 API)
│   └─ _mock_generate() (模拟生成)
└─ is_available() (检查可用性)
```

---

## 🔒 安全建议

1. **生产环境必须使用 Redis**
   - 避免内存缓存导致的数据丢失
   - 支持多实例部署

2. **保护 API Key**
   - 不要提交到 Git
   - 使用环境变量或密钥管理系统

3. **设置合理的缓存 TTL**
   - 避免过期数据
   - 平衡性能和时效性

4. **监控缓存性能**
   - 定期检查 `/api/ai/cache/stats`
   - 设置告警阈值

---

## 🎯 下一步优化

1. [ ] 添加 Redis Sentinel 支持（高可用）
2. [ ] 实现缓存预热机制
3. [ ] 添加分布式锁（防止缓存击穿）
4. [ ] 支持多级缓存（本地 + Redis）
5. [ ] 添加 Prometheus 指标导出

---

## 📞 技术支持

- 查看日志：`tail -f logs/app.log`
- 监控 Redis：`redis-cli monitor`
- API 文档：http://localhost:8000/docs

---

**开发时间**：2025-11-04
**开发者**：Yang Kaidi
**AI 助手**：Claude Code

🤖 Generated with [Claude Code](https://claude.com/claude-code)
