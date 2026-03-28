from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from supabase import Client, create_client


REPORT_PATHS = {
    "strong": Path(
        r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Import_2026-03-16.json"
    ),
    "moderate": Path(
        r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Import_Moderate_2026-03-16.json"
    ),
}

TRACKED_EXTENSIONS = [".csv", ".dxf", ".kml", ".pdf", ".tbkp", ".topo", ".txt"]


def get_client(url: str, key: str) -> Client:
    return create_client(url, key)


def load_report_rows() -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for tier, report_path in REPORT_PATHS.items():
        if not report_path.exists():
            continue
        rows = json.loads(report_path.read_text(encoding="utf-8"))
        for row in rows:
            row["import_tier"] = tier
            merged[row["projeto_id"]] = row
    return merged


def folder_stats(folder_path: Path | None) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "folder_exists": False,
        "files_total": 0,
    }
    for extension in TRACKED_EXTENSIONS:
        stats[f"count_{extension[1:]}"] = 0

    if folder_path is None or not folder_path.exists():
        return stats

    stats["folder_exists"] = True
    for path in folder_path.rglob("*"):
        if not path.is_file():
            continue
        stats["files_total"] += 1
        extension = path.suffix.lower()
        if extension in TRACKED_EXTENSIONS:
            stats[f"count_{extension[1:]}"] += 1
    return stats


def fetch_projects(client: Client) -> list[dict[str, Any]]:
    result = client.table("vw_projetos_completo").select("*").order("projeto_nome").execute()
    return getattr(result, "data", []) or []


def build_rows(projects: list[dict[str, Any]], report_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    table_rows: list[dict[str, Any]] = []
    for project in projects:
        report_row = report_rows.get(project["id"])
        source_folder = Path(report_row["folder_path"]) if report_row else None
        stats = folder_stats(source_folder)

        row = {
            "projeto_id": project["id"],
            "cliente_nome": project.get("cliente_nome"),
            "projeto_nome": project.get("projeto_nome"),
            "numero_job": project.get("numero_job"),
            "status": project.get("status"),
            "zona_utm": project.get("zona_utm"),
            "total_pontos": project.get("total_pontos"),
            "cpf_cnpj": project.get("cpf_cnpj"),
            "telefone": project.get("telefone"),
            "email": project.get("email"),
            "cliente_municipio": project.get("cliente_municipio"),
            "valor_servico": project.get("valor_servico"),
            "valor_pago": project.get("valor_pago"),
            "saldo_devedor": project.get("saldo_devedor"),
            "criado_em": project.get("criado_em"),
            "atualizado_em": project.get("atualizado_em"),
            "import_tier": report_row.get("import_tier") if report_row else "seed/manual",
            "folder_name": report_row.get("folder_name") if report_row else None,
            "folder_path": report_row.get("folder_path") if report_row else None,
            "cliente_status": report_row.get("cliente_status") if report_row else None,
            "projeto_status": report_row.get("projeto_status") if report_row else None,
            "notes": report_row.get("notes") if report_row else None,
        }
        row.update(stats)
        table_rows.append(row)
    return table_rows


def write_csv(rows: list[dict[str, Any]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tabela Completa de Pastas de Trabalho",
        "",
        f"Total de registros: {len(rows)}",
        "",
        "| Tier | Cliente | Projeto | Job | Pontos | PDF | KML | CSV | DXF | TOPO | Pasta |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {tier} | {cliente} | {projeto} | {job} | {pontos} | {pdf} | {kml} | {csv} | {dxf} | {topo} | {pasta} |".format(
                tier=row["import_tier"] or "",
                cliente=(row["cliente_nome"] or "").replace("|", "/"),
                projeto=(row["projeto_nome"] or "").replace("|", "/"),
                job=row["numero_job"] or "",
                pontos=row["total_pontos"] or 0,
                pdf=row["count_pdf"],
                kml=row["count_kml"],
                csv=row["count_csv"],
                dxf=row["count_dxf"],
                topo=row["count_topo"],
                pasta=(row["folder_name"] or "").replace("|", "/"),
            )
        )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera tabela completa com dados importados das pastas de trabalho.")
    parser.add_argument("--supabase-url", required=True)
    parser.add_argument("--supabase-key", required=True)
    parser.add_argument(
        "--csv-output",
        default=r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Full_Table_2026-03-16.csv",
    )
    parser.add_argument(
        "--md-output",
        default=r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Full_Table_2026-03-16.md",
    )
    args = parser.parse_args()

    client = get_client(args.supabase_url, args.supabase_key)
    projects = fetch_projects(client)
    report_rows = load_report_rows()
    rows = build_rows(projects, report_rows)

    write_csv(rows, Path(args.csv_output))
    write_markdown(rows, Path(args.md_output))
    print(f"CSV: {args.csv_output}")
    print(f"MD: {args.md_output}")
    print(f"Registros: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
