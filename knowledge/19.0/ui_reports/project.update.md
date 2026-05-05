# UI Report: project.update

**Odoo Version:** 19.0
**Source:** `odoo/addons/project/models/project_update.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.update` |
| `_description` | `Project Update` |
| `_inherit` | `mail.thread.cc`, `mail.activity.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `id desc` |

Extended by:
- `odoo/addons/hr_timesheet/models/project_update.py` — adds timesheet snapshot fields.
- `odoo/addons/sale_project/models/project_update.py` — enriches `_get_template_values` with SOL details (no new fields).
- `enterprise/project_account_budget/models/project_update.py` — enriches `_get_template_values` with budget data (no new fields).

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Title of the update. Tracked. |
| `status` | Selection | Yes | computed in `default_get` | Options: `on_track`, `at_risk`, `off_track`, `on_hold`, `done`. Tracked. Not translated for export. |
| `progress` | Integer | No | last update's progress (from `default_get`) | 0-100. Tracked. |
| `progress_percentage` | Float | No | computed | `progress / 100`. Read-only. |
| `user_id` | Many2one → `res.users` | Yes | current user | Label "Author". Read-only in form. |
| `description` | Html | No | rendered from `project.project_update_default_description` QWeb template | Built by `_build_description(project)` in `default_get`. |
| `date` | Date | No | `fields.Date.context_today` | Tracked. |
| `project_id` | Many2one → `project.project` | Yes | `context.active_id` (from `default_get`) | Domain: `[('is_template', '=', False)]`. Indexed. Hidden in form (`invisible="1"`). |
| `color` | Integer | No | computed from `status` | `STATUS_COLOR` map. Read-only. |
| `name_cropped` | Char | No | computed | Truncates `name` to 60 chars with ellipsis. Kanban display only. |
| `task_count` | Integer | No | written in `create()` from `project.task_count` | Read-only (snapshot). |
| `closed_task_count` | Integer | No | written in `create()` from `project.task_count - project.open_task_count` | Read-only (snapshot). |
| `closed_task_percentage` | Integer | No | computed | `round(closed_task_count * 100 / task_count)`. |
| `label_tasks` | Char | No | related to `project_id.label_tasks` | Read-only. |

### Added by `hr_timesheet`

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `display_timesheet_stats` | Boolean | No | computed | True when `project_id.allow_timesheets`. |
| `allocated_time` | Integer | No | written in `create()` | Snapshot of `round(project.allocated_hours * ratio)` where ratio converts hours to the company's `timesheet_encode_uom_id`. Read-only. |
| `timesheet_time` | Integer | No | written in `create()` | Snapshot of `round(project.sudo().total_timesheet_time)`. Read-only. |
| `timesheet_percentage` | Integer | No | computed | `round(timesheet_time * 100 / allocated_time)`. |
| `uom_id` | Many2one → `uom.uom` | No | written in `create()` as `env.company.timesheet_encode_uom_id` | Read-only snapshot. |

## Selection Values for `status`

| Value | Label |
|---|---|
| `on_track` | On Track |
| `at_risk` | At Risk |
| `off_track` | Off Track |
| `on_hold` | On Hold |
| `done` | Complete |

Note: `to_define` exists on `project.project.last_update_status` but is **not** a valid value for `project.update.status` itself. `default_get` coerces a source `to_define` into `on_track`.

## Form View (`project_update_view_form`)

Source: `odoo/addons/project/views/project_update_views.xml`.

- Title field: `name` (placeholder "e.g. Monthly review").
- Left group: `project_id` (hidden), `color` (hidden), `status` (widget `status_with_color`), `progress` (widget `progressbar`, editable).
- Right group: `user_id` (widget `many2one_avatar_user`, `readonly="1"`), `date`.
- Notebook single page "Description": `description` (Html, collaborative editor).
- `js_class="form_description_expander"` — the QWeb-rendered default description is intended to be edited in place.
- Chatter enabled with `reload_on_follower="True"`.

No `<header>` / no state buttons / no workflow transitions. Updates are plain records.

## Kanban / List / Search

- Kanban (`project_update_view_kanban`): cards show `name_cropped`, `user_id`, `status` (colored), `progress_percentage`, `closed_task_count / task_count (closed_task_percentage%)`, `date`. `highlight_color="color"`.
- List (`project_update_view_tree`): `name`, `user_id`, `date`, `progress`, `status`.
- Search (`project_update_view_search`): fields `name`, `project_id` (invisible), `user_id`, `description`, `status`. Filters: My Updates, status filters (On Track / At Risk / Off Track / On Hold), date filter.

Action `project_update_all_action` has `path="project-dashboard"`, view mode `kanban,list,form`, and its default domain is `[('project_id', '=', active_id)]` — the action is opened from a project context.

## Constraints

No `@api.constrains` on `project.update` itself. SQL/domain constraints only:
- `project_id` domain excludes template projects (`is_template = False`).
- `name`, `status`, `user_id`, `project_id` are `required=True` at the field level.

## create() / write() Overrides

**`create()` (base, `project_update.py:87`)** is `@api.model_create_multi`. After `super().create()`, for each new update it:
1. Sets `update.project_id.last_update_id = update` (sudo).
2. Writes snapshot values on the update: `task_count = project.task_count`, `closed_task_count = project.task_count - project.open_task_count`.

**`create()` (hr_timesheet, `project_update.py:27`)** extends `super().create()` to also write the snapshot fields `uom_id`, `allocated_time`, `timesheet_time` and re-sets `project.last_update_id = update`.

These snapshots are captured **at creation time only** and are marked `readonly=True`; they do not update later.

**`unlink()`**: recomputes `project.last_update_id` to the most recent remaining update by date desc.

**`default_get()`** (not an override of create/write, but material for CSV):
- Pulls `project_id` from `context.active_id` if not set.
- Defaults `progress` from `project.last_update_id.progress`.
- Defaults `description` from `_build_description(project)` (QWeb-rendered HTML snapshot of milestones, profitability, and — via inheritance — budget and SOL sections).
- Defaults `status` from `project.last_update_status` (mapping `to_define` → `on_track`).

**Reverse creation path**: `project.project.write()` (`project_project.py:646`) creates a `project.update` automatically when `last_update_status` is written with a value other than `to_define` — the new update carries `name = _('Status Update')` and the written `status`.

## Demo Data Patterns

From `odoo/addons/project/data/project_demo.xml:1780-1812`:

```xml
<record id="project_update_1" model="project.update"
        context="{'default_project_id': ref('project.project_project_1')}">
    <field name="name">Review of the situation</field>
    <field name="user_id" eval="ref('base.user_demo')"/>
    <field name="progress" eval="15"/>
    <field name="status">at_risk</field>
