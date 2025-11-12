"""
错误监控路由
提供错误统计、监控和管理功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from ..utils.error_handler import error_monitor, fallback_handler, ErrorSeverity, ErrorCategory
from ..utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/error-monitoring", tags=["error-monitoring"])


@router.get("/summary")
async def get_error_summary(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取错误摘要统计"""
    try:
        summary = error_monitor.get_error_summary()
        
        # 添加额外的统计信息
        summary["service_health"] = {
            "status": "healthy" if summary["recent_errors_24h"] < 50 else "degraded",
            "error_rate": calculate_error_rate(),
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"获取错误摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取错误摘要失败")


@router.get("/errors")
async def get_recent_errors(
    limit: int = Query(50, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # 最多7天
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取最近的错误列表"""
    try:
        # 过滤错误
        filtered_errors = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for error_info in error_monitor.errors:
            if error_info.timestamp < cutoff_time:
                continue
                
            if severity and error_info.severity.value != severity:
                continue
                
            if category and error_info.category.value != category:
                continue
                
            filtered_errors.append(error_info.to_dict())
        
        # 按时间倒序排列
        filtered_errors.sort(
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        return {
            "success": True,
            "data": {
                "errors": filtered_errors[:limit],
                "total": len(filtered_errors),
                "filters": {
                    "severity": severity,
                    "category": category,
                    "hours": hours
                }
            }
        }
    except Exception as e:
        logger.error(f"获取错误列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取错误列表失败")


@router.get("/stats")
async def get_error_stats(
    days: int = Query(7, ge=1, le=30),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取错误统计信息"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_errors = [
            error for error in error_monitor.errors
            if error.timestamp > cutoff_time
        ]
        
        # 按日期分组统计
        daily_stats = {}
        for error in recent_errors:
            date_key = error.timestamp.strftime("%Y-%m-%d")
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "total": 0,
                    "by_category": {},
                    "by_severity": {}
                }
            
            daily_stats[date_key]["total"] += 1
            
            category = error.category.value
            daily_stats[date_key]["by_category"][category] = \
                daily_stats[date_key]["by_category"].get(category, 0) + 1
            
            severity = error.severity.value
            daily_stats[date_key]["by_severity"][severity] = \
                daily_stats[date_key]["by_severity"].get(severity, 0) + 1
        
        # 计算趋势
        dates = sorted(daily_stats.keys())
        trend = "stable"
        if len(dates) >= 2:
            recent_avg = sum(daily_stats[d]["total"] for d in dates[-3:]) / min(3, len(dates))
            earlier_avg = sum(daily_stats[d]["total"] for d in dates[:-3]) / max(1, len(dates) - 3)
            if recent_avg > earlier_avg * 1.2:
                trend = "increasing"
            elif recent_avg < earlier_avg * 0.8:
                trend = "decreasing"
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "total_errors": len(recent_errors),
                "daily_stats": daily_stats,
                "trend": trend,
                "top_errors": get_top_errors(recent_errors)
            }
        }
    except Exception as e:
        logger.error(f"获取错误统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取错误统计失败")


@router.get("/health")
async def get_system_health(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取系统健康状态"""
    try:
        summary = error_monitor.get_error_summary()
        error_rate = calculate_error_rate()
        
        # 确定健康状态
        if error_rate < 0.01:  # 小于1%
            status = "healthy"
            status_code = 200
        elif error_rate < 0.05:  # 小于5%
            status = "degraded"
            status_code = 200
        else:
            status = "unhealthy"
            status_code = 503
        
        # 检查关键错误
        critical_errors = summary.get("recent_critical_errors", [])
        if critical_errors:
            status = "unhealthy"
            status_code = 503
        
        return {
            "success": True,
            "data": {
                "status": status,
                "error_rate": error_rate,
                "total_errors": summary["total_errors"],
                "recent_errors_24h": summary["recent_errors_24h"],
                "critical_errors_count": len(critical_errors),
                "last_updated": datetime.now().isoformat()
            }
        }, status_code
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        return {
            "success": False,
            "data": {
                "status": "unknown",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
        }, 500


@router.post("/clear")
async def clear_error_history(
    days: int = Query(7, ge=1, le=30),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """清除错误历史记录"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 保留最近的错误
        error_monitor.errors = [
            error for error in error_monitor.errors
            if error.timestamp > cutoff_time
        ]
        
        logger.info(f"清除了 {days} 天前的错误记录")
        
        return {
            "success": True,
            "message": f"已清除 {days} 天前的错误记录",
            "remaining_errors": len(error_monitor.errors)
        }
    except Exception as e:
        logger.error(f"清除错误记录失败: {e}")
        raise HTTPException(status_code=500, detail="清除错误记录失败")


@router.get("/fallbacks")
async def get_fallback_services(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取降级服务列表"""
    try:
        fallback_services = list(fallback_handler.fallbacks.keys())
        
        return {
            "success": True,
            "data": {
                "services": fallback_services,
                "total": len(fallback_services)
            }
        }
    except Exception as e:
        logger.error(f"获取降级服务列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取降级服务列表失败")


def calculate_error_rate() -> float:
    """计算错误率"""
    try:
        # 这里应该基于总请求数计算，简化版本使用错误数量
        recent_errors = len([
            error for error in error_monitor.errors
            if error.timestamp > datetime.now() - timedelta(hours=24)
        ])
        
        # 假设每小时有100个请求作为基准
        total_requests = 24 * 100
        return recent_errors / total_requests if total_requests > 0 else 0
    except Exception:
        return 0


def get_top_errors(errors: List, limit: int = 10) -> List[Dict[str, Any]]:
    """获取最常见的错误"""
    try:
        error_counts = {}
        
        for error in errors:
            key = f"{error.error.__class__.__name__}:{error.category.value}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        # 按频率排序
        sorted_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "error_type": error_type,
                "count": count,
                "percentage": (count / len(errors)) * 100
            }
            for error_type, count in sorted_errors[:limit]
        ]
    except Exception:
        return []