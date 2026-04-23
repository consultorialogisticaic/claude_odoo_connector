# Feature Catalog — Project Enterprise (project_enterprise) — Sub-catalog

Sub-catalog — Enterprise companion to `project`: gantt, map, task recurrence, advanced project views. See `project.md` for the mainline catalog.

**Version:** 19.0
**Source:** enterprise
**Category:** Services/Project
**Dependencies:** project, web_map, web_gantt, web_enterprise

## Business Capabilities

- **Gantt planning for tasks and projects:** Adds a fully-featured Gantt view for `project.task` (grouped by assignee, project, or milestone) and for `project.project` itself, with drag-and-drop scheduling, dependency arrows, pill progress bars, and day/week/month/quarter/year scales.
- **Map view with route planning:** Displays tasks on an interactive map using each task's partner address; supports route computation (`routing="1"`), sequencing via drag-and-drop, and is activated automatically on actions like "Tasks from Milestone" and project task lists.
- **Smart auto-scheduling & auto-shift:** The `schedule_tasks` engine plans tasks inside each assignee's working calendar, respecting dependencies (topological sort), priorities, and flexible-resource week/day budgets. Auto-shift propagates a manual date change to dependent tasks forward or backward in time with buffer-preservation options.
- **Planning conflict & dependency warnings:** Computes `planning_overlap` (same assignee scheduled on overlapping windows that exceed their work calendar) and `dependency_warning` (task planned before a blocker's deadline). Both surface as inline alerts on the task form and as Gantt decorations.
- **Task recurrence extension:** Extends `project.task.recurrence` (defined in base `project`) so that `planned_date_begin` is carried forward / postponed along with the existing recurrence cycle, keeping Gantt-scheduled recurring work in sync.
- **Working-hours-aware allocated hours:** `allocated_hours` is auto-computed from `planned_date_begin` / `date_deadline` crossed with the assignee's (or company's) `resource.calendar`, factoring flexible resources' per-day and per-week hour caps.
- **Project sharing Gantt:** Adds a dedicated `task_sharing_gantt` view for the portal project-sharing experience so external collaborators see the same Gantt timeline (read-scoped, no cell creation).

## Feature Inventory

### Menu Structure

`project_enterprise` defines no new menu items — it is a bridge module that plugs additional view modes (`gantt`, `map`) into the base Project app's existing actions. All features surface by switching the view mode from inside the mainline `project` menus.

| Menu Path (inherited from `project`) | View Modes Added | Description |
|---|---|---|
| Project > My Tasks | `gantt`, `map` | `view_task_gantt_inherit_my_task` grouped by `project_id`; task Map view with assignees and planned date |
| Project > All Tasks | `gantt`, `map` | `view_task_gantt_inherit_all_task` grouped by `user_ids`; Map view with planned date and customer |
| Project > Projects (list/kanban) | `gantt` | `project_project_view_gantt` — timeline of all projects with `date_start` → `date`, grouped by project manager |
| Project > (inside a Project) > Tasks | `gantt`, `map` | `project_task_dependency_view_gantt` (color by stage, sparse dependencies); `project_task_map_view_no_title` (no project column) |
| Project > (Milestone stat button) > Tasks | `gantt`, `map` | `project_task_gantt_view_project_milestone` (grouped by milestone); map view without title |
| Contact > Tasks stat button | `gantt`, `map` | `project_task_view_gantt_res_partner` (project required on form) |
| Portal > Project Sharing | `gantt` | `project_task_view_gantt_inherited_project_sharing_task` with `js_class="task_sharing_gantt"` (read-only scheduling for shared portal users) |

### Settings & Feature Flags

`project_enterprise` does not expose its own settings records; it only tweaks the base Project settings form. The only change is a label refinement.

| Setting | Technical Field | What it Enables |
|---|---|---|
| Timesheets (setting label override) | inherited from `project.res_config_settings_view_form` — `setting[@id='log_time_tasks_setting']` | Re-labels the existing "Log time on tasks" setting to "Timesheets" on the enterprise UI (view override in `views/res_config_settings_views.xml`). |

All scheduling, Gantt, and map behavior is active by default once the module is installed (`auto_install=True` when `web_enterprise` + `web_gantt` + `web_map` are present).

### Key Models

