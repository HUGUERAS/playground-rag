from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import IntEnum


class QualidadeFix(IntEnum):
    SEM_FIX = 0
    AUTONOMO = 1
    DGPS = 2
    RTK_FIX = 4
    RTK_FLOAT = 5


QUALIDADE_LABELS = {
    QualidadeFix.SEM_FIX: "Sem fix",
    QualidadeFix.AUTONOMO: "GPS autonomo (~3m)",
    QualidadeFix.DGPS: "DGPS/SBAS (~1m)",
    QualidadeFix.RTK_FIX: "RTK Fix (cm) ✓",
    QualidadeFix.RTK_FLOAT: "RTK Float (~0.3m)",
}

PRECISAO_ESPERADA = {
    QualidadeFix.RTK_FIX: 0.02,
    QualidadeFix.RTK_FLOAT: 0.30,
    QualidadeFix.DGPS: 1.00,
    QualidadeFix.AUTONOMO: 3.00,
}


@dataclass
class PosicaoGNSS:
    latitude: float
    longitude: float
    altitude_m: float
    separacao_geoidal_m: float
    qualidade: int
    qualidade_label: str
    num_satelites: int
    hdop: float
    hora_utc: str
    sentenca_raw: str
    inclinacao_x: float = 0.0
    inclinacao_y: float = 0.0
    inclinacao_z: float = 0.0
    compensacao_ativa: bool = False

    @property
    def rtk_fix(self) -> bool:
        return self.qualidade == QualidadeFix.RTK_FIX

    @property
    def utilizavel(self) -> bool:
        return self.qualidade in (QualidadeFix.RTK_FIX, QualidadeFix.RTK_FLOAT)

    @property
    def precisao_estimada_m(self) -> float:
        try:
            return PRECISAO_ESPERADA[QualidadeFix(self.qualidade)]
        except Exception:
            return 999.0


@dataclass
class SatelitesGNSS:
    pdop: float = 0.0
    hdop: float = 0.0
    vdop: float = 0.0
    ids_usados: list[str] = field(default_factory=list)


def validar_checksum(sentenca: str) -> bool:
    sentenca = sentenca.strip()
    if not sentenca.startswith("$") or "*" not in sentenca:
        return False

    try:
        corpo, checksum_str = sentenca[1:].rsplit("*", 1)
        checksum_calculado = 0
        for caractere in corpo:
            checksum_calculado ^= ord(caractere)
        return checksum_calculado == int(checksum_str[:2], 16)
    except (ValueError, IndexError):
        return False


def _nmea_para_decimal(valor: str, hemisferio: str) -> float:
    if not valor or not hemisferio:
        raise ValueError("[ERRO-501] Coordenada NMEA vazia.")

    try:
        valor_float = float(valor)
    except ValueError as exc:
        raise ValueError(f"[ERRO-502] Coordenada invalida: '{valor}'") from exc

    graus = int(valor_float / 100)
    minutos = valor_float - (graus * 100)
    decimal = graus + (minutos / 60.0)

    if hemisferio in ("S", "W"):
        decimal = -decimal

    return round(decimal, 8)


def _nmea_hora(hora_str: str) -> str:
    if len(hora_str) < 6:
        return hora_str
    return f"{hora_str[:2]}:{hora_str[2:4]}:{hora_str[4:]}"


def parsear_gga(sentenca: str) -> PosicaoGNSS:
    if not validar_checksum(sentenca):
        raise ValueError(f"[ERRO-503] Checksum invalido: {sentenca[:30]}")

    corpo = sentenca.split("*")[0]
    campos = corpo.split(",")
    if len(campos) < 14:
        raise ValueError(
            f"[ERRO-504] Sentenca GGA incompleta: {len(campos)} campos "
            f"(esperado >= 14). Sentenca: {sentenca[:50]}"
        )

    identificador = campos[0].lstrip("$")
    if not any(identificador.startswith(prefixo) for prefixo in ("GNGGA", "GPGGA", "GLGGA", "GAGGA", "GBGGA")):
        raise ValueError(f"[ERRO-505] Sentenca nao e GGA: {identificador}")

    if not campos[2] or not campos[4]:
        raise ValueError("[ERRO-506] Sentenca GGA sem dados de posicao.")

    try:
        qualidade = int(campos[6]) if campos[6] else 0
    except ValueError:
        qualidade = 0

    if qualidade == QualidadeFix.SEM_FIX:
        raise ValueError(
            "[ERRO-601] Receptor sem fix. Verifique visibilidade do ceu e conexao NTRIP."
        )

    latitude = _nmea_para_decimal(campos[2], campos[3])
    longitude = _nmea_para_decimal(campos[4], campos[5])

    try:
        num_satelites = int(campos[7]) if campos[7] else 0
    except ValueError:
        num_satelites = 0

    try:
        hdop = float(campos[8]) if campos[8] else 99.9
    except ValueError:
        hdop = 99.9

    try:
        altitude = float(campos[9]) if campos[9] else 0.0
    except ValueError:
        altitude = 0.0

    try:
        separacao = float(campos[11]) if campos[11] else 0.0
    except ValueError:
        separacao = 0.0

    return PosicaoGNSS(
        latitude=latitude,
        longitude=longitude,
        altitude_m=round(altitude, 4),
        separacao_geoidal_m=round(separacao, 4),
        qualidade=qualidade,
        qualidade_label=QUALIDADE_LABELS.get(QualidadeFix(qualidade), f"Codigo {qualidade}")
        if qualidade in [item.value for item in QualidadeFix]
        else f"Codigo {qualidade}",
        num_satelites=num_satelites,
        hdop=round(hdop, 2),
        hora_utc=_nmea_hora(campos[1]),
        sentenca_raw=sentenca.strip(),
    )


