"""
PDF 导出模块
使用 reportlab 生成 PDF 文档
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import os
import re
from typing import Optional, Dict, Any


class PDFExporter:
    """PDF 导出器"""

    def __init__(self, output_dir: str = "exports/pdf"):
        """
        初始化 PDF 导出器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 注册中文字体（如果系统有）
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册常见的中文字体
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "C:\\Windows\\Fonts\\simsun.ttc",  # Windows
                "C:\\Windows\\Fonts\\msyh.ttc",
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        self.has_chinese_font = True
                        break
                    except:
                        continue
            else:
                self.has_chinese_font = False
        except Exception as e:
            print(f"字体注册失败: {e}")
            self.has_chinese_font = False

    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """获取样式配置"""
        styles = getSampleStyleSheet()

        # 自定义样式
        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Chinese' if self.has_chinese_font else 'Helvetica-Bold'
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Chinese' if self.has_chinese_font else 'Helvetica-Bold'
            ),
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=10,
                spaceBefore=10,
                fontName='Chinese' if self.has_chinese_font else 'Helvetica-Bold'
            ),
            'Body': ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=8,
                fontName='Chinese' if self.has_chinese_font else 'Helvetica'
            ),
            'Metadata': ParagraphStyle(
                'Metadata',
                fontSize=9,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_LEFT,
                fontName='Chinese' if self.has_chinese_font else 'Helvetica'
            )
        }

        return custom_styles

    def _html_to_text(self, html_content: str) -> str:
        """
        将 HTML 转换为纯文本

        Args:
            html_content: HTML 内容

        Returns:
            纯文本内容
        """
        if not html_content:
            return ""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 移除 script 和 style 标签
            for script in soup(["script", "style"]):
                script.decompose()

            # 获取文本
            text = soup.get_text(separator='\n')

            # 清理多余的空行
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n\n'.join(lines)
        except Exception as e:
            print(f"HTML 解析失败: {e}")
            return html_content

    def _generate_filename(self, title: str, timestamp: bool = True) -> str:
        """
        生成文件名

        Args:
            title: 文档标题
            timestamp: 是否添加时间戳

        Returns:
            文件名
        """
        # 清理标题中的特殊字符
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        clean_title = clean_title[:50]  # 限制长度

        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_title}_{ts}.pdf"
        else:
            filename = f"{clean_title}.pdf"

        return filename

    def export(
        self,
        title: str,
        content: str,
        content_type: str = "html",
        metadata: Optional[Dict[str, Any]] = None,
        custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出文档为 PDF

        Args:
            title: 文档标题
            content: 文档内容
            content_type: 内容类型 (html, markdown, text)
            metadata: 文档元数据
            custom_filename: 自定义文件名

        Returns:
            导出结果字典
        """
        try:
            # 生成文件名
            filename = custom_filename if custom_filename else self._generate_filename(title)
            filepath = self.output_dir / filename

            # 创建 PDF 文档
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # 获取样式
            styles = self._get_styles()

            # 构建文档内容
            story = []

            # 添加标题
            story.append(Paragraph(title, styles['Title']))
            story.append(Spacer(1, 0.5*cm))

            # 添加元数据
            if metadata:
                metadata_text = []
                if metadata.get('author'):
                    metadata_text.append(f"作者: {metadata['author']}")
                if metadata.get('created_at'):
                    metadata_text.append(f"创建时间: {metadata['created_at']}")
                if metadata.get('version'):
                    metadata_text.append(f"版本: {metadata['version']}")

                if metadata_text:
                    story.append(Paragraph(' | '.join(metadata_text), styles['Metadata']))
                    story.append(Spacer(1, 0.3*cm))

            # 添加导出时间戳
            export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"导出时间: {export_time}", styles['Metadata']))
            story.append(Spacer(1, 0.5*cm))

            # 添加分隔线
            story.append(Spacer(1, 0.2*cm))

            # 处理内容
            if content_type == "html":
                text_content = self._html_to_text(content)
            else:
                text_content = content

            # 将内容分段添加
            paragraphs = text_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # 检测是否为标题（简单规则）
                    if para.strip().startswith('#'):
                        # Markdown 风格标题
                        if para.startswith('###'):
                            story.append(Paragraph(para.replace('#', '').strip(), styles['Heading2']))
                        elif para.startswith('##'):
                            story.append(Paragraph(para.replace('#', '').strip(), styles['Heading1']))
                        else:
                            story.append(Paragraph(para.replace('#', '').strip(), styles['Title']))
                    else:
                        # 普通段落
                        story.append(Paragraph(para.strip(), styles['Body']))
                    story.append(Spacer(1, 0.2*cm))

            # 生成 PDF
            doc.build(story)

            # 验证文件是否存在
            if not filepath.exists():
                raise Exception("PDF 文件生成失败")

            file_size = filepath.stat().st_size

            return {
                'success': True,
                'filename': filename,
                'filepath': str(filepath),
                'file_size': file_size,
                'export_time': export_time,
                'message': 'PDF 导出成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'PDF 导出失败: {str(e)}'
            }

    def export_batch(
        self,
        documents: list,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量导出文档为单个 PDF

        Args:
            documents: 文档列表，每个文档包含 title, content, content_type
            output_filename: 输出文件名

        Returns:
            导出结果字典
        """
        try:
            # 生成文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"batch_export_{timestamp}.pdf"

            filepath = self.output_dir / output_filename

            # 创建 PDF 文档
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # 获取样式
            styles = self._get_styles()

            # 构建文档内容
            story = []

            # 添加封面
            story.append(Paragraph("批量文档导出", styles['Title']))
            story.append(Spacer(1, 0.5*cm))

            export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"导出时间: {export_time}", styles['Metadata']))
            story.append(Paragraph(f"文档数量: {len(documents)}", styles['Metadata']))
            story.append(PageBreak())

            # 添加每个文档
            for idx, doc_data in enumerate(documents, 1):
                # 文档标题
                story.append(Paragraph(f"{idx}. {doc_data['title']}", styles['Title']))
                story.append(Spacer(1, 0.3*cm))

                # 处理内容
                content_type = doc_data.get('content_type', 'html')
                content = doc_data.get('content', '')

                if content_type == "html":
                    text_content = self._html_to_text(content)
                else:
                    text_content = content

                # 添加内容段落
                paragraphs = text_content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), styles['Body']))
                        story.append(Spacer(1, 0.2*cm))

                # 文档分隔
                if idx < len(documents):
                    story.append(PageBreak())

            # 生成 PDF
            doc.build(story)

            # 验证文件
            if not filepath.exists():
                raise Exception("批量 PDF 文件生成失败")

            file_size = filepath.stat().st_size

            return {
                'success': True,
                'filename': output_filename,
                'filepath': str(filepath),
                'file_size': file_size,
                'document_count': len(documents),
                'export_time': export_time,
                'message': '批量 PDF 导出成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'批量 PDF 导出失败: {str(e)}'
            }
