# Feature Catalog — Project Forecast family (project_forecast + sale_project_forecast + project_timesheet_forecast + project_timesheet_forecast_sale) — Sub-catalog

**Sub-catalog — Resource planning and forecasting for projects, integrating with `planning`, `sale_project`, and `timesheet`. See `project.md` for the mainline catalog.**

**Version:** 19.0
**Source:** enterprise
**Category:** Services/Project, Services/Timesheets, Sales/Sales
**Dependencies:**
- `project_forecast`: project, planning, web_grid
- `sale_project_forecast`: sale_planning, sale_project, project_forecast (auto_install)
- `project_timesheet_forecast`: timesheet_grid, project_forecast (auto_install)
- `project_timesheet_forecast_sale`: project_timesheet_forecast, sale_timesheet, sale_project_forecast (auto_install)

## Business Capabilities

- **Project-aware resource scheduling:** Attach every `planning.slot` (shift) and `planning.slot.template` to a `project.project`, letting managers plan the workload for each project on a Gantt/calendar/kanban board and see the total forecast hours straight on the project form. Cited in `enterprise/project_forecast/models/planning_slot.py` and `enterprise/project_forecast/models/project_project.py`.
- **Sales-driven auto-forecasting:** When a sales order line uses a plannable service product (`planning_enabled=True` on the product), the system pre-computes project and task from the SOL (`sale_line_id.task_id.project_id` or `sale_line_id.project_id`) and can automatically generate the corresponding shifts. Cited in `enterprise/sale_project_forecast/models/planning_slot.py` and `enterprise/sale_project_forecast/models/sale_order_line.py`.
- **Plan vs. actuals on every shift:** Each slot exposes `effective_hours` (sum of timesheets logged by the same employee on the same project during the shift window) and a live `percentage_hours` progress bar, so a planner immediately sees whether the forecast was respected. Cited in `enterprise/project_timesheet_forecast/models/planning_slot.py`.
- **Planning vs. Timesheet analysis report:** A dedicated SQL view (`project.timesheet.forecast.report.analysis`) unions planned shifts and actual timesheets day-by-day, producing pivot/graph analytics of planned hours, effective hours and the difference, with costs, revenues and billable/non-billable splits when the sales extension is installed. Cited in `enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis.py` and `enterprise/project_timesheet_forecast_sale/report/project_timesheet_forecast_report_analysis.py`.
- **Billable vs. non-billable forecast tracking:** With `project_timesheet_forecast_sale` installed, shifts linked to a sale order line are tagged billable and surfaced as `billable_allocated_hours` / `non_billable_allocated_hours`, and the planning report adds planned/effective revenues and margins. Cited in `enterprise/project_timesheet_forecast_sale/report/planning_analysis_report.py` and `.../project_timesheet_forecast_report_analysis.py`.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| Planning > Schedule > By Project | Schedule by Project | Gantt/calendar/list/kanban/pivot/graph of `planning.slot` grouped by `project_id`, with `planning_expand_project=1` so empty projects still render a row (`enterprise/project_forecast/views/planning_slot_views.xml`, `planning_menus.xml`) |
| Planning > Schedule > By Resource | Schedule by Resource | Overridden resource view that uses the `forecast_gantt` JS class and preserves project-aware expansion (`enterprise/project_forecast/views/planning_slot_views.xml`, `planning_menus.xml`) |
| Planning > Schedule > By Role | Schedule by Role | Variant added by `project_timesheet_forecast` with role-grouped Gantt and project-aware progress bars (`enterprise/project_timesheet_forecast/views/planning_slot_views.xml`, `project_timesheet_forecast_menus.xml`) |
| Planning > Reporting > Planning / Timesheets Analysis | Planning / Timesheets Analysis | Pivot/graph comparing planned vs. effective hours; visible only to users who are both Planning Manager and Timesheet Approver (`enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis_views.xml`, `enterprise/project_timesheet_forecast/models/ir_ui_menu.py`) |
| Project > (project kanban dashboard action) > Planning | Project Planning embedded action | Planning gantt scoped to a single project via `planning_action_schedule_project` / `project_forecast_action_from_project`; surfaced as an `ir.embedded.actions` under the project tasks action and project update action (`enterprise/project_forecast/views/project_project_views.xml`, `planning_slot_views.xml`) |
| Project form > stat buttons | "Planned" stat button | Shows total forecast hours on a project and opens the project-filtered planning gantt (`enterprise/project_forecast/models/project_project.py::_get_stat_buttons`) |
| Project form > stat buttons | "Timesheets and Planning" stat button | Added by `project_timesheet_forecast_sale`; opens the Planning / Timesheets Analysis filtered on the current project (`enterprise/project_timesheet_forecast_sale/models/project_project.py`) |
| Project kanban dropdown | "Timesheets and Planning Analysis" | Dropdown entry on the project kanban card, shown when `display_planning_timesheet_analysis` is true (`enterprise/project_timesheet_forecast_sale/views/project_project_views.xml`) |

