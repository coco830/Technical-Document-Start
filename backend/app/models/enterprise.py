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
    legal_representative = Column(String(100), comment="法定代表人")
    contact_phone = Column(String(50), comment="联系电话")
    fax = Column(String(50), comment="传真")
    email = Column(String(100), comment="电子邮箱")
    overview = Column(Text, comment="企业概况")
    risk_level = Column(String(50), comment="风险级别")
    
    # 环保手续信息
    env_assessment_no = Column(String(255), comment="环评批复编号")
    acceptance_no = Column(String(255), comment="验收文件编号")
    discharge_permit_no = Column(String(255), comment="排污许可证编号")
    has_emergency_plan = Column(String(10), comment="是否有历史应急预案")  # 有/无
    emergency_plan_code = Column(String(100), comment="历史应急预案编号")  # 仅当有预案时填写
    
    # 危险化学品信息 (JSON格式存储)
    hazardous_materials = Column(JSON, comment="危险化学品信息列表")
    
    # 应急资源信息 (JSON格式存储)
    emergency_resources = Column(JSON, comment="应急资源信息列表")
    
    # 应急组织信息 (JSON格式存储)
    emergency_orgs = Column(JSON, comment="应急组织信息列表")
    
    # 外部应急救援通讯方式 (JSON格式存储)
    external_emergency_contacts = Column(JSON, comment="外部应急救援通讯方式列表")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="enterprise_infos")
    project = relationship("Project", back_populates="enterprise_info")
    
    def __repr__(self):
        return f"<EnterpriseInfo(id={self.id}, enterprise_name='{self.enterprise_name}')>"