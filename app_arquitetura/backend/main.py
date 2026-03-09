from __future__ import annotations

import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_DIR = ROOT / "automacao" / "metrica"
RUN_SCRIPT = AUTOMATION_DIR / "run_tudo_real.ps1"
DEFAULT_CONFIG = AUTOMATION_DIR / "config.json"
FRONTEND_INDEX = ROOT / "app_arquitetura" / "frontend" / "index.html"

app = FastAPI(title="App Arquitetura Integrada", version="0.1.0")

_rag_chain = None
_rag_unavailable_reason: str | None = None
_current_job: subprocess.Popen[str] | None = None
_sessions: dict[str, dict[str, Any]] = {}
_rural_onboardings: list[dict[str, Any]] = []
_urban_activations: list[dict[str, Any]] = []


class QueryRequest(BaseModel):
    question: str


class StartRequest(BaseModel):
    dry_run: bool = True
    config_path: str | None = None


class TechLoginRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=4)


class RuralOnboardRequest(BaseModel):
    owner_name: str = Field(min_length=2)
    farm_name: str = Field(min_length=2)
    area_hectares: float = Field(gt=0)
    city: str = Field(min_length=2)
    state: str = Field(min_length=2, max_length=2)


class UrbanActivateRequest(BaseModel):
    owner_name: str = Field(min_length=2)
    property_code: str = Field(min_length=2)
    city: str = Field(min_length=2)
    state: str = Field(min_length=2, max_length=2)
    active: bool = True


def _ensure_rag_available(reindex: bool = False):
    """Carrega o pipeline RAG sob demanda para evitar erro no boot da API."""
    global _rag_chain, _rag_unavailable_reason

    try:
        from rag import setup_rag
    except Exception as exc:
        _rag_unavailable_reason = f"Dependencias RAG indisponiveis: {exc}"
        return None

    if _rag_chain is None or reindex:
        try:
            _rag_chain = setup_rag(reindex=reindex)
        except Exception as exc:
            _rag_unavailable_reason = f"Falha ao inicializar RAG: {exc}"
            return None

    return _rag_chain


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


