# UI Report: project.collaborator

**Odoo Version:** 19.0
**Source:** `addons/project/models/project_collaborator.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.collaborator` |
| `_description` | `Collaborators in project shared` |
| `_inherit` | — (extended by `hr_timesheet` for portal rule toggling) |
| `_rec_name` | `display_name` (computed from `project_id` + `partner_id`; no `name` field) |
| `_order` | default (`id`) |

Junction model linking a portal `res.partner` to a `project.project` whose `privacy_visibility = 'portal'`, granting controlled external (portal) access to that project's tasks. Creating the first row also flips on the portal `ir.model.access` and `ir.rule` records for project sharing (and timesheets, via `hr_timesheet`).

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `project_id` | Many2one → `project.project` | Yes | — | `readonly=True`. Domain: `[('privacy_visibility', '=', 'portal'), ('is_template', '=', False)]`. Parent project MUST be `privacy_visibility='portal'` and not a template. |
| `partner_id` | Many2one → `res.partner` | Yes | — | `readonly=True`. In UI (share wizard) filtered to `partner_share=True` (i.e. portal-facing partners). |
| `partner_email` | Char (related `partner_id.email`) | No | — | Read-only mirror of the partner's email. Do not set in CSV. |
| `limited_access` | Boolean | No | `False` | `False` = full edit on all tasks; `True` = edit only on followed tasks (maps to wizard `access_mode='edit_limited'`). |
| `display_name` | Char (computed) | No | — | `"{project.display_name} - {partner.display_name}"`. Not stored-writable. |

No `name` field exists on this model. `display_name` is computed in `_compute_display_name` (lines 20–23).

## Constraints

- **SQL `_unique_collaborator`** (`project_collaborator.py:15`): `UNIQUE(project_id, partner_id)` — a partner cannot appear twice on the same project. Message: *"A collaborator cannot be selected more than once in the project sharing access. Please remove duplicate(s) and try again."*
- **Implicit via `project_id` domain**: the referenced project must have `privacy_visibility='portal'` and `is_template=False`. The domain is enforced in the UI (share wizard) but not by a Python `@api.constrains`. CSV loads bypassing the UI will succeed at the DB level but the project-sharing security rules only trigger correctly when the project is actually set to portal visibility — otherwise the collaborator record is functionally dead.
- No `@api.constrains` decorators on this model.

## create() / write() / unlink() Overrides

- **`create()`** (`project_collaborator.py:25-31`): `@api.model_create_multi`. Before delegating to `super()`, checks whether ANY `project.collaborator` already exists. If the table was empty, after creation it calls `_toggle_project_sharing_portal_rules(True)` — activating `project.access_project_sharing_task_portal` and `project.project_task_rule_portal_project_sharing` (and, with `hr_timesheet` installed, `hr_timesheet.access_account_analytic_line_portal_user` and `hr_timesheet.timesheet_line_rule_portal_user`). **Side effect: the first CSV row silently re-enables portal sharing ACLs globally.**
- **`write()`**: not overridden.
- **`unlink()`** (`project_collaborator.py:33-39`): after `super().unlink()`, if no collaborator remains, calls `_toggle_project_sharing_portal_rules(False)` disabling the same ACL/ir.rule records. Wiping all rows turns portal project sharing off.
- **`_toggle_project_sharing_portal_rules(active)`** (`project_collaborator.py:41-58`): idempotent enable/disable of the portal sharing `ir.model.access` + `ir.rule` via `sudo().write({'active': active})`.

## Inheritance

- `hr_timesheet/models/project_collaborator.py:7` (`_inherit = 'project.collaborator'`): overrides `_toggle_project_sharing_portal_rules` to also flip the timesheet portal ACL and ir.rule records in lockstep with project sharing.

## Form View

**There is NO dedicated form/list view for `project.collaborator`.** It has no window action, no menu entry, and no top-level form. Records are manipulated exclusively through:

- **`project.share.wizard`** (transient) at `addons/project/wizard/project_share_wizard.py` and `addons/project/wizard/project_share_wizard_views.xml:4-38`. The wizard exposes a One2many to `project.share.collaborator.wizard` (editable list inline) with:
  - `partner_id` — domain `[('id', 'not in', parent.existing_partner_ids), ('partner_share', '=', True)]`, `no_create=True`, `no_open=True`.
  - `access_mode` — Selection: `read` / `edit` / `edit_limited` (wizard-only; does NOT exist on `project.collaborator`).
  - `send_invitation` — Boolean (wizard-only).
- Wizard `action_share_record` / `action_send_mail` translate `access_mode` → write `project.collaborator` rows with `limited_access = (access_mode == 'edit_limited')`. `access_mode='read'` is NOT persisted as a collaborator — `read` partners become simple followers of the project instead.
- The `collaborator_ids` One2many lives on `project.project` (`addons/project/models/project_project.py:151`) so the "native" UI entry point is always the parent project's sharing dialog.

## Demo Data Patterns

The `project` module ships no demo data for `project.collaborator` (no `demo/` entries reference this model). Test fixtures (`addons/project/tests/test_project_sharing.py:78`, `test_project_sharing_ui.py:55`) create rows via the parent project's One2many:

```python
self.project_portal.write({
    'collaborator_ids': [
        Command.create({'partner_id': partner.id, 'limited_access': False}),
    ],
})
```

## UI Creation Flow (as a human would do it)

1. Open a project whose `privacy_visibility='portal'`.
2. Click **Share** → opens `project.share.wizard` (action `project_share_wizard_action`).
3. Add a row: pick a portal `partner_id` (must have `partner_share=True`), choose `access_mode`:
   - `read` → follower only, no `project.collaborator` row created.
   - `edit` → `project.collaborator` row with `limited_access=False`.
   - `edit_limited` → `project.collaborator` row with `limited_access=True`.
4. Click **Share Project** → confirmation form → **Grant Portal Access** triggers `action_send_mail` which persists the collaborator row(s) and sends invitation emails (when `send_invitation=True`).

The CSV loader bypasses this wizard entirely and writes directly to `project.collaborator` — which means no invitation email, no `partner_share` auto-promotion, and no follower subscription. Pre-validate upstream that `partner_id.partner_share = True` and `project_id.privacy_visibility = 'portal'` before loading.

## CSV Recommendations

- Always load `project_id` + `partner_id` + `limited_access` together in a single row; the `project_id` domain is not enforced in code, so a malformed row can create a "dead" collaborator that has no effect.
- Both `project_id` and `partner_id` are declared `readonly=True` in the field definition — the ORM honors the readonly flag only in UI; `create()` via CSV still accepts them.
- Be aware of the **global side effect on first insert**: if the table was empty before your load, the portal sharing ACL/ir.rule (and the timesheet ones with `hr_timesheet` installed) are re-activated. Do not empty/refill this table in production without accepting that toggling.
- The parent project's `privacy_visibility` must already equal `'portal'` when the row is loaded; otherwise security rules scoped on `project_id.collaborator_ids` (see `addons/project/security/project_security.xml:208,230,344`) will silently fail to grant the intended access.
- Resolve `partner_id` by email or explicit XML ID — `partner_id.partner_share` should be `True` for the collaborator to actually reach the portal project sharing UI.
- Do not include `display_name` or `partner_email` in CSV (computed / related).

## Recommended Identity Key for csv_loader

This model has no `name` field. Identity is the compound of the two FKs, enforced by the DB-level `UNIQUE(project_id, partner_id)` constraint.

```
"project.collaborator": ["project_id", "partner_id"]
```
