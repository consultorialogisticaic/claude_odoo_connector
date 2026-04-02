"""
Odoo self-discovery tool.

Connects to a running Odoo instance and extracts information about installed
custom modules, their models, fields, views, and actions via XML-RPC introspection.

Usage:
    from tools.odoo_rpc import OdooRPC
    from tools.discovery import get_custom_modules, get_module_models

    rpc = OdooRPC.from_env()
    custom = get_custom_modules(rpc)
    for mod in custom:
        models = get_module_models(rpc, mod["name"])
"""

from __future__ import annotations

from tools.odoo_rpc import OdooRPC

# Authors that identify standard Odoo modules — filter these out
STANDARD_AUTHORS = {"Odoo S.A.", "Odoo"}

# Technical name prefixes that identify standard infrastructure modules
_STANDARD_PREFIXES = (
    "base", "web", "mail", "ir_", "report_", "test_",
    "auth_", "l10n_", "theme_", "hw_", "point_of_sale",
)


def get_custom_modules(rpc: OdooRPC) -> list[dict]:
    """
    Return all installed non-standard modules.

    Filters out modules authored by Odoo S.A./Odoo and modules whose
    technical name starts with known standard prefixes.
    """
    all_modules = rpc.search_read(
        "ir.module.module",
        [["state", "=", "installed"]],
        ["name", "shortdesc", "author", "description", "summary", "depends", "installed_version"],
    )
    return [
        m for m in all_modules
        if m.get("author", "") not in STANDARD_AUTHORS
        and not any(m["name"].startswith(p) for p in _STANDARD_PREFIXES)
    ]


def get_module_models(rpc: OdooRPC, module_name: str) -> list[dict]:
    """
    Return ir.model records belonging to the given module technical name.
    """
    return rpc.search_read(
        "ir.model",
        [["modules", "like", module_name]],
        ["model", "name", "info"],
    )


def get_model_fields(rpc: OdooRPC, model_name: str) -> list[dict]:
    """
    Return ir.model.fields records for the given model, excluding one2many fields.
    One2many fields are noise for discovery — they're the inverse of many2one.
    """
    return rpc.search_read(
        "ir.model.fields",
        [["model_id.model", "=", model_name], ["ttype", "!=", "one2many"]],
        ["name", "field_description", "ttype", "required", "store", "relation"],
    )


def check_model_views(rpc: OdooRPC, model_name: str) -> dict[str, bool]:
    """
    Check which view types exist for the given model.
    Returns {"form": bool, "list": bool, "kanban": bool}.
    """
    result: dict[str, bool] = {}
    for vtype in ("form", "list", "kanban"):
        ids = rpc.search(
            "ir.ui.view",
            [["model", "=", model_name], ["type", "=", vtype], ["active", "=", True]],
            limit=1,
        )
        result[vtype] = bool(ids)
    return result


def get_model_actions(rpc: OdooRPC, model_name: str) -> list[str]:
    """
    Return the names of all ir.actions.act_window that open the given model.
    """
    actions = rpc.search_read(
        "ir.actions.act_window",
        [["res_model", "=", model_name]],
        ["name"],
    )
    return [a["name"] for a in actions]
