from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.clients.supabase import get_supabase_client
from app.services.points import (
    QUALITY_LABELS,
    PointsError,
    archive_point,
    create_point,
    ensure_project,
    list_points,
    quality_warning,
)

logger = logging.getLogger("geoadmin.pontos")

router = APIRouter(prefix="/pontos", tags=["pontos"])


def _error_response(code: int, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"erro": message, "codigo": code})


def _require_supabase():
    client = get_supabase_client()
    if client is None:
        raise PointsError(301, "Supabase nao configurado.", status_code=503)
    return client


class PointCreateRequest(BaseModel):
    projeto_id: str
    nome: str = Field(..., min_length=1, max_length=20)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float | None = None
    separacao_geoidal_m: float | None = None
    qualidade_fix: int = Field(default=1, ge=0, le=5)
    hdop: float | None = Field(default=None, ge=0, le=99)
    num_satelites: int | None = Field(default=None, ge=0)
    num_amostras: int = Field(default=1, ge=1)
    descricao: str | None = None
    codigo: str | None = None
    camada: str = "PONTOS"
    operador: str | None = None
    receptor_gnss: str = "CHC i73+"
    id_local: str | None = None

    @field_validator("qualidade_fix")
    @classmethod
    def validate_quality(cls, value: int) -> int:
        valid_values = {0, 1, 2, 4, 5}
        if value not in valid_values:
            raise ValueError("[ERRO-101] qualidade_fix deve ser um de [0, 1, 2, 4, 5].")
        return value

    @field_validator("nome")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("[ERRO-102] Nome do ponto nao pode ser vazio.")
        return normalized

    @field_validator("camada")
    @classmethod
    def validate_layer(cls, value: str) -> str:
        normalized = value.strip().upper()
        return normalized or "PONTOS"


class PointResponse(BaseModel):
    id: str
    projeto_id: str
    nome: str
    latitude: float
    longitude: float
    altitude_m: float | None = None
    qualidade_fix: int
    qualidade_label: str
    hdop: float | None = None
    num_amostras: int
    camada: str
    coletado_em: str
    sincronizado: bool
    aviso: str | None = None


class PointSyncRequest(BaseModel):
    pontos: list[PointCreateRequest] = Field(..., min_length=1, max_length=500)


class PointSyncResponse(BaseModel):
    total_enviados: int
    total_salvos: int
    total_erros: int
    erros: list[dict[str, Any]]


@router.post("", response_model=PointResponse, status_code=201)
def post_ponto(payload: PointCreateRequest) -> PointResponse | JSONResponse:
    try:
        client = _require_supabase()
        ensure_project(client, payload.projeto_id)
        inserted = create_point(client, payload.model_dump(exclude_none=True))
        warning = quality_warning(payload.qualidade_fix, payload.hdop)
        if warning:
            logger.warning("Ponto %s salvo com aviso: %s", payload.nome, warning)

        return PointResponse(
            id=inserted["id"],
            projeto_id=inserted["projeto_id"],
            nome=inserted["nome"],
            latitude=payload.latitude,
            longitude=payload.longitude,
            altitude_m=inserted.get("altitude_m"),
            qualidade_fix=inserted["qualidade_fix"],
            qualidade_label=QUALITY_LABELS.get(inserted["qualidade_fix"], "Desconhecido"),
            hdop=inserted.get("hdop"),
            num_amostras=inserted.get("num_amostras", 1),
            camada=inserted.get("camada", "PONTOS"),
            coletado_em=inserted.get("coletado_em", ""),
            sincronizado=bool(inserted.get("sincronizado", True)),
            aviso=warning,
        )
    except PointsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)


@router.post("/sync", response_model=PointSyncResponse)
def post_pontos_sync(payload: PointSyncRequest) -> PointSyncResponse | JSONResponse:
    try:
        client = _require_supabase()
    except PointsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)

    verified_projects: set[str] = set()
    saved = 0
    errors: list[dict[str, Any]] = []

    for index, point in enumerate(payload.pontos):
        try:
            if point.projeto_id not in verified_projects:
                ensure_project(client, point.projeto_id)
                verified_projects.add(point.projeto_id)
            create_point(client, point.model_dump(exclude_none=True))
            saved += 1
        except PointsError as exc:
            errors.append(
                {
                    "indice": index,
                    "nome": point.nome,
                    "id_local": point.id_local,
                    "erro": exc.message,
                    "codigo": exc.code,
                }
            )

    return PointSyncResponse(
        total_enviados=len(payload.pontos),
        total_salvos=saved,
        total_erros=len(errors),
        erros=errors,
    )


@router.get("/{project_id}", response_model=None)
def get_pontos(project_id: str, camada: str | None = Query(default=None)) -> dict[str, Any] | JSONResponse:
    try:
        client = _require_supabase()
        ensure_project(client, project_id)
        points = list_points(client, project_id, camada)
        return {"projeto_id": project_id, "total": len(points), "pontos": points}
    except PointsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)


@router.delete("/{point_id}", response_model=None)
def delete_ponto(point_id: str) -> dict[str, Any] | JSONResponse:
    try:
        client = _require_supabase()
        archived = archive_point(client, point_id)
        return {"mensagem": f"Ponto {point_id} arquivado.", "deleted_at": archived["deleted_at"]}
    except PointsError as exc:
        return _error_response(exc.code, exc.message, exc.status_code)