### Settings & Feature Flags

These modules add no `res.config.settings` toggles of their own. Feature activation comes from dependencies (`planning`, `timesheet_grid`, `sale_planning`, `sale_timesheet`) and from three per-record flags:

| Setting | Technical Field | What it Enables |
|---|---|---|
| Plan services for a product | `product.template.planning_enabled` (inherited from `sale_planning`) | Makes the product generate planning shifts when sold; disabled automatically when `service_policy` is `delivered_manual` or `delivered_milestones` (`enterprise/sale_project_forecast/models/product_template.py`) |
| Allow timesheets on a project | `project.project.allow_timesheets` (inherited from `hr_timesheet`) | Exposes `effective_hours`, the "Recorded" button on slots, and enables per-project progress bars in gantt (`enterprise/project_timesheet_forecast/models/planning_slot.py`, `views/planning_slot_views.xml`) |
| Planning role ↔ product link | `planning.role.product_ids` domain override | Restricts products that can be attached to a planning role to service products with a compatible service_tracking (`enterprise/sale_project_forecast/models/planning_role.py`) |
| Show "Timesheets and Planning" button | `project.project.display_planning_timesheet_analysis` (computed) | Visible only when the current user has both `planning.group_planning_manager` and `hr_timesheet.group_hr_timesheet_approver` and the project allows timesheets (`enterprise/project_timesheet_forecast_sale/models/project_project.py`) |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `planning.slot` (extended) | Primary | Adds `project_id` (computed from template, SOL or context), `effective_hours`, `percentage_hours`, `timesheet_ids`, `can_open_timesheets`, `allow_timesheets` and plan-vs-actual helpers (`enterprise/project_forecast/models/planning_slot.py`, `enterprise/sale_project_forecast/models/planning_slot.py`, `enterprise/project_timesheet_forecast/models/planning_slot.py`, `enterprise/project_timesheet_forecast_sale/models/planning_slot.py`) | Yes |
| `planning.slot.template` (extended) | Configuration | Adds `project_id` and a `company_id` related to it, and appends the project name to `display_name` (`enterprise/project_forecast/models/planning_slot_template.py`) | Yes |
| `project.project` (extended) | Primary | Adds `total_forecast_time` (sum of allocated_hours on its shifts), the "Planned" stat button, the `_check_company_id` constraint against slot companies, and `display_planning_timesheet_analysis` (`enterprise/project_forecast/models/project_project.py`, `enterprise/project_timesheet_forecast/models/project_project.py`, `enterprise/project_timesheet_forecast_sale/models/project_project.py`) | Yes |
| `planning.role` (extended) | Configuration | Tightens the `product_ids` domain so only plannable service products attach to a role (`enterprise/sale_project_forecast/models/planning_role.py`) | Yes (embedded in role form) |
| `sale.order.line` (extended) | Transactional | Passes `project_id` into `_planning_slot_values()` when generating shifts; reworks `_compute_planning_hours_planned` to consider validated timesheets for plannable products (`enterprise/sale_project_forecast/models/sale_order_line.py`, `enterprise/project_timesheet_forecast_sale/models/sale_order_line.py`) | Yes (embedded in SO) |
| `account.analytic.line` (extended) | Transactional | On write, re-triggers `_post_process_planning_sale_line` when `validated` or `unit_amount` change, keeping SOL planning figures in sync (`enterprise/project_timesheet_forecast_sale/models/analytic_account_line.py`) | Yes (embedded in timesheet) |
| `product.template` (extended) | Configuration | Forces `planning_enabled=False` for `delivered_manual` / `delivered_milestones` service policies (`enterprise/sale_project_forecast/models/product_template.py`) | Yes |
| `planning.analysis.report` (extended) | Reporting | Adds `project_id` (project_forecast), `percentage_hours` / `effective_hours` / `remaining_hours` / allocated+effective costs (project_timesheet_forecast), `billable_allocated_hours` / `non_billable_allocated_hours` (project_timesheet_forecast_sale) (`enterprise/project_forecast/report/planning_analysis_report.py`, `enterprise/project_timesheet_forecast/report/planning_analysis_report.py`, `enterprise/project_timesheet_forecast_sale/report/planning_analysis_report.py`) | Yes (pivot/graph) |
| `project.timesheet.forecast.report.analysis` | Reporting | SQL view that UNION-ALLs planning shifts (split per working day, honoring `resource_calendar_attendance` and leaves) with timesheets; surfaces `planned_hours`, `effective_hours`, `difference`, `planned_costs`, `effective_costs`, and (with sale) revenues, margins and billable/non-billable splits (`enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis.py`, `enterprise/project_timesheet_forecast_sale/report/project_timesheet_forecast_report_analysis.py`) | Yes (pivot/graph/list) |
| `ir.ui.menu` (extended) | Internal | Blacklists the analysis menu for users missing both Planning Manager and Timesheet Approver groups (`enterprise/project_timesheet_forecast/models/ir_ui_menu.py`) | No |

