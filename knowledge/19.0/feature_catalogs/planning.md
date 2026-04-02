# Feature Catalog: Planning (Enterprise)

**Module:** `planning`
**Version:** 19.0 | **Category:** Human Resources/Planning
**License:** OEEL-1 (Enterprise)
**Dependencies:** `hr`, `hr_hourly_cost`, `web_gantt`, `digest`

---

## 1. Menu Structure

| Menu Path | Action / Model | Access Groups |
|---|---|---|
| Planning | Root menu | `base.group_user` (all internal) |
| Planning > Schedule | Parent menu | `group_planning_manager` or `group_planning_user` |
| Planning > Schedule > By Resource | `planning.slot` (Gantt grouped by resource) | Manager/User |
| Planning > Schedule > By Role | `planning.slot` (Gantt grouped by role) | Manager/User |
| Planning > Open Shifts | `planning.slot` (unassigned shifts) | `group_planning_manager` |
| Planning > My Planning | `planning.slot` (current user's shifts, calendar) | All internal |
| Planning > Reporting > Planning Analysis | `planning.analysis.report` (pivot/graph) | `group_planning_user` |
| Planning > Configuration > Settings | `res.config.settings` (Planning app) | `base.group_system` |
| Planning > Configuration > Employees | `hr.employee` list | `group_planning_manager` |
| Planning > Configuration > Materials | `resource.resource` (material type) | `group_planning_manager` |
| Planning > Configuration > Roles | `planning.role` | `group_planning_manager` |
| Planning > Configuration > Shift Templates | `planning.slot.template` | `group_planning_manager` |

---

## 2. Settings

**Settings > Planning** (requires Planning Manager + System):

| Setting | Field | Description |
|---|---|---|
| Employee Unavailabilities | `planning_employee_unavailabilities` | Radio: `switch` (employees can request to switch shifts) or `unassign` (employees can unassign themselves). When `unassign`, a deadline field appears. |
| Deadline (days before shift) | `planning_self_unassign_days_before` | Integer: how many days before shift start an employee can unassign. |
| Project Planning | `module_project_forecast` | Boolean (upgrade): enables `project_forecast` module for project-based resource allocation. |
| Recurring Shifts (debug) | `planning_generation_interval` | Integer: how many months ahead to auto-generate recurring shifts. |

---

## 3. Key Models

| Model | Description | Key Fields |
|---|---|---|
| `planning.slot` | **Core entity: a shift** assigned to a resource for a time range | `name` (note), `resource_id`, `employee_id` (computed from resource), `role_id`, `start_datetime`, `end_datetime`, `allocated_hours`, `allocated_percentage`, `state` (draft/published), `template_id`, `company_id`, `department_id`, `repeat`/`repeat_interval`/`repeat_unit`/`repeat_type`/`repeat_until` |
| `planning.role` | Named role with color, assignable to resources | `name`, `color`, `resource_ids` (M2M), `sequence`, `slot_properties_definition` |
| `planning.slot.template` | Reusable shift pattern (start/end hours + role) | `name` (computed "HH:MM - HH:MM"), `role_id`, `start_time` (float), `end_time` (float), `duration_days` |
| `planning.recurrency` | Recurrence rule linked to a slot | `repeat_interval`, `repeat_unit`, `repeat_type`, `repeat_until`, `repeat_number`, `slot_ids` |
| `planning.planning` | Published schedule snapshot (sent to employees via email/portal) | `start_datetime`, `end_datetime`, `include_unassigned`, `access_token`, `is_planning_preview` |
| `planning.analysis.report` | SQL view for pivot/graph reporting | `allocated_hours`, `role_id`, `employee_id`, `department_id`, `start_datetime`, `state` |
| `planning.calendar.resource` | Resource availability for calendar rendering | (computed) |
| `resource.resource` | Extended by planning: adds `role_ids`, `default_role_id` | (from `resource` module, extended) |
| `hr.employee` | Extended: adds `default_planning_role_id`, `planning_role_ids`, `employee_token` | (from `hr` module, extended) |
| `res.company` | Extended: adds `planning_generation_interval`, `planning_employee_unavailabilities`, `planning_self_unassign_days_before` | (from `base`, extended) |

### Shift Lifecycle
1. **Draft** -- shift created, visible only to managers.
2. **Published** -- shift sent to employees via email with ICS calendar attachment; visible in employee portal and "My Planning".
3. Employees can **self-unassign** (if setting enabled) or **request to switch** with colleagues.
4. **Open Shifts** (no resource assigned) are visible to employees matching the role.

### Recurrence
- Shifts can repeat on day/week/month/year intervals.
- Recurring shifts are auto-generated up to N months ahead (configurable via `planning_generation_interval`, default 6 months).
- Edits can target "this shift", "this and following", or "all shifts" in the series.

---

## 4. Views

| View Type | Key Features |
|---|---|
| **Gantt** (custom JS: `planning_gantt`) | Primary view for scheduling; drag-and-drop shift assignment; grouped by resource or role; copy previous week; color-coded by role |
| **List** (custom JS: `planning_tree`) | Multi-edit; inline "Publish & Send" button; self-assign/unassign buttons for employees |
| **Form** (custom JS: `planning_form`) | Shift details: resource, role, dates, allocation %, recurrence settings, template autocomplete, properties |
| **Calendar** | Monthly/weekly calendar of shifts |
| **Kanban** | Shift cards grouped by resource/role |
| **Pivot** | Planning Analysis: allocated hours by month (custom JS) |
| **Graph** | Planning Analysis: allocated hours by resource per month (custom JS) |
| **Search** | Filters: My Shifts, Open Shifts, Published, Recurring; Group By: Resource, Role, Department, Start Date |

---

## 5. Reports

| Report | Model | Type | Description |
|---|---|---|---|
| **Planning Analysis** | `planning.analysis.report` | Pivot + Graph (SQL view) | Analyze allocated hours across roles, employees, departments over time. Measures: allocated_hours, allocated_percentage. |
| **Shift Schedule** (print) | `planning.slot` | QWeb HTML template (`slot_report`) | Printable weekly grid showing shifts per resource per day, color-coded by role. Used for posting physical schedules. |

---

## 6. Wizards

| Wizard | Model | Purpose |
|---|---|---|
| **Send Planning** | `planning.send` | Publish and email shifts to employees for a date range. Detects employees without email. Sends ICS attachments. Options: include open shifts, extra message. |
| **Planning Preview** | `planning.preview` | Preview the employee portal view of their schedule before publishing. Opens portal URL in new tab. |
| **HR Departure** | `hr_departure_wizard` (extended) | When archiving an employee, handles their future planning slots. |

---

## 7. Security Groups

| Group | XML ID | Implied By | Permissions |
|---|---|---|---|
| **User** | `planning.group_planning_user` | `base.group_user` | Read all shifts, manage own planning |
| **Administrator** | `planning.group_planning_manager` | `group_planning_user` | Full CRUD on shifts, roles, templates, settings, publishing |

### Key Access Rules
- Internal users can only **read** their own published shifts + open shifts + switch-requested shifts.
- Planning Users can read/write shifts.
- Planning Managers have full access.

---

## 8. Demo Data

File: `data/planning_demo.xml` (large file with many records)

### What the demo creates:
- **Roles:** Developer, Community Manager, Management, Crane, Projector, Scanner, Maintenance Technician, Quality Control Inspector, Furniture Assembler, Shipping Associate, Furniture Tools
- **Default roles** assigned to demo employees (admin, qdp, vad, ngh)
- **Shift Templates:** Morning/afternoon templates per role (e.g., Management 8:00-12:00, Developer 8:00-12:00)
- **Planning Slots:** Multiple weeks of shifts assigned to demo employees with various roles
- **Material Resources:** Demo material resources (Crane, Projector, Scanner) with shifts

### Demo patterns relevant to Percimon:
- Roles with color assignments
- Employees linked to multiple roles
- Shift templates with morning/afternoon splits
- Recurring shift patterns

---

## 9. Companion Modules

| Module | Source | Purpose |
|---|---|---|
| `planning_holidays` | Enterprise | Sync planning with time-off/leaves; block shifts during approved leaves |
| `planning_hr_skills` | Enterprise | Match shift roles to employee skills for smarter assignment |
| `hr_work_entry_planning` | Enterprise | Generate work entries (for payroll) from planning shifts |
| `project_forecast` | Enterprise | Resource allocation across projects; enabled via Settings toggle |
| `sale_planning` | Enterprise | Link planning shifts to sale orders for service delivery scheduling |

---

## 10. Percimon Relevance

For a Colombian frozen yogurt chain with multiple stores, Planning is ideal for:

- **Role-Based Scheduling:** Define roles matching store positions:
  - `Cajero/a` (Cashier) -- front register, POS operations
  - `Cocina` (Kitchen) -- yogurt prep, topping prep, restocking
  - `Gerente de Tienda` (Store Manager) -- opening/closing, cash reconciliation, staff supervision
  - `Limpieza` (Cleaning) -- if dedicated cleaning shifts exist
  - `Entrenamiento` (Training) -- for new hire onboarding shifts

- **Shift Templates:** Create reusable templates per role:
  - Morning shift: 6:00 - 14:00
  - Afternoon shift: 14:00 - 22:00
  - Opening shift: 5:30 - 10:00 (manager)
  - Closing shift: 18:00 - 23:00 (manager)

- **Multi-Store Scheduling:** Use `company_id` or `department_id` to separate shifts per store location. Each store is a department with its own schedule view.

- **Employee Self-Service:** Enable "Employee Unavailabilities" so staff can request shift switches or mark unavailability. Useful for part-time/student workers common in food service.

- **Weekly Publishing:** Managers build next week's schedule in Gantt view, then "Publish & Send" to push schedules to all employees via email with calendar attachments.

- **Recurring Shifts:** Set up weekly recurring patterns for stable staff, then adjust exceptions.

- **Planning Analysis:** Track allocated hours per role per store to optimize labor costs.

### Key models for demo data

| Model | CSV Loadable | Purpose |
|---|---|---|
| `planning.role` | Yes | Cashier, Kitchen, Manager, etc. |
| `planning.slot.template` | Yes | Morning/afternoon shift patterns per role |
| `hr.employee` | Yes (extend existing) | Set `default_planning_role_id`, `planning_role_ids` |
| `planning.slot` | Yes | Actual shift assignments (use relative dates) |
