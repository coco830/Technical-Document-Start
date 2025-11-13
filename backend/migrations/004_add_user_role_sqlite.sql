-- 添加用户角色字段 (SQLite版本)
-- 迁移脚本：为用户表添加角色字段

-- 添加角色字段到用户表
ALTER TABLE users 
ADD COLUMN role TEXT DEFAULT 'user' NOT NULL;

-- 为角色字段创建索引
CREATE INDEX idx_users_role ON users(role);

-- 更新现有用户：将第一个用户设置为管理员，其他用户设置为普通用户
UPDATE users 
SET role = CASE 
    WHEN id = 1 THEN 'admin'
    ELSE 'user'
END
WHERE role IS NULL OR role = 'user';