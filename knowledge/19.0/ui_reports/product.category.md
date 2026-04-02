# UI Report: product.category (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `product.category` |
| `_inherit` | `mail.thread` |
| `_description` | "Product Category" |
| `_parent_name` | `parent_id` |
| `_parent_store` | True |
| `_rec_name` | `complete_name` |
| `_order` | `complete_name` |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | -- | Category name, trigram-indexed |
| `parent_id` | Many2one (product.category) | No | -- | Parent category (hierarchical) |
| `complete_name` | Char | Computed/Stored | -- | Full path: "Parent / Child". Auto-computed. |
| `product_properties_definition` | PropertiesDefinition | No | -- | Custom properties for products in this category |

## Constraints

1. **No recursive categories**: `_check_category_recursion()` prevents circular parent references.

## create() / write() Overrides

- No custom `create()` or `write()` overrides beyond standard ORM.
- `name_create(name)` creates a category with just the name.

## Display Name / _rec_name

- `_rec_name = 'complete_name'` -- FK resolution uses `complete_name` (e.g., "Furniture / Office").
- `_compute_display_name` respects `hierarchical_naming` context flag. Default shows `complete_name`.

## Odoo Demo Data Patterns

```xml
<record id="product_category_furniture" model="product.category">
    <field name="name">Furniture</field>
</record>
<record id="product_category_office" model="product.category">
    <field name="parent_id" ref="product.product_category_furniture"/>
    <field name="name">Office</field>
</record>
```

## CSV Loading Recommendations

### Recommended CSV Headers
```
name,parent_id
```

### Important Notes
1. Load parent categories before children (ordering matters).
2. `parent_id` FK resolves via `complete_name` (e.g., "Furniture").
3. `complete_name` is auto-computed -- never set it directly in CSV.
4. For nested categories, reference the parent by its `complete_name`.

## Identity Key

**`complete_name`** -- The complete hierarchical name is unique and is the `_rec_name`. Use `name` only if all categories are top-level; otherwise use `complete_name` for dedup.
