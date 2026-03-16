from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
TESTS_ROOT = API_ROOT / "tests"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from app.services.geodesy import GeodesyError, calculate_inverse, calculate_polygon_area, convert_geographic_to_utm
from geoadmin_shared_types.calculations import AreaRequest, ConvertCoordinateRequest, CoordinatePoint, InverseRequest
from gabarito_geodesico import AREA_CASE, CONVERT_CASE, INVERSE_CASE


def test_inverse_matches_gabarito() -> None:
    payload = InverseRequest(
        start=CoordinatePoint(**INVERSE_CASE["start"]),
        end=CoordinatePoint(**INVERSE_CASE["end"]),
    )

    result = calculate_inverse(payload)

    assert result.distancia == pytest.approx(INVERSE_CASE["expected"]["distancia"], abs=1e-6)
    assert result.azimute_decimal == pytest.approx(INVERSE_CASE["expected"]["azimute_decimal"], abs=1e-6)
    assert result.azimute_dms == INVERSE_CASE["expected"]["azimute_dms"]


def test_area_matches_gabarito() -> None:
    payload = AreaRequest(points=[CoordinatePoint(**point) for point in AREA_CASE["points"]], srid=31983)

    result = calculate_polygon_area(payload)

    assert result.area_m2 == pytest.approx(AREA_CASE["expected"]["area_m2"], abs=1e-6)
    assert result.perimetro_m == pytest.approx(AREA_CASE["expected"]["perimetro_m"], abs=1e-6)
    assert result.area_ha == pytest.approx(AREA_CASE["expected"]["area_ha"], abs=1e-6)
    assert result.valido is True


def test_invalid_polygon_raises_structured_error() -> None:
    payload = AreaRequest(
        points=[
            CoordinatePoint(x=0, y=0),
            CoordinatePoint(x=10, y=10),
            CoordinatePoint(x=10, y=0),
            CoordinatePoint(x=0, y=10),
        ],
        srid=31983,
    )

    with pytest.raises(GeodesyError) as exc_info:
        calculate_polygon_area(payload)

    assert exc_info.value.code == 201
    assert "Poligono invalido" in exc_info.value.message


def test_coordinate_conversion_uses_zone_mapping() -> None:
    payload = ConvertCoordinateRequest(
        lat=CONVERT_CASE["lat"],
        lon=CONVERT_CASE["lon"],
        zona=CONVERT_CASE["zona"],
    )

    result = convert_geographic_to_utm(payload)

    assert result.este == pytest.approx(CONVERT_CASE["expected"]["este"], abs=1e-6)
    assert result.norte == pytest.approx(CONVERT_CASE["expected"]["norte"], abs=1e-6)
    assert result.srid == CONVERT_CASE["expected"]["srid"]
