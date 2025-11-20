#!/usr/bin/env python3
"""
将合规矩阵内容合并到AI段落配置文件中
"""

import json
import os

def merge_compliance_to_ai_sections():
    """将合规矩阵内容合并到AI段落配置文件中"""
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, "app", "prompts", "config")
    
    # 读取合规矩阵配置
    compliance_matrix_path = os.path.join(config_dir, "compliance_matrix.json")
    with open(compliance_matrix_path, 'r', encoding='utf-8') as f:
        compliance_matrix = json.load(f)
    
    # 读取AI段落配置
    ai_sections_path = os.path.join(config_dir, "ai_sections_complete.json")
    with open(ai_sections_path, 'r', encoding='utf-8') as f:
        ai_sections_config = json.load(f)
    
    # 为每个section的system_prompt添加合规要求
    for section_key, section_config in ai_sections_config["sections"].items():
        if section_key in compliance_matrix:
            compliance_rules = compliance_matrix[section_key]
            
            # 构建合规要求文本
            compliance_text = "\n\n## 合规要求\n\n"
            
            # 添加必须覆盖的内容
            if "must_cover" in compliance_rules and compliance_rules["must_cover"]:
                compliance_text += "你必须覆盖以下内容：\n"
                for item in compliance_rules["must_cover"]:
                    compliance_text += f"- {item}\n"
                compliance_text += "\n"
            
            # 添加必须避免的内容
            if "avoid" in compliance_rules and compliance_rules["avoid"]:
                compliance_text += "你必须避免以下内容：\n"
                for item in compliance_rules["avoid"]:
                    compliance_text += f"- {item}\n"
                compliance_text += "\n"
            
            # 添加特殊要求
            if "requirements" in compliance_rules and compliance_rules["requirements"]:
                compliance_text += "特殊要求：\n"
                for item in compliance_rules["requirements"]:
                    compliance_text += f"- {item}\n"
                compliance_text += "\n"
            
            # 将合规要求添加到现有的system_prompt中
            original_prompt = section_config.get("system_prompt", "")
            section_config["system_prompt"] = original_prompt + compliance_text
    
    # 保存更新后的AI段落配置
    output_path = os.path.join(config_dir, "ai_sections_with_compliance.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ai_sections_config, f, ensure_ascii=False, indent=2)
    
    print(f"已将合规要求合并到AI段落配置中，保存至: {output_path}")
    
    # 同时更新原始文件
    with open(ai_sections_path, 'w', encoding='utf-8') as f:
        json.dump(ai_sections_config, f, ensure_ascii=False, indent=2)
    
    print(f"已更新原始AI段落配置文件: {ai_sections_path}")

if __name__ == "__main__":
    merge_compliance_to_ai_sections()