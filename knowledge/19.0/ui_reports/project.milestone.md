# UI Report: project.milestone

**Odoo Version:** 19.0
**Source:** `addons/project/models/project_milestone.py`
**Extended by:** `addons/sale_project/models/project_milestone.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.milestone` |
| `_description` | `Project Milestone` |
| `_inherit` | `mail.thread` |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, deadline, is_reached desc, name` |

No `_rec_names_search` override. `_compute_display_name` appends the deadline to the display name when the context flag `display_milestone_deadline` is set (used by `sale_project` for SO/project actions).

## Precondition: allow_milestones on the parent project

`project.milestone` records are only meaningful when the parent `project.project` has `allow_milestones=True`. Source:
- `project.project.allow_milestones` is a Boolean gated by the group `project.group_project_milestone` (`addons/project/models/project_project.py`, line 143; inverse `_inverse_allow_milestones` at line 439 enforces the group).
- The project form hides the milestones tab, and the embedded action `project_embedded_action_project_milestones` filters with `[('allow_milestones', '=', True)]` (`addons/project/views/project_milestone_views.xml`, line 132).
- `project.milestone.project_allow_milestones` is a computed mirror of `project_id.allow_milestones`; the form-view stat button is hidden when it is False, and `task_count` only counts tasks whose project has `allow_milestones=True` (`project_milestone.py`, lines 57-58).

**CSV implication:** Before loading milestones, ensure each target `project.project` row has `allow_milestones=True`. Loading a milestone against a project where `allow_milestones=False` succeeds (no constraint), but the record is effectively invisible in the UI and its tasks will not count toward `task_count`.

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | No translation. |
| `sequence` | Integer | No | `10` | Used in `_order`; list view has `widget="handle"`. |
| `project_id` | Many2one -> `project.project` | Yes | `context.default_project_id` or `context.active_id` | Domain `[('is_template', '=', False)]`; `ondelete='cascade'`; indexed. Form view sets this `invisible="1"` (expected to come from context). |
| `deadline` | Date | No | — | `tracking=True`, `copy=False`. |
| `is_reached` | Boolean | No | `False` | `copy=False`. Kanban uses `widget="task_done_checkmark"`. |
| `reached_date` | Date | No | computed | `compute='_compute_reached_date'`, stored. Set to today when `is_reached` flips True, else False. Demo data overrides this directly when seeding past milestones. |
| `task_ids` | One2many -> `project.task` (`milestone_id`) | No | — | Reverse side; set from tasks, not from milestone. |

### Computed / non-stored (informational only, do not set from CSV)

| Field | Notes |
|---|---|
| `project_allow_milestones` | Mirror of `project_id.allow_milestones`; has a `search` method so it is usable in domains. |
| `is_deadline_exceeded` | `not is_reached and deadline < today`. |
| `is_deadline_future` | `deadline > today`. |
| `task_count`, `done_task_count` | Read from `project.task` grouped by milestone, restricted to tasks whose project has `allow_milestones=True`. Gated by group `project.group_project_milestone`. |
| `can_be_marked_as_done` | True when milestone not reached and at least one closed task exists and no open tasks. |

### Added by `sale_project` (only when module installed)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `sale_line_id` | Many2one -> `sale.order.line` | No | `_default_sale_line_id` (picks a milestone-delivery SO line from the project's SO) | `index='btree_not_null'`; domain `[('order_partner_id', '=?', project_partner_id), ('qty_delivered_method', '=', 'milestones')]`. Setting this marks the milestone as a billing trigger. |
| `quantity_percentage` | Float | No | computed | `compute='_compute_quantity_percentage'`, stored. Equals `product_uom_qty / sale_line_id.product_uom_qty`. |
| `product_uom_qty` | Float | No | computed, writable | Recomputed from `quantity_percentage * sale_line_id.product_uom_qty`; editable in UI under the salesman group. |
| `allow_billable` | Boolean | No | related | `related='project_id.allow_billable'`. |
| `project_partner_id` | Many2one -> `res.partner` | No | related | `related='project_id.partner_id'`, used by the `sale_line_id` domain. |
| `product_uom_id` | Many2one -> `uom.uom` | No | related | `related='sale_line_id.product_uom_id'`. |
| `sale_line_display_name` | Char | No | related | `related='sale_line_id.display_name'`. |

Form-view sale block is wrapped in `invisible="not allow_billable"` — CSV can safely omit these fields when `sale_project` is not installed or the project is not billable.

## Constraints

- **No `@api.constrains` decorators** on `project.milestone` (core or `sale_project`). Required fields are enforced by the ORM (`name`, `project_id`).
- `project_id` domain `[('is_template', '=', False)]` — milestones cannot be attached to template projects (ORM allows it silently if forced, but the UI hides them).
- `sale_line_id` domain requires the SO line's `qty_delivered_method='milestones'`; setting an SO line without that will be rejected only in the UI (ORM will accept it).

## create() / write() Overrides

- **No `create()` override.** Core ORM path; `reached_date` is recomputed from `is_reached` on write.
- **No `write()` override.**
- **`copy()` override** (core, lines 128-135): if the source project has `allow_milestones=True`, records the old -> new id mapping in `context['milestone_mapping']`. Used by `project.project.copy()` to remap task `milestone_id` when duplicating a project. Irrelevant for CSV loading but important for consumers that duplicate projects.
- **`_compute_display_name` override** (lines 137-143): appends `- <deadline>` to the display name when `context['display_milestone_deadline']` is True. `sale_project` sets this flag on SO-driven project actions (`addons/sale_project/views/project_views.xml`, lines 90-106).

## Form View

`addons/project/views/project_milestone_views.xml` (`project_milestone_view_form`):

- `project_id` is `invisible="1"` (expected from context via the parent project's embedded action).
- Visible inputs: `name` (placeholder "e.g: Product Launch"), `deadline`, `is_reached`.
- Stat button "Tasks" is hidden when `not project_allow_milestones`, and gated by group `project.group_project_milestone`.

List view (`project_milestone_view_tree`, editable="bottom"): `sequence` (handle), `name`, `deadline`, `is_reached`, plus a "View Tasks" action button. `decoration-success` when `can_be_marked_as_done`, `decoration-danger` when `is_deadline_exceeded and not can_be_marked_as_done`, `decoration-muted` when `is_reached`.

Kanban view (`project_milestone_view_kanban`): mobile-oriented, shows `is_reached` checkmark, `name`, and colored `deadline`.

`sale_project` extensions (`addons/sale_project/views/project_task_views.xml`, lines 292-347, 372-387): add the `sale_line_id` / `quantity_percentage` / `product_uom_qty` block to form and list, add "Sales Order" stat and list buttons, and inject `quantity_percentage` into the kanban card. All wrapped in `invisible="not allow_billable"` / `invisible="not sale_line_id"`.

## Demo Data Patterns

From `addons/project/data/project_demo.xml` (lines 375-414):

```xml
<record id="project_1_milestone_1" model="project.milestone">
    <field name="is_reached" eval="True"/>
    <field name="deadline" eval="time.strftime('%Y-%m-10')"/>
    <field name="name">First Phase</field>
    <field name="reached_date" eval="time.strftime('%Y-%m-10')"/>
    <field name="project_id" ref="project.project_project_1"/>
