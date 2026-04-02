# UI Report: stock.warehouse.orderpoint (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.warehouse.orderpoint` |
| `_description` | "Minimum Inventory Rule" |
| `_order` | `location_id, company_id, id` |
| `_check_company_auto` | True |
| `_rec_name` | `name` (default) |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | auto-sequence | Auto-generated from `stock.orderpoint` sequence. Read-only. |
| `product_id` | Many2one (product.product) | Yes | -- | Product (must be storable). ondelete=cascade. |
| `warehouse_id` | Many2one (stock.warehouse) | Yes | computed from location | Auto-computed from `location_id.warehouse_id` |
| `location_id` | Many2one (stock.location) | Yes | computed from warehouse | Auto-computed as `warehouse.lot_stock_id` |
| `product_min_qty` | Float | Yes | `0.0` | Minimum stock level (trigger point) |
| `product_max_qty` | Float | Yes | `0.0` | Maximum stock level (target) |
| `trigger` | Selection | Yes | `'auto'` | `auto` or `manual` |
| `company_id` | Many2one (res.company) | Yes | current company | |
| `route_id` | Many2one (stock.route) | No | -- | Specific replenishment route |
| `replenishment_uom_id` | Many2one (uom.uom) | No | -- | Rounding UoM for procurement |
| `active` | Boolean | No | `True` | |

## Constraints

1. **Unique product per location per company**: `unique(product_id, location_id, company_id)` (SQL). Only one reordering rule per product per location.

## create() / write() Overrides

- No significant custom `create()` or `write()` overrides for data loading purposes.
- `name` is auto-generated from `ir.sequence('stock.orderpoint')` -- read-only.
- `warehouse_id` auto-computes from `location_id`.
- `location_id` auto-computes from `warehouse_id`.

## Odoo Demo Data Patterns

```xml
<record id="stock_warehouse_orderpoint_1" model="stock.warehouse.orderpoint">
    <field name="product_max_qty">10.0</field>
    <field name="product_min_qty">5.0</field>
    <field name="product_uom" ref="uom.product_uom_unit"/>
    <field model="stock.warehouse" name="warehouse_id" search="[]"/>
    <field name="product_id" ref="product.product_delivery_02"/>
    <field name="location_id" model="stock.location"
        eval="obj().env.ref('stock.warehouse0').lot_stock_id.id"/>
</record>
```

**Pattern**: Set `product_id`, `warehouse_id`, `location_id`, `product_min_qty`, `product_max_qty`.

## CSV Loading Recommendations

### Recommended CSV Headers
```
product_id,warehouse_id,location_id,product_min_qty,product_max_qty
```

Or minimal (uses defaults):
```
product_id,product_min_qty,product_max_qty
```

### Important Notes
1. `product_id` resolves via name_search on `product.product`.
2. `warehouse_id` resolves via warehouse `name`. If omitted, auto-computed from location.
3. `location_id` resolves via `complete_name`. If omitted, defaults to warehouse's stock location.
4. Only one rule per (product, location, company) is allowed.
5. `name` is auto-generated -- do NOT set in CSV.
6. `product_uom` is related to `product_id.uom_id` -- do not set.

## Identity Key

**`product_id` + `warehouse_id`** -- One reordering rule per product per warehouse (technically per location, but location defaults to the warehouse stock location). The SQL constraint enforces `unique(product_id, location_id, company_id)`.
