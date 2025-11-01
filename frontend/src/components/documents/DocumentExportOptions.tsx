import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  DocumentExportRequest, 
  ExportFormat, 
  ExportOptions,
  ExportTemplate
} from '@/types';
import { documentApi } from '@/lib/api';
import { 
  FileText, 
  File, 
  Code, 
  Globe,
  Settings,
  Download,
  Loader2
} from 'lucide-react';

interface DocumentExportOptionsProps {
  documentId: number;
  documentTitle: string;
  onExportStart?: (exportRequest: DocumentExportRequest) => void;
  onCancel?: () => void;
}

export function DocumentExportOptions({ 
  documentId, 
  documentTitle, 
  onExportStart, 
  onCancel 
}: DocumentExportOptionsProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>(ExportFormat.PDF);
  const [templates, setTemplates] = useState<ExportTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ExportTemplate | null>(null);
  const [loading, setLoading] = useState(false);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    // PDF选项
    pdf_page_size: 'A4',
    pdf_orientation: 'portrait',
    pdf_margin_top: 2.54,
    pdf_margin_bottom: 2.54,
    pdf_margin_left: 1.91,
    pdf_margin_right: 1.91,
    pdf_font_size: 12,
    pdf_line_height: 1.5,
    
    // Word选项
    word_page_size: 'A4',
    word_orientation: 'portrait',
    word_margin_top: 2.54,
    word_margin_bottom: 2.54,
    word_margin_left: 1.91,
    word_margin_right: 1.91,
    word_font_size: 12,
    word_line_height: 1.5,
    
    // HTML选项
    html_css_style: 'default',
    html_include_toc: false,
    html_responsive: true,
    
    // 通用选项
    include_header: false,
    include_footer: false,
    include_page_numbers: true,
    include_watermark: false,
    watermark_text: '',
    watermark_opacity: 0.1
  });

  // 获取导出模板
  const fetchTemplates = async (format: ExportFormat) => {
    try {
      setTemplatesLoading(true);
      const response = await documentApi.getExportTemplates(format);
      if (response.success && response.data) {
        setTemplates(response.data.templates);
        
        // 自动选择默认模板
        const defaultTemplate = response.data.templates.find(t => t.is_default);
        if (defaultTemplate) {
          setSelectedTemplate(defaultTemplate);
          setExportOptions(defaultTemplate.options);
        }
      }
    } catch (error) {
      console.error('获取导出模板失败:', error);
    } finally {
      setTemplatesLoading(false);
    }
  };

  // 格式变化时获取对应模板
  const handleFormatChange = (format: ExportFormat) => {
    setSelectedFormat(format);
    setSelectedTemplate(null);
    fetchTemplates(format);
  };

  // 模板变化时应用模板选项
  const handleTemplateChange = (template: ExportTemplate) => {
    setSelectedTemplate(template);
    setExportOptions(template.options);
  };

  // 开始导出
  const handleExport = async () => {
    try {
      setLoading(true);
      
      const exportRequest: DocumentExportRequest = {
        format: selectedFormat,
        include_metadata: true,
        include_versions: false,
        watermark: exportOptions.include_watermark ? exportOptions.watermark_text : undefined,
        page_size: selectedFormat === ExportFormat.PDF ? exportOptions.pdf_page_size : 
                   selectedFormat === ExportFormat.WORD ? exportOptions.word_page_size : 'A4',
        margin: 'normal',
        header: exportOptions.include_header ? '文档标题' : undefined,
        footer: exportOptions.include_footer ? '页脚' : undefined,
        table_of_contents: exportOptions.html_include_toc
      };
      
      const response = await documentApi.exportDocument(documentId, exportRequest);
      if (response.success && response.data) {
        if (onExportStart) {
          onExportStart(exportRequest);
        }
      }
    } catch (error) {
      console.error('导出失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取格式图标
  const getFormatIcon = (format: ExportFormat) => {
    switch (format) {
      case ExportFormat.PDF:
        return <FileText className="h-5 w-5" />;
      case ExportFormat.WORD:
        return <File className="h-5 w-5" />;
      case ExportFormat.HTML:
        return <Globe className="h-5 w-5" />;
      case ExportFormat.MARKDOWN:
        return <Code className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  // 获取格式名称
  const getFormatName = (format: ExportFormat) => {
    switch (format) {
      case ExportFormat.PDF:
        return 'PDF文档';
      case ExportFormat.WORD:
        return 'Word文档';
      case ExportFormat.HTML:
        return 'HTML网页';
      case ExportFormat.MARKDOWN:
        return 'Markdown文档';
      default:
        return '未知格式';
    }
  };

  // 初始加载PDF模板
  React.useEffect(() => {
    fetchTemplates(ExportFormat.PDF);
  }, []);

  return (
    <div className="space-y-6">
      {/* 格式选择 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            导出格式
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.values(ExportFormat).map((format) => (
              <div
                key={format}
                className={`flex flex-col items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedFormat === format 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleFormatChange(format)}
              >
                {getFormatIcon(format)}
                <span className="mt-2 text-sm font-medium">{getFormatName(format)}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 模板选择 */}
      {templates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>导出模板</CardTitle>
          </CardHeader>
          <CardContent>
            {templatesLoading ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-6 w-6 animate-spin mr-2" />
                <span>加载模板中...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  className={`flex flex-col p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedTemplate === null
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedTemplate(null)}
                >
                  <div className="font-medium">自定义选项</div>
                  <div className="text-sm text-gray-500">使用自定义导出选项</div>
                </div>
                {templates.map((template) => (
                  <div
                    key={template.id || template.name}
                    className={`flex flex-col p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedTemplate?.name === template.name
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleTemplateChange(template)}
                  >
                    <div className="font-medium">{template.name}</div>
                    <div className="text-sm text-gray-500">{template.description}</div>
                    {template.is_default && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          默认
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 导出选项 */}
      <Card>
        <CardHeader>
          <CardTitle>导出选项</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* PDF选项 */}
          {selectedFormat === ExportFormat.PDF && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium">PDF选项</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">页面大小</label>
                  <select
                    value={exportOptions.pdf_page_size}
                    onChange={(e) => setExportOptions({...exportOptions, pdf_page_size: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="A4">A4</option>
                    <option value="A3">A3</option>
                    <option value="Letter">Letter</option>
                    <option value="Legal">Legal</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">字体大小</label>
                  <Input
                    type="number"
                    value={exportOptions.pdf_font_size}
                    onChange={(e) => setExportOptions({...exportOptions, pdf_font_size: parseInt(e.target.value) || 12})}
                    min="8"
                    max="24"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Word选项 */}
          {selectedFormat === ExportFormat.WORD && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium">Word选项</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">页面大小</label>
                  <select
                    value={exportOptions.word_page_size}
                    onChange={(e) => setExportOptions({...exportOptions, word_page_size: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="A4">A4</option>
                    <option value="A3">A3</option>
                    <option value="Letter">Letter</option>
                    <option value="Legal">Legal</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">字体大小</label>
                  <Input
                    type="number"
                    value={exportOptions.word_font_size}
                    onChange={(e) => setExportOptions({...exportOptions, word_font_size: parseInt(e.target.value) || 12})}
                    min="8"
                    max="24"
                  />
                </div>
              </div>
            </div>
          )}

          {/* HTML选项 */}
          {selectedFormat === ExportFormat.HTML && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium">HTML选项</h4>
              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="html_responsive"
                    checked={exportOptions.html_responsive}
                    onChange={(e) => setExportOptions({...exportOptions, html_responsive: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="html_responsive" className="text-sm font-medium">
                    响应式设计
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="html_include_toc"
                    checked={exportOptions.html_include_toc}
                    onChange={(e) => setExportOptions({...exportOptions, html_include_toc: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="html_include_toc" className="text-sm font-medium">
                    包含目录
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* 通用选项 */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium">通用选项</h4>
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_header"
                  checked={exportOptions.include_header}
                  onChange={(e) => setExportOptions({...exportOptions, include_header: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="include_header" className="text-sm font-medium">
                  包含页眉
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_footer"
                  checked={exportOptions.include_footer}
                  onChange={(e) => setExportOptions({...exportOptions, include_footer: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="include_footer" className="text-sm font-medium">
                  包含页脚
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_page_numbers"
                  checked={exportOptions.include_page_numbers}
                  onChange={(e) => setExportOptions({...exportOptions, include_page_numbers: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="include_page_numbers" className="text-sm font-medium">
                  包含页码
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="include_watermark"
                  checked={exportOptions.include_watermark}
                  onChange={(e) => setExportOptions({...exportOptions, include_watermark: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="include_watermark" className="text-sm font-medium">
                  包含水印
                </label>
              </div>
              {exportOptions.include_watermark && (
                <div className="ml-6 space-y-2">
                  <div>
                    <label className="block text-sm font-medium mb-2">水印文本</label>
                    <Input
                      value={exportOptions.watermark_text}
                      onChange={(e) => setExportOptions({...exportOptions, watermark_text: e.target.value})}
                      placeholder="输入水印文本"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">水印透明度</label>
                    <Input
                      type="number"
                      value={exportOptions.watermark_opacity}
                      onChange={(e) => setExportOptions({...exportOptions, watermark_opacity: parseFloat(e.target.value) || 0.1})}
                      min="0"
                      max="1"
                      step="0.1"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 操作按钮 */}
      <div className="flex justify-end gap-3">
        {onCancel && (
          <Button variant="outline" onClick={onCancel}>
            取消
          </Button>
        )}
        <Button 
          onClick={handleExport} 
          disabled={loading}
          className="min-w-32"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              导出中...
            </>
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              开始导出
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

export default DocumentExportOptions;