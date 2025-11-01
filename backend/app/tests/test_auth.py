import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.services.user import user
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token
from app.schemas.user import UserCreate, UserLogin


class TestAuthAPI:
    """认证API测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        # 创建测试数据库会话
        self.db = next(get_db())
        
        # 创建测试用户
        test_user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        self.test_user = user.create(self.db, obj_in=test_user_data)
        
        # 创建测试客户端
        self.client = TestClient(app)
    
    def teardown_method(self):
        """测试后的清理"""
        # 清理测试数据
        self.db.query(User).filter(User.email == "test@example.com").delete()
        self.db.commit()
        self.db.close()
    
    def test_login_success(self):
        """测试登录成功"""
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_invalid_credentials(self):
        """测试登录失败 - 无效凭据"""
        login_data = {
            "username": "test@example.com",
            "password": "WrongPassword"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "用户名或密码错误" in data["detail"]
    
    def test_login_missing_fields(self):
        """测试登录失败 - 缺少字段"""
        # 缺少密码
        login_data = {
            "username": "test@example.com"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422
        
        # 缺少用户名
        login_data = {
            "password": "TestPassword123"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422
    
    def test_register_success(self):
        """测试注册成功"""
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "full_name": "New User"
        }
        
        response = self.client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        
        # 验证用户已创建
        db_user = user.get_by_email(self.db, email="newuser@example.com")
        assert db_user is not None
        assert db_user.username == "newuser"
        
        # 清理测试数据
        self.db.query(User).filter(User.email == "newuser@example.com").delete()
        self.db.commit()
    
    def test_register_duplicate_email(self):
        """测试注册失败 - 邮箱已存在"""
        register_data = {
            "username": "newuser2",
            "email": "test@example.com",  # 已存在的邮箱
            "password": "NewPassword123",
            "full_name": "New User 2"
        }
        
        response = self.client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "邮箱已存在" in data["detail"]
    
    def test_register_duplicate_username(self):
        """测试注册失败 - 用户名已存在"""
        register_data = {
            "username": "testuser",  # 已存在的用户名
            "email": "newuser3@example.com",
            "password": "NewPassword123",
            "full_name": "New User 3"
        }
        
        response = self.client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "用户名已存在" in data["detail"]
    
    def test_register_invalid_password(self):
        """测试注册失败 - 密码不符合要求"""
        register_data = {
            "username": "newuser4",
            "email": "newuser4@example.com",
            "password": "123",  # 太短的密码
            "full_name": "New User 4"
        }
        
        response = self.client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 422
    
    def test_logout_success(self):
        """测试登出成功"""
        # 先登录
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123"
        }
        login_response = self.client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 登出
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "登出成功"
    
    def test_logout_unauthorized(self):
        """测试登出失败 - 未授权"""
        response = self.client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
    
    def test_get_current_user_success(self):
        """测试获取当前用户信息成功"""
        # 先登录
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123"
        }
        login_response = self.client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self):
        """测试获取当前用户信息失败 - 未授权"""
        response = self.client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self):
        """测试刷新token成功"""
        # 先登录
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123"
        }
        login_response = self.client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json().get("refresh_token")
        
        if not refresh_token:
            pytest.skip("No refresh token returned")
        
        # 刷新token
        headers = {"X-Refresh-Token": refresh_token}
        response = self.client.post("/api/v1/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self):
        """测试刷新token失败 - 无效token"""
        headers = {"X-Refresh-Token": "invalid_token"}
        response = self.client.post("/api/v1/auth/refresh", headers=headers)
        
        assert response.status_code == 401
    
    @patch('app.utils.email.send_verification_email')
    def test_send_verification_code_success(self, mock_send_email):
        """测试发送验证码成功"""
        mock_send_email.return_value = True
        
        response = self.client.post(
            "/api/v1/auth/send-verification-code",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "验证码已发送"
        
        # 验证邮件发送函数被调用
        mock_send_email.assert_called_once()
    
    @patch('app.utils.email.send_password_reset_email')
    def test_reset_password_success(self, mock_send_email):
        """测试重置密码成功"""
        mock_send_email.return_value = True
        
        response = self.client.post(
            "/api/v1/auth/reset-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "重置密码链接已发送到您的邮箱"
        
        # 验证邮件发送函数被调用
        mock_send_email.assert_called_once()
    
    def test_reset_password_nonexistent_user(self):
        """测试重置密码 - 用户不存在"""
        with patch('app.utils.email.send_password_reset_email', return_value=True):
            response = self.client.post(
                "/api/v1/auth/reset-password",
                json={"email": "nonexistent@example.com"}
            )
            
            # 即使用户不存在，也应该返回成功消息（安全考虑）
            assert response.status_code == 200
            data = response.json()
            assert "message" in data


class TestUserService:
    """用户服务测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.db = next(get_db())
    
    def teardown_method(self):
        """测试后的清理"""
        self.db.close()
    
    def test_create_user(self):
        """测试创建用户"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        
        created_user = user.create(self.db, obj_in=user_data)
        
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"
        assert created_user.full_name == "Test User"
        assert created_user.is_active is True
        assert created_user.is_verified is False
        assert created_user.role == "user"
        
        # 验证密码已哈希
        assert created_user.password_hash != "TestPassword123"
        assert verify_password("TestPassword123", created_user.password_hash) is True
        
        # 清理测试数据
        self.db.delete(created_user)
        self.db.commit()
    
    def test_authenticate_user_success(self):
        """测试用户认证成功"""
        # 先创建用户
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        created_user = user.create(self.db, obj_in=user_data)
        
        # 认证用户
        authenticated_user = user.authenticate(
            self.db, email="test@example.com", password="TestPassword123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == "test@example.com"
        
        # 清理测试数据
        self.db.delete(created_user)
        self.db.commit()
    
    def test_authenticate_user_invalid_password(self):
        """测试用户认证失败 - 错误密码"""
        # 先创建用户
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        created_user = user.create(self.db, obj_in=user_data)
        
        # 认证用户
        authenticated_user = user.authenticate(
            self.db, email="test@example.com", password="WrongPassword"
        )
        
        assert authenticated_user is None
        
        # 清理测试数据
        self.db.delete(created_user)
        self.db.commit()
    
    def test_authenticate_user_nonexistent(self):
        """测试用户认证失败 - 用户不存在"""
        # 认证不存在的用户
        authenticated_user = user.authenticate(
            self.db, email="nonexistent@example.com", password="TestPassword123"
        )
        
        assert authenticated_user is None
    
    def test_update_user(self):
        """测试更新用户"""
        # 先创建用户
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        created_user = user.create(self.db, obj_in=user_data)
        
        # 更新用户
        update_data = {"full_name": "Updated Name"}
        updated_user = user.update(self.db, db_obj=created_user, obj_in=update_data)
        
        assert updated_user.full_name == "Updated Name"
        
        # 清理测试数据
        self.db.delete(created_user)
        self.db.commit()
    
    def test_update_user_password(self):
        """测试更新用户密码"""
        # 先创建用户
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
        created_user = user.create(self.db, obj_in=user_data)
        original_password_hash = created_user.password_hash
        
        # 更新用户密码
        update_data = {"password": "NewPassword456"}
        updated_user = user.update(self.db, db_obj=created_user, obj_in=update_data)
        
        # 验证密码已更新
        assert updated_user.password_hash != original_password_hash
        assert verify_password("NewPassword456", updated_user.password_hash) is True
        assert verify_password("TestPassword123", updated_user.password_hash) is False
        
        # 清理测试数据
        self.db.delete(created_user)
        self.db.commit()


class TestSecurity:
    """安全功能测试类"""
    
    def test_password_hashing(self):
        """测试密码哈希"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        # 验证哈希不等于原密码
        assert hashed != password
        
        # 验证哈希可以验证原密码
        assert verify_password(password, hashed) is True
        
        # 验证错误密码无法通过验证
        assert verify_password("WrongPassword", hashed) is False
    
    def test_token_creation_and_verification(self):
        """测试token创建和验证"""
        user_id = 1
        
        # 创建token
        token = create_access_token(subject=user_id)
        
        # 验证token
        payload = verify_token(token)
        
        assert payload == str(user_id)
        
        # 验证无效token
        invalid_token = "invalid.token"
        payload = verify_token(invalid_token)
        
        assert payload is None


