# UI Report -- restaurant.table

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `restaurant.table` |
| **Defining module** | `pos_restaurant` (addons/pos_restaurant/models/pos_restaurant.py) |
| **`_rec_name`** | No `name` field. No explicit `_rec_name`. |
| **`_compute_display_name`** | Custom: `"{floor_name}, {table_number}"` (line 111) |
| **`_rec_names_search`** | Not set |
| **Inheriting modules** | None |

**WARNING**: This model has NO `name` field. `display_name` is computed as `"Floor Name, Table Number"`. FK resolution via `name_search` will match against `display_name`. Use compound identity keys.

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `table_number` | Integer | Python required=True (line 97) | The table number displayed on floor plan. Default: 0. |
| `shape` | Selection | Python required=True (line 98) | `'square'` or `'round'`. Default: `'square'`. |

Practically required (foreign key):
| Field | Type | Notes |
|---|---|---|
| `floor_id` | Many2one(restaurant.floor) | Not marked required in Python, but a table without a floor is meaningless. |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `table_number` + `floor_id` | `display_name` | Computed: `"Floor Name, Table Number"` |

---

## 4. Constraint Rules

### Python Constraints

- None explicitly.

### SQL Constraints

- None. Table numbers are NOT unique -- different floors can have same table numbers.

### Delete protection

- `_unlink_except_active_pos_session` (line 131): Cannot delete tables when their floor's config has an open session.

---

## 5. create() / write() Side Effects

- No create/write overrides on the table model.
- `are_orders_still_in_draft()` (line 123): Utility check -- raises error if draft orders exist for the table.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `floor_id` | name_search on restaurant.floor | Resolved by floor name |
| `parent_id` | name_search on restaurant.table | For grouped tables. Matches by display_name ("Floor, Number"). |

**Identity keys for deduplication:** `["floor_id", "table_number"]`

A table is uniquely identified by its floor + table number combination.

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/pos_restaurant/data/scenarios/restaurant_floor.xml`

**Key patterns:**
- Main Floor: 12 tables (numbers 1-12), seats 2-6, all square shape.
- Patio: 12 tables (numbers 101-112), seats 2-4, all square shape.
- Colors are CSS rgb strings: `"rgb(53,211,116)"` (green), `"rgb(235,109,109)"` (red), `"rgb(172,109,173)"` (purple), `"rgb(235,191,109)"` (orange).
- Position and size values:
  - Small tables: width=90, height=90
  - Large tables: width=130-165, height=85-120
  - Positions: h=100-800, v=50-565 (pixel coordinates)
- `active` defaults to True.

---

## 8. CSV Generation Recommendations

- CSV headers: `floor_id,table_number,seats,shape,width,height,position_h,position_v,color`
- `floor_id` resolves by name_search on restaurant.floor (match by name).
- `table_number` is an integer -- the number displayed on the floor plan.
- `shape`: `'square'` or `'round'`.
- `seats`: integer, default 1. Set realistic values (2, 4, 6, 8).
- `width` and `height`: pixels for floor plan display. Typical: 90x90 for small, 130x100 for large.
- `position_h` and `position_v`: pixel coordinates. Space them logically (e.g., increment by ~175px).
- `color`: CSS rgb string like `"rgb(53,211,116)"`. Optional.
- `active`: defaults to True, omit unless deactivating.
- Load AFTER `restaurant.floor` records exist.
- Table numbers are NOT globally unique -- only unique per floor by convention.
