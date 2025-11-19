"""
AI Section处理器
负责处理AI Section的模板渲染和LLM调用
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
import time
import uuid

logger = logging.getLogger(__name__)

def render_user_template(template_str: str, enterprise_data: dict) -> str:
    """
    将user_template中的{xxx.yyy}占位符替换为enterprise_data中的实际值
    
    Args:
        template_str: 包含占位符的模板字符串
        enterprise_data: 企业数据字典
        
    Returns:
        渲染后的字符串
    """
    try:
        # 使用正则表达式查找所有占位符
        pattern = r'\{([^}]+)\}'
        placeholders = re.findall(pattern, template_str)
        
        rendered_str = template_str
        
        # 替换每个占位符
        for placeholder in placeholders:
            value = get_value_by_path(enterprise_data, placeholder)
            if value is not None:
                # 处理不同类型的值
                if isinstance(value, list):
                    # 列表类型，转换为字符串
                    value_str = summarize_list(value)
                elif isinstance(value, dict):
                    # 字典类型，转换为JSON字符串
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    # 其他类型，直接转换为字符串
                    value_str = str(value)
                
                # 替换占位符
                rendered_str = rendered_str.replace(f'{{{placeholder}}}', value_str)
            else:
                # 值不存在，替换为空字符串或默认提示
                rendered_str = rendered_str.replace(f'{{{placeholder}}}', "（企业未提供相关信息）")
        
        return rendered_str
        
    except Exception as e:
        logger.error(f"渲染用户模板失败: {str(e)}")
        return template_str  # 返回原始模板

def get_value_by_path(data: dict, path: str) -> Any:
    """
    根据路径获取字典中的值
    
    Args:
        data: 数据字典
        path: 路径，如 "basic_info.company_name"
        
    Returns:
        找到的值，如果找不到返回None
    """
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
        
    except Exception as e:
        logger.error(f"获取路径值失败: {path}, 错误: {str(e)}")
        return None

def summarize_list(value: List[Any]) -> str:
    """
    将列表转换为摘要字符串
    
    Args:
        value: 列表值
        
    Returns:
        摘要字符串
    """
    try:
        if not value:
            return "无"
        
        if len(value) <= 3:
            # 如果列表项不多，全部列出
            items = []
            for item in value:
                if isinstance(item, dict):
                    # 如果是字典，尝试获取name字段
                    name = item.get('name', '') or item.get('product_name', '') or item.get('chemical_name', '') or str(item)
                    items.append(name)
                else:
                    items.append(str(item))
            return "、".join(items)
        else:
            # 如果列表项较多，只显示前几项
            items = []
            for i, item in enumerate(value[:3]):
                if isinstance(item, dict):
                    name = item.get('name', '') or item.get('product_name', '') or item.get('chemical_name', '') or str(item)
                    items.append(name)
                else:
                    items.append(str(item))
            
            return f"{'、'.join(items)}等{len(value)}项"
            
    except Exception as e:
        logger.error(f"列表摘要生成失败: {str(e)}")
        return f"共{len(value)}项"

def call_llm(model: str, system: str, user: str, user_id: Optional[str] = None) -> str:
    """
    调用大语言模型生成内容（Mock实现）
    
    Args:
        model: 模型名称
        system: 系统提示词
        user: 用户提示词
        user_id: 用户ID（用于使用量统计）
        
    Returns:
        生成的文本内容
    """
    try:
        # 记录调用信息
        call_id = str(uuid.uuid4())
        logger.info(f"LLM调用开始 - ID: {call_id}, 模型: {model}, 用户ID: {user_id}")
        
        # Mock实现 - 模拟AI生成内容
        # 在实际应用中，这里应该调用真实的AI服务
        mock_content = generate_mock_content(system, user)
        
        # 模拟处理时间
        time.sleep(0.5)
        
        logger.info(f"LLM调用完成 - ID: {call_id}, 生成长度: {len(mock_content)}")
        
        return mock_content
        
    except Exception as e:
        logger.error(f"LLM调用失败: {str(e)}")
        return f"[AI生成失败] {str(e)}"

def generate_mock_content(system: str, user: str) -> str:
    """
    生成Mock内容
    
    Args:
        system: 系统提示词
        user: 用户提示词
        
    Returns:
        Mock生成的内容
    """
    # 根据系统提示词和用户提示词生成mock内容
    if "企业概况" in system or "企业概况" in user:
        return "该企业成立于2005年，是一家专业从事化工产品生产的企业。公司占地面积约50亩，建筑面积约20000平方米，总投资约5000万元，其中环保投资约500万元。主要产品包括有机溶剂、化工中间体等，年产量约10000吨。企业实行三班制生产，每班8小时，全年生产时间约330天。"
    
    elif "地理位置" in system or "地理位置" in user:
        return "企业位于XX省XX市XX工业园区内，距市中心约15公里。厂区东邻XX路，南接XX高速，西靠XX河，北临XX铁路。交通便利，原材料和产品运输方便。地理位置坐标为东经XX度XX分，北纬XX度XX分。"
    
    elif "地形地貌" in system or "地形地貌" in user:
        return "企业所在地地势平坦，海拔约50米，地形以平原为主。厂区内地势南高北低，高差约2米，有利于雨水排放。周边无山体滑坡、泥石流等地质灾害隐患。"
    
    elif "气象条件" in system or "气象条件" in user:
        return "该地区属亚热带季风气候，四季分明，年平均气温16.5℃，年平均降水量1200毫米。主导风向为东南风，年平均风速2.5米/秒。无霜期约280天，气候条件适宜工业生产。"
    
    elif "水文" in system or "水文" in user:
        return "企业周边主要水体为XX河，距离厂区约1公里，河流自西向东流，年平均流量50立方米/秒。厂区地下水埋深约5-8米，水质良好。周边无饮用水源地保护区。"
    
    elif "生产工艺" in system or "生产工艺" in user:
        return "企业采用先进的连续化生产工艺，主要包括原料预处理、反应合成、分离精制、产品包装等工序。生产过程采用DCS控制系统，实现自动化生产。主要设备包括反应釜、蒸馏塔、储罐等，设备布局合理，工艺流程顺畅。"
    
    elif "安全生产管理" in system or "安全生产管理" in user:
        return "企业建立了完善的安全生产管理体系，配备了专职安全管理人员，定期开展安全培训和应急演练。应急救援物资包括消防器材、泄漏处理设备、个人防护用品等，储备充足，定期检查更新。"
    
    elif "水环境影响" in system or "水环境影响" in user:
        return "企业生产废水主要来源于设备清洗水和地面冲洗水，废水中主要污染物为COD、氨氮等。废水处理采用物化+生化工艺，处理能力50吨/日，处理后达到《污水综合排放标准》一级标准后排入市政污水管网。"
    
    elif "大气环境影响" in system or "大气环境影响" in user:
        return "企业废气主要来源于反应过程和储罐呼吸，主要污染物为VOCs。废气处理采用活性炭吸附+催化燃烧工艺，处理效率达到90%以上。处理后废气通过15米高排气筒排放，满足相关排放标准要求。"
    
    elif "噪声环境影响" in system or "噪声环境影响" in user:
        return "企业噪声主要来源于泵类、风机等设备，噪声级约85-95分贝。采取的降噪措施包括设备基础减振、安装消声器、建设隔声墙等。厂界噪声满足《工业企业厂界环境噪声排放标准》三类标准要求。"
    
    elif "固体废物影响" in system or "固体废物影响" in user:
        return "企业固体废物主要包括废包装材料、废活性炭、废催化剂等。一般工业固废分类收集后外售综合利用，危险废物委托有资质单位处理。建立了完善的固废管理台账，执行转移联单制度。"
    
    elif "风险管理结论" in system or "风险管理结论" in user:
        return "企业环境风险管理制度健全，应急资源配备充足，风险防控能力较强。企业风险等级为一般风险，能够有效应对突发环境事件。建议继续加强日常环境管理，定期开展应急演练，不断提高环境风险防控水平。"
    
    elif "长期计划" in system or "长期计划" in user:
        return "企业环境风险防控长期计划包括：完善环境管理制度体系，加强污染治理设施运行管理，推进清洁生产改造，建立环境风险预警系统，加强环境应急能力建设，提升员工环境意识，实现企业与环境协调发展。"
    
    elif "中期计划" in system or "中期计划" in user:
        return "企业环境风险防控中期计划包括：更新完善应急预案，增加应急物资储备，开展应急演练培训，加强污染源监测，建立环境隐患排查制度，完善应急响应机制，提高环境风险防控能力。"
    
    elif "短期计划" in system or "短期计划" in user:
        return "企业环境风险防控短期计划包括：开展环境风险评估，完善应急物资配备，组织应急演练培训，加强废水处理设施运行管理，建立环境监测制度，完善环境风险防控措施。"
    
    elif "环保工作情况" in system or "环保工作情况" in user:
        return "企业环保手续齐全，已取得环评批复并通过环保验收，持有排污许可证。与有资质单位签订了危险废物处置合同，严格按照环保要求进行生产经营。建立了完善的环境管理体系，定期开展环境监测。"
    
    elif "建设布置情况" in system or "建设布置情况" in user:
        return "企业总占地面积50亩，建筑面积20000平方米。生产区、办公区、仓储区布局合理，符合安全距离要求。生产车间采用封闭式结构，配备了完善的通风、防爆、消防设施。储罐区设置了防渗漏设施和围堰。"
    
    elif "风险防范措施" in system or "风险防范措施" in user:
        return "企业针对各类环境风险源采取了完善的防范措施：储罐区设置了防渗漏设施和泄漏检测报警装置，生产区配备了废气收集处理系统，废水处理设施正常运行，危险废物储存场所符合规范要求，建立了环境风险隐患排查制度。"
    
    elif "应急措施" in system or "应急措施" in user:
        return "企业突发环境事件现场应急措施包括：发现泄漏立即启动应急响应，组织人员疏散，切断污染源，采取围堵、收集、吸附等措施防止污染扩散，启动应急处理设备，监测环境质量，及时向环保部门报告事件情况。"
    
    elif "应急处置卡" in system or "应急处置卡" in user:
        return "化学品泄漏应急处置卡：1.立即报告应急指挥部；2.疏散无关人员，设立警戒区；3.切断泄漏源；4.使用吸附材料围堵收集泄漏物；5.开启通风设备；6.穿戴防护装备进行处理；7.监测环境质量；8.清理现场，恢复生产。"
    
    elif "调查过程" in system or "调查过程" in user:
        return "应急资源调查工作于2023年1月1日至1月31日进行，调查基准时间为2023年1月1日。调查工作由企业安全环保部负责，成立了专项调查小组，采用资料收集、现场核查、人员访谈等方式，全面调查了企业应急资源现状。"
    
    elif "差距分析" in system or "差距分析" in user:
        return "企业应急资源存在一定差距：应急救援队伍人员数量不足，专业技能有待提高；应急救援装备种类不够齐全，部分设备老化；应急知识培训不够系统，员工应急意识需要加强；应急演练频次不足，实战能力有待提升。"
    
    elif "结论" in system or "结论" in user:
        return "企业应急资源基本满足突发环境事件应急处置需要，但仍有提升空间。建议加强应急救援队伍建设，增加应急装备投入，完善应急知识培训体系，增加应急演练频次，不断提高企业环境应急能力。"
    
    else:
        # 默认mock内容
        return f"根据提供的信息，该企业在相关方面表现良好，符合相关法规要求。建议继续加强管理，持续改进，确保环境安全。"

def postprocess_ai_output(content: str) -> str:
    """
    后处理AI输出内容
    
    Args:
        content: AI生成的原始内容
        
    Returns:
        处理后的内容
    """
    try:
        # 去除首尾空行
        content = content.strip()
        
        # 替换多个连续空行为单个空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 确保标点符号后有空格（中文不需要）
        # content = re.sub(r'([。！？；])([^\s])', r'\1\2', content)
        
        return content
        
    except Exception as e:
        logger.error(f"后处理AI输出失败: {str(e)}")
        return content