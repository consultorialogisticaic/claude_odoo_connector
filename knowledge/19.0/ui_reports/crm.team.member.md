# UI Report: crm.team.member

**Odoo Version:** 19.0
**Source:** `odoo/addons/sales_team/models/crm_team_member.py`
**Extension:** `odoo/addons/crm/models/crm_team_member.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.team.member` |
| `_description` | `Sales Team Member` |
| `_inherit` | `mail.thread` |
| `_rec_name` | `user_id` |
| `_order` | `create_date ASC, id` |
| `_check_company_auto` | `True` |

Note: `_rec_name = 'user_id'` means `display_name` resolves through the `res.users` name. The model has a `name` field, but it is a writable `related='user_id.display_name'` — not a standalone identity field.

## Fields for CSV

### Base fields (`sales_team`)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `crm_team_id` | Many2one → `crm.team` | Yes | `False` | `ondelete="cascade"`, `check_company=False`, `index=True`. Default is intentionally `False` ("TDE: temporary fix to activate depending computed fields"). |
| `user_id` | Many2one → `res.users` | Yes | — | `ondelete='cascade'`, `check_company=True`, `index=True`. Domain: `[('share', '=', False), ('id', 'not in', user_in_teams_ids), ('company_ids', 'in', user_company_ids)]` — internal (non-portal) users in the team's company. |
| `active` | Boolean | No | `True` | Archive flag. Archived memberships may coexist with an active duplicate (see constraint). |
| `name` | Char | No | computed | `related='user_id.display_name'`, writable. Do not set in CSV — derived from the user. |
| `email` | Char | No | computed | `related='user_id.email'`. Read-only via related. |
| `phone` | Char | No | computed | `related='user_id.phone'`. Read-only via related. |
| `company_id` | Many2one → `res.company` | No | computed | `related='user_id.company_id'`. |
| `image_1920` | Image | No | computed | `related='user_id.image_1920'`. |
| `image_128` | Image | No | computed | `related='user_id.image_128'`. |
| `user_in_teams_ids` | Many2many → `res.users` | No | computed | UX-only; drives the `user_id` domain. Never set in CSV. |
| `user_company_ids` | Many2many → `res.company` | No | computed | UX-only; drives the `user_id` domain. Never set in CSV. |
| `is_membership_multi` | Boolean | No | computed | Reads `ir.config_parameter` `sales_team.membership_multi`. Never set in CSV. |
| `member_warning` | Text | No | computed | UX warning when creating a member who already belongs to other teams. Never set in CSV. |

### Extension fields (`crm`)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `assignment_enabled` | Boolean | No | computed | `related='crm_team_id.assignment_enabled'`. Read-only via related. |
| `assignment_optout` | Boolean | No | `False` | Pause lead assignment for this member. |
| `assignment_max` | Integer | No | `30` | Average leads capacity on 30 days. Daily quota = `round(assignment_max / 30)`. |
| `assignment_domain` | Char | No | — | Text-serialized domain on `crm.lead`. `tracking=True`. Validated with `literal_eval` + `crm.lead.search(..., limit=1)`. |
| `assignment_domain_preferred` | Char | No | — | Text-serialized "priority" domain on `crm.lead`. `tracking=True`. Validated the same way. |
| `lead_day_count` | Integer | No | computed | Assigned leads in last 24h. Never set in CSV. |
| `lead_month_count` | Integer | No | computed | Assigned leads in last 30 days. Never set in CSV. |

## Constraints

- `_constrains_membership` (on `crm_team_id`, `user_id`, `active`): in mono-membership mode (`ir.config_parameter` `sales_team.membership_multi` falsy), no two **active** memberships may share the same `(user_id, crm_team_id)` pair. Archived duplicates are allowed — which is why there is **no SQL unique constraint**. Raises `ValidationError` listing the conflicting pairs.
- `_constrains_company_membership` (on `crm_team_id`, `user_id`): if the team has a `company_id`, that company must appear in `user_id.company_ids`. Raises `UserError`.
- `_constrains_assignment_domain` / `_constrains_assignment_domain_preferred` (crm extension): domain must parse via `literal_eval` and be a valid search domain on `crm.lead`. Raises `ValidationError` on malformed domain.

There are **no `_sql_constraints`** on this model. Identity is enforced in Python only.

## create() / write() Overrides

- **create()** (`sales_team`, `@api.model_create_multi`): in mono-membership mode, calls `_synchronize_memberships(vals_list)` **before** `super().create()`, which archives any other active membership for each `user_id` on a different team. Adds `mail_create_nosubscribe=True` to the context — team members are not auto-subscribed as followers on create.
- **write()** (`sales_team`): if `vals` contains `active=True` and mono-membership mode is active, re-runs `_synchronize_memberships` against the current `(user_id, crm_team_id)` pairs to archive other active memberships for those users. Manual edits to `user_id` / `team_id` on an existing membership are explicitly **not supported** (comment: "This either works, either crashes").
- `_synchronize_memberships(user_team_ids)`: helper that calls `action_archive()` on conflicting active memberships. Side-effect: other `crm.team.member` rows get `active=False`.

