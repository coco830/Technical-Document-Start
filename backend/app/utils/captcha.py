import random
import string
import io
import base64
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import os


class CaptchaGenerator:
    """验证码生成器"""
    
    def __init__(self, width: int = 120, height: int = 50, length: int = 4):
        self.width = width
        self.height = height
        self.length = length
        self.font_path = self._get_default_font()
    
    def _get_default_font(self) -> Optional[str]:
        """获取默认字体路径"""
        # 尝试使用系统字体
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/Windows/Fonts/arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "arial.ttf"  # 当前目录
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def generate_text_captcha(self) -> Tuple[str, str]:
        """生成文本验证码"""
        # 生成随机字符串
        characters = string.ascii_uppercase + string.digits
        captcha_text = ''.join(random.choice(characters) for _ in range(self.length))
        
        # 创建图片
        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, size=30)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 绘制文字
        text_width, text_height = draw.textsize(captcha_text, font=font)
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # 添加噪点
        for _ in range(100):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            draw.point((x1, y1), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 添加干扰线
        for _ in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 绘制验证码文字
        draw.text((x, y), captcha_text, fill=(0, 0, 0), font=font)
        
        # 将图片转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return captcha_text, f"data:image/png;base64,{image_base64}"
    
    def generate_math_captcha(self) -> Tuple[str, str]:
        """生成数学验证码"""
        # 生成简单的数学表达式
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operators = ['+', '-']
        operator = random.choice(operators)
        
        if operator == '+':
            result = num1 + num2
            expression = f"{num1} + {num2} = ?"
        else:
            # 确保结果为正数
            if num1 < num2:
                num1, num2 = num2, num1
            result = num1 - num2
            expression = f"{num1} - {num2} = ?"
        
        # 创建图片
        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, size=25)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 添加噪点
        for _ in range(100):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            draw.point((x1, y1), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 添加干扰线
        for _ in range(3):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 绘制数学表达式
        text_width, text_height = draw.textsize(expression, font=font)
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        draw.text((x, y), expression, fill=(0, 0, 0), font=font)
        
        # 将图片转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return str(result), f"data:image/png;base64,{image_base64}"
    
    def generate_numeric_captcha(self) -> Tuple[str, str]:
        """生成数字验证码"""
        # 生成随机数字
        captcha_text = ''.join(random.choice(string.digits) for _ in range(self.length))
        
        # 创建图片
        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, size=35)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 添加噪点
        for _ in range(150):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            draw.point((x1, y1), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 添加干扰线
        for _ in range(8):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # 绘制验证码文字
        text_width, text_height = draw.textsize(captcha_text, font=font)
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        draw.text((x, y), captcha_text, fill=(0, 0, 0), font=font)
        
        # 将图片转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return captcha_text, f"data:image/png;base64,{image_base64}"


# 全局验证码生成器实例
captcha_generator = CaptchaGenerator()


def generate_text_captcha(width: int = 120, height: int = 50, length: int = 4) -> Tuple[str, str]:
    """生成文本验证码的便捷函数"""
    generator = CaptchaGenerator(width, height, length)
    return generator.generate_text_captcha()


def generate_math_captcha(width: int = 120, height: int = 50) -> Tuple[str, str]:
    """生成数学验证码的便捷函数"""
    generator = CaptchaGenerator(width, height)
    return generator.generate_math_captcha()


def generate_numeric_captcha(width: int = 120, height: int = 50, length: int = 4) -> Tuple[str, str]:
    """生成数字验证码的便捷函数"""
    generator = CaptchaGenerator(width, height, length)
    return generator.generate_numeric_captcha()


def generate_verification_code(length: int = 6) -> str:
    """生成数字验证码"""
    return ''.join(random.choice(string.digits) for _ in range(length))


def generate_random_string(length: int = 8, include_digits: bool = True, include_uppercase: bool = True, include_lowercase: bool = True) -> str:
    """生成随机字符串"""
    characters = ""
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_digits:
        characters += string.digits
    
    if not characters:
        characters = string.ascii_lowercase
    
    return ''.join(random.choice(characters) for _ in range(length))