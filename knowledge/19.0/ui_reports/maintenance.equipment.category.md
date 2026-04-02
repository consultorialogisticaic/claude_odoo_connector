# UI Report: maintenance.equipment.category

## Model Summary
- **Model:** `maintenance.equipment.category`
- **Description:** Maintenance Equipment Category
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/maintenance/models/maintenance.py`
- **Inherits:** None (standalone model)
- **_rec_name:** `name` (default)

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Category name, translatable |
| `company_id` | Many2one → res.company | No | Defaults to current company |
| `technician_user_id` | Many2one → res.users | No | Default responsible technician, defaults to current user |
| `color` | Integer | No | Kanban color index |
| `note` | Html | No | Comments |

## Constraints
- **`_unlink_except_contains_maintenance_requests`**: Cannot delete if equipment or maintenance requests are linked.

## create() / write() Overrides
- No custom `create()` or `write()`.

## Demo Data Patterns (Odoo 19.0)
```
name: Computers
name: Software
name: Printers
name: Monitors, technician_user_id: Administrator, color: 3
name: Phones, technician_user_id: Administrator
```

## Identity Key Recommendation
- **`name`** -- category names are unique in practice.

## CSV Loading Notes
- Simple master data model. Load BEFORE `maintenance.equipment`.
- `technician_user_id` resolves by user name or login.
- `equipment_properties_definition` is a PropertiesDefinition field -- advanced, typically not set via CSV.
