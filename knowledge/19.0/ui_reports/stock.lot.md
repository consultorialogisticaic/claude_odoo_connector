# UI Report: stock.lot (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.lot` |
| `_inherit` | `mail.thread`, `mail.activity.mixin` |
| `_description` | "Lot/Serial" |
| `_order` | `name, id` |
| `_rec_name` | `name` (default) |
| `_check_company_auto` | True |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | auto-generated from sequence | Lot/Serial Number, trigram-indexed |
| `product_id` | Many2one (product.product) | Yes | -- | Product (must have `tracking != 'none'` and `is_storable = True`) |
| `company_id` | Many2one (res.company) | No | computed from product | Auto-computed from `product_id.company_id` |
| `ref` | Char | No | -- | Internal reference |
| `note` | Html | No | -- | Description |
| `lot_properties` | Properties | No | -- | Custom lot properties |

### Computed/Read-only Fields (do NOT set)

| Field | Notes |
|---|---|
| `product_uom_id` | Related to `product_id.uom_id` |
| `product_qty` | Computed from quants |
| `location_id` | Computed from quants (single location only) |

## Constraints

1. **Unique lot per product per company**: `_check_unique_lot()` -- The combination of `(name, product_id, company_id)` must be unique. Cross-company lots (no company) are also checked.

## create() / write() Overrides

### create()
- Calls `_check_create()` to verify the picking type allows lot creation.
- Creates with `mail_create_nosubscribe=True` context.

### write()
- **Cannot change company**: If lot is in a location belonging to another company.
- **Cannot change product**: If stock moves exist with the lot and a different product.

### name computation
- `name` is computed: if not set, auto-generated from `product_id.lot_sequence_id.next_by_id()`.

## Odoo Demo Data Patterns

```xml
<record id="lot_product_27" model="stock.lot">
    <field name="name">0000000000029</field>
    <field name="product_id" ref="product.product_product_27"/>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,product_id
```

### Important Notes
1. `product_id` resolves via product `name` (or `default_code` via name_search).
2. The product must have `tracking` set to `'lot'` or `'serial'` and `is_storable = True`.
3. `name` can be auto-generated if left empty (uses product's lot sequence).
4. `company_id` is auto-computed from the product -- do not set manually.
5. Lot records only define the lot metadata. Actual stock quantities are in `stock.quant`.

## Identity Key

**`product_id` + `name`** -- The lot/serial number is unique per product (and company). This compound key is the natural identifier.
