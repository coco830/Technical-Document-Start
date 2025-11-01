import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { API_BASE_URL, STORAGE_KEYS, ERROR_MESSAGES } from './constants'
import {
  ApiResponse,
  Project,
  ProjectWithDetails,
  ProjectList,
  ProjectForm,
  ProjectFormWithDetails,
  ProjectFormList,
  ProjectFormCreate,
  ProjectFormUpdate,
  ProjectStatistics,
  ProjectProgress,
  ProjectType,
  ProjectStatus,
  Company,
  CompanyWithDetails,
  CompanyList,
  CompanyCreate,
  CompanyUpdate,
  CompanySearch,
  CompanyStatistics,
  CompanyVerification,
  CompanyVerificationCreate,
  CompanyVerificationUpdate,
  CompanyVerificationWithDetails,
  CompanyVerificationList,
  CompanyDocument,
  CompanyDocumentCreate,
  CompanyDocumentUpdate,
  CompanyDocumentWithDetails,
  CompanyDocumentList,
  CompanyContact,
  CompanyContactCreate,
  CompanyContactUpdate,
  CompanyContactWithDetails,
  CompanyContactList,
  AIGeneration,
  AIGenerationWithDetails,
  AIGenerationList,
  AIGenerationCreate,
  AIGenerationUpdate,
  AIGenerationRequest,
  AIGenerationResponse,
  AIGenerationConfig,
  AIGenerationTemplate,
  AIGenerationTemplateCreate,
  AIGenerationTemplateUpdate,
  AIGenerationTemplateList,
  AIGenerationStatus,
  AIGenerationStatusInfo,
  Document,
  DocumentWithDetails,
  DocumentCreate,
  DocumentUpdate,
  DocumentList,
  DocumentVersion,
  DocumentVersionWithDetails,
  DocumentVersionCreate,
  DocumentVersionList,
  DocumentFormat,
  DocumentStatus,
  DocumentSearch,
  DocumentStatistics,
  DocumentExport,
  DocumentExportWithDetails,
  DocumentExportList,
  DocumentExportRequest,
  DocumentExportResponse,
  ExportFormat,
  ExportStatus,
  ExportOptions,
  ExportTemplate,
  ExportTemplateCreate,
  ExportTemplateUpdate,
  ExportTemplateList,
  ExportStatistics,
  FileUploadRequest,
  FileUploadResponse,
  FileDownloadRequest,
  FileDeleteRequest,
  FileListRequest,
  FileListResponse,
  FileInfo,
  FileSyncRequest,
  FileBackupRequest,
  FilePresignedUrlRequest,
  FileStorageSwitchRequest,
  FileStorageStatus,
  FileOperationResponse,
  FileUploadProgress,
  FileChunkUploadRequest,
  FileChunkUploadResponse
} from '@/types'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳
    if (config.params) {
      config.params._t = Date.now()
    } else {
      config.params = { _t: Date.now() }
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    
    // 处理401未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // 尝试刷新token
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token)
          
          // 重新发送原始请求
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // 刷新token失败，清除本地存储并跳转到登录页
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.USER_INFO)
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      }
    }
    
    // 处理其他错误
    let errorMessage: string = ERROR_MESSAGES.NETWORK_ERROR
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = (data as any)?.message || ERROR_MESSAGES.VALIDATION_ERROR
          break
        case 401:
          errorMessage = ERROR_MESSAGES.UNAUTHORIZED
          break
        case 403:
          errorMessage = ERROR_MESSAGES.FORBIDDEN
          break
        case 404:
          errorMessage = ERROR_MESSAGES.NOT_FOUND
          break
        case 422:
          errorMessage = (data as any)?.detail || ERROR_MESSAGES.VALIDATION_ERROR
          break
        case 500:
          errorMessage = ERROR_MESSAGES.SERVER_ERROR
          break
        default:
          errorMessage = (data as any)?.message || ERROR_MESSAGES.NETWORK_ERROR
      }
    } else if (error.request) {
      errorMessage = ERROR_MESSAGES.NETWORK_ERROR
    }
    
    return Promise.reject({
      ...error,
      message: errorMessage,
      originalError: error,
    })
  }
)

