"""
API endpoints для метрик
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.metrics import MetricsCatalog, MetricsData
from app.models.user import User
from app.models.equipment import Equipment
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter, check_factory_access
from sqlalchemy import select, func

router = APIRouter()


@router.get("/catalog")
async def list_metrics_catalog(
    category: Optional[str] = Query(None),
    is_kpi: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить каталог метрик
    """
    query = select(MetricsCatalog)
    
    if category:
        query = query.where(MetricsCatalog.category == category)
    if is_kpi is not None:
        query = query.where(MetricsCatalog.is_kpi == is_kpi)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(m.id),
                "name_ru": m.name_ru,
                "code": m.code,
                "unit": m.unit,
                "category": m.category,
                "is_kpi": m.is_kpi,
                "is_critical": m.is_critical,
            }
            for m in metrics
        ]
    }


@router.get("/data")
async def get_metrics_data(
    equipment_id: UUID = Query(...),
    metric_id: Optional[UUID] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить исторические данные метрик
    Для не-админов доступны только данные оборудования их завода
    """
    # Проверка доступа к оборудованию
    equipment = await db.scalar(select(Equipment).where(Equipment.id == equipment_id))
    if not equipment:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    
    check_factory_access(current_user, equipment.factory_id)
    
    query = select(MetricsData).where(MetricsData.equipment_id == equipment_id)
    
    if metric_id:
        query = query.where(MetricsData.metric_id == metric_id)
    if start_time:
        query = query.where(MetricsData.timestamp >= start_time)
    if end_time:
        query = query.where(MetricsData.timestamp <= end_time)
    
    query = query.order_by(MetricsData.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    data_points = result.scalars().all()
    
    return {
        "equipment_id": str(equipment_id),
        "data_points": [
            {
                "timestamp": dp.timestamp.isoformat(),
                "value": float(dp.value) if dp.value else None,
                "is_anomaly": dp.is_anomaly,
                "is_critical": dp.is_critical,
            }
            for dp in data_points
        ]
    }

