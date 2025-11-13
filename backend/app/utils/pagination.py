"""
分页查询优化工具
提供高效的分页查询实现，避免深分页性能问题
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Generic
from sqlalchemy.orm import Query, Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel
from app.utils.query_monitor import log_pagination_performance

logger = logging.getLogger(__name__)

class PaginationParams:
    """分页参数类"""
    
    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        max_page_size: int = 100,
        cursor: Optional[str] = None
    ):
        self.page = max(1, page)  # 确保页码至少为1
        self.page_size = min(max(1, page_size), max_page_size)  # 限制页大小
        self.cursor = cursor
        self.offset = (self.page - 1) * self.page_size

class CursorPaginationResult:
    """游标分页结果"""
    
    def __init__(
        self,
        items: List[Any],
        next_cursor: Optional[str] = None,
        has_next: bool = False,
        has_previous: bool = False
    ):
        self.items = items
        self.next_cursor = next_cursor
        self.has_next = has_next
        self.has_previous = has_previous

class OffsetPaginationResult:
    """偏移分页结果"""
    
    def __init__(
        self,
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        total_pages: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages

def optimize_offset_pagination(
    query: Query,
    pagination: PaginationParams,
    db: Session
) -> OffsetPaginationResult:
    """
    优化偏移分页查询
    
    对于深分页使用子查询优化，避免性能问题
    """
    start_time = time.time()
    
    # 获取总数（不包含排序和关联加载）
    count_query = query.statement.with_only_columns([func.count()])
    total = db.execute(count_query).scalar()
    
    # 计算总页数
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    # 对于深分页（页码超过100），使用子查询优化
    if pagination.page > 100:
        logger.info(f"使用深分页优化 - 页码: {pagination.page}")
        
        # 获取主键列
        primary_key = query.column_descriptions[0]['type'].__table__.primary_key.columns.values()[0]
        
        # 使用子查询优化深分页
        subquery = query.with_entities(primary_key).order_by(primary_key).offset(pagination.offset).limit(pagination.page_size).subquery()
        
        # 主查询使用子查询结果
        items = query.join(subquery, primary_key == subquery.c[primary_key.name]).all()
    else:
        # 普通分页
        items = query.offset(pagination.offset).limit(pagination.page_size).all()
    
    # 记录性能
    duration = time.time() - start_time
    log_pagination_performance(pagination.page, pagination.page_size, total, duration)
    
    return OffsetPaginationResult(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages
    )

def cursor_pagination(
    query: Query,
    pagination: PaginationParams,
    cursor_field: str = "id",
    db: Session = None
) -> CursorPaginationResult:
    """
    游标分页查询
    适用于大数据集的高效分页
    """
    start_time = time.time()
    
    # 获取游标字段
    model = query.column_descriptions[0]['type']
    cursor_column = getattr(model, cursor_field)
    
    # 如果有游标，添加过滤条件
    if pagination.cursor:
        try:
            cursor_value = int(pagination.cursor)
            query = query.filter(cursor_column > cursor_value)
        except ValueError:
            logger.warning(f"无效的游标值: {pagination.cursor}")
    
    # 按游标字段排序并限制数量
    items = query.order_by(cursor_column).limit(pagination.page_size + 1).all()
    
    # 确定是否有下一页
    has_next = len(items) > pagination.page_size
    if has_next:
        items = items[:-1]  # 移除多查询的一项
    
    # 生成下一页游标
    next_cursor = None
    if has_next and items:
        next_cursor = str(getattr(items[-1], cursor_field))
    
    # 记录性能
    duration = time.time() - start_time
    logger.info(f"游标分页查询 - 耗时: {duration:.3f}s, 项目数: {len(items)}, 有下一页: {has_next}")
    
    return CursorPaginationResult(
        items=items,
        next_cursor=next_cursor,
        has_next=has_next,
        has_previous=bool(pagination.cursor)
    )

def search_optimized_pagination(
    query: Query,
    search_term: str,
    search_fields: List[str],
    pagination: PaginationParams,
    db: Session
) -> OffsetPaginationResult:
    """
    搜索优化的分页查询
    对于搜索结果使用特殊优化
    """
    start_time = time.time()
    
    # 构建搜索条件
    model = query.column_descriptions[0]['type']
    search_conditions = []
    
    for field in search_fields:
        if hasattr(model, field):
            field_attr = getattr(model, field)
            search_conditions.append(field_attr.ilike(f"%{search_term}%"))
    
    # 应用搜索条件
    if search_conditions:
        query = query.filter(or_(*search_conditions))
    
    # 使用优化的偏移分页
    result = optimize_offset_pagination(query, pagination, db)
    
    # 记录搜索性能
    duration = time.time() - start_time
    logger.info(f"搜索分页查询 - 搜索词: '{search_term}', 耗时: {duration:.3f}s, 结果数: {result.total}")
    
    return result

def get_pagination_recommendations(
    total: int,
    page: int,
    page_size: int,
    duration: float
) -> List[str]:
    """
    获取分页性能建议
    """
    recommendations = []
    
    # 检查深分页
    if page > 100:
        recommendations.append(
            f"深分页警告 (页码: {page})，建议使用游标分页或限制最大页码"
        )
    
    # 检查页大小
    if page_size > 50:
        recommendations.append(
            f"页大小较大 ({page_size})，建议减少页大小以提高性能"
        )
    
    # 检查查询时间
    if duration > 0.5:
        recommendations.append(
            f"查询时间较长 ({duration:.3f}s)，建议优化查询或添加索引"
        )
    
    # 检查总数据量
    if total > 10000:
        recommendations.append(
            f"数据集较大 ({total} 条记录)，建议使用缓存或搜索优化"
        )
    
    return recommendations

def create_pagination_response(
    result: Union[OffsetPaginationResult, CursorPaginationResult],
    request_path: str,
    additional_params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    创建标准化的分页响应
    """
    additional_params = additional_params or {}
    
    if isinstance(result, OffsetPaginationResult):
        response = {
            "items": result.items,
            "pagination": {
                "type": "offset",
                "page": result.page,
                "page_size": result.page_size,
                "total": result.total,
                "total_pages": result.total_pages,
                "has_next": result.page < result.total_pages,
                "has_previous": result.page > 1
            }
        }
        
        # 添加导航链接
        if result.page > 1:
            prev_params = {**additional_params, "page": result.page - 1, "page_size": result.page_size}
            response["pagination"]["prev_url"] = f"{request_path}?{ '&'.join([f'{k}={v}' for k, v in prev_params.items()]) }"
        
        if result.page < result.total_pages:
            next_params = {**additional_params, "page": result.page + 1, "page_size": result.page_size}
            response["pagination"]["next_url"] = f"{request_path}?{ '&'.join([f'{k}={v}' for k, v in next_params.items()]) }"
    
    elif isinstance(result, CursorPaginationResult):
        response = {
            "items": result.items,
            "pagination": {
                "type": "cursor",
                "page_size": len(result.items),
                "has_next": result.has_next,
                "has_previous": result.has_previous
            }
        }
        
        # 添加游标信息
        if result.next_cursor:
            next_params = {**additional_params, "cursor": result.next_cursor, "page_size": len(result.items)}
            response["pagination"]["next_url"] = f"{request_path}?{ '&'.join([f'{k}={v}' for k, v in next_params.items()]) }"
    
    return response


def get_pagination_params(page: int, page_size: int) -> PaginationParams:
    """获取分页参数"""
    return PaginationParams(page=page, page_size=page_size)


def paginate_query(query, page: int, page_size: int, db: Session = None):
    """分页查询函数"""
    pagination_params = get_pagination_params(page, page_size)
    if db is None:
        from app.database import get_db
        db = next(get_db())
    return optimize_offset_pagination(query, pagination_params, db)


class PaginatedResponse(BaseModel):
    """分页响应基类"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)