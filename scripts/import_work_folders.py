from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from supabase import Client, create_client


STRONG_CANDIDATES = [
    "abadia",
    "bruno e luana",
    "campo 1812",
    "CH vitoria zildinha[",
    "colinas 040",
    "emerson e gabriel",
    "fazenda margarida",
    "indaia",
    "japo",
    "licinha e marcus",
    "MANGABA2",
    "pirinopolis",
    "samambaia",
    "teodora",
    "victor",
]

MODERATE_CANDIDATES = [
    "amandas",
    "assentamento",
    "calito",
    "candido",
    "cristalina",
    "descriminatoria",
    "erejota",
    "escola pet",
    "fiorello",
    "gilson amorim",
    "jardimbotanico",
    "joana",
    "lago norte",
    "lauro",
    "lote ca",
    "nabil",
    "paracatuu",
    "renata parkway",
    "renato lago sul",
    "sidrolandia",
    "togim cartorio",
    "toguim",
]


@dataclass
class ImportResult:
    folder_name: str
    folder_path: str
    cliente_id: str | None
    projeto_id: str | None
    cliente_status: str
    projeto_status: str
    notes: str | None = None


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL") or os.getenv("GEOADMIN_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("GEOADMIN_SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY nao definidos.")
    return create_client(url, key)


def _rows(result: Any) -> list[dict[str, Any]]:
    data = getattr(result, "data", None)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def find_cliente(client: Client, nome: str) -> dict[str, Any] | None:
    result = client.table("clientes").select("id,nome,deleted_at").eq("nome", nome).execute()
    for row in _rows(result):
        if row.get("deleted_at") is None:
            return row
    return None


def create_cliente(client: Client, nome: str) -> dict[str, Any]:
    result = client.table("clientes").insert({"nome": nome}).execute()
    rows = _rows(result)
    if not rows:
        raise RuntimeError(f"Falha ao criar cliente '{nome}'.")
    return rows[0]


def find_projeto(client: Client, nome: str, cliente_id: str) -> dict[str, Any] | None:
    result = (
        client.table("projetos")
        .select("id,nome,cliente_id,deleted_at")
        .eq("nome", nome)
        .eq("cliente_id", cliente_id)
        .execute()
    )
    for row in _rows(result):
        if row.get("deleted_at") is None:
            return row
    return None


def create_projeto(client: Client, nome: str, cliente_id: str, folder_path: Path) -> dict[str, Any]:
    imported_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "cliente_id": cliente_id,
        "nome": nome,
        "descricao": f"Importado automaticamente de {folder_path} em {imported_at}",
        "status": "medicao",
        "zona_utm": "23S",
    }
    result = client.table("projetos").insert(payload).execute()
    rows = _rows(result)
    if not rows:
        raise RuntimeError(f"Falha ao criar projeto '{nome}'.")
    return rows[0]


def import_candidates(root: Path, candidates: list[str]) -> list[ImportResult]:
    client = get_client()
    results: list[ImportResult] = []

    for folder_name in candidates:
        folder_path = root / folder_name
        if not folder_path.exists():
            results.append(
                ImportResult(
                    folder_name=folder_name,
                    folder_path=str(folder_path),
                    cliente_id=None,
                    projeto_id=None,
                    cliente_status="missing_folder",
                    projeto_status="missing_folder",
                    notes="Pasta nao encontrada no disco.",
                )
            )
            continue

        cliente = find_cliente(client, folder_name)
        if cliente:
            cliente_id = cliente["id"]
            cliente_status = "existing"
        else:
            cliente = create_cliente(client, folder_name)
            cliente_id = cliente["id"]
            cliente_status = "created"

        projeto = find_projeto(client, folder_name, cliente_id)
        if projeto:
            projeto_id = projeto["id"]
            projeto_status = "existing"
        else:
            projeto = create_projeto(client, folder_name, cliente_id, folder_path)
            projeto_id = projeto["id"]
            projeto_status = "created"

        results.append(
            ImportResult(
                folder_name=folder_name,
                folder_path=str(folder_path),
                cliente_id=cliente_id,
                projeto_id=projeto_id,
                cliente_status=cliente_status,
                projeto_status=projeto_status,
            )
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa candidatos fortes de pastas de trabalho para Supabase.")
    parser.add_argument(
        "--root",
        default=r"D:\pastas de trabalho",
        help="Raiz das pastas de trabalho.",
    )
    parser.add_argument(
        "--report",
        default=r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Import_2026-03-16.json",
        help="Arquivo JSON de relatorio.",
    )
    parser.add_argument(
        "--tier",
        choices=["strong", "moderate", "all"],
        default="strong",
        help="Seleciona quais candidatos importar.",
    )
    args = parser.parse_args()

    if args.tier == "strong":
        candidates = STRONG_CANDIDATES
    elif args.tier == "moderate":
        candidates = MODERATE_CANDIDATES
    else:
        candidates = STRONG_CANDIDATES + MODERATE_CANDIDATES

    results = import_candidates(Path(args.root), candidates)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    created = sum(1 for item in results if item.projeto_status == "created")
    existing = sum(1 for item in results if item.projeto_status == "existing")
    print(f"Import concluido. Projetos criados: {created}. Projetos ja existentes: {existing}.")
    print(f"Relatorio: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
