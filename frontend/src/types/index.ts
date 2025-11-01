// 用户相关类型
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  company_id?: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 企业相关类型
export interface Company {
  id: number;
  name: string;
  unified_social_credit_code?: string;
  legal_representative?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  industry?: string;
  business_scope?: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyWithDetails extends Company {
  projects_count?: number;
  active_projects_count?: number;
  completed_projects_count?: number;
  documents_count?: number;
}

export interface CompanyList {
  companies: CompanyWithDetails[];
  total: number;
  page: number;
  size: number;
}

export interface CompanyCreate {
  name: string;
  unified_social_credit_code?: string;
  legal_representative?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  industry?: string;
  business_scope?: string;
}

export interface CompanyUpdate {
  name?: string;
  unified_social_credit_code?: string;
  legal_representative?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  industry?: string;
  business_scope?: string;
}

export interface CompanySearch {
  keyword?: string;
  industry?: string;
  unified_social_credit_code?: string;
  legal_representative?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  created_after?: string;
  created_before?: string;
}

export interface CompanyStatistics {
  total_companies: number;
  active_companies: number;
  new_companies_today: number;
  new_companies_this_week: number;
  new_companies_this_month: number;
  companies_by_industry: Record<string, number>;
  company_registration_trend: Array<Record<string, any>>;
  top_industries: Array<Record<string, any>>;
}

// 企业验证相关类型
export interface CompanyVerification {
  id?: number;
  company_id: number;
  verification_type: string;
  verification_status: string;
  verification_data: Record<string, any>;
  verified_by?: number;
  verified_at?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CompanyVerificationCreate {
  company_id: number;
  verification_type: string;
  verification_data: Record<string, any>;
  notes?: string;
}

export interface CompanyVerificationUpdate {
  verification_status: string;
  verified_by?: number;
  verified_at?: string;
  notes?: string;
}

export interface CompanyVerificationWithDetails extends CompanyVerification {
  company_name?: string;
  verified_by_name?: string;
}

export interface CompanyVerificationList {
  verifications: CompanyVerificationWithDetails[];
  total: number;
  page: number;
  size: number;
}

// 企业文档相关类型
export interface CompanyDocument {
  id?: number;
  company_id: number;
  document_type: string;
  document_name: string;
  file_url: string;
  file_size: number;
  upload_by: number;
  is_verified: boolean;
  verified_by?: number;
  verified_at?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CompanyDocumentCreate {
  company_id: number;
  document_type: string;
  document_name: string;
  file_url: string;
  file_size: number;
  notes?: string;
}

export interface CompanyDocumentUpdate {
  document_type?: string;
  document_name?: string;
  file_url?: string;
  file_size?: number;
  is_verified?: boolean;
  verified_by?: number;
  verified_at?: string;
  notes?: string;
}

export interface CompanyDocumentWithDetails extends CompanyDocument {
  company_name?: string;
  upload_by_name?: string;
  verified_by_name?: string;
}

export interface CompanyDocumentList {
  documents: CompanyDocumentWithDetails[];
  total: number;
  page: number;
  size: number;
}

// 企业联系人相关类型
export interface CompanyContact {
  id?: number;
  company_id: number;
  name: string;
  position?: string;
  phone?: string;
  email?: string;
  department?: string;
  is_primary: boolean;
  is_active: boolean;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CompanyContactCreate {
  company_id: number;
  name: string;
  position?: string;
  phone?: string;
  email?: string;
  department?: string;
  is_primary: boolean;
  notes?: string;
}

export interface CompanyContactUpdate {
  name?: string;
  position?: string;
  phone?: string;
  email?: string;
  department?: string;
  is_primary?: boolean;
  is_active?: boolean;
  notes?: string;
}

export interface CompanyContactWithDetails extends CompanyContact {
  company_name?: string;
}

export interface CompanyContactList {
  contacts: CompanyContactWithDetails[];
  total: number;
  page: number;
  size: number;
}

// 项目相关类型
export interface Project {
  id: number;
  name: string;
  description?: string;
  type: ProjectType;
  status: ProjectStatus;
  user_id: number;
  company_id?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  metadata?: Record<string, any>;
}

export interface ProjectWithDetails extends Project {
  user_name?: string;
  company_name?: string;
  documents_count?: number;
  forms_count?: number;
  progress?: number;
}

export interface ProjectList {
  projects: ProjectWithDetails[];
  total: number;
  page: number;
  size: number;
}

export enum ProjectType {
  EMERGENCY_PLAN = 'emergency_plan',
  ENVIRONMENTAL_ASSESSMENT = 'environmental_assessment',
}

export enum ProjectStatus {
  DRAFT = 'draft',
  GENERATING = 'generating',
  REVIEWING = 'reviewing',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

// 项目表单相关类型
export interface ProjectForm {
  id: number;
  project_id: number;
  form_type: string;
  form_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ProjectFormWithDetails extends ProjectForm {
  project_name?: string;
  fields_count?: number;
}

export interface ProjectFormList {
  forms: ProjectFormWithDetails[];
  total: number;
  page: number;
  size: number;
}

export interface ProjectFormCreate {
  project_id: number;
  form_type: string;
  form_data: Record<string, any>;
}

export interface ProjectFormUpdate {
  form_type?: string;
  form_data?: Record<string, any>;
}

// 项目统计相关类型
export interface ProjectStatistics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  projects_by_type: Record<string, number>;
  projects_by_status: Record<string, number>;
  new_projects_today: number;
  new_projects_this_week: number;
  new_projects_this_month: number;
  project_creation_trend: Array<Record<string, any>>;
  average_completion_time?: number;
}

// 项目进度相关类型
export interface ProjectProgress {
  project_id: number;
  total_steps: number;
  completed_steps: number;
  progress_percentage: number;
  current_step?: string;
  next_step?: string;
  estimated_completion?: string;
}

// 文档相关类型
export enum DocumentFormat {
  MARKDOWN = "markdown",
  HTML = "html",
  PLAIN_TEXT = "plain_text"
}

export enum DocumentStatus {
  DRAFT = "draft",
  REVIEWING = "reviewing",
  APPROVED = "approved",
  PUBLISHED = "published"
}

export interface Document {
  id: number;
  title: string;
  content?: string;
  format: DocumentFormat;
  status: DocumentStatus;
  project_id: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface DocumentWithDetails extends Document {
  project_name?: string;
  versions_count?: number;
  ai_generations_count?: number;
  exports_count?: number;
}

export interface DocumentCreate {
  title: string;
  content?: string;
  format?: DocumentFormat;
  status?: DocumentStatus;
  project_id: number;
  metadata?: Record<string, any>;
}

export interface DocumentUpdate {
  title?: string;
  content?: string;
  format?: DocumentFormat;
  status?: DocumentStatus;
  metadata?: Record<string, any>;
}

export interface DocumentList {
  documents: DocumentWithDetails[];
  total: number;
  page: number;
  size: number;
}

export interface DocumentVersion {
  id: number;
  document_id: number;
  version_number: number;
  content: string;
  changes_summary?: Record<string, any>;
  created_by: number;
  created_at: string;
}

export interface DocumentVersionWithDetails extends DocumentVersion {
  document_title?: string;
  created_by_name?: string;
}

export interface DocumentVersionCreate {
  document_id: number;
  version_number: number;
  content: string;
  changes_summary?: Record<string, any>;
  created_by: number;
}

export interface DocumentVersionList {
  versions: DocumentVersionWithDetails[];
  total: number;
  document_id: number;
}

export interface DocumentSection {
  id: string;
  title: string;
  content?: string;
  order: number;
  document_id: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentSearch {
  keyword?: string;
  project_id?: number;
  status?: DocumentStatus;
  format?: DocumentFormat;
  created_after?: string;
  created_before?: string;
  updated_after?: string;
  updated_before?: string;
}

export interface DocumentStatistics {
  total_documents: number;
  draft_documents: number;
  reviewing_documents: number;
  approved_documents: number;
  published_documents: number;
  documents_by_format: Record<string, number>;
  documents_by_project: Record<string, number>;
  new_documents_today: number;
  new_documents_this_week: number;
  new_documents_this_month: number;
  document_creation_trend: Array<Record<string, any>>;
}

// AI生成相关类型
export enum AIGenerationStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface AIGeneration {
  id: number;
  document_id: number;
  user_id: number;
  prompt: string;
  generation_config?: Record<string, any>;
  generated_content?: string;
  status: AIGenerationStatus;
  metadata?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface AIGenerationWithDetails extends AIGeneration {
  document_title?: string;
  user_name?: string;
  processing_time?: number;
}

export interface AIGenerationList {
  generations: AIGenerationWithDetails[];
  total: number;
  page: number;
  size: number;
}

export interface AIGenerationCreate {
  document_id: number;
  user_id?: number;
  prompt: string;
  generation_config?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface AIGenerationUpdate {
  status?: AIGenerationStatus;
  generated_content?: string;
  metadata?: Record<string, any>;
  completed_at?: string;
}

export interface AIGenerationRequest {
  prompt: string;
  context?: string;
  generation_config?: AIGenerationConfig;
  section?: string;
}

export interface AIGenerationResponse {
  id: number;
  status: AIGenerationStatus;
  generated_content?: string;
  message?: string;
  processing_time?: number;
}

export interface AIGenerationConfig {
  model: string;
  temperature: number;
  max_tokens: number;
  top_p: number;
  frequency_penalty: number;
  presence_penalty: number;
  stop_sequences?: string[];
  system_prompt?: string;
}

export interface AIGenerationTemplate {
  id?: number;
  name: string;
  description?: string;
  prompt_template: string;
  config: AIGenerationConfig;
  category?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AIGenerationTemplateCreate {
  name: string;
  description?: string;
  prompt_template: string;
  config: AIGenerationConfig;
  category?: string;
}

export interface AIGenerationTemplateUpdate {
  name?: string;
  description?: string;
  prompt_template?: string;
  config?: AIGenerationConfig;
  category?: string;
  is_active?: boolean;
}

export interface AIGenerationTemplateList {
  templates: AIGenerationTemplate[];
  total: number;
  page: number;
  size: number;
}

export interface AIGenerationStatusInfo {
  id: number;
  status: AIGenerationStatus;
  progress?: number;
  message?: string;
  created_at: string;
  updated_at: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 认证相关类型
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

// 表单相关类型
export interface FormFieldError {
  field: string;
  message: string;
}

export interface FormState {
  isSubmitting: boolean;
  errors: FormFieldError[];
}

// 主题相关类型
export type Theme = 'light' | 'dark' | 'system';

// 路由相关类型
export interface Route {
  path: string;
  name: string;
  icon?: string;
  protected?: boolean;
  children?: Route[];
}

// 通知相关类型
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  created_at: string;
}

// 文档导出相关类型
export enum ExportFormat {
  PDF = 'pdf',
  WORD = 'word',
  HTML = 'html',
  MARKDOWN = 'markdown'
}

export enum ExportStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface DocumentExport {
  id: number;
  document_id: number;
  user_id: number;
  format: ExportFormat;
  file_url?: string;
  file_name?: string;
  file_size?: number;
  created_at: string;
}

export interface DocumentExportWithDetails extends DocumentExport {
  document_title?: string;
  user_name?: string;
  status?: ExportStatus;
  error_message?: string;
  download_url?: string;
}

export interface DocumentExportList {
  exports: DocumentExportWithDetails[];
  total: number;
  page: number;
  size: number;
}

export interface DocumentExportRequest {
  format: ExportFormat;
  include_metadata?: boolean;
  include_versions?: boolean;
  watermark?: string;
  page_size?: string;
  margin?: string;
  header?: string;
  footer?: string;
  table_of_contents?: boolean;
}

export interface DocumentExportResponse {
  export_id: number;
  status: ExportStatus;
  message?: string;
  download_url?: string;
  file_name?: string;
  file_size?: number;
  estimated_time?: number;
}

export interface ExportOptions {
  // PDF选项
  pdf_page_size?: string;
  pdf_orientation?: string;
  pdf_margin_top?: number;
  pdf_margin_bottom?: number;
  pdf_margin_left?: number;
  pdf_margin_right?: number;
  pdf_font_size?: number;
  pdf_line_height?: number;
  
