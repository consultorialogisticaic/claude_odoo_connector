---
name: odoo-deploy
description: Database deployment skill. Covers creating new Odoo instances, cloning repos, restoring SQL dumps, and managing multiple versions.
---

You have been invoked as the Odoo deployment expert. Use the steps below.

## Workspace structure recap

```
odoo-workspace/
  workspace.json         ← instance registry
  .env -> <active>/.env  ← symlink to active instance
  <version>/
    odoo/                ← git clone of odoo/odoo
    enterprise/          ← git clone of odoo/enterprise
    themes/              ← git clone of odoo/design-themes
    clients/<client>/
      odoo.conf
      .env
      addons/
      data/
      client.md
      demo.md
      odoo.log
```

## Creating a new version environment

### 1. Clone the repos
```bash
cd odoo-workspace
mkdir -p 17.0 && cd 17.0
git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git odoo
# Enterprise (requires access):
git clone --depth 1 --branch 17.0 git@github.com:odoo/enterprise.git enterprise
# Themes:
git clone --depth 1 --branch 17.0 https://github.com/odoo/design-themes.git themes
```

### 2. Create Python virtual environment
```bash
cd odoo-workspace/17.0/odoo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create PostgreSQL database
```bash
createdb <db_name>
# or via psql:
psql -c "CREATE DATABASE <db_name> OWNER odoo;"
```

### 4. Create instance via dashboard
- Open http://localhost:7070
- Click "+ New Instance"
- The dashboard auto-generates `odoo.conf`, `.env`, and folder structure.

### 5. Initialize the database
```bash
odoo-workspace/17.0/odoo/odoo-bin \
  -c odoo-workspace/17.0/<client>/odoo.conf \
  -d <db_name> \
  --without-demo=all \
  --stop-after-init
```

---

## Restoring from a SQL dump

```bash
# Stop the instance first (dashboard or kill pid)
dropdb --if-exists <db_name>
createdb <db_name>
psql -d <db_name> -f path/to/dump.sql
# or for .sql.gz:
gunzip -c dump.sql.gz | psql -d <db_name>
```

Then start the instance. Odoo will detect the restored database automatically.

---

## Restoring from a .zip (filestore included)

Odoo `.zip` backups contain `dump.sql` + `filestore/`.
```bash
unzip backup.zip -d /tmp/restore/
dropdb --if-exists <db_name> && createdb <db_name>
psql -d <db_name> -f /tmp/restore/dump.sql
cp -r /tmp/restore/filestore/* odoo-workspace/<version>/<client>/data/filestore/
```

---

## Managing multiple versions (runbot-style)

Each version lives under `odoo-workspace/<version>/`. Ports are assigned sequentially
starting from 8069 by the dashboard. To list all running instances:

```bash
cat odoo-workspace/workspace.json | python3 -m json.tool
```

To switch the active `.env` symlink:
```bash
ln -sf odoo-workspace/<version>/<client>/.env odoo-workspace/.env
```

---

## Port allocation

| Version | Client | Port |
|---|---|---|
| 17.0 | acme | 8069 |
| 17.0 | beta-client | 8070 |
| 16.0 | legacy | 8071 |

Ports are auto-assigned by the dashboard's `next_port()` function. Never hardcode ports.

---

## Upgrading Odoo version

1. Clone the new version repo (see step 1 above)
2. Restore a snapshot of the old database
3. Run the upgrade:
   ```bash
   odoo-bin -c new.conf -d <db> -u all --stop-after-init
   ```
4. Check logs for migration errors
5. Use `/odoo-version-delta` skill to identify fields that need manual migration
