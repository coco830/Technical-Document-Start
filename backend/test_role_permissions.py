"""
角色权限系统测试脚本
测试基于角色的权限控制功能
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.auth import create_access_token, get_password_hash

# 配置
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
USER_EMAIL = os.getenv("USER_EMAIL", "user@example.com")
USER_PASSWORD = os.getenv("USER_PASSWORD", "user123")

class RolePermissionTester:
    """角色权限测试器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.user_token = None
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def setup_test_data(self):
        """设置测试数据"""
        print("\n🔧 设置测试数据...")
        
        try:
            db = next(get_db())
            
            # 创建管理员用户
            admin_user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
            if not admin_user:
                admin_user = User(
                    name="测试管理员",
                    email=ADMIN_EMAIL,
                    hashed_password=get_password_hash(ADMIN_PASSWORD),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                print(f"   创建管理员用户: {ADMIN_EMAIL}")
            else:
                # 确保现有用户是管理员
                admin_user.role = UserRole.ADMIN
                admin_user.is_active = True
                admin_user.is_verified = True
                db.commit()
                print(f"   更新管理员用户: {ADMIN_EMAIL}")
            
            # 创建普通用户
            user = db.query(User).filter(User.email == USER_EMAIL).first()
            if not user:
                user = User(
                    name="测试用户",
                    email=USER_EMAIL,
                    hashed_password=get_password_hash(USER_PASSWORD),
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"   创建普通用户: {USER_EMAIL}")
            else:
                # 确保现有用户是普通用户
                user.role = UserRole.USER
                user.is_active = True
                user.is_verified = True
                db.commit()
                print(f"   更新普通用户: {USER_EMAIL}")
            
            db.close()
            self.log_result("设置测试数据", True, "测试用户创建/更新成功")
            
        except Exception as e:
            self.log_result("设置测试数据", False, f"设置测试数据失败: {str(e)}")
    
    def login(self, email: str, password: str) -> Optional[str]:
        """登录并获取token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            else:
                print(f"   登录失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   登录请求异常: {str(e)}")
            return None
    
    def setup_tokens(self):
        """设置认证token"""
        print("\n🔐 获取认证token...")
        
        # 获取管理员token
        self.admin_token = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if self.admin_token:
            self.log_result("管理员登录", True, f"管理员 {ADMIN_EMAIL} 登录成功")
        else:
            self.log_result("管理员登录", False, f"管理员 {ADMIN_EMAIL} 登录失败")
        
        # 获取普通用户token
        self.user_token = self.login(USER_EMAIL, USER_PASSWORD)
        if self.user_token:
            self.log_result("普通用户登录", True, f"用户 {USER_EMAIL} 登录成功")
        else:
            self.log_result("普通用户登录", False, f"用户 {USER_EMAIL} 登录失败")
    
    def test_admin_endpoints(self):
        """测试管理员端点"""
        print("\n👑 测试管理员端点...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # 测试获取用户列表
        try:
            response = requests.get(f"{self.base_url}/api/admin/users", headers=headers)
            success = response.status_code == 200
            self.log_result(
                "管理员获取用户列表",
                success,
                f"状态码: {response.status_code}" if not success else f"获取到 {len(response.json().get('items', []))} 个用户"
            )
        except Exception as e:
            self.log_result("管理员获取用户列表", False, f"请求异常: {str(e)}")
        
        # 测试获取用户统计
        try:
            response = requests.get(f"{self.base_url}/api/admin/stats", headers=headers)
            success = response.status_code == 200
            self.log_result(
                "管理员获取用户统计",
                success,
                f"状态码: {response.status_code}" if not success else "统计信息获取成功"
            )
        except Exception as e:
            self.log_result("管理员获取用户统计", False, f"请求异常: {str(e)}")
        
        # 测试清除缓存
        try:
            response = requests.delete(f"{self.base_url}/api/ai/cache", headers=headers)
            success = response.status_code == 200
            self.log_result(
                "管理员清除缓存",
                success,
                f"状态码: {response.status_code}" if not success else "缓存清除成功"
            )
        except Exception as e:
            self.log_result("管理员清除缓存", False, f"请求异常: {str(e)}")
    
    def test_user_permission_denied(self):
        """测试普通用户权限被拒绝"""
        print("\n🚫 测试普通用户权限被拒绝...")
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # 测试普通用户访问管理员端点
        admin_endpoints = [
            ("/api/admin/users", "GET", "获取用户列表"),
            ("/api/admin/stats", "GET", "获取用户统计"),
            ("/api/ai/cache", "DELETE", "清除缓存")
        ]
        
        for endpoint, method, description in admin_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                elif method == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
                
                # 期望返回403权限被拒绝
                success = response.status_code == 403
                self.log_result(
                    f"普通用户{description}",
                    success,
                    f"状态码: {response.status_code}" if success else f"期望403但得到{response.status_code}"
                )
            except Exception as e:
                self.log_result(f"普通用户{description}", False, f"请求异常: {str(e)}")
    
    def test_user_allowed_endpoints(self):
        """测试普通用户允许访问的端点"""
        print("\n✅ 测试普通用户允许访问的端点...")
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # 测试获取模板列表
        try:
            response = requests.get(f"{self.base_url}/api/ai/templates", headers=headers)
            success = response.status_code == 200
            self.log_result(
                "普通用户获取模板列表",
                success,
                f"状态码: {response.status_code}" if not success else "模板列表获取成功"
            )
        except Exception as e:
            self.log_result("普通用户获取模板列表", False, f"请求异常: {str(e)}")
        
        # 测试获取个人使用统计
        try:
            response = requests.get(f"{self.base_url}/api/ai/usage/stats", headers=headers)
            success = response.status_code == 200
            self.log_result(
                "普通用户获取使用统计",
                success,
                f"状态码: {response.status_code}" if not success else "使用统计获取成功"
            )
        except Exception as e:
            self.log_result("普通用户获取使用统计", False, f"请求异常: {str(e)}")
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        print("\n🔒 测试未授权访问...")
        
        # 测试无token访问管理员端点
        try:
            response = requests.get(f"{self.base_url}/api/admin/users")
            success = response.status_code == 401
            self.log_result(
                "无token访问管理员端点",
                success,
                f"状态码: {response.status_code}" if success else f"期望401但得到{response.status_code}"
            )
        except Exception as e:
            self.log_result("无token访问管理员端点", False, f"请求异常: {str(e)}")
        
        # 测试无效token访问
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        try:
            response = requests.get(f"{self.base_url}/api/admin/users", headers=invalid_headers)
            success = response.status_code == 401
            self.log_result(
                "无效token访问管理员端点",
                success,
                f"状态码: {response.status_code}" if success else f"期望401但得到{response.status_code}"
            )
        except Exception as e:
            self.log_result("无效token访问管理员端点", False, f"请求异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始角色权限系统测试")
        print("=" * 50)
        
        # 设置测试数据
        self.setup_test_data()
        
        # 获取认证token
        self.setup_tokens()
        
        # 如果没有获取到token，跳过后续测试
        if not self.admin_token or not self.user_token:
            print("\n❌ 无法获取认证token，跳过权限测试")
            return
        
        # 运行各种测试
        self.test_admin_endpoints()
        self.test_user_permission_denied()
        self.test_user_allowed_endpoints()
        self.test_unauthorized_access()
        
        # 输出测试结果
        self.print_summary()
    
    def print_summary(self):
        """打印测试结果摘要"""
        print("\n" + "=" * 50)
        print("📊 测试结果摘要")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 50)
        if failed_tests == 0:
            print("🎉 所有测试通过！角色权限系统工作正常。")
        else:
            print("⚠️  部分测试失败，请检查权限系统配置。")


def main():
    """主函数"""
    # 检查环境变量
    required_env_vars = ["SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请确保在.env文件中设置了这些变量。")
        return
    
    # 运行测试
    tester = RolePermissionTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()