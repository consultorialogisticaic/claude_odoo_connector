# UI Report: project.task

**Odoo Version:** 19.0
**Source:** `addons/project/models/project_task.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.task` |
| `_description` | `Task` |
| `_inherit` | `portal.mixin`, `mail.thread.cc`, `mail.activity.mixin`, `rating.mixin`, `mail.tracking.duration.mixin`, `html.field.history.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `priority desc, sequence, date_deadline asc, id desc` |
| `_date_name` | `date_assign` |
| `_mail_post_access` | `read` |
| `_track_duration_field` | `stage_id` |
| `_primary_email` | `email_from` |

Form view: `addons/project/views/project_task_views.xml` (`view_task_form2`, line 322).

## Fields for CSV

Focused on fields that matter for CSV creation. The model has 100+ fields counting extensions; the ones below are the ones a CSV loader will realistically set.

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | `required=True`, `index='trigram'`, tracked. Task title. If empty but `display_name` is set, `create()` copies `display_name` into `name` (line 1124). `project_todo` further auto-fills `name` from `description` or `"Untitled to-do"` when both `project_id` and `parent_id` are empty (`addons/project_todo/models/project_task.py:12`). |
| `project_id` | Many2one → `project.project` | Conditional | computed from `parent_id.project_id` | `required="parent_id or child_ids or is_template"` (view line 422). If blank the task is a **private task** (see `_private_task_has_no_parent` constraint). Precomputed, store=True, recursive. Domain filters by `company_id`. Tracking. |
| `stage_id` | Many2one → `project.task.type` | No | computed via `_get_default_stage_id` / `_compute_stage_id` | Kanban stage. Domain: `[('project_ids', '=', project_id)]`. In `create()`: if `project_id` is set and no stage passed, default is resolved via `default_get(['stage_id'])` per project (line 1137-1145). If `project_id` is empty, `stage_id` is forced to `False` (line 1134). `ondelete='restrict'`. |
| `state` | Selection | Yes | `'01_in_progress'` | Values: `01_in_progress`, `02_changes_requested`, `03_approved`, `1_done`, `1_canceled`, `04_waiting_normal`. Compute+store+inverse — see "State vs stage_id" below. `default_get()` rewrites `04_waiting_normal` → `01_in_progress` on create (line 996). |
| `user_ids` | Many2many → `res.users` | No | current user (only when `default_personal_stage_type_ids` in context) | `relation='project_task_user_rel'`. Domain `[('share', '=', False), ('active', '=', True)]` — internal users only. Tracked. If `user_ids` is set at create, `date_assign` is auto-filled (line 1117). |
| `partner_id` | Many2one → `res.partner` | No | inherited from `project_id.partner_id` or `parent_id.partner_id` | Compute+store+readonly=False. `_get_default_partner_id()` picks parent's partner first, then project's. Domain enforces same-company. `btree_not_null` index. Tracked. |
| `date_deadline` | Datetime | No | — | Deadline. Tracked. In `project_enterprise`, must be `>= planned_date_begin` (SQL `_planned_dates_check`). |
| `priority` | Selection | No | `'0'` | `0=Low`, `1=Medium`, `2=High`, `3=Urgent`. Tracked. |
| `tag_ids` | Many2many → `project.tags` | No | parent's `tag_ids` if `parent_id` set at create | Widget: `many2many_tags`. CSV: comma-separated tag names (resolved via `name_search`). |
| `parent_id` | Many2one → `project.task` | No | — | Parent task for sub-tasks. Domain: `['!', ('id', 'child_of', id)]` (no cycles). Cycle check via `_check_parent_id` using `_has_cycle()`. Tracked. When a parent is set, subtask's `display_in_project` is inverted (`_inverse_parent_id`). |
| `milestone_id` | Many2one → `project.milestone` | No | parent task's milestone if same project | Compute+store+readonly=False. Domain: `[('project_id', '=', project_id)]`. Tracked. `write()` resets invalid milestones when project changes (line 1217-1231). |
| `sequence` | Integer | No | `10` | Manual ordering within a stage/kanban. |
| `allocated_hours` | Float | No | `0.0` | Renamed from legacy `planned_hours`. Tracked. Visible only via `hr_timesheet` / `project_enterprise`. |
| `description` | Html | No | — | `sanitize_attributes=False`. Versioned via `html.field.history.mixin`. |
| `company_id` | Many2one → `res.company` | No | project's company or context default | Compute+store+readonly=False, recursive. Validated against `partner_id.company_id` (see constraints). |
| `active` | Boolean | No | `True` | Archive flag. |
| `color` | Integer | No | `0` | Kanban color. |
| `recurring_task` | Boolean | No | `False` | If `True` with any `repeat_*` field in vals, `create()` creates a `project.task.recurrence` and writes `recurrence_id` (line 1151-1156). Incompatible with `parent_id` (constraint `_recurring_task_has_no_parent`). |
| `recurrence_id` | Many2one → `project.task.recurrence` | No | — | Auto-created in `create()` — never set this directly in CSV. |
| `repeat_interval` | Integer | Conditional | 1 | `required="recurring_task"` in form. |
| `repeat_unit` | Selection | Conditional | `'week'` | `day/week/month/year`. |
| `repeat_type` | Selection | Conditional | `'forever'` | `forever/until`. |
| `repeat_until` | Date | Conditional | today + 7d | `required="repeat_type == 'until'"`. |
| `depend_on_ids` | Many2many → `project.task` | No | — | Self-M2M via relation `task_dependencies_rel` (`column1='task_id'`, `column2='depends_on_id'`). "Blocked By". Tracked. Cycles rejected by `_check_no_cyclic_dependencies`. |
| `email_from` | Char | No | — | Primary email for mail gateway. |
| `email_cc` | Char | No | — | Auto-subscribed as followers when matching partners exist. |
| `displayed_image_id` | Many2one → `ir.attachment` | No | — | Cover image. Domain scoped to this task's attachments. |

### Fields you should NOT set in CSV

- `date_assign`, `date_end`, `date_last_stage_update` — computed/auto-set in `create()` / `write()`.
- `recurrence_id` — created by `create()` when `recurring_task=True`.
- `personal_stage_id`, `personal_stage_type_id`, `personal_stage_type_ids` — per-user state, managed by `_populate_missing_personal_stages()`.
- `display_name` — inverse parses `#tag @user !/!!/!!!` shortcuts; setting it will mutate `name`, `tag_ids`, `user_ids`, `priority`.
- `portal_user_names`, `subtask_*`, `working_*`, `dependent_tasks_count`, `depend_on_count`, `recurring_count`, `has_*`, `stage_id_color`, `is_closed` — all computed.

