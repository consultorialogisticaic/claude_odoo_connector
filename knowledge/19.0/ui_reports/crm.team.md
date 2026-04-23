# UI Report: crm.team

**Odoo Version:** 19.0
**Source:** `odoo/addons/sales_team/models/crm_team.py` (base), `odoo/addons/crm/models/crm_team.py` (CRM extension)

`crm.team` is a SHARED model. The same record is used as a Sales Team by Sales/Invoicing (`use_quotations` does not exist in 19.0 — quotation ownership is expressed via `team_id` on `sale.order`) and as a CRM Pipeline Team by CRM (`use_leads`, `use_opportunities`). A single team can hold leads, opportunities and sale orders at the same time. Feature toggles are added by the `crm` module when installed.

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.team` |
| `_description` | `Sales Team` |
| `_inherit` | `mail.thread` (base), `mail.alias.mixin` (added by `crm`) |
| `_rec_name` | `name` (default) |
| `_order` | `sequence ASC, create_date DESC, id DESC` |
| `_check_company_auto` | `True` |

Combined from two sources:
- `odoo/addons/sales_team/models/crm_team.py` — base model, `_inherit = ['mail.thread']`.
- `odoo/addons/crm/models/crm_team.py` — extends with `_inherit = ['mail.alias.mixin', 'crm.team']`, adds lead/opportunity toggles, alias, assignment.

Further extensions (not adding toggles, just fields):
- `odoo/addons/sale/models/crm_team.py` — adds `invoiced`, `invoiced_target`, `sale_order_count`.
- `odoo/addons/sale_crm/models/crm_team.py` — dashboard button override only.
- `odoo/addons/website_sale/models/crm_team.py` — adds `website_ids`, abandoned-cart counts.
- `odoo/addons/pos_sale/models/crm_team.py` — adds `pos_config_ids`.
- `odoo/addons/survey_crm/models/crm_team.py` — adds `origin_survey_ids`.
- `enterprise/sale_commission/model/crm_team.py` — adds `commission_plan_ids`.

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | `Sales Team`. Translatable. |
| `sequence` | Integer | No | 10 | |
| `active` | Boolean | No | `True` | |
| `company_id` | Many2one → `res.company` | No | — | Leave empty for "Visible to all". `_check_company_auto = True`: members must belong to this company. |
| `currency_id` | Many2one → `res.currency` | No | computed | `related='company_id.currency_id'`, readonly. |
| `user_id` | Many2one → `res.users` | No | — | Team Leader. Domain: `share != True`. `check_company=True`. |
| `member_ids` | Many2many → `res.users` | No | — | Salespersons. Computed/inverse over `crm_team_member_ids`. Domain: non-share users whose companies include `member_company_ids`. Inverse creates/archives `crm.team.member` rows. |
| `crm_team_member_ids` | One2many → `crm.team.member` | No | — | Explicit membership rows (with capacity/domain for assignment). |
| `color` | Integer | No | random 1..11 | Kanban color index. |
| `favorite_user_ids` | Many2many → `res.users` | No | current user | Dashboard favorites. |
| `is_favorite` | Boolean | No | computed | UX toggle over `favorite_user_ids`. |
| `is_membership_multi` | Boolean | No | computed | Reads `ir.config_parameter` `sales_team.membership_multi`. |
| `alias_id` | Many2one → `mail.alias` | No | auto-created | From `mail.alias.mixin` (when `crm` installed). Incoming emails create leads/opps. |
| `alias_name` | Char | No | — | Local part of the alias. Cleared by onchange when both `use_leads` and `use_opportunities` are False. |
| `alias_domain_id` | Many2one → `mail.alias.domain` | No | — | From mixin. |
| `alias_contact` | Selection | No | — | From mixin. |
| `use_leads` | Boolean | No | `False` | Added by `crm`. Enables lead qualification. |
| `use_opportunities` | Boolean | No | `True` | Added by `crm`. Enables pipeline. |
| `assignment_optout` | Boolean | No | `False` | Skip auto assignment cron. |
| `assignment_domain` | Char (domain) | No | — | Added by `crm`. `@api.constrains` validates domain parses and is a valid `crm.lead` domain. |
| `assignment_max` | Integer | No | computed | Sum of members' `assignment_max`. |
| `assignment_enabled` | Boolean | No | computed | Reads CRM rule-based assignment config. |
| `assignment_auto_enabled` | Boolean | No | computed | Reads `crm.ir_cron_crm_lead_assign` active flag. |
| `lead_properties_definition` | PropertiesDefinition | No | — | Schema for lead properties scoped to the team. |
| `invoiced` | Float | No | computed | From `sale`. Current-month posted invoice total. |
| `invoiced_target` | Float | No | — | From `sale`. Monthly target. |
| `sale_order_count` | Integer | No | computed | From `sale`. Non-cancelled SOs. |
| `website_ids` | One2many → `website` | No | — | From `website_sale`. |
| `pos_config_ids` | One2many → `pos.config` | No | — | From `pos_sale`. |
| `commission_plan_ids` | Many2many → `sale.commission.plan` | No | — | From enterprise `sale_commission`. |

## Feature Toggles

| Field | Source | Effect |
|---|---|---|
| `use_leads` | `crm` | Enables the lead qualification step (two-stage pipeline). Requires group `crm.group_use_lead` to appear in the form. |
| `use_opportunities` | `crm` | Enables the opportunity/pipeline view. Default `True` once `crm` is installed. |
| `assignment_optout` | `crm` | Excludes the team from the automatic lead assignment cron. |

Note: unlike `helpdesk.team`, none of these toggles trigger module installs on `write()`. They only enable features exposed by already-installed modules. There is no `use_quotations` field in 19.0 — sale orders and quotations are linked via `team_id` on `sale.order` and do not need a toggle on the team.

## Constraints

- `_constrains_company_members` (`sales_team/models/crm_team.py`, `@api.constrains('company_id')`): when `company_id` is set, every user in `crm_team_member_ids` must have that company in `company_ids`. Raises `UserError` listing offending users. Fires on create and write.
- `_constrains_assignment_domain` (`crm/models/crm_team.py`, `@api.constrains('assignment_domain')`): `assignment_domain` must be a valid Python-literal domain that `crm.lead.search()` accepts. Raises `ValidationError`.
- `@api.onchange('use_leads', 'use_opportunities')`: if both are False, clears `alias_name` in the UI. CSV loader does not fire onchanges — set `alias_name` explicitly (or leave empty) when both toggles are False.
- `@api.ondelete` `_unlink_except_default` (base): cannot delete `sales_team.salesteam_website_sales` or `sales_team.pos_sales_team`.
- `@api.ondelete` `_unlink_except_used_for_sales` (from `sale`): cannot delete a team with 5 or more active `sale.order`s; archive instead.

## create() / write() Overrides

- **create()** (base): `super().create()` is called with `mail_create_nosubscribe=True`. After creation, any team that has `member_ids` has those members added to `favorite_user_ids` via `_add_members_to_favorites`.
- **write()** (base): after `super().write()`, if `company_id` changed, re-runs `crm.team.member._constrains_membership`. If `member_ids` changed, re-syncs favorites.
- **write()** (crm): after `super().write()`, if `use_leads` or `use_opportunities` is in vals, recomputes alias values via `_alias_get_creation_values` and writes `alias_name` + `alias_defaults` back. Setting both toggles to False clears `alias_name`.
- **unlink()** (crm): rolls up `crm.lead.scoring.frequency` records from deleted teams into the "no team" (global) frequencies instead of losing them.
- **_inverse_member_ids**: assigning `member_ids` creates `crm.team.member` rows for new users and toggles `active` on existing memberships to match the list. CSV writes to `member_ids` therefore materialise as membership rows; they do not delete old rows, only archive them.
- **_alias_get_creation_values** (crm): fills `alias_model_id` with `crm.lead`, sets `alias_defaults['type']` to `'lead'` (if user has `crm.group_use_lead` and `use_leads`) or `'opportunity'`, and `alias_defaults['team_id']` to the team's id. Called from `mail.alias.mixin` during alias creation and on toggle changes.

## Demo Data Patterns

From `odoo/addons/sales_team/data/crm_team_data.xml` (base data, `noupdate="1"`):

```xml
<record id="team_sales_department" model="crm.team">
    <field name="name">Sales</field>
    <field name="sequence">0</field>
    <field name="company_id" eval="False"/>
    <field name="user_id" ref="base.user_admin"/>
