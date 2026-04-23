# UI Report: project.task.recurrence

**Odoo Version:** 19.0
**Source:** `odoo/addons/project/models/project_task_recurrence.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.task.recurrence` |
| `_description` | `Task Recurrence` |
| `_inherit` | — (plain `models.Model`; no mixins) |
| `_rec_name` | `display_name` (default; no `name` field defined) |
| `_order` | default (`id desc`) |

Inheritance extensions (v19):
- `enterprise/project_enterprise/models/project_task_recurrence.py` — adds `planned_date_begin` to `_get_recurring_fields_to_postpone()` so Gantt planning dates shift with each new occurrence.
- `enterprise/industry_fsm/models/project_task_recurrence.py` — adds `partner_phone` to `_get_recurring_fields_to_copy()`.
- `enterprise/industry_fsm_report/models/project_task_recurrence.py` — adds `worksheet_template_id` to `_get_recurring_fields_to_copy()`.
- `odoo/addons/sale_project/models/project_task_recurrence.py` — adds `sale_line_id` to `_get_recurring_fields_to_copy()`.

None of these extensions add fields to the recurrence record itself — they only influence which fields are carried over or shifted when the next task occurrence is generated.

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `repeat_interval` | Integer | No (enforced >0 by `@api.constrains`) | `1` | Label: "Repeat Every". Must be strictly greater than 0 — see constraints. |
| `repeat_unit` | Selection | No | `week` | Values: `day`, `week`, `month`, `year`. `export_string_translation=False`. |
| `repeat_type` | Selection | No | `forever` | Values: `forever`, `until`. Label: "Until". |
| `repeat_until` | Date | Conditional | — | Required when `repeat_type='until'` (enforced in the task form view, not on the recurrence model). Must be `>= today` when `repeat_type='until'`. |
| `task_ids` | One2many → `project.task` (inverse `recurrence_id`) | No | — | `copy=False`. Reverse of `project.task.recurrence_id`; normally populated by the task, not the recurrence. |

There is no `name`, `active`, `company_id`, `repeat_number`, `repeat_weekday`, `repeat_on_month`, `repeat_on_year`, `repeat_day`, `mon`/`tue`/... field on this model in v19. The recurrence rule is strictly interval + unit + terminator.

## Form View / UI Surface

The model has **no dedicated form view**. The recurrence is edited inline on the task form at `odoo/addons/project/views/project_task_views.xml:439-456` through related fields on `project.task` (`recurring_task`, `repeat_interval`, `repeat_unit`, `repeat_type`, `repeat_until`):

```xml
<field name="recurring_task" widget="boolean_icon" options="{'icon': 'fa-repeat'}"
       invisible="not active or parent_id or not allow_recurring_tasks"
       groups="project.group_project_recurring_tasks"/>
...
<div invisible="not recurring_task or not allow_recurring_tasks" ...>
    <field name="repeat_interval" required="recurring_task"/>
    <field name="repeat_unit"     required="recurring_task"/>
    <field name="repeat_type"     required="recurring_task"/>
    <field name="repeat_until"    invisible="repeat_type != 'until'"
                                  required="repeat_type == 'until'"/>
</div>
```

UI gating rules that must be respected when creating tasks whose creation chains into recurrence creation:
- `allow_recurring_tasks` (related from `project.project`) must be `True` on the project — otherwise the widget is hidden and the recurrence branch is not triggered.
- The task must not have a `parent_id` (sub-tasks cannot be recurring; DB-enforced by `project.task._recurring_task_has_no_parent` CHECK constraint at `odoo/addons/project/models/project_task.py:331-332`).
- The user must belong to `project.group_project_recurring_tasks` (see `odoo/addons/project/security/project_security.xml:31`).

## Constraints

Both `@api.constrains` live on the recurrence model (`odoo/addons/project/models/project_task_recurrence.py:29-38`):

- `_check_repeat_interval`: `repeat_interval` must be strictly > 0 → `ValidationError("The interval should be greater than 0")`.
- `_check_repeat_until_date`: if `repeat_type == 'until'` and `repeat_until < today`, raises `ValidationError("The end date should be in the future")`. Practical effect: **you cannot load a recurrence with a past end date**. Any CSV with `repeat_type=until` must keep `repeat_until` in the future at load time.

No SQL / `models.Constraint` declarations on the recurrence itself.

## create() / write() Overrides

`project.task.recurrence` defines **no** `create`, `write`, or `unlink` override. The record is a passive configuration bag.

The real orchestration lives on `project.task` (`odoo/addons/project/models/project_task.py`):
- `create()` (line 1151-1156): if `vals.get('recurring_task') is True` and any of `{repeat_interval, repeat_unit, repeat_type, repeat_until}` are in vals, it creates a `project.task.recurrence` with those values and sets `vals['recurrence_id']` on the task.
- `write()` (line 1272-1286): same logic — if recurrence fields change and the task already has `recurrence_id`, it writes through; if `recurring_task` is toggled off, it unlinks the recurrence and clears `recurring_task` on all sibling tasks in the recurrence.
- `_load_records_create()` (line 1076-1087): during XML/CSV load, if `recurring_task=True` but no explicit `recurrence_id`, it fills recurrence-field defaults before super.
- `unlink()` path (line 1376-1379): deleting the last task of a recurrence unlinks the `project.task.recurrence` as well.

