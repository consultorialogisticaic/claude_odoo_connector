"""
OCA and Odoo Apps Store search for custom modules.

Given a module technical name and description, searches the OCA GitHub org
and returns the best matching repository URL with a confidence score.

Uses only stdlib — no requests or other external dependencies.

Usage:
    from tools.oca_search import search_oca
    match = search_oca("account_invoice_export", "Export invoices from Odoo")
    if match:
        print(match["url"], match["confidence"])
"""

from __future__ import annotations

import difflib
import json
import urllib.parse
import urllib.request

_CONFIDENCE_THRESHOLD = 0.5
_OCA_ORG = "OCA"


def search_oca(module_name: str, description: str = "") -> dict | None:
    """
    Search OCA GitHub org for a repo matching module_name + description.

    Returns a dict with keys:
        url         — GitHub repo HTML URL
        confidence  — float 0.0–1.0 (name similarity * 0.7 + desc similarity * 0.3)
        readme_url  — raw GitHub URL for the README.rst
        description — repo description from GitHub

    Returns None if no match above the confidence threshold or on network error.
    """
    query = urllib.parse.quote(f"org:{_OCA_ORG} {module_name} in:name")
    api_url = f"https://api.github.com/search/repositories?q={query}&per_page=5"

    try:
        req = urllib.request.Request(
            api_url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "claude-odoo-connector",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return None

    items = data.get("items", [])
    if not items:
        return None

    best: dict | None = None
    best_score = 0.0

    for item in items:
        name_score = difflib.SequenceMatcher(
            None, module_name, item.get("name", "")
        ).ratio()
        desc_score = 0.0
        if description and item.get("description"):
            desc_score = difflib.SequenceMatcher(
                None, description[:200], item["description"]
            ).ratio()
        score = (name_score * 0.7) + (desc_score * 0.3)
        if score > best_score:
            best_score = score
            best = item

    if best_score < _CONFIDENCE_THRESHOLD or best is None:
        return None

    repo_name = best["name"]
    return {
        "url": best["html_url"],
        "confidence": round(best_score, 2),
        "readme_url": f"https://raw.githubusercontent.com/{_OCA_ORG}/{repo_name}/HEAD/README.rst",
        "description": best.get("description", ""),
    }
