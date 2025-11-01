// 模拟项目数据
export const mockProjects = [
  {
    id: 1,
    name: '某化工厂应急预案',
    type: 'emergency_plan',
    status: 'completed',
    description: '针对某化工企业制定的应急响应预案，包括火灾、泄漏等紧急情况的处理流程',
    created_at: '2024-10-15T10:30:00Z',
    updated_at: '2024-10-20T14:20:00Z',
    user_id: 1,
    company_id: 1,
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      full_name: '管理员'
    },
    company: {
      id: 1,
      name: '某某化工有限公司',
      registration_number: '91310000MA1K12345X'
    },
    documents_count: 3,
    ai_generations_count: 5
  },
  {
    id: 2,
    name: '新能源项目环评报告',
    type: 'environmental_assessment',
    status: 'in_progress',
    description: '某新能源发电项目的环境影响评价报告，包括生态影响、噪音影响等分析',
    created_at: '2024-10-18T09:15:00Z',
    updated_at: '2024-10-21T16:45:00Z',
    user_id: 1,
    company_id: 2,
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      full_name: '管理员'
    },
    company: {
      id: 2,
      name: '某某新能源科技有限公司',
      registration_number: '91310000MA1K67890Y'
    },
    documents_count: 1,
    ai_generations_count: 3
  },
  {
    id: 3,
    name: '工业园区安全应急预案',
    type: 'emergency_plan',
    status: 'draft',
    description: '某工业园区综合安全应急预案，涵盖消防、爆炸、泄漏等多种紧急情况',
    created_at: '2024-10-22T11:00:00Z',
    updated_at: '2024-10-22T11:00:00Z',
    user_id: 1,
    company_id: 3,
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      full_name: '管理员'
    },
    company: {
      id: 3,
      name: '某某工业园管理有限公司',
      registration_number: '91310000MA1K54321Z'
    },
    documents_count: 0,
    ai_generations_count: 2
  }
]

// 模拟文档数据
export const mockDocuments = [
  {
    id: 1,
    title: '应急预案-初版',
    content: '# 应急预案初稿\n\n## 一、应急响应组织\n\n...',
    format: 'markdown',
    status: 'draft',
    project_id: 1,
    created_at: '2024-10-16T08:00:00Z',
    updated_at: '2024-10-18T15:30:00Z',
    word_count: 1250,
    project: {
      id: 1,
      name: '某化工厂应急预案',
      type: 'emergency_plan'
    }
  },
  {
    id: 2,
    title: '环评报告-送审稿',
    content: '# 环境影响评价报告\n\n## 项目概况\n\n...',
    format: 'markdown',
    status: 'reviewing',
    project_id: 2,
    created_at: '2024-10-19T10:00:00Z',
    updated_at: '2024-10-21T14:00:00Z',
    word_count: 2800,
    project: {
      id: 2,
      name: '新能源项目环评报告',
      type: 'environmental_assessment'
    }
  },
  {
    id: 3,
    title: '安全评估报告',
    content: '# 安全评估报告\n\n## 风险识别\n\n...',
    format: 'markdown',
    status: 'completed',
    project_id: 1,
    created_at: '2024-10-17T14:00:00Z',
    updated_at: '2024-10-20T16:00:00Z',
    word_count: 1850,
    project: {
      id: 1,
      name: '某化工厂应急预案',
      type: 'emergency_plan'
    }
  }
]

