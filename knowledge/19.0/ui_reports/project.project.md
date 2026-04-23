# UI Report: project.project

**Odoo Version:** 19.0
**Source:** `odoo/addons/project/models/project_project.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.project` |
| `_description` | `Project` |
| `_inherit` | `portal.mixin`, `mail.alias.mixin`, `rating.parent.mixin`, `mail.activity.mixin`, `mail.tracking.duration.mixin`, `analytic.plan.fields.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, name, id` |
| `_track_duration_field` | `stage_id` |

## Fields for CSV

Focused on CSV-relevant creation fields. The model has 60+ fields; the remainder are computed, technical, or counters.

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable, indexed (trigram). `default_export_compatible=True`. |
| `description` | Html | No | — | Free-form project description. |
| `active` | Boolean | No | `True` | |
| `sequence` | Integer | No | `10` | |
| `partner_id` | Many2one → `res.partner` | No | — | Customer. Domain restricts to matching or company-less partners. Tracked. |
| `user_id` | Many2one → `res.users` | No | current user | "Project Manager". Domain: non-share users only (form view). |
| `company_id` | Many2one → `res.company` | No (computed) | partner's / account's company | Computed from `account_id.company_id` or `partner_id.company_id`, but writable. |
| `stage_id` | Many2one → `project.project.stage` | No | lowest-sequence stage | Visible only with group `project.group_project_stages`. Must share company with the project (constraint). |
| `privacy_visibility` | Selection | Yes | `portal` | `followers` (invited internal), `invited_users` (invited internal + portal), `employees` (all internal), `portal` (all internal + invited portal). |
| `allow_milestones` | Boolean | No | `False` | Feature toggle; implies `project.group_project_milestone` on `base.group_user`. See Feature Toggles below. |
| `allow_task_dependencies` | Boolean | No | `False` | Feature toggle; implies `project.group_project_task_dependencies`. |
| `allow_recurring_tasks` | Boolean | No | `False` | Feature toggle; implies `project.group_project_recurring_tasks`. |
| `account_id` | Many2one → `account.analytic.account` | No | — | Analytic account. Domain: `company_id` must match (and with `hr_timesheet`, `partner_id` must match). Auto-created by `create()` if `hr_timesheet` installed and `allow_timesheets=True`. |
| `date_start` | Date | Conditional | — | Planned start. Form requires it when `date` is set. |
| `date` | Date | Conditional | — | Planned expiration / end. Constraint: `date >= date_start`. |
| `label_tasks` | Char | No | `"Tasks"` | Translatable. What tasks are called in the UI (e.g. "Tickets"). Reset to `"Tasks"` if blanked out in `create()`. |
| `color` | Integer | No | `0` | |
| `tag_ids` | Many2many → `project.tags` | No | — | |
| `type_ids` | Many2many → `project.task.type` | No | — | Task stages for this project. On `name_create`, a "New" task stage is auto-created. |
| `favorite_user_ids` | Many2many → `res.users` | No | — | Users who favorited the project. Use `is_favorite` in forms (computed, writable via `_set_favorite_user_ids`). |
| `is_favorite` | Boolean | No | computed | Convenience; in `create()`, if truthy, adds current user to `favorite_user_ids`. |
| `resource_calendar_id` | Many2one → `resource.calendar` | No | computed | Related to company calendar; read-only. |
| `alias_name` | Char | No | — | Email alias local-part (inherited from `mail.alias.mixin`). Combined with `alias_domain_id` gives `alias_email`. |
| `alias_domain_id` | Many2one → `mail.alias.domain` | No | — | |
| `alias_contact` | Selection | No | — | Who can post by email to the alias. |
| `is_template` | Boolean | No | `False` | Marks the project as a template. |
| `last_update_status` | Selection | Yes | `to_define` | `on_track`, `at_risk`, `off_track`, `on_hold`, `to_define`, `done`. Writing a non-`to_define` value via `write()` creates a `project.update` record (side effect). |

### Fields added by common extensions

