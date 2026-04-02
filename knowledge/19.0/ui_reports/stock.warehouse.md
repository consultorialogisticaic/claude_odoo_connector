# UI Report: stock.warehouse (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.warehouse` |
| `_description` | "Warehouse" |
| `_order` | `sequence, id` |
| `_check_company_auto` | True |
| `_rec_name` | `name` (default) |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | company name + counter | Warehouse name |
| `code` | Char(5) | Yes | company name[:5] | Short name (max 5 chars) |
| `company_id` | Many2one (res.company) | Yes | current company | Read-only after creation |
| `partner_id` | Many2one (res.partner) | No | company partner | Warehouse address |
| `reception_steps` | Selection | Yes | `'one_step'` | `one_step`, `two_steps`, `three_steps` |
| `delivery_steps` | Selection | Yes | `'ship_only'` | `ship_only`, `pick_ship`, `pick_pack_ship` |
| `active` | Boolean | No | `True` | |
| `sequence` | Integer | No | `10` | |

### Auto-created Fields (do NOT set in CSV)

| Field | Notes |
|---|---|
| `view_location_id` | Auto-created view location |
| `lot_stock_id` | Auto-created stock location |
| `wh_input_stock_loc_id` | Auto-created input location |
| `wh_output_stock_loc_id` | Auto-created output location |
| `wh_pack_stock_loc_id` | Auto-created packing location |
| `wh_qc_stock_loc_id` | Auto-created QC location |
| All `*_type_id` fields | Auto-created picking types |
| `reception_route_id`, `delivery_route_id` | Auto-created routes |

## Constraints

1. **Unique name per company**: `unique(name, company_id)` (SQL).
2. **Unique code per company**: `unique(code, company_id)` (SQL).
3. **Cannot change company**: `write()` raises UserError if `company_id` changes.
4. **Cannot archive with ongoing moves**: Raises UserError if active moves exist.

## create() / write() Overrides

### create()
- **Heavily overridden**: Auto-creates view location, sub-locations, sequences, picking types, routes, and stock rules.
- If `company_id` set: auto-fills `name`, `code`, `partner_id` from company if missing.
- Creates full warehouse infrastructure (locations, picking types, routes).

### write()
- Cannot change `company_id`.
- Changes to `reception_steps` / `delivery_steps` trigger location and route rebuilding.
- Changes to `code` / `name` trigger sequence and picking type updates.
- Archiving checks for ongoing operations.

## Odoo Demo Data Patterns

The default warehouse (`stock.warehouse0`) is created by stock module data, not demo data. Demo data only references it. Typically warehouses are NOT loaded via CSV -- they are created through the UI or during module installation.

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,code,reception_steps,delivery_steps
```

### Important Notes
1. **Rarely loaded via CSV** -- the default warehouse is auto-created. Only load additional warehouses.
2. `code` must be max 5 characters and unique per company.
3. Do NOT set location or picking type fields -- they are auto-created.
4. The `create()` method is very complex; minimal fields suffice.
5. `company_id` defaults to current company and cannot be changed after creation.

## Identity Key

**`name`** -- Warehouse name is unique per company (SQL constraint).