// API请求方法封装
class ApiClient {
  // GET请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.get<ApiResponse<T>>(url, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // POST请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.post<ApiResponse<T>>(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // PUT请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.put<ApiResponse<T>>(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // PATCH请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.patch<ApiResponse<T>>(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // DELETE请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await apiClient.delete<ApiResponse<T>>(url, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // 文件上传
  async upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await apiClient.post<ApiResponse<T>>(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...config?.headers,
        },
      })
      
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // 文件上传（带额外参数）
  async uploadWithParams<T = any>(url: string, file: File, params?: Record<string, any>, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // 添加额外参数
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (typeof value === 'string' || value instanceof Blob) {
            formData.append(key, value)
          } else {
            formData.append(key, JSON.stringify(value))
          }
        })
      }
      
      const response = await apiClient.post<ApiResponse<T>>(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...config?.headers,
        },
      })
      
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // 下载文件
  async download(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
    try {
      const response = await apiClient.get(url, {
        ...config,
        responseType: 'blob',
      })
      
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      throw this.handleError(error)
    }
  }
  
  // 错误处理
  private handleError(error: any): Error {
    if (error.response) {
      // 服务器响应错误
      return new Error(error.message || ERROR_MESSAGES.SERVER_ERROR)
    } else if (error.request) {
      // 网络错误
      return new Error(ERROR_MESSAGES.NETWORK_ERROR)
    } else {
      // 其他错误
      return new Error(error.message || ERROR_MESSAGES.NETWORK_ERROR)
    }
  }
}

// 创建API客户端实例
export const api = new ApiClient()

// 导出axios实例以供高级用法
export { apiClient }

