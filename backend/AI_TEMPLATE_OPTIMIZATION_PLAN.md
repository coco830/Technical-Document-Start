# AI 模板生成系统 - 优化建议与改进方案

版本：v1.0
日期：2025-11-04
作者：AI Assistant

---

## 一、已完成功能总结

### ✅ 核心功能
1. **模板管理系统**
   - YAML 配置文件注册表
   - 模板动态加载与缓存
   - 多模板支持（当前：应急预案模板）

2. **安全防护机制**
   - Jinja2 沙箱模式
   - 输入验证（类型、字段名、危险关键字）
   - 输出清理（XSS 防护）
   - 文件大小限制
   - 请求限流

3. **API 接口**
   - `GET /api/ai/templates` - 列出所有模板
   - `GET /api/ai/templates/{id}/schema` - 获取模板结构
   - `POST /api/ai/generate` - 生成内容
   - `DELETE /api/ai/cache` - 清除缓存

4. **缓存机制**
   - 内存缓存
   - MD5 哈希键
   - TTL 过期（1小时）

---

## 二、短期优化建议（1-2周）

### 🔧 优先级 P0：生产环境就绪

#### 1. 接入真实 AI 模型
**目标**：替换模拟生成，接入 OpenAI/Claude/通义千问等

**实施步骤**：
```python
# 1. 安装 SDK
# requirements.txt
openai==1.12.0  # 或 anthropic==0.18.0

# 2. 配置环境变量
# .env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4-turbo-preview

# 3. 实现 AI 服务
# backend/app/services/ai_service.py
from openai import OpenAI
import os

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )

    def generate(self, prompt: str, config: dict) -> str:
        response = self.client.chat.completions.create(
            model=config.get("model", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000)
        )
        return response.choices[0].message.content

# 4. 在 ai_generate.py 中集成
from ..services.ai_service import AIService

ai_service = AIService()
generated_content = ai_service.generate(prompt, ai_config)
```

**预估工作量**：4-6 小时

---

#### 2. 集成 Redis 缓存
**目标**：替换内存缓存，支持分布式部署

**实施步骤**：
```python
# 1. 安装依赖
# requirements.txt
redis==5.0.1

# 2. 配置环境变量
# .env
REDIS_URL=redis://localhost:6379/0

# 3. 实现 Redis 缓存服务
# backend/app/services/cache_service.py
import redis
import json
from typing import Optional

class CacheService:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)

    def get(self, key: str) -> Optional[dict]:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: dict, ttl: int = 3600):
        self.client.setex(
            key,
            ttl,
            json.dumps(value, ensure_ascii=False)
        )

    def delete(self, key: str):
        self.client.delete(key)

    def clear_pattern(self, pattern: str):
        """清除匹配模式的所有键"""
        for key in self.client.scan_iter(match=pattern):
            self.client.delete(key)

# 4. 在 ai_generate.py 中使用
cache_service = CacheService(os.getenv("REDIS_URL"))

# 检查缓存
cached = cache_service.get(cache_key)
if cached:
    return GenerationResponse(success=True, content=cached["content"], cached=True)

# 保存缓存
cache_service.set(cache_key, {"content": generated_content}, ttl)
```

**预估工作量**：3-4 小时

---

#### 3. 添加重试机制
**目标**：提高 AI API 调用稳定性

**实施步骤**：
```python
# 1. 安装依赖
# requirements.txt
tenacity==8.2.3

# 2. 实现重试装饰器
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAIError

class AIService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((OpenAIError, TimeoutError)),
        reraise=True
    )
    def generate(self, prompt: str, config: dict) -> str:
        try:
            response = self.client.chat.completions.create(
                model=config.get("model", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2000),
                timeout=30  # 30 秒超时
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI 生成失败: {e}")
            raise
```

**预估工作量**：2 小时

---

### 🔧 优先级 P1：功能增强

#### 4. 实现流式响应
**目标**：提升用户体验，实时显示生成内容

```python
from fastapi.responses import StreamingResponse
from openai import OpenAI

@router.post("/api/ai/generate/stream")
async def stream_generate(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """流式生成内容"""

    async def generate_stream():
        # 渲染 prompt
        prompt = template_loader.render_prompt(...)

        # 流式调用 OpenAI
        stream = ai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

**预估工作量**：4 小时

---

#### 5. 批量生成接口
**目标**：支持一次生成多个章节

```python
@router.post("/api/ai/generate/batch")
async def batch_generate(
    requests: List[GenerationRequest],
    current_user: User = Depends(get_current_user)
):
    """批量生成内容"""
    import asyncio

    async def generate_single(req: GenerationRequest):
        try:
            return await generate_content(req, current_user)
        except Exception as e:
            return GenerationResponse(success=False, error=str(e))

    # 并发生成
    results = await asyncio.gather(
        *[generate_single(req) for req in requests],
        return_exceptions=False
    )

    return {
        "success": True,
        "results": results,
        "total": len(requests),
        "succeeded": sum(1 for r in results if r.success)
    }