### Reports & Analytics

- **Schedule by Project gantt** (`planning_action_schedule_by_project`, `enterprise/project_forecast/views/planning_slot_views.xml`) — Gantt grouped by project with the `forecast_gantt` JS class, plus calendar/list/kanban/pivot/graph variants. Progress bars use `resource_id,project_id` and `percentage_hours` once `project_timesheet_forecast` is installed.
- **Schedule by Resource / Schedule by Role** — Same slot model, different default grouping, all sharing the project-aware context (`planning_expand_project: 1`) so empty buckets render. "Schedule by Role" is contributed by `project_timesheet_forecast` to re-route the core menu through a view-set that exposes the progress bar.
- **Planning Analysis Report pivot/graph** (`planning.analysis.report`) — Gains project, percentage/effective/remaining hours, allocated and effective hourly costs (grouped under `hr.group_hr_user` / `hr_timesheet.group_hr_timesheet_approver`), and billable vs. non-billable allocated hours with sale.
- **Planning / Timesheets Analysis** (`project.timesheet.forecast.report.analysis`, menu `planning.planning_menu_reporting`) — SQL view with list, pivot and graph; default pivot rows by month and line_type (`forecast` vs `timesheet`); saved filter `ir_filter_project_timesheet_forecast` ("Timesheet vs Planning") ships with it. Filters cover My Team, My Department, My Projects, This Week / Today / Last Week (`enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis_views.xml`, `enterprise/project_timesheet_forecast/data/ir_filters_data.xml`).
- **With sale extension:** adds planned/effective revenues, margins, and planned/effective billable and non-billable hours as measures on the pivot and graph (`enterprise/project_timesheet_forecast_sale/report/project_timesheet_forecast_report_analysis_views.xml`).
- **Project stat buttons:** "Planned — N Hours" (from `project_forecast`) and "Timesheets and Planning" (from `project_timesheet_forecast_sale`) on the project form; plus a dropdown entry "Timesheets and Planning Analysis" on the project kanban card.
- **Gantt progress bar per project** (`_gantt_progress_bar_project_id`) — In-line bar comparing the sum of `allocated_hours` against `project.allocated_hours` for each project row (`enterprise/project_timesheet_forecast/models/planning_slot.py`).

### Wizards & Advanced Actions

No `TransientModel` wizards are introduced by this family; advanced actions are exposed as model methods and `ir.actions.act_window`.

