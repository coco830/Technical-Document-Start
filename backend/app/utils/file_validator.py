import os
import logging
import mimetypes
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import magic

# 配置日志
logger = logging.getLogger(__name__)

# 文件类型白名单配置
ALLOWED_FILE_TYPES = {
    'image/jpeg': {
        'extensions': ['.jpg', '.jpeg'],
        'magic_numbers': [b'\xff\xd8\xff'],
        'max_size': 5 * 1024 * 1024,  # 5MB
        'description': 'JPEG图片'
    },
    'image/png': {
        'extensions': ['.png'],
        'magic_numbers': [b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'],
        'max_size': 5 * 1024 * 1024,  # 5MB
        'description': 'PNG图片'
    },
    'image/gif': {
        'extensions': ['.gif'],
        'magic_numbers': [b'GIF87a', b'GIF89a'],
        'max_size': 5 * 1024 * 1024,  # 5MB
        'description': 'GIF图片'
    },
    'image/webp': {
        'extensions': ['.webp'],
        'magic_numbers': [b'RIFF', b'WEBP'],
        'max_size': 5 * 1024 * 1024,  # 5MB
        'description': 'WebP图片'
    },
    'application/pdf': {
        'extensions': ['.pdf'],
        'magic_numbers': [b'%PDF-'],
        'max_size': 10 * 1024 * 1024,  # 10MB
        'description': 'PDF文档'
    },
    'text/plain': {
        'extensions': ['.txt'],
        'magic_numbers': [b''],
        'max_size': 1 * 1024 * 1024,  # 1MB
        'description': '纯文本文件'
    },
    'application/msword': {
        'extensions': ['.doc'],
        'magic_numbers': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
        'max_size': 10 * 1024 * 1024,  # 10MB
        'description': 'Word文档'
    },
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {
        'extensions': ['.docx'],
        'magic_numbers': [b'PK\x03\x04'],
        'max_size': 10 * 1024 * 1024,  # 10MB
        'description': 'Word文档'
    }
}

# 危险文件扩展名黑名单
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.app', '.deb', '.pkg', '.dmg', '.rpm', '.deb', '.sh', '.ps1', '.php',
    '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl', '.lua', '.sql', '.sh'
]

class FileValidationError(Exception):
    """文件验证错误异常类"""
    pass