```

**预估工作量**：3 小时

---

## 三、中期优化建议（1个月）

### 📊 日志与监控

#### 6. 完善审计日志
```python
import logging
from datetime import datetime

# 创建审计日志记录器
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# 文件处理器
handler = logging.FileHandler("logs/audit.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(message)s'
))
audit_logger.addHandler(handler)

# 记录审计事件
def log_ai_generation(user_id, template_id, section_id, success, duration):
    audit_logger.info(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "event": "ai_generate",
        "user_id": user_id,
        "template_id": template_id,
        "section_id": section_id,
        "success": success,
        "duration_ms": duration,
        "ip_address": request.client.host
    }, ensure_ascii=False))
```

---

#### 7. Prometheus 监控指标
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI generation requests',
    ['template_id', 'section_id', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request duration in seconds',
    ['template_id']
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate',
    ['template_id']
)

# 使用指标
@router.post("/api/ai/generate")
async def generate_content(...):
    start_time = time.time()

    try:
        # ... 生成逻辑 ...
        ai_requests_total.labels(
            template_id=template_id,
            section_id=section_id,
            status="success"
        ).inc()
    except Exception as e:
        ai_requests_total.labels(
            template_id=template_id,
            section_id=section_id,
            status="error"
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        ai_request_duration.labels(template_id=template_id).observe(duration)
```

---

### 🔐 安全增强

#### 8. RBAC 权限控制
```python
# 定义权限枚举
class Permission(str, Enum):
    AI_GENERATE = "ai:generate"
    AI_BATCH_GENERATE = "ai:batch_generate"
    AI_ADMIN = "ai:admin"

# 权限检查装饰器
def require_permission(permission: Permission):
    def decorator(func):
        async def wrapper(*args, current_user: User, **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail="权限不足"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用权限控制
@router.post("/api/ai/generate")
@require_permission(Permission.AI_GENERATE)
async def generate_content(...):
    pass
```

---

#### 9. 内容审核机制
```python
# 敏感词过滤
SENSITIVE_WORDS = ["敏感词1", "敏感词2", ...]

def content_moderation(text: str) -> Tuple[bool, str]:
    """内容审核"""
    # 1. 敏感词检测
    for word in SENSITIVE_WORDS:
        if word in text:
            return False, f"内容包含敏感词: {word}"

    # 2. 长度检查
    if len(text) > 100000:
        return False, "内容过长"

    # 3. 调用第三方审核 API（可选）
    # result = moderation_api.check(text)

    return True, ""

# 在生成后应用
generated_content = ai_service.generate(prompt, config)
is_safe, reason = content_moderation(generated_content)
if not is_safe:
    raise HTTPException(400, detail=f"内容审核失败: {reason}")
```

---

## 四、长期优化建议（3-6个月）

### 🚀 性能优化

#### 10. 数据库持久化模板
```python
# 将模板存储到数据库
from sqlalchemy import Column, String, JSON, Boolean

class TemplateModel(Base):
    __tablename__ = "ai_templates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    schema = Column(JSON)  # 模板结构
    prompt_template = Column(String)  # Jinja2 模板
    enabled = Column(Boolean, default=True)
    version = Column(String)
```

---

#### 11. AI 模型微调
```python
# 使用企业数据微调模型
# 1. 收集高质量生成样本
# 2. 构建训练数据集
# 3. 使用 OpenAI Fine-tuning API

import openai

# 上传训练数据
openai.File.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# 创建微调任务
openai.FineTuningJob.create(
    training_file="file-xxx",
    model="gpt-4"
)

# 使用微调模型
response = openai.ChatCompletion.create(
    model="ft:gpt-4:org-xxx",
    messages=[...]
)
```

---

#### 12. 多模型路由策略
```python
class ModelRouter:
    """智能模型路由"""

    def select_model(self, template_id: str, section_id: str, data: dict) -> str:
        """根据任务复杂度选择模型"""

        # 简单任务 -> 使用快速低成本模型
        if self._is_simple_task(template_id, section_id):
            return "gpt-3.5-turbo"

        # 复杂任务 -> 使用高质量模型
        if self._is_complex_task(template_id, section_id):
            return "gpt-4-turbo"

        # 默认模型
        return "gpt-4"

    def _is_simple_task(self, template_id, section_id) -> bool:
        # 判断任务复杂度
        simple_sections = ["1", "7", "8"]  # 总则、附录等
        return section_id in simple_sections
```

---

## 五、前端集成建议

### 🎨 前端对接 API

