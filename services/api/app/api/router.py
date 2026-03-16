from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.calculations import router as calculations_router
from app.api.routes.health import router as health_router
from app.api.routes.projetos import router as projetos_router
from app.api.routes.subdivision import router as subdivision_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(calculations_router)
api_router.include_router(projetos_router)
api_router.include_router(subdivision_router)
