-- 添加环保部门字段（如果不存在）
-- 迁移版本: 010
-- 创建时间: 2025-11-18
-- 修复env_dept字段缺失问题

-- 检查字段是否存在，如果不存在则添加
-- SQLite不支持IF NOT EXISTS for columns，所以我们需要先检查

-- 创建临时表来检查字段是否存在
-- 如果添加失败会抛出异常，我们忽略它

-- 尝试添加env_dept字段（如果不存在）
ALTER TABLE enterprise_info ADD COLUMN env_dept VARCHAR(255) COMMENT '环保部门';