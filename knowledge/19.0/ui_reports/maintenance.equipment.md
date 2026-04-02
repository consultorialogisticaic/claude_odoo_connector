# UI Report: maintenance.equipment

## Model Summary
- **Model:** `maintenance.equipment`
- **Description:** Maintenance Equipment
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/maintenance/models/maintenance.py`
- **Inherits:** `mail.thread`, `mail.activity.mixin`, `maintenance.mixin`
- **_rec_name:** `name` (default, but display_name is computed as "name/serial_no")
- **_check_company_auto:** True

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Equipment name, translatable |
| `category_id` | Many2one → maintenance.equipment.category | No | Equipment category |
| `company_id` | Many2one → res.company | No | Defaults to current company (from maintenance.mixin) |
| `owner_user_id` | Many2one → res.users | No | Owner/assignee |
| `technician_user_id` | Many2one → res.users | No | Responsible technician |
| `maintenance_team_id` | Many2one → maintenance.team | No | Assigned maintenance team |
| `serial_no` | Char | No | Serial number, must be globally unique |
| `model` | Char | No | Equipment model/make |
| `partner_id` | Many2one → res.partner | No | Vendor/supplier |
| `partner_ref` | Char | No | Vendor reference |
| `effective_date` | Date | Yes (default today) | Used for MTBF calculations |
| `cost` | Float | No | Equipment cost |
| `warranty_date` | Date | No | Warranty expiration |
| `assign_date` | Date | No | Date assigned to owner |
| `scrap_date` | Date | No | Scrap/disposal date |
| `note` | Html | No | Notes |
| `color` | Integer | No | Kanban color index |
| `active` | Boolean | No | Default True |
| `expected_mtbf` | Integer | No | Expected mean time between failure (days) |

## SQL Constraints
- **`_serial_no`**: `unique(serial_no)` -- serial number must be globally unique.

## _compute_display_name
- If `serial_no` is set: `"name/serial_no"`. Otherwise just `name`.

## create() Override
- Subscribes `owner_user_id` as a follower if set.

## write() Override
- Subscribes new `owner_user_id` as a follower if changed.

## _onchange_category_id
- When category changes, sets `technician_user_id` from the category's default technician.

## Demo Data Patterns (Odoo 19.0)
```
name: Samsung Monitor 15", category_id: Monitors, serial_no: MT/122/11112222, model: NP300E5X
name: Samsung Monitor 15", category_id: Monitors, serial_no: MT/125/22778837, model: NP355E5X
name: Samsung Monitor 15", category_id: Monitors, serial_no: MT/127/18291018, model: NP355E5X, color: 3
name: Acer Laptop, category_id: Computers, serial_no: LP/203/19281928, model: NE56R
name: Acer Laptop, category_id: Computers, serial_no: LP/205/12928291, model: V5131
name: HP Laptop, category_id: Computers, serial_no: LP/303/28292090, model: 17-j059nr
name: HP Laptop, category_id: Computers, serial_no: LP/305/17281718
name: HP Inkjet printer, category_id: Printers, serial_no: PR/011/2928191889
```
- Note: Multiple equipment records share the SAME name but have UNIQUE serial numbers.
- All have `owner_user_id` and `technician_user_id` set.
- `assign_date` uses relative dates.

## Identity Key Recommendation
- **`serial_no`** -- globally unique by SQL constraint. This is the best dedup key since names are not unique.

## CSV Loading Notes
- Load `maintenance.equipment.category` BEFORE this model.
- `serial_no` MUST be unique -- use it as the identity key for dedup.
- `name` is NOT unique (multiple monitors can share "Samsung Monitor 15").
- `owner_user_id` and `technician_user_id` resolve by user name.
- `maintenance_team_id` resolves by team name.
- `effective_date` defaults to today if not set.
