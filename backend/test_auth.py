#!/usr/bin/env python3
"""
认证流程测试脚本
用于测试用户注册、登录和token刷新功能
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000/api/auth"

def test_register():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    
    register_data = {
        "name": "测试用户",
        "email": "test@example.com",
        "password": "test123456",
        "confirm_password": "test123456",
        "accept_terms": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        
        if response.status_code == 201:
            print("✅ 注册成功")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 注册失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ 注册请求异常: {e}")
        return False

def test_login():
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    
    login_data = {
        "email": "test@example.com",
        "password": "test123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ 登录成功")
            data = response.json()
            print(f"用户信息: {data['user']}")
            return data['access_token']
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return None

def test_verify_token(token):
    """测试token验证"""
    print("\n🔍 测试token验证...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/verify", headers=headers)
        
        if response.status_code == 200:
            print("✅ Token验证成功")
            print(f"用户信息: {response.json()}")
            return True
        else:
            print(f"❌ Token验证失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Token验证请求异常: {e}")
        return False

def test_refresh_token(token):
    """测试token刷新"""
    print("\n🔍 测试token刷新...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/refresh", headers=headers)
        
        if response.status_code == 200:
            print("✅ Token刷新成功")
            data = response.json()
            print(f"新token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"❌ Token刷新失败: {response.status_code}")
            print(f"错误信息: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Token刷新请求异常: {e}")
        return None

def main():
    """主测试函数"""
    print("🌿 悦恩平台认证流程测试")
    print("=" * 40)
    
    # 测试注册
    if not test_register():
        print("\n❌ 注册测试失败，终止测试")
        sys.exit(1)
    
    # 测试登录
    token = test_login()
    if not token:
        print("\n❌ 登录测试失败，终止测试")
        sys.exit(1)
    
    # 测试token验证
    if not test_verify_token(token):
        print("\n❌ Token验证测试失败，终止测试")
        sys.exit(1)
    
    # 测试token刷新
    new_token = test_refresh_token(token)
    if not new_token:
        print("\n❌ Token刷新测试失败，终止测试")
        sys.exit(1)
    
    # 验证新token
    if not test_verify_token(new_token):
        print("\n❌ 新Token验证测试失败，终止测试")
        sys.exit(1)
    
    print("\n🎉 所有认证测试通过！")

if __name__ == "__main__":
    main()