"""
AI Section配置加载器
负责加载、验证和管理ai_sections.json配置文件
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

logger = logging.getLogger(__name__)

class AISectionsLoader:
    """AI Section配置加载器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化AI Section配置加载器
        
        Args:
            config_path: 配置文件路径，默认为 app/prompts/config/ai_sections.json
        """
        if config_path is None:
            # 获取当前文件所在目录的父目录
            current_dir = Path(__file__).parent
            self.config_path = current_dir / "config" / "ai_sections.json"
        else:
            self.config_path = Path(config_path)
        
        self._sections_config: Optional[Dict[str, Any]] = None
        self._last_modified: Optional[float] = None
        
        logger.info(f"AI Section配置加载器初始化完成，配置文件路径: {self.config_path}")
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载AI Section配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            AI Section配置字典
        """
        try:
            # 检查文件是否存在
            if not self.config_path.exists():
                logger.error(f"配置文件不存在: {self.config_path}")
                return {}
            
            # 检查文件是否需要重新加载
            current_modified = self.config_path.stat().st_mtime
            if not force_reload and self._sections_config is not None and self._last_modified == current_modified:
                return self._sections_config
            
            # 加载配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置格式
            is_valid, errors = self._validate_config(config)
            if not is_valid:
                logger.error(f"配置文件格式验证失败: {errors}")
                return {}
            
            # 缓存配置
            self._sections_config = config
            self._last_modified = current_modified
            
            logger.info(f"成功加载AI Section配置，共{len(config.get('sections', {}))}个section")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def _validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置文件格式
        
        Args:
            config: 配置字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查顶级结构
        if not isinstance(config, dict):
            errors.append("配置文件必须是字典类型")
            return False, errors
        
        if "sections" not in config:
            errors.append("缺少必需字段: sections")
            return False, errors
        
        sections = config["sections"]
        if not isinstance(sections, dict):
            errors.append("sections字段必须是字典类型")
            return False, errors
        
        # 检查每个section的配置
        for section_key, section_config in sections.items():
            section_errors = self._validate_section_config(section_key, section_config)
            errors.extend(section_errors)
        
        return len(errors) == 0, errors
    
    def _validate_section_config(self, section_key: str, section_config: Any) -> List[str]:
        """
        验证单个section配置
        
        Args:
            section_key: section键名
            section_config: section配置
            
        Returns:
            错误信息列表
        """
        errors = []
        
        # 检查section配置是否为字典
        if not isinstance(section_config, dict):
            errors.append(f"section '{section_key}' 的配置必须是字典类型")
            return errors
        
        # 检查必需字段
        required_fields = ["enabled", "document", "description", "version", "system_prompt", "user_template"]
        for field in required_fields:
            if field not in section_config:
                errors.append(f"section '{section_key}' 缺少必需字段: {field}")
        
        # 检查字段类型
        if "enabled" in section_config and not isinstance(section_config["enabled"], bool):
            errors.append(f"section '{section_key}' 的enabled字段必须是布尔类型")
        
        if "document" in section_config and not isinstance(section_config["document"], str):
            errors.append(f"section '{section_key}' 的document字段必须是字符串类型")
        
        if "description" in section_config and not isinstance(section_config["description"], str):
            errors.append(f"section '{section_key}' 的description字段必须是字符串类型")
        
        if "version" in section_config and not isinstance(section_config["version"], int):
            errors.append(f"section '{section_key}' 的version字段必须是整数类型")
        
        if "system_prompt" in section_config and not isinstance(section_config["system_prompt"], str):
            errors.append(f"section '{section_key}' 的system_prompt字段必须是字符串类型")
        
        if "user_template" in section_config and not isinstance(section_config["user_template"], str):
            errors.append(f"section '{section_key}' 的user_template字段必须是字符串类型")
        
        if "fields" in section_config and not isinstance(section_config["fields"], list):
            errors.append(f"section '{section_key}' 的fields字段必须是列表类型")
        
        # 检查document字段值
        if "document" in section_config:
            valid_documents = ["risk_assessment", "emergency_plan", "resource_report"]
            if section_config["document"] not in valid_documents:
                errors.append(f"section '{section_key}' 的document字段值必须是: {valid_documents}")
        
        return errors
    
    def get_sections_config(self) -> Dict[str, Any]:
        """
        获取所有sections配置
        
        Returns:
            sections配置字典
        """
        config = self.load_config()
        return config.get("sections", {})
    
    def get_section_config(self, section_key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定section的配置
        
        Args:
            section_key: section键名
            
        Returns:
            section配置字典，如果不存在返回None
        """
        sections = self.get_sections_config()
        return sections.get(section_key)
    
    def get_enabled_sections(self) -> Dict[str, Any]:
        """
        获取所有启用的sections
        
        Returns:
            启用的sections配置字典
        """
        sections = self.get_sections_config()
        enabled_sections = {}
        
        for section_key, section_config in sections.items():
            if section_config.get("enabled", True):
                enabled_sections[section_key] = section_config
        
        return enabled_sections
    
    def get_sections_by_document(self, document_type: str) -> Dict[str, Any]:
        """
        根据文档类型获取sections
        
        Args:
            document_type: 文档类型 (risk_assessment/emergency_plan/resource_report)
            
        Returns:
            指定文档类型的sections配置字典
        """
        sections = self.get_enabled_sections()
        document_sections = {}
        
        for section_key, section_config in sections.items():
            if section_config.get("document") == document_type:
                document_sections[section_key] = section_config
        
        return document_sections
    
    def get_section_keys(self) -> List[str]:
        """
        获取所有section键名
        
        Returns:
            section键名列表
        """
        sections = self.get_sections_config()
        return list(sections.keys())
    
    def get_enabled_section_keys(self) -> List[str]:
        """
        获取所有启用的section键名
        
        Returns:
            启用的section键名列表
        """
        sections = self.get_enabled_sections()
        return list(sections.keys())
    
    def is_section_enabled(self, section_key: str) -> bool:
        """
        检查section是否启用
        
        Args:
            section_key: section键名
            
        Returns:
            是否启用
        """
        section_config = self.get_section_config(section_key)
        if section_config is None:
            return False
        
        return section_config.get("enabled", True)
    
    def extract_template_variables(self, template_str: str) -> List[str]:
        """
        从模板字符串中提取变量
        
        Args:
            template_str: 模板字符串
            
        Returns:
            变量名列表
        """
        # 使用正则表达式提取 {variable} 格式的变量
        pattern = r'\{([^}]+)\}'
        variables = re.findall(pattern, template_str)
        return list(set(variables))  # 去重
    
    def validate_template_variables(self, section_key: str, enterprise_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证模板变量是否在企业数据中存在
        
        Args:
            section_key: section键名
            enterprise_data: 企业数据
            
        Returns:
            (是否有效, 缺失的变量列表)
        """
        section_config = self.get_section_config(section_key)
        if section_config is None:
            return False, [f"Section '{section_key}' 不存在"]
        
        user_template = section_config.get("user_template", "")
        template_variables = self.extract_template_variables(user_template)
        
        missing_variables = []
        for var in template_variables:
            if not self._check_variable_exists(var, enterprise_data):
                missing_variables.append(var)
        
        return len(missing_variables) == 0, missing_variables
    
    def _check_variable_exists(self, variable_path: str, data: Dict[str, Any]) -> bool:
        """
        检查变量路径是否在数据中存在
        
        Args:
            variable_path: 变量路径，如 "basic_info.company_name"
            data: 数据字典
            
        Returns:
            是否存在
        """
        try:
            keys = variable_path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False
            
            return True
        except Exception:
            return False


# 创建全局AI Section配置加载器实例
ai_sections_loader = AISectionsLoader()