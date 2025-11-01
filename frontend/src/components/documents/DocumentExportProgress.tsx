import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  DocumentExportWithDetails, 
  ExportStatus, 
  ExportFormat 
} from '@/types';
import { documentApi } from '@/lib/api';
import { 
  CheckCircle, 
  Clock, 
  XCircle, 
  Download, 
  Trash2, 
  RefreshCw,
  FileText,
  File,
  Code,
  Globe
} from 'lucide-react';

interface DocumentExportProgressProps {
  exportId: number;
  onComplete?: (result: DocumentExportWithDetails) => void;
  onError?: (result: DocumentExportWithDetails) => void;
  onDelete?: (exportId: number) => void;
}

export function DocumentExportProgress({ 
  exportId, 
  onComplete, 
  onError, 
  onDelete 
}: DocumentExportProgressProps) {
  const [exportData, setExportData] = useState<DocumentExportWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  // 获取导出状态
  const fetchExportStatus = async () => {
    try {
      setLoading(true);
      const response = await documentApi.getExportStatus(exportId);
      if (response.success && response.data) {
        setExportData(response.data);
        
        // 根据状态触发回调
        if (response.data.status === ExportStatus.COMPLETED && onComplete) {
          onComplete(response.data);
        } else if (response.data.status === ExportStatus.FAILED && onError) {
          onError(response.data);
        }
      }
    } catch (error) {
      console.error('获取导出状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 删除导出记录
  const handleDelete = async () => {
    if (!exportData) return;
    
    if (window.confirm('确定要删除这个导出记录吗？')) {
      try {
        await documentApi.deleteExport(exportId);
        if (onDelete) {
          onDelete(exportId);
        }
      } catch (error) {
        console.error('删除导出记录失败:', error);
      }
    }
  };

  // 下载导出文件
  const handleDownload = async () => {
    if (!exportData || !exportData.download_url) return;
    
    try {
      await documentApi.downloadExportFile(exportId, exportData.file_name);
    } catch (error) {
      console.error('下载导出文件失败:', error);
    }
  };

  // 获取格式图标
  const getFormatIcon = (format: ExportFormat) => {
    switch (format) {
      case ExportFormat.PDF:
        return <FileText className="h-4 w-4" />;
      case ExportFormat.WORD:
        return <File className="h-4 w-4" />;
      case ExportFormat.HTML:
        return <Globe className="h-4 w-4" />;
      case ExportFormat.MARKDOWN:
        return <Code className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  // 获取状态图标
  const getStatusIcon = (status?: ExportStatus) => {
    switch (status) {
      case ExportStatus.PENDING:
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case ExportStatus.PROCESSING:
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case ExportStatus.COMPLETED:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case ExportStatus.FAILED:
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  // 获取状态文本
  const getStatusText = (status?: ExportStatus) => {
    switch (status) {
      case ExportStatus.PENDING:
        return '等待中';
      case ExportStatus.PROCESSING:
        return '处理中';
      case ExportStatus.COMPLETED:
        return '已完成';
      case ExportStatus.FAILED:
        return '失败';
      default:
        return '未知';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status?: ExportStatus) => {
    switch (status) {
      case ExportStatus.PENDING:
        return 'text-yellow-600 bg-yellow-50';
      case ExportStatus.PROCESSING:
        return 'text-blue-600 bg-blue-50';
      case ExportStatus.COMPLETED:
        return 'text-green-600 bg-green-50';
      case ExportStatus.FAILED:
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  // 格式化文件大小
  const formatFileSize = (size?: number) => {
    if (!size) return '未知';
    
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else {
      return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    }
  };

  // 初始加载
  useEffect(() => {
    fetchExportStatus();
  }, [exportId]);

  // 轮询处理中的导出
  useEffect(() => {
    if (exportData?.status === ExportStatus.PROCESSING && !polling) {
      setPolling(true);
      const interval = setInterval(fetchExportStatus, 3000); // 每3秒轮询一次
      
      return () => {
        clearInterval(interval);
        setPolling(false);
      };
    }
  }, [exportData?.status, polling]);

  if (!exportData) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center p-6">
          <div className="text-center">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
            <p className="text-sm text-gray-500">加载导出信息...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            {getFormatIcon(exportData.format)}
            <span>
              {exportData.document_title || '文档'} - {exportData.format.toUpperCase()}
            </span>
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(exportData.status)}`}>
              {getStatusIcon(exportData.status)}
              <span>{getStatusText(exportData.status)}</span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 导出信息 */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">创建时间:</span>
            <p className="font-medium">
              {new Date(exportData.created_at).toLocaleString()}
            </p>
          </div>
          <div>
            <span className="text-gray-500">文件大小:</span>
            <p className="font-medium">
              {formatFileSize(exportData.file_size)}
            </p>
          </div>
          <div>
            <span className="text-gray-500">创建用户:</span>
            <p className="font-medium">
              {exportData.user_name || '未知用户'}
            </p>
          </div>
          <div>
            <span className="text-gray-500">文件名:</span>
            <p className="font-medium truncate">
              {exportData.file_name || '未生成'}
            </p>
          </div>
        </div>

        {/* 错误信息 */}
        {exportData.status === ExportStatus.FAILED && exportData.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="flex">
              <XCircle className="h-4 w-4 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-700">
                <p className="font-medium">导出失败</p>
                <p className="mt-1">{exportData.error_message}</p>
              </div>
            </div>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex justify-end gap-2 pt-2">
          {exportData.status === ExportStatus.PROCESSING && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchExportStatus}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              刷新状态
            </Button>
          )}
          
          {exportData.status === ExportStatus.COMPLETED && exportData.download_url && (
            <Button 
              variant="default" 
              size="sm" 
              onClick={handleDownload}
            >
              <Download className="h-4 w-4 mr-2" />
              下载文件
            </Button>
          )}
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleDelete}
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            删除
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default DocumentExportProgress;