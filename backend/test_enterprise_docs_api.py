"""
简单测试企业文档生成API的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_enterprise_docs_api():
    """测试企业文档生成API"""
    
    # 1. 首先登录获取访问令牌
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    try:
        print("正在登录...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}")
            print(f"响应内容: {login_response.text}")
            return
        
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        
        if not access_token:
            print("登录成功但未获取到访问令牌")
            return
        
        print("登录成功，获取到访问令牌")
        
        # 2. 直接使用已知的企业ID进行测试
        headers = {"Authorization": f"Bearer {access_token}"}
        enterprise_id = 6  # 使用已知的企业ID
        enterprise_name = "测试企业有限公司"
        
        print(f"\n使用已知企业ID进行测试: {enterprise_name} (ID: {enterprise_id})")
        
        # 3. 测试文档生成API
        print("\n正在测试文档生成API...")
        
        # 准备请求数据
        request_data = {
            "basic_info": {
                "company_name": enterprise_name,
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
        
        # 发送文档生成请求
        docs_response = requests.post(
            f"{BASE_URL}/api/enterprise/{enterprise_id}/generate-docs",
            headers=headers,
            json=request_data
        )
        
        if docs_response.status_code != 200:
            print(f"文档生成失败: {docs_response.status_code}")
            print(f"响应内容: {docs_response.text}")
            return
        
        docs_result = docs_response.json()
        
        if docs_result.get("success"):
            print("\n✅ 文档生成成功!")
            
            # 显示生成的文档信息
            data = docs_result.get("data", {})
            tabs = data.get("tabs", [])
            enterprise_info = data.get("enterprise_info", {})
            
            print(f"\n企业信息:")
            print(f"  ID: {enterprise_info.get('id')}")
            print(f"  名称: {enterprise_info.get('name')}")
            print(f"  生成时间: {enterprise_info.get('generated_at')}")
            
            print(f"\n生成的文档:")
            for i, tab in enumerate(tabs, 1):
                print(f"  {i}. {tab['title']}")
                print(f"     ID: {tab['id']}")
                print(f"     字数: {tab['word_count']}")
                print(f"     内容长度: {len(tab['content'])} 字符")
            
            # 保存第一个文档到文件
            if tabs:
                first_doc = tabs[0]
                filename = f"test_output/{first_doc['id']}.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(first_doc['content'])
                print(f"\n已将第一个文档保存到: {filename}")
        else:
            print("\n❌ 文档生成失败!")
            errors = docs_result.get("errors", [])
            if errors:
                print("错误信息:")
                for error in errors:
                    print(f"  - {error}")
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    print("=== 企业文档生成API测试 ===")
    test_enterprise_docs_api()