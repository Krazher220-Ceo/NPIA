"""
API endpoints для интеграций
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.models.integrations import ExternalSystem
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter
from sqlalchemy import select

router = APIRouter()


@router.get("/")
async def list_external_systems(
    factory_id: Optional[UUID] = Query(None),
    system_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список внешних систем
    Для не-админов показываются только системы их завода
    """
    query = select(ExternalSystem)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(ExternalSystem.factory_id == user_factory_id)
    elif factory_id:
        from app.api.v1.endpoints.rbac import check_factory_access
        check_factory_access(current_user, factory_id)
        query = query.where(ExternalSystem.factory_id == factory_id)
    
    if system_type:
        query = query.where(ExternalSystem.system_type == system_type)
    if is_active is not None:
        query = query.where(ExternalSystem.is_active == is_active)
    
    result = await db.execute(query)
    systems = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(s.id),
                "factory_id": str(s.factory_id) if s.factory_id else None,
                "system_type": s.system_type,
                "name": s.name,
                "connection_type": s.connection_type,
                "sync_frequency": s.sync_frequency,
                "is_active": s.is_active,
                "last_sync_at": s.last_sync_at.isoformat() if s.last_sync_at else None,
            }
            for s in systems
        ]
    }

