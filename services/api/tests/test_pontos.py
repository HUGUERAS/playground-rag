from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.main import app
from app.api.routes import pontos as pontos_route


class FakeSupabaseClient:
    def __init__(self) -> None:
        self.projects = {
            "proj-1": {"id": "proj-1", "nome": "Projeto Teste", "status": "medicao", "deleted_at": None},
        }
        self.points = [
            {
                "id": "pt-1",
                "projeto_id": "proj-1",
                "nome": "P01",
                "latitude": -15.779167,
                "longitude": -47.929722,
                "altitude_m": 1172.0,
                "qualidade_fix": 4,
                "hdop": 0.6,
                "num_amostras": 5,
                "camada": "PONTOS",
                "coletado_em": "2026-03-16T12:00:00+00:00",
                "sincronizado": True,
                "deleted_at": None,
            }
        ]

    def table(self, table_name: str) -> "_FakeQuery":
        return _FakeQuery(self, table_name)


class _FakeQuery:
    def __init__(self, client: FakeSupabaseClient, table_name: str) -> None:
        self.client = client
        self.table_name = table_name
        self.filters: list[tuple[str, str, Any]] = []
        self.insert_payload: dict[str, Any] | None = None
        self.update_payload: dict[str, Any] | None = None
        self.order_field: str | None = None

    def select(self, _: str) -> "_FakeQuery":
        return self

    def insert(self, payload: dict[str, Any]) -> "_FakeQuery":
        self.insert_payload = payload
        return self

    def update(self, payload: dict[str, Any]) -> "_FakeQuery":
        self.update_payload = payload
        return self

    def eq(self, field: str, value: Any) -> "_FakeQuery":
        self.filters.append(("eq", field, value))
        return self

    def is_(self, field: str, value: Any) -> "_FakeQuery":
        self.filters.append(("is", field, value))
        return self

    def order(self, field: str) -> "_FakeQuery":
        self.order_field = field
        return self

    def execute(self) -> SimpleNamespace:
        if self.table_name == "projetos":
            return SimpleNamespace(data=self._filter_projects())

        if self.table_name == "pontos":
            if self.insert_payload is not None:
                point = {
                    "id": f"pt-{len(self.client.points) + 1}",
                    "deleted_at": None,
                    **self.insert_payload,
                }
                self.client.points.append(point)
                return SimpleNamespace(data=[point])

            if self.update_payload is not None:
                point = self._match_single_point()
                if point is None:
                    return SimpleNamespace(data=[])
                point.update(self.update_payload)
                return SimpleNamespace(data=[point])

            return SimpleNamespace(data=self._filter_points(include_geometry_table=True))

        if self.table_name == "vw_pontos_utm":
            return SimpleNamespace(data=self._filter_points(include_geometry_table=False))

        raise AssertionError(f"Tabela inesperada no teste: {self.table_name}")

    def _filter_projects(self) -> list[dict[str, Any]]:
        rows = list(self.client.projects.values())
        for filter_type, field, value in self.filters:
            if filter_type == "eq":
                rows = [row for row in rows if row.get(field) == value]
        return rows

    def _filter_points(self, include_geometry_table: bool) -> list[dict[str, Any]]:
        rows = list(self.client.points)
        for filter_type, field, value in self.filters:
            if filter_type == "eq":
                rows = [row for row in rows if row.get(field) == value]
            elif filter_type == "is" and value == "null":
                rows = [row for row in rows if row.get(field) is None]
        if self.order_field:
            rows.sort(key=lambda row: row.get(self.order_field) or "")
        if include_geometry_table:
            return rows
        return [
            {
                "id": row["id"],
                "projeto_id": row["projeto_id"],
                "nome": row["nome"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "altitude_m": row.get("altitude_m"),
                "qualidade_fix": row["qualidade_fix"],
                "hdop": row.get("hdop"),
                "num_amostras": row.get("num_amostras", 1),
                "camada": row.get("camada", "PONTOS"),
                "coletado_em": row.get("coletado_em"),
                "sincronizado": row.get("sincronizado", True),
            }
            for row in rows
            if row.get("deleted_at") is None
        ]

    def _match_single_point(self) -> dict[str, Any] | None:
        rows = self._filter_points(include_geometry_table=True)
        return rows[0] if rows else None


@pytest.fixture
def fake_supabase(monkeypatch: pytest.MonkeyPatch) -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    monkeypatch.setattr(pontos_route, "get_supabase_client", lambda: client)
    return client


@pytest.mark.anyio
async def test_post_pontos_creates_point_and_returns_warning(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/pontos",
            json={
                "projeto_id": "proj-1",
                "nome": "p02",
                "latitude": -15.78,
                "longitude": -47.93,
                "altitude_m": 1173.0,
                "qualidade_fix": 1,
                "hdop": 3.2,
                "num_amostras": 1,
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["nome"] == "P02"
    assert payload["qualidade_fix"] == 1
    assert "HDOP" in payload["aviso"]
    assert any(point["nome"] == "P02" for point in fake_supabase.points)


@pytest.mark.anyio
async def test_post_pontos_sync_reports_partial_failure(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/pontos/sync",
            json={
                "pontos": [
                    {
                        "projeto_id": "proj-1",
                        "nome": "P03",
                        "latitude": -15.781,
                        "longitude": -47.931,
                        "qualidade_fix": 4,
                        "id_local": "local-1",
                    },
                    {
                        "projeto_id": "proj-x",
                        "nome": "P04",
                        "latitude": -15.782,
                        "longitude": -47.932,
                        "qualidade_fix": 4,
                        "id_local": "local-2",
                    },
                ]
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_enviados"] == 2
    assert payload["total_salvos"] == 1
    assert payload["total_erros"] == 1
    assert payload["erros"][0]["id_local"] == "local-2"
    assert payload["erros"][0]["codigo"] == 401


@pytest.mark.anyio
async def test_get_and_delete_pontos_work_for_project(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        list_response = await client.get("/pontos/proj-1")
        delete_response = await client.delete("/pontos/pt-1")

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["projeto_id"] == "proj-1"
    assert list_payload["total"] == 1
    assert list_payload["pontos"][0]["nome"] == "P01"

    assert delete_response.status_code == 200
    delete_payload = delete_response.json()
    assert delete_payload["mensagem"] == "Ponto pt-1 arquivado."
    assert fake_supabase.points[0]["deleted_at"] is not None
