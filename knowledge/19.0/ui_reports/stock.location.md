# UI Report: stock.location (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.location` |
| `_description` | "Inventory Locations" |
| `_parent_name` | `location_id` |
| `_parent_store` | True |
| `_order` | `complete_name, id` |
| `_rec_name` | `name` (default -- but display_name uses `complete_name`) |
| `_rec_names_search` | `['complete_name', 'barcode']` |
| `_check_company_auto` | True |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | -- | Location name |
| `location_id` | Many2one (stock.location) | No | -- | Parent location |
| `usage` | Selection | Yes | `'internal'` | `supplier`, `view`, `internal`, `customer`, `inventory`, `production`, `transit` |
| `company_id` | Many2one (res.company) | No | current company | Empty = shared |
| `active` | Boolean | No | `True` | |
| `barcode` | Char | No | -- | Unique per company |
| `storage_category_id` | Many2one (stock.storage.category) | No | -- | Storage category |
| `replenish_location` | Boolean | No | False | Trigger replenishment suggestions |
| `cyclic_inventory_frequency` | Integer | No | `0` | Inventory frequency in days |

### Computed/Read-only Fields (do NOT set)

| Field | Notes |
|---|---|
| `complete_name` | Auto-computed: "Parent/Child" path |
| `warehouse_id` | Auto-computed from parent path |
| `parent_path` | Auto-managed by `_parent_store` |

## Constraints

1. **Unique barcode per company**: `unique(barcode, company_id)` (SQL).
2. **Non-negative inventory frequency**: `check(cyclic_inventory_frequency >= 0)` (SQL).
3. **Replenish location**: Cannot have parent/child both set as replenish.
4. **Scrap location**: Cannot set `usage='inventory'` if used as manufacturing destination.

## create() / write() Overrides

### create()
- Invalidates `warehouse_id` model cache after creation.

### write()
- **Cannot change company**: Raises UserError.
- **Cannot change usage to view**: If location has quants.
- **Cannot change usage**: If location has stock (reserved quantities).
- **Cannot archive**: If location is used by an active warehouse.
- **Cascading archive**: Archives/unarchives child locations when parent is toggled.
- Children with stock cannot be archived.

### name_create()
- Supports slash-separated names: "WH/Stock/Shelf1" auto-finds parent by `complete_name`.

## Odoo Demo Data Patterns

```xml
<record id="stock_location_14" model="stock.location">
    <field name="name">Shelf 2</field>
    <field name="barcode">SHELF2</field>
    <field name="location_id" model="stock.location"
        eval="obj().env.ref('stock.warehouse0').lot_stock_id.id"/>
</record>
<record id="location_order" model="stock.location">
    <field name="name">Order Processing</field>
    <field name="usage">internal</field>
    <field name="location_id" ref="stock.stock_location_company"/>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,location_id,usage,barcode,storage_category_id
```

### Important Notes
1. Load parent locations before children.
2. `location_id` (parent) resolves via `complete_name` (e.g., "WH/Stock").
3. `usage` defaults to `internal` -- only set if different.
4. `complete_name` is auto-computed -- never set it.
5. Most warehouse locations are auto-created by `stock.warehouse.create()` -- only add sub-locations (shelves, zones, bins).
6. `storage_category_id` resolves by `name`.

## Identity Key

**`complete_name`** -- The full hierarchical path is the natural unique identifier. It is used for `_rec_names_search` and `name_create()` resolution.
