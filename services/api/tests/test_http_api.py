from __future__ import annotations

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
TESTS_ROOT = API_ROOT / "tests"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from app.main import app
from gabarito_geodesico import AREA_CASE, CONVERT_CASE, INVERSE_CASE


@pytest.mark.anyio
async def test_health_endpoint_reports_supabase_status() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "GeoAdmin API"
    assert "supabase" in payload
    assert payload["supabase"]["configured"] in (True, False)


@pytest.mark.anyio
async def test_http_inverse_matches_gabarito() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/inverso",
            json={
                "start": INVERSE_CASE["start"],
                "end": INVERSE_CASE["end"],
                "unit": "meters",
                "srid": 4674,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["distancia"] == INVERSE_CASE["expected"]["distancia"]
    assert payload["azimute_decimal"] == INVERSE_CASE["expected"]["azimute_decimal"]
    assert payload["azimute_dms"] == INVERSE_CASE["expected"]["azimute_dms"]


@pytest.mark.anyio
async def test_http_area_matches_gabarito() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/area",
            json={
                "points": AREA_CASE["points"],
                "unit": "meters",
                "srid": 31983,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area_m2"] == AREA_CASE["expected"]["area_m2"]
    assert payload["perimetro_m"] == AREA_CASE["expected"]["perimetro_m"]
    assert payload["area_ha"] == AREA_CASE["expected"]["area_ha"]
    assert payload["valido"] is True


@pytest.mark.anyio
async def test_http_area_invalid_polygon_returns_structured_error() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/area",
            json={
                "points": [
                    {"x": 0, "y": 0},
                    {"x": 10, "y": 10},
                    {"x": 10, "y": 0},
                    {"x": 0, "y": 10},
                ],
                "unit": "meters",
                "srid": 31983,
            },
        )

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"]["codigo"] == 201
    assert "Poligono invalido" in payload["detail"]["erro"]


@pytest.mark.anyio
async def test_http_convert_uses_always_xy_case() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/converter",
            json={
                "lat": CONVERT_CASE["lat"],
                "lon": CONVERT_CASE["lon"],
                "zona": CONVERT_CASE["zona"],
                "source_srid": 4674,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["este"] == CONVERT_CASE["expected"]["este"]
    assert payload["norte"] == CONVERT_CASE["expected"]["norte"]
    assert payload["srid"] == CONVERT_CASE["expected"]["srid"]
