#!/usr/bin/env python3
"""
测试企业信息保存功能
"""

import requests
import json

def test_enterprise_save():
    """测试企业信息保存API"""
    
    # 测试数据
    test_data = {
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
    
    # API端点
    url = "http://localhost:8000/api/enterprise/info"
    
    try:
        print("正在测试企业信息保存API...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        # 发送POST请求
        response = requests.post(url, json=test_data)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 企业信息保存成功！")
            print(f"响应内容: {response.json()}")
            return True
        else:
            print("✗ 企业信息保存失败！")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = test_enterprise_save()
    if success:
        print("\n🎉 测试通过！企业信息保存功能已修复")
    else:
        print("\n❌ 测试失败！企业信息保存功能仍有问题")