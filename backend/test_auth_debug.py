#!/usr/bin/env python3
"""
认证调试测试脚本
用于测试认证端点是否正常工作
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_auth_endpoints():
    """测试认证相关端点"""
    print("🔍 开始测试认证端点...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 2. 测试登录
    print("\n2. 测试登录...")
    login_data = {
        "email": "test@example.com",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"📋 登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            print(f"✅ 登录成功，token: {token[:30] if token else 'None'}...")
            
            # 3. 测试token验证
            print("\n3. 测试token验证...")
            headers = {"Authorization": f"Bearer {token}"}
            
            verify_response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
            print(f"📋 验证响应状态: {verify_response.status_code}")
            
            if verify_response.status_code == 200:
                print(f"✅ Token验证成功: {verify_response.json()}")
                
                # 4. 测试token刷新
                print("\n4. 测试token刷新...")
                refresh_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
                print(f"📋 刷新响应状态: {refresh_response.status_code}")
                
                if refresh_response.status_code == 200:
                    refresh_result = refresh_response.json()
                    new_token = refresh_result.get("access_token")
                    print(f"✅ Token刷新成功，新token: {new_token[:30] if new_token else 'None'}...")
                    
                    # 5. 测试企业信息API（需要认证）
                    print("\n5. 测试企业信息API...")
                    enterprise_data = {
                        "project_id": 1,
                        "enterprise_identity": {
                            "enterprise_name": "测试企业",
                            "industry": "测试行业"
                        }
                    }
                    
                    enterprise_response = requests.post(
                        f"{BASE_URL}/enterprise/info", 
                        json=enterprise_data,
                        headers=headers
                    )
                    print(f"📋 企业信息API响应状态: {enterprise_response.status_code}")
                    
                    if enterprise_response.status_code == 201:
                        print(f"✅ 企业信息创建成功: {enterprise_response.json()}")
                    else:
                        print(f"❌ 企业信息创建失败: {enterprise_response.text}")
                        
                else:
                    print(f"❌ Token刷新失败: {refresh_response.text}")
            else:
                print(f"❌ Token验证失败: {verify_response.text}")
        else:
            print(f"❌ 登录失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    
    return True

def test_user_creation():
    """测试用户创建"""
    print("\n🔍 测试用户创建...")
    
    # 先尝试创建测试用户
    user_data = {
        "email": "test@example.com",
        "name": "测试用户",
        "password": "test123456",
        "confirm_password": "test123456",
        "accept_terms": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"📋 用户创建响应状态: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ 用户创建成功: {response.json()}")
            return True
        elif response.status_code == 409:
            print(f"⚠️ 用户已存在: {response.json()}")
            return True
        else:
            print(f"❌ 用户创建失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 用户创建出错: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始认证调试测试...")
    
    # 创建测试用户
    test_user_creation()
    
    # 测试认证流程
    success = test_auth_endpoints()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)