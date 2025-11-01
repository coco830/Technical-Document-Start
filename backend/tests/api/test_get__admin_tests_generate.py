
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__admin_tests_generate():
    """"测试 GET /admin/tests/generate"""
    response = client.get(
        "/admin/tests/generate"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /admin/tests/generate")


if __name__ == "__main__":
    test_get__admin_tests_generate()
        