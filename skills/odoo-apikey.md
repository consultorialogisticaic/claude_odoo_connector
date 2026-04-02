---
name: odoo-apikey
description: Reference for Odoo API key auto-generation. Documents how keys are created after instance start and manual fallback steps.
---

# Odoo API Key Management

## How auto-generation works

When an instance is started from the dashboard, the system automatically:

1. Waits for Odoo to become responsive (polls XML-RPC `/xmlrpc/2/common` for up to 120s)
2. Runs `odoo-bin shell` to reset the admin password to `admin` and generate an API key
3. Writes the key to the instance's `.env` file as `ODOO_API_KEY=<key>`

This happens in a background thread — the instance is usable immediately, and the key
appears in the Info card on the instance detail page within a few seconds of Odoo starting.

The generation is skipped if `ODOO_API_KEY` already has a value in `.env`.

## Manual generation

If auto-generation fails (e.g., restored database with non-standard user setup):

### Via dashboard
Click the **Retry** / **Generate** button in the Info card on the instance detail page.

### Via API
```bash
curl -X POST http://localhost:7070/instances/<instance_id>/generate-apikey
# Check status:
curl http://localhost:7070/instances/<instance_id>/apikey-status
```

### Via odoo-bin shell (direct)
```bash
# Activate the instance's conda env
conda activate odoo-<instance_id>

# Run shell
odoo-workspace/<version>/odoo/odoo-bin shell \
  -d <db_name> \
  -c odoo-workspace/<version>/<client>/odoo.conf \
  --no-http
```

Then in the shell:
```python
user = env['res.users'].browse(2)
user.password = 'admin'
key = env['res.users.apikeys']._generate('odoo-demo-creator', user.id)
print(key)
env.cr.commit()
```

Copy the printed key into `ODOO_API_KEY=` in the instance `.env` file.

## Troubleshooting

- **"Odoo did not become responsive"** — instance may have crashed on startup. Check logs.
- **"Could not extract API key"** — the `odoo-bin shell` command failed. Check the error
  message for Python tracebacks. Common cause: missing Python dependencies (run env setup).
- **Key works for some tools but not others** — verify all tools are reading from the same
  `.env` file. Check the symlink at `odoo-workspace/.env`.
