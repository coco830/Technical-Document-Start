"""
项目管理API端点测试脚本
"""
import asyncio
import json
from typing import Dict, Any, Optional
import httpx
from fastapi.testclient import TestClient

# 导入应用
from main import app

# 创建测试客户端
client = TestClient(app)

# 测试数据
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "测试用户"
}

TEST_PROJECT = {
    "name": "测试项目",
    "type": "emergency_plan",
    "description": "这是一个测试项目",
    "metadata": {"key": "value"}
}

TEST_FORM = {
    "form_type": "basic_info",
    "form_data": {
        "title": "表单标题",
        "content": "表单内容"
    }
}

class ProjectAPITester:
    """项目管理API测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.access_token: Optional[str] = None
        self.project_id: Optional[int] = None
        self.form_id: Optional[int] = None
    
    def register_and_login(self) -> bool:
        """注册并登录用户"""
        try:
            # 注册用户
            register_response = client.post("/api/v1/auth/register", json=TEST_USER)
            if register_response.status_code not in [200, 400]:  # 400可能表示用户已存在
                print(f"注册失败: {register_response.status_code} - {register_response.text}")
                return False
            
            # 登录用户
            login_data = {
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            login_response = client.post("/api/v1/auth/login", json=login_data)
            if login_response.status_code != 200:
                print(f"登录失败: {login_response.status_code} - {login_response.text}")
                return False
            
            login_result = login_response.json()
            self.access_token = login_result["access_token"]
            print("用户登录成功")
            return True
        except Exception as e:
            print(f"注册或登录过程中出错: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def test_create_project(self) -> bool:
        """测试创建项目"""
        try:
            response = client.post(
                "/api/v1/projects/",
                json=TEST_PROJECT,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"创建项目失败: {response.status_code} - {response.text}")
                return False
            
            project = response.json()
            self.project_id = project["id"]
            print(f"创建项目成功，项目ID: {self.project_id}")
            return True
        except Exception as e:
            print(f"创建项目过程中出错: {str(e)}")
            return False
    
    def test_get_projects(self) -> bool:
        """测试获取项目列表"""
        try:
            response = client.get(
                "/api/v1/projects/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"获取项目列表失败: {response.status_code} - {response.text}")
                return False
            
            projects = response.json()
            print(f"获取项目列表成功，共 {projects['total']} 个项目")
            return True
        except Exception as e:
            print(f"获取项目列表过程中出错: {str(e)}")
            return False
    
    def test_get_project(self) -> bool:
        """测试获取单个项目"""
        try:
            response = client.get(
                f"/api/v1/projects/{self.project_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"获取项目详情失败: {response.status_code} - {response.text}")
                return False
            
            project = response.json()
            print(f"获取项目详情成功，项目名称: {project['name']}")
            return True
        except Exception as e:
            print(f"获取项目详情过程中出错: {str(e)}")
            return False
    
    def test_update_project(self) -> bool:
        """测试更新项目"""
        try:
            update_data = {
                "name": "更新后的项目名称",
                "description": "更新后的项目描述"
            }
            
            response = client.put(
                f"/api/v1/projects/{self.project_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"更新项目失败: {response.status_code} - {response.text}")
                return False
            
            project = response.json()
            print(f"更新项目成功，新名称: {project['name']}")
            return True
        except Exception as e:
            print(f"更新项目过程中出错: {str(e)}")
            return False
    
    def test_update_project_status(self) -> bool:
        """测试更新项目状态"""
        try:
            status_data = {"status": "generating"}
            
            response = client.put(
                f"/api/v1/projects/{self.project_id}/status",
                json=status_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"更新项目状态失败: {response.status_code} - {response.text}")
                return False
            
            project = response.json()
            print(f"更新项目状态成功，新状态: {project['status']}")
            return True
        except Exception as e:
            print(f"更新项目状态过程中出错: {str(e)}")
            return False
    
    def test_get_project_statistics(self) -> bool:
        """测试获取项目统计信息"""
        try:
            response = client.get(
                "/api/v1/projects/statistics",
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"获取项目统计信息失败: {response.status_code} - {response.text}")
                return False
            
            statistics = response.json()
            print(f"获取项目统计信息成功，总项目数: {statistics['total_projects']}")
            return True
        except Exception as e:
            print(f"获取项目统计信息过程中出错: {str(e)}")
            return False
    
    def test_create_project_form(self) -> bool:
        """测试创建项目表单"""
        try:
            response = client.post(
                f"/api/v1/projects/{self.project_id}/forms",
                json=TEST_FORM,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"创建项目表单失败: {response.status_code} - {response.text}")
                return False
            
            form = response.json()
            self.form_id = form["id"]
            print(f"创建项目表单成功，表单ID: {self.form_id}")
            return True
        except Exception as e:
            print(f"创建项目表单过程中出错: {str(e)}")
            return False
    
    def test_get_project_forms(self) -> bool:
        """测试获取项目表单列表"""
        try:
            response = client.get(
                f"/api/v1/projects/{self.project_id}/forms",
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"获取项目表单列表失败: {response.status_code} - {response.text}")
                return False
            
            forms = response.json()
            print(f"获取项目表单列表成功，共 {forms['total']} 个表单")
            return True
        except Exception as e:
            print(f"获取项目表单列表过程中出错: {str(e)}")
            return False
    
    def test_update_project_form(self) -> bool:
        """测试更新项目表单"""
        try:
            update_data = {
                "form_data": {
                    "title": "更新后的表单标题",
                    "content": "更新后的表单内容"
                }
            }
            
            response = client.put(
                f"/api/v1/projects/{self.project_id}/forms/{self.form_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"更新项目表单失败: {response.status_code} - {response.text}")
                return False
            
            form = response.json()
            print(f"更新项目表单成功，表单类型: {form['form_type']}")
            return True
        except Exception as e:
            print(f"更新项目表单过程中出错: {str(e)}")
            return False
    
    def test_delete_project(self) -> bool:
        """测试删除项目"""
        try:
            response = client.delete(
                f"/api/v1/projects/{self.project_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code != 200:
                print(f"删除项目失败: {response.status_code} - {response.text}")
                return False
            
            result = response.json()
            print(f"删除项目成功: {result['message']}")
            return True
        except Exception as e:
            print(f"删除项目过程中出错: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("开始运行项目管理API测试...")
        
        # 注册并登录
        if not self.register_and_login():
            return False
        
        # 测试创建项目
        if not self.test_create_project():
            return False
        
        # 测试获取项目列表
        if not self.test_get_projects():
            return False
        
        # 测试获取单个项目
        if not self.test_get_project():
            return False
        
        # 测试更新项目
        if not self.test_update_project():
            return False
        
        # 测试更新项目状态
        if not self.test_update_project_status():
            return False
        
        # 测试获取项目统计信息
        if not self.test_get_project_statistics():
            return False
        
        # 测试创建项目表单
        if not self.test_create_project_form():
            return False
        
        # 测试获取项目表单列表
        if not self.test_get_project_forms():
            return False
        
        # 测试更新项目表单
        if not self.test_update_project_form():
            return False
        
        # 测试删除项目
        if not self.test_delete_project():
            return False
        
        print("所有测试通过！")
        return True


if __name__ == "__main__":
    tester = ProjectAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("项目管理API测试成功完成！")
    else:
        print("项目管理API测试失败！")