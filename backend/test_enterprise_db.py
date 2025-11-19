#!/usr/bin/env python3
"""
直接测试企业信息数据库操作
"""

from app.database import SessionLocal, engine
from app.models.enterprise import EnterpriseInfo
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.comment import Comment
from sqlalchemy.orm import Session

def test_enterprise_db():
    """测试企业信息数据库操作"""
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        print("正在测试企业信息数据库操作...")
        
        # 创建测试用户（如果不存在）
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            print("创建测试用户...")
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password="hashed_password",
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✓ 测试用户创建成功，ID: {test_user.id}")
        else:
            print(f"✓ 使用现有测试用户，ID: {test_user.id}")
        
        # 创建企业信息测试数据
        print("创建企业信息测试数据...")
        enterprise_data = {
            "user_id": test_user.id,
            "enterprise_name": "测试企业有限公司",
            "unified_social_credit_code": "91110000000000000X",
            "industry": "制造业",
            "province": "北京市",
            "city": "北京市",
            "district": "海淀区",
            "detailed_address": "测试地址123号",
            "legal_representative_name": "张三",
            "legal_representative_phone": "13800138000",
            "env_officer": "环保负责人测试",  # 这是之前缺失的字段
            "env_officer_name": "李四",
            "env_officer_position": "环保经理",
            "env_officer_phone": "13900139000",
            "emergency_contact_name": "王五",
            "emergency_contact_position": "安全主管",
            "emergency_contact_phone": "13700137000",
            "enterprise_email": "test@example.com",
            "risk_level": "一般",
            "total_employees": 100,
            "production_staff": 80,
            "management_staff": 20
        }
        
        # 创建企业信息对象
        enterprise = EnterpriseInfo(**enterprise_data)
        
        # 保存到数据库
        print("正在保存企业信息到数据库...")
        db.add(enterprise)
        db.commit()
        db.refresh(enterprise)
        
        print(f"✓ 企业信息保存成功！ID: {enterprise.id}")
        print(f"✓ 环保负责人字段值: {enterprise.env_officer}")
        
        # 查询验证
        print("验证数据是否正确保存...")
        saved_enterprise = db.query(EnterpriseInfo).filter(EnterpriseInfo.id == enterprise.id).first()
        
        if saved_enterprise and saved_enterprise.env_officer == "环保负责人测试":
            print("✓ 数据验证成功！env_officer字段已正确保存")
            return True
        else:
            print("✗ 数据验证失败！")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_enterprise_db()
    if success:
        print("\n🎉 数据库测试通过！企业信息保存功能已修复")
    else:
        print("\n❌ 数据库测试失败！企业信息保存功能仍有问题")