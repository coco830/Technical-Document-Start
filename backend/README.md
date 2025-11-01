# 悦恩人机共写平台后端

## 项目概述

悦恩人机共写平台后端基于FastAPI框架构建，提供环保应急预案和环评报告的AI辅助写作功能。

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL (使用SQLAlchemy ORM)
- **数据库迁移**: Alembic
- **认证**: JWT (JSON Web Tokens)
- **密码哈希**: bcrypt
- **测试**: pytest
- **代码格式化**: black, isort
- **代码检查**: flake8

## 项目结构

```
backend/
├── app/
│   ├── api/                    # API路由
│   │   └── api_v1/
│   │       ├── endpoints/     # API端点
│   │       └── api.py        # API路由聚合
│   ├── core/                   # 核心功能
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   ├── security.py       # 安全相关
│   │   ├── deps.py           # 依赖注入
│   │   ├── exceptions.py     # 异常处理
│   │   └── middleware.py     # 中间件
│   ├── models/                  # 数据库模型
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── project.py
│   │   ├── document.py
│   │   ├── ai_generation.py
│   │   ├── document_export.py
│   │   └── __init__.py
│   ├── schemas/                 # Pydantic模式
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── project.py
│   │   ├── document.py
│   │   ├── ai_generation.py
│   │   ├── document_export.py
│   │   └── __init__.py
│   ├── services/                # 业务逻辑层
│   │   ├── base.py
│   │   └── user.py
│   └── utils/                   # 工具函数
│       ├── datetime.py
│       ├── file.py
│       ├── email.py
│       └── captcha.py
├── alembic/                     # 数据库迁移
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── tests/                       # 测试
│   ├── conftest.py
│   └── utils.py
├── conftest.py                  # 测试配置
├── requirements.txt              # 依赖包
└── main.py                     # 应用入口
```

## 安装和运行

### 1. 环境准备

确保已安装以下软件：
- Python 3.8+
- MySQL 5.7+ 或 MariaDB 10.2+

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下变量：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT密钥
- `SMTP_*`: 邮件配置（可选）
- `OPENAI_API_KEY` 或 `ZHIPUAI_API_KEY`: AI服务配置（可选）

### 5. 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head
```

### 6. 运行应用

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API文档

启动应用后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 代码规范

### 代码格式化

```bash
# 格式化代码
black .

# 排序导入
isort .
```

### 代码检查

```bash
# 检查代码风格
flake8 app/
```

## 部署

### Docker部署

1. 构建镜像：
```bash
docker build -t ai-writing-platform .
```

2. 运行容器：
```bash
docker run -p 8000:8000 --env-file .env ai-writing-platform
```

### 传统部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量

3. 运行数据库迁移：
```bash
alembic upgrade head
```

4. 启动应用：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 开发指南

### 添加新的API端点

1. 在 `app/schemas/` 中定义请求/响应模式
2. 在 `app/models/` 中定义数据库模型（如需要）
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/api/api_v1/endpoints/` 中创建端点
5. 在 `app/api/api_v1/api.py` 中注册路由

### 数据库模型变更

1. 修改模型文件
2. 生成迁移：`alembic revision --autogenerate -m "描述"`
3. 应用迁移：`alembic upgrade head`

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/新功能`
3. 提交更改：`git commit -m "添加新功能"`
4. 推送分支：`git push origin feature/新功能`
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。