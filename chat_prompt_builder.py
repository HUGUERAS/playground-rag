#!/usr/bin/env python3
"""
CLI para consolidar conversas de IA (VS Code/Cursor/Antigravity/export) e
gerar:
1) consolidated_conversations.md
2) summary.md
3) master_prompt.md
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".jsonl", ".log"}
CHAT_FILENAME_HINTS = (
    "chat",
    "conversation",
    "history",
    "messages",
)
CHAT_PATH_HINTS = (
    "\\chat-session-resources\\",
    "\\chatsessions\\",
    "\\chateditingsessions\\",
    "\\emptywindowchatsessions\\",
    "\\continue_sessions\\",
    "\\antigravity\\brain\\",
    "chatinteraction",
    "toolusage",
    "editinteraction",
)
CHAT_BASENAMES = {
    "chatinteraction.jsonl",
    "toolusage.jsonl",
    "editinteraction.jsonl",
    "chat.json",
    "messages.json",
    "sessions.json",
    "conversation.json",
    "conversations.json",
    "history.json",
}
EXCLUDED_PATH_HINTS = (
    "\\node_modules\\",
    "\\.git\\",
    "\\.venv\\",
    "\\venv\\",
    "\\site-packages\\",
    "\\extensions\\",
    "\\ms-playwright\\",
    "\\ask-agent\\",
    "\\explore-agent\\",
    "\\plan-agent\\",
    "\\resources\\app\\",
)
EXCLUDED_BASENAME_EXACT = {
    "workspace.json",
    "api.json",
    "copilotcli.session.metadata.json",
}
JSON_TEXT_FIELD_HINTS = {
    "content",
    "text",
    "message",
    "prompt",
    "response",
    "question",
    "answer",
    "assistant",
    "user",
    "body",
    "delta",
    "output",
    "input",
    "summary",
}
STOPWORDS = {
    "a",
    "o",
    "e",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "no",
    "na",
    "nos",
    "nas",
    "um",
    "uma",
    "uns",
    "umas",
    "com",
    "sem",
    "para",
    "por",
    "em",
    "que",
    "se",
    "ao",
    "aos",
    "as",
    "os",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "is",
    "it",
    "for",
    "on",
    "you",
    "we",
    "they",
    "this",
    "that",
    "be",
    "with",
    "as",
    "an",
}

TECH_KEYWORDS = {
    "python": {"python", "fastapi", "django", "flask", "pydantic"},
    "javascript/typescript": {"javascript", "typescript", "node", "next", "react", "vue", "svelte"},
    ".net": {"dotnet", ".net", "c#", "asp.net", "aspnet", "blazor"},
    "java": {"java", "spring", "springboot", "kotlin"},
    "go": {"golang", "go", "gin", "fiber"},
    "database": {"postgres", "mysql", "sqlite", "mongodb", "redis", "sql"},
    "cloud/devops": {"docker", "kubernetes", "aws", "azure", "gcp", "ci", "cd", "github actions"},
    "ai/llm": {"openai", "ollama", "rag", "embedding", "vector", "langchain", "llm"},
}

DEFAULT_SOURCE_CANDIDATES = [
    r"C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat",
    r"C:\Users\User\AppData\Roaming\Code\User\workspaceStorage",
    r"C:\Users\User\AppData\Roaming\Cursor\User\globalStorage",
    r"C:\Users\User\AppData\Roaming\Cursor\User\workspaceStorage",
    r"C:\Users\User\.cursor",
    r"C:\Users\User\.gemini\antigravity",
]


@dataclass
class ChatEntry:
    source: Path
    content: str
    char_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolida conversas de IA e gera resumo + prompt mestre para criar app."
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Arquivo ou pasta de entrada (pode repetir).",
    )
    parser.add_argument(
        "--include-default-sources",
        action="store_true",
        help="Inclui caminhos padrao locais (VS Code/Cursor/Antigravity).",
    )
    parser.add_argument(
        "--output-dir",
        default="chat_context_output",
        help="Pasta de saida para arquivos gerados.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=300,
        help="Limite de arquivos processados.",
    )
    parser.add_argument(
        "--max-chars-per-file",
        type=int,
        default=12000,
        help="Limite de caracteres aproveitados por arquivo.",
    )
    parser.add_argument(
        "--min-line-length",
        type=int,
        default=10,
        help="Tamanho minimo de linha para entrar no resumo.",
    )
    return parser.parse_args()


def normalize_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"\r\n?", "\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def iter_sources(args: argparse.Namespace) -> List[Path]:
    found: List[Path] = []
    raw_sources = list(args.source)
    if args.include_default_sources:
        raw_sources.extend(DEFAULT_SOURCE_CANDIDATES)

    dedup = set()
    for raw in raw_sources:
        p = Path(raw).expanduser()
        key = str(p).lower()
        if key in dedup:
            continue
        dedup.add(key)
        if p.exists():
            found.append(p)
    return found


def is_candidate_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    raw = str(path).lower()
    name = path.name.lower()
    if name in EXCLUDED_BASENAME_EXACT:
        return False
    if name.endswith("-audit.json") or name.endswith(".metadata.json"):
        return False
    if any(hint in raw for hint in EXCLUDED_PATH_HINTS):
        return False
    if name in CHAT_BASENAMES:
        return True
    if any(hint in name for hint in CHAT_FILENAME_HINTS):
        return True
    if any(hint in raw for hint in CHAT_PATH_HINTS):
        return True
    if (
        path.suffix.lower() in {".md", ".txt"}
        and "\\antigravity\\brain\\" in raw
    ):
        return True
    return False


def list_candidate_files(
    sources: Sequence[Path],
    max_files: int,
    explicit_file_sources: Sequence[Path],
) -> List[Path]:
    files: List[Path] = []
    explicit_set = {str(p.resolve()).lower() for p in explicit_file_sources if p.is_file()}
    for source in sources:
        if source.is_file():
            if source.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(source)
        else:
            for p in source.rglob("*"):
                if str(p.resolve()).lower() in explicit_set:
                    files.append(p)
                elif is_candidate_file(p):
                    files.append(p)
                if len(files) >= max_files:
                    return files
        if len(files) >= max_files:
            return files
    return files


def _extract_text_fragments_from_json(value, key_hint: str = "") -> List[str]:
    fragments: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            fragments.extend(_extract_text_fragments_from_json(child, str(key).lower()))
    elif isinstance(value, list):
        for child in value:
            fragments.extend(_extract_text_fragments_from_json(child, key_hint))
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return fragments
        if key_hint in JSON_TEXT_FIELD_HINTS:
            fragments.append(text)
        elif len(text) > 80:
            fragments.append(text)
    return fragments


def read_text_file(path: Path, max_chars: int) -> str:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return normalize_text(content[:max_chars])
    except Exception:
        return ""


def read_json_file(path: Path, max_chars: int) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return ""
    fragments = _extract_text_fragments_from_json(data)
    merged = "\n".join(fragments)
    return normalize_text(merged[:max_chars])


def read_jsonl_file(path: Path, max_chars: int) -> str:
    collected: List[str] = []
    budget = max_chars
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    fragments = _extract_text_fragments_from_json(data)
                    for fragment in fragments:
                        if budget <= 0:
                            break
                        clipped = fragment[:budget]
                        collected.append(clipped)
                        budget -= len(clipped)
                except json.JSONDecodeError:
                    clipped = line[:budget]
                    collected.append(clipped)
                    budget -= len(clipped)
                if budget <= 0:
                    break
    except Exception:
        return ""
    return normalize_text("\n".join(collected))


def load_chat_entries(files: Sequence[Path], max_chars_per_file: int) -> List[ChatEntry]:
    entries: List[ChatEntry] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".json":
            text = read_json_file(path, max_chars_per_file)
        elif suffix == ".jsonl":
            text = read_jsonl_file(path, max_chars_per_file)
        else:
            text = read_text_file(path, max_chars_per_file)
        if not text:
            continue
        entries.append(ChatEntry(source=path, content=text, char_count=len(text)))
    return entries


def sentence_candidates(text: str, min_line_length: int) -> List[str]:
    lines = [normalize_text(line) for line in text.split("\n")]
    lines = [line for line in lines if len(line) >= min_line_length]
    cleaned: List[str] = []
    for line in lines:
        if line.lower().startswith(("http://", "https://")):
            continue
        if line.count("\\") >= 3 or re.search(r"[A-Za-z]:\\", line):
            continue
        if re.match(r"^[\{\[\]\},:;\"']+$", line):
            continue
        if line.startswith(("{", "[", "}", "]")):
            continue
        if re.search(r"[A-Za-z0-9]", line):
            cleaned.append(line)
    return cleaned


def select_relevant_lines(lines: Iterable[str], patterns: Sequence[str], limit: int) -> List[str]:
    picked: List[str] = []
    seen = set()
    rx_list = [re.compile(p, re.IGNORECASE) for p in patterns]
    for line in lines:
        if len(picked) >= limit:
            break
        if any(rx.search(line) for rx in rx_list):
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            picked.append(line[:220])
    return picked


def top_keywords(text: str, limit: int = 20) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9\.\-\+#]{3,}", text.lower())
    filtered = [
        t for t in tokens
        if t not in STOPWORDS and not t.isdigit() and not t.startswith("http")
    ]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]


def detect_technologies(text: str) -> List[str]:
    low = text.lower()
    detected: List[str] = []
    for label, keywords in TECH_KEYWORDS.items():
        if any(keyword in low for keyword in keywords):
            detected.append(label)
    return detected


def build_summary(entries: Sequence[ChatEntry], min_line_length: int) -> Dict[str, List[str]]:
    all_text = "\n\n".join(entry.content for entry in entries)
    lines = sentence_candidates(all_text, min_line_length=min_line_length)

    objective_patterns = [
        r"\b(objetivo|goal|meta|quero|preciso|need to|we need|vamos|build|criar app|criar um app)\b",
        r"\b(feature|funcionalidade|entrega|scope|escopo|mvp)\b",
    ]
    constraint_patterns = [
        r"\b(n[ãa]o|sem|must|deve|obrigat[oó]rio|restri[cç][aã]o|constraint|limite|deadline)\b",
        r"\b(performance|seguran[cç]a|security|custo|lat[eê]ncia|compliance)\b",
    ]
    architecture_patterns = [
        r"\b(api|backend|frontend|database|db|arquitetura|microservi[cç]o|monolito|event)\b",
    ]
    test_patterns = [
        r"\b(test|teste|qa|valida[cç][aã]o|crit[eé]rio de aceite|aceita[cç][aã]o)\b",
    ]
    risk_patterns = [
        r"\b(risco|risk|problema|bloqueio|blocker|unknown|incerteza|trade[- ]?off)\b",
    ]

    objectives = select_relevant_lines(lines, objective_patterns, limit=12)
    constraints = select_relevant_lines(lines, constraint_patterns, limit=12)
    architecture = select_relevant_lines(lines, architecture_patterns, limit=12)
    tests = select_relevant_lines(lines, test_patterns, limit=8)
    risks = select_relevant_lines(lines, risk_patterns, limit=8)
    keywords = top_keywords(all_text, limit=20)
    techs = detect_technologies(all_text)

    if not objectives:
        objectives = ["Definir objetivos do app a partir do contexto consolidado."]
    if not constraints:
        constraints = ["Sem restricoes explicitas suficientes; revisar conversas para limites adicionais."]
    if not architecture:
        architecture = ["Arquitetura ainda aberta; decidir stack e modularizacao."]
    if not tests:
        tests = ["Definir criterios de aceite por funcionalidade principal."]
    if not risks:
        risks = ["Riscos nao explicitados claramente nas conversas extraidas."]

    return {
        "objectives": objectives,
        "constraints": constraints,
        "architecture": architecture,
        "tests": tests,
        "risks": risks,
        "keywords": keywords,
        "technologies": techs,
    }


def write_consolidated(entries: Sequence[ChatEntry], output_file: Path) -> None:
    lines: List[str] = ["# Consolidated Conversations", ""]
    for index, entry in enumerate(entries, start=1):
        lines.append(f"## Source {index}: {entry.source}")
        lines.append("")
        lines.append(f"- Characters: {entry.char_count}")
        lines.append("")
        lines.append("```text")
        lines.append(entry.content)
        lines.append("```")
        lines.append("")
    output_file.write_text("\n".join(lines), encoding="utf-8")


def write_summary(
    summary: Dict[str, List[str]],
    entries: Sequence[ChatEntry],
    output_file: Path,
) -> None:
    lines: List[str] = [
        "# Summary",
        "",
        f"- Total sources used: {len(entries)}",
        f"- Total extracted chars: {sum(e.char_count for e in entries)}",
        "",
        "## Technologies",
    ]
    techs = summary["technologies"] or ["Nao detectado claramente."]
    lines.extend([f"- {item}" for item in techs])
    lines.append("")
    lines.append("## Main Objectives")
    lines.extend([f"- {item}" for item in summary["objectives"]])
    lines.append("")
    lines.append("## Constraints")
    lines.extend([f"- {item}" for item in summary["constraints"]])
    lines.append("")
    lines.append("## Architecture Signals")
    lines.extend([f"- {item}" for item in summary["architecture"]])
    lines.append("")
    lines.append("## Validation and Tests")
    lines.extend([f"- {item}" for item in summary["tests"]])
    lines.append("")
    lines.append("## Risks and Open Points")
    lines.extend([f"- {item}" for item in summary["risks"]])
    lines.append("")
    lines.append("## Top Keywords")
    lines.extend([f"- {item}" for item in summary["keywords"]])
    lines.append("")
    output_file.write_text("\n".join(lines), encoding="utf-8")


def write_master_prompt(
    summary: Dict[str, List[str]],
    entries: Sequence[ChatEntry],
    output_file: Path,
) -> None:
    references = [str(e.source) for e in entries]
    ref_lines = "\n".join(f"- {r}" for r in references[:40])
    if len(references) > 40:
        ref_lines += f"\n- ... e mais {len(references) - 40} arquivos"

    lines = [
        "# Prompt Mestre para Criacao de App",
        "",
        "Use o prompt abaixo em outra IA para iniciar o desenvolvimento com contexto consolidado:",
        "",
        "```text",
        "Voce e um engenheiro de software senior e vai projetar e implementar um app.",
        "",
        "Contexto consolidado:",
        f"- Tecnologias detectadas: {', '.join(summary['technologies']) if summary['technologies'] else 'Nao definido'}",
        "- Objetivos principais:",
    ]
    lines.extend([f"  - {item}" for item in summary["objectives"][:8]])
    lines.append("- Restricoes e condicoes:")
    lines.extend([f"  - {item}" for item in summary["constraints"][:8]])
    lines.append("- Sinais de arquitetura:")
    lines.extend([f"  - {item}" for item in summary["architecture"][:8]])
    lines.append("- Riscos e duvidas abertas:")
    lines.extend([f"  - {item}" for item in summary["risks"][:6]])
    lines.extend(
        [
            "",
            "Entrega esperada:",
            "1. Defina escopo de MVP com backlog priorizado.",
            "2. Proponha arquitetura (componentes, dados, APIs e fluxo).",
            "3. Liste plano de implementacao por fases com estimativa relativa.",
            "4. Defina testes (unitarios, integracao e aceite).",
            "5. Explique trade-offs tecnicos e riscos com mitigacao.",
            "",
            "Formato de resposta:",
            "- Seja especifico.",
            "- Use listas objetivas.",
            "- Nao invente requisitos ausentes; marque suposicoes explicitamente.",
            "```",
            "",
            "## References",
            ref_lines or "- Nenhuma referencia listada.",
            "",
        ]
    )
    output_file.write_text("\n".join(lines), encoding="utf-8")


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run() -> int:
    args = parse_args()
    sources = iter_sources(args)
    if not sources:
        print("Nenhuma fonte valida encontrada. Use --source e/ou --include-default-sources.")
        return 2

    explicit_file_sources = [Path(s).expanduser() for s in args.source if Path(s).expanduser().is_file()]
    files = list_candidate_files(
        sources,
        max_files=args.max_files,
        explicit_file_sources=explicit_file_sources,
    )
    if not files:
        print("Nenhum arquivo candidato encontrado nas fontes informadas.")
        return 3

    entries = load_chat_entries(files, max_chars_per_file=args.max_chars_per_file)
    if not entries:
        print("Nenhum conteudo textual util foi extraido.")
        return 4

    summary = build_summary(entries, min_line_length=args.min_line_length)

    output_dir = Path(args.output_dir).expanduser().resolve()
    ensure_output_dir(output_dir)
    consolidated_file = output_dir / "consolidated_conversations.md"
    summary_file = output_dir / "summary.md"
    prompt_file = output_dir / "master_prompt.md"

    write_consolidated(entries, consolidated_file)
    write_summary(summary, entries, summary_file)
    write_master_prompt(summary, entries, prompt_file)

    print(f"OK: fontes={len(sources)} arquivos_lidos={len(entries)}")
    print(f"OK: {consolidated_file}")
    print(f"OK: {summary_file}")
    print(f"OK: {prompt_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
