"""
API endpoints для отчетов
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.models.integrations import ReportTemplate, GeneratedReport
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.rbac import get_user_factory_filter
from sqlalchemy import select, desc

router = APIRouter()


@router.get("/templates")
async def list_report_templates(
    report_type: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список шаблонов отчетов
    Доступны всем авторизованным пользователям
    """
    query = select(ReportTemplate)
    
    if report_type:
        query = query.where(ReportTemplate.report_type == report_type)
    if is_public is not None:
        query = query.where(ReportTemplate.is_public == is_public)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "report_type": t.report_type,
                "format": t.format,
                "schedule": t.schedule,
                "is_public": t.is_public,
            }
            for t in templates
        ]
    }


@router.get("/generated")
async def list_generated_reports(
    factory_id: Optional[UUID] = Query(None),
    template_id: Optional[UUID] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список сгенерированных отчетов
    Для не-админов показываются только отчеты их завода
    """
    query = select(GeneratedReport)
    
    # Фильтрация по доступу пользователя
    user_factory_id = get_user_factory_filter(current_user)
    if user_factory_id:
        query = query.where(GeneratedReport.factory_id == user_factory_id)
    elif factory_id:
        from app.api.v1.endpoints.rbac import check_factory_access
        check_factory_access(current_user, factory_id)
        query = query.where(GeneratedReport.factory_id == factory_id)
    
    if template_id:
        query = query.where(GeneratedReport.template_id == template_id)
    
    query = query.order_by(desc(GeneratedReport.generated_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(r.id),
                "template_id": str(r.template_id) if r.template_id else None,
                "factory_id": str(r.factory_id) if r.factory_id else None,
                "period_start": r.period_start.isoformat() if r.period_start else None,
                "period_end": r.period_end.isoformat() if r.period_end else None,
                "file_url": r.file_url,
                "file_size_bytes": r.file_size_bytes,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in reports
        ],
        "limit": limit,
        "offset": offset
    }