`project_enterprise` defines no new models — every class in `models/` uses `_inherit` to extend existing ones. The table below documents what is added to each.

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `project.task` (extended) | Primary | Adds scheduling layer: `planned_date_begin`, `planned_date_start` (calendar-view compute), `planning_overlap`, `dependency_warning`, `user_names`, overlap/deadline search helpers, and the full auto-schedule / auto-shift engine (`schedule_tasks`, `_scheduling`, `_web_gantt_move_candidates`, `_gantt_progress_bar`, `_gantt_unavailability`, `get_all_deadlines`) | Yes |
| `project.project` (extended) | Primary | `web_gantt_write` for drag-and-drop on the project Gantt; `action_view_tasks` swaps in no-milestone Map view when milestones are disabled and removes Map entirely for template/hidden-partner projects; `action_create_from_template` reschedules tasks when a project is created from a template, shifting dates by the template delta | Yes |
| `project.task.recurrence` (extended) | Transactional | Adds `planned_date_begin` to `_get_recurring_fields_to_postpone` so recurring tasks keep their Gantt start date offset correctly | No (internal) |
| `res.users` (extended) | Configuration | `_get_calendars_validity_within_period`, `_get_valid_work_intervals`, `_get_project_task_resource` — used by the scheduling engine to fetch each user's work calendar and flex-resource hours | No (internal) |
| `report.project.task.user` (extended) | Reporting | Adds `planned_date_begin` to the Tasks Analysis SQL view (select + group_by), enabling pivot/graph analysis by scheduled start date | Yes (pivot/graph) |

### Reports & Analytics

