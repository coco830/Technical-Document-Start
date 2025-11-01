"""
异步任务处理模块
使用Celery实现后台任务队列
"""
import logging
from typing import Any, Dict, Optional, Callable
from celery import Celery
from celery.result import AsyncResult

from app.core.config import settings

# 设置日志
logger = logging.getLogger(__name__)

# 创建Celery实例
celery_app = Celery(
    "yueen_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # 任务路由配置
    task_routes={
        "app.tasks.ai_generation.*": {"queue": "ai_generation"},
        "app.tasks.document_export.*": {"queue": "document_export"},
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.notification.*": {"queue": "notification"},
    },
    # 队列配置
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "ai_generation": {
            "exchange": "ai_generation",
            "routing_key": "ai_generation",
        },
        "document_export": {
            "exchange": "document_export",
            "routing_key": "document_export",
        },
        "email": {
            "exchange": "email",
            "routing_key": "email",
        },
        "notification": {
            "exchange": "notification",
            "routing_key": "notification",
        },
    }
)


class TaskManager:
    """任务管理器，提供高级任务操作"""
    
    @staticmethod
    def send_task(task_name: str, args: tuple = (), kwargs: dict = None, queue: str = None) -> AsyncResult:
        """
        发送任务到队列
        
        Args:
            task_name: 任务名称
            args: 位置参数
            kwargs: 关键字参数
            queue: 队列名称
            
        Returns:
            任务结果对象
        """
        try:
            result = celery_app.send_task(
                task_name, 
                args=args, 
                kwargs=kwargs or {},
                queue=queue
            )
            logger.info(f"任务已发送: {task_name} - ID: {result.id}")
            return result
        except Exception as e:
            logger.error(f"发送任务失败: {task_name} - 错误: {str(e)}")
            raise
    
    @staticmethod
    def get_task_result(task_id: str) -> Optional[Any]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        try:
            result = AsyncResult(task_id, app=celery_app)
            return result.get(timeout=1) if result.ready() else None
        except Exception as e:
            logger.error(f"获取任务结果失败: {task_id} - 错误: {str(e)}")
            return None
    
    @staticmethod
    def get_task_status(task_id: str) -> Optional[str]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态
        """
        try:
            result = AsyncResult(task_id, app=celery_app)
            return result.status if result else None
        except Exception as e:
            logger.error(f"获取任务状态失败: {task_id} - 错误: {str(e)}")
            return None
    
    @staticmethod
    def revoke_task(task_id: str, terminate: bool = False) -> bool:
        """
        撤销任务
        
        Args:
            task_id: 任务ID
            terminate: 是否强制终止
            
        Returns:
            是否成功
        """
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"任务已撤销: {task_id} - 终止: {terminate}")
            return True
        except Exception as e:
            logger.error(f"撤销任务失败: {task_id} - 错误: {str(e)}")
            return False
    
    @staticmethod
    def get_active_tasks() -> Dict[str, Any]:
        """
        获取活动任务
        
        Returns:
            活动任务信息
        """
        try:
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            return active_tasks or {}
        except Exception as e:
            logger.error(f"获取活动任务失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_scheduled_tasks() -> Dict[str, Any]:
        """
        获取计划任务
        
        Returns:
            计划任务信息
        """
        try:
            inspect = celery_app.control.inspect()
            scheduled_tasks = inspect.scheduled()
            return scheduled_tasks or {}
        except Exception as e:
            logger.error(f"获取计划任务失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_reserved_tasks() -> Dict[str, Any]:
        """
        获取预留任务
        
        Returns:
            预留任务信息
        """
        try:
            inspect = celery_app.control.inspect()
            reserved_tasks = inspect.reserved()
            return reserved_tasks or {}
        except Exception as e:
            logger.error(f"获取预留任务失败: {str(e)}")
            return {}
    
    @staticmethod
    def get_worker_stats() -> Dict[str, Any]:
        """
        获取工作进程统计
        
        Returns:
            工作进程统计信息
        """
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            return stats or {}
        except Exception as e:
            logger.error(f"获取工作进程统计失败: {str(e)}")
            return {}
    
    @staticmethod
    def purge_queue(queue: str = None) -> bool:
        """
        清空队列
        
        Args:
            queue: 队列名称，None表示清空所有队列
            
        Returns:
            是否成功
        """
        try:
            with celery_app.pool.acquire(block=True) as conn:
                if queue:
                    conn.default_channel.queue_purge(queue)
                    logger.info(f"队列已清空: {queue}")
                else:
                    # 清空所有队列
                    for q in celery_app.conf.task_queues.keys():
                        conn.default_channel.queue_purge(q)
                        logger.info(f"队列已清空: {q}")
                return True
        except Exception as e:
            logger.error(f"清空队列失败: {queue} - 错误: {str(e)}")
            return False


def task(queue: str = None, bind: bool = True):
    """
    任务装饰器
    
    Args:
        queue: 队列名称
        bind: 是否绑定任务实例
    """
    def decorator(func: Callable) -> Callable:
        return celery_app.task(func, queue=queue, bind=bind)
    return decorator


# 创建任务管理器实例
task_manager = TaskManager()