---
name: odoo-discover
description: Run self-discovery on a connected Odoo instance that has no source code access. Discovers custom modules, models, fields, views, and actions. Searches OCA for open-source matches. Writes a client-specific knowledge base.
---

You are the Odoo discovery orchestrator. Your job is to run self-discovery on an instance registered in `workspace.json`.

## Step 1 — Identify the target instance

Ask the user for the instance ID, or read it from context.

Read `odoo-workspace/workspace.json`. Find the instance entry.

If `source_access` is not `"none"`, stop and tell the user:
- If `local-clone`: "Source is available locally — use `/odoo-orm` to investigate models."
- If `github`: "Source is on GitHub at `<github_repo>` — use `/odoo-orm` to investigate, pointing at the GitHub URL."

## Step 2 — Check discovery status

If `discovery_status` is `"complete"`, ask the user: "Discovery was already completed for this instance. Re-run? (yes/no)"

If they say no, stop and tell them where the knowledge base is:
`odoo-workspace/<version>/clients/<id>/knowledge/`

## Step 3 — Set status to in-progress

Update `workspace.json` entry: set `discovery_status: "in-progress"`.

## Step 4 — Create knowledge base directories

```bash
mkdir -p odoo-workspace/<version>/clients/<id>/knowledge/custom_modules
mkdir -p odoo-workspace/<version>/clients/<id>/knowledge/models
mkdir -p odoo-workspace/<version>/clients/<id>/knowledge/oca_matches
```

## Step 5 — Dispatch discovery_agent

Invoke the `discovery_agent` subagent with this context:
- Instance ID: `<id>`
- Instance path: `odoo-workspace/<version>/clients/<id>`
- .env path: `odoo-workspace/<version>/clients/<id>/.env`
- Knowledge base path: `odoo-workspace/<version>/clients/<id>/knowledge/`

The discovery_agent will:
1. Pull custom modules list
2. Pull models and fields per module
3. Search OCA for each module
4. Write all knowledge base files

## Step 6 — Update discovery_status

After the discovery_agent completes, update `workspace.json`: set `discovery_status: "complete"`.

## Step 7 — Print summary

Print a summary of what was discovered:
- Number of custom modules found
- Number of custom models discovered
- Number of OCA matches found
- Location of knowledge base: `odoo-workspace/<version>/clients/<id>/knowledge/`
