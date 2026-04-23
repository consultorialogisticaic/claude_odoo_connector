# UI Report: crm.lead

**Odoo Version:** 19.0
**Source:** `odoo/addons/crm/models/crm_lead.py`

One model stores both **leads** and **opportunities** — the `type` selection field distinguishes them (`'lead'` vs `'opportunity'`). The form view toggles whole field groups on `type`, and a handful of fields (`stage_id`, `probability`, `expected_revenue`) behave very differently between the two.

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.lead` |
| `_description` | `Lead` |
| `_inherit` | `mail.thread.cc`, `mail.thread.blacklist`, `mail.thread.phone`, `mail.activity.mixin`, `utm.mixin`, `format.address.mixin`, `mail.tracking.duration.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `priority desc, id desc` |
| `_primary_email` | `email_from` |
| `_check_company_auto` | `True` |
| `_track_duration_field` | `stage_id` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | computed from `partner_id` | Computed: `"<partner.name>'s opportunity"` if empty and `partner_id` set. Still required — always pass a value to be safe. |
| `type` | Selection | Yes | `'lead'` if user has `crm.group_use_lead`, else `'opportunity'` | Values: `lead`, `opportunity`. Drives form-view visibility and most downstream behavior. |
| `user_id` | Many2one → `res.users` | No | current user | Domain: `share=False`. Setting/changing triggers `date_open = now`. |
| `team_id` | Many2one → `crm.team` | No | computed from `user_id` + `type` | Computed via `crm.team._get_default_team_id` with domain `use_leads=True` (for leads) or `use_opportunities=True` (for opps). `precompute=True, store=True`. |
| `company_id` | Many2one → `res.company` | No | computed | Derived from `team_id.company_id` > `user_id.company_id` > `partner_id.company_id`. Validated against `user_id.company_ids`. |
| `stage_id` | Many2one → `crm.stage` | No | computed (first non-folded stage for team) | Domain: `['|', ('team_ids', '=', False), ('team_ids', 'in', team_id)]`. `ondelete='restrict'`. Resolution order: `sequence, id` via `_stage_find()` (crm_lead.py:1071). |
| `priority` | Selection | No | `'0'` | From `crm_stage.AVAILABLE_PRIORITIES`: `'0'`, `'1'`, `'2'`, `'3'` (Low to Very High). |
| `partner_id` | Many2one → `res.partner` | No | — | Contact/customer. Setting it recomputes `contact_name`, `partner_name`, `email_from`, `phone`, `function`, `website`, `lang_id`, and all address fields (via `_compute_partner_address_values`). |
| `partner_name` | Char | No | computed from `partner_id` | "Company Name" — the would-be partner company when the lead converts. Free-text if no `partner_id`. |
| `contact_name` | Char | No | computed from `partner_id` | Contact person name when no `partner_id` exists yet. |
| `email_from` | Char | No | computed from `partner_id.email` | Inverse writes back to partner when `_get_partner_email_update()` is truthy. Normalized into `email_normalized` via `mail.thread.blacklist`. |
| `phone` | Char | No | computed from `partner_id.phone` | Sanitized into `phone_sanitized` via `mail.thread.phone`. |
| `function` | Char | No | computed from `partner_id.function` | Job position. |
| `website` | Char | No | computed from `partner_id.website` | Run through `res.partner._clean_website()` in both `create()` and `write()`. |
| `street` / `street2` / `city` / `zip` | Char | No | computed from `partner_id` | All address fields sync as a block — see `_compute_partner_address_values`. |
| `state_id` | Many2one → `res.country.state` | No | computed | Domain: `[('country_id', '=?', country_id)]`. |
| `country_id` | Many2one → `res.country` | No | computed | |
| `lang_id` | Many2one → `res.lang` | No | computed from `partner_id.lang` | Resolved via `res.lang._get_data(code=...)`. |
| `description` | Html | No | — | Internal notes. |
| `active` | Boolean | No | `True` | Lost leads are archived (`active=False` + `probability=0`). |
| `tag_ids` | Many2many → `crm.tag` | No | — | Relation table `crm_tag_rel`. Use `(6, 0, [...])` or comma-separated names with `many2many_tags` widget. |
| `expected_revenue` | Monetary | No | `0.0` | Currency: `company_currency` (computed from `company_id`). Opportunity-only in UI but stored for leads too. |
| `recurring_revenue` | Monetary | No | `0.0` | Requires group `crm.group_use_recurring_revenues` in UI. |
| `recurring_plan` | Many2one → `crm.recurring.plan` | Conditional | — | `required="recurring_revenue != 0"` in view (not Python). |
| `probability` | Float | No | computed (Naive Bayes PLS) | Range-constrained `0..100` (SQL check `_check_probability`). Overridable — `is_automated_probability` tracks whether user edited it. |
| `date_deadline` | Date | No | — | Expected closing date (opportunity-only in UI). |
| `date_open` | Datetime | No | auto-set | Set to `now` on create/write when `user_id` is (re)assigned. Reset to `False` if `user_id` unset. |
| `date_closed` | Datetime | No | auto-set | Set to `now` when `probability >= 100` or `active=False`; reset when `probability > 0` and stage not won. |
| `date_last_stage_update` | Datetime | No | auto-set on stage change | `store=True, readonly=True`. |
| `date_conversion` | Datetime | No | — | Set by `convert_opportunity()` flow, not the form. |
| `lost_reason_id` | Many2one → `crm.lost.reason` | No | — | Visible only when `won_status == 'lost'`. |
| `referred` | Char | No | — | "Referred By". |
| `campaign_id` / `medium_id` / `source_id` | Many2one | No | — | UTM mixin. `ondelete='set null'`. |
| `lead_properties` | Properties | No | — | Definition on `team_id.lead_properties_definition`. |
| `color` | Integer | No | `0` | Kanban color. |

