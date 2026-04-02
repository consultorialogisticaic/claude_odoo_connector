# UI Report: planning.slot.template

## Model Summary
- **Model:** `planning.slot.template`
- **Description:** Shift Template
- **Odoo Version:** 19.0
- **Source:** `odoo-workspace/19.0/enterprise/planning/models/planning_template.py`
- **Inherits:** None (standalone model)
- **_rec_name:** `name` (computed from start_time/end_time, e.g., "8:00 - 12:00")
- **_rec_names_search:** `['name', 'role_id']`
- **_order:** `sequence`

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `role_id` | Many2one → planning.role | No | Associated role |
| `start_time` | Float | No | Start hour as float (default 8.0 = 8:00 AM) |
| `end_time` | Float | No | End hour as float (default 17.0 = 5:00 PM) |
| `duration_days` | Integer | No | Span in working days, default 1, must be >= 1 |
| `sequence` | Integer | No | Display order |
| `active` | Boolean | No | Default True |

**Note:** `name` is a **computed stored field** ("8:00 - 17:00") -- do NOT set it in CSV.

## SQL Constraints
- **`_check_start_time_lower_than_24`**: `CHECK(start_time < 24)`
- **`_check_start_time_positive`**: `CHECK(start_time >= 0)`
- **`_check_duration_days_positive`**: `CHECK(duration_days > 0)`

## Python Constraints
- **`_check_start_and_end_times`**: For 1-day shifts, end_time must be >= start_time.

## create() / write() Overrides
- No custom `create()` or `write()`.

## Demo Data Patterns (Odoo 19.0)
```
role_id: Management, start_time: 8, end_time: 12, duration_days: 1, sequence: 1
role_id: Developer, start_time: 8, end_time: 12, duration_days: 1, sequence: 2
role_id: Community Manager, start_time: 8, end_time: 12, duration_days: 1, sequence: 3
role_id: Crane, start_time: 8, end_time: ..., duration_days: 1
```
- Morning shifts (8-12) and afternoon shifts (13-17) per role.
- Full day shifts (8-17) also exist.

## Identity Key Recommendation
- **`role_id` + `start_time` + `end_time`** -- combination of role and hours uniquely identifies a template. Since `name` is computed, it cannot serve as a direct lookup key.

## CSV Loading Notes
- Load `planning.role` BEFORE this model.
- `start_time` and `end_time` are floats: 8.5 = 8:30 AM, 13.0 = 1:00 PM, etc.
- `name` is auto-computed -- do not include in CSV.
- No company_id field -- templates are global.
