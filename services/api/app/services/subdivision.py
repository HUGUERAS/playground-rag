from __future__ import annotations

import re

from app.services.geodesy import GeodesyError
from app.services.subdivisao_area import (
    ResultadoSubdivisao,
    subdividir_por_area as core_subdividir_por_area,
    subdividir_por_percentual as core_subdividir_por_percentual,
    subdividir_por_ponto_fixo as core_subdividir_por_ponto_fixo,
    subdividir_por_vertice as core_subdividir_por_vertice,
)
from geoadmin_shared_types.calculations import CoordinatePoint
from geoadmin_shared_types.subdivision import (
    LineSegment,
    SubdivisionByAreaRequest,
    SubdivisionByFixedPointRequest,
    SubdivisionByPercentualRequest,
    SubdivisionByVertexRequest,
    SubdivisionResult,
)

ERROR_PATTERN = re.compile(r"\[ERRO-(\d+)\]\s*(.*)")


def subdividir_por_area(payload: SubdivisionByAreaRequest) -> SubdivisionResult:
    try:
        result = core_subdividir_por_area(
            pontos=_points_to_tuples(payload.points),
            area_desejada_m2=payload.area_alvo_m2,
        )
        return _to_shared_result(result, payload.srid, payload.unit)
    except ValueError as exc:
        raise _convert_error(exc) from exc


def subdividir_por_percentual(payload: SubdivisionByPercentualRequest) -> SubdivisionResult:
    try:
        result = core_subdividir_por_percentual(
            pontos=_points_to_tuples(payload.points),
            percentual_a=payload.percentual,
        )
        return _to_shared_result(result, payload.srid, payload.unit)
    except ValueError as exc:
        raise _convert_error(exc) from exc


def subdividir_por_vertice(payload: SubdivisionByVertexRequest) -> SubdivisionResult:
    try:
        result = core_subdividir_por_vertice(
            pontos=_points_to_tuples(payload.points),
            indice_vertice=payload.indice_vertice,
            area_desejada_m2=payload.area_alvo_m2,
        )
        return _to_shared_result(result, payload.srid, payload.unit)
    except ValueError as exc:
        raise _convert_error(exc) from exc


def subdividir_por_ponto_fixo(payload: SubdivisionByFixedPointRequest) -> SubdivisionResult:
    try:
        result = core_subdividir_por_ponto_fixo(
            pontos=_points_to_tuples(payload.points),
            ponto_fixo=(payload.ponto_fixo.x, payload.ponto_fixo.y),
            area_desejada_m2=payload.area_alvo_m2,
        )
        return _to_shared_result(result, payload.srid, payload.unit)
    except ValueError as exc:
        raise _convert_error(exc) from exc


def _convert_error(exc: ValueError) -> GeodesyError:
    message = str(exc)
    match = ERROR_PATTERN.search(message)
    if not match:
        return GeodesyError(422, message)
    code = int(match.group(1))
    clean_message = match.group(2).strip() or message
    return GeodesyError(code, clean_message)


def _points_to_tuples(points: list[CoordinatePoint]) -> list[tuple[float, float]]:
    return [(point.x, point.y) for point in points]


def _tuple_points_to_models(points: list[tuple[float, float]]) -> list[CoordinatePoint]:
    return [CoordinatePoint(x=round(x, 6), y=round(y, 6)) for x, y in points]


def _to_shared_result(result: ResultadoSubdivisao, srid: int, unit: str) -> SubdivisionResult:
    line_points = result.linha_divisoria[:2]
    if len(line_points) < 2:
        raise GeodesyError(422, "Linha divisoria incompleta no resultado da subdivisao.")

    return SubdivisionResult(
        metodo=result.metodo,
        area_total_m2=round(result.area_total_m2, 6),
        area_parte_a_m2=round(result.area_a_m2, 6),
        area_parte_b_m2=round(result.area_b_m2, 6),
        percentual_parte_a=round((result.area_a_m2 / result.area_total_m2) * 100, 6),
        percentual_parte_b=round((result.area_b_m2 / result.area_total_m2) * 100, 6),
        linha_corte=LineSegment(
            inicio=CoordinatePoint(x=round(line_points[0][0], 6), y=round(line_points[0][1], 6)),
            fim=CoordinatePoint(x=round(line_points[1][0], 6), y=round(line_points[1][1], 6)),
        ),
        poligono_parte_a=_tuple_points_to_models(result.poligono_a),
        poligono_parte_b=_tuple_points_to_models(result.poligono_b),
        iteracoes=0,
        erro_m2=round(result.erro_m2, 6),
        valido=True,
        unit=unit,
        srid=srid,
    )
