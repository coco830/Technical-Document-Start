"""
企业文档生成API测试
"""

import pytest
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.enterprise import EnterpriseInfo
from app.utils.auth import create_access_token

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试客户端
client = TestClient(app)

# 覆盖数据库依赖
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 创建测试数据
@pytest.fixture(scope="module")
def setup_test_data():
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # 创建测试用户
    test_user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role="user"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # 创建测试企业
    test_enterprise = EnterpriseInfo(
        user_id=test_user.id,
        enterprise_name="测试企业",
        unified_social_credit_code="123456789",
        industry="制造业",
        province="北京市",
        city="北京市",
        district="朝阳区",
        detailed_address="测试地址123号",
        legal_representative_name="张三",
        legal_representative_phone="13800138000",
        env_officer_name="李四",
        env_officer_phone="13900139000",
        emergency_contact_name="王五",
        emergency_contact_phone="13700137000",
        total_employees=100,
        production_staff=80,
        risk_level="一般",
        products_info=[
            {
                "product_name": "测试产品",
                "product_type": "主产品",
                "design_capacity": "1000吨/年",
                "actual_annual_output": "800吨/年"
            }
        ],
        raw_materials_info=[
            {
                "material_name": "测试原料",
                "material_category": "原料",
                "is_hazardous": "否",
                "annual_usage": "500吨/年"
            }
        ],
        emergency_materials_list=[
            {
                "material_name": "灭火器",
                "unit": "个",
                "quantity": "10",
                "purpose": ["消防"],
                "storage_location": "仓库",
                "custodian_name": "保管员",
                "custodian_phone": "13600136000"
            }
        ]
    )
    db.add(test_enterprise)
    db.commit()
    db.refresh(test_enterprise)
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": test_user.email})
    
    db.close()
    
    return {
        "user_id": test_user.id,
        "enterprise_id": test_enterprise.id,
        "access_token": access_token
    }

def test_generate_enterprise_docs_success(setup_test_data):
    """测试成功生成企业文档"""
    headers = {"Authorization": f"Bearer {setup_test_data['access_token']}"}
    
    # 准备请求数据
    request_data = {
        "basic_info": {
            "company_name": "测试企业",
            "risk_level": "一般"
        },
        "production_process": {
            "products": [
                {
                    "product_name": "测试产品",
                    "product_type": "主产品",
                    "design_capacity": "1000吨/年",
                    "actual_output": "800吨/年"
                }
            ]
        },
        "environment_info": {
            "nearby_receivers": [
                {
                    "receiver_type": "水体",
                    "name": "测试河流",
                    "direction": "东",
                    "distance_m": 500,
                    "population_or_scale": "小型河流"
                }
            ]
        },
        "emergency_resources": {
            "contact_list_internal": [
                {
                    "role": "应急指挥",
                    "name": "张三",
                    "department": "管理部",
                    "mobile": "13800138000"
                }
            ],
            "emergency_materials": [
                {
                    "material_name": "灭火器",
                    "unit": "个",
                    "quantity": 10,
                    "purpose": "消防",
                    "storage_location": "仓库",
                    "keeper": "保管员"
                }
            ]
        }
    }
    
    # 发送请求
    response = client.post(
        f"/enterprise/{setup_test_data['enterprise_id']}/generate-docs",
        headers=headers,
        json=request_data
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "tabs" in data["data"]
    assert len(data["data"]["tabs"]) == 3  # 应该有三个文档
    
    # 验证每个文档的结构
    for tab in data["data"]["tabs"]:
        assert "id" in tab
        assert "title" in tab
        assert "content" in tab
        assert "word_count" in tab
        assert isinstance(tab["word_count"], int)
        assert tab["word_count"] > 0
    
    # 验证企业信息
    assert "enterprise_info" in data["data"]
    assert data["data"]["enterprise_info"]["id"] == setup_test_data["enterprise_id"]
    assert data["data"]["enterprise_info"]["name"] == "测试企业"
    assert "generated_at" in data["data"]["enterprise_info"]

def test_generate_enterprise_docs_not_found(setup_test_data):
    """测试企业不存在的情况"""
    headers = {"Authorization": f"Bearer {setup_test_data['access_token']}"}
    
    # 使用不存在的企业ID
    response = client.post(
        "/enterprise/99999/generate-docs",
        headers=headers,
        json={}
    )
    
    # 验证响应
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "企业信息不存在"

def test_generate_enterprise_docs_unauthorized():
    """测试未授权访问"""
    # 不提供认证头
    response = client.post(
        "/enterprise/1/generate-docs",
        json={}
    )
    
    # 验证响应
    assert response.status_code == 401

def test_generate_enterprise_docs_invalid_data(setup_test_data):
    """测试无效数据的情况"""
    headers = {"Authorization": f"Bearer {setup_test_data['access_token']}"}
    
    # 发送无效数据
    response = client.post(
        f"/enterprise/{setup_test_data['enterprise_id']}/generate-docs",
        headers=headers,
        json={"invalid_field": "invalid_value"}
    )
    
    # 验证响应 - 应该仍然能够生成文档，因为使用了数据库中的默认数据
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_generate_enterprise_docs_with_additional_data(setup_test_data):
    """测试带有额外数据的情况"""
    headers = {"Authorization": f"Bearer {setup_test_data['access_token']}"}
    
    # 准备请求数据，包含额外数据
    request_data = {
        "additional_data": {
            "basic_info": {
                "company_name": "覆盖企业名称",
                "risk_level": "重大"
            },
            "custom_field": "自定义值"
        }
    }
    
    # 发送请求
    response = client.post(
        f"/enterprise/{setup_test_data['enterprise_id']}/generate-docs",
        headers=headers,
        json=request_data
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "tabs" in data["data"]
    assert len(data["data"]["tabs"]) == 3  # 应该有三个文档

if __name__ == "__main__":
    # 运行测试
    import sys
    sys.exit(pytest.main([__file__]))