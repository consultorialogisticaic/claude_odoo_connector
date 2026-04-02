# UI Report -- pos.preset

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.preset` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_preset.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | `pos_restaurant` (adds `use_guest` boolean field) |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 12) | e.g. "Dine In", "Takeout", "Delivery" |
| `identification` | Selection | Python required=True (line 15) | Values: `'none'`, `'address'`, `'name'`. Default: `'none'` |

Conditionally required:
| Field | Condition | Notes |
|---|---|---|
| `resource_calendar_id` | `use_timing == True` | Form view: `required="use_timing"` |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `use_timing` | Enables `resource_calendar_id`, `slots_per_interval`, `interval_time` | These fields become readonly when `use_timing=False`. |

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_slots` (line 31): For each attendance in `attendance_ids`, `hour_from % 24` must be less than `hour_to % 24` (start time before end time).

### SQL Constraints

- None defined.

### Delete protection

- `_unlink_except_used_preset` (line 113): Cannot delete a preset linked to any pos.config.
- `_unlink_except_master_presets` (pos_restaurant, line 14): Cannot delete the 3 master presets (Dine In, Takeout, Delivery).

---

## 5. create() / write() Side Effects

- No significant create/write overrides on the base pos.preset model.
- Presets are simple configuration records with no auto-creation side effects.

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `pricelist_id` | name_search on product.pricelist | Optional. display_name includes currency. |
| `fiscal_position_id` | name_search on account.fiscal.position | Optional |
| `resource_calendar_id` | name_search on resource.calendar | Required only if use_timing=True |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/pos_restaurant/data/scenarios/restaurant_preset.xml`

**Key patterns:**
- 3 presets created: "Dine In" (color=4, identification=none), "Takeout" (color=3, identification=name, use_timing=True with resource calendar), "Delivery" (color=2, identification=address).
- Takeout preset links to a `resource.calendar` with Tuesday-Saturday lunch+afternoon slots.
- Presets are referenced by the restaurant scenario config via `default_preset_id` and `available_preset_ids`.

---

## 8. CSV Generation Recommendations

- Simple model -- just `name`, `identification`, `color` are sufficient for basic presets.
- If `use_timing=True`, create the `resource.calendar` record FIRST, then reference it in `resource_calendar_id`.
- Set `slots_per_interval` (default 5) and `interval_time` (default 20) when using timing.
- `color` is an integer 0-10 for the color picker widget.
- Load presets BEFORE pos.config so they can be linked via `default_preset_id` and `available_preset_ids`.
- For restaurant setups with pos_restaurant installed, also set `use_guest` (boolean, from pos_restaurant).