</record>
<record id="project_1_milestone_2" model="project.milestone">
    <field name="is_reached" eval="False"/>
    <field name="deadline" eval="(DateTime.now() + relativedelta(years=1)).strftime('%Y-%m-15')"/>
    <field name="name">Second Phase</field>
    <field name="project_id" ref="project.project_project_1"/>
</record>
```

Notes from demo:
- Parent projects (`project.project_project_1`, `project.project_home_construction`) are created with `allow_milestones=True` (lines 141, 160, 186, 222).
- When `is_reached=True`, demo also sets `reached_date` explicitly (even though it is computed) — the stored compute only runs on write, so seeding both in one `create` guarantees the value exists before subsequent task/SO-line references.
- Tasks reference milestones via `milestone_id` (`project_demo.xml`, lines 426, 437, 483, 529, 575, 616, 654, 686, 733, 789); the CSV ordering must create milestones before tasks.

## UI Creation Flow (for CSV parity)

1. From a project with `allow_milestones=True`, open the "Milestones" embedded action (`project_milestone_action`) — this injects `default_project_id` into the context.
2. Click "New" on the editable list. `project_id` comes from context (no user input). `sequence` defaults to 10.
3. Enter `name` (required), optionally `deadline`.
4. Tick `is_reached` when the milestone is done — this triggers the `_compute_reached_date` on save.
5. (sale_project only) Pick a `sale_line_id` and adjust `quantity_percentage` or `product_uom_qty`.

CSV loader must:
- Set `project_id` explicitly (no context injection at load time).
- Set `reached_date` explicitly for `is_reached=True` rows if a specific historical date is wanted; otherwise the compute will stamp `today`.
- Omit `sale_line_id` / `quantity_percentage` unless `sale_project` is installed.

## CSV Recommendations

- Always verify `project_id.allow_milestones=True` before loading milestones; otherwise the records will be invisible in the UI and excluded from task counts.
- `name` is not unique globally — scope uniqueness to `(project_id, name)`.
- `deadline` is a Date (not Datetime) — use `YYYY-MM-DD`.
- `is_reached=True` without `reached_date` will stamp today's date on create; set `reached_date` explicitly for backdated data.
- `sale_line_id` only accepts SO lines whose product's `qty_delivered_method='milestones'`; otherwise the UI domain hides the choice but the ORM will accept it silently.
- `group_project_milestone` must be on the user running the import for stat buttons/count compute to render correctly (no hard block on create).

## Recommended Identity Key for csv_loader

Compound identity — `name` alone is not unique across projects (demo ships two "First Phase"-style names across different projects is plausible, and `project_id` is the natural scoping dimension):

```
"project.milestone": ["project_id", "name"]
```
