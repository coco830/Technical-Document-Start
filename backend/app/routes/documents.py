from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.project import Project
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentAutoSave,
    MessageResponse
)
from app.utils.auth import get_current_user
import math

router = APIRouter(prefix="/api/documents", tags=["文档管理"])

@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, max_length=100, description="搜索关键词"),
    project_id: Optional[int] = Query(None, description="按项目ID过滤"),
    is_template: Optional[int] = Query(None, description="过滤模板"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的文档列表（分页）

    - **page**: 页码（从1开始）
    - **page_size**: 每页显示数量（1-100）
    - **search**: 可选的搜索关键词（在标题中搜索）
    - **project_id**: 可选的项目ID过滤
    - **is_template**: 可选的模板过滤（0: 普通文档, 1: 模板）
    """
    # 构建基础查询
    query = db.query(Document).filter(Document.user_id == current_user.id)

    # 项目过滤
    if project_id is not None:
        # 验证项目是否属于当前用户
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权访问"
            )
        query = query.filter(Document.project_id == project_id)

    # 模板过滤
    if is_template is not None:
        if is_template not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="is_template 必须是 0 或 1"
            )
        query = query.filter(Document.is_template == is_template)

    # 搜索功能
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))

    # 获取总数
    total = query.count()

    # 计算总页数
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # 分页查询（按更新时间倒序）
    documents = query.order_by(Document.updated_at.desc())\
                    .offset((page - 1) * page_size)\
                    .limit(page_size)\
                    .all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新文档

    - **title**: 文档标题（必填，1-200字符）
    - **content**: 文档内容（可选）
    - **content_type**: 内容类型（html/json/markdown，默认：html）
    - **project_id**: 所属项目ID（可选）
    - **is_template**: 是否为模板（0或1，默认：0）
    - **metadata**: 元数据（可选）
    """
    # 如果指定了项目，验证项目是否属于当前用户
    if document_data.project_id is not None:
        project = db.query(Project).filter(
            Project.id == document_data.project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权访问"
            )

    # 创建文档
    new_document = Document(
        title=document_data.title,
        content=document_data.content,
        content_type=document_data.content_type,
        project_id=document_data.project_id,
        user_id=current_user.id,
        is_template=document_data.is_template,
        doc_metadata=document_data.doc_metadata
    )

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档创建失败：{str(e)}"
        )

    return DocumentResponse.model_validate(new_document)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个文档详情

    - **document_id**: 文档ID
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    return DocumentResponse.model_validate(document)

@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新文档信息

    - **document_id**: 文档ID
    - **title**: 文档标题（可选）
    - **content**: 文档内容（可选）
    - **content_type**: 内容类型（可选）
    - **project_id**: 所属项目ID（可选）
    - **is_template**: 是否为模板（可选）
    - **metadata**: 元数据（可选）
    """
    # 查找文档
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    # 更新字段
    update_data = document_data.model_dump(exclude_unset=True)

    if not update_data:
        return DocumentResponse.model_validate(document)

    # 如果更新了项目ID，验证项目是否属于当前用户
    if 'project_id' in update_data and update_data['project_id'] is not None:
        project = db.query(Project).filter(
            Project.id == update_data['project_id'],
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权访问"
            )

    for field, value in update_data.items():
        setattr(document, field, value)

    # 更新版本号
    if 'content' in update_data:
        document.version += 1

    try:
        db.commit()
        db.refresh(document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档更新失败：{str(e)}"
        )

    return DocumentResponse.model_validate(document)

@router.post("/{document_id}/autosave", response_model=MessageResponse)
async def autosave_document(
    document_id: int,
    autosave_data: DocumentAutoSave,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    自动保存文档内容

    - **document_id**: 文档ID
    - **content**: 文档内容
    - **version**: 当前版本号（用于乐观锁）
    """
    # 查找文档
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    # 版本控制：防止覆盖其他用户的修改
    if document.version != autosave_data.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"文档已被修改，当前版本：{document.version}，请求版本：{autosave_data.version}"
        )

    # 更新内容和版本
    document.content = autosave_data.content
    document.version += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"自动保存失败：{str(e)}"
        )

    return MessageResponse(
        message="自动保存成功",
        detail=f"文档版本已更新至 {document.version}"
    )

@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除文档

    - **document_id**: 文档ID
    """
    # 查找文档
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档删除失败：{str(e)}"
        )

    return MessageResponse(
        message="文档删除成功",
        detail=f"文档「{document.title}」已被删除"
    )

@router.post("/from-template/{template_id}", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_from_template(
    template_id: int,
    title: str = Query(..., description="新文档标题"),
    project_id: Optional[int] = Query(None, description="所属项目ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从模板创建文档

    - **template_id**: 模板文档ID
    - **title**: 新文档标题
    - **project_id**: 所属项目ID（可选）
    """
    # 查找模板
    template = db.query(Document).filter(
        Document.id == template_id,
        Document.user_id == current_user.id,
        Document.is_template == 1
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权访问"
        )

    # 如果指定了项目，验证项目是否属于当前用户
    if project_id is not None:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在或无权访问"
            )

    # 从模板创建新文档
    new_document = Document(
        title=title,
        content=template.content,
        content_type=template.content_type,
        project_id=project_id,
        user_id=current_user.id,
        is_template=0,
        doc_metadata=template.doc_metadata
    )

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"从模板创建文档失败：{str(e)}"
        )

    return DocumentResponse.model_validate(new_document)
