'use client'

import React, { useState, useRef, useCallback } from 'react'
import { Upload, Button, Progress, message, Card, Space, Typography, Switch, Input, Form, Select } from 'antd'
import type { UploadProps as AntUploadProps } from 'antd/es/upload/interface'
import { InboxOutlined, CloudUploadOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons'
import { fileApi } from '@/lib/api'
import { FileUploadRequest, FileUploadResponse, FileUploadProgress } from '@/types'
import type { UploadProps } from 'antd'

const { Dragger } = Upload
const { Title, Text, Paragraph } = Typography
const { Option } = Select

interface FileUploadProps {
  onUploadSuccess?: (response: FileUploadResponse) => void
  onUploadError?: (error: any) => void
  onProgress?: (progress: FileUploadProgress) => void
  maxFileSize?: number // MB
  allowedFileTypes?: string[]
  defaultPrefix?: string
  showAdvancedOptions?: boolean
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  onProgress,
  maxFileSize = 10,
  allowedFileTypes = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif'],
  defaultPrefix = 'uploads',
  showAdvancedOptions = false
}) => {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, FileUploadProgress>>({})
  const [useCloudStorage, setUseCloudStorage] = useState(true)
  const [prefix, setPrefix] = useState(defaultPrefix)
  const [metadata, setMetadata] = useState<Record<string, string>>({})
  const [chunkedUpload, setChunkedUpload] = useState(false)
  const [chunkSize, setChunkSize] = useState(5) // MB
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const progressTimers = useRef<Record<string, NodeJS.Timeout>>({})

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 验证文件
  const validateFile = (file: File): boolean => {
    // 检查文件类型
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedFileTypes.includes(fileExtension)) {
      message.error(`不支持的文件类型: ${fileExtension}`)
      return false
    }
    
    // 检查文件大小
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxFileSize) {
      message.error(`文件大小超过限制 (${maxFileSize}MB)`)
      return false
    }
    
    return true
  }

  // 上传文件
  const uploadFile = async (file: File): Promise<void> => {
    if (!validateFile(file)) return
    
    setUploading(true)
    
    try {
      const uploadRequest: FileUploadRequest = {
        prefix,
        backup_to_cloud: useCloudStorage,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined
      }
      
      if (chunkedUpload && file.size > chunkSize * 1024 * 1024) {
        // 分片上传
        await uploadFileInChunks(file, uploadRequest)
      } else {
        // 普通上传
        const response = await fileApi.uploadFile(file, uploadRequest)
        
        if (response.success && response.data) {
          message.success(`文件 ${file.name} 上传成功`)
          onUploadSuccess?.(response.data)
        } else {
          message.error(`文件上传失败: ${response.message || '未知错误'}`)
          onUploadError?.(response.message)
        }
      }
    } catch (error: any) {
      console.error('文件上传错误:', error)
      message.error(`文件上传失败: ${error.message || '未知错误'}`)
      onUploadError?.(error)
    } finally {
      setUploading(false)
    }
  }

  // 分片上传文件
  const uploadFileInChunks = async (file: File, uploadRequest: FileUploadRequest): Promise<void> => {
    const chunkSizeBytes = chunkSize * 1024 * 1024
    const totalChunks = Math.ceil(file.size / chunkSizeBytes)
    const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 创建初始进度记录
    const initialProgress: FileUploadProgress = {
      file_id: fileId,
      filename: file.name,
      total_size: file.size,
      uploaded_size: 0,
      progress: 0,
      status: 'uploading',
      message: '开始分片上传',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    setUploadProgress(prev => ({ ...prev, [fileId]: initialProgress }))
    onProgress?.(initialProgress)
    
    // 上传分片
    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
      const start = chunkIndex * chunkSizeBytes
      const end = Math.min(start + chunkSizeBytes, file.size)
      const chunk = file.slice(start, end)
      
      try {
        const chunkData = await fileToBase64(chunk)
        const chunkHash = await calculateHash(chunk)
        
        const chunkRequest = {
          file_id: fileId,
          chunk_index: chunkIndex,
          total_chunks: totalChunks,
          chunk_data: new Blob([chunk]),
          chunk_hash: chunkHash,
          file_hash: await calculateHash(file),
          filename: file.name,
          file_size: file.size,
          content_type: file.type
        }
        
        const response = await fileApi.uploadFileChunk(chunkRequest)
        
        if (response.success && response.data) {
          const chunkResult = response.data
          const extraFields = chunkResult as Partial<{ uploaded_size: number; progress: number }>
          const rawUploadedSize = extraFields.uploaded_size
          const uploadedSize =
            typeof rawUploadedSize === 'number'
              ? rawUploadedSize
              : Math.min((chunkIndex + 1) * chunkSizeBytes, file.size)
          const uploadComplete = chunkResult.upload_complete ?? false
          const nextChunkIndex = chunkResult.next_chunk_index
          const fileInfo = chunkResult.file_info
          const rawProgress = extraFields.progress
          const progressValue =
            typeof rawProgress === 'number' ? rawProgress : (uploadedSize / file.size) * 100
          const statusMessage =
            chunkResult.message || (uploadComplete ? '上传完成' : `上传分片 ${chunkIndex + 1}/${totalChunks}`)

          // 更新进度
          const updatedProgress: FileUploadProgress = {
            ...initialProgress,
            uploaded_size: uploadedSize,
            progress: progressValue,
            status: uploadComplete ? 'completed' : 'uploading',
            message: statusMessage,
            updated_at: new Date().toISOString()
          }

          setUploadProgress(prev => ({ ...prev, [fileId]: updatedProgress }))
          onProgress?.(updatedProgress)

          if (uploadComplete && fileInfo) {
            message.success(`文件 ${file.name} 上传成功`)
            onUploadSuccess?.(fileInfo)
            return
          }

          // 如果需要继续上传下一个分片
          if (nextChunkIndex !== undefined && nextChunkIndex < totalChunks) {
            // 继续下一个分片
            continue
          }
        } else {
          throw new Error(response.message || '分片上传失败')
        }
      } catch (error: any) {
        console.error(`分片 ${chunkIndex + 1} 上传失败:`, error)
        
        // 更新进度为失败
        const failedProgress: FileUploadProgress = {
          ...initialProgress,
          status: 'failed',
          message: `分片 ${chunkIndex + 1} 上传失败: ${error.message || '未知错误'}`,
          updated_at: new Date().toISOString()
        }
        
        setUploadProgress(prev => ({ ...prev, [fileId]: failedProgress }))
        onProgress?.(failedProgress)
        
        message.error(`文件上传失败: ${error.message || '未知错误'}`)
        onUploadError?.(error)
        return
      }
    }
  }

  // 文件转Base64
  const fileToBase64 = (file: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => {
        const result = reader.result as string
        // 移除data:image/...;base64,前缀
        const base64 = result.split(',')[1]
        resolve(base64)
      }
      reader.onerror = error => reject(error)
    })
  }

  // 计算文件哈希
  const calculateHash = async (data: Blob | string): Promise<string> => {
    let buffer: ArrayBuffer

    if (typeof data === 'string') {
      const byteCharacters = atob(data)
      const byteNumbers = new Uint8Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      buffer = byteNumbers.buffer
    } else {
      buffer = await data.arrayBuffer()
    }

    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    return hashHex
  }

  // 处理文件选择
  const handleFileChange: AntUploadProps['onChange'] = info => {
    const file = info.file.originFileObj
    if (file) {
      uploadFile(file as File)
    }
  }

  // 处理拖拽
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      uploadFile(files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  // 轮询上传进度
  const pollUploadProgress = useCallback((fileId: string) => {
    const poll = async () => {
      try {
        const response = await fileApi.getUploadProgress(fileId)
        
        if (response.success && response.data) {
          const progress = response.data
          setUploadProgress(prev => ({ ...prev, [fileId]: progress }))
          onProgress?.(progress)
          
          // 如果上传完成或失败，停止轮询
          if (progress.status === 'completed' || progress.status === 'failed') {
            if (progressTimers.current[fileId]) {
              clearTimeout(progressTimers.current[fileId])
              delete progressTimers.current[fileId]
            }
            return
          }
        }
      } catch (error) {
        console.error('获取上传进度失败:', error)
      }
      
      // 继续轮询
      progressTimers.current[fileId] = setTimeout(poll, 1000)
    }
    
    poll()
    
    // 清理函数
    return () => {
      if (progressTimers.current[fileId]) {
        clearTimeout(progressTimers.current[fileId])
        delete progressTimers.current[fileId]
      }
    }
  }, [onProgress])

  // 组件卸载时清理定时器
  React.useEffect(() => {
    return () => {
      Object.values(progressTimers.current).forEach(timer => clearTimeout(timer))
    }
  }, [])

  return (
    <Card title="文件上传" className="w-full">
      <Space direction="vertical" className="w-full">
        {showAdvancedOptions && (
          <div className="bg-gray-50 p-4 rounded-md mb-4">
            <Title level={5}>上传选项</Title>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <Text strong>存储位置:</Text>
                <div className="flex items-center mt-2">
                  <span className="mr-2">本地存储</span>
                  <Switch 
                    checked={useCloudStorage} 
                    onChange={setUseCloudStorage} 
                  />
                  <span className="ml-2">云存储</span>
                </div>
              </div>
              
              <div>
                <Text strong>存储前缀:</Text>
                <Input 
                  value={prefix} 
                  onChange={e => setPrefix(e.target.value)}
                  placeholder="例如: uploads/documents"
                  className="mt-2"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <Text strong>分片上传:</Text>
                <div className="flex items-center mt-2">
                  <span className="mr-2">关闭</span>
                  <Switch 
                    checked={chunkedUpload} 
                    onChange={setChunkedUpload} 
                  />
                  <span className="ml-2">开启</span>
                </div>
              </div>
              
              {chunkedUpload && (
                <div>
                  <Text strong>分片大小 (MB):</Text>
                  <Input 
                    type="number"
                    value={chunkSize} 
                    onChange={e => setChunkSize(Number(e.target.value))}
                    min={1}
                    max={100}
                    className="mt-2"
                  />
                </div>
              )}
            </div>
            
            <div>
              <Text strong>元数据 (可选):</Text>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                <Input 
                  placeholder="键" 
                  onChange={e => {
                    const key = e.target.value
                    if (key && !metadata[key]) {
                      setMetadata(prev => ({ ...prev, [key]: '' }))
                    }
                  }}
                />
                <Input 
                  placeholder="值" 
                  value={metadata[Object.keys(metadata).pop() || ''] || ''}
                  onChange={e => {
                    const lastKey = Object.keys(metadata).pop() || ''
                    if (lastKey) {
                      setMetadata(prev => ({ ...prev, [lastKey]: e.target.value }))
                    }
                  }}
                />
              </div>
            </div>
          </div>
        )}
        
        <Dragger
          name="file"
          multiple={false}
          onChange={handleFileChange}
          onDrop={handleDrop}
          beforeUpload={() => false} // 阻止自动上传
          disabled={uploading}
          className="w-full"
        >
          <p className="ant-upload-drag-icon">
            {useCloudStorage ? <CloudUploadOutlined /> : <InboxOutlined />}
          </p>
          <p className="ant-upload-text">
            点击或拖拽文件到此区域上传
          </p>
          <p className="ant-upload-hint">
            支持单个文件上传，文件类型: {allowedFileTypes.join(', ')}，最大大小: {maxFileSize}MB
          </p>
        </Dragger>
        
        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4">
            <Title level={5}>上传进度</Title>
            {Object.entries(uploadProgress).map(([fileId, progress]) => (
              <div key={fileId} className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <Text strong>{progress.filename}</Text>
                  <Text>{progress.progress.toFixed(1)}%</Text>
                </div>
                <Progress 
                  percent={progress.progress} 
                  status={progress.status === 'failed' ? 'exception' : 'active'}
                  format={() => `${formatFileSize(progress.uploaded_size)} / ${formatFileSize(progress.total_size)}`}
                />
                <div className="flex justify-between items-center mt-1">
                  <Text type="secondary">{progress.message}</Text>
                  {progress.status === 'completed' && (
                    <Button 
                      type="link" 
                      icon={<EyeOutlined />}
                      size="small"
                    >
                      查看
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div className="mt-4 flex justify-end">
          <Button 
            onClick={() => fileInputRef.current?.click()}
            loading={uploading}
            type="primary"
            icon={<CloudUploadOutlined />}
          >
            选择文件
          </Button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          style={{ display: 'none' }}
          onChange={e => {
            const files = e.target.files
            if (files && files.length > 0) {
              uploadFile(files[0])
            }
          }}
        />
      </Space>
    </Card>
  )
}

export default FileUpload
