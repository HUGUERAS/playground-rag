from __future__ import annotations

from postgrest.exceptions import APIError

from app.clients.supabase import get_supabase_client
from geoadmin_shared_types.health import DependencyStatus, HealthResponse


def build_health_response(service: str, version: str, environment: str) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=service,
        version=version,
        environment=environment,
        supabase=inspect_supabase_dependency(),
    )


def inspect_supabase_dependency() -> DependencyStatus:
    client = get_supabase_client()
    if client is None:
        return DependencyStatus(
            configured=False,
            reachable=False,
            message="Supabase nao configurado. Defina GEOADMIN_SUPABASE_URL e GEOADMIN_SUPABASE_KEY.",
        )

    try:
        client.table("projetos").select("id", count="exact").limit(1).execute()
        return DependencyStatus(
            configured=True,
            reachable=True,
            message="Supabase configurado e consulta basica executada.",
        )
    except APIError as exc:
        return DependencyStatus(
            configured=True,
            reachable=False,
            message=f"Supabase respondeu com erro: {exc.message}",
        )
    except Exception as exc:
        return DependencyStatus(
            configured=True,
            reachable=False,
            message=f"Falha ao conectar no Supabase: {exc}",
        )
