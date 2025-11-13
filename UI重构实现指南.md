# UI重构实现指南

## 概述
根据用户要求，需要重新设计整个UI架构，将"企业信息"、"AI生成"、"导出"等功能从全局菜单移到项目内部，实现"项目驱动型 SaaS"的行业标准设计。

## 当前问题分析
1. 全局菜单过多，包括企业信息、AI生成、导出等应该属于项目内部的功能
2. 用户不清楚当前操作属于哪个项目
3. 没有明确的工作流程顺序
4. 导航层级混乱

## 新UI设计方案

### 全局导航（仅3个菜单项）
1. 🏠 工作台
2. 📁 项目管理
3. 🧩 模板管理（管理员）

### 项目内部导航
- 📄 项目概览
- 🏭 企业信息
  - 基本信息
  - 生产过程
  - 环境信息
  - 环保手续
- 🤖 AI 生成
  - 选择模板
  - 生成章节
  - 历史记录
- ✏ 编辑校对
- 📤 导出
  - PDF 导出
  - Word 导出
  - 导出历史

## 实现步骤

### 1. 修改Layout组件（全局导航）

**文件**: `frontend/src/components/Layout.tsx`

需要修改的部分：
```typescript
// 将navItems简化为只有3个菜单项
const navItems = [
  { path: '/dashboard', label: '工作台', icon: '🏠' },
  { path: '/projects', label: '项目管理', icon: '📁' },
  { path: '/templates', label: '模板管理', icon: '🧩' }
]
```

移除原有的子菜单结构，简化为单层菜单。

### 2. 修改ProjectLayout组件（项目内部导航）

**文件**: `frontend/src/components/ProjectLayout.tsx`

需要重新设计projectNavItems，实现完整的项目内部导航结构：

```typescript
// 项目内部导航菜单
const projectNavItems = [
  {
    path: `/project/${currentProjectId}`,
    label: '项目概览',
    icon: '📄',
    description: '查看项目基本信息和进度'
  },
  {
    path: `/project/${currentProjectId}/enterprise`,
    label: '企业信息',
    icon: '🏭',
    description: '企业基本信息收集',
    children: [
      {
        path: `/project/${currentProjectId}/enterprise`,
        label: '基本信息',
        icon: '📝'
      },
      {
        path: `/project/${currentProjectId}/enterprise/production`,
        label: '生产过程',
        icon: '⚙️'
      },
      {
        path: `/project/${currentProjectId}/enterprise/environment`,
        label: '环境信息',
        icon: '🌍'
      },
      {
        path: `/project/${currentProjectId}/enterprise/permits`,
        label: '环保手续',
        icon: '📋'
      }
    ]
  },
  {
    path: `/project/${currentProjectId}/ai-generate`,
    label: 'AI 生成',
    icon: '🤖',
    description: 'AI智能生成预案文档',
    children: [
      {
        path: `/project/${currentProjectId}/ai-generate`,
        label: '选择模板',
        icon: '📋'
      },
      {
        path: `/project/${currentProjectId}/ai-generate/chapters`,
        label: '生成章节',
        icon: '🔧'
      },
      {
        path: `/project/${currentProjectId}/ai-generate/history`,
        label: '历史记录',
        icon: '📚'
      }
    ]
  },
  {
    path: `/project/${currentProjectId}/editor`,
    label: '编辑校对',
    icon: '✏️',
    description: '文档编辑与校对'
  },
  {
    path: `/project/${currentProjectId}/export`,
    label: '导出',
    icon: '📤',
    description: '文档导出功能',
    children: [
      {
        path: `/project/${currentProjectId}/export/pdf`,
        label: 'PDF 导出',
        icon: '📄'
      },
      {
        path: `/project/${currentProjectId}/export/word`,
        label: 'Word 导出',
        icon: '📝'
      },
      {
        path: `/project/${currentProjectId}/export/history`,
        label: '导出历史',
        icon: '📚'
      }
    ]
  }
]
```

### 3. 更新路由系统

**文件**: `frontend/src/App.tsx`

需要简化路由结构，移除全局的企业信息、AI生成、导出路由，只保留项目内部的路由：