### Fields That Look Settable But Are Computed

These are `readonly=True` or have no inverse — **do not set in CSV**, they will either be ignored or recomputed immediately:

| Field | Why |
|---|---|
| `won_status` | Computed from `active`, `probability`, `stage_id.is_won`. |
| `automated_probability` | Computed by PLS Naive Bayes. |
| `prorated_revenue`, `recurring_revenue_monthly`, `recurring_revenue_monthly_prorated`, `recurring_revenue_prorated` | All stored computes. |
| `day_open`, `day_close`, `date_open`, `date_last_stage_update` | Derived from create/stage/user events. |
| `email_normalized`, `phone_sanitized`, `email_domain_criterion` | Derived from `email_from` / `phone`. |
| `email_state`, `phone_state` | Computed quality flags. |
| `commercial_partner_id` | `store=False` UX helper only. |
| `duplicate_lead_ids`, `duplicate_lead_count` | Computed duplicate detection. |

## Notable Extensions (fields added by other modules)

| Module | Fields added | Notes |
|---|---|---|
| `sale_crm` | `order_ids` (One2many), `sale_amount_total`, `quotation_count`, `sale_order_count` | All computed/O2m — do not set from CSV. |
| `website_crm_partner_assign` | `partner_assigned_id`, `partner_latitude`, `partner_longitude`, `partner_declined_ids`, `date_partner_assign` | Partner-network assignment. |
| `crm_iap_mine` | `lead_mining_request_id` | Back-reference to mining request. |
| `event_crm` | `event_id`, `event_lead_rule_id`, `registration_ids` | Back-references from event module. |
| `website_crm` | `visitor_ids`, `visitor_page_count` | Web-visitor tracking. |
| `crm_enterprise` | `days_to_convert`, `days_exceeding_closing` | Stored computes only. |
| `partner_commission` | Commission-related fields | See `enterprise/partner_commission/models/crm_lead.py`. |

None of these extension fields are required for base CSV creation of a `crm.lead`.

## Constraints

- `_check_probability` (SQL check): `probability >= 0 AND probability <= 100` (`crm_lead.py:254`).
- `_check_won_validity` (`@api.constrains('probability', 'stage_id')`, `crm_lead.py:262`): a lead in a `stage.is_won == True` stage must have `probability == 100`. Raises `ValidationError("A lead in a Won stage cannot be lost. Move it to another stage first.")`.
- Additional runtime check in `_handle_won_lost` (called from both `create()` and `write()`): a lead cannot be simultaneously won and lost — raises `ValidationError("The lead %s cannot be won and lost at the same time.", lead)` (`crm_lead.py:1004`).

