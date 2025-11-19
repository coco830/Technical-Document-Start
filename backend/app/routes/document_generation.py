"""
文档生成路由
处理文档生成的API请求
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from app.services.document_generator import document_generator
from app.utils.auth import get_current_user
from app.models.user import User
import logging

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["文档生成"])

class DocumentGenerationRequest(BaseModel):
    """文档生成请求模型"""
    enterprise_data: Dict[str, Any] = Field(..., description="企业数据，符合emergency_plan.json结构")
    
    class Config:
        schema_extra = {
            "example": {
                "enterprise_data": {
                    "basic_info": {
                        "company_name": "示例企业有限公司",
                        "company_short_name": "示例企业",
                        "credit_code": "91110000000000000X",
                        "industry_category": "制造业",
                        "industry_subcategory": "化工产品制造",
                        "park_name": "示例工业园区",
                        "risk_level": "一般",
                        "address": {
                            "province": "北京市",
                            "city": "北京市",
                            "district": "海淀区",
                            "detail": "示例街道123号",
                            "longitude": 116.404,
                            "latitude": 39.915
                        },
                        "contacts": {
                            "legal_person": {
                                "name": "张三",
                                "position": "法定代表人",
                                "mobile": "13800138000"
                            },
                            "environmental_manager": {
                                "name": "李四",
                                "position": "环保负责人",
                                "mobile": "13900139000"
                            },
                            "emergency_contact": {
                                "name": "王五",
                                "position": "应急联系人",
                                "mobile": "13700137000"
                            },
                            "office_phone": "010-12345678",
                            "email": "contact@example.com"
                        },
                        "operation": {
                            "established_date": "2020-01-01",
                            "production_status": "在产",
                            "employees_total": 100,
                            "employees_production": 80,
                            "work_shift": "三班倒",
                            "work_hours_per_shift": 8,
                            "operating_days_per_year": 300,
                            "land_area": 10000,
                            "building_area": 5000,
                            "investment_total": 10000000,
                            "investment_environmental": 1000000,
                            "company_intro": "示例企业是一家专业从事化工产品制造的企业"
                        }
                    },
                    "production_process": {
                        "products": [
                            {
                                "product_name": "示例产品A",
                                "product_type": "化工产品",
                                "design_capacity": "1000吨/年",
                                "actual_output": "800吨/年"
                            }
                        ],
                        "raw_materials": [
                            {
                                "name": "原料A",
                                "cas_no": "123-45-6",
                                "material_category": "有机原料",
                                "is_hazardous": True,
                                "hazard_types": ["易燃", "有毒"],
                                "annual_usage": 500,
                                "max_storage": 50,
                                "used_in_process": "生产过程A",
                                "phase": "液体"
                            }
                        ],
                        "energy": {
                            "water_consumption": 10000,
                            "electricity_consumption": 50000,
                            "natural_gas": 10000,
                            "other_energy": "其他能源"
                        },
                        "process_description": "示例生产工艺流程描述",
                        "storage_units": [
                            {
                                "unit_name": "储罐A",
                                "facility_type": "储罐",
                                "stored_materials": ["原料A"],
                                "capacity": 50,
                                "max_actual_storage": 40,
                                "location_desc": "厂区东侧",
                                "anti_leak_measures": "防渗漏措施"
                            }
                        ],
                        "hazardous_chemicals": [
                            {
                                "chemical_name": "化学品A",
                                "cas_no": "123-45-6",
                                "hazard_category": "易燃液体",
                                "max_storage": 50,
                                "phase": "液体",
                                "is_major_source": False
                            }
                        ],
                        "hazardous_waste": [
                            {
                                "waste_name": "废液A",
                                "hw_category": "废有机溶剂",
                                "waste_code": "HW06",
                                "source_process": "生产过程A",
                                "hazard_characteristics": ["易燃", "有毒"],
                                "max_storage": 5,
                                "storage_location": "危废暂存间",
                                "disposal_company": "示例处置公司"
                            }
                        ]
                    },
                    "environment_info": {
                        "nearby_receivers": [
                            {
                                "receiver_type": "水环境",
                                "name": "示例河流",
                                "direction": "东",
                                "distance_m": 500,
                                "population_or_scale": "小型河流"
                            },
                            {
                                "receiver_type": "大气环境",
                                "name": "示例居民区",
                                "direction": "西",
                                "distance_m": 1000,
                                "population_or_scale": "1000人"
                            }
                        ],
                        "wastewater": {
                            "production_wastewater": True,
                            "domestic_wastewater": True,
                            "treatment_facilities": [
                                {
                                    "facility_name": "污水处理站",
                                    "process_type": "生化处理",
                                    "design_capacity": 100,
                                    "actual_capacity": 80,
                                    "discharge_destination": "市政管网"
                                }
                            ]
                        },
                        "waste_gas": {
                            "organized_sources": [
                                {
                                    "source_name": "排气筒A",
                                    "main_pollutants": ["VOCs", "NOx"],
                                    "treatment_method": "活性炭吸附",
                                    "stack_height": 15
                                }
                            ],
                            "fugitive_sources_desc": "无组织排放源描述"
                        },
                        "noise": [
                            {
                                "noise_source": "泵房",
                                "location": "厂区北侧",
                                "control_measures": "隔声罩"
                            }
                        ],
                        "solid_waste": [
                            {
                                "waste_name": "包装材料",
                                "waste_type": "一般固废",
                                "annual_production": 10,
                                "storage_method": "分类存放",
                                "disposal_method": "回收利用"
                            }
                        ]
                    },
                    "compliance_info": {
                        "eia": {
                            "project_name": "示例项目",
                            "approval_document_no": "环审[2020]123号",
                            "approval_date": "2020-01-01",
                            "consistency_status": "一致"
                        },
                        "acceptance": {
                            "type": "竣工环境保护验收",
                            "document_no": "验[2020]456号",
                            "date": "2020-12-01"
                        },
                        "pollutant_permit": {
                            "permit_no": "排污许可证123456",
                            "authority": "北京市生态环境局",
                            "valid_from": "2021-01-01",
                            "valid_to": "2026-01-01",
                            "permitted_pollutants": ["COD", "氨氮", "VOCs", "NOx"]
                        },
                        "hazardous_waste_contracts": [
                            {
                                "company_name": "示例处置公司",
                                "permit_no": "危废经营许可证123456",
                                "contract_from": "2021-01-01",
                                "contract_to": "2026-01-01"
                            }
                        ]
                    },
                    "emergency_resources": {
                        "contact_list_internal": [
                            {
                                "role": "总指挥",
                                "name": "张三",
                                "department": "总经理办公室",
                                "mobile": "13800138000"
                            },
                            {
                                "role": "副总指挥",
                                "name": "李四",
                                "department": "环保部",
                                "mobile": "13900139000"
                            }
                        ],
                        "contact_list_external": [
                            {
                                "unit_type": "消防部门",
                                "unit_name": "示例消防队",
                                "phone": "119"
                            },
                            {
                                "unit_type": "环保部门",
                                "unit_name": "示例环保局",
                                "phone": "12369"
                            }
                        ],
                        "emergency_materials": [
                            {
                                "material_name": "灭火器",
                                "unit": "个",
                                "quantity": 20,
                                "purpose": "灭火",
                                "storage_location": "各车间",
                                "keeper": "安全管理员",
                                "keeper_phone": "13600136000"
                            },
                            {
                                "material_name": "应急灯",
                                "unit": "个",
                                "quantity": 10,
                                "purpose": "应急照明",
                                "storage_location": "仓库",
                                "keeper": "仓库管理员",
                                "keeper_phone": "13500135000"
                            }
                        ],
                        "emergency_team": {
                            "has_internal_team": True,
                            "team_size": 15,
                            "team_structure": "总指挥、副总指挥、应急办公室、现场处置组、后勤保障组"
                        },
                        "emergency_drills": [
                            {
                                "drill_date": "2023-06-15",
                                "drill_type": "综合应急演练",
                                "scenario": "化学品泄漏",
                                "participants": "全体员工"
                            }
                        ]
                    }
                }
            }
        }

class DocumentGenerationResponse(BaseModel):
    """文档生成响应模型"""
    success: bool = Field(..., description="生成是否成功")
    risk_report: Optional[str] = Field(None, description="风险评估报告HTML")
    emergency_plan: Optional[str] = Field(None, description="应急预案HTML")
    resource_report: Optional[str] = Field(None, description="应急资源调查报告HTML")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "risk_report": "<html>...</html>",
                "emergency_plan": "<html>...</html>",
                "resource_report": "<html>...</html>",
                "errors": []
            }
        }

@router.post("/generate-all", response_model=DocumentGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_all_documents(
    request: DocumentGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成所有三个应急预案文档
    
    - **enterprise_data**: 企业数据，符合emergency_plan.json结构
    
    返回三个文档的HTML渲染结果：
    - 风险评估报告
    - 应急预案
    - 应急资源调查报告
    """
    try:
        # 记录请求
        logger.info(f"用户 {current_user.id} 请求生成文档")
        
        # 调用文档生成服务
        result = document_generator.generate_all_documents(request.enterprise_data)
        
        # 记录结果
        if result["success"]:
            logger.info(f"用户 {current_user.id} 文档生成成功")
        else:
            logger.warning(f"用户 {current_user.id} 文档生成失败，错误: {result['errors']}")
        
        return DocumentGenerationResponse(**result)
        
    except Exception as e:
        error_msg = f"文档生成过程中发生错误: {str(e)}"
        logger.error(error_msg)
        
        return DocumentGenerationResponse(
            success=False,
            errors=[error_msg]
        )

@router.get("/generate-status", response_model=dict)
async def get_generation_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取文档生成服务状态
    
    返回文档生成服务的当前状态信息
    """
    try:
        # 检查模板文件是否存在
        template_files = [
            "template_risk_plan.jinja2",
            "template_emergency_plan.jinja2",
            "template_resource_investigation.jinja2"
        ]
        
        templates_status = {}
        for template_file in template_files:
            template = document_generator.load_template(template_file)
            templates_status[template_file] = template is not None
        
        all_templates_available = all(templates_status.values())
        
        return {
            "status": "available" if all_templates_available else "unavailable",
            "templates": templates_status,
            "message": "所有模板文件可用" if all_templates_available else "部分模板文件不可用"
        }
        
    except Exception as e:
        error_msg = f"获取文档生成状态时发生错误: {str(e)}"
        logger.error(error_msg)
        
        return {
            "status": "error",
            "message": error_msg
        }