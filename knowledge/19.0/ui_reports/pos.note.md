# UI Report -- pos.note

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.note` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_note.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | None |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 12) | e.g. "Wait", "To Serve", "No Dressing" |

---

## 3. Onchange Chains

None. All fields are independent.

---

## 4. Constraint Rules

### Python Constraints

- None.

### SQL Constraints (Odoo 19 style `models.Constraint`)

- `_name_unique` (line 16): `unique (name)` -- note names must be unique across all records.

---

## 5. create() / write() Side Effects

- No overrides. Pure simple model.

---

## 6. FK Resolution Strategy

No foreign key fields. Self-contained model.

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- `addons/point_of_sale/data/pos_note_data.xml` (non-demo data, always loaded)

**Key patterns:**
- 4 notes created: "Wait" (seq 1), "To Serve" (seq 2), "Emergency" (seq 3), "No Dressing" (seq 4).
- Notes are linked to pos.config via `note_ids` Many2many field.
- These are data records (not demo), so they exist in all installations.

---

## 8. CSV Generation Recommendations

- Extremely simple: just `name`, `sequence`, optional `color`.
- `name` must be unique (SQL constraint).
- `sequence` controls display order (default 1).
- `color` is integer for color picker widget.
- Notes are linked to configs via `pos.config.note_ids` -- set that on the config CSV, not here.
- The 4 default notes ("Wait", "To Serve", "Emergency", "No Dressing") already exist after module install. Only create additional custom notes.
