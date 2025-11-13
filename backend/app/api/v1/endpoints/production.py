"""
API endpoints для производственных циклов и обслуживания
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.production import ProductionCycle, MaintenanceLog
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter
from fastapi import HTTPException
from sqlalchemy import select, desc

router = APIRouter()


@router.get("/cycles")
async def list_production_cycles(
    factory_id: Optional[UUID] = Query(None),
    equipment_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список производственных циклов
    Для не-админов показываются только циклы их завода
    """
    query = select(ProductionCycle)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(ProductionCycle.factory_id == user_factory_id)
    elif factory_id:
        query = query.where(ProductionCycle.factory_id == factory_id)
    
    if equipment_id:
        query = query.where(ProductionCycle.equipment_id == equipment_id)
    if status:
        query = query.where(ProductionCycle.status == status)
    
    query = query.order_by(desc(ProductionCycle.start_time)).offset(offset).limit(limit)
    result = await db.execute(query)
    cycles = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(c.id),
                "factory_id": str(c.factory_id),
                "equipment_id": str(c.equipment_id) if c.equipment_id else None,
                "start_time": c.start_time.isoformat() if c.start_time else None,
                "end_time": c.end_time.isoformat() if c.end_time else None,
                "product_name": c.product_name,
                "planned_quantity": float(c.planned_quantity) if c.planned_quantity else None,
                "actual_quantity": float(c.actual_quantity) if c.actual_quantity else None,
                "oee_score": float(c.oee_score) if c.oee_score else None,
                "status": c.status,
            }
            for c in cycles
        ],
        "limit": limit,
        "offset": offset
    }


@router.get("/maintenance")
async def list_maintenance_logs(
    equipment_id: Optional[UUID] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить журнал обслуживания
    Для не-админов показываются только записи оборудования их завода
    """
    from app.models.equipment import Equipment
    
    query = select(MaintenanceLog).join(Equipment, MaintenanceLog.equipment_id == Equipment.id)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(Equipment.factory_id == user_factory_id)
    
    if equipment_id:
        # Проверка доступа к оборудованию
        if user_factory_id:
            equipment = await db.scalar(select(Equipment).where(Equipment.id == equipment_id))
            if equipment and str(equipment.factory_id) != str(user_factory_id):
                raise HTTPException(status_code=403, detail="Доступ запрещен")
        query = query.where(MaintenanceLog.equipment_id == equipment_id)
    if type:
        query = query.where(MaintenanceLog.type == type)
    if status:
        query = query.where(MaintenanceLog.status == status)
    
    query = query.order_by(desc(MaintenanceLog.scheduled_date)).offset(offset).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(l.id),
                "equipment_id": str(l.equipment_id),
                "type": l.type,
                "title": l.title,
                "scheduled_date": l.scheduled_date.isoformat() if l.scheduled_date else None,
                "start_time": l.start_time.isoformat() if l.start_time else None,
                "end_time": l.end_time.isoformat() if l.end_time else None,
                "duration_minutes": l.duration_minutes,
                "cost": float(l.cost) if l.cost else None,
                "status": l.status,
            }
            for l in logs
        ],
        "limit": limit,
        "offset": offset
    }

