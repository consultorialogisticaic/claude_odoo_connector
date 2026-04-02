"""
Odoo JSON-RPC client.

Reads connection settings from the active .env file or from explicit arguments.
Supports all standard ORM operations plus raw execute_kw passthrough.

Usage:
    from tools.odoo_rpc import OdooRPC

    rpc = OdooRPC.from_env()          # reads odoo-workspace/.env
    rpc = OdooRPC(url, db, user, key) # explicit

    records = rpc.search_read("sale.order", [["state","=","sale"]], ["name","amount_total"])
    id_ = rpc.create("res.partner", {"name": "Acme Corp", "is_company": True})
    rpc.write("res.partner", [id_], {"phone": "+1 555 0100"})
    rpc.call("account.move", "action_post", [[invoice_id]])
"""

from __future__ import annotations

import json
import os
import pathlib
import xmlrpc.client
from typing import Any

# ---------------------------------------------------------------------------
# Location helpers
# ---------------------------------------------------------------------------

_WORKSPACE_ROOT = pathlib.Path(__file__).parent.parent / "odoo-workspace"
_DEFAULT_ENV = _WORKSPACE_ROOT / ".env"


def _load_env(path: pathlib.Path | str | None = None) -> dict[str, str]:
    """Parse a .env file into a dict. Does NOT set os.environ."""
    env_path = pathlib.Path(path) if path else _DEFAULT_ENV
    result: dict[str, str] = {}
    if not env_path.exists():
        return result
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


# ---------------------------------------------------------------------------
# Main client
# ---------------------------------------------------------------------------


