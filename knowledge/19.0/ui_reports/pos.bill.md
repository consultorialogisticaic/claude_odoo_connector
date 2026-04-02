# UI Report -- pos.bill

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.bill` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_bill.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | None |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `value` | Float | Python required=True (line 14) | The denomination value, e.g. 0.25, 1.00, 20.00. Digits=(16,4). |

Optional:
| `name` | Char | Not required | Display name. Usually same as value string ("0.25", "1.00"). |

---

## 3. Onchange Chains

None. Fields are independent.

---

## 4. Constraint Rules

### Python Constraints

- None.

### SQL Constraints

- None.

---

## 5. create() / write() Side Effects

- **name_create()** (line 16): Overridden. When creating via name, the name is parsed as float to set `value`. Raises UserError if name is not a valid number.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `pos_config_ids` | name_search on pos.config | Many2many. If empty, bill applies to all POS configs. |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/point_of_sale/data/point_of_sale_data.xml` (data, noupdate=1, forcecreate=0)

**Key patterns:**
- 13 denominations created: 0.05, 0.10, 0.20, 0.25, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00, 200.00.
- Both `name` and `value` are set (name = string representation of value).
- `pos_config_ids` is NOT set -- bills apply to all configs by default.
- Records use `forcecreate="0"` so they are only created on fresh install.

---

## 8. CSV Generation Recommendations

- These records already exist after module install. Only add custom denominations.
- Set both `name` (string) and `value` (float) for each denomination.
- `pos_config_ids` is optional -- leave empty for all configs, or specify config names.
- The `_order` is by `value` -- no need for a sequence field.
- Typically no need to create these via CSV -- the default set covers most currencies.
