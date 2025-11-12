# 文件上传安全功能文档

## 概述

本文档描述了项目中实现的文件上传安全功能，包括文件类型验证、大小限制、魔数检查和恶意内容扫描等安全措施。

## 功能特性

### 1. 文件类型白名单验证

系统只允许上传预定义的安全文件类型：

- **图片文件**: JPEG, PNG, GIF, WebP (最大5MB)
- **文档文件**: PDF, DOC, DOCX (最大10MB)
- **文本文件**: TXT (最大1MB)

### 2. 文件头验证（魔数检查）

不仅依赖文件扩展名，还检查文件头（魔数）以确保文件类型真实性：

- JPEG: `\xff\xd8\xff`
- PNG: `\x89\x50\x4e\x47\x0d\x0a\x1a\x0a`
- GIF: `GIF87a` 或 `GIF89a`
- WebP: `RIFF` 和 `WEBP`
- PDF: `%PDF-`
- 等等...

### 3. 文件大小限制

根据文件类型设置不同的大小限制，防止资源耗尽攻击：

- 图片文件: 5MB
- 文档文件: 10MB
- 文本文件: 1MB
- 系统总限制: 50MB

### 4. 文件名安全检查

- 检查路径遍历攻击 (`../`, `..\\`)
- 检查危险字符 (`:`, `*`, `?`, `"`, `<`, `>`, `|`)
- 检查危险扩展名 (`.exe`, `.bat`, `.cmd`, `.com`, `.scr` 等)

### 5. 恶意内容扫描

扫描文件内容中的可疑模式：

- 脚本标签 (`<script>`)
- JavaScript协议 (`javascript:`)
- VBScript协议 (`vbscript:`)
- HTML数据URI (`data:text/html`)
- 可执行代码模式 (`eval(`, `exec(`, `system(` 等)
- 可执行文件签名 (PE, ELF, Java class, Mach-O 等)

### 6. 详细日志记录

记录所有文件上传尝试，包括：

- 用户ID
- 文件名
- 声明的Content-Type
- 文件大小
- 验证结果
- 错误信息（如果有）

## 使用方法

### 1. 基本使用

```python
from app.utils.file_validator import validate_uploaded_file, scan_file_security

# 验证上传的文件
try:
    result = validate_uploaded_file(
        file_content=file_bytes,
        filename="example.jpg",
        content_type="image/jpeg"
    )
    print(f"文件验证成功: {result}")
except FileValidationError as e:
    print(f"文件验证失败: {e}")

# 扫描文件安全性
if scan_file_security(file_bytes):
    print("文件安全")
else:
    print("文件包含可疑内容")
```

### 2. API使用

```python
# 上传图片
POST /api/documents/upload-image
Content-Type: multipart/form-data
Authorization: Bearer <token>

# 请求体
file: <binary_file_data>

# 响应
{
    "url": "/uploads/images/uuid-filename.jpg",
    "filename": "uuid-filename.jpg",
    "size": 12345,
    "content_type": "image/jpeg",
    "description": "JPEG图片"
}
```

## 配置选项

### 1. 修改文件类型白名单

编辑 `backend/app/utils/file_validator.py` 中的 `ALLOWED_FILE_TYPES` 字典：

```python
ALLOWED_FILE_TYPES = {
    'image/jpeg': {
        'extensions': ['.jpg', '.jpeg'],
        'magic_numbers': [b'\xff\xd8\xff'],
        'max_size': 5 * 1024 * 1024,  # 5MB
        'description': 'JPEG图片'
    },
    # 添加新的文件类型...
}
```

### 2. 修改危险扩展名列表

编辑 `DANGEROUS_EXTENSIONS` 列表：

```python
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    # 添加新的危险扩展名...
]
```

### 3. 修改恶意内容模式

编辑 `scan_for_malicious_content` 方法中的 `suspicious_patterns` 列表：

```python
suspicious_patterns = [
    b'<script',
    b'javascript:',
    # 添加新的可疑模式...
]
```

## 依赖项

- `python-magic`: 用于文件类型检测
- `fastapi`: Web框架
- `python-multipart`: 文件上传支持

安装依赖：

```bash
pip install python-magic==0.4.27
```

## 测试

运行文件上传安全测试：

```bash
cd backend
python test_file_upload_security.py
```

或使用pytest：

```bash
cd backend
pytest test_file_upload_security.py -v
```

## 安全注意事项

1. **定期更新**: 定期更新文件类型定义和恶意内容模式
2. **监控日志**: 监控文件上传日志，及时发现可疑活动
3. **限制权限**: 确保上传目录的权限设置正确
4. **定期扫描**: 定期扫描已上传的文件，发现新的威胁
5. **备份策略**: 制定文件备份和恢复策略

## 错误处理

系统提供详细的错误信息：

- `FileValidationError`: 文件验证失败
- `HTTPException`: API错误响应
- 详细日志记录用于调试和审计

## 性能考虑

1. **文件大小检查**: 在读取完整文件前进行大小检查
2. **魔数验证**: 只检查文件头部，不读取整个文件
3. **异步处理**: 使用异步文件操作
4. **缓存结果**: 考虑缓存文件类型检测结果

## 扩展功能

可以考虑添加的功能：

1. **病毒扫描**: 集成第三方病毒扫描引擎
2. **图像处理**: 自动调整图像大小和格式
3. **内容审核**: 使用AI进行图像内容审核
4. **文件加密**: 对敏感文件进行加密存储
5. **访问控制**: 更细粒度的文件访问控制

## 故障排除

### 常见问题

1. **python-magic安装失败**
   - Ubuntu/Debian: `sudo apt-get install libmagic1`
   - CentOS/RHEL: `sudo yum install file-devel`
   - macOS: `brew install libmagic`

2. **文件类型检测不准确**
   - 确保`python-magic`库正确安装
   - 检查文件头定义是否正确

3. **性能问题**
   - 考虑使用异步文件处理
   - 优化文件大小检查逻辑

## 更新日志

- **v1.0.0**: 初始版本，实现基本文件验证功能
- **v1.1.0**: 添加恶意内容扫描
- **v1.2.0**: 增强日志记录和错误处理