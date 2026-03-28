from __future__ import annotations

from typing import Any

from supabase import Client


class ProjectsError(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _unwrap_result(result: Any) -> list[dict[str, Any]]:
    data = getattr(result, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def list_projects(client: Client) -> list[dict[str, Any]]:
    try:
        result = client.table("vw_projetos_completo").select("*").execute()
        return _unwrap_result(result)
    except Exception as exc:
        raise ProjectsError(711, "Falha ao consultar projetos no Supabase.", status_code=500) from exc


def create_project(client: Client, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        insert_result = client.table("projetos").insert(payload).execute()
    except Exception as exc:
        raise ProjectsError(712, "Falha ao criar projeto no Supabase.", status_code=500) from exc

    inserted = _unwrap_result(insert_result)
    if not inserted:
        raise ProjectsError(713, "Supabase nao retornou o projeto criado.", status_code=500)

    project_id = inserted[0].get("id")
    if not project_id:
        raise ProjectsError(714, "Projeto criado sem identificador retornado pelo Supabase.", status_code=500)

    return get_project(client, project_id)


def get_project(client: Client, project_id: str) -> dict[str, Any]:
    try:
        result = client.table("vw_projetos_completo").select("*").eq("id", project_id).execute()
    except Exception as exc:
        raise ProjectsError(715, "Falha ao consultar projeto no Supabase.", status_code=500) from exc

    projects = _unwrap_result(result)
    if not projects:
        raise ProjectsError(704, "Projeto nao encontrado.", status_code=404)

    return projects[0]


def get_project_points(client: Client, project_id: str) -> list[dict[str, Any]]:
    try:
        result = client.table("vw_pontos_utm").select("*").eq("projeto_id", project_id).execute()
        return _unwrap_result(result)
    except Exception as exc:
        raise ProjectsError(716, "Falha ao consultar pontos do projeto no Supabase.", status_code=500) from exc
