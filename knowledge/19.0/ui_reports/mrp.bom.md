# UI Report: mrp.bom (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `mrp.bom` |
| `_inherit` | `mail.thread`, `product.catalog.mixin` |
| `_description` | "Bill of Material" |
| `_order` | `sequence, id` |
| `_rec_name` | `product_tmpl_id` |
| `_rec_names_search` | `['product_tmpl_id', 'code']` |
| `_check_company_auto` | True |

## Key Fields for CSV Loading

### Required / Critical Fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `product_tmpl_id` | Many2one (product.template) | Yes | -- | Product template; domain `[('type', '=', 'consu')]`. FK resolved by name |
| `product_qty` | Float | Yes | `1.0` | Quantity to produce. SQL constraint: must be > 0 |
| `product_uom_id` | Many2one (uom.uom) | Yes | first UOM | Unit of Measure |
| `type` | Selection | Yes | `'normal'` | `normal` = Manufacture, `phantom` = Kit |
| `consumption` | Selection | Yes | `'warning'` | `flexible`, `warning`, `strict` |
| `ready_to_produce` | Selection | Yes | `'all_available'` | `all_available` or `asap` |

### Common Optional Fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `code` | Char | -- | BOM Reference (e.g. "BOM-001"). Used in `_rec_names_search` |
| `product_id` | Many2one (product.product) | -- | Specific variant; domain requires same template and `type='consu'` |
| `sequence` | Integer | -- | Display ordering |
| `active` | Boolean | `True` | Archiving flag |
| `produce_delay` | Integer | `0` | Manufacturing lead time in days |
| `days_to_prepare_mo` | Integer | `0` | Days in advance to create MO |
| `picking_type_id` | Many2one (stock.picking.type) | -- | Operation type; domain `[('code', '=', 'mrp_operation')]` |
| `company_id` | Many2one (res.company) | current company | Company |
| `allow_operation_dependencies` | Boolean | -- | Enable operation-level dependencies |
| `batch_size` | Float | `1.0` | Auto-generated MO batch size |
| `enable_batch_size` | Boolean | `False` | Toggle batch size feature |

### One2many Sub-lines (loaded separately)

| Field | Target Model | Notes |
|---|---|---|
| `bom_line_ids` | `mrp.bom.line` | Component lines (see separate report) |
| `byproduct_ids` | `mrp.bom.byproduct` | By-products |
| `operation_ids` | `mrp.routing.workcenter` | Work center operations |

## Constraints

1. **Product qty positive** (SQL): `product_qty > 0` -- "The quantity to produce must be positive!"
2. **BOM cycle check** (`_check_bom_cycle`): Prevents circular references where a BOM component eventually references the finished product.
3. **Variant consistency** (`_check_bom_lines`): Cannot use "Apply on Variant" attribute values when the BOM is for a specific variant (`product_id` set).
4. **By-product not same as main product**: A by-product cannot be the same product as the BOM's finished product.
5. **By-product cost share**: Must be >= 0 per line, total per variant cannot exceed 100%.

## create() / write() Overrides

### create()
- If `parent_production_id` is in context, links the new BOM to that Manufacturing Order automatically. No field-level side effects for CSV loading.

### write()
- If `bom_line_ids`, `byproduct_ids`, `product_tmpl_id`, `product_id`, or `product_qty` change, marks related MOs as having an outdated BOM.
- If `sequence` changes, re-runs the cycle check.

## Odoo Demo Data Patterns

From `mrp/data/mrp_demo.xml`:
- BOMs reference existing `product.template` records via XML ID
- `product_uom_id` set to `uom.product_uom_unit`
- `sequence` = 1
- `produce_delay` = 10 (days)
- Component lines created as separate `mrp.bom.line` records referencing the BOM
- Operations (`mrp.routing.workcenter`) created separately referencing the BOM

## CSV Loading Notes

- **Identity key**: `product_tmpl_id` (product template name). If multiple BOMs per product exist, add `code` as a compound key.
- **FK resolution**: `product_tmpl_id` resolves via `name_search` on `product.template`. `product_uom_id` resolves on `uom.uom`.
- **Load order**: Must load AFTER `product.template`. Load BEFORE `mrp.bom.line`.
- **type field**: Use `normal` for standard manufacturing BOMs, `phantom` for kits.
- **Avoid**: Do not set `bom_line_ids` inline; load `mrp.bom.line` in a separate CSV with FK to `bom_id`.

## Recommended Identity Keys

```json
["product_tmpl_id"]
```

If multiple BOMs per product template:
```json
["product_tmpl_id", "code"]
```
