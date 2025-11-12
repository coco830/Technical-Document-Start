-- 添加用户角色字段
-- 迁移脚本：为用户表添加角色字段和枚举类型

-- 创建用户角色枚举类型
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 添加角色字段到用户表
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role user_role DEFAULT 'user' NOT NULL;

-- 为角色字段创建索引
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 更新现有用户：将第一个用户设置为管理员，其他用户设置为普通用户
UPDATE users 
SET role = CASE 
    WHEN id = 1 THEN 'admin'::user_role
    ELSE 'user'::user_role
END
WHERE role IS NULL OR role = 'user'::user_role;

-- 添加注释
COMMENT ON COLUMN users.role IS '用户角色：user(普通用户), admin(管理员), moderator(版主)';
COMMENT ON TYPE user_role IS '用户角色枚举类型';