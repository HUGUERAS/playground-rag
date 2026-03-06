import argparse
import json
import mimetypes
import re
import shutil
import subprocess
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
LOGS_DIR = AUTOMATION_DIR / "logs"
DEFAULT_CONFIG = AUTOMATION_DIR / "config.json"
BATCH_RUNS_DIR = AUTOMATION_DIR / "batch_runs"


class JobState:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_job = None
        self.history = deque(maxlen=50)
        self.batch_current = None
        self.batch_history = deque(maxlen=20)


STATE = JobState()


def iso_now():
    return datetime.now().isoformat(timespec="seconds")


def find_powershell_exe():
    candidates = [
        shutil.which("pwsh"),
        shutil.which("powershell"),
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def parse_checklist(path: Path):
    if not path.exists():
        return {"exists": False, "path": str(path), "content": "", "items": [], "stats": {"done": 0, "total": 0}}

    content = path.read_text(encoding="utf-8", errors="replace")
    items = []
    done = 0
    total = 0

    for line in content.splitlines():
        if line.startswith("- [") and "] [" in line:
            try:
                left, rest = line[0:6], line[6:]
                checked = "[x]" in left
                start = rest.find("[")
                end = rest.find("]", start + 1)
                if start >= 0 and end > start:
                    item_id = rest[start + 1:end].strip()
                    title = rest[end + 1 :].strip()
                    items.append({"id": item_id, "title": title, "done": checked})
                    total += 1
                    if checked:
                        done += 1
            except Exception:
                continue

    return {
        "exists": True,
        "path": str(path),
        "content": content,
        "items": items,
        "stats": {"done": done, "total": total},
    }


def list_logs():
    if not LOGS_DIR.exists():
        return []
    files = sorted(LOGS_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for p in files[:50]:
        stat = p.stat()
        result.append(
            {
                "name": p.name,
                "path": str(p),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            }
        )
    return result


def tail_text(path: Path, max_lines: int = 200):
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max_lines:])


def sanitize_job(job):
    if job is None:
        return None
    return {
        "id": job["id"],
        "status": job["status"],
        "started_at": job["started_at"],
        "ended_at": job.get("ended_at"),
        "return_code": job.get("return_code"),
        "dry_run": job["dry_run"],
        "config_path": job["config_path"],
        "command": job["command"],
        "output_tail": list(job["output"])[-350:],
    }


def sanitize_batch(batch):
    if batch is None:
        return None

    items = []
    for item in batch["items"]:
        items.append(
            {
                "index": item["index"],
                "project_path": item["project_path"],
                "status": item["status"],
                "started_at": item.get("started_at"),
                "ended_at": item.get("ended_at"),
                "return_code": item.get("return_code"),
                "error": item.get("error"),
                "job_id": item.get("job_id"),
                "config_path": item.get("config_path"),
            }
        )

    return {
        "id": batch["id"],
        "status": batch["status"],
        "started_at": batch["started_at"],
        "ended_at": batch.get("ended_at"),
        "dry_run": batch["dry_run"],
        "base_config_path": batch["base_config_path"],
        "total": len(items),
        "current_index": batch.get("current_index", 0),
        "stop_requested": batch.get("stop_requested", False),
        "items": items,
    }


def append_output(job, line: str):
    with STATE.lock:
        job["output"].append(line.rstrip("\n"))


def finalize_job(job, return_code: int):
    with STATE.lock:
        if job["status"] == "stopped":
            job["return_code"] = return_code
            job["ended_at"] = iso_now()
        else:
            job["return_code"] = return_code
            job["ended_at"] = iso_now()
            job["status"] = "completed" if return_code == 0 else "failed"
        STATE.history.appendleft(sanitize_job(job))


def monitor_job(job):
    process = job["process"]
    try:
        for line in process.stdout:
            append_output(job, line)
    finally:
        rc = process.wait()
        finalize_job(job, rc)


def resolve_config_path(config_path: str):
    cfg_path = Path(config_path) if config_path else DEFAULT_CONFIG
    if not cfg_path.is_absolute():
        cfg_path = (AUTOMATION_DIR / cfg_path).resolve()
    return cfg_path