| Action | Trigger | Purpose |
|---|---|---|
| `action_project_forecast_from_project` | "Planned" stat button on project | Opens `project_forecast_action_from_project` scoped to the project; initial date is the first future shift or the project's `date_start` (`enterprise/project_forecast/models/project_project.py`) |
| `action_open_timesheets` | "Recorded" stat button on planning slot | Opens timesheets filtered by employee, project and the slot's date range; pre-fills `default_date`, `default_employee_id`, `default_project_id`, `default_unit_amount` when shift duration < 24h (`enterprise/project_timesheet_forecast/models/planning_slot.py`) |
| `open_timesheets_planning_report` | "Timesheets and Planning" stat button / kanban dropdown | Opens the Planning / Timesheets Analysis pivot filtered on the current project (`enterprise/project_timesheet_forecast_sale/models/project_project.py`) |
| `_init_remaining_hours_to_plan` / `_update_remaining_hours_to_plan_and_values` | Auto-planning from SOL | When the sold product does not have `planning_enabled`, caps the generated slots so the sum of shifts does not exceed `project.allocated_hours`, re-slicing the last slot's `end_datetime` to fit (`enterprise/project_timesheet_forecast_sale/models/planning_slot.py`) |
| Portal "Send Planning" extensions | Planning portal list / ICS | `enterprise/project_forecast/controllers/main.py` exposes `project` on open-shift and unwanted-shift portal listings; `enterprise/sale_project_forecast/views/planning_templates.xml` moves the Sale Order Item column to come after the Project column in the portal templates; ICS description gains a Project line via `_get_ics_description_data` |

### Per-module Feature Inventory

#### project_forecast (base layer)

- Adds `project_id` Many2one to `planning.slot` and `planning.slot.template`, with `check_company`, `group_expand='_read_group_project_id'` (so empty projects show up in Gantt when `planning_expand_project` is set), and domain `is_template=False` (`enterprise/project_forecast/models/planning_slot.py`, `planning_slot_template.py`).
- Inserts `project_id` in all planning views: list, form (one read-only variant, one clickable), calendar, kanban, search (with "My Projects" filter and "Project" group-by), pivot (row), graph (`enterprise/project_forecast/views/planning_slot_views.xml`).
- Contributes the "Schedule by Project" gantt action and menu, and overrides "Schedule by Resource" to install the `forecast_gantt` JS class and the project-aware context.
- Forces `gantt_view_id` of the project-scoped action to a variant that removes the `action_self_unassign` footer button, so planners (not the employee) control unassignment from the Gantt inline form.
- Adds `project.project.total_forecast_time` and the "Planned" stat button (shown only to `planning.group_planning_user`), plus the `_check_company_id` constraint preventing a company change on a project with shifts in other companies.
- Registers three `ir.rule` records on `planning.slot.template`: multi-company, admin-override for Project Managers, and a follower/visibility rule for regular users (`enterprise/project_forecast/security/project_forecast_security.xml`).
- Embeds the planning action on the project record via two `ir.embedded.actions` (tasks action and project-update action), gated by `planning.group_planning_user` (`enterprise/project_forecast/views/project_project_views.xml`).
- Portal: `ShiftControllerProject` overrides `_planning_get`, `_get_slot_title`, `_get_slot_vals` to surface the project in open/unwanted shift lists and in the slot ICS export (`enterprise/project_forecast/controllers/main.py`).
- Uninstall hook resets the "Schedule by Resource" menu back to the core planning action (`enterprise/project_forecast/__init__.py::_uninstall_hook`).
- Demo: `planning_role_demo.xml`, `planning_slot_template_demo.xml`, `planning_slot_demo.xml` (demo-only).

#### sale_project_forecast (auto-install bridge: sale_planning + sale_project + project_forecast)

- Makes `planning.slot.project_id` computable from the linked sale order line: uses `sale_line_id.task_id.project_id` if available, else `sale_line_id.project_id`. Conversely, when a project is set, the SOL is back-filled from `project.sale_line_id` (`enterprise/sale_project_forecast/models/planning_slot.py`).
- In "shifts to plan" gantt mode, if a `default_project_id` is in context, the domain is rewritten to match shifts on any SOL that belongs to the project's open tasks (`_get_shifts_to_plan_domain` in the same file).
- `_display_name_fields` re-orders so the project appears before the SOL in display names.
- Pushes `project_id` into `sale.order.line._planning_slot_values()` so auto-generated shifts land on the right project (`enterprise/sale_project_forecast/models/sale_order_line.py`).
- Restricts `planning.role.product_ids` to service, sellable, plannable products with a compatible `service_tracking` (`enterprise/sale_project_forecast/models/planning_role.py`).
- Disables `planning_enabled` on products whose `service_policy` is `delivered_manual` or `delivered_milestones` (`enterprise/sale_project_forecast/models/product_template.py`).
- Views: re-orders the "My Projects" and "My Sale Orders" filters in the planning search; adds `planning_expand_sale_line_id` to all planning action contexts; drops the `start/end_datetime` constraint from the project-scoped "Schedule by Project" action so SOL-only shifts still appear (`enterprise/sale_project_forecast/views/planning_slot_views.xml`).
- Product form: hides `service_policy` and `planning_enabled` fields for service policies that are incompatible with planning (`enterprise/sale_project_forecast/views/product_template_views.xml`).
- Portal: rearranges the period report and open/unwanted-shift templates so the Sale Order Item column follows the Project column (`enterprise/sale_project_forecast/views/planning_templates.xml`).

