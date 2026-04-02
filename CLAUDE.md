# CLAUDE.md — claude_odoo_connector

This project is the Odoo infrastructure layer used by Claude agents. It provides
RPC tools, instance management, self-discovery, and version-specific knowledge bases.

## Skills (slash commands)

| Command | Purpose |
|---|---|
| `/odoo-connect` | Register a local or remote Odoo instance (interactive wizard) |
| `/odoo-discover` | Self-discover custom modules on a remote instance with no source access |
| `/odoo-orm` | ORM model investigation: fields, inheritance, methods |
| `/odoo-debug` | Debug a running instance: tail logs, classify tracebacks |
| `/odoo-deploy` | Create instances, restore SQL dumps, multi-version management |
| `/odoo-source-install` | Install Odoo from source (pip deps, system libs, v14–v19) |
| `/odoo-version-delta` | Breaking changes between Odoo versions |
| `/odoo-apikey` | API key management: auto-generation via dashboard, manual fallback steps |

## Subagents

- `subagents/technical_expert.md` — ORM source traversal + version delta
- `subagents/functional_expert.md` — functional configuration + module install guidance
- `subagents/debugger.md` — log parsing, traceback classification, update runner
- `subagents/discovery_agent.md` — self-discovery: ir.models introspection + OCA enrichment
- `subagents/app_features_expert.md` — reads manifests + source to produce a Feature Catalog per app
- `subagents/ui_expert.md` — form view investigation, constraints, demo data patterns per model

## Tools

```bash
# Connect to a local instance via XML-RPC
python tools/odoo_rpc.py res.partner --domain '[]' --fields name --limit 5

# Discover custom modules on a connected instance
python -c "
from tools.odoo_rpc import OdooRPC
from tools.discovery import get_custom_modules
rpc = OdooRPC.from_env()
for m in get_custom_modules(rpc): print(m['name'])
"

# Search OCA for a module
python -c "
from tools.oca_search import search_oca
print(search_oca('account_invoice_export', 'Export invoices'))
"

# Parse installed modules from local Odoo source
python tools/manifest_parser.py --version 18.0 --apps-only
```

## Running the dashboard

```bash
pip install -r requirements.txt
# From the consumer project root (e.g. odoo_demo_creator/):
uvicorn connector.dashboard.main:app --reload --port 7070
# Or set workspace path explicitly:
ODOO_WORKSPACE_ROOT=/path/to/odoo-workspace uvicorn connector.dashboard.main:app --port 7070
```

Dashboard at http://localhost:7070. Manages local and remote Odoo instances.

## Workspace layout

```
odoo-workspace/          ← gitignored runtime workspace
  workspace.json         ← instance registry
  .env                   ← symlink to active instance .env
  <version>/
    odoo/                ← git clone of odoo/odoo
    enterprise/
    design-themes/
    clients/<client>/
      odoo.conf
      .env               ← ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY
      knowledge/         ← client-specific discovery output (gitignored)
        modules.json
        custom_modules/
        models/
        oca_matches/

knowledge/               ← version-level research, committed to git
  <version>/
    feature_catalogs/
    ui_reports/
    identity_keys.json
```

## Adding a consumer project

```bash
cd <consumer-project>
git submodule add <connector-repo-url> connector
git submodule update --init
bash connector/setup-links.sh
```
