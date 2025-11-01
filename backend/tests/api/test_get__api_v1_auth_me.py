
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_auth_me():
    """"测试 GET /api/v1/auth/me"""
    response = client.get(
        "/api/v1/auth/me"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/auth/me")


if __name__ == "__main__":
    test_get__api_v1_auth_me()
        