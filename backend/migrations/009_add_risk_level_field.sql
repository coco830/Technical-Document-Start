-- 添加风险级别字段
-- 执行时间: 2025-11-13

-- 添加风险级别字段
ALTER TABLE enterprise_info 
ADD COLUMN risk_level VARCHAR(50) COMMENT '风险级别';