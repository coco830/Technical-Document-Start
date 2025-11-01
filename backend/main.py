"""
悦恩人机共写平台主应用文件
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import add_exception_handlers
from app.core.security_middleware import create_security_middleware
from app.core.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.core.rate_limiter import RateLimitMiddleware
from app.core.logging_service import setup_logging, performance_logger, error_tracker, log_aggregator
from app.core.database_optimization import db_optimizer, query_optimizer
from app.core.api_documentation import generate_api_documentation, generate_test_cases

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="悦恩人机共写平台 API",
    description="一个创新的人机协作写作平台API",
    version="1.0.0",
    docs_url="/docs" if getattr(settings, 'ENVIRONMENT', 'development') == "development" else None,
    redoc_url="/redoc" if getattr(settings, 'ENVIRONMENT', 'development') == "development" else None,
    openapi_url="/openapi.json" if getattr(settings, 'ENVIRONMENT', 'development') == "development" else None,
)

# 添加异常处理器
add_exception_handlers(app)

# 添加中间件
# 1. 信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=getattr(settings, 'ALLOWED_HOSTS', ["*"])
)

# 2. CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'ALLOWED_ORIGINS', ["*"]),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# 3. 安全中间件
app.add_middleware(
    create_security_middleware,
    enable_csrf=True,
    enable_rate_limit=True
)

# 4. 速率限制中间件
app.add_middleware(
    RateLimitMiddleware,
    default_limit={"times": 60, "limit": getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)}
)

# 5. 日志中间件
app.add_middleware(LoggingMiddleware)

# 6. 错误处理中间件
app.add_middleware(ErrorHandlingMiddleware)

# 添加API路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用启动中...")
    
    # 创建数据库表
    create_tables()
    
    # 初始化缓存
    from app.core.cache import cache_service
    if cache_service.is_available():
        logger.info("Redis缓存服务已连接")
    else:
        logger.warning("Redis缓存服务不可用，使用内存缓存")
    
    # 初始化任务队列
    try:
        from app.core.tasks import celery_app
        celery_app.control.inspect().stats()
        logger.info("Celery任务队列已连接")
    except Exception as e:
        logger.warning(f"Celery任务队列连接失败: {str(e)}")
    
    # 初始化数据库优化
    try:
        # 分析数据库性能
        db_stats = db_optimizer.get_database_stats()
        logger.info(f"数据库统计: {db_stats}")
        
        # 分析主要表性能
        main_tables = ["users", "projects", "documents", "companies", "ai_generations"]
        for table in main_tables:
            try:
                table_stats = db_optimizer.analyze_table_performance(table)
                logger.info(f"表 {table} 性能分析: {table_stats}")
                
                # 根据建议创建索引
                if table_stats.get("recommendations"):
                    logger.info(f"表 {table} 优化建议: {table_stats['recommendations']}")
            except Exception as e:
                logger.warning(f"分析表 {table} 失败: {str(e)}")
    except Exception as e:
        logger.warning(f"数据库优化初始化失败: {str(e)}")
    
    # 生成API文档和测试用例
    try:
        if getattr(settings, 'ENVIRONMENT', 'development') == "development":
            generate_api_documentation(app, output_dir="docs/api")
            generate_test_cases(app, output_dir="tests/api")
            logger.info("API文档和测试用例已生成")
    except Exception as e:
        logger.warning(f"生成API文档和测试用例失败: {str(e)}")
    
    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用关闭中...")
    
    # 关闭数据库连接
    from app.core.database import engine
    engine.dispose()
    
    logger.info("应用已关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用悦恩人机共写平台 API",
        "version": "1.0.0",
        "docs": "/docs" if getattr(settings, 'ENVIRONMENT', 'development') == "development" else None
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    from app.core.cache import cache_service
    
    # 检查各组件状态
    status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "components": {
            "database": "healthy",
            "cache": "healthy" if cache_service.is_available() else "degraded",
            "task_queue": "healthy"
        }
    }
    
    # 检查数据库连接
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        status["components"]["database"] = "unhealthy"
        status["status"] = "unhealthy"
    
    # 检查任务队列
    try:
        from app.core.tasks import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            status["components"]["task_queue"] = "healthy"
        else:
            status["components"]["task_queue"] = "degraded"
    except Exception as e:
        logger.error(f"任务队列健康检查失败: {str(e)}")
        status["components"]["task_queue"] = "unhealthy"
        status["status"] = "unhealthy"
    
    # 返回相应状态码
    response_code = 200 if status["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=response_code,
        content=status
    )


@app.get("/metrics")
async def metrics():
    """系统指标端点"""
    # 获取聚合统计
    stats = log_aggregator.aggregate_hourly_stats()
    
    # 获取系统资源使用情况
    try:
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            }
        }
    except ImportError:
        system_metrics = {
            "cpu_percent": 0,
            "memory": {"total": 0, "available": 0, "percent": 0},
            "disk": {"total": 0, "used": 0, "percent": 0}
        }
    
    # 获取数据库性能指标
    try:
        db_stats = db_optimizer.get_database_stats()
        db_metrics = {
            "total_size_mb": db_stats.get("total_size_mb", 0),
            "table_count": len(db_stats.get("tables", [])),
            "tables": db_stats.get("tables", [])
        }
    except Exception as e:
        logger.error(f"获取数据库指标失败: {str(e)}")
        db_metrics = {
            "total_size_mb": 0,
            "table_count": 0,
            "tables": []
        }
    
    return {
        "timestamp": "2024-01-01T00:00:00Z",
        "stats": stats,
        "system": system_metrics,
        "database": db_metrics
    }


@app.get("/admin/database/optimize")
async def optimize_database():
    """数据库优化端点"""
    try:
        # 获取数据库统计
        db_stats = db_optimizer.get_database_stats()
        
        # 优化主要表
        main_tables = ["users", "projects", "documents", "companies", "ai_generations"]
        optimization_results = {}
        
        for table in main_tables:
            try:
                # 分析表性能
                table_stats = db_optimizer.analyze_table_performance(table)
                
                # 优化表
                optimize_result = db_optimizer.optimize_table(table)
                
                # 建议并创建索引
                suggested_indexes = db_optimizer.suggest_indexes_for_table(table)
                if suggested_indexes:
                    index_result = db_optimizer.create_missing_indexes(table, suggested_indexes)
                else:
                    index_result = True
                
                optimization_results[table] = {
                    "analyzed": True,
                    "optimized": optimize_result,
                    "indexes_created": index_result,
                    "recommendations": table_stats.get("recommendations", [])
                }
            except Exception as e:
                logger.error(f"优化表 {table} 失败: {str(e)}")
                optimization_results[table] = {
                    "analyzed": False,
                    "optimized": False,
                    "indexes_created": False,
                    "error": str(e)
                }
        
        # 分析慢查询
        slow_queries = db_optimizer.analyze_slow_queries()
        
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "database_stats": db_stats,
            "optimization_results": optimization_results,
            "slow_queries": slow_queries
        }
    except Exception as e:
        logger.error(f"数据库优化失败: {str(e)}")
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "error": str(e)
        }


@app.get("/admin/database/analyze/{table_name}")
async def analyze_table(table_name: str):
    """分析表性能端点"""
    try:
        # 分析表性能
        table_stats = db_optimizer.analyze_table_performance(table_name)
        
        # 建议索引
        suggested_indexes = db_optimizer.suggest_indexes_for_table(table_name)
        
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "table_name": table_name,
            "stats": table_stats,
            "suggested_indexes": suggested_indexes
        }
    except Exception as e:
        logger.error(f"分析表 {table_name} 失败: {str(e)}")
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "table_name": table_name,
            "error": str(e)
        }


@app.get("/admin/docs/generate")
async def generate_docs():
    """生成API文档端点"""
    try:
        # 生成API文档
        generate_api_documentation(app, output_dir="docs/api")
        
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "message": "API文档已生成",
            "output_dir": "docs/api"
        }
    except Exception as e:
        logger.error(f"生成API文档失败: {str(e)}")
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "error": str(e)
        }


@app.get("/admin/tests/generate")
async def generate_tests():
    """生成测试用例端点"""
    try:
        # 生成测试用例
        generate_test_cases(app, output_dir="tests/api")
        
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "message": "测试用例已生成",
            "output_dir": "tests/api"
        }
    except Exception as e:
        logger.error(f"生成测试用例失败: {str(e)}")
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    # 启动应用
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=getattr(settings, 'ENVIRONMENT', 'development') == "development",
        log_level="info",
        access_log=True,
        # SSL配置
        ssl_keyfile=getattr(settings, 'SSL_KEYFILE', None),
        ssl_certfile=getattr(settings, 'SSL_CERTFILE', None),
    )