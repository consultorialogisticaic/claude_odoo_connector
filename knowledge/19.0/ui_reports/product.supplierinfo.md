# UI Report: product.supplierinfo (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `product.supplierinfo` |
| `_description` | "Supplier Pricelist" |
| `_order` | `sequence, min_qty DESC, price, id` |
| `_rec_name` | `partner_id` |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `partner_id` | Many2one (res.partner) | Yes | -- | Vendor (ondelete=cascade) |
| `product_tmpl_id` | Many2one (product.template) | Yes | -- | Product Template (ondelete=cascade) |
| `product_id` | Many2one (product.product) | No | -- | Specific variant (optional) |
| `price` | Float | No | `0.0` | Unit price from vendor |
| `min_qty` | Float | Yes | `0.0` | Minimum quantity for this price |
| `currency_id` | Many2one (res.currency) | Yes | company currency | Currency |
| `delay` | Integer | Yes | `1` | Lead time in days |
| `sequence` | Integer | No | `1` | Priority ordering |
| `product_uom_id` | Many2one (uom.uom) | Yes | product's UoM | Auto-computed from product |
| `product_name` | Char | No | -- | Vendor's product name |
| `product_code` | Char | No | -- | Vendor's product code |
| `date_start` | Date | No | -- | Start date for this price |
| `date_end` | Date | No | -- | End date for this price |
| `discount` | Float | No | `0.0` | Discount percentage |
| `company_id` | Many2one (res.company) | No | current company | Company |

## Constraints

- No SQL or Python constraints.

## create() / write() Overrides

### create()
- `_sanitize_vals()`: If `product_id` is set but `product_tmpl_id` is not, automatically fills `product_tmpl_id` from the product's template.

### write()
- Same `_sanitize_vals()` logic applied.

## Odoo Demo Data Patterns

```xml
<record id="product_supplierinfo_1" model="product.supplierinfo">
    <field name="product_tmpl_id" ref="product_product_6_product_template"/>
    <field name="partner_id" ref="base.res_partner_1"/>
    <field name="delay">3</field>
    <field name="min_qty">1</field>
    <field name="price">750</field>
    <field name="currency_id" ref="base.USD"/>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
partner_id,product_tmpl_id,min_qty,price,currency_id,delay,product_code,product_name
```

### Important Notes
1. `partner_id` resolves via partner `name` (name_search).
2. `product_tmpl_id` resolves via product template `name`.
3. Multiple records can exist for the same product+vendor (different `min_qty` tiers).
4. `product_uom_id` is auto-computed -- do not set in CSV unless overriding.
5. `currency_id` resolves by currency `name` (e.g., "USD", "EUR").

## Identity Key

**`partner_id` + `product_tmpl_id` + `min_qty`** -- A vendor pricelist line is identified by the combination of vendor, product, and minimum quantity tier.
