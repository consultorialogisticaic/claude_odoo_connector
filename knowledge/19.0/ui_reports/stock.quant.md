# UI Report: stock.quant (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.quant` |
| `_description` | "Quants" |
| `_rec_name` | `product_id` |
| `_rec_names_search` | `['location_id', 'lot_id', 'package_id', 'owner_id']` |

## Key Fields for CSV Loading

### Identity Fields (define which quant to create/update)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `product_id` | Many2one (product.product) | Yes | -- | Product (ondelete=restrict) |
| `location_id` | Many2one (stock.location) | Yes | warehouse lot_stock_id | Location (ondelete=restrict) |
| `lot_id` | Many2one (stock.lot) | No | -- | Lot/Serial (ondelete=restrict) |
| `package_id` | Many2one (stock.package) | No | -- | Package (ondelete=restrict) |
| `owner_id` | Many2one (res.partner) | No | -- | Owner |

### Quantity Fields

| Field | Type | Notes |
|---|---|---|
| `inventory_quantity` | Float | The counted quantity (used in inventory mode) |
| `inventory_quantity_auto_apply` | Float | Alternative to `inventory_quantity` (auto-applies) |
| `quantity` | Float | **Read-only** -- actual on-hand quantity |
| `reserved_quantity` | Float | **Read-only** -- reserved quantity |

### Other Fields

| Field | Type | Notes |
|---|---|---|
| `in_date` | Datetime | Incoming date, defaults to now |
| `user_id` | Many2one (res.users) | Assigned user for counting |
| `inventory_date` | Date | Scheduled count date |

## Constraints

- **Cannot duplicate**: `copy()` raises UserError.
- **name_create returns False**: Cannot create via name_create.
- **Forbidden fields in inventory mode**: Cannot edit `product_id`, `location_id`, `lot_id`, `package_id`, `owner_id` on existing quants.

## create() / write() Overrides

### create() -- CRITICAL
The `create()` method is heavily overridden for inventory mode:
1. If `inventory_quantity` or `inventory_quantity_auto_apply` is in vals:
   - Validates only allowed fields are set.
   - Uses `_gather()` to find existing quant with same (product, location, lot, package, owner).
   - If existing quant found: updates it (does NOT create duplicate).
   - If no existing quant: creates new one.
   - Sets `inventory_quantity` which triggers inventory adjustment move.
2. If NOT in inventory mode: standard create.

### _load_records_create() (import mode)
- Auto-fills `location_id` with warehouse stock location if missing.
- Switches to `inventory_mode=True` context.

### Key Implication for CSV Loading
**Quants merge automatically.** If you create a quant for the same (product, location, lot, package, owner), it updates the existing one rather than creating a duplicate. This is inventory-safe.

## Odoo Demo Data Patterns

```xml
<record id="stock_inventory_1" model="stock.quant">
    <field name="product_id" ref="product.product_product_24"/>
    <field name="inventory_quantity">16.0</field>
    <field name="location_id" model="stock.location"
        eval="obj().env.ref('stock.warehouse0').lot_stock_id.id"/>
</record>
```

**Pattern**: Only set `product_id`, `location_id`, and `inventory_quantity`. The create method handles merging and inventory adjustment.

## CSV Loading Recommendations

### Recommended CSV Headers
```
product_id,location_id,inventory_quantity
```

For lot-tracked products:
```
product_id,location_id,lot_id,inventory_quantity
```

### Important Notes
1. **Use `inventory_quantity`** (not `quantity`) -- this triggers proper inventory adjustment moves.
2. `product_id` resolves via product name/default_code (name_search on `product.product`).
3. `location_id` resolves via `complete_name` (e.g., "WH/Stock/Shelf 1").
4. `lot_id` resolves via lot `name` -- but beware: lot name is only unique per product, so name_search may be ambiguous. Prefer loading lots separately first.
5. `location_id` auto-defaults to warehouse stock location if missing during import.
6. Duplicate (product, location, lot, package, owner) combinations merge automatically.

## Identity Key

**`product_id` + `location_id` + `lot_id`** -- The quant is uniquely identified by its product, location, and lot (plus package and owner, but those are rarely used in basic demos). The create method enforces this uniqueness via `_gather()`.
