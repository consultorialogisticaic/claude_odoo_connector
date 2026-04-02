# UI Report: maintenance.request

## Model Summary
- **Model:** `maintenance.request`
- **Description:** Maintenance Request
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/maintenance/models/maintenance.py`
- **Inherits:** `mail.thread.cc`, `mail.activity.mixin`
- **_rec_name:** `name` (default)
- **_order:** `id desc`
- **_check_company_auto:** True

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Request subject |
| `company_id` | Many2one → res.company | Yes | Required, defaults to current company |
| `equipment_id` | Many2one → maintenance.equipment | No | Related equipment (ondelete='restrict') |
| `category_id` | Many2one → maintenance.equipment.category | Computed | Related from equipment_id.category_id, readonly |
| `maintenance_team_id` | Many2one → maintenance.team | Yes | Required, auto-defaults to first team |
| `user_id` | Many2one → res.users | No | Technician, computed from equipment's technician |
| `owner_user_id` | Many2one → res.users | No | Requester, defaults to current user |
| `stage_id` | Many2one → maintenance.stage | No | Pipeline stage, defaults to first stage |
| `priority` | Selection | No | '0'=Very Low, '1'=Low, '2'=Normal, '3'=High |
| `maintenance_type` | Selection | No | 'corrective' (default) or 'preventive' |
| `request_date` | Date | No | Request date, defaults to today, readonly in form |
| `schedule_date` | Datetime | No | Planned maintenance date |
| `schedule_end` | Datetime | No | Computed: schedule_date + 1 hour, can be overridden |
| `close_date` | Date | No | Auto-set when stage is marked done |
| `description` | Html | No | Request description/notes |
| `kanban_state` | Selection | Yes | Default 'normal'. Options: normal, blocked, done |
| `archive` | Boolean | No | Default False. Used instead of `active` for cancellation |
| `color` | Integer | No | Kanban color index |
| `recurring_maintenance` | Boolean | No | Enable recurrence (only for preventive type) |
| `repeat_interval` | Integer | No | Repeat every N, default 1 |
| `repeat_unit` | Selection | No | day/week/month/year, default 'week' |
| `repeat_type` | Selection | No | 'forever' or 'until', default 'forever' |
| `repeat_until` | Date | No | End date for recurrence |

### Instruction Fields
| Field | Type | Notes |
|---|---|---|
| `instruction_type` | Selection | 'pdf', 'google_slide', or 'text' (default 'text') |
| `instruction_pdf` | Binary | PDF attachment |
| `instruction_google_slide` | Char | Google Slides URL |
| `instruction_text` | Html | Text instructions |

## Python Constraints
- **`_check_schedule_end`**: End date cannot be earlier than start date.
- **`_check_repeat_interval`**: Repeat interval must be >= 1.

## _compute_maintenance_team_id
- If equipment has a team, use it.
- If current team's company doesn't match, clear it.

## _compute_user_id
- If equipment is set, uses equipment's technician or category's technician.
- Clears if user not in the request's company.

## create() Override
- Adds owner and technician as followers.
- Clears `close_date` if stage is not done; sets it to today if stage is done.
- Calls `activity_update()` to schedule maintenance activities.

## write() Override (Complex)
- Resets `kanban_state` to 'normal' when stage changes.
- **Recurrence:** When a preventive recurring request is moved to a "done" stage, automatically copies it with the next scheduled date.
- Sets `close_date` when stage is done, clears when not done.
- Updates activities on user/schedule changes.

## Demo Data Patterns (Odoo 19.0)
```
name: Resolution is bad, equipment_id: Samsung Monitor 15" (MT/127/...), stage_id: stage_3
name: Some keys are not working, equipment_id: Acer Laptop (LP/203/...), stage_id: stage_0
name: Motherboard failed, equipment_id: Acer Laptop (LP/205/...), stage_id: stage_4
name: Battery drains fast, equipment_id: HP Laptop (LP/303/...), stage_id: stage_1
name: Touchpad not working, equipment_id: HP Laptop (LP/305/...), stage_id: stage_1
```
- All requests have `maintenance_team_id` set.
- `user_id` (technician) and `owner_user_id` (requester) are always set.
- Various stages used (stage_0 through stage_4).
- `color` is set on some requests.

## Identity Key Recommendation
- **`name`** -- request subjects are typically unique within a demo dataset. For production-like data with potential duplicates, `name` + `equipment_id` could be used but `name` alone is practical for CSV dedup.

## CSV Loading Notes
- Load `maintenance.equipment.category`, `maintenance.equipment`, `maintenance.team` BEFORE this model.
- `equipment_id` resolves by display_name which is "name/serial_no" for equipment with serial numbers.
- `stage_id` resolves by name (e.g., "New Request", "In Progress", "Repaired", "Done").
- Default stages are created by `maintenance_data.xml`: New Request, In Progress, Repaired, Scrap (folded, done).
- `category_id` is auto-computed from equipment -- do NOT set it in CSV.
- `close_date` is auto-managed by stage transitions -- do NOT set it in CSV.
- `maintenance_type` defaults to 'corrective'; set to 'preventive' for scheduled maintenance with recurrence.
- `archive` is used for cancellation instead of `active`.
- `_target_state` pseudo-column can be used if you need stage transitions via CSV loader.