  // Word选项
  word_page_size?: string;
  word_orientation?: string;
  word_margin_top?: number;
  word_margin_bottom?: number;
  word_margin_left?: number;
  word_margin_right?: number;
  word_font_size?: number;
  word_line_height?: number;
  
  // HTML选项
  html_css_style?: string;
  html_include_toc?: boolean;
  html_responsive?: boolean;
  
  // 通用选项
  include_header?: boolean;
  include_footer?: boolean;
  include_page_numbers?: boolean;
  include_watermark?: boolean;
  watermark_text?: string;
  watermark_opacity?: number;
}

export interface ExportTemplate {
  id?: number;
  name: string;
  description?: string;
  format: ExportFormat;
  options: ExportOptions;
  is_default?: boolean;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ExportTemplateCreate {
  name: string;
  description?: string;
  format: ExportFormat;
  options: ExportOptions;
  is_default?: boolean;
}

export interface ExportTemplateUpdate {
  name?: string;
  description?: string;
  options?: ExportOptions;
  is_default?: boolean;
  is_active?: boolean;
}

export interface ExportTemplateList {
  templates: ExportTemplate[];
  total: number;
  page: number;
  size: number;
}

export interface ExportStatistics {
  total_exports: number;
  successful_exports: number;
  failed_exports: number;
  exports_by_format: Record<string, number>;
  exports_by_user: Record<string, number>;
  average_file_size?: number;
  total_file_size?: number;
  most_exported_documents: Array<Record<string, any>>;
}

// 文件管理相关类型
export interface FileUploadRequest {
  prefix?: string;
  backup_to_cloud?: boolean;
  metadata?: Record<string, string>;
}

export interface FileUploadResponse {
  filename: string;
  original_filename: string;
  file_path: string;
  object_key?: string;
  file_url?: string;
  file_size: number;
  file_hash: string;
  content_type?: string;
  storage_type: string;
  metadata?: Record<string, any>;
  local_backup_path?: string;
  cloud_backup_path?: string;
  file_id?: string;
}

export interface FileDownloadRequest {
  file_path: string;
  local_path?: string;
  from_cloud?: boolean;
}

export interface FileDeleteRequest {
  file_path: string;
  delete_from_cloud?: boolean;
}

export interface FileListRequest {
  prefix?: string;
  storage_type?: string;
  limit?: number;
}

export interface FileListResponse {
  files: FileInfo[];
  total: number;
  prefix: string;
}

export interface FileInfo {
  filename: string;
  file_path: string;
  file_size: number;
  last_modified?: string;
  storage_type?: string;
  file_url?: string;
  etag?: string;
  content_type?: string;
  metadata?: Record<string, any>;
}

export interface FileSyncRequest {
  local_file_path: string;
  cloud_file_path?: string;
  force_upload?: boolean;
}

export interface FileBackupRequest {
  local_file_path: string;
  backup_prefix?: string;
}

export interface FilePresignedUrlRequest {
  file_path: string;
  expires_in?: number;
  method?: string;
}

export interface FileStorageSwitchRequest {
  storage_type: string;
}

export interface FileStorageStatus {
  current_type: string;
  local_available: boolean;
  cloud_available: boolean;
  upload_dir: string;
  cloud_bucket?: string;
  cloud_region?: string;
  cloud_domain?: string;
}

export interface FileOperationResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

export interface FileUploadProgress {
  file_id: string;
  filename: string;
  total_size: number;
  uploaded_size: number;
  progress: number;
  status: string;
  message?: string;
  created_at: string;
  updated_at: string;
}

export interface FileChunkUploadRequest {
  file_id: string;
  chunk_index: number;
  total_chunks: number;
  chunk_data: Blob;
  chunk_hash: string;
  file_hash: string;
  filename: string;
  file_size: number;
  content_type?: string;
}

export interface FileChunkUploadResponse {
  chunk_index: number;
  uploaded: boolean;
  message: string;
  next_chunk_index?: number;
  upload_complete?: boolean;
  file_info?: FileUploadResponse;
}