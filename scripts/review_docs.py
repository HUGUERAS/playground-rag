from __future__ import annotations

import argparse
import locale
import re
import sys
from collections import Counter
from pathlib import Path


EXPECTED_FILES = [
    "README.md",
    "01-product/PRD_GeoAdmin.md",
    "01-product/Product_Vision_GeoAdmin.md",
    "02-planning/Roadmap_GeoAdmin.md",
    "03-functional-mapping/App_Functional_Mapping.md",
    "04-reference/Comandos_Agentes.md",
    "04-reference/Blindagem_Resiliencia.md",
    "04-reference/Regras_Agentes_e_Validacoes.md",
    "04-reference/Formulas_e_Validacoes_Criticas.md",
    "05-source-archive/Source_Index.md",
]

KEY_TERMS = [
    "Projeto",
    "Levantamento",
    "Config",
    "Ferramentas",
    "Vista CAD",
    "Camadas",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight review on the GeoAdmin docs structure.")
    parser.add_argument(
        "--root",
        default="geoadmin-docs",
        help="Root directory of the GeoAdmin docs tree.",
    )
    return parser.parse_args()


def safe_print(text: str) -> None:
    encoding = sys.stdout.encoding or locale.getpreferredencoding(False) or "utf-8"
    cleaned = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(cleaned)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def markdown_headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("#")]


def duplicate_headings(files: list[Path]) -> list[str]:
    headings: list[str] = []
    for path in files:
        headings.extend(markdown_headings(read_text(path)))
    counts = Counter(headings)
    return [heading for heading, count in counts.items() if count > 1]


def missing_expected_files(root: Path) -> list[str]:
    missing = []
    for rel in EXPECTED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def check_mapping_terms(root: Path) -> list[str]:
    target = root / "03-functional-mapping" / "App_Functional_Mapping.md"
    if not target.exists():
        return ["mapping file is missing"]
    text = read_text(target)
    missing_terms = [term for term in KEY_TERMS if term not in text]
    return [f"mapping missing key term: {term}" for term in missing_terms]


def detect_empty_markdown(files: list[Path]) -> list[str]:
    empty = []
    for path in files:
        text = read_text(path).strip()
        body = re.sub(r"[#`\-\s|:]", "", text)
        if not body:
            empty.append(str(path))
    return empty


def find_gap_markers(root: Path) -> list[str]:
    markers = []
    for path in root.rglob("*.md"):
        text = read_text(path)
        if "Gaps identificados" in text or "Pendencias abertas" in text:
            markers.append(str(path.relative_to(root)))
    return markers


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"docs root not found: {root}", file=sys.stderr)
        return 1

    markdown_files = sorted(root.rglob("*.md"))
    missing = missing_expected_files(root)
    duplicates = duplicate_headings(markdown_files)
    empty_files = detect_empty_markdown(markdown_files)
    mapping_issues = check_mapping_terms(root)
    gap_files = find_gap_markers(root)

    safe_print("GeoAdmin docs review")
    safe_print(f"Root: {root}")
    safe_print(f"Markdown files: {len(markdown_files)}")

    safe_print("\nMissing expected files:")
    if missing:
        for item in missing:
            safe_print(f"- {item}")
    else:
        safe_print("- none")

    safe_print("\nDuplicate headings:")
    if duplicates:
        for item in duplicates:
            safe_print(f"- {item}")
    else:
        safe_print("- none")

    safe_print("\nEmpty markdown files:")
    if empty_files:
        for item in empty_files:
            safe_print(f"- {item}")
    else:
        safe_print("- none")

    safe_print("\nFunctional mapping coverage:")
    if mapping_issues:
        for item in mapping_issues:
            safe_print(f"- {item}")
    else:
        safe_print("- all key areas referenced")

    safe_print("\nFiles with explicit gaps or pending items:")
    if gap_files:
        for item in gap_files:
            safe_print(f"- {item}")
    else:
        safe_print("- none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
