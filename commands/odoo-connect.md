---
name: odoo-connect
description: Register a local or remote Odoo instance into workspace.json. Interactive wizard — asks for type, URL, credentials, and SSH details.
---

You are the Odoo connection wizard. Register a new instance in `odoo-workspace/workspace.json`.

## Step 1 — Ask for instance type

Ask: "What type of instance are you connecting to?"
- **local** — running on this machine, managed by the dashboard
- **remote-url** — accessible via URL + API key only (SaaS, on-prem, no SSH)
- **remote-ssh** — server you control via SSH + URL + API key

## Step 2 — Collect required information

For all types:
- Instance ID (short slug, e.g. `acme-17`, `customer-prod`)
- Odoo version (e.g. `17.0`)
- Odoo URL (e.g. `https://customer.odoo.com` or `http://localhost:8069`)
- Database name
- Odoo user email
- API key

For **local** only:
- Port (default: auto-assigned from 8069 up)
- Client folder name (used as path inside odoo-workspace/)

For **remote-ssh** only:
- SSH host
- SSH user

For **remote-url** and **remote-ssh**:
- Does source code exist? Options: `github` (provide repo URL), `none` (self-discovery needed)

## Step 3 — Build the instance entry

Construct the JSON entry based on type:

**local:**
```json
{
  "id": "<id>",
  "type": "local",
  "version": "<version>",
  "path": "<version>/clients/<client>",
  "db": "<db>",
  "port": <port>,
  "url": "http://localhost:<port>",
  "capabilities": ["start", "stop", "install-cli", "install-rpc"],
  "source_access": "local-clone"
}
```

**remote-url:**
```json
{
  "id": "<id>",
  "type": "remote-url",
  "version": "<version>",
  "url": "<url>",
  "db": "<db>",
  "path": "<version>/clients/<id>",
  "capabilities": ["install-rpc"],
  "source_access": "<github|none>",
  "discovery_status": "none"
}
```
(Omit `discovery_status` if `source_access` is `github`. Add `"github_repo": "<org/repo>"` if github.)

**remote-ssh:**
```json
{
  "id": "<id>",
  "type": "remote-ssh",
  "version": "<version>",
  "url": "<url>",
  "ssh_host": "<host>",
  "ssh_user": "<user>",
  "db": "<db>",
  "path": "<version>/clients/<id>",
  "capabilities": ["start", "stop", "install-cli", "install-rpc"],
  "source_access": "<github|none>"
}
```

## Step 4 — Write to workspace.json

Read `odoo-workspace/workspace.json` (create it with `{"instances": []}` if missing).
Check that no instance with the same `id` already exists — if it does, ask the user to confirm overwrite.
Append the new entry to `instances` and write back.

## Step 5 — Create client folder and .env

```bash
mkdir -p odoo-workspace/<version>/clients/<id>
```

Create `odoo-workspace/<version>/clients/<id>/.env`:
```
ODOO_URL=<url>
ODOO_DB=<db>
ODOO_USER=<user>
ODOO_API_KEY=<api_key>
ODOO_VERSION=<version>
```

## Step 6 — Verify connection

Run a quick check using the Python tool:
```bash
python tools/odoo_rpc.py res.partner --domain '[]' --fields name --limit 1 --env odoo-workspace/<version>/clients/<id>/.env
```

If it returns a record, print: "Connected successfully to <id> (<url>)".
If it fails, print the error and suggest checking credentials.

## Step 7 — Suggest next step

If `source_access: none`, tell the user: "Run `/odoo-discover <id>` to build a knowledge base of custom modules for this instance."
If `source_access: github`, tell the user the repo URL and that ORM introspection can be done with `/odoo-orm`.
