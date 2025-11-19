"""
模板解析工具
用于检查模板中AI Section与配置文件之间的一致性
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .ai_sections_loader import ai_sections_loader

logger = logging.getLogger(__name__)

class TemplateChecker:
    """模板检查器类"""
    
    def __init__(self):
        """初始化模板检查器"""
        # 获取当前文件所在目录的父目录
        current_dir = Path(__file__).parent
        self.templates_dir = current_dir / "templates"
        
        # 模板文件映射
        self.template_files = {
            "risk_assessment": "template_risk_plan.jinja2",
            "emergency_plan": "template_emergency_plan.jinja2",
            "resource_report": "template_resource_investigation.jinja2"
        }
        
        logger.info(f"模板检查器初始化完成，模板目录: {self.templates_dir}")
    
    def extract_ai_sections_from_template(self, template_path: Path) -> Set[str]:
        """
        从模板文件中提取AI Section变量
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            AI Section变量名集合
        """
        try:
            if not template_path.exists():
                logger.error(f"模板文件不存在: {template_path}")
                return set()
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 使用正则表达式提取 ai_sections.xxx 变量
            pattern = r'\{\{\s*ai_sections\.([a-zA-Z0-9_]+)\s*\}\}'
            matches = re.findall(pattern, template_content)
            
            return set(matches)
            
        except Exception as e:
            logger.error(f"提取模板AI Section失败: {template_path}, 错误: {str(e)}")
            return set()
    
    def check_template_consistency(self) -> Dict[str, any]:
        """
        检查所有模板与配置文件的一致性
        
        Returns:
            检查结果字典
        """
        result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "template_analysis": {},
            "summary": {}
        }
        
        try:
            # 加载AI Section配置
            sections_config = ai_sections_loader.get_sections_config()
            defined_sections = set(sections_config.keys())
            enabled_sections = set(ai_sections_loader.get_enabled_section_keys())
            
            # 分析每个模板
            template_analysis = {}
            all_used_sections = set()
            
            for doc_type, template_file in self.template_files.items():
                template_path = self.templates_dir / template_file
                used_sections = self.extract_ai_sections_from_template(template_path)
                
                # 记录所有使用的sections
                all_used_sections.update(used_sections)
                
                # 分析当前模板
                missing_in_config = used_sections - defined_sections
                disabled_sections = used_sections - enabled_sections
                
                template_analysis[doc_type] = {
                    "template_file": template_file,
                    "used_sections": list(used_sections),
                    "missing_in_config": list(missing_in_config),
                    "disabled_sections": list(disabled_sections),
                    "is_valid": len(missing_in_config) == 0
                }
                
                # 记录错误和警告
                if missing_in_config:
                    result["errors"].append(
                        f"模板 {template_file} 中使用的AI Section未在配置中定义: {', '.join(missing_in_config)}"
                    )
                    result["success"] = False
                
                if disabled_sections:
                    result["warnings"].append(
                        f"模板 {template_file} 中使用的AI Section已禁用: {', '.join(disabled_sections)}"
                    )
            
            result["template_analysis"] = template_analysis
            
            # 检查配置中未使用的sections
            unused_in_templates = defined_sections - all_used_sections
            if unused_in_templates:
                result["warnings"].append(
                    f"配置中定义但未在任何模板中使用的AI Section: {', '.join(unused_in_templates)}"
                )
            
            # 生成摘要
            result["summary"] = {
                "total_sections_in_config": len(defined_sections),
                "enabled_sections": len(enabled_sections),
                "total_sections_used_in_templates": len(all_used_sections),
                "templates_checked": len(self.template_files),
                "missing_sections": len(result["errors"]),
                "disabled_sections": len(set(s for analysis in template_analysis.values() for s in analysis["disabled_sections"])),
                "unused_sections": len(unused_in_templates)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"检查模板一致性失败: {str(e)}")
            result["success"] = False
            result["errors"].append(f"检查过程中发生错误: {str(e)}")
            return result
    
    def check_single_template(self, doc_type: str) -> Dict[str, any]:
        """
        检查单个模板的一致性
        
        Args:
            doc_type: 文档类型 (risk_assessment/emergency_plan/resource_report)
            
        Returns:
            检查结果字典
        """
        result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "template_analysis": {}
        }
        
        try:
            # 检查文档类型是否有效
            if doc_type not in self.template_files:
                result["success"] = False
                result["errors"].append(f"不支持的文档类型: {doc_type}")
                return result
            
            # 加载AI Section配置
            sections_config = ai_sections_loader.get_sections_config()
            defined_sections = set(sections_config.keys())
            enabled_sections = set(ai_sections_loader.get_enabled_section_keys())
            
            # 分析模板
            template_file = self.template_files[doc_type]
            template_path = self.templates_dir / template_file
            used_sections = self.extract_ai_sections_from_template(template_path)
            
            # 分析结果
            missing_in_config = used_sections - defined_sections
            disabled_sections = used_sections - enabled_sections
            
            result["template_analysis"] = {
                "doc_type": doc_type,
                "template_file": template_file,
                "used_sections": list(used_sections),
                "missing_in_config": list(missing_in_config),
                "disabled_sections": list(disabled_sections),
                "is_valid": len(missing_in_config) == 0
            }
            
            # 记录错误和警告
            if missing_in_config:
                result["success"] = False
                result["errors"].append(
                    f"模板 {template_file} 中使用的AI Section未在配置中定义: {', '.join(missing_in_config)}"
                )
            
            if disabled_sections:
                result["warnings"].append(
                    f"模板 {template_file} 中使用的AI Section已禁用: {', '.join(disabled_sections)}"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"检查单个模板失败: {doc_type}, 错误: {str(e)}")
            result["success"] = False
            result["errors"].append(f"检查过程中发生错误: {str(e)}")
            return result
    
    def generate_fix_suggestions(self, check_result: Dict[str, any]) -> List[str]:
        """
        根据检查结果生成修复建议
        
        Args:
            check_result: 检查结果
            
        Returns:
            修复建议列表
        """
        suggestions = []
        
        try:
            # 处理缺失的sections
            if check_result.get("errors"):
                for error in check_result["errors"]:
                    if "未在配置中定义" in error:
                        # 提取缺失的section名称
                        match = re.search(r': (.+)$', error)
                        if match:
                            missing_sections = match.group(1).split(', ')
                            for section in missing_sections:
                                suggestions.append(
                                    f"在 ai_sections.json 中添加缺失的section配置: {section}"
                                )
            
            # 处理禁用的sections
            if check_result.get("warnings"):
                for warning in check_result["warnings"]:
                    if "已禁用" in warning:
                        # 提取禁用的section名称
                        match = re.search(r': (.+)$', warning)
                        if match:
                            disabled_sections = match.group(1).split(', ')
                            for section in disabled_sections:
                                suggestions.append(
                                    f"在 ai_sections.json 中启用section: {section} (设置 enabled: true)"
                                )
            
            # 处理未使用的sections
            for warning in check_result.get("warnings", []):
                if "未在任何模板中使用" in warning:
                    # 提取未使用的section名称
                    match = re.search(r': (.+)$', warning)
                    if match:
                        unused_sections = match.group(1).split(', ')
                        for section in unused_sections:
                            suggestions.append(
                                f"考虑在 ai_sections.json 中删除未使用的section: {section}，或在模板中使用它"
                            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成修复建议失败: {str(e)}")
            return ["生成修复建议时发生错误"]


# 创建全局模板检查器实例
template_checker = TemplateChecker()


def check_all_templates() -> Dict[str, any]:
    """
    检查所有模板的一致性（便捷函数）
    
    Returns:
        检查结果字典
    """
    return template_checker.check_template_consistency()


def check_single_template(doc_type: str) -> Dict[str, any]:
    """
    检查单个模板的一致性（便捷函数）
    
    Args:
        doc_type: 文档类型
        
    Returns:
        检查结果字典
    """
    return template_checker.check_single_template(doc_type)


def generate_fix_suggestions(check_result: Dict[str, any]) -> List[str]:
    """
    生成修复建议（便捷函数）
    
    Args:
        check_result: 检查结果
        
    Returns:
        修复建议列表
    """
    return template_checker.generate_fix_suggestions(check_result)


if __name__ == "__main__":
    # 如果直接运行此脚本，执行模板检查
    import json
    
    print("开始检查模板一致性...")
    result = check_all_templates()
    
    print("\n=== 检查结果 ===")
    print(f"检查状态: {'成功' if result['success'] else '失败'}")
    
    if result["errors"]:
        print("\n错误:")
        for error in result["errors"]:
            print(f"  - {error}")
    
    if result["warnings"]:
        print("\n警告:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
    
    print("\n=== 摘要 ===")
    for key, value in result["summary"].items():
        print(f"{key}: {value}")
    
    print("\n=== 修复建议 ===")
    suggestions = generate_fix_suggestions(result)
    for suggestion in suggestions:
        print(f"  - {suggestion}")