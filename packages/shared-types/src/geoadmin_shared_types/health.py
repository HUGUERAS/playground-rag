from __future__ import annotations

from pydantic import BaseModel


class DependencyStatus(BaseModel):
    configured: bool
    reachable: bool
    message: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    supabase: DependencyStatus
