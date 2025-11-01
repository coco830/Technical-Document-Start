from typing import Callable, List, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.deps import get_current_user
from app.core.permissions import has_permission, Permission
from app.models.user import User


class RBACMiddleware(BaseHTTPMiddleware):
    """基于角色的访问控制中间件"""
    
    def __init__(
        self,
        app,
        public_paths: List[str] = None,
        require_auth_paths: List[str] = None,
        permission_paths: dict = None
    ):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/confirm-reset-password",
            "/docs",
            "/openapi.json",
        ]
        self.require_auth_paths = require_auth_paths or [
            "/api/v1/users/me",
            "/api/v1/auth/logout",
            "/api/v1/auth/refresh",
        ]
        self.permission_paths = permission_paths or {
            # 用户管理相关路径
            "/api/v1/users": ["user:read"],
            "POST:/api/v1/users": ["user:create"],
            "PUT:/api/v1/users": ["user:write"],
            "DELETE:/api/v1/users": ["user:delete"],
            
            # 项目管理相关路径
            "/api/v1/projects": ["project:read"],
            "POST:/api/v1/projects": ["project:create"],
            "PUT:/api/v1/projects": ["project:write"],
            "DELETE:/api/v1/projects": ["project:delete"],
            
            # 文档管理相关路径
            "/api/v1/documents": ["document:read"],
            "POST:/api/v1/documents": ["document:create"],
            "PUT:/api/v1/documents": ["document:write"],
            "DELETE:/api/v1/documents": ["document:delete"],
            
            # AI生成相关路径
            "POST:/api/v1/ai/generate": ["ai:generate"],
            "PUT:/api/v1/ai/configure": ["ai:configure"],
            
            # 系统管理相关路径
            "/api/v1/admin": ["system:admin"],
            "/api/v1/system": ["system:monitor"],
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        
        # 检查是否是公开路径
        if self._is_public_path(path):
            return await call_next(request)
        
        # 检查是否需要认证
        if self._requires_auth(path):
            try:
                # 获取当前用户
                user = await self._get_user_from_request(request)
                if not user:
                    return self._unauthorized_response("需要登录")
                
                # 检查用户是否激活
                if not user.is_active:
                    return self._forbidden_response("账户已被禁用")
                
                # 检查权限
                required_permissions = self._get_required_permissions(method, path)
                if required_permissions:
                    for permission in required_permissions:
                        if not has_permission(user, permission):
                            return self._forbidden_response(f"缺少权限: {permission}")
                
                # 将用户信息添加到请求状态
                request.state.user = user
                
            except HTTPException:
                # 如果已经是HTTPException，直接抛出
                raise
            except Exception as e:
                # 其他异常，返回500错误
                return self._error_response(f"认证错误: {str(e)}")
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路径"""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def _requires_auth(self, path: str) -> bool:
        """检查是否需要认证"""
        for auth_path in self.require_auth_paths:
            if path.startswith(auth_path):
                return True
        return False
    
    def _get_required_permissions(self, method: str, path: str) -> Optional[List[str]]:
        """获取路径所需的权限"""
        # 检查精确匹配
        key = f"{method}:{path}"
        if key in self.permission_paths:
            return self.permission_paths[key]
        
        # 检查路径前缀匹配
        for perm_path, permissions in self.permission_paths.items():
            if ":" in perm_path:
                # 有方法前缀，检查精确匹配
                continue
            elif path.startswith(perm_path):
                return permissions
        
        return None
    
    async def _get_user_from_request(self, request: Request) -> Optional[User]:
        """从请求中获取用户信息"""
        try:
            # 使用依赖注入获取用户
            from app.core.database import get_db
            from app.core.deps import get_db as get_db_dep
            
            # 这里需要获取数据库会话
            # 在中间件中直接使用依赖注入比较复杂，这里简化处理
            # 实际使用时可能需要调整
            return None
        except Exception:
            return None
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """返回未授权响应"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "path": "",
            }
        )
    
    def _forbidden_response(self, message: str) -> JSONResponse:
        """返回禁止访问响应"""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_403_FORBIDDEN,
                "path": "",
            }
        )
    
    def _error_response(self, message: str) -> JSONResponse:
        """返回错误响应"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "path": "",
            }
        )


class ResourcePermissionMiddleware(BaseHTTPMiddleware):
    """资源权限中间件，用于检查对特定资源的访问权限"""
    
    def __init__(self, app, resource_type: str):
        super().__init__(app)
        self.resource_type = resource_type
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        
        # 只处理特定资源类型的路径
        if f"/api/v1/{self.resource_type}" not in path:
            return await call_next(request)
        
        try:
            # 获取当前用户
            user = await self._get_user_from_request(request)
            if not user:
                return self._unauthorized_response("需要登录")
            
            # 获取资源ID
            resource_id = self._extract_resource_id(path)
            if not resource_id:
                return await call_next(request)
            
            # 检查资源权限
            action = self._method_to_action(method)
            if not self._check_resource_permission(user, resource_id, action):
                return self._forbidden_response(f"没有权限对{self.resource_type}执行{action}操作")
            
            # 将用户和资源信息添加到请求状态
            request.state.user = user
            request.state.resource_id = resource_id
            request.state.action = action
            
        except HTTPException:
            raise
        except Exception as e:
            return self._error_response(f"权限检查错误: {str(e)}")
        
        return await call_next(request)
    
    async def _get_user_from_request(self, request: Request) -> Optional[User]:
        """从请求中获取用户信息"""
        # 这里需要实现获取用户信息的逻辑
        return None
    
    def _extract_resource_id(self, path: str) -> Optional[str]:
        """从路径中提取资源ID"""
        import re
        pattern = f"/api/v1/{self.resource_type}/(\\d+)"
        match = re.search(pattern, path)
        return match.group(1) if match else None
    
    def _method_to_action(self, method: str) -> str:
        """将HTTP方法转换为操作名称"""
        action_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "write",
            "PATCH": "write",
            "DELETE": "delete",
        }
        return action_map.get(method, "unknown")
    
    def _check_resource_permission(self, user: User, resource_id: str, action: str) -> bool:
        """检查用户对资源的权限"""
        # 管理员拥有所有权限
        if user.role == "admin":
            return True
        
        # 这里需要实现具体的资源权限检查逻辑
        # 例如：检查用户是否是资源的所有者、是否有特定角色等
        return False
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """返回未授权响应"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "path": "",
            }
        )
    
    def _forbidden_response(self, message: str) -> JSONResponse:
        """返回禁止访问响应"""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_403_FORBIDDEN,
                "path": "",
            }
        )
    
    def _error_response(self, message: str) -> JSONResponse:
        """返回错误响应"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": message,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "path": "",
            }
        )