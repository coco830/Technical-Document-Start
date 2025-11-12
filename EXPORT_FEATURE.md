# 文档导出功能说明

## 概述

本系统提供了完整的文档导出功能，支持将文档导出为 PDF 和 Word (DOCX) 格式。导出功能包含以下特性：

- ✅ 支持 PDF 和 Word 两种格式
- ✅ 自动添加文档元数据（作者、创建时间、版本等）
- ✅ 自动生成时间戳文件名
- ✅ HTML 内容自动转换为纯文本
- ✅ 支持单个文档导出和批量导出
- ✅ 完整的错误处理和用户提示
- ✅ 导出前自动保存未保存的更改

## 系统架构

### 后端模块

```
backend/app/export/
├── __init__.py          # 导出模块入口
├── pdf_export.py        # PDF 导出器
└── docx_export.py       # Word 导出器

backend/app/routes/
└── export.py            # 导出 API 路由
```

### 前端模块

```
frontend/src/utils/
└── export.ts            # 导出工具函数

frontend/src/pages/
└── Editor.tsx           # 编辑器页面（包含导出按钮）
```

## 安装依赖

### 后端依赖

在 `backend` 目录下安装以下依赖：

```bash
cd backend
pip install reportlab==4.0.7 python-docx==1.1.0 beautifulsoup4==4.12.2
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 系统字体（可选）

为了更好地支持中文 PDF 导出，建议安装中文字体：

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install fonts-wqy-zenhei
```

**macOS:**
系统自带 PingFang 字体，无需额外安装。

**Windows:**
系统自带宋体和微软雅黑，无需额外安装。

## API 接口说明

### 1. 导出单个文档

**接口:** `POST /api/export/document/{document_id}`

**参数:**
- `document_id` (路径参数): 文档 ID
- `format` (查询参数): 导出格式，可选值 `pdf` 或 `docx`
- `include_metadata` (查询参数): 是否包含元数据，默认 `true`

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/export/document/1?format=pdf&include_metadata=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output document.pdf
```

**响应:**
- 成功: 返回文件流（Content-Type: application/octet-stream）
- 失败: 返回 JSON 错误信息

### 2. 批量导出文档

**接口:** `POST /api/export/batch`

**请求体:**
```json
{
  "document_ids": [1, 2, 3],
  "format": "pdf",
  "custom_filename": "batch_export_2024.pdf"
}
```

**示例请求:**
```bash
curl -X POST "http://localhost:8000/api/export/batch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_ids": [1, 2, 3], "format": "pdf"}' \
  --output batch.pdf
