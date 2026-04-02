# UI Report -- pos.config

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.config` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_config.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | `pos_restaurant` (floor_ids, iface_splitbill, set_tip_after_payment, default_screen) |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | form view required="1" (line 71) | e.g. "Main POS", "Bar" |
| `picking_type_id` | Many2one(stock.picking.type) | Python required=True (line 77) | Auto-defaults to warehouse pos_type_id |
| `company_id` | Many2one(res.company) | Python required=True (line 143) | Defaults to current company |
| `iface_tax_included` | Selection | Python required=True (line 111) | Defaults to 'total' |
| `picking_policy` | Selection | Python required=True (line 186) | Defaults to 'direct' |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `journal_id` | `currency_id` | Computed, stored. Currency from journal or company. |
| `payment_method_ids` | `cash_control`, `fast_payment_method_ids` | Computed. cash_control=True if any cash method. |
| `module_pos_restaurant` | installs pos_restaurant module | Side effect: triggers module install on create/write. Also auto-creates a floor and table (pos_restaurant). |
| `use_presets` + `default_preset_id` | `available_preset_ids` | write() auto-adds default_preset_id to available_preset_ids if missing. |
| `payment_method_ids` | `fast_payment_method_ids` | Filtered to only include methods in payment_method_ids. |

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_rounding_method_strategy`: If `cash_rounding=True`, `rounding_method.strategy` must be `'add_invoice_line'`. (line 448)
- `_check_company_payment`: All `payment_method_ids` must belong to the same company as the config. (line 469)
- `_check_currencies`: Default pricelist must be in `available_pricelist_ids`. All pricelist currencies must match config currency. Payment method journal currencies must match. Invoice journal currency must match. (line 475)
- `_check_pricelists`: Default pricelist company must match config company or be empty. (line 500)
- `_check_companies`: All available pricelists must belong to the config's company or no company. (line 508)
- `_check_payment_method_ids_journal`: Each cash payment method can only be used by ONE pos.config. Same cash journal cannot be on multiple payment methods. (line 520)
- `_check_trusted_config_ids_currency`: Trusted configs must use the same currency. (line 530)

### SQL Constraints

- None defined.

---

## 5. create() / write() Side Effects

- **create()**: Auto-creates 4 `ir.sequence` records (order_seq_id, order_backend_seq_id, order_line_seq_id, device_seq_id). (line 564)
- **create()**: Triggers `_check_modules_to_install()` -- installs modules for any `module_*` boolean set to True. (line 558)
- **create()**: If no warehouse exists, auto-creates one. (line 548)
- **create() [pos_restaurant]**: If `module_pos_restaurant=True`, auto-creates a default `restaurant.floor` with one table. (line 37, pos_restaurant/models/pos_config.py)
- **write()**: Cannot modify `module_pos_restaurant`, `payment_method_ids`, or `active` while a session is open. (line 717)
- **write()**: If `module_pos_restaurant` is set to False, clears `floor_ids`. (line 42, pos_restaurant)
- **write()**: Auto-adds `default_preset_id` to `available_preset_ids` if missing. (line 655)
- **_default_payment_methods()**: If no payment methods exist, auto-creates journal and payment methods. (line 55)

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `company_id` | name_search on res.company | Usually the main company |
| `journal_id` | name_search on account.journal | Must be type 'general' or 'sale' |
| `invoice_journal_id` | name_search on account.journal | Must be type 'sale' |
| `pricelist_id` | name_search on product.pricelist | display_name includes currency |
| `payment_method_ids` | name_search on pos.payment.method | Resolved by name |
| `default_preset_id` | name_search on pos.preset | |
| `available_preset_ids` | name_search on pos.preset | |
| `floor_ids` | name_search on restaurant.floor | |
| `iface_available_categ_ids` | name_search on pos.category | |
| `note_ids` | name_search on pos.note | |
| `default_bill_ids` | name_search on pos.bill | Resolved by name (which is the value string) |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/point_of_sale/data/demo_data.xml` -- calls `load_onboarding_furniture_scenario`, `load_onboarding_clothes_scenario`, `load_onboarding_bakery_scenario`
- `addons/pos_restaurant/data/demo_data.xml` -- calls `load_onboarding_restaurant_scenario`, `load_onboarding_bar_scenario`

**Key patterns:**
- POS configs are created programmatically via scenario loader methods, NOT via XML records.
- Restaurant scenario creates config with `module_pos_restaurant=True`, `use_presets=True`, `iface_splitbill=True`, and links preset records (Dine In, Takeout, Delivery).
- Bar scenario creates config with `module_pos_restaurant=True`, `default_screen='register'`, `iface_splitbill=True`.
- Each config gets its own dedicated cash journal and payment methods.
- Floors are linked to configs via `floor_ids` after creation.

---

## 8. CSV Generation Recommendations

- **Do NOT create pos.config via CSV** if possible -- the create() method has heavy side effects (sequence creation, module installation, floor auto-creation). Prefer creating via the Odoo UI or RPC.
- If you must use CSV, ensure `picking_type_id`, `journal_id`, and at least one `payment_method_ids` entry exist first.
- Set `module_pos_restaurant` to True for restaurant/bar configs -- this triggers pos_restaurant module installation.
- Set `use_presets=True` and link presets AFTER the preset records exist.
- Link `floor_ids` AFTER floor records exist.
- The `payment_method_ids` field is Many2many -- use comma-separated names in CSV.
- Cash payment methods are exclusive to one config -- do not share them.