@app.get("/")
def home() -> Any:
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return {
        "ok": True,
        "message": "Frontend nao encontrado. Abra /health ou configure app_arquitetura/frontend/index.html",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    rag_ready = _rag_chain is not None
    return {
        "ok": True,
        "service": "app-arquitetura",
        "rag_ready": rag_ready,
        "rag_reason": _rag_unavailable_reason or ("RAG ainda nao inicializado" if not rag_ready else None),
        "functions_ready": {
            "tech_login": True,
            "rural_onboard": True,
            "urban_activate": True,
            "metrica_orchestration": True,
            "rag_query": True,
        },
    }


@app.get("/api/spec/functions")
def api_functions() -> dict[str, Any]:
    return {
        "profiles": ["Topografo", "Proprietario", "Agricultor"],
        "functions": [
            {"name": "Tech Login", "method": "POST", "path": "/api/tech/login"},
            {"name": "Rural Onboard", "method": "POST", "path": "/api/rural/onboard"},
            {"name": "Urban Activate", "method": "POST", "path": "/api/urban/activate"},
            {"name": "Onboarding Snapshot", "method": "GET", "path": "/api/onboarding/snapshot"},
            {"name": "RAG Query", "method": "POST", "path": "/rag/query"},
            {"name": "Metrica Start", "method": "POST", "path": "/metrica/start"},
            {"name": "Metrica Status", "method": "GET", "path": "/metrica/status"},
        ],
    }


@app.post("/api/tech/login")
def tech_login(payload: TechLoginRequest) -> dict[str, Any]:
    # MVP com token local para simular autenticacao do perfil Topografo.
    token = _new_id("tok")
    session = {
        "token": token,
        "email": payload.email,
        "role": "Topografo",
        "created_at": _now_iso(),
    }
    _sessions[token] = session
    return {
        "ok": True,
        "message": "Login realizado com sucesso",
        "token": token,
        "profile": "Topografo",
    }


@app.post("/api/rural/onboard")
def rural_onboard(payload: RuralOnboardRequest) -> dict[str, Any]:
    onboarding_id = _new_id("rural")
    record = {
        "onboarding_id": onboarding_id,
        "owner_name": payload.owner_name,
        "farm_name": payload.farm_name,
        "area_hectares": payload.area_hectares,
        "city": payload.city,
        "state": payload.state.upper(),
        "status": "registered",
        "created_at": _now_iso(),
    }
    _rural_onboardings.append(record)
    return {
        "ok": True,
        "message": "Onboarding rural registrado",
        "data": record,
    }


@app.post("/api/urban/activate")
def urban_activate(payload: UrbanActivateRequest) -> dict[str, Any]:
    activation_id = _new_id("urban")
    record = {
        "activation_id": activation_id,
        "owner_name": payload.owner_name,
        "property_code": payload.property_code,
        "city": payload.city,
        "state": payload.state.upper(),
        "active": payload.active,
        "status": "active" if payload.active else "inactive",
        "created_at": _now_iso(),
    }
    _urban_activations.append(record)
    return {
        "ok": True,
        "message": "Ativacao urbana registrada",
        "data": record,
    }


@app.get("/api/onboarding/snapshot")
def onboarding_snapshot() -> dict[str, Any]:
    return {
        "ok": True,
        "stats": {
            "sessions": len(_sessions),
            "rural_onboardings": len(_rural_onboardings),
            "urban_activations": len(_urban_activations),
        },
        "latest": {
            "rural": _rural_onboardings[-1] if _rural_onboardings else None,
            "urban": _urban_activations[-1] if _urban_activations else None,
        },
    }


@app.post("/rag/reindex")
def rag_reindex() -> dict[str, Any]:
    rag_chain = _ensure_rag_available(reindex=True)
    if rag_chain is None:
        raise HTTPException(status_code=503, detail=_rag_unavailable_reason or "RAG indisponivel")

    if rag_chain is None:
        raise HTTPException(status_code=500, detail="Falha ao criar chain RAG")

    return {"ok": True, "message": "Indice RAG reindexado com sucesso"}


@app.post("/rag/query")
def rag_query(payload: QueryRequest) -> dict[str, Any]:
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia")

    rag_chain = _ensure_rag_available(reindex=False)
    if rag_chain is None:
        raise HTTPException(status_code=503, detail=_rag_unavailable_reason or "RAG indisponivel")

    try:
        result = rag_chain.invoke({"input": payload.question})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar RAG: {exc}") from exc

    return {
        "ok": True,
        "answer": result.get("answer", ""),
    }


@app.post("/metrica/start")
def metrica_start(payload: StartRequest) -> dict[str, Any]:
    global _current_job

    if _current_job is not None and _current_job.poll() is None:
        raise HTTPException(status_code=409, detail="Ja existe execucao Metrica ativa")

    if not RUN_SCRIPT.exists():
        raise HTTPException(status_code=404, detail=f"Script nao encontrado: {RUN_SCRIPT}")

    cfg = Path(payload.config_path) if payload.config_path else DEFAULT_CONFIG
    if not cfg.is_absolute():
        cfg = (AUTOMATION_DIR / cfg).resolve()

    if not cfg.exists():
        raise HTTPException(status_code=404, detail=f"Config nao encontrada: {cfg}")

    cmd = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(RUN_SCRIPT),
        "-ConfigPath",
        str(cfg),
    ]
    if payload.dry_run:
        cmd.append("-DryRun")

    try:
        _current_job = subprocess.Popen(
            cmd,
            cwd=str(AUTOMATION_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao iniciar Metrica: {exc}") from exc

    return {"ok": True, "pid": _current_job.pid, "dry_run": payload.dry_run}


@app.post("/metrica/stop")
def metrica_stop() -> dict[str, Any]:
    global _current_job

    if _current_job is None or _current_job.poll() is not None:
        return {"ok": True, "message": "Nenhuma execucao ativa"}

    _current_job.terminate()
    return {"ok": True, "message": "Sinal de parada enviado"}


@app.get("/metrica/status")
def metrica_status() -> dict[str, Any]:
    global _current_job

    if _current_job is None:
        return {"running": False}

    return_code = _current_job.poll()
    return {
        "running": return_code is None,
        "pid": _current_job.pid,
        "return_code": return_code,
    }