```

### 3. 获取支持的格式

**接口:** `GET /api/export/formats`

**响应:**
```json
{
  "formats": [
    {
      "id": "pdf",
      "name": "PDF 文档",
      "description": "便携式文档格式，适合打印和分享",
      "extension": ".pdf",
      "mime_type": "application/pdf"
    },
    {
      "id": "docx",
      "name": "Word 文档",
      "description": "Microsoft Word 格式，可编辑",
      "extension": ".docx",
      "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
  ]
}
```

## 前端使用

### 在编辑器中使用

1. 打开文档编辑器
2. 确保文档已保存
3. 点击编辑器顶部的"📥 导出"按钮
4. 选择导出格式（PDF 或 Word）
5. 文件将自动下载到浏览器默认下载位置

### 编程方式调用

```typescript
import { exportDocument } from '@/utils/export'

// 导出为 PDF
await exportDocument({
  documentId: 1,
  format: 'pdf',
  includeMetadata: true
})

// 导出为 Word
await exportDocument({
  documentId: 1,
  format: 'docx',
  includeMetadata: true
})
```

### 批量导出

```typescript
import { exportBatch } from '@/utils/export'

// 批量导出为 PDF
await exportBatch({
  documentIds: [1, 2, 3],
  format: 'pdf',
  customFilename: 'my_documents.pdf'
})
```

## 导出文件格式

### PDF 导出

**特点:**
- A4 纸张大小
- 2cm 页边距
- 支持中文字体（如果系统已安装）
- 自动添加文档标题、元数据、导出时间
- 段落自动换行和排版

**文件命名规则:**
```
{文档标题}_{时间戳}.pdf
例如: 环保报告_20241104_223000.pdf
```

### Word 导出

**特点:**
- A4 纸张大小
- 2.5cm 左右页边距，2cm 上下页边距
- 自定义样式（标题、正文等）
- 1.5 倍行距
- 可在 Microsoft Word 或 WPS 中编辑

**文件命名规则:**
```
{文档标题}_{时间戳}.docx
例如: 环保报告_20241104_223000.docx
```

## 高级功能

### 1. HTML 内容处理

导出器会自动处理 HTML 内容：
- 移除 `<script>` 和 `<style>` 标签
- 提取纯文本内容
- 保留段落结构
- 识别简单的 Markdown 标题语法

### 2. 文档元数据

导出的文档包含以下元数据：
- 作者（当前用户）
- 创建时间
- 文档版本
- 导出时间

### 3. 批量导出

批量导出会将多个文档合并为一个文件：
- 每个文档占据独立的页面
- 自动添加封面（包含文档数量和导出时间）
- 文档之间自动分页

### 4. 错误处理

系统提供完善的错误处理：
- 文档不存在或无权访问
- 导出过程失败
- 文件生成失败
- 网络连接问题

## 文件存储

导出的文件临时存储在服务器上：

```
backend/exports/
├── pdf/          # PDF 文件目录
└── docx/         # Word 文件目录
```

**注意:** 建议定期清理导出文件，避免占用过多磁盘空间。可以设置定时任务自动清理超过 24 小时的导出文件。

## 性能优化建议

1. **并发控制:** 限制同时导出的文档数量
2. **文件清理:** 定期清理临时导出文件
3. **缓存策略:** 对相同文档的重复导出可以使用缓存
4. **异步处理:** 对于大文档或批量导出，可以改为异步队列处理

## 安全考虑

1. **权限验证:**
   - 所有导出接口都需要用户认证
   - 只能导出用户自己的文档

2. **文件访问控制:**
   - 导出文件存储在受保护的目录
   - 文件名使用时间戳避免冲突

3. **内容安全:**
   - HTML 内容自动清理 script 和 style 标签
   - 防止 XSS 攻击

## 故障排查

### 问题 1: PDF 中文显示为方块

**原因:** 系统未安装中文字体

**解决方案:**
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei

# 或手动下载字体文件放到系统字体目录
```

### 问题 2: 导出按钮禁用

**原因:** 文档未保存

**解决方案:** 先保存文档，然后再导出

### 问题 3: 导出失败（500 错误）

**可能原因:**
1. 后端依赖未安装
2. 导出目录权限问题
3. 磁盘空间不足

**解决方案:**
```bash
# 检查依赖
pip list | grep -E "reportlab|python-docx|beautifulsoup4"

# 检查目录权限
chmod 755 backend/exports

# 检查磁盘空间
df -h
```

## 未来扩展

可以考虑添加以下功能：

1. **更多导出格式:**
   - Markdown
   - HTML
   - 纯文本
   - ePub（电子书格式）

2. **样式定制:**
   - 自定义字体
   - 自定义颜色主题
   - 自定义页眉页脚
   - 添加水印

3. **高级功能:**
   - 目录自动生成
   - 图片导出支持
   - 表格样式优化
   - 代码高亮

4. **云存储集成:**
   - 直接导出到 Google Drive
   - 直接导出到 Dropbox
   - 直接导出到阿里云 OSS

## 相关文档

- [项目总体架构](./PROJECT_STRUCTURE.md)
- [API 文档](./API_DOCUMENTATION.md)
- [安全审查](./SECURITY_REVIEW.md)
