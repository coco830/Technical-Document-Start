# 开发指南

## 项目结构

```
悦恩人机共写平台/
├── frontend/          # Next.js前端项目
│   ├── src/
│   │   ├── app/      # App Router页面
│   │   ├── components/  # 可复用组件
│   │   ├── lib/      # 工具函数
│   │   ├── hooks/    # 自定义Hooks
│   │   ├── store/    # 状态管理
│   │   ├── types/    # TypeScript类型定义
│   │   └── utils/    # 工具函数
│   ├── public/       # 静态资源
│   └── package.json
├── backend/           # FastAPI后端项目
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── core/     # 核心配置
│   │   ├── models/   # 数据模型
│   │   ├── schemas/  # Pydantic模式
│   │   ├── services/ # 业务逻辑
│   │   └── utils/    # 工具函数
│   ├── alembic/      # 数据库迁移
│   └── requirements.txt
├── docs/              # 项目文档
├── README.md          # 项目说明
└── .gitignore         # Git忽略文件
```

## 开发环境搭建

### 前端环境

1. 安装Node.js 18+
2. 进入frontend目录
3. 安装依赖：
   ```bash
   npm install
   ```
4. 复制环境配置：
   ```bash
   cp .env.local.example .env.local
   ```
5. 启动开发服务器：
   ```bash
   npm run dev
   ```

### 后端环境

1. 安装Python 3.9+
2. 进入backend目录
3. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
5. 复制环境配置：
   ```bash
   cp .env.example .env
   ```
6. 启动开发服务器：
   ```bash
   uvicorn main:app --reload
   ```

## 开发规范

### 代码风格

#### 前端

- 使用TypeScript进行类型检查
- 使用ESLint进行代码检查
- 使用Prettier进行代码格式化
- 组件命名使用PascalCase
- 文件命名使用kebab-case
- 常量使用UPPER_SNAKE_CASE

#### 后端

- 遵循PEP 8代码规范
- 使用Black进行代码格式化
- 使用isort进行导入排序
- 使用flake8进行代码检查
- 函数和变量使用snake_case
- 类名使用PascalCase

### Git提交规范

使用Conventional Commits规范：

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加用户登录功能
fix: 修复文档保存bug
docs: 更新API文档
```

### 分支管理

- `main`: 主分支，用于生产环境
- `develop`: 开发分支，用于集成新功能
- `feature/*`: 功能分支，用于开发新功能
- `hotfix/*`: 热修复分支，用于紧急修复

## 开发流程

1. 从develop分支创建功能分支
2. 在功能分支上进行开发
3. 提交代码并推送到远程仓库
4. 创建Pull Request到develop分支
5. 代码审查通过后合并
6. 定期将develop分支合并到main分支

## 测试

### 前端测试

```bash
# 运行单元测试
npm test

# 运行端到端测试
npm run test:e2e

# 生成测试覆盖率报告
npm run test:coverage
```

### 后端测试

```bash
# 运行单元测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 生成测试覆盖率报告
pytest --cov=app tests/
```

## 部署

### 前端部署

1. 构建生产版本：
   ```bash
   npm run build
   ```
2. 部署到静态文件服务器

### 后端部署

1. 安装生产依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 运行数据库迁移：
   ```bash
   alembic upgrade head
   ```
3. 启动生产服务器：
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 常见问题

### 前端

1. **依赖安装失败**
   - 清除npm缓存：`npm cache clean --force`
   - 删除node_modules和package-lock.json后重新安装

2. **TypeScript类型错误**
   - 检查tsconfig.json配置
   - 确保所有依赖都已正确安装

### 后端

1. **依赖安装失败**
   - 使用虚拟环境
   - 检查Python版本兼容性

2. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接字符串配置

## 联系方式

如有问题，请联系开发团队或提交Issue。