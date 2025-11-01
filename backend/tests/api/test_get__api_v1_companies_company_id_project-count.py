
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_companies_company_id_project-count():
    """"测试 GET /api/v1/companies/{company_id}/project-count"""
    response = client.get(
        "/api/v1/companies/{company_id}/project-count"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/companies/{company_id}/project-count")


if __name__ == "__main__":
    test_get__api_v1_companies_company_id_project-count()
        