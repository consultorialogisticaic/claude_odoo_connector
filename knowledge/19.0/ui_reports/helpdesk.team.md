# UI Report: helpdesk.team

**Odoo Version:** 19.0
**Source:** `enterprise/helpdesk/models/helpdesk_team.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `helpdesk.team` |
| `_description` | `Helpdesk Team` |
| `_inherit` | `mail.alias.mixin`, `mail.thread`, `rating.parent.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, name` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `description` | Html | No | — | About the team. Translatable. |
| `active` | Boolean | No | `True` | |
| `company_id` | Many2one → `res.company` | Yes | current company | |
| `sequence` | Integer | No | 10 | |
| `color` | Integer | No | 0 | |
| `stage_ids` | Many2many → `helpdesk.stage` | No | default 4 stages | Default: New, In Progress, Solved, Cancelled. |
| `auto_assignment` | Boolean | No | `False` | |
| `assign_method` | Selection | Yes | `randomly` | `randomly`, `balanced`, `tags`. |
| `member_ids` | Many2many → `res.users` | Yes | current user | Domain: users with helpdesk group. |
| `privacy_visibility` | Selection | Yes | `portal` | `invited_internal`, `internal`, `portal`. |
| `use_alias` | Boolean | No | `True` | |
| `allow_portal_ticket_closing` | Boolean | No | `False` | |
| `use_website_helpdesk_form` | Boolean | No | computed | Requires `privacy_visibility=portal`. |
| `use_credit_notes` | Boolean | No | `False` | |
| `use_coupons` | Boolean | No | `False` | |
| `use_rating` | Boolean | No | `False` | Customer ratings. |
| `use_sla` | Boolean | No | `True` | SLA policies. |
| `resource_calendar_id` | Many2one → `resource.calendar` | No | company default | Working hours for SLA calculation. |
| `auto_close_ticket` | Boolean | No | `False` | |
| `auto_close_day` | Integer | No | 7 | Days of inactivity before auto-close. |
| `to_stage_id` | Many2one → `helpdesk.stage` | No | computed | Auto-close target stage. |

## Feature Toggles (Boolean fields that trigger module installs)

| Field | Notes |
|---|---|
| `use_website_helpdesk_livechat` | Installs live chat |
| `use_website_helpdesk_forum` | Installs forum |
| `use_website_helpdesk_slides` | Installs eLearning |
| `use_website_helpdesk_knowledge` | Installs Knowledge |
| `use_helpdesk_timesheet` | Installs timesheets |
| `use_helpdesk_sale_timesheet` | Installs time billing |
| `use_fsm` | Installs field service |
| `use_product_returns` | Returns feature |
| `use_product_replacements` | Replacements feature |
| `use_product_repairs` | Repairs feature |

**WARNING**: Setting these to `True` in a CSV will trigger module installations during `write()`. Only enable features you actually want installed.

## Constraints

- `_check_website_privacy`: If `use_website_helpdesk_form=True`, `privacy_visibility` must be `portal`.

## create() / write() Overrides

- **create()**: After `super().create()`, calls `_check_sla_group`, `_check_rating_group`, `_check_auto_assignment_group`, `_check_modules_to_install`. These may install modules.
- **write()**: Handles privacy visibility changes (subscribes/unsubscribes portal users). Checks groups and installs modules when feature toggles change. Updates auto-close cron.
- **unlink()**: Removes stages that only belong to the deleted team.

## Demo Data Patterns

From `helpdesk/data/helpdesk_demo.xml`:
```xml
<record id="helpdesk_team2" model="helpdesk.team">
    <field name="name">IT Support (Auto Assignment by Tags)</field>
    <field name="stage_ids" eval="[(6, 0, [...])]"/>
    <field name="use_rating" eval="True"/>
    <field name="color">8</field>
    <field name="auto_assignment" eval="True"/>
    <field name="assign_method">tags</field>
    <field name="privacy_visibility">invited_internal</field>
</record>
```

A default team `helpdesk_team1` (Customer Care) is created by module data, not demo.

## CSV Recommendations

- A default team ("Customer Care") is created on module install. You may want to update it rather than create a new one.
- `member_ids` is Many2many -- use `name_search` to resolve user names.
- `stage_ids` defaults to 4 standard stages on create. Only set explicitly if you need custom stages.
- Avoid enabling module-install toggles (use_fsm, use_helpdesk_timesheet, etc.) unless those modules are already installed.

## Recommended Identity Key for csv_loader

```
"helpdesk.team": ["name"]
```
