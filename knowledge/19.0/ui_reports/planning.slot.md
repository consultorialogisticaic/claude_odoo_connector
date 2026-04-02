# UI Report: planning.slot

## Model Summary
- **Model:** `planning.slot`
- **Description:** Planning Shift
- **Odoo Version:** 19.0
- **Source:** `odoo-workspace/19.0/enterprise/planning/models/planning_slot.py`
- **Inherits:** None (standalone, but uses resource.resource for employees)
- **_rec_name:** `name` (Text field -- the shift note, often empty)
- **_order:** `start_datetime desc, id desc`
- **_check_company_auto:** True

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `resource_id` | Many2one → resource.resource | No | The assigned resource (employee or material). Empty = Open Shift |
| `employee_id` | Many2one → hr.employee | Computed | Auto-set from resource_id if resource_type == 'user'. Do NOT set directly. |
| `role_id` | Many2one → planning.role | No | Shift role. Auto-computed from resource default or template |
| `start_datetime` | Datetime | Yes | Shift start (required by SQL constraint) |
| `end_datetime` | Datetime | Yes | Shift end (must be > start_datetime) |
| `allocated_hours` | Float | No | Hours allocated, computed from percentage and work intervals |
| `allocated_percentage` | Float | No | Default 100%, used for partial allocation |
| `company_id` | Many2one → res.company | Yes | Required, computed from resource or defaults to env.company |
| `template_id` | Many2one → planning.slot.template | No | Shift template used |
| `name` | Text | No | Shift note/description |
| `state` | Selection | No | 'draft' (default) or 'published' |
| `repeat` | Boolean | No | Enable recurrence (not stored, UI only) |

## SQL Constraints
- **`_check_start_date_lower_end_date`**: `CHECK(end_datetime > start_datetime)`
- **`_check_allocated_hours_positive`**: `CHECK(allocated_hours >= 0)`

## Python Constraints
- **`_check_repeat_until`**: Recurrence end date must be after shift start date.

## create() Override
- Sets `company_id` from resource if not provided.
- Sets `state = 'published'` for material resources.
- In `multi_create` context, filters slots against resource work schedules.

## write() Override (Complex)
- Handles shift reassignment email notifications.
- Clears `request_to_switch` when resource/dates change.
- Complex recurrence handling (`recurrence_update`): this/subsequent/all.

## _compute_role_id
- If no role set, takes `resource_id.default_role_id`.
- If `template_id` has a role, uses that role.

## _compute_employee_id
- `employee_id = resource_id.employee_id` when `resource_type == 'user'`.

## display_name Computation
- Built from start_datetime, resource_id, role_id, name (up to 4 labels joined by " - ").

## Demo Data Patterns (Odoo 19.0)
- Shifts are created via Python code in demo, not XML records with static values.
- Typical pattern: resource + role + start/end datetimes.
- Templates link shifts to roles for quick creation.

## Identity Key Recommendation
- **`resource_id` + `start_datetime` + `role_id`** -- compound key. A resource should not have overlapping shifts for the same role at the same time.

## CSV Loading Notes
- **IMPORTANT:** Set `resource_id` (not `employee_id`). The employee_id is computed.
- To find the resource_id for an employee, the FK resolver needs to search `resource.resource` by name or use the employee's resource.
- `start_datetime` and `end_datetime` must be UTC datetimes (e.g., "2026-04-01 08:00:00").
- Load `planning.role`, `hr.employee` BEFORE this model.
- `allocated_hours` is computed -- if set explicitly, `allocated_percentage` will recompute. Prefer setting `allocated_percentage` (default 100) and letting hours compute.
- For open shifts (no employee), leave `resource_id` empty.
- `state` defaults to 'draft'; set to 'published' if shifts should be visible to employees immediately.
- Recurrence fields (`repeat`, `repeat_interval`, etc.) are non-stored UI fields -- do not set in CSV.
