# UI Report: project.task.type

**Odoo Version:** 19.0
**Source:** `odoo/addons/project/models/project_task_type.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.task.type` |
| `_description` | `Task Stage` |
| `_inherit` | (none — bare `models.Model`) |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, id` |

Extended by:
- `odoo/addons/sale_project/models/project_task_type.py` — adds compute `show_rating_active` and `_onchange_project_ids` that clears `rating_active` when none of the linked projects allow billing.
- `odoo/addons/project_sms/models/project_task_type.py` — adds `sms_template_id` (Many2one -> `sms.template`, domain `model = project.task`).
- `enterprise/industry_fsm/models/project_task_type.py` — overrides `_get_default_project_ids` to auto-target the FSM project when `fsm_mode` context is set.

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `sequence` | Integer | No | `1` | Controls stage order (model `_order = sequence, id`). |
| `active` | Boolean | No | `True` | Archiving the stage also archives all tasks currently in the stage (see `write()`). |
| `project_ids` | Many2many -> `project.project` (rel `project_task_type_rel`) | Conditional | `default_project_id` from context if present, else `None` | Required in the form when `user_id` is not set (`required="not user_id"`). Empty = stage is not attached to any project. See "Stage visibility semantics" below. |
| `user_id` | Many2one -> `res.users` | No | current user (`self.env.uid`) when no `default_project_id` in context | This is the **personal stage owner**. Computed+stored; set to `False` automatically when `project_ids` is populated (see `_compute_user_id`). Hidden in the form (`invisible="1"`). |
| `mail_template_id` | Many2one -> `mail.template` | No | — | Domain: `model = project.task`. If set, an email is sent to the customer when a task reaches this stage. Hidden in the form for personal stages (`invisible="user_id"`). |
| `rating_template_id` | Many2one -> `mail.template` | Conditional | — | Domain: `model = project.task`. Required when `rating_active = True`. Rating request email. |
| `rating_active` | Boolean | No | `False` | Enables customer rating on the stage. Toggling this on also un-hides the related `mt_project_task_rating`/`mt_task_rating` subtypes and reactivates `rating_project_request_email_template` (see `write()`). |
| `rating_status` | Selection | Yes | `stage` | Values: `stage` (on entering stage), `periodic`. |
| `rating_status_period` | Selection | Yes | `monthly` | Values: `daily`, `weekly`, `bimonthly`, `monthly`, `quarterly`, `yearly`. Required in form when `rating_status == 'periodic'`. |
| `rating_request_deadline` | Datetime | No (computed, stored) | — | Computed from `rating_status` + `rating_status_period`; used by the `_send_rating_all` cron. |
| `auto_validation_state` | Boolean | No | `False` | Auto-flip task kanban state (`approved` / `changes_requested`) on customer feedback. Hidden in form unless `rating_template_id` is set. |
| `fold` | Boolean | No | `False` | Folded column in kanban. |
| `color` | Integer | No | `0` | Color picker; `export_string_translation=False`. |
| `rotting_threshold_days` | Integer | No | `0` | Days before a task in this stage is considered rotting. `0` disables. Changing the value does not backfill existing tasks. |

### Fields added by extension modules

| Module | Field | Type | Notes |
|---|---|---|---|
| `project_sms` | `sms_template_id` | Many2one -> `sms.template` | Domain: `model = project.task`. Auto-SMS on stage entry. |
| `sale_project` | `show_rating_active` | Boolean (compute) | `export_string_translation=False`. True when any linked project has `allow_billable`. UI-only; not for CSV. |

### Fields NOT on this model (common confusion)

- `legend_blocked`, `legend_done`, `legend_normal` — these live on `project.project`, **not** on `project.task.type`. Do not include them in a task-stage CSV.
- `disabled_rating_warning` — present in stale translation files but **removed from 19.0 source**. Do not reference it.

## Stage visibility semantics

A single stage can play two distinct roles, and the two are mutually exclusive (see `@api.constrains` below):

1. **Project stage** — `project_ids` populated, `user_id = False`. Visible in every listed project's kanban. Omitting `project_ids` on a project-stage means the record exists but is not attached to any project (orphan), which is rarely useful — the form view enforces `required="not user_id"`. There is **no "global stage" mode** in the data model; a stage with empty `project_ids` and empty `user_id` is valid at the DB level but invisible in every project pipeline.
2. **Personal stage** — `user_id` populated, `project_ids` empty. Per-user "Inbox / Today / Later / Done / Cancelled" columns used by the `My Tasks` view. `_unlink_if_remaining_personal_stages` refuses to delete a user's last personal stage.

Sharing a stage across projects is the whole point of Many2many here: set `project_ids = [Command.link(ref('project_A')), Command.link(ref('project_B'))]` and the stage appears in both pipelines.

## Constraints

- `_check_personal_stage_not_linked_to_projects` (`@api.constrains('user_id', 'project_ids')`): a stage cannot have both `user_id` and `project_ids` set. Enforced by `_compute_user_id` too — writing `project_ids` clears `user_id` automatically, but writing both in the same `create()` call raises `UserError`.

## Onchange / compute behavior

- `_compute_user_id` (depends on `project_ids`, stored): sets `user_id = False` whenever `project_ids` is non-empty. Runs on create and write — relevant for CSV because `user_id` default is `self.env.uid`, so loading a project-stage CSV with `project_ids` set will automatically clear the default `user_id`.
- `_compute_rating_request_deadline` (depends on `rating_status`, `rating_status_period`, stored): `now + N days` where N comes from the period map.
- `sale_project._onchange_project_ids`: clears `rating_active` when no linked project has `allow_billable`. **Onchange only fires in the UI** — the CSV loader bypasses it. If you enable rating on a non-billable project via CSV, the value will stick (possibly incorrectly) until the user opens the form.

## create() / write() / unlink() Overrides

- **`write()`**:
  - If `active` is set to `False`, also archives every task in this stage (`project.task.search([('stage_id', 'in', self.ids)]).write({'active': False})`).
  - If `rating_active` is toggled, flips the hidden/default attributes of `project.mt_project_task_rating`, `project.mt_task_rating`, and toggles `active` on `project.rating_project_request_email_template` globally. **Side effect is global** (not scoped to this stage) — changing `rating_active` on one stage affects every other stage's subtype visibility.
- **`copy_data()`**: appends ` (copy)` to `name`.
- **`unlink_wizard()`**: server-action path (see `unlink_task_type_action` in views). Opens `project.task.type.delete.wizard` for re-assigning tasks before deletion; direct `unlink()` on stages with tasks in them is discouraged.
- **`_unlink_if_remaining_personal_stages`** (`@api.ondelete`): refuses to delete a user's last personal stage. Needed before mass-deleting personal stages via CSV cleanup.
- **`action_unarchive()`**: if archived tasks exist in the un-archived stage, opens `project.task.type.delete.wizard` (variant `view_project_task_type_unarchive_wizard`) to prompt reactivation.

## Form view highlights

`odoo/addons/project/views/project_task_type_views.xml` (view id `task_type_edit`):

- `name` placeholder: "e.g. To Do".
- `project_ids` is a `many2many_tags` widget, **`required="not user_id"`**, hidden for personal stages.
- `mail_template_id`, the entire "Customer Rating" settings block, and `project_ids` are hidden when `user_id` is set (personal-stage mode).
- `auto_validation_state` is hidden unless `rating_template_id` is set.
- `rating_status_period` is hidden and not required unless `rating_status == 'periodic'`.
- `rating_template_id` becomes `required="rating_active"` inside the Customer Rating setting block.
- `sequence` is only visible with `groups="base.group_no_one"` (developer mode).

List view (`task_type_tree`) treats `project_ids` as `required="1"` — consistent with the form's "not user_id" rule since the list is scoped to project stages via the action domain `[('user_id', '=', False)]`.

## Demo Data Patterns

From `odoo/addons/project/data/project_demo.xml`:

```xml
<!-- Shared/project stages (project_ids set via project.project.type_ids) -->
<record id="project_stage_0" model="project.task.type">
    <field name="sequence">1</field>
    <field name="name">New</field>
    <field name="mail_template_id" ref="project.mail_template_data_project_task"/>
