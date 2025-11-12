# 基于角色的权限控制系统实现指南

## 概述

本文档描述了悦恩人机共写平台中实现的基于角色的权限控制系统（RBAC）。该系统提供了灵活的权限管理机制，支持用户角色分级和细粒度的权限控制。

## 系统架构

### 1. 用户角色定义

系统定义了三种用户角色：

- **USER（普通用户）**: 基础权限，可以创建和管理自己的项目、文档
- **MODERATOR（版主）**: 中级权限，可以管理内容，但不能管理用户
- **ADMIN（管理员）**: 最高权限，可以管理所有用户和系统设置

### 2. 权限层级

权限采用层级设计，高级角色自动拥有低级角色的所有权限：

```
ADMIN > MODERATOR > USER
```

## 实现细节

### 1. 数据模型

#### User模型扩展

在 `backend/app/models/user.py` 中添加了角色相关字段：

```python
class UserRole(PyEnum):
    """用户角色枚举"""
    USER = "user"  # 普通用户
    ADMIN = "admin"  # 管理员
    MODERATOR = "moderator"  # 版主（可扩展）

class User(Base):
    # ... 其他字段 ...
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, index=True)
    
    @property
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_moderator(self) -> bool:
        """检查用户是否为版主或管理员"""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN]
    
    def has_permission(self, required_role: UserRole) -> bool:
        """检查用户是否具有所需权限"""
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.MODERATOR: 1,
            UserRole.ADMIN: 2
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
```

### 2. 权限验证装饰器

在 `backend/app/utils/auth.py` 中实现了权限验证装饰器：

```python
def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

def require_role(required_role: str):
    """角色权限验证装饰器工厂函数"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # 权限检查逻辑
        if not current_user.has_permission(role_mapping[required_role]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要{required_role}或更高权限"
            )
        return current_user
    return role_checker
```

### 3. 管理员功能

创建了完整的管理员功能模块 `backend/app/routes/admin.py`，包括：

- 用户列表查询（支持分页、搜索、筛选）
- 用户详情查看
- 用户创建、更新、删除
- 密码重置
- 用户统计信息

### 4. 权限保护示例

#### 清除缓存接口

```python
@router.delete("/cache")
async def clear_cache(
    current_user: User = Depends(get_current_admin_user)  # 仅管理员可访问
):
    """清除缓存（仅管理员）"""
    # 实现逻辑...
```

#### 使用量统计接口

```python
@router.get("/usage/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user)  # 所有用户可访问
):
    """获取AI使用量统计信息"""
    # 获取用户个人使用量
    user_usage = ai_service.get_user_usage(str(current_user.id))
    
    # 如果是管理员，获取全局统计
    global_stats = None
    if current_user.is_admin:  # 管理员额外权限
        global_stats = ai_service.get_usage_stats()
    
    return {
        "success": True,
        "user_usage": user_usage,
        "global_stats": global_stats,
        "service_available": ai_service.is_available()
    }
```

## 数据库迁移

创建了迁移脚本 `backend/migrations/004_add_user_role.sql`：

```sql
-- 创建用户角色枚举类型
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');

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
```

## API端点权限控制

### 管理员专用端点

- `GET /api/admin/users` - 获取用户列表
- `GET /api/admin/users/{user_id}` - 获取用户详情
- `POST /api/admin/users` - 创建用户
- `PUT /api/admin/users/{user_id}` - 更新用户
- `DELETE /api/admin/users/{user_id}` - 删除用户
- `POST /api/admin/users/{user_id}/reset-password` - 重置用户密码
- `GET /api/admin/stats` - 获取用户统计信息
- `DELETE /api/ai/cache` - 清除缓存

### 权限分级端点

- `GET /api/ai/usage/stats` - 所有用户可访问，管理员获取额外信息

## 测试

创建了完整的测试脚本 `backend/test_role_permissions.py`，测试内容包括：

1. **测试数据设置**: 创建管理员和普通用户
2. **认证测试**: 验证登录和token获取
3. **管理员权限测试**: 验证管理员可以访问所有端点
4. **权限拒绝测试**: 验证普通用户无法访问管理员端点
5. **未授权访问测试**: 验证无token和无效token的处理

### 运行测试

```bash
cd backend
python test_role_permissions.py
```

## 安全考虑

1. **最小权限原则**: 每个用户只拥有完成其工作所需的最小权限
2. **权限继承**: 高级角色自动拥有低级角色的权限
3. **自我保护**: 管理员不能删除自己的账户或将自己的角色降级
4. **Token验证**: 所有API端点都需要有效的JWT token
5. **权限检查**: 在数据库操作前进行权限验证

## 扩展性

系统设计支持未来扩展：

1. **新角色**: 可以轻松添加新的用户角色
2. **细粒度权限**: 可以实现基于资源的权限控制
3. **权限组**: 可以创建权限组来管理复杂权限
4. **动态权限**: 可以实现基于条件的动态权限检查

## 使用示例

### 创建管理员用户

```python
# 在数据库中直接创建
admin_user = User(
    name="管理员",
    email="admin@example.com",
    hashed_password=get_password_hash("secure_password"),
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
db.add(admin_user)
db.commit()
```

### 在路由中使用权限验证

```python
from app.utils.auth import get_current_admin_user, require_role

# 方法1：使用预定义装饰器
@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: User = Depends(get_current_admin_user)
):
    # 只有管理员可以访问
    pass

# 方法2：使用动态角色验证
@router.get("/moderator-or-above")
async def moderator_endpoint(
    current_user: User = Depends(require_role('moderator'))
):
    # 版主和管理员可以访问
    pass
```

### 检查用户权限

```python
# 在代码中检查权限
if current_user.is_admin:
    # 管理员专用逻辑
    pass

if current_user.has_permission(UserRole.MODERATOR):
    # 版主或管理员权限
    pass
```

## 总结

本权限系统提供了：

1. **完整的角色管理**: 支持多级用户角色
2. **灵活的权限控制**: 装饰器模式，易于使用和扩展
3. **安全的设计**: 遵循最小权限原则
4. **全面的管理功能**: 完整的用户管理界面
5. **详细的测试**: 确保系统可靠性

该系统为悦恩人机共写平台提供了坚实的权限控制基础，确保了系统的安全性和可管理性。