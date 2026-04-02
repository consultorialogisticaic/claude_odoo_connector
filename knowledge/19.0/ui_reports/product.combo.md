# UI Report -- product.combo

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `product.combo` |
| **Defining module** | `product` (addons/product/models/product_combo.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | `point_of_sale` (adds `qty_max`, `qty_free` fields) |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 12) | e.g. "Burger Choice", "Side Choice", "Drink Choice" |

Fields with validation at create (from constraints):
| Field | Type | Source | Notes |
|---|---|---|---|
| `combo_item_ids` | One2many | `@api.constrains` (line 64) | Must have at least 1 item. **Cannot be empty.** |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `combo_item_ids` | `base_price`, `combo_item_count` | base_price = min lst_price among items. Computed, not stored. |
| `company_id` | `currency_id` | Computed from company or main company. |

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_combo_item_ids_not_empty` (line 64): combo_item_ids must NOT be empty. Every combo must have >= 1 product.
- `_check_combo_item_ids_no_duplicates` (line 69): No duplicate `product_id` within the same combo.
- `_check_company_id` (line 75): Company consistency with parent product.template and combo items.
- `_check_qty_max` (POS, line 23): `qty_max >= 1`.
- `_check_qty_free` (POS, line 27): `qty_free >= 0`.
- `_check_qty_max_greater_than_qty_free` (POS, line 31): `qty_free <= qty_max`.

### SQL Constraints

- None.

---

## 5. create() / write() Side Effects

- No significant create/write overrides.
- `base_price` is computed (min price of items) -- do NOT set in CSV.

**CRITICAL**: The `_check_combo_item_ids_not_empty` constraint fires on create(). This means you CANNOT create a product.combo record without simultaneously providing combo_item_ids. However, since combo items are a separate model loaded via separate CSV, you must either:
1. Load combo items inline (One2many command syntax -- not supported by csv_loader), or
2. Create the combo record first, then immediately create combo items pointing to it (the constraint fires on create of the combo, not the items -- so loading the combo CSV with no items will FAIL).

**Workaround:** Load `product.combo` and `product.combo.item` in the same step, or disable the constraint temporarily.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `company_id` | name_search on res.company | Optional. Leave empty for "Visible to all". |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- Combo products are typically created programmatically within scenario loaders, not via standalone demo XML.

**Key patterns:**
- Combos are groups like "Burger Choice", "Side Choice", "Drink Choice".
- Each combo must have at least 1 combo item.
- POS extension adds `qty_max` (default 1) and `qty_free` (default 1).

---

## 8. CSV Generation Recommendations

- **IMPORTANT**: Due to the `_check_combo_item_ids_not_empty` constraint, you may need to handle combo creation carefully. The csv_loader creates records via `create()` which triggers the constraint.
- Set `name`, optionally `qty_max` and `qty_free` (from POS extension).
- `base_price` is computed -- do NOT include in CSV.
- `sequence` controls display order (default 10).
- Load `product.combo` BEFORE `product.combo.item`, but be aware of the non-empty constraint.
- If the constraint blocks creation, consider creating combos with a single dummy item first, then adding real items.
