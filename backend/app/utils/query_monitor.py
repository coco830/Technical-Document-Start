"""
查询性能监控工具
用于监控和记录数据库查询性能
"""

import time
import logging
from functools import wraps
from typing import Callable, Any
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 配置日志
logger = logging.getLogger(__name__)

# 查询性能阈值（秒）
SLOW_QUERY_THRESHOLD = 0.5  # 超过0.5秒的查询被认为是慢查询

class QueryMonitor:
    """查询性能监控器"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_count = 0
        self.total_time = 0
    
    def log_slow_query(self, query: str, duration: float, params: dict = None):
        """记录慢查询"""
        self.slow_queries.append({
            'query': query,
            'duration': duration,
            'params': params,
            'timestamp': time.time()
        })
        
        logger.warning(
            f"慢查询检测 - 耗时: {duration:.3f}s - SQL: {query[:200]}..."
            f"{' - 参数: ' + str(params) if params else ''}"
        )
    
    def get_stats(self) -> dict:
        """获取查询统计信息"""
        avg_time = self.total_time / self.query_count if self.query_count > 0 else 0
        return {
            'query_count': self.query_count,
            'total_time': self.total_time,
            'avg_time': avg_time,
            'slow_query_count': len(self.slow_queries),
            'slow_queries': self.slow_queries[-10:]  # 最近10个慢查询
        }

# 全局查询监控器实例
query_monitor = QueryMonitor()

def monitor_query_performance(func: Callable) -> Callable:
    """
    装饰器：监控函数执行时间
    用于监控路由处理函数的性能
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            if duration > SLOW_QUERY_THRESHOLD:
                logger.warning(f"慢路由检测 - 函数: {func.__name__} - 耗时: {duration:.3f}s")
            else:
                logger.debug(f"路由执行 - 函数: {func.__name__} - 耗时: {duration:.3f}s")
    return wrapper

def setup_sqlalchemy_monitoring(engine: Engine):
    """
    设置SQLAlchemy查询监控
    """
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        duration = time.time() - context._query_start_time
        query_monitor.query_count += 1
        query_monitor.total_time += duration
        
        # 记录慢查询
        if duration > SLOW_QUERY_THRESHOLD:
            query_monitor.log_slow_query(statement, duration, parameters)
        else:
            logger.debug(f"SQL查询 - 耗时: {duration:.3f}s - SQL: {statement[:100]}...")

def log_pagination_performance(page: int, page_size: int, total: int, duration: float):
    """
    记录分页查询性能
    """
    total_pages = (total + page_size - 1) // page_size
    logger.info(
        f"分页查询性能 - 页码: {page}/{total_pages}, "
        f"页大小: {page_size}, 总数: {total}, 耗时: {duration:.3f}s"
    )
    
    # 检查分页效率
    if page > 100 and duration > 0.1:
        logger.warning(
            f"深分页性能警告 - 页码: {page}, 耗时: {duration:.3f}s. "
            f"建议使用基于游标的分页或限制最大页码"
        )

def optimize_pagination_query(query, page: int, page_size: int):
    """
    优化分页查询
    对于深分页使用更高效的查询方式
    """
    # 对于深分页（页码超过100），使用子查询优化
    if page > 100:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 使用子查询优化深分页
        subquery = query.order_by(query.column_descriptions[0]['type'].id).offset(offset).limit(page_size).subquery()
        return query.session.query(query.column_descriptions[0]['type']).join(subquery)
    
    # 对于普通分页，使用标准方式
    return query.offset((page - 1) * page_size).limit(page_size)

def get_query_recommendations() -> list:
    """
    基于查询性能数据获取优化建议
    """
    recommendations = []
    stats = query_monitor.get_stats()
    
    # 检查慢查询数量
    if stats['slow_query_count'] > 0:
        recommendations.append(
            f"检测到 {stats['slow_query_count']} 个慢查询，建议检查索引和查询优化"
        )
    
    # 检查平均查询时间
    if stats['avg_time'] > 0.2:
        recommendations.append(
            f"平均查询时间较长 ({stats['avg_time']:.3f}s)，建议优化数据库查询"
        )
    
    # 检查查询总数
    if stats['query_count'] > 1000:
        recommendations.append(
            f"查询总数较多 ({stats['query_count']})，建议考虑使用缓存或批量查询"
        )
    
    return recommendations