## create() / write() Overrides

Defined at `crm_lead.py:796` (`create`) and `crm_lead.py:829` (`write`).

**`create()` side effects:**
- `vals['website']` is normalized via `res.partner._clean_website()`.
- If the created lead lands directly in a `stage_id.is_won` stage, `date_closed` is force-set to `fields.Datetime.now()`.
- If `partner_id` default is `None` but `commercial_partner_id` is provided and the lead has matching `phone`/`email_from`, `partner_id` is auto-linked to the commercial partner; otherwise `partner_name` is back-filled from `commercial_partner.name`.
- `_handle_won_lost()` is invoked to update the PLS (Predictive Lead Scoring) frequency tables when a lead is created directly in a won/lost state.

**`write()` side effects:**
- `vals['website']` cleaned (same as create).
- On `stage_id` change: sets `date_last_stage_update = now`. If the new stage has `is_won`, force-sets `{'active': True, 'probability': 100, 'automated_probability': 100}`.
- On `user_id` change: `date_open = now` (or `False` if user cleared).
- `probability >= 100` or `active=False` → `date_closed = now`. `probability > 0` (and < 100) → `date_closed = False`.
- `_handle_won_lost()` recomputes PLS frequency tables whenever `active`, `stage_id`, or `probability` change.
- Won-stage-to-won-stage transitions preserve the original `date_closed` (special-cased via two `super().write()` calls).

**`copy_data()`** (`crm_lead.py:1023`): propagates `type` and `team_id`, sets `date_open = now` for opportunities with active users, clears `user_id` if source user is archived, and zeroes `recurring_revenue` / `recurring_plan` for users without the recurring-revenues group.

## Demo Data Patterns

From `odoo/addons/crm/data/crm_lead_demo.xml` (all wrapped in `<data noupdate="1">`).

**Lead example** (minimal — no revenue/probability, `type='lead'`):
```xml
<record id="crm_case_1" model="crm.lead">
    <field name="type">lead</field>
    <field name="name">Club Office Furnitures</field>
    <field name="contact_name">Jacques Dunagan</field>
    <field name="partner_name">Le Club SARL</field>
    <field name="email_from">jdunagan@leclub.example.com</field>
    <field name="function">Training Manager</field>
    <field name="country_id" ref="base.fr"/>
    <field name="city">Paris</field>
    <field name="zip">93190</field>
    <field name="street">Rue Léon Dierx 73</field>
    <field name="phone">+33 1 25 54 45 69</field>
    <field name="tag_ids" eval="[(6, 0, [ref('sales_team.categ_oppor6')])]"/>
    <field name="priority">1</field>
    <field name="team_id" ref="sales_team.team_sales_department"/>
    <field name="user_id" ref="base.user_admin"/>
    <field name="stage_id" ref="stage_lead1"/>
    <field name="campaign_id" ref="utm.utm_campaign_email_campaign_services"/>
    <field name="medium_id" ref="utm.utm_medium_email"/>
    <field name="source_id" ref="utm.utm_source_mailing"/>
</record>
```

**Opportunity example** (`type='opportunity'`, explicit revenue + probability + deadline):
```xml
<record id="crm_case_13" model="crm.lead">
    <field name="type">opportunity</field>
    <field name="name">Quote for 12 Tables</field>
    <field name="expected_revenue">40000</field>
    <field name="probability">10.0</field>
    <field name="contact_name">Will McEncroe</field>
    <field name="partner_name">Rediff Mail</field>
    <field name="email_from">willmac@rediffmail.example.com</field>
    <field name="date_deadline" eval="(DateTime.today() + relativedelta(months=1)).strftime('%Y-%m-%d %H:%M')"/>
    <field name="team_id" ref="sales_team.team_sales_department"/>
    <field name="user_id" ref="base.user_admin"/>
    <field name="stage_id" ref="crm.stage_lead1"/>
</record>
```

