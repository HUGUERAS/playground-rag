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

from app.services.nmea_parser import (
    AcumuladorPontos,
    QualidadeFix,
    parsear_gga,
    parsear_gsa,
    parsear_pchc,
    parsear_rmc,
    processar_sentenca,
    validar_checksum,
)
from gabarito_nmea import (
    GGA_FIX_SENTENCE,
    GGA_NO_FIX_SENTENCE,
    GSA_SENTENCE,
    PCHC_LEGACY_SENTENCE,
    PCHC_SENTENCE,
    RMC_SENTENCE,
)


def test_parsear_gga_rtk_fix_brasilia() -> None:
    pos = parsear_gga(GGA_FIX_SENTENCE)

    assert pos.latitude == pytest.approx(-15.77916667, abs=1e-8)
    assert pos.longitude == pytest.approx(-47.92972167, abs=1e-8)
    assert pos.altitude_m == pytest.approx(-950.5, abs=1e-4)
    assert pos.qualidade == QualidadeFix.RTK_FIX
    assert pos.num_satelites == 24
    assert pos.hdop == pytest.approx(0.6, abs=1e-2)
    assert pos.rtk_fix is True
    assert pos.utilizavel is True


def test_validar_checksum_true_and_false() -> None:
    assert validar_checksum(GGA_FIX_SENTENCE) is True
    assert validar_checksum(GGA_FIX_SENTENCE[:-2] + "FF") is False


def test_parsear_pchc() -> None:
    dados = parsear_pchc(PCHC_SENTENCE)

    assert dados["tilt_x"] == pytest.approx(3.2, abs=1e-2)
    assert dados["tilt_y"] == pytest.approx(-1.5, abs=1e-2)
    assert dados["tilt_z"] == pytest.approx(0.0, abs=1e-2)
    assert dados["heading_graus"] == pytest.approx(127.4, abs=1e-2)
    assert dados["compensacao_ativa"] is True


def test_parsear_pchc_legacy_sem_tilt_z() -> None:
    dados = parsear_pchc(PCHC_LEGACY_SENTENCE)

    assert dados["tilt_x"] == pytest.approx(3.2, abs=1e-2)
    assert dados["tilt_y"] == pytest.approx(-1.5, abs=1e-2)
    assert dados["tilt_z"] == pytest.approx(0.0, abs=1e-2)
    assert dados["heading_graus"] == pytest.approx(127.4, abs=1e-2)
    assert dados["compensacao_ativa"] is True


def test_parsear_gga_sem_fix_lanca_erro() -> None:
    with pytest.raises(ValueError) as exc_info:
        parsear_gga(GGA_NO_FIX_SENTENCE)

    assert "[ERRO-601]" in str(exc_info.value)


def test_parsear_rmc() -> None:
    dados = parsear_rmc(RMC_SENTENCE)

    assert dados["hora_utc"] == "12:00:00.00"
    assert dados["data_utc"] == "2026-03-16"
    assert dados["velocidade_kmh"] == pytest.approx(0.96, abs=1e-2)


def test_parsear_gsa() -> None:
    dados = parsear_gsa(GSA_SENTENCE)

    assert dados.pdop == pytest.approx(1.2, abs=1e-2)
    assert dados.hdop == pytest.approx(0.6, abs=1e-2)
    assert dados.vdop == pytest.approx(1.0, abs=1e-2)
    assert len(dados.ids_usados) == 11


def test_processar_sentenca_dispatcher() -> None:
    resultado = processar_sentenca(GGA_FIX_SENTENCE)
    assert resultado["tipo"] == "GGA"
    assert resultado["erro"] is None
    assert resultado["dados"]["rtk_fix"] is True


def test_acumulador_pontos_media() -> None:
    acumulador = AcumuladorPontos(n_amostras=5, exigir_rtk_fix=True)

    for index in range(5):
        acumulador.adicionar(
            {
                "latitude": -15.779167 + (index * 0.0000001),
                "longitude": -47.929722 + (index * 0.0000001),
                "altitude_m": -950.5,
                "hdop": 0.6,
                "rtk_fix": True,
                "qualidade": 4,
                "qualidade_label": "RTK Fix (cm) ✓",
            }
        )

    media = acumulador.media()
    assert acumulador.completo is True
    assert media["n_amostras"] == 5
    assert media["qualidade"] == 4
    assert media["desvio_padrao_m"] >= 0
