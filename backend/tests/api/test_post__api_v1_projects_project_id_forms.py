
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post__api_v1_projects_project_id_forms():
    """"测试 POST /api/v1/projects/{project_id}/forms"""
    response = client.post(
        "/api/v1/projects/{project_id}/forms"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: POST /api/v1/projects/{project_id}/forms")


if __name__ == "__main__":
    test_post__api_v1_projects_project_id_forms()
        