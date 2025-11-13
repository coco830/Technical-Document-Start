#!/usr/bin/env python3
"""
测试登录API脚本
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
sys.path.append(os.path.dirname(__file__))

import requests
import json

def test_login_api():
    """测试登录API"""
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 登录数据
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    print(f"🔍 测试登录API...")
    print(f"   URL: {base_url}/auth/login")
    print(f"   邮箱: {login_data['email']}")
    print(f"   密码: {login_data['password']}")
    
    try:
        # 发送登录请求
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 登录成功！")
            data = response.json()
            print(f"   访问令牌: {data['access_token'][:50]}...")
            print(f"   用户信息: {data['user']['name']} ({data['user']['email']})")
            
            # 测试验证token
            print("\n🔍 测试验证token...")
            token_response = requests.get(
                f"{base_url}/auth/verify",
                headers={"Authorization": f"Bearer {data['access_token']}"}
            )
            
            if token_response.status_code == 200:
                print("✅ Token验证成功！")
                user_data = token_response.json()
                print(f"   用户信息: {user_data['name']} ({user_data['email']})")
            else:
                print(f"❌ Token验证失败: {token_response.status_code}")
                print(f"   错误信息: {token_response.text}")
        else:
            print("❌ 登录失败！")
            print(f"   错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_login_api()