Patterns worth copying:
- Leads omit `expected_revenue` / `probability` / `date_deadline`.
- Opportunities set all three explicitly.
- `tag_ids` always uses `(6, 0, [...])` replace-semantics, never `(4, id)` append.
- `stage_id` always points at a stage XML ID (`crm.stage_lead1..4` live in `crm_stage_data.xml`; `stage_lead4` is the only `is_won=True` built-in stage).
- Demo never sets `user_id` / `team_id` without also setting `stage_id` — because `stage_id` is computed from `team_id` at create time, setting a stage afterwards requires an explicit value.

## CSV Recommendations

**Lead vs opportunity:** Always set `type` explicitly. Do not rely on the default (which depends on whether the loading user has `crm.group_use_lead`). If the target DB has "Leads" disabled, setting `type='lead'` is still accepted by `create()` — the selection allows both values regardless of group.

**Stage resolution:** `stage_id` is precomputed from `team_id + type`. If you want records to land in a specific stage, set `stage_id` explicitly. The default resolves via `_stage_find()` (`crm_lead.py:1071`): first non-folded stage where `team_ids` is empty OR contains the lead's team, ordered by `sequence, id`. On a fresh `crm` install, this means `crm.stage_lead1` ("New").

**Team auto-assignment:** If you omit `team_id` but set `user_id`, `_compute_team_id` picks a team via `crm.team._get_default_team_id(user_id=..., domain=[('use_leads'|'use_opportunities', '=', True)])`. If the user has no sales team matching `type`, `team_id` stays empty — which also leaves `company_id` unset. **Set both `user_id` and `team_id` explicitly to avoid surprises.**

**Do not land leads in a Won stage from CSV** unless you also set `probability=100`, `active=True`, and `date_closed`. Writing a non-100 probability to a `is_won` stage raises `_check_won_validity`. `create()` will auto-set `date_closed=now` for won-stage leads, but bulk loaders often re-write after create and can trip the constraint.

**Partner sync gotcha:** If you set `partner_id`, the compute methods will overwrite any `contact_name`, `partner_name`, `email_from`, `phone`, `function`, `website`, `lang_id`, `street`, `street2`, `city`, `zip`, `state_id`, `country_id` values you also sent in the same `create()` call (they depend on `partner_id`). Either:
- Set `partner_id` alone and let partner data propagate, OR
- Omit `partner_id` and set the denormalized fields (typical lead pattern — no partner yet).

**UTM fields (`campaign_id`, `medium_id`, `source_id`):** Resolve by name via `utm.*` XML IDs. All three are `ondelete='set null'` so a stale UTM reference won't block import.

**Currency:** `company_currency` is computed from `company_id`. Monetary fields (`expected_revenue`, `recurring_revenue`) are denominated in `company_currency`, not `res.company.currency_id` directly — make sure `company_id` is correct before loading monetary values.

**Date fields auto-recompute:** `date_open`, `date_closed`, `date_last_stage_update`, `date_conversion`, `day_open`, `day_close` are all set by `create()`/`write()` or by stored computes. Avoid setting them in CSV unless backfilling historical data, in which case pass them in the same `create()` call (write-after-create will overwrite them).

**`probability`:** Writing a value decouples it from the PLS automation (`is_automated_probability` becomes `False`). For bulk CSV of historic opportunities this is usually what you want.

## Recommended Identity Key for csv_loader

`crm.lead.name` is **not unique** by design — Odoo allows many leads with identical names (e.g. multiple "Info about services" entries). Demo data itself relies on XML IDs, not name uniqueness. A single-column key would silently merge unrelated leads on reload.

Use a compound key that captures the business identity of a lead:

```
"crm.lead": ["name", "email_from", "partner_name"]
```

Rationale:
- `name` alone is too weak (duplicates are normal).
- `email_from` is the strongest single discriminator for inbound leads — it's the `_primary_email` and is indexed via `email_normalized`.
- `partner_name` covers the lead phase where `partner_id` is empty but the prospect company is known.
- `partner_id` is deliberately excluded: it is often `False` for leads and gets auto-filled post-import, so including it would flip the identity after the first reload.

If the dataset is exclusively opportunities with a `partner_id` set from day one, `["name", "partner_id"]` is acceptable. For mixed lead+opportunity loads, the three-field key above is safer.
