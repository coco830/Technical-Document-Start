# API 文档

## 概述

悦恩人机共写平台API文档，提供完整的接口说明和使用示例。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 接口列表

### 认证模块 (/auth)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /auth/login | 用户登录 |
| POST | /auth/register | 用户注册 |
| POST | /auth/logout | 用户登出 |
| GET | /auth/me | 获取当前用户信息 |

### 用户模块 (/users)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /users/ | 获取用户列表 |
| GET | /users/{user_id} | 获取用户详情 |
| PUT | /users/{user_id} | 更新用户信息 |
| DELETE | /users/{user_id} | 删除用户 |

### 项目模块 (/projects)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /projects/ | 获取项目列表 |
| POST | /projects/ | 创建新项目 |
| GET | /projects/{project_id} | 获取项目详情 |
| PUT | /projects/{project_id} | 更新项目信息 |
| DELETE | /projects/{project_id} | 删除项目 |

### 文档模块 (/documents)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /documents/ | 获取文档列表 |
| POST | /documents/ | 创建新文档 |
| GET | /documents/{document_id} | 获取文档详情 |
| PUT | /documents/{document_id} | 更新文档内容 |
| DELETE | /documents/{document_id} | 删除文档 |
| POST | /documents/{document_id}/generate | AI生成文档内容 |
| POST | /documents/{document_id}/export | 导出文档 |

## 数据模型

### 用户模型

```json
{
  "id": 1,
  "username": "user@example.com",
  "full_name": "用户姓名",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 项目模型

```json
{
  "id": 1,
  "name": "项目名称",
  "description": "项目描述",
  "status": "draft",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 文档模型

```json
{
  "id": 1,
  "title": "文档标题",
  "content": "文档内容",
  "type": "emergency_plan",
  "status": "draft",
  "project_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 错误处理

所有API错误都会返回统一的错误格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

常见错误码：

- `400`: 请求参数错误
- `401`: 未授权访问
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误