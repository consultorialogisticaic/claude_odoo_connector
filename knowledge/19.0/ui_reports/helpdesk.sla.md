# UI Report: helpdesk.sla

**Odoo Version:** 19.0
**Source:** `enterprise/helpdesk/models/helpdesk_sla.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `helpdesk.sla` |
| `_description` | `Helpdesk SLA Policies` |
| `_rec_name` | `name` (default) |
| `_order` | `name` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `description` | Html | No | — | Translatable. |
| `active` | Boolean | No | `True` | |
| `team_id` | Many2one → `helpdesk.team` | Yes | — | FK lookup by team name. |
| `tag_ids` | Many2many → `helpdesk.tag` | No | — | Filter: SLA applies only to tickets with these tags. |
| `stage_id` | Many2one → `helpdesk.stage` | No | default: first folded stage or last stage of team | Target stage the ticket must reach. |
| `exclude_stage_ids` | Many2many → `helpdesk.stage` | No | — | Stages excluded from SLA time calculation. |
| `priority` | Selection | Yes | `0` | `0` (Low), `1` (Medium), `2` (High), `3` (Urgent). From `TICKET_PRIORITY`. |
| `partner_ids` | Many2many → `res.partner` | No | — | SLA applies only to these customers. |
| `company_id` | Many2one → `res.company` | — | related to `team_id.company_id` | Readonly, stored. |
| `time` | Float | Yes | 0 | Maximum working hours to reach target stage. |

## Constraints

- No SQL constraints.
- No Python constraints beyond standard field validation.

## create() / write() Overrides

- No custom `create()` or `write()` overrides.
- `default_get`: Auto-sets `team_id` and `stage_id` based on context.

## Demo Data Patterns

No SLA demo records found in the helpdesk demo file. SLAs are typically created manually per team.

## CSV Recommendations

- Compound identity: An SLA is uniquely identified by `team_id` + `name` (though technically the same name could exist for different teams).
- `stage_id` should reference a stage that belongs to the team's `stage_ids`. Use the stage name for FK resolution.
- `time` is in working hours (float), not calendar hours. E.g., `8.0` = 8 working hours.
- `priority` maps to: `0`=All, `1`=Low, `2`=High, `3`=Urgent (matches ticket priority levels).

## Recommended Identity Key for csv_loader

```
"helpdesk.sla": ["team_id", "name"]
```
