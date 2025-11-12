from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.comment import Comment
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
    CommentWithReplies,
    MessageResponse
)
from app.utils.auth import get_current_user
import logging

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["评论管理"])

@router.get("/{document_id}/comments", response_model=CommentListResponse)
async def get_comments(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取文档的所有评论

    - **document_id**: 文档ID
    - 返回评论列表，包含回复（树形结构）
    """
    # 验证文档是否存在且用户有权访问
    document = db.query(Document).options(
        joinedload(Document.user)  # 预加载关联的用户
    ).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    # 获取所有根评论（没有父评论的评论），使用eager loading避免N+1问题
    root_comments = db.query(Comment).options(
        joinedload(Comment.user)  # 预加载关联的用户
    ).filter(
        Comment.document_id == document_id,
        Comment.parent_id == None
    ).order_by(Comment.created_at.desc()).all()

    # 获取所有回复，使用eager loading避免N+1问题
    all_replies = db.query(Comment).options(
        joinedload(Comment.user)  # 预加载关联的用户
    ).filter(
        Comment.document_id == document_id,
        Comment.parent_id != None
    ).order_by(Comment.created_at.asc()).all()

    # 构建评论树
    comments_with_replies = []
    for comment in root_comments:
        comment_dict = CommentResponse.model_validate(comment).model_dump()
        comment_dict['replies'] = [
            CommentResponse.model_validate(reply)
            for reply in all_replies
            if reply.parent_id == comment.id
        ]
        comments_with_replies.append(CommentWithReplies(**comment_dict))

    total = len(root_comments)
    
    # 记录查询性能
    logger.info(f"用户 {current_user.id} 查询文档 {document_id} 的评论: 根评论数={total}, 回复数={len(all_replies)}")

    return CommentListResponse(
        comments=comments_with_replies,
        total=total
    )

@router.post("/{document_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    document_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建评论或批注

    - **document_id**: 文档ID
    - **content**: 评论内容
    - **selection_text**: 批注的选中文本（可选）
    - **position_start**: 批注位置开始（可选）
    - **position_end**: 批注位置结束（可选）
    - **parent_id**: 回复的父评论ID（可选）
    """
    # 验证文档是否存在且用户有权访问
    document = db.query(Document).options(
        joinedload(Document.user)  # 预加载关联的用户
    ).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在或无权访问"
        )

    # 如果是回复，验证父评论是否存在
    if comment_data.parent_id:
        parent_comment = db.query(Comment).options(
            joinedload(Comment.user)  # 预加载关联的用户
        ).filter(
            Comment.id == comment_data.parent_id,
            Comment.document_id == document_id
        ).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )

    # 创建评论
    new_comment = Comment(
        document_id=document_id,
        user_id=current_user.id,
        content=comment_data.content,
        selection_text=comment_data.selection_text,
        position_start=comment_data.position_start,
        position_end=comment_data.position_end,
        parent_id=comment_data.parent_id
    )

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论创建失败：{str(e)}"
        )

    return CommentResponse.model_validate(new_comment)

@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新评论内容

    - **comment_id**: 评论ID
    - **content**: 新的评论内容
    """
    # 查找评论
    comment = db.query(Comment).options(
        joinedload(Comment.user),      # 预加载关联的用户
        joinedload(Comment.document)   # 预加载关联的文档
    ).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权修改"
        )

    # 更新评论
    comment.content = comment_data.content

    try:
        db.commit()
        db.refresh(comment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论更新失败：{str(e)}"
        )

    return CommentResponse.model_validate(comment)

@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除评论

    - **comment_id**: 评论ID
    - 删除评论时，会同时删除所有回复
    """
    # 查找评论
    comment = db.query(Comment).options(
        joinedload(Comment.user),      # 预加载关联的用户
        joinedload(Comment.document)   # 预加载关联的文档
    ).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权删除"
        )

    # 删除所有回复
    db.query(Comment).filter(Comment.parent_id == comment_id).delete()

    # 删除评论
    try:
        db.delete(comment)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评论删除失败：{str(e)}"
        )

    return MessageResponse(
        message="评论删除成功",
        detail=f"评论 {comment_id} 及其所有回复已被删除"
    )