def parsear_rmc(sentenca: str) -> dict:
    if not validar_checksum(sentenca):
        raise ValueError(f"[ERRO-503] Checksum invalido: {sentenca[:30]}")

    corpo = sentenca.split("*")[0]
    campos = corpo.split(",")
    if len(campos) < 10:
        raise ValueError("[ERRO-507] Sentenca RMC incompleta.")

    status = campos[2]
    if status == "V":
        raise ValueError("[ERRO-602] RMC invalido. Receptor em movimento ou sem sinal.")

    velocidade_nos = float(campos[7]) if campos[7] else 0.0
    velocidade_kmh = round(velocidade_nos * 1.852, 2)

    data_str = campos[9]
    data_formatada = ""
    if len(data_str) == 6:
        data_formatada = f"20{data_str[4:6]}-{data_str[2:4]}-{data_str[:2]}"

    return {
        "hora_utc": _nmea_hora(campos[1]),
        "data_utc": data_formatada,
        "latitude": _nmea_para_decimal(campos[3], campos[4]),
        "longitude": _nmea_para_decimal(campos[5], campos[6]),
        "velocidade_kmh": velocidade_kmh,
        "rumo_graus": float(campos[8]) if campos[8] else 0.0,
    }


def parsear_pchc(sentenca: str) -> dict:
    corpo = sentenca.split("*")[0]
    campos = corpo.split(",")
    if len(campos) < 4:
        return {"compensacao_ativa": False}

    try:
        tilt_x = float(campos[1]) if campos[1] else 0.0
        tilt_y = float(campos[2]) if campos[2] else 0.0
        tilt_total = math.sqrt((tilt_x ** 2) + (tilt_y ** 2))
        # Alguns firmwares do CHC i73+ emitem "$PCHC,x,y,heading" e outros
        # "$PCHC,x,y,z,heading". Aceitamos os dois formatos aqui.
        if len(campos) >= 5:
            tilt_z = float(campos[3]) if campos[3] else 0.0
            heading = float(campos[4]) if campos[4] else 0.0
        else:
            tilt_z = 0.0
            heading = float(campos[3]) if campos[3] else 0.0
        compensacao_ativa = tilt_total <= 60.0
    except (ValueError, IndexError):
        return {"compensacao_ativa": False}

    return {
        "tilt_x": round(tilt_x, 2),
        "tilt_y": round(tilt_y, 2),
        "tilt_z": round(tilt_z, 2),
        "tilt_total_graus": round(tilt_total, 2),
        "heading_graus": round(heading, 2),
        "compensacao_ativa": compensacao_ativa,
        "aviso": None if tilt_total <= 30 else f"Inclinacao alta: {tilt_total:.1f}° - verificar posicao do bastao",
    }


def parsear_gsa(sentenca: str) -> SatelitesGNSS:
    if not validar_checksum(sentenca):
        return SatelitesGNSS()

    corpo = sentenca.split("*")[0]
    campos = corpo.split(",")
    if len(campos) < 18:
        return SatelitesGNSS()

    try:
        pdop = float(campos[15]) if campos[15] else 0.0
        hdop = float(campos[16]) if campos[16] else 0.0
        vdop = float(campos[17]) if campos[17] else 0.0
    except (ValueError, IndexError):
        pdop = hdop = vdop = 0.0

    ids = [campos[index] for index in range(3, 15) if campos[index]]
    return SatelitesGNSS(pdop=pdop, hdop=hdop, vdop=vdop, ids_usados=ids)


