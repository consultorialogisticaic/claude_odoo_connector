#!/usr/bin/env python3
"""Parse Odoo __manifest__.py files and produce a module registry JSON.

Usage:
    python tools/manifest_parser.py --version 18.0
    python tools/manifest_parser.py --version 18.0 --apps-only
    python tools/manifest_parser.py --version 18.0 --output /tmp/modules.json

Output JSON structure (list of objects):
    {
        "name": "Sale",
        "technical_name": "sale",
        "application": true,
        "category": "Sales/Sales",
        "summary": "From quotations to invoices",
        "description": "...",
        "depends": ["sale_management", ...],
        "auto_install": false,
        "license": "LGPL-3",
        "source": "community",       # community | enterprise | design-themes
        "manifest_path": "/abs/path/to/__manifest__.py"
    }
"""

import argparse
import ast
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "odoo-workspace"

# Directories to scan inside a version folder, and their source label
SOURCE_DIRS = [
    ("odoo/addons", "community"),
    ("odoo/odoo/addons", "community"),  # base lives here
    ("enterprise", "enterprise"),
    ("design-themes", "design-themes"),
]


def parse_manifest(manifest_path: Path) -> dict | None:
    """Safely evaluate a __manifest__.py and return its dict, or None on failure."""
    try:
        source = manifest_path.read_text(encoding="utf-8", errors="replace")
        node = ast.literal_eval(source.split("{", 1)[0] + "{" + source.split("{", 1)[1]
                                if "{" in source else source)
        # Some manifests are just a dict literal, possibly preceded by comments.
        # ast.literal_eval handles that fine.
    except Exception:
        # Fallback: strip leading comments/encoding declarations, eval the dict.
        try:
            text = manifest_path.read_text(encoding="utf-8", errors="replace")
            # Find the first '{' and last '}'
            start = text.index("{")
            end = text.rindex("}") + 1
            node = ast.literal_eval(text[start:end])
        except Exception:
            return None
    if not isinstance(node, dict):
        return None
    return node


def scan_version(version: str, apps_only: bool = False) -> list[dict]:
    """Scan all addon directories for a given Odoo version."""
    version_dir = WORKSPACE / version
    if not version_dir.is_dir():
        print(f"Error: version directory not found: {version_dir}", file=sys.stderr)
        sys.exit(1)

    modules = []
    seen_technical = set()

    for rel_dir, source_label in SOURCE_DIRS:
        addons_dir = version_dir / rel_dir
        if not addons_dir.is_dir():
            continue
        for manifest_path in sorted(addons_dir.glob("*/__manifest__.py")):
            technical_name = manifest_path.parent.name
            if technical_name in seen_technical:
                continue  # enterprise can override community; keep first hit
            data = parse_manifest(manifest_path)
            if data is None:
                continue

            is_app = bool(data.get("application", False))
            if apps_only and not is_app:
                continue

            seen_technical.add(technical_name)
            modules.append({
                "name": data.get("name", technical_name),
                "technical_name": technical_name,
                "application": is_app,
                "category": data.get("category", ""),
                "summary": data.get("summary", ""),
                "description": (data.get("description") or "").strip()[:500],
                "depends": data.get("depends", []),
                "auto_install": bool(data.get("auto_install", False)),
                "license": data.get("license", ""),
                "source": source_label,
                "manifest_path": str(manifest_path),
            })

    modules.sort(key=lambda m: m["technical_name"])
    return modules


def main():
    parser = argparse.ArgumentParser(description="Parse Odoo module manifests into JSON")
    parser.add_argument("--version", required=True, help="Odoo version, e.g. 18.0")
    parser.add_argument("--apps-only", action="store_true", help="Only include application modules")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    modules = scan_version(args.version, apps_only=args.apps_only)

    result = json.dumps(modules, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Wrote {len(modules)} modules to {args.output}", file=sys.stderr)
    else:
        print(result)

    print(f"Total: {len(modules)} modules", file=sys.stderr)


if __name__ == "__main__":
    main()
