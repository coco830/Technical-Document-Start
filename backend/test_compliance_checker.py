#!/usr/bin/env python3
"""
测试AI合规检查器功能
"""

import json
import os
import sys
from app.services.ai_compliance_checker import ai_compliance_checker
from app.services.document_generator import document_generator

def test_compliance_checker():
    """测试合规检查器功能"""
    print("=" * 60)
    print("AI合规检查器功能测试")
    print("=" * 60)
    
    # 测试1: 检查单个段落
    print("\n1. 测试单个段落合规检查")
    print("-" * 40)
    
    # 测试风险管理结论段落（应该包含HJ941-2018）
    test_text_with_hj941 = "依据HJ941-2018标准，企业环境风险等级为一般，具备基本的风险防控能力。"
    test_text_without_hj941 = "企业环境风险等级为一般，具备基本的风险防控能力。"
    
    result1 = ai_compliance_checker.check_ai_output("risk_management_conclusion", test_text_with_hj941)
    print(f"包含HJ941-2018的文本: 通过={result1['passed']}, 问题数={len(result1['issues'])}")
    
    result2 = ai_compliance_checker.check_ai_output("risk_management_conclusion", test_text_without_hj941)
    print(f"不包含HJ941-2018的文本: 通过={result2['passed']}, 问题数={len(result2['issues'])}")
    print(f"问题示例: {result2['issues'][:1] if result2['issues'] else '无'}")
    
    # 测试2: 检查应急处置卡段落（应该包含三类事故）
    test_text_complete = "液体泄漏应急处置：1.立即报告应急指挥部；2.疏散无关人员，设立警戒区；3.切断泄漏源；4.使用吸附材料围堵收集泄漏物。气体泄漏应急处置：1.立即报告应急指挥部；2.疏散无关人员，设立警戒区；3.切断泄漏源；4.启动通风设备。火灾应急处置：1.立即报告应急指挥部；2.疏散无关人员，设立警戒区；3.使用灭火器灭火；4.切断泄漏源。"
    test_text_incomplete = "液体泄漏应急处置：1.立即报告应急指挥部；2.疏散无关人员，设立警戒区；3.切断泄漏源；4.使用吸附材料围堵收集泄漏物。"
    
    result3 = ai_compliance_checker.check_ai_output("incident_response_card", test_text_complete)
    print(f"包含三类事故的文本: 通过={result3['passed']}, 问题数={len(result3['issues'])}")
    
    result4 = ai_compliance_checker.check_ai_output("incident_response_card", test_text_incomplete)
    print(f"不包含三类事故的文本: 通过={result4['passed']}, 问题数={len(result4['issues'])}")
    print(f"问题示例: {result4['issues'][:1] if result4['issues'] else '无'}")
    
    # 测试3: 检查绝对化词语
    test_text_absolute = "企业绝对不会造成环境污染，完全满足所有环保要求。"
    result5 = ai_compliance_checker.check_ai_output("enterprise_overview", test_text_absolute)
    print(f"包含绝对化词语的文本: 通过={result5['passed']}, 问题数={len(result5['issues'])}")
    print(f"问题示例: {result5['issues'][:1] if result5['issues'] else '无'}")
    
    # 测试4: 批量检查多个段落
    print("\n2. 测试批量段落合规检查")
    print("-" * 40)
    
    test_sections = {
        "risk_management_conclusion": "依据HJ941-2018标准，企业环境风险等级为一般。",
        "incident_response_card": "液体泄漏应急处置：1.立即报告；2.疏散；3.切断泄漏源。",
        "enterprise_overview": "企业绝对不会造成环境污染。",  # 包含绝对化词语
        "hydrology_description": "企业周边有河流，位于东侧。"  # 缺少上下游方向
    }
    
    batch_result = ai_compliance_checker.check_multiple_sections(test_sections)
    print(f"批量检查结果: 总体通过={batch_result['overall_passed']}")
    print(f"总问题数: {batch_result['total_issues']}")
    print(f"总警告数: {batch_result['total_warnings']}")
    print(f"总体评分: {batch_result['overall_score']}/100")
    
    # 显示每个段落的详细结果
    for section_key, section_result in batch_result["section_results"].items():
        status = "✓ 通过" if section_result["passed"] else "✗ 失败"
        print(f"  {section_key}: {status} (问题数: {len(section_result['issues'])}, 警告数: {len(section_result['warnings'])})")
    
    # 测试5: 集成到文档生成流程测试
    print("\n3. 测试集成到文档生成流程")
    print("-" * 40)
    
    # 加载示例企业数据
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_data_path = os.path.join(current_dir, "sample_enterprise.json")
    
    if not os.path.exists(sample_data_path):
        print(f"警告: 未找到示例企业数据文件: {sample_data_path}")
        return
    
    with open(sample_data_path, 'r', encoding='utf-8') as f:
        enterprise_data = json.load(f)
    
    print("使用示例企业数据测试文档生成（带合规检查）...")
    
    # 测试生成单个段落（带合规检查）
    try:
        section_result = document_generator.generate_single_section(
            "risk_management_conclusion", 
            enterprise_data, 
            user_id="test_user"
        )
        
        print(f"单个段落生成结果: 成功={section_result['success']}")
        if not section_result['success']:
            print(f"错误: {section_result['errors']}")
        else:
            print(f"生成的内容长度: {len(section_result['content'])} 字符")
    except Exception as e:
        print(f"单个段落生成测试失败: {str(e)}")
    
    # 测试生成所有文档（带合规检查）
    try:
        all_docs_result = document_generator.generate_all_documents(
            enterprise_data, 
            user_id="test_user",
            use_v2=True
        )
        
        print(f"所有文档生成结果: 成功={all_docs_result['success']}")
        if not all_docs_result['success']:
            print(f"错误: {all_docs_result['errors']}")
        else:
            print(f"生成的AI段落数: {len(all_docs_result['ai_sections_used'])}")
            
            # 检查是否有合规结果
            if "compliance_results" in all_docs_result:
                compliance_results = all_docs_result["compliance_results"]
                print(f"合规检查结果: 总体通过={compliance_results['overall_passed']}")
                print(f"总问题数: {compliance_results['total_issues']}")
                print(f"总体评分: {compliance_results['overall_score']}/100")
            else:
                print("未找到合规检查结果")
    except Exception as e:
        print(f"所有文档生成测试失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_compliance_checker()