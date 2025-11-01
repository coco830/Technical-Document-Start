"""
文档导出相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ExportFormat(str, Enum):
    """导出格式枚举"""
    PDF = "pdf"
    WORD = "word"
    HTML = "html"
    MARKDOWN = "markdown"


class ExportStatus(str, Enum):
    """导出状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentExportBase(BaseModel):
    """文档导出基础模式"""
    format: ExportFormat = Field(..., description="导出格式")


class DocumentExportCreate(DocumentExportBase):
    """创建文档导出记录模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    user_id: int = Field(..., gt=0, description="用户ID")
    export_options: Optional[Dict[str, Any]] = Field(None, description="导出选项")


class DocumentExportUpdate(BaseModel):
    """更新文档导出记录模式"""
    file_url: Optional[str] = Field(None, description="文件URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小(字节)")
    status: Optional[ExportStatus] = Field(None, description="导出状态")
    error_message: Optional[str] = Field(None, description="错误信息")


class DocumentExport(DocumentExportBase):
    """文档导出记录完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="导出记录ID")
    document_id: int = Field(..., description="文档ID")
    user_id: int = Field(..., description="用户ID")
    file_url: Optional[str] = Field(None, description="文件URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    created_at: datetime = Field(..., description="创建时间")


class DocumentExportWithDetails(DocumentExport):
    """包含详细信息的文档导出记录模式"""
    document_title: Optional[str] = Field(None, description="文档标题")
    user_name: Optional[str] = Field(None, description="用户姓名")
    status: Optional[ExportStatus] = Field(None, description="导出状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    download_url: Optional[str] = Field(None, description="下载链接")


class DocumentExportRequest(BaseModel):
    """文档导出请求模式"""
    format: ExportFormat = Field(..., description="导出格式")
    include_metadata: bool = Field(True, description="是否包含元数据")
    include_versions: bool = Field(False, description="是否包含版本历史")
    watermark: Optional[str] = Field(None, description="水印文本")
    page_size: Optional[str] = Field("A4", description="页面大小")
    margin: Optional[str] = Field("normal", description="页边距")
    header: Optional[str] = Field(None, description="页眉")
    footer: Optional[str] = Field(None, description="页脚")
    table_of_contents: bool = Field(False, description="是否生成目录")


class DocumentExportResponse(BaseModel):
    """文档导出响应模式"""
    export_id: int = Field(..., description="导出记录ID")
    status: ExportStatus = Field(..., description="导出状态")
    message: Optional[str] = Field(None, description="状态消息")
    download_url: Optional[str] = Field(None, description="下载链接")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    estimated_time: Optional[int] = Field(None, description="预计完成时间(秒)")


class DocumentExportList(BaseModel):
    """文档导出记录列表响应模式"""
    exports: List[DocumentExportWithDetails] = Field(..., description="导出记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class ExportOptions(BaseModel):
    """导出选项模式"""
    # PDF选项
    pdf_page_size: str = Field("A4", description="PDF页面大小")
    pdf_orientation: str = Field("portrait", description="PDF页面方向")
    pdf_margin_top: float = Field(2.54, description="PDF上边距(cm)")
    pdf_margin_bottom: float = Field(2.54, description="PDF下边距(cm)")
    pdf_margin_left: float = Field(1.91, description="PDF左边距(cm)")
    pdf_margin_right: float = Field(1.91, description="PDF右边距(cm)")
    pdf_font_size: int = Field(12, description="PDF字体大小")
    pdf_line_height: float = Field(1.5, description="PDF行高")
    
    # Word选项
    word_page_size: str = Field("A4", description="Word页面大小")
    word_orientation: str = Field("portrait", description="Word页面方向")
    word_margin_top: float = Field(2.54, description="Word上边距(cm)")
    word_margin_bottom: float = Field(2.54, description="Word下边距(cm)")
    word_margin_left: float = Field(1.91, description="Word左边距(cm)")
    word_margin_right: float = Field(1.91, description="Word右边距(cm)")
    word_font_size: int = Field(12, description="Word字体大小")
    word_line_height: float = Field(1.5, description="Word行高")
    
    # HTML选项
    html_css_style: str = Field("default", description="HTML样式")
    html_include_toc: bool = Field(False, description="HTML是否包含目录")
    html_responsive: bool = Field(True, description="HTML是否响应式")
    
    # 通用选项
    include_header: bool = Field(False, description="是否包含页眉")
    include_footer: bool = Field(False, description="是否包含页脚")
    include_page_numbers: bool = Field(True, description="是否包含页码")
    include_watermark: bool = Field(False, description="是否包含水印")
    watermark_text: Optional[str] = Field(None, description="水印文本")
    watermark_opacity: float = Field(0.1, ge=0.0, le=1.0, description="水印透明度")


class ExportTemplate(BaseModel):
    """导出模板模式"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    format: ExportFormat = Field(..., description="导出格式")
    options: ExportOptions = Field(..., description="导出选项")
    is_default: bool = Field(False, description="是否为默认模板")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ExportTemplateCreate(BaseModel):
    """创建导出模板模式"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    format: ExportFormat = Field(..., description="导出格式")
    options: ExportOptions = Field(..., description="导出选项")
    is_default: bool = Field(False, description="是否为默认模板")


class ExportTemplateUpdate(BaseModel):
    """更新导出模板模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    options: Optional[ExportOptions] = Field(None, description="导出选项")
    is_default: Optional[bool] = Field(None, description="是否为默认模板")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ExportTemplateList(BaseModel):
    """导出模板列表响应模式"""
    templates: List[ExportTemplate] = Field(..., description="模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class ExportStatistics(BaseModel):
    """导出统计模式"""
    total_exports: int = Field(..., description="总导出次数")
    successful_exports: int = Field(..., description="成功导出次数")
    failed_exports: int = Field(..., description="失败导出次数")
    exports_by_format: Dict[str, int] = Field(..., description="按格式统计导出次数")
    exports_by_user: Dict[str, int] = Field(..., description="按用户统计导出次数")
    average_file_size: Optional[float] = Field(None, description="平均文件大小(KB)")
    total_file_size: Optional[int] = Field(None, description="总文件大小(KB)")
    most_exported_documents: List[Dict[str, Any]] = Field(..., description="最常导出的文档")
    storage_stats: Optional[Dict[str, Any]] = Field(None, description="存储统计信息")