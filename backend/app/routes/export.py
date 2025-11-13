"""
文档导出路由
提供 PDF 和 Word 文档导出功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.utils.auth import get_current_user
from app.export.pdf_export import PDFExporter
from app.export.docx_export import DocxExporter

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    """单个文档导出请求"""
    document_id: int
    format: str  # pdf 或 docx
    include_metadata: bool = True


class BatchExportRequest(BaseModel):
    """批量导出请求"""
    document_ids: List[int]
    format: str  # pdf 或 docx
    custom_filename: Optional[str] = None


class ExportHistoryItem(BaseModel):
    """导出历史项"""
    id: int
    project_id: int
    project_title: str
    format: str
    created_at: str
    file_url: Optional[str] = None


@router.post("/document/{document_id}")
async def export_document(
    document_id: int,
    format: str = Query(..., regex="^(pdf|docx)$", description="导出格式: pdf 或 docx"),
    include_metadata: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    导出单个文档

    Args:
        document_id: 文档 ID
        format: 导出格式 (pdf 或 docx)
        include_metadata: 是否包含元数据
        db: 数据库会话
        current_user: 当前用户

    Returns:
        文件下载响应
    """
    # 查询文档
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user["id"]
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="文档不存在或无权访问")

    # 准备元数据
    metadata = None
    if include_metadata:
        metadata = {
            'author': current_user.get('username', 'Unknown'),
            'created_at': document.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'version': document.version,
        }

    try:
        # 根据格式选择导出器
        if format == "pdf":
            exporter = PDFExporter()
            result = exporter.export(
                title=document.title,
                content=document.content or "",
                content_type=document.content_type,
                metadata=metadata
            )
        else:  # docx
            exporter = DocxExporter()
            result = exporter.export(
                title=document.title,
                content=document.content or "",
                content_type=document.content_type,
                metadata=metadata
            )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['message'])

        # 返回文件
        filepath = result['filepath']
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="导出文件不存在")

        return FileResponse(
            path=filepath,
            filename=result['filename'],
            media_type='application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/batch")
async def export_batch(
    request: BatchExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    批量导出文档

    Args:
        request: 批量导出请求
        db: 数据库会话
        current_user: 当前用户

    Returns:
        文件下载响应
    """
    # 验证格式
    if request.format not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="格式必须是 pdf 或 docx")

    # 查询文档
    documents = db.query(Document).filter(
        Document.id.in_(request.document_ids),
        Document.user_id == current_user["id"]
    ).all()

    if not documents:
        raise HTTPException(status_code=404, detail="未找到可导出的文档")

    if len(documents) != len(request.document_ids):
        raise HTTPException(status_code=403, detail="部分文档不存在或无权访问")

    # 准备文档数据
    doc_data_list = []
    for doc in documents:
        doc_data_list.append({
            'title': doc.title,
            'content': doc.content or "",
            'content_type': doc.content_type
        })

    try:
        # 根据格式选择导出器
        if request.format == "pdf":
            exporter = PDFExporter()
            result = exporter.export_batch(
                documents=doc_data_list,
                output_filename=request.custom_filename
            )
        else:  # docx
            exporter = DocxExporter()
            result = exporter.export_batch(
                documents=doc_data_list,
                output_filename=request.custom_filename
            )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['message'])

        # 返回文件
        filepath = result['filepath']
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="导出文件不存在")

        return FileResponse(
            path=filepath,
            filename=result['filename'],
            media_type='application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导出失败: {str(e)}")


@router.get("/history/", response_model=List[ExportHistoryItem])
async def get_export_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取导出历史记录

    Returns:
        导出历史记录列表
    """
    try:
        # 查询用户的文档
        documents = db.query(Document).filter(
            Document.user_id == current_user.id
        ).order_by(Document.updated_at.desc()).all()

        # 模拟导出历史数据（实际应该有专门的导出记录表）
        export_history = []
        for i, doc in enumerate(documents[:10]):  # 限制最近10条
            # 模拟不同的导出格式
            formats = ['pdf', 'word'] if i % 2 == 0 else ['pdf']
            for fmt in formats:
                history_item = ExportHistoryItem(
                    id=len(export_history) + 1,
                    project_id=doc.id,
                    project_title=doc.title,
                    format=fmt,
                    created_at=doc.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    file_url=f"/exports/{doc.id}.{fmt}" if i < 3 else None  # 模拟文件URL
                )
                export_history.append(history_item)

        return export_history

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出历史失败: {str(e)}"
        )


@router.get("/formats")
async def get_supported_formats():
    """
    获取支持的导出格式

    Returns:
        支持的格式列表
    """
    return {
        'formats': [
            {
                'id': 'pdf',
                'name': 'PDF 文档',
                'description': '便携式文档格式，适合打印和分享',
                'extension': '.pdf',
                'mime_type': 'application/pdf'
            },
            {
                'id': 'docx',
                'name': 'Word 文档',
                'description': 'Microsoft Word 格式，可编辑',
                'extension': '.docx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        ]
    }
