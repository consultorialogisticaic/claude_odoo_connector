# UI Report: stock.storage.category (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.storage.category` |
| `_description` | "Storage Category" |
| `_order` | `name` |
| `_rec_name` | `name` (default) |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | -- | Storage category name |
| `max_weight` | Float | No | `0.0` | Maximum weight (must be >= 0) |
| `allow_new_product` | Selection | Yes | `'mixed'` | `empty`, `same`, `mixed` |
| `company_id` | Many2one (res.company) | No | -- | Company (optional) |

### Related Models

**`stock.storage.category.capacity`** (One2many via `capacity_ids`):

| Field | Type | Required | Notes |
|---|---|---|---|
| `storage_category_id` | Many2one | Yes | Parent storage category |
| `product_id` | Many2one (product.product) | No | Product capacity rule |
| `package_type_id` | Many2one (stock.package.type) | No | Package type capacity rule |
| `quantity` | Float | Yes | Must be > 0 |

Capacity constraints:
- `unique(product_id, storage_category_id)` -- one capacity rule per product.
- `unique(package_type_id, storage_category_id)` -- one capacity rule per package type.

## Constraints

1. **Non-negative max_weight**: `CHECK(max_weight >= 0)` (SQL).

## create() / write() Overrides

- No custom `create()` or `write()` overrides.

## Odoo Demo Data Patterns

```xml
<record id="stock_storage_category_high_small" model="stock.storage.category">
    <field name="name">High frequency - Small</field>
    <field name="max_weight">200</field>
</record>
<record id="stock_storage_category_high_big" model="stock.storage.category">
    <field name="name">High frequency - Big</field>
    <field name="max_weight">3000</field>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,max_weight,allow_new_product
```

### Important Notes
1. Simple model -- just `name` and `max_weight` are typically sufficient.
2. `allow_new_product` defaults to `mixed` -- only set if you need `empty` or `same`.
3. Capacity rules (product/package limits) are loaded separately as `stock.storage.category.capacity` records.
4. Assign to locations via `stock.location.storage_category_id`.

## Identity Key

**`name`** -- Storage category name is the natural identifier.