| Field | Added by | Type | Default | Notes |
|---|---|---|---|---|
| `allow_timesheets` | `odoo/addons/hr_timesheet/models/project_project.py` | Boolean | `True` | Installing `hr_timesheet` turns this on for new projects. Triggers analytic-account auto-creation. See Constraints. |
| `allocated_hours` | `odoo/addons/hr_timesheet/models/project_project.py` | Float | `0.0` | Allocated budget time, tracked. |
| `allow_billable` | `odoo/addons/sale_project/models/project_project.py` | Boolean | `False` | Enables "Billable" behaviour; required for `sale_line_id` and invoicing integration. |
| `sale_line_id` | `odoo/addons/sale_project/models/project_project.py` | Many2one → `sale.order.line` | computed | Cleared if `partner_id` changes or does not match. |
| `reinvoiced_sale_order_id` | `odoo/addons/sale_project/models/project_project.py` | Many2one → `sale.order` | — | Domain: `partner_id` must match. |
| `pricing_type` | `odoo/addons/sale_timesheet/models/project_project.py` | Selection | `task_rate` | `task_rate`, `fixed_rate`, `employee_rate`. Computed from `sale_line_id`/`sale_line_employee_ids`. |
| `timesheet_product_id` | `odoo/addons/sale_timesheet/models/project_project.py` | Many2one → `product.product` | `sale_timesheet.time_product` | Must be a `service` product with `invoice_policy='delivery'`, `service_type='timesheet'`. |
| `billing_type` | `odoo/addons/sale_timesheet/models/project_project.py` | Selection | `not_billable` | `not_billable`, `manually`. |
| `is_fsm` | `enterprise/industry_fsm/models/project_project.py` | Boolean | `False` | Marks as Field Service project. |
| `allow_geolocation` | `enterprise/industry_fsm/models/project_project.py` | Boolean | computed | Only meaningful when `is_fsm=True` and `allow_timesheets=True`. |
| `allow_material` | `enterprise/industry_fsm_sale/models/project_project.py` | Boolean | computed | Requires `allow_billable=True` (SQL constraint). |
| `allow_quotations` | `enterprise/industry_fsm_sale/models/project_project.py` | Boolean | computed | |
| `hide_price` | `enterprise/industry_fsm_sale/models/project_project.py` | Boolean | `False` | |
| `documents_folder_id` | `enterprise/documents_project/models/project_project.py` | Many2one → `documents.document` | — | Attached documents folder. |

## Feature Toggles (Boolean fields that gate modules / groups)

| Field | Effect |
|---|---|
| `allow_milestones` | Adds `project.group_project_milestone` to all users when any project has it `True`; removed otherwise. Not a module install. |
| `allow_task_dependencies` | Adds `project.group_project_task_dependencies`; toggles `project.mt_task_waiting` / `project.mt_project_task_waiting` subtype visibility. Disabling it rewrites waiting tasks to `01_in_progress`. |
| `allow_recurring_tasks` | Adds `project.group_project_recurring_tasks`. Disabling it clears `recurring_task` on the project's tasks. |
| `allow_timesheets` | Only meaningful if `hr_timesheet` is installed. Enabling it on `create()` or `write()` auto-creates an `account.analytic.account` when none is provided. Enforced by `_check_allow_timesheet` constraint. |
| `allow_billable` | Only meaningful if `sale_project` is installed. Unlocks `sale_line_id`, `reinvoiced_sale_order_id`, and sales reporting stat buttons. |
| `is_fsm` | Only meaningful if `industry_fsm` is installed. Default stages and FSM behaviour differ. |
| `allow_material`, `allow_quotations` | Only meaningful if `industry_fsm_sale` is installed. SQL check constraints tie them to `allow_billable` / `allow_timesheets` / `is_fsm`. |

**WARNING**: Unlike `helpdesk.team`, these toggles do **not** trigger module installations — they only toggle user-group membership via `_check_project_group_with_field`. But their meaning depends entirely on which modules are already installed. Setting `allow_billable=True` without `sale_project` installed writes to a column that doesn't exist; setting `is_fsm=True` without `industry_fsm` installed is similarly a no-op. Only set toggles for modules you know are installed.

## Constraints

- SQL: `check(date >= date_start)` — "The project's start date must be before its end date." (base model).
- `@api.constrains('stage_id') _ensure_stage_has_same_company`: `stage_id.company_id` (if set) must equal `company_id`.
- `_inverse_company_id` (fires on `company_id` write): the project's company must match `partner_id.company_id` when the partner has a company; raises `UserError` otherwise. Also refuses to change `company_id` when the attached analytic account has analytic lines or is shared with another project.
- `_check_allow_timesheet` (added by `hr_timesheet`): if `allow_timesheets=True` and `is_template=False`, `account_id` is required — raises `ValidationError` otherwise. Note that `create()` defends against this by pre-creating the analytic account.
- SQL (added by `industry_fsm_sale`):
  - `allow_material` requires `allow_billable`.
  - Combinations of `allow_billable`, `allow_timesheets`, `is_fsm`, and `timesheet_product_id` are constrained (see file).

## create() / write() Overrides

- **`create()`** (`project_project.py:585`):
  - Forces `mail_create_nosubscribe` context.
  - Normalizes blank `label_tasks` back to `"Tasks"`.
  - If the user has `project.group_project_stages`, auto-picks `stage_id` from the stages scoped to the project's company (lowest `sequence`).
  - Pops `is_favorite` from vals and converts it into `favorite_user_ids = [uid]`.
  - **Side effect (hr_timesheet)**: if `allow_timesheets=True` and no `account_id` was provided (and not a template), auto-creates an `account.analytic.account` with `{name: project.name, company_id, partner_id, plan_id: project_plan}` and assigns it. This happens **before** `super().create()` to avoid the `_check_allow_timesheet` ValidationError.
  - **Side effect (`name_create`)**: creates a `"New"` `project.task.type` and links it via `type_ids`.

