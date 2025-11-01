from functools import wraps
from typing import List, Callable, Any, Union
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.deps import get_current_user
from app.models.user import User
from app.core.exceptions import PermissionException

security = HTTPBearer()


class Permission:
    """权限类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Permission('{self.name}')"


class Role:
    """角色类"""
    
    def __init__(self, name: str, permissions: List[Permission] = None):
        self.name = name
        self.permissions = permissions or []
    
    def has_permission(self, permission: Union[str, Permission]) -> bool:
        """检查角色是否有特定权限"""
        perm_name = permission if isinstance(permission, str) else permission.name
        return any(p.name == perm_name for p in self.permissions)
    
    def add_permission(self, permission: Permission):
        """添加权限"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: Union[str, Permission]):
        """移除权限"""
        perm_name = permission if isinstance(permission, str) else permission.name
        self.permissions = [p for p in self.permissions if p.name != perm_name]


# 定义系统权限
PERMISSIONS = {
    # 用户管理权限
    "user:read": Permission("user:read", "查看用户信息"),
    "user:write": Permission("user:write", "修改用户信息"),
    "user:create": Permission("user:create", "创建用户"),
    "user:delete": Permission("user:delete", "删除用户"),
    
    # 项目管理权限
    "project:read": Permission("project:read", "查看项目"),
    "project:write": Permission("project:write", "修改项目"),
    "project:create": Permission("project:create", "创建项目"),
    "project:delete": Permission("project:delete", "删除项目"),
    
    # 文档管理权限
    "document:read": Permission("document:read", "查看文档"),
    "document:write": Permission("document:write", "修改文档"),
    "document:create": Permission("document:create", "创建文档"),
    "document:delete": Permission("document:delete", "删除文档"),
    
    # AI生成权限
    "ai:generate": Permission("ai:generate", "使用AI生成功能"),
    "ai:configure": Permission("ai:configure", "配置AI参数"),
    
    # 系统管理权限
    "system:admin": Permission("system:admin", "系统管理"),
    "system:monitor": Permission("system:monitor", "系统监控"),
}

# 定义系统角色
ROLES = {
    "user": Role(
        "user",
        [
            PERMISSIONS["user:read"],
            PERMISSIONS["user:write"],
            PERMISSIONS["project:read"],
            PERMISSIONS["project:write"],
            PERMISSIONS["project:create"],
            PERMISSIONS["project:delete"],
            PERMISSIONS["document:read"],
            PERMISSIONS["document:write"],
            PERMISSIONS["document:create"],
            PERMISSIONS["document:delete"],
            PERMISSIONS["ai:generate"],
        ]
    ),
    "admin": Role(
        "admin",
        list(PERMISSIONS.values())  # 管理员拥有所有权限
    ),
}


def has_permission(user: User, permission: Union[str, Permission]) -> bool:
    """检查用户是否有特定权限"""
    if not user or not user.is_active:
        return False
    
    # 获取用户角色
    user_role = ROLES.get(user.role)
    if not user_role:
        return False
    
    return user_role.has_permission(permission)


def require_permissions(permissions: List[Union[str, Permission]]):
    """权限装饰器，要求用户拥有所有指定权限"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取request和current_user
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise PermissionException("需要登录")
            
            # 检查所有权限
            for permission in permissions:
                if not has_permission(current_user, permission):
                    perm_name = permission if isinstance(permission, str) else permission.name
                    raise PermissionException(f"缺少权限: {perm_name}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[Union[str, Permission]]):
    """权限装饰器，要求用户拥有任意一个指定权限"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取request和current_user
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise PermissionException("需要登录")
            
            # 检查是否有任意一个权限
            has_any = any(has_permission(current_user, perm) for perm in permissions)
            if not has_any:
                perm_names = [p if isinstance(p, str) else p.name for p in permissions]
                raise PermissionException(f"缺少以下任意权限: {', '.join(perm_names)}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(roles: List[str]):
    """角色装饰器，要求用户拥有指定角色"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取request和current_user
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise PermissionException("需要登录")
            
            if current_user.role not in roles:
                raise PermissionException(f"需要以下角色之一: {', '.join(roles)}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_resource_permission(user: User, resource_type: str, resource_id: Any, action: str) -> bool:
    """检查用户对特定资源的权限"""
    # 管理员拥有所有权限
    if user.role == "admin":
        return True
    
    # 检查用户是否是资源的所有者
    if resource_type == "project":
        from app.services.project import project
        from app.core.database import get_db
        
        # 这里需要获取数据库会话，但在装饰器中可能不太合适
        # 实际使用时可能需要调整
        pass
    elif resource_type == "document":
        from app.services.document import document
        pass
    
    # 默认情况下，用户只能操作自己的资源
    return False


def require_resource_permission(resource_type: str, action: str):
    """资源权限装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取request和current_user
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise PermissionException("需要登录")
            
            # 从路径参数中获取资源ID
            resource_id = kwargs.get("id") or request.path_params.get("id")
            if not resource_id:
                raise PermissionException("缺少资源ID")
            
            # 检查资源权限
            if not check_resource_permission(current_user, resource_type, resource_id, action):
                raise PermissionException(f"没有权限对{resource_type}执行{action}操作")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """权限检查器类"""
    
    def __init__(self, user: User):
        self.user = user
    
    def has_permission(self, permission: Union[str, Permission]) -> bool:
        """检查是否有权限"""
        return has_permission(self.user, permission)
    
    def has_role(self, role: str) -> bool:
        """检查是否有角色"""
        return self.user.role == role
    
    def can_read_user(self, user_id: int) -> bool:
        """检查是否可以读取用户信息"""
        # 可以读取自己的信息
        if self.user.id == user_id:
            return True
        
        # 管理员可以读取所有用户信息
        if self.user.role == "admin":
            return True
        
        return False
    
    def can_write_user(self, user_id: int) -> bool:
        """检查是否可以修改用户信息"""
        # 可以修改自己的信息
        if self.user.id == user_id:
            return True
        
        # 管理员可以修改所有用户信息
        if self.user.role == "admin":
            return True
        
        return False
    
    def can_delete_user(self, user_id: int) -> bool:
        """检查是否可以删除用户"""
        # 不能删除自己
        if self.user.id == user_id:
            return False
        
        # 只有管理员可以删除用户
        return self.user.role == "admin"
    
    def can_access_project(self, project_id: int) -> bool:
        """检查是否可以访问项目"""
        # 管理员可以访问所有项目
        if self.user.role == "admin":
            return True
        
        # 这里需要检查项目成员关系
        # 实际实现时需要查询数据库
        return False
    
    def can_modify_project(self, project_id: int) -> bool:
        """检查是否可以修改项目"""
        # 管理员可以修改所有项目
        if self.user.role == "admin":
            return True
        
        # 这里需要检查项目所有者或成员权限
        # 实际实现时需要查询数据库
        return False