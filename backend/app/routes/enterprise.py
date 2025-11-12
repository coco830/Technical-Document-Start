"""
企业信息相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from app.database import get_db
from app.models.enterprise import EnterpriseInfo
from app.models.user import User
from app.schemas.enterprise import (
    EnterpriseInfoCreate, EnterpriseInfoResponse, EnterpriseInfoUpdate, 
    EnterpriseInfoList, EnterpriseBasicResponse, EnvPermitsResponse,
    HazardousMaterialResponse, EmergencyResourceResponse, EmergencyOrgResponse
)
from app.utils.auth import get_current_user
from app.utils.pagination import get_pagination_params, paginate_query
from app.utils.error_handler import handle_error, ErrorCategory

router = APIRouter(prefix="/api/enterprise", tags=["企业信息"])


def convert_enterprise_to_response(enterprise: EnterpriseInfo) -> EnterpriseInfoResponse:
    """将企业信息模型转换为响应模式"""
    return EnterpriseInfoResponse(
        id=enterprise.id,
        user_id=enterprise.user_id,
        project_id=enterprise.project_id,
        enterprise_basic=EnterpriseBasicResponse(
            enterprise_name=enterprise.enterprise_name,
            address=enterprise.address,
            industry=enterprise.industry,
            contact_person=enterprise.contact_person,
            phone=enterprise.phone,
            employee_count=enterprise.employee_count,
            main_products=enterprise.main_products,
            annual_output=enterprise.annual_output,
            description=enterprise.description
        ),
        env_permits=EnvPermitsResponse(
            env_assessment_no=enterprise.env_assessment_no,
            acceptance_no=enterprise.acceptance_no,
            discharge_permit_no=enterprise.discharge_permit_no,
            env_dept=enterprise.env_dept
        ),
        hazardous_materials=[
            HazardousMaterialResponse(
                id=str(material.get('id', '')),
                name=material.get('name', ''),
                max_storage=material.get('max_storage', ''),
                annual_usage=material.get('annual_usage', ''),
                storage_location=material.get('storage_location', '')
            )
            for material in (enterprise.hazardous_materials or [])
        ],
        emergency_resources=[
            EmergencyResourceResponse(
                id=str(resource.get('id', '')),
                name=resource.get('name', ''),
                quantity=resource.get('quantity', ''),
                purpose=resource.get('purpose', ''),
                storage_location=resource.get('storage_location', ''),
                custodian=resource.get('custodian', '')
            )
            for resource in (enterprise.emergency_resources or [])
        ],
        emergency_orgs=[
            EmergencyOrgResponse(
                id=str(org.get('id', '')),
                org_name=org.get('org_name', ''),
                responsible_person=org.get('responsible_person', ''),
                contact_phone=org.get('contact_phone', ''),
                duties=org.get('duties', '')
            )
            for org in (enterprise.emergency_orgs or [])
        ],
        created_at=enterprise.created_at,
        updated_at=enterprise.updated_at
    )


@router.post("/info", response_model=EnterpriseInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise_info(
    enterprise_data: EnterpriseInfoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建企业信息
    """
    try:
        # 检查用户是否已有企业信息（可选限制）
        existing_info = db.query(EnterpriseInfo).filter(
            EnterpriseInfo.user_id == current_user.id
        ).first()
        
        # 如果需要限制每个用户只能有一条企业信息，可以取消下面的注释
        # if existing_info:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="用户已存在企业信息，请更新现有信息"
        #     )
        
        # 创建新的企业信息
        db_enterprise = EnterpriseInfo(
            user_id=current_user.id,
            project_id=enterprise_data.project_id,
            
            # 企业基本信息
            enterprise_name=enterprise_data.enterprise_basic.enterprise_name,
            address=enterprise_data.enterprise_basic.address,
            industry=enterprise_data.enterprise_basic.industry,
            contact_person=enterprise_data.enterprise_basic.contact_person,
            phone=enterprise_data.enterprise_basic.phone,
            employee_count=enterprise_data.enterprise_basic.employee_count,
            main_products=enterprise_data.enterprise_basic.main_products,
            annual_output=enterprise_data.enterprise_basic.annual_output,
            description=enterprise_data.enterprise_basic.description,
            
            # 环保手续信息
            env_assessment_no=enterprise_data.env_permits.env_assessment_no,
            acceptance_no=enterprise_data.env_permits.acceptance_no,
            discharge_permit_no=enterprise_data.env_permits.discharge_permit_no,
            env_dept=enterprise_data.env_permits.env_dept,
            
            # JSON数据
            hazardous_materials=[material.dict() for material in enterprise_data.hazardous_materials],
            emergency_resources=[resource.dict() for resource in enterprise_data.emergency_resources],
            emergency_orgs=[org.dict() for org in enterprise_data.emergency_orgs]
        )
        
        db.add(db_enterprise)
        db.commit()
        db.refresh(db_enterprise)
        
        return convert_enterprise_to_response(db_enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "operation": "create_enterprise_info"},
            user_message="创建企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.get("/info", response_model=EnterpriseInfoList)
async def get_enterprise_infos(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的企业信息列表
    """
    try:
        # 构建查询
        query = db.query(EnterpriseInfo).filter(EnterpriseInfo.user_id == current_user.id)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    EnterpriseInfo.enterprise_name.contains(search),
                    EnterpriseInfo.address.contains(search),
                    EnterpriseInfo.industry.contains(search)
                )
            )
        
        # 按创建时间倒序排列
        query = query.order_by(desc(EnterpriseInfo.created_at))
        
        # 分页
        pagination = get_pagination_params(page, page_size)
        paginated_query = paginate_query(query, pagination)
        
        enterprise_infos = paginated_query.all()
        total = query.count()
        
        return EnterpriseInfoList(
            enterprise_infos=[convert_enterprise_to_response(info) for info in enterprise_infos],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
        
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "operation": "get_enterprise_infos"},
            user_message="获取企业信息列表失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.get("/info/{info_id}", response_model=EnterpriseInfoResponse)
async def get_enterprise_info(
    info_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取特定企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        return convert_enterprise_to_response(enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "get_enterprise_info"},
            user_message="获取企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.put("/info/{info_id}", response_model=EnterpriseInfoResponse)
async def update_enterprise_info(
    info_id: int,
    enterprise_data: EnterpriseInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        # 更新企业基本信息
        if enterprise_data.enterprise_basic:
            for field, value in enterprise_data.enterprise_basic.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新环保手续信息
        if enterprise_data.env_permits:
            for field, value in enterprise_data.env_permits.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新JSON数据
        if enterprise_data.hazardous_materials is not None:
            enterprise.hazardous_materials = [material.dict() for material in enterprise_data.hazardous_materials]
        
        if enterprise_data.emergency_resources is not None:
            enterprise.emergency_resources = [resource.dict() for resource in enterprise_data.emergency_resources]
        
        if enterprise_data.emergency_orgs is not None:
            enterprise.emergency_orgs = [org.dict() for org in enterprise_data.emergency_orgs]
        
        # 更新项目关联
        if enterprise_data.project_id is not None:
            enterprise.project_id = enterprise_data.project_id
        
        db.commit()
        db.refresh(enterprise)
        
        return convert_enterprise_to_response(enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "update_enterprise_info"},
            user_message="更新企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.delete("/info/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise_info(
    info_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        db.delete(enterprise)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "delete_enterprise_info"},
            user_message="删除企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )