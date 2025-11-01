# 悦恩人机共写平台 - 数据库性能优化文档

## 目录

1. [概述](#概述)
2. [数据库查询模式分析](#数据库查询模式分析)
3. [性能瓶颈分析](#性能瓶颈分析)
4. [索引策略设计](#索引策略设计)
5. [数据库分区策略](#数据库分区策略)
6. [查询优化方案](#查询优化方案)
7. [缓存策略设计](#缓存策略设计)
8. [数据库连接池配置](#数据库连接池配置)
9. [读写分离策略](#读写分离策略)
10. [分库分表方案](#分库分表方案)
11. [慢查询优化](#慢查询优化)
12. [数据库参数调优](#数据库参数调优)
13. [性能监控指标](#性能监控指标)
14. [索引维护和监控](#索引维护和监控)
15. [定期维护任务](#定期维护任务)
16. [性能测试方案](#性能测试方案)
17. [实施建议](#实施建议)

## 概述

本文档基于悦恩人机共写平台的数据库设计和API接口规范，提供全面的数据库性能优化策略。平台主要用于生成环保应急预案和环评报告，支持AI辅助写作和人机协作，具有以下特点：

- **数据特点**：文档内容大、版本记录多、AI生成频繁
- **访问模式**：读写比例约为6:4，高峰期并发访问较高
- **增长趋势**：预计年增长率200%，3年内用户量达到10万级
- **性能要求**：查询响应时间<200ms，写入操作<500ms

## 数据库查询模式分析

### 1. 常见查询模式

基于API接口规范，分析出以下高频查询模式：

#### 1.1 用户相关查询
```sql
-- 用户登录认证（高频）
SELECT id, username, email, password_hash, role, is_active 
FROM users 
WHERE username = ? OR email = ?;

-- 获取用户信息（中频）
SELECT id, username, email, full_name, avatar_url, role, created_at, last_login_at
FROM users 
WHERE id = ?;

-- 用户会话验证（高频）
SELECT us.id, us.user_id, us.expires_at, u.username, u.role
FROM user_sessions us
JOIN users u ON us.user_id = u.id
WHERE us.token_hash = ? AND us.expires_at > NOW();
```

#### 1.2 项目相关查询
```sql
-- 获取用户项目列表（高频）
SELECT p.id, p.name, p.type, p.status, p.description, p.created_at, p.updated_at,
       c.name as company_name, u.username as user_name
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
WHERE p.user_id = ?
ORDER BY p.updated_at DESC
LIMIT ? OFFSET ?;

-- 项目详情查询（中频）
SELECT p.*, c.name as company_name, u.username as user_name,
       (SELECT COUNT(*) FROM documents WHERE project_id = p.id) as documents_count,
       (SELECT COUNT(*) FROM project_forms WHERE project_id = p.id) as forms_count
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
WHERE p.id = ?;
```

#### 1.3 文档相关查询
```sql
-- 获取项目文档列表（高频）
SELECT d.id, d.title, d.format, d.status, d.created_at, d.updated_at,
       (SELECT COUNT(*) FROM document_versions WHERE document_id = d.id) as versions_count,
       (SELECT COUNT(*) FROM ai_generations WHERE document_id = d.id) as ai_generations_count
FROM documents d
WHERE d.project_id = ?
ORDER BY d.updated_at DESC
LIMIT ? OFFSET ?;

-- 文档内容查询（高频）
SELECT d.id, d.title, d.content, d.format, d.status, d.metadata, d.created_at, d.updated_at
FROM documents d
WHERE d.id = ?;

-- 文档版本历史（中频）
SELECT dv.id, dv.version_number, dv.changes_summary, dv.created_at, u.username as created_by_name
FROM document_versions dv
JOIN users u ON dv.created_by = u.id
WHERE dv.document_id = ?
ORDER BY dv.version_number DESC;
```

#### 1.4 AI生成相关查询
```sql
-- 获取AI生成记录（高频）
SELECT ag.id, ag.status, ag.created_at, ag.completed_at,
       d.title as document_title
FROM ai_generations ag
JOIN documents d ON ag.document_id = d.id
WHERE ag.user_id = ? AND ag.document_id = ?
ORDER BY ag.created_at DESC;

-- AI生成状态查询（高频）
SELECT id, status, generated_content, metadata, completed_at
FROM ai_generations
WHERE id = ?;
```

### 2. 查询频率分析

| 查询类型 | 频率 | 峰值QPS | 平均响应时间要求 |
|---------|------|---------|------------------|
| 用户认证 | 高 | 100 | <100ms |
| 用户信息获取 | 中 | 50 | <150ms |
| 项目列表查询 | 高 | 80 | <200ms |
| 项目详情查询 | 中 | 40 | <200ms |
| 文档列表查询 | 高 | 120 | <200ms |
| 文档内容查询 | 高 | 150 | <150ms |
| 文档版本查询 | 中 | 30 | <250ms |
| AI生成记录查询 | 高 | 90 | <200ms |
| AI生成状态查询 | 高 | 200 | <100ms |

## 性能瓶颈分析

### 1. 当前系统瓶颈

#### 1.1 数据库层面
- **大文本字段查询**：documents.content和ai_generations.generated_content字段较大，影响查询性能
- **关联查询复杂**：多表JOIN操作较多，特别是涉及统计信息的查询
- **索引覆盖不足**：部分查询缺少合适的复合索引
- **版本数据增长**：document_versions表数据增长快，影响历史查询性能

#### 1.2 应用层面
- **N+1查询问题**：在获取列表数据时，可能存在N+1查询问题
- **事务范围过大**：某些操作事务范围过大，锁定时间过长
- **缓存使用不足**：热点数据未有效缓存，重复查询数据库

#### 1.3 硬件层面
- **I/O瓶颈**：大文本字段的读写导致I/O压力
- **内存不足**：缓存数据占用内存过多，导致内存不足
- **CPU压力**：复杂查询和AI生成任务导致CPU压力

### 2. 性能瓶颈影响评估

| 瓶颈类型 | 影响程度 | 影响范围 | 优先级 |
|---------|---------|---------|--------|
| 大文本字段查询 | 高 | 文档相关操作 | 1 |
| 索引覆盖不足 | 高 | 所有查询操作 | 1 |
| N+1查询问题 | 中 | 列表查询操作 | 2 |
| 缓存使用不足 | 高 | 重复查询操作 | 1 |
| 版本数据增长 | 中 | 历史数据查询 | 2 |
| 事务范围过大 | 中 | 写入操作 | 3 |

## 索引策略设计

### 1. 主键索引优化

所有表的主键使用自增整数，确保插入性能和索引效率：

```sql
-- 用户表
ALTER TABLE users ADD PRIMARY KEY (id);

-- 项目表
ALTER TABLE projects ADD PRIMARY KEY (id);

-- 文档表
ALTER TABLE documents ADD PRIMARY KEY (id);

-- AI生成记录表
ALTER TABLE ai_generations ADD PRIMARY KEY (id);
```

### 2. 唯一索引设计

```sql
-- 用户表唯一索引
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 企业表唯一索引
CREATE UNIQUE INDEX idx_companies_unified_social_credit_code ON companies(unified_social_credit_code);

-- 用户会话表唯一索引
CREATE UNIQUE INDEX idx_user_sessions_token_hash ON user_sessions(token_hash);

-- 文档版本表唯一索引
CREATE UNIQUE INDEX idx_document_versions_doc_version ON document_versions(document_id, version_number);
```

### 3. 单列索引设计

```sql
-- 用户表单列索引
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_verified ON users(is_verified);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_last_login_at ON users(last_login_at);

-- 项目表单列索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_company_id ON projects(company_id);
CREATE INDEX idx_projects_type ON projects(type);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_updated_at ON projects(updated_at);
CREATE INDEX idx_projects_completed_at ON projects(completed_at);

-- 文档表单列索引
CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_title ON documents(title);
CREATE INDEX idx_documents_format ON documents(format);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_updated_at ON documents(updated_at);

-- AI生成记录表单列索引
CREATE INDEX idx_ai_generations_document_id ON ai_generations(document_id);
CREATE INDEX idx_ai_generations_user_id ON ai_generations(user_id);
CREATE INDEX idx_ai_generations_status ON ai_generations(status);
CREATE INDEX idx_ai_generations_created_at ON ai_generations(created_at);
CREATE INDEX idx_ai_generations_completed_at ON ai_generations(completed_at);

-- 用户会话表单列索引
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- 企业表单列索引
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_created_at ON companies(created_at);

-- 项目表单表单列索引
CREATE INDEX idx_project_forms_project_id ON project_forms(project_id);
CREATE INDEX idx_project_forms_form_type ON project_forms(form_type);
CREATE INDEX idx_project_forms_created_at ON project_forms(created_at);

-- 表单字段表单列索引
CREATE INDEX idx_form_fields_form_id ON form_fields(form_id);
CREATE INDEX idx_form_fields_field_name ON form_fields(field_name);
CREATE INDEX idx_form_fields_sort_order ON form_fields(sort_order);

-- 文档版本表单列索引
CREATE INDEX idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX idx_document_versions_created_by ON document_versions(created_by);
CREATE INDEX idx_document_versions_created_at ON document_versions(created_at);

-- 文档导出表单列索引
CREATE INDEX idx_document_exports_document_id ON document_exports(document_id);
CREATE INDEX idx_document_exports_user_id ON document_exports(user_id);
CREATE INDEX idx_document_exports_format ON document_exports(format);
CREATE INDEX idx_document_exports_created_at ON document_exports(created_at);
```

### 4. 复合索引设计

基于查询模式分析，设计以下复合索引：

```sql
-- 用户认证复合索引
CREATE INDEX idx_users_auth ON users(username, password_hash, is_active);
CREATE INDEX idx_users_email_auth ON users(email, password_hash, is_active);

-- 项目查询复合索引
CREATE INDEX idx_projects_user_status ON projects(user_id, status);
CREATE INDEX idx_projects_user_updated ON projects(user_id, updated_at DESC);
CREATE INDEX idx_projects_type_status ON projects(type, status);
CREATE INDEX idx_projects_company_status ON projects(company_id, status);

-- 文档查询复合索引
CREATE INDEX idx_documents_project_status ON documents(project_id, status);
CREATE INDEX idx_documents_project_updated ON documents(project_id, updated_at DESC);
CREATE INDEX idx_documents_status_updated ON documents(status, updated_at DESC);

-- AI生成记录复合索引
CREATE INDEX idx_ai_generations_document_status ON ai_generations(document_id, status);
CREATE INDEX idx_ai_generations_user_created ON ai_generations(user_id, created_at DESC);
CREATE INDEX idx_ai_generations_status_created ON ai_generations(status, created_at DESC);
CREATE INDEX idx_ai_generations_document_user ON ai_generations(document_id, user_id);

-- 用户会话复合索引
CREATE INDEX idx_user_sessions_user_expires ON user_sessions(user_id, expires_at);

-- 文档版本复合索引
CREATE INDEX idx_document_versions_doc_created ON document_versions(document_id, created_at DESC);
CREATE INDEX idx_document_versions_doc_version ON document_versions(document_id, version_number DESC);

-- 文档导出复合索引
CREATE INDEX idx_document_exports_user_created ON document_exports(user_id, created_at DESC);
CREATE INDEX idx_document_exports_document_format ON document_exports(document_id, format);
```

### 5. 全文索引设计

对于需要全文搜索的字段，创建全文索引：

```sql
-- 文档标题和内容全文索引
CREATE FULLTEXT INDEX idx_documents_fulltext ON documents(title, content);

-- AI生成记录全文索引
CREATE FULLTEXT INDEX idx_ai_generations_fulltext ON ai_generations(prompt, generated_content);

-- 企业名称和经营范围全文索引
CREATE FULLTEXT INDEX idx_companies_fulltext ON companies(name, business_scope);
```

### 6. 索引使用原则

1. **选择性原则**：优先为选择性高的字段创建索引
2. **最左前缀原则**：复合索引按照查询频率和选择性排序字段
3. **覆盖索引原则**：设计包含查询所有字段的索引，避免回表
4. **索引数量控制**：单表索引数量不超过6个，避免影响写入性能
5. **定期维护**：定期分析索引使用情况，删除无用索引

## 数据库分区策略

### 1. 分区表选择

基于数据量和查询模式，选择以下表进行分区：

#### 1.1 AI生成记录表（ai_generations）
按时间分区，因为：
- 数据量大，增长速度快
- 查询主要按时间范围进行
- 历史数据访问频率低

```sql
-- 按月分区
ALTER TABLE ai_generations 
PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    PARTITION p202403 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202405),
    PARTITION p202405 VALUES LESS THAN (202406),
    PARTITION p202406 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202408),
    PARTITION p202408 VALUES LESS THAN (202409),
    PARTITION p202409 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202411),
    PARTITION p202411 VALUES LESS THAN (202412),
    PARTITION p202412 VALUES LESS THAN (202501),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

#### 1.2 文档版本表（document_versions）
按文档ID哈希分区，因为：
- 数据量大，与文档数量成正比
- 查询主要按文档ID进行
- 需要避免热点数据

```sql
-- 按文档ID哈希分区
ALTER TABLE document_versions 
PARTITION BY HASH(document_id) 
PARTITIONS 8;
```

#### 1.3 用户会话表（user_sessions）
按时间分区，因为：
- 数据量大，会话频繁创建和过期
- 查询主要按有效时间进行
- 可以定期清理过期数据

```sql
-- 按周分区
ALTER TABLE user_sessions 
PARTITION BY RANGE (TO_DAYS(expires_at)) (
    PARTITION p_current VALUES LESS THAN (TO_DAYS(NOW() + INTERVAL 7 DAY)),
    PARTITION p_next VALUES LESS THAN (TO_DAYS(NOW() + INTERVAL 14 DAY)),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 2. 分区维护策略

#### 2.1 自动分区管理
```sql
-- 存储过程：自动添加新分区
DELIMITER $$
CREATE PROCEDURE add_monthly_partition(IN table_name VARCHAR(64), IN partition_name VARCHAR(64))
BEGIN
    SET @sql = CONCAT('ALTER TABLE ', table_name, 
                     ' REORGANIZE PARTITION p_future INTO (',
                     'PARTITION ', partition_name, ' VALUES LESS THAN (',
                     'YEAR(CURRENT_DATE) * 100 + MONTH(CURRENT_DATE) + 1, '),',
                     'PARTITION p_future VALUES LESS THAN MAXVALUE)');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;

-- 定时事件：每月1号添加新分区
CREATE EVENT auto_add_partition
ON SCHEDULE EVERY 1 MONTH
STARTS '2024-02-01 00:00:00'
DO
    CALL add_monthly_partition('ai_generations', CONCAT('p', DATE_FORMAT(NOW(), '%Y%m')));
```

#### 2.2 分区清理策略
```sql
-- 存储过程：清理过期分区
DELIMITER $$
CREATE PROCEDURE drop_old_partitions(IN table_name VARCHAR(64), IN months_to_keep INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE partition_name VARCHAR(64);
    DECLARE partition_values INT;
    DECLARE cur CURSOR FOR 
        SELECT PARTITION_NAME, PARTITION_DESCRIPTION 
        FROM INFORMATION_SCHEMA.PARTITIONS 
        WHERE TABLE_NAME = table_name 
        AND PARTITION_NAME != 'p_future'
        AND PARTITION_DESCRIPTION IS NOT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO partition_name, partition_values;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        IF partition_values < (YEAR(CURRENT_DATE) * 100 + MONTH(CURRENT_DATE) - months_to_keep) THEN
            SET @sql = CONCAT('ALTER TABLE ', table_name, ' DROP PARTITION ', partition_name);
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END IF;
    END LOOP;
    CLOSE cur;
END$$
DELIMITER ;

-- 定时事件：每季度清理6个月前的分区
CREATE EVENT auto_drop_partitions
ON SCHEDULE EVERY 1 QUARTER
STARTS '2024-04-01 00:00:00'
DO
    CALL drop_old_partitions('ai_generations', 6);
```

### 3. 分区查询优化

```sql
-- 分区裁剪优化查询
SELECT * FROM ai_generations 
WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01'
AND document_id = ?;

-- 分区信息查询
SELECT 
    PARTITION_NAME,
    PARTITION_DESCRIPTION,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH
FROM INFORMATION_SCHEMA.PARTITIONS 
WHERE TABLE_NAME = 'ai_generations';
```

## 查询优化方案

### 1. SQL查询优化

#### 1.1 避免SELECT *
```sql
-- 优化前
SELECT * FROM documents WHERE project_id = ?;

-- 优化后
SELECT id, title, format, status, created_at, updated_at 
FROM documents WHERE project_id = ?;
```

#### 1.2 使用LIMIT限制结果集
```sql
-- 优化前
SELECT * FROM ai_generations WHERE user_id = ? ORDER BY created_at DESC;

-- 优化后
SELECT id, status, created_at, completed_at 
FROM ai_generations 
WHERE user_id = ? 
ORDER BY created_at DESC 
LIMIT 20;
```

#### 1.3 避免在WHERE子句中使用函数
```sql
-- 优化前
SELECT * FROM user_sessions WHERE YEAR(expires_at) = YEAR(NOW());

-- 优化后
SELECT * FROM user_sessions 
WHERE expires_at >= DATE_FORMAT(NOW(), '%Y-01-01') 
AND expires_at < DATE_FORMAT(NOW(), '%Y-01-01') + INTERVAL 1 YEAR;
```

#### 1.4 使用JOIN替代子查询
```sql
-- 优化前
SELECT p.*, 
       (SELECT COUNT(*) FROM documents WHERE project_id = p.id) as doc_count
FROM projects p WHERE p.user_id = ?;

-- 优化后
SELECT p.*, COUNT(d.id) as doc_count
FROM projects p
LEFT JOIN documents d ON p.id = d.project_id
WHERE p.user_id = ?
GROUP BY p.id;
```

### 2. 复杂查询优化

#### 2.1 项目列表查询优化
```sql
-- 优化后的项目列表查询
SELECT 
    p.id, p.name, p.type, p.status, p.description, 
    p.created_at, p.updated_at,
    c.name as company_name,
    u.username as user_name,
    COALESCE(doc_counts.doc_count, 0) as documents_count,
    COALESCE(form_counts.form_count, 0) as forms_count
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
LEFT JOIN (
    SELECT project_id, COUNT(*) as doc_count
    FROM documents
    GROUP BY project_id
) doc_counts ON p.id = doc_counts.project_id
LEFT JOIN (
    SELECT project_id, COUNT(*) as form_count
    FROM project_forms
    GROUP BY project_id
) form_counts ON p.id = form_counts.project_id
WHERE p.user_id = ?
ORDER BY p.updated_at DESC
LIMIT ? OFFSET ?;
```

#### 2.2 文档搜索优化
```sql
-- 优化后的文档全文搜索
SELECT 
    d.id, d.title, d.format, d.status, d.created_at, d.updated_at,
    p.name as project_name,
    MATCH(d.title, d.content) AGAINST(? IN NATURAL LANGUAGE MODE) as relevance_score
FROM documents d
JOIN projects p ON d.project_id = p.id
WHERE MATCH(d.title, d.content) AGAINST(? IN NATURAL LANGUAGE MODE)
AND p.user_id = ?
ORDER BY relevance_score DESC, d.updated_at DESC
LIMIT ? OFFSET ?;
```

### 3. 查询执行计划分析

```sql
-- 分析查询执行计划
EXPLAIN FORMAT=JSON
SELECT d.id, d.title, d.status, d.created_at
FROM documents d
JOIN projects p ON d.project_id = p.id
WHERE p.user_id = ? AND d.status = 'draft'
ORDER BY d.updated_at DESC
LIMIT 20;

-- 查看索引使用情况
SHOW INDEX FROM documents;
SHOW INDEX FROM projects;

-- 分析表统计信息
ANALYZE TABLE documents;
ANALYZE TABLE projects;
```

### 4. 查询缓存优化

```sql
-- 启用查询缓存（MySQL 8.0以下版本）
SET GLOBAL query_cache_size = 268435456; -- 256MB
SET GLOBAL query_cache_type = ON;
SET GLOBAL query_cache_limit = 1048576; -- 1MB

-- 查看缓存状态
SHOW STATUS LIKE 'Qcache%';
```

## 缓存策略设计

### 1. Redis缓存架构

```mermaid
graph TB
    A[应用服务器] --> B[Redis集群]
    B --> C[缓存层1: 用户会话]
    B --> D[缓存层2: 用户信息]
    B --> E[缓存层3: 项目列表]
    B --> F[缓存层4: 文档内容]
    B --> G[缓存层5: AI生成结果]
    
    H[MySQL主库] --> I[MySQL从库1]
    H --> J[MySQL从库2]
    
    B --> H
    A --> I
    A --> J
```

### 2. 缓存键设计规范

```python
# 缓存键命名规范
CACHE_KEYS = {
    # 用户相关
    'user_info': 'user:info:{user_id}',
    'user_sessions': 'user:sessions:{user_id}',
    'user_permissions': 'user:permissions:{user_id}',
    
    # 项目相关
    'project_info': 'project:info:{project_id}',
    'project_list': 'project:list:{user_id}:{page}:{size}',
    'project_forms': 'project:forms:{project_id}',
    
    # 文档相关
    'document_info': 'document:info:{document_id}',
    'document_content': 'document:content:{document_id}',
    'document_list': 'document:list:{project_id}:{page}:{size}',
    'document_versions': 'document:versions:{document_id}',
    
    # AI生成相关
    'ai_generation': 'ai:generation:{generation_id}',
    'ai_generation_list': 'ai:list:{user_id}:{page}:{size}',
    
    # 企业相关
    'company_info': 'company:info:{company_id}',
    'company_list': 'company:list:{page}:{size}',
}
```

### 3. 缓存策略实现

#### 3.1 用户信息缓存
```python
# 缓存用户基本信息，TTL: 1小时
@cache_result(key=CACHE_KEYS['user_info'], ttl=3600)
def get_user_info(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'avatar_url': user.avatar_url,
            'role': user.role.value,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat(),
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
        }
    return None

# 缓存用户会话，TTL: 8天（与JWT过期时间一致）
@cache_result(key=CACHE_KEYS['user_sessions'], ttl=691200)
def get_user_sessions(user_id: int):
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.expires_at > datetime.utcnow()
    ).all()
    return [session.to_dict() for session in sessions]
```

#### 3.2 项目信息缓存
```python
# 缓存项目基本信息，TTL: 30分钟
@cache_result(key=CACHE_KEYS['project_info'], ttl=1800)
def get_project_info(project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        return {
            'id': project.id,
            'name': project.name,
            'type': project.type.value,
            'status': project.status.value,
            'description': project.description,
            'user_id': project.user_id,
            'company_id': project.company_id,
            'metadata': project.metadata,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'completed_at': project.completed_at.isoformat() if project.completed_at else None
        }
    return None

# 缓存项目列表，TTL: 10分钟
@cache_result(key=CACHE_KEYS['project_list'], ttl=600)
def get_user_projects(user_id: int, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    projects = db.query(Project).filter(Project.user_id == user_id)\
        .order_by(Project.updated_at.desc())\
        .offset(offset).limit(size).all()
    
    total = db.query(Project).filter(Project.user_id == user_id).count()
    
    return {
        'items': [project.to_dict() for project in projects],
        'total': total,
        'page': page,
        'size': size,
        'pages': (total + size - 1) // size
    }
```

#### 3.3 文档内容缓存
```python
# 缓存文档基本信息，TTL: 30分钟
@cache_result(key=CACHE_KEYS['document_info'], ttl=1800)
def get_document_info(document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        return {
            'id': document.id,
            'title': document.title,
            'format': document.format.value,
            'status': document.status.value,
            'project_id': document.project_id,
            'metadata': document.metadata,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat()
        }
    return None

# 缓存文档内容，TTL: 1小时
@cache_result(key=CACHE_KEYS['document_content'], ttl=3600)
def get_document_content(document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        return {
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'format': document.format.value,
            'updated_at': document.updated_at.isoformat()
        }
    return None
```

#### 3.4 AI生成结果缓存
```python
# 缓存AI生成结果，TTL: 24小时
@cache_result(key=CACHE_KEYS['ai_generation'], ttl=86400)
def get_ai_generation(generation_id: int):
    generation = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
    if generation:
        return {
            'id': generation.id,
            'document_id': generation.document_id,
            'user_id': generation.user_id,
            'status': generation.status.value,
            'prompt': generation.prompt,
            'generated_content': generation.generated_content,
            'generation_config': generation.generation_config,
            'metadata': generation.metadata,
            'created_at': generation.created_at.isoformat(),
            'completed_at': generation.completed_at.isoformat() if generation.completed_at else None
        }
    return None
```

### 4. 缓存失效策略

#### 4.1 主动失效
```python
# 更新用户信息时清除相关缓存
def update_user_info(user_id: int, update_data: dict):
    # 更新数据库
    db.query(User).filter(User.id == user_id).update(update_data)
    db.commit()
    
    # 清除相关缓存
    cache_keys = [
        CACHE_KEYS['user_info'].format(user_id=user_id),
        CACHE_KEYS['user_sessions'].format(user_id=user_id),
        CACHE_KEYS['user_permissions'].format(user_id=user_id)
    ]
    redis_client.delete(*cache_keys)
    
    # 清除用户项目列表缓存
    pattern = CACHE_KEYS['project_list'].format(user_id=user_id, page='*', size='*')
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

# 更新文档内容时清除相关缓存
def update_document_content(document_id: int, content: str):
    # 更新数据库
    db.query(Document).filter(Document.id == document_id).update({'content': content})
    db.commit()
    
    # 清除相关缓存
    cache_keys = [
        CACHE_KEYS['document_info'].format(document_id=document_id),
        CACHE_KEYS['document_content'].format(document_id=document_id)
    ]
    redis_client.delete(*cache_keys)
    
    # 获取文档所属项目ID，清除项目相关缓存
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        project_cache_pattern = CACHE_KEYS['project_info'].format(project_id=document.project_id)
        redis_client.delete(project_cache_pattern)
```

#### 4.2 定时失效
```python
# 定时清理过期缓存
def clean_expired_cache():
    # 清理过期的用户会话缓存
    pattern = 'user:sessions:*'
    keys = redis_client.keys(pattern)
    for key in keys:
        if redis_client.ttl(key) == -1:  # 没有设置过期时间
            redis_client.expire(key, 3600)  # 设置1小时过期
    
    # 清理过期的AI生成结果缓存
    pattern = 'ai:generation:*'
    keys = redis_client.keys(pattern)
    for key in keys:
        data = redis_client.get(key)
        if data:
            generation = json.loads(data)
            if generation.get('status') == 'completed':
                # 已完成的生成结果保留24小时
                redis_client.expire(key, 86400)
            else:
                # 未完成的生成结果保留1小时
                redis_client.expire(key, 3600)
```

### 5. 缓存预热策略

```python
# 系统启动时预热热点数据
def warm_up_cache():
    # 预热活跃用户信息
    active_users = db.query(User).filter(
        User.is_active == True,
        User.last_login_at >= datetime.utcnow() - timedelta(days=7)
    ).limit(1000).all()
    
    for user in active_users:
        get_user_info(user.id)
        get_user_projects(user.id, 1, 20)
    
    # 预热最近更新的项目
    recent_projects = db.query(Project).filter(
        Project.updated_at >= datetime.utcnow() - timedelta(days=3)
    ).limit(500).all()
    
    for project in recent_projects:
        get_project_info(project.id)
    
    # 预热最近编辑的文档
    recent_documents = db.query(Document).filter(
        Document.updated_at >= datetime.utcnow() - timedelta(days=1)
    ).limit(1000).all()
    
    for document in recent_documents:
        get_document_info(document.id)
        if document.content and len(document.content) < 10000:  # 只缓存小文档
            get_document_content(document.id)

# 定时预热缓存
@schedule.every(6).hours.do
def scheduled_warm_up():
    warm_up_cache()
```

## 数据库连接池配置

### 1. SQLAlchemy连接池配置

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# 生产环境连接池配置
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,                    # 连接池大小
    max_overflow=30,                 # 最大溢出连接数
    pool_pre_ping=True,              # 连接前ping检查
    pool_recycle=3600,               # 连接回收时间（秒）
    pool_timeout=30,                 # 获取连接超时时间（秒）
    echo=False,                      # 生产环境关闭SQL日志
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30
    }
)

# 开发环境连接池配置
dev_engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=10,
    echo=True,                       # 开发环境开启SQL日志
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False
    }
)
```

### 2. 连接池监控

```python
# backend/app/core/pool_monitor.py
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# 连接池监控事件
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """连接建立时记录"""
    logger.debug(f"数据库连接已建立: {dbapi_connection}")

@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """连接从池中取出时记录"""
    logger.debug(f"从连接池获取连接: {dbapi_connection}")

@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """连接返回池中时记录"""
    logger.debug(f"连接返回连接池: {dbapi_connection}")

# 连接池状态监控
def get_pool_status():
    """获取连接池状态"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }

# 定时监控连接池状态
def monitor_pool_status():
    """定时监控连接池状态"""
    while True:
        status = get_pool_status()
        logger.info(f"连接池状态: {status}")
        
        # 检查连接池使用率
        usage_rate = status["checked_out"] / (status["pool_size"] + status["overflow"])
        if usage_rate > 0.8:
            logger.warning(f"连接池使用率过高: {usage_rate:.2%}")
        
        time.sleep(60)  # 每分钟检查一次
```

### 3. 连接池优化建议

1. **连接池大小设置**：
   - 生产环境：pool_size = CPU核心数 * 2 + 有效磁盘数
   - 开发环境：pool_size = 5-10
   - max_overflow = pool_size * 1.5

2. **连接回收时间**：
   - 生产环境：3600秒（1小时）
   - 开发环境：1800秒（30分钟）

3. **连接超时设置**：
   - 获取连接超时：30秒
   - 查询超时：30秒
   - 连接超时：10秒

4. **连接预热**：
```python
# 应用启动时预热连接池
def warm_up_connection_pool():
    """预热连接池"""
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    logger.info("连接池预热完成")
```

## 读写分离策略

### 1. 读写分离架构

```mermaid
graph TB
    A[应用服务器] --> B[数据库代理层]
    B --> C[MySQL主库]
    B --> D[MySQL从库1]
    B --> E[MySQL从库2]
    B --> F[MySQL从库3]
    
    C --> G[主库binlog]
    G --> D
    G --> E
    G --> F
    
    H[写操作] --> C
    I[读操作] --> D
    I --> E
    I --> F
```

### 2. 读写分离实现

#### 2.1 数据库配置
```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.config import settings

# 主库配置（写操作）
master_engine = create_engine(
    settings.MASTER_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30
)

# 从库配置（读操作）
slave_engines = [
    create_engine(
        url,
        pool_size=15,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30
    ) for url in settings.SLAVE_DATABASE_URLS
]

# 会话工厂
MasterSessionLocal = sessionmaker(bind=master_engine)
SlaveSessionLocals = [sessionmaker(bind=engine) for engine in slave_engines]
```

#### 2.2 读写分离路由
```python
# backend/app/core/database_router.py
import random
from typing import Generator
from sqlalchemy.orm import Session
from .database import MasterSessionLocal, SlaveSessionLocals

class DatabaseRouter:
    """数据库读写分离路由"""
    
    def __init__(self):
        self.current_slave_index = 0
    
    def get_master_session(self) -> Generator[Session, None, None]:
        """获取主库会话（写操作）"""
        session = MasterSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def get_slave_session(self) -> Generator[Session, None, None]:
        """获取从库会话（读操作）"""
        # 轮询负载均衡
        self.current_slave_index = (self.current_slave_index + 1) % len(SlaveSessionLocals)
        session_factory = SlaveSessionLocals[self.current_slave_index]
        session = session_factory()
        try:
            yield session
        finally:
            session.close()
    
    def get_read_session(self) -> Generator[Session, None, None]:
        """获取读会话（优先从从库读取）"""
        try:
            yield from self.get_slave_session()
        except Exception:
            # 从库不可用时，降级到主库
            yield from self.get_master_session()

# 全局路由实例
db_router = DatabaseRouter()
```

#### 2.3 读写分离装饰器
```python
# backend/app/core/database_decorators.py
from functools import wraps
from sqlalchemy.orm import Session
from .database_router import db_router

def read_operation(func):
    """读操作装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 将数据库会话替换为从库会话
        if 'db' in kwargs:
            original_db = kwargs['db']
            kwargs['db'] = next(db_router.get_read_session())
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                kwargs['db'].close()
                kwargs['db'] = original_db
        else:
            with next(db_router.get_read_session()) as db:
                kwargs['db'] = db
                return func(*args, **kwargs)
    return wrapper

def write_operation(func):
    """写操作装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 确保使用主库会话
        if 'db' in kwargs:
            original_db = kwargs['db']
            kwargs['db'] = next(db_router.get_master_session())
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                kwargs['db'].close()
                kwargs['db'] = original_db
        else:
            with next(db_router.get_master_session()) as db:
                kwargs['db'] = db
                return func(*args, **kwargs)
    return wrapper
```

#### 2.4 应用示例
```python
# backend/app/api/api_v1/endpoints/projects.py
from app.core.database_decorators import read_operation, write_operation

@read_operation
def get_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """获取项目列表（读操作）"""
    return db.query(Project).filter(Project.user_id == user_id)\
        .offset(skip).limit(limit).all()

@write_operation
def create_project(db: Session, project: ProjectCreate, user_id: int):
    """创建项目（写操作）"""
    db_project = Project(**project.dict(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@read_operation
def get_project(db: Session, project_id: int):
    """获取项目详情（读操作）"""
    return db.query(Project).filter(Project.id == project_id).first()

@write_operation
def update_project(db: Session, project_id: int, project_update: ProjectUpdate):
    """更新项目（写操作）"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project:
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        db.commit()
        db.refresh(db_project)
    return db_project
```

### 3. 主从同步监控

```python
# backend/app/core/replication_monitor.py
import time
import logging
from sqlalchemy import text
from .database import master_engine, slave_engines

logger = logging.getLogger(__name__)

def check_replication_lag():
    """检查主从同步延迟"""
    try:
        # 获取主库位置
        with master_engine.connect() as master_conn:
            master_result = master_conn.execute(text("SHOW MASTER STATUS"))
            master_status = master_result.fetchone()
            if not master_status:
                return None
            
            master_file, master_position = master_status[0], master_status[1]
        
        # 检查各从库同步状态
        lag_info = []
        for i, slave_engine in enumerate(slave_engines):
            try:
                with slave_engine.connect() as slave_conn:
                    # 获取从库同步状态
                    slave_result = slave_conn.execute(text("SHOW SLAVE STATUS"))
                    slave_status = slave_result.fetchone()
                    
                    if slave_status:
                        slave_file = slave_status[9]  # Relay_Master_Log_File
                        slave_position = slave_status[10]  # Exec_Master_Log_Pos
                        seconds_behind = slave_status[32]  # Seconds_Behind_Master
                        
                        lag_info.append({
                            'slave_id': i + 1,
                            'master_file': master_file,
                            'master_position': master_position,
                            'slave_file': slave_file,
                            'slave_position': slave_position,
                            'seconds_behind': seconds_behind,
                            'is_synced': (master_file == slave_file and 
                                        master_position == slave_position)
                        })
            except Exception as e:
                logger.error(f"检查从库 {i+1} 同步状态失败: {e}")
                lag_info.append({
                    'slave_id': i + 1,
                    'error': str(e),
                    'is_synced': False
                })
        
        return lag_info
    except Exception as e:
        logger.error(f"检查主从同步状态失败: {e}")
        return None

def monitor_replication():
    """定时监控主从同步"""
    while True:
        lag_info = check_replication_lag()
        if lag_info:
            for info in lag_info:
                if not info.get('is_synced', False):
                    logger.warning(f"从库 {info['slave_id']} 同步延迟: {info}")
                else:
                    logger.info(f"从库 {info['slave_id']} 同步正常")
        
        time.sleep(30)  # 每30秒检查一次
```

## 分库分表方案

### 1. 分库分表策略

#### 1.1 分库策略
根据业务特点和数据量，采用以下分库策略：

```mermaid
graph TB
    A[应用层] --> B[数据库路由层]
    B --> C[用户库<br/>user_db]
    B --> D[项目库<br/>project_db]
    B --> E[文档库<br/>document_db]
    B --> F[AI生成库<br/>ai_generation_db]
    B --> G[日志库<br/>log_db]
    
    C --> C1[用户表]
    C --> C2[用户会话表]
    C --> C3[企业表]
    
    D --> D1[项目表]
    D --> D2[项目表单表]
    D --> D3[表单字段表]
    
    E --> E1[文档表]
    E --> E2[文档版本表]
    E --> E3[文档导出表]
    
    F --> F1[AI生成记录表]
    F --> F2[AI生成模板表]
    
    G --> G1[操作日志表]
    G --> G2[系统日志表]
```

#### 1.2 分表策略
对于大表，采用水平分表策略：

```python
# backend/app/core/sharding_config.py

# 分表配置
SHARDING_CONFIG = {
    # 文档表按项目ID分表
    'documents': {
        'shard_key': 'project_id',
        'shard_count': 8,
        'table_pattern': 'documents_{shard_id}'
    },
    
    # 文档版本表按文档ID分表
    'document_versions': {
        'shard_key': 'document_id',
        'shard_count': 16,
        'table_pattern': 'document_versions_{shard_id}'
    },
    
    # AI生成记录表按用户ID分表
    'ai_generations': {
        'shard_key': 'user_id',
        'shard_count': 8,
        'table_pattern': 'ai_generations_{shard_id}'
    },
    
    # 用户会话表按用户ID分表
    'user_sessions': {
        'shard_key': 'user_id',
        'shard_count': 4,
        'table_pattern': 'user_sessions_{shard_id}'
    }
}
```

### 2. 分库分表实现

#### 2.1 数据库路由器
```python
# backend/app/core/sharding_router.py
from typing import Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .sharding_config import SHARDING_CONFIG

class ShardingRouter:
    """分库分表路由器"""
    
    def __init__(self):
        self.databases = {}
        self.sessions = {}
        self._init_databases()
    
    def _init_databases(self):
        """初始化数据库连接"""
        # 初始化各数据库连接
        db_configs = {
            'user_db': 'mysql://user:pass@localhost/user_db',
            'project_db': 'mysql://user:pass@localhost/project_db',
            'document_db': 'mysql://user:pass@localhost/document_db',
            'ai_generation_db': 'mysql://user:pass@localhost/ai_generation_db',
            'log_db': 'mysql://user:pass@localhost/log_db'
        }
        
        for db_name, db_url in db_configs.items():
            engine = create_engine(db_url, pool_size=10, max_overflow=20)
            self.databases[db_name] = engine
            self.sessions[db_name] = sessionmaker(bind=engine)
    
    def get_database(self, table_name: str):
        """根据表名获取对应数据库"""
        if table_name in ['users', 'user_sessions', 'companies']:
            return self.databases['user_db']
        elif table_name in ['projects', 'project_forms', 'form_fields']:
            return self.databases['project_db']
        elif table_name in ['documents', 'document_versions', 'document_exports']:
            return self.databases['document_db']
        elif table_name in ['ai_generations', 'ai_templates']:
            return self.databases['ai_generation_db']
        elif table_name in ['operation_logs', 'system_logs']:
            return self.databases['log_db']
        else:
            return self.databases['user_db']  # 默认数据库
    
    def get_shard_table(self, table_name: str, shard_key_value: int) -> str:
        """获取分表名称"""
        if table_name not in SHARDING_CONFIG:
            return table_name
        
        config = SHARDING_CONFIG[table_name]
        shard_id = shard_key_value % config['shard_count']
        return config['table_pattern'].format(shard_id=shard_id)
    
    def get_session(self, table_name: str, shard_key_value: int = None):
        """获取数据库会话"""
        db_engine = self.get_database(table_name)
        
        if table_name in SHARDING_CONFIG and shard_key_value is not None:
            # 分表会话
            session_factory = sessionmaker(bind=db_engine)
            return session_factory()
        else:
            # 普通会话
            db_name = None
            if table_name in ['users', 'user_sessions', 'companies']:
                db_name = 'user_db'
            elif table_name in ['projects', 'project_forms', 'form_fields']:
                db_name = 'project_db'
            elif table_name in ['documents', 'document_versions', 'document_exports']:
                db_name = 'document_db'
            elif table_name in ['ai_generations', 'ai_templates']:
                db_name = 'ai_generation_db'
            elif table_name in ['operation_logs', 'system_logs']:
                db_name = 'log_db'
            
            if db_name:
                return self.sessions[db_name]()
            else:
                return self.sessions['user_db']()

# 全局分片路由器
sharding_router = ShardingRouter()
```

#### 2.2 分表模型基类
```python
# backend/app/models/sharding_base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func
from ..core.sharding_router import sharding_router

ShardingBase = declarative_base()

class ShardingModel(ShardingBase):
    """分表模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    @classmethod
    def get_table_name(cls, shard_key_value: int) -> str:
        """获取分表名称"""
        return sharding_router.get_shard_table(cls.__tablename__, shard_key_value)
    
    @classmethod
    def get_session(cls, shard_key_value: int):
        """获取分表会话"""
        return sharding_router.get_session(cls.__tablename__, shard_key_value)
```

#### 2.3 分表模型实现
```python
# backend/app/models/sharding_models.py
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, Index, JSON, LongText
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .sharding_base import ShardingModel
from .document import DocumentFormat, DocumentStatus

class ShardedDocument(ShardingModel):
    """分表文档模型"""
    __tablename__ = "documents"
    
    project_id = Column(Integer, nullable=False, index=True, comment="所属项目ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(LongText, nullable=True, comment="文档内容")
    format = Column(Enum(DocumentFormat), default=DocumentFormat.MARKDOWN, nullable=False, comment="文档格式")
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False, comment="文档状态")
    metadata = Column(JSON, nullable=True, comment="文档元数据")
    
    # 索引
    __table_args__ = (
        Index('idx_documents_project_id', 'project_id'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_created_at', 'created_at'),
        Index('idx_documents_project_status', 'project_id', 'status'),
    )
    
    @classmethod
    def get_by_project_id(cls, project_id: int, document_id: int):
        """根据项目ID和文档ID获取文档"""
        session = cls.get_session(project_id)
        table_name = cls.get_table_name(project_id)
        
        # 动态映射到分表
        from sqlalchemy import Table
        document_table = Table(table_name, ShardingModel.metadata, autoload_with=session.bind)
        
        return session.query(document_table).filter(
            document_table.c.id == document_id,
            document_table.c.project_id == project_id
        ).first()

class ShardedDocumentVersion(ShardingModel):
    """分表文档版本模型"""
    __tablename__ = "document_versions"
    
    document_id = Column(Integer, nullable=False, index=True, comment="文档ID")
    version_number = Column(Integer, nullable=False, comment="版本号")
    content = Column(LongText, nullable=False, comment="版本内容")
    changes_summary = Column(JSON, nullable=True, comment="变更摘要")
    created_by = Column(Integer, nullable=False, comment="创建者ID")
    
    # 索引
    __table_args__ = (
        Index('idx_document_versions_document_id', 'document_id'),
        Index('idx_document_versions_version_number', 'document_id', 'version_number'),
    )
    
    @classmethod
    def get_by_document_id(cls, document_id: int, version_number: int = None):
        """根据文档ID获取版本"""
        session = cls.get_session(document_id)
        table_name = cls.get_table_name(document_id)
        
        # 动态映射到分表
        from sqlalchemy import Table
        version_table = Table(table_name, ShardingModel.metadata, autoload_with=session.bind)
        
        query = session.query(version_table).filter(
            version_table.c.document_id == document_id
        )
        
        if version_number is not None:
            query = query.filter(version_table.c.version_number == version_number)
        
        return query.order_by(version_table.c.version_number.desc()).all()
```

### 3. 分库分表迁移方案

#### 3.1 数据迁移脚本
```python
# backend/scripts/migrate_sharding.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.sharding_config import SHARDING_CONFIG

def create_shard_tables():
    """创建分表"""
    source_engine = create_engine(settings.DATABASE_URL)
    
    for table_name, config in SHARDING_CONFIG.items():
        for shard_id in range(config['shard_count']):
            shard_table_name = config['table_pattern'].format(shard_id=shard_id)
            
            # 创建分表SQL
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {shard_table_name} (
                LIKE {table_name} INCLUDING ALL
            )
            """
            
            try:
                with source_engine.connect() as conn:
                    conn.execute(text(create_sql))
                    conn.commit()
                print(f"创建分表成功: {shard_table_name}")
            except Exception as e:
                print(f"创建分表失败 {shard_table_name}: {e}")

def migrate_data_to_shards():
    """将数据迁移到分表"""
    source_engine = create_engine(settings.DATABASE_URL)
    
    for table_name, config in SHARDING_CONFIG.items():
        shard_key = config['shard_key']
        
        # 获取源表数据
        with source_engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            
            # 按分表分组数据
            shard_data = {}
            for row in rows:
                shard_key_value = getattr(row, shard_key)
                shard_id = shard_key_value % config['shard_count']
                shard_table_name = config['table_pattern'].format(shard_id=shard_id)
                
                if shard_table_name not in shard_data:
                    shard_data[shard_table_name] = []
                shard_data[shard_table_name].append(row)
            
            # 插入数据到分表
            for shard_table_name, data in shard_data.items():
                if data:
                    # 构建插入SQL
                    columns = data[0]._fields
                    placeholders = ', '.join(['%s'] * len(columns))
                    insert_sql = f"""
                    INSERT INTO {shard_table_name} ({', '.join(columns)})
                    VALUES ({placeholders})
                    """
                    
                    try:
                        with source_engine.connect() as conn:
                            for row in data:
                                conn.execute(text(insert_sql), tuple(row))
                            conn.commit()
                        print(f"迁移数据成功: {shard_table_name}, {len(data)} 条记录")
                    except Exception as e:
                        print(f"迁移数据失败 {shard_table_name}: {e}")

if __name__ == "__main__":
    print("开始创建分表...")
    create_shard_tables()
    
    print("开始迁移数据...")
    migrate_data_to_shards()
    
    print("分库分表迁移完成!")
```

#### 3.2 双写方案
```python
# backend/app/core/dual_write.py
from typing import Any, Dict
from sqlalchemy.orm import Session
from .sharding_router import sharding_router

class DualWriteManager:
    """双写管理器，用于平滑迁移"""
    
    def __init__(self, enable_dual_write: bool = True):
        self.enable_dual_write = enable_dual_write
    
    def write_to_both(self, table_name: str, data: Dict[str, Any], shard_key_value: int = None):
        """同时写入原表和分表"""
        if not self.enable_dual_write:
            return self.write_to_shard(table_name, data, shard_key_value)
        
        # 写入原表
        try:
            original_session = sharding_router.get_session(table_name)
            # 执行插入操作
            original_session.execute(f"INSERT INTO {table_name} ...")
            original_session.commit()
        except Exception as e:
            print(f"写入原表失败: {e}")
        
        # 写入分表
        try:
            self.write_to_shard(table_name, data, shard_key_value)
        except Exception as e:
            print(f"写入分表失败: {e}")
    
    def write_to_shard(self, table_name: str, data: Dict[str, Any], shard_key_value: int):
        """写入分表"""
        session = sharding_router.get_session(table_name, shard_key_value)
        table_name = sharding_router.get_shard_table(table_name, shard_key_value)
        
        # 执行插入操作
        session.execute(f"INSERT INTO {table_name} ...")
        session.commit()
    
    def read_from_shard(self, table_name: str, shard_key_value: int, query_conditions: Dict[str, Any]):
        """从分表读取"""
        session = sharding_router.get_session(table_name, shard_key_value)
        table_name = sharding_router.get_shard_table(table_name, shard_key_value)
        
        # 构建查询条件
        where_clause = " AND ".join([f"{k} = %s" for k in query_conditions.keys()])
        values = list(query_conditions.values())
        
        # 执行查询
        result = session.execute(f"SELECT * FROM {table_name} WHERE {where_clause}", values)
        return result.fetchall()

# 全局双写管理器
dual_write_manager = DualWriteManager(enable_dual_write=True)
```

## 慢查询优化

### 1. 慢查询监控

#### 1.1 MySQL慢查询配置
```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/log/mysql/mysql-slow.log';
SET GLOBAL long_query_time = 0.2; -- 记录执行时间超过200ms的查询
SET GLOBAL log_queries_not_using_indexes = 'ON'; -- 记录未使用索引的查询

-- 查看慢查询配置
SHOW VARIABLES LIKE '%slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
```

#### 1.2 慢查询分析工具
```python
# backend/app/core/slow_query_analyzer.py
import re
import json
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SlowQuery:
    """慢查询数据结构"""
    timestamp: datetime
    query_time: float
    lock_time: float
    rows_sent: int
    rows_examined: int
    database: str
    sql: str
    explain: Dict[str, Any] = None

class SlowQueryAnalyzer:
    """慢查询分析器"""
    
    def __init__(self, log_file: str = '/var/log/mysql/mysql-slow.log'):
        self.log_file = log_file
    
    def parse_slow_log(self) -> List[SlowQuery]:
        """解析慢查询日志"""
        slow_queries = []
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式解析慢查询日志
        query_pattern = r"""
            # Time: (\d{6}\s+\d{2}:\d{2}:\d{2})\n
            # User@Host: .*?\n
            # Query_time: (\d+\.\d+)\s+Lock_time: (\d+\.\d+)\s+Rows_sent: (\d+)\s+Rows_examined: (\d+)\n
            SET timestamp=\d+;\n
            (.*?)
            (?=\n# Time:|\nSET timestamp=|$)
        """
        
        matches = re.findall(query_pattern, content, re.VERBOSE | re.DOTALL)
        
        for match in matches:
            timestamp_str, query_time, lock_time, rows_sent, rows_examined, sql = match
            timestamp = datetime.strptime(timestamp_str, '%y%m%d %H:%M:%S')
            
            slow_query = SlowQuery(
                timestamp=timestamp,
                query_time=float(query_time),
                lock_time=float(lock_time),
                rows_sent=int(rows_sent),
                rows_examined=int(rows_examined),
                database='',  # 需要从SQL中提取
                sql=sql.strip()
            )
            
            slow_queries.append(slow_query)
        
        return slow_queries
    
    def analyze_query_patterns(self, slow_queries: List[SlowQuery]) -> Dict[str, Any]:
        """分析慢查询模式"""
        # 按SQL模板分组
        query_templates = {}
        
        for query in slow_queries:
            # 提取SQL模板（去除具体值）
            template = self.extract_query_template(query.sql)
            
            if template not in query_templates:
                query_templates[template] = {
                    'count': 0,
                    'total_time': 0,
                    'max_time': 0,
                    'avg_time': 0,
                    'total_rows_examined': 0,
                    'examples': []
                }
            
            query_templates[template]['count'] += 1
            query_templates[template]['total_time'] += query.query_time
            query_templates[template]['max_time'] = max(query_templates[template]['max_time'], query.query_time)
            query_templates[template]['total_rows_examined'] += query.rows_examined
            
            # 保留示例
            if len(query_templates[template]['examples']) < 3:
                query_templates[template]['examples'].append({
                    'timestamp': query.timestamp.isoformat(),
                    'query_time': query.query_time,
                    'sql': query.sql
                })
        
        # 计算平均时间
        for template, stats in query_templates.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
        
        # 按总时间排序
        sorted_templates = dict(sorted(
            query_templates.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        ))
        
        return sorted_templates
    
    def extract_query_template(self, sql: str) -> str:
        """提取SQL模板"""
        # 替换字符串字面量
        sql = re.sub(r"'[^']*'", "'?'", sql)
        sql = re.sub(r'"[^"]*"', "'?'", sql)
        
        # 替换数字
        sql = re.sub(r'\b\d+\b', '?', sql)
        
        # 标准化空白字符
        sql = re.sub(r'\s+', ' ', sql).strip()
        
        return sql
    
    def generate_optimization_suggestions(self, query_templates: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        
        for template, stats in query_templates.items():
            suggestion = {
                'template': template,
                'stats': stats,
                'recommendations': []
            }
            
            # 分析查询类型
            if 'SELECT' in template.upper():
                if 'rows_examined' in stats and stats['total_rows_examined'] > stats['count'] * 1000:
                    suggestion['recommendations'].append('检查是否缺少合适的索引')
                
                if 'JOIN' in template.upper():
                    suggestion['recommendations'].append('优化JOIN操作，确保连接字段有索引')
                
                if 'ORDER BY' in template.upper() and 'LIMIT' in template.upper():
                    suggestion['recommendations'].append('考虑使用覆盖索引优化ORDER BY + LIMIT查询')
                
                if 'GROUP BY' in template.upper():
                    suggestion['recommendations'].append('优化GROUP BY操作，考虑添加复合索引')
            
            elif 'INSERT' in template.upper():
                if stats['avg_time'] > 0.5:
                    suggestion['recommendations'].append('考虑批量插入或使用LOAD DATA INFILE')
            
            elif 'UPDATE' in template.upper() or 'DELETE' in template.upper():
                if stats['avg_time'] > 0.3:
                    suggestion['recommendations'].append('检查WHERE条件是否使用索引')
            
            if suggestion['recommendations']:
                suggestions.append(suggestion)
        
        return suggestions

# 使用示例
analyzer = SlowQueryAnalyzer()
slow_queries = analyzer.parse_slow_log()
query_patterns = analyzer.analyze_query_patterns(slow_queries)
suggestions = analyzer.generate_optimization_suggestions(query_patterns)
```

### 2. 慢查询优化案例

#### 2.1 项目列表查询优化
```sql
-- 优化前的慢查询
SELECT p.*, c.name as company_name, u.username as user_name,
       (SELECT COUNT(*) FROM documents WHERE project_id = p.id) as doc_count,
       (SELECT COUNT(*) FROM project_forms WHERE project_id = p.id) as form_count
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
WHERE p.user_id = 12345
ORDER BY p.updated_at DESC
LIMIT 20 OFFSET 0;

-- 执行计划分析
EXPLAIN FORMAT=JSON
SELECT p.*, c.name as company_name, u.username as user_name,
       (SELECT COUNT(*) FROM documents WHERE project_id = p.id) as doc_count,
       (SELECT COUNT(*) FROM project_forms WHERE project_id = p.id) as form_count
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
WHERE p.user_id = 12345
ORDER BY p.updated_at DESC
LIMIT 20 OFFSET 0;

-- 优化后的查询
SELECT p.id, p.name, p.type, p.status, p.description, p.created_at, p.updated_at,
       c.name as company_name,
       u.username as user_name,
       COALESCE(doc_counts.doc_count, 0) as documents_count,
       COALESCE(form_counts.form_count, 0) as forms_count
FROM projects p
LEFT JOIN companies c ON p.company_id = c.id
JOIN users u ON p.user_id = u.id
LEFT JOIN (
    SELECT project_id, COUNT(*) as doc_count
    FROM documents
    GROUP BY project_id
) doc_counts ON p.id = doc_counts.project_id
LEFT JOIN (
    SELECT project_id, COUNT(*) as form_count
    FROM project_forms
    GROUP BY project_id
) form_counts ON p.id = form_counts.project_id
WHERE p.user_id = 12345
ORDER BY p.updated_at DESC
LIMIT 20 OFFSET 0;

-- 添加优化索引
CREATE INDEX idx_projects_user_updated ON projects(user_id, updated_at DESC);
CREATE INDEX idx_documents_project_group ON documents(project_id);
CREATE INDEX idx_project_forms_project_group ON project_forms(project_id);
```

#### 2.2 文档搜索优化
```sql
-- 优化前的慢查询
SELECT d.*, p.name as project_name
FROM documents d
JOIN projects p ON d.project_id = p.id
WHERE p.user_id = 12345
AND (d.title LIKE '%关键词%' OR d.content LIKE '%关键词%')
ORDER BY d.updated_at DESC
LIMIT 20;

-- 优化后的查询（使用全文索引）
SELECT d.id, d.title, d.format, d.status, d.created_at, d.updated_at,
       p.name as project_name,
       MATCH(d.title, d.content) AGAINST('关键词' IN NATURAL LANGUAGE MODE) as relevance_score
FROM documents d
JOIN projects p ON d.project_id = p.id
WHERE p.user_id = 12345
AND MATCH(d.title, d.content) AGAINST('关键词' IN NATURAL LANGUAGE MODE)
ORDER BY relevance_score DESC, d.updated_at DESC
LIMIT 20;

-- 添加全文索引
CREATE FULLTEXT INDEX idx_documents_fulltext ON documents(title, content);
```

#### 2.3 AI生成记录查询优化
```sql
-- 优化前的慢查询
SELECT ag.*, d.title as document_title
FROM ai_generations ag
JOIN documents d ON ag.document_id = d.id
WHERE ag.user_id = 12345
AND ag.status = 'completed'
ORDER BY ag.created_at DESC
LIMIT 20;

-- 优化后的查询
SELECT ag.id, ag.status, ag.created_at, ag.completed_at,
       d.title as document_title
FROM ai_generations ag
JOIN documents d ON ag.document_id = d.id
WHERE ag.user_id = 12345
AND ag.status = 'completed'
ORDER BY ag.created_at DESC
LIMIT 20;

-- 添加优化索引
CREATE INDEX idx_ai_generations_user_status_created ON ai_generations(user_id, status, created_at DESC);
```

### 3. 慢查询监控告警

```python
# backend/app/core/slow_query_monitor.py
import time
import logging
from typing import Dict, Any
from sqlalchemy import text
from .database import engine

logger = logging.getLogger(__name__)

class SlowQueryMonitor:
    """慢查询监控器"""
    
    def __init__(self, threshold_seconds: float = 0.2):
        self.threshold_seconds = threshold_seconds
    
    def check_slow_queries(self) -> Dict[str, Any]:
        """检查慢查询"""
        with engine.connect() as conn:
            # 查询慢查询统计
            result = conn.execute(text("""
                SELECT 
                    DIGEST_TEXT as query_template,
                    COUNT_STAR as execution_count,
                    AVG_TIMER_WAIT/1000000000 as avg_time_seconds,
                    MAX_TIMER_WAIT/1000000000 as max_time_seconds,
                    SUM_ROWS_EXAMINED/COUNT_STAR as avg_rows_examined,
                    SUM_ROWS_SENT/COUNT_STAR as avg_rows_sent
                FROM performance_schema.events_statements_summary_by_digest 
                WHERE AVG_TIMER_WAIT/1000000000 > :threshold
                ORDER BY AVG_TIMER_WAIT DESC
                LIMIT 10
            """), {"threshold": self.threshold_seconds * 1000000000})
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'query_template': row.query_template,
                    'execution_count': row.execution_count,
                    'avg_time_seconds': row.avg_time_seconds,
                    'max_time_seconds': row.max_time_seconds,
                    'avg_rows_examined': row.avg_rows_examined,
                    'avg_rows_sent': row.avg_rows_sent
                })
            
            return {
                'threshold_seconds': self.threshold_seconds,
                'slow_queries': slow_queries,
                'total_slow_queries': len(slow_queries)
            }
    
    def check_index_usage(self) -> Dict[str, Any]:
        """检查索引使用情况"""
        with engine.connect() as conn:
            # 查询未使用索引的表
            result = conn.execute(text("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_ROWS
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
                AND TABLE_ROWS > 1000
                AND TABLE_NAME NOT IN (
                    SELECT DISTINCT TABLE_NAME 
                    FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = TABLES.TABLE_SCHEMA
                    AND INDEX_NAME != 'PRIMARY'
                )
            """))
            
            tables_without_indexes = []
            for row in result:
                tables_without_indexes.append({
                    'schema': row.TABLE_SCHEMA,
                    'table': row.TABLE_NAME,
                    'rows': row.TABLE_ROWS
                })
            
            return {
                'tables_without_indexes': tables_without_indexes,
                'total_tables': len(tables_without_indexes)
            }
    
    def send_alert(self, slow_queries: Dict[str, Any]):
        """发送慢查询告警"""
        if slow_queries['total_slow_queries'] > 0:
            alert_message = f"发现 {slow_queries['total_slow_queries']} 个慢查询:\n\n"
            
            for i, query in enumerate(slow_queries['slow_queries'][:5], 1):
                alert_message += f"{i}. 查询模板: {query['query_template'][:100]}...\n"
                alert_message += f"   执行次数: {query['execution_count']}\n"
                alert_message += f"   平均时间: {query['avg_time_seconds']:.3f}s\n"
                alert_message += f"   最大时间: {query['max_time_seconds']:.3f}s\n\n"
            
            logger.warning(alert_message)
            
            # 这里可以集成邮件、短信或其他告警方式
            # send_email_alert(alert_message)
            # send_slack_alert(alert_message)
    
    def monitor_loop(self):
        """监控循环"""
        while True:
            try:
                # 检查慢查询
                slow_queries = self.check_slow_queries()
                self.send_alert(slow_queries)
                
                # 检查索引使用情况
                index_usage = self.check_index_usage()
                if index_usage['total_tables'] > 0:
                    logger.warning(f"发现 {index_usage['total_tables']} 个表缺少索引")
                
                time.sleep(300)  # 每5分钟检查一次
                
            except Exception as e:
                logger.error(f"慢查询监控出错: {e}")
                time.sleep(60)  # 出错后1分钟重试

# 启动慢查询监控
def start_slow_query_monitor():
    monitor = SlowQueryMonitor(threshold_seconds=0.2)
    monitor.monitor_loop()
```

## 数据库参数调优

### 1. MySQL配置优化

#### 1.1 内存配置
```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf

# 基础内存配置
# 根据服务器内存大小调整，建议为物理内存的70-80%
innodb_buffer_pool_size = 4G          # InnoDB缓冲池大小
innodb_buffer_pool_instances = 4      # 缓冲池实例数（通常为CPU核心数）
innodb_log_buffer_size = 64M           # InnoDB日志缓冲区

# MyISAM内存配置
key_buffer_size = 256M                 # MyISAM索引缓冲区
myisam_sort_buffer_size = 64M         # MyISAM排序缓冲区

# 连接内存配置
read_buffer_size = 2M                  # 顺序读缓冲区
read_rnd_buffer_size = 8M              # 随机读缓冲区
sort_buffer_size = 4M                  # 排序缓冲区
join_buffer_size = 4M                  # 连接缓冲区
tmp_table_size = 256M                  # 临时表大小
max_heap_table_size = 256M             # 内存表最大大小
```

#### 1.2 连接配置
```ini
# 连接相关配置
max_connections = 500                   # 最大连接数
max_connect_errors = 1000              # 最大连接错误数
connect_timeout = 10                   # 连接超时时间
wait_timeout = 28800                   # 等待超时时间（8小时）
interactive_timeout = 28800            # 交互式超时时间

# 连接池配置
thread_cache_size = 50                 # 线程缓存大小
thread_stack = 256K                    # 线程栈大小
```

#### 1.3 InnoDB配置
```ini
# InnoDB引擎配置
innodb_file_per_table = 1              # 每表一个文件
innodb_flush_log_at_trx_commit = 2     # 事务日志刷新策略
innodb_log_file_size = 512M             # 日志文件大小
innodb_log_files_in_group = 2          # 日志文件组数量
innodb_flush_method = O_DIRECT          # 刷新方法
innodb_io_capacity = 2000               # I/O容量
innodb_io_capacity_max = 4000           # 最大I/O容量
innodb_read_io_threads = 8              # 读I/O线程数
innodb_write_io_threads = 8             # 写I/O线程数
innodb_thread_concurrency = 16          # 线程并发数
innodb_lock_wait_timeout = 50           # 锁等待超时时间
innodb_deadlock_detect = ON             # 死锁检测
```

#### 1.4 查询缓存配置
```ini
# 查询缓存配置（MySQL 8.0以下版本）
query_cache_type = 1                    # 查询缓存类型
query_cache_size = 256M                 # 查询缓存大小
query_cache_limit = 2M                  # 单个查询缓存限制
```

#### 1.5 日志配置
```ini
# 日志配置
log_error = /var/log/mysql/error.log    # 错误日志
slow_query_log = 1                      # 慢查询日志
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 0.2                   # 慢查询阈值
log_queries_not_using_indexes = 1       # 记录未使用索引的查询
log_throttle_queries_not_using_indexes = 10  # 限制记录频率

# 二进制日志配置
log_bin = /var/log/mysql/mysql-bin.log  # 二进制日志
binlog_format = ROW                     # 二进制日志格式
expire_logs_days = 7                    # 日志过期天数
max_binlog_size = 500M                 # 单个日志文件大小
```

### 2. 性能监控参数

```sql
-- 查看当前MySQL参数配置
SHOW VARIABLES;

-- 查看InnoDB状态
SHOW ENGINE INNODB STATUS;

-- 查看全局状态
SHOW GLOBAL STATUS;

-- 查看性能指标
SELECT 
    VARIABLE_NAME,
    VARIABLE_VALUE
FROM performance_schema.global_status 
WHERE VARIABLE_NAME IN (
    'Connections',
    'Threads_connected',
    'Threads_running',
    'Queries',
    'Questions',
    'Slow_queries',
    'Innodb_buffer_pool_read_requests',
    'Innodb_buffer_pool_reads',
    'Innodb_rows_read',
    'Innodb_rows_inserted',
    'Innodb_rows_updated',
    'Innodb_rows_deleted'
);
```

### 3. 参数调优脚本

```python
# backend/scripts/mysql_tuner.py
import subprocess
import re
from typing import Dict, Any

class MySQLTuner:
    """MySQL参数调优工具"""
    
    def __init__(self):
        self.server_memory = self.get_server_memory()
        self.current_config = self.get_mysql_config()
        self.current_status = self.get_mysql_status()
    
    def get_server_memory(self) -> int:
        """获取服务器内存大小（字节）"""
        try:
            result = subprocess.run(['free', '-b'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    parts = line.split()
                    return int(parts[1])
        except Exception:
            pass
        return 8 * 1024 * 1024 * 1024  # 默认8GB
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """获取MySQL当前配置"""
        config = {}
        try:
            result = subprocess.run(['mysql', '-e', 'SHOW VARIABLES;'], 
                                  capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # 跳过标题行
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        config[parts[0]] = parts[1]
        except Exception:
            pass
        return config
    
    def get_mysql_status(self) -> Dict[str, Any]:
        """获取MySQL状态"""
        status = {}
        try:
            result = subprocess.run(['mysql', '-e', 'SHOW GLOBAL STATUS;'], 
                                  capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # 跳过标题行
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status[parts[0]] = parts[1]
        except Exception:
            pass
        return status
    
    def analyze_buffer_pool(self) -> Dict[str, Any]:
        """分析缓冲池配置"""
        current_size = int(self.current_config.get('innodb_buffer_pool_size', 0))
        recommended_size = int(self.server_memory * 0.7)
        
        # 计算缓冲池命中率
        read_requests = int(self.current_status.get('Innodb_buffer_pool_read_requests', 0))
        reads = int(self.current_status.get('Innodb_buffer_pool_reads', 0))
        hit_rate = 1 - (reads / read_requests) if read_requests > 0 else 0
        
        return {
            'current_size_mb': current_size // (1024 * 1024),
            'recommended_size_mb': recommended_size // (1024 * 1024),
            'hit_rate': hit_rate,
            'is_optimal': current_size >= recommended_size * 0.8 and hit_rate > 0.95
        }
    
    def analyze_connections(self) -> Dict[str, Any]:
        """分析连接配置"""
        max_connections = int(self.current_config.get('max_connections', 0))
        threads_connected = int(self.current_status.get('Threads_connected', 0))
        connections = int(self.current_status.get('Connections', 0))
        
        # 计算连接使用率
        usage_rate = threads_connected / max_connections if max_connections > 0 else 0
        
        return {
            'max_connections': max_connections,
            'current_connections': threads_connected,
            'usage_rate': usage_rate,
            'total_connections': connections,
            'is_optimal': usage_rate < 0.8
        }
    
    def analyze_query_cache(self) -> Dict[str, Any]:
        """分析查询缓存"""
        query_cache_size = int(self.current_config.get('query_cache_size', 0))
        qcache_hits = int(self.current_status.get('Qcache_hits', 0))
        qcache_inserts = int(self.current_status.get('Qcache_inserts', 0))
        
        # 计算查询缓存命中率
        total_queries = qcache_hits + qcache_inserts
        hit_rate = qcache_hits / total_queries if total_queries > 0 else 0
        
        return {
            'cache_size_mb': query_cache_size // (1024 * 1024),
            'hit_rate': hit_rate,
            'is_enabled': query_cache_size > 0,
            'is_optimal': hit_rate > 0.2 if query_cache_size > 0 else True
        }
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """生成优化建议"""
        recommendations = []
        
        # 分析缓冲池
        buffer_pool = self.analyze_buffer_pool()
        if not buffer_pool['is_optimal']:
            if buffer_pool['current_size_mb'] < buffer_pool['recommended_size_mb'] * 0.8:
                recommendations.append({
                    'parameter': 'innodb_buffer_pool_size',
                    'current': f"{buffer_pool['current_size_mb']}M",
                    'recommended': f"{buffer_pool['recommended_size_mb']}M",
                    'reason': '缓冲池大小不足，建议增加以提高性能'
                })
            elif buffer_pool['hit_rate'] < 0.95:
                recommendations.append({
                    'parameter': 'innodb_buffer_pool_size',
                    'current': f"{buffer_pool['current_size_mb']}M",
                    'recommended': f"{buffer_pool['current_size_mb'] * 1.5}M",
                    'reason': f'缓冲池命中率较低({buffer_pool["hit_rate"]:.2%})，建议增加缓冲池大小'
                })
        
        # 分析连接
        connections = self.analyze_connections()
        if not connections['is_optimal']:
            if connections['usage_rate'] > 0.8:
                recommendations.append({
                    'parameter': 'max_connections',
                    'current': connections['max_connections'],
                    'recommended': connections['max_connections'] * 2,
                    'reason': f'连接使用率过高({connections["usage_rate"]:.2%})，建议增加最大连接数'
                })
        
        # 分析查询缓存
        query_cache = self.analyze_query_cache()
        if query_cache['is_enabled'] and not query_cache['is_optimal']:
            if query_cache['hit_rate'] < 0.2:
                recommendations.append({
                    'parameter': 'query_cache_size',
                    'current': f"{query_cache['cache_size_mb']}M",
                    'recommended': '0',
                    'reason': f'查询缓存命中率过低({query_cache["hit_rate"]:.2%})，建议禁用查询缓存'
                })
        
        return {
            'server_memory_gb': self.server_memory // (1024 * 1024 * 1024),
            'buffer_pool': buffer_pool,
            'connections': connections,
            'query_cache': query_cache,
            'recommendations': recommendations
        }

if __name__ == "__main__":
    tuner = MySQLTuner()
    analysis = tuner.generate_recommendations()
    
    print("MySQL性能分析结果:")
    print(f"服务器内存: {analysis['server_memory_gb']}GB")
    print(f"缓冲池命中率: {analysis['buffer_pool']['hit_rate']:.2%}")
    print(f"连接使用率: {analysis['connections']['usage_rate']:.2%}")
    
    if analysis['recommendations']:
        print("\n优化建议:")
        for rec in analysis['recommendations']:
            print(f"- {rec['parameter']}: {rec['current']} -> {rec['recommended']}")
            print(f"  原因: {rec['reason']}")
    else:
        print("\n当前配置已优化，无需调整")
```

## 性能监控指标

### 1. 数据库性能指标

#### 1.1 基础性能指标
```python
# backend/app/core/performance_monitor.py
import time
import psutil
from typing import Dict, Any, List
from sqlalchemy import text
from .database import engine

class DatabasePerformanceMonitor:
    """数据库性能监控器"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 1000
    
    def collect_basic_metrics(self) -> Dict[str, Any]:
        """收集基础性能指标"""
        with engine.connect() as conn:
            # 连接数指标
            connections_result = conn.execute(text("""
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_status 
                WHERE VARIABLE_NAME IN (
                    'Threads_connected',
                    'Threads_running',
                    'Connections',
                    'Max_used_connections'
                )
            """))
            
            connection_metrics = {row.VARIABLE_NAME: int(row.VARIABLE_VALUE) 
                               for row in connections_result}
            
            # 查询指标
            query_result = conn.execute(text("""
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_status 
                WHERE VARIABLE_NAME IN (
                    'Queries',
                    'Questions',
                    'Slow_queries',
                    'Com_select',
                    'Com_insert',
                    'Com_update',
                    'Com_delete'
                )
            """))
            
            query_metrics = {row.VARIABLE_NAME: int(row.VARIABLE_VALUE) 
                           for row in query_result}
            
            # InnoDB指标
            innodb_result = conn.execute(text("""
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_status 
                WHERE VARIABLE_NAME IN (
                    'Innodb_buffer_pool_read_requests',
                    'Innodb_buffer_pool_reads',
                    'Innodb_rows_read',
                    'Innodb_rows_inserted',
                    'Innodb_rows_updated',
                    'Innodb_rows_deleted',
                    'Innodb_row_lock_time',
                    'Innodb_row_lock_waits'
                )
            """))
            
            innodb_metrics = {row.VARIABLE_NAME: int(row.VARIABLE_VALUE) 
                            for row in innodb_result}
            
            # 计算衍生指标
            buffer_pool_hit_rate = 1 - (innodb_metrics['Innodb_buffer_pool_reads'] / 
                                       innodb_metrics['Innodb_buffer_pool_read_requests']) \
                if innodb_metrics['Innodb_buffer_pool_read_requests'] > 0 else 0
            
            return {
                'timestamp': time.time(),
                'connections': {
                    'connected': connection_metrics.get('Threads_connected', 0),
                    'running': connection_metrics.get('Threads_running', 0),
                    'total': connection_metrics.get('Connections', 0),
                    'max_used': connection_metrics.get('Max_used_connections', 0)
                },
                'queries': {
                    'total': query_metrics.get('Queries', 0),
                    'questions': query_metrics.get('Questions', 0),
                    'slow': query_metrics.get('Slow_queries', 0),
                    'select': query_metrics.get('Com_select', 0),
                    'insert': query_metrics.get('Com_insert', 0),
                    'update': query_metrics.get('Com_update', 0),
                    'delete': query_metrics.get('Com_delete', 0)
                },
                'innodb': {
                    'buffer_pool_hit_rate': buffer_pool_hit_rate,
                    'rows_read': innodb_metrics.get('Innodb_rows_read', 0),
                    'rows_inserted': innodb_metrics.get('Innodb_rows_inserted', 0),
                    'rows_updated': innodb_metrics.get('Innodb_rows_updated', 0),
                    'rows_deleted': innodb_metrics.get('Innodb_rows_deleted', 0),
                    'row_lock_time': innodb_metrics.get('Innodb_row_lock_time', 0),
                    'row_lock_waits': innodb_metrics.get('Innodb_row_lock_waits', 0)
                }
            }
    
    def collect_table_metrics(self) -> List[Dict[str, Any]]:
        """收集表级别指标"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    TABLE_ROWS,
                    DATA_LENGTH,
                    INDEX_LENGTH,
                    DATA_FREE
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
                ORDER BY DATA_LENGTH DESC
                LIMIT 20
            """))
            
            table_metrics = []
            for row in result:
                table_metrics.append({
                    'schema': row.TABLE_SCHEMA,
                    'table': row.TABLE_NAME,
                    'rows': row.TABLE_ROWS or 0,
                    'data_size_mb': (row.DATA_LENGTH or 0) // (1024 * 1024),
                    'index_size_mb': (row.INDEX_LENGTH or 0) // (1024 * 1024),
                    'free_space_mb': (row.DATA_FREE or 0) // (1024 * 1024)
                })
            
            return table_metrics
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 网络I/O
        network = psutil.net_io_counters()
        
        return {
            'cpu': {
                'usage_percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'total_gb': memory.total // (1024 ** 3),
                'available_gb': memory.available // (1024 ** 3),
                'usage_percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total // (1024 ** 3),
                'free_gb': disk.free // (1024 ** 3),
                'usage_percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        }
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有指标"""
        return {
            'database': self.collect_basic_metrics(),
            'tables': self.collect_table_metrics(),
            'system': self.collect_system_metrics()
        }
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """存储指标数据"""
        self.metrics_history.append(metrics)
        
        # 限制历史数据大小
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """获取指标摘要"""
        # 获取指定时间范围内的指标
        current_time = time.time()
        time_threshold = current_time - (hours * 3600)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if m['database']['timestamp'] > time_threshold
        ]
        
        if not recent_metrics:
            return {}
        
        # 计算平均值、最大值、最小值
        avg_connections = sum(m['database']['connections']['connected'] 
                            for m in recent_metrics) / len(recent_metrics)
        max_connections = max(m['database']['connections']['connected'] 
                            for m in recent_metrics)
        
        avg_buffer_pool_hit_rate = sum(m['database']['innodb']['buffer_pool_hit_rate'] 
                                     for m in recent_metrics) / len(recent_metrics)
        min_buffer_pool_hit_rate = min(m['database']['innodb']['buffer_pool_hit_rate'] 
                                     for m in recent_metrics)
        
        avg_slow_queries = sum(m['database']['queries']['slow'] 
                             for m in recent_metrics) / len(recent_metrics)
        
        return {
            'time_range_hours': hours,
            'sample_count': len(recent_metrics),
            'connections': {
                'average': avg_connections,
                'maximum': max_connections
            },
            'buffer_pool_hit_rate': {
                'average': avg_buffer_pool_hit_rate,
                'minimum': min_buffer_pool_hit_rate
            },
            'slow_queries': {
                'average': avg_slow_queries
            }
        }
```

#### 1.2 告警规则配置
```python
# backend/app/core/alert_rules.py
from typing import Dict, Any, List
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertRule:
    """告警规则"""
    
    def __init__(self, name: str, level: AlertLevel, condition: str, message: str):
        self.name = name
        self.level = level
        self.condition = condition
        self.message = message
    
    def evaluate(self, metrics: Dict[str, Any]) -> bool:
        """评估告警条件"""
        # 简单的条件评估实现
        # 实际应用中可以使用更复杂的表达式解析器
        try:
            return eval(self.condition, {"__builtins__": {}}, metrics)
        except Exception:
            return False

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules = self._init_rules()
        self.active_alerts = []
    
    def _init_rules(self) -> List[AlertRule]:
        """初始化告警规则"""
        return [
            # 连接数告警
            AlertRule(
                name="high_connections",
                level=AlertLevel.WARNING,
                condition="metrics['database']['connections']['connected'] > metrics['database']['connections']['max_used'] * 0.8",
                message="数据库连接数过高，当前值: {connected}, 最大值: {max_used}"
            ),
            
            # 缓冲池命中率告警
            AlertRule(
                name="low_buffer_pool_hit_rate",
                level=AlertLevel.WARNING,
                condition="metrics['database']['innodb']['buffer_pool_hit_rate'] < 0.95",
                message="InnoDB缓冲池命中率过低，当前值: {buffer_pool_hit_rate:.2%}"
            ),
            
            # 慢查询告警
            AlertRule(
                name="high_slow_queries",
                level=AlertLevel.CRITICAL,
                condition="metrics['database']['queries']['slow'] > 100",
                message="慢查询数量过多，当前值: {slow}"
            ),
            
            # CPU使用率告警
            AlertRule(
                name="high_cpu_usage",
                level=AlertLevel.WARNING,
                condition="metrics['system']['cpu']['usage_percent'] > 80",
                message="CPU使用率过高，当前值: {cpu_usage:.1f}%"
            ),
            
            # 内存使用率告警
            AlertRule(
                name="high_memory_usage",
                level=AlertLevel.CRITICAL,
                condition="metrics['system']['memory']['usage_percent'] > 90",
                message="内存使用率过高，当前值: {memory_usage:.1f}%"
            ),
            
            # 磁盘使用率告警
            AlertRule(
                name="high_disk_usage",
                level=AlertLevel.WARNING,
                condition="metrics['system']['disk']['usage_percent'] > 85",
                message="磁盘使用率过高，当前值: {disk_usage:.1f}%"
            )
        ]
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警"""
        triggered_alerts = []
        
        for rule in self.rules:
            if rule.evaluate(metrics):
                alert = {
                    'name': rule.name,
                    'level': rule.level.value,
                    'message': rule.message.format(**self._flatten_metrics(metrics)),
                    'timestamp': metrics['database']['timestamp']
                }
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def _flatten_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """扁平化指标字典"""
        flattened = {}
        
        def _flatten(obj, prefix=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _flatten(v, f"{prefix}{k}_")
            else:
                flattened[prefix.rstrip('_')] = obj
        
        _flatten(metrics)
        return flattened
```

### 2. 监控仪表板

```python
# backend/app/api/monitoring.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from ..core.performance_monitor import DatabasePerformanceMonitor
from ..core.alert_rules import AlertManager

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# 全局监控器实例
performance_monitor = DatabasePerformanceMonitor()
alert_manager = AlertManager()

@router.get("/metrics/current")
async def get_current_metrics():
    """获取当前性能指标"""
    metrics = performance_monitor.collect_all_metrics()
    performance_monitor.store_metrics(metrics)
    
    # 检查告警
    alerts = alert_manager.check_alerts(metrics)
    
    return {
        "metrics": metrics,
        "alerts": alerts,
        "timestamp": metrics['database']['timestamp']
    }

@router.get("/metrics/summary")
async def get_metrics_summary(hours: int = 1):
    """获取指标摘要"""
    summary = performance_monitor.get_metrics_summary(hours)
    return summary

@router.get("/metrics/history")
async def get_metrics_history(hours: int = 24):
    """获取历史指标"""
    current_time = time.time()
    time_threshold = current_time - (hours * 3600)
    
    history = [
        m for m in performance_monitor.metrics_history 
        if m['database']['timestamp'] > time_threshold
    ]
    
    return {
        "time_range_hours": hours,
        "data_points": len(history),
        "history": history
    }

@router.get("/tables/metrics")
async def get_table_metrics():
    """获取表级别指标"""
    return performance_monitor.collect_table_metrics()

@router.get("/alerts/rules")
async def get_alert_rules():
    """获取告警规则"""
    return [
        {
            "name": rule.name,
            "level": rule.level.value,
            "condition": rule.condition,
            "message": rule.message
        }
        for rule in alert_manager.rules
    ]

@router.get("/alerts/active")
async def get_active_alerts():
    """获取活跃告警"""
    if not performance_monitor.metrics_history:
        return {"alerts": []}
    
    latest_metrics = performance_monitor.metrics_history[-1]
    alerts = alert_manager.check_alerts(latest_metrics)
    
    return {"alerts": alerts}
```

## 索引维护和监控

### 1. 索引使用情况监控

```python
# backend/app/core/index_monitor.py
from typing import Dict, Any, List
from sqlalchemy import text
from .database import engine

class IndexMonitor:
    """索引监控器"""
    
    def get_unused_indexes(self) -> List[Dict[str, Any]]:
        """获取未使用的索引"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    OBJECT_SCHEMA,
                    OBJECT_NAME,
                    INDEX_NAME
                FROM performance_schema.table_io_waits_summary_by_index_usage
                WHERE INDEX_NAME IS NOT NULL
                AND COUNT_STAR = 0
                AND OBJECT_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
            """))
            
            unused_indexes = []
            for row in result:
                unused_indexes.append({
                    'schema': row.OBJECT_SCHEMA,
                    'table': row.OBJECT_NAME,
                    'index': row.INDEX_NAME
                })
            
            return unused_indexes
    
    def get_index_usage_stats(self) -> List[Dict[str, Any]]:
        """获取索引使用统计"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    OBJECT_SCHEMA,
                    OBJECT_NAME,
                    INDEX_NAME,
                    COUNT_STAR as usage_count,
                    SUM_TIMER_WAIT/1000000000 as total_time_seconds,
                    AVG_TIMER_WAIT/1000000000 as avg_time_seconds
                FROM performance_schema.table_io_waits_summary_by_index_usage
                WHERE INDEX_NAME IS NOT NULL
                AND OBJECT_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
                ORDER BY COUNT_STAR DESC
                LIMIT 50
            """))
            
            index_stats = []
            for row in result:
                index_stats.append({
                    'schema': row.OBJECT_SCHEMA,
                    'table': row.OBJECT_NAME,
                    'index': row.INDEX_NAME,
                    'usage_count': row.usage_count,
                    'total_time_seconds': row.total_time_seconds,
                    'avg_time_seconds': row.avg_time_seconds
                })
            
            return index_stats
    
    def get_index_cardinality(self) -> List[Dict[str, Any]]:
        """获取索引基数"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    INDEX_NAME,
                    COLUMN_NAME,
                    CARDINALITY
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
                ORDER BY TABLE_SCHEMA, TABLE_NAME, SEQ_IN_INDEX
            """))
            
            cardinality_info = []
            for row in result:
                cardinality_info.append({
                    'schema': row.TABLE_SCHEMA,
                    'table': row.TABLE_NAME,
                    'index': row.INDEX_NAME,
                    'column': row.COLUMN_NAME,
                    'cardinality': row.CARDINALITY
                })
            
            return cardinality_info
    
    def analyze_index_efficiency(self) -> Dict[str, Any]:
        """分析索引效率"""
        unused_indexes = self.get_unused_indexes()
        index_stats = self.get_index_usage_stats()
        cardinality_info = self.get_index_cardinality()
        
        # 计算索引效率指标
        total_indexes = len(index_stats)
        unused_count = len(unused_indexes)
        usage_rate = (total_indexes - unused_count) / total_indexes if total_indexes > 0 else 0
        
        # 找出低效索引（使用次数少但基数高）
        inefficient_indexes = []
        for stat in index_stats:
            if stat['usage_count'] < 100:  # 使用次数少
                # 查找对应的基数信息
                for card in cardinality_info:
                    if (card['schema'] == stat['schema'] and 
                        card['table'] == stat['table'] and 
                        card['index'] == stat['index']):
                        if card['cardinality'] > 1000:  # 基数高
                            inefficient_indexes.append({
                                'schema': stat['schema'],
                                'table': stat['table'],
                                'index': stat['index'],
                                'usage_count': stat['usage_count'],
                                'cardinality': card['cardinality']
                            })
                        break
        
        return {
            'total_indexes': total_indexes,
            'unused_indexes': unused_count,
            'usage_rate': usage_rate,
            'unused_index_list': unused_indexes,
            'inefficient_indexes': inefficient_indexes
        }
```

### 2. 索引维护任务

```python
# backend/app/core/index_maintenance.py
import logging
from typing import List, Dict, Any
from sqlalchemy import text
from .database import engine

logger = logging.getLogger(__name__)

class IndexMaintenance:
    """索引维护工具"""
    
    def rebuild_fragmented_indexes(self, fragmentation_threshold: float = 10.0) -> List[Dict[str, Any]]:
        """重建碎片化的索引"""
        with engine.connect() as conn:
            # 获取索引碎片信息
            result = conn.execute(text("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    INDEX_NAME,
                    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS size_mb,
                    ROUND((DATA_FREE / 1024 / 1024), 2) AS free_mb,
                    ROUND((DATA_FREE / (DATA_LENGTH + INDEX_LENGTH)) * 100, 2) AS fragmentation_percent
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
                AND DATA_FREE > 0
                HAVING fragmentation_percent > :threshold
                ORDER BY fragmentation_percent DESC
            """), {"threshold": fragmentation_threshold})
            
            fragmented_tables = []
            for row in result:
                fragmented_tables.append({
                    'schema': row.TABLE_SCHEMA,
                    'table': row.TABLE_NAME,
                    'size_mb': row.size_mb,
                    'free_mb': row.free_mb,
                    'fragmentation_percent': row.fragmentation_percent
                })
            
            # 重建表以消除碎片
            rebuilt_tables = []
            for table in fragmented_tables:
                try:
                    # 使用OPTIMIZE TABLE重建表
                    optimize_sql = f"OPTIMIZE TABLE `{table['schema']}`.`{table['table']}`"
                    conn.execute(text(optimize_sql))
                    conn.commit()
                    
                    rebuilt_tables.append(table)
                    logger.info(f"已优化表: {table['schema']}.{table['table']}")
                    
                except Exception as e:
                    logger.error(f"优化表失败 {table['schema']}.{table['table']}: {e}")
            
            return rebuilt_tables
    
    def update_table_statistics(self) -> List[str]:
        """更新表统计信息"""
        with engine.connect() as conn:
            # 获取所有表
            result = conn.execute(text("""
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
                AND TABLE_TYPE = 'BASE TABLE'
            """))
            
            updated_tables = []
            for row in result:
                try:
                    # 更新表统计信息
                    analyze_sql = f"ANALYZE TABLE `{row.TABLE_SCHEMA}`.`{row.TABLE_NAME}`"
                    conn.execute(text(analyze_sql))
                    conn.commit()
                    
                    updated_tables.append(f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}")
                    logger.info(f"已更新统计信息: {row.TABLE_SCHEMA}.{row.TABLE_NAME}")
                    
                except Exception as e:
                    logger.error(f"更新统计信息失败 {row.TABLE_SCHEMA}.{row.TABLE_NAME}: {e}")
            
            return updated_tables
    
    def drop_unused_indexes(self, dry_run: bool = True) -> List[Dict[str, Any]]:
        """删除未使用的索引"""
        from .index_monitor import IndexMonitor
        
        monitor = IndexMonitor()
        unused_indexes = monitor.get_unused_indexes()
        
        dropped_indexes = []
        for index in unused_indexes:
            # 跳过主键索引
            if index['index'] == 'PRIMARY':
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] 将删除索引: {index['schema']}.{index['table']}.{index['index']}")
                dropped_indexes.append(index)
            else:
                try:
                    # 删除索引
                    drop_sql = f"DROP INDEX `{index['index']}` ON `{index['schema']}`.`{index['table']}`"
                    with engine.connect() as conn:
                        conn.execute(text(drop_sql))
                        conn.commit()
                    
                    dropped_indexes.append(index)
                    logger.info(f"已删除索引: {index['schema']}.{index['table']}.{index['index']}")
                    
                except Exception as e:
                    logger.error(f"删除索引失败 {index['schema']}.{index['table']}.{index['index']}: {e}")
        
        return dropped_indexes
    
    def create_missing_indexes(self) -> List[Dict[str, Any]]:
        """创建缺失的索引"""
        # 这里可以根据查询模式分析，自动创建缺失的索引
        # 简化实现，实际应用中需要更复杂的分析逻辑
        
        missing_indexes = []
        
        # 检查外键索引
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    COLUMN_NAME,
                    CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE REFERENCED_TABLE_NAME IS NOT NULL
                AND TABLE_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
                AND CONSTRAINT_NAME NOT IN (
                    SELECT INDEX_NAME 
                    FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = TABLE_SCHEMA 
                    AND TABLE_NAME = TABLE_NAME
                )
            """))
            
            for row in result:
                index_name = f"idx_{row.TABLE_NAME}_{row.COLUMN_NAME}"
                create_sql = f"""
                CREATE INDEX `{index_name}` 
                ON `{row.TABLE_SCHEMA}`.`{row.TABLE_NAME}` (`{row.COLUMN_NAME}`)
                """
                
                try:
                    conn.execute(text(create_sql))
                    conn.commit()
                    
                    missing_indexes.append({
                        'schema': row.TABLE_SCHEMA,
                        'table': row.TABLE_NAME,
                        'column': row.COLUMN_NAME,
                        'index_name': index_name,
                        'type': 'foreign_key'
                    })
                    
                    logger.info(f"已创建外键索引: {index_name}")
                    
                except Exception as e:
                    logger.error(f"创建外键索引失败 {index_name}: {e}")
        
        return missing_indexes
```

### 3. 索引维护调度

```python
# backend/app/tasks/index_tasks.py
import schedule
import time
import logging
from ..core.index_maintenance import IndexMaintenance
from ..core.index_monitor import IndexMonitor

logger = logging.getLogger(__name__)

def run_index_maintenance():
    """运行索引维护任务"""
    maintenance = IndexMaintenance()
    monitor = IndexMonitor()
    
    try:
        # 1. 分析索引效率
        logger.info("开始分析索引效率...")
        efficiency = monitor.analyze_index_efficiency()
        logger.info(f"索引效率分析完成: 总索引数={efficiency['total_indexes']}, "
                   f"未使用索引数={efficiency['unused_indexes']}, "
                   f"使用率={efficiency['usage_rate']:.2%}")
        
        # 2. 重建碎片化索引
        logger.info("开始重建碎片化索引...")
        rebuilt_tables = maintenance.rebuild_fragmented_indexes(fragmentation_threshold=10.0)
        logger.info(f"重建碎片化索引完成: {len(rebuilt_tables)} 个表")
        
        # 3. 更新表统计信息
        logger.info("开始更新表统计信息...")
        updated_tables = maintenance.update_table_statistics()
        logger.info(f"更新表统计信息完成: {len(updated_tables)} 个表")
        
        # 4. 创建缺失索引
        logger.info("开始创建缺失索引...")
        created_indexes = maintenance.create_missing_indexes()
        logger.info(f"创建缺失索引完成: {len(created_indexes)} 个索引")
        
        # 5. 删除未使用索引（先进行干运行）
        logger.info("开始分析未使用索引...")
        unused_indexes = maintenance.drop_unused_indexes(dry_run=True)
        logger.info(f"发现未使用索引: {len(unused_indexes)} 个")
        
        # 记录维护结果
        maintenance_result = {
            'timestamp': time.time(),
            'efficiency': efficiency,
            'rebuilt_tables': len(rebuilt_tables),
            'updated_tables': len(updated_tables),
            'created_indexes': len(created_indexes),
            'unused_indexes': len(unused_indexes)
        }
        
        return maintenance_result
        
    except Exception as e:
        logger.error(f"索引维护任务失败: {e}")
        return None

def schedule_index_maintenance():
    """调度索引维护任务"""
    # 每周日凌晨2点执行完整索引维护
    schedule.every().sunday.at("02:00").do(run_index_maintenance)
    
    # 每天凌晨4点更新表统计信息
    maintenance = IndexMaintenance()
    schedule.every().day.at("04:00").do(maintenance.update_table_statistics)
    
    # 每小时检查索引效率
    monitor = IndexMonitor()
    schedule.every().hour.do(monitor.analyze_index_efficiency)
    
    logger.info("索引维护任务已调度")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_index_maintenance()
```

## 定期维护任务

### 1. 数据清理任务

```python
# backend/app/tasks/data_cleanup.py
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from ..core.database import engine

logger = logging.getLogger(__name__)

class DataCleanup:
    """数据清理工具"""
    
    def __init__(self):
        self.engine = engine
    
    def clean_expired_sessions(self, days: int = 30) -> int:
        """清理过期用户会话"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM user_sessions 
                WHERE expires_at < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            deleted_count = result.rowcount
            conn.commit()
            
            logger.info(f"清理过期会话: {deleted_count} 条记录")
            return deleted_count
    
    def clean_old_ai_generations(self, days: int = 90) -> int:
        """清理旧的AI生成记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM ai_generations 
                WHERE created_at < :cutoff_date 
                AND status = 'completed'
            """), {"cutoff_date": cutoff_date})
            
            deleted_count = result.rowcount
            conn.commit()
            
            logger.info(f"清理旧AI生成记录: {deleted_count} 条记录")
            return deleted_count
    
    def clean_old_document_versions(self, keep_versions: int = 10) -> int:
        """清理旧的文档版本，只保留最近的N个版本"""
        with self.engine.connect() as conn:
            # 获取需要清理的文档ID
            result = conn.execute(text("""
                SELECT document_id 
                FROM document_versions 
                GROUP BY document_id 
                HAVING COUNT(*) > :keep_versions
            """), {"keep_versions": keep_versions})
            
            document_ids = [row.document_id for row in result]
            deleted_count = 0
            
            for doc_id in document_ids:
                # 获取需要保留的版本号
                result = conn.execute(text("""
                    SELECT version_number 
                    FROM document_versions 
                    WHERE document_id = :doc_id 
                    ORDER BY version_number DESC 
                    LIMIT :keep_versions
                """), {"doc_id": doc_id, "keep_versions": keep_versions})
                
                keep_versions_list = [row.version_number for row in result]
                
                # 删除不需要保留的版本
                if keep_versions_list:
                    result = conn.execute(text("""
                        DELETE FROM document_versions 
                        WHERE document_id = :doc_id 
                        AND version_number NOT IN :keep_versions
                    """), {"doc_id": doc_id, "keep_versions": tuple(keep_versions_list)})
                else:
                    result = conn.execute(text("""
                        DELETE FROM document_versions 
                        WHERE document_id = :doc_id
                    """), {"doc_id": doc_id})
                
                deleted_count += result.rowcount
            
            conn.commit()
            logger.info(f"清理旧文档版本: {deleted_count} 条记录")
            return deleted_count
    
    def clean_old_export_files(self, days: int = 30) -> int:
        """清理旧的导出文件记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM document_exports 
                WHERE created_at < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            deleted_count = result.rowcount
            conn.commit()
            
            logger.info(f"清理旧导出文件记录: {deleted_count} 条记录")
            return deleted_count
    
    def clean_operation_logs(self, days: int = 180) -> int:
        """清理操作日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM operation_logs 
                WHERE created_at < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            deleted_count = result.rowcount
            conn.commit()
            
            logger.info(f"清理操作日志: {deleted_count} 条记录")
            return deleted_count
    
    def run_full_cleanup(self) -> dict:
        """运行完整的数据清理"""
        results = {}
        
        try:
            results['expired_sessions'] = self.clean_expired_sessions(days=30)
            results['old_ai_generations'] = self.clean_old_ai_generations(days=90)
            results['old_document_versions'] = self.clean_old_document_versions(keep_versions=10)
            results['old_export_files'] = self.clean_old_export_files(days=30)
            results['operation_logs'] = self.clean_operation_logs(days=180)
            
            total_deleted = sum(results.values())
            logger.info(f"数据清理完成，共删除 {total_deleted} 条记录")
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            results['error'] = str(e)
        
        return results
```

### 2. 数据备份任务

```python
# backend/app/tasks/data_backup.py
import os
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """数据库备份工具"""
    
    def __init__(self, backup_dir: str = "/var/backups/mysql"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def backup_database(self, database: str, compression: bool = True) -> Dict[str, Any]:
        """备份数据库"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{database}_{timestamp}.sql"
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # 构建mysqldump命令
            cmd = [
                "mysqldump",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                "--hex-blob",
                "--set-gtid-purged=OFF",
                "--result-file", filepath,
                database
            ]
            
            # 执行备份
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"mysqldump失败: {result.stderr}")
            
            # 压缩备份文件
            if compression:
                compressed_filepath = f"{filepath}.gz"
                subprocess.run(["gzip", filepath], check=True)
                filepath = compressed_filepath
                filename = f"{filename}.gz"
            
            # 获取文件大小
            file_size = os.path.getsize(filepath)
            
            backup_info = {
                'database': database,
                'filename': filename,
                'filepath': filepath,
                'file_size_mb': file_size // (1024 * 1024),
                'timestamp': timestamp,
                'success': True
            }
            
            logger.info(f"数据库备份成功: {database} -> {filename}")
            return backup_info
            
        except Exception as e:
            logger.error(f"数据库备份失败 {database}: {e}")
            return {
                'database': database,
                'filename': filename,
                'error': str(e),
                'success': False
            }
    
    def backup_all_databases(self) -> Dict[str, Any]:
        """备份所有数据库"""
        databases = [
            'user_db',
            'project_db', 
            'document_db',
            'ai_generation_db',
            'log_db'
        ]
        
        results = {}
        for database in databases:
            results[database] = self.backup_database(database)
        
        return results
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """清理旧备份文件"""
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
        deleted_count = 0
        
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            if os.path.isfile(filepath):
                file_mtime = os.path.getmtime(filepath)
                if file_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"删除旧备份文件: {filename}")
                    except Exception as e:
                        logger.error(f"删除备份文件失败 {filename}: {e}")
        
        logger.info(f"清理旧备份文件完成: {deleted_count} 个文件")
        return deleted_count
    
    def verify_backup(self, filepath: str) -> bool:
        """验证备份文件完整性"""
        try:
            # 检查文件是否存在
            if not os.path.exists(filepath):
                return False
            
            # 如果是压缩文件，先解压
            if filepath.endswith('.gz'):
                import gzip
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    # 读取前几行验证格式
                    for i, line in enumerate(f):
                        if i > 10:  # 只检查前10行
                            break
                        if '-- MySQL dump' in line:
                            return True
            else:
                # 检查普通SQL文件
                with open(filepath, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i > 10:  # 只检查前10行
                            break
                        if '-- MySQL dump' in line:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"验证备份文件失败 {filepath}: {e}")
            return False
```

### 3. 维护任务调度

```python
# backend/app/tasks/maintenance_scheduler.py
import schedule
import time
import logging
from .data_cleanup import DataCleanup
from .data_backup import DatabaseBackup
from .index_maintenance import run_index_maintenance

logger = logging.getLogger(__name__)

class MaintenanceScheduler:
    """维护任务调度器"""
    
    def __init__(self):
        self.data_cleanup = DataCleanup()
        self.database_backup = DatabaseBackup()
    
    def schedule_all_tasks(self):
        """调度所有维护任务"""
        
        # 每日任务
        schedule.every().day.at("01:00").do(self.daily_cleanup)
        schedule.every().day.at("02:00").do(self.daily_backup)
        
        # 每周任务
        schedule.every().sunday.at("03:00").do(self.weekly_maintenance)
        
        # 每月任务
        schedule.every().month.do(self.monthly_maintenance)
        
        logger.info("维护任务已调度")
    
    def daily_cleanup(self):
        """每日清理任务"""
        logger.info("开始执行每日清理任务")
        
        try:
            # 清理过期会话
            self.data_cleanup.clean_expired_sessions(days=30)
            
            # 清理旧导出文件记录
            self.data_cleanup.clean_old_export_files(days=30)
            
            logger.info("每日清理任务完成")
            
        except Exception as e:
            logger.error(f"每日清理任务失败: {e}")
    
    def daily_backup(self):
        """每日备份任务"""
        logger.info("开始执行每日备份任务")
        
        try:
            # 备份所有数据库
            backup_results = self.database_backup.backup_all_databases()
            
            # 验证备份文件
            for db, result in backup_results.items():
                if result['success']:
                    self.database_backup.verify_backup(result['filepath'])
            
            logger.info("每日备份任务完成")
            
        except Exception as e:
            logger.error(f"每日备份任务失败: {e}")
    
    def weekly_maintenance(self):
        """每周维护任务"""
        logger.info("开始执行每周维护任务")
        
        try:
            # 运行索引维护
            run_index_maintenance()
            
            # 清理旧AI生成记录
            self.data_cleanup.clean_old_ai_generations(days=90)
            
            # 清理旧文档版本
            self.data_cleanup.clean_old_document_versions(keep_versions=10)
            
            # 清理旧备份文件
            self.database_backup.cleanup_old_backups(keep_days=30)
            
            logger.info("每周维护任务完成")
            
        except Exception as e:
            logger.error(f"每周维护任务失败: {e}")
    
    def monthly_maintenance(self):
        """每月维护任务"""
        logger.info("开始执行每月维护任务")
        
        try:
            # 运行完整数据清理
            cleanup_results = self.data_cleanup.run_full_cleanup()
            
            # 创建完整备份
            backup_results = self.database_backup.backup_all_databases()
            
            # 分析数据库性能
            from ..core.performance_monitor import DatabasePerformanceMonitor
            monitor = DatabasePerformanceMonitor()
            metrics = monitor.collect_all_metrics()
            
            # 生成月度报告
            self.generate_monthly_report(cleanup_results, backup_results, metrics)
            
            logger.info("每月维护任务完成")
            
        except Exception as e:
            logger.error(f"每月维护任务失败: {e}")
    
    def generate_monthly_report(self, cleanup_results: dict, backup_results: dict, metrics: dict):
        """生成月度维护报告"""
        from datetime import datetime
        
        report = {
            'month': datetime.now().strftime("%Y-%m"),
            'cleanup_results': cleanup_results,
            'backup_results': backup_results,
            'performance_metrics': metrics,
            'generated_at': datetime.now().isoformat()
        }
        
        # 保存报告到文件
        import json
        report_filename = f"maintenance_report_{report['month']}.json"
        report_filepath = os.path.join("/var/log/maintenance", report_filename)
        
        os.makedirs(os.path.dirname(report_filepath), exist_ok=True)
        with open(report_filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"月度维护报告已生成: {report_filepath}")
    
    def run_scheduler(self):
        """运行调度器"""
        self.schedule_all_tasks()
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = MaintenanceScheduler()
    scheduler.run_scheduler()
```

## 性能测试方案

### 1. 基准测试

```python
# backend/tests/performance/benchmark.py
import time
import statistics
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import User, Project, Document, AIGeneration

class DatabaseBenchmark:
    """数据库基准测试工具"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_query(self, query_func, iterations: int = 100) -> Dict[str, Any]:
        """基准测试查询性能"""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            try:
                result = query_func()
                end_time = time.time()
                times.append(end_time - start_time)
            except Exception as e:
                print(f"查询执行失败: {e}")
                continue
        
        if not times:
            return {'error': '所有查询执行失败'}
        
        return {
            'iterations': len(times),
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'p95': statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times),
            'p99': statistics.quantiles(times, n=100)[98] if len(times) > 100 else max(times)
        }
    
    def test_user_login(self) -> Dict[str, Any]:
        """测试用户登录查询性能"""
        def login_query():
            with SessionLocal() as db:
                user = db.query(User).filter(
                    User.username == "test_user",
                    User.is_active == True
                ).first()
                return user
        
        return self.benchmark_query(login_query, iterations=1000)
    
    def test_project_list(self) -> Dict[str, Any]:
        """测试项目列表查询性能"""
        def project_list_query():
            with SessionLocal() as db:
                projects = db.query(Project).filter(
                    Project.user_id == 1
                ).order_by(Project.updated_at.desc()).limit(20).all()
                return projects
        
        return self.benchmark_query(project_list_query, iterations=500)
    
    def test_document_search(self) -> Dict[str, Any]:
        """测试文档搜索查询性能"""
        def document_search_query():
            with SessionLocal() as db:
                documents = db.query(Document).filter(
                    Document.title.like("%测试%"),
                    Document.project_id == 1
                ).order_by(Document.updated_at.desc()).limit(20).all()
                return documents
        
        return self.benchmark_query(document_search_query, iterations=200)
    
    def test_ai_generation_status(self) -> Dict[str, Any]:
        """测试AI生成状态查询性能"""
        def ai_generation_query():
            with SessionLocal() as db:
                generation = db.query(AIGeneration).filter(
                    AIGeneration.id == 1,
                    AIGeneration.user_id == 1
                ).first()
                return generation
        
        return self.benchmark_query(ai_generation_query, iterations=1000)
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        print("开始数据库基准测试...")
        
        self.results['user_login'] = self.test_user_login()
        print("用户登录查询测试完成")
        
        self.results['project_list'] = self.test_project_list()
        print("项目列表查询测试完成")
        
        self.results['document_search'] = self.test_document_search()
        print("文档搜索查询测试完成")
        
        self.results['ai_generation_status'] = self.test_ai_generation_status()
        print("AI生成状态查询测试完成")
        
        return self.results
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = "# 数据库基准测试报告\n\n"
        report += f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for test_name, results in self.results.items():
            if 'error' in results:
                report += f"## {test_name}\n"
                report += f"错误: {results['error']}\n\n"
                continue
            
            report += f"## {test_name}\n"
            report += f"- 迭代次数: {results['iterations']}\n"
            report += f"- 平均响应时间: {results['avg_time']*1000:.2f}ms\n"
            report += f"- 最小响应时间: {results['min_time']*1000:.2f}ms\n"
            report += f"- 最大响应时间: {results['max_time']*1000:.2f}ms\n"
            report += f"- 中位数响应时间: {results['median_time']*1000:.2f}ms\n"
            report += f"- P95响应时间: {results['p95']*1000:.2f}ms\n"
            report += f"- P99响应时间: {results['p99']*1000:.2f}ms\n"
            report += f"- 标准差: {results['std_dev']*1000:.2f}ms\n\n"
        
        return report

if __name__ == "__main__":
    benchmark = DatabaseBenchmark()
    results = benchmark.run_all_benchmarks()
    report = benchmark.generate_report()
    
    # 保存报告
    with open("database_benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("基准测试完成，报告已保存到 database_benchmark_report.md")
```

### 2. 负载测试

```python
# backend/tests/performance/load_test.py
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    """负载测试工具"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    async def single_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", 
                           data: dict = None, headers: dict = None) -> Dict[str, Any]:
        """执行单个请求"""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    await response.text()
                    status_code = response.status
            elif method.upper() == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                    await response.text()
                    status_code = response.status
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': True,
                'status_code': status_code,
                'response_time': response_time,
                'timestamp': start_time
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'timestamp': start_time
            }
    
    async def concurrent_requests(self, endpoint: str, concurrent_users: int = 10, 
                               requests_per_user: int = 10, method: str = "GET", 
                               data: dict = None, headers: dict = None) -> List[Dict[str, Any]]:
        """执行并发请求"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    task = self.single_request(session, endpoint, method, data, headers)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
    
    def test_api_endpoint(self, endpoint: str, concurrent_users: int = 10, 
                         requests_per_user: int = 10, method: str = "GET", 
                         data: dict = None, headers: dict = None) -> Dict[str, Any]:
        """测试API端点性能"""
        print(f"开始测试端点: {endpoint}")
        print(f"并发用户数: {concurrent_users}, 每用户请求数: {requests_per_user}")
        
        start_time = time.time()
        results = asyncio.run(self.concurrent_requests(
            endpoint, concurrent_users, requests_per_user, method, data, headers
        ))
        end_time = time.time()
        
        # 分析结果
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            status_codes = [r['status_code'] for r in successful_requests]
            
            analysis = {
                'endpoint': endpoint,
                'method': method,
                'concurrent_users': concurrent_users,
                'requests_per_user': requests_per_user,
                'total_requests': len(results),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': len(successful_requests) / len(results),
                'total_time': end_time - start_time,
                'requests_per_second': len(results) / (end_time - start_time),
                'response_time': {
                    'min': min(response_times),
                    'max': max(response_times),
                    'avg': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                    'p99': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
                },
                'status_codes': {code: status_codes.count(code) for code in set(status_codes)}
            }
        else:
            analysis = {
                'endpoint': endpoint,
                'method': method,
                'concurrent_users': concurrent_users,
                'requests_per_user': requests_per_user,
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_requests),
                'success_rate': 0,
                'errors': [r['error'] for r in failed_requests[:5]]  # 只显示前5个错误
            }
        
        return analysis
    
    def run_load_tests(self) -> Dict[str, Any]:
        """运行负载测试"""
        # 测试用户登录
        self.results['login'] = self.test_api_endpoint(
            "/api/v1/auth/login",
            concurrent_users=20,
            requests_per_user=5,
            method="POST",
            data={"username": "test_user", "password": "test_password"}
        )
        
        # 测试获取项目列表
        self.results['project_list'] = self.test_api_endpoint(
            "/api/v1/projects/",
            concurrent_users=30,
            requests_per_user=10,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 测试获取文档列表
        self.results['document_list'] = self.test_api_endpoint(
            "/api/v1/documents/",
            concurrent_users=25,
            requests_per_user=8,
            headers={"Authorization": "Bearer test_token"}
        )
        
        # 测试AI生成
        self.results['ai_generation'] = self.test_api_endpoint(
            "/api/v1/ai/generate",
            concurrent_users=10,
            requests_per_user=3,
            method="POST",
            data={
                "document_id": 1,
                "prompt": "测试生成内容"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        return self.results
    
    def generate_report(self) -> str:
        """生成负载测试报告"""
        report = "# API负载测试报告\n\n"
        report += f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for endpoint, results in self.results.items():
            report += f"## {endpoint}\n\n"
            report += f"- 端点: {results['endpoint']}\n"
            report += f"- 方法: {results['method']}\n"
            report += f"- 并发用户数: {results['concurrent_users']}\n"
            report += f"- 每用户请求数: {results['requests_per_user']}\n"
            report += f"- 总请求数: {results['total_requests']}\n"
            report += f"- 成功请求数: {results['successful_requests']}\n"
            report += f"- 失败请求数: {results['failed_requests']}\n"
            report += f"- 成功率: {results['success_rate']:.2%}\n"
            report += f"- 总耗时: {results['total_time']:.2f}s\n"
            report += f"- QPS: {results['requests_per_second']:.2f}\n"
            
            if 'response_time' in results:
                rt = results['response_time']
                report += f"- 响应时间(平均): {rt['avg']*1000:.2f}ms\n"
                report += f"- 响应时间(最小): {rt['min']*1000:.2f}ms\n"
                report += f"- 响应时间(最大): {rt['max']*1000:.2f}ms\n"
                report += f"- 响应时间(P95): {rt['p95']*1000:.2f}ms\n"
                report += f"- 响应时间(P99): {rt['p99']*1000:.2f}ms\n"
            
            if 'status_codes' in results:
                report += "- 状态码分布:\n"
                for code, count in results['status_codes'].items():
                    report += f"  - {code}: {count}\n"
            
            if 'errors' in results:
                report += "- 错误信息:\n"
                for error in results['errors']:
                    report += f"  - {error}\n"
            
            report += "\n"
        
        return report

if __name__ == "__main__":
    tester = LoadTester()
    results = tester.run_load_tests()
    report = tester.generate_report()
    
    # 保存报告
    with open("api_load_test_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("负载测试完成，报告已保存到 api_load_test_report.md")
```

### 3. 性能测试自动化

```python
# backend/tests/performance/test_runner.py
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, Any

class PerformanceTestRunner:
    """性能测试运行器"""
    
    def __init__(self, output_dir: str = "./test_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run_database_benchmark(self) -> Dict[str, Any]:
        """运行数据库基准测试"""
        print("运行数据库基准测试...")
        
        try:
            result = subprocess.run([
                sys.executable, "benchmark.py"
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr
                }
            
            # 解析结果
            # 这里简化处理，实际可以从生成的报告中解析
            return {
                'success': True,
                'output': result.stdout,
                'report_file': os.path.join(os.path.dirname(__file__), "database_benchmark_report.md")
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_load_test(self) -> Dict[str, Any]:
        """运行负载测试"""
        print("运行API负载测试...")
        
        try:
            result = subprocess.run([
                sys.executable, "load_test.py"
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr
                }
            
            return {
                'success': True,
                'output': result.stdout,
                'report_file': os.path.join(os.path.dirname(__file__), "api_load_test_report.md")
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_stress_test(self) -> Dict[str, Any]:
        """运行压力测试"""
        print("运行压力测试...")
        
        # 这里可以集成更专业的压力测试工具，如JMeter、Locust等
        # 简化实现，使用负载测试的更高并发版本
        
        try:
            from load_test import LoadTester
            tester = LoadTester()
            
            # 高并发压力测试
            results = {
                'high_concurrency_login': tester.test_api_endpoint(
                    "/api/v1/auth/login",
                    concurrent_users=100,
                    requests_per_user=10,
                    method="POST",
                    data={"username": "test_user", "password": "test_password"}
                ),
                'high_concurrency_projects': tester.test_api_endpoint(
                    "/api/v1/projects/",
                    concurrent_users=150,
                    requests_per_user=20,
                    headers={"Authorization": "Bearer test_token"}
                )
            }
            
            return {
                'success': True,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有性能测试"""
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # 运行数据库基准测试
        test_results['tests']['database_benchmark'] = self.run_database_benchmark()
        
        # 运行负载测试
        test_results['tests']['load_test'] = self.run_load_test()
        
        # 运行压力测试
        test_results['tests']['stress_test'] = self.run_stress_test()
        
        # 保存测试结果
        results_file = os.path.join(self.output_dir, f"performance_test_results_{int(time.time())}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        # 生成综合报告
        self.generate_comprehensive_report(test_results)
        
        return test_results
    
    def generate_comprehensive_report(self, test_results: Dict[str, Any]):
        """生成综合性能测试报告"""
        report = "# 综合性能测试报告\n\n"
        report += f"测试时间: {test_results['timestamp']}\n\n"
        
        for test_name, result in test_results['tests'].items():
            report += f"## {test_name}\n\n"
            
            if result['success']:
                report += "状态: ✅ 通过\n\n"
                
                if 'report_file' in result:
                    report += f"详细报告: {result['report_file']}\n\n"
                
                if 'results' in result:
                    # 简化显示结果
                    for endpoint, data in result['results'].items():
                        report += f"### {endpoint}\n"
                        report += f"- 成功率: {data['success_rate']:.2%}\n"
                        report += f"- QPS: {data['requests_per_second']:.2f}\n"
                        if 'response_time' in data:
                            report += f"- 平均响应时间: {data['response_time']['avg']*1000:.2f}ms\n"
                        report += "\n"
            else:
                report += "状态: ❌ 失败\n\n"
                report += f"错误: {result['error']}\n\n"
        
        # 保存综合报告
        report_file = os.path.join(self.output_dir, f"comprehensive_performance_report_{int(time.time())}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"综合性能测试报告已保存到: {report_file}")

if __name__ == "__main__":
    runner = PerformanceTestRunner()
    results = runner.run_all_tests()
    
    print("性能测试完成!")
    print(f"测试结果: {len(results['tests'])} 个测试")
    
    success_count = sum(1 for test in results['tests'].values() if test['success'])
    print(f"成功: {success_count}, 失败: {len(results['tests']) - success_count}")
```

## 实施建议

### 1. 实施优先级

基于性能瓶颈分析和优化策略，建议按以下优先级实施：

#### 第一阶段（高优先级）
1. **索引优化**：实施完整的索引策略，特别是复合索引和全文索引
2. **缓存策略**：部署Redis缓存，实现热点数据缓存
3. **查询优化**：优化慢查询，特别是项目列表和文档搜索查询
4. **连接池配置**：优化数据库连接池参数

#### 第二阶段（中优先级）
1. **读写分离**：配置主从复制，实现读写分离
2. **分区策略**：对大表实施分区，特别是AI生成记录表
3. **慢查询监控**：部署慢查询监控和告警系统
4. **性能监控**：实施全面的性能监控指标

#### 第三阶段（低优先级）
1. **分库分表**：根据数据增长情况，实施分库分表策略
2. **数据库参数调优**：根据实际负载情况，调整数据库参数
3. **定期维护任务**：建立自动化维护任务调度
4. **性能测试**：建立性能测试自动化流程

### 2. 实施步骤

#### 2.1 准备阶段
1. **环境评估**：评估当前数据库环境和性能状况
2. **备份策略**：建立完整的数据备份和恢复机制
3. **测试环境**：搭建与生产环境一致的测试环境
4. **监控基线**：建立性能监控基线，记录优化前的性能指标

#### 2.2 实施阶段
1. **索引创建**：在低峰期创建索引，监控创建过程对性能的影响
2. **缓存部署**：逐步部署缓存策略，先从热点数据开始
3. **查询优化**：逐个优化慢查询，每次优化后进行性能测试
4. **参数调整**：逐步调整数据库参数，每次调整后观察性能变化

#### 2.3 验证阶段
1. **性能测试**：运行基准测试和负载测试，验证优化效果
2. **监控观察**：持续监控性能指标，确保优化效果稳定
3. **业务验证**：与业务方确认系统功能正常，性能有明显提升
4. **文档更新**：更新数据库设计文档和运维文档

### 3. 风险控制

#### 3.1 数据安全
1. **备份验证**：每次重大变更前验证备份可用性
2. **回滚方案**：准备详细的回滚方案，确保可以快速恢复
3. **灰度发布**：新策略先在测试环境验证，再小范围上线
4. **监控告警**：设置关键指标告警，及时发现问题

#### 3.2 性能风险
1. **索引影响**：创建索引可能影响写入性能，需要在低峰期操作
2. **缓存一致性**：确保缓存与数据库数据一致性
3. **连接数控制**：监控数据库连接数，防止连接数过多
4. **资源监控**：监控系统资源使用情况，防止资源耗尽

### 4. 长期维护

#### 4.1 定期评估
1. **性能评估**：每月进行性能评估，识别新的性能瓶颈
2. **索引优化**：每季度分析索引使用情况，删除无用索引
3. **容量规划**：根据数据增长趋势，提前进行容量规划
4. **技术更新**：关注数据库新技术，适时进行版本升级

#### 4.2 持续优化
1. **监控分析**：持续分析性能监控数据，发现优化机会
2. **业务反馈**：收集业务方反馈，了解用户体验
3. **新技术应用**：评估新技术应用价值，如分布式数据库
4. **团队培训**：定期进行数据库性能优化培训，提升团队技能

通过以上全面的数据库性能优化策略，悦恩人机共写平台的数据库性能将得到显著提升，能够支持业务的快速发展和用户规模的增长。