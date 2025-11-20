"""
文档生成服务
负责根据企业数据生成三个应急预案文档
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from .ai_service import get_ai_service
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template, TemplateNotFound, TemplateSyntaxError
from jinja2.sandbox import SandboxedEnvironment
import os
import yaml

# 导入AI Section相关模块
from ..prompts.ai_sections_loader import ai_sections_loader
from ..prompts.ai_section_processor import render_user_template, call_llm, postprocess_ai_output
from .ai_compliance_checker import ai_compliance_checker

# 配置日志
logger = logging.getLogger(__name__)

class DocumentGenerator:
    """文档生成器类"""
    
    def __init__(self):
        """初始化文档生成器"""
        # 获取当前文件所在目录的父目录
        current_dir = Path(__file__).parent.parent
        self.templates_dir = current_dir / "prompts" / "templates"
        
        # 初始化 Jinja2 环境（使用沙箱模式）
        self.jinja_env = SandboxedEnvironment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 添加自定义过滤器
        self.jinja_env.filters['tojson'] = self._tojson_filter
        
        # 缓存已加载的模板
        self._template_cache: Dict[str, Template] = {}
        
        # 加载模板注册表
        self._load_template_registry()
        
        logger.info(f"文档生成器初始化完成，模板目录: {self.templates_dir}")
    
    def _tojson_filter(self, value, indent=2):
        """JSON 序列化过滤器"""
        return json.dumps(value, ensure_ascii=False, indent=indent)
    
    def _load_template_registry(self):
        """加载模板注册表"""
        try:
            # 获取当前文件所在目录的父目录
            current_dir = Path(__file__).parent.parent
            registry_path = current_dir / "prompts" / "template_registry_v2.json"
            
            if registry_path.exists():
                with open(registry_path, 'r', encoding='utf-8') as f:
                    self.template_registry = json.load(f)
                logger.info(f"成功加载模板注册表: {registry_path}")
            else:
                logger.warning(f"模板注册表文件不存在: {registry_path}")
                self.template_registry = {"templates": {}, "document_types": {}}
        except Exception as e:
            logger.error(f"加载模板注册表失败: {str(e)}")
            self.template_registry = {"templates": {}, "document_types": {}}
    
    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """
        获取模板信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板信息字典，如果不存在返回None
        """
        for template_name, template_info in self.template_registry.get("templates", {}).items():
            if template_info.get("id") == template_id:
                return template_info
        return None
    
    def get_document_type_info(self, document_type: str) -> Optional[Dict]:
        """
        获取文档类型信息
        
        Args:
            document_type: 文档类型
            
        Returns:
            文档类型信息字典，如果不存在返回None
        """
        return self.template_registry.get("document_types", {}).get(document_type)
    
    def get_all_document_types(self) -> Dict[str, Dict]:
        """
        获取所有文档类型
        
        Returns:
            文档类型字典
        """
        return self.template_registry.get("document_types", {})
    
    def get_template_path(self, template_id: str) -> Optional[str]:
        """
        获取模板文件路径
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板文件路径，如果不存在返回None
        """
        template_info = self.get_template_info(template_id)
        if template_info:
            return template_info.get("template_path")
        return None
    
    def get_template_ai_sections(self, template_id: str) -> List[str]:
        """
        获取模板所需的AI段落列表
        
        Args:
            template_id: 模板ID
            
        Returns:
            AI段落列表
        """
        template_info = self.get_template_info(template_id)
        if template_info:
            return template_info.get("ai_sections", [])
        return []
    
    def validate_enterprise_data(self, data: dict) -> Tuple[bool, List[str]]:
        """
        验证企业数据格式是否符合 emergency_plan.json 结构
        
        Args:
            data: 企业数据字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        try:
            # 基本结构验证
            if not isinstance(data, dict):
                errors.append("数据必须是字典类型")
                return False, errors
            
            # 检查必需的顶级字段
            required_fields = ["basic_info", "production_process", "environment_info", "compliance_info", "emergency_resources"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"缺少必需字段: {field}")
                elif not isinstance(data[field], dict):
                    errors.append(f"字段 {field} 必须是字典类型")
            
            # 检查 basic_info 中的必需字段
            if "basic_info" in data:
                basic_info = data["basic_info"]
                if "company_name" not in basic_info:
                    errors.append("缺少企业名称: basic_info.company_name")
                
                # 检查联系人信息
                if "contacts" in basic_info and basic_info["contacts"]:
                    contacts = basic_info["contacts"]
                    required_contact_fields = ["legal_person", "environmental_manager", "emergency_contact"]
                    for field in required_contact_fields:
                        if field not in contacts:
                            errors.append(f"缺少联系人信息: basic_info.contacts.{field}")
            
            # 检查生产流程中的必需字段
            if "production_process" in data:
                prod_process = data["production_process"]
                if "products" in prod_process and not isinstance(prod_process["products"], list):
                    errors.append("production_process.products 必须是列表类型")
                if "raw_materials" in prod_process and not isinstance(prod_process["raw_materials"], list):
                    errors.append("production_process.raw_materials 必须是列表类型")
            
            # 检查应急资源中的必需字段
            if "emergency_resources" in data:
                emergency_res = data["emergency_resources"]
                if "contact_list_internal" in emergency_res and not isinstance(emergency_res["contact_list_internal"], list):
                    errors.append("emergency_resources.contact_list_internal 必须是列表类型")
                if "contact_list_external" in emergency_res and not isinstance(emergency_res["contact_list_external"], list):
                    errors.append("emergency_resources.contact_list_external 必须是列表类型")
                if "emergency_materials" in emergency_res and not isinstance(emergency_res["emergency_materials"], list):
                    errors.append("emergency_resources.emergency_materials 必须是列表类型")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"验证企业数据时发生错误: {str(e)}")
            errors.append(f"验证过程中发生错误: {str(e)}")
            return False, errors
    
    def load_template(self, template_name: str) -> Optional[Template]:
        """
        加载 Jinja2 模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            Jinja2 模板对象，如果加载失败返回 None
        """
        # 检查缓存
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        try:
            # 加载模板
            template = self.jinja_env.get_template(template_name)
            
            # 缓存模板
            self._template_cache[template_name] = template
            
            logger.info(f"成功加载模板: {template_name}")
            return template
            
        except TemplateNotFound as e:
            logger.error(f"模板文件不存在: {template_name}, 错误: {str(e)}")
            return None
        except TemplateSyntaxError as e:
            logger.error(f"模板语法错误: {template_name}, 行 {e.lineno}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"加载模板失败: {template_name}, 错误: {str(e)}")
            return None
    
    def render_jinja(self, template_name: str, data: dict) -> Optional[str]:
        """
        渲染单个模板
        
        Args:
            template_name: 模板名称
            data: 渲染数据
            
        Returns:
            渲染后的 HTML 字符串，如果渲染失败返回 None
        """
        try:
            # 加载模板
            template = self.load_template(template_name)
            if not template:
                return None
            
            # 渲染模板
            rendered_html = template.render(**data)
            
            logger.info(f"成功渲染模板: {template_name}")
            return rendered_html
            
        except Exception as e:
            logger.error(f"渲染模板失败: {template_name}, 错误: {str(e)}")
            return None
    
    def _prepare_template_data(self, enterprise_data: dict) -> dict:
        """
        准备模板数据，处理一些通用字段和默认值
        
        Args:
            enterprise_data: 企业原始数据
            
        Returns:
            处理后的模板数据
        """
        # 创建数据副本，避免修改原始数据
        data = enterprise_data.copy()
        
        # 设置默认值
        defaults = {
            "plan_version": "1",
            "assessment_date": "2023年1月",
            "investigation_date": "2023年1月",
            "publish_date": "2023年1月1日",
            "implement_date": "2023年1月1日",
            "compile_unit": data.get("basic_info", {}).get("company_name", ""),
            "record_number": "",
            "record_date": "",
            "organization_code": "",
            "legal_representative": "",
            "legal_phone": "",
            "contact_person": "",
            "contact_phone": "",
            "fax": "/",
            "email": "",
            "address": "",
            "risk_level": "L",
            "plan_signer": "",
            "submit_time": "",
            "commander_name": "",
            "emergency_phone": "",
            "regional_plan_name": "XX区突发环境事件应急预案",
            "longitude": "xxx",
            "latitude": "xxx",
            "terrain_description": "",
            "weather_description": "",
            "hydrology_description": "",
            "location_description": "",
            "enterprise_overview": "",
            "environmental_work": "",
            "construction_layout": "",
            "production_process_description": "",
            "safety_management_description": "",
            "water_environment_impact": "",
            "air_environment_impact": "",
            "noise_environment_impact": "",
            "solid_waste_impact": "",
            "risk_management_conclusion": "",
            "long_term_plan": "",
            "medium_term_plan": "",
            "short_term_plan": "",
            "final_risk_level": "",
            "q_value": "",
            "water_q_value": "",
            "has_violations": False,
            "investigation_baseline_date": "2023年",
            "investigation_start_date": "2023年1月1日",
            "investigation_end_date": "2023年1月31日",
            "investigation_leader": "",
            "investigation_contact": "",
            "investigation_process": "",
            "resource_types": "",
            "has_external_support": False,
            "external_support_count": 0,
            "investigation_reviewed": False,
            "investigation_archived": False,
            "update_mechanism": False,
            "resource_match": "满足",
            "gap_analysis_1": "",
            "gap_analysis_2": "",
            "gap_analysis_3": "",
            "gap_analysis_4": "",
            "conclusion": "",
            "main_responsible_person": "",
            "env_responsible_person": "",
            "incident_type": "",
            "incident_description": "",
            "incident_consequence_analysis": "",
            "emergency_materials_for_incident": "",
            "incident_response_measures": "",
            "incident_response_precautions": "",
            "internal_emergency_contacts": "",
            "fire_police": "119",
            "env_bureau": "",
            "surrounding_units": "",
            "incident_name": "",
            "incident_time": "",
            "incident_unit": "",
            "incident_category": "",
            "incident_location": "",
            "incident_reporter": "",
            "incident_briefing": "",
            "incident_receiver": "",
            "incident_info_transfer_method": "",
            "incident_preliminary_cause": "",
            "incident_taken_measures": "",
            "has_casualties": "",
            "casualties_details": "",
            "info_report_leader": "",
            "report_time": "",
            "report_method": "",
            "report_content": "",
            "leader_instructions": "",
            "is_plan_activated": "",
            "response_level": "",
            "is_external_help_requested": "",
            "rescue_departments": "",
            "used_emergency_materials": "",
            "main_emergency_measures": "",
            "emergency_result": "",
            "form_filler": "",
            "start_order_signer": "",
            "start_order_time": "",
            "start_order_messenger": "",
            "start_order_transmit_time": "",
            "end_order_signer": "",
            "end_order_time": "",
            "end_order_messenger": "",
            "end_order_transmit_time": "",
            "drill_time": "",
            "drill_participants": "",
            "drill_content": "",
            "drill_preparation": "",
            "drill_other": "",
            "drill_planner": "",
            "drill_approver": "",
            "drill_plan_date": "",
            "drill_recorder": "",
            "drill_record_date": "",
            "drill_reviewer": "",
            "drill_review_date": "",
            "change_reason": "",
            "change_applying_unit": "",
            "emergency_response_card_content": ""
        }
        
        # 合并默认值
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        # 处理企业名称
        if "basic_info" in data and "company_name" in data["basic_info"]:
            data["enterprise_name"] = data["basic_info"]["company_name"]
        else:
            data["enterprise_name"] = "企业名称"
        
        # 处理地址
        if "basic_info" in data and "address" in data["basic_info"]:
            address = data["basic_info"]["address"]
            if isinstance(address, dict):
                # 组合地址各部分
                address_parts = []
                if "province" in address and address["province"]:
                    address_parts.append(address["province"])
                if "city" in address and address["city"]:
                    address_parts.append(address["city"])
                if "district" in address and address["district"]:
                    address_parts.append(address["district"])
                if "detail" in address and address["detail"]:
                    address_parts.append(address["detail"])
                data["address"] = "".join(address_parts)
                
                # 提取经纬度
                if "longitude" in address:
                    data["longitude"] = address["longitude"]
                if "latitude" in address:
                    data["latitude"] = address["latitude"]
        
        # 处理联系人信息
        if "basic_info" in data and "contacts" in data["basic_info"]:
            contacts = data["basic_info"]["contacts"]
            if isinstance(contacts, dict):
                # 法定代表人
                if "legal_person" in contacts and isinstance(contacts["legal_person"], dict):
                    legal_person = contacts["legal_person"]
                    if "name" in legal_person:
                        data["legal_representative"] = legal_person["name"]
                    if "mobile" in legal_person:
                        data["legal_phone"] = legal_person["mobile"]
                
                # 环保负责人
                if "environmental_manager" in contacts and isinstance(contacts["environmental_manager"], dict):
                    env_manager = contacts["environmental_manager"]
                    if "name" in env_manager:
                        data["env_responsible_person"] = env_manager["name"]
                
                # 应急联系人
                if "emergency_contact" in contacts and isinstance(contacts["emergency_contact"], dict):
                    emergency_contact = contacts["emergency_contact"]
                    if "name" in emergency_contact:
                        data["contact_person"] = emergency_contact["name"]
                    if "mobile" in emergency_contact:
                        data["contact_phone"] = emergency_contact["mobile"]
                
                # 办公电话和邮箱
                if "office_phone" in contacts:
                    data["emergency_phone"] = contacts["office_phone"]
                if "email" in contacts:
                    data["email"] = contacts["email"]
        
        # 处理风险等级
        if "basic_info" in data and "risk_level" in data["basic_info"]:
            risk_level = data["basic_info"]["risk_level"]
            if risk_level == "一般":
                data["risk_level"] = "L"
            elif risk_level == "较大":
                data["risk_level"] = "M"
            elif risk_level == "重大":
                data["risk_level"] = "H"
            else:
                data["risk_level"] = "L"
        
        # 处理内部联系人列表
        if "emergency_resources" in data and "contact_list_internal" in data["emergency_resources"]:
            data["internal_contacts"] = data["emergency_resources"]["contact_list_internal"]
        else:
            data["internal_contacts"] = []
        
        # 处理外部联系人列表
        if "emergency_resources" in data and "contact_list_external" in data["emergency_resources"]:
            data["external_contacts"] = data["emergency_resources"]["contact_list_external"]
        else:
            data["external_contacts"] = []
        
        # 处理应急物资
        if "emergency_resources" in data and "emergency_materials" in data["emergency_resources"]:
            data["emergency_materials"] = data["emergency_resources"]["emergency_materials"]
        else:
            data["emergency_materials"] = []
        
        # 处理应急队伍
        if "emergency_resources" in data and "emergency_team" in data["emergency_resources"]:
            emergency_team = data["emergency_resources"]["emergency_team"]
            
            # 构建应急队伍列表
            emergency_teams = []
            
            # 总指挥
            if "basic_info" in data and "contacts" in data["basic_info"] and "legal_person" in data["basic_info"]["contacts"]:
                legal_person = data["basic_info"]["contacts"]["legal_person"]
                if isinstance(legal_person, dict):
                    emergency_teams.append({
                        "organization": "应急指挥部",
                        "department": "总指挥",
                        "leader": legal_person.get("name", ""),
                        "contact": legal_person.get("mobile", "")
                    })
            
            # 副总指挥
            if "basic_info" in data and "contacts" in data["basic_info"] and "environmental_manager" in data["basic_info"]["contacts"]:
                env_manager = data["basic_info"]["contacts"]["environmental_manager"]
                if isinstance(env_manager, dict):
                    emergency_teams.append({
                        "organization": "应急指挥部",
                        "department": "副总指挥",
                        "leader": env_manager.get("name", ""),
                        "contact": env_manager.get("mobile", "")
                    })
            
            # 添加其他内部联系人到应急队伍
            if "internal_contacts" in data and isinstance(data["internal_contacts"], list):
                for contact in data["internal_contacts"]:
                    if isinstance(contact, dict):
                        emergency_teams.append({
                            "organization": contact.get("department", ""),
                            "department": contact.get("role", ""),
                            "leader": contact.get("name", ""),
                            "contact": contact.get("mobile", "")
                        })
            
            data["emergency_teams"] = emergency_teams
        
        # 处理产品信息
        if "production_process" in data and "products" in data["production_process"]:
            data["products"] = data["production_process"]["products"]
        else:
            data["products"] = []
        
        # 处理原材料信息
        if "production_process" in data and "raw_materials" in data["production_process"]:
            data["raw_materials"] = data["production_process"]["raw_materials"]
        else:
            data["raw_materials"] = []
        
        # 处理危险化学品信息
        if "production_process" in data and "hazardous_chemicals" in data["production_process"]:
            data["hazardous_chemicals"] = data["production_process"]["hazardous_chemicals"]
        else:
            data["hazardous_chemicals"] = []
        
        # 处理危险废物信息
        if "production_process" in data and "hazardous_waste" in data["production_process"]:
            data["hazardous_waste"] = data["production_process"]["hazardous_waste"]
        else:
            data["hazardous_waste"] = []
        
        # 处理环境受体信息
        if "environment_info" in data and "nearby_receivers" in data["environment_info"]:
            nearby_receivers = data["environment_info"]["nearby_receivers"]
            
            # 分离水环境和大气环境受体
            water_receptors = []
            air_receptors = []
            
            for receptor in nearby_receivers:
                if isinstance(receptor, dict):
                    receptor_type = receptor.get("receiver_type", "")
                    if "水" in receptor_type:
                        water_receptors.append(receptor)
                    else:
                        air_receptors.append(receptor)
            
            data["water_receptors"] = water_receptors
            data["air_receptors"] = air_receptors
        else:
            data["water_receptors"] = []
            data["air_receptors"] = []
        
        # 处理能源消耗信息
        if "production_process" in data and "energy" in data["production_process"]:
            energy = data["production_process"]["energy"]
            if isinstance(energy, dict):
                energy_consumption = []
                
                if "water_consumption" in energy:
                    energy_consumption.append({
                        "type": "水",
                        "unit": "吨/年",
                        "annual_consumption": energy["water_consumption"]
                    })
                
                if "electricity_consumption" in energy:
                    energy_consumption.append({
                        "type": "电",
                        "unit": "千瓦时/年",
                        "annual_consumption": energy["electricity_consumption"]
                    })
                
                if "natural_gas" in energy:
                    energy_consumption.append({
                        "type": "天然气",
                        "unit": "立方米/年",
                        "annual_consumption": energy["natural_gas"]
                    })
                
                if "other_energy" in energy:
                    energy_consumption.append({
                        "type": "其他能源",
                        "unit": "",
                        "annual_consumption": energy["other_energy"]
                    })
                
                data["energy_consumption"] = energy_consumption
        else:
            data["energy_consumption"] = []
        
        # 处理应急演练信息
        if "emergency_resources" in data and "emergency_drills" in data["emergency_resources"]:
            data["emergency_drills"] = data["emergency_resources"]["emergency_drills"]
        else:
            data["emergency_drills"] = []
        
        return data
    
    def generate_ai_section(self, section_name: str, enterprise_data: dict, user_id: Optional[str] = None) -> str:
        """
        生成AI段落内容
        
        Args:
            section_name: 章节名称，如 "enterprise_overview", "risk_prevention_measures"
            enterprise_data: 整个企业数据
            user_id: 用户ID（用于使用量统计）
            
        Returns:
            对应章节的一段中文文案
        """
        try:
            # 获取AI服务实例
            ai_service = get_ai_service()
            
            # 构建提示词（这里使用简单的提示词，后续可以优化）
            prompt = self._build_section_prompt(section_name, enterprise_data)
            
            # AI配置
            config = {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # 调用AI生成内容
            content = ai_service.generate(prompt, config, user_id)
            
            logger.info(f"成功生成AI段落: {section_name}")
            return content
            
        except Exception as e:
            logger.error(f"生成AI段落失败: {section_name}, 错误: {str(e)}")
            # 返回错误提示内容
            return f"[AI生成失败: {section_name}] {str(e)}"
    
    def _build_section_prompt(self, section_name: str, enterprise_data: dict) -> str:
        """
        构建章节提示词
        
        Args:
            section_name: 章节名称
            enterprise_data: 企业数据
            
        Returns:
            构建好的提示词
        """
        # 获取企业名称
        enterprise_name = enterprise_data.get("basic_info", {}).get("company_name", "企业名称")
        
        # 根据章节名称构建不同的提示词
        prompts = {
            "enterprise_overview": f"""
            请为"{enterprise_name}"生成企业概况描述，内容应包括：
            - 企业成立时间
            - 环保投资情况
            - 主要建设内容
            - 主要生产能力
            - 主要产品名称
            - 工作制度
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "location_description": f"""
            请为"{enterprise_name}"生成地理位置及交通描述，内容应包括：
            - 企业地理位置
            - 周边交通情况
            - 经纬度坐标
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}).get("address", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在150-200字
            """,
            
            "terrain_description": f"""
            请为"{enterprise_name}"生成地形地貌描述，内容应包括：
            - 企业所在区域的地形特征
            - 地貌特点
            - 对环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在150-200字
            """,
            
            "weather_description": f"""
            请为"{enterprise_name}"生成气象条件描述，内容应包括：
            - 企业所在区域的气候特征
            - 主要气象参数
            - 对环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在150-200字
            """,
            
            "hydrology_description": f"""
            请为"{enterprise_name}"生成水文描述，内容应包括：
            - 企业所在区域的水文情况
            - 周边地表水情况
            - 对环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在150-200字
            """,
            
            "production_process_description": f"""
            请为"{enterprise_name}"生成生产工艺描述，内容应包括：
            - 主要生产工艺流程
            - 关键生产环节
            - 环境影响因素
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("production_process", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在300-400字
            """,
            
            "safety_management_description": f"""
            请为"{enterprise_name}"生成安全生产管理描述，内容应包括：
            - 安全生产管理体系
            - 应急救援物资配备情况
            - 相关措施和制度
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("emergency_resources", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "water_environment_impact": f"""
            请为"{enterprise_name}"生成水环境影响分析，内容应包括：
            - 废水产生情况
            - 处理方式和效果
            - 对水环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("production_process", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("environment_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "air_environment_impact": f"""
            请为"{enterprise_name}"生成大气环境影响分析，内容应包括：
            - 废气产生情况
            - 处理方式和效果
            - 对大气环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("production_process", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("environment_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "noise_environment_impact": f"""
            请为"{enterprise_name}"生成噪声环境影响分析，内容应包括：
            - 噪声产生源
            - 噪声控制措施
            - 对声环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("production_process", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("environment_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在150-200字
            """,
            
            "solid_waste_impact": f"""
            请为"{enterprise_name}"生成固体废物影响分析，内容应包括：
            - 固体废物产生情况
            - 处置方式
            - 对环境的影响
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("production_process", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("environment_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "risk_management_conclusion": f"""
            请为"{enterprise_name}"生成风险管理结论，内容应包括：
            - 环境风险管理制度评估
            - 应急资源评估
            - 风险防控能力评估
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("emergency_resources", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "long_term_plan": f"""
            请为"{enterprise_name}"制定环境风险防控长期计划，内容应包括：
            - 长期目标和措施
            - 实施步骤和时间安排
            - 预期效果
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "medium_term_plan": f"""
            请为"{enterprise_name}"制定环境风险防控中期计划，内容应包括：
            - 中期目标和措施
            - 实施步骤和时间安排
            - 预期效果
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("emergency_resources", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """,
            
            "short_term_plan": f"""
            请为"{enterprise_name}"制定环境风险防控短期计划，内容应包括：
            - 短期目标和措施
            - 实施步骤和时间安排
            - 预期效果
            
            请根据以下企业信息生成：
            {json.dumps(enterprise_data.get("basic_info", {}), ensure_ascii=False, indent=2)}
            {json.dumps(enterprise_data.get("emergency_resources", {}), ensure_ascii=False, indent=2)}
            
            要求：
            1. 内容专业、准确
            2. 语言简洁明了
            3. 符合环保文档风格
            4. 字数控制在200-300字
            """
        }
        
        # 返回对应的提示词，如果没有找到则返回通用提示词
        return prompts.get(section_name, f"请为'{enterprise_name}'生成'{section_name}'章节的内容，要求专业、准确、简洁。")
    
    def build_ai_sections(self, enterprise_data: dict, user_id: Optional[str] = None, document_type: Optional[str] = None, enable_compliance_check: bool = True, max_retries: int = 2) -> dict:
        """
        构建AI段落（使用配置文件）
        
        Args:
            enterprise_data: 整个企业数据
            user_id: 用户ID（用于使用量统计）
            document_type: 文档类型，可选，用于过滤特定文档的sections
            enable_compliance_check: 是否启用合规检查
            max_retries: 最大重试次数
            
        Returns:
            包含所有AI段落的字典
        """
        try:
            # 加载AI Section配置
            sections_config = ai_sections_loader.load_config()
            
            # 根据文档类型过滤sections
            if document_type:
                sections_to_process = ai_sections_loader.get_sections_by_document(document_type)
            else:
                sections_to_process = ai_sections_loader.get_enabled_sections()
            
            ai_sections = {}
            
            # 生成每个段落
            for section_key, section_config in sections_to_process.items():
                try:
                    # 检查section是否启用
                    if not section_config.get("enabled", True):
                        ai_sections[section_key] = ""
                        continue
                    
                    # 获取system prompt和user template
                    system_prompt = section_config.get("system_prompt", "")
                    user_template = section_config.get("user_template", "")
                    
                    # 渲染user template
                    user_prompt = render_user_template(user_template, enterprise_data)
                    
                    # 初始化重试计数器
                    retry_count = 0
                    processed_content = ""
                    compliance_passed = False
                    
                    # 重试循环，直到通过合规检查或达到最大重试次数
                    while retry_count < max_retries and not compliance_passed:
                        retry_count += 1
                        
                        # 调用LLM生成内容
                        model = section_config.get("model", "xunfei_spark_v4")
                        generated_content = call_llm(model, system_prompt, user_prompt, user_id)
                        
                        # 后处理AI输出
                        processed_content = postprocess_ai_output(generated_content)
                        
                        # 如果启用合规检查，则进行验证
                        if enable_compliance_check:
                            compliance_result = ai_compliance_checker.check_ai_output(section_key, processed_content)
                            compliance_passed = compliance_result["passed"]
                            
                            if not compliance_passed:
                                logger.warning(f"AI段落 {section_key} 第 {retry_count} 次生成未通过合规检查")
                                logger.warning(f"合规问题: {compliance_result['issues']}")
                                
                                # 如果不是最后一次重试，调整system prompt加入合规要求
                                if retry_count < max_retries:
                                    system_prompt += f"\n\n请注意，上次生成的内容存在以下合规问题：{', '.join(compliance_result['issues'])}。请在本次生成中修正这些问题。"
                            else:
                                logger.info(f"AI段落 {section_key} 通过合规检查")
                        else:
                            # 如果不启用合规检查，直接通过
                            compliance_passed = True
                    
                    ai_sections[section_key] = processed_content
                    logger.info(f"成功生成AI段落: {section_key}, 重试次数: {retry_count}")
                    
                except Exception as e:
                    logger.error(f"生成AI段落失败: {section_key}, 错误: {str(e)}")
                    ai_sections[section_key] = f"[AI生成失败: {section_key}] {str(e)}"
            
            return ai_sections
            
        except Exception as e:
            logger.error(f"构建AI段落失败: {str(e)}")
            return {}
    
    def generate_all_documents(self, enterprise_data: dict, user_id: Optional[str] = None, use_v2: bool = True) -> dict:
        """
        生成所有文档（支持V2版本）
        
        Args:
            enterprise_data: 符合 emergency_plan.json 的企业数据
            user_id: 用户ID（用于使用量统计）
            use_v2: 是否使用V2版本模板
            
        Returns:
            包含所有文档渲染结果的字典
        """
        result = {
            "risk_report": None,
            "emergency_plan": None,
            "resource_report": None,
            "release_order": None,
            "opinion_adoption": None,
            "emergency_monitoring_plan": None,
            "revision_note": None,
            "success": False,
            "errors": [],
            "ai_sections_used": []
        }
        
        try:
            # 验证企业数据
            is_valid, errors = self.validate_enterprise_data(enterprise_data)
            if not is_valid:
                result["errors"] = errors
                logger.error(f"企业数据验证失败: {errors}")
                return result
            
            # 生成所有AI段落（启用合规检查）
            logger.info("开始生成AI段落（启用合规检查）...")
            ai_sections = self.build_ai_sections(enterprise_data, user_id, enable_compliance_check=True)
            result["ai_sections_used"] = list(ai_sections.keys())
            
            # 进行整体合规性检查
            logger.info("进行整体合规性检查...")
            compliance_results = ai_compliance_checker.check_multiple_sections(ai_sections)
            result["compliance_results"] = compliance_results
            
            if not compliance_results["overall_passed"]:
                logger.warning(f"部分AI段落未通过合规检查，总问题数: {compliance_results['total_issues']}")
                result["warnings"] = [f"合规检查发现问题，总评分: {compliance_results['overall_score']}/100"]
            else:
                logger.info("所有AI段落通过合规检查")
            
            # 准备模板数据，合并AI段落
            template_data = self._prepare_template_data(enterprise_data)
            template_data["ai_sections"] = ai_sections
            
            if use_v2:
                # 使用V2版本模板
                document_types = self.get_all_document_types()
                
                for doc_type, doc_info in document_types.items():
                    template_id = doc_info.get("template_id")
                    template_path = self.get_template_path(template_id)
                    
                    if template_path:
                        logger.info(f"渲染{doc_info.get('output_name', doc_type)}...")
                        content = self.render_jinja(template_path, template_data)
                        
                        if content is None:
                            result["errors"].append(f"{doc_info.get('output_name', doc_type)}生成失败")
                        else:
                            # 映射文档类型到结果键名
                            if doc_type == "risk_assessment":
                                result["risk_report"] = content
                            else:
                                result[doc_type] = content
                    else:
                        logger.warning(f"未找到{doc_type}的模板路径")
            else:
                # 使用V1版本模板（保持向后兼容）
                # 渲染风险评估报告
                logger.info("渲染风险评估报告...")
                risk_report = self.render_jinja("template_risk_plan.jinja2", template_data)
                if risk_report is None:
                    result["errors"].append("风险评估报告生成失败")
                else:
                    result["risk_report"] = risk_report
                
                # 渲染应急预案
                logger.info("渲染应急预案...")
                emergency_plan = self.render_jinja("template_emergency_plan.jinja2", template_data)
                if emergency_plan is None:
                    result["errors"].append("应急预案生成失败")
                else:
                    result["emergency_plan"] = emergency_plan
                
                # 渲染应急资源调查报告
                logger.info("渲染应急资源调查报告...")
                resource_report = self.render_jinja("template_resource_investigation.jinja2", template_data)
                if resource_report is None:
                    result["errors"].append("应急资源调查报告生成失败")
                else:
                    result["resource_report"] = resource_report
            
            # 检查是否所有文档都生成成功
            main_docs = [result["risk_report"], result["emergency_plan"], result["resource_report"]]
            if all(doc is not None for doc in main_docs):
                result["success"] = True
                logger.info("主要文档生成成功")
            else:
                logger.error(f"部分文档生成失败，错误: {result['errors']}")
            
            return result
            
        except Exception as e:
            error_msg = f"生成文档时发生错误: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
            return result
    
    def generate_single_document(self, document_type: str, enterprise_data: dict, user_id: Optional[str] = None, use_v2: bool = True) -> dict:
        """
        生成单个文档（支持V2版本）
        
        Args:
            document_type: 文档类型 (risk_assessment/emergency_plan/resource_report/release_order/opinion_adoption/emergency_monitoring_plan/revision_note)
            enterprise_data: 符合 emergency_plan.json 的企业数据
            user_id: 用户ID（用于使用量统计）
            use_v2: 是否使用V2版本模板
            
        Returns:
            包含文档渲染结果的字典
        """
        result = {
            "content": None,
            "success": False,
            "errors": [],
            "ai_sections_used": []
        }
        
        try:
            # 验证企业数据
            is_valid, errors = self.validate_enterprise_data(enterprise_data)
            if not is_valid:
                result["errors"] = errors
                logger.error(f"企业数据验证失败: {errors}")
                return result
            
            if use_v2:
                # 使用V2版本模板
                doc_info = self.get_document_type_info(document_type)
                if not doc_info:
                    result["errors"].append(f"不支持的文档类型: {document_type}")
                    return result
                
                template_id = doc_info.get("template_id")
                template_path = self.get_template_path(template_id)
                
                if not template_path:
                    result["errors"].append(f"未找到{document_type}的模板路径")
                    return result
                
                # 获取模板所需的AI段落
                ai_sections_needed = self.get_template_ai_sections(template_id)
                
                # 生成特定文档类型的AI段落（启用合规检查）
                logger.info(f"开始生成{document_type}的AI段落（启用合规检查）...")
                ai_sections = {}
                
                if ai_sections_needed:
                    # 只生成需要的AI段落
                    all_ai_sections = self.build_ai_sections(enterprise_data, user_id, enable_compliance_check=True)
                    for section in ai_sections_needed:
                        if section in all_ai_sections:
                            ai_sections[section] = all_ai_sections[section]
                
                result["ai_sections_used"] = list(ai_sections.keys())
                
                # 准备模板数据，合并AI段落
                template_data = self._prepare_template_data(enterprise_data)
                template_data["ai_sections"] = ai_sections
                
                # 渲染文档
                logger.info(f"渲染{doc_info.get('output_name', document_type)}文档...")
                content = self.render_jinja(template_path, template_data)
                
            else:
                # 使用V1版本模板（保持向后兼容）
                # 根据文档类型选择模板
                template_map = {
                    "risk_assessment": "template_risk_plan.jinja2",
                    "emergency_plan": "template_emergency_plan.jinja2",
                    "resource_report": "template_resource_investigation.jinja2"
                }
                
                template_name = template_map.get(document_type)
                if not template_name:
                    result["errors"].append(f"不支持的文档类型: {document_type}")
                    return result
                
                # 生成特定文档类型的AI段落
                logger.info(f"开始生成{document_type}的AI段落...")
                ai_sections = self.build_ai_sections(enterprise_data, user_id, document_type)
                result["ai_sections_used"] = list(ai_sections.keys())
                
                # 准备模板数据，合并AI段落
                template_data = self._prepare_template_data(enterprise_data)
                template_data["ai_sections"] = ai_sections
                
                # 渲染文档
                logger.info(f"渲染{document_type}文档...")
                content = self.render_jinja(template_name, template_data)
            
            if content is None:
                result["errors"].append(f"{document_type}文档生成失败")
            else:
                result["content"] = content
                result["success"] = True
                logger.info(f"{document_type}文档生成成功")
            
            return result
            
        except Exception as e:
            error_msg = f"生成{document_type}文档时发生错误: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
            return result
    
    def generate_single_section(self, section_key: str, enterprise_data: dict, user_id: Optional[str] = None) -> dict:
        """
        生成单个AI段落
        
        Args:
            section_key: AI段落键名
            enterprise_data: 符合 emergency_plan.json 的企业数据
            user_id: 用户ID（用于使用量统计）
            
        Returns:
            包含AI段落生成结果的字典
        """
        result = {
            "content": None,
            "success": False,
            "errors": []
        }
        
        try:
            # 检查section是否存在
            section_config = ai_sections_loader.get_section_config(section_key)
            if section_config is None:
                result["errors"].append(f"AI段落不存在: {section_key}")
                return result
            
            # 检查section是否启用
            if not section_config.get("enabled", True):
                result["errors"].append(f"AI段落已禁用: {section_key}")
                return result
            
            # 获取system prompt和user template
            system_prompt = section_config.get("system_prompt", "")
            user_template = section_config.get("user_template", "")
            
            # 渲染user template
            user_prompt = render_user_template(user_template, enterprise_data)
            
            # 调用LLM生成内容
            model = section_config.get("model", "xunfei_spark_v4")
            generated_content = call_llm(model, system_prompt, user_prompt, user_id)
            
            # 后处理AI输出
            processed_content = postprocess_ai_output(generated_content)
            
            result["content"] = processed_content
            result["success"] = True
            logger.info(f"成功生成AI段落: {section_key}")
            
            return result
            
        except Exception as e:
            error_msg = f"生成AI段落时发生错误: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
            return result


# 创建全局文档生成器实例
document_generator = DocumentGenerator()