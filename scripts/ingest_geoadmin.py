from __future__ import annotations

import argparse
import locale
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


OUTER_MAP = {
    "PRD: Sistema GeoAdmin (Projeto Desenrola).md": "01-product/PRD_GeoAdmin.md",
    "Master Plan: Estratégia de Desenvolvimento GeoAdmin.md": "02-planning/Roadmap_GeoAdmin.md",
    ".cursorrules": "04-reference/Regras_Agentes_e_Validacoes.md",
    "Biblioteca de Comandos (Prompt Dictionary) - GeoAdmin Pro.md": "04-reference/Comandos_Agentes.md",
    "Blindagem e Resiliência (Error Handling) - GeoAdmin Pro.md": "04-reference/Blindagem_Resiliencia.md",
    "🗺️ GeoAdmin Pro (Projeto Desenrola).md": "01-product/Product_Vision_GeoAdmin.md",
}

INNER_MAP = {
    "PRD_GeoAdmin.md": "01-product/PRD_GeoAdmin.md",
    "Master_Plan.md": "02-planning/Roadmap_GeoAdmin.md",
    ".cursorrules": "04-reference/Regras_Agentes_e_Validacoes.md",
    "Comandos_Agentes.md": "04-reference/Comandos_Agentes.md",
    "Blindagem_Resiliencia.md": "04-reference/Blindagem_Resiliencia.md",
    "README.md": "01-product/Product_Vision_GeoAdmin.md",
}

STRUCTURE = [
    "01-product",
    "02-planning",
    "03-functional-mapping",
    "04-reference",
    "05-source-archive",
]


@dataclass
class IngestReport:
    copied: list[str]
    skipped: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest GeoAdmin source bundle into a structured docs workspace."
    )
    parser.add_argument("--zip", required=True, help="Path to the outer GeoAdmin zip file.")
    parser.add_argument(
        "--html",
        required=False,
        help="Optional path to the Gemini HTML export to archive as historical source.",
    )
    parser.add_argument(
        "--output",
        default="geoadmin-docs",
        help="Output directory for the structured documentation.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite already existing files in the output structure.",
    )
    return parser.parse_args()


def safe_print(text: str) -> None:
    encoding = sys.stdout.encoding or locale.getpreferredencoding(False) or "utf-8"
    cleaned = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(cleaned)


def ensure_structure(root: Path) -> None:
    for part in STRUCTURE:
        (root / part).mkdir(parents=True, exist_ok=True)


def copy_entry_bytes(
    zf: zipfile.ZipFile,
    entry_name: str,
    destination: Path,
    overwrite: bool,
    report: IngestReport,
) -> None:
    if destination.exists() and not overwrite:
        report.skipped.append(f"kept existing file: {destination}")
        return
    try:
        data = zf.read(entry_name)
    except KeyError:
        report.warnings.append(f"missing entry in zip: {entry_name}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    report.copied.append(f"copied: {entry_name} -> {destination}")


def archive_sources(
    output_root: Path,
    zip_path: Path,
    html_path: Path | None,
    inner_zip_bytes: bytes | None,
    report: IngestReport,
) -> None:
    archive_dir = output_root / "05-source-archive"
    shutil.copy2(zip_path, archive_dir / "GeoAdmin_source_bundle_outer.zip")
    report.copied.append("archived outer zip")
    if html_path:
        shutil.copy2(html_path, archive_dir / "Google_Gemini_source.html")
        report.copied.append("archived html source")
    if inner_zip_bytes:
        (archive_dir / "GeoAdmin_source_bundle_inner.zip").write_bytes(inner_zip_bytes)
        report.copied.append("archived inner zip")


def extract_inner_zip_bytes(outer_zip: zipfile.ZipFile) -> bytes | None:
    for candidate in ("GeoAdmin_Project_Organizado.zip",):
        try:
            return outer_zip.read(candidate)
        except KeyError:
            continue
    return None


def ingest_from_zip(zip_path: Path, html_path: Path | None, output_root: Path, overwrite: bool) -> IngestReport:
    report = IngestReport(copied=[], skipped=[], warnings=[])
    ensure_structure(output_root)

    with zipfile.ZipFile(zip_path) as outer_zip:
        for src_name, relative_dest in OUTER_MAP.items():
            copy_entry_bytes(outer_zip, src_name, output_root / relative_dest, overwrite, report)

        inner_zip_bytes = extract_inner_zip_bytes(outer_zip)
        if inner_zip_bytes:
            with zipfile.ZipFile(Path(zip_path.parent / "__tmp_inner_geoadmin.zip"), "w"):
                pass
            tmp_path = output_root / "05-source-archive" / "__tmp_inner_geoadmin.zip"
            tmp_path.write_bytes(inner_zip_bytes)
            with zipfile.ZipFile(tmp_path) as inner_zip:
                for src_name, relative_dest in INNER_MAP.items():
                    copy_entry_bytes(inner_zip, src_name, output_root / relative_dest, overwrite, report)
            tmp_path.unlink(missing_ok=True)
        else:
            report.warnings.append("inner zip not found in outer bundle")

        archive_sources(output_root, zip_path, html_path, inner_zip_bytes, report)

    return report


def write_source_index(output_root: Path, html_path: Path | None) -> None:
    html_line = "- `Google_Gemini_source.html`: export bruto da conversa usada como contexto historico.\n" if html_path else ""
    content = f"""# Source Index GeoAdmin

## Papel desta pasta

Esta pasta guarda apenas a trilha de origem do material consolidado. Os arquivos daqui nao sao a documentacao oficial de trabalho diario.

## Fontes arquivadas

- `GeoAdmin_source_bundle_outer.zip`: pacote original recebido.
- `GeoAdmin_source_bundle_inner.zip`: pacote interno com nomes de arquivos padronizados.
{html_line}
## Documentos oficiais esperados

- `01-product/PRD_GeoAdmin.md`
- `01-product/Product_Vision_GeoAdmin.md`
- `02-planning/Roadmap_GeoAdmin.md`
- `03-functional-mapping/App_Functional_Mapping.md`
- `04-reference/Comandos_Agentes.md`
- `04-reference/Blindagem_Resiliencia.md`
- `04-reference/Regras_Agentes_e_Validacoes.md`
"""
    (output_root / "05-source-archive" / "Source_Index.md").write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    zip_path = Path(args.zip).expanduser().resolve()
    html_path = Path(args.html).expanduser().resolve() if args.html else None
    output_root = Path(args.output).expanduser().resolve()

    if not zip_path.exists():
        print(f"zip not found: {zip_path}", file=sys.stderr)
        return 1
    if html_path and not html_path.exists():
        print(f"html not found: {html_path}", file=sys.stderr)
        return 1

    report = ingest_from_zip(zip_path, html_path, output_root, args.overwrite)
    write_source_index(output_root, html_path)

    print("GeoAdmin ingest complete.")
    safe_print(f"Output: {output_root}")
    if report.copied:
        print("\nCopied:")
        for item in report.copied:
            safe_print(f"- {item}")
    if report.skipped:
        print("\nSkipped:")
        for item in report.skipped:
            safe_print(f"- {item}")
    if report.warnings:
        print("\nWarnings:")
        for item in report.warnings:
            safe_print(f"- {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
