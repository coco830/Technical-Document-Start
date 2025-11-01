"""
增强的日志服务
提供结构化日志、日志聚合、性能监控等功能
"""
import logging
import json
import time
import traceback
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.core.cache import cache_service

# 日志级别
LOG_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10
}

# 日志格式
class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 基本日志信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, name: str = "performance"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 创建处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
    
    def log_request(self, method: str, url: str, status_code: int, 
                   response_time: float, user_id: Optional[str] = None, 
                   request_id: Optional[str] = None, **kwargs):
        """记录请求日志"""
        self.logger.info(
            f"{method} {url} - {status_code}",
            extra={
                "extra_fields": {
                    "event_type": "http_request",
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "response_time_ms": response_time * 1000,
                    "user_id": user_id,
                    "request_id": request_id,
                    **kwargs
                }
            }
        )
    
    def log_database_query(self, query: str, execution_time: float, 
                         rows_affected: Optional[int] = None, **kwargs):
        """记录数据库查询日志"""
        self.logger.info(
            f"DB Query: {query[:100]}...",
            extra={
                "extra_fields": {
                    "event_type": "database_query",
                    "query": query,
                    "execution_time_ms": execution_time * 1000,
                    "rows_affected": rows_affected,
                    **kwargs
                }
            }
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, 
                        execution_time: float, **kwargs):
        """记录缓存操作日志"""
        self.logger.info(
            f"Cache {operation}: {key} - {'HIT' if hit else 'MISS'}",
            extra={
                "extra_fields": {
                    "event_type": "cache_operation",
                    "operation": operation,
                    "key": key,
                    "hit": hit,
                    "execution_time_ms": execution_time * 1000,
                    **kwargs
                }
            }
        )
    
    def log_ai_generation(self, generation_id: str, model: str, prompt_length: int, 
                       response_length: int, generation_time: float, 
                       status: str, **kwargs):
        """记录AI生成日志"""
        self.logger.info(
            f"AI Generation: {generation_id} - {status}",
            extra={
                "extra_fields": {
                    "event_type": "ai_generation",
                    "generation_id": generation_id,
                    "model": model,
                    "prompt_length": prompt_length,
                    "response_length": response_length,
                    "generation_time_ms": generation_time * 1000,
                    "status": status,
                    **kwargs
                }
            }
        )


class ErrorTracker:
    """错误跟踪器"""
    
    def __init__(self, name: str = "error_tracker"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.ERROR)
        
        # 创建处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
    
    def track_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, 
                  user_id: Optional[str] = None, request_id: Optional[str] = None):
        """跟踪错误"""
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}",
            extra={
                "extra_fields": {
                    "event_type": "error",
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "error_traceback": traceback.format_exc(),
                    "context": context or {},
                    "user_id": user_id,
                    "request_id": request_id
                }
            }
        )
    
    def track_exception(self, func_name: str, args: tuple, kwargs: dict, 
                      exception: Exception, user_id: Optional[str] = None):
        """跟踪函数异常"""
        self.track_error(
            exception,
            context={
                "function": func_name,
                "args": str(args)[:200],  # 限制长度
                "kwargs": str(kwargs)[:200]  # 限制长度
            },
            user_id=user_id
        )