- **Task Gantt (`project_task_view_gantt`)** — flagship view. `date_start="planned_date_begin"`, `date_stop="date_deadline"`, scales day→year, `display_unavailability="1"` (greys out off-hours via `_gantt_unavailability` computed from `resource.resource` leaves), `progress_bar="user_ids"` (workload bar per user, value = allocated hours, max = user's work hours), `decoration-danger="planning_overlap"` (red pill on conflict), `dependency_field="depend_on_ids"` (arrow drawing), `total_row="True"`, `pill_label="True"`, `precision="{'day': 'hour:quarter', 'week': 'day:half', 'month': 'day:half'}"`, `color="project_id"`. Popover includes an **Unschedule** action.
- **Task Gantt variants** — `view_task_gantt_inherit_my_task` (group by project), `view_task_gantt_inherit_all_task` (group by user), `project_task_gantt_view_project_milestone` (group by milestone), `project_task_dependency_view_gantt` (`color=stage_id_color`, `display_mode=sparse`), `project_task_view_gantt_res_partner` (project required).
- **Project Gantt (`project_project_view_gantt`)** — Projects themselves on a timeline (`date_start` → `date`), grouped by project manager, colored by stage, scales week→year. `js_class="project_gantt"` for rescheduling logic.
- **Project Sharing Gantt (`project_task_view_gantt_inherited_project_sharing_task`)** — `js_class="task_sharing_gantt"`, `cell_create="False"`, grouped by stage, exposes `portal_user_names` so external collaborators see assignees without internal user records.
- **Task Map (`project_task_map_view`, `..._no_title`, `..._no_title_no_milestone`)** — `res_partner="partner_id"`, `routing="1"` for route rendering, `allow_resequence="true"`, `default_order="sequence, planned_date_begin"`, `js_class="project_task_map"`. Exposes customer, project, milestone, assignees, planned date in the popover.
- **Task Calendar (extended)** — overridden to use `planned_date_start` (compute fallback to `date_deadline`) as `date_start`, so tasks without an explicit `planned_date_begin` still appear on the calendar.
- **Tasks Analysis (`report.project.task.user`, extended)** — the existing pivot/graph now includes `planned_date_begin` as a measurable/groupable dimension.
- **Planning Overlap & Dependency Warnings** — rendered inline on `project.task.view.form` via `project_task_view_form` inherit: yellow alert blocks with `planning_overlap` (HTML with overlapping-tasks summary) and `dependency_warning` (HTML with blocker task names). A **Tasks in Conflict** filter (`search_default_conflict_task`) + action `action_fsm_view_overlapping_tasks` surfaces conflicting tasks in Gantt + Map.
- **Deadline overlay (`get_all_deadlines`)** — RPC-readable endpoint returning project and milestone deadlines within a Gantt window, used client-side to render vertical deadline markers on the Gantt.

### Wizards & Advanced Actions

`project_enterprise` ships no `TransientModel` wizards. Its "advanced actions" are implicit gestures in the Gantt/Map/Calendar views, all backed by server-side methods:

| Action | Trigger | Backing Method | Purpose |
|---|---|---|---|
| Unschedule Task | Gantt popover button, task form "Unschedule" footer button | `action_unschedule_task` | Clears `planned_date_begin` + `date_deadline` |
| Smart Schedule | Gantt drag-to-plan on an unscheduled pill | `schedule_tasks(vals)` → `_scheduling(...)` | Topologically sorts the recordset by dependencies and priority, then plans each task inside its assignee's valid work intervals (honoring flexible-resource daily/weekly budgets); returns warnings (`no_intervals`) for tasks that could not be fit. |
| Rollback Scheduling | Notification "Undo" link after auto-schedule | `action_rollback_auto_scheduling(old_vals_per_task_id)` | Reverts each rescheduled task to its prior `planned_date_begin`/`date_deadline`/`user_ids`. |
| Auto-Shift Dependents | Moving a task pill in Gantt | `_web_gantt_move_candidates(...)` with forward/backward search, optional `consume_buffer` | Propagates the move to dependents (forward) or blockers (backward), preserving inter-task buffers. Emits warnings: `initial_deadline`, `conflict`, `no_intervals_error`, `past_error`. |
| Plan in Calendar | Calendar view drop | `plan_task_in_calendar(vals)` | Snaps `date_deadline` to the end of the contiguous work-interval run that covers `allocated_hours`; supports `task_calendar_plan_full_day`. |
| Check Overlapping Tasks | "Check it out" link on overlap alert | `action_fsm_view_overlapping_tasks` | Opens the combined Gantt + Map view filtered to the current user's conflicting tasks, centered on `planned_date_begin`. |
| View Tasks (Project Gantt popover) | Project Gantt popover | `action_view_tasks` (overridden) | Opens the project's task views, dropping the Map view when milestones or partner are hidden; otherwise substitutes the no-milestone map variant. |
| Gantt drag-write | Any Gantt pill edit | `web_gantt_write(data)` on `project.task` and `project.project` | Handles bulk m2m deltas (e.g. add/remove one user per pill) and protects m2o fields on `project.project` during schedule writes. |
| Create Project from Template | Project action from template | `action_create_from_template` (extended) | After the base copy, computes a delta between template and new `date_start` and re-runs `_scheduling` on the new tasks so their Gantt pills shift coherently. |

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `project_enterprise_hr` | enterprise (`enterprise/project_enterprise_hr/`) | Bridges `project_enterprise` with `hr`. Points `_get_project_task_resource()` to `employee_id.resource_id` so task scheduling uses HR working calendars / time off instead of the user's raw calendar. Adds a `to-do@` mail alias on `project.task` (bounces an "Create to-dos by email" hint into the task list help), re-created by `res.config.settings` if deleted. |
| `project_enterprise_hr_skills` | enterprise (`enterprise/project_enterprise_hr_skills/`) | Bridges with `project_hr_skills`. Overrides `project.task._get_additional_users(domain)` so that a Gantt/kanban search filter on `user_skill_ids` group-expands to employees who own the matching `hr.skill` records — i.e., you can pivot the Gantt by skill and see every user who can do the work. |
| `project_enterprise_hr_contract` | enterprise (`enterprise/project_enterprise_hr_contract/`) | Present in 19.0 enterprise as a tests-only shell (no manifest, no models) — reserved namespace that test suites in `hr_contract`-aware setups use to verify contract-aware validity windows drive the `_get_calendars_validity_within_period` override. No runtime features. |

Downstream modules that build on `project_enterprise`'s Gantt/Map layer (not companions of this module per se, but worth naming): `industry_fsm`, `project_holidays`, `project_helpdesk`, `project_account_budget`, `timesheet_grid`, `esg_project` — each depends on `project_enterprise` and adds domain-specific Gantt decorations (FSM scheduling, holiday greying, helpdesk→task linking, budget pills, timesheet grid slots, ESG rollups).

## Demo Highlights

1. **Gantt with Smart Auto-Schedule** — Drop an unscheduled task on the Gantt; the engine places it at the next valid interval in the assignee's work calendar, skips holidays/overlaps, honors dependencies, and respects priority. A toast offers **Undo** that reverts every date it touched. The dependency arrows and red overlap pills make the planning story visible at a glance.

2. **Route-Planning Task Map** — Open a project's tasks in Map view; customer addresses plot on OpenStreetMap and the **routing** flag draws the driving route in task order. Dragging a pin reorders the sequence. Flagship for field-visit or multi-site delivery projects where a consultant needs to show "one afternoon's work, one optimal route."

3. **Workload Progress Bars per Assignee** — On the Gantt grouped by assignee, each row shows a progress bar: current-period allocated hours vs. the assignee's available work hours (computed from their `resource.calendar`, leaves, and flexible-resource caps). Instantly reveals who is over-allocated for the week without running a report.

4. **Planning Conflict & Dependency Alerts** — A task form shows a yellow banner: "Maria has 3 tasks at the same time" with a "Check it out" link that opens the Gantt filtered to conflicting tasks. A second banner appears when a task is scheduled before its blocker's deadline, listing the blocker task names. Prevents scheduling errors before they hit the team.

5. **Create Project from Template with Re-Scheduled Tasks** — Demo the template workflow: pick a template project, set a new `date_start`, confirm — the new project's tasks are shifted by the exact template delta, then re-run through the calendar scheduler so they land on working hours. Turns a 4-week project plan into a reusable 30-second operation.
