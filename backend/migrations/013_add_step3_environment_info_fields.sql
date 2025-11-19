-- 添加步骤3：环境信息相关字段
-- 迁移脚本：013_add_step3_environment_info_fields.sql

-- 步骤3：环境信息 - 3.1 自然与功能区信息
ALTER TABLE enterprise_info ADD COLUMN administrative_division_code VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN water_environment_function_zone VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN atmospheric_environment_function_zone VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN watershed_name VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN nearest_surface_water_body VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN distance_to_surface_water VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN surface_water_direction VARCHAR(100);

-- 步骤3：环境信息 - 3.2 周边环境风险受体（动态数组）
ALTER TABLE enterprise_info ADD COLUMN environmental_risk_receptors JSON;

-- 步骤3：环境信息 - 3.3 废水产生与治理
ALTER TABLE enterprise_info ADD COLUMN drainage_system VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN has_production_wastewater VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN has_domestic_sewage VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN wastewater_treatment_facilities JSON;
ALTER TABLE enterprise_info ADD COLUMN wastewater_outlets JSON;

-- 步骤3：环境信息 - 3.4 废气产生与治理
ALTER TABLE enterprise_info ADD COLUMN organized_waste_gas_sources JSON;
ALTER TABLE enterprise_info ADD COLUMN unorganized_waste_gas JSON;

-- 步骤3：环境信息 - 3.5 噪声与固体废物
ALTER TABLE enterprise_info ADD COLUMN main_noise_sources JSON;
ALTER TABLE enterprise_info ADD COLUMN general_solid_wastes JSON;

-- 步骤3：环境信息 - 3.6 事故防控设施
ALTER TABLE enterprise_info ADD COLUMN has_rain_sewage_diversion VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN rain_sewage_diversion_description TEXT;
ALTER TABLE enterprise_info ADD COLUMN has_key_area_bunds VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN bunds_location VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN hazardous_chemicals_warehouse_seepage TEXT;
ALTER TABLE enterprise_info ADD COLUMN key_valves_and_shutoff_facilities TEXT;

-- 添加索引以提高查询性能
CREATE INDEX idx_enterprise_administrative_division_code ON enterprise_info(administrative_division_code);
CREATE INDEX idx_enterprise_watershed_name ON enterprise_info(watershed_name);
CREATE INDEX idx_enterprise_drainage_system ON enterprise_info(drainage_system);