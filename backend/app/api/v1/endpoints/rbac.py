"""
Утилиты для проверки прав доступа (RBAC)
"""
from fastapi import HTTPException, status
from app.models.user import User
from uuid import UUID
from typing import Optional


def check_role(user: User, allowed_roles: list[str]):
    """Проверка роли пользователя"""
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещен. Требуются роли: {', '.join(allowed_roles)}"
        )


def check_factory_access(user: User, factory_id: UUID):
    """Проверка доступа к заводу"""
    # Админ имеет доступ ко всем заводам
    if user.role == "admin":
        return
    
    # Пользователь должен быть привязан к заводу
    if not user.factory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не привязан к заводу"
        )
    
    # Проверка соответствия завода
    if str(user.factory_id) != str(factory_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Вы можете работать только с данными своего завода"
        )


async def check_equipment_limit(user: User, current_count: int, db_session):
    """Проверка лимита оборудования по подписке"""
    # Админ и корпоративный план не имеют лимитов
    if user.role == "admin":
        return
    
    # Получаем активную подписку завода
    from app.models.subscription import Subscription
    from sqlalchemy import select
    from datetime import date
    
    if not user.factory_id:
        return
    
    subscription = await db_session.scalar(
        select(Subscription)
        .where(Subscription.factory_id == user.factory_id)
        .where(Subscription.is_active == True)
        .where(Subscription.end_date >= date.today())
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    
    if subscription and subscription.equipment_limit:
        if current_count >= subscription.equipment_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Достигнут лимит оборудования ({subscription.equipment_limit}). Обновите подписку."
            )


def get_user_factory_filter(user: User) -> Optional[UUID]:
    """Получить factory_id для фильтрации (если пользователь не админ)"""
    if user.role == "admin":
        return None
    return user.factory_id