## State vs stage_id (read this before generating CSV)

`project.task` has **two separate status fields** and they are not the same thing:

- `stage_id` → `project.task.type` record. This is the **kanban column** (e.g. "New", "In Progress", "Done"). Set per project via `project_id.type_ids`. Shown in the form header as a statusbar. Default is resolved at create-time from the project's first non-folded stage. `ondelete='restrict'`.
- `state` → `Selection` on the task itself. Workflow status independent of the kanban layout. Values:
  - `01_in_progress` — default, "In Progress"
  - `02_changes_requested` — "Changes Requested"
  - `03_approved` — "Approved"
  - `1_done` — "Done" (closed)
  - `1_canceled` — "Cancelled" (closed)
  - `04_waiting_normal` — "Waiting" (computed-only — task is blocked by an open `depend_on_ids`)

Interaction rules (from `_compute_state`, line 386):
- `state` is **computed and stored** with `readonly=False`. The compute runs on dependency changes: if any `depend_on_ids` is open and current state is not closed, it forces `04_waiting_normal`; if all dependencies are closed and state is `04_waiting_normal`, it falls back to `01_in_progress`.
- `default_get()` rejects `04_waiting_normal` on create (line 996) — never set this value in CSV.
- `_onchange_project_id` resets to `01_in_progress` when the project changes (UI only, not triggered by CSV).
- The two closed states (`1_done`, `1_canceled`) gate several behaviours (subtask visibility, rotting, recurrence next-occurrence creation via `_inverse_state`).

