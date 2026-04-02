"""
Module installer — installs Odoo modules via JSON-RPC or CLI.

Two modes:
  - RPC mode (default): uses the running Odoo JSON-RPC API (works for community & enterprise)
  - CLI mode: SSH / subprocess into the server and calls odoo-bin directly

Usage:
    python tools/module_installer.py sale purchase stock --env odoo-workspace/.env
    python tools/module_installer.py sale --mode cli --instance acme-17
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.odoo_rpc import OdooRPC, _load_env

_WORKSPACE_ROOT = Path(__file__).parent.parent / "odoo-workspace"


# ---------------------------------------------------------------------------
# RPC installer
# ---------------------------------------------------------------------------


def install_via_rpc(modules: list[str], env_path: str | None = None) -> None:
    rpc = OdooRPC.from_env(env_path)
    print(f"[rpc] Connected to {rpc.url} db={rpc.db}")

    already = set(rpc.installed_modules())
    to_install = [m for m in modules if m not in already]

    if not to_install:
        print("[rpc] All modules already installed.")
        return

    print(f"[rpc] Installing: {', '.join(to_install)}")
    rpc.install_module(*to_install)
    print("[rpc] Done.")


# ---------------------------------------------------------------------------
# CLI installer
# ---------------------------------------------------------------------------


def install_via_cli(modules: list[str], instance_id: str) -> None:
    """
    Locate the odoo-workspace entry for instance_id and run odoo-bin -i.
    Expects the instance to be stopped (or restartable).
    """
    import json

    registry_path = _WORKSPACE_ROOT / "workspace.json"
    if not registry_path.exists():
        raise FileNotFoundError(f"workspace.json not found at {registry_path}")

    registry = json.loads(registry_path.read_text())
    instance = next((i for i in registry.get("instances", []) if i["id"] == instance_id), None)
    if not instance:
        raise ValueError(f"Instance '{instance_id}' not found in workspace.json")

    instance_path = _WORKSPACE_ROOT / instance["path"]
    env = _load_env(instance_path / ".env")
    version = env.get("ODOO_VERSION", instance.get("version", "17.0"))

    odoo_bin = _WORKSPACE_ROOT / version / "odoo" / "odoo-bin"
    if not odoo_bin.exists():
        raise FileNotFoundError(f"odoo-bin not found at {odoo_bin}")

    conf = instance_path / "odoo.conf"
    db = instance["db"]
    module_list = ",".join(modules)

    cmd = [
        str(odoo_bin),
        "-c", str(conf),
        "-d", db,
        "-i", module_list,
        "--stop-after-init",
    ]

    print(f"[cli] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        raise RuntimeError(f"odoo-bin exited with code {result.returncode}")
    print("[cli] Done.")


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


def upgrade_via_rpc(modules: list[str], env_path: str | None = None) -> None:
    rpc = OdooRPC.from_env(env_path)
    print(f"[rpc] Connected to {rpc.url} db={rpc.db}")
    print(f"[rpc] Upgrading: {', '.join(modules)}")
    rpc.upgrade_module(*modules)
    print("[rpc] Done.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install or upgrade Odoo modules")
    parser.add_argument("modules", nargs="+", help="Technical module names")
    parser.add_argument(
        "--mode",
        choices=["rpc", "cli"],
        default="rpc",
        help="rpc (default) uses the live Odoo API; cli calls odoo-bin directly",
    )
    parser.add_argument("--env", default=None, help="Path to .env file (rpc mode)")
    parser.add_argument("--instance", default=None, help="Instance ID from workspace.json (cli mode)")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade instead of install")
    args = parser.parse_args()

    if args.mode == "rpc":
        if args.upgrade:
            upgrade_via_rpc(args.modules, args.env)
        else:
            install_via_rpc(args.modules, args.env)
    else:
        if not args.instance:
            parser.error("--instance is required for cli mode")
        install_via_cli(args.modules, args.instance)
