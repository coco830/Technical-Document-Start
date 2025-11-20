#!/usr/bin/env python3
"""
端到端Demo：生成所有7种文档
使用Mock AI服务生成7个文档并保存到test_output目录
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from app.services.document_generator import DocumentGenerator
from app.prompts.ai_sections_loader import ai_sections_loader

def generate_all_7_documents():
    """Demo主函数：生成所有7种文档"""
    print("=" * 60)
    print("企业文档生成Demo - 生成所有7种文档")
    print("=" * 60)
    
    # 读取企业数据
    sample_file = project_root / "sample_enterprise.json"
    if not sample_file.exists():
        print(f"错误：找不到企业数据文件 {sample_file}")
        return False
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            enterprise_data = json.load(f)
        print(f"✓ 成功加载企业数据：{enterprise_data['basic_info']['company_name']}")
    except Exception as e:
        print(f"错误：加载企业数据失败 - {str(e)}")
        return False
    
    # 创建文档生成器
    try:
        generator = DocumentGenerator()
        print("✓ 文档生成器初始化成功")
    except Exception as e:
        print(f"错误：文档生成器初始化失败 - {str(e)}")
        return False
    
    print("\n开始生成所有7种文档...")
    try:
        # 生成所有7种文档
        result = generator.generate_all_documents(enterprise_data, "demo_user", use_v2=True)
        
        print(f"生成结果: {result}")
        
        if result["success"]:
            print("✓ 所有文档生成成功")
            
            # 保存文档到test_output目录
            output_dir = project_root / "test_output"
            output_dir.mkdir(exist_ok=True)
            
            # 文档类型映射
            doc_type_names = {
                "risk_report": "环境风险评估报告",
                "emergency_plan": "突发环境事件应急预案",
                "resource_report": "应急资源调查报告",
                "release_order": "发布令",
                "opinion_adoption": "意见采纳情况表",
                "emergency_monitoring_plan": "应急监测方案",
                "revision_note": "修编说明"
            }
            
            # 保存所有生成的文档
            saved_files = []
            for doc_type, content in result.items():
                if doc_type in ["success", "errors", "ai_sections_used"]:
                    continue
                    
                if content:
                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{doc_type}_v2_demo_{timestamp}.html"
                    file_path = output_dir / filename
                    
                    # 保存文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    doc_name = doc_type_names.get(doc_type, doc_type)
                    print(f"✓ {doc_name}已保存：{file_path}")
                    saved_files.append(file_path)
            
            # 保存AI段落信息
            if "ai_sections_used" in result:
                sections_file = output_dir / f"ai_sections_v2_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(sections_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "ai_sections_used": result["ai_sections_used"],
                        "generation_time": datetime.now().isoformat(),
                        "document_count": len(saved_files)
                    }, f, ensure_ascii=False, indent=2)
                print(f"✓ AI段落信息已保存：{sections_file}")
            
            # 生成汇总报告
            summary_file = output_dir / f"generation_summary_v2_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(generate_summary_html(result, doc_type_names, saved_files))
            print(f"✓ 生成汇总报告：{summary_file}")
            
            return True
        else:
            print(f"错误：文档生成失败 - {result['errors']}")
            return False
            
    except Exception as e:
        print(f"错误：文档生成过程中发生异常 - {str(e)}")
        return False

def generate_summary_html(result: Dict, doc_type_names: Dict, saved_files: List[Path]) -> str:
    """生成汇总报告HTML"""
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文档生成汇总报告</title>
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #3498db;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .status {{
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .doc-list {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .doc-item {{
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background-color: #f9f9f9;
            }}
            .doc-item h3 {{
                margin-top: 0;
                color: #2c3e50;
            }}
            .word-count {{
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }}
            .timestamp {{
                text-align: center;
                color: #666;
                margin-top: 30px;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>企业文档生成汇总报告</h1>
            
            <div class="status {'success' if result['success'] else 'error'}">
                <strong>生成状态：</strong> {'成功' if result['success'] else '失败'}
            </div>
            
            {f"<div class='error'><strong>错误信息：</strong> {', '.join(result['errors'])}</div>" if result['errors'] else ''}
            
            <h2>生成的文档</h2>
            <div class="doc-list">
    """
    
    # 添加每个文档的信息
    for doc_type, content in result.items():
        if doc_type in ["success", "errors", "ai_sections_used"]:
            continue
            
        if content:
            doc_name = doc_type_names.get(doc_type, doc_type)
            word_count = len(content.replace('<', '').replace('>', '').replace(' ', ''))
            html += f"""
                <div class="doc-item">
                    <h3>{doc_name}</h3>
                    <div class="word-count">字数：{word_count}</div>
                    <div>文件类型：{doc_type}</div>
                </div>
            """
    
    html += f"""
            </div>
            
            <h2>AI段落使用情况</h2>
            <p>共使用了 {len(result.get('ai_sections_used', []))} 个AI段落</p>
            <ul>
    """
    
    for section in result.get('ai_sections_used', []):
        html += f"<li>{section}</li>"
    
    html += f"""
            </ul>
            
            <div class="timestamp">
                生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    success = generate_all_7_documents()
    if success:
        print("\n" + "=" * 60)
        print("Demo执行成功！")
        print("生成的7种文档已保存到 test_output 目录")
        print("可以使用浏览器打开HTML文件查看生成的文档")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Demo执行失败！请检查错误信息")
        print("=" * 60)
        sys.exit(1)