## Demo Data Patterns

From `odoo/addons/sales_team/data/crm_team_data.xml` (noupdate="1", module data — not demo):
```xml
<record id="crm_team_member_admin_sales" model="crm.team.member" forcecreate="0">
    <field name="crm_team_id" ref="team_sales_department"/>
    <field name="user_id" ref="base.user_admin"/>
</record>
```

From `odoo/addons/sales_team/data/crm_team_demo.xml` (noupdate="1"):
```xml
<record id="crm_team_member_demo_team_1" model="crm.team.member">
    <field name="user_id" ref="base.user_demo"/>
    <field name="crm_team_id" ref="sales_team.crm_team_1"/>
</record>
```

From `odoo/addons/crm/data/crm_team_member_demo.xml` (noupdate="1") — crm extends the existing rows with assignment tuning:
```xml
<record id="sales_team.crm_team_member_admin_sales" model="crm.team.member">
    <field name="assignment_max">30</field>
    <field name="assignment_domain">[['probability', '>=', 20]]</field>
</record>
<record id="sales_team.crm_team_member_demo_team_1" model="crm.team.member">
    <field name="assignment_max">45</field>
    <field name="assignment_domain">[['probability', '>=', 5]]</field>
</record>
```

The canonical pattern is: create the membership with just `(user_id, crm_team_id)` first, then layer `assignment_*` fields in a second pass (or in the same dict — both work).

## UI Creation Flow (form view: `sales_team.crm_team_member_view_form`)

1. Click "New" on the Team Members action (`sales_team.crm_team_member_action`, views `kanban,list,form`).
2. Pick `user_id` (the only visible required field in the header). Domain hides: portal/share users, users already in some team (mono-mode), and users not in the team's company.
3. Pick `crm_team_id` in the `crm_team_id` group. If the form was opened **from a team** (`sales_team.crm_team_member_view_form_from_team`), this group is removed and `crm_team_id` comes from `default_crm_team_id` context.
4. If `user_id` already belongs to other teams (mono-mode), `member_warning` is shown with an inline button to switch to multi-team mode (`crm_team_activate_multi_membership`).
5. (crm) In the "Lead Assignment" notebook page:
   - Toggle `assignment_optout` to pause assignment.
   - If `assignment_enabled` (team-level) and `assignment_max > 0` and not opted out, fill `assignment_domain_preferred` and `assignment_domain` via the domain widget on `crm.lead`.
6. Save — `create()` auto-archives any other active membership for this user in mono-mode.

The list view (`sales_team.crm_team_member_view_tree`) shows `crm_team_id, user_id`; crm appends `assignment_optout, assignment_max, lead_month_count`.

The kanban is `default_group_by="crm_team_id"`, `quick_create="false"`, `group_create="0"`.

## CSV Recommendations

- Always set `user_id` and `crm_team_id` together — both are `required=True` and the two `@api.constrains` fire on both.
- Do not attempt to set `name`, `email`, `phone`, `company_id`, `image_1920`, `image_128` — they are `related` to `user_id` and will be overwritten on save.
- In mono-membership mode, loading a new `(user_id, team_B)` pair will **silently archive** the existing `(user_id, team_A)` membership. If the loader re-runs and recreates `(user_id, team_A)`, it will archive `(user_id, team_B)`. This can thrash. Check `ir.config_parameter sales_team.membership_multi` before loading multi-team memberships.
- `assignment_domain` and `assignment_domain_preferred` must be stored as the **string form** of a list of tuples (e.g. `"[['probability', '>=', 20]]"`) — they are `Char`, not `Serialized`. An empty string or absent value is treated as `[]`.
- `assignment_max` defaults to 30; set explicitly if you want a different capacity. A value of `0` hides the assignment domain fields in the UI but is otherwise valid.
- Module data row `sales_team.crm_team_member_admin_sales` uses `forcecreate="0"` — it is **only** created if missing. If you ship a CSV that targets the admin/`team_sales_department` pair, prefer updating the existing xmlid rather than creating a parallel row.
- No `name` field to search on — use compound `(crm_team_id, user_id)` resolution. `name_search` on this model goes through `user_id.display_name` via `_rec_name`, which is ambiguous when a user belongs to multiple teams (multi-mode).

## Recommended Identity Key for csv_loader

```
"crm.team.member": ["crm_team_id", "user_id"]
```

Rationale: there is no SQL unique constraint, but `_constrains_membership` enforces this pair as unique among **active** rows in mono-mode, and it is the only pair that uniquely identifies a membership in practice. `active` is **not** part of the identity key — archived and active rows with the same pair are allowed to coexist, so the loader must decide whether to reactivate an archived row or create a new one.
