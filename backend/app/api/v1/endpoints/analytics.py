"""
API endpoints для аналитики
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.models.analytics import KPICalculation, Anomaly, Prediction, Recommendation
from app.models.user import User
from app.models.equipment import Equipment
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter, check_factory_access
from fastapi import HTTPException
from sqlalchemy import select, func, desc

router = APIRouter()


@router.get("/kpi")
async def get_kpi(
    entity_type: str = Query(..., description="factory, equipment, production_line"),
    entity_id: UUID = Query(...),
    period_type: str = Query("daily", description="hourly, daily, weekly, monthly"),
    limit: int = Query(30, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить KPI для сущности
    Для не-админов доступны только KPI их завода
    """
    # Проверка доступа
    user_factory_id = get_user_factory_filter(current_user)
    if entity_type == "factory":
        if user_factory_id and str(entity_id) != str(user_factory_id):
            raise HTTPException(status_code=403, detail="Доступ запрещен")
    elif entity_type == "equipment":
        # Проверка доступа к оборудованию
        equipment = await db.scalar(select(Equipment).where(Equipment.id == entity_id))
        if equipment:
            check_factory_access(current_user, equipment.factory_id)
    
    query = (
        select(KPICalculation)
        .where(KPICalculation.entity_type == entity_type)
        .where(KPICalculation.entity_id == entity_id)
        .where(KPICalculation.period_type == period_type)
        .order_by(desc(KPICalculation.period_start))
        .limit(limit)
    )
    
    result = await db.execute(query)
    kpi_data = result.scalars().all()
    
    return {
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "period_type": period_type,
        "kpi_data": [
            {
                "period_start": kpi.period_start.isoformat(),
                "period_end": kpi.period_end.isoformat(),
                "oee_score": float(kpi.oee_score) if kpi.oee_score else None,
                "availability": float(kpi.availability) if kpi.availability else None,
                "performance": float(kpi.performance) if kpi.performance else None,
                "quality": float(kpi.quality) if kpi.quality else None,
                "downtime_minutes": kpi.downtime_minutes,
            }
            for kpi in kpi_data
        ]
    }


@router.get("/anomalies")
async def list_anomalies(
    equipment_id: Optional[UUID] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список аномалий
    Для не-админов показываются только аномалии оборудования их завода
    """
    query = select(Anomaly).join(Equipment, Anomaly.equipment_id == Equipment.id)
    
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
        query = query.where(Anomaly.equipment_id == equipment_id)
    if severity:
        query = query.where(Anomaly.severity == severity)
    if status:
        query = query.where(Anomaly.status == status)
    
    query = query.order_by(desc(Anomaly.detected_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    anomalies = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(a.id),
                "equipment_id": str(a.equipment_id),
                "detected_at": a.detected_at.isoformat(),
                "severity": a.severity,
                "anomaly_score": float(a.anomaly_score) if a.anomaly_score else None,
                "anomaly_type": a.anomaly_type,
                "status": a.status,
            }
            for a in anomalies
        ],
        "limit": limit,
        "offset": offset
    }


@router.get("/predictions")
async def list_predictions(
    equipment_id: Optional[UUID] = Query(None),
    prediction_type: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список прогнозов
    Для не-админов показываются только прогнозы оборудования их завода
    """
    query = select(Prediction).join(Equipment, Prediction.equipment_id == Equipment.id)
    
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
        query = query.where(Prediction.equipment_id == equipment_id)
    if prediction_type:
        query = query.where(Prediction.prediction_type == prediction_type)
    
    query = query.order_by(desc(Prediction.created_at)).limit(limit)
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(p.id),
                "equipment_id": str(p.equipment_id),
                "prediction_type": p.prediction_type,
                "predicted_for": p.predicted_for.isoformat(),
                "confidence": float(p.confidence) if p.confidence else None,
                "recommended_action": p.recommended_action,
            }
            for p in predictions
        ]
    }


@router.get("/recommendations")
async def list_recommendations(
    target_type: Optional[str] = Query(None),
    target_id: Optional[UUID] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список рекомендаций
    Для не-админов показываются только рекомендации для их завода
    """
    query = select(Recommendation)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        # Показываем рекомендации только для завода пользователя
        query = query.where(Recommendation.target_type == "factory")
        query = query.where(Recommendation.target_id == user_factory_id)
    
    if target_type:
        query = query.where(Recommendation.target_type == target_type)
    if target_id:
        # Проверка доступа
        if user_factory_id and target_type == "factory" and str(target_id) != str(user_factory_id):
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        query = query.where(Recommendation.target_id == target_id)
    if priority:
        query = query.where(Recommendation.priority == priority)
    if status:
        query = query.where(Recommendation.status == status)
    
    query = query.order_by(desc(Recommendation.created_at)).limit(limit)
    result = await db.execute(query)
    recommendations = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(r.id),
                "target_type": r.target_type,
                "target_id": str(r.target_id),
                "title": r.title,
                "category": r.category,
                "priority": r.priority,
                "estimated_savings": float(r.estimated_savings) if r.estimated_savings else None,
                "status": r.status,
            }
            for r in recommendations
        ]
    }

