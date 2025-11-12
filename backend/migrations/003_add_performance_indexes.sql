-- 添加性能优化索引
-- 迁移脚本：003_add_performance_indexes.sql
-- 描述：为提高查询性能添加必要的索引

-- 用户表索引优化
-- 为活跃状态和验证状态添加索引
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 项目表索引优化
-- 复合索引用于用户项目状态过滤
CREATE INDEX IF NOT EXISTS idx_projects_user_status ON projects(user_id, status);
-- 复合索引用于用户项目按创建时间排序
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at);

-- 文档表索引优化
-- 为模板字段添加索引
CREATE INDEX IF NOT EXISTS idx_documents_is_template ON documents(is_template);
-- 复合索引用于用户模板过滤
CREATE INDEX IF NOT EXISTS idx_documents_user_template ON documents(user_id, is_template);
-- 复合索引用于用户项目文档查询
CREATE INDEX IF NOT EXISTS idx_documents_user_project ON documents(user_id, project_id);
-- 复合索引用于项目文档按更新时间排序
CREATE INDEX IF NOT EXISTS idx_documents_project_updated ON documents(project_id, updated_at);
-- 复合索引用于用户文档按更新时间排序
CREATE INDEX IF NOT EXISTS idx_documents_user_updated ON documents(user_id, updated_at);

-- 评论表索引优化
-- 复合索引用于获取评论和回复
CREATE INDEX IF NOT EXISTS idx_comments_document_parent ON comments(document_id, parent_id);
-- 复合索引用于文档评论按时间排序
CREATE INDEX IF NOT EXISTS idx_comments_document_created ON comments(document_id, created_at);
-- 复合索引用于回复按时间排序
CREATE INDEX IF NOT EXISTS idx_comments_parent_created ON comments(parent_id, created_at);

-- 分析表以更新统计信息
ANALYZE users;
ANALYZE projects;
ANALYZE documents;
ANALYZE comments;

-- 记录迁移完成
INSERT INTO migrations (version, description, applied_at) 
VALUES (3, '添加性能优化索引', datetime('now'))
ON CONFLICT (version) DO NOTHING;

-- 输出迁移完成信息
SELECT 'Performance indexes migration completed successfully' as message;