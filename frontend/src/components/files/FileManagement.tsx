'use client'

import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Input, 
  Select, 
  Modal, 
  message, 
  Popconfirm, 
  Tag, 
  Tooltip, 
  Typography, 
  Switch,
  Progress,
  Form,
  Divider
} from 'antd'
import { 
  SearchOutlined, 
  DeleteOutlined, 
  DownloadOutlined, 
  EyeOutlined, 
  CloudUploadOutlined, 
  SyncOutlined, 
  InfoCircleOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons'
import { fileApi } from '@/lib/api'
import { 
  FileInfo, 
  FileListResponse, 
  FileStorageStatus, 
  FileOperationResponse,
  FileSyncRequest,
  FileBackupRequest,
  FilePresignedUrlRequest
} from '@/types'

const { Search } = Input
const { Option } = Select
const { Title, Text, Paragraph } = Typography
const { Item } = Form

interface FileManagementProps {
  prefix?: string
  showAdvancedOptions?: boolean
  onFileSelect?: (file: FileInfo) => void
  selectionMode?: boolean
}

const FileManagement: React.FC<FileManagementProps> = ({
  prefix = '',
  showAdvancedOptions = false,
  onFileSelect,
  selectionMode = false
}) => {
  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [storageType, setStorageType] = useState<string>('')
  const [storageStatus, setStorageStatus] = useState<FileStorageStatus | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [syncModalVisible, setSyncModalVisible] = useState(false)
  const [backupModalVisible, setBackupModalVisible] = useState(false)
  const [presignedModalVisible, setPresignedModalVisible] = useState(false)
  const [presignedUrl, setPresignedUrl] = useState('')
  const [syncForm] = Form.useForm()
  const [backupForm] = Form.useForm()
  const [presignedForm] = Form.useForm()
  const [switchStorageModalVisible, setSwitchStorageModalVisible] = useState(false)
  const [newStorageType, setNewStorageType] = useState('')

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 格式化日期
  const formatDate = (dateString: string): string => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  // 获取文件列表
  const fetchFiles = async () => {
    setLoading(true)
    try {
      const params: any = {
        prefix,
        limit: pageSize,
        skip: (currentPage - 1) * pageSize
      }
      
      if (storageType) {
        params.storage_type = storageType
      }
      
      const response = await fileApi.getFiles(params)
      
      if (response.success && response.data) {
        setFiles(response.data.files)
        setTotal(response.data.total)
      } else {
        message.error(`获取文件列表失败: ${response.message || '未知错误'}`)
      }
    } catch (error: any) {
      console.error('获取文件列表错误:', error)
      message.error(`获取文件列表失败: ${error.message || '未知错误'}`)
    } finally {
      setLoading(false)
    }
  }

  // 获取存储状态
  const fetchStorageStatus = async () => {
    try {
      const response = await fileApi.getStorageStatus()
      
      if (response.success && response.data) {
        setStorageStatus(response.data)
        setStorageType(response.data.current_type)
      } else {
        message.error(`获取存储状态失败: ${response.message || '未知错误'}`)
      }
    } catch (error: any) {
      console.error('获取存储状态错误:', error)
      message.error(`获取存储状态失败: ${error.message || '未知错误'}`)
    }
  }

  // 删除文件
  const deleteFile = async (file: FileInfo) => {
    try {
      const response = await fileApi.deleteFile({
        file_path: file.file_path,
        delete_from_cloud: true
      })
      
      if (response.success) {
        message.success(`文件 ${file.filename} 删除成功`)
        fetchFiles()
      } else {
        message.error(`删除文件失败: ${response.message}`)
      }
    } catch (error: any) {
      console.error('删除文件错误:', error)
      message.error(`删除文件失败: ${error.message || '未知错误'}`)
    }
  }

  // 下载文件
  const downloadFile = async (file: FileInfo) => {
    try {
      const response = await fileApi.downloadFile(file.file_path, {
        from_cloud: file.storage_type === 'cos'
      })
      
      if (response.success && response.data) {
        // 如果是云存储文件，返回下载URL
        if (file.storage_type === 'cos' && response.data.download_url) {
          window.open(response.data.download_url, '_blank')
        } else {
          // 本地文件，直接下载
          window.open(`/api/v1/files/download/${file.file_path}`, '_blank')
        }
        
        message.success(`文件 ${file.filename} 下载成功`)
      } else {
        message.error(`下载文件失败: ${response.message || '未知错误'}`)
      }
    } catch (error: any) {
      console.error('下载文件错误:', error)
      message.error(`下载文件失败: ${error.message || '未知错误'}`)
    }
  }

  // 同步文件到云存储
  const syncFileToCloud = async (values: any) => {
    try {
      const request: FileSyncRequest = {
        local_file_path: values.local_file_path,
        cloud_file_path: values.cloud_file_path,
        force_upload: values.force_upload || false
      }
      
      const response = await fileApi.syncFileToCloud(request)
      
      if (response.success) {
        message.success(`文件同步成功`)
        setSyncModalVisible(false)
        syncForm.resetFields()
        fetchFiles()
      } else {
        message.error(`文件同步失败: ${response.message}`)
      }
    } catch (error: any) {
      console.error('文件同步错误:', error)
      message.error(`文件同步失败: ${error.message || '未知错误'}`)
    }
  }

  // 备份文件到云存储
  const backupFileToCloud = async (values: any) => {
    try {
      const request: FileBackupRequest = {
        local_file_path: values.local_file_path,
        backup_prefix: values.backup_prefix || 'backups'
      }
      
      const response = await fileApi.backupFileToCloud(request)
      
      if (response.success) {
        message.success(`文件备份成功`)
        setBackupModalVisible(false)
        backupForm.resetFields()
        fetchFiles()
      } else {
        message.error(`文件备份失败: ${response.message}`)
      }
    } catch (error: any) {
      console.error('文件备份错误:', error)
      message.error(`文件备份失败: ${error.message || '未知错误'}`)
    }
  }

  // 生成预签名URL
  const generatePresignedUrl = async (values: any) => {
    try {
      const request: FilePresignedUrlRequest = {
        file_path: values.file_path,
        expires_in: values.expires_in || 3600,
        method: values.method || 'GET'
      }
      
      const response = await fileApi.generatePresignedUrl(request)
      
      if (response.success && response.data) {
        setPresignedUrl(response.data.presigned_url)
        setPresignedModalVisible(true)
      } else {
        message.error(`生成预签名URL失败: ${response.message || '未知错误'}`)
      }
    } catch (error: any) {
      console.error('生成预签名URL错误:', error)
      message.error(`生成预签名URL失败: ${error.message || '未知错误'}`)
    }
  }

  // 切换存储类型
  const switchStorageType = async () => {
    try {
      const response = await fileApi.switchStorageType({
        storage_type: newStorageType
      })
      
      if (response.success) {
        message.success(`存储类型切换成功`)
        setSwitchStorageModalVisible(false)
        fetchStorageStatus()
        fetchFiles()
      } else {
        message.error(`存储类型切换失败: ${response.message}`)
      }
    } catch (error: any) {
      console.error('存储类型切换错误:', error)
      message.error(`存储类型切换失败: ${error.message || '未知错误'}`)
    }
  }

  // 查看文件详情
  const viewFileDetails = (file: FileInfo) => {
    setSelectedFile(file)
    setDetailModalVisible(true)
  }

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value)
  }

  // 处理分页
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  // 处理存储类型变化
  const handleStorageTypeChange = (value: string) => {
    setStorageType(value)
    setCurrentPage(1)
  }

  // 处理表格选择变化
  const handleSelectionChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys)
    
    if (selectionMode && newSelectedRowKeys.length === 1) {
      const selectedFile = files.find(file => file.file_path === newSelectedRowKeys[0])
      if (selectedFile) {
        onFileSelect?.(selectedFile)
      }
    }
  }

  // 初始化
  useEffect(() => {
    fetchFiles()
    fetchStorageStatus()
  }, [currentPage, pageSize, storageType])

  // 表格列定义
  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string, record: FileInfo) => (
        <div className="flex items-center">
          <Text strong>{text}</Text>
          {record.storage_type === 'cos' && (
            <Tag color="blue" className="ml-2">云存储</Tag>
          )}
        </div>
      )
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => formatFileSize(size)
    },
    {
      title: '存储类型',
      dataIndex: 'storage_type',
      key: 'storage_type',
      render: (type: string) => (
        <Tag color={type === 'cos' ? 'blue' : 'green'}>
          {type === 'cos' ? '云存储' : '本地存储'}
        </Tag>
      )
    },
    {
      title: '最后修改',
      dataIndex: 'last_modified',
      key: 'last_modified',
      render: (date: string) => formatDate(date)
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: FileInfo) => (
        <Space size="middle">
          <Tooltip title="查看详情">
            <Button 
              type="link" 
              icon={<EyeOutlined />} 
              onClick={() => viewFileDetails(record)}
            />
          </Tooltip>
          
          <Tooltip title="下载">
            <Button 
              type="link" 
              icon={<DownloadOutlined />} 
              onClick={() => downloadFile(record)}
            />
          </Tooltip>
          
          <Popconfirm
            title="确定要删除这个文件吗?"
            onConfirm={() => deleteFile(record)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button 
                type="link" 
                danger 
                icon={<DeleteOutlined />} 
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ]

  // 行选择配置
  const rowSelection = selectionMode ? {
    selectedRowKeys,
    onChange: handleSelectionChange,
    type: 'radio' as const
  } : undefined

  return (
    <div className="file-management">
      <Card 
        title="文件管理" 
        extra={
          <Space>
            <Search
              placeholder="搜索文件"
              allowClear
              enterButton={<SearchOutlined />}
              style={{ width: 200 }}
              onSearch={handleSearch}
              onChange={e => handleSearch(e.target.value)}
            />
            
            <Select
              placeholder="存储类型"
              allowClear
              style={{ width: 120 }}
              value={storageType}
              onChange={handleStorageTypeChange}
            >
              <Option value="">全部</Option>
              <Option value="local">本地存储</Option>
              <Option value="cos">云存储</Option>
            </Select>
            
            {showAdvancedOptions && storageStatus && (
              <Button 
                icon={<InfoCircleOutlined />} 
                onClick={() => setSwitchStorageModalVisible(true)}
              >
                存储设置
              </Button>
            )}
          </Space>
        }
      >
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={files}
          rowKey="file_path"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: handlePageChange,
            onShowSizeChange: (current, size) => {
              setCurrentPage(current)
              setPageSize(size)
            }
          }}
        />
      </Card>
      
      {/* 文件详情模态框 */}
      <Modal
        title="文件详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedFile && (
          <div>
            <div className="mb-4">
              <Text strong>文件名:</Text>
              <div className="mt-1">{selectedFile.filename}</div>
            </div>
            
            <div className="mb-4">
              <Text strong>文件路径:</Text>
              <div className="mt-1">{selectedFile.file_path}</div>
            </div>
            
            <div className="mb-4">
              <Text strong>文件大小:</Text>
              <div className="mt-1">{formatFileSize(selectedFile.file_size)}</div>
            </div>
            
            <div className="mb-4">
              <Text strong>存储类型:</Text>
              <div className="mt-1">
                <Tag color={selectedFile.storage_type === 'cos' ? 'blue' : 'green'}>
                  {selectedFile.storage_type === 'cos' ? '云存储' : '本地存储'}
                </Tag>
              </div>
            </div>
            
            {selectedFile.last_modified && (
              <div className="mb-4">
                <Text strong>最后修改时间:</Text>
                <div className="mt-1">{formatDate(selectedFile.last_modified)}</div>
              </div>
            )}
            
            {selectedFile.content_type && (
              <div className="mb-4">
                <Text strong>文件类型:</Text>
                <div className="mt-1">{selectedFile.content_type}</div>
              </div>
            )}
            
            {selectedFile.metadata && Object.keys(selectedFile.metadata).length > 0 && (
              <div className="mb-4">
                <Text strong>元数据:</Text>
                <div className="mt-1">
                  <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                    {JSON.stringify(selectedFile.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
      
      {/* 存储设置模态框 */}
      {showAdvancedOptions && storageStatus && (
        <Modal
          title="存储设置"
          open={switchStorageModalVisible}
          onCancel={() => setSwitchStorageModalVisible(false)}
          footer={[
            <Button key="cancel" onClick={() => setSwitchStorageModalVisible(false)}>
              取消
            </Button>,
            <Button 
              key="switch" 
              type="primary" 
              onClick={switchStorageType}
              disabled={!newStorageType || newStorageType === storageStatus.current_type}
            >
              切换
            </Button>
          ]}
        >
          <div className="mb-4">
            <Title level={5}>当前存储状态</Title>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <Text strong>当前存储类型:</Text>
                <div className="mt-1">
                  <Tag color={storageStatus.current_type === 'cos' ? 'blue' : 'green'}>
                    {storageStatus.current_type === 'cos' ? '云存储' : '本地存储'}
                  </Tag>
                </div>
              </div>
              
              <div>
                <Text strong>本地存储可用:</Text>
                <div className="mt-1">
                  {storageStatus.local_available ? (
                    <Tag color="green" icon={<CheckCircleOutlined />}>可用</Tag>
                  ) : (
                    <Tag color="red" icon={<CloseCircleOutlined />}>不可用</Tag>
                  )}
                </div>
              </div>
              
              <div>
                <Text strong>云存储可用:</Text>
                <div className="mt-1">
                  {storageStatus.cloud_available ? (
                    <Tag color="green" icon={<CheckCircleOutlined />}>可用</Tag>
                  ) : (
                    <Tag color="red" icon={<CloseCircleOutlined />}>不可用</Tag>
                  )}
                </div>
              </div>
              
              <div>
                <Text strong>上传目录:</Text>
                <div className="mt-1">{storageStatus.upload_dir}</div>
              </div>
            </div>
            
            {storageStatus.cloud_available && (
              <div className="mb-4">
                <Title level={5}>云存储配置</Title>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Text strong>存储桶:</Text>
                    <div className="mt-1">{storageStatus.cloud_bucket || '-'}</div>
                  </div>
                  
                  <div>
                    <Text strong>区域:</Text>
                    <div className="mt-1">{storageStatus.cloud_region || '-'}</div>
                  </div>
                  
                  <div>
                    <Text strong>域名:</Text>
                    <div className="mt-1">{storageStatus.cloud_domain || '-'}</div>
                  </div>
                </div>
              </div>
            )}
            
            <Divider />
            
            <Title level={5}>切换存储类型</Title>
            
            <div className="mb-4">
              <Text strong>选择新的存储类型:</Text>
              <Select
                style={{ width: '100%', marginTop: 8 }}
                value={newStorageType}
                onChange={setNewStorageType}
                placeholder="请选择存储类型"
              >
                <Option value="local">本地存储</Option>
                {storageStatus.cloud_available && <Option value="cos">云存储</Option>}
              </Select>
            </div>
          </div>
        </Modal>
      )}
      
      {/* 同步文件模态框 */}
      <Modal
        title="同步文件到云存储"
        open={syncModalVisible}
        onCancel={() => setSyncModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setSyncModalVisible(false)}>
            取消
          </Button>,
          <Button key="sync" type="primary" onClick={() => syncForm.submit()}>
            同步
          </Button>
        ]}
      >
        <Form
          form={syncForm}
          layout="vertical"
          onFinish={syncFileToCloud}
        >
          <Form.Item
            name="local_file_path"
            label="本地文件路径"
            rules={[{ required: true, message: '请输入本地文件路径' }]}
          >
            <Input placeholder="例如: /path/to/local/file" />
          </Form.Item>
          
          <Form.Item
            name="cloud_file_path"
            label="云存储文件路径"
            rules={[{ required: true, message: '请输入云存储文件路径' }]}
          >
            <Input placeholder="例如: uploads/remote/file" />
          </Form.Item>
          
          <Form.Item
            name="force_upload"
            label="强制上传"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 备份文件模态框 */}
      <Modal
        title="备份文件到云存储"
        open={backupModalVisible}
        onCancel={() => setBackupModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setBackupModalVisible(false)}>
            取消
          </Button>,
          <Button key="backup" type="primary" onClick={() => backupForm.submit()}>
            备份
          </Button>
        ]}
      >
        <Form
          form={backupForm}
          layout="vertical"
          onFinish={backupFileToCloud}
        >
          <Form.Item
            name="local_file_path"
            label="本地文件路径"
            rules={[{ required: true, message: '请输入本地文件路径' }]}
          >
            <Input placeholder="例如: /path/to/local/file" />
          </Form.Item>
          
          <Form.Item
            name="backup_prefix"
            label="备份前缀"
            initialValue="backups"
          >
            <Input placeholder="例如: backups" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 预签名URL模态框 */}
      <Modal
        title="预签名URL"
        open={presignedModalVisible}
        onCancel={() => setPresignedModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPresignedModalVisible(false)}>
            关闭
          </Button>,
          <Button 
            key="copy" 
            type="primary" 
            onClick={() => {
              navigator.clipboard.writeText(presignedUrl)
              message.success('已复制到剪贴板')
            }}
          >
            复制URL
          </Button>
        ]}
      >
        <div>
          <Text strong>预签名URL:</Text>
          <div className="mt-2 p-2 bg-gray-100 rounded">
            <Text copyable>{presignedUrl}</Text>
          </div>
        </div>
      </Modal>
      
      {showAdvancedOptions && (
        <Card title="高级操作" className="mt-4">
          <Space wrap>
            <Button 
              icon={<SyncOutlined />} 
              onClick={() => setSyncModalVisible(true)}
            >
              同步文件
            </Button>
            
            <Button 
              icon={<CloudUploadOutlined />} 
              onClick={() => setBackupModalVisible(true)}
            >
              备份文件
            </Button>
            
            <Button 
              icon={<InfoCircleOutlined />} 
              onClick={() => {
                if (selectedFile) {
                  presignedForm.setFieldsValue({
                    file_path: selectedFile.file_path
                  })
                  generatePresignedUrl(presignedForm.getFieldsValue())
                } else {
                  message.warning('请先选择一个文件')
                }
              }}
            >
              生成预签名URL
            </Button>
          </Space>
        </Card>
      )}
    </div>
  )
}

export default FileManagement
