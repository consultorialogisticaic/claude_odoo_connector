# UI Report: account.analytic.plan

**Odoo Version:** 19.0
**Source:** `odoo/addons/analytic/models/analytic_plan.py` (base), `odoo/addons/account/models/account_analytic_plan.py` (account extension)

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `account.analytic.plan` |
| `_description` | `Analytic Plans` |
| `_rec_name` | `complete_name` |
| `_order` | `sequence asc, id` |
| `_parent_store` | `True` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. Triggers `_inverse_name` (syncs dynamic plan columns). |
| `description` | Text | No | — | |
| `parent_id` | Many2one → `account.analytic.plan` | No | — | Hierarchical. Domain: `['!', ('id', 'child_of', id)]`. ondelete=cascade. |
| `complete_name` | Char | — | computed, stored | `Parent / Child` format. Stored, recursive. Used as `_rec_name`. |
| `color` | Integer | No | random 1-11 | |
| `sequence` | Integer | No | 10 | |
| `default_applicability` | Selection | No | `optional` (set via ir.default) | Options: `optional`, `mandatory`, `unavailable`. Company-dependent. |

## Constraints

- No SQL constraints defined on the model itself.
- `_onchange_parent_id`: Prevents adding a parent to the base "Project" plan (raises `UserError`).
- The "Project" plan is special: its ID is stored in `ir.config_parameter` `analytic.project_plan` and cannot have a parent.

## create() / write() Overrides

- **write()**: When `parent_id` changes, updates analytic line column references via `_update_accounts_in_analytic_lines`. Calls `_sync_plan_column` to create/delete dynamic fields on models inheriting `analytic.plan.fields.mixin`.
- **unlink()**: Removes dynamic fields created for the plan.
- **_inverse_name** / **_inverse_parent_id**: Both trigger `_sync_all_plan_column()` which creates or renames dynamic fields across all analytic mixin models.

## Demo Data Patterns

From `analytic/data/analytic_data.xml`:
- A default "Project" plan is created with `default_applicability=optional`.

From `analytic/data/analytic_account_demo.xml`:
- "Departments" plan (`default_applicability=optional`)
- "Internal" plan (`default_applicability=unavailable`)

## CSV Recommendations

- **Do NOT create the "Project" plan** -- it is auto-created by the module. Only create additional plans.
- Keep `name` unique per level (there is no SQL unique constraint but `complete_name` is the display name).
- Use `sequence` to control ordering.
- For hierarchical plans, load parent rows first.

## Identity Key

`name` (unique at root level; for sub-plans use compound `parent_id` + `name`)

## Recommended Identity Key for csv_loader

```
"account.analytic.plan": ["name"]
```
