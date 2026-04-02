# UI Report: product.template (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `product.template` |
| `_inherit` | `mail.thread`, `mail.activity.mixin`, `image.mixin` |
| `_description` | "Product" |
| `_order` | `is_favorite desc, name` |
| `_rec_name` | `name` (default) |
| `_check_company_auto` | True |

## Key Fields for CSV Loading

### Required / Critical Fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | -- | Product name, translatable, trigram-indexed |
| `type` | Selection | Yes | `'consu'` | `consu` (Goods), `service` (Service), `combo` (Combo) |
| `uom_id` | Many2one (uom.uom) | Yes | `uom.product_uom_unit` | Default Unit of Measure |
| `categ_id` | Many2one (product.category) | No | -- | Product Category (FK resolved by name) |
| `list_price` | Float | No | `1.0` | Sales price |
| `standard_price` | Float | No | `0.0` | Cost (company-dependent, set via variant) |

### Stock-Specific Fields (from `stock` module inheriting `product.template`)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `is_storable` | Boolean | No | `False` | Must be `True` for inventory-tracked products |
| `tracking` | Selection | No | `'none'` | `serial`, `lot`, `none`. Auto-set to `none` if `is_storable=False` |
| `sale_delay` | Integer | No | `0` | Customer lead time in days |
| `responsible_id` | Many2one (res.users) | No | current user | Company-dependent |
| `description_picking` | Text | No | -- | Description on picking |

### Common Optional Fields

| Field | Type | Notes |
|---|---|---|
| `default_code` | Char | Internal Reference (stored, computed from single variant) |
| `barcode` | Char | Barcode (computed from single variant) |
| `sale_ok` | Boolean | Default `True` |
| `purchase_ok` | Boolean | Default `True` |
| `active` | Boolean | Default `True` |
| `weight` | Float | Weight (computed from variant) |
| `volume` | Float | Volume (computed from variant) |
| `description_sale` | Text | Sales description |
| `description_purchase` | Text | Purchase description |
| `image_1920` | Binary | Product image (supports `@images/` reference) |
| `sequence` | Integer | Default `1` |
| `product_tag_ids` | Many2many | Product tags |

## Constraints

1. **Combo must have choices**: If `type == 'combo'`, `combo_ids` cannot be empty (`_check_combo_ids_not_empty`).
2. **Combo sale_ok check**: If `type == 'combo'` and `sale_ok == True`, all combo item products must also be `sale_ok` (`_check_sale_combo_ids`).
3. **Barcode uniqueness**: Checked via `product_variant_ids._check_barcode_uniqueness()`.
4. **Negative cost warning**: `_onchange_standard_price` raises ValidationError if `standard_price < 0`.
5. **Tracking auto-reset**: If `is_storable` becomes False, `tracking` is forced to `'none'`.

## create() / write() Overrides

### create()
- Calls `_create_variant_ids()` to auto-create `product.product` variant(s).
- Propagates related fields (`barcode`, `default_code`, `standard_price`, `volume`, `weight`, `product_properties`) to the first variant.

### write()
- If `uom_id` changes: triggers UoM conversion on existing variants.
- If `attribute_line_ids` changes or product re-activated: calls `_create_variant_ids()`.
- If `active` set to `False`: deactivates all variants.
- If `image_1920` changes: invalidates variant image cache.
- If `type` changed away from `combo`: clears `combo_ids`.
- If `is_storable` changes (stock module): resets tracking, handles storable transition.

## Odoo Demo Data Patterns

From `product/data/product_demo.xml`:
```xml
<record id="product_delivery_01" model="product.product">
    <field name="name">Office Chair</field>
    <field name="categ_id" ref="product_category_office"/>
    <field name="standard_price">55.0</field>
    <field name="list_price">70.0</field>
    <field name="type">consu</field>
    <field name="weight">0.01</field>
    <field name="uom_id" ref="uom.product_uom_unit"/>
    <field name="default_code">FURN_7777</field>
    <field name="image_1920" type="base64" file="product/static/img/product_chair.jpg"/>
</record>
```

**Key pattern**: Demo creates `product.product` records (not `product.template`). Each product.product auto-creates its template. For CSV loading via RPC, use `product.template` to set template-level fields (name, categ_id, type, list_price) and set variant-level fields (default_code, barcode, standard_price) which propagate to the single variant.

For storable products, `is_storable` is set separately in `stock/data/stock_demo_pre.xml`:
```xml
<record id="product.product_product_3" model="product.product">
    <field name="is_storable" eval="True"/>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,type,categ_id,list_price,standard_price,default_code,uom_id,is_storable,tracking,sale_ok,purchase_ok,weight,image_1920
```

### Important Notes
1. Set `is_storable` to `True` for any product needing inventory tracking.
2. Set `tracking` only when `is_storable` is `True` (otherwise auto-reset to `none`).
3. `categ_id` resolves via `complete_name` (e.g., "Furniture / Office").
4. `uom_id` resolves via `name` (e.g., "Units", "kg").
5. `image_1920` supports `@images/<filename>` syntax for auto-encoding.
6. `default_code` and `barcode` are propagated to the auto-created variant.

## Identity Key

**`name`** -- Product name is the natural identifier. `default_code` is also unique-ish but not enforced at DB level (only a warning). Use `name` for dedup.
