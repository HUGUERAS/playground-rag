from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.geodesy import GeodesyError
from app.services.subdivision import (
    subdividir_por_area,
    subdividir_por_percentual,
    subdividir_por_ponto_fixo,
    subdividir_por_vertice,
)
from geoadmin_shared_types.calculations import ErrorResponse
from geoadmin_shared_types.subdivision import (
    SubdivisionByAreaRequest,
    SubdivisionByFixedPointRequest,
    SubdivisionByPercentualRequest,
    SubdivisionByVertexRequest,
    SubdivisionResult,
)

router = APIRouter(prefix="/geo/subdivisao", tags=["geo-subdivisao"])


def _unprocessable(exc: GeodesyError) -> HTTPException:
    return HTTPException(status_code=422, detail=ErrorResponse(erro=exc.message, codigo=exc.code).model_dump())


@router.post("/area", response_model=SubdivisionResult)
def post_subdivision_area(payload: SubdivisionByAreaRequest) -> SubdivisionResult:
    try:
        return subdividir_por_area(payload)
    except GeodesyError as exc:
        raise _unprocessable(exc) from exc


@router.post("/percentual", response_model=SubdivisionResult)
def post_subdivision_percentual(payload: SubdivisionByPercentualRequest) -> SubdivisionResult:
    try:
        return subdividir_por_percentual(payload)
    except GeodesyError as exc:
        raise _unprocessable(exc) from exc


@router.post("/vertice", response_model=SubdivisionResult)
def post_subdivision_vertex(payload: SubdivisionByVertexRequest) -> SubdivisionResult:
    try:
        return subdividir_por_vertice(payload)
    except GeodesyError as exc:
        raise _unprocessable(exc) from exc


@router.post("/ponto-fixo", response_model=SubdivisionResult)
def post_subdivision_fixed_point(payload: SubdivisionByFixedPointRequest) -> SubdivisionResult:
    try:
        return subdividir_por_ponto_fixo(payload)
    except GeodesyError as exc:
        raise _unprocessable(exc) from exc
