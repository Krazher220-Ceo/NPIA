"""
Главный роутер API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    factories, equipment, metrics, analytics, users, auth, dashboard,
    subscriptions, production, reports, integrations, applications, admin,
    individual_entrepreneurs
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(factories.router, prefix="/factories", tags=["factories"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(production.router, prefix="/production", tags=["production"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(individual_entrepreneurs.router, prefix="/individual-entrepreneurs", tags=["individual-entrepreneurs"])

