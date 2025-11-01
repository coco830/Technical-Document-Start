
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post__api_v1_auth_send-verification-code():
    """"测试 POST /api/v1/auth/send-verification-code"""
    response = client.post(
        "/api/v1/auth/send-verification-code"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: POST /api/v1/auth/send-verification-code")


if __name__ == "__main__":
    test_post__api_v1_auth_send-verification-code()
        