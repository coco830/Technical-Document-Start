#!/usr/bin/env python3
"""
直接在数据库中创建测试企业
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from app.database import SessionLocal
from app.models import user, project, enterprise, document, comment
from app.models.user import User
from app.models.enterprise import EnterpriseInfo
from app.models.project import Project
from app.models.document import Document
from app.models.comment import Comment

def create_test_enterprise():
    """创建测试企业"""
    db = SessionLocal()
    
    try:
        # 查找测试用户
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            print("❌ 测试用户不存在")
            return
        
        # 检查是否已有企业信息
        existing_enterprise = db.query(EnterpriseInfo).filter(EnterpriseInfo.user_id == test_user.id).first()
        if existing_enterprise:
            print("✅ 测试企业已存在")
            print(f"   企业ID: {existing_enterprise.id}")
            print(f"   企业名称: {existing_enterprise.enterprise_name}")
            return existing_enterprise.id
        
        # 创建测试企业
        test_enterprise = EnterpriseInfo(
            user_id=test_user.id,
            project_id=None,  # 设置为None，因为它是可为空的
            enterprise_name="测试企业有限公司",
            unified_social_credit_code="91110000000000000X",
            industry="制造业",
            province="北京市",
            city="北京市",
            district="海淀区",
            detailed_address="测试地址123号",
            legal_representative_name="张三",
            legal_representative_phone="13800138000",
            env_officer_name="李四",
            env_officer_position="环保经理",
            env_officer_phone="13900139000",
            emergency_contact_name="王五",
            emergency_contact_position="安全主管",
            emergency_contact_phone="13700137000",
            enterprise_email="test@example.com",
            risk_level="一般",
            total_employees=100,
            production_staff=80,
            management_staff=20,
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
        
        print(f"✅ 测试企业创建成功:")
        print(f"   企业ID: {test_enterprise.id}")
        print(f"   企业名称: {test_enterprise.enterprise_name}")
        return test_enterprise.id
        
    except Exception as e:
        print(f"❌ 创建测试企业失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_enterprise()