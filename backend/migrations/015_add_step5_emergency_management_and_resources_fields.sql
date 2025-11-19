-- 添加步骤5：应急管理与资源相关字段
-- 执行时间: 2025-11-19

-- 5.1 应急组织机构与联络方式
ALTER TABLE enterprise_info ADD COLUMN enterprise_24h_duty_phone VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN internal_emergency_contacts JSON;
ALTER TABLE enterprise_info ADD COLUMN external_emergency_unit_contacts JSON;

-- 5.2 应急物资与装备
ALTER TABLE enterprise_info ADD COLUMN emergency_materials_list JSON;
ALTER TABLE enterprise_info ADD COLUMN emergency_warehouse_count INTEGER;
ALTER TABLE enterprise_info ADD COLUMN warehouse_total_area DECIMAL(10,2);
ALTER TABLE enterprise_info ADD COLUMN has_accident_pool BOOLEAN;
ALTER TABLE enterprise_info ADD COLUMN accident_pool_volume DECIMAL(10,2);
ALTER TABLE enterprise_info ADD COLUMN emergency_vehicles VARCHAR(200);

-- 5.3 应急队伍与保障
ALTER TABLE enterprise_info ADD COLUMN has_internal_rescue_team BOOLEAN;
ALTER TABLE enterprise_info ADD COLUMN rescue_team_size INTEGER;
ALTER TABLE enterprise_info ADD COLUMN team_composition_description TEXT;
ALTER TABLE enterprise_info ADD COLUMN has_emergency_budget BOOLEAN;
ALTER TABLE enterprise_info ADD COLUMN annual_emergency_budget DECIMAL(12,2);

-- 5.4 演练与培训记录
ALTER TABLE enterprise_info ADD COLUMN has_conducted_drills BOOLEAN;
ALTER TABLE enterprise_info ADD COLUMN drill_records JSON;
ALTER TABLE enterprise_info ADD COLUMN annual_emergency_training_count INTEGER;
ALTER TABLE enterprise_info ADD COLUMN annual_environmental_training_count INTEGER;
ALTER TABLE enterprise_info ADD COLUMN employee_coverage_rate DECIMAL(5,2);
ALTER TABLE enterprise_info ADD COLUMN includes_hazardous_chemicals_safety BOOLEAN;

-- 5.5 应急资源调查元数据
ALTER TABLE enterprise_info ADD COLUMN emergency_resource_survey_year INTEGER;
ALTER TABLE enterprise_info ADD COLUMN survey_start_date DATE;
ALTER TABLE enterprise_info ADD COLUMN survey_end_date DATE;
ALTER TABLE enterprise_info ADD COLUMN survey_leader_name VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN survey_contact_phone VARCHAR(50);

-- 添加索引以提高查询性能
CREATE INDEX idx_enterprise_info_emergency_24h_duty_phone ON enterprise_info(enterprise_24h_duty_phone);
CREATE INDEX idx_enterprise_info_has_internal_rescue_team ON enterprise_info(has_internal_rescue_team);
CREATE INDEX idx_enterprise_info_has_emergency_budget ON enterprise_info(has_emergency_budget);
CREATE INDEX idx_enterprise_info_emergency_resource_survey_year ON enterprise_info(emergency_resource_survey_year);