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

from app.services.subdivision import (
    subdividir_por_area,
    subdividir_por_percentual,
    subdividir_por_ponto_fixo,
    subdividir_por_vertice,
)
from geoadmin_shared_types.calculations import CoordinatePoint
from geoadmin_shared_types.subdivision import (
    SubdivisionByAreaRequest,
    SubdivisionByFixedPointRequest,
    SubdivisionByPercentualRequest,
    SubdivisionByVertexRequest,
)
from gabarito_subdivisao import RECTANGLE_POINTS, RECTANGLE_TOTAL_AREA, SUBDIVISION_CASES


def _rectangle_points() -> list[CoordinatePoint]:
    return [CoordinatePoint(**point) for point in RECTANGLE_POINTS]


def test_subdividir_por_area_retangulo() -> None:
    result = subdividir_por_area(
        SubdivisionByAreaRequest(points=_rectangle_points(), area_alvo_m2=SUBDIVISION_CASES["area"]["area_alvo_m2"])
    )

    assert result.area_total_m2 == RECTANGLE_TOTAL_AREA
    assert result.area_parte_a_m2 == pytest.approx(SUBDIVISION_CASES["area"]["expected_a"], abs=1e-3)
    assert result.area_parte_b_m2 == pytest.approx(SUBDIVISION_CASES["area"]["expected_b"], abs=1e-3)


def test_subdividir_por_percentual_retangulo() -> None:
    result = subdividir_por_percentual(
        SubdivisionByPercentualRequest(points=_rectangle_points(), percentual=SUBDIVISION_CASES["percentual"]["percentual"])
    )

    assert result.area_parte_a_m2 == pytest.approx(SUBDIVISION_CASES["percentual"]["expected_a"], abs=1e-3)
    assert result.area_parte_b_m2 == pytest.approx(SUBDIVISION_CASES["percentual"]["expected_b"], abs=1e-3)


def test_subdividir_por_vertice_retangulo() -> None:
    result = subdividir_por_vertice(
        SubdivisionByVertexRequest(
            points=_rectangle_points(),
            indice_vertice=SUBDIVISION_CASES["vertice"]["indice_vertice"],
            area_alvo_m2=SUBDIVISION_CASES["vertice"]["area_alvo_m2"],
        )
    )

    assert result.area_parte_a_m2 == pytest.approx(SUBDIVISION_CASES["vertice"]["expected_a"], abs=1e-3)
    assert result.area_parte_b_m2 == pytest.approx(SUBDIVISION_CASES["vertice"]["expected_b"], abs=1e-3)


def test_subdividir_por_ponto_fixo_retangulo() -> None:
    result = subdividir_por_ponto_fixo(
        SubdivisionByFixedPointRequest(
            points=_rectangle_points(),
            ponto_fixo=CoordinatePoint(**SUBDIVISION_CASES["ponto_fixo"]["ponto_fixo"]),
            area_alvo_m2=SUBDIVISION_CASES["ponto_fixo"]["area_alvo_m2"],
        )
    )

    assert result.area_parte_a_m2 == pytest.approx(SUBDIVISION_CASES["ponto_fixo"]["expected_a"], abs=1e-3)
    assert result.area_parte_b_m2 == pytest.approx(SUBDIVISION_CASES["ponto_fixo"]["expected_b"], abs=1e-3)
