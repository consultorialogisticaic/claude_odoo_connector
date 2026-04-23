# UI Report: crm.recurring.plan

**Odoo Version:** 19.0
**Source:** `odoo/addons/crm/models/crm_recurring_plan.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.recurring.plan` |
| `_description` | `CRM Recurring revenue plans` |
| `_inherit` | — |
| `_rec_name` | `name` (default) |
| `_order` | `sequence` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Plan Name. Translatable. |
| `number_of_months` | Integer | Yes | — | # Months. Must be `>= 0` (SQL check). |
| `active` | Boolean | No | `True` | Archive flag. |
| `sequence` | Integer | No | 10 | Drives list ordering; editable via `handle` widget in the list view. |

## Constraints

- `_check_number_of_months` (SQL `CHECK(number_of_months >= 0)`): `number_of_months` cannot be negative. Raised on insert/update at the database level.

## create() / write() Overrides

None. The model has no Python `create`/`write`/`unlink` overrides and no `@api.constrains` methods — only the SQL check above.

## View Layout

From `odoo/addons/crm/views/crm_recurring_plan_views.xml`:

- No form view. The only edit surface is an **editable list view** (`editable="bottom"`) with columns: `sequence` (handle), `name`, `number_of_months`.
- Search view exposes `name` and an `Archived` filter on `active`.
- Action `crm_recurring_plan_action` is `view_mode="list"` only.

Because there is no form view, the UI creation flow is: open the Recurring Plans list, click the bottom row, type the plan name and number of months, save. There are no onchanges, no buttons, no state transitions.

## Relationship to `crm.lead`

Defined in `odoo/addons/crm/models/crm_lead.py`:

- `crm.lead.recurring_plan` — `Many2one('crm.recurring.plan')` (line 144).
- `crm.lead.recurring_revenue` — `Monetary` manual input (line 143).
- `crm.lead.recurring_revenue_monthly` — computed, stored (lines 145–146):

  ```python
  @api.depends('recurring_revenue', 'recurring_plan.number_of_months')
  def _compute_recurring_revenue_monthly(self):
      for lead in self:
          lead.recurring_revenue_monthly = (lead.recurring_revenue or 0.0) / (lead.recurring_plan.number_of_months or 1)
  ```
- `crm.lead.recurring_revenue_monthly_prorated` — MRR × probability / 100 (lines 147–148, 578–581).
- `crm.lead.recurring_revenue_prorated` — total × probability / 100 (lines 149–150, 583–586).

The MRR computation divides by `number_of_months`, falling back to `1` when the plan is unset or its months are zero. A plan with `number_of_months = 0` therefore behaves identically to "no plan" for MRR purposes — it does not raise — but it will still pass the SQL check.

Recurring revenue fields are only meaningful when the group `crm.group_use_recurring_revenues` is enabled; `crm.lead.copy_data` zeroes `recurring_revenue` and clears `recurring_plan` when the user lacks that group (`crm_lead.py` lines 1027–1029).

## Demo / Seed Data Patterns

From `odoo/addons/crm/data/crm_recurring_plan_data.xml` (loaded with `noupdate="1"` — these records ship as module data, not demo, and are not overwritten on upgrade):

```xml
<record id="crm_recurring_plan_monthly" model="crm.recurring.plan">
    <field name="name">Monthly</field>
    <field name="number_of_months">1</field>
</record>
<record id="crm_recurring_plan_yearly" model="crm.recurring.plan">
    <field name="name">Yearly</field>
    <field name="number_of_months">12</field>
</record>
<record id="crm_recurring_plan_over_3_years" model="crm.recurring.plan">
    <field name="name">Over 3 years</field>
    <field name="number_of_months">36</field>
</record>
<record id="crm_recurring_plan_over_5_years" model="crm.recurring.plan">
    <field name="name">Over 5 years </field>
    <field name="number_of_months">60</field>
</record>
```

Note: the `"Over 5 years "` name carries a trailing space in the canonical data — match it exactly if your CSV targets the existing record by name.

`sequence` and `active` are not set in demo data; they rely on the model defaults (`10`, `True`).

No demo lead in `crm/data/crm_lead_demo.xml` references a recurring plan.

## CSV Recommendations

- Four plans (Monthly / Yearly / Over 3 years / Over 5 years) are created on install of `crm`. Prefer **updating by name** over creating duplicates if targeting a fresh install — otherwise `name_search` on those strings will hit the seeded records.
- Always set `number_of_months` explicitly — it is required and has no default.
- Use strictly positive `number_of_months` values for anything feeding MRR; `0` passes the SQL check but is silently treated as `1` by `_compute_recurring_revenue_monthly`.
- Set `sequence` only if ordering matters; let it default otherwise.
- There is no `company_id` field — plans are global across companies.
- `name` is translatable; CSV provides the source-language value.

## Recommended Identity Key for csv_loader

```
"crm.recurring.plan": ["name"]
```
