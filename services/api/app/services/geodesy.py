from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.validation import explain_validity

from geoadmin_shared_types.calculations import (
    AreaRequest,
    AreaResponse,
    ConvertCoordinateRequest,
    ConvertCoordinateResponse,
    InverseRequest,
    InverseResponse,
    UTM_ZONE_TO_EPSG,
)


class GeodesyError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def format_dms(decimal_degrees: float) -> str:
    degrees = int(decimal_degrees)
    minutes_float = (decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return f'{degrees}°{minutes:02d}\'{seconds:.2f}"'


def calculate_inverse(payload: InverseRequest) -> InverseResponse:
    delta_x = payload.end.x - payload.start.x
    delta_y = payload.end.y - payload.start.y
    distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))

    if distance == 0:
        raise GeodesyError(101, "Pontos identicos, azimute indefinido.")

    azimuth_radians = math.atan2(delta_x, delta_y)
    azimuth_degrees = math.degrees(azimuth_radians)
    if azimuth_degrees < 0:
        azimuth_degrees += 360

    return InverseResponse(
        delta_x=round(delta_x, 6),
        delta_y=round(delta_y, 6),
        distancia=round(distance, 6),
        azimute_decimal=round(azimuth_degrees, 6),
        azimute_dms=format_dms(azimuth_degrees),
        unit=payload.unit,
        srid=payload.srid,
    )


def calculate_polygon_area(payload: AreaRequest) -> AreaResponse:
    if len(payload.points) < 3:
        raise GeodesyError(201, "Poligono requer pelo menos 3 pontos.")

    coordinates = [(point.x, point.y) for point in payload.points]
    polygon = Polygon(coordinates)

    if not polygon.is_valid:
        raise GeodesyError(201, f"Poligono invalido: {explain_validity(polygon)}")

    if polygon.exterior.is_ccw is False:
        polygon = polygon.reverse()

    area_m2 = round(polygon.area, 6)
    perimeter_m = round(polygon.length, 6)

    return AreaResponse(
        point_count=len(payload.points),
        area_m2=area_m2,
        perimetro_m=perimeter_m,
        area_ha=round(area_m2 / 10000, 6),
        valido=True,
        unit=payload.unit,
        srid=payload.srid,
    )


def convert_geographic_to_utm(payload: ConvertCoordinateRequest) -> ConvertCoordinateResponse:
    target_epsg = UTM_ZONE_TO_EPSG.get(payload.zona.upper())
    if not target_epsg:
        supported = ", ".join(sorted(UTM_ZONE_TO_EPSG))
        raise GeodesyError(301, f"Zona UTM invalida. Use uma destas: {supported}")

    transformer = Transformer.from_crs(
        f"EPSG:{payload.source_srid}",
        target_epsg,
        always_xy=True,
    )
    easting, northing = transformer.transform(payload.lon, payload.lat)

    return ConvertCoordinateResponse(
        este=round(easting, 6),
        norte=round(northing, 6),
        zona=payload.zona.upper(),
        srid=int(target_epsg.split(":")[1]),
    )


def export_project_dxf(project: dict[str, Any], output_path: str | Path) -> Path:
    try:
        import ezdxf
    except ImportError as exc:
        raise GeodesyError(401, "ezdxf nao instalado. Instale a dependencia para exportar DXF.") from exc

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    document = ezdxf.new(dxfversion="R2010")
    modelspace = document.modelspace()

    for layer_name, color in (("PONTOS", 2), ("PERIMETRO", 1), ("TEXTOS", 7)):
        if layer_name not in document.layers:
            document.layers.add(layer_name, color=color)

    points = project.get("pontos", [])
    for point in points:
        x = point["este"]
        y = point["norte"]
        z = point.get("cota", 0.0)

        modelspace.add_point((x, y, z), dxfattribs={"layer": "PONTOS"})
        modelspace.add_text(
            point["nome"],
            dxfattribs={"layer": "TEXTOS", "height": 0.5, "insert": (x + 0.3, y + 0.3, z)},
        )

    if len(points) >= 3:
        coordinates = [(point["este"], point["norte"]) for point in points]
        coordinates.append(coordinates[0])
        modelspace.add_lwpolyline(coordinates, dxfattribs={"layer": "PERIMETRO", "closed": True})

    document.saveas(destination)
    return destination
