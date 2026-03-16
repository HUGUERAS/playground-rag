from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.main import app
from app.api.routes import projetos as projetos_route


class FakeSupabaseClient:
    def __init__(self) -> None:
        self.project = {
            "id": "proj-1",
            "numero_job": "20260316000001",
            "projeto_nome": "Levantamento Teste",
            "status": "medicao",
            "zona_utm": "23S",
            "cliente_nome": "Cliente Teste",
            "total_pontos": 1,
        }
        self.points = [
            {
                "id": "pt-1",
                "projeto_id": "proj-1",
                "nome": "P01",
                "latitude": -15.779167,
                "longitude": -47.929722,
                "este_utm": 186085.106223,
                "norte_utm": 8253307.867629,
            }
        ]

    def table(self, table_name: str) -> "_FakeQuery":
        return _FakeQuery(self, table_name)


class _FakeQuery:
    def __init__(self, client: FakeSupabaseClient, table_name: str) -> None:
        self.client = client
        self.table_name = table_name
        self.filters: dict[str, str] = {}
        self.insert_payload: dict[str, object] | None = None

    def select(self, _: str) -> "_FakeQuery":
        return self

    def insert(self, payload: dict[str, object]) -> "_FakeQuery":
        self.insert_payload = payload
        return self

    def eq(self, field: str, value: str) -> "_FakeQuery":
        self.filters[field] = value
        return self

    def execute(self) -> SimpleNamespace:
        if self.table_name == "vw_projetos_completo":
            project_id = self.filters.get("id")
            if project_id is None or project_id == self.client.project["id"]:
                return SimpleNamespace(data=[self.client.project])
            return SimpleNamespace(data=[])

        if self.table_name == "projetos":
            assert self.insert_payload is not None
            self.client.project = {
                "id": "proj-1",
                "numero_job": self.insert_payload.get("numero_job"),
                "projeto_nome": self.insert_payload["nome"],
                "status": self.insert_payload.get("status", "medicao"),
                "zona_utm": self.insert_payload.get("zona_utm", "23S"),
                "cliente_nome": None,
                "total_pontos": 0,
            }
            return SimpleNamespace(data=[{"id": "proj-1"}])

        if self.table_name == "vw_pontos_utm":
            project_id = self.filters.get("projeto_id")
            if project_id is None or project_id == self.client.project["id"]:
                return SimpleNamespace(data=self.client.points)
            return SimpleNamespace(data=[])

        raise AssertionError(f"Tabela inesperada no teste: {self.table_name}")


@pytest.fixture
def fake_supabase(monkeypatch: pytest.MonkeyPatch) -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    monkeypatch.setattr(projetos_route, "get_supabase_client", lambda: client)
    return client


@pytest.mark.anyio
async def test_get_projetos_returns_view_rows(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/projetos")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == fake_supabase.project["id"]
    assert payload[0]["projeto_nome"] == fake_supabase.project["projeto_nome"]


@pytest.mark.anyio
async def test_post_projetos_inserts_and_returns_created(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/projetos",
            json={
                "nome": "Projeto Novo",
                "numero_job": "20260316000002",
                "municipio": "Brasilia",
                "estado": "DF",
                "zona_utm": "23S",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == "proj-1"
    assert payload["projeto_nome"] == "Projeto Novo"
    assert payload["numero_job"] == "20260316000002"


@pytest.mark.anyio
async def test_get_projeto_by_id_returns_project_and_points(fake_supabase: FakeSupabaseClient) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/projetos/proj-1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["projeto"]["id"] == "proj-1"
    assert len(payload["pontos"]) == 1
    assert payload["pontos"][0]["nome"] == "P01"
