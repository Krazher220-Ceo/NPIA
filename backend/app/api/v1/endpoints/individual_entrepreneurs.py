"""
API endpoints для управления индивидуальными предпринимателями (ИП)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.models.individual_entrepreneur import IndividualEntrepreneur, ip_factory_association
from app.models.factory import Factory
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter()


class IPCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    bin: Optional[str] = None
    plan_code: str  # basic, analytics, ip
    factory_ids: Optional[List[str]] = None  # Для ИП тарифа - список ID заводов


class IPUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bin: Optional[str] = None
    plan_code: Optional[str] = None
    is_active: Optional[bool] = None
    factory_ids: Optional[List[str]] = None


class IPResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    bin: Optional[str]
    plan_code: str
    factory_limit: Optional[str]
    is_active: bool
    user_id: Optional[str]
    factory_ids: List[str]
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=IPResponse, status_code=status.HTTP_201_CREATED)
async def create_ip(
    ip_data: IPCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать нового ИП (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора"
        )
    
    # Проверка существующего email
    existing = await db.scalar(
        select(IndividualEntrepreneur).where(IndividualEntrepreneur.email == ip_data.email)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ИП с таким email уже существует"
        )
    
    # Создание ИП
    new_ip = IndividualEntrepreneur(
        full_name=ip_data.full_name,
        email=ip_data.email,
        phone=ip_data.phone,
        bin=ip_data.bin,
        plan_code=ip_data.plan_code,
        factory_limit="1" if ip_data.plan_code in ["basic", "analytics"] else None
    )
    
    db.add(new_ip)
    await db.flush()
    
    # Связывание с заводами (если указаны)
    if ip_data.factory_ids:
        for factory_id_str in ip_data.factory_ids:
            try:
                factory_id = UUID(factory_id_str)
                factory = await db.scalar(select(Factory).where(Factory.id == factory_id))
                if factory:
                    new_ip.factories.append(factory)
            except ValueError:
                pass
    
    await db.commit()
    await db.refresh(new_ip)
    
    # Получаем список ID заводов
    factory_ids = [str(f.id) for f in new_ip.factories]
    
    return IPResponse(
        id=str(new_ip.id),
        full_name=new_ip.full_name,
        email=new_ip.email,
        phone=new_ip.phone,
        bin=new_ip.bin,
        plan_code=new_ip.plan_code,
        factory_limit=new_ip.factory_limit,
        is_active=new_ip.is_active,
        user_id=str(new_ip.user_id) if new_ip.user_id else None,
        factory_ids=factory_ids,
        created_at=new_ip.created_at.isoformat() if new_ip.created_at else "",
    )


@router.get("/", response_model=List[IPResponse])
async def list_ips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех ИП (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    result = await db.execute(select(IndividualEntrepreneur))
    ips = result.scalars().all()
    
    return [
        IPResponse(
            id=str(ip.id),
            full_name=ip.full_name,
            email=ip.email,
            phone=ip.phone,
            bin=ip.bin,
            plan_code=ip.plan_code,
            factory_limit=ip.factory_limit,
            is_active=ip.is_active,
            user_id=str(ip.user_id) if ip.user_id else None,
            factory_ids=[str(f.id) for f in ip.factories],
            created_at=ip.created_at.isoformat() if ip.created_at else "",
        )
        for ip in ips
    ]


@router.get("/{ip_id}", response_model=IPResponse)
async def get_ip(
    ip_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить детали ИП (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    ip = await db.scalar(select(IndividualEntrepreneur).where(IndividualEntrepreneur.id == ip_id))
    if not ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ИП не найден"
        )
    
    return IPResponse(
        id=str(ip.id),
        full_name=ip.full_name,
        email=ip.email,
        phone=ip.phone,
        bin=ip.bin,
        plan_code=ip.plan_code,
        factory_limit=ip.factory_limit,
        is_active=ip.is_active,
        user_id=str(ip.user_id) if ip.user_id else None,
        factory_ids=[str(f.id) for f in ip.factories],
        created_at=ip.created_at.isoformat() if ip.created_at else "",
    )


@router.put("/{ip_id}", response_model=IPResponse)
async def update_ip(
    ip_id: UUID,
    ip_data: IPUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные ИП (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    ip = await db.scalar(select(IndividualEntrepreneur).where(IndividualEntrepreneur.id == ip_id))
    if not ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ИП не найден"
        )
    
    # Обновление полей
    if ip_data.full_name is not None:
        ip.full_name = ip_data.full_name
    if ip_data.phone is not None:
        ip.phone = ip_data.phone
    if ip_data.bin is not None:
        ip.bin = ip_data.bin
    if ip_data.plan_code is not None:
        ip.plan_code = ip_data.plan_code
        ip.factory_limit = "1" if ip_data.plan_code in ["basic", "analytics"] else None
    if ip_data.is_active is not None:
        ip.is_active = ip_data.is_active
    
    # Обновление связей с заводами
    if ip_data.factory_ids is not None:
        ip.factories.clear()
        for factory_id_str in ip_data.factory_ids:
            try:
                factory_id = UUID(factory_id_str)
                factory = await db.scalar(select(Factory).where(Factory.id == factory_id))
                if factory:
                    ip.factories.append(factory)
            except ValueError:
                pass
    
    await db.commit()
    await db.refresh(ip)
    
    return IPResponse(
        id=str(ip.id),
        full_name=ip.full_name,
        email=ip.email,
        phone=ip.phone,
        bin=ip.bin,
        plan_code=ip.plan_code,
        factory_limit=ip.factory_limit,
        is_active=ip.is_active,
        user_id=str(ip.user_id) if ip.user_id else None,
        factory_ids=[str(f.id) for f in ip.factories],
        created_at=ip.created_at.isoformat() if ip.created_at else "",
    )


@router.delete("/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ip(
    ip_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить ИП (только для админов)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    ip = await db.scalar(select(IndividualEntrepreneur).where(IndividualEntrepreneur.id == ip_id))
    if not ip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ИП не найден"
        )
    
    await db.delete(ip)
    await db.commit()

