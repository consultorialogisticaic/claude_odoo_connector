# UI Report: mrp.bom.line (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `mrp.bom.line` |
| `_description` | "Bill of Material Line" |
| `_order` | `sequence, id` |
| `_rec_name` | `product_id` |
| `_check_company_auto` | True |

## Key Fields for CSV Loading

### Required / Critical Fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `bom_id` | Many2one (mrp.bom) | Yes | -- | Parent BOM. FK resolved by `product_tmpl_id` name on `mrp.bom`. `ondelete='cascade'` |
| `product_id` | Many2one (product.product) | Yes | -- | Component product. FK resolved by name or `default_code` |
| `product_qty` | Float | Yes | `1.0` | Component quantity. SQL constraint: must be >= 0 |
| `product_uom_id` | Many2one (uom.uom) | Yes | first UOM | Auto-set from `product_id.uom_id` in create() if not provided |

### Common Optional Fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `sequence` | Integer | `1` | Display ordering |
| `operation_id` | Many2one (mrp.routing.workcenter) | -- | Which operation consumes this component. Only visible with `group_mrp_routings` |
| `bom_product_template_attribute_value_ids` | Many2many | -- | "Apply on Variants" -- only when BOM has no specific `product_id` |

### Computed / Read-only Fields (do NOT include in CSV)

| Field | Notes |
|---|---|
| `product_tmpl_id` | Related from `product_id.product_tmpl_id` (stored, read-only) |
| `parent_product_tmpl_id` | Related from `bom_id.product_tmpl_id` |
| `company_id` | Related from `bom_id.company_id` |
| `child_bom_id` | Computed: sub-BOM if the component has its own BOM |
| `tracking` | Related from `product_id.tracking` |

## Constraints

1. **Product qty non-negative** (SQL): `product_qty >= 0` -- quantities of 0 are treated as optional lines.
2. **BOM cycle** (inherited from parent `mrp.bom._check_bom_cycle`): Adding a line triggers parent BOM cycle validation.

## create() Override

- If `product_id` is set but `product_uom_id` is NOT provided, automatically sets `product_uom_id` to the product's default UOM (`product_id.uom_id`).
- This means `product_uom_id` can be omitted in CSV if you want the product's default UOM.

## Odoo Demo Data Patterns

From `mrp/data/mrp_demo.xml`:
```xml
<record id="mrp_bom_manufacture_line_1" model="mrp.bom.line">
    <field name="product_id" ref="product.product_product_12"/>
    <field name="product_qty">1</field>
    <field name="product_uom_id" ref="uom.product_uom_unit"/>
    <field name="sequence">5</field>
    <field name="bom_id" ref="mrp_bom_manufacture"/>
</record>
```

Key patterns:
- Each line is a separate record referencing the parent BOM
- `product_qty` always provided explicitly
- `product_uom_id` always set (though create() would auto-set it)
- `sequence` = 5 used as default for all lines in the same BOM

## CSV Loading Notes

- **Identity key**: Compound `bom_id` + `product_id` (a BOM should not have the same component twice).
- **FK resolution for `bom_id`**: The loader needs to find the parent BOM. Use the BOM's `product_tmpl_id` name (since `_rec_name = 'product_tmpl_id'`). If multiple BOMs exist per product, the BOM `code` field helps disambiguate.
- **FK resolution for `product_id`**: Resolves via `name_search` on `product.product`.
- **Load order**: Must load AFTER `mrp.bom` and `product.product`.
- **product_uom_id**: Can be omitted; create() auto-sets from product. Include only if the component UOM differs from the product's default.
- **Zero-quantity lines**: Allowed (treated as optional components).

## Recommended Identity Keys

```json
["bom_id", "product_id"]
```
