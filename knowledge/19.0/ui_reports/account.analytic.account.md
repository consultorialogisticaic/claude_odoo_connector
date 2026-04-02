# UI Report: account.analytic.account

**Odoo Version:** 19.0
**Source:** `odoo/addons/analytic/models/analytic_account.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `account.analytic.account` |
| `_description` | `Analytic Account` |
| `_inherit` | `mail.thread` |
| `_rec_name` | `name` (default) |
| `_rec_names_search` | `['name', 'code']` |
| `_order` | `plan_id, name asc` |
| `_check_company_auto` | `True` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable, indexed (trigram). |
| `code` | Char | No | — | Reference. Indexed. Included in `_rec_names_search`. |
| `active` | Boolean | No | `True` | |
| `plan_id` | Many2one → `account.analytic.plan` | Yes | — | FK lookup by plan name. |
| `company_id` | Many2one → `res.company` | No | current company | Set to `False` for multi-company visibility. |
| `partner_id` | Many2one → `res.partner` | No | — | Customer. |

## Computed / Display Fields (skip in CSV)

- `root_plan_id`: computed from `plan_id.root_id`, stored.
- `color`: related to `plan_id.color`.
- `balance`, `debit`, `credit`: computed from analytic lines.
- `currency_id`: related to `company_id.currency_id`.
- `complete_name` / `display_name`: computed as `[code] name - partner`.

## Constraints

- `_check_company_consistency`: Cannot change company if analytic lines exist in a different company.

## create() / write() Overrides

- **write()**: When `plan_id` changes, calls `_update_accounts_in_analytic_lines` to move analytic line references from old plan column to new plan column.
- No custom `create()` override on this model.

## Demo Data Patterns

From `analytic/data/analytic_account_demo.xml`:
```xml
<record id="analytic_our_super_product" model="account.analytic.account">
    <field name="name">Our Super Product</field>
    <field name="partner_id" ref="base.res_partner_2"/>
    <field name="plan_id" ref="analytic.analytic_plan_projects"/>
    <field name="company_id" eval="False"/>
</record>
```

Pattern: name + plan_id + optional partner_id. `company_id` set to False for multi-company.

## CSV Recommendations

- Compound identity: `plan_id` + `name` (same name can exist under different plans).
- Use `company_id` = empty/False for shared accounts.
- `code` is optional but useful for fast lookups.

## Recommended Identity Key for csv_loader

```
"account.analytic.account": ["plan_id", "name"]
```
