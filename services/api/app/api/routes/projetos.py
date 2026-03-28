from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.clients.supabase import get_supabase_client
from app.services.projects import (
    ProjectsError,
    create_project,
    get_project,
    get_project_points,
    list_projects,
)

router = APIRouter(prefix="/projetos", tags=["projetos"])


class ProjetoCreateRequest(BaseModel):
    cliente_id: str | None = None
    nome: str = Field(..., min_length=2)
    numero_job: str | None = None
    descricao: str | None = None
    municipio: str | None = None
    estado: str | None = None
    matricula: str | None = None
    comarca: str | None = None
    zona_utm: str = "23S"
    status: str = "medicao"
    data_medicao: str | None = None
    data_protocolo: str | None = None
    data_aprovacao: str | None = None
    data_entrega: str | None = None
    prazo_estimado: str | None = None
    valor_servico: float | None = None
    valor_pago: float | None = None


def _error_response(code: int, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"erro": message, "codigo": code})


def _require_supabase():
    client = get_supabase_client()
    if client is None:
        raise ProjectsError(701, "Supabase nao configurado.", status_code=503)
    return client


@router.get("", response_model=None)
def get_projetos() -> list[dict[str, Any]] | JSONResponse:
    try:
        client = _require_supabase()
        return list_projects(client)
    except ProjectsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)


@router.post("", status_code=201, response_model=None)
def post_projetos(payload: ProjetoCreateRequest) -> dict[str, Any] | JSONResponse:
    try:
        client = _require_supabase()
        return create_project(client, payload.model_dump(exclude_none=True))
    except ProjectsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)


@router.get("/{project_id}", response_model=None)
def get_projeto_by_id(project_id: str) -> dict[str, Any] | JSONResponse:
    try:
        client = _require_supabase()
        projeto = get_project(client, project_id)
        pontos = get_project_points(client, project_id)
        return {"projeto": projeto, "pontos": pontos}
    except ProjectsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)
