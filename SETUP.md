# 🚀 项目环境配置指南

## 系统要求

- **操作系统**: Ubuntu 22.04 / WSL2
- **Node.js**: 18+
- **Python**: 3.10+
- **包管理器**: npm/pnpm (前端), pip (后端)

## 环境配置步骤

### 1. 安装系统依赖

```bash
# 安装Python pip和venv
sudo apt update
sudo apt install python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
node --version
npm --version
```

### 2. 后端环境配置

#### 方法一：使用虚拟环境（推荐）

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 方法二：直接安装（不推荐）

```bash
cd backend
pip3 install --user -r requirements.txt
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端环境配置

```bash
cd frontend

# 安装依赖
npm install
# 或使用pnpm（更快）
pnpm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 常见问题

### Q: 提示 "No module named pip"

**A**: 需要安装pip模块：
```bash
sudo apt install python3-pip
```

### Q: 虚拟环境创建失败

**A**: 需要安装python3-venv：
```bash
sudo apt install python3.12-venv  # 根据你的Python版本调整
```

### Q: npm install 速度慢

**A**: 可以使用淘宝镜像或pnpm：
```bash
npm config set registry https://registry.npmmirror.com
# 或安装pnpm
npm install -g pnpm
```

### Q: CORS错误

**A**: 确保后端的CORS配置包含前端地址（已在main.py中配置）

## 开发模式运行

### 同时启动前后端（推荐使用两个终端）

**终端1 - 后端**:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**终端2 - 前端**:
```bash
cd frontend
npm run dev
```

## 生产环境部署

### 后端部署

```bash
# 使用gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署

```bash
# 构建生产版本
npm run build

# dist目录包含静态文件，可部署到任何静态服务器
```

## 下一步

完成环境配置后，请查看 [README.md](./README.md) 了解项目功能和开发计划。
