-- 添加步骤4：环保手续与管理制度相关字段
-- 执行时间: 2025-11-19

-- 4.1 环保手续（证照）- 环评文件
ALTER TABLE enterprise_info ADD COLUMN eia_project_name VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN eia_document_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN eia_approval_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN eia_consistency_status VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN eia_report_upload VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN eia_approval_upload VARCHAR(255);

-- 4.1 环保手续（证照）- 竣工环保验收
ALTER TABLE enterprise_info ADD COLUMN acceptance_type VARCHAR(100);
ALTER TABLE enterprise_info ADD COLUMN acceptance_document_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN acceptance_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN acceptance_report_upload VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN acceptance_approval_upload VARCHAR(255);

-- 4.1 环保手续（证照）- 排污许可证
ALTER TABLE enterprise_info ADD COLUMN discharge_permit_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN issuing_authority VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN permit_start_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN permit_end_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN permitted_pollutants TEXT;
ALTER TABLE enterprise_info ADD COLUMN permit_scan_upload VARCHAR(255);

-- 4.1 环保手续（证照）- 其他环保相关许可证（动态数组）
ALTER TABLE enterprise_info ADD COLUMN other_env_certificates JSON;

-- 4.2 危险废物/医废处置协议 - 危废处置协议
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_agreement_unit VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_unit_permit_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_agreement_start_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_agreement_end_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_categories TEXT;
ALTER TABLE enterprise_info ADD COLUMN hazardous_waste_agreement_upload VARCHAR(255);

-- 4.2 危险废物/医废处置协议 - 医疗废物处置协议（如适用）
ALTER TABLE enterprise_info ADD COLUMN medical_waste_agreement_unit VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN medical_waste_unit_permit_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN medical_waste_agreement_start_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN medical_waste_agreement_end_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN medical_waste_categories TEXT;
ALTER TABLE enterprise_info ADD COLUMN medical_waste_agreement_upload VARCHAR(255);

-- 4.3 环境应急预案备案情况
-- 注意：has_emergency_plan 字段已存在，将重命名为 has_emergency_plan_old 以保留原有数据
ALTER TABLE enterprise_info RENAME COLUMN has_emergency_plan TO has_emergency_plan_old;
ALTER TABLE enterprise_info ADD COLUMN has_emergency_plan VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN has_emergency_plan_filed VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN emergency_plan_filing_number VARCHAR(255);
ALTER TABLE enterprise_info ADD COLUMN emergency_plan_filing_date VARCHAR(50);
ALTER TABLE enterprise_info ADD COLUMN emergency_plan_filing_upload VARCHAR(255);

-- 4.4 管理制度与处罚记录 - 管理制度情况
ALTER TABLE enterprise_info ADD COLUMN has_risk_inspection_system VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN has_hazardous_chemicals_management_system VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN has_hazardous_waste_management_system VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN has_emergency_drill_training_system VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN management_system_files_upload VARCHAR(255);

-- 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
ALTER TABLE enterprise_info ADD COLUMN has_administrative_penalty VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN administrative_penalty_details TEXT;
ALTER TABLE enterprise_info ADD COLUMN has_environmental_accident VARCHAR(10);
ALTER TABLE enterprise_info ADD COLUMN environmental_accident_details TEXT;

-- 更新时间戳
UPDATE enterprise_info SET updated_at = CURRENT_TIMESTAMP WHERE 1=1;