#### 1. API 客户端封装
```typescript
// frontend/src/services/aiService.ts
import axios from 'axios';

interface GenerationRequest {
  template_id: string;
  section_id: string;
  data: Record<string, any>;
}

interface GenerationResponse {
  success: boolean;
  content?: string;
  section_title?: string;
  cached: boolean;
  error?: string;
}

export class AIService {
  private baseURL = '/api/ai';

  async listTemplates() {
    const response = await axios.get(`${this.baseURL}/templates`);
    return response.data;
  }

  async getTemplateSchema(templateId: string) {
    const response = await axios.get(`${this.baseURL}/templates/${templateId}/schema`);
    return response.data;
  }

  async generate(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await axios.post(`${this.baseURL}/generate`, request);
    return response.data;
  }

  async streamGenerate(request: GenerationRequest, onChunk: (chunk: string) => void) {
    const response = await fetch(`${this.baseURL}/generate/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          onChunk(data.content);
        }
      }
    }
  }
}
```

---

#### 2. React 组件示例
```tsx
// frontend/src/components/AIGenerator.tsx
import { useState } from 'react';
import { AIService } from '../services/aiService';

export function AIGenerator({ documentId, sectionId }) {
  const [generating, setGenerating] = useState(false);
  const [content, setContent] = useState('');
  const aiService = new AIService();

  const handleGenerate = async () => {
    setGenerating(true);
    setContent('');

    try {
      // 准备数据
      const data = {
        enterprise_info: {
          enterprise_name: "示例企业",
          industry_type: "化工制造",
          // ...
        }
      };

      // 流式生成
      await aiService.streamGenerate(
        {
          template_id: 'emergency_plan',
          section_id: sectionId,
          data
        },
        (chunk) => {
          setContent(prev => prev + chunk);
        }
      );
    } catch (error) {
      console.error('生成失败:', error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={generating}>
        {generating ? 'AI 生成中...' : '✨ AI 生成'}
      </button>

      {content && (
        <div className="generated-content">
          {content}
        </div>
      )}
    </div>
  );
}
```

---

## 六、测试建议

### 🧪 单元测试
```python
# backend/tests/test_ai_generate.py
import pytest
from app.prompts.template_loader import TemplateLoader
from app.prompts.template_validator import TemplateValidator

def test_template_loader():
    loader = TemplateLoader()
    templates = loader.list_templates()
    assert len(templates) > 0
    assert templates[0]["id"] == "emergency_plan"

def test_template_validator():
    validator = TemplateValidator()

    # 测试正常数据
    data = {"enterprise_info": {"name": "测试企业"}}
    is_valid, errors = validator.validate_template_data(data)
    assert is_valid

    # 测试危险数据
    malicious_data = {"field": "{{__import__('os').system('ls')}}"}
    is_valid, errors = validator.validate_template_data(malicious_data)
    assert not is_valid
    assert len(errors) > 0

def test_ai_generate_api(client, auth_headers):
    response = client.post(
        "/api/ai/generate",
        json={
            "template_id": "emergency_plan",
            "section_id": "1",
            "data": {"enterprise_info": {"name": "测试"}}
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
```

---

## 七、文档建议

### 📚 API 文档
在 FastAPI 自动生成文档基础上，添加详细说明：

```python
@router.post(
    "/api/ai/generate",
    response_model=GenerationResponse,
    summary="生成 AI 内容",
    description="""
    根据模板和数据生成 AI 内容

    **使用步骤：**
    1. 调用 /api/ai/templates 获取可用模板列表
    2. 调用 /api/ai/templates/{id}/schema 获取模板结构
    3. 准备数据并调用本接口生成内容

    **限流说明：**
    - 1分钟内最多 10 次请求
    - 1小时内最多 100 次请求

    **缓存机制：**
    - 相同输入会返回缓存结果
    - 缓存有效期 1 小时
    """,
    responses={
        200: {"description": "生成成功"},
        400: {"description": "数据验证失败"},
        429: {"description": "请求过于频繁"},
        500: {"description": "服务器错误"}
    }
)
async def generate_content(...):
    pass
```

---

## 八、部署建议

### 🚢 Docker 化部署

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/yueen
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=yueen
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  redis_data:
  db_data:
```

---

## 九、成本优化

### 💰 AI API 成本控制

1. **模型选择策略**
   - 简单任务：gpt-3.5-turbo ($0.001/1K tokens)
   - 复杂任务：gpt-4-turbo ($0.01/1K tokens)

2. **缓存优化**
   - 提高缓存命中率，减少重复请求
   - 缓存热门章节内容

3. **批量处理**
   - 合并多个小请求为一个大请求
   - 减少 API 调用次数

4. **Token 控制**
   - 限制 max_tokens 避免过长输出
   - 优化 Prompt 长度

---

## 十、总结

### ✅ 立即可做（本周）
1. 接入真实 AI 模型
2. 集成 Redis 缓存
3. 添加重试机制
4. 完善错误日志

### 🔜 近期计划（本月）
1. 实现流式响应
2. 批量生成接口
3. 审计日志完善
4. Prometheus 监控

### 🎯 长期规划（3-6个月）
1. 模型微调
2. 多模板扩展
3. 性能优化
4. 成本优化

当前系统已具备生产环境基础，完成上述优化后可以安全、高效地投入使用。
