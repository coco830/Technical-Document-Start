# 悦恩人机共写平台 API

一个创新的人机协作写作平台API

## API规范

版本: 1.0.0

## 服务器

- **开发环境**: http://localhost:8000
- **生产环境**: https://api.yueen.com

## 标签

- AI生成
- 企业
- 文件管理
- 文档
- 用户
- 认证
- 项目

## 路径

### /api/v1/auth/login

#### POST POST /api/v1/auth/login

用户登录

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| user_login | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/register

#### POST POST /api/v1/auth/register

用户注册

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| user_register | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/logout

#### POST POST /api/v1/auth/logout

用户登出

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| current_user | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/me

#### GET GET /api/v1/auth/me

获取当前用户信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/refresh

#### POST POST /api/v1/auth/refresh

刷新访问令牌

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/verify-email

#### POST POST /api/v1/auth/verify-email

验证邮箱

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| email | query | - | 是 |  |
| code | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/send-verification-code

#### POST POST /api/v1/auth/send-verification-code

发送验证码

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| email | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/reset-password

#### POST POST /api/v1/auth/reset-password

重置密码

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| email | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/confirm-reset-password

#### POST POST /api/v1/auth/confirm-reset-password

确认重置密码

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| token | query | - | 是 |  |
| new_password | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/auth/change-password

#### POST POST /api/v1/auth/change-password

修改密码

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| current_password | query | - | 是 |  |
| new_password | query | - | 是 |  |
| current_user | query | - | 是 |  |
| db | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/users/

#### GET GET /api/v1/users/

获取用户列表

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/users/{user_id}

#### GET GET /api/v1/users/{user_id}

获取用户详情

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| user_id | query | - | 是 |  |

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### PUT PUT /api/v1/users/{user_id}

更新用户信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| user_id | query | - | 是 |  |

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### DELETE DELETE /api/v1/users/{user_id}

删除用户

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| user_id | query | - | 是 |  |

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/

#### GET GET /api/v1/companies/

获取企业列表（支持分页、筛选、排序）

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| keyword | query | - | 是 |  |
| industry | query | - | 是 |  |
| unified_social_credit_code | query | - | 是 |  |
| legal_representative | query | - | 是 |  |
| contact_phone | query | - | 是 |  |
| contact_email | query | - | 是 |  |
| address | query | - | 是 |  |
| order_by | query | - | 是 |  |
| order_desc | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/companies/

创建新企业

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| company_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/{company_id}

#### GET GET /api/v1/companies/{company_id}

获取单个企业详情

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### PUT PUT /api/v1/companies/{company_id}

更新企业信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| company_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### DELETE DELETE /api/v1/companies/{company_id}

删除企业

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/search

#### GET GET /api/v1/companies/search

搜索企业

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| keyword | query | - | 是 |  |
| industry | query | - | 是 |  |
| unified_social_credit_code | query | - | 是 |  |
| legal_representative | query | - | 是 |  |
| contact_phone | query | - | 是 |  |
| contact_email | query | - | 是 |  |
| address | query | - | 是 |  |
| created_after | query | - | 是 |  |
| created_before | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/by-verification-status

#### GET GET /api/v1/companies/by-verification-status

按验证状态获取企业

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| verification_status | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/statistics

#### GET GET /api/v1/companies/statistics

获取企业统计信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/{company_id}/project-count

#### GET GET /api/v1/companies/{company_id}/project-count

获取企业项目数量

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/{company_id}/verify

#### POST POST /api/v1/companies/{company_id}/verify

验证企业

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| verification_data | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/companies/{company_id}/verification-status

#### PUT PUT /api/v1/companies/{company_id}/verification-status

更新验证状态

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| company_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| verification_status | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/

#### GET GET /api/v1/projects/

获取项目列表（支持分页、筛选、排序）

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| user_id | query | - | 是 |  |
| company_id | query | - | 是 |  |
| status | query | - | 是 |  |
| project_type | query | - | 是 |  |
| order_by | query | - | 是 |  |
| order_desc | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/projects/