</record>
<record id="project_stage_1" model="project.task.type">
    <field name="sequence">10</field>
    <field name="name">In Progress</field>
</record>
<record id="project_stage_2" model="project.task.type">
    <field name="sequence">20</field>
    <field name="name">Done</field>
    <field name="fold" eval="False"/>
</record>
<record id="project_stage_3" model="project.task.type">
    <field name="sequence">30</field>
    <field name="name">Cancelled</field>
    <field name="fold" eval="True"/>
</record>

<!-- project.project then links them via type_ids = Many2many (inverse side) -->
<record id="project_project_1" model="project.project">
    ...
    <field name="type_ids" eval="[Command.link(ref('project_stage_0')), Command.link(ref('project_stage_1')),
                                   Command.link(ref('project_stage_2')), Command.link(ref('project_stage_3'))]"/>
</record>

<!-- Personal stage -->
<record id="project_personal_stage_admin_0" model="project.task.type">
    <field name="sequence">1</field>
    <field name="name">Inbox</field>
    <field name="user_id" ref="base.user_admin"/>
</record>
```

Note the pattern: the demo defines stages **without** `project_ids` on the stage record, then attaches them from the `project.project` side via `type_ids`. Either direction works (both sides of the same Many2many), but the project-side Command list is the convention.

Rating setup is patched in as a second pass at the bottom of the same file:

```xml
<record id="project.project_stage_2" model="project.task.type">
    <field name="rating_template_id" ref="rating_project_request_email_template"/>