// 项目相关API
export const projectApi = {
  // 获取项目列表
  getProjects: async (params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    company_id?: number;
    status?: ProjectStatus;
    type?: ProjectType;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<ProjectList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/projects${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<ProjectList>(url);
  },

  // 创建项目
  createProject: async (data: {
    name: string;
    type: ProjectType;
    description?: string;
    user_id?: number;
    company_id?: number;
    metadata?: Record<string, any>;
  }): Promise<ApiResponse<Project>> => {
    return api.post<Project>('/api/v1/projects', data);
  },

  // 获取项目详情
  getProject: async (id: number): Promise<ApiResponse<ProjectWithDetails>> => {
    return api.get<ProjectWithDetails>(`/api/v1/projects/${id}`);
  },

  // 更新项目
  updateProject: async (id: number, data: {
    name?: string;
    type?: ProjectType;
    status?: ProjectStatus;
    description?: string;
    metadata?: Record<string, any>;
    company_id?: number;
    completed_at?: string;
  }): Promise<ApiResponse<Project>> => {
    return api.put<Project>(`/api/v1/projects/${id}`, data);
  },

  // 删除项目
  deleteProject: async (id: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/projects/${id}`);
  },

  // 更新项目状态
  updateProjectStatus: async (id: number, status: ProjectStatus): Promise<ApiResponse<Project>> => {
    return api.put<Project>(`/api/v1/projects/${id}/status`, { status });
  },

  // 获取项目统计
  getProjectStatistics: async (user_id?: number): Promise<ApiResponse<ProjectStatistics>> => {
    const queryParams = user_id ? `?user_id=${user_id}` : '';
    return api.get<ProjectStatistics>(`/api/v1/projects/statistics${queryParams}`);
  },

  // 获取项目表单列表
  getProjectForms: async (projectId: number, params?: {
    skip?: number;
    limit?: number;
    form_type?: string;
  }): Promise<ApiResponse<ProjectFormList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/projects/${projectId}/forms${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<ProjectFormList>(url);
  },

  // 创建项目表单
  createProjectForm: async (projectId: number, data: ProjectFormCreate): Promise<ApiResponse<ProjectForm>> => {
    return api.post<ProjectForm>(`/api/v1/projects/${projectId}/forms`, data);
  },

  // 更新项目表单
  updateProjectForm: async (projectId: number, formId: number, data: ProjectFormUpdate): Promise<ApiResponse<ProjectForm>> => {
    return api.put<ProjectForm>(`/api/v1/projects/${projectId}/forms/${formId}`, data);
  },
};

// 企业相关API
export const companyApi = {
  // 获取企业列表
  getCompanies: async (params?: {
    skip?: number;
    limit?: number;
    keyword?: string;
    industry?: string;
    unified_social_credit_code?: string;
    legal_representative?: string;
    contact_phone?: string;
    contact_email?: string;
    address?: string;
    created_after?: string;
    created_before?: string;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<CompanyList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/companies${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<CompanyList>(url);
  },

  // 创建企业
  createCompany: async (data: CompanyCreate): Promise<ApiResponse<Company>> => {
    return api.post<Company>('/api/v1/companies', data);
  },

  // 获取企业详情
  getCompany: async (id: number): Promise<ApiResponse<CompanyWithDetails>> => {
    return api.get<CompanyWithDetails>(`/api/v1/companies/${id}`);
  },

  // 更新企业
  updateCompany: async (id: number, data: CompanyUpdate): Promise<ApiResponse<Company>> => {
    return api.put<Company>(`/api/v1/companies/${id}`, data);
  },

  // 删除企业
  deleteCompany: async (id: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/companies/${id}`);
  },

  // 获取企业统计
  getCompanyStatistics: async (): Promise<ApiResponse<CompanyStatistics>> => {
    return api.get<CompanyStatistics>('/api/v1/companies/statistics');
  },

  // 搜索企业
  searchCompanies: async (searchParams: CompanySearch, params?: {
    skip?: number;
    limit?: number;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<CompanyList>> => {
    const queryParams = new URLSearchParams();
    
    // 添加搜索参数
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
    
    // 添加分页和排序参数
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/companies/search${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<CompanyList>(url);
  },

  // 企业验证相关API
  // 获取企业验证记录列表
  getCompanyVerifications: async (companyId: number, params?: {
    skip?: number;
    limit?: number;
    verification_type?: string;
    verification_status?: string;
  }): Promise<ApiResponse<CompanyVerificationList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/companies/${companyId}/verifications${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<CompanyVerificationList>(url);
  },

  // 创建企业验证记录
  createCompanyVerification: async (companyId: number, data: CompanyVerificationCreate): Promise<ApiResponse<CompanyVerification>> => {
    return api.post<CompanyVerification>(`/api/v1/companies/${companyId}/verifications`, data);
  },

  // 更新企业验证记录
  updateCompanyVerification: async (companyId: number, verificationId: number, data: CompanyVerificationUpdate): Promise<ApiResponse<CompanyVerification>> => {
    return api.put<CompanyVerification>(`/api/v1/companies/${companyId}/verifications/${verificationId}`, data);
  },

  // 企业文档相关API
  // 获取企业文档列表
  getCompanyDocuments: async (companyId: number, params?: {
    skip?: number;
    limit?: number;
    document_type?: string;
    is_verified?: boolean;
  }): Promise<ApiResponse<CompanyDocumentList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/companies/${companyId}/documents${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<CompanyDocumentList>(url);
  },

  // 创建企业文档
  createCompanyDocument: async (companyId: number, data: CompanyDocumentCreate): Promise<ApiResponse<CompanyDocument>> => {
    return api.post<CompanyDocument>(`/api/v1/companies/${companyId}/documents`, data);
  },

  // 更新企业文档
  updateCompanyDocument: async (companyId: number, documentId: number, data: CompanyDocumentUpdate): Promise<ApiResponse<CompanyDocument>> => {
    return api.put<CompanyDocument>(`/api/v1/companies/${companyId}/documents/${documentId}`, data);
  },

  // 删除企业文档
  deleteCompanyDocument: async (companyId: number, documentId: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/companies/${companyId}/documents/${documentId}`);
  },

  // 企业联系人相关API
  // 获取企业联系人列表
  getCompanyContacts: async (companyId: number, params?: {
    skip?: number;
    limit?: number;
    is_primary?: boolean;
    is_active?: boolean;
  }): Promise<ApiResponse<CompanyContactList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/companies/${companyId}/contacts${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<CompanyContactList>(url);
  },

  // 创建企业联系人
  createCompanyContact: async (companyId: number, data: CompanyContactCreate): Promise<ApiResponse<CompanyContact>> => {
    return api.post<CompanyContact>(`/api/v1/companies/${companyId}/contacts`, data);
  },

  // 更新企业联系人
  updateCompanyContact: async (companyId: number, contactId: number, data: CompanyContactUpdate): Promise<ApiResponse<CompanyContact>> => {
    return api.put<CompanyContact>(`/api/v1/companies/${companyId}/contacts/${contactId}`, data);
  },

  // 删除企业联系人
  deleteCompanyContact: async (companyId: number, contactId: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/companies/${companyId}/contacts/${contactId}`);
  },
};

// AI生成相关API
export const aiGenerationApi = {
  // 获取AI生成记录列表
  getAIGenerations: async (params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    document_id?: number;
    status?: AIGenerationStatus;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<AIGenerationList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/ai-generations${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<AIGenerationList>(url);
  },

  // 创建AI生成记录
  createAIGeneration: async (data: AIGenerationCreate): Promise<ApiResponse<AIGeneration>> => {
    return api.post<AIGeneration>('/api/v1/ai-generations', data);
  },

  // 获取AI生成记录详情
  getAIGeneration: async (id: number): Promise<ApiResponse<AIGenerationWithDetails>> => {
    return api.get<AIGenerationWithDetails>(`/api/v1/ai-generations/${id}`);
  },

  // 更新AI生成记录
  updateAIGeneration: async (id: number, data: AIGenerationUpdate): Promise<ApiResponse<AIGeneration>> => {
    return api.put<AIGeneration>(`/api/v1/ai-generations/${id}`, data);
  },

  // 删除AI生成记录
  deleteAIGeneration: async (id: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/ai-generations/${id}`);
  },

  // 生成AI内容
  generateContent: async (request: AIGenerationRequest, documentId: number): Promise<ApiResponse<AIGenerationResponse>> => {
    return api.post<AIGenerationResponse>(`/api/v1/ai-generations/generate?document_id=${documentId}`, request);
  },

  // 生成应急预案
  generateEmergencyPlan: async (
    planType: string,
    companyInfo: Record<string, any>,
    documentId: number
  ): Promise<ApiResponse<AIGenerationResponse>> => {
    return api.post<AIGenerationResponse>(
      `/api/v1/ai-generations/generate/emergency-plan?plan_type=${planType}&document_id=${documentId}`,
      companyInfo
    );
  },

  // 生成环评报告
  generateEnvironmentalAssessment: async (
    projectInfo: Record<string, any>,
    documentId: number
  ): Promise<ApiResponse<AIGenerationResponse>> => {
    return api.post<AIGenerationResponse>(
      `/api/v1/ai-generations/generate/environmental-assessment?document_id=${documentId}`,
      projectInfo
    );
  },

  // 检查生成状态
  checkGenerationStatus: async (id: number): Promise<ApiResponse<AIGenerationStatusInfo>> => {
    return api.get<AIGenerationStatusInfo>(`/api/v1/ai-generations/${id}/status`);
  },

  // 启动异步处理
  processGenerationAsync: async (id: number): Promise<ApiResponse<any>> => {
    return api.post<any>(`/api/v1/ai-generations/${id}/process`);
  },

  // 模板管理相关API
  // 获取所有模板
  getAllTemplates: async (): Promise<ApiResponse<AIGenerationTemplateList>> => {
    return api.get<AIGenerationTemplateList>('/api/v1/ai-generations/templates');
  },

  // 根据类型获取模板
  getTemplateByType: async (templateType: string): Promise<ApiResponse<AIGenerationTemplate>> => {
    return api.get<AIGenerationTemplate>(`/api/v1/ai-generations/templates/${templateType}`);
  },
};

// 文档相关API
export const documentApi = {
  // 获取文档列表
  getDocuments: async (params?: {
    skip?: number;
    limit?: number;
    project_id?: number;
    status?: DocumentStatus;
    format?: DocumentFormat;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<DocumentList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/documents${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<DocumentList>(url);
  },

  // 创建文档
  createDocument: async (data: DocumentCreate): Promise<ApiResponse<Document>> => {
    return api.post<Document>('/api/v1/documents', data);
  },

  // 获取文档详情
  getDocument: async (id: number): Promise<ApiResponse<DocumentWithDetails>> => {
    return api.get<DocumentWithDetails>(`/api/v1/documents/${id}`);
  },

  // 更新文档
  updateDocument: async (id: number, data: DocumentUpdate): Promise<ApiResponse<Document>> => {
    return api.put<Document>(`/api/v1/documents/${id}`, data);
  },

  // 删除文档
  deleteDocument: async (id: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/documents/${id}`);
  },

  // 更新文档状态
  updateDocumentStatus: async (id: number, status: DocumentStatus): Promise<ApiResponse<Document>> => {
    return api.put<Document>(`/api/v1/documents/${id}/status`, { status });
  },

  // 搜索文档
  searchDocuments: async (searchParams: DocumentSearch, params?: {
    skip?: number;
    limit?: number;
    order_by?: string;
    order_desc?: boolean;
  }): Promise<ApiResponse<DocumentList>> => {
    const queryParams = new URLSearchParams();
    
    // 添加搜索参数
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
    
    // 添加分页和排序参数
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/documents/search${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<DocumentList>(url);
  },

  // 获取文档统计
  getDocumentStatistics: async (project_id?: number): Promise<ApiResponse<DocumentStatistics>> => {
    const queryParams = project_id ? `?project_id=${project_id}` : '';
    return api.get<DocumentStatistics>(`/api/v1/documents/statistics${queryParams}`);
  },

  // 文档版本相关API
  // 获取文档版本列表
  getDocumentVersions: async (documentId: number, params?: {
    skip?: number;
    limit?: number;
  }): Promise<ApiResponse<DocumentVersionList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/documents/${documentId}/versions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<DocumentVersionList>(url);
  },

  // 创建文档版本
  createDocumentVersion: async (documentId: number, data: DocumentVersionCreate): Promise<ApiResponse<DocumentVersion>> => {
    return api.post<DocumentVersion>(`/api/v1/documents/${documentId}/versions`, data);
  },

  // 获取文档版本详情
  getDocumentVersion: async (documentId: number, versionId: number): Promise<ApiResponse<DocumentVersionWithDetails>> => {
    return api.get<DocumentVersionWithDetails>(`/api/v1/documents/${documentId}/versions/${versionId}`);
  },

  // 恢复到指定版本
  restoreDocumentVersion: async (documentId: number, versionId: number): Promise<ApiResponse<Document>> => {
    return api.post<Document>(`/api/v1/documents/${documentId}/versions/${versionId}/restore`);
  },

  // 导出文档
  exportDocument: async (id: number, request: DocumentExportRequest): Promise<ApiResponse<DocumentExportResponse>> => {
    return api.post<DocumentExportResponse>(`/api/v1/documents/${id}/export`, request);
  },

  // 获取导出状态
  getExportStatus: async (exportId: number): Promise<ApiResponse<DocumentExportWithDetails>> => {
    return api.get<DocumentExportWithDetails>(`/api/v1/documents/exports/${exportId}`);
  },

  // 获取导出历史
  getExportHistory: async (params?: {
    document_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<ApiResponse<DocumentExportList>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/documents/exports${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<DocumentExportList>(url);
  },

  // 删除导出记录
  deleteExport: async (exportId: number): Promise<ApiResponse<any>> => {
    return api.delete<any>(`/api/v1/documents/exports/${exportId}`);
  },

  // 下载导出文件
  downloadExportFile: async (exportId: number, filename?: string): Promise<void> => {
    return api.download(`/api/v1/documents/exports/${exportId}/download`, filename);
  },

  // 获取导出模板
  getExportTemplates: async (format?: ExportFormat): Promise<ApiResponse<ExportTemplateList>> => {
    const queryParams = format ? `?format=${format}` : '';
    return api.get<ExportTemplateList>(`/api/v1/documents/exports/templates${queryParams}`);
  },

  // 获取导出统计
  getExportStatistics: async (params?: {
    days?: number;
  }): Promise<ApiResponse<ExportStatistics>> => {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/documents/exports/statistics${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return api.get<ExportStatistics>(url);
  },

  // 自动保存文档
  autoSaveDocument: async (id: number, data: DocumentUpdate): Promise<ApiResponse<Document>> => {
    return api.patch<Document>(`/api/v1/documents/${id}/autosave`, data);
  },
};

// 文件管理相关API
export const fileApi = {
// 上传文件
uploadFile: async (file: File, params?: {
  prefix?: string;
  backup_to_cloud?: boolean;
  metadata?: Record<string, string>;
}): Promise<ApiResponse<FileUploadResponse>> => {
  return api.uploadWithParams<FileUploadResponse>('/api/v1/files/upload', file, params);
},

// 分片上传文件
uploadFileChunk: async (data: FileChunkUploadRequest): Promise<ApiResponse<FileChunkUploadResponse>> => {
  return api.post<FileChunkUploadResponse>('/api/v1/files/upload/chunk', data);
},

// 获取上传进度
getUploadProgress: async (fileId: string): Promise<ApiResponse<FileUploadProgress>> => {
  return api.get<FileUploadProgress>(`/api/v1/files/upload/progress/${fileId}`);
},

// 下载文件
downloadFile: async (fileId: string, params?: {
  from_cloud?: boolean;
}): Promise<ApiResponse<any>> => {
  const queryParams = params ? new URLSearchParams(Object.entries(params).filter(([_, v]) => v !== undefined).map(([k, v]) => [k, v.toString()])) : '';
  return api.get<any>(`/api/v1/files/download/${fileId}${queryParams ? `?${queryParams}` : ''}`);
},

// 删除文件
deleteFile: async (data: FileDeleteRequest): Promise<ApiResponse<FileOperationResponse>> => {
  return api.post<FileOperationResponse>('/api/v1/files/delete', data);
},

// 获取文件列表
getFiles: async (params?: {
  prefix?: string;
  storage_type?: string;
  limit?: number;
}): Promise<ApiResponse<FileListResponse>> => {
  const queryParams = new URLSearchParams();
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
  }
  
  const url = `/api/v1/files/list${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  return api.get<FileListResponse>(url);
},

// 获取文件信息
getFileInfo: async (fileId: string): Promise<ApiResponse<FileInfo>> => {
  return api.get<FileInfo>(`/api/v1/files/info/${fileId}`);
},

// 同步文件到云存储
syncFileToCloud: async (data: FileSyncRequest): Promise<ApiResponse<FileOperationResponse>> => {
  return api.post<FileOperationResponse>('/api/v1/files/sync', data);
},

// 备份文件到云存储
backupFileToCloud: async (data: FileBackupRequest): Promise<ApiResponse<FileOperationResponse>> => {
  return api.post<FileOperationResponse>('/api/v1/files/backup', data);
},

// 生成预签名URL
generatePresignedUrl: async (data: FilePresignedUrlRequest): Promise<ApiResponse<Record<string, string>>> => {
  return api.post<Record<string, string>>('/api/v1/files/presigned-url', data);
},

// 切换存储类型
switchStorageType: async (data: FileStorageSwitchRequest): Promise<ApiResponse<FileOperationResponse>> => {
  return api.post<FileOperationResponse>('/api/v1/files/storage/switch', data);
},

// 获取存储状态
getStorageStatus: async (): Promise<ApiResponse<FileStorageStatus>> => {
  return api.get<FileStorageStatus>('/api/v1/files/storage/status');
},
};

// 导出类型
export type { AxiosRequestConfig, AxiosResponse, AxiosError }