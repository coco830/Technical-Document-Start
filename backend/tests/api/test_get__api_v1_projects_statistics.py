
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_projects_statistics():
    """"测试 GET /api/v1/projects/statistics"""
    response = client.get(
        "/api/v1/projects/statistics"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/projects/statistics")


if __name__ == "__main__":
    test_get__api_v1_projects_statistics()
        