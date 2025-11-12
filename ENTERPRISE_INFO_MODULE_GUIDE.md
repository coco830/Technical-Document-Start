# 企业信息收集模块使用指南

## 📋 模块概述

企业信息收集模块是环保应急预案系统的第一阶段（Data Intake），用于采集企业的基本资料，为后续应急预案AI撰写提供数据支持。

## 🚀 快速开始

### 1. 访问企业信息收集页面

1. 登录悦恩人机共写平台
2. 在工作台点击"企业信息收集"卡片
3. 或直接访问 `/enterprise-info` 路径

### 2. 填写企业信息

#### 企业基本信息
- **企业名称**（必填）：输入企业全称
- **地址**：输入企业详细地址
- **所属行业**（必填）：从下拉列表选择行业类型
- **联系人**：输入企业联系人姓名
- **电话**：输入联系人电话
- **员工人数**：输入企业员工总数
- **主要产品**：输入企业主要产品
- **年产量**：输入企业年产量
- **企业简介**：输入企业详细描述

#### 环保手续信息
- **环评批复编号**：输入环境影响评价批复编号
- **验收文件编号**：输入环保验收文件编号
- **排污许可证编号**：输入排污许可证编号
- **环保主管部门**：输入环保主管部门名称

#### 危险化学品信息
1. 点击"添加危险化学品"按钮
2. 填写化学品信息：
   - 化学品名称
   - 最大储存量（吨）
   - 年使用量（吨）
   - 储存位置
3. 可添加多个危险化学品信息
4. 点击垃圾桶图标删除不需要的条目

#### 应急资源信息
1. 点击"添加应急资源"按钮
2. 填写资源信息：
   - 物资名称
   - 数量
   - 用途
   - 存放地点
   - 保管人
3. 可添加多个应急资源信息
4. 点击垃圾桶图标删除不需要的条目

#### 应急组织与通讯信息
1. 点击"添加应急组织"按钮
2. 填写组织信息：
   - 组织机构名称
   - 负责人
   - 联系电话
   - 职责说明
3. 可添加多个应急组织信息
4. 点击垃圾桶图标删除不需要的条目

### 3. 提交信息

1. 填写完所有必要信息后，点击"提交信息"按钮
2. 系统会验证表单数据
3. 提交成功后会显示成功提示
4. 如需保存草稿，可点击"保存草稿"按钮

## 📊 数据结构

提交的企业信息数据结构如下：

```json
{
  "enterprise_basic": {
    "enterprise_name": "企业名称",
    "address": "企业地址",
    "industry": "所属行业",
    "contact_person": "联系人",
    "phone": "联系电话",
    "employee_count": "员工人数",
    "main_products": "主要产品",
    "annual_output": "年产量",
    "description": "企业简介"
  },
  "env_permits": {
    "env_assessment_no": "环评批复编号",
    "acceptance_no": "验收文件编号",
    "discharge_permit_no": "排污许可证编号",
    "env_dept": "环保主管部门"
  },
  "hazardous_materials": [
    {
      "name": "化学品名称",
      "max_storage": "最大储存量",
      "annual_usage": "年使用量",
      "storage_location": "储存位置"
    }
  ],
  "emergency_resources": [
    {
      "name": "物资名称",
      "quantity": "数量",
      "purpose": "用途",
      "storage_location": "存放地点",
      "custodian": "保管人"
    }
  ],
  "emergency_orgs": [
    {
      "org_name": "组织机构名称",
      "responsible_person": "负责人",
      "contact_phone": "联系电话",
      "duties": "职责说明"
    }
  ]
}
```

## 🔧 技术实现

### 前端技术栈
- **React 18**：组件化UI框架
- **TypeScript**：类型安全的JavaScript
- **React Hook Form**：表单状态管理和验证
- **TailwindCSS**：实用优先的CSS框架
- **React Router**：单页应用路由

