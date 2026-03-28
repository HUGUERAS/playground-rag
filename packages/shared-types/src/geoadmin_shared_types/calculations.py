from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

UnitLiteral = Literal["meters", "feet"]
UTMZoneLiteral = Literal["18S", "19S", "20S", "21S", "22S", "23S", "24S", "25S"]

UTM_ZONE_TO_EPSG: dict[str, str] = {
    "18S": "EPSG:31978",
    "19S": "EPSG:31979",
    "20S": "EPSG:31980",
    "21S": "EPSG:31981",
    "22S": "EPSG:31982",
    "23S": "EPSG:31983",
    "24S": "EPSG:31984",
    "25S": "EPSG:31985",
}


class CoordinatePoint(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    x: float
    y: float
    z: float | None = None


class InverseRequest(BaseModel):
    start: CoordinatePoint
    end: CoordinatePoint
    unit: UnitLiteral = "meters"
    srid: int = 4674


class InverseResponse(BaseModel):
    delta_x: float
    delta_y: float
    distancia: float
    azimute_decimal: float
    azimute_dms: str
    unit: UnitLiteral
    srid: int


class AreaRequest(BaseModel):
    points: list[CoordinatePoint]
    unit: UnitLiteral = "meters"
    srid: int = 4674


class AreaResponse(BaseModel):
    point_count: int
    area_m2: float
    perimetro_m: float
    area_ha: float
    valido: bool
    unit: UnitLiteral
    srid: int


class ConvertCoordinateRequest(BaseModel):
    lat: float
    lon: float
    zona: UTMZoneLiteral
    source_srid: int = 4674


class ConvertCoordinateResponse(BaseModel):
    este: float
    norte: float
    zona: UTMZoneLiteral
    srid: int


class ErrorResponse(BaseModel):
    erro: str
    codigo: int