创建新项目

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| project_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/{project_id}

#### GET GET /api/v1/projects/{project_id}

获取单个项目详情

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### PUT PUT /api/v1/projects/{project_id}

更新项目信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| project_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### DELETE DELETE /api/v1/projects/{project_id}

删除项目

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/{project_id}/status

#### PUT PUT /api/v1/projects/{project_id}/status

更新项目状态

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| status | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/statistics

#### GET GET /api/v1/projects/statistics

获取项目统计信息

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| user_id | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/{project_id}/forms

#### GET GET /api/v1/projects/{project_id}/forms

获取项目表单列表

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| form_type | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/projects/{project_id}/forms

创建项目表单

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| form_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/projects/{project_id}/forms/{form_id}

#### PUT PUT /api/v1/projects/{project_id}/forms/{form_id}

更新项目表单

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| project_id | query | - | 是 |  |
| form_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| form_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/

#### GET GET /api/v1/documents/

获取文档列表（支持分页、筛选、排序）

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| project_id | query | - | 是 |  |
| status | query | - | 是 |  |
| format | query | - | 是 |  |
| order_by | query | - | 是 |  |
| order_desc | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/documents/

创建新文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| document_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}

#### GET GET /api/v1/documents/{document_id}

获取单个文档详情

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### PUT PUT /api/v1/documents/{document_id}

更新文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| document_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### DELETE DELETE /api/v1/documents/{document_id}

删除文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/versions

#### GET GET /api/v1/documents/{document_id}/versions

获取文档版本列表

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/documents/{document_id}/versions

创建文档版本

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| content | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/versions/{version_id}

#### GET GET /api/v1/documents/{document_id}/versions/{version_id}

获取特定版本的文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| version_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/versions/{version_id}/restore

#### POST POST /api/v1/documents/{document_id}/versions/{version_id}/restore

恢复文档到特定版本

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| version_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/status

#### PUT PUT /api/v1/documents/{document_id}/status

更新文档状态

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| status | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/by-status

#### GET GET /api/v1/documents/by-status

按状态获取文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| status | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/search

#### GET GET /api/v1/documents/search

搜索文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| query | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/by-project

#### GET GET /api/v1/documents/by-project

获取项目相关文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| project_id | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/export

#### POST POST /api/v1/documents/{document_id}/export

导出文档

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| export_request | query | - | 是 |  |
| background_tasks | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/export-history

#### GET GET /api/v1/documents/{document_id}/export-history

获取导出历史

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/ai-generate

#### POST POST /api/v1/documents/{document_id}/ai-generate

AI生成文档内容

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| request | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/exports/{export_id}/download

#### GET GET /api/v1/documents/exports/{export_id}/download

下载导出文件

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| export_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/exports/{export_id}

#### DELETE DELETE /api/v1/documents/exports/{export_id}

删除导出记录

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| export_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/exports/templates

#### GET GET /api/v1/documents/exports/templates

获取导出模板列表

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| format | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/exports/statistics

#### GET GET /api/v1/documents/exports/statistics

获取导出统计

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| days | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/documents/{document_id}/ai-enhance

#### POST POST /api/v1/documents/{document_id}/ai-enhance

AI增强文档内容

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| document_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| enhancement_type | query | - | 是 |  |
| target_section | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations

#### GET GET /api/v1/ai-generations

获取AI生成记录列表（支持分页、筛选）

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| skip | query | - | 是 |  |
| limit | query | - | 是 |  |
| user_id | query | - | 是 |  |
| document_id | query | - | 是 |  |
| status | query | - | 是 |  |
| order_by | query | - | 是 |  |
| order_desc | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### POST POST /api/v1/ai-generations

创建新的AI生成记录

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| generation_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/{generation_id}

#### GET GET /api/v1/ai-generations/{generation_id}

获取单个AI生成记录详情

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| generation_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### PUT PUT /api/v1/ai-generations/{generation_id}

