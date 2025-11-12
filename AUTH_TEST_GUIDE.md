# 认证流程测试指南

## 概述

本文档描述了如何测试悦恩平台的用户认证流程，包括注册、登录、token验证和token刷新功能。

## 测试前准备

1. 确保后端服务正在运行：
   ```bash
   cd backend
   source .venv/bin/activate  # 如果使用虚拟环境
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. 确保前端服务正在运行：
   ```bash
   cd frontend
   npm run dev
   ```

## 自动化测试

运行后端测试脚本：
```bash
cd backend
python test_auth.py
```

该脚本将测试以下功能：
- 用户注册
- 用户登录
- Token验证
- Token刷新

## 手动测试

### 1. 用户注册测试

1. 访问 `http://localhost:3000/register`
2. 填写注册表单：
   - 姓名：测试用户
   - 邮箱：test@example.com
   - 密码：test123456
   - 确认密码：test123456
   - 勾选服务条款
3. 点击"注册账号"按钮
4. 预期结果：显示注册成功消息，并跳转到登录页面

### 2. 用户登录测试

1. 访问 `http://localhost:3000/login`
2. 使用注册的账号登录：
   - 邮箱：test@example.com
   - 密码：test123456
3. 点击"登录"按钮
4. 预期结果：登录成功，跳转到项目页面

### 3. 认证状态持久化测试

1. 登录成功后，刷新页面（F5）
2. 预期结果：仍然保持登录状态，不会跳转到登录页面

### 4. 受保护路由测试

1. 在未登录状态下，直接访问 `http://localhost:3000/projects`
2. 预期结果：自动跳转到登录页面

### 5. Token自动刷新测试

1. 登录成功后，等待token过期（默认30分钟）
2. 或者修改后端环境变量，将token过期时间设置为较短时间（如1分钟）
3. 在token过期后，尝试访问需要认证的API
4. 预期结果：应用自动刷新token，用户无感知

## API测试

### 注册API

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试用户",
    "email": "test@example.com",
    "password": "test123456",
    "confirm_password": "test123456",
    "accept_terms": true
  }'
```

### 登录API

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

### Token验证API

```bash
curl -X GET "http://localhost:8000/api/auth/verify" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Token刷新API

```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 常见问题

1. **注册失败：邮箱已被注册**
   - 解决方案：使用不同的邮箱地址，或删除现有用户

2. **登录失败：邮箱或密码错误**
   - 解决方案：检查输入的邮箱和密码是否正确

3. **Token验证失败**
   - 解决方案：检查token是否过期，或重新登录获取新token

4. **前端页面无法访问后端API**
   - 解决方案：检查后端服务是否正在运行，以及CORS配置是否正确

## 测试结果记录

请记录测试结果，包括：
- 测试日期
- 测试环境
- 测试结果（通过/失败）
- 发现的问题
- 解决方案

## 注意事项

1. 测试完成后，建议删除测试用户数据
2. 不要在生产环境中使用测试账号
3. 确保测试环境的数据库可以随时重置