// 模拟企业数据
export const mockCompanies = [
  {
    id: 1,
    name: '某某化工有限公司',
    registration_number: '91310000MA1K12345X',
    address: '上海市浦东新区张江高科技园区',
    contact_person: '张三',
    contact_email: 'zhangsan@example.com',
    contact_phone: '021-12345678',
    industry: '化工',
    description: '专业从事精细化工产品生产的高新技术企业',
    created_at: '2024-09-01T10:00:00Z',
    updated_at: '2024-10-15T14:30:00Z',
    projects_count: 2,
    documents_count: 5
  },
  {
    id: 2,
    name: '某某新能源科技有限公司',
    registration_number: '91310000MA1K67890Y',
    address: '江苏省苏州市工业园区',
    contact_person: '李四',
    contact_email: 'lisi@example.com',
    contact_phone: '0512-87654321',
    industry: '新能源',
    description: '专注于太阳能发电系统研发与制造',
    created_at: '2024-09-10T09:30:00Z',
    updated_at: '2024-10-18T11:20:00Z',
    projects_count: 1,
    documents_count: 2
  },
  {
    id: 3,
    name: '某某工业园管理有限公司',
    registration_number: '91310000MA1K54321Z',
    address: '浙江省杭州市萧山区',
    contact_person: '王五',
    contact_email: 'wangwu@example.com',
    contact_phone: '0571-13579246',
    industry: '工业园区',
    description: '综合性工业园区开发运营管理企业',
    created_at: '2024-08-15T08:45:00Z',
    updated_at: '2024-10-22T16:10:00Z',
    projects_count: 1,
    documents_count: 1
  }
]

// 模拟AI生成数据
export const mockAIGenerations = [
  {
    id: 1,
    type: 'emergency_plan',
    status: 'completed',
    prompt: '为一家化工厂制定应急预案',
    generated_content: '# 应急预案\n\n## 应急响应组织架构\n\n### 总指挥\n负责整个应急响应工作的统一指挥...',
    model_used: 'GPT-4',
    tokens_used: 1250,
    created_at: '2024-10-16T09:00:00Z',
    updated_at: '2024-10-16T09:05:00Z',
    project_id: 1,
    document_id: null
  },
  {
    id: 2,
    type: 'environmental_assessment',
    status: 'completed',
    prompt: '新能源发电项目的环境影响评价',
    generated_content: '# 环境影响评价报告\n\n## 项目概况\n\n本项目为100MW太阳能发电项目...',
    model_used: 'GPT-4',
    tokens_used: 2100,
    created_at: '2024-10-19T10:30:00Z',
    updated_at: '2024-10-19T10:38:00Z',
    project_id: 2,
    document_id: null
  },
  {
    id: 3,
    type: 'emergency_plan',
    status: 'generating',
    prompt: '工业园区安全应急预案',
    generated_content: '',
    model_used: 'GPT-4',
    tokens_used: 0,
    created_at: '2024-10-22T11:00:00Z',
    updated_at: '2024-10-22T11:00:00Z',
    project_id: 3,
    document_id: null
  }
]

// 模拟API响应
export const mockApiResponse = {
  projects: {
    getProjects: (params: any) => ({
      success: true,
      data: {
        projects: mockProjects,
        total: mockProjects.length
      }
    }),
    createProject: (data: any) => ({
      success: true,
      data: {
        ...data,
        id: Date.now(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        documents_count: 0,
        ai_generations_count: 0
      }
    }),
    getProject: (id: number) => ({
      success: true,
      data: mockProjects.find(p => p.id === id)
    }),
    deleteProject: (id: number) => ({
      success: true
    })
  },
  documents: {
    getDocuments: (params: any) => ({
      success: true,
      data: {
        documents: mockDocuments,
        total: mockDocuments.length
      }
    }),
    createDocument: (data: any) => ({
      success: true,
      data: {
        ...data,
        id: Date.now(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }),
    deleteDocument: (id: number) => ({
      success: true
    })
  },
  companies: {
    getCompanies: (params: any) => ({
      success: true,
      data: {
        companies: mockCompanies,
        total: mockCompanies.length,
        page: 1,
        size: params.limit || 12
      }
    }),
    createCompany: (data: any) => ({
      success: true,
      data: {
        ...data,
        id: Date.now(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        projects_count: 0,
        documents_count: 0
      }
    }),
    deleteCompany: (id: number) => ({
      success: true
    })
  },
  aiGeneration: {
    getAIGenerations: (params: any) => ({
      success: true,
      data: {
        generations: mockAIGenerations,
        total: mockAIGenerations.length
      }
    }),
    createAIGeneration: (data: any) => ({
      success: true,
      data: {
        ...data,
        id: Date.now(),
        status: 'completed',
        model_used: 'GPT-4',
        tokens_used: Math.floor(Math.random() * 2000) + 500,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    })
  }
}
