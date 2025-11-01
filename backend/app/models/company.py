from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class Company(BaseModel):
    """企业模型"""
    __tablename__ = "companies"
    
    name = Column(String(200), nullable=False, index=True, comment="企业名称")
    unified_social_credit_code = Column(String(18), unique=True, nullable=True, index=True, comment="统一社会信用代码")
    legal_representative = Column(String(100), nullable=True, comment="法定代表人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    contact_email = Column(String(100), nullable=True, comment="联系邮箱")
    address = Column(Text, nullable=True, comment="企业地址")
    industry = Column(String(100), nullable=True, comment="所属行业")
    business_scope = Column(Text, nullable=True, comment="经营范围")
    
    # 关系
    projects = relationship("Project", back_populates="company")
    
    # 索引
    __table_args__ = (
        Index('idx_companies_name', 'name'),
        Index('idx_companies_unified_social_credit_code', 'unified_social_credit_code'),
    )