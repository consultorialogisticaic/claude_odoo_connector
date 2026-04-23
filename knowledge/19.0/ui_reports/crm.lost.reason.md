# UI Report: crm.lost.reason

**Odoo Version:** 19.0
**Source:** `odoo/addons/crm/models/crm_lost_reason.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.lost.reason` |
| `_description` | `Opp. Lost Reason` |
| `_inherit` | — |
| `_rec_name` | `name` (default) |
| `_order` | default (`id`) |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Label `Description`. Translatable. Unique identity in practice. |
| `active` | Boolean | No | `True` | Archive flag. Hidden in the form (`invisible="1"`); toggled via ribbon/archive action. |
| `leads_count` | Integer | — | computed | Read-only. Counts `crm.lead` records whose `lost_reason_id` points here (with `active_test=False`). Do not set in CSV. |

## Constraints

- No `@api.constrains` declared on the model.
- No SQL uniqueness constraint on `name` — duplicates are technically allowed, but the loader should still treat `name` as identity to avoid fan-out.
- `crm.lead.lost_reason_id` is defined with `ondelete='restrict'` (`odoo/addons/crm/models/crm_lead.py:234-236`) — a lost reason cannot be deleted while any lead references it. Archive (`active=False`) instead of delete.

## create() / write() Overrides

- None. The model uses default ORM `create()` / `write()`.
- `_compute_leads_count` is a non-stored compute reading `crm.lead` with `active_test=False`; it does not mutate state.

## Role in the Lost-Opportunity Workflow

`crm.lost.reason` is a pure configuration catalog consumed by the "Mark as Lost" flow on `crm.lead`:

1. On a lead/opportunity, the user clicks **Lost** / **Mark Lost** (`odoo/addons/crm/views/crm_lead_views.xml:16,346,756`). This opens the `crm.lead.lost` transient wizard via `crm.crm_lead_lost_action`.
2. The wizard (`odoo/addons/crm/wizard/crm_lead_lost.py:9-30`, `odoo/addons/crm/wizard/crm_lead_lost_views.xml`) exposes:
   - `lost_reason_id` — Many2one to `crm.lost.reason`, rendered with `widget="selection_badge"`.
   - `lost_feedback` — Html closing note.
3. On `action_lost_reason_apply`, the wizard calls `self.lead_ids.action_set_lost(lost_reason_id=self.lost_reason_id.id)`, which writes `lost_reason_id` onto `crm.lead` and flips `won_status` to `lost`.
4. `crm.lead.lost_reason_id` is defined with `ondelete='restrict'` and `tracking=71` — changes are chattered on the lead, and the lost reason cannot be dropped while leads reference it.
5. Back on `crm.lost.reason`, the form exposes a stat button (`action_lost_leads`) that opens the list of leads pointing at this reason (`odoo/addons/crm/models/crm_lost_reason.py:25-33`).

## Form / List View Notes

From `odoo/addons/crm/views/crm_lost_reason_views.xml`:

- **Form** (`crm_lost_reason_view_form`): single editable field `name` inside `oe_title` (placeholder `"e.g. Too expensive"`); `active` hidden; `web_ribbon` shows `Archived` when `active=False`; stat button `action_lost_leads` surfaces `leads_count`.
- **List** (`crm_lost_reason_view_tree`): `editable="bottom"`, single column `name` — inline creation is the normal UI path.
- **Search** (`crm_lost_reason_view_search`): filters `Active` and `Archived` on `active`.
- **Action** (`crm_lost_reason_action`): menu target for Configuration → Lead & Opportunities → Lost Reasons.

## Demo / Seed Data Patterns

From `odoo/addons/crm/data/crm_lost_reason_data.xml` (loaded with `noupdate="1"`):

```xml
<record id="lost_reason_1" model="crm.lost.reason">
    <field name="name">Too expensive</field>
</record>
<record id="lost_reason_2" model="crm.lost.reason">
    <field name="name">We don't have people/skills</field>
</record>
<record id="lost_reason_3" model="crm.lost.reason">
    <field name="name">Not enough stock</field>
</record>
```

These three seed reasons are shipped by the `crm` module itself (module data, not demo). Because `noupdate="1"`, later module upgrades will not overwrite them if an admin renamed them.

## CSV Recommendations

- Populate only `name` (and optionally `active`). Skip `leads_count` — it is computed.
- Before creating, check whether the three seed reasons (`Too expensive`, `We don't have people/skills`, `Not enough stock`) already satisfy the need; reuse rather than duplicate.
- Do not attempt to delete existing lost reasons via CSV — `ondelete='restrict'` on `crm.lead.lost_reason_id` will block removal if any lead references them. Set `active=False` to retire a reason instead.
- `name` is translatable; load the source-language value and rely on Odoo translation machinery for other locales.
- The wizard is the only standard UI entry point that writes `lost_reason_id` onto leads — loading lost reasons via CSV is safe and side-effect-free on leads.

## Recommended Identity Key for csv_loader

```
"crm.lost.reason": ["name"]
```
