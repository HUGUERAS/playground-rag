from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import Client


class PointsError(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


QUALITY_LABELS = {
    0: "Sem fix",
    1: "GPS autonomo (~3m)",
    2: "DGPS/SBAS (~1m)",
    4: "RTK Fix (cm)",
    5: "RTK Float (~0.3m)",
}


def _unwrap_result(result: Any) -> list[dict[str, Any]]:
    data = getattr(result, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def quality_warning(quality_fix: int, hdop: float | None) -> str | None:
    warnings: list[str] = []
    if quality_fix not in (4, 5):
        warnings.append(
            f"Qualidade '{QUALITY_LABELS.get(quality_fix, 'Desconhecida')}' insuficiente para levantamento oficial."
        )
    if hdop is not None and hdop > 2.0:
        warnings.append(f"HDOP={hdop:.1f} alto; geometria de satelites fraca.")
    return " | ".join(warnings) if warnings else None


def ensure_project(client: Client, project_id: str) -> dict[str, Any]:
    try:
        result = client.table("projetos").select("id, nome, status, deleted_at").eq("id", project_id).execute()
    except Exception as exc:
        raise PointsError(401, "Projeto nao encontrado.", status_code=404) from exc

    projects = _unwrap_result(result)
    if not projects:
        raise PointsError(401, "Projeto nao encontrado.", status_code=404)

    project = projects[0]
    if project.get("deleted_at"):
        raise PointsError(402, "Projeto arquivado.", status_code=410)

    return project


def _point_exists(client: Client, project_id: str, name: str) -> bool:
    try:
        result = (
            client.table("pontos")
            .select("id")
            .eq("projeto_id", project_id)
            .eq("nome", name)
            .is_("deleted_at", "null")
            .execute()
        )
    except Exception:
        return False

    return bool(_unwrap_result(result))


def create_point(client: Client, payload: dict[str, Any]) -> dict[str, Any]:
    point_name = str(payload["nome"])
    project_id = str(payload["projeto_id"])

    if _point_exists(client, project_id, point_name):
        raise PointsError(302, f"Ponto '{point_name}' ja existe neste projeto.", status_code=409)

    insert_payload = {
        "projeto_id": project_id,
        "nome": point_name,
        "descricao": payload.get("descricao"),
        "codigo": payload.get("codigo"),
        "coordenada": f"SRID=4674;POINT({payload['longitude']} {payload['latitude']})",
        "altitude_m": payload.get("altitude_m"),
        "separacao_geoidal_m": payload.get("separacao_geoidal_m"),
        "qualidade_fix": payload["qualidade_fix"],
        "hdop": payload.get("hdop"),
        "num_satelites": payload.get("num_satelites"),
        "num_amostras": payload.get("num_amostras", 1),
        "camada": str(payload.get("camada", "PONTOS")).upper(),
        "operador": payload.get("operador"),
        "receptor_gnss": payload.get("receptor_gnss", "CHC i73+"),
        "sincronizado": True,
        "coletado_em": datetime.now(timezone.utc).isoformat(),
    }
    insert_payload = {key: value for key, value in insert_payload.items() if value is not None}

    try:
        result = client.table("pontos").insert(insert_payload).execute()
    except Exception as exc:
        raise PointsError(303, "Falha ao salvar ponto no Supabase.", status_code=500) from exc

    inserted = _unwrap_result(result)
    if not inserted:
        raise PointsError(304, "Supabase nao retornou o ponto criado.", status_code=500)

    return inserted[0]


def list_points(client: Client, project_id: str, layer: str | None = None) -> list[dict[str, Any]]:
    try:
        query = client.table("vw_pontos_utm").select("*").eq("projeto_id", project_id).order("coletado_em")
        if layer:
            query = query.eq("camada", layer.upper())
        result = query.execute()
    except Exception as exc:
        raise PointsError(306, "Falha ao consultar pontos do projeto no Supabase.", status_code=500) from exc

    return _unwrap_result(result)


def archive_point(client: Client, point_id: str) -> dict[str, Any]:
    try:
        result = (
            client.table("pontos")
            .update({"deleted_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", point_id)
            .is_("deleted_at", "null")
            .execute()
        )
    except Exception as exc:
        raise PointsError(307, "Falha ao arquivar ponto no Supabase.", status_code=500) from exc

    archived = _unwrap_result(result)
    if not archived:
        raise PointsError(403, "Ponto nao encontrado.", status_code=404)

    return archived[0]
