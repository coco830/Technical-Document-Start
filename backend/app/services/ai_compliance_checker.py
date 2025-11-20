"""
AI输出合规性检查器
用于验证AI生成的段落是否符合专家评审要求
"""

import json
import re
import os
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

class AIComplianceChecker:
    """AI输出合规性检查器"""
    
    def __init__(self):
        """初始化合规检查器"""
        # 获取当前文件所在目录的父目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(current_dir, "prompts", "config")
        
        # 加载合规矩阵配置
        compliance_matrix_path = os.path.join(config_dir, "compliance_matrix.json")
        with open(compliance_matrix_path, 'r', encoding='utf-8') as f:
            self.compliance_matrix = json.load(f)
        
        logger.info(f"合规检查器初始化完成，已加载 {len(self.compliance_matrix)} 个段落的合规规则")
    
    def check_ai_output(self, section_key: str, text: str) -> Dict[str, Any]:
        """
        检查AI输出是否符合合规要求
        
        Args:
            section_key: AI段落键名
            text: AI生成的文本内容
            
        Returns:
            包含检查结果的字典
        """
        result = {
            "section": section_key,
            "passed": True,
            "issues": [],
            "warnings": [],
            "compliance_score": 100  # 满分100分
        }
        
        # 如果该段落没有合规规则，直接返回通过
        if section_key not in self.compliance_matrix:
            result["warnings"].append(f"段落 {section_key} 没有对应的合规规则")
            return result
        
        rules = self.compliance_matrix[section_key]
        
        # 检查必须覆盖的内容
        if "must_cover" in rules:
            self._check_must_cover(text, rules["must_cover"], result)
        
        # 检查必须避免的内容
        if "avoid" in rules:
            self._check_avoid(text, rules["avoid"], result)
        
        # 检查特殊要求
        if "requirements" in rules:
            self._check_requirements(section_key, text, rules["requirements"], result)
        
        # 通用检查
        self._check_general_compliance(text, result)
        
        # 计算合规分数
        if result["issues"]:
            result["passed"] = False
            result["compliance_score"] = max(0, 100 - len(result["issues"]) * 10)
        
        return result
    
    def _check_must_cover(self, text: str, must_cover_items: List[str], result: Dict):
        """检查必须覆盖的内容"""
        for item in must_cover_items:
            # 将规则项转换为检查关键词
            keywords = self._get_check_keywords(item)
            
            # 检查是否包含至少一个关键词
            found = False
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    found = True
                    break
            
            if not found:
                result["issues"].append(f"缺少必须覆盖的内容: {item}")
    
    def _check_avoid(self, text: str, avoid_items: List[str], result: Dict):
        """检查必须避免的内容"""
        for item in avoid_items:
            # 将规则项转换为检查关键词
            keywords = self._get_check_keywords(item)
            
            # 检查是否包含关键词
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    result["issues"].append(f"包含应避免的内容: {item}")
                    break
    
    def _check_requirements(self, section_key: str, text: str, requirements: List[str], result: Dict):
        """检查特殊要求"""
        for requirement in requirements:
            if section_key == "risk_management_conclusion" and requirement == "reference_hj941_2018":
                if "HJ941-2018" not in text and "HJ941" not in text:
                    result["issues"].append("风险管理结论必须引用HJ941-2018标准")
            
            elif section_key == "hydrology_description" and requirement == "if_river_mentioned_upstream_downstream":
                if "河" in text and ("上游" not in text and "下游" not in text):
                    result["issues"].append("水文描述中提到河流时必须说明上下游方向")
            
            elif section_key == "incident_response_card" and requirement == "scenario_liquid_leak":
                if "泄漏" not in text and "液体" not in text:
                    result["issues"].append("应急处置卡必须包含液体泄漏场景")
            
            elif section_key == "incident_response_card" and requirement == "scenario_gas_leak":
                if "气体" not in text and "挥发" not in text:
                    result["issues"].append("应急处置卡必须包含气体泄漏场景")
            
            elif section_key == "incident_response_card" and requirement == "scenario_fire":
                if "火灾" not in text and "燃烧" not in text:
                    result["issues"].append("应急处置卡必须包含火灾场景")
            
            elif section_key == "water_environment_impact" and requirement == "reference_hydrology_field":
                # 检查是否引用了水文字段相关内容
                if "水体" not in text and "河流" not in text and "地表水" not in text:
                    result["warnings"].append("建议在水环境影响分析中引用水文信息")
            
            elif section_key == "air_environment_impact" and requirement == "mention_dominant_wind":
                if "风向" not in text and "主导风向" not in text:
                    result["issues"].append("大气环境影响分析必须提到主导风向")
            
            elif section_key == "solid_waste_impact" and requirement == "reference_hazardous_waste_field":
                if "危废" not in text and "危险废物" not in text:
                    result["issues"].append("固体废物影响分析必须引用危险废物信息")
            
            elif section_key == "risk_prevention_measures" and requirement == "mention_equipment_materials":
                if "物资" not in text and "设备" not in text and "装备" not in text:
                    result["issues"].append("风险防范措施必须提到应急物资或设备")
            
            elif section_key == "emergency_response_measures" and requirement == "follow_flow_structure":
                # 检查是否有流程化结构
                flow_indicators = ["报警", "研判", "处置", "报告", "疏散", "警戒"]
                found_flow = any(indicator in text for indicator in flow_indicators)
                if not found_flow:
                    result["warnings"].append("建议应急响应措施按照流程化结构编写")
            
            elif section_key == "investigation_process" and requirement == "data_review":
                if "资料" not in text and "审核" not in text:
                    result["issues"].append("调查过程必须体现资料审核")
            
            elif section_key == "investigation_process" and requirement == "site_verification":
                if "现场" not in text and "核查" not in text and "查看" not in text:
                    result["issues"].append("调查过程必须体现现场查验")
            
            elif section_key == "short_term_plan" and requirement == "can_write_inspection_system_update":
                if "巡检" not in text and "制度" not in text and "更新" not in text:
                    result["warnings"].append("短期计划可包含巡检、制度更新等内容")
    
    def _check_general_compliance(self, text: str, result: Dict):
        """通用合规性检查"""
        # 检查绝对化词语
        absolute_words = ["绝对不会", "完全不会", "绝对安全", "完全满足", "绝对不会造成影响"]
        for word in absolute_words:
            if word in text:
                result["issues"].append(f"使用了绝对化词语: {word}")
        
        # 检查是否过于简短
        if len(text) < 50:
            result["warnings"].append("内容过于简短，可能不够详细")
        
        # 检查是否只有标题没有内容
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 3:
            result["warnings"].append("内容结构过于简单，建议增加更多细节")
    
    def _get_check_keywords(self, rule_item: str) -> List[str]:
        """根据规则项生成检查关键词"""
        keyword_map = {
            "scenario_liquid_leak": ["泄漏", "液体", "溢流", "渗漏"],
            "scenario_gas_leak": ["气体", "挥发", "泄漏", "扩散"],
            "scenario_fire": ["火灾", "燃烧", "爆炸", "灭火"],
            "basic_company_info": ["企业", "公司", "规模", "产品"],
            "sensitive_point_location": ["位置", "方位", "距离", "敏感点"],
            "direction_distance": ["方位", "距离", "方向", "米"],
            "dominant_wind_direction": ["风向", "主导风向", "风"],
            "monitoring_plan_water_info": ["水体", "河流", "监测", "点位"],
            "process_consistent_with_incident_scenarios": ["工艺", "流程", "事故", "场景"],
            "management_system_existence": ["制度", "管理", "体系", "建立"],
            "water_impact_corresponds_to_sensitive_points": ["水体", "影响", "敏感点"],
            "gas_diffusion_mention_dominant_wind": ["气体", "扩散", "风向"],
            "hazardous_waste_risk": ["危废", "危险废物", "风险"],
            "reference_hj941_2018": ["HJ941", "标准", "依据"],
            "continuous_improvement": ["持续", "改进", "提升"],
            "specific_operable_actions": ["具体", "措施", "行动", "操作"],
            "real_enterprise_work_situation": ["企业", "实际", "现状", "工作"],
            "layout_rationality": ["布局", "布置", "合理", "功能"],
            "measures_consistent_with_resources": ["措施", "资源", "一致", "匹配"],
            "complete_process_response": ["报警", "研判", "处置", "报告"],
            "team_capability_gaps": ["队伍", "能力", "不足", "差距"],
            "equipment_gaps": ["装备", "设备", "不足", "差距"],
            "training_gaps": ["培训", "知识", "不足", "差距"],
            "drill_gaps": ["演练", "不足", "差距", "频次"],
            "overall_evaluation": ["总体", "评价", "结论"],
            "gaps": ["差距", "不足", "问题"],
            "recommendations": ["建议", "措施", "改进"],
            "data_review": ["资料", "审核", "查阅"],
            "site_verification": ["现场", "核查", "查看", "实地"],
            "absolute_language": ["绝对", "完全", "肯定", "一定"],
            "emergency_organization": ["应急组织", "指挥部", "队伍"],
            "response_measures": ["应急措施", "处置", "响应"],
            "fabricated_terrain_data": ["海拔", "坐标", "高程"],
            "specific_yearly_values": ["年降雨量", "年均", "毫米/年"],
            "fabricated_equipment_or_process": ["虚构", "编造", "假设"],
            "evaluate_perfection_level": ["完善", "不足", "良好"],
            "provide_numerical_values": ["分贝", "dB", "毫克"],
            "provide_decibel_values": ["分贝", "dB"],
            "commitment_engineering_projects": ["投资", "建设", "工程"],
            "investment_plans": ["投资", "资金", "预算"],
            "generic_content": ["八股", "模板", "通用"],
            "insufficient_drawings": ["图纸", "图件", "缺失"],
            "reference_hydrology_field": ["水文", "水体", "河流"],
            "mention_equipment_materials": ["物资", "设备", "装备"],
            "follow_flow_structure": ["流程", "步骤", "程序"]
        }
        
        return keyword_map.get(rule_item, [rule_item])
    
    def check_multiple_sections(self, sections_data: Dict[str, str]) -> Dict[str, Any]:
        """
        批量检查多个AI段落的合规性
        
        Args:
            sections_data: 段落键名到文本的映射
            
        Returns:
            包含所有段落检查结果的字典
        """
        results = {
            "overall_passed": True,
            "overall_score": 100,
            "section_results": {},
            "total_issues": 0,
            "total_warnings": 0
        }
        
        for section_key, text in sections_data.items():
            section_result = self.check_ai_output(section_key, text)
            results["section_results"][section_key] = section_result
            
            if not section_result["passed"]:
                results["overall_passed"] = False
            
            results["total_issues"] += len(section_result["issues"])
            results["total_warnings"] += len(section_result["warnings"])
        
        # 计算总体分数
        if results["total_issues"] > 0:
            results["overall_score"] = max(0, 100 - results["total_issues"] * 5)
        
        return results


# 创建全局合规检查器实例
ai_compliance_checker = AIComplianceChecker()