</record>
```

## UI creation flow (shared stage, for reference)

1. Open Project > Configuration > Task Stages, click "New".
2. Enter `name` (required).
3. Pick `project_ids` tag widget — required because `user_id` is hidden/empty.
4. Optionally set `fold`, `mail_template_id`, `rotting_threshold_days`, `color`, `sequence` (dev-mode only).
5. Toggle `rating_active` -> the Customer Rating block expands; `rating_status` (radio) defaults to `stage`. Switching to `periodic` reveals `rating_status_period` (required) and forces `rating_template_id` to be set.
6. Save.

Personal stages are created from `My Tasks` with `default_user_id` in context; the same form hides project/rating blocks via `invisible="user_id"`.

## CSV Recommendations

- Four default project stages (`New`, `In Progress`, `Done`, `Cancelled`) are installed by `project_demo` when demo is loaded. On a no-demo DB, **no default stages exist** — the user creates them from a project's kanban.
- To share a stage across projects, set `project_ids` as a comma-separated list of project `name_search`-resolvable names (or use XML-ID imports with `Command.link`).
- Never set both `project_ids` and `user_id` in the same row — `_check_personal_stage_not_linked_to_projects` will raise.
- To make a stage visible in the "Task Stages" admin list view, keep `user_id = False` (the action domain filters personal stages out).
- Do not include `legend_blocked`/`legend_done`/`legend_normal` columns; those belong to `project.project`.
- `sequence` gaps matter for ordering but nothing else. Match the demo cadence (1 / 10 / 20 / 30) if you want room to insert later.
- Onchange `_onchange_project_ids` from `sale_project` does NOT fire via CSV — if you set `rating_active=True` on a stage attached only to non-billable projects, the value will persist.

## Recommended Identity Key for csv_loader

Because the same `name` can legitimately exist in multiple contexts (e.g. "Done" as a shared project stage, "Done" as user A's personal stage, "Done" as user B's personal stage) the identity key must disambiguate:

```
"project.task.type": ["name", "user_id", "project_ids"]
```

Rationale:
- `name` alone collides across personal stages of different users and across disjoint project pipelines that happen to reuse the same label.
- Adding `user_id` separates personal stages by owner.
- Adding `project_ids` (the Many2many tuple) separates shared stages that belong to different project sets. Two shared stages with identical `name` but different `project_ids` are legitimately different rows.
- If your CSV only loads shared stages, `["name", "project_ids"]` is sufficient. If it only loads personal stages, `["name", "user_id"]` is sufficient. The three-key form is safe for mixed loads.

If the loader cannot key on Many2many values, fall back to `["name", "user_id"]` and accept that shared-stage uniqueness is enforced by `project_ids` content checks in a post-load pass.
