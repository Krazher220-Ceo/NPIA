"""
API endpoints для заявок на роль руководителя
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.models.application import Application
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter()


class ApplicationCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    plan_code: Optional[str] = None  # basic, analytics, ip
    description: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    plan_code: Optional[str]
    description: Optional[str]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    created_user_id: Optional[str]
    created_username: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[str]
    rejection_reason: Optional[str]


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Подать заявку на роль руководителя"""
    # Проверка существующего email
    existing = await db.scalar(
        select(Application).where(Application.email == application.email)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка с таким email уже существует"
        )
    
    # Проверка существующего пользователя
    existing_user = await db.scalar(
        select(User).where(User.email == application.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    new_application = Application(
        full_name=application.full_name,
        email=application.email,
        phone=application.phone,
        plan_code=application.plan_code,
        description=application.description,
        status="new"
    )
    
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)
    
    return ApplicationResponse(
        id=str(new_application.id),
        full_name=new_application.full_name,
        email=new_application.email,
        phone=new_application.phone,
        plan_code=new_application.plan_code,
        description=new_application.description,
        status=new_application.status,
        created_at=new_application.created_at.isoformat() if new_application.created_at else "",
    )


@router.get("/", response_model=list[ApplicationDetailResponse])
async def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список заявок (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора"
        )
    
    query = select(Application)
    
    if status_filter:
        query = query.where(Application.status == status_filter)
    
    query = query.order_by(desc(Application.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return [
        ApplicationDetailResponse(
            id=str(app.id),
            full_name=app.full_name,
            email=app.email,
            phone=app.phone,
            plan_code=app.plan_code,
            description=app.description,
            status=app.status,
            created_at=app.created_at.isoformat() if app.created_at else "",
            created_user_id=str(app.created_user_id) if app.created_user_id else None,
            created_username=app.created_username,
            reviewed_by=str(app.reviewed_by) if app.reviewed_by else None,
            reviewed_at=app.reviewed_at.isoformat() if app.reviewed_at else None,
            rejection_reason=app.rejection_reason,
        )
        for app in applications
    ]


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить детали заявки (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    application = await db.scalar(
        select(Application).where(Application.id == application_id)
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    return ApplicationDetailResponse(
        id=str(application.id),
        full_name=application.full_name,
        email=application.email,
        phone=application.phone,
        plan_code=application.plan_code,
        description=application.description,
        status=application.status,
        created_at=application.created_at.isoformat() if application.created_at else "",
        created_user_id=str(application.created_user_id) if application.created_user_id else None,
        created_username=application.created_username,
        reviewed_by=str(application.reviewed_by) if application.reviewed_by else None,
        reviewed_at=application.reviewed_at.isoformat() if application.reviewed_at else None,
        rejection_reason=application.rejection_reason,
    )

