# 悦恩人机共写平台

## 项目简介

悦恩人机共写平台是一个AI驱动的环保文案生成SaaS平台，专注于解决环保服务行业中大量文书（尤其是"应急预案"和"环评报告"）撰写繁琐、模板化、效率低的问题。

## 核心理念

"让AI生成80%八股文模板内容，剩余20%由人机共创、人工复核"

## 技术栈

### 前端
- Next.js 14+ (React框架)
- TypeScript
- TailwindCSS (样式框架)
- Zustand (状态管理)
- Shadcn/UI (UI组件库)

### 后端
- FastAPI (Python Web框架)
- MySQL (数据库)
- Redis (缓存)
- LangChain (AI集成)
- 智谱GLM4.6 API (AI模型)

### 云服务
- 腾讯云CloudBase (数据库)
- 腾讯云COS (文件存储)

## 项目结构

```
悦恩人机共写平台/
├── frontend/          # Next.js前端项目
├── backend/           # FastAPI后端项目
├── docs/              # 项目文档
├── README.md          # 项目说明
└── .gitignore         # Git忽略文件
```

## 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 开发计划

1. 项目初始化和环境搭建
2. 设计数据库结构和API接口规范
3. 搭建前端基础框架
4. 搭建后端基础框架
5. 实现用户认证和权限管理系统
6. 开发项目管理模块
7. 开发企业信息表单模块
8. 集成AI服务和文案生成功能
9. 开发富文本编辑器和AI辅助写作功能
10. 实现文档保存、版本管理和导出功能
11. 集成云存储服务
12. UI/UX优化和响应式设计
13. 系统测试和性能优化
14. 部署和上线准备

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情