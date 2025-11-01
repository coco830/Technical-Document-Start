import json
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def get_auth_headers(token: str) -> Dict[str, str]:
        """获取认证头"""
        return {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    def create_user(client: TestClient, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    def login_user(client: TestClient, email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        login_data = {"email": email, "password": password}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        return response.json()
    
    @staticmethod
    def create_project(
        client: TestClient, 
        project_data: Dict[str, Any], 
        token: str
    ) -> Dict[str, Any]:
        """创建项目"""
        headers = TestUtils.get_auth_headers(token)
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    def create_company(
        client: TestClient, 
        company_data: Dict[str, Any], 
        token: str
    ) -> Dict[str, Any]:
        """创建企业"""
        headers = TestUtils.get_auth_headers(token)
        response = client.post("/api/v1/companies/", json=company_data, headers=headers)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    def create_document(
        client: TestClient, 
        document_data: Dict[str, Any], 
        project_id: int,
        token: str
    ) -> Dict[str, Any]:
        """创建文档"""
        headers = TestUtils.get_auth_headers(token)
        response = client.post(
            f"/api/v1/projects/{project_id}/documents/", 
            json=document_data, 
            headers=headers
        )
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    def assert_error_response(response, expected_status_code: int, expected_message: Optional[str] = None):
        """断言错误响应"""
        assert response.status_code == expected_status_code
        data = response.json()
        assert data.get("error") is True
        if expected_message:
            assert expected_message in data.get("message", "")
    
    @staticmethod
    def assert_success_response(response, expected_status_code: int = 200):
        """断言成功响应"""
        assert response.status_code == expected_status_code
        data = response.json()
        assert data.get("error") is not True
    
    @staticmethod
    def assert_pagination_response(response, expected_count: Optional[int] = None):
        """断言分页响应"""
        TestUtils.assert_success_response(response)
        data = response.json()
        
        # 检查分页字段
        assert "items" in data
        assert "page" in data
        assert "size" in data
        assert "total" in data
        
        if expected_count is not None:
            assert data["total"] == expected_count
    
    @staticmethod
    def compare_objects(obj1: Dict[str, Any], obj2: Dict[str, Any], exclude_fields: Optional[list] = None):
        """比较两个对象"""
        exclude_fields = exclude_fields or []
        
        for key, value in obj1.items():
            if key in exclude_fields:
                continue
            assert key in obj2, f"键 '{key}' 在第二个对象中不存在"
            assert obj2[key] == value, f"键 '{key}' 的值不匹配: {value} != {obj2[key]}"
    
    @staticmethod
    def assert_datetime_close(dt1, dt2, seconds: int = 5):
        """断言两个时间接近"""
        diff = abs(dt1 - dt2).total_seconds()
        assert diff <= seconds, f"时间差超过 {seconds} 秒: {diff}"
    
    @staticmethod
    def create_test_file_content() -> str:
        """创建测试文件内容"""
        return """# 测试文档

这是一个测试文档的内容。

## 章节1

测试内容1。

## 章节2

测试内容2。

### 子章节

测试子内容。
"""
    
    @staticmethod
    def get_test_file_data() -> Dict[str, Any]:
        """获取测试文件数据"""
        return {
            "filename": "test_document.md",
            "content": TestUtils.create_test_file_content(),
            "size": len(TestUtils.create_test_file_content().encode('utf-8'))
        }
    
    @staticmethod
    def assert_file_response(response, expected_filename: Optional[str] = None):
        """断言文件响应"""
        assert response.status_code == 200
        assert "application/octet-stream" in response.headers.get("content-type", "")
        
        if expected_filename:
            content_disposition = response.headers.get("content-disposition", "")
            assert expected_filename in content_disposition
    
    @staticmethod
    def cleanup_test_data(db: Session):
        """清理测试数据"""
        # 按照依赖关系顺序删除
        from app.models import (
            DocumentExport, AIGeneration, DocumentVersion, 
            Document, ProjectForm, FormField, Project,
            UserSession, Company, User
        )
        
        # 删除导出记录
        db.query(DocumentExport).delete()
        
        # 删除AI生成记录
        db.query(AIGeneration).delete()
        
        # 删除文档版本
        db.query(DocumentVersion).delete()
        
        # 删除文档
        db.query(Document).delete()
        
        # 删除表单字段
        db.query(FormField).delete()
        
        # 删除项目表单
        db.query(ProjectForm).delete()
        
        # 删除项目
        db.query(Project).delete()
        
        # 删除用户会话
        db.query(UserSession).delete()
        
        # 删除企业
        db.query(Company).delete()
        
        # 删除用户
        db.query(User).delete()
        
        db.commit()