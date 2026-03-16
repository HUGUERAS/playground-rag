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
from gabarito_subdivisao import RECTANGLE_POINTS, SUBDIVISION_CASES


@pytest.mark.anyio
async def test_http_subdivision_area() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/subdivisao/area",
            json={"points": RECTANGLE_POINTS, "area_alvo_m2": SUBDIVISION_CASES["area"]["area_alvo_m2"]},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area_parte_a_m2"] == pytest.approx(SUBDIVISION_CASES["area"]["expected_a"], abs=1e-3)
    assert payload["area_parte_b_m2"] == pytest.approx(SUBDIVISION_CASES["area"]["expected_b"], abs=1e-3)


@pytest.mark.anyio
async def test_http_subdivision_percentual() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/subdivisao/percentual",
            json={"points": RECTANGLE_POINTS, "percentual": SUBDIVISION_CASES["percentual"]["percentual"]},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area_parte_a_m2"] == pytest.approx(SUBDIVISION_CASES["percentual"]["expected_a"], abs=1e-3)
    assert payload["area_parte_b_m2"] == pytest.approx(SUBDIVISION_CASES["percentual"]["expected_b"], abs=1e-3)


@pytest.mark.anyio
async def test_http_subdivision_vertice() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/subdivisao/vertice",
            json={
                "points": RECTANGLE_POINTS,
                "indice_vertice": SUBDIVISION_CASES["vertice"]["indice_vertice"],
                "area_alvo_m2": SUBDIVISION_CASES["vertice"]["area_alvo_m2"],
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area_parte_a_m2"] == pytest.approx(SUBDIVISION_CASES["vertice"]["expected_a"], abs=1e-3)


@pytest.mark.anyio
async def test_http_subdivision_ponto_fixo() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/subdivisao/ponto-fixo",
            json={
                "points": RECTANGLE_POINTS,
                "ponto_fixo": SUBDIVISION_CASES["ponto_fixo"]["ponto_fixo"],
                "area_alvo_m2": SUBDIVISION_CASES["ponto_fixo"]["area_alvo_m2"],
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["area_parte_a_m2"] == pytest.approx(SUBDIVISION_CASES["ponto_fixo"]["expected_a"], abs=1e-3)


@pytest.mark.anyio
async def test_http_subdivision_error_returns_422() -> None:
    invalid_points = [
        {"x": 0, "y": 0},
        {"x": 10, "y": 10},
        {"x": 10, "y": 0},
        {"x": 0, "y": 10},
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/geo/subdivisao/area",
            json={"points": invalid_points, "area_alvo_m2": 10.0},
        )

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"]["codigo"] == 201
    assert "Poligono invalido" in payload["detail"]["erro"]