- **`write()`** (`project_project.py:620`):
  - If `company_id` changes and stages are enabled, automatically re-picks a compatible `stage_id`.
  - If `last_update_status` is changed to any non-`to_define` value, **creates a `project.update` record** with the date-formatted name and that status, then pops the value out of vals. This is a significant side effect — do not write `last_update_status` casually.
  - If `privacy_visibility` is changed, `_change_privacy_visibility` subscribes / unsubscribes portal users and resets `access_token` when leaving `portal`/`invited_users`.
  - `date_start` / `date` interact: blanking one blanks both; setting only one when neither existed is discarded.
  - Toggling `active` cascades to all the project's tasks.
  - Changing `name` renames the attached analytic account (only if the project uniquely owns it).
  - Toggling `allow_timesheets` on (hr_timesheet) also auto-creates an analytic account if missing.
  - Toggling `allow_task_dependencies` off rewrites waiting tasks back to `01_in_progress`.
  - Toggling `allow_recurring_tasks` off clears `recurring_task` on tasks.

- **`unlink()`**:
  - Deletes the project's tasks (including archived ones), then the project.
  - Deletes the attached analytic account **only if** it has no analytic lines.
  - Deletes `res.users.settings.embedded.action` rows linked to the project.

- **`copy()` / `copy_data()`**: appends `(copy)` to the name unless copying from a template. `milestone_ids` not copied by default. Shared embedded actions and their configs are duplicated. Templates set `partner_id=False` by default (blacklist in `_get_template_field_blacklist`).

## Demo Data Patterns

From `odoo/addons/project/data/project_demo.xml`:

```xml
<record id="project_project_1" model="project.project">
    <field name="name">Office Design</field>
    <field name="date_start" eval="DateTime.today() - relativedelta(weeks=9)"/>
    <field name="date" eval="DateTime.today() + relativedelta(weekday=4,weeks=1)"/>
    <field name="color">3</field>
    <field name="user_id" ref="base.user_demo"/>
    <field name="partner_id" ref="base.partner_demo_portal"/>
    <field name="privacy_visibility">portal</field>
    <field name="stage_id" ref="project.project_project_stage_1"/>
    <field name="account_id" ref="project.analytic_office_design"/>
    <field name="type_ids" eval="[Command.link(ref('project_stage_0')), ...]"/>
    <field name="favorite_user_ids" eval="[Command.link(ref('base.user_admin'))]"/>
    <field name="tag_ids" eval="[Command.link(ref('project.project_tags_05'))]"/>
    <field name="allow_milestones" eval="True"/>
    <field name="allow_recurring_tasks" eval="True"/>
    <field name="allow_task_dependencies" eval="True"/>
</record>
```

Observations:
- Every demo project sets `privacy_visibility` explicitly — values used: `portal`, `followers`, `employees`.
- `account_id` is set explicitly rather than relying on `hr_timesheet` auto-creation.
- `stage_id` is always set when the `group_project_stages` group is expected.
- `type_ids` always links the 4 default `project.task.type` stages.
- A template project (`project_template_1`) sets `is_template=True` and no `partner_id`.
- The default project stages live in `odoo/addons/project/data/project_data.xml` (`project_project_stage_0`..`_3`, `noupdate="1"`).

## CSV Recommendations

- **Default stages**: `project.project.stage` records `project_project_stage_0..3` are installed as data (`noupdate="1"`). Reference them by XML ID rather than creating new stages.
- **Default task stages**: `project.task.type` `project_stage_0..3` exist in the module. When setting `type_ids`, reuse them.
- **`account_id` strategy**: If `hr_timesheet` is installed and `allow_timesheets=True`, omitting `account_id` triggers auto-creation of a new analytic account per row. For CSV reproducibility, prefer **explicitly linking an existing analytic account** so reloads don't create duplicate accounts.
- **`privacy_visibility`**: Always set it explicitly in CSV — the default `portal` subscribes the customer and tasks' partners on privacy changes via `write()`, which is a non-trivial side effect if mass-updating.
- **`last_update_status`**: Do not set via CSV unless you want a `project.update` record created per row. Leave at default `to_define`.
- **`is_favorite`**: Do not use in CSV — it would favorite under the loader's user. Use `favorite_user_ids` explicitly if needed.
- **`label_tasks`**: Blank/null is normalized to `"Tasks"`. Set it to something meaningful (e.g. `"Tickets"`) or omit the column.
- **`company_id`**: Let it compute from `partner_id`/`account_id` unless you specifically need a different company. Mismatches raise `UserError`.
- **Feature toggles**: Only set `allow_*` / `is_fsm` toggles whose implementing modules are installed in the target DB; otherwise the columns may not exist.
- **Onchange gotcha (`_onchange_company_id`)**: If you change `company_id` and the current `stage_id` is company-specific, the UI reassigns the stage. The CSV loader does not fire onchanges — either set a compatible `stage_id` in the same row or leave `stage_id` out and let `create()` pick one.

## Recommended Identity Key for csv_loader

```
"project.project": ["name", "company_id"]
```

`name` is required but not unique across companies (two companies can each have their own "Internal"). Use the compound key to avoid cross-company collisions. For single-company databases, `["name"]` alone is sufficient.
