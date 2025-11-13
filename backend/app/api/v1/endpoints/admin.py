"""
API endpoints для админ-панели (одобрение заявок, создание аккаунтов)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.application import Application
from app.models.factory import Factory
from app.core.security import get_password_hash
from app.utils.pdf_generator import generate_credentials_pdf
from fastapi.responses import Response
import secrets
import string

router = APIRouter()


def generate_secure_password(length: int = 16) -> str:
    """Генерация безопасного пароля"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


class ApproveApplicationRequest(BaseModel):
    username: str
    factory_id: Optional[UUID] = None


class ApproveApplicationResponse(BaseModel):
    success: bool
    user_id: str
    username: str
    email: str
    password: str
    message: str


@router.post("/applications/{application_id}/approve", response_model=ApproveApplicationResponse)
async def approve_application(
    application_id: UUID,
    request: ApproveApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Одобрить заявку и создать аккаунт (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора"
        )
    
    # Получаем заявку
    application = await db.scalar(
        select(Application).where(Application.id == application_id)
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    if application.status != "new":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Заявка уже обработана (статус: {application.status})"
        )
    
    # Проверка уникальности username
    existing_user = await db.scalar(
        select(User).where(User.email == application.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Проверка username
    existing_username = await db.scalar(
        select(User).where(User.email == request.username)
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )
    
    # Генерация пароля
    password = generate_secure_password(16)
    password_hash = get_password_hash(password)
    
    # Получаем factory_id (если не указан, берем первый)
    factory_id = request.factory_id
    if not factory_id:
        factory = await db.scalar(select(Factory).limit(1))
        if factory:
            factory_id = factory.id
    
    # Создаем пользователя
    new_user = User(
        email=application.email,
        password_hash=password_hash,
        full_name=application.full_name,
        phone=application.phone,
        position="Руководитель",
        factory_id=factory_id,
        role="manager",
        is_active=True,
        is_verified=True,
        language="ru",
        timezone="Asia/Almaty"
    )
    
    db.add(new_user)
    
    # Обновляем заявку
    application.status = "approved"
    application.created_user_id = new_user.id
    application.created_username = request.username
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.utcnow()
    
    # Генерация PDF
    pdf_data = {
        'username': request.username,
        'password': password,
        'email': application.email
    }
    pdf_buffer = generate_credentials_pdf(pdf_data)
    
    # Сохраняем PDF (в реальном проекте - в S3 или файловое хранилище)
    # Здесь просто сохраняем путь в БД
    pdf_filename = f"credentials_{request.username}_{new_user.id}.pdf"
    application.password_pdf_url = f"/pdfs/{pdf_filename}"
    
    await db.commit()
    await db.refresh(new_user)
    
    return ApproveApplicationResponse(
        success=True,
        user_id=str(new_user.id),
        username=request.username,
        email=application.email,
        password=password,
        message="Аккаунт успешно создан"
    )


@router.get("/applications/{application_id}/pdf")
async def download_credentials_pdf(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Скачать PDF с данными для входа (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    application = await db.scalar(
        select(Application).where(Application.id == application_id)
    )
    
    if not application or application.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена или не одобрена"
        )
    
    if not application.created_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данные для входа не найдены"
        )
    
    # В реальном проекте здесь нужно получить пароль из безопасного хранилища
    # Для демонстрации генерируем новый PDF с placeholder
    pdf_data = {
        'username': application.created_username,
        'password': '*** (пароль был отправлен при создании аккаунта)',
        'email': application.email
    }
    
    pdf_buffer = generate_credentials_pdf(pdf_data)
    
    return Response(
        content=pdf_buffer.read(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=credentials_{application.created_username}.pdf"
        }
    )


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: UUID,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отклонить заявку (только для админов)"""
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
    
    if application.status != "new":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка уже обработана"
        )
    
    application.status = "rejected"
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.utcnow()
    application.rejection_reason = reason
    
    await db.commit()
    
    return {"success": True, "message": "Заявка отклонена"}

