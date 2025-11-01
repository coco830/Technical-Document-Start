
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get__api_v1_files_upload_progress_file_id():
    """"测试 GET /api/v1/files/upload/progress/{file_id}"""
    response = client.get(
        "/api/v1/files/upload/progress/{file_id}"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {}
    
    print(f"测试通过: GET /api/v1/files/upload/progress/{file_id}")


if __name__ == "__main__":
    test_get__api_v1_files_upload_progress_file_id()
        