from fastapi import APIRouter, HTTPException, status, Depends, Query, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.project import Project
from app.models.comment import Comment
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentAutoSave,
    MessageResponse
)
from app.utils.auth import get_current_user
from app.utils.file_validator import validate_uploaded_file, scan_file_security, FileValidationError
from app.utils.pagination import PaginationParams, optimize_offset_pagination, search_optimized_pagination
import math
import os
import uuid
import shutil
import logging
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

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
    # 构建基础查询，使用eager loading避免N+1问题
    query = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user)      # 预加载关联的用户
    ).filter(Document.user_id == current_user.id)

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

    # 创建分页参数
    pagination = PaginationParams(page=page, page_size=page_size)
    
    # 使用优化的分页查询
    if search:
        # 搜索优化的分页
        result = search_optimized_pagination(
            query=query,
            search_term=search,
            search_fields=['title'],
            pagination=pagination,
            db=db
        )
    else:
        # 普通优化的分页
        query = query.order_by(Document.updated_at.desc())
        result = optimize_offset_pagination(query, pagination, db)

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages
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
    document = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user),     # 预加载关联的用户
        joinedload(Document.comments)  # 预加载关联的评论
    ).filter(
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
    document = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user)      # 预加载关联的用户
    ).filter(
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
    document = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user)      # 预加载关联的用户
    ).filter(
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
    document = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user)      # 预加载关联的用户
    ).filter(
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
    template = db.query(Document).options(
        joinedload(Document.project),  # 预加载关联的项目
        joinedload(Document.user)      # 预加载关联的用户
    ).filter(
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

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传图片到服务器

    - **file**: 图片文件（支持 jpg, jpeg, png, gif, webp）
    - 返回图片访问URL
    """
    # 记录上传尝试
    logger.info(f"用户 {current_user.id} 尝试上传文件: {file.filename}, 声明类型: {file.content_type}")
    
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 使用文件验证器进行安全验证
        validation_result = validate_uploaded_file(
            file_content=contents,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # 验证是否为图片类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"只允许上传图片文件，当前类型: {file.content_type}"
            )
        
        # 扫描文件安全性
        if not scan_file_security(contents):
            logger.warning(f"检测到用户 {current_user.id} 上传的文件 {file.filename} 包含可疑内容")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件包含不安全内容，上传被拒绝"
            )
        
        # 生成唯一文件名，使用验证后的扩展名
        file_extension = validation_result['extension']
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 确保上传目录存在
        upload_dir = Path("uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = upload_dir / unique_filename

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            # 记录成功上传
            logger.info(f"用户 {current_user.id} 成功上传文件: {unique_filename}, 大小: {len(contents)} bytes")
            
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}, 用户: {current_user.id}, 文件: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件保存失败: {str(e)}"
            )

        # 返回图片URL
        image_url = f"/uploads/images/{unique_filename}"

        return {
            "url": image_url,
            "filename": unique_filename,
            "size": len(contents),
            "content_type": validation_result['content_type'],
            "description": validation_result['description']
        }
        
    except FileValidationError as e:
        logger.warning(f"文件验证失败: {str(e)}, 用户: {current_user.id}, 文件: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"文件上传过程中发生未知错误: {str(e)}, 用户: {current_user.id}, 文件: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传过程中发生错误，请稍后重试"
        )