Key methods on `project.task.recurrence` itself (all called by the task, not by the UI):
- `_get_recurring_fields_to_copy()` — fields copied verbatim to the next occurrence. Base: `['recurrence_id']`. Extended by sale_project, industry_fsm, industry_fsm_report.
- `_get_recurring_fields_to_postpone()` — fields shifted by `_get_recurrence_delta()`. Base: `['date_deadline']`. Extended by project_enterprise to add `planned_date_begin`.
- `_get_recurrence_delta()` — `relativedelta(**{f"{repeat_unit}s": repeat_interval})`.
- `_create_next_occurrences(occurrences_from)` — generates the next task(s); skips occurrences whose next deadline would exceed `repeat_until` when `repeat_type='until'`.

## Identity and name_search

- No `name` field; no `_rec_name` override, so `display_name` falls back to the default ORM computation (`"<model>,<id>"` style). The record is effectively anonymous.
- No `_rec_names_search`.
- Consequence: FK resolution by display name is **not reliable**. External loaders must either (a) use `external_id` / XML ID via `__export__` style `id` columns, or (b) not reference recurrence records directly at all — see CSV Recommendations.

## Demo Data Patterns

From `odoo/addons/project/data/project_demo.xml:769-800`:

```xml
<record id="project_task_recurrence_1" model="project.task.recurrence">
    <field name="repeat_unit">month</field>
    <field name="repeat_type">until</field>
    <field name="repeat_until" eval="DateTime.now() + relativedelta(months=4)"/>
</record>
<record id="project_task_recurrence_2" model="project.task.recurrence">
    <field name="repeat_unit">week</field>
    <field name="repeat_type">forever</field>
</record>
<record id="project_1_task_10" model="project.task">
    ...
    <field name="recurring_task" eval="True"/>
    <field name="recurrence_id" ref="project_task_recurrence_1"/>
</record>
```

Notes:
- Demo sets only `repeat_unit`, `repeat_type`, (optionally) `repeat_until`. `repeat_interval` is left to default `1`.
- `repeat_until` is always computed dynamically as a future date — never hardcoded — to avoid `_check_repeat_until_date` failing on later re-loads.
- Recurrence records are created first, then referenced by task records with both `recurring_task=True` and `recurrence_id`.

## CSV Recommendations

- **Prefer transitive creation.** In practice this model is rarely loaded via its own CSV. The canonical pattern (matching the UI and demo data) is to load `project.task` rows with `recurring_task=True` plus the four `repeat_*` fields — `project.task._load_records_create()` / `create()` will spawn the `project.task.recurrence` and wire `recurrence_id` automatically. This keeps a single writer for the recurrence, identical to UI flow.
- **If you must share one recurrence across several tasks** (e.g., to mimic `project_task_recurrence_2` in the demo), load the recurrence CSV first with an `id` (XML ID) column, then reference it via `recurrence_id/id` on the task rows. Do not try to resolve by display name — there is none.
- **Never load a past `repeat_until`.** `_check_repeat_until_date` fires on `create` and `write`. Use a relative future date at generation time, not a frozen value.
- **Always set `repeat_interval >= 1`** if you override the default — `_check_repeat_interval` rejects 0 and negatives.
- **Ensure the parent project has `allow_recurring_tasks=True`** before loading recurring tasks; otherwise the UI contract breaks (the task itself still loads, but users cannot edit the recurrence from the form).
- **Never mark a sub-task recurring.** The DB CHECK constraint `_recurring_task_has_no_parent` on `project.task` will reject `recurring_task=True AND parent_id IS NOT NULL`.
- **Recurrence-carried fields depend on installed modules.** If `sale_project`, `industry_fsm`, `industry_fsm_report`, or `project_enterprise` are installed, extra fields (`sale_line_id`, `partner_phone`, `worksheet_template_id`, `planned_date_begin`) will be copied/postponed to next occurrences — set them on the seed task if you want them to persist across generations.
- **Do not set `task_ids` on the recurrence CSV.** It is the inverse of `project.task.recurrence_id`; drive it from the task side.

## Recommended Identity Key for csv_loader

No natural key exists on this model (no `name`, no `_rec_name`, no unique business columns). Two viable approaches:

```
# Preferred — load transitively via project.task; do not register a key for project.task.recurrence.
# If direct loading is unavoidable, use XML ID as the only stable identity:
"project.task.recurrence": ["id"]
```

If the loader requires at least one business field, the only pseudo-key available is the compound `(repeat_interval, repeat_unit, repeat_type, repeat_until)` — but this is **not unique by design** (two distinct tasks can share identical recurrence settings while holding separate recurrence records). Prefer XML ID / `id` resolution.
