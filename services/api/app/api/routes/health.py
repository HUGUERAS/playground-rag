from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.services.health import build_health_response
from geoadmin_shared_types.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return build_health_response(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )
