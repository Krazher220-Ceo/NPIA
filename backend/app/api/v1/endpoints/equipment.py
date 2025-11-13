"""
API endpoints для оборудования
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.models.equipment import Equipment
from app.models.user import User
from app.models.factory import Factory
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter, check_factory_access, check_role
from sqlalchemy import select, func

router = APIRouter()


@router.get("/")
async def list_equipment(
    factory_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    equipment_type: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список оборудования с фильтрами
    Для не-админов показывается только оборудование их завода
    """
    query = select(Equipment)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        # Если пользователь не админ, показываем только его завод
        effective_factory_id = user_factory_id
    else:
        # Админ может фильтровать по любому заводу
        effective_factory_id = factory_id
    
    if effective_factory_id:
        query = query.where(Equipment.factory_id == effective_factory_id)
    elif factory_id:
        query = query.where(Equipment.factory_id == factory_id)
    
    if status:
        query = query.where(Equipment.status == status)
    if equipment_type:
        query = query.where(Equipment.equipment_type_id == equipment_type)
    if search:
        query = query.where(Equipment.name.ilike(f"%{search}%"))
    
    # Подсчет общего количества
    count_query = select(func.count()).select_from(Equipment)
    if effective_factory_id:
        count_query = count_query.where(Equipment.factory_id == effective_factory_id)
    elif factory_id:
        count_query = count_query.where(Equipment.factory_id == factory_id)
    if status:
        count_query = count_query.where(Equipment.status == status)
    if equipment_type:
        count_query = count_query.where(Equipment.equipment_type_id == equipment_type)
    if search:
        count_query = count_query.where(Equipment.name.ilike(f"%{search}%"))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Получение данных с пагинацией
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    equipment_list = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(e.id),
                "name": e.name,
                "factory_id": str(e.factory_id),
                "status": e.status,
                "health_score": float(e.health_score) if e.health_score else None,
                "workshop": e.workshop,
                "line": e.line,
            }
            for e in equipment_list
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{equipment_id}")
async def get_equipment(
    equipment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию об оборудовании
    """
    query = select(Equipment).where(Equipment.id == equipment_id)
    result = await db.execute(query)
    equipment = result.scalar_one_or_none()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    
    # Проверка доступа к заводу оборудования
    check_factory_access(current_user, equipment.factory_id)
    
    return {
        "id": str(equipment.id),
        "name": equipment.name,
        "factory_id": str(equipment.factory_id),
        "serial_number": equipment.serial_number,
        "status": equipment.status,
        "health_score": float(equipment.health_score) if equipment.health_score else None,
        "workshop": equipment.workshop,
        "line": equipment.line,
        "manufacturer": equipment.manufacturer,
        "model": equipment.model,
        "power_consumption_kw": float(equipment.power_consumption_kw) if equipment.power_consumption_kw else None,
    }

