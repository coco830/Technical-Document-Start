from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.permissions import has_permission
from app.core.exceptions import PermissionException, NotFoundException, ValidationException
from app.models.user import User
from app.schemas.company import (
    Company, CompanyCreate, CompanyUpdate, CompanyWithDetails, CompanyList,
    CompanySearch, CompanyStatistics, CompanyVerification, CompanyVerificationCreate,
    CompanyVerificationUpdate, CompanyVerificationWithDetails
)
from app.services.company import company_service

router = APIRouter()


# 企业CRUD API端点
@router.get("/", response_model=CompanyList)
async def get_companies(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    industry: Optional[str] = Query(None, description="按行业筛选"),
    unified_social_credit_code: Optional[str] = Query(None, description="按统一社会信用代码筛选"),
    legal_representative: Optional[str] = Query(None, description="按法定代表人筛选"),
    contact_phone: Optional[str] = Query(None, description="按联系电话筛选"),
    contact_email: Optional[str] = Query(None, description="按联系邮箱筛选"),
    address: Optional[str] = Query(None, description="按地址筛选"),
    order_by: Optional[str] = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序")
) -> Any:
    """获取企业列表（支持分页、筛选、排序）"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看企业的权限"
        )
    
    # 构建搜索参数
    search_params = CompanySearch(
        keyword=keyword,
        industry=industry,
        unified_social_credit_code=unified_social_credit_code,
        legal_representative=legal_representative,
        contact_phone=contact_phone,
        contact_email=contact_email,
        address=address
    )
    
    # 获取企业列表
    companies = company_service.get_companies(
        db=db,
        search_params=search_params,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc,
        current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(companies)
    
    return {
        "companies": companies,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.post("/", response_model=Company)
async def create_company(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_in: CompanyCreate
) -> Any:
    """创建新企业"""
    # 检查权限
    if not has_permission(current_user, "company:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建企业的权限"
        )
    
    # 创建企业
    company = company_service.create_company(
        db=db, company_in=company_in, current_user=current_user
    )
    
    return company


@router.get("/{company_id}", response_model=CompanyWithDetails)
async def get_company(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取单个企业详情"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看企业的权限"
        )
    
    # 获取企业详情
    company = company_service.get_company(
        db=db, company_id=company_id, current_user=current_user
    )
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在"
        )
    
    return company


@router.put("/{company_id}", response_model=Company)
async def update_company(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_in: CompanyUpdate
) -> Any:
    """更新企业信息"""
    # 检查权限
    if not has_permission(current_user, "company:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改企业的权限"
        )
    
    # 更新企业
    company = company_service.update_company(
        db=db, company_id=company_id, company_in=company_in, current_user=current_user
    )
    
    return company


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除企业"""
    # 检查权限
    if not has_permission(current_user, "company:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除企业的权限"
        )
    
    # 删除企业
    company = company_service.delete_company(
        db=db, company_id=company_id, current_user=current_user
    )
    
    return {"message": f"企业 {company_id} 已成功删除"}


# 企业搜索API端点
@router.get("/search", response_model=List[Company])
async def search_companies(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    industry: Optional[str] = Query(None, description="按行业筛选"),
    unified_social_credit_code: Optional[str] = Query(None, description="按统一社会信用代码筛选"),
    legal_representative: Optional[str] = Query(None, description="按法定代表人筛选"),
    contact_phone: Optional[str] = Query(None, description="按联系电话筛选"),
    contact_email: Optional[str] = Query(None, description="按联系邮箱筛选"),
    address: Optional[str] = Query(None, description="按地址筛选"),
    created_after: Optional[str] = Query(None, description="创建时间起始"),
    created_before: Optional[str] = Query(None, description="创建时间结束"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """搜索企业"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有搜索企业的权限"
        )
    
    # 构建搜索参数
    search_params = CompanySearch(
        keyword=keyword,
        industry=industry,
        unified_social_credit_code=unified_social_credit_code,
        legal_representative=legal_representative,
        contact_phone=contact_phone,
        contact_email=contact_email,
        address=address
    )
    
    # 搜索企业
    companies = company_service.search_companies(
        db=db, search_params=search_params, skip=skip, limit=limit, current_user=current_user
    )
    
    return companies


@router.get("/by-verification-status", response_model=List[Company])
async def get_companies_by_verification_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    verification_status: str = Query(..., description="验证状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """按验证状态获取企业"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看企业的权限"
        )
    
    # 按验证状态获取企业
    companies = company_service.get_companies_by_verification_status(
        db=db, verification_status=verification_status, skip=skip, limit=limit, current_user=current_user
    )
    
    return companies


# 企业统计API端点
@router.get("/statistics", response_model=CompanyStatistics)
async def get_company_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取企业统计信息"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看企业统计的权限"
        )
    
    # 获取企业统计信息
    statistics = company_service.get_company_statistics(
        db=db, current_user=current_user
    )
    
    return statistics


@router.get("/{company_id}/project-count", response_model=Dict[str, int])
async def get_company_project_count(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取企业项目数量"""
    # 检查权限
    if not has_permission(current_user, "company:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看企业项目数量的权限"
        )
    
    # 获取企业项目数量
    count = company_service.get_company_project_count(
        db=db, company_id=company_id, current_user=current_user
    )
    
    return {"company_id": company_id, "project_count": count}


# 企业验证管理API端点
@router.post("/{company_id}/verify", response_model=Dict[str, Any])
async def verify_company(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    verification_data: Dict[str, Any]
) -> Any:
    """验证企业"""
    # 检查权限
    if not has_permission(current_user, "company:verify"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有验证企业的权限"
        )
    
    # 验证企业
    result = company_service.verify_company(
        db=db, company_id=company_id, verification_data=verification_data, current_user=current_user
    )
    
    return result


@router.put("/{company_id}/verification-status", response_model=Dict[str, Any])
async def update_verification_status(
    company_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    verification_status: str
) -> Any:
    """更新验证状态"""
    # 检查权限
    if not has_permission(current_user, "company:verify"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有更新企业验证状态的权限"
        )
    
    # 更新验证状态
    result = company_service.update_verification_status(
        db=db, company_id=company_id, verification_status=verification_status, current_user=current_user
    )
    
    return result