# 文档导出功能 - 快速安装指南

## 📋 前置要求

- Python 3.8+
- Node.js 16+
- 运行中的后端服务（FastAPI）
- 运行中的前端服务（React + Vite）

## 🚀 快速安装

### 1. 安装后端依赖

```bash
cd backend

# 安装 Python 依赖
pip install reportlab==4.0.7 python-docx==1.1.0 beautifulsoup4==4.12.2

# 或者使用 requirements.txt
pip install -r requirements.txt
```

### 2. 安装中文字体支持（可选但推荐）

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install fonts-wqy-zenhei
```

**macOS:**
```bash
# macOS 系统自带中文字体，无需额外安装
```

**Windows:**
```bash
# Windows 系统自带中文字体，无需额外安装
```

### 3. 创建导出目录

```bash
cd backend
mkdir -p exports/pdf exports/docx
chmod 755 exports
```

### 4. 重启后端服务

```bash
# 使用 uvicorn
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用项目提供的启动脚本
./start-dev.sh
```

### 5. 验证安装

访问 API 文档查看导出接口：
```
http://localhost:8000/docs
```

查找以下接口：
- `POST /api/export/document/{document_id}`
- `POST /api/export/batch`
- `GET /api/export/formats`

## ✅ 功能测试

### 测试单个文档导出

1. 登录系统
2. 打开或创建一个文档
3. 确保文档已保存
4. 点击顶部工具栏的"📥 导出"按钮
5. 选择"📄 导出为 PDF"或"📝 导出为 Word"
6. 检查浏览器下载目录，确认文件已下载

### 测试 API 接口

使用 curl 测试：

```bash
# 获取支持的格式
curl http://localhost:8000/api/export/formats

# 导出文档（需要替换 TOKEN 和 DOCUMENT_ID）
curl -X POST "http://localhost:8000/api/export/document/1?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output test.pdf
```

## 🔧 故障排查

### 问题 1: 导入错误 "No module named 'reportlab'"

**解决方案:**
```bash
pip install reportlab==4.0.7
```

### 问题 2: PDF 中文显示为方块

**解决方案:**
```bash
# Linux
sudo apt-get install fonts-wqy-zenhei

# 然后重启后端服务
```

### 问题 3: 权限错误 "Permission denied"

**解决方案:**
```bash
cd backend
chmod 755 exports
chmod 755 exports/pdf
chmod 755 exports/docx
```

### 问题 4: 前端导出按钮不显示

**解决方案:**
```bash
# 确保前端代码已更新
cd frontend
npm install
npm run dev
```

### 问题 5: 导出时提示"请先保存文档"

**解决方案:**
这是正常行为。请先点击"💾 保存"按钮保存文档，然后再导出。

## 📚 详细文档

查看完整文档：
- [功能详细说明](./EXPORT_FEATURE.md)
- [API 接口文档](http://localhost:8000/docs)

## 🎯 核心功能

✅ **支持格式:**
- PDF 文档（适合打印和分享）
- Word 文档（可编辑）

✅ **智能功能:**
- 自动添加文档元数据
- 自动生成时间戳文件名
- HTML 转纯文本
- 批量导出支持

✅ **用户体验:**
- 一键导出
- 下拉菜单选择格式
- 导出前自动保存提示
- 完整的错误提示

## 🔐 安全特性

- ✅ 用户认证保护
- ✅ 权限验证（只能导出自己的文档）
- ✅ HTML 内容自动清理
- ✅ 文件名安全处理

## 📦 依赖版本

```txt
reportlab==4.0.7
python-docx==1.1.0
beautifulsoup4==4.12.2
```

## 💡 使用提示

1. **导出前保存:** 确保文档已保存，否则导出按钮会被禁用
2. **文件命名:** 导出的文件自动使用"文档标题_时间戳"格式命名
3. **批量导出:** 可以通过 API 一次性导出多个文档
4. **格式选择:** PDF 适合最终分享，Word 适合继续编辑

## 🎉 完成！

现在您可以开始使用文档导出功能了！

如有问题，请查看：
- [完整功能文档](./EXPORT_FEATURE.md)
- [项目 GitHub Issues](https://github.com/yourusername/yourrepo/issues)
