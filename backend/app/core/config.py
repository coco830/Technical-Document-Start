from typing import List, Optional, Union
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "悦恩人机共写平台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    DATABASE_URL: str = "mysql://user:password@localhost/ai_writing_platform"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # AI服务配置
    OPENAI_API_KEY: Optional[str] = None
    ZHIPUAI_API_KEY: Optional[str] = None
    
    # 腾讯云配置
    TENCENT_SECRET_ID: Optional[str] = None
    TENCENT_SECRET_KEY: Optional[str] = None
    TENCENT_COS_BUCKET: Optional[str] = None
    TENCENT_COS_REGION: Optional[str] = None
    TENCENT_COS_DOMAIN: Optional[str] = None  # CDN域名
    TENCENT_COS_SCHEME: str = "https"  # 协议类型
    TENCENT_COS_TIMEOUT: int = 30  # 超时时间(秒)
    TENCENT_COS_RETRY: int = 3  # 重试次数
    TENCENT_COS_CHUNK_SIZE: int = 8 * 1024 * 1024  # 分片大小(8MB)
    TENCENT_COS_MAX_THREADS: int = 10  # 最大并发线程数
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local 或 cos
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 最大文件大小(100MB)
    ALLOWED_FILE_TYPES: List[str] = [
        ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif",
        ".bmp", ".webp", ".svg", ".mp3", ".mp4", ".zip",
        ".rar", ".7z", ".tar", ".gz"
    ]
    
    # 邮件配置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 测试配置
    TEST_DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()