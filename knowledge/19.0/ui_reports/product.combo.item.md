# UI Report -- product.combo.item

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `product.combo.item` |
| **Defining module** | `product` (addons/product/models/product_combo_item.py) |
| **`_rec_name`** | No `name` field. No `_rec_name` set. Uses default `display_name`. |
| **`_rec_names_search`** | Not set |
| **Inheriting modules** | `point_of_sale` (adds pos.load.mixin, no extra fields) |

**WARNING**: This model has NO `name` field. The csv_loader's FK resolution via `name_search` will not work for references TO this model. Identity must be resolved via compound keys.

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `combo_id` | Many2one(product.combo) | Python required=True (line 13) | Parent combo group |
| `product_id` | Many2one(product.product) | Python required=True (line 14) | The product option. Domain: `type != 'combo'`. |

Optional:
| Field | Type | Notes |
|---|---|---|
| `extra_price` | Float | Extra charge on top of combo base price. Default 0.0. |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `product_id` | `currency_id`, `lst_price` | Both are `related` fields from product_id. |

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_product_id_no_combo` (line 30): `product_id.type` cannot be `'combo'`. No combo-of-combos.

### SQL Constraints

- None. But parent combo has `_check_combo_item_ids_no_duplicates` -- no duplicate product_id within a combo.

---

## 5. create() / write() Side Effects

- No create/write overrides. Simple CRUD model.
- Creating a combo item triggers recomputation of parent combo's `base_price` and `combo_item_count`.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `combo_id` | name_search on product.combo | Resolved by combo name |
| `product_id` | name_search on product.product | Resolved by product name/default_code |

**Identity keys for deduplication:** `["combo_id", "product_id"]`

This is a compound identity model -- a combo item is uniquely identified by its parent combo + product.

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- Created programmatically as part of combo product scenarios.

**Key patterns:**
- Combo items are embedded in the combo form as inline editable list rows.
- Each item has `product_id` and optional `extra_price`.
- `lst_price` (related to product) is displayed but not stored on the item.

---

## 8. CSV Generation Recommendations

- CSV headers: `combo_id,product_id,extra_price`
- `combo_id` resolves by name_search on product.combo (match by name).
- `product_id` resolves by name_search on product.product.
- `extra_price` defaults to 0.0 if omitted.
- Load AFTER both `product.combo` and the product records exist.
- Ensure no duplicate `product_id` within the same `combo_id` (parent constraint).
- Products referenced must NOT be of type 'combo'.
