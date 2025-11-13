"""
API endpoints для подписок и тарифов
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.models.subscription import Subscription
from app.models.factory import Factory
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter, check_factory_access
from sqlalchemy import select, func

router = APIRouter()


@router.get("/")
async def list_subscriptions(
    factory_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список подписок
    Для не-админов показываются только подписки их завода
    """
    query = select(Subscription)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(Subscription.factory_id == user_factory_id)
    elif factory_id:
        # Проверка доступа к заводу
        check_factory_access(current_user, factory_id)
        query = query.where(Subscription.factory_id == factory_id)
    
    if is_active is not None:
        query = query.where(Subscription.is_active == is_active)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(s.id),
                "factory_id": str(s.factory_id),
                "plan": s.plan,
                "start_date": s.start_date.isoformat() if s.start_date else None,
                "end_date": s.end_date.isoformat() if s.end_date else None,
                "equipment_limit": s.equipment_limit,
                "equipment_count": s.equipment_count,
                "monthly_price": float(s.monthly_price) if s.monthly_price else None,
                "currency": s.currency,
                "is_trial": s.is_trial,
                "is_active": s.is_active,
            }
            for s in subscriptions
        ]
    }


@router.get("/plans")
async def get_subscription_plans():
    """Получить информацию о тарифных планах"""
    return {
        "plans": [
            {
                "code": "basic",
                "name": "Базовый",
                "price": 150000,
                "currency": "KZT",
                "equipment_limit": 10,
                "features": [
                    "Сбор данных в реальном времени",
                    "Базовые дашборды",
                    "Экспорт отчётов (CSV, Excel, PDF)",
                    "Мобильное приложение",
                    "Техподдержка email"
                ]
            },
            {
                "code": "analytics",
                "name": "Аналитический",
                "price": 450000,
                "currency": "KZT",
                "equipment_limit": 50,
                "features": [
                    "Всё из Базового",
                    "ИИ-анализ и предиктивная аналитика",
                    "Прогнозирование отказов (точность 85%+)",
                    "Рекомендации по оптимизации",
                    "Расчёт OEE и других KPI",
                    "Оповещения (SMS, email, Telegram)",
                    "API для интеграций",
                    "Техподдержка по телефону"
                ]
            },
            {
                "code": "corporate",
                "name": "Корпоративный",
                "price": 1200000,
                "currency": "KZT",
                "equipment_limit": None,
                "features": [
                    "Всё из Аналитического",
                    "Неограниченное количество оборудования",
                    "Мультизаводская аналитика",
                    "Интеграция с ERP/MES",
                    "Белый label",
                    "Выделенный менеджер",
                    "Техподдержка 24/7",
                    "Индивидуальная инфраструктура"
                ]
            }
        ]
    }

