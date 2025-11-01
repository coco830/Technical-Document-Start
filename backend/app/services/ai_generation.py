"""
AI生成服务层实现
"""
import logging
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.ai_generation import AIGeneration, AIGenerationStatus
from app.models.document import Document
from app.models.user import User
from app.schemas.ai_generation import (
    AIGenerationCreate, AIGenerationUpdate, AIGenerationWithDetails,
    AIGenerationList, AIGenerationRequest, AIGenerationResponse,
    AIGenerationConfig, AIGenerationTemplate, AIGenerationTemplateCreate,
    AIGenerationTemplateUpdate, AIGenerationTemplateList, AIGenerationStatusInfo
)
from app.services.base import CRUDBase
from app.core.exceptions import PermissionException, NotFoundException, ValidationException
from app.core.cache import cache_service, cache_async_result
from app.core.tasks import task_manager
from app.tasks.ai_generation import (
    submit_generation_task, submit_emergency_plan_task, submit_environmental_assessment_task
)

# 设置日志
logger = logging.getLogger(__name__)


def has_permission(user: User, permission: str) -> bool:
    """检查用户是否有特定权限"""
    if not user or not user.is_active:
        return False
    
    # 管理员拥有所有权限
    if user.role == "admin":
        return True
    
    # 普通用户权限
    permission_map = {
        "user": ["read_own", "write_own", "ai:generate"],
        "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin", 
                 "ai:generate", "system:admin"],
    }
    
    user_permissions = permission_map.get(user.role, [])
    return permission in user_permissions


