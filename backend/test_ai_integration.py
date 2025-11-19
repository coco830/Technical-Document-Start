#!/usr/bin/env python3
"""
测试AI集成功能
验证AI段落生成和文档生成是否正常工作
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.document_generator import document_generator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_enterprise_data():
    """创建测试企业数据"""
    return {
        "basic_info": {
            "company_name": "测试环保科技有限公司",
            "establishment_date": "2020-01-15",
            "environmental_investment": "500万元",
            "main_construction": "办公楼、生产车间、仓库、污水处理站",
            "production_capacity": "年产环保设备100套",
            "work_system": "8小时工作制，双休",
            "address": {
                "province": "江苏省",
                "city": "苏州市",
                "district": "工业园区",
                "detail": "环保路88号",
                "longitude": "120.6199",
                "latitude": "31.2989"
            },
            "contacts": {
                "legal_person": {
                    "name": "张三",
                    "mobile": "13800138000"
                },
                "environmental_manager": {
                    "name": "李四",
                    "mobile": "13800138001"
                },
                "emergency_contact": {
                    "name": "王五",
                    "mobile": "13800138002"
                },
                "office_phone": "0512-88888888",
                "email": "test@example.com"
            },
            "risk_level": "一般"
        },
        "production_process": {
            "products": [
                {
                    "name": "废气处理设备",
                    "annual_output": "50",
                    "unit": "套"
                },
                {
                    "name": "废水处理设备",
                    "annual_output": "30",
                    "unit": "套"
                }
            ],
            "raw_materials": [
                {
                    "name": "不锈钢",
                    "annual_usage": "100",
                    "max_storage": "20",
                    "unit": "吨"
                },
                {
                    "name": "电机",
                    "annual_usage": "200",
                    "max_storage": "50",
                    "unit": "台"
                }
            ],
            "hazardous_chemicals": [
                {
                    "name": "盐酸",
                    "storage_location": "化学品仓库",
                    "storage_condition": "密封储存",
                    "max_storage": "0.5",
                    "unit": "吨"
                }
            ],
            "energy": {
                "water_consumption": "5000",
                "electricity_consumption": "100000",
                "natural_gas": "10000"
            }
        },
        "environment_info": {
            "nearby_receivers": [
                {
                    "name": "东河",
                    "receiver_type": "水环境",
                    "direction": "东",
                    "distance": "500",
                    "description": "饮用水源",
                    "quality_target": "III类"
                },
                {
                    "name": "居民区",
                    "receiver_type": "大气环境",
                    "direction": "南",
                    "distance": "300",
                    "description": "约1000人",
                    "quality_target": "二级"
                }
            ]
        },
        "emergency_resources": {
            "contact_list_internal": [
                {
                    "department": "生产部",
                    "role": "安全员",
                    "name": "赵六",
                    "mobile": "13800138003"
                }
            ],
            "contact_list_external": [
                {
                    "name": "消防队",
                    "phone": "119"
                },
                {
                    "name": "环保局",
                    "phone": "12369"
                }
            ],
            "emergency_materials": [
                {
                    "name": "灭火器",
                    "unit": "个",
                    "quantity": "20",
                    "purpose": "初期火灾扑救",
                    "storage_location": "消防器材室",
                    "custodian": "安全员",
                    "custodian_phone": "13800138003"
                }
            ]
        },
        "compliance_info": {
            "environmental_procedures": "已办理环评手续",
            "eia_approval": "苏环建[2020]123号",
            "acceptance": "已通过验收",
            "discharge_permit": "已取得排污许可证"
        }
    }

def test_single_ai_section():
    """测试单个AI段落生成"""
    print("\n=== 测试单个AI段落生成 ===")
    
    # 创建测试数据
    enterprise_data = create_test_enterprise_data()
    
    # 测试企业概况段落生成
    try:
        section_name = "enterprise_overview"
        print(f"正在生成AI段落: {section_name}")
        
        content = document_generator.generate_ai_section(section_name, enterprise_data)
        
        print(f"生成的段落内容 ({section_name}):")
        print(content[:200] + "..." if len(content) > 200 else content)
        print("-" * 50)
        
    except Exception as e:
        print(f"生成AI段落失败: {e}")
        return False
    
    return True

def test_build_ai_sections():
    """测试批量AI段落生成"""
    print("\n=== 测试批量AI段落生成 ===")
    
    # 创建测试数据
    enterprise_data = create_test_enterprise_data()
    
    try:
        print("正在批量生成AI段落...")
        ai_sections = document_generator.build_ai_sections(enterprise_data)
        
        print(f"成功生成 {len(ai_sections)} 个AI段落:")
        for name, content in ai_sections.items():
            print(f"- {name}: {len(content)} 字符")
        
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"批量生成AI段落失败: {e}")
        return False

def test_document_generation_with_ai():
    """测试集成AI的文档生成"""
    print("\n=== 测试集成AI的文档生成 ===")
    
    # 创建测试数据
    enterprise_data = create_test_enterprise_data()
    
    try:
        print("正在生成包含AI段落的文档...")
        result = document_generator.generate_all_documents(enterprise_data)
        
        if result["success"]:
            print("文档生成成功!")
            print(f"- 风险评估报告: {len(result['risk_report'])} 字符")
            print(f"- 应急预案: {len(result['emergency_plan'])} 字符")
            print(f"- 应急资源调查报告: {len(result['resource_report'])} 字符")
            
            # 检查是否包含AI段落标记
            risk_report = result["risk_report"]
            if "ai_sections.enterprise_overview" in risk_report:
                print("✓ 风险评估报告包含AI段落")
            else:
                print("✗ 风险评估报告未包含AI段落")
                
        else:
            print("文档生成失败:")
            for error in result["errors"]:
                print(f"- {error}")
        
        print("-" * 50)
        return result["success"]
        
    except Exception as e:
        print(f"生成文档失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试AI集成功能...")
    
    # 检查AI服务是否可用
    from app.services.ai_service import get_ai_service
    ai_service = get_ai_service()
    
    if ai_service.is_available():
        print("✓ AI服务可用")
    else:
        print("✗ AI服务不可用，将使用模拟生成")
    
    # 执行测试
    test_results = []
    test_results.append(("单个AI段落生成", test_single_ai_section()))
    test_results.append(("批量AI段落生成", test_build_ai_sections()))
    test_results.append(("集成AI的文档生成", test_document_generation_with_ai()))
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    # 计算通过率
    passed_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)
    pass_rate = (passed_count / total_count) * 100
    
    print(f"\n总体通过率: {pass_rate:.1f}% ({passed_count}/{total_count})")
    
    if pass_rate == 100:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())