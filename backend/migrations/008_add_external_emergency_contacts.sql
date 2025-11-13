-- 添加外部应急救援通讯方式字段
-- 执行时间: 2025-11-12

-- 添加外部应急救援通讯方式字段
ALTER TABLE enterprise_info 
ADD COLUMN external_emergency_contacts JSON COMMENT '外部应急救援通讯方式列表';