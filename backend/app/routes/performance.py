"""
性能监控路由
提供数据库查询性能统计和优化建议
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database import get_db, get_db_stats
from app.models.user import User
from app.utils.auth import get_current_user, require_admin
from app.utils.query_monitor import get_query_recommendations, query_monitor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["性能监控"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_performance_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据库查询性能统计信息
    
    需要管理员权限
    """
    # 检查管理员权限
    if not require_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        # 获取查询统计信息
        stats = get_db_stats()
        
        # 获取优化建议
        recommendations = get_query_recommendations()
        
        return {
            "query_stats": stats,
            "recommendations": recommendations,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"获取性能统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取性能统计失败"
        )

@router.get("/slow-queries", response_model=List[Dict[str, Any]])
async def get_slow_queries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取慢查询列表
    
    需要管理员权限
    """
    # 检查管理员权限
    if not require_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        # 获取慢查询列表
        slow_queries = query_monitor.slow_queries
        
        # 格式化慢查询信息
        formatted_queries = []
        for query in slow_queries[-20:]:  # 返回最近20个慢查询
            formatted_queries.append({
                "query": query["query"][:200] + "..." if len(query["query"]) > 200 else query["query"],
                "duration": round(query["duration"], 3),
                "params": query.get("params"),
                "timestamp": query["timestamp"]
            })
        
        return formatted_queries
    except Exception as e:
        logger.error(f"获取慢查询列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取慢查询列表失败"
        )

@router.post("/reset-stats", response_model=Dict[str, str])
async def reset_performance_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重置性能统计信息
    
    需要管理员权限
    """
    # 检查管理员权限
    if not require_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        # 重置统计信息
        query_monitor.slow_queries = []
        query_monitor.query_count = 0
        query_monitor.total_time = 0
        
        logger.info(f"管理员 {current_user.id} 重置了性能统计信息")
        
        return {"message": "性能统计信息已重置", "status": "success"}
    except Exception as e:
        logger.error(f"重置性能统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置性能统计失败"
        )

@router.get("/health", response_model=Dict[str, Any])
async def get_database_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据库健康状态
    
    需要管理员权限
    """
    # 检查管理员权限
    if not require_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        # 执行简单查询测试数据库连接
        db.execute("SELECT 1")
        
        # 获取性能统计
        stats = get_db_stats()
        
        # 计算健康状态
        health_score = 100
        issues = []
        
        # 检查慢查询
        if stats['slow_query_count'] > 10:
            health_score -= 20
            issues.append(f"检测到 {stats['slow_query_count']} 个慢查询")
        
        # 检查平均查询时间
        if stats['avg_time'] > 0.5:
            health_score -= 15
            issues.append(f"平均查询时间过长: {stats['avg_time']:.3f}s")
        
        # 检查查询总数
        if stats['query_count'] > 10000:
            health_score -= 10
            issues.append(f"查询总数过多: {stats['query_count']}")
        
        # 确定健康状态
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "query_stats": stats,
            "database_connected": True
        }
    except Exception as e:
        logger.error(f"获取数据库健康状态失败: {str(e)}")
        return {
            "status": "error",
            "health_score": 0,
            "issues": [f"数据库连接错误: {str(e)}"],
            "database_connected": False
        }