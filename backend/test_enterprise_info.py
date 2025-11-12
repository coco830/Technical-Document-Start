"""
企业信息API测试
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_enterprise.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def create_test_user():
    """创建测试用户"""
    db = TestingSessionLocal()
    
    # 检查是否已存在测试用户
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        db.close()
        return existing_user
    
    # 创建新用户
    hashed_password = get_password_hash("testpassword")
    user = User(
        name="测试用户",
        email="test@example.com",
        hashed_password=hashed_password,
        role=UserRole.USER
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def get_auth_headers():
    """获取认证头"""
    user = create_test_user()
    
    # 登录获取token
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        data={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


client = TestClient(app)


def test_create_enterprise_info():
    """测试创建企业信息"""
    headers = get_auth_headers()
    
    enterprise_data = {
        "enterprise_basic": {
            "enterprise_name": "测试企业有限公司",
            "address": "测试地址123号",
            "industry": "化工",
            "contact_person": "张三",
            "phone": "13800138000",
            "employee_count": "100",
            "main_products": "化工产品A",
            "annual_output": "1000吨",
            "description": "这是一家测试企业"
        },
        "env_permits": {
            "env_assessment_no": "环评2023-001",
            "acceptance_no": "验收2023-001",
            "discharge_permit_no": "排污2023-001",
            "env_dept": "环保局"
        },
        "hazardous_materials": [
            {
                "name": "化学品A",
                "max_storage": "10",
                "annual_usage": "50",
                "storage_location": "仓库A"
            },
            {
                "name": "化学品B",
                "max_storage": "5",
                "annual_usage": "20",
                "storage_location": "仓库B"
            }
        ],
        "emergency_resources": [
            {
                "name": "灭火器",
                "quantity": "20",
                "purpose": "灭火",
                "storage_location": "各楼层",
                "custodian": "安全员"
            },
            {
                "name": "应急灯",
                "quantity": "10",
                "purpose": "应急照明",
                "storage_location": "各楼层",
                "custodian": "安全员"
            }
        ],
        "emergency_orgs": [
            {
                "org_name": "应急指挥部",
                "responsible_person": "李四",
                "contact_phone": "13900139000",
                "duties": "负责应急指挥"
            },
            {
                "org_name": "应急救援队",
                "responsible_person": "王五",
                "contact_phone": "13700137000",
                "duties": "负责现场救援"
            }
        ]
    }
    
    response = client.post(
        "/api/enterprise/info",
        json=enterprise_data,
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["enterprise_basic"]["enterprise_name"] == "测试企业有限公司"
    assert len(data["hazardous_materials"]) == 2
    assert len(data["emergency_resources"]) == 2
    assert len(data["emergency_orgs"]) == 2


def test_get_enterprise_infos():
    """测试获取企业信息列表"""
    headers = get_auth_headers()
    
    response = client.get(
        "/api/enterprise/info",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "enterprise_infos" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data


def test_get_enterprise_info():
    """测试获取特定企业信息"""
    headers = get_auth_headers()
    
    # 先创建一个企业信息
    enterprise_data = {
        "enterprise_basic": {
            "enterprise_name": "测试企业2",
            "address": "测试地址456号",
            "industry": "石化",
            "contact_person": "赵六",
            "phone": "13600136000",
            "employee_count": "200",
            "main_products": "石化产品B",
            "annual_output": "2000吨",
            "description": "这是第二家测试企业"
        },
        "env_permits": {
            "env_assessment_no": "环评2023-002",
            "acceptance_no": "验收2023-002",
            "discharge_permit_no": "排污2023-002",
            "env_dept": "环保局"
        },
        "hazardous_materials": [],
        "emergency_resources": [],
        "emergency_orgs": []
    }
    
    create_response = client.post(
        "/api/enterprise/info",
        json=enterprise_data,
        headers=headers
    )
    
    enterprise_id = create_response.json()["id"]
    
    # 获取企业信息
    response = client.get(
        f"/api/enterprise/info/{enterprise_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["enterprise_basic"]["enterprise_name"] == "测试企业2"
    assert data["enterprise_basic"]["industry"] == "石化"


def test_update_enterprise_info():
    """测试更新企业信息"""
    headers = get_auth_headers()
    
    # 先创建一个企业信息
    enterprise_data = {
        "enterprise_basic": {
            "enterprise_name": "测试企业3",
            "address": "测试地址789号",
            "industry": "冶金",
            "contact_person": "钱七",
            "phone": "13500135000",
            "employee_count": "300",
            "main_products": "冶金产品C",
            "annual_output": "3000吨",
            "description": "这是第三家测试企业"
        },
        "env_permits": {
            "env_assessment_no": "环评2023-003",
            "acceptance_no": "验收2023-003",
            "discharge_permit_no": "排污2023-003",
            "env_dept": "环保局"
        },
        "hazardous_materials": [],
        "emergency_resources": [],
        "emergency_orgs": []
    }
    
    create_response = client.post(
        "/api/enterprise/info",
        json=enterprise_data,
        headers=headers
    )
    
    enterprise_id = create_response.json()["id"]
    
    # 更新企业信息
    update_data = {
        "enterprise_basic": {
            "enterprise_name": "更新后的企业3",
            "address": "更新后的地址789号",
            "industry": "电子",
            "contact_person": "更新后的钱七",
            "phone": "13500135001",
            "employee_count": "350",
            "main_products": "更新后的冶金产品C",
            "annual_output": "3500吨",
            "description": "这是更新后的第三家测试企业"
        }
    }
    
    response = client.put(
        f"/api/enterprise/info/{enterprise_id}",
        json=update_data,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["enterprise_basic"]["enterprise_name"] == "更新后的企业3"
    assert data["enterprise_basic"]["industry"] == "电子"


def test_delete_enterprise_info():
    """测试删除企业信息"""
    headers = get_auth_headers()
    
    # 先创建一个企业信息
    enterprise_data = {
        "enterprise_basic": {
            "enterprise_name": "测试企业4",
            "address": "测试地址101112号",
            "industry": "纺织",
            "contact_person": "孙八",
            "phone": "13400134000",
            "employee_count": "400",
            "main_products": "纺织品D",
            "annual_output": "4000吨",
            "description": "这是第四家测试企业"
        },
        "env_permits": {
            "env_assessment_no": "环评2023-004",
            "acceptance_no": "验收2023-004",
            "discharge_permit_no": "排污2023-004",
            "env_dept": "环保局"
        },
        "hazardous_materials": [],
        "emergency_resources": [],
        "emergency_orgs": []
    }
    
    create_response = client.post(
        "/api/enterprise/info",
        json=enterprise_data,
        headers=headers
    )
    
    enterprise_id = create_response.json()["id"]
    
    # 删除企业信息
    response = client.delete(
        f"/api/enterprise/info/{enterprise_id}",
        headers=headers
    )
    
    assert response.status_code == 204
    
    # 验证已删除
    get_response = client.get(
        f"/api/enterprise/info/{enterprise_id}",
        headers=headers
    )
    
    assert get_response.status_code == 404


def test_create_enterprise_info_validation():
    """测试创建企业信息时的验证"""
    headers = get_auth_headers()
    
    # 缺少必填字段
    invalid_data = {
        "enterprise_basic": {
            "address": "测试地址123号",
            "industry": "化工",
            "contact_person": "张三",
            "phone": "13800138000",
            "employee_count": "100",
            "main_products": "化工产品A",
            "annual_output": "1000吨",
            "description": "这是一家测试企业"
        },
        "env_permits": {
            "env_assessment_no": "环评2023-001",
            "acceptance_no": "验收2023-001",
            "discharge_permit_no": "排污2023-001",
            "env_dept": "环保局"
        },
        "hazardous_materials": [],
        "emergency_resources": [],
        "emergency_orgs": []
    }
    
    response = client.post(
        "/api/enterprise/info",
        json=invalid_data,
        headers=headers
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


if __name__ == "__main__":
    # 运行测试
    test_create_enterprise_info()
    test_get_enterprise_infos()
    test_get_enterprise_info()
    test_update_enterprise_info()
    test_delete_enterprise_info()
    test_create_enterprise_info_validation()
    
    print("所有企业信息API测试通过！")