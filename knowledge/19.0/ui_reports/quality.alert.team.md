# UI Report: quality.alert.team (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `quality.alert.team` |
| `_inherit` | `mail.alias.mixin`, `mail.thread` |
| `_description` | "Quality Alert Team" |
| `_order` | `sequence, id` |
| `_rec_name` | `name` (default) |

## Key Fields for CSV Loading

### Required / Critical Fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | -- | Team name (e.g. "Main Quality Team", "Incoming Inspection") |

### Common Optional Fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `company_id` | Many2one (res.company) | -- | Company (optional, unlike most models). If empty, visible to all companies |
| `sequence` | Integer | -- | Display ordering |
| `color` | Integer | `1` | Kanban color index |

### Computed / Read-only Fields (do NOT include in CSV)

| Field | Notes |
|---|---|
| `check_count` | Count of quality checks with `quality_state = 'none'` |
| `alert_count` | Count of open quality alerts (stage not done) |

## Constraints

- No SQL constraints.
- `_get_quality_team()` class method raises `UserError` if no team matches a given company domain. This is called as default for `team_id` on `quality.point` and `quality.check`, so at least one team MUST exist before creating quality points or checks.

## create() / write() Overrides

- No custom `create()` or `write()` overrides on this model.
- Inherits `_alias_get_creation_values()` from `mail.alias.mixin`: sets `alias_model_id` to `quality.alert` and `alias_defaults` with `team_id` and `company_id`. This creates an email alias that auto-creates quality alerts for the team.

## Odoo Demo / Data Patterns

From `quality/data/quality_data.xml`:
```xml
<record id="quality_alert_team0" model="quality.alert.team">
    <field name="name">Main Quality Team</field>
    <field name="alias_id" ref="mail_alias_quality_alert"/>
</record>
```

Key patterns:
- Only `name` is set (plus alias, which is data-seeded separately)
- Single default team created in data (not demo), so it exists even without demo data
- `company_id` not set -- team is global

## CSV Loading Notes

- **Identity key**: `name` (team names should be unique).
- **Simple model**: Only `name` is required. `company_id` and `sequence` are optional.
- **Load order**: Must load BEFORE `quality.point`, `quality.check`, and `quality.alert` (they require a team).
- **Default team**: Odoo seeds "Main Quality Team" via `quality_data.xml`. If you only need the default team, you may not need to load this model at all. Only load if you need additional teams.
- **alias_id**: Do NOT set in CSV. The mail alias is auto-managed by `mail.alias.mixin`.

## Recommended Identity Keys

```json
["name"]
```
