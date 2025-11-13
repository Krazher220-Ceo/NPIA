"""
API endpoints для заводов
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.models.factory import Factory, Industry
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter, check_factory_access
from sqlalchemy import select, func

router = APIRouter()


@router.get("/")
async def list_factories(
    industry_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список заводов с фильтрами
    Для не-админов показываются только заводы, к которым есть доступ
    """
    query = select(Factory)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(Factory.id == user_factory_id)
    
    if industry_id:
        query = query.where(Factory.industry_id == industry_id)
    if status:
        query = query.where(Factory.status == status)
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(Factory)
    if user_factory_id:
        count_query = count_query.where(Factory.id == user_factory_id)
    if industry_id:
        count_query = count_query.where(Factory.industry_id == industry_id)
    if status:
        count_query = count_query.where(Factory.status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Получение данных с пагинацией
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    factories = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(f.id),
                "name": f.name,
                "city": f.city,
                "status": f.status,
                "equipment_count": f.equipment_count,
            }
            for f in factories
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{factory_id}")
async def get_factory(
    factory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию о заводе
    """
    # Проверка доступа к заводу
    check_factory_access(current_user, factory_id)
    
    query = select(Factory).where(Factory.id == factory_id)
    result = await db.execute(query)
    factory = result.scalar_one_or_none()
    
    if not factory:
        raise HTTPException(status_code=404, detail="Завод не найден")
    
    return {
        "id": str(factory.id),
        "name": factory.name,
        "industry_id": str(factory.industry_id) if factory.industry_id else None,
        "region": factory.region,
        "city": factory.city,
        "address": factory.address,
        "director_name": factory.director_name,
        "phone": factory.phone,
        "email": factory.email,
        "production_capacity": float(factory.production_capacity) if factory.production_capacity else None,
        "equipment_count": factory.equipment_count,
        "status": factory.status,
        "subscription_plan": factory.subscription_plan,
    }


@router.get("/industries/")
async def list_industries(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список отраслей промышленности
    """
    query = select(Industry)
    result = await db.execute(query)
    industries = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(i.id),
                "name_ru": i.name_ru,
                "name_kk": i.name_kk,
                "name_en": i.name_en,
                "code": i.code,
            }
            for i in industries
        ]
    }

