# UI Report: hr.department

## Model Summary
- **Model:** `hr.department`
- **Description:** Department
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/hr/models/hr_department.py`
- **Inherits:** `mail.thread`, `mail.activity.mixin`
- **_rec_name:** `complete_name` (computed: "Parent / Child" hierarchy)
- **_order:** `name`
- **_parent_store:** True (hierarchical)

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Department Name, translatable |
| `parent_id` | Many2one → hr.department | No | Parent department (FK lookup by `complete_name`) |
| `manager_id` | Many2one → hr.employee | No | Department manager (FK lookup by `name`) |
| `company_id` | Many2one → res.company | No | Defaults to current company; computed from parent if parent has one |
| `color` | Integer | No | Kanban color index |
| `note` | Text | No | Notes |
| `active` | Boolean | No | Default True |

## Constraints
- **`_check_parent_id`**: No recursive departments (no cycles in parent chain).

## create() Override
- Calls `super().create()` with `mail_create_nosubscribe=True` context (prevents auto-subscribing creator).

## write() Override
- If `manager_id` changes, updates `parent_id` on all employees in the department whose current parent was the old manager.

## _compute_company_id
- If `parent_id` has a `company_id`, the child department inherits it.

## Demo Data Patterns (Odoo 19.0)
```
name: Management (top-level)
name: Sales, parent_id: Management
name: Research & Development, parent_id: Management
name: R&D USA, parent_id: Research & Development
name: Long Term Projects, parent_id: R&D USA
name: Professional Services, parent_id: Management
```
- Hierarchy goes up to 3 levels deep.
- Colors are set (5, 8, 9, 10, 3).
- Managers are set after employees exist.

## Identity Key Recommendation
- **`name`** -- department names are unique per company in practice. For hierarchical departments with duplicate names, use `complete_name` for FK resolution (the `_rec_name`).

## CSV Loading Notes
- Load top-level departments first, then children, so `parent_id` FK resolves.
- `manager_id` references `hr.employee` by name; set after employees exist or leave blank initially.
- The `complete_name` is computed (e.g., "Management / Sales"), not stored directly -- cannot be set via CSV.
