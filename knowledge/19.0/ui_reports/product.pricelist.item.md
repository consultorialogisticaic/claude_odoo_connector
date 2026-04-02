# UI Report -- product.pricelist.item

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `product.pricelist.item` |
| **Defining module** | `product` (addons/product/models/product_pricelist_item.py) |
| **`_rec_name`** | `name` (computed field, not stored) |
| **`_rec_names_search`** | Not set |
| **Inheriting modules** | `point_of_sale` (adds pos.load.mixin, no extra fields) |

**Note:** The `name` field is COMPUTED (line 155) -- it generates a description like "All Products", "Category: Electronics", or the product name. It cannot be set in CSV. This model lacks a natural unique identifier.

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `applied_on` | Selection | Python required=True (line 52) | `'3_global'`, `'2_product_category'`, `'1_product'`, `'0_product_variant'`. Default: `'3_global'`. Auto-computed in create() if not provided. |
| `display_applied_on` | Selection | Python required=True (line 63) | `'1_product'`, `'2_product_category'`. Default: `'1_product'` |
| `base` | Selection | Python required=True (line 92) | `'list_price'`, `'standard_price'`, `'pricelist'`. Default: `'list_price'` |
| `compute_price` | Selection | Python required=True (line 106) | `'percentage'`, `'formula'`, `'fixed'`. Default: `'fixed'` |

Conditionally required (based on `applied_on`):
| Field | Condition | Notes |
|---|---|---|
| `categ_id` | `applied_on == '2_product_category'` | Constraint: `_check_product_consistency` |
| `product_tmpl_id` | `applied_on == '1_product'` | Constraint: `_check_product_consistency` |
| `product_id` | `applied_on == '0_product_variant'` | Constraint: `_check_product_consistency` |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `compute_price` | `fixed_price`, `percent_price`, `base`, margins | Changing compute_price resets irrelevant fields to 0. **Must set explicitly in CSV.** |
| `product_id` | `product_tmpl_id`, `applied_on` | Auto-deduces template from variant. |
| `product_tmpl_id` | `applied_on` | |
| `base` | `price_discount`, `price_markup` | Resets to 0 on base change. |

**Critical for CSV:** Onchanges don't fire via create(). The create() method auto-computes `applied_on` from presence of product_id/product_tmpl_id/categ_id if not explicitly set. It also clears irrelevant fields based on applied_on.

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_base_pricelist_id` (line 317): If `base == 'pricelist'`, `base_pricelist_id` must be set.
- `_check_pricelist_recursion` (line 321): No circular pricelist references.
- `_check_date_range` (line 341): `date_end` must be after `date_start`.
- `_check_margin` (line 353): `price_min_margin <= price_max_margin`.
- `_check_product_consistency` (line 358): If `applied_on == '2_product_category'`, `categ_id` required. If `'1_product'`, `product_tmpl_id` required. If `'0_product_variant'`, `product_id` required.

### SQL Constraints

- None.

---

## 5. create() / write() Side Effects

- **create()** (line 466): Auto-sets `applied_on` based on which product/category fields are provided. Clears irrelevant fields based on `applied_on` (e.g., if global, clears product_id, product_tmpl_id, categ_id).
- **create()**: If `product_id` is set but `product_tmpl_id` is not, auto-deduces `product_tmpl_id` from the variant.
- **write()**: Same field cleanup based on `applied_on`.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `pricelist_id` | name_search on product.pricelist | Parent pricelist. display_name includes currency. |
| `product_tmpl_id` | name_search on product.template | |
| `product_id` | name_search on product.product | |
| `categ_id` | name_search on product.category | Internal product category, NOT pos.category |
| `base_pricelist_id` | name_search on product.pricelist | Only when base='pricelist' |

**Identity keys for deduplication:** `["pricelist_id", "product_tmpl_id", "applied_on", "compute_price", "min_quantity"]`

This is a complex compound identity. A pricelist rule is most practically identified by its pricelist + what it applies to + computation type + min quantity.

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- No standalone pricelist item demo data in POS module.
- Product module creates a default "Public Pricelist" with no special rules.

**Key patterns:**
- Rules are created inline within the pricelist form.
- Most common use case: fixed price rule for a specific product.
- Percentage discounts on all products or categories.

---

## 8. CSV Generation Recommendations

- Set `pricelist_id` to parent pricelist name.
- For fixed price rules: `compute_price=fixed`, `fixed_price=<amount>`, `applied_on=1_product`, `product_tmpl_id=<product name>`.
- For percentage discounts: `compute_price=percentage`, `percent_price=<discount%>`.
- For global rules: `applied_on=3_global` (no product/category needed).
- You can omit `applied_on` -- create() auto-computes it from product_tmpl_id/product_id/categ_id presence.
- `base` defaults to `'list_price'` which is correct for most cases.
- `min_quantity` defaults to 0 (applies to any quantity).
- Do NOT set `name` in CSV -- it is computed.
- Load AFTER product.pricelist, product.template, and product.category records exist.
