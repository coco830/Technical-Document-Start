import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self._initialized = False
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.smtp_tls = None
        self.from_email = None
        self.from_name = None
    
    def _initialize(self):
        """延迟初始化邮件配置"""
        if self._initialized:
            return
            
        # 验证必需的配置项
        required_configs = [
            ('SMTP_HOST', settings.SMTP_HOST),
            ('SMTP_USER', settings.SMTP_USER),
            ('SMTP_PASSWORD', settings.SMTP_PASSWORD),
            ('EMAILS_FROM_EMAIL', settings.EMAILS_FROM_EMAIL)
        ]
        
        missing_configs = [name for name, value in required_configs if not value]
        if missing_configs:
            error_msg = f"邮件配置缺失，缺少以下配置项: {', '.join(missing_configs)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 设置配置
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT or 587
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS if settings.SMTP_TLS is not None else True
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME or "悦恩人机共写平台"
        
        self._initialized = True
        logger.info("邮件配置初始化成功")
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """发送邮件"""
        try:
            # 延迟初始化
            self._initialize()
            
            # 验证参数
            if not to_emails:
                logger.error("收件人列表不能为空")
                return False
                
            if not subject:
                logger.error("邮件主题不能为空")
                return False
                
            if not body and not html_body:
                logger.error("邮件内容不能为空")
                return False
            
            logger.info(f"开始发送邮件到: {', '.join(to_emails)}, 主题: {subject}")
            
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # 添加邮件正文
            if html_body:
                # 添加HTML和纯文本版本
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功到: {', '.join(to_emails)}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}", exc_info=True)
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """添加附件到邮件"""
        try:
            # 参数验证
            if not isinstance(attachment, dict):
                logger.error("附件参数必须是字典类型")
                return
                
            file_path = attachment.get('path')
            if not file_path:
                logger.error("附件路径不能为空")
                return
                
            filename = attachment.get('name', Path(file_path).name)
            
            if not os.path.exists(file_path):
                logger.error(f"附件文件不存在: {file_path}")
                return
            
            # 检查文件大小，防止过大文件
            file_size = os.path.getsize(file_path)
            max_size = 25 * 1024 * 1024  # 25MB
            if file_size > max_size:
                logger.error(f"附件文件过大: {file_path}, 大小: {file_size} bytes")
                return
            
            with open(file_path, "rb") as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            logger.info(f"附件添加成功: {filename}")
        except Exception as e:
            logger.error(f"添加附件失败: {str(e)}", exc_info=True)
    
    def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """发送验证邮件"""
        subject = "邮箱验证"
        body = f"""
        您好！
        
        您的验证码是：{verification_code}
        
        验证码有效期为10分钟，请及时使用。
        
        如果您没有申请验证码，请忽略此邮件。
        
        悦恩人机共写平台
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>邮箱验证</h2>
            <p>您好！</p>
            <p>您的验证码是：<strong style="font-size: 24px; color: #007bff;">{verification_code}</strong></p>
            <p>验证码有效期为10分钟，请及时使用。</p>
            <p>如果您没有申请验证码，请忽略此邮件。</p>
            <p>悦恩人机共写平台</p>
        </body>
        </html>
        """
        
        return self.send_email([to_email], subject, body, html_body, None)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """发送密码重置邮件"""
        subject = "密码重置"
        body = f"""
        您好！
        
        您请求重置密码，请点击以下链接重置密码：
        {reset_token}
        
        链接有效期为30分钟，请及时使用。
        
        如果您没有请求重置密码，请忽略此邮件。
        
        悦恩人机共写平台
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>密码重置</h2>
            <p>您好！</p>
            <p>您请求重置密码，请点击以下链接重置密码：</p>
            <p><a href="{reset_token}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">重置密码</a></p>
            <p>链接有效期为30分钟，请及时使用。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
            <p>悦恩人机共写平台</p>
        </body>
        </html>
        """
        
        return self.send_email([to_email], subject, body, html_body, None)
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        subject = "欢迎加入悦恩人机共写平台"
        body = f"""
        亲爱的 {username}：
        
        欢迎加入悦恩人机共写平台！
        
        我们致力于为您提供最优质的AI辅助写作体验，帮助您高效完成环保应急预案和环评报告的编写工作。
        
        如果您有任何问题或建议，请随时联系我们。
        
        祝您使用愉快！
        
        悦恩人机共写平台团队
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>欢迎加入悦恩人机共写平台</h2>
            <p>亲爱的 <strong>{username}</strong>：</p>
            <p>欢迎加入悦恩人机共写平台！</p>
            <p>我们致力于为您提供最优质的AI辅助写作体验，帮助您高效完成环保应急预案和环评报告的编写工作。</p>
            <p>如果您有任何问题或建议，请随时联系我们。</p>
            <p>祝您使用愉快！</p>
            <p>悦恩人机共写平台团队</p>
        </body>
        </html>
        """
        
        return self.send_email([to_email], subject, body, html_body, None)


# 全局邮件发送器实例（延迟初始化）
_email_sender = None


def get_email_sender() -> EmailSender:
    """获取邮件发送器实例（延迟初始化）"""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender


def send_email(
    to_emails: List[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """发送邮件的便捷函数"""
    return get_email_sender().send_email(to_emails, subject, body, html_body, attachments)


def send_verification_email(to_email: str, verification_code: str) -> bool:
    """发送验证邮件的便捷函数"""
    return get_email_sender().send_verification_email(to_email, verification_code)


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """发送密码重置邮件的便捷函数"""
    return get_email_sender().send_password_reset_email(to_email, reset_token)


def send_welcome_email(to_email: str, username: str) -> bool:
    """发送欢迎邮件的便捷函数"""
    return get_email_sender().send_welcome_email(to_email, username)