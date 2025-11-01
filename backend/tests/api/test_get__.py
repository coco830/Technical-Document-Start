
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__():
    """"测试 GET /"""
    response = client.get(
        "/"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /")


if __name__ == "__main__":
    test_get__()
        