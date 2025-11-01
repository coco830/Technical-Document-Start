import pytest
import os
import tempfile
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models import Base


# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def db_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_session(db_engine):
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def db(db_session):
    """获取测试数据库会话"""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_db
    yield db_session
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def temp_file(temp_dir):
    """创建临时文件"""
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("test content")
    return file_path


@pytest.fixture
def user_token():
    """测试用户token"""
    return "test_token"


@pytest.fixture
def admin_user():
    """测试管理员用户数据"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "password123",
        "full_name": "管理员",
        "role": "admin"
    }


@pytest.fixture
def normal_user():
    """测试普通用户数据"""
    return {
        "username": "user",
        "email": "user@example.com",
        "password": "password123",
        "full_name": "普通用户",
        "role": "user"
    }


@pytest.fixture
def test_project():
    """测试项目数据"""
    return {
        "name": "测试项目",
        "type": "emergency_plan",
        "description": "这是一个测试项目"
    }


@pytest.fixture
def test_company():
    """测试企业数据"""
    return {
        "name": "测试企业",
        "unified_social_credit_code": "123456789012345678",
        "legal_representative": "测试法人",
        "contact_phone": "13800138000",
        "contact_email": "company@example.com",
        "address": "测试地址",
        "industry": "测试行业",
        "business_scope": "测试经营范围"
    }


@pytest.fixture
def test_document():
    """测试文档数据"""
    return {
        "title": "测试文档",
        "content": "这是测试文档内容",
        "format": "markdown",
        "status": "draft"
    }