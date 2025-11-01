
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_put__api_v1_companies_company_id_verification-status():
    """"测试 PUT /api/v1/companies/{company_id}/verification-status"""
    response = client.put(
        "/api/v1/companies/{company_id}/verification-status"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: PUT /api/v1/companies/{company_id}/verification-status")


if __name__ == "__main__":
    test_put__api_v1_companies_company_id_verification-status()
        