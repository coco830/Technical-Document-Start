"""
安全中间件
提供API安全、请求验证、速率限制等功能
"""
import logging
import time
import hashlib
import hmac
import secrets
from typing import Dict, List, Optional, Callable, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.cache import cache_service
from app.core.exceptions import SecurityException

# 设置日志
logger = logging.getLogger(__name__)

# 安全头配置
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "upgrade-insecure-requests: 1; "
        "block-all-mixed-content"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# 允许的HTTP方法
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

# 允许的HTTP头
ALLOWED_HEADERS = [
    "Accept",
    "Accept-Language",
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-CSRF-Token"
]

# 敏感参数列表（需要额外验证）
SENSITIVE_PARAMS = [
    "password",
    "token",
    "secret",
    "key",
    "api_key",
    "access_token",
    "refresh_token"
]


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件类"""
    
    def __init__(self, app, enable_csrf: bool = True, enable_rate_limit: bool = True):
        super().__init__(app)
        self.enable_csrf = enable_csrf
        self.enable_rate_limit = enable_rate_limit
        
        # 初始化CSRF令牌存储
        self.csrf_tokens = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并应用安全措施"""
        start_time = time.time()
        
        try:
            # 1. 预处理请求
            processed_request = await self.preprocess_request(request)
            
            # 2. 调用下一个中间件
            response = await call_next(processed_request)
            
            # 3. 后处理响应
            processed_response = await self.postprocess_response(response, request)
            
            # 4. 记录请求日志
            await self.log_request(processed_request, processed_response, start_time)
            
            return processed_response
            
        except HTTPException as e:
            # 处理HTTP异常
            logger.warning(f"HTTP异常: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "error_code": "HTTP_EXCEPTION"}
            )
        except Exception as e:
            # 处理其他异常
            logger.error(f"未处理的异常: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "内部服务器错误", "error_code": "INTERNAL_ERROR"}
            )
    
    async def preprocess_request(self, request: Request) -> Request:
        """预处理请求"""
        # 1. 添加安全属性到请求状态
        request.state.security = {
            "client_ip": self.get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": secrets.token_hex(16)
        }
        
        # 2. 验证请求方法
        if request.method not in ALLOWED_METHODS:
            logger.warning(f"不允许的HTTP方法: {request.method}")
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"方法 {request.method} 不被允许"
            )
        
        # 3. 验证请求头
        self.validate_headers(request)
        
        # 4. CSRF保护（仅对状态改变请求）
        if self.enable_csrf and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            self.validate_csrf(request)
        
        # 5. 速率限制
        if self.enable_rate_limit:
            await self.check_rate_limit(request)
        
        # 6. 验证请求体
        await self.validate_body(request)
        
        return request
    
    async def postprocess_response(self, response: Response, request: Request) -> Response:
        """后处理响应"""
        # 1. 添加安全头
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # 2. 添加CORS头
        self.add_cors_headers(response, request)
        
        # 3. 添加安全元数据
        if hasattr(response, "headers"):
            response.headers["X-Request-ID"] = request.state.security["request_id"]
            response.headers["X-Response-Time"] = str(int((time.time() - request.state.security.get("start_time", time.time())) * 1000))
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 使用客户端IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def validate_headers(self, request: Request) -> None:
        """验证请求头"""
        # 检查可疑头
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Forwarded-Proto",
            "X-Forwarded-For",
            "X-Real-IP"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                logger.warning(f"检测到可疑头: {header}={request.headers[header]}")
        
        # 检查内容类型
        content_type = request.headers.get("content-type", "")
        if "text/html" in content_type and request.method in ["POST", "PUT", "PATCH"]:
            logger.warning(f"检测到HTML内容类型: {content_type}")
    
    def validate_csrf(self, request: Request) -> None:
        """验证CSRF令牌"""
        # 获取CSRF令牌
        csrf_token = request.headers.get("X-CSRF-Token")
        csrf_cookie = request.cookies.get("csrf_token")
        
        # 对于API请求，检查Authorization头而不是CSRF
        if "authorization" in request.headers:
            return
        
        # 验证CSRF令牌
        if not csrf_token and not csrf_cookie:
            logger.warning("缺少CSRF令牌")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="缺少CSRF令牌"
            )
        
        if csrf_token != csrf_cookie:
            logger.warning("无效的CSRF令牌")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无效的CSRF令牌"
            )
    
    async def check_rate_limit(self, request: Request) -> None:
        """检查速率限制"""
        client_ip = request.state.security["client_ip"]
        
        # 使用缓存实现速率限制
        cache_key = f"rate_limit:{client_ip}"
        current_count = cache_service.get(cache_key) or 0
        
        # 检查是否超过限制
        if current_count >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"速率限制触发: {client_ip} - {current_count}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 增加计数
        cache_service.set(cache_key, current_count + 1, ttl=60)  # 1分钟过期
    
    async def validate_body(self, request: Request) -> None:
        """验证请求体"""
        if request.method in ["POST", "PUT", "PATCH"] and hasattr(request, "_json"):
            try:
                # 获取JSON数据
                body = await request.json()
                
                # 检查敏感参数
                if isinstance(body, dict):
                    for param in SENSITIVE_PARAMS:
                        if param in body:
                            # 记录敏感参数访问
                            logger.warning(f"敏感参数访问: {param} from {request.state.security['client_ip']}")
                            
                            # 检查参数值是否安全
                            value = str(body[param])
                            if self.is_insecure_value(value):
                                logger.warning(f"检测到不安全的参数值: {param}={value}")
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"参数 {param} 包含不安全的内容"
                                )
                
                # 检查SQL注入
                if self.detect_sql_injection(body):
                    logger.warning(f"检测到可能的SQL注入: {body}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="检测到不安全的内容"
                    )
                
            except Exception as e:
                logger.error(f"验证请求体失败: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的请求体"
                )
    
    def is_insecure_value(self, value: str) -> bool:
        """检查值是否不安全"""
        # 检查常见的不安全模式
        insecure_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover=",
            "eval(",
            "expression(",
            "url(",
            "@import",
            "<iframe",
            "<object",
            "<embed",
            "<form",
            "alert(",
            "document.cookie",
            "window.location",
            "document.write"
        ]
        
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in insecure_patterns)
    
    def detect_sql_injection(self, data: Any) -> bool:
        """检测SQL注入"""
        if not isinstance(data, (str, dict)):
            return False
        
        # SQL注入关键词
        sql_keywords = [
            "union", "select", "insert", "update", "delete", "drop",
            "exec", "execute", "sp_", "xp_", "declare",
            "cast", "convert", "substring", "char", "ascii",
            "concat", "waitfor", "delay", "if", "else", "end",
            "--", "/*", "*/", ";", "'", "\"", "#"
        ]
        
        # 转换为字符串并检查
        data_str = str(data).lower()
        return any(keyword in data_str for keyword in sql_keywords)
    
    def add_cors_headers(self, response: Response, request: Request) -> None:
        """添加CORS头"""
        origin = request.headers.get("origin")
        
        # 检查是否允许的源
        allowed_origins = settings.ALLOWED_ORIGINS if hasattr(settings, 'ALLOWED_ORIGINS') else ["*"]
        
        if origin and (allowed_origins == ["*"] or origin in allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
        response.headers["Access-Control-Max-Age"] = "86400"  # 24小时
    
    async def log_request(self, request: Request, response: Response, start_time: float) -> None:
        """记录请求日志"""
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000  # 毫秒
        
        # 记录请求信息
        log_data = {
            "request_id": request.state.security["request_id"],
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.state.security["client_ip"],
            "user_agent": request.state.security["user_agent"],
            "status_code": response.status_code,
            "process_time": process_time,
            "timestamp": time.time()
        }
        
        # 记录到日志
        logger.info(f"请求日志: {log_data}")
        
        # 记录到缓存（用于分析）
        cache_key = f"request_log:{request.state.security['request_id']}"
        cache_service.set(cache_key, log_data, ttl=3600)  # 1小时过期


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """生成CSRF令牌"""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> str:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用PBKDF2哈希
        import hashlib
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000,  # 迭代次数
            dklen=128  # 密钥长度
        )
        
        return f"{salt}${pwdhash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = hashed_password.split('$')
            import hashlib
            pwdhash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000,
                dklen=128
            )
            
            return hmac.compare_digest(pwdhash.hexdigest(), hash_value)
        except Exception:
            return False
    
    @staticmethod
    def encrypt_data(data: str, key: str = None) -> str:
        """加密数据"""
        if key is None:
            key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else "default-key"
        
        from cryptography.fernet import Fernet
        f = Fernet(key.encode())
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str = None) -> str:
        """解密数据"""
        if key is None:
            key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else "default-key"
        
        from cryptography.fernet import Fernet
        f = Fernet(key.encode())
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """清理输入字符串"""
        import html
        # HTML转义
        escaped = html.escape(input_str)
        
        # 移除潜在的危险字符
        dangerous_chars = ["<", ">", "&", "\"", "'", "/", "\\", ";", ":", "%"]
        for char in dangerous_chars:
            escaped = escaped.replace(char, "")
        
        return escaped.strip()


# 创建安全中间件实例
def create_security_middleware(app, enable_csrf: bool = True, enable_rate_limit: bool = True):
    """创建安全中间件"""
    return SecurityMiddleware(app, enable_csrf=enable_csrf, enable_rate_limit=enable_rate_limit)