class OdooRPC:
    """Thin wrapper around Odoo's JSON-RPC / XML-RPC interfaces."""

    def __init__(
        self,
        url: str,
        db: str,
        user: str,
        api_key: str,
    ) -> None:
        self.url = url.rstrip("/")
        self.db = db
        self.user = user
        self.api_key = api_key
        self._uid: int | None = None

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, env_path: str | None = None) -> "OdooRPC":
        """Build an OdooRPC instance from a .env file."""
        env = _load_env(env_path)
        missing = [k for k in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_API_KEY") if k not in env]
        if missing:
            raise EnvironmentError(f"Missing .env keys: {', '.join(missing)}")
        return cls(
            url=env["ODOO_URL"],
            db=env["ODOO_DB"],
            user=env["ODOO_USER"],
            api_key=env["ODOO_API_KEY"],
        )

    @classmethod
    def from_os_env(cls) -> "OdooRPC":
        """Build from environment variables already set in the shell."""
        return cls(
            url=os.environ["ODOO_URL"],
            db=os.environ["ODOO_DB"],
            user=os.environ["ODOO_USER"],
            api_key=os.environ["ODOO_API_KEY"],
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    @property
    def uid(self) -> int:
        if self._uid is None:
            self._uid = self._authenticate()
        return self._uid

    def _authenticate(self) -> int:
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        uid = common.authenticate(self.db, self.user, self.api_key, {})
        if not uid:
            raise PermissionError(f"Authentication failed for user '{self.user}' on '{self.url}'")
        return uid

    # ------------------------------------------------------------------
    # Core ORM operations
    # ------------------------------------------------------------------

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list,
        kwargs: dict | None = None,
    ) -> Any:
        """Raw execute_kw passthrough."""
        models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        return models.execute_kw(
            self.db, self.uid, self.api_key,
            model, method, args, kwargs or {},
        )

    def search(self, model: str, domain: list, **kwargs) -> list[int]:
        return self.execute_kw(model, "search", [domain], kwargs)

    def search_read(
        self,
        model: str,
        domain: list,
        fields: list[str] | None = None,
        limit: int = 0,
        offset: int = 0,
        order: str | None = None,
    ) -> list[dict]:
        kw: dict[str, Any] = {}
        if fields:
            kw["fields"] = fields
        if limit:
            kw["limit"] = limit
        if offset:
            kw["offset"] = offset
        if order:
            kw["order"] = order
        return self.execute_kw(model, "search_read", [domain], kw)

    def read(self, model: str, ids: list[int], fields: list[str] | None = None) -> list[dict]:
        kw = {"fields": fields} if fields else {}
        return self.execute_kw(model, "read", [ids], kw)

    def create(self, model: str, vals: dict) -> int:
        return self.execute_kw(model, "create", [vals])

    def create_many(self, model: str, vals_list: list[dict]) -> list[int]:
        return self.execute_kw(model, "create", [vals_list])

    def write(self, model: str, ids: list[int], vals: dict) -> bool:
        return self.execute_kw(model, "write", [ids, vals])

    def unlink(self, model: str, ids: list[int]) -> bool:
        return self.execute_kw(model, "unlink", [ids])

    def call(self, model: str, method: str, args: list, kwargs: dict | None = None) -> Any:
        """Call any model method (e.g. action_post, button_confirm, etc.)."""
        return self.execute_kw(model, method, args, kwargs)

    def fields_get(self, model: str, attributes: list[str] | None = None) -> dict:
        kw = {"attributes": attributes} if attributes else {}
        return self.execute_kw(model, "fields_get", [], kw)

    # ------------------------------------------------------------------
    # Module management
    # ------------------------------------------------------------------

    def installed_modules(self) -> list[str]:
        records = self.search_read(
            "ir.module.module",
            [["state", "=", "installed"]],
            ["name"],
        )
        return [r["name"] for r in records]

    def install_module(self, *module_names: str) -> None:
        """Install one or more modules by technical name."""
        records = self.search_read(
            "ir.module.module",
            [["name", "in", list(module_names)], ["state", "!=", "installed"]],
            ["id", "name"],
        )
        if not records:
            return
        ids = [r["id"] for r in records]
        self.call("ir.module.module", "button_immediate_install", [ids])

    def upgrade_module(self, *module_names: str) -> None:
        records = self.search_read(
            "ir.module.module",
            [["name", "in", list(module_names)], ["state", "=", "installed"]],
            ["id"],
        )
        if not records:
            return
        ids = [r["id"] for r in records]
        self.call("ir.module.module", "button_immediate_upgrade", [ids])

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def ref(self, xml_id: str) -> int | None:
        """Resolve an XML ID to a record ID (like env.ref in Odoo)."""
        parts = xml_id.split(".", 1)
        if len(parts) != 2:
            raise ValueError(f"xml_id must be 'module.name', got: {xml_id!r}")
        module, name = parts
        records = self.search_read(
            "ir.model.data",
            [["module", "=", module], ["name", "=", name]],
            ["res_id"],
        )
        return records[0]["res_id"] if records else None

    def get_or_create(self, model: str, domain: list, vals: dict) -> tuple[int, bool]:
        """
        Return (id, created). If a record matching domain exists, return it.
        Otherwise create one with vals.
        """
        ids = self.search(model, domain, limit=1)
        if ids:
            return ids[0], False
        return self.create(model, vals), True

    # ------------------------------------------------------------------
    # Debug / introspection
    # ------------------------------------------------------------------

    def version(self) -> dict:
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        return common.version()

    def __repr__(self) -> str:
        return f"OdooRPC(url={self.url!r}, db={self.db!r}, user={self.user!r})"


# ---------------------------------------------------------------------------
# CLI entry point for quick ad-hoc queries
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import pprint

    parser = argparse.ArgumentParser(description="Quick Odoo JSON-RPC query")
    parser.add_argument("model", help="Model name, e.g. res.partner")
    parser.add_argument("--domain", default="[]", help="Domain as JSON, e.g. '[[\"active\",\"=\",true]]'")
    parser.add_argument("--fields", default="", help="Comma-separated field names")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--env", default=None, help="Path to .env file")
    args = parser.parse_args()

    rpc = OdooRPC.from_env(args.env)
    domain = json.loads(args.domain)
    fields = [f.strip() for f in args.fields.split(",") if f.strip()] or None
    results = rpc.search_read(args.model, domain, fields, limit=args.limit)
    pprint.pprint(results)
