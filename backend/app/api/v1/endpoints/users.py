"""
API endpoints для пользователей
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.api.v1.deps import get_current_user
from sqlalchemy import select

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о текущем пользователе
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "position": current_user.position,
        "role": current_user.role,
        "factory_id": str(current_user.factory_id) if current_user.factory_id else None,
        "language": current_user.language,
        "timezone": current_user.timezone,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
    }