</record>
<record id="project_update_construction_1" model="project.update"
        context="{'default_project_id': ref('project.project_home_construction')}">
    <field name="name">Design Approval</field>
    <field name="user_id" eval="ref('base.user_admin')"/>
    <field name="progress" eval="65"/>
    <field name="status">on_track</field>
    <field name="date" eval="time.strftime('%Y-%m-5')"/>
</record>
```

Notes from demo:
- `project_id` is passed via `context="{'default_project_id': ...}"` rather than as a direct field. `default_get` reads this from `context.active_id` / `default_project_id`.
- `description` is never set explicitly in demo — the QWeb default is used.
- `date` is sometimes omitted (defaults to today).

## CSV Recommendations

- Set `project_id` **explicitly** in the CSV — CSV loading calls `create()` directly, so `default_get`'s `context.active_id` fallback won't help.
- Set `status` **explicitly** — `default_get` resolves it from the project's last update, but loaders bypass that flow.
- Set `user_id` explicitly (default `env.user` is usually the loader user and may not be what you want).
- Do **not** set `task_count`, `closed_task_count`, `allocated_time`, `timesheet_time`, `uom_id` — `create()` overwrites them from the project at the moment of creation. They are snapshot fields.
- Do **not** set `color`, `progress_percentage`, `name_cropped`, `closed_task_percentage`, `timesheet_percentage`, `display_timesheet_stats`, `label_tasks` — all computed/related and read-only in practice.
- `description` may be left empty (loader will not trigger the QWeb default that `default_get` produces). If you want the rich auto-description, you must render it yourself or trigger creation through the UI/default path.
- If you use `name = "Status Update"` and write `project.last_update_status`, the framework will create the update for you — avoid double-creating.
- `progress` is a raw Integer 0-100, not a 0.0-1.0 ratio (despite `progress_percentage` being the ratio form).

## Recommended Identity Key for csv_loader

`name` alone is not unique (demo has multiple "Status"/"Weekly review" names across projects). A project has many updates over time, and two updates on the same project+date with the same title are legitimately different runs, but practically the compound key below is the best surrogate:

```
"project.update": ["project_id", "date", "name"]
```
