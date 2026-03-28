from __future__ import annotations

from pydantic import BaseModel, Field

from geoadmin_shared_types.calculations import CoordinatePoint, UnitLiteral


class LineSegment(BaseModel):
    inicio: CoordinatePoint
    fim: CoordinatePoint


class SubdivisionResult(BaseModel):
    metodo: str
    area_total_m2: float
    area_parte_a_m2: float
    area_parte_b_m2: float
    percentual_parte_a: float
    percentual_parte_b: float
    linha_corte: LineSegment
    poligono_parte_a: list[CoordinatePoint]
    poligono_parte_b: list[CoordinatePoint]
    iteracoes: int
    erro_m2: float
    valido: bool
    unit: UnitLiteral = "meters"
    srid: int = 31983


class SubdivisionByAreaRequest(BaseModel):
    points: list[CoordinatePoint] = Field(min_length=3)
    area_alvo_m2: float = Field(gt=0)
    unit: UnitLiteral = "meters"
    srid: int = 31983


class SubdivisionByPercentualRequest(BaseModel):
    points: list[CoordinatePoint] = Field(min_length=3)
    percentual: float = Field(gt=0, lt=100)
    unit: UnitLiteral = "meters"
    srid: int = 31983


class SubdivisionByVertexRequest(BaseModel):
    points: list[CoordinatePoint] = Field(min_length=3)
    indice_vertice: int = Field(ge=0)
    area_alvo_m2: float = Field(gt=0)
    unit: UnitLiteral = "meters"
    srid: int = 31983


class SubdivisionByFixedPointRequest(BaseModel):
    points: list[CoordinatePoint] = Field(min_length=3)
    ponto_fixo: CoordinatePoint
    area_alvo_m2: float = Field(gt=0)
    unit: UnitLiteral = "meters"
    srid: int = 31983
