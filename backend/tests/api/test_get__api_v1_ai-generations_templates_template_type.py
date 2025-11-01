
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_ai-generations_templates_template_type():
    """"测试 GET /api/v1/ai-generations/templates/{template_type}"""
    response = client.get(
        "/api/v1/ai-generations/templates/{template_type}"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/ai-generations/templates/{template_type}")


if __name__ == "__main__":
    test_get__api_v1_ai-generations_templates_template_type()
        