class FileValidator:
    """文件验证器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_file(self, file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """
        验证上传的文件
        
        Args:
            file_content: 文件二进制内容
            filename: 文件名
            content_type: 声明的Content-Type
            
        Returns:
            包含验证结果的字典
            
        Raises:
            FileValidationError: 文件验证失败时抛出
        """
        self.logger.info(f"开始验证文件: {filename}, 声明类型: {content_type}, 大小: {len(file_content)} bytes")
        
        # 1. 检查文件名
        self._validate_filename(filename)
        
        # 2. 检查文件大小
        self._validate_file_size(file_content, content_type)
        
        # 3. 检查文件扩展名
        file_extension = self._get_file_extension(filename)
        
        # 4. 验证文件类型白名单
        if content_type not in ALLOWED_FILE_TYPES:
            raise FileValidationError(f"不支持的文件类型: {content_type}")
        
        file_type_config = ALLOWED_FILE_TYPES[content_type]
        
        # 5. 验证扩展名是否匹配
        if file_extension not in file_type_config['extensions']:
            raise FileValidationError(
                f"文件扩展名 {file_extension} 与声明的文件类型 {content_type} 不匹配"
            )
        
        # 6. 验证文件头（魔数）
        self._validate_magic_numbers(file_content, content_type)
        
        # 7. 使用python-magic库进行额外验证
        self._validate_with_magic(file_content, content_type)
        
        # 8. 记录成功日志
        self.logger.info(f"文件验证成功: {filename}, 类型: {content_type}")
        
        return {
            'filename': filename,
            'content_type': content_type,
            'size': len(file_content),
            'extension': file_extension,
            'is_valid': True,
            'description': file_type_config['description']
        }
    
    def _validate_filename(self, filename: str) -> None:
        """验证文件名安全性"""
        if not filename:
            raise FileValidationError("文件名不能为空")
        
        # 检查文件名长度
        if len(filename) > 255:
            raise FileValidationError("文件名过长，最大支持255个字符")
        
        # 检查危险字符
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                raise FileValidationError(f"文件名包含危险字符: {char}")
        
        # 检查危险扩展名
        file_extension = self._get_file_extension(filename).lower()
        if file_extension in DANGEROUS_EXTENSIONS:
            raise FileValidationError(f"不允许上传的文件类型: {file_extension}")
    
    def _validate_file_size(self, file_content: bytes, content_type: str) -> None:
        """验证文件大小"""
        file_size = len(file_content)
        
        if content_type in ALLOWED_FILE_TYPES:
            max_size = ALLOWED_FILE_TYPES[content_type]['max_size']
            if file_size > max_size:
                raise FileValidationError(
                    f"文件大小 {file_size} bytes 超过限制 {max_size} bytes"
                )
        
        # 通用大小检查（防止过大文件）
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise FileValidationError("文件大小超过系统限制 50MB")
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return Path(filename).suffix.lower()
    
    def _validate_magic_numbers(self, file_content: bytes, content_type: str) -> None:
        """验证文件头（魔数）"""
        if content_type not in ALLOWED_FILE_TYPES:
            return
        
        magic_numbers = ALLOWED_FILE_TYPES[content_type]['magic_numbers']
        if not magic_numbers:
            return  # 某些文件类型（如文本）没有特定的魔数
        
        # 检查文件头是否匹配任何允许的魔数
        is_valid = False
        for magic in magic_numbers:
            if file_content.startswith(magic):
                is_valid = True
                break
        
        if not is_valid:
            raise FileValidationError(
                f"文件头与声明的类型 {content_type} 不匹配，可能不是真实的 {ALLOWED_FILE_TYPES[content_type]['description']}"
            )
    
    def _validate_with_magic(self, file_content: bytes, expected_type: str) -> None:
        """使用python-magic库进行文件类型验证"""
        try:
            # 检测文件类型
            detected_type = magic.from_buffer(file_content, mime=True)
            
            # 对于某些文件类型，允许更宽松的匹配
            type_mappings = {
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
                    'application/zip', 'application/x-zip-compressed'
                ],
                'application/msword': [
                    'application/x-msword'
                ]
            }
            
            # 检查检测到的类型是否与预期类型匹配
            if expected_type in type_mappings:
                allowed_types = type_mappings[expected_type]
                if detected_type not in allowed_types and detected_type != expected_type:
                    raise FileValidationError(
                        f"检测到的文件类型 {detected_type} 与声明的类型 {expected_type} 不匹配"
                    )
            else:
                # 严格匹配
                if detected_type != expected_type:
                    raise FileValidationError(
                        f"检测到的文件类型 {detected_type} 与声明的类型 {expected_type} 不匹配"
                    )
            
            self.logger.info(f"Magic库验证通过: 检测类型={detected_type}, 声明类型={expected_type}")
            
        except ImportError:
            self.logger.warning("python-magic库未安装，跳过魔数验证")
        except Exception as e:
            self.logger.error(f"Magic库验证失败: {str(e)}")
            # 不阻止上传，但记录警告
            self.logger.warning("由于Magic库验证失败，继续使用基础验证")
    
    def scan_for_malicious_content(self, file_content: bytes) -> bool:
        """
        扫描文件中的恶意内容（基础实现）
        
        Args:
            file_content: 文件二进制内容
            
        Returns:
            True 如果文件安全，False 如果检测到可疑内容
        """
        # 基础恶意内容检测
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'data:text/html',
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec(',
            b'passthru(',
            b'file_get_contents(',
            b'fopen(',
            b'unlink(',
            b'rmdir(',
            b'mkdir('
        ]
        
        content_lower = file_content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                self.logger.warning(f"检测到可疑内容模式: {pattern}")
                return False
        
        # 检查是否包含可执行文件的魔数
        executable_signatures = [
            b'MZ',  # Windows PE
            b'\x7fELF',  # Linux ELF
            b'\xca\xfe\xba\xbe',  # Java class
            b'\xfe\xed\xfa\xce',  # Mach-O binary (macOS)
            b'\xfe\xed\xfa\xcf',  # Mach-O binary (macOS)
        ]
        
        for signature in executable_signatures:
            if file_content.startswith(signature):
                self.logger.warning(f"检测到可执行文件签名: {signature}")
                return False
        
        return True

# 创建全局验证器实例
file_validator = FileValidator()

def validate_uploaded_file(file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
    """
    验证上传的文件的便捷函数
    
    Args:
        file_content: 文件二进制内容
        filename: 文件名
        content_type: 声明的Content-Type
        
    Returns:
        包含验证结果的字典
        
    Raises:
        FileValidationError: 文件验证失败时抛出
    """
    return file_validator.validate_file(file_content, filename, content_type)

def scan_file_security(file_content: bytes) -> bool:
    """
    扫描文件安全性的便捷函数
    
    Args:
        file_content: 文件二进制内容
        
    Returns:
        True 如果文件安全，False 如果检测到可疑内容
    """
    return file_validator.scan_for_malicious_content(file_content)