class CRUDAIGeneration(CRUDBase[AIGeneration, AIGenerationCreate, AIGenerationUpdate]):
    def get_by_document_id(self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100) -> List[AIGeneration]:
        """获取文档的AI生成记录列表"""
        return (
            db.query(self.model)
            .filter(AIGeneration.document_id == document_id)
            .order_by(desc(AIGeneration.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[AIGeneration]:
        """获取用户的AI生成记录列表"""
        return (
            db.query(self.model)
            .filter(AIGeneration.user_id == user_id)
            .order_by(desc(AIGeneration.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, db: Session, *, status: AIGenerationStatus, skip: int = 0, limit: int = 100) -> List[AIGeneration]:
        """根据状态获取AI生成记录列表"""
        return (
            db.query(self.model)
            .filter(AIGeneration.status == status)
            .order_by(desc(AIGeneration.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, generation_id: int) -> Optional[AIGenerationWithDetails]:
        """获取包含详细信息的AI生成记录"""
        generation = db.query(self.model).filter(AIGeneration.id == generation_id).first()
        if not generation:
            return None
        
        # 获取关联信息
        document_title = generation.document.title if generation.document else None
        user_name = generation.user.full_name if generation.user else None
        
        return AIGenerationWithDetails(
            id=int(generation.id),
            document_id=int(generation.document_id),
            user_id=int(generation.user_id),
            prompt=str(generation.prompt),
            generation_config=dict(generation.generation_config) if generation.generation_config else None,
            generated_content=str(generation.generated_content) if generation.generated_content else None,
            status=AIGenerationStatus(generation.status.value),
            metadata=dict(generation.metadata) if generation.metadata else None,
            created_at=generation.created_at,
            updated_at=generation.updated_at,
            completed_at=generation.completed_at,
            document_title=document_title,
            user_name=user_name
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[AIGenerationStatus] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[AIGenerationWithDetails]:
        """获取包含详细信息的多个AI生成记录"""
        query = db.query(self.model)
        
        # 应用筛选条件
        if document_id:
            query = query.filter(AIGeneration.document_id == document_id)
        if user_id:
            query = query.filter(AIGeneration.user_id == user_id)
        if status:
            query = query.filter(AIGeneration.status == status)
        
        # 应用排序
        if order_by and hasattr(AIGeneration, order_by):
            order_column = getattr(AIGeneration, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        
        generations = query.offset(skip).limit(limit).all()
        
        result = []
        for generation in generations:
            document_title = generation.document.title if generation.document else None
            user_name = generation.user.full_name if generation.user else None
            
            result.append(AIGenerationWithDetails(
                id=int(generation.id),
                document_id=int(generation.document_id),
                user_id=int(generation.user_id),
                prompt=str(generation.prompt),
                generation_config=dict(generation.generation_config) if generation.generation_config else None,
                generated_content=str(generation.generated_content) if generation.generated_content else None,
                status=AIGenerationStatus(generation.status.value),
                metadata=dict(generation.metadata) if generation.metadata else None,
                created_at=generation.created_at,
                updated_at=generation.updated_at,
                completed_at=generation.completed_at,
                document_title=document_title,
                user_name=user_name
            ))
        
        return result

    def create_with_user(self, db: Session, *, obj_in: AIGenerationCreate, current_user: User) -> AIGeneration:
        """创建AI生成记录"""
        # 检查权限
        if not has_permission(current_user, "ai:generate"):
            raise PermissionException("没有创建AI生成记录的权限")
        
        # 检查文档权限
        document = db.query(Document).filter(Document.id == obj_in.document_id).first()
        if not document:
            raise NotFoundException(f"文档 {obj_in.document_id} 不存在")
        
        if document.project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为此文档创建AI生成记录")
        
        db_obj = AIGeneration(
            document_id=obj_in.document_id,
            user_id=obj_in.user_id or current_user.id,
            prompt=obj_in.prompt,
            generation_config=obj_in.generation_config,
            status=obj_in.status or AIGenerationStatus.PENDING,
            metadata=obj_in.metadata,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"用户 {current_user.id} 创建了AI生成记录 {db_obj.id}")
        return db_obj

    def update_with_user(
        self, 
        db: Session, 
        *, 
        db_obj: AIGeneration, 
        obj_in: Union[AIGenerationUpdate, Dict[str, Any]],
        current_user: User
    ) -> AIGeneration:
        """更新AI生成记录"""
        # 检查权限
        if not self._can_modify_generation(db_obj, current_user):
            raise PermissionException("没有修改此AI生成记录的权限")
        
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        # 如果状态变为完成，设置完成时间
        if "status" in update_data and update_data["status"] == AIGenerationStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        result = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        logger.info(f"用户 {current_user.id} 更新了AI生成记录 {db_obj.id}")
        return result

    def delete_with_user(self, db: Session, *, generation_id: int, current_user: User) -> AIGeneration:
        """删除AI生成记录"""
        generation = self.get(db, id=generation_id)
        if not generation:
            raise NotFoundException(f"AI生成记录 {generation_id} 不存在")
        
        # 检查权限
        if not self._can_modify_generation(generation, current_user):
            raise PermissionException("没有删除此AI生成记录的权限")
        
        db.delete(generation)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除了AI生成记录 {generation_id}")
        return generation

    def _can_modify_generation(self, generation: AIGeneration, user: User) -> bool:
        """检查用户是否可以修改AI生成记录"""
        # 管理员可以修改所有记录
        if has_permission(user, "system:admin"):
            return True
        
        # 记录所有者可以修改
        if generation.user_id == user.id:
            return True
        
        # 文档项目所有者可以修改
        if generation.document and generation.document.project.user_id == user.id:
            return True
        
        return False


class AIGenerationService:
    """AI生成服务类，继承自BaseService"""
    
    def __init__(self):
        self.crud_ai_generation = CRUDAIGeneration(AIGeneration)
    
    # AI生成CRUD操作
    def create_generation(self, db: Session, *, generation_in: AIGenerationCreate, current_user: User) -> AIGeneration:
        """创建AI生成记录"""
        return self.crud_ai_generation.create_with_user(db=db, obj_in=generation_in, current_user=current_user)
    
    def get_generation(self, db: Session, *, generation_id: int, current_user: User) -> Optional[AIGenerationWithDetails]:
        """获取单个AI生成记录"""
        generation = self.crud_ai_generation.get(db, id=generation_id)
        if not generation:
            raise NotFoundException(f"AI生成记录 {generation_id} 不存在")
        
        # 检查权限
        if not self.crud_ai_generation._can_modify_generation(generation, current_user) and \
           not has_permission(current_user, "ai:generate"):
            raise PermissionException("没有权限查看此AI生成记录")
        
        return self.crud_ai_generation.get_with_details(db, generation_id=generation_id)
    
    def get_generations(
        self, 
        db: Session, 
        *, 
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[AIGenerationStatus] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True,
        current_user: User = None
    ) -> List[AIGenerationWithDetails]:
        """获取AI生成记录列表（支持分页、筛选、排序）"""
        # 如果不是管理员，只返回用户有权限的记录
        if current_user and not has_permission(current_user, "system:admin"):
            user_id = current_user.id
        
        return self.crud_ai_generation.get_multi_with_details(
            db=db,
            document_id=document_id,
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def update_generation(
        self, 
        db: Session, 
        *, 
        generation_id: int, 
        generation_in: AIGenerationUpdate, 
        current_user: User
    ) -> AIGeneration:
        """更新AI生成记录"""
        generation = self.crud_ai_generation.get(db, id=generation_id)
        if not generation:
            raise NotFoundException(f"AI生成记录 {generation_id} 不存在")
        
        return self.crud_ai_generation.update_with_user(db, db_obj=generation, obj_in=generation_in, current_user=current_user)
    
    def delete_generation(self, db: Session, *, generation_id: int, current_user: User) -> AIGeneration:
        """删除AI生成记录"""
        return self.crud_ai_generation.delete_with_user(db, generation_id=generation_id, current_user=current_user)
    
    # AI内容生成
    @cache_async_result(key_prefix="ai_generate", ttl=1800)  # 缓存30分钟
    async def generate_content(
        self, 
        db: Session, 
        *, 
        request: AIGenerationRequest, 
        document_id: int, 
        current_user: User
    ) -> AIGenerationResponse:
        """生成AI内容"""
        # 检查权限
        if not has_permission(current_user, "ai:generate"):
            raise PermissionException("没有使用AI生成功能的权限")
        
        # 检查文档权限
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if document.project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为此文档生成AI内容")
        
        # 创建AI生成记录
        generation_in = AIGenerationCreate(
            document_id=document_id,
            user_id=current_user.id,
            prompt=request.prompt,
            generation_config=request.config.dict() if request.config else None,
            status=AIGenerationStatus.PENDING,
            metadata={
                "context": request.context,
                "section": request.section,
                "model": "glm-4.6"
            }
        )
        
        generation = self.create_generation(db=db, generation_in=generation_in, current_user=current_user)
        
        # 提交异步任务
        task_id = submit_generation_task(
            generation_id=generation.id,
            prompt=request.prompt,
            config=request.config.dict() if request.config else {}
        )
        
        # 更新生成记录，添加任务ID
        self.update_generation(
            db=db,
            generation_id=generation.id,
            generation_in=AIGenerationUpdate(
                metadata={
                    **(generation.metadata or {}),
                    "task_id": task_id
                }
            ),
            current_user=current_user
        )
        
        return AIGenerationResponse(
            generation_id=generation.id,
            status=AIGenerationStatus.PENDING,
            message="AI生成任务已提交",
            task_id=task_id
        )
    
    async def generate_emergency_plan(
        self,
        db: Session,
        *,
        plan_type: str,
        company_info: Dict[str, Any],
        document_id: int,
        current_user: User
    ) -> AIGenerationResponse:
        """生成应急预案"""
        # 检查权限
        if not has_permission(current_user, "ai:generate"):
            raise PermissionException("没有使用AI生成功能的权限")
        
        # 检查文档权限
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if document.project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为此文档生成应急预案")
        
        # 构建提示词
        prompt = f"请根据以下企业信息生成一份详细的{plan_type}应急预案：\n\n"
        for key, value in company_info.items():
            prompt += f"- {key}：{value}\n"
        
        # 创建AI生成记录
        generation_in = AIGenerationCreate(
            document_id=document_id,
            user_id=current_user.id,
            prompt=prompt,
            generation_config={
                "temperature": 0.3,
                "max_tokens": 4000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            },
            status=AIGenerationStatus.PENDING,
            metadata={
                "type": "emergency_plan",
                "plan_type": plan_type,
                "company_info": company_info,
                "model": "glm-4.6"
            }
        )
        
        generation = self.create_generation(db=db, generation_in=generation_in, current_user=current_user)
        
        # 提交异步任务
        task_id = submit_emergency_plan_task(
            generation_id=generation.id,
            plan_type=plan_type,
            company_info=company_info
        )
        
        # 更新生成记录，添加任务ID
        self.update_generation(
            db=db,
            generation_id=generation.id,
            generation_in=AIGenerationUpdate(
                metadata={
                    **(generation.metadata or {}),
                    "task_id": task_id
                }
            ),
            current_user=current_user
        )
        
        return AIGenerationResponse(
            generation_id=generation.id,
            status=AIGenerationStatus.PENDING,
            message=f"{plan_type}应急预案生成任务已提交",
            task_id=task_id
        )
    
    async def generate_environmental_assessment(
        self,
        db: Session,
        *,
        project_info: Dict[str, Any],
        document_id: int,
        current_user: User
    ) -> AIGenerationResponse:
        """生成环评报告"""
        # 检查权限
        if not has_permission(current_user, "ai:generate"):
            raise PermissionException("没有使用AI生成功能的权限")
        
        # 检查文档权限
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if document.project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为此文档生成环评报告")
        
        # 构建提示词
        prompt = f"请根据以下项目信息生成环境影响评价报告：\n\n"
        for key, value in project_info.items():
            prompt += f"- {key}：{value}\n"
        
        # 创建AI生成记录
        generation_in = AIGenerationCreate(
            document_id=document_id,
            user_id=current_user.id,
            prompt=prompt,
            generation_config={
                "temperature": 0.2,
                "max_tokens": 5000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            },
            status=AIGenerationStatus.PENDING,
            metadata={
                "type": "environmental_assessment",
                "project_info": project_info,
                "model": "glm-4.6"
            }
        )
        
        generation = self.create_generation(db=db, generation_in=generation_in, current_user=current_user)
        
        # 提交异步任务
        task_id = submit_environmental_assessment_task(
            generation_id=generation.id,
            project_info=project_info
        )
        
        # 更新生成记录，添加任务ID
        self.update_generation(
            db=db,
            generation_id=generation.id,
            generation_in=AIGenerationUpdate(
                metadata={
                    **(generation.metadata or {}),
                    "task_id": task_id
                }
            ),
            current_user=current_user
        )
        
        return AIGenerationResponse(
            generation_id=generation.id,
            status=AIGenerationStatus.PENDING,
            message="环评报告生成任务已提交",
            task_id=task_id
        )
    
    # 任务状态管理
    def check_generation_status(
        self,
        db: Session,
        *,
        generation_id: int,
        current_user: User
    ) -> AIGenerationStatusInfo:
        """检查生成状态"""
        generation = self.crud_ai_generation.get(db, id=generation_id)
        if not generation:
            raise NotFoundException(f"AI生成记录 {generation_id} 不存在")
        
        # 检查权限
        if not self.crud_ai_generation._can_modify_generation(generation, current_user):
            raise PermissionException("没有权限查看此AI生成记录的状态")
        
        # 获取任务ID
        task_id = None
        if generation.metadata and "task_id" in generation.metadata:
            task_id = generation.metadata["task_id"]
        
        # 如果有任务ID，检查任务状态
        if task_id:
            task_status = task_manager.get_task_status(task_id)
            if task_status and task_status != generation.status.value:
                # 更新生成记录状态
                new_status = AIGenerationStatus.PENDING
                if task_status == "SUCCESS":
                    new_status = AIGenerationStatus.COMPLETED
                elif task_status == "FAILURE":
                    new_status = AIGenerationStatus.FAILED
                elif task_status == "RETRY":
                    new_status = AIGenerationStatus.PROCESSING
                elif task_status == "REVOKED":
                    new_status = AIGenerationStatus.FAILED
                
                self.update_generation(
                    db=db,
                    generation_id=generation_id,
                    generation_in=AIGenerationUpdate(status=new_status),
                    current_user=current_user
                )
                
                generation.status = new_status
        
        # 获取任务结果
        task_result = None
        if task_id and generation.status == AIGenerationStatus.COMPLETED:
            task_result = task_manager.get_task_result(task_id)
            if task_result and "content" in task_result:
                # 更新生成记录内容
                self.update_generation(
                    db=db,
                    generation_id=generation_id,
                    generation_in=AIGenerationUpdate(generated_content=task_result["content"]),
                    current_user=current_user
                )
                
                generation.generated_content = task_result["content"]
        
        return AIGenerationStatusInfo(
            generation_id=generation_id,
            status=generation.status,
            task_id=task_id,
            task_status=task_status,
            task_result=task_result,
            created_at=generation.created_at,
            updated_at=generation.updated_at,
            completed_at=generation.completed_at
        )
    
    def process_generation_async(
        self,
        db: Session,
        *,
        generation_id: int,
        current_user: User
    ) -> bool:
        """启动异步处理"""
        generation = self.crud_ai_generation.get(db, id=generation_id)
        if not generation:
            raise NotFoundException(f"AI生成记录 {generation_id} 不存在")
        
        # 检查权限
        if not self.crud_ai_generation._can_modify_generation(generation, current_user):
            raise PermissionException("没有权限处理此AI生成记录")
        
        # 如果状态不是待处理，直接返回
        if generation.status != AIGenerationStatus.PENDING:
            return False
        
        # 更新状态为处理中
        self.update_generation(
            db=db,
            generation_id=generation_id,
            generation_in=AIGenerationUpdate(status=AIGenerationStatus.PROCESSING),
            current_user=current_user
        )
        
        # 根据生成类型提交相应的任务
        if generation.metadata and "type" in generation.metadata:
            gen_type = generation.metadata["type"]
            
            if gen_type == "emergency_plan" and "plan_type" in generation.metadata and "company_info" in generation.metadata:
                task_id = submit_emergency_plan_task(
                    generation_id=generation_id,
                    plan_type=generation.metadata["plan_type"],
                    company_info=generation.metadata["company_info"]
                )
            elif gen_type == "environmental_assessment" and "project_info" in generation.metadata:
                task_id = submit_environmental_assessment_task(
                    generation_id=generation_id,
                    project_info=generation.metadata["project_info"]
                )
            else:
                # 默认内容生成
                task_id = submit_generation_task(
                    generation_id=generation_id,
                    prompt=generation.prompt,
                    config=generation.generation_config or {}
                )
            
            # 更新生成记录，添加任务ID
            self.update_generation(
                db=db,
                generation_id=generation_id,
                generation_in=AIGenerationUpdate(
                    metadata={
                        **(generation.metadata or {}),
                        "task_id": task_id
                    }
                ),
                current_user=current_user
            )
            
            return True
        
        return False
    
    # 模板管理
    def get_all_templates(self) -> List[AIGenerationTemplate]:
        """获取所有模板"""
        templates = [
            AIGenerationTemplate(
                id="emergency_plan",
                name="应急预案模板",
                description="用于生成各类应急预案的模板",
                type="emergency_plan",
                config={
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                },
                is_default=True,
                is_active=True
            ),
            AIGenerationTemplate(
                id="environmental_assessment",
                name="环评报告模板",
                description="用于生成环境影响评价报告的模板",
                type="environmental_assessment",
                config={
                    "temperature": 0.2,
                    "max_tokens": 5000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                },
                is_default=True,
                is_active=True
            ),
            AIGenerationTemplate(
                id="content_enhancement",
                name="内容增强模板",
                description="用于增强文档内容的模板",
                type="content_enhancement",
                config={
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                },
                is_default=True,
                is_active=True
            )
        ]
        
        return templates
    
    def get_template_by_type(self, template_type: str) -> AIGenerationTemplate:
        """根据类型获取模板"""
        templates = self.get_all_templates()
        for template in templates:
            if template.type == template_type:
                return template
        
        raise ValidationException(f"模板类型 {template_type} 不存在")


# 创建实例
crud_ai_generation = CRUDAIGeneration(AIGeneration)
ai_generation_service = AIGenerationService()