For CSV: set `state` to one of `01_in_progress`, `02_changes_requested`, `03_approved`, `1_done`, `1_canceled`. Set `stage_id` explicitly only if you don't want the project's default folded-first stage.

## Subtasks (parent_id / child_ids)

- `parent_id` is a Many2one to self; `child_ids` is the reverse One2many with `domain=[('recurring_task', '=', False)]`.
- **No explicit depth limit in the code.** The only guard is `_check_parent_id` / `_has_cycle()` which forbids cycles.
- A sub-task must have a project if the parent has subtasks: the constraint `_ensure_super_task_is_not_private` raises if a task has `subtask_count > 0` and `project_id IS NULL`.
- SQL constraint `_private_task_has_no_parent`: a task with `project_id IS NULL` cannot have a `parent_id`.
- In `default_get()`, when `parent_id` is set at create, `tag_ids` is copied from the parent (line 1023-1027).
- In `create()`, when no `default_project_id` is in context and exactly one parent is referenced across the batch, the parent's project is used as the default (line 1099-1102).
- Load sub-tasks **after** their parents. `parent_id` is not computed, so it must be resolved to an existing task id at load time.

## Recurrence side effect

If a CSV row has `recurring_task=True` **and** any of `repeat_interval`, `repeat_unit`, `repeat_type`, `repeat_until` in the payload, `create()` will:
1. Build `rec_values` from those keys.
2. Call `self.env['project.task.recurrence'].create(rec_values)`.
3. Assign `vals['recurrence_id']` to the new recurrence.

This happens **once per task** — each recurring task gets its own `project.task.recurrence` record. Do not pre-create recurrences and do not set `recurrence_id` in the CSV.

Also: `recurring_task=True` requires `parent_id IS NULL` (SQL constraint `_recurring_task_has_no_parent`).

## Constraints

Python `@api.constrains`:
- `_ensure_company_consistency_with_partner` (line 342): `partner_id.company_id` must match `company_id` when both are set.
- `_ensure_super_task_is_not_private` (line 349): a task with children cannot have `project_id=False`.
- `_check_no_cyclic_dependencies` (line 498): `depend_on_ids` must be acyclic (uses `_has_cycle`).
- `_check_parent_id` (line 580): `parent_id` must be acyclic.

SQL-level `models.Constraint`:
- `_recurring_task_has_no_parent`: `CHECK (NOT (recurring_task IS TRUE AND parent_id IS NOT NULL))`.
- `_private_task_has_no_parent`: `CHECK (NOT (project_id IS NULL AND parent_id IS NOT NULL))`.
- In `project_enterprise`: `_planned_dates_check` — `CHECK (planned_date_begin <= date_deadline)` (`enterprise/project_enterprise/models/project_task.py:41`).

Extension constraints:
- `hr_timesheet._check_project_root` (`addons/hr_timesheet/models/project_task.py:60`): a task cannot become private (`project_id=False`) if timesheets are linked to it.
- `sale_project._check_sale_line_type` (`addons/sale_project/models/project_task.py:142`): `sale_line_id` must be a service and not a re-invoiced expense.

## create() / write() Overrides

`ProjectTask.create()` (`addons/project/models/project_task.py:1090`):
- Adds current user to `user_ids` when creating under a parent and user isn't in the list.
- Sets `date_assign` automatically if `user_ids` is provided.
- Copies `display_name` → `name` if `name` is empty (line 1124).
- Resolves `company_id` from `project_id` when not given (line 1130-1133).
- Forces `stage_id=False` when `project_id` is absent (line 1134).
- Auto-selects default `stage_id` per project via `default_get(['stage_id'])` — batched per project id.
- Updates `date_end` (via `update_date_end`) if the target stage is folded, and sets `date_last_stage_update=now()`.
- Creates the `project.task.recurrence` record when `recurring_task=True` and any recurrence field is in vals.
- Calls `_populate_missing_personal_stages()` for every task.
- Subscribes the current partner and any `email_cc`-matched partners as followers.
- Calls `_set_stage_on_project_from_task()` to link a brand-new stage back to the project's `type_ids` if missing.

