"""Tests for tools/oca_search.py — urllib is mocked."""
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.oca_search import search_oca


def _mock_github_response(items: list[dict]):
    """Return a context manager that yields a fake urllib response."""
    body = json.dumps({"items": items}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_returns_none_when_no_github_results():
    mock_resp = _mock_github_response([])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = search_oca("my_custom_module", "Custom stuff")
    assert result is None


def test_returns_match_for_exact_name():
    items = [
        {
            "name": "my_custom_module",
            "html_url": "https://github.com/OCA/my_custom_module",
            "description": "Custom stuff for Odoo",
        }
    ]
    mock_resp = _mock_github_response(items)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = search_oca("my_custom_module", "Custom stuff")
    assert result is not None
    assert result["url"] == "https://github.com/OCA/my_custom_module"
    assert result["confidence"] >= 0.5
    assert "readme_url" in result


def test_returns_none_when_confidence_below_threshold():
    items = [
        {
            "name": "completely_different_repo",
            "html_url": "https://github.com/OCA/completely_different_repo",
            "description": "Nothing related",
        }
    ]
    mock_resp = _mock_github_response(items)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = search_oca("my_custom_module", "Custom stuff")
    assert result is None


def test_returns_none_on_network_error():
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        result = search_oca("my_custom_module", "Custom stuff")
    assert result is None


def test_readme_url_points_to_oca_raw():
    items = [
        {
            "name": "account_invoice_export",
            "html_url": "https://github.com/OCA/account_invoice_export",
            "description": "Export invoices from Odoo",
        }
    ]
    mock_resp = _mock_github_response(items)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = search_oca("account_invoice_export", "Export invoices")
    assert result is not None
    assert result["readme_url"].startswith("https://raw.githubusercontent.com/OCA/")
