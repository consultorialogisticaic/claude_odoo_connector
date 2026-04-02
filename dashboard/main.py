"""
Odoo Demo Creator — Dashboard

Lightweight FastAPI + Jinja2 + HTMX web UI for managing local Odoo instances.

Run:
    cd odoo_demo_creator
    uvicorn dashboard.main:app --reload --port 7070
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
import xmlrpc.client
import zipfile
from pathlib import Path
from typing import Optional

import re
import threading

import aiofiles
import httpx
import psutil
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
# ODOO_WORKSPACE_ROOT env var lets consumers (e.g. a parent repo using connector
# as a submodule) point to their own odoo-workspace. Falls back to cwd/odoo-workspace
# so `uvicorn connector.dashboard.main:app` run from the project root works naturally.
WORKSPACE_ROOT = Path(os.environ.get("ODOO_WORKSPACE_ROOT", Path.cwd() / "odoo-workspace"))
REGISTRY_PATH = WORKSPACE_ROOT / "workspace.json"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Odoo Demo Creator")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ---------------------------------------------------------------------------
# PostgreSQL helpers
# ---------------------------------------------------------------------------

DB_USER = "odoo"
DB_PASSWORD = "odoo"


def _ensure_pg_role() -> None:
    """Create the 'odoo' PostgreSQL role if it doesn't exist.

    Uses `createuser` CLI so we don't need psycopg2 at the dashboard level.
    The role gets CREATEDB so odoo-bin can create/drop databases.
    """
    # Check if role already exists
    check = subprocess.run(
        ["psql", "-tAc", f"SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}'", "postgres"],
        capture_output=True, text=True,
    )
    if check.stdout.strip() == "1":
        return  # role exists

    # Create the role with a password and CREATEDB privilege
    result = subprocess.run(
        ["psql", "-c",
         f"CREATE ROLE {DB_USER} LOGIN PASSWORD '{DB_PASSWORD}' CREATEDB;",
         "postgres"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to create PostgreSQL role '{DB_USER}': {result.stderr.strip()}"
        )


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"instances": []}
    return json.loads(REGISTRY_PATH.read_text())


def save_registry(reg: dict) -> None:
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2))


def get_instance(instance_id: str) -> dict:
    reg = load_registry()
    inst = next((i for i in reg["instances"] if i["id"] == instance_id), None)
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found")
    return inst


def next_port(reg: dict) -> int:
    used = {i.get("port", 0) for i in reg["instances"]}
    port = 8069
    while port in used:
        port += 1
    return port


def _pid_file(instance_id: str) -> Path:
    return WORKSPACE_ROOT / f".{instance_id}.pid"


def _is_running(instance_id: str) -> bool:
    pid_file = _pid_file(instance_id)
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
        return psutil.pid_exists(pid)
    except (ValueError, OSError):
        return False


def _enrich(inst: dict) -> dict:
    inst = dict(inst)
    inst_type = inst.get("type", "local")
    inst["instance_type"] = inst_type
    inst["capabilities"] = inst.get("capabilities", ["start", "stop", "install-cli", "install-rpc"])

    if inst_type == "local":
        inst["running"] = _is_running(inst["id"])
        if inst["running"]:
            inst["status"] = "running"
        elif inst.get("status") != "error":
            inst["status"] = "stopped"
        inst["version_ready"] = _is_version_ready(inst["version"])
        inst["env_ready"] = _is_instance_env_ready(inst["id"])
    else:
        # Remote instances: no pid tracking, always show as "remote"
        inst["running"] = False
        inst["status"] = "remote"
        inst["version_ready"] = True
        inst["env_ready"] = True

    inst["last_error"] = inst.get("last_error", "")
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    inst["api_key_ready"] = bool(_parse_env_file(env_path).get("ODOO_API_KEY"))
    with _apikey_lock:
        ak = _apikey_state.get(inst["id"], {})
    inst["api_key_status"] = ak.get("status", "unknown")
    inst["api_key_message"] = ak.get("message", "")
    return inst


def _parse_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def _write_env_file(path: Path, data: dict[str, str]) -> None:
    path.write_text("\n".join(f"{k}={v}" for k, v in data.items()) + "\n")


# ---------------------------------------------------------------------------
# Version-setup helpers (git clone — version-scoped)
# ---------------------------------------------------------------------------

# In-memory store:  version -> {"status": "cloning"|"done"|"error", "log": [...]}
_clone_state: dict[str, dict] = {}
_clone_lock = threading.Lock()

CONDA_BASE = Path(
    subprocess.check_output(
        ["/Users/josemonsalvediaz/miniconda3/bin/conda", "info", "--base"],
        text=True,
    ).strip()
)
CONDA_BIN = CONDA_BASE / "bin" / "conda"

_ODOO_PYTHON_VERSION: dict[int, str] = {
    14: "3.8",
    15: "3.8",
    16: "3.10",
    17: "3.11",
    18: "3.11",
    19: "3.11",
}
_DEFAULT_PYTHON = "3.11"


def _python_for_version(version: str) -> str:
    try:
        major = int(version.split(".")[0])
        return _ODOO_PYTHON_VERSION.get(major, _DEFAULT_PYTHON)
    except (ValueError, IndexError):
        return _DEFAULT_PYTHON


def _version_log_path(version: str) -> Path:
    return WORKSPACE_ROOT / version / ".clone.log"


def _version_state_path(version: str) -> Path:
    return WORKSPACE_ROOT / version / ".clone.state"


def _odoo_bin_path(version: str) -> Path:
    return WORKSPACE_ROOT / version / "odoo" / "odoo-bin"


def _is_version_ready(version: str) -> bool:
    return _odoo_bin_path(version).exists()


# ---------------------------------------------------------------------------
# Instance-env helpers (conda env — instance-scoped)
# ---------------------------------------------------------------------------

# In-memory store:  instance_id -> {"status": "installing"|"done"|"error", "log": [...]}
_env_state: dict[str, dict] = {}
_env_lock = threading.Lock()


def _instance_env_name(instance_id: str) -> str:
    return f"odoo-{instance_id}"


def _instance_env_python(instance_id: str) -> Path:
    return CONDA_BASE / "envs" / _instance_env_name(instance_id) / "bin" / "python"


def _is_instance_env_ready(instance_id: str) -> bool:
    return _instance_env_python(instance_id).exists()


def _instance_env_log_path(inst: dict) -> Path:
    return WORKSPACE_ROOT / inst["path"] / ".env_setup.log"


def _instance_env_state_path(inst: dict) -> Path:
    return WORKSPACE_ROOT / inst["path"] / ".env_setup.state"


def _persist_env_state(instance_id: str, inst: dict) -> None:
    with _env_lock:
        state = _env_state.get(instance_id, {})
    sp = _instance_env_state_path(inst)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps({
        "status": state.get("status", "unknown"),
        "last_line": state["log"][-1] if state.get("log") else "",
    }))


def _restore_env_states() -> None:
    reg = load_registry()
    for inst in reg.get("instances", []):
        sf = _instance_env_state_path(inst)
        if not sf.exists():
            continue
        try:
            saved = json.loads(sf.read_text())
        except Exception:
            continue
        log_lines = []
        lp = _instance_env_log_path(inst)
        if lp.exists():
            log_lines = lp.read_text().splitlines()
        status = saved.get("status", "unknown")
        if status == "installing":
            status = "done" if _is_instance_env_ready(inst["id"]) else "error"
            saved["status"] = status
            sf.write_text(json.dumps(saved))
        with _env_lock:
            _env_state[inst["id"]] = {"status": status, "log": log_lines}


def _setup_instance_env_sync(instance_id: str, inst: dict) -> None:
    """Create a per-instance conda env and install Odoo requirements."""
    version = inst["version"]
    log_path = _instance_env_log_path(inst)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("")

    env_name = _instance_env_name(instance_id)
    py_ver = _python_for_version(version)
    req_file = WORKSPACE_ROOT / version / "odoo" / "requirements.txt"

    with _env_lock:
        _env_state[instance_id] = {"status": "installing", "log": []}
    _persist_env_state(instance_id, inst)

    def _append(line: str) -> None:
        with _env_lock:
            _env_state[instance_id]["log"].append(line)
        with open(log_path, "a") as f:
            f.write(line + "\n")
        _persist_env_state(instance_id, inst)

    try:
        if _is_instance_env_ready(instance_id):
            _append(f"[info] conda env '{env_name}' already exists — skipping")
        else:
            _append(f"[info] Creating conda env '{env_name}' (Python {py_ver}) via conda-forge …")
            proc = subprocess.Popen(
                [str(CONDA_BIN), "create", "-n", env_name,
                 f"python={py_ver}", "-c", "conda-forge", "--yes", "--quiet"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            for line in proc.stdout:
                if line.strip():
                    _append(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"conda create failed (exit {proc.returncode})")
            _append(f"[info] conda env '{env_name}' created.")

        if req_file.exists():
            _append("[info] Installing Odoo requirements …")
            pip = CONDA_BASE / "envs" / env_name / "bin" / "pip"
            proc2 = subprocess.Popen(
                [str(pip), "install", "-r", str(req_file), "--quiet"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            for line in proc2.stdout:
                if line.strip():
                    _append(line.rstrip())
            proc2.wait()
            if proc2.returncode != 0:
                raise RuntimeError(f"pip install failed (exit {proc2.returncode})")
            _append("[info] Requirements installed.")

        _append("[info] Environment ready.")
        with _env_lock:
            _env_state[instance_id]["status"] = "done"
        _persist_env_state(instance_id, inst)

    except Exception as exc:
        _append(f"[error] {exc}")
        with _env_lock:
            _env_state[instance_id]["status"] = "error"
        _persist_env_state(instance_id, inst)


def _persist_clone_state(version: str) -> None:
    """Write current state to disk so it survives server restarts."""
    with _clone_lock:
        state = _clone_state.get(version, {})
    state_path = _version_state_path(version)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({
        "status": state.get("status", "unknown"),
        "last_line": state["log"][-1] if state.get("log") else "",
    }))


def _restore_clone_states() -> None:
    """On startup, reconstruct _clone_state from .clone.state + .clone.log files."""
    for state_file in WORKSPACE_ROOT.glob("*/.clone.state"):
        version = state_file.parent.name
        try:
            saved = json.loads(state_file.read_text())
        except Exception:
            continue
        log_path = _version_log_path(version)
        log_lines = log_path.read_text().splitlines() if log_path.exists() else []
        status = saved.get("status", "unknown")
        # If mid-flight when server died, resolve from actual disk state
        if status == "cloning":
            status = "done" if _is_version_ready(version) else "error"
            saved["status"] = status
            state_file.write_text(json.dumps(saved))
        with _clone_lock:
            _clone_state[version] = {"status": status, "log": log_lines}


def _clone_version_sync(version: str) -> None:
    """Run git clone in a background thread; stream output to a log file."""
    log_path = _version_log_path(version)
    version_dir = WORKSPACE_ROOT / version
    version_dir.mkdir(parents=True, exist_ok=True)
    odoo_dir = version_dir / "odoo"

    with _clone_lock:
        _clone_state[version] = {"status": "cloning", "log": []}
    _persist_clone_state(version)

    def _append(line: str) -> None:
        with _clone_lock:
            _clone_state[version]["log"].append(line)
        with open(log_path, "a") as f:
            f.write(line + "\n")
        _persist_clone_state(version)

    def _run_clone(repo_url: str, target_dir: Path, label: str) -> None:
        """Clone a single repo with progress streaming."""
        if target_dir.exists() and any(target_dir.iterdir()):
            _append(f"[info] {label} already present — skipping clone")
            return
        _append(f"[info] Cloning {label}@{version} …")
        cmd = [
            "git", "clone", "--depth", "1", "--branch", version,
            repo_url, str(target_dir),
        ]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        buf = ""
        for chunk in iter(lambda: proc.stdout.read(256), ""):
            buf += chunk
            # git uses \r for progress — split on both \r and \n
            parts = buf.replace("\r", "\n").split("\n")
            buf = parts[-1]
            for part in parts[:-1]:
                if part.strip():
                    _append(part.strip())
        if buf.strip():
            _append(buf.strip())
        proc.wait()
        if proc.returncode != 0:
            # Clean up partial clone so a retry starts fresh
            if target_dir.exists():
                shutil.rmtree(target_dir)
            raise RuntimeError(
                f"git clone {label} failed (exit {proc.returncode}). "
                f"Partial directory removed. Use the Clone button to retry."
            )
        _append(f"[info] {label} clone complete.")

    try:
        _run_clone("https://github.com/odoo/odoo.git", odoo_dir, "odoo/odoo")
        _run_clone(
            "https://github.com/odoo/enterprise.git",
            version_dir / "enterprise", "odoo/enterprise",
        )
        _run_clone(
            "https://github.com/odoo/design-themes.git",
            version_dir / "design-themes", "odoo/design-themes",
        )

        with _clone_lock:
            _clone_state[version]["status"] = "done"
        _persist_clone_state(version)

    except Exception as exc:
        _append(f"[error] {exc}")
        with _clone_lock:
            _clone_state[version]["status"] = "error"
        _persist_clone_state(version)


# ---------------------------------------------------------------------------
# API-key helpers (auto-generate after instance start)
# ---------------------------------------------------------------------------

_apikey_state: dict[str, dict] = {}
_apikey_lock = threading.Lock()


def _apikey_state_path(inst: dict) -> Path:
    return WORKSPACE_ROOT / inst["path"] / ".apikey.state"


def _persist_apikey_state(instance_id: str, inst: dict) -> None:
    with _apikey_lock:
        state = _apikey_state.get(instance_id, {})
    sp = _apikey_state_path(inst)
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps({
        "status": state.get("status", "unknown"),
        "message": state.get("message", ""),
    }))


def _restore_apikey_states() -> None:
    reg = load_registry()
    for inst in reg.get("instances", []):
        sf = _apikey_state_path(inst)
        if not sf.exists():
            continue
        try:
            saved = json.loads(sf.read_text())
        except Exception:
            continue
        status = saved.get("status", "unknown")
        if status == "generating":
            env_path = WORKSPACE_ROOT / inst["path"] / ".env"
            has_key = bool(_parse_env_file(env_path).get("ODOO_API_KEY"))
            status = "ready" if has_key else "error"
            saved["status"] = status
            sf.write_text(json.dumps(saved))
        with _apikey_lock:
            _apikey_state[inst["id"]] = {
                "status": status,
                "message": saved.get("message", ""),
            }


def _generate_api_key_sync(instance_id: str, inst: dict) -> None:
    """Wait for Odoo to be responsive, then generate an API key via odoo-bin shell."""
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    version = inst["version"]
    db = inst["db"]
    conf = WORKSPACE_ROOT / inst["path"] / "odoo.conf"
    odoo_bin = _odoo_bin_path(version)
    conda_python = _instance_env_python(instance_id)

    # Check if key already exists
    existing = _parse_env_file(env_path).get("ODOO_API_KEY", "")
    if existing:
        with _apikey_lock:
            _apikey_state[instance_id] = {"status": "ready", "message": "Key already present"}
        _persist_apikey_state(instance_id, inst)
        return

    with _apikey_lock:
        _apikey_state[instance_id] = {"status": "generating", "message": "Waiting for Odoo…"}
    _persist_apikey_state(instance_id, inst)

    try:
        # Poll until Odoo is responsive (up to 120s)
        url = f"http://localhost:{inst['port']}"
        responsive = False
        for _ in range(60):
            try:
                proxy = xmlrpc.client.ServerProxy(
                    f"{url}/xmlrpc/2/common", allow_none=True
                )
                proxy.version()
                responsive = True
                break
            except Exception:
                time.sleep(2)
        if not responsive:
            raise RuntimeError("Odoo did not become responsive within 120 seconds")

        with _apikey_lock:
            _apikey_state[instance_id]["message"] = "Generating API key…"
        _persist_apikey_state(instance_id, inst)

        # Generate API key via odoo-bin shell.
        # Odoo 19 added a required expiration_date argument to _generate().
        # Try new signature (False = no expiration) and fall back to old one.
        shell_script = (
            "user = env['res.users'].browse(2)\n"
            "user.password = 'admin'\n"
            "try:\n"
            "    key = env['res.users.apikeys']._generate('odoo-demo-creator', user.id, False)\n"
            "except TypeError:\n"
            "    key = env['res.users.apikeys']._generate('odoo-demo-creator', user.id)\n"
            "print(f'API_KEY={key}')\n"
            "env.cr.commit()\n"
        )
        result = subprocess.run(
            [str(conda_python), str(odoo_bin), "shell",
             "-d", db, "-c", str(conf), "--no-http"],
            input=shell_script,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Parse API_KEY= from stdout
        api_key = ""
        for line in result.stdout.splitlines():
            if line.startswith("API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break

        if not api_key:
            stderr_tail = result.stderr[-500:] if result.stderr else ""
            stdout_tail = result.stdout[-500:] if result.stdout else ""
            raise RuntimeError(
                f"Could not extract API key from shell output.\n"
                f"stdout: {stdout_tail}\nstderr: {stderr_tail}"
            )

        # Write key to .env
        env_data = _parse_env_file(env_path)
        env_data["ODOO_API_KEY"] = api_key
        _write_env_file(env_path, env_data)

        with _apikey_lock:
            _apikey_state[instance_id] = {"status": "ready", "message": "API key generated"}
        _persist_apikey_state(instance_id, inst)

    except Exception as exc:
        with _apikey_lock:
            _apikey_state[instance_id] = {"status": "error", "message": str(exc)}
        _persist_apikey_state(instance_id, inst)


# Restore state from disk on module load (survives hot-reloads)
_restore_clone_states()
_restore_env_states()
_restore_apikey_states()


# ---------------------------------------------------------------------------
# Routes — meta / utility
# ---------------------------------------------------------------------------

_VERSION_RE = re.compile(r"^\d+\.\d+$")


@app.get("/api/odoo-versions")
async def odoo_versions():
    """Return Odoo version branches from github.com/odoo/odoo, sorted descending."""
    url = "https://api.github.com/repos/odoo/odoo/branches?per_page=100"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            branches = [b["name"] for b in resp.json()]
    except Exception as exc:
        # Fallback to a static list so the UI never breaks
        branches = ["18.0", "17.0", "16.0", "15.0", "14.0"]
        return JSONResponse({"versions": branches, "source": "fallback", "error": str(exc)})

    versions = sorted(
        [b for b in branches if _VERSION_RE.match(b)],
        key=lambda v: float(v),
        reverse=True,
    )
    return JSONResponse({"versions": versions, "source": "github"})


@app.post("/versions/{version}/clone")
async def clone_version(version: str):
    """Kick off a background git clone for the given Odoo version."""
    if _is_version_ready(version):
        return {"status": "already_ready", "version": version}

    with _clone_lock:
        state = _clone_state.get(version, {})
        if state.get("status") == "cloning":
            return {"status": "already_cloning", "version": version}

    # Wipe any previous log
    log_path = _version_log_path(version)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("")

    t = threading.Thread(target=_clone_version_sync, args=(version,), daemon=True)
    t.start()
    return {"status": "started", "version": version}


@app.get("/versions/{version}/clone-status")
async def clone_status_sse(version: str):
    """SSE stream that tails the clone log until done or error.

    Reads from the log file on disk so it survives server hot-reloads.
    """

    async def generate():
        log_path = _version_log_path(version)
        sent = 0
        while True:
            # Prefer in-memory (faster), fall back to disk
            with _clone_lock:
                state = _clone_state.get(version, {})
                lines = list(state.get("log", []))
                status = state.get("status", "cloning")

            # If in-memory is empty but log file exists, read from disk
            if not lines and log_path.exists():
                lines = log_path.read_text().splitlines()
                state_path = _version_state_path(version)
                if state_path.exists():
                    try:
                        status = json.loads(state_path.read_text()).get("status", "cloning")
                    except Exception:
                        pass

            for line in lines[sent:]:
                yield f"data: {line}\n\n"
            sent = len(lines)

            if status in ("done", "error"):
                yield f"data: [status] {status}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/versions/{version}/ready")
async def version_ready(version: str):
    return {"ready": _is_version_ready(version), "version": version}


@app.post("/instances/{instance_id}/setup-env")
async def setup_env(instance_id: str):
    """Trigger conda env creation for an instance (idempotent)."""
    inst = get_instance(instance_id)
    if _is_instance_env_ready(instance_id):
        return {"status": "already_ready", "instance_id": instance_id}
    with _env_lock:
        if _env_state.get(instance_id, {}).get("status") == "installing":
            return {"status": "already_installing", "instance_id": instance_id}
    t = threading.Thread(
        target=_setup_instance_env_sync, args=(instance_id, inst), daemon=True
    )
    t.start()
    return {"status": "started", "instance_id": instance_id}


@app.get("/instances/{instance_id}/env-status")
async def instance_env_status_sse(instance_id: str):
    """SSE stream of conda env setup progress for an instance."""
    inst = get_instance(instance_id)

    async def generate():
        log_path = _instance_env_log_path(inst)
        sent = 0
        while True:
            with _env_lock:
                state = _env_state.get(instance_id, {})
                lines = list(state.get("log", []))
                status = state.get("status", "installing")

            if not lines and log_path.exists():
                lines = log_path.read_text().splitlines()
                sp = _instance_env_state_path(inst)
                if sp.exists():
                    try:
                        status = json.loads(sp.read_text()).get("status", "installing")
                    except Exception:
                        pass

            for line in lines[sent:]:
                yield f"data: {line}\n\n"
            sent = len(lines)

            if status in ("done", "error"):
                yield f"data: [status] {status}\n\n"
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/instances/{instance_id}/env-ready")
async def instance_env_ready(instance_id: str):
    return {"ready": _is_instance_env_ready(instance_id), "instance_id": instance_id}


@app.get("/instances/envs/installing")
async def instances_installing():
    """Return all instances currently installing their conda env."""
    with _env_lock:
        snapshot = {
            iid: {"status": s["status"], "last_line": s["log"][-1] if s["log"] else ""}
            for iid, s in _env_state.items()
        }
    return JSONResponse(snapshot)


@app.post("/instances/{instance_id}/generate-apikey")
async def generate_apikey(instance_id: str):
    """Trigger API key generation for an instance (idempotent)."""
    inst = get_instance(instance_id)
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    if _parse_env_file(env_path).get("ODOO_API_KEY"):
        return {"status": "already_ready", "instance_id": instance_id}
    with _apikey_lock:
        if _apikey_state.get(instance_id, {}).get("status") == "generating":
            return {"status": "already_generating", "instance_id": instance_id}
    t = threading.Thread(
        target=_generate_api_key_sync, args=(instance_id, inst), daemon=True
    )
    t.start()
    return {"status": "started", "instance_id": instance_id}


@app.get("/instances/{instance_id}/apikey-value")
async def apikey_value(instance_id: str):
    """Return the raw API key value for display in the UI."""
    inst = get_instance(instance_id)
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    key = _parse_env_file(env_path).get("ODOO_API_KEY", "")
    return {"key": key}


@app.get("/instances/{instance_id}/apikey-status")
async def apikey_status(instance_id: str):
    """Return current API key generation status."""
    inst = get_instance(instance_id)
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    has_key = bool(_parse_env_file(env_path).get("ODOO_API_KEY"))
    with _apikey_lock:
        state = _apikey_state.get(instance_id, {})
    return {
        "status": state.get("status", "unknown"),
        "message": state.get("message", ""),
        "has_key": has_key,
    }


@app.get("/versions/cloning")
async def versions_cloning():
    """Return all versions that are currently cloning or recently finished/errored."""
    with _clone_lock:
        snapshot = {
            v: {
                "status": s["status"],
                "last_line": s["log"][-1] if s["log"] else "",
            }
            for v, s in _clone_state.items()
        }
    return JSONResponse(snapshot)


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    reg = load_registry()
    instances = [_enrich(i) for i in reg["instances"]]
    return templates.TemplateResponse(
        "index.html", {"request": request, "instances": instances}
    )


@app.get("/instance/{instance_id}", response_class=HTMLResponse)
async def instance_detail(request: Request, instance_id: str):
    inst = _enrich(get_instance(instance_id))
    return templates.TemplateResponse(
        "instance.html", {"request": request, "inst": inst}
    )


# ---------------------------------------------------------------------------
# Routes — instance CRUD
# ---------------------------------------------------------------------------


@app.post("/instances/create", response_class=HTMLResponse)
async def create_instance(
    request: Request,
    client: str = Form(...),
    version: str = Form(...),
    db_name: str = Form(...),
    base: str = Form("fresh"),
    sql_path: Optional[str] = Form(None),
    zip_upload: Optional[UploadFile] = File(None),
    source_instance: Optional[str] = Form(None),
):
    reg = load_registry()
    instance_id = f"{client}-{version.replace('.', '')}"

    if any(i["id"] == instance_id for i in reg["instances"]):
        raise HTTPException(status_code=400, detail=f"Instance '{instance_id}' already exists")

    port = next_port(reg)
    instance_path = WORKSPACE_ROOT / version / "clients" / client

    if instance_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Folder already exists: odoo-workspace/{version}/clients/{client}",
        )

    # Create folder structure
    (instance_path / "addons").mkdir(parents=True, exist_ok=True)
    (instance_path / "data").mkdir(parents=True, exist_ok=True)

    # Write .env
    env_content = (
        f"ODOO_URL=http://localhost:{port}\n"
        f"ODOO_DB={db_name}\n"
        f"ODOO_USER=admin\n"
        f"ODOO_API_KEY=\n"
        f"ODOO_VERSION={version}\n"
        f"CLIENT={client}\n"
    )
    (instance_path / ".env").write_text(env_content)

    # Write odoo.conf
    odoo_conf = (
        f"[options]\n"
        f"addons_path = {WORKSPACE_ROOT / version / 'odoo' / 'addons'},"
        f"{WORKSPACE_ROOT / version / 'enterprise'},"
        f"{WORKSPACE_ROOT / version / 'design-themes'},"
        f"{instance_path / 'addons'}\n"
        f"db_host = localhost\n"
        f"db_port = 5432\n"
        f"db_user = {DB_USER}\n"
        f"db_password = {DB_PASSWORD}\n"
        f"db_name = {db_name}\n"
        f"http_port = {port}\n"
        f"logfile = {instance_path / 'odoo.log'}\n"
        f"data_dir = {instance_path / 'data'}\n"
    )
    (instance_path / "odoo.conf").write_text(odoo_conf)

    # Ensure the PostgreSQL role exists before any DB operations
    _ensure_pg_role()

    # Auto-clone Odoo source for this version if not present
    if not _is_version_ready(version):
        with _clone_lock:
            already = _clone_state.get(version, {}).get("status") == "cloning"
        if not already:
            log_path = _version_log_path(version)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("")
            t = threading.Thread(target=_clone_version_sync, args=(version,), daemon=True)
            t.start()

    # Copy templates if they don't exist
    for tmpl in ("client.template.md", "demo.template.md"):
        src = BASE_DIR.parent / "templates" / tmpl
        dst = instance_path / tmpl.replace(".template", "")
        if src.exists() and not dst.exists():
            dst.write_text(src.read_text())

    # Database initialisation based on 'base' choice
    if base == "sql":
        if not sql_path or not Path(sql_path).exists():
            raise HTTPException(status_code=400, detail=f"sql_path not found: {sql_path!r}")
        subprocess.run(["createdb", db_name], check=True)
        result = subprocess.run(
            ["psql", "-d", db_name, "-f", sql_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

    elif base == "zip":
        if not zip_upload:
            raise HTTPException(status_code=400, detail="No zip file uploaded")
        filestore_dest = instance_path / "data" / "filestore" / db_name
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tmp_zip = tmp_path / (zip_upload.filename or "backup.zip")
            tmp_zip.write_bytes(await zip_upload.read())
            with zipfile.ZipFile(tmp_zip) as zf:
                if "dump.sql" not in zf.namelist():
                    raise HTTPException(
                        status_code=400,
                        detail="ZIP does not contain dump.sql — is this an Odoo backup?",
                    )
                zf.extractall(tmp_path)
            subprocess.run(["createdb", db_name], check=True)
            result = subprocess.run(
                ["psql", "-d", db_name, "-f", str(tmp_path / "dump.sql")],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=result.stderr[:2000])
            extracted_filestore = tmp_path / "filestore"
            if extracted_filestore.is_dir():
                if filestore_dest.exists():
                    shutil.rmtree(filestore_dest)
                filestore_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(extracted_filestore, filestore_dest)

    elif base == "clone":
        src_inst = next(
            (i for i in reg["instances"] if i["id"] == source_instance), None
        )
        if not src_inst:
            raise HTTPException(
                status_code=400, detail=f"Source instance '{source_instance}' not found"
            )
        src_db = src_inst["db"]
        subprocess.run(["createdb", db_name], check=True)
        dump = subprocess.Popen(
            ["pg_dump", src_db], stdout=subprocess.PIPE
        )
        restore = subprocess.Popen(
            ["psql", db_name], stdin=dump.stdout
        )
        dump.stdout.close()
        restore.communicate()

    # else base == "fresh": no DB created here — odoo-bin --init will handle it

    entry = {
        "id": instance_id,
        "client": client,
        "version": version,
        "port": port,
        "db": db_name,
        "status": "stopped",
        "path": str(Path(version) / "clients" / client),
        "base": base,
    }
    reg["instances"].append(entry)
    save_registry(reg)

    # Update symlink to active .env
    active_env = WORKSPACE_ROOT / ".env"
    if active_env.is_symlink():
        active_env.unlink()
    active_env.symlink_to(instance_path / ".env")

    # Auto-setup conda env for this instance
    if not _is_instance_env_ready(instance_id):
        with _env_lock:
            already = _env_state.get(instance_id, {}).get("status") == "installing"
        if not already:
            t = threading.Thread(
                target=_setup_instance_env_sync, args=(instance_id, entry), daemon=True
            )
            t.start()

    instances = [_enrich(i) for i in reg["instances"]]
    return templates.TemplateResponse(
        "partials/instance_list.html", {"request": request, "instances": instances}
    )


@app.delete("/instances/{instance_id}", response_class=HTMLResponse)
async def delete_instance(request: Request, instance_id: str):
    reg = load_registry()
    reg["instances"] = [i for i in reg["instances"] if i["id"] != instance_id]
    save_registry(reg)
    instances = [_enrich(i) for i in reg["instances"]]
    return templates.TemplateResponse(
        "partials/instance_list.html", {"request": request, "instances": instances}
    )


# ---------------------------------------------------------------------------
# Routes — process control
#   start/stop accept ?view=detail to return the controls partial instead of
#   the list-row partial (used from the instance detail page).
# ---------------------------------------------------------------------------


@app.post("/instances/{instance_id}/start", response_class=HTMLResponse)
async def start_instance(request: Request, instance_id: str, view: str = "list"):
    inst = get_instance(instance_id)
    if _is_running(instance_id):
        raise HTTPException(status_code=400, detail="Already running")

    instance_path = WORKSPACE_ROOT / inst["path"]
    version = inst["version"]
    odoo_bin = WORKSPACE_ROOT / version / "odoo" / "odoo-bin"

    if not odoo_bin.exists():
        with _clone_lock:
            already = _clone_state.get(version, {}).get("status") == "cloning"
        if not already:
            log_path = _version_log_path(version)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("")
            t = threading.Thread(target=_clone_version_sync, args=(version,), daemon=True)
            t.start()
        raise HTTPException(
            status_code=400,
            detail=f"Odoo {version} source not ready — clone started, watch /versions/{version}/clone-status",
        )

    if not _is_instance_env_ready(instance_id):
        with _env_lock:
            already = _env_state.get(instance_id, {}).get("status") == "installing"
        if not already:
            t = threading.Thread(
                target=_setup_instance_env_sync, args=(instance_id, inst), daemon=True
            )
            t.start()
        raise HTTPException(
            status_code=400,
            detail=f"conda env not ready — setup started, watch /instances/{instance_id}/env-status",
        )

    log_file = instance_path / "odoo.log"
    conf = instance_path / "odoo.conf"

    conda_python = _instance_env_python(instance_id)
    # Odoo 19+ has no __init__.py — the source root must be on PYTHONPATH
    env = {**os.environ, "PYTHONPATH": str(odoo_bin.parent)}
    proc = subprocess.Popen(
        [str(conda_python), str(odoo_bin), "-c", str(conf)],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=env,
    )

    # Wait briefly to catch immediate startup failures (import errors, bad config, etc.)
    await asyncio.sleep(2)
    if proc.poll() is not None:
        # Process already exited — record error state and surface log tail
        _pid_file(instance_id).unlink(missing_ok=True)
        tail = ""
        if log_file.exists():
            lines = log_file.read_text().splitlines()
            tail = "\n".join(lines[-10:])
        error_msg = f"Process exited (code {proc.returncode}):\n{tail}"
        reg = load_registry()
        for i in reg["instances"]:
            if i["id"] == instance_id:
                i["status"] = "error"
                i["last_error"] = error_msg
        save_registry(reg)
        inst = _enrich(get_instance(instance_id))
        partial = "partials/instance_controls.html" if view == "detail" else "partials/instance_row.html"
        return templates.TemplateResponse(partial, {"request": request, "inst": inst}, status_code=200)

    _pid_file(instance_id).write_text(str(proc.pid))

    reg = load_registry()
    for i in reg["instances"]:
        if i["id"] == instance_id:
            i["status"] = "running"
            i.pop("last_error", None)
    save_registry(reg)

    # Auto-generate API key if not already present
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    if not _parse_env_file(env_path).get("ODOO_API_KEY"):
        with _apikey_lock:
            already = _apikey_state.get(instance_id, {}).get("status") == "generating"
        if not already:
            t = threading.Thread(
                target=_generate_api_key_sync, args=(instance_id, inst), daemon=True
            )
            t.start()

    inst = _enrich(get_instance(instance_id))
    partial = "partials/instance_controls.html" if view == "detail" else "partials/instance_row.html"
    return templates.TemplateResponse(partial, {"request": request, "inst": inst})


@app.post("/instances/{instance_id}/stop", response_class=HTMLResponse)
async def stop_instance(request: Request, instance_id: str, view: str = "list"):
    pid_file = _pid_file(instance_id)
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
        except (ProcessLookupError, ValueError):
            pass
        pid_file.unlink(missing_ok=True)

    reg = load_registry()
    for i in reg["instances"]:
        if i["id"] == instance_id:
            i["status"] = "stopped"
            i.pop("last_error", None)
    save_registry(reg)

    inst = _enrich(get_instance(instance_id))
    partial = "partials/instance_controls.html" if view == "detail" else "partials/instance_row.html"
    return templates.TemplateResponse(partial, {"request": request, "inst": inst})


# ---------------------------------------------------------------------------
# Routes — .env editor
# ---------------------------------------------------------------------------


@app.get("/instances/{instance_id}/env", response_class=HTMLResponse)
async def get_env(request: Request, instance_id: str):
    inst = get_instance(instance_id)
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    env_data = _parse_env_file(env_path)
    return templates.TemplateResponse(
        "partials/env_editor.html",
        {"request": request, "instance_id": instance_id, "env_data": env_data},
    )


@app.post("/instances/{instance_id}/env", response_class=HTMLResponse)
async def save_env(request: Request, instance_id: str):
    inst = get_instance(instance_id)
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"

    form = await request.form()
    # form keys are env var names; values are their new values
    new_data = {k: v for k, v in form.items() if k and not k.startswith("_")}
    _write_env_file(env_path, new_data)

    return templates.TemplateResponse(
        "partials/env_editor.html",
        {"request": request, "instance_id": instance_id, "env_data": new_data, "saved": True},
    )


# ---------------------------------------------------------------------------
# Routes — logs
# ---------------------------------------------------------------------------


@app.get("/instances/{instance_id}/logs")
async def get_logs(instance_id: str, lines: int = 100):
    inst = get_instance(instance_id)
    log_path = WORKSPACE_ROOT / inst["path"] / "odoo.log"

    if not log_path.exists():
        return JSONResponse({"lines": []})

    all_lines = log_path.read_text().splitlines()
    return JSONResponse({"lines": all_lines[-lines:]})


@app.get("/instances/{instance_id}/logs/stream")
async def stream_logs_sse(instance_id: str):
    """Server-sent events stream for live log tailing (non-blocking)."""
    inst = get_instance(instance_id)
    log_path = WORKSPACE_ROOT / inst["path"] / "odoo.log"

    async def generate():
        async with aiofiles.open(log_path, "r") as f:
            await f.seek(0, 2)  # seek to end
            while True:
                line = await f.readline()
                if line:
                    yield f"data: {line.rstrip()}\n\n"
                else:
                    await asyncio.sleep(0.3)

    return StreamingResponse(generate(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Routes — module upload
# ---------------------------------------------------------------------------


@app.post("/instances/{instance_id}/upload-module")
async def upload_module_github(
    instance_id: str,
    github_url: str = Form(...),
):
    """Clone a module from a GitHub URL into the instance's addons folder."""
    inst = get_instance(instance_id)
    addons_path = WORKSPACE_ROOT / inst["path"] / "addons"

    result = subprocess.run(
        ["git", "clone", github_url],
        cwd=addons_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    return {"status": "ok", "message": f"Cloned {github_url} into {addons_path}"}


@app.post("/instances/{instance_id}/upload-module-zip")
async def upload_module_zip(
    instance_id: str,
    zip_file: UploadFile = File(...),
):
    """Unzip a module archive into the instance's addons folder."""
    inst = get_instance(instance_id)
    addons_path = WORKSPACE_ROOT / inst["path"] / "addons"

    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_zip = Path(tmp) / zip_file.filename
        content = await zip_file.read()
        tmp_zip.write_bytes(content)

        with zipfile.ZipFile(tmp_zip) as zf:
            # Validate: at least one __manifest__.py must exist
            names = zf.namelist()
            if not any("__manifest__.py" in n for n in names):
                raise HTTPException(
                    status_code=400,
                    detail="zip does not appear to contain an Odoo module (__manifest__.py not found)",
                )
            zf.extractall(tmp)

        # Move extracted dirs (skip __MACOSX etc.) into addons/
        for item in Path(tmp).iterdir():
            if item.is_dir() and item.name != "__MACOSX":
                dest = addons_path / item.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)

    return {"status": "ok", "message": f"Module installed into {addons_path}"}


