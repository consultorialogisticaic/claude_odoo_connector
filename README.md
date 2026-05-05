# claude-odoo-connector

Odoo infrastructure layer for Claude Code agents. Provides slash commands, subagents, and Python tooling for connecting to, discovering, deploying, and debugging Odoo instances (versions 14–19).

## What it gives you

**Slash commands** (in `commands/`):

| Command | Purpose |
|---|---|
| `/odoo-connect` | Register a local or remote Odoo instance (interactive wizard) |
| `/odoo-discover` | Self-discover custom modules on a remote instance with no source access |
| `/odoo-orm` | ORM model investigation: fields, inheritance, methods |
| `/odoo-debug` | Debug a running instance: tail logs, classify tracebacks |
| `/odoo-deploy` | Create instances, restore SQL dumps, multi-version management |
| `/odoo-source-install` | Install Odoo from source (pip deps, system libs) |
| `/odoo-version-delta` | Breaking changes between Odoo versions |
| `/odoo-apikey` | API key management |

**Subagents** (in `subagents/`): `technical_expert`, `functional_expert`, `debugger`, `discovery_agent`, `app_features_expert`, `ui_expert`.

**Python tools** (in `tools/`): XML-RPC client, OCA search, manifest parser, discovery helpers — usable directly or via the slash commands above.

**Version knowledge** (in `knowledge/<version>/`): committed feature catalogs, UI reports, and identity keys per Odoo version.

---

## Install as a Claude Code plugin

This repo is a Claude Code plugin. The plugin manifest lives at `.claude-plugin/plugin.json` and the marketplace listing at `.claude-plugin/marketplace.json`.

```bash
# 1. Add this repo as a marketplace
/plugin marketplace add consultorialogisticaic/claude_odoo_connector

# 2. Install the plugin
/plugin install claude-odoo-connector@claude-odoo-connector
```

After install, slash commands appear namespaced as `/claude-odoo-connector:odoo-connect`, etc.

### Updates

The plugin is pinned to an explicit `version` in `plugin.json`. Users only receive updates when the version is bumped. To pull updates:

```bash
/plugin update claude-odoo-connector
```

You can also enable per-marketplace auto-update from the `/plugin` UI → **Marketplaces** tab.

---

## Use as a git submodule (alternative)

If you're consuming this from another orchestration repo, add it as a submodule:

```bash
cd <consumer-project>
git submodule add https://github.com/consultorialogisticaic/claude_odoo_connector.git connector
git submodule update --init
bash connector/setup-links.sh   # symlinks slash commands into <consumer>/.claude/commands/
```

To update later: `git submodule update --remote connector`.

---

## Running the dashboard

```bash
pip install -r requirements.txt
uvicorn connector.dashboard.main:app --reload --port 7070
# Or set workspace path explicitly:
ODOO_WORKSPACE_ROOT=/path/to/odoo-workspace uvicorn connector.dashboard.main:app --port 7070
```

Dashboard at http://localhost:7070.

---

## Workspace layout

```
odoo-workspace/          ← gitignored runtime workspace
  workspace.json         ← instance registry
  <version>/
    odoo/                ← git clone of odoo/odoo
    enterprise/
    clients/<client>/
      odoo.conf
      .env               ← ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY
      knowledge/         ← per-instance discovery output (gitignored)

knowledge/               ← version-level research, committed
  <version>/
    feature_catalogs/
    ui_reports/
    identity_keys.json
```

See [`CLAUDE.md`](CLAUDE.md) for agent-facing operational details.
