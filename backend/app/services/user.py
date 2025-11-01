from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta

from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserUpdate, UserPreferencesUpdate
from app.services.base import CRUDBase
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_multi_active(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return (
            db.query(self.model)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_role(
        self, db: Session, *, role: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return (
            db.query(self.model)
            .filter(User.role == role)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_users(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return (
            db.query(self.model)
            .filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.full_name.ilike(f"%{query}%"),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            is_active=True,
            is_verified=False,
            role="user",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password_hash"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def update_last_login(self, db: Session, *, user: User) -> User:
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    def update_preferences(
        self, db: Session, *, user: User, preferences_in: UserPreferencesUpdate
    ) -> User:
        # 这里假设User模型有一个preferences字段来存储用户偏好设置
        # 如果没有，可以添加一个JSON字段或者单独的表
        update_data = preferences_in.dict(exclude_unset=True)
        return self.update(db, db_obj=user, obj_in=update_data)

    def activate_user(self, db: Session, *, user: User) -> User:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user

    def deactivate_user(self, db: Session, *, user: User) -> User:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def verify_user(self, db: Session, *, user: User) -> User:
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user

    def change_role(self, db: Session, *, user: User, new_role: str) -> User:
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def authenticate_by_username(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_verified(self, user: User) -> bool:
        return user.is_verified

    def is_superuser(self, user: User) -> bool:
        return user.role == "admin"

    def has_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有特定权限"""
        # 简单的权限检查，可以根据需要扩展
        if user.role == "admin":
            return True
        
        # 可以在这里添加更复杂的权限逻辑
        # 例如：检查用户角色与权限的映射关系
        permission_map = {
            "user": ["read_own", "write_own"],
            "manager": ["read_own", "write_own", "read_team", "write_team"],
            "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin"],
        }
        
        user_permissions = permission_map.get(user.role, [])
        return permission in user_permissions

    def get_user_statistics(self, db: Session) -> Dict[str, Any]:
        """获取用户统计信息"""
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        
        # 今日新增用户
        today = datetime.utcnow().date()
        new_users_today = db.query(User).filter(
            and_(
                User.created_at >= today,
                User.created_at < today + timedelta(days=1)
            )
        ).count()
        
        # 本周新增用户
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_this_week = db.query(User).filter(User.created_at >= week_ago).count()
        
        # 本月新增用户
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_users_this_month = db.query(User).filter(User.created_at >= month_ago).count()
        
        # 按角色统计
        users_by_role = {}
        for role in ["user", "admin"]:
            count = db.query(User).filter(User.role == role).count()
            users_by_role[role] = count
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "new_users_today": new_users_today,
            "new_users_this_week": new_users_this_week,
            "new_users_this_month": new_users_this_month,
            "users_by_role": users_by_role,
        }


class CRUDUserSession(CRUDBase[UserSession, dict, dict]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> List[UserSession]:
        return (
            db.query(self.model)
            .filter(UserSession.user_id == user_id)
            .order_by(desc(UserSession.created_at))
            .all()
        )

    def get_active_sessions(self, db: Session, *, user_id: int) -> List[UserSession]:
        now = datetime.utcnow()
        return (
            db.query(self.model)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.expires_at > now
                )
            )
            .order_by(desc(UserSession.created_at))
            .all()
        )

    def create_session(
        self,
        db: Session,
        *,
        user_id: int,
        token_hash: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        expires_in_minutes: int = 60 * 24 * 8  # 默认8天
    ) -> UserSession:
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        db_obj = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def revoke_session(self, db: Session, *, session_id: int) -> UserSession:
        session = self.get(db, id=session_id)
        if session:
            session.expires_at = datetime.utcnow()  # 立即过期
            db.commit()
            db.refresh(session)
        return session

    def revoke_all_user_sessions(self, db: Session, *, user_id: int) -> int:
        count = (
            db.query(self.model)
            .filter(UserSession.user_id == user_id)
            .update({"expires_at": datetime.utcnow()})
        )
        db.commit()
        return count

    def cleanup_expired_sessions(self, db: Session) -> int:
        """清理过期的会话"""
        now = datetime.utcnow()
        count = (
            db.query(self.model)
            .filter(UserSession.expires_at <= now)
            .delete()
        )
        db.commit()
        return count


user = CRUDUser(User)
user_session = CRUDUserSession(UserSession)