Extension `create()` overrides:
- `sale_project.create()` — after super, if any `sale_line_id` was set, confirms its draft `sale.order` (`addons/sale_project/models/project_task.py:166`).
- `project_todo.create()` — auto-fills `name` from first line of `description` (or `"Untitled to-do"`) for records with no project and no parent.

`ProjectTask.write()` (`addons/project/models/project_task.py:1204`):
- Handles milestone reassignment cascades when `project_id` changes.
- Propagates `date_deadline`, `partner_id`, `user_ids`, `project_id`, `milestone_id` to children depending on value.
- Updates `date_end` / `date_last_stage_update` on stage transitions.
- Creates a recurrence record on `write()` as well if `recurring_task` flips to `True` with repeat fields.
- Fires `_task_message_auto_subscribe_notify` for added assignees.

**No `ir.sequence` is used.** There is no `sequence_id` or `default_code`-style identifier on `project.task`. The `sequence` Integer field is only for manual kanban/list ordering.

`ProjectTask.unlink()` (line 1373):
- Expands the recordset with `_get_all_subtasks()` — deleting a task deletes the entire subtree.
- If the deleted task is the last in its recurrence, the recurrence is also unlinked.

## onchange handlers (UI-only, bypassed by CSV loader)

- `_onchange_project_id` (line 426): resets `state` to `01_in_progress` unless it's `04_waiting_normal`.
- `_onchange_task_company` (line 661): clears `project_id` if it belongs to a different company.
- `project_enterprise._onchange_planned_date_begin` (enterprise): clears `planned_date_begin` if it is after `date_deadline`.

**Action:** in CSV, explicitly set `state`, `company_id` and (for `project_enterprise`) `planned_date_begin` / `date_deadline` consistently — no onchange will fix them for you.

## Form view creation flow

From `view_task_form2` (`addons/project/views/project_task_views.xml:322`):

1. `name` (title) — required.
2. `project_id` — required if the task has children, is a sub-task, or is a template; otherwise optional (private task). Domain filtered by `company_id`.
3. `milestone_id` — visible only when `project_id` and `allow_milestones` are set.
4. `user_ids` — many2many_avatar_user, filtered to internal active users.
5. `tag_ids` — many2many_tags.
6. `partner_id` — visible only when `project_id` is set.
7. `date_deadline`.
8. `recurring_task` toggle — exposes `repeat_interval` / `repeat_unit` / `repeat_type` / `repeat_until` (all `required="recurring_task"`, plus `repeat_until` required when `repeat_type == 'until'`).
9. Header statusbar: `stage_id` (visible only when `project_id` is set) and `state` (hidden selection widget).
10. Notebook pages: `description`, `sub-tasks`, `blocked by`, `extra info`, and several more added by enterprise modules.

Tabs with embedded editable list views (`sub_tasks_page`, `task_dependencies`) use `default_project_id`, `default_parent_id`, `default_partner_id`, `default_milestone_id`, `default_tag_ids` context keys — not relevant for CSV loaders that issue explicit `create()` calls.

## Inheritance chain (for CSV writers: which modules add fields you may see)

Community:
- `addons/project_todo/models/project_task.py` — `create()` override for name auto-fill.
- `addons/hr_timesheet/models/project_task.py` — adds `allow_timesheets`, `timesheet_ids`, `effective_hours`, `remaining_hours`, `progress`, `overtime`, `total_hours_spent`, `subtask_effective_hours`. Restricts `project_id` domain.
- `addons/sale_project/models/project_task.py` — adds `sale_order_id`, `sale_line_id`, `task_to_invoice`, `allow_billable`. Creates/confirms SOs in `create()`/`write()`.
- `addons/sale_timesheet/models/project_task.py` — adds `remaining_hours_so`, `pricing_type`, `timesheet_product_id`, `has_multi_sol`.
- `addons/project_sms/models/project_task.py`, `addons/project_hr_skills/models/project_task.py`, `addons/website_project/models/project_task.py`, `addons/project_timesheet_holidays/models/project_task.py`.

