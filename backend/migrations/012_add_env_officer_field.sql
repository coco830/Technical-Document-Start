-- 添加缺失的 env_officer 字段
-- 迁移版本: 012
-- 创建时间: 2025-11-19
-- 修复问题: 企业信息表缺少 env_officer 字段，导致保存时出现 500 错误

-- 添加缺失的环保负责人字段
ALTER TABLE enterprise_info ADD COLUMN env_officer VARCHAR(100);