更新AI生成记录

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| generation_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| generation_in | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

#### DELETE DELETE /api/v1/ai-generations/{generation_id}

删除AI生成记录

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| generation_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/generate

#### POST POST /api/v1/ai-generations/generate

生成AI内容

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| request | query | - | 是 |  |
| document_id | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/generate/emergency-plan

#### POST POST /api/v1/ai-generations/generate/emergency-plan

生成应急预案

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| plan_type | query | - | 是 |  |
| company_info | query | - | 是 |  |
| document_id | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/generate/environmental-assessment

#### POST POST /api/v1/ai-generations/generate/environmental-assessment

生成环评报告

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| project_info | query | - | 是 |  |
| document_id | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/{generation_id}/status

#### GET GET /api/v1/ai-generations/{generation_id}/status

检查生成状态

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| generation_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/{generation_id}/process

#### POST POST /api/v1/ai-generations/{generation_id}/process

启动异步处理

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| generation_id | query | - | 是 |  |
| db | query | - | 是 |  |
| current_user | query | - | 是 |  |
| background_tasks | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/templates

#### GET GET /api/v1/ai-generations/templates

获取所有模板

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/ai-generations/templates/{template_type}

#### GET GET /api/v1/ai-generations/templates/{template_type}

根据类型获取模板

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| template_type | query | - | 是 |  |
| current_user | query | - | 是 |  |
| return | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/upload

#### POST POST /api/v1/files/upload

上传文件

需要权限: file:upload

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| background_tasks | query | - | 是 |  |
| file | query | - | 是 |  |
| prefix | query | - | 是 |  |
| backup_to_cloud | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/upload/chunk

#### POST POST /api/v1/files/upload/chunk

分片上传文件

需要权限: file:upload

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| chunk_data | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/upload/progress/{file_id}

#### GET GET /api/v1/files/upload/progress/{file_id}

获取文件上传进度

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| file_id | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/download/{file_path:path}

#### GET GET /api/v1/files/download/{file_path:path}

下载文件

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| file_path | query | - | 是 |  |
| from_cloud | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/delete

#### DELETE DELETE /api/v1/files/delete

删除文件

需要权限: file:delete

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/list

#### GET GET /api/v1/files/list

列出文件

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| prefix | query | - | 是 |  |
| storage_type | query | - | 是 |  |
| limit | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/info/{file_path:path}

#### GET GET /api/v1/files/info/{file_path:path}

获取文件信息

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| file_path | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/sync

#### POST POST /api/v1/files/sync

同步文件到云存储

需要权限: file:write

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/backup

#### POST POST /api/v1/files/backup

备份文件到云存储

需要权限: file:write

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/presigned-url

#### POST POST /api/v1/files/presigned-url

生成预签名URL

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/storage/switch

#### POST POST /api/v1/files/storage/switch

切换存储类型

需要权限: system:admin

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| request | query | - | 是 |  |
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /api/v1/files/storage/status

#### GET GET /api/v1/files/storage/status

获取存储状态

需要权限: file:read

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| current_user | query | - | 是 |  |

**响应:**

- **200**: 成功响应
- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /

#### GET GET /

根路径

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /health

#### GET GET /health

健康检查端点

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /metrics

#### GET GET /metrics

系统指标端点

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /admin/database/optimize

#### GET GET /admin/database/optimize

数据库优化端点

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /admin/database/analyze/{table_name}

#### GET GET /admin/database/analyze/{table_name}

分析表性能端点

**参数:**

| 名称 | 位置 | 类型 | 必需 | 描述 |
|------|--------|------|--------|--------|
| table_name | query | - | 是 |  |

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /admin/docs/generate

#### GET GET /admin/docs/generate

生成API文档端点

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

### /admin/tests/generate

#### GET GET /admin/tests/generate

生成测试用例端点

**响应:**

- **400**: 请求参数错误
- **401**: 未授权
- **403**: 禁止访问
- **404**: 资源不存在
- **500**: 服务器内部错误