# ---------------------------------------------------------------------------
# Routes — snapshot / restore
# ---------------------------------------------------------------------------


@app.post("/instances/{instance_id}/snapshot")
async def snapshot(instance_id: str):
    inst = get_instance(instance_id)
    db = inst["db"]
    instance_path = WORKSPACE_ROOT / inst["path"]
    dump_path = instance_path / "data" / f"{db}_snapshot.sql"

    result = subprocess.run(
        ["pg_dump", "-F", "p", "-f", str(dump_path), db],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    return {"status": "ok", "path": str(dump_path)}


@app.get("/instances/{instance_id}/snapshot/download")
async def snapshot_download(instance_id: str):
    """Stream a pg_dump of the instance database directly as a file download."""
    inst = get_instance(instance_id)
    db = inst["db"]
    filename = f"{db}_snapshot.sql"

    async def _stream():
        proc = await asyncio.create_subprocess_exec(
            "pg_dump", "-F", "p", db,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert proc.stdout is not None
        while True:
            chunk = await proc.stdout.read(65536)
            if not chunk:
                break
            yield chunk
        await proc.wait()

    return StreamingResponse(
        _stream(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/instances/{instance_id}/restore")
async def restore(instance_id: str, sql_path: str = Form(...)):
    inst = get_instance(instance_id)
    db = inst["db"]

    if not Path(sql_path).exists():
        raise HTTPException(status_code=400, detail=f"File not found: {sql_path}")

    subprocess.run(["dropdb", "--if-exists", db], check=False)
    subprocess.run(["createdb", db], check=True)

    result = subprocess.run(
        ["psql", "-d", db, "-f", sql_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    return {"status": "ok"}


@app.post("/instances/{instance_id}/restore-zip")
async def restore_zip(
    instance_id: str,
    zip_file: UploadFile = File(...),
):
    """Restore from an Odoo backup ZIP (dump.sql + filestore/).

    Expected ZIP layout (standard Odoo backup format):
        dump.sql
        filestore/<hash>/...
    """
    inst = get_instance(instance_id)
    db = inst["db"]
    instance_path = WORKSPACE_ROOT / inst["path"]
    filestore_dest = instance_path / "data" / "filestore" / db

    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .zip archive")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tmp_zip = tmp_path / zip_file.filename
        tmp_zip.write_bytes(await zip_file.read())

        with zipfile.ZipFile(tmp_zip) as zf:
            names = zf.namelist()
            if "dump.sql" not in names:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP does not contain dump.sql — is this an Odoo backup?",
                )
            zf.extractall(tmp_path)

        # Restore database
        dump_sql = tmp_path / "dump.sql"
        subprocess.run(["dropdb", "--if-exists", db], check=False)
        subprocess.run(["createdb", db], check=True)
        result = subprocess.run(
            ["psql", "-d", db, "-f", str(dump_sql)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr[:2000])

        # Restore filestore
        extracted_filestore = tmp_path / "filestore"
        if extracted_filestore.is_dir():
            if filestore_dest.exists():
                shutil.rmtree(filestore_dest)
            filestore_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(extracted_filestore, filestore_dest)

    return {"status": "ok", "db": db, "filestore": str(filestore_dest)}


# ---------------------------------------------------------------------------
# Routes — user management (connect-as / change-password)
# ---------------------------------------------------------------------------

import html as _html


def _rpc_execute(inst: dict, model: str, method: str, args: list, kw: dict | None = None):
    """Call Odoo XML-RPC using the instance API key."""
    env_path = WORKSPACE_ROOT / inst["path"] / ".env"
    env_data = _parse_env_file(env_path)
    api_key = env_data.get("ODOO_API_KEY", "")
    odoo_user = env_data.get("ODOO_USER", "admin")
    db = inst["db"]
    url = inst.get("url") or f"http://localhost:{inst['port']}"

    if not api_key:
        raise HTTPException(status_code=400, detail="No API key — generate one first from the instance detail page")

    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, odoo_user, api_key, {})
        if not uid:
            raise HTTPException(status_code=401, detail="Odoo authentication failed — check API key")
        models_proxy = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
        return models_proxy.execute_kw(db, uid, api_key, model, method, args, kw or {})
    except xmlrpc.client.Fault as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot reach instance: {e}")


def _set_password_via_shell(inst: dict, user_id: int, password: str) -> str:
    """Set a user's password using odoo-bin shell. Returns the user's login."""
    instance_id = inst["id"]
    conf_path = WORKSPACE_ROOT / inst["path"] / "odoo.conf"
    odoo_bin = _odoo_bin_path(inst["version"])
    conda_python = _instance_env_python(instance_id)
    db = inst["db"]

    shell_script = (
        f"user = env['res.users'].browse({int(user_id)})\n"
        f"login = user.login\n"
        f"user.write({{'password': {repr(password)}}})\n"
        f"env.cr.commit()\n"
        f"print(f'LOGIN={{login}}')\n"
    )

    result = subprocess.run(
        [str(conda_python), str(odoo_bin), "shell",
         "-d", db, "-c", str(conf_path), "--no-http"],
        input=shell_script,
        capture_output=True,
        text=True,
        timeout=30,
    )

    login = ""
    for line in result.stdout.splitlines():
        if line.startswith("LOGIN="):
            login = line.split("=", 1)[1].strip()

    if not login and result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr[:500])

    return login or "(unknown)"


@app.get("/instances/{instance_id}/users")
def instance_users(instance_id: str):
    """Return list of internal users via direct PostgreSQL query."""
    inst = get_instance(instance_id)
    db = inst["db"]

    # Query directly — avoids ORM access rules and odoo-bin shell startup time.
    # res_users.name is a delegated field from res_partner, not a direct column.
    sql = (
        "SELECT u.id, p.name, u.login "
        "FROM res_users u JOIN res_partner p ON p.id = u.partner_id "
        "WHERE u.share = FALSE AND u.active = TRUE AND u.login NOT IN ('__system__') "
        "ORDER BY p.name LIMIT 200"
    )
    result = subprocess.run(
        ["psql", "-d", db, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr[:300])

    users = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            users.append({"id": int(parts[0]), "name": parts[1], "login": parts[2]})

    return {"users": users}


@app.get("/instances/{instance_id}/open-as/{user_id}")
def open_as(instance_id: str, user_id: int):
    """Set user password to 'demo' and auto-login to Odoo."""
    inst = get_instance(instance_id)
    if inst.get("type", "local") != "local":
        raise HTTPException(status_code=400, detail="Only supported for local instances")

    login = _set_password_via_shell(inst, user_id, "demo")

    port = inst["port"]
    db = inst["db"]
    odoo_url = f"http://localhost:{port}"

    def esc(s: str) -> str:
        return _html.escape(str(s), quote=True)

    # Server-side GET Odoo login page to capture both the csrf_token AND the
    # session_id cookie. Both must match — the CSRF token is derived from the
    # session secret, so we must forward the session cookie to the browser so
    # it's included when the form auto-submits.
    csrf_token = ""
    session_id = ""
    try:
        with httpx.Client(timeout=5, follow_redirects=True) as client:
            resp = client.get(f"{odoo_url}/web/login")
            m = re.search(r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"', resp.text)
            if not m:
                m = re.search(r'"csrf_token"\s*:\s*"([^"]+)"', resp.text)
            if m:
                csrf_token = m.group(1)
            session_id = resp.cookies.get("session_id", "")
    except Exception:
        pass

    page = f"""<!DOCTYPE html>
<html>
<head><title>Connecting as {esc(login)}…</title>
<style>body{{font-family:sans-serif;padding:2rem;color:#333}}</style>
</head>
<body>
<p>Connecting as <strong>{esc(login)}</strong>&hellip; (temporary password: <code>demo</code>)</p>
<form method="POST" action="{esc(odoo_url)}/web/login" id="f">
  <input type="hidden" name="db" value="{esc(db)}">
  <input type="hidden" name="login" value="{esc(login)}">
  <input type="hidden" name="password" value="demo">
  <input type="hidden" name="redirect" value="/odoo">
  <input type="hidden" name="csrf_token" value="{esc(csrf_token)}">
</form>
<script>document.getElementById('f').submit();</script>
</body>
</html>"""

    response = HTMLResponse(page)
    if session_id:
        # Forward Odoo's session cookie with Domain=localhost so the browser
        # sends it when posting the form to localhost:{port}. Both the dashboard
        # (localhost:7070) and Odoo (localhost:{port}) share the localhost domain,
        # so SameSite=Lax allows the cookie to be included in the cross-port POST.
        response.set_cookie(
            "session_id", session_id,
            domain="localhost",
            path="/",
            httponly=True,
            samesite="lax",
        )
    return response


@app.post("/instances/{instance_id}/change-password")
def change_password_endpoint(
    instance_id: str,
    user_id: int = Form(...),
    password: str = Form(...),
):
    """Change a user's password."""
    inst = get_instance(instance_id)
    if inst.get("type", "local") != "local":
        raise HTTPException(status_code=400, detail="Only supported for local instances")
    login = _set_password_via_shell(inst, user_id, password)
    return {"status": "ok", "login": login}


# ---------------------------------------------------------------------------
# Routes — version detection
# ---------------------------------------------------------------------------


def _detect_odoo_version_from_sql(sql_text: str) -> str | None:
    """
    Detect Odoo major version from SQL dump content.
    Looks for module version strings (e.g. '17.0.1.3') near 'base' or 'ir_module'
    in the first 300 KB of the dump.
    """
    known = {"19.0", "18.0", "17.0", "16.0", "15.0", "14.0", "13.0", "12.0"}
    chunk = sql_text[:300_000]
    for m in re.finditer(r"(\d+\.\d+)\.\d+\.\d+", chunk):
        candidate = m.group(1) + ".0"
        if candidate in known:
            start = max(0, m.start() - 500)
            end = min(len(chunk), m.end() + 100)
            context = chunk[start:end]
            if "base" in context or "ir_module" in context:
                return candidate
    return None


@app.post("/api/detect-version")
async def detect_version(zip_file: UploadFile = File(...)):
    """Detect Odoo version from a backup ZIP file by scanning dump.sql."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tmp_zip = tmp_path / (zip_file.filename or "backup.zip")
        tmp_zip.write_bytes(await zip_file.read())

        try:
            with zipfile.ZipFile(tmp_zip) as zf:
                if "dump.sql" not in zf.namelist():
                    return {"version": None, "error": "No dump.sql found in ZIP"}
                with zf.open("dump.sql") as f:
                    sql_chunk = f.read(300_000).decode("utf-8", errors="replace")
        except zipfile.BadZipFile:
            return {"version": None, "error": "Invalid ZIP file"}

        version = _detect_odoo_version_from_sql(sql_chunk)
        return {"version": version}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    return {"status": "ok", "workspace": str(WORKSPACE_ROOT)}