class LogAggregator:
    """日志聚合器"""
    
    def __init__(self):
        self.logger = logging.getLogger("log_aggregator")
        self.logger.setLevel(logging.INFO)
        
        # 创建处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
    
    def aggregate_hourly_stats(self) -> Dict[str, Any]:
        """聚合每小时统计"""
        # 从缓存获取统计数据
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 记录聚合统计
        self.logger.info(
            "Hourly stats aggregation",
            extra={
                "extra_fields": {
                    "event_type": "hourly_stats",
                    "stats": stats
                }
            }
        )
        
        return stats
    
    def update_request_stats(self, response_time: float, is_error: bool = False):
        """更新请求统计"""
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 更新请求统计
        stats["requests"]["count"] += 1
        current_avg = stats["requests"]["avg_response_time"]
        count = stats["requests"]["count"]
        stats["requests"]["avg_response_time"] = (current_avg * (count - 1) + response_time) / count
        
        if is_error:
            stats["requests"]["error_rate"] = (stats["requests"]["error_rate"] * (count - 1) + 1) / count
        
        # 保存到缓存（1小时过期）
        cache_service.set(cache_key, stats, ttl=3600)
    
    def update_database_stats(self, execution_time: float):
        """更新数据库统计"""
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 更新数据库查询统计
        stats["database_queries"]["count"] += 1
        current_avg = stats["database_queries"]["avg_execution_time"]
        count = stats["database_queries"]["count"]
        stats["database_queries"]["avg_execution_time"] = (current_avg * (count - 1) + execution_time) / count
        
        # 保存到缓存（1小时过期）
        cache_service.set(cache_key, stats, ttl=3600)
    
    def update_cache_stats(self, hit: bool):
        """更新缓存统计"""
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 更新缓存操作统计
        stats["cache_operations"]["count"] += 1
        current_hits = stats["cache_operations"]["hit_rate"] * (stats["cache_operations"]["count"] - 1)
        stats["cache_operations"]["hit_rate"] = (current_hits + (1 if hit else 0)) / stats["cache_operations"]["count"]
        
        # 保存到缓存（1小时过期）
        cache_service.set(cache_key, stats, ttl=3600)
    
    def update_ai_generation_stats(self, generation_time: float, success: bool):
        """更新AI生成统计"""
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 更新AI生成统计
        stats["ai_generations"]["count"] += 1
        current_avg_time = stats["ai_generations"]["avg_generation_time"]
        current_success_rate = stats["ai_generations"]["success_rate"]
        count = stats["ai_generations"]["count"]
        
        stats["ai_generations"]["avg_generation_time"] = (current_avg_time * (count - 1) + generation_time) / count
        stats["ai_generations"]["success_rate"] = (current_success_rate * (count - 1) + (1 if success else 0)) / count
        
        # 保存到缓存（1小时过期）
        cache_service.set(cache_key, stats, ttl=3600)
    
    def update_error_stats(self, error_type: str):
        """更新错误统计"""
        cache_key = "hourly_stats"
        stats = cache_service.get(cache_key) or {
            "requests": {"count": 0, "avg_response_time": 0, "error_rate": 0},
            "database_queries": {"count": 0, "avg_execution_time": 0},
            "cache_operations": {"count": 0, "hit_rate": 0},
            "ai_generations": {"count": 0, "avg_generation_time": 0, "success_rate": 0},
            "errors": {"count": 0, "by_type": {}}
        }
        
        # 更新错误统计
        stats["errors"]["count"] += 1
        if error_type not in stats["errors"]["by_type"]:
            stats["errors"]["by_type"][error_type] = 0
        stats["errors"]["by_type"][error_type] += 1
        
        # 保存到缓存（1小时过期）
        cache_service.set(cache_key, stats, ttl=3600)


class LogFileHandler:
    """日志文件处理器"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建不同级别的日志文件
        self.log_files = {
            "DEBUG": self.log_dir / "debug.log",
            "INFO": self.log_dir / "info.log",
            "WARNING": self.log_dir / "warning.log",
            "ERROR": self.log_dir / "error.log",
            "CRITICAL": self.log_dir / "critical.log"
        }
        
        self.log_level = LOG_LEVELS.get(log_level.upper(), LOG_LEVELS["INFO"])
        
        # 创建文件处理器
        self.handlers = {}
        for level, file_path in self.log_files.items():
            if LOG_LEVELS[level] >= self.log_level:
                handler = logging.FileHandler(file_path)
                handler.setFormatter(StructuredFormatter())
                self.handlers[level] = handler
    
    def get_handler(self, level: str) -> Optional[logging.Handler]:
        """获取指定级别的处理器"""
        return self.handlers.get(level.upper())
    
    def setup_logger(self, logger_name: str) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        
        # 添加所有适用的处理器
        for level, handler in self.handlers.items():
            logger.addHandler(handler)
        
        return logger


def setup_logging():
    """设置应用日志"""
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(settings, 'LOG_LEVEL', 'INFO'))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # 添加文件处理器（如果配置了日志目录）
    if hasattr(settings, 'LOG_DIR'):
        file_handler = LogFileHandler(
            log_dir=settings.LOG_DIR,
            log_level=getattr(settings, 'LOG_LEVEL', 'INFO')
        )
        
        # 为不同模块设置专门的日志记录器
        module_loggers = [
            "app.api",
            "app.core",
            "app.services",
            "app.tasks",
            "performance",
            "error_tracker",
            "log_aggregator"
        ]
        
        for module_name in module_loggers:
            logger = file_handler.setup_logger(module_name)
            logger.propagate = False  # 防止传播到根日志记录器
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)


# 创建全局实例
performance_logger = PerformanceLogger()
error_tracker = ErrorTracker()
log_aggregator = LogAggregator()