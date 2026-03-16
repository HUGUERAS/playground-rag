from __future__ import annotations

from fastapi import FastAPI

from app import bootstrap_shared_types
from app.api.router import api_router
from app.config import settings

bootstrap_shared_types()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
