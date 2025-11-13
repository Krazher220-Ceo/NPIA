"""
API endpoints для дашборда
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.factory import Factory
from app.models.equipment import Equipment
from app.models.analytics import KPICalculation, Anomaly, Recommendation
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter
from typing import Dict, Any

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получить общую статистику для дашборда
    Для не-админов показывается статистика только их завода
    """
    user_factory_id = get_user_factory_filter(current_user)
    
    # Количество заводов (для не-админов всегда 1)
    if user_factory_id:
        factories_count = 1
    else:
        factories_count = await db.scalar(select(func.count(Factory.id))) or 0
    
    # Количество оборудования
    equipment_query = select(func.count(Equipment.id))
    if user_factory_id:
        equipment_query = equipment_query.where(Equipment.factory_id == user_factory_id)
    equipment_count = await db.scalar(equipment_query) or 0
    
    # Активное оборудование
    active_equipment_query = select(func.count(Equipment.id)).where(Equipment.status == "operational")
    if user_factory_id:
        active_equipment_query = active_equipment_query.where(Equipment.factory_id == user_factory_id)
    active_equipment = await db.scalar(active_equipment_query) or 0
    
    # Активные аномалии (только для оборудования завода пользователя)
    from app.models.equipment import Equipment as EqModel
    anomalies_query = (
        select(func.count(Anomaly.id))
        .join(EqModel, Anomaly.equipment_id == EqModel.id)
        .where(Anomaly.status.in_(["new", "acknowledged"]))
    )
    if user_factory_id:
        anomalies_query = anomalies_query.where(EqModel.factory_id == user_factory_id)
    active_anomalies = await db.scalar(anomalies_query) or 0
    
    # Новые рекомендации (только для завода пользователя)
    recommendations_query = select(func.count(Recommendation.id)).where(Recommendation.status == "new")
    if user_factory_id:
        recommendations_query = recommendations_query.where(
            Recommendation.target_type == "factory"
        ).where(Recommendation.target_id == user_factory_id)
    new_recommendations = await db.scalar(recommendations_query) or 0
    
    # Последний KPI (сегодня) - только для завода пользователя
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    kpi_query = (
        select(KPICalculation)
        .where(KPICalculation.period_type == "daily")
        .where(KPICalculation.period_start >= today)
    )
    if user_factory_id:
        kpi_query = kpi_query.where(
            KPICalculation.entity_type == "factory"
        ).where(KPICalculation.entity_id == user_factory_id)
    
    latest_kpi = await db.scalar(kpi_query.order_by(KPICalculation.period_start.desc()).limit(1))
    
    avg_oee = None
    if latest_kpi:
        # Средний OEE за сегодня
        avg_oee_query = (
            select(func.avg(KPICalculation.oee_score))
            .where(KPICalculation.period_type == "daily")
            .where(KPICalculation.period_start >= today)
        )
        if user_factory_id:
            avg_oee_query = avg_oee_query.where(
                KPICalculation.entity_type == "factory"
            ).where(KPICalculation.entity_id == user_factory_id)
        
        avg_oee_result = await db.scalar(avg_oee_query)
        avg_oee = float(avg_oee_result) if avg_oee_result else None
    
    return {
        "factories_count": factories_count,
        "equipment_count": equipment_count,
        "active_equipment": active_equipment,
        "active_alerts": active_anomalies,
        "new_recommendations": new_recommendations,
        "average_oee": round(avg_oee, 2) if avg_oee else None,
    }


@router.get("/kpi-summary")
async def get_kpi_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получить сводку KPI за последние N дней
    Для не-админов показывается статистика только их завода
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    user_factory_id = get_user_factory_filter(current_user)
    
    # Агрегированные KPI
    kpi_query = select(
        func.avg(KPICalculation.oee_score).label("avg_oee"),
        func.avg(KPICalculation.availability).label("avg_availability"),
        func.avg(KPICalculation.performance).label("avg_performance"),
        func.avg(KPICalculation.quality).label("avg_quality"),
        func.sum(KPICalculation.downtime_minutes).label("total_downtime"),
    ).where(
        KPICalculation.period_type == "daily"
    ).where(
        KPICalculation.period_start >= start_date
    )
    
    # Фильтрация по заводу пользователя
    if user_factory_id:
        kpi_query = kpi_query.where(
            KPICalculation.entity_type == "factory"
        ).where(
            KPICalculation.entity_id == user_factory_id
        )
    
    result = await db.execute(kpi_query)
    row = result.first()
    
    return {
        "period_days": days,
        "average_oee": round(float(row.avg_oee), 2) if row.avg_oee else None,
        "average_availability": round(float(row.avg_availability), 2) if row.avg_availability else None,
        "average_performance": round(float(row.avg_performance), 2) if row.avg_performance else None,
        "average_quality": round(float(row.avg_quality), 2) if row.avg_quality else None,
        "total_downtime_minutes": int(row.total_downtime) if row.total_downtime else 0,
    }

