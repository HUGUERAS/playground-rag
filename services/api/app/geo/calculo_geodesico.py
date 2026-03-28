from __future__ import annotations

from dataclasses import dataclass

from app.services.geodesy import GeodesyError, calculate_inverse
from geoadmin_shared_types.calculations import CoordinatePoint, InverseRequest


class GeoAdminError(Exception):
    def __init__(self, codigo: int, erro: str) -> None:
        super().__init__(erro)
        self.codigo = codigo
        self.erro = erro


@dataclass(frozen=True)
class ResultadoInverso:
    distancia: float
    azimute_decimal: float
    azimute_graus_ms: str


def calcular_inverso(x1: float, y1: float, x2: float, y2: float) -> ResultadoInverso:
    try:
        resultado = calculate_inverse(
            InverseRequest(
                start=CoordinatePoint(x=x1, y=y1),
                end=CoordinatePoint(x=x2, y=y2),
            )
        )
    except GeodesyError as exc:
        raise GeoAdminError(exc.code, exc.message) from exc

    return ResultadoInverso(
        distancia=resultado.distancia,
        azimute_decimal=resultado.azimute_decimal,
        azimute_graus_ms=resultado.azimute_dms,
    )
