"""
文件上传安全功能测试
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.file_validator import (
    FileValidator, 
    FileValidationError,
    validate_uploaded_file,
    scan_file_security
)
from app.main import app

# 创建测试客户端
client = TestClient(app)

class TestFileValidator:
    """文件验证器测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.validator = FileValidator()
    
    def test_valid_jpeg_file(self):
        """测试有效的JPEG文件"""
        # 创建一个简单的JPEG文件头
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        jpeg_content = jpeg_header + b'\xff' * 1000  # 添加一些内容
        
        result = self.validator.validate_file(
            file_content=jpeg_content,
            filename="test.jpg",
            content_type="image/jpeg"
        )
        
        assert result['is_valid'] is True
        assert result['content_type'] == "image/jpeg"
        assert result['extension'] == ".jpg"
        assert result['size'] == len(jpeg_content)
    
    def test_valid_png_file(self):
        """测试有效的PNG文件"""
        # 创建一个简单的PNG文件头
        png_header = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
        png_content = png_header + b'\x00' * 1000  # 添加一些内容
        
        result = self.validator.validate_file(
            file_content=png_content,
            filename="test.png",
            content_type="image/png"
        )
        
        assert result['is_valid'] is True
        assert result['content_type'] == "image/png"
        assert result['extension'] == ".png"
    
    def test_invalid_file_type(self):
        """测试无效的文件类型"""
        # 创建一个二进制文件
        binary_content = b'\x00\x01\x02\x03\x04\x05' * 100
        
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=binary_content,
                filename="test.exe",
                content_type="application/octet-stream"
            )
        
        assert "不支持的文件类型" in str(exc_info.value)
    
    def test_mismatched_extension(self):
        """测试扩展名与内容类型不匹配"""
        # 创建一个JPEG文件头但使用PNG扩展名
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        jpeg_content = jpeg_header + b'\xff' * 1000
        
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=jpeg_content,
                filename="test.png",  # 错误的扩展名
                content_type="image/jpeg"
            )
        
        assert "文件扩展名" in str(exc_info.value)
        assert "与声明的文件类型" in str(exc_info.value)
    
    def test_invalid_magic_number(self):
        """测试无效的魔数"""
        # 创建一个内容类型为JPEG但魔数不正确的文件
        fake_jpeg = b'\x00\x01\x02\x03\x04\x05' * 100
        
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=fake_jpeg,
                filename="test.jpg",
                content_type="image/jpeg"
            )
        
        assert "文件头与声明的类型" in str(exc_info.value)
    
    def test_file_size_limit(self):
        """测试文件大小限制"""
        # 创建一个超过大小限制的JPEG文件
        large_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        large_jpeg += b'\xff' * (6 * 1024 * 1024)  # 6MB，超过5MB限制
        
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=large_jpeg,
                filename="large.jpg",
                content_type="image/jpeg"
            )
        
        assert "文件大小" in str(exc_info.value)
        assert "超过限制" in str(exc_info.value)
    
    def test_dangerous_filename(self):
        """测试危险文件名"""
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        jpeg_content += b'\xff' * 1000
        
        # 测试包含路径遍历的文件名
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=jpeg_content,
                filename="../../../etc/passwd.jpg",
                content_type="image/jpeg"
            )
        
        assert "文件名包含危险字符" in str(exc_info.value)
        
        # 测试危险扩展名
        with pytest.raises(FileValidationError) as exc_info:
            self.validator.validate_file(
                file_content=jpeg_content,
                filename="test.exe",
                content_type="image/jpeg"
            )
        
        assert "不允许上传的文件类型" in str(exc_info.value)
    
    def test_scan_malicious_content(self):
        """测试恶意内容扫描"""
        # 测试包含脚本标签的内容
        malicious_content = b'<script>alert("xss")</script>'
        
        assert not self.validator.scan_for_malicious_content(malicious_content)
        
        # 测试包含可执行文件签名的内容
        exe_signature = b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff'
        
        assert not self.validator.scan_for_malicious_content(exe_signature)
        
        # 测试安全内容
        safe_content = b'This is a safe image content'
        
        assert self.validator.scan_for_malicious_content(safe_content)

class TestFileUploadAPI:
    """文件上传API测试类"""
    
    def test_upload_valid_image(self):
        """测试上传有效图片"""
        # 创建一个简单的JPEG文件
        jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        jpeg_content += b'\xff' * 1000
        
        # 模拟用户认证
        with patch('app.utils.auth.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_auth.return_value = mock_user
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(jpeg_content)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    response = client.post(
                        "/api/documents/upload-image",
                        files={"file": ("test.jpg", f, "image/jpeg")},
                        headers={"Authorization": "Bearer fake_token"}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "url" in data
                assert "filename" in data
                assert "size" in data
                assert "content_type" in data
                assert data["content_type"] == "image/jpeg"
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
    
    def test_upload_invalid_file_type(self):
        """测试上传无效文件类型"""
        # 创建一个文本文件但声明为图片
        text_content = b"This is not an image file"
        
        # 模拟用户认证
        with patch('app.utils.auth.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_auth.return_value = mock_user
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
                temp_file.write(text_content)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    response = client.post(
                        "/api/documents/upload-image",
                        files={"file": ("fake.jpg", f, "image/jpeg")},
                        headers={"Authorization": "Bearer fake_token"}
                    )
                
                assert response.status_code == 400
                assert "文件头与声明的类型" in response.json()["detail"]
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
    
    def test_upload_oversized_file(self):
        """测试上传过大文件"""
        # 创建一个超过大小限制的JPEG文件头
        large_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        large_jpeg += b'\xff' * (6 * 1024 * 1024)  # 6MB，超过5MB限制
        
        # 模拟用户认证
        with patch('app.utils.auth.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_auth.return_value = mock_user
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(large_jpeg)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    response = client.post(
                        "/api/documents/upload-image",
                        files={"file": ("large.jpg", f, "image/jpeg")},
                        headers={"Authorization": "Bearer fake_token"}
                    )
                
                assert response.status_code == 400
                assert "文件大小" in response.json()["detail"]
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)

def test_convenience_functions():
    """测试便捷函数"""
    # 测试validate_uploaded_file函数
    jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    jpeg_content += b'\xff' * 1000
    
    result = validate_uploaded_file(
        file_content=jpeg_content,
        filename="test.jpg",
        content_type="image/jpeg"
    )
    
    assert result['is_valid'] is True
    
    # 测试scan_file_security函数
    safe_content = b"This is safe content"
    assert scan_file_security(safe_content) is True
    
    malicious_content = b'<script>alert("xss")</script>'
    assert scan_file_security(malicious_content) is False

if __name__ == "__main__":
    print("运行文件上传安全测试...")
    
    # 运行测试
    pytest.main([__file__, "-v"])