</record>

<record id="salesteam_website_sales" model="crm.team">
    <field name="name">Website</field>
    <field name="company_id" eval="False"/>
    <field name="active" eval="False"/>
</record>

<record id="pos_sales_team" model="crm.team">
    <field name="name">Point of Sale</field>
    <field name="company_id" eval="False"/>
    <field name="active" eval="False"/>
</record>
```

From `odoo/addons/sales_team/data/crm_team_demo.xml`:

```xml
<record model="crm.team" id="crm_team_1">
    <field name="name">Pre-Sales</field>
    <field name="company_id" eval="False"/>
</record>

<record id="crm_team_member_demo_team_1" model="crm.team.member">
    <field name="user_id" ref="base.user_demo"/>
    <field name="crm_team_id" ref="sales_team.crm_team_1"/>
</record>
```

From `odoo/addons/crm/data/crm_team_data.xml` (post-`crm`-install overlay, `noupdate="1"`):

```xml
<record id="sales_team.team_sales_department" model="crm.team" forcecreate="False">
    <field name="alias_name">info</field>
</record>

<record id="sales_team.salesteam_website_sales" model="crm.team" forcecreate="False">
    <field name="use_opportunities" eval="False"/>
</record>

<record id="sales_team.pos_sales_team" model="crm.team" forcecreate="False">
    <field name="use_opportunities" eval="False"/>