### 后端技术栈
- **FastAPI**：现代、快速的Web框架
- **SQLAlchemy**：Python SQL工具包和ORM
- **Pydantic**：数据验证和设置管理
- **SQLite**：轻量级数据库

### API接口

#### 创建企业信息
```
POST /api/enterprise/info
Content-Type: application/json
Authorization: Bearer <token>

{
  "enterprise_basic": {...},
  "env_permits": {...},
  "hazardous_materials": [...],
  "emergency_resources": [...],
  "emergency_orgs": [...]
}
```

#### 获取企业信息列表
```
GET /api/enterprise/info?page=1&page_size=10&search=关键词
Authorization: Bearer <token>
```

#### 获取特定企业信息
```
GET /api/enterprise/info/{id}
Authorization: Bearer <token>
```

#### 更新企业信息
```
PUT /api/enterprise/info/{id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "enterprise_basic": {...},
  "env_permits": {...},
  "hazardous_materials": [...],
  "emergency_resources": [...],
  "emergency_orgs": [...]
}
```

#### 删除企业信息
```
DELETE /api/enterprise/info/{id}
Authorization: Bearer <token>
```

## 🧪 测试

### 运行后端测试
```bash
cd backend
python test_enterprise_info.py
```

### 测试覆盖
- 创建企业信息
- 获取企业信息列表
- 获取特定企业信息
- 更新企业信息
- 删除企业信息
- 表单验证

## 📝 开发说明

### 前端组件结构
```
frontend/src/pages/EnterpriseInfo.tsx
├── 表单状态管理
├── 企业基本信息表单
├── 环保手续信息表单
├── 危险化学品信息动态表单
├── 应急资源信息动态表单
├── 应急组织与通讯信息动态表单
└── 表单提交和验证逻辑
```

### 后端文件结构
```
backend/
├── app/models/enterprise.py          # 企业信息数据模型
├── app/schemas/enterprise.py         # 企业信息Pydantic模式
├── app/routes/enterprise.py          # 企业信息API路由
├── migrations/005_create_enterprise_info_table.sql  # 数据库迁移
└── test_enterprise_info.py          # API测试
```

### 数据库表结构
```sql
CREATE TABLE enterprise_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_id INTEGER,
    
    -- 企业基本信息
    enterprise_name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    industry VARCHAR(100),
    contact_person VARCHAR(100),
    phone VARCHAR(50),
    employee_count VARCHAR(50),
    main_products TEXT,
    annual_output TEXT,
    description TEXT,
    
    -- 环保手续信息
    env_assessment_no VARCHAR(255),
    acceptance_no VARCHAR(255),
    discharge_permit_no VARCHAR(255),
    env_dept VARCHAR(255),
    
    -- 危险化学品信息 (JSON格式存储)
    hazardous_materials TEXT,
    
    -- 应急资源信息 (JSON格式存储)
    emergency_resources TEXT,
    
    -- 应急组织信息 (JSON格式存储)
    emergency_orgs TEXT,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL
);
```

## 🔒 安全考虑

1. **认证授权**：所有API接口需要JWT令牌认证
2. **数据验证**：使用Pydantic进行严格的输入验证
3. **用户隔离**：用户只能访问自己的企业信息
4. **SQL注入防护**：使用ORM防止SQL注入攻击
5. **XSS防护**：前端对用户输入进行转义处理

## 🚀 后续扩展

1. **数据导入导出**：支持Excel批量导入导出
2. **模板预设**：提供行业特定的信息模板
3. **数据可视化**：企业信息图表展示
4. **审批流程**：企业信息审核和批准流程
5. **历史版本**：企业信息变更历史记录

## 📞 技术支持

如需技术支持或有任何问题，请联系：
- 邮箱：support@yueen.com
- 文档：https://docs.yueen.com
- 问题反馈：https://github.com/yueen/platform/issues

---

**文档版本**：v1.0  
**创建日期**：2025-11-12  
**最后更新**：2025-11-12  
**维护团队**：悦恩技术团队