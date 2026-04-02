# UI Report -- restaurant.floor

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `restaurant.floor` |
| **Defining module** | `pos_restaurant` (addons/pos_restaurant/models/pos_restaurant.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | None |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 15) | e.g. "Main Floor", "Patio", "Terrace" |

---

## 3. Onchange Chains

None. Fields are independent.

---

## 4. Constraint Rules

### Python Constraints

- None explicitly, but write() has session-check logic.

### SQL Constraints

- None.

### Delete / Write protection

- `_unlink_except_active_pos_session` (line 32): Cannot delete a floor linked to a POS config with an open session.
- `write()` (line 44): Cannot modify `pos_config_ids` or `active` while linked configs have active sessions.

---

## 5. create() / write() Side Effects

- No significant create() override.
- `sync_from_ui()` (line 63): Alternative creation method used by the POS UI. Creates floor and links it to a config.
- `deactivate_floor()` (line 79): Deactivates the floor and all its tables. Raises error if draft orders exist.

**Note:** When pos.config is created with `module_pos_restaurant=True`, a default floor is auto-created by the pos_restaurant module (see pos.config create() override).

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `pos_config_ids` | name_search on pos.config | Many2many. Domain: `module_pos_restaurant=True`. |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/pos_restaurant/data/scenarios/restaurant_floor.xml`

**Key patterns:**
- 2 floors: "Main Floor" (with background image, 12 tables) and "Patio" (no image, 12 tables).
- Floors are NOT linked to configs in the XML -- linking happens programmatically in the scenario loader via `floor_ids = [(4, floor_id)]`.
- `background_color` is set to 'white'.
- `floor_background_image` uses a base64 file reference.

---

## 8. CSV Generation Recommendations

- Simple: `name`, optional `background_color`, optional `pos_config_ids`.
- `pos_config_ids` links floors to restaurant POS configs -- use comma-separated config names.
- `sequence` controls display order (default 1).
- `active` defaults to True.
- Tables are loaded as separate `restaurant.table` records referencing this floor via `floor_id`.
- Load floors AFTER pos.config (if linking via pos_config_ids), OR load floors first and link from config side.
- `floor_background_image` can be set but is optional (Image field, base64 encoded).
