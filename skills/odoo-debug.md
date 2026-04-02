---
name: odoo-debug
description: Debug a running Odoo instance. Tails logs, classifies tracebacks, triggers module upgrades, and proposes targeted fixes. Delegates to the Debugger subagent.
---

You have invoked `/odoo-debug`. Follow these steps using the methodology in `subagents/debugger.md`.

## Step 1 — Identify the target instance

Read `odoo-workspace/workspace.json` and list running instances.
Ask the user which instance to debug if more than one is running.

Load the instance's `odoo.conf` and `.env`.

## Step 2 — Collect logs

Fetch the last 200 lines of the instance log:

```bash
tail -n 200 odoo-workspace/<version>/<client>/odoo.log
```

Or use the dashboard API:
```bash
curl -s http://localhost:7070/instances/<id>/logs?lines=200 | python3 -m json.tool
```

## Step 3 — Classify the error

Look for these patterns (see `subagents/debugger.md` for the full catalog):

| Pattern | Likely cause |
|---|---|
| `ValidationError` | `_sql_constraints` or `@api.constrains` violation |
| `NotNullViolation` | Required field missing in create/write |
| `KeyError` / `AttributeError` on model | Field does not exist; check version |
| `MissingError` | Record deleted or wrong company filter |
| `AccessError` | User lacks group or record rule blocks access |
| XML parse / view error | Malformed `<field>` or `<xpath>` in view XML |

## Step 4 — Trigger upgrade if needed

If the error is in a custom module, upgrade it:

```bash
# Via tool (RPC, instance must be running)
python tools/module_installer.py <module_name> --upgrade

# Via CLI (stops Odoo, safer for structural changes)
python tools/module_installer.py <module_name> --mode cli --instance <id> --upgrade
```

## Step 5 — Propose fix

Present the fix as a unified diff. Do NOT apply it automatically. Example:

```diff
--- a/addons/custom_module/models/sale_order.py
+++ b/addons/custom_module/models/sale_order.py
@@ -42,7 +42,7 @@
-        return self.env['product.product'].browse(ids)
+        return self.env['product.product'].browse(ids).exists()
```

Ask for confirmation before applying.

## Step 6 — Apply fix and verify

After user approves:
1. Apply the patch with the Edit tool
2. Re-run the upgrade (Step 4)
3. Confirm the log is clean (Step 2)
4. Report FIXED or still failing with the new error
