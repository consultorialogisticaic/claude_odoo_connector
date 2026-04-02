# UI Report -- pos.category

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.category` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_category.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **`_compute_display_name`** | Custom: joins parent hierarchy with " / " separator (line 58) |
| **Inheriting modules** | None significant |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 25) | e.g. "Soft Drinks", "Food", "Desserts" |

---

## 3. Onchange Chains

No significant onchange chains. Fields are independent.

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_category_recursion` (line 17): No circular parent references allowed (calls `_has_cycle()`).
- `_check_hour` (line 81): `hour_until` and `hour_after` must be between 0.0 and 24.0. `hour_until` must be >= `hour_after`.

### SQL Constraints

- None defined.

### Delete protection

- `_unlink_except_session_open` (line 62): Cannot delete categories while any POS session is open (across all configs).

---

## 5. create() / write() Side Effects

- No create/write overrides. Simple CRUD model.
- `display_name` is computed as parent hierarchy: "Parent / Child / Grandchild".

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `parent_id` | name_search on pos.category | Beware: display_name is hierarchical ("Parent / Child") but name_search matches on `name` field |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/pos_restaurant/data/scenarios/restaurant_category_data.xml` -- creates "Food" and "Drinks" categories (referenced as `pos_restaurant.food`, `pos_restaurant.drinks`)
- `addons/pos_restaurant/data/scenarios/bar_category_data.xml` -- creates "Cocktails" and "Soft Drinks"
- `addons/point_of_sale/data/scenarios/furniture_category_data.xml`, `clothes_category_data.xml`, `bakery_category_data.xml`

**Key patterns:**
- Categories are created as flat records (no parent hierarchy in demo).
- Configs reference categories via `iface_available_categ_ids` when `limit_categories=True`.
- Color is set via `get_default_color()` which returns random 0-10.

---

## 8. CSV Generation Recommendations

- Simple model: `name`, optional `parent_id`, optional `sequence`, optional `color`.
- Set `parent_id` by name if creating hierarchical categories (e.g., "Food" as parent, "Appetizers" as child).
- `color` is integer 0-10. If omitted, a random color is assigned.
- `sequence` controls display order.
- `image_512` can be set for category images (base64 encoded).
- Load categories BEFORE pos.config (if config uses `limit_categories` + `iface_available_categ_ids`).
- `hour_after` and `hour_until` are Float fields for availability windows (online/self-order only). Default 0.0 and 24.0. Usually leave at defaults.
