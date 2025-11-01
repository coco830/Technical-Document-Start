
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_documents_by-status():
    """"测试 GET /api/v1/documents/by-status"""
    response = client.get(
        "/api/v1/documents/by-status"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/documents/by-status")


if __name__ == "__main__":
    test_get__api_v1_documents_by-status()
        