"""
企业信息数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EnterpriseInfo(Base):
    """企业基本信息表"""
    __tablename__ = "enterprise_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    
    # 企业基本信息
    enterprise_name = Column(String(255), nullable=False, comment="企业名称")
    address = Column(String(500), comment="企业地址")
    industry = Column(String(100), comment="所属行业")
    contact_person = Column(String(100), comment="联系人")
    phone = Column(String(50), comment="联系电话")
    employee_count = Column(String(50), comment="员工人数")
    main_products = Column(Text, comment="主要产品")
    annual_output = Column(Text, comment="年产量")
    description = Column(Text, comment="企业简介")
    
    # 环保手续信息
    env_assessment_no = Column(String(255), comment="环评批复编号")
    acceptance_no = Column(String(255), comment="验收文件编号")
    discharge_permit_no = Column(String(255), comment="排污许可证编号")
    env_dept = Column(String(255), comment="环保主管部门")
    
    # 危险化学品信息 (JSON格式存储)
    hazardous_materials = Column(JSON, comment="危险化学品信息列表")
    
    # 应急资源信息 (JSON格式存储)
    emergency_resources = Column(JSON, comment="应急资源信息列表")
    
    # 应急组织信息 (JSON格式存储)
    emergency_orgs = Column(JSON, comment="应急组织信息列表")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="enterprise_infos")
    project = relationship("Project", back_populates="enterprise_info")
    
    def __repr__(self):
        return f"<EnterpriseInfo(id={self.id}, enterprise_name='{self.enterprise_name}')>"