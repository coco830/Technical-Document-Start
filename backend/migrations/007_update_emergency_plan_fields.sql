-- 添加历史应急预案相关字段
-- 执行时间: 2025-11-12

-- 添加历史应急预案相关字段
ALTER TABLE enterprise_info 
ADD COLUMN has_emergency_plan VARCHAR(10) COMMENT '是否有历史应急预案',  -- 有/无
ADD COLUMN emergency_plan_code VARCHAR(100) COMMENT '历史应急预案编号';  -- 仅当有预案时填写

-- 删除环保主管部门字段
ALTER TABLE enterprise_info 
DROP COLUMN env_dept;