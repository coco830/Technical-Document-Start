# 悦恩人机共写平台 - API接口规范文档

## 目录

1. [概述](#概述)
2. [基础信息](#基础信息)
3. [认证与授权](#认证与授权)
4. [通用响应格式](#通用响应格式)
5. [错误处理](#错误处理)
6. [接口分类](#接口分类)
   - [用户认证接口](#用户认证接口)
   - [用户管理接口](#用户管理接口)
   - [企业管理接口](#企业管理接口)
   - [项目管理接口](#项目管理接口)
   - [文档管理接口](#文档管理接口)
   - [AI生成接口](#ai生成接口)
   - [文档导出接口](#文档导出接口)
7. [接口版本控制](#接口版本控制)
8. [分页和过滤](#分页和过滤)
9. [安全策略](#安全策略)
10. [接口限流](#接口限流)

## 概述

本文档描述了悦恩人机共写平台的完整API接口规范，包括所有数据模型的CRUD操作、用户认证和授权、AI文案生成、文档导出和版本管理等功能。API遵循RESTful设计原则，使用JSON格式进行数据交换，支持JWT令牌认证。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **OpenAPI规范**: `http://localhost:8000/openapi.json`

## 认证与授权

### JWT令牌认证

所有需要认证的接口都需要在请求头中包含有效的JWT令牌：

```
Authorization: Bearer <access_token>
```

### 令牌获取

通过用户登录接口获取JWT令牌，令牌有效期为8天（可配置）。

### 权限控制

系统采用基于角色的访问控制（RBAC）：

- **user**: 普通用户，可以访问自己的资源
- **admin**: 管理员，可以访问所有资源

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 列表响应

```json
{
  "success": true,
  "data": {
    "items": [
      // 数据项列表
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  },
  "message": "获取成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 分页参数

所有列表接口支持以下分页参数：

- `page`: 页码，从1开始，默认为1
- `size`: 每页大小，默认为20，最大为100

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {
      // 详细错误信息
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 常见错误码

| 状态码 | 错误码 | 描述 |
|--------|--------|------|
| 400 | INVALID_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未授权访问 |
| 403 | FORBIDDEN | 权限不足 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

## 接口分类

### 用户认证接口

#### 用户登录

**端点**: `POST /api/v1/auth/login`

**描述**: 用户登录获取访问令牌

**请求体**:
```json
{
  "username": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 691200,
    "user": {
      "id": 1,
      "username": "user@example.com",
      "full_name": "用户姓名",
      "avatar_url": "https://example.com/avatar.jpg",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    }
  },
  "message": "登录成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

#### 用户注册

**端点**: `POST /api/v1/auth/register`

**描述**: 新用户注册

**请求体**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "新用户",
  "phone": "13800138000"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "新用户",
    "phone": "13800138000",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "注册成功"
}
```

#### 用户登出

**端点**: `POST /api/v1/auth/logout`

**描述**: 用户登出，使令牌失效

**认证**: 需要JWT令牌

**响应**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

#### 获取当前用户信息

**端点**: `GET /api/v1/auth/me`

**描述**: 获取当前登录用户的详细信息

**认证**: 需要JWT令牌

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "full_name": "用户姓名",
    "phone": "13800138000",
    "avatar_url": "https://example.com/avatar.jpg",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 刷新令牌

**端点**: `POST /api/v1/auth/refresh`

**描述**: 刷新访问令牌

**认证**: 需要有效的JWT令牌

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 691200
  }
}
```

#### 修改密码

**端点**: `PUT /api/v1/auth/password`

**描述**: 修改当前用户密码

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**响应**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

### 用户管理接口

#### 获取用户列表

**端点**: `GET /api/v1/users/`

**描述**: 获取用户列表（管理员权限）

**认证**: 需要管理员权限

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `keyword`: 搜索关键词（用户名、邮箱、全名）
- `role`: 用户角色筛选
- `is_active`: 是否激活筛选
- `is_verified`: 是否验证筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "user@example.com",
        "email": "user@example.com",
        "full_name": "用户姓名",
        "role": "user",
        "is_active": true,
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login_at": "2024-01-01T12:00:00Z",
        "projects_count": 5,
        "documents_count": 12
      }
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

#### 获取用户详情

**端点**: `GET /api/v1/users/{user_id}`

**描述**: 获取指定用户的详细信息

**认证**: 需要JWT令牌（用户只能查看自己的信息，管理员可查看所有用户）

**路径参数**:
- `user_id`: 用户ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "full_name": "用户姓名",
    "phone": "13800138000",
    "avatar_url": "https://example.com/avatar.jpg",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-01T12:00:00Z",
    "projects_count": 5,
    "documents_count": 12,
    "ai_generations_count": 25
  }
}
```

#### 更新用户信息

**端点**: `PUT /api/v1/users/{user_id}`

**描述**: 更新用户信息

**认证**: 需要JWT令牌（用户只能更新自己的信息，管理员可更新所有用户）

**路径参数**:
- `user_id`: 用户ID

**请求体**:
```json
{
  "full_name": "新的用户姓名",
  "phone": "13900139000",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "full_name": "新的用户姓名",
    "phone": "13900139000",
    "avatar_url": "https://example.com/new-avatar.jpg",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "用户信息更新成功"
}
```

#### 删除用户

**端点**: `DELETE /api/v1/users/{user_id}`

**描述**: 删除用户（软删除，仅管理员可操作）

**认证**: 需要管理员权限

**路径参数**:
- `user_id`: 用户ID

**响应**:
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

#### 获取用户偏好设置

**端点**: `GET /api/v1/users/{user_id}/preferences`

**描述**: 获取用户偏好设置

**认证**: 需要JWT令牌

**路径参数**:
- `user_id`: 用户ID

**响应**:
```json
{
  "success": true,
  "data": {
    "theme": "light",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "email_notifications": true,
    "push_notifications": true,
    "auto_save": true,
    "default_document_format": "markdown",
    "default_export_format": "pdf"
  }
}
```

#### 更新用户偏好设置

**端点**: `PUT /api/v1/users/{user_id}/preferences`

**描述**: 更新用户偏好设置

**认证**: 需要JWT令牌

**路径参数**:
- `user_id`: 用户ID

**请求体**:
```json
{
  "theme": "dark",
  "language": "en-US",
  "email_notifications": false
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "theme": "dark",
    "language": "en-US",
    "timezone": "Asia/Shanghai",
    "email_notifications": false,
    "push_notifications": true,
    "auto_save": true,
    "default_document_format": "markdown",
    "default_export_format": "pdf"
  },
  "message": "偏好设置更新成功"
}
```

### 企业管理接口

#### 获取企业列表

**端点**: `GET /api/v1/companies/`

**描述**: 获取企业列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `keyword`: 搜索关键词（企业名称、法定代表人）
- `industry`: 行业筛选
- `unified_social_credit_code`: 统一社会信用代码

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "示例化工有限公司",
        "unified_social_credit_code": "91110000123456789X",
        "legal_representative": "张三",
        "contact_phone": "13800138000",
        "contact_email": "contact@example.com",
        "industry": "化工",
        "created_at": "2024-01-01T00:00:00Z",
        "projects_count": 3,
        "active_projects_count": 2,
        "completed_projects_count": 1
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  }
}
```

#### 创建企业

**端点**: `POST /api/v1/companies/`

**描述**: 创建新企业

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "name": "新企业有限公司",
  "unified_social_credit_code": "91110000987654321Y",
  "legal_representative": "李四",
  "contact_phone": "13900139000",
  "contact_email": "contact@newcompany.com",
  "address": "北京市朝阳区示例街道456号",
  "industry": "环保",
  "business_scope": "环保技术开发与服务"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "新企业有限公司",
    "unified_social_credit_code": "91110000987654321Y",
    "legal_representative": "李四",
    "contact_phone": "13900139000",
    "contact_email": "contact@newcompany.com",
    "address": "北京市朝阳区示例街道456号",
    "industry": "环保",
    "business_scope": "环保技术开发与服务",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "企业创建成功"
}
```

#### 获取企业详情

**端点**: `GET /api/v1/companies/{company_id}`

**描述**: 获取指定企业的详细信息

**认证**: 需要JWT令牌

**路径参数**:
- `company_id`: 企业ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "示例化工有限公司",
    "unified_social_credit_code": "91110000123456789X",
    "legal_representative": "张三",
    "contact_phone": "13800138000",
    "contact_email": "contact@example.com",
    "address": "北京市朝阳区示例街道123号",
    "industry": "化工",
    "business_scope": "化工产品生产与销售",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "projects_count": 3,
    "active_projects_count": 2,
    "completed_projects_count": 1,
    "documents_count": 8
  }
}
```

#### 更新企业信息

**端点**: `PUT /api/v1/companies/{company_id}`

**描述**: 更新企业信息

**认证**: 需要JWT令牌

**路径参数**:
- `company_id`: 企业ID

**请求体**:
```json
{
  "contact_phone": "13700137000",
  "contact_email": "newcontact@example.com",
  "address": "北京市朝阳区更新地址789号"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "示例化工有限公司",
    "unified_social_credit_code": "91110000123456789X",
    "legal_representative": "张三",
    "contact_phone": "13700137000",
    "contact_email": "newcontact@example.com",
    "address": "北京市朝阳区更新地址789号",
    "industry": "化工",
    "business_scope": "化工产品生产与销售",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "企业信息更新成功"
}
```

#### 删除企业

**端点**: `DELETE /api/v1/companies/{company_id}`

**描述**: 删除企业（软删除）

**认证**: 需要JWT令牌

**路径参数**:
- `company_id`: 企业ID

**响应**:
```json
{
  "success": true,
  "message": "企业删除成功"
}
```

#### 获取企业联系人列表

**端点**: `GET /api/v1/companies/{company_id}/contacts`

**描述**: 获取企业联系人列表

**认证**: 需要JWT令牌

**路径参数**:
- `company_id`: 企业ID

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `is_active`: 是否活跃筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "company_id": 1,
        "name": "王五",
        "position": "项目经理",
        "phone": "13600136000",
        "email": "wangwu@example.com",
        "department": "项目部",
        "is_primary": true,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 创建企业联系人

**端点**: `POST /api/v1/companies/{company_id}/contacts`

**描述**: 为企业添加联系人

**认证**: 需要JWT令牌

**路径参数**:
- `company_id`: 企业ID

**请求体**:
```json
{
  "name": "赵六",
  "position": "技术总监",
  "phone": "13500135000",
  "email": "zhaoliu@example.com",
  "department": "技术部",
  "is_primary": false,
  "notes": "技术负责人"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "company_id": 1,
    "name": "赵六",
    "position": "技术总监",
    "phone": "13500135000",
    "email": "zhaoliu@example.com",
    "department": "技术部",
    "is_primary": false,
    "is_active": true,
    "notes": "技术负责人",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "联系人添加成功"
}
```

### 项目管理接口

#### 获取项目列表

**端点**: `GET /api/v1/projects/`

**描述**: 获取项目列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `user_id`: 用户ID筛选（管理员可用）
- `company_id`: 企业ID筛选
- `type`: 项目类型筛选
- `status`: 项目状态筛选
- `keyword`: 搜索关键词（项目名称、描述）

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "化工企业环保应急预案",
        "type": "emergency_plan",
        "status": "draft",
        "description": "为化工企业制定的环保应急预案",
        "user_id": 1,
        "user_name": "张三",
        "company_id": 1,
        "company_name": "示例化工有限公司",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "documents_count": 3,
        "forms_count": 5,
        "progress": 25.5
      }
    ],
    "total": 30,
    "page": 1,
    "size": 20,
    "pages": 2
  }
}
```

#### 创建项目

**端点**: `POST /api/v1/projects/`

**描述**: 创建新项目

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "name": "新项目环评报告",
  "type": "environmental_assessment",
  "status": "draft",
  "description": "新项目的环境影响评价报告",
  "user_id": 1,
  "company_id": 1,
  "metadata": {
    "priority": "high",
    "deadline": "2024-06-30"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "新项目环评报告",
    "type": "environmental_assessment",
    "status": "draft",
    "description": "新项目的环境影响评价报告",
    "user_id": 1,
    "company_id": 1,
    "metadata": {
      "priority": "high",
      "deadline": "2024-06-30"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "项目创建成功"
}
```

#### 获取项目详情

**端点**: `GET /api/v1/projects/{project_id}`

**描述**: 获取指定项目的详细信息

**认证**: 需要JWT令牌

**路径参数**:
- `project_id`: 项目ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "化工企业环保应急预案",
    "type": "emergency_plan",
    "status": "draft",
    "description": "为化工企业制定的环保应急预案",
    "user_id": 1,
    "user_name": "张三",
    "company_id": 1,
    "company_name": "示例化工有限公司",
    "metadata": {
      "priority": "high",
      "deadline": "2024-06-30"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "completed_at": null,
    "documents_count": 3,
    "forms_count": 5,
    "progress": 25.5
  }
}
```

#### 更新项目信息

**端点**: `PUT /api/v1/projects/{project_id}`

**描述**: 更新项目信息

**认证**: 需要JWT令牌

**路径参数**:
- `project_id`: 项目ID

**请求体**:
```json
{
  "name": "更新后的项目名称",
  "status": "generating",
  "description": "更新后的项目描述",
  "metadata": {
    "priority": "medium",
    "deadline": "2024-07-31"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "更新后的项目名称",
    "type": "emergency_plan",
    "status": "generating",
    "description": "更新后的项目描述",
    "user_id": 1,
    "company_id": 1,
    "metadata": {
      "priority": "medium",
      "deadline": "2024-07-31"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "项目信息更新成功"
}
```

#### 删除项目

**端点**: `DELETE /api/v1/projects/{project_id}`

**描述**: 删除项目（软删除）

**认证**: 需要JWT令牌

**路径参数**:
- `project_id`: 项目ID

**响应**:
```json
{
  "success": true,
  "message": "项目删除成功"
}
```

#### 获取项目表单列表

**端点**: `GET /api/v1/projects/{project_id}/forms`

**描述**: 获取项目表单列表

**认证**: 需要JWT令牌

**路径参数**:
- `project_id`: 项目ID

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `form_type`: 表单类型筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "project_id": 1,
        "form_type": "basic_info",
        "form_data": {
          "company_name": "示例化工有限公司",
          "address": "北京市朝阳区示例街道123号"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "fields_count": 10
      }
    ],
    "total": 5,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 创建项目表单

**端点**: `POST /api/v1/projects/{project_id}/forms`

**描述**: 为项目创建表单

**认证**: 需要JWT令牌

**路径参数**:
- `project_id`: 项目ID

**请求体**:
```json
{
  "form_type": "environmental_info",
  "form_data": {
    "industry_type": "化工",
    "production_scale": "大型",
    "main_products": ["化工产品A", "化工产品B"]
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "project_id": 1,
    "form_type": "environmental_info",
    "form_data": {
      "industry_type": "化工",
      "production_scale": "大型",
      "main_products": ["化工产品A", "化工产品B"]
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "表单创建成功"
}
```

### 文档管理接口

#### 获取文档列表

**端点**: `GET /api/v1/documents/`

**描述**: 获取文档列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `project_id`: 项目ID筛选
- `status`: 文档状态筛选
- `format`: 文档格式筛选
- `keyword`: 搜索关键词（文档标题、内容）

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "环保应急预案第一章",
        "project_id": 1,
        "project_name": "化工企业环保应急预案",
        "format": "markdown",
        "status": "draft",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "versions_count": 3,
        "ai_generations_count": 5,
        "exports_count": 2
      }
    ],
    "total": 25,
    "page": 1,
    "size": 20,
    "pages": 2
  }
}
```

#### 创建文档

**端点**: `POST /api/v1/documents/`

**描述**: 创建新文档

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "title": "新文档标题",
  "content": "# 新文档内容\n\n这是文档的正文内容...",
  "format": "markdown",
  "status": "draft",
  "project_id": 1,
  "metadata": {
    "chapter": 2,
    "section": "风险评估"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "title": "新文档标题",
    "content": "# 新文档内容\n\n这是文档的正文内容...",
    "format": "markdown",
    "status": "draft",
    "project_id": 1,
    "metadata": {
      "chapter": 2,
      "section": "风险评估"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "文档创建成功"
}
```

#### 获取文档详情

**端点**: `GET /api/v1/documents/{document_id}`

**描述**: 获取指定文档的详细信息

**认证**: 需要JWT令牌

**路径参数**:
- `document_id`: 文档ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "环保应急预案第一章",
    "content": "# 环保应急预案第一章\n\n这是第一章的内容...",
    "format": "markdown",
    "status": "draft",
    "project_id": 1,
    "project_name": "化工企业环保应急预案",
    "metadata": {
      "chapter": 1,
      "section": "总则"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "versions_count": 3,
    "ai_generations_count": 5,
    "exports_count": 2
  }
}
```

#### 更新文档内容

**端点**: `PUT /api/v1/documents/{document_id}`

**描述**: 更新文档内容

**认证**: 需要JWT令牌

**路径参数**:
- `document_id`: 文档ID

**请求体**:
```json
{
  "title": "更新后的文档标题",
  "content": "# 更新后的文档内容\n\n这是更新后的正文内容...",
  "status": "reviewing",
  "metadata": {
    "chapter": 1,
    "section": "总则",
    "last_editor": "张三"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "更新后的文档标题",
    "content": "# 更新后的文档内容\n\n这是更新后的正文内容...",
    "format": "markdown",
    "status": "reviewing",
    "project_id": 1,
    "metadata": {
      "chapter": 1,
      "section": "总则",
      "last_editor": "张三"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "文档更新成功"
}
```

#### 删除文档

**端点**: `DELETE /api/v1/documents/{document_id}`

**描述**: 删除文档（软删除）

**认证**: 需要JWT令牌

**路径参数**:
- `document_id`: 文档ID

**响应**:
```json
{
  "success": true,
  "message": "文档删除成功"
}
```

#### 获取文档版本列表

**端点**: `GET /api/v1/documents/{document_id}/versions`

**描述**: 获取文档版本历史

**认证**: 需要JWT令牌

**路径参数**:
- `document_id`: 文档ID

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "document_id": 1,
        "version_number": 1,
        "content": "# 初始版本内容\n\n这是初始版本的内容...",
        "changes_summary": {
          "type": "initial",
          "description": "初始版本"
        },
        "created_by": 1,
        "created_by_name": "张三",
        "created_at": "2024-01-01T00:00:00Z"
      },
      {
        "id": 2,
        "document_id": 1,
        "version_number": 2,
        "content": "# 更新版本内容\n\n这是更新后的内容...",
        "changes_summary": {
          "type": "update",
          "description": "更新了第二章内容"
        },
        "created_by": 1,
        "created_by_name": "张三",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 3,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 创建文档版本

**端点**: `POST /api/v1/documents/{document_id}/versions`

**描述**: 创建文档新版本

**认证**: 需要JWT令牌

**路径参数**:
- `document_id`: 文档ID

**请求体**:
```json
{
  "content": "# 新版本内容\n\n这是新版本的内容...",
  "changes_summary": {
    "type": "major_update",
    "description": "重大更新，重写了第三章"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 3,
    "document_id": 1,
    "version_number": 3,
    "content": "# 新版本内容\n\n这是新版本的内容...",
    "changes_summary": {
      "type": "major_update",
      "description": "重大更新，重写了第三章"
    },
    "created_by": 1,
    "created_at": "2024-01-01T18:00:00Z"
  },
  "message": "文档版本创建成功"
}
```

### AI生成接口

#### AI生成文档内容

**端点**: `POST /api/v1/ai/generate`

**描述**: 使用AI生成文档内容

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "document_id": 1,
  "prompt": "请生成环保应急预案的应急响应部分，包括应急组织机构、应急响应程序和应急处置措施",
  "context": "这是一个化工企业的环保应急预案，主要涉及化学品泄漏应急处理",
  "section": "应急响应",
  "generation_config": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 0.9,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "document_id": 1,
    "user_id": 1,
    "status": "processing",
    "prompt": "请生成环保应急预案的应急响应部分，包括应急组织机构、应急响应程序和应急处置措施",
    "generation_config": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 0.9,
      "frequency_penalty": 0.1,
      "presence_penalty": 0.1
    },
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "AI生成任务已提交，正在处理中"
}
```

#### 获取AI生成状态

**端点**: `GET /api/v1/ai/generations/{generation_id}`

**描述**: 获取AI生成任务状态和结果

**认证**: 需要JWT令牌

**路径参数**:
- `generation_id`: 生成记录ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "document_id": 1,
    "document_title": "环保应急预案第一章",
    "user_id": 1,
    "user_name": "张三",
    "status": "completed",
    "prompt": "请生成环保应急预案的应急响应部分，包括应急组织机构、应急响应程序和应急处置措施",
    "generated_content": "# 应急响应\n\n## 应急组织机构\n\n...",
    "generation_config": {
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "processing_time": 15,
    "created_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:00:15Z"
  }
}
```

#### 获取AI生成记录列表

**端点**: `GET /api/v1/ai/generations`

**描述**: 获取AI生成记录列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `document_id`: 文档ID筛选
- `user_id`: 用户ID筛选（管理员可用）
- `status`: 生成状态筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "document_id": 1,
        "document_title": "环保应急预案第一章",
        "user_id": 1,
        "user_name": "张三",
        "status": "completed",
        "prompt": "请生成环保应急预案的应急响应部分...",
        "processing_time": 15,
        "created_at": "2024-01-01T12:00:00Z",
        "completed_at": "2024-01-01T12:00:15Z"
      }
    ],
    "total": 25,
    "page": 1,
    "size": 20,
    "pages": 2
  }
}
```

#### 获取AI生成模板列表

**端点**: `GET /api/v1/ai/templates`

**描述**: 获取AI生成模板列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `category`: 模板分类筛选
- `is_active`: 是否启用筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "应急预案模板",
        "description": "用于生成环保应急预案的标准模板",
        "prompt_template": "请为{industry_type}企业生成{document_type}，重点包括{key_points}",
        "config": {
          "temperature": 0.7,
          "max_tokens": 2000
        },
        "category": "应急预案",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 创建AI生成模板

**端点**: `POST /api/v1/ai/templates`

**描述**: 创建AI生成模板

**认证**: 需要管理员权限

**请求体**:
```json
{
  "name": "环评报告模板",
  "description": "用于生成环境影响评价报告的标准模板",
  "prompt_template": "请为{project_type}项目生成环境影响评价报告的{section}部分，考虑{factors}等因素",
  "config": {
    "temperature": 0.6,
    "max_tokens": 2500,
    "top_p": 0.9
  },
  "category": "环评报告"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "环评报告模板",
    "description": "用于生成环境影响评价报告的标准模板",
    "prompt_template": "请为{project_type}项目生成环境影响评价报告的{section}部分，考虑{factors}等因素",
    "config": {
      "temperature": 0.6,
      "max_tokens": 2500,
      "top_p": 0.9
    },
    "category": "环评报告",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "AI生成模板创建成功"
}
```

### 文档导出接口

#### 导出文档

**端点**: `POST /api/v1/exports`

**描述**: 导出文档为指定格式

**认证**: 需要JWT令牌

**请求体**:
```json
{
  "document_id": 1,
  "format": "pdf",
  "include_metadata": true,
  "include_versions": false,
  "watermark": "内部文档",
  "page_size": "A4",
  "margin": "normal",
  "header": "环保应急预案",
  "footer": "示例化工有限公司",
  "table_of_contents": true
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "export_id": 1,
    "document_id": 1,
    "format": "pdf",
    "status": "processing",
    "message": "文档导出任务已提交，正在处理中",
    "estimated_time": 30
  }
}
```

#### 获取导出状态

**端点**: `GET /api/v1/exports/{export_id}`

**描述**: 获取文档导出状态和下载链接

**认证**: 需要JWT令牌

**路径参数**:
- `export_id`: 导出记录ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "document_id": 1,
    "document_title": "环保应急预案第一章",
    "user_id": 1,
    "user_name": "张三",
    "format": "pdf",
    "status": "completed",
    "file_url": "https://example.com/exports/document_1_20240101.pdf",
    "file_name": "环保应急预案第一章_20240101.pdf",
    "file_size": 1024000,
    "download_url": "https://example.com/api/v1/exports/1/download",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 下载导出文件

**端点**: `GET /api/v1/exports/{export_id}/download`

**描述**: 下载导出的文档文件

**认证**: 需要JWT令牌

**路径参数**:
- `export_id`: 导出记录ID

**响应**: 文件流

#### 获取导出记录列表

**端点**: `GET /api/v1/exports`

**描述**: 获取文档导出记录列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `document_id`: 文档ID筛选
- `user_id`: 用户ID筛选（管理员可用）
- `format`: 导出格式筛选
- `status`: 导出状态筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "document_id": 1,
        "document_title": "环保应急预案第一章",
        "user_id": 1,
        "user_name": "张三",
        "format": "pdf",
        "status": "completed",
        "file_name": "环保应急预案第一章_20240101.pdf",
        "file_size": 1024000,
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 15,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 获取导出模板列表

**端点**: `GET /api/v1/exports/templates`

**描述**: 获取文档导出模板列表

**认证**: 需要JWT令牌

**查询参数**:
- `page`: 页码，默认为1
- `size`: 每页大小，默认为20
- `format`: 导出格式筛选
- `is_active`: 是否启用筛选

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "标准PDF模板",
        "description": "用于导出标准PDF文档的模板",
        "format": "pdf",
        "options": {
          "pdf_page_size": "A4",
          "pdf_orientation": "portrait",
          "pdf_margin_top": 2.54,
          "pdf_margin_bottom": 2.54,
          "pdf_margin_left": 1.91,
          "pdf_margin_right": 1.91,
          "pdf_font_size": 12,
          "pdf_line_height": 1.5,
          "include_header": true,
          "include_footer": true,
          "include_page_numbers": true
        },
        "is_default": true,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 创建导出模板

**端点**: `POST /api/v1/exports/templates`

**描述**: 创建文档导出模板

**认证**: 需要管理员权限

**请求体**:
```json
{
  "name": "自定义Word模板",
  "description": "用于导出自定义Word文档的模板",
  "format": "word",
  "options": {
    "word_page_size": "A4",
    "word_orientation": "portrait",
    "word_margin_top": 2.54,
    "word_margin_bottom": 2.54,
    "word_margin_left": 1.91,
    "word_margin_right": 1.91,
    "word_font_size": 12,
    "word_line_height": 1.5,
    "include_header": false,
    "include_footer": true,
    "include_page_numbers": true,
    "include_watermark": true,
    "watermark_text": "机密文档",
    "watermark_opacity": 0.1
  },
  "is_default": false
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "自定义Word模板",
    "description": "用于导出自定义Word文档的模板",
    "format": "word",
    "options": {
      "word_page_size": "A4",
      "word_orientation": "portrait",
      "word_margin_top": 2.54,
      "word_margin_bottom": 2.54,
      "word_margin_left": 1.91,
      "word_margin_right": 1.91,
      "word_font_size": 12,
      "word_line_height": 1.5,
      "include_header": false,
      "include_footer": true,
      "include_page_numbers": true,
      "include_watermark": true,
      "watermark_text": "机密文档",
      "watermark_opacity": 0.1
    },
    "is_default": false,
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "导出模板创建成功"
}
```

## 接口版本控制

### 版本策略

API采用语义化版本控制，当前版本为v1。版本号在URL路径中指定：

```
/api/v1/  - 版本1
/api/v2/  - 版本2（未来版本）
```

### 版本兼容性

- 向后兼容的更改不会增加主版本号
- 破坏性更改会增加主版本号
- 旧版本会保持维护一段时间，提供迁移指南

### 版本选择

客户端可以通过以下方式指定API版本：

1. **URL路径版本**（推荐）:
   ```
   /api/v1/users/
   ```

2. **请求头版本**:
   ```
   Accept: application/vnd.api+json;version=1
   ```

## 分页和过滤

### 分页参数

所有列表接口支持以下分页参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码，从1开始 |
| size | integer | 20 | 每页大小，最大100 |

### 分页响应

分页响应包含以下信息：

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### 过滤参数

不同接口支持不同的过滤参数，常见的过滤参数包括：

- `keyword`: 关键词搜索
- `status`: 状态筛选
- `created_after`: 创建时间起始
- `created_before`: 创建时间结束
- `user_id`: 用户ID筛选
- `company_id`: 企业ID筛选

### 排序参数

支持通过以下参数进行排序：

- `sort_by`: 排序字段
- `sort_order`: 排序方向（asc/desc）

示例：
```
GET /api/v1/projects/?sort_by=created_at&sort_order=desc
```

## 安全策略

### 认证机制

1. **JWT令牌认证**:
   - 使用HS256算法签名
   - 令牌有效期8天（可配置）
   - 包含用户ID、角色和过期时间

2. **令牌刷新**:
   - 提供令牌刷新接口
   - 旧令牌在刷新后失效

### 授权控制

1. **基于角色的访问控制（RBAC）**:
   - user: 普通用户权限
   - admin: 管理员权限

2. **资源级权限控制**:
   - 用户只能访问自己的资源
   - 管理员可以访问所有资源

### 数据安全

1. **密码安全**:
   - 使用bcrypt加密存储密码
   - 密码强度验证（最少8位）

2. **敏感数据保护**:
   - 日志中不记录敏感信息
   - 数据库连接使用SSL

3. **输入验证**:
   - 所有输入数据经过验证和清理
   - 防止SQL注入和XSS攻击

### HTTPS支持

生产环境必须使用HTTPS协议，确保数据传输安全。

## 接口限流

### 限流策略

1. **用户级限流**:
   - 普通用户：100请求/分钟
   - 管理员：200请求/分钟

2. **接口级限流**:
   - 认证接口：10请求/分钟
   - AI生成接口：20请求/小时
   - 文档导出接口：30请求/小时

### 限流响应

当请求超过限制时，返回429状态码：

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超过限制",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_time": "2024-01-01T12:01:00Z"
    }
  }
}
```

### 限流头信息

响应中包含以下限流相关头信息：

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 接口使用示例

### 完整的项目创建和文档生成流程

1. **用户登录**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
```

2. **创建项目**:
```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "化工企业环保应急预案",
    "type": "emergency_plan",
    "description": "为化工企业制定的环保应急预案",
    "company_id": 1
  }'
```

3. **创建文档**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "环保应急预案第一章",
    "content": "# 第一章 总则\n\n",
    "project_id": 1
  }'
```

4. **AI生成内容**:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "prompt": "请生成环保应急预案的总则部分，包括编制目的、依据和适用范围",
    "section": "总则"
  }'
```

5. **导出文档**:
```bash
curl -X POST "http://localhost:8000/api/v1/exports" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "format": "pdf",
    "watermark": "内部文档"
  }'
```

## 总结

本文档提供了悦恩人机共写平台的完整API接口规范，包括：

1. **用户认证和授权**：JWT令牌认证，基于角色的访问控制
2. **用户管理**：用户CRUD操作、偏好设置管理
3. **企业管理**：企业信息管理、联系人管理
4. **项目管理**：项目CRUD操作、表单管理
5. **文档管理**：文档CRUD操作、版本控制
6. **AI生成**：AI内容生成、模板管理
7. **文档导出**：多格式文档导出、模板管理

所有接口遵循RESTful设计原则，提供统一的响应格式和错误处理机制，支持分页、过滤和排序功能，并实现了完善的安全策略和接口限流机制。