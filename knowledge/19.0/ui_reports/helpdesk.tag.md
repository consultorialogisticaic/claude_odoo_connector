# UI Report: helpdesk.tag

**Odoo Version:** 19.0
**Source:** `enterprise/helpdesk/models/helpdesk_tag.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `helpdesk.tag` |
| `_description` | `Helpdesk Tags` |
| `_rec_name` | `name` (default) |
| `_order` | `name` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. Must be unique (SQL constraint). |
| `color` | Integer | No | random 1-11 | |

## Constraints

- **SQL**: `_name_uniq`: `unique(name)` -- "A tag with the same name already exists."

## create() / write() Overrides

- No custom `create()` or `write()` overrides.
- `name_create()`: Checks for existing tag with case-insensitive match before creating. Returns existing tag if found.

## Demo Data Patterns

From `helpdesk/data/helpdesk_demo.xml`:
```xml
<record id="tag_crm" model="helpdesk.tag">
    <field name="name">CRM</field>
</record>
<record id="tag_website" model="helpdesk.tag">
    <field name="name">Website</field>
</record>
<record id="tag_service" model="helpdesk.tag">
    <field name="name">Service</field>
</record>
<record id="tag_repair" model="helpdesk.tag">
    <field name="name">Repair</field>
</record>
```

## CSV Recommendations

- Very simple model. Just `name` and optionally `color`.
- The unique constraint on `name` means the csv_loader's dedup by `name` will work perfectly.
- `name_create` does case-insensitive dedup, so "repair" and "Repair" are treated as the same tag.

## Recommended Identity Key for csv_loader

```
"helpdesk.tag": ["name"]
```
