
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__admin_database_analyze_table_name():
    """"测试 GET /admin/database/analyze/{table_name}"""
    response = client.get(
        "/admin/database/analyze/{table_name}"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /admin/database/analyze/{table_name}")


if __name__ == "__main__":
    test_get__admin_database_analyze_table_name()
        