class TestPermissions:
    """权限功能测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.db = next(get_db())
        
        # 创建测试用户
        admin_user_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="AdminPassword123",
            full_name="Admin User"
        )
        self.admin_user = user.create(self.db, obj_in=admin_user_data)
        self.admin_user.role = "admin"
        self.db.commit()
        
        regular_user_data = UserCreate(
            username="regular",
            email="regular@example.com",
            password="RegularPassword123",
            full_name="Regular User"
        )
        self.regular_user = user.create(self.db, obj_in=regular_user_data)
        self.db.commit()
    
    def teardown_method(self):
        """测试后的清理"""
        # 清理测试数据
        self.db.query(User).filter(
            User.email.in_(["admin@example.com", "regular@example.com"])
        ).delete(synchronize_session=False)
        self.db.commit()
        self.db.close()
    
    def test_admin_permissions(self):
        """测试管理员权限"""
        from app.core.permissions import has_permission, PERMISSIONS
        
        # 管理员应该拥有所有权限
        for permission_name, permission in PERMISSIONS.items():
            assert has_permission(self.admin_user, permission) is True
    
    def test_regular_user_permissions(self):
        """测试普通用户权限"""
        from app.core.permissions import has_permission, PERMISSIONS
        
        # 普通用户应该拥有基本权限，但没有管理员权限
        basic_permissions = [
            PERMISSIONS["user:read"],
            PERMISSIONS["user:write"],
            PERMISSIONS["project:read"],
            PERMISSIONS["project:write"],
            PERMISSIONS["project:create"],
            PERMISSIONS["project:delete"],
            PERMISSIONS["document:read"],
            PERMISSIONS["document:write"],
            PERMISSIONS["document:create"],
            PERMISSIONS["document:delete"],
            PERMISSIONS["ai:generate"],
        ]
        
        admin_permissions = [
            PERMISSIONS["system:admin"],
            PERMISSIONS["system:monitor"],
        ]
        
        # 检查基本权限
        for permission in basic_permissions:
            assert has_permission(self.regular_user, permission) is True
        
        # 检查管理员权限
        for permission in admin_permissions:
            assert has_permission(self.regular_user, permission) is False
    
    def test_inactive_user_permissions(self):
        """测试非活跃用户权限"""
        from app.core.permissions import has_permission, PERMISSIONS
        
        # 设置用户为非活跃
        self.regular_user.is_active = False
        
        # 非活跃用户不应该有任何权限
        for permission_name, permission in PERMISSIONS.items():
            assert has_permission(self.regular_user, permission) is False