-- 创建企业信息表
-- 迁移版本: 005
-- 创建时间: 2025-11-12

CREATE TABLE IF NOT EXISTS enterprise_info (
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_enterprise_user_id ON enterprise_info (user_id);
CREATE INDEX IF NOT EXISTS idx_enterprise_project_id ON enterprise_info (project_id);
CREATE INDEX IF NOT EXISTS idx_enterprise_name ON enterprise_info (enterprise_name);
CREATE INDEX IF NOT EXISTS idx_enterprise_industry ON enterprise_info (industry);
CREATE INDEX IF NOT EXISTS idx_enterprise_created_at ON enterprise_info (created_at);

-- 复合索引用于用户企业信息查询
CREATE INDEX IF NOT EXISTS idx_enterprise_user_created ON enterprise_info (user_id, created_at DESC);