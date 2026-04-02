"""Tests for tools/discovery.py — all OdooRPC calls are mocked."""
from unittest.mock import MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.discovery import (
    get_custom_modules,
    get_module_models,
    get_model_fields,
    check_model_views,
    get_model_actions,
)


def _make_rpc():
    return MagicMock()


def test_get_custom_modules_filters_standard_authors():
    rpc = _make_rpc()
    rpc.search_read.return_value = [
        {"name": "sale", "author": "Odoo S.A.", "shortdesc": "Sales", "description": "", "summary": "", "depends": [], "installed_version": "17.0"},
        {"name": "my_module", "author": "Acme Corp", "shortdesc": "Acme Stuff", "description": "Custom", "summary": "", "depends": ["sale"], "installed_version": "1.0"},
    ]
    result = get_custom_modules(rpc)
    assert len(result) == 1
    assert result[0]["name"] == "my_module"


def test_get_custom_modules_filters_standard_prefixes():
    rpc = _make_rpc()
    rpc.search_read.return_value = [
        {"name": "base_setup", "author": "Unknown", "shortdesc": "Base Setup", "description": "", "summary": "", "depends": [], "installed_version": "1.0"},
        {"name": "acme_pos", "author": "Unknown", "shortdesc": "Acme POS", "description": "", "summary": "", "depends": [], "installed_version": "1.0"},
    ]
    result = get_custom_modules(rpc)
    assert len(result) == 1
    assert result[0]["name"] == "acme_pos"


def test_get_module_models_calls_ir_model():
    rpc = _make_rpc()
    rpc.search_read.return_value = [
        {"model": "acme.order", "name": "Acme Order", "info": ""},
    ]
    result = get_module_models(rpc, "acme_pos")
    rpc.search_read.assert_called_once_with(
        "ir.model",
        [["modules", "like", "acme_pos"]],
        ["model", "name", "info"],
    )
    assert result[0]["model"] == "acme.order"


def test_get_model_fields_excludes_one2many():
    rpc = _make_rpc()
    rpc.search_read.return_value = [
        {"name": "name", "field_description": "Name", "ttype": "char", "required": True, "store": True, "relation": ""},
        {"name": "partner_id", "field_description": "Partner", "ttype": "many2one", "required": False, "store": True, "relation": "res.partner"},
    ]
    result = get_model_fields(rpc, "acme.order")
    rpc.search_read.assert_called_once_with(
        "ir.model.fields",
        [["model_id.model", "=", "acme.order"], ["ttype", "!=", "one2many"]],
        ["name", "field_description", "ttype", "required", "store", "relation"],
    )
    assert len(result) == 2


def test_check_model_views_returns_dict():
    rpc = _make_rpc()
    rpc.search.side_effect = [
        [1],   # form exists
        [],    # list does not
        [],    # kanban does not
    ]
    result = check_model_views(rpc, "acme.order")
    assert result == {"form": True, "list": False, "kanban": False}


def test_get_model_actions_returns_names():
    rpc = _make_rpc()
    rpc.search_read.return_value = [
        {"name": "Acme Orders"},
        {"name": "Acme Orders (all)"},
    ]
    result = get_model_actions(rpc, "acme.order")
    assert result == ["Acme Orders", "Acme Orders (all)"]


def test_get_model_actions_returns_empty_when_none():
    rpc = _make_rpc()
    rpc.search_read.return_value = []
    result = get_model_actions(rpc, "acme.order")
    assert result == []