```typescript
// 移除这些全局路由
// /enterprise-info
// /ai-generate
// /export
// /editor/:id?

// 只保留项目内部路由
<Route path="/project/:id" element={<ProjectDetail />} />
<Route path="/project/:id/enterprise" element={<ProjectEnterprise />} />
<Route path="/project/:id/enterprise/:step" element={<ProjectEnterprise />} />
<Route path="/project/:id/ai-generate" element={<AIGenerate />} />
<Route path="/project/:id/ai-generate/:step" element={<AIGenerate />} />
<Route path="/project/:id/editor" element={<Editor />} />
<Route path="/project/:id/export" element={<Export />} />
<Route path="/project/:id/export/:format" element={<Export />} />
```

### 4. 修改页面组件

#### 4.1 修改Dashboard页面
**文件**: `frontend/src/pages/Dashboard.tsx`

需要更新快速操作区域的跳转链接：
```typescript
// 修改快速操作区域的跳转链接
<button onClick={() => navigate('/projects')}>
  // 继续编辑应该跳转到项目列表，然后选择项目进入
</button>

// 移除直接跳转到企业信息、AI生成、导出的按钮
// 这些操作应该在项目内部进行
```

#### 4.2 修改Projects页面
**文件**: `frontend/src/pages/Projects.tsx`

更新项目卡片的"进入项目"按钮：
```typescript
<button
  onClick={() => navigate(`/project/${project.id}`)}
  className="flex-1 bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
>
  进入项目
</button>
```

#### 4.3 修改ProjectDetail页面
**文件**: `frontend/src/pages/ProjectDetail.tsx`

确保所有快速操作按钮跳转到正确的项目内部路由：
```typescript
<button onClick={() => navigate(`/project/${id}/enterprise`)}>
  企业信息
</button>
<button onClick={() => navigate(`/project/${id}/ai-generate`)}>
  AI生成
</button>
<button onClick={() => navigate(`/project/${id}/editor`)}>
  编辑校对
</button>
<button onClick={() => navigate(`/project/${id}/export`)}>
  导出文档
</button>
```

#### 4.4 修改AIGenerate页面
**文件**: `frontend/src/pages/AIGenerate.tsx`

需要修改为项目内部组件，移除项目选择功能，因为已经在项目内部：
```typescript
// 移除项目选择功能，因为已经在项目内部
// 直接使用URL参数中的项目ID
const { id } = useParams()
const projectId = parseInt(id || '0')

// 修改生成成功后的跳转
navigate(`/project/${projectId}/editor`)
```

#### 4.5 修改Export页面
**文件**: `frontend/src/pages/Export.tsx`

同样需要修改为项目内部组件：
```typescript
// 移除项目选择功能，使用URL参数中的项目ID
const { id } = useParams()
const projectId = parseInt(id || '0')

// 修改导出成功后的处理
// 保持在项目内部，不跳转到其他页面
```

### 5. 删除不需要的页面

删除以下页面，因为它们的功能已经移到项目内部：
- `frontend/src/pages/EnterpriseInfo.tsx`（保留ProjectEnterprise.tsx）

### 6. 更新导航逻辑

确保所有导航都遵循以下流程：
1. 工作台 → 项目管理 → 选择项目 → 项目内部导航
2. 项目内部按照：项目概览 → 企业信息 → AI生成 → 编辑校对 → 导出的顺序

## 实现顺序

1. 首先修改Layout组件，简化全局导航
2. 然后修改ProjectLayout组件，完善项目内部导航
3. 更新App.tsx中的路由结构
4. 逐个修改页面组件以适应新的导航结构
5. 删除不需要的页面文件
6. 测试整个导航流程

## 测试要点

1. 确保全局菜单只有3个选项
2. 确保项目内部导航完整且功能正常
3. 确保所有跳转链接正确
4. 确保用户流程清晰：从项目列表进入项目，然后按照顺序完成各个步骤
5. 确保不会出现用户不知道当前操作属于哪个项目的情况

## 预期效果

实现后的系统将具有以下特点：
1. 清晰的全局导航，只有3个菜单项
2. 完整的项目内部导航，所有操作都明确属于某个项目
3. 明确的工作流程顺序
4. 行业标准的项目驱动型SaaS设计
5. 用户不会迷失在复杂的导航结构中