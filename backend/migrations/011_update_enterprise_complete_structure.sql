-- 更新企业信息表完整结构
-- 迁移版本: 011
-- 创建时间: 2025-11-18

-- 添加企业身份信息字段
ALTER TABLE enterprise_info ADD COLUMN unified_social_credit_code VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN group_company VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN industry_subdivision TEXT;
ALTER TABLE enterprise_info ADD COLUMN park_name VARCHAR(255);
-- 注意：risk_level字段已存在，不需要重复添加

-- 添加地址与空间信息字段
ALTER TABLE enterprise_info ADD COLUMN province VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN city VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN district VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN detailed_address VARCHAR(500);
ALTER TABLE enterprise_info ADD COLUMN postal_code VARCHAR(20);
ALTER TABLE enterprise_info ADD COLUMN longitude VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN latitude VARCHAR(50);

-- 添加联系人与职责字段
ALTER TABLE enterprise_info ADD COLUMN legal_representative_name VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN legal_representative_phone VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN env_officer_name VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN env_officer_position VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN env_officer_phone VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN emergency_contact_name VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN emergency_contact_position VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN emergency_contact_phone VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN landline_phone VARCHAR(50);
-- 注意：email字段已存在，重命名为enterprise_email
ALTER TABLE enterprise_info RENAME COLUMN email TO enterprise_email;

-- 添加企业运营概况字段
ALTER TABLE enterprise_info ADD COLUMN establishment_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN production_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN production_status VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN total_employees INTEGER;
ALTER TABLE enterprise_info ADD COLUMN production_staff INTEGER;
ALTER TABLE enterprise_info ADD COLUMN management_staff INTEGER;
ALTER TABLE enterprise_info ADD COLUMN shift_system VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN daily_work_hours VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN annual_work_days INTEGER;
ALTER TABLE enterprise_info ADD COLUMN land_area INTEGER;
ALTER TABLE enterprise_info ADD COLUMN building_area INTEGER;
ALTER TABLE enterprise_info ADD COLUMN total_investment INTEGER;
ALTER TABLE enterprise_info ADD COLUMN env_investment INTEGER;
ALTER TABLE enterprise_info ADD COLUMN business_types TEXT;

-- 添加企业简介文本字段
ALTER TABLE enterprise_info ADD COLUMN enterprise_intro TEXT;

-- 添加步骤2：生产过程与风险物质字段
ALTER TABLE enterprise_info ADD COLUMN products_info TEXT;
ALTER TABLE enterprise_info ADD COLUMN raw_materials_info TEXT;
ALTER TABLE enterprise_info ADD COLUMN energy_usage TEXT;
ALTER TABLE enterprise_info ADD COLUMN production_process TEXT;
ALTER TABLE enterprise_info ADD COLUMN storage_facilities TEXT;
ALTER TABLE enterprise_info ADD COLUMN loading_operations TEXT;
ALTER TABLE enterprise_info ADD COLUMN hazardous_chemicals TEXT;
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste TEXT;

-- 添加环境信息字段
ALTER TABLE enterprise_info ADD COLUMN env_receptor_info TEXT;
ALTER TABLE enterprise_info ADD COLUMN env_pollutant_info TEXT;
ALTER TABLE enterprise_info ADD COLUMN env_prevention_facilities TEXT;

-- 添加环境管理制度字段
ALTER TABLE enterprise_info ADD COLUMN env_management_system VARCHAR(50);
-- 注意：env_officer字段已存在，不需要重复添加

-- 删除不再需要的旧字段
ALTER TABLE enterprise_info DROP COLUMN address;
ALTER TABLE enterprise_info DROP COLUMN legal_representative;
ALTER TABLE enterprise_info DROP COLUMN contact_phone;
ALTER TABLE enterprise_info DROP COLUMN overview;

-- 创建新的索引
CREATE INDEX IF NOT EXISTS idx_enterprise_unified_social_credit_code ON enterprise_info (unified_social_credit_code);
CREATE INDEX IF NOT EXISTS idx_enterprise_group_company ON enterprise_info (group_company);
CREATE INDEX IF NOT EXISTS idx_enterprise_province ON enterprise_info (province);
CREATE INDEX IF NOT EXISTS idx_enterprise_city ON enterprise_info (city);