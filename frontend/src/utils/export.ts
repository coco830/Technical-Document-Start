/**
 * 文档导出工具函数
 */

import { apiClient } from './api'

export interface ExportOptions {
  documentId: number
  format: 'pdf' | 'docx'
  includeMetadata?: boolean
}

export interface BatchExportOptions {
  documentIds: number[]
  format: 'pdf' | 'docx'
  customFilename?: string
}

/**
 * 导出单个文档
 * @param options 导出选项
 * @returns 下载的 Blob
 */
export async function exportDocument(options: ExportOptions): Promise<void> {
  const { documentId, format, includeMetadata = true } = options

  try {
    const response = await apiClient.post(
      `/api/export/document/${documentId}`,
      null,
      {
        params: {
          format,
          include_metadata: includeMetadata,
        },
        responseType: 'blob',
      }
    )

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `document_${documentId}.${format}`

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename=(.+)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('导出失败:', error)
    throw new Error(error.response?.data?.detail || '导出失败，请稍后重试')
  }
}

/**
 * 批量导出文档
 * @param options 批量导出选项
 * @returns 下载的 Blob
 */
export async function exportBatch(options: BatchExportOptions): Promise<void> {
  const { documentIds, format, customFilename } = options

  try {
    const response = await apiClient.post(
      '/api/export/batch',
      {
        document_ids: documentIds,
        format,
        custom_filename: customFilename,
      },
      {
        responseType: 'blob',
      }
    )

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `batch_export.${format}`

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename=(.+)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('批量导出失败:', error)
    throw new Error(error.response?.data?.detail || '批量导出失败，请稍后重试')
  }
}

/**
 * 获取支持的导出格式
 * @returns 支持的格式列表
 */
export async function getSupportedFormats() {
  try {
    const response = await apiClient.get('/api/export/formats')
    return response.data.formats
  } catch (error) {
    console.error('获取支持格式失败:', error)
    return []
  }
}