#### project_timesheet_forecast (auto-install bridge: timesheet_grid + project_forecast)

- Adds timesheet awareness to `planning.slot`: `allow_timesheets` (related to project), `effective_hours`, `percentage_hours`, `timesheet_ids`, `can_open_timesheets`, `encode_uom_in_days`. `effective_hours` sums `account.analytic.line.unit_amount` for the same employee + project + date range; `percentage_hours` is `effective / allocated × 100` (`enterprise/project_timesheet_forecast/models/planning_slot.py`).
- Implements `_gantt_progress_bar_project_id` to render planned-vs-capacity bars for each project row in Gantt, reading `project.allocated_hours` as the ceiling.
- Slot form adds a "Recorded" stat button linking to timesheets; list view adds an optional `effective_hours` column; pivot and graph expose `effective_hours` and `percentage_hours` as measures (gated on `hr_timesheet.group_hr_timesheet_approver`) (`enterprise/project_timesheet_forecast/views/planning_slot_views.xml`).
- Patches the project-scoped planning action to use a pivot view that renders `percentage_hours` as a measure (`enterprise/project_timesheet_forecast/models/project_project.py`).
- Adds `project.timesheet.forecast.report.analysis` — a full SQL view that:
  - Expands each planning slot into one row per working day using the employee's `resource_calendar_attendance`, excluding days under a `resource.calendar.leaves` (`enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis.py::_from`, `_where`).
  - Unions that with timesheet rows converted to hours via the `uom.product_uom_hour` factor.
  - Exposes `entry_date`, `employee_id`, `company_id`, `project_id`, `user_id`, `line_type` (`forecast` or `timesheet`), `planned_hours`, `effective_hours`, `difference`, `planned_costs`, `effective_costs`, `is_published`.
- Ships list, pivot, graph, search views and the "Planning / Timesheets Analysis" menu with a default `ir.filters` ("Timesheet vs Planning") and multi-company `ir.rule` (`enterprise/project_timesheet_forecast/report/project_timesheet_forecast_report_analysis_views.xml`, `enterprise/project_timesheet_forecast/data/ir_filters_data.xml`).
- Menu is hidden from users who are not both Planning Manager and Timesheet Approver (`enterprise/project_timesheet_forecast/models/ir_ui_menu.py`).
- Re-adds the "Schedule by Role" menu with a project-aware variant that renders progress bars; overrides the form in Gantt to drop `action_self_unassign`.
- Uninstall hook mirrors the `project_forecast` one (resets the schedule-by-resource menu).

#### project_timesheet_forecast_sale (auto-install bridge: project_timesheet_forecast + sale_timesheet + sale_project_forecast)

