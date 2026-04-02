# UI Report -- product.pricelist

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `product.pricelist` |
| **Defining module** | `product` (addons/product/models/product_pricelist.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | `['name', 'currency_id']` (line 13) |
| **`_compute_display_name`** | Custom: `"Pricelist Name (CURRENCY)"` e.g. "USD Retailers (USD)" (line 67) |
| **Inheriting modules** | `point_of_sale` (adds pos.load.mixin), `sale`, `website_sale`, etc. |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 28) | e.g. "Public Pricelist", "USD Retailers" |
| `currency_id` | Many2one(res.currency) | Python required=True (line 37) | Defaults to company currency |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `currency_id` | `display_name` | display_name includes currency in parentheses |

---

## 4. Constraint Rules

### Python Constraints

- None on the pricelist model itself. Constraints are on pricelist items.

### SQL Constraints

- None.

---

## 5. create() / write() Side Effects

- **write()**: After company_id change, validates company consistency on all item_ids. (line 72)
- No significant create() override.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `currency_id` | name_search on res.currency | By currency name or code |
| `company_id` | name_search on res.company | Optional -- leave empty for "Visible to all" |
| `country_group_ids` | name_search on res.country.group | Many2many, optional |

**Identity keys for deduplication:** `["name"]`

**Note on FK resolution TO this model:** `display_name` is `"Name (CURRENCY)"`. When other models reference a pricelist via name_search, the search checks both `name` and `currency_id` fields (due to `_rec_names_search`). Searching by just the pricelist name should work.

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- Default "Public Pricelist" is created by the product module's data files.
- POS scenarios do not create additional pricelists in demo.

**Key patterns:**
- Pricelists are typically pre-existing (default pricelist).
- POS configs reference pricelists via `pricelist_id` (default) and `available_pricelist_ids`.
- All available pricelists must share the same currency as the POS config.

---

## 8. CSV Generation Recommendations

- Simple model: `name`, `currency_id` are sufficient.
- `sequence` controls ordering (default 16).
- `company_id` is optional -- leave empty for multi-company visibility.
- Pricelist rules are loaded via separate `product.pricelist.item` CSV.
- Load pricelists BEFORE pos.config (config references pricelists).
- A default "Public Pricelist" usually already exists -- check before creating duplicates.
