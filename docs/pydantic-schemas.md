# Pydantic API模式定义文档

本文档描述了悦恩人机共写平台的完整Pydantic API模式定义，包括所有实体的基础模式、创建模式、更新模式和响应模式。

## 目录

1. [文档模式](#文档模式)
2. [AI生成模式](#ai生成模式)
3. [文档导出模式](#文档导出模式)
4. [用户模式](#用户模式)
5. [项目模式](#项目模式)
6. [企业模式](#企业模式)

## 文档模式

### 文档基础模式 (DocumentBase)

```python
class DocumentBase(BaseModel):
    """文档基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    format: DocumentFormat = Field(DocumentFormat.MARKDOWN, description="文档格式")
    status: DocumentStatus = Field(DocumentStatus.DRAFT, description="文档状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
```

### 文档格式枚举 (DocumentFormat)

```python
class DocumentFormat(str, Enum):
    """文档格式枚举"""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
```

### 文档状态枚举 (DocumentStatus)

```python
class DocumentStatus(str, Enum):
    """文档状态枚举"""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    PUBLISHED = "published"
```

### 文档创建模式 (DocumentCreate)

继承自DocumentBase，添加了项目ID字段：

```python
class DocumentCreate(DocumentBase):
    """创建文档模式"""
    project_id: int = Field(..., gt=0, description="所属项目ID")
```

### 文档更新模式 (DocumentUpdate)

```python
class DocumentUpdate(BaseModel):
    """更新文档模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    format: Optional[DocumentFormat] = Field(None, description="文档格式")
    status: Optional[DocumentStatus] = Field(None, description="文档状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
```

### 文档完整模式 (Document)

```python
class Document(DocumentBase):
    """文档完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="文档ID")
    project_id: int = Field(..., description="所属项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
```

### 文档详细信息模式 (DocumentWithDetails)

继承自Document，添加了关联信息：

```python
class DocumentWithDetails(Document):
    """包含详细信息的文档模式"""
    project_name: Optional[str] = Field(None, description="项目名称")
    versions_count: Optional[int] = Field(0, description="版本数量")
    ai_generations_count: Optional[int] = Field(0, description="AI生成次数")
    exports_count: Optional[int] = Field(0, description="导出次数")
```

### 文档版本模式

#### 文档版本基础模式 (DocumentVersionBase)

```python
class DocumentVersionBase(BaseModel):
    """文档版本基础模式"""
    version_number: int = Field(..., gt=0, description="版本号")
    content: str = Field(..., description="版本内容")
    changes_summary: Optional[Dict[str, Any]] = Field(None, description="变更摘要")
```

#### 文档版本创建模式 (DocumentVersionCreate)

```python
class DocumentVersionCreate(DocumentVersionBase):
    """创建文档版本模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    created_by: int = Field(..., gt=0, description="创建者ID")
```

#### 文档版本完整模式 (DocumentVersion)

```python
class DocumentVersion(DocumentVersionBase):
    """文档版本完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="版本ID")
    document_id: int = Field(..., description="文档ID")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
```

### 列表响应模式

#### 文档列表 (DocumentList)

```python
class DocumentList(BaseModel):
    """文档列表响应模式"""
    documents: List[DocumentWithDetails] = Field(..., description="文档列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

#### 文档版本列表 (DocumentVersionList)

```python
class DocumentVersionList(BaseModel):
    """文档版本列表响应模式"""
    versions: List[DocumentVersionWithDetails] = Field(..., description="版本列表")
    total: int = Field(..., description="总数量")
    document_id: int = Field(..., description="文档ID")
```

## AI生成模式

### AI生成状态枚举 (AIGenerationStatus)

```python
class AIGenerationStatus(str, Enum):
    """AI生成状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### AI生成基础模式 (AIGenerationBase)

```python
class AIGenerationBase(BaseModel):
    """AI生成基础模式"""
    prompt: str = Field(..., min_length=1, description="生成提示词")
    generation_config: Optional[Dict[str, Any]] = Field(None, description="生成配置")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
```

### AI生成创建模式 (AIGenerationCreate)

```python
class AIGenerationCreate(AIGenerationBase):
    """创建AI生成记录模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    user_id: int = Field(..., gt=0, description="用户ID")
```

### AI生成更新模式 (AIGenerationUpdate)

```python
class AIGenerationUpdate(BaseModel):
    """更新AI生成记录模式"""
    status: Optional[AIGenerationStatus] = Field(None, description="生成状态")
    generated_content: Optional[str] = Field(None, description="生成内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
```

### AI生成完整模式 (AIGeneration)

```python
class AIGeneration(AIGenerationBase):
    """AI生成记录完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="生成记录ID")
    document_id: int = Field(..., description="文档ID")
    user_id: int = Field(..., description="用户ID")
    generated_content: Optional[str] = Field(None, description="生成内容")
    status: AIGenerationStatus = Field(..., description="生成状态")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
```

### AI生成请求和响应模式

#### AI生成请求模式 (AIGenerationRequest)

```python
class AIGenerationRequest(BaseModel):
    """AI生成请求模式"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="生成提示词")
    context: Optional[str] = Field(None, description="上下文内容")
    generation_config: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        },
        description="生成配置参数"
    )
    section: Optional[str] = Field(None, description="生成文档的章节")
```

#### AI生成响应模式 (AIGenerationResponse)

```python
class AIGenerationResponse(BaseModel):
    """AI生成响应模式"""
    id: int = Field(..., description="生成记录ID")
    status: AIGenerationStatus = Field(..., description="生成状态")
    generated_content: Optional[str] = Field(None, description="生成内容")
    message: Optional[str] = Field(None, description="状态消息")
    processing_time: Optional[int] = Field(None, description="处理时间(秒)")
```

### AI生成配置模式 (AIGenerationConfig)

```python
class AIGenerationConfig(BaseModel):
    """AI生成配置模式"""
    model: str = Field("gpt-3.5-turbo", description="使用的模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制随机性")
    max_tokens: int = Field(2000, gt=0, le=4000, description="最大生成令牌数")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="核采样参数")
    frequency_penalty: float = Field(0.1, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: float = Field(0.1, ge=-2.0, le=2.0, description="存在惩罚")
    stop_sequences: Optional[List[str]] = Field(None, description="停止序列")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
```

### AI生成模板模式

#### AI生成模板基础模式 (AIGenerationTemplate)

```python
class AIGenerationTemplate(BaseModel):
    """AI生成模板模式"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    prompt_template: str = Field(..., min_length=1, description="提示词模板")
    config: AIGenerationConfig = Field(..., description="默认生成配置")
    category: Optional[str] = Field(None, description="模板分类")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
```

#### AI生成模板创建模式 (AIGenerationTemplateCreate)

```python
class AIGenerationTemplateCreate(BaseModel):
    """创建AI生成模板模式"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    prompt_template: str = Field(..., min_length=1, description="提示词模板")
    config: AIGenerationConfig = Field(..., description="默认生成配置")
    category: Optional[str] = Field(None, description="模板分类")
```

### 列表响应模式

#### AI生成记录列表 (AIGenerationList)

```python
class AIGenerationList(BaseModel):
    """AI生成记录列表响应模式"""
    generations: List[AIGenerationWithDetails] = Field(..., description="生成记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

## 文档导出模式

### 导出格式枚举 (ExportFormat)

```python
class ExportFormat(str, Enum):
    """导出格式枚举"""
    PDF = "pdf"
    WORD = "word"
    HTML = "html"
    MARKDOWN = "markdown"
```

### 导出状态枚举 (ExportStatus)

```python
class ExportStatus(str, Enum):
    """导出状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 文档导出基础模式 (DocumentExportBase)

```python
class DocumentExportBase(BaseModel):
    """文档导出基础模式"""
    format: ExportFormat = Field(..., description="导出格式")
```

### 文档导出创建模式 (DocumentExportCreate)

```python
class DocumentExportCreate(DocumentExportBase):
    """创建文档导出记录模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    user_id: int = Field(..., gt=0, description="用户ID")
    export_options: Optional[Dict[str, Any]] = Field(None, description="导出选项")
```

### 文档导出更新模式 (DocumentExportUpdate)

```python
class DocumentExportUpdate(BaseModel):
    """更新文档导出记录模式"""
    file_url: Optional[str] = Field(None, description="文件URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小(字节)")
    status: Optional[ExportStatus] = Field(None, description="导出状态")
    error_message: Optional[str] = Field(None, description="错误信息")
```

### 文档导出完整模式 (DocumentExport)

```python
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
```

### 文档导出请求和响应模式

#### 文档导出请求模式 (DocumentExportRequest)

```python
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
```

#### 文档导出响应模式 (DocumentExportResponse)

```python
class DocumentExportResponse(BaseModel):
    """文档导出响应模式"""
    export_id: int = Field(..., description="导出记录ID")
    status: ExportStatus = Field(..., description="导出状态")
    message: Optional[str] = Field(None, description="状态消息")
    download_url: Optional[str] = Field(None, description="下载链接")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    estimated_time: Optional[int] = Field(None, description="预计完成时间(秒)")
```

### 导出选项模式 (ExportOptions)

```python
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
```

### 导出模板模式

#### 导出模板基础模式 (ExportTemplate)

```python
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
```

### 列表响应模式

#### 文档导出记录列表 (DocumentExportList)

```python
class DocumentExportList(BaseModel):
    """文档导出记录列表响应模式"""
    exports: List[DocumentExportWithDetails] = Field(..., description="导出记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

## 用户模式

### 用户角色枚举 (UserRole)

```python
class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
```

### 用户基础模式 (UserBase)

```python
class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    role: UserRole = Field(UserRole.USER, description="用户角色")
    is_active: bool = Field(True, description="账户是否激活")
    is_verified: bool = Field(False, description="邮箱是否验证")
```

### 用户创建模式 (UserCreate)

```python
class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=8, max_length=128, description="密码")
```

### 用户更新模式 (UserUpdate)

```python
class UserUpdate(BaseModel):
    """更新用户模式"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="账户是否激活")
    is_verified: Optional[bool] = Field(None, description="邮箱是否验证")
```

### 用户密码更新模式 (UserPasswordUpdate)

```python
class UserPasswordUpdate(BaseModel):
    """更新用户密码模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
```

### 用户完整模式 (User)

```python
class User(UserBase):
    """用户完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
```

### 用户公开信息模式 (UserPublic)

```python
class UserPublic(BaseModel):
    """用户公开信息模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    full_name: Optional[str] = Field(None, description="用户全名")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    created_at: datetime = Field(..., description="创建时间")
```

### 用户认证模式

#### 用户登录模式 (UserLogin)

```python
class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="是否记住登录状态")
```

#### 用户注册模式 (UserRegister)

```python
class UserRegister(BaseModel):
    """用户注册模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
```

#### 用户登录响应模式 (UserLoginResponse)

```python
class UserLoginResponse(BaseModel):
    """用户登录响应模式"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间(秒)")
    user: UserPublic = Field(..., description="用户信息")
```

### 用户会话模式

#### 用户会话基础模式 (UserSessionBase)

```python
class UserSessionBase(BaseModel):
    """用户会话基础模式"""
    device_info: Optional[str] = Field(None, description="设备信息")
    ip_address: Optional[str] = Field(None, description="IP地址")
```

#### 用户会话完整模式 (UserSession)

```python
class UserSession(UserSessionBase):
    """用户会话完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    expires_at: datetime = Field(..., description="过期时间")
    created_at: datetime = Field(..., description="创建时间")
```

### 用户偏好设置模式

#### 用户偏好设置模式 (UserPreferences)

```python
class UserPreferences(BaseModel):
    """用户偏好设置模式"""
    theme: str = Field("light", description="主题设置")
    language: str = Field("zh-CN", description="语言设置")
    timezone: str = Field("Asia/Shanghai", description="时区设置")
    email_notifications: bool = Field(True, description="是否接收邮件通知")
    push_notifications: bool = Field(True, description="是否接收推送通知")
    auto_save: bool = Field(True, description="是否自动保存")
    default_document_format: str = Field("markdown", description="默认文档格式")
    default_export_format: str = Field("pdf", description="默认导出格式")
```

### 列表响应模式

#### 用户列表 (UserList)

```python
class UserList(BaseModel):
    """用户列表响应模式"""
    users: List[UserWithDetails] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

## 项目模式

### 项目类型枚举 (ProjectType)

```python
class ProjectType(str, Enum):
    """项目类型枚举"""
    EMERGENCY_PLAN = "emergency_plan"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"
```

### 项目状态枚举 (ProjectStatus)

```python
class ProjectStatus(str, Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
```

### 项目基础模式 (ProjectBase)

```python
class ProjectBase(BaseModel):
    """项目基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    type: ProjectType = Field(..., description="项目类型")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="项目状态")
    description: Optional[str] = Field(None, description="项目描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")
```

### 项目创建模式 (ProjectCreate)

```python
class ProjectCreate(ProjectBase):
    """创建项目模式"""
    user_id: int = Field(..., gt=0, description="所属用户ID")
    company_id: Optional[int] = Field(None, gt=0, description="关联企业ID")
```

### 项目更新模式 (ProjectUpdate)

```python
class ProjectUpdate(BaseModel):
    """更新项目模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    type: Optional[ProjectType] = Field(None, description="项目类型")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")
    description: Optional[str] = Field(None, description="项目描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")
    company_id: Optional[int] = Field(None, gt=0, description="关联企业ID")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
```

### 项目完整模式 (Project)

```python
class Project(ProjectBase):
    """项目完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="项目ID")
    user_id: int = Field(..., description="所属用户ID")
    company_id: Optional[int] = Field(None, description="关联企业ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
```

### 项目详细信息模式 (ProjectWithDetails)

```python
class ProjectWithDetails(Project):
    """包含详细信息的项目模式"""
    user_name: Optional[str] = Field(None, description="用户名")
    company_name: Optional[str] = Field(None, description="企业名称")
    documents_count: Optional[int] = Field(0, description="文档数量")
    forms_count: Optional[int] = Field(0, description="表单数量")
    progress: Optional[float] = Field(0.0, description="项目进度(0-100)")
```

### 项目表单模式

#### 项目表单基础模式 (ProjectFormBase)

```python
class ProjectFormBase(BaseModel):
    """项目表单基础模式"""
    form_type: str = Field(..., min_length=1, max_length=50, description="表单类型")
    form_data: Dict[str, Any] = Field(..., description="表单数据")
```

#### 项目表单创建模式 (ProjectFormCreate)

```python
class ProjectFormCreate(ProjectFormBase):
    """创建项目表单模式"""
    project_id: int = Field(..., gt=0, description="所属项目ID")
```

### 表单字段模式

#### 表单字段基础模式 (FormFieldBase)

```python
class FormFieldBase(BaseModel):
    """表单字段基础模式"""
    field_name: str = Field(..., min_length=1, max_length=100, description="字段名称")
    field_type: str = Field(..., min_length=1, max_length=50, description="字段类型")
    field_label: str = Field(..., min_length=1, max_length=200, description="字段标签")
    field_config: Optional[Dict[str, Any]] = Field(None, description="字段配置")
    sort_order: int = Field(0, description="排序顺序")
    is_required: bool = Field(False, description="是否必填")
```

#### 表单字段创建模式 (FormFieldCreate)

```python
class FormFieldCreate(FormFieldBase):
    """创建表单字段模式"""
    form_id: int = Field(..., gt=0, description="所属表单ID")
```

### 项目模板模式

#### 项目模板基础模式 (ProjectTemplate)

```python
class ProjectTemplate(BaseModel):
    """项目模板模式"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    type: ProjectType = Field(..., description="项目类型")
    template_data: Dict[str, Any] = Field(..., description="模板数据")
    forms: List[Dict[str, Any]] = Field(..., description="表单模板")
    is_default: bool = Field(False, description="是否为默认模板")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
```

### 列表响应模式

#### 项目列表 (ProjectList)

```python
class ProjectList(BaseModel):
    """项目列表响应模式"""
    projects: List[ProjectWithDetails] = Field(..., description="项目列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

## 企业模式

### 企业基础模式 (CompanyBase)

```python
class CompanyBase(BaseModel):
    """企业基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="企业名称")
    unified_social_credit_code: Optional[str] = Field(None, min_length=18, max_length=18, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    business_scope: Optional[str] = Field(None, description="经营范围")
```

### 企业创建模式 (CompanyCreate)

```python
class CompanyCreate(CompanyBase):
    """创建企业模式"""
    pass
```

### 企业更新模式 (CompanyUpdate)

```python
class CompanyUpdate(BaseModel):
    """更新企业模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="企业名称")
    unified_social_credit_code: Optional[str] = Field(None, min_length=18, max_length=18, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    business_scope: Optional[str] = Field(None, description="经营范围")
```

### 企业完整模式 (Company)

```python
class Company(CompanyBase):
    """企业完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="企业ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
```

### 企业详细信息模式 (CompanyWithDetails)

```python
class CompanyWithDetails(Company):
    """包含详细信息的企业模式"""
    projects_count: Optional[int] = Field(0, description="项目数量")
    active_projects_count: Optional[int] = Field(0, description="活跃项目数量")
    completed_projects_count: Optional[int] = Field(0, description="已完成项目数量")
    documents_count: Optional[int] = Field(0, description="文档数量")
```

### 企业搜索模式 (CompanySearch)

```python
class CompanySearch(BaseModel):
    """企业搜索模式"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    industry: Optional[str] = Field(None, description="所属行业")
    unified_social_credit_code: Optional[str] = Field(None, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    created_after: Optional[datetime] = Field(None, description="创建时间起始")
    created_before: Optional[datetime] = Field(None, description="创建时间结束")
```

### 企业验证模式

#### 企业验证基础模式 (CompanyVerification)

```python
class CompanyVerification(BaseModel):
    """企业验证模式"""
    id: Optional[int] = Field(None, description="验证记录ID")
    company_id: int = Field(..., description="企业ID")
    verification_type: str = Field(..., description="验证类型")
    verification_status: str = Field(..., description="验证状态")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="验证备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
```

#### 企业验证创建模式 (CompanyVerificationCreate)

```python
class CompanyVerificationCreate(BaseModel):
    """创建企业验证记录模式"""
    company_id: int = Field(..., description="企业ID")
    verification_type: str = Field(..., description="验证类型")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    notes: Optional[str] = Field(None, description="验证备注")
```

### 企业文档模式

#### 企业文档基础模式 (CompanyDocument)

```python
class CompanyDocument(BaseModel):
    """企业文档模式"""
    id: Optional[int] = Field(None, description="文档ID")
    company_id: int = Field(..., description="企业ID")
    document_type: str = Field(..., description="文档类型")
    document_name: str = Field(..., description="文档名称")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小(字节)")
    upload_by: int = Field(..., description="上传人ID")
    is_verified: bool = Field(False, description="是否已验证")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
```

#### 企业文档创建模式 (CompanyDocumentCreate)

```python
class CompanyDocumentCreate(BaseModel):
    """创建企业文档模式"""
    company_id: int = Field(..., description="企业ID")
    document_type: str = Field(..., description="文档类型")
    document_name: str = Field(..., description="文档名称")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小(字节)")
    notes: Optional[str] = Field(None, description="备注")
```

### 企业联系人模式

#### 企业联系人基础模式 (CompanyContact)

```python
class CompanyContact(BaseModel):
    """企业联系人模式"""
    id: Optional[int] = Field(None, description="联系人ID")
    company_id: int = Field(..., description="企业ID")
    name: str = Field(..., description="联系人姓名")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    is_primary: bool = Field(False, description="是否主要联系人")
    is_active: bool = Field(True, description="是否活跃")
    notes: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
```

#### 企业联系人创建模式 (CompanyContactCreate)

```python
class CompanyContactCreate(BaseModel):
    """创建企业联系人模式"""
    company_id: int = Field(..., description="企业ID")
    name: str = Field(..., description="联系人姓名")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    is_primary: bool = Field(False, description="是否主要联系人")
    notes: Optional[str] = Field(None, description="备注")
```

### 列表响应模式

#### 企业列表 (CompanyList)

```python
class CompanyList(BaseModel):
    """企业列表响应模式"""
    companies: List[CompanyWithDetails] = Field(..., description="企业列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
```

## 使用示例

### 创建文档

```python
from app.schemas import DocumentCreate, DocumentFormat

document_data = DocumentCreate(
    project_id=1,
    title="环保应急预案",
    content="# 环保应急预案\n\n这是预案内容...",
    format=DocumentFormat.MARKDOWN
)
```

### AI生成请求

```python
from app.schemas import AIGenerationRequest

generation_request = AIGenerationRequest(
    prompt="请生成环保应急预案的应急响应部分",
    context="这是一个化工企业的环保应急预案",
    section="应急响应"
)
```

### 文档导出请求

```python
from app.schemas import DocumentExportRequest, ExportFormat

export_request = DocumentExportRequest(
    format=ExportFormat.PDF,
    include_metadata=True,
    watermark="内部文档",
    page_size="A4"
)
```

### 用户注册

```python
from app.schemas import UserRegister

user_data = UserRegister(
    username="testuser",
    email="test@example.com",
    password="securepassword123",
    full_name="测试用户"
)
```

### 项目创建

```python
from app.schemas import ProjectCreate, ProjectType

project_data = ProjectCreate(
    user_id=1,
    company_id=1,
    name="化工企业环保应急预案",
    type=ProjectType.EMERGENCY_PLAN,
    description="为化工企业制定的环保应急预案"
)
```

### 企业创建

```python
from app.schemas import CompanyCreate

company_data = CompanyCreate(
    name="示例化工有限公司",
    unified_social_credit_code="91110000123456789X",
    legal_representative="张三",
    contact_phone="13800138000",
    contact_email="contact@example.com",
    address="北京市朝阳区示例街道123号",
    industry="化工",
    business_scope="化工产品生产与销售"
)
```

## 总结

本文档提供了悦恩人机共写平台的完整Pydantic API模式定义，包括：

1. **文档模式**：文档和文档版本的完整生命周期管理
2. **AI生成模式**：AI内容生成的请求、响应和配置管理
3. **文档导出模式**：文档导出的格式、选项和模板管理
4. **用户模式**：用户认证、会话和偏好设置管理
5. **项目模式**：项目、表单和模板的完整管理
6. **企业模式**：企业信息、验证和联系人管理

所有模式都包含了适当的字段验证、类型注解和文档字符串，确保API的数据一致性和可靠性。这些模式可以直接用于FastAPI的请求和响应处理，提供类型安全和自动文档生成功能。