def launch_job(dry_run: bool, config_path: str):
    ps_exe = find_powershell_exe()
    if ps_exe is None:
        return None, "PowerShell nao encontrado no sistema."

    script_path = AUTOMATION_DIR / "run_tudo_real.ps1"
    if not script_path.exists():
        return None, f"Script nao encontrado: {script_path}"

    cfg_path = resolve_config_path(config_path)
    if not cfg_path.exists():
        return None, f"Config nao encontrada: {cfg_path}"

    with STATE.lock:
        running = STATE.current_job and STATE.current_job["status"] == "running"
        if running:
            return None, "Ja existe uma execucao em andamento."

    cmd = [
        ps_exe,
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-ConfigPath",
        str(cfg_path),
    ]
    if dry_run:
        cmd.append("-DryRun")

    process = subprocess.Popen(
        cmd,
        cwd=str(AUTOMATION_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    job = {
        "id": str(uuid.uuid4()),
        "status": "running",
        "started_at": iso_now(),
        "dry_run": dry_run,
        "config_path": str(cfg_path),
        "command": cmd,
        "output": deque(maxlen=6000),
        "process": process,
    }

    with STATE.lock:
        STATE.current_job = job

    thread = threading.Thread(target=monitor_job, args=(job,), daemon=True)
    thread.start()
    return sanitize_job(job), None


def stop_current_job():
    with STATE.lock:
        job = STATE.current_job
        if not job or job["status"] != "running":
            return None, "Nenhuma execucao ativa para parar."
        process = job["process"]
        job["status"] = "stopped"

    process.terminate()
    return sanitize_job(job), None


def safe_name(raw: str):
    clean = re.sub(r"[^A-Za-z0-9._-]", "_", raw)
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean[:80] if clean else "lote"


def ensure_checklist_copy(cfg_data: dict, run_dir: Path):
    checklist_data = cfg_data.get("Checklist")
    if not isinstance(checklist_data, dict):
        checklist_data = {"Enabled": True}
        cfg_data["Checklist"] = checklist_data

    enabled = bool(checklist_data.get("Enabled", True))
    checklist_data["Enabled"] = enabled
    if not enabled:
        return

    template_value = checklist_data.get("Path")
    template_path = Path(template_value) if template_value else (AUTOMATION_DIR / "checklist_roteiro.md")
    if not template_path.is_absolute():
        template_path = (AUTOMATION_DIR / template_path).resolve()

    run_checklist = run_dir / "checklist_roteiro.md"
    if template_path.exists():
        shutil.copyfile(template_path, run_checklist)
    else:
        run_checklist.write_text("# Checklist Roteiro\n\n## Historico\n", encoding="utf-8")

    checklist_data["Path"] = str(run_checklist)


def build_runtime_config(base_config_path: Path, project_path: str, batch_id: str, item_index: int):
    cfg = json.loads(base_config_path.read_text(encoding="utf-8"))
    lot_name = safe_name(Path(project_path).stem)
    run_dir = BATCH_RUNS_DIR / batch_id / f"{item_index:03d}_{lot_name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg["ProjectPath"] = project_path
    cfg["LogDir"] = str(run_dir / "logs")

    ensure_checklist_copy(cfg, run_dir)

    post = cfg.get("PostProcess")
    if isinstance(post, dict) and bool(post.get("Enabled", False)):
        out_base = post.get("OutputDir")
        out_path = Path(out_base) if out_base else (run_dir / "output_geo")
        if not out_path.is_absolute():
            out_path = (AUTOMATION_DIR / out_path).resolve()
        post["OutputDir"] = str(out_path / lot_name)

    runtime_cfg = run_dir / "config.runtime.json"
    runtime_cfg.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return runtime_cfg


def parse_projects_from_payload(payload: dict):
    projects = []

    raw_list = payload.get("projects")
    if isinstance(raw_list, list):
        for item in raw_list:
            txt = str(item).strip()
            if txt and not txt.startswith("#") and not txt.startswith(";"):
                projects.append(txt)

    raw_text = payload.get("projects_text")
    if isinstance(raw_text, str) and raw_text.strip():
        for line in raw_text.splitlines():
            txt = line.strip()
            if txt and not txt.startswith("#") and not txt.startswith(";"):
                projects.append(txt)

    projects_file = payload.get("projects_file")
    if isinstance(projects_file, str) and projects_file.strip():
        p = Path(projects_file)
        if not p.is_absolute():
            p = (AUTOMATION_DIR / p).resolve()
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                txt = line.strip()
                if txt and not txt.startswith("#") and not txt.startswith(";"):
                    projects.append(txt)

    normalized = []
    for p in projects:
        normalized.append(p)
    return normalized


def wait_for_job_finish(job_id: str):
    while True:
        time.sleep(0.4)
        with STATE.lock:
            cur = STATE.current_job
            if cur and cur.get("id") == job_id:
                if cur.get("status") == "running":
                    continue
                return {
                    "status": cur.get("status"),
                    "return_code": cur.get("return_code"),
                    "ended_at": cur.get("ended_at"),
                }

            hist = None
            for h in STATE.history:
                if h.get("id") == job_id:
                    hist = h
                    break
            if hist:
                return {
                    "status": hist.get("status"),
                    "return_code": hist.get("return_code"),
                    "ended_at": hist.get("ended_at"),
                }


def batch_worker(batch):
    any_failed = False

    for item in batch["items"]:
        with STATE.lock:
            if batch.get("stop_requested"):
                item["status"] = "skipped"
                item["ended_at"] = iso_now()
                continue
            batch["current_index"] = item["index"]
            item["status"] = "preparing"
            item["started_at"] = iso_now()

        project_path = item["project_path"]
        project_file = Path(project_path)
        if not project_file.exists():
            with STATE.lock:
                item["status"] = "failed"
                item["error"] = f"Projeto nao encontrado: {project_path}"
                item["ended_at"] = iso_now()
            any_failed = True
            continue

        try:
            cfg_path = build_runtime_config(
                base_config_path=Path(batch["base_config_path"]),
                project_path=project_path,
                batch_id=batch["id"],
                item_index=item["index"],
            )
            with STATE.lock:
                item["config_path"] = str(cfg_path)
                item["status"] = "running"
        except Exception as exc:
            with STATE.lock:
                item["status"] = "failed"
                item["error"] = f"Falha ao preparar config: {exc}"
                item["ended_at"] = iso_now()
            any_failed = True
            continue

        job, err = launch_job(dry_run=batch["dry_run"], config_path=str(cfg_path))
        if err:
            with STATE.lock:
                item["status"] = "failed"
                item["error"] = err
                item["ended_at"] = iso_now()
            any_failed = True
            continue

        with STATE.lock:
            item["job_id"] = job["id"]

        result = wait_for_job_finish(job["id"])

        with STATE.lock:
            item["ended_at"] = result.get("ended_at") or iso_now()
            item["return_code"] = result.get("return_code")
            status = result.get("status")
            if status == "completed" and item["return_code"] == 0:
                item["status"] = "completed"
            elif status == "stopped":
                item["status"] = "stopped"
                batch["stop_requested"] = True
            else:
                item["status"] = "failed"
                any_failed = True

    with STATE.lock:
        if batch.get("stop_requested"):
            for item in batch["items"]:
                if item["status"] in ("pending", "preparing"):
                    item["status"] = "skipped"
                    item["ended_at"] = iso_now()
            batch["status"] = "stopped"
        elif any_failed:
            batch["status"] = "failed"
        else:
            batch["status"] = "completed"

        batch["ended_at"] = iso_now()
        STATE.batch_history.appendleft(sanitize_batch(batch))


def start_batch(dry_run: bool, base_config_path: str, projects: list[str]):
    cfg_path = resolve_config_path(base_config_path)
    if not cfg_path.exists():
        return None, f"Config nao encontrada: {cfg_path}"

    if not projects:
        return None, "Nenhum projeto informado para lote."

    with STATE.lock:
        running_job = STATE.current_job and STATE.current_job.get("status") == "running"
        running_batch = STATE.batch_current and STATE.batch_current.get("status") == "running"
        if running_job or running_batch:
            return None, "Ja existe execucao em andamento."

        batch_id = str(uuid.uuid4())
        items = []
        for i, proj in enumerate(projects, start=1):
            items.append(
                {
                    "index": i,
                    "project_path": proj,
                    "status": "pending",
                    "started_at": None,
                    "ended_at": None,
                    "return_code": None,
                    "error": None,
                    "job_id": None,
                    "config_path": None,
                }
            )

        batch = {
            "id": batch_id,
            "status": "running",
            "started_at": iso_now(),
            "ended_at": None,
            "dry_run": dry_run,
            "base_config_path": str(cfg_path),
            "current_index": 0,
            "stop_requested": False,
            "items": items,
        }
        STATE.batch_current = batch

    BATCH_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    thread = threading.Thread(target=batch_worker, args=(batch,), daemon=True)
    thread.start()

    return sanitize_batch(batch), None


def stop_batch():
    with STATE.lock:
        batch = STATE.batch_current
        if not batch or batch.get("status") != "running":
            return None, "Nenhum lote em execucao para parar."
        batch["stop_requested"] = True

    stop_current_job()
    return sanitize_batch(batch), None


class Handler(BaseHTTPRequestHandler):
    server_version = "MetricaUI/1.1"

    def log_message(self, format, *args):
        return

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _serve_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado")
            return
        data = path.read_bytes()
        ctype, _ = mimetypes.guess_type(str(path))
        if not ctype:
            ctype = "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/":
            return self._serve_file(STATIC_DIR / "index.html")

        if route.startswith("/static/"):
            rel = route.replace("/static/", "", 1)
            return self._serve_file(STATIC_DIR / rel)

        if route == "/api/status":
            with STATE.lock:
                current = sanitize_job(STATE.current_job)
                history = list(STATE.history)
                batch_current = sanitize_batch(STATE.batch_current)
                batch_history = list(STATE.batch_history)
            checklist = parse_checklist(AUTOMATION_DIR / "checklist_roteiro.md")
            payload = {
                "current": current,
                "history": history,
                "batch_current": batch_current,
                "batch_history": batch_history,
                "logs": list_logs(),
                "checklist_stats": checklist["stats"],
            }
            return self._json(HTTPStatus.OK, payload)

        if route == "/api/checklist":
            checklist = parse_checklist(AUTOMATION_DIR / "checklist_roteiro.md")
            return self._json(HTTPStatus.OK, checklist)

        if route == "/api/logs":
            qs = parse_qs(parsed.query)
            name = (qs.get("name") or [None])[0]
            lines = int((qs.get("lines") or ["200"])[0])
            logs = list_logs()
            selected = None
            if name:
                for item in logs:
                    if item["name"] == name:
                        selected = item
                        break
            if selected is None and logs:
                selected = logs[0]

            text = ""
            if selected:
                text = tail_text(Path(selected["path"]), max_lines=max(10, min(lines, 2000)))

            return self._json(
                HTTPStatus.OK,
                {
                    "files": logs,
                    "selected": selected,
                    "content": text,
                },
            )

        return self.send_error(HTTPStatus.NOT_FOUND, "Rota nao encontrada")

    def do_POST(self):
        route = urlparse(self.path).path

        if route == "/api/run":
            try:
                payload = self._read_json()
            except Exception as exc:
                return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": f"JSON invalido: {exc}"})

            dry_run = bool(payload.get("dry_run", False))
            config_path = str(payload.get("config_path") or DEFAULT_CONFIG)
            job, err = launch_job(dry_run=dry_run, config_path=config_path)
            if err:
                return self._json(HTTPStatus.CONFLICT, {"ok": False, "error": err})
            return self._json(HTTPStatus.OK, {"ok": True, "job": job})

        if route == "/api/stop":
            job, err = stop_current_job()
            if err:
                return self._json(HTTPStatus.CONFLICT, {"ok": False, "error": err})
            return self._json(HTTPStatus.OK, {"ok": True, "job": job})

        if route == "/api/batch/start":
            try:
                payload = self._read_json()
            except Exception as exc:
                return self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": f"JSON invalido: {exc}"})

            dry_run = bool(payload.get("dry_run", False))
            config_path = str(payload.get("config_path") or DEFAULT_CONFIG)
            projects = parse_projects_from_payload(payload)
            batch, err = start_batch(dry_run=dry_run, base_config_path=config_path, projects=projects)
            if err:
                return self._json(HTTPStatus.CONFLICT, {"ok": False, "error": err})
            return self._json(HTTPStatus.OK, {"ok": True, "batch": batch})

        if route == "/api/batch/stop":
            batch, err = stop_batch()
            if err:
                return self._json(HTTPStatus.CONFLICT, {"ok": False, "error": err})
            return self._json(HTTPStatus.OK, {"ok": True, "batch": batch})

        return self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Rota nao encontrada"})


def main():
    parser = argparse.ArgumentParser(description="Metrica Automacao UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Metrica UI disponivel em http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