Enterprise:
- `enterprise/project_enterprise/models/project_task.py` — adds `planned_date_begin`, `planned_date_start`, makes `allocated_hours` computed-writable, adds `_planned_dates_check` SQL constraint.
- `enterprise/project_holidays/models/project_task.py` — adds `leave_warning`, `is_absent`.
- `enterprise/industry_fsm/models/project_task.py` (+ `industry_fsm_sale`, `industry_fsm_stock`, `industry_fsm_report`, `industry_fsm_sale_report`, `industry_fsm_sale_subscription`) — adds `is_fsm`, `fsm_done`, `worksheet_signature`, `partner_city/zip/street`, etc.
- `enterprise/project_helpdesk/models/project_task.py`, `enterprise/helpdesk_fsm/models/project_task.py`.
- `enterprise/sale_timesheet_enterprise/models/project_task.py`.
- `enterprise/project_enterprise_hr/models/project_task.py`, `enterprise/project_enterprise_hr_skills/models/project_task.py`.
- `enterprise/l10n_din5008_industry_fsm/models/project_task.py`.
- `enterprise/website_appointment_sale_project/models/project_task.py`.

None of the extensions change the identity of a task — `name` + `project_id` remain the natural key across all of them.

## Demo Data Patterns

From `addons/project/data/project_demo.xml`:

```xml
<record id="project_template_1_task_1" model="project.task">
    <field name="name">Market Analysis</field>
    <field name="project_id" ref="project_template_1"/>
</record>

<record id="project_template_1_task_2" model="project.task">
    <field name="name">Define Target Audience</field>
    <field name="project_id" ref="project_template_1"/>
    <field name="depend_on_ids" eval="[Command.link(ref('project_template_1_task_1'))]"/>
</record>
```

Canonical pattern: **only `name` and `project_id` are set**. Everything else is derived — stage from the project's first stage, state from the compute, partner from the project, company from the project. Demo tasks load without any custom stage/state/partner fields.

## CSV Recommendations

- **Order of columns / load order:** `name`, `project_id`, then optional `user_ids`, `tag_ids`, `partner_id`, `date_deadline`, `priority`, `state`, `stage_id`, `description`, `milestone_id`, `parent_id`, `depend_on_ids`, `allocated_hours`.
- **Parents before children.** `parent_id` must reference an already-loaded task.
- **Stages must exist on the project** (`project.task.type.project_ids`). Load `project.task.type` rows first, or let Odoo use the project's default stages and omit `stage_id`.
- **Never set `state = '04_waiting_normal'`** in CSV — `default_get()` rewrites it.
- **Never set `recurrence_id`** directly. If you need a recurring task, set `recurring_task=True` plus `repeat_interval`, `repeat_unit`, `repeat_type`, and (for `repeat_type='until'`) `repeat_until` — the recurrence record is created by `create()`.
- **Private tasks** (no `project_id`) can have no `parent_id` and no children, cannot have timesheets (`hr_timesheet`), and must have `stage_id=False` — Odoo enforces all three.
- **`user_ids`** — resolve via `name_search` on `res.users`, filtered to internal users (`share=False`).
- **`tag_ids`** — `name_search` on `project.tags`; tags auto-create if missing when using the `display_name` shortcut, but CSV should pre-create `project.tags` rows.
- **`partner_id`** — must satisfy the same-company constraint with `company_id`. Omitting it lets Odoo copy the project's customer.
- Avoid touching `display_name` in CSV — the inverse mutates four other fields.

## Recommended Identity Key for csv_loader

```
"project.task": ["project_id", "name"]
```

`name` alone is not unique: the same task title routinely appears in different projects (see the demo file, which uses names like "Market Analysis" that will recur in any template-instantiated project). Private tasks (where `project_id` is `False`) collapse to the `name`-only case; if private tasks are part of the dataset, the loader should treat `(False, name)` tuples as unique per CSV run and fall back to creation. No `default_code` exists on this model, so the compound `(project_id, name)` key is the cleanest natural identity.