</record>
```

From `odoo/addons/crm/data/crm_team_demo.xml`:

```xml
<record id="sales_team.team_sales_department" model="crm.team" forcecreate="False">
    <field name="assignment_domain">[['probability', '>=', 20]]</field>
</record>

<record id="sales_team.crm_team_1" model="crm.team">
    <field name="use_leads">True</field>
    <field name="assignment_domain">[['phone', '!=', False]]</field>
</record>
```

Observations:
- `company_id` is explicitly `False` on every default team — meaning "visible to all companies".
- Membership is written through `crm.team.member` records, not through `member_ids` on the team. That is the canonical pattern.
- The default `Sales` team (`sales_team.team_sales_department`) is created by module data; CSV data should update it, not recreate it.

## CSV Recommendations

- Prefer updating `sales_team.team_sales_department` over creating a new "Sales" team on fresh databases.
- When `company_id` is set, every user referenced in `member_ids` / `crm_team_member_ids` must have that company in `company_ids` — otherwise `_constrains_company_members` raises. For cross-company teams, leave `company_id` empty.
- For membership, prefer creating `crm.team.member` rows directly (with `crm_team_id` + `user_id`) rather than writing `member_ids` on the team. This matches demo data, supports `assignment_max` / `assignment_domain` per member, and is the storage that `member_ids` inverses into anyway.
- If you do write `member_ids` via CSV (Many2many), use `name_search`-resolvable user names (logins or display names) — the inverse will create memberships and archive those not in the list.
- `user_id` (team leader) must be a non-share user and, if `company_id` is set, in that company.
- `alias_name` is only meaningful when `use_leads` or `use_opportunities` is True. If both are False, leave `alias_name` empty — the onchange that clears it does NOT run on CSV import.
- `assignment_domain` must be a Python-literal list (e.g. `[['probability', '>=', 20]]`). Invalid domains fail `_constrains_assignment_domain`.
- Do not set `color` unless needed — the default (`_get_default_color`) randomises 1..11.
- Avoid deleting `sales_team.salesteam_website_sales` and `sales_team.pos_sales_team` — `_unlink_except_default` blocks it. Archive with `active=False` instead.
- `is_favorite` is a computed UX flag per-user; do not attempt to set it in CSV.

## Recommended Identity Key for csv_loader

```
"crm.team": ["name"]
```

`name` is `required=True` and teams are typically identified by their display name in both admin UI and XML IDs. No `default_code`, no compound identity. If multi-company CSVs produce collisions (same team name in two companies), escalate to `["name", "company_id"]`.