def processar_sentenca(sentenca: str) -> dict:
    sentenca = sentenca.strip()
    if not sentenca:
        return {"tipo": "vazio", "dados": None, "erro": None}

    tag = sentenca.lstrip("$").split(",")[0].upper()

    try:
        if tag in ("GNGGA", "GPGGA", "GLGGA", "GAGGA", "GBGGA"):
            pos = parsear_gga(sentenca)
            return {
                "tipo": "GGA",
                "dados": {
                    "latitude": pos.latitude,
                    "longitude": pos.longitude,
                    "altitude_m": pos.altitude_m,
                    "qualidade": pos.qualidade,
                    "qualidade_label": pos.qualidade_label,
                    "rtk_fix": pos.rtk_fix,
                    "utilizavel": pos.utilizavel,
                    "num_satelites": pos.num_satelites,
                    "hdop": pos.hdop,
                    "hora_utc": pos.hora_utc,
                    "precisao_estimada_m": pos.precisao_estimada_m,
                },
                "erro": None,
            }
        if tag in ("GNRMC", "GPRMC", "GLRMC"):
            return {"tipo": "RMC", "dados": parsear_rmc(sentenca), "erro": None}
        if tag in ("GNGSA", "GPGSA", "GLGSA"):
            sat = parsear_gsa(sentenca)
            return {
                "tipo": "GSA",
                "dados": {
                    "pdop": sat.pdop,
                    "hdop": sat.hdop,
                    "vdop": sat.vdop,
                    "num_satelites_usados": len(sat.ids_usados),
                },
                "erro": None,
            }
        if tag == "PCHC":
            return {"tipo": "PCHC", "dados": parsear_pchc(sentenca), "erro": None}
        if tag in ("GNGSV", "GPGSV", "GLGSV"):
            return {"tipo": "GSV", "dados": None, "erro": None}
        if tag in ("GNZDA", "GPZDA"):
            return {"tipo": "ZDA", "dados": None, "erro": None}
        return {"tipo": "desconhecido", "dados": None, "erro": None}
    except ValueError as exc:
        return {"tipo": tag, "dados": None, "erro": str(exc)}


class AcumuladorPontos:
    def __init__(self, n_amostras: int = 5, exigir_rtk_fix: bool = True):
        if n_amostras < 1:
            raise ValueError("[ERRO-109] n_amostras deve ser >= 1.")
        self.n_amostras = n_amostras
        self.exigir_rtk_fix = exigir_rtk_fix
        self._buffer: list[dict] = []
        self.descartadas = 0

    @property
    def completo(self) -> bool:
        return len(self._buffer) >= self.n_amostras

    @property
    def progresso(self) -> str:
        return f"{len(self._buffer)}/{self.n_amostras}"

    def adicionar(self, dados_gga: dict) -> bool:
        if self.completo:
            return False

        if self.exigir_rtk_fix and not dados_gga.get("rtk_fix", False):
            self.descartadas += 1
            return False

        self._buffer.append(dados_gga)
        return True

    def media(self) -> dict:
        if not self._buffer:
            raise ValueError("[ERRO-603] Buffer vazio - nenhuma amostra coletada.")

        quantidade = len(self._buffer)
        lat_media = sum(item["latitude"] for item in self._buffer) / quantidade
        lon_media = sum(item["longitude"] for item in self._buffer) / quantidade
        alt_media = sum(item["altitude_m"] for item in self._buffer) / quantidade
        hdop_medio = sum(item["hdop"] for item in self._buffer) / quantidade

        lat_std = math.sqrt(sum((item["latitude"] - lat_media) ** 2 for item in self._buffer) / quantidade)
        lon_std = math.sqrt(sum((item["longitude"] - lon_media) ** 2 for item in self._buffer) / quantidade)
        std_m = math.sqrt(
            (lat_std * 111320) ** 2
            + (lon_std * 111320 * math.cos(math.radians(lat_media))) ** 2
        )

        return {
            "latitude": round(lat_media, 8),
            "longitude": round(lon_media, 8),
            "altitude_m": round(alt_media, 4),
            "hdop_medio": round(hdop_medio, 2),
            "n_amostras": quantidade,
            "amostras_descartadas": self.descartadas,
            "desvio_padrao_m": round(std_m, 4),
            "qualidade": self._buffer[0]["qualidade"],
            "qualidade_label": self._buffer[0]["qualidade_label"],
        }

    def resetar(self) -> None:
        self._buffer.clear()
        self.descartadas = 0
