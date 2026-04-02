# UI Report: planning.role

## Model Summary
- **Model:** `planning.role`
- **Description:** Planning Role
- **Odoo Version:** 19.0
- **Source:** `odoo-workspace/19.0/enterprise/planning/models/planning_role.py`
- **Inherits:** None (standalone model)
- **_rec_name:** `name`
- **_order:** `sequence`

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Role name, translatable |
| `color` | Integer | No | Random default 1-11 |
| `sequence` | Integer | No | Display order |
| `active` | Boolean | No | Default True |
| `resource_ids` | Many2many → resource.resource | No | Resources assigned to this role |

## Constraints
- None (no SQL or Python constraints).

## create() / write() Overrides
- No custom `create()` or `write()`.
- `copy_data()` appends "(copy)" to name.

## Demo Data Patterns (Odoo 19.0)
```
name: Developer, color: 2
name: Community Manager, color: 3
name: Management, color: 4
name: Crane, color: 5
name: Projector, color: 6
name: Scanner, color: 7
name: Maintenance Technician, color: 8
name: Quality Control Inspector, color: 9
name: Furniture Assembler
name: Shipping Associate
name: Furniture Tools, color: 8
```
- Roles like Crane, Projector, Scanner, Furniture Tools are for material resources.
- `resource_ids` links roles to specific employee resources.

## Identity Key Recommendation
- **`name`** -- role names are unique in practice.

## CSV Loading Notes
- Simple model, load before `planning.slot.template` and `planning.slot`.
- `resource_ids` is Many2many and can be set later when assigning employees to roles via `hr.employee.planning_role_ids`.
- No company_id field -- roles are global.
