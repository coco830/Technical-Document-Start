from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    selection_text: Optional[str] = Field(None, max_length=500, description="批注的选中文本")
    position_start: Optional[int] = Field(None, ge=0, description="批注位置开始")
    position_end: Optional[int] = Field(None, ge=0, description="批注位置结束")
    parent_id: Optional[int] = Field(None, description="回复的父评论ID")

class CommentUpdate(BaseModel):
    """更新评论请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")

class CommentResponse(BaseModel):
    """评论响应"""
    id: int
    document_id: int
    user_id: int
    content: str
    selection_text: Optional[str]
    position_start: Optional[int]
    position_end: Optional[int]
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class CommentWithReplies(CommentResponse):
    """带回复的评论响应"""
    replies: List[CommentResponse] = []

class CommentListResponse(BaseModel):
    """评论列表响应"""
    comments: List[CommentWithReplies]
    total: int

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    detail: Optional[str] = None
