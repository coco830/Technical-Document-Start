from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta

from app.models.user import User
from app.core.database import get_db


class AuthLogService:
    """认证日志服务"""
    
    def create_log(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> Any:
        """创建认证日志"""
        # 这里需要创建一个AuthLog模型，但为了简化，我们暂时使用字典
        # 实际使用时应该创建对应的模型和表
        log_entry = {
            "user_id": user_id,
            "email": email,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "details": details or {},
            "created_at": datetime.utcnow()
        }
        
        # 在实际实现中，这里应该保存到数据库
        # db.add(AuthLog(**log_entry))
        # db.commit()
        
        # 为了演示，我们只是打印日志
        print(f"Auth Log: {log_entry}")
        return log_entry
    
    def get_user_logs(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取用户的认证日志"""
        # 在实际实现中，这里应该从数据库查询
        # logs = db.query(AuthLog).filter(AuthLog.user_id == user_id).order_by(desc(AuthLog.created_at)).offset(skip).limit(limit).all()
        
        # 为了演示，我们返回模拟数据
        return []
    
    def get_failed_attempts(
        self,
        db: Session,
        *,
        email: str,
        minutes: int = 30
    ) -> int:
        """获取指定时间内的失败尝试次数"""
        # 在实际实现中，这里应该从数据库查询
        # since = datetime.utcnow() - timedelta(minutes=minutes)
        # count = db.query(AuthLog).filter(
        #     and_(
        #         AuthLog.email == email,
        #         AuthLog.action == "login",
        #         AuthLog.success == False,
        #         AuthLog.created_at >= since
        #     )
        # ).count()
        
        # 为了演示，我们返回0
        return 0
    
    def get_recent_successful_logins(
        self,
        db: Session,
        *,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取用户最近的成功登录记录"""
        # 在实际实现中，这里应该从数据库查询
        # since = datetime.utcnow() - timedelta(days=days)
        # logs = db.query(AuthLog).filter(
        #     and_(
        #         AuthLog.user_id == user_id,
        #         AuthLog.action == "login",
        #         AuthLog.success == True,
        #         AuthLog.created_at >= since
        #     )
        # ).order_by(desc(AuthLog.created_at)).all()
        
        # 为了演示，我们返回模拟数据
        return []
    
    def get_login_statistics(
        self,
        db: Session,
        *,
        days: int = 7
    ) -> Dict[str, Any]:
        """获取登录统计信息"""
        # 在实际实现中，这里应该从数据库查询
        # since = datetime.utcnow() - timedelta(days=days)
        
        # 总登录次数
        # total_logins = db.query(AuthLog).filter(
        #     and_(
        #         AuthLog.action == "login",
        #         AuthLog.created_at >= since
        #     )
        # ).count()
        
        # 成功登录次数
        # successful_logins = db.query(AuthLog).filter(
        #     and_(
        #         AuthLog.action == "login",
        #         AuthLog.success == True,
        #         AuthLog.created_at >= since
        #     )
        # ).count()
        
        # 失败登录次数
        # failed_logins = total_logins - successful_logins
        
        # 按天统计
        # daily_stats = []
        # for i in range(days):
        #     day = datetime.utcnow() - timedelta(days=i)
        #     day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        #     day_end = day_start + timedelta(days=1)
        #     
        #     day_logins = db.query(AuthLog).filter(
        #         and_(
        #             AuthLog.action == "login",
        #             AuthLog.created_at >= day_start,
        #             AuthLog.created_at < day_end
        #         )
        #     ).count()
        #     
        #     day_successful = db.query(AuthLog).filter(
        #         and_(
        #             AuthLog.action == "login",
        #             AuthLog.success == True,
        #             AuthLog.created_at >= day_start,
        #             AuthLog.created_at < day_end
        #         )
        #     ).count()
        #     
        #     daily_stats.append({
        #         "date": day_start.date().isoformat(),
        #         "total": day_logins,
        #         "successful": day_successful,
        #         "failed": day_logins - day_successful
        #     })
        
        # 为了演示，我们返回模拟数据
        return {
            "total_logins": 0,
            "successful_logins": 0,
            "failed_logins": 0,
            "success_rate": 0.0,
            "daily_stats": []
        }


class SessionService:
    """会话管理服务"""
    
    def create_session(
        self,
        db: Session,
        *,
        user_id: int,
        token_hash: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        expires_in_minutes: int = 60 * 24 * 8  # 默认8天
    ) -> Any:
        """创建用户会话"""
        from app.models.user import UserSession
        from app.utils.datetime import utc_now
        
        expires_at = utc_now() + timedelta(minutes=expires_in_minutes)
        
        session = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def get_user_sessions(
        self,
        db: Session,
        *,
        user_id: int,
        active_only: bool = False
    ) -> List[Any]:
        """获取用户的所有会话"""
        from app.models.user import UserSession
        
        query = db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            from app.utils.datetime import utc_now
            query = query.filter(UserSession.expires_at > utc_now())
        
        return query.order_by(desc(UserSession.created_at)).all()
    
    def revoke_session(
        self,
        db: Session,
        *,
        session_id: int
    ) -> bool:
        """撤销指定会话"""
        from app.models.user import UserSession
        from app.utils.datetime import utc_now
        
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if not session:
            return False
        
        # 设置会话立即过期
        session.expires_at = utc_now()
        db.commit()
        
        return True
    
    def revoke_all_user_sessions(
        self,
        db: Session,
        *,
        user_id: int,
        except_current: bool = False
    ) -> int:
        """撤销用户的所有会话"""
        from app.models.user import UserSession
        from app.utils.datetime import utc_now
        
        query = db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if except_current:
            # 获取当前会话ID（如果有）
            # 这里需要从请求中获取当前会话ID
            # current_session_id = get_current_session_id()
            # query = query.filter(UserSession.id != current_session_id)
            pass
        
        # 设置所有会话立即过期
        count = query.count()
        query.update({"expires_at": utc_now()})
        db.commit()
        
        return count
    
    def cleanup_expired_sessions(self, db: Session) -> int:
        """清理过期的会话"""
        from app.models.user import UserSession
        from app.utils.datetime import utc_now
        
        count = db.query(UserSession).filter(UserSession.expires_at <= utc_now()).count()
        db.query(UserSession).filter(UserSession.expires_at <= utc_now()).delete()
        db.commit()
        
        return count
    
    def get_session_statistics(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """获取会话统计信息"""
        from app.models.user import UserSession
        from app.utils.datetime import utc_now
        
        # 总会话数
        total_sessions = db.query(UserSession).count()
        
        # 活跃会话数
        active_sessions = db.query(UserSession).filter(UserSession.expires_at > utc_now()).count()
        
        # 过期会话数
        expired_sessions = total_sessions - active_sessions
        
        # 按设备类型统计
        # device_stats = {}
        # sessions = db.query(UserSession).all()
        # for session in sessions:
        #     device = session.device_info or "Unknown"
        #     device_stats[device] = device_stats.get(device, 0) + 1
        
        # 为了演示，我们返回模拟数据
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "device_stats": {}
        }


# 创建服务实例
auth_log_service = AuthLogService()
session_service = SessionService()