- `sale.order.line._compute_planning_hours_planned` is rewritten for plannable products whose project (or task) allows timesheets: picks up validated timesheets once, then only counts shifts after the latest validated timesheet date, avoiding double-counting when an employee logs the hours (`enterprise/project_timesheet_forecast_sale/models/sale_order_line.py`).
- On timesheet write, if `validated` or `unit_amount` change, triggers `so_line._post_process_planning_sale_line()` so subsequent shifts are re-capped (`enterprise/project_timesheet_forecast_sale/models/analytic_account_line.py`).
- `planning.slot._init_remaining_hours_to_plan` / `_update_remaining_hours_to_plan_and_values` are overridden so auto-generated shifts for non-plannable products respect `project.allocated_hours`, re-slicing the last shift's `end_datetime` to fit the remaining budget (`enterprise/project_timesheet_forecast_sale/models/planning_slot.py`).
- `project.project` gains `display_planning_timesheet_analysis` and the `open_timesheets_planning_report` action + stat button, plus the kanban dropdown item "Timesheets and Planning Analysis" (`enterprise/project_timesheet_forecast_sale/models/project_project.py`, `views/project_project_views.xml`).
- `planning.analysis.report` gains `billable_allocated_hours` (shifts with a SOL) and `non_billable_allocated_hours` (shifts without a SOL), plumbed into the pivot and graph (`enterprise/project_timesheet_forecast_sale/report/planning_analysis_report.py`, `planning_analysis_report_views.xml`).
- `project.timesheet.forecast.report.analysis` gains `planned_revenues`, `effective_revenues`, `planned_margin`, `effective_margin`, `planned_billable_hours`, `effective_billable_hours`, `planned_non_billable_hours`, `effective_non_billable_hours`, all computed by joining `sale_order_line.price_unit` and `hr_employee.hourly_cost` (`enterprise/project_timesheet_forecast_sale/report/project_timesheet_forecast_report_analysis.py`, `project_timesheet_forecast_report_analysis_views.xml`).
- Slot form adds `with_remaining_hours=True` on the `sale_line_id` field so the SOL autocomplete shows how many hours are still unplanned (`enterprise/project_timesheet_forecast_sale/views/planning_slot_views.xml`).
- Demo: planning roles, employees, plannable products and sale order lines (`enterprise/project_timesheet_forecast_sale/data/*`).

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `planning` | enterprise | Core shift/slot model (`planning.slot`) that these modules extend with `project_id` |
| `web_grid` | community | Grid widget required by `project_forecast` (gantt/grid planning) |
| `project` | community | Provides `project.project` that every extension above decorates |
| `sale_planning` | enterprise | Provides the SOL↔slot bridge and the auto-planning plumbing extended by `sale_project_forecast` |
| `sale_project` | enterprise | Links sale order lines to projects/tasks, consumed by `sale_project_forecast._compute_project_id` |
| `timesheet_grid` | enterprise | Grid-based timesheet entry; required by `project_timesheet_forecast` and used by the "Recorded" stat button |
| `hr_timesheet` | community | Provides `account.analytic.line` timesheets summed into `effective_hours`; groups gating measures in analytics (`group_hr_timesheet_user`, `group_hr_timesheet_approver`) |
| `sale_timesheet` | enterprise | Billable/non-billable semantics reused by `project_timesheet_forecast_sale` for margin and revenue computation |
| `project_forecast` | enterprise | Base layer; the other three all depend on it |
| `sale_project_forecast` | enterprise | Auto-installs when `sale_planning` + `sale_project` + `project_forecast` coexist |
| `project_timesheet_forecast` | enterprise | Auto-installs when `timesheet_grid` + `project_forecast` coexist |
| `project_timesheet_forecast_sale` | enterprise | Auto-installs when `project_timesheet_forecast` + `sale_timesheet` + `sale_project_forecast` coexist |

## Demo Highlights

1. **"Schedule by Project" Gantt with live plan-vs-actual progress bars** — Open `Planning > Schedule > By Project`, drop a service product's shifts onto the timeline; the Gantt renders each project as a swimlane with a `percentage_hours` progress bar computed from real timesheets. Moving a shift instantly re-colors the bar. Contributed by `project_forecast` + `project_timesheet_forecast`.

2. **Sell a plannable service, shifts appear automatically on the right project** — On a service product tick "Plan Services", attach a Planning Role, then quote and confirm a sale order. `sale_project_forecast` resolves `sale_line_id.task_id.project_id`, auto-creates shifts on the project, and the "Planned" stat button on the project already shows the forecast hours. Compelling for services/consulting prospects.

3. **"Timesheets and Planning" analysis** — From the project form (or the project kanban dropdown) the "Timesheets and Planning" button opens a pivot that unions planned shifts (day-by-day) and actual timesheets side by side, filtered on that project. With sale installed, the same pivot exposes planned vs. effective revenues and margins — a single screen that answers "did we stay on budget?".

4. **Budget-aware auto-planning** — Sell a service on a project with `allocated_hours = 40h`. Auto-planning stops exactly at 40h: `project_timesheet_forecast_sale` re-slices the last shift's `end_datetime` so the sum of allocated shifts does not exceed the project budget. Visible instantly on the "Planned" stat button.

5. **Billable vs. non-billable capacity** — In the Planning Analysis pivot, toggle the `billable_allocated_hours` / `non_billable_allocated_hours` measures to split forecasted workload between SOL-backed (billable) and internal (non-billable) shifts per employee or role — a demo-worthy KPI for services managers evaluating utilization.
