# Feature Catalog — Website CRM Partner Assign (website_crm_partner_assign) — Sub-catalog

Sub-catalog — Partner assignment and geolocation matching on leads; public partner directory. Extends `crm` + `website_partner`.

**Version:** 19.0
**Source:** community
**Category:** Website/Website
**Dependencies:** base_geolocalize, crm, account, partnership, website_partner, website_google_map, portal

## Business Capabilities

- **Geo-matching of leads to local partners/resellers:** Automatically assign incoming leads to the nearest partner using lead address geocoding, partner GPS coordinates, country filter, and partner-grade-weighted probability sampling.
- **Partner level / weight system:** Give each partner a grade with a numeric `partner_weight`; weight drives both eligibility (>0) and the random-weighted pick when several partners fit the geography.
- **Partner lifecycle tracking:** Track partner onboarding via an `activation` dimension (First Contact / Ramp-up / Fully Operational) plus partnership date, last review date, next review date, and a partnership analysis pivot.
- **Public reseller directory with map and facets:** Ship a public `/partners` page that lists published resellers grouped by grade and country, with Google Maps integration, industry filter, free-text search, country auto-detection via GeoIP, and SEO-friendly sitemap entries per grade and per country.
- **Portal for assigned partners:** Give resellers a `/my/leads` and `/my/opportunities` portal where they can accept or decline forwarded leads, update contact details, move stages, log activities, and create their own opportunities — all without back-office access.
- **Forward-to-partner workflow:** A wizard (`crm.lead.forward.to.partner`) emails selected leads to partners either individually or in bulk via geo-assignment, using a predefined mail template.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| CRM > Configuration > Partner Activations | Partner Activations | List/edit partner activation stages (First Contact, Ramp-up, Fully Operational) used for onboarding tracking (`res_partner_activation_act`, parent `partnership.crm_menu_partners`) |
| CRM > Reporting > Partnerships | Partnership Analysis | Graph view over `crm.partner.report.assign` showing #opportunities and turnover per partner/grade (`action_report_crm_partner_assign`, parent `crm.crm_menu_report`) |
| CRM > Leads / Pipeline (list action: Forward to partner) | Mass forward to partners | `ir.actions.act_window` bound to `crm.lead` (binding_model_id) that opens the forward wizard in mass-mail mode, performing geo-assignment per lead |
| Contacts > Partner form > "Assigned Partner" page (Partner Activation + Partner Review groups) | Partner assignment fields | Activation, partner_weight, date_review, date_review_next, date_partnership; inherited into `base_geolocalize.view_crm_partner_geo_form` |
| Contacts > Partner Grade form (inherited from `partnership`) | Publish grade on website | Adds `partner_weight` and a `website_redirect_button` on `is_published` so each grade has a public page at `/partners/grade/<slug>` |
| CRM > Leads/Pipeline > form > Assigned Partner page | Per-lead assignment panel | Geolocation (`partner_latitude`/`partner_longitude`), `partner_assigned_id` many2one-avatar, "Automatic Assignment" button (`action_assign_partner`) and "Send Email" button opening the forward wizard for the single assignee |

Note: this module adds no top-level app menu; it grafts onto the CRM, Contacts and Partnership menus of the apps it depends on.

### Public / Portal Routes (Controllers)

All public and portal controllers live in `odoo/addons/website_crm_partner_assign/controllers/main.py`.

| Route | Auth | Handler | Purpose |
|---|---|---|---|
| `/partners`, `/partners/page/<int:page>` | public | `WebsiteCrmPartnerAssign.partners` | Public resellers directory: published partners with a grade, filterable by grade, country, industry; free-text search on name/description/address; GeoIP-inferred default country; pager of 40 references; renders `website_crm_partner_assign.index` |
| `/partners/grade/<model("res.partner.grade"):grade>` (+ `/page/<int:page>`) | public | `WebsiteCrmPartnerAssign.partners` | Directory filtered by grade; SEO sitemap entry per published grade |
| `/partners/country/<model("res.country"):country>` (+ `/page/<int:page>`) | public | `WebsiteCrmPartnerAssign.partners` | Directory filtered by country; SEO sitemap entry per country that has resellers |
| `/partners/grade/<grade>/country/<country>` (+ `/page/<int:page>`) | public | `WebsiteCrmPartnerAssign.partners` | Directory filtered by both grade and country |
| `/partners/<slug>` | public | `WebsiteCrmPartnerAssign.partners_detail` (override of `website_partner`) | Public partner detail page; redirects to canonical slug; renders `website_crm_partner_assign.partner` |
| Google Maps domain hook | public | `WebsiteCrmPartnerAssign._get_gmap_domains` | Overrides `website_google_map` to pin published partners (with grade) on the embedded map, respecting current grade/country facets |
| `/my/leads` (+ `/page/<int:page>`) | user | `WebsiteAccount.portal_my_leads` | Portal list of leads whose `partner_assigned_id` is a descendant of the logged-in commercial partner |
| `/my/lead/<crm.lead>` | user | `WebsiteAccount.portal_my_lead` | Portal detail/edit page for a single assigned lead (accept/decline buttons wired to `partner_interested` / `partner_desinterested`) |
| `/my/opportunities` (+ `/page/<int:page>`) | user | `WebsiteAccount.portal_my_opportunities` | Portal list of assigned opportunities with filters (active / no activities / late / today / future / won / lost) and sort (date, name, revenue, probability, stage) |
| `/my/opportunity/<crm.lead>` | user | `WebsiteAccount.portal_my_opportunity` | Portal detail for an opportunity: edit expected revenue/probability/priority/deadline, change stage, log/update an activity, update contact & address, create new opportunity |

The public directory is listed as a suggested website content entry ("Resellers" → `/partners`) via `Website.get_suggested_controllers` in `odoo/addons/website_crm_partner_assign/models/website.py`, and declared via `list_as_website_content=_lt("Partners")` on the `/partners` route.

### Settings & Feature Flags

This module does not expose `res.config.settings` toggles; its behavior is driven by **per-record configuration**:

| Toggle | Technical Field | What it Enables |
|---|---|---|
| Publish a partner | `res.partner.website_published` (from `website_partner`) | Makes the partner appear on `/partners` and on its slug page |
| Partner level (eligibility + weight) | `res.partner.grade_id` → `res.partner.grade.partner_weight` | `partner_weight > 0` on the partner is the gate for being a candidate in `search_geo_partner`; higher weight ⇒ higher pick probability |
| Publish a grade | `res.partner.grade.is_published` | Controls whether a grade's public page (`/partners/grade/<slug>`) is visible to non-editors and whether partners with that grade show to the public |
| Activation stage | `res.partner.activation` (Many2one to `res.partner.activation`, tracked) | Onboarding state used in reporting and filters; seeded with 3 levels (First Contact, Ramp-up, Fully Operational) via `data/res_partner_activation_data.xml` |
| Customer implementation link | `res.partner.assigned_partner_id` + `implemented_partner_ids` | Lets a published customer reference be linked to the reseller that implemented it; drives `implemented_partner_count` shown on `/partners` cards |
| Google Maps on `/partners` | `website.google_maps_api_key` (from `website_google_map`) | Without an API key the list renders but the map is disabled |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `res.partner` (extended) | Primary | Adds `partner_weight` (computed from grade, editable, tracked), `grade_sequence` (stored related), `activation`, `date_partnership`, `date_review`, `date_review_next`, `assigned_partner_id` ("Implemented by"), `implemented_partner_ids`, `implemented_partner_count`. Also overrides `_compute_opportunity_count` to include leads assigned to the partner or its children. | Yes |
| `res.partner.grade` (extended) | Configuration | Inherits `website.published.mixin`; adds `partner_weight` and a `website_url = /partners/grade/<slug>`; grade is the eligibility + probability weight for geo-matching. | Yes |
| `res.partner.activation` | Configuration | Onboarding stages for resellers (sequenced, archivable). | Yes |
| `crm.lead` (extended) | Primary | Adds `partner_latitude`, `partner_longitude`, `partner_assigned_id` (tracked), `partner_declined_ids` (many2many of partners that refused this lead), `date_partner_assign` (computed from `partner_assigned_id` set). Hosts `action_assign_partner`, `assign_partner`, `assign_geo_localize`, `search_geo_partner`, `partner_interested`, `partner_desinterested`, `update_lead_portal`, `update_contact_details_from_portal`, `update_stage_from_portal`, `create_opp_portal`. | Yes |
| `crm.lead.forward.to.partner` | Transactional (wizard) | Compose-and-forward wizard; supports `forward_type = single` (pick one partner) or `assigned` (auto-assign each lead by geo + weight). Sends via template `email_template_lead_forward_mail`, writes `partner_assigned_id` + `user_id` on each lead, subscribes the partner. | Yes (wizard form) |
| `crm.lead.assignation` | Transactional (wizard line) | Per-lead row inside the forward wizard, holding the proposed `partner_assigned_id`, lead & partner locations, and portal link. | Yes (embedded) |
| `crm.partner.report.assign` | Reporting | SQL view (`_auto = False`) joining `res_partner` with `account.invoice.report` and `crm.lead`, exposing #opportunities and invoiced turnover per partner, grouped by grade / activation / user / partnership date / review date. | Yes (graph/search) |
| `website` (extended) | Configuration | `get_suggested_controllers` advertises "/partners" as a website content entry. | No (admin UI side-effect) |

### Public Website Templates (QWeb)

Declared in `odoo/addons/website_crm_partner_assign/views/website_crm_partner_assign_templates.xml`.

| Template | Purpose |
|---|---|
| `website_crm_partner_assign.layout` | Outer layout for all `/partners*` pages with two `oe_structure` drop zones for website builder blocks |
| `website_crm_partner_assign.index` | Directory page: filters by grade/country (desktop dropdowns + mobile off-canvas), search box, partner cards grouped by grade, pager |
| `website_crm_partner_assign.index_filter_by_industry` | Optional inherited filter (activable from the builder) that adds an industry facet driven by `implemented_partner_ids.industry_id` |
| `website_crm_partner_assign.ref_country` | Optional inherited block that renders the Google Maps world map of resellers |
| `website_crm_partner_assign.o_wcrm_partner_address` | Optional inherited block showing partner addresses on directory cards |
| `website_crm_partner_assign.partner` | Public partner detail page (builds on `website_partner.partner_detail`) |
| `website_crm_partner_assign.contact_details` / `.grade_in_detail` / `.references_block` | Inherits adding contact info, grade badge, and a references/implemented-customers block to the partner detail |
| `website_crm_partner_assign.portal_my_home_lead` / `.portal_my_home_menu_lead` | Portal home cards/breadcrumbs linking to "/my/leads" and "/my/opportunities" |
| `website_crm_partner_assign.portal_my_leads` / `.portal_my_opportunities` | Portal lists with sort/filter/pager |
| `website_crm_partner_assign.portal_my_lead` | Portal lead detail with two modal forms: "I'm interested" (→ `partner_interested`) and "Not interested" (→ `partner_desinterested`, optional "mark as spam") |
| `website_crm_partner_assign.portal_my_opportunity` | Portal opportunity detail: edit revenue/probability/priority/deadline, pick stage, edit contact + address, log/update an activity, modal to create a new opportunity via `create_opp_portal` |

### Reports & Analytics

- **Partnership Analysis** (`crm.partner.report.assign`, view file `report/crm_partner_report_view.xml`): graph view measuring `nbr_opportunities` and `turnover` by grade; searchable/groupable by Salesperson, Partner, Partnership Date, Review Date; activation as a filter. Default domain excludes rows with no grade.
- **CRM pivot/graph extensions** (`views/crm_lead_views.xml`): `partner_latitude` / `partner_longitude` are added as invisible fields to the CRM pivot (`crm.crm_lead_view_pivot`), opportunity report pivot/graph, forecast pivot/graph, so they are available as measures/dimensions when the user switches them on.
- **Enterprise extras** — see Companion Modules below: `crm_enterprise_partner_assign` extends the enterprise-only CRM graph and cohort views with the same lat/long fields.

### Wizards & Advanced Actions

| Wizard / Action | Model / XML id | Purpose |
|---|---|---|
| Forward to Partner (single) | `crm.lead.forward.to.partner` / `crm_lead_forward_to_partner_act` | From a single lead: pick a partner manually and email them with the lead details via `email_template_lead_forward_mail`; writes `partner_assigned_id` and subscribes the partner |
| Forward to Partner (mass, geo-assignment) | `crm.lead.forward.to.partner` / `action_crm_send_mass_forward` | List-view action (`binding_model_id=crm.lead`) that runs `search_geo_partner` over selected leads, proposes one partner per lead in an editable line list, then emails each |
| Automatic Assignment (per lead) | `crm.lead.action_assign_partner` / `assign_partner` | Button on the lead's "Assigned Partner" page. Geolocates the lead, runs the 6-step geographic search in `search_geo_partner` (narrow box ±2°/±1.5°, wider ±4°/±3°, wider ±8°, same-country fallback, nearest-neighbor SQL via PostgreSQL `point <-> point`), weighted random pick by `partner_weight`; tags the lead with `tag_portal_lead_partner_unavailable` when no candidate exists |
| Assign salesman of assigned partner | `crm.lead.assign_salesman_of_assigned_partner` | Reassigns each lead's `user_id` to the assigned partner's `user_id` |
| Create portal opportunity | `crm.lead.create_opp_portal` | Invoked from the portal "new opportunity" modal; requires the caller's commercial partner to have a grade; tags with `tag_portal_lead_own_opp` |
| Portal accept lead | `crm.lead.partner_interested` | Posts a message and converts the lead to an opportunity in sudo |
| Portal decline lead | `crm.lead.partner_desinterested` | Unsubscribes the commercial-partner chain, optionally flags `tag_portal_lead_is_spam`, records the partner(s) in `partner_declined_ids`, clears `partner_assigned_id` so the lead can be re-assigned |

### Data / Seed records

- `data/res_partner_activation_data.xml` — seeds Fully Operational / Ramp-up / First Contact activation stages.
- `data/crm_tag_data.xml` — seeds 3 CRM tags used by the portal flow: `tag_portal_lead_partner_unavailable`, `tag_portal_lead_is_spam`, `tag_portal_lead_own_opp`.
- `data/mail_template_data.xml` — mail template `email_template_lead_forward_mail` used by the forward wizard.
- `data/crm_lead_merge_template.xml` — QWeb template used when merging leads, so `partner_latitude/longitude/partner_assigned_id/date_partner_assign` survive the merge (`_merge_get_fields` in `crm_lead.py`).
- `security/ir_rule.xml` + `security/ir.model.access.csv` — portal-read on `crm.lead` and `crm.stage`; manager write on activations; sales-salesman CRUD on the wizard models; public/portal read on `res.partner.grade`.

### Frontend Assets

| Bundle | Files |
|---|---|
| `web.assets_frontend` | `static/src/interactions/crm_partner_assign.js` (client-side behavior of `/partners`, facet clicks, mobile off-canvas) |
| `website.website_builder_assets` | `static/src/website_builder/partner_page_option*.{js,xml}`, `website_crm_partner_assign_option*.{js,xml}` — website builder snippet options for the partner page and the resellers directory |
| `web.assets_tests` | `static/tests/tours/*` — HTTP tours covering the `/partners` and portal flows |

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `crm_enterprise_partner_assign` | enterprise | `auto_install=True` bridge: re-adds `partner_latitude`/`partner_longitude` as invisible fields on the enterprise-only CRM pivot, cohort, and graph views (`crm_enterprise.crm_lead_view_cohort`, `crm_enterprise.crm_opportunity_view_graph`, etc.). No new models or routes. |
| `website_customer` | community | Public customer references directory (`/customers`) reusing the partner page infrastructure; depends on `website_crm_partner_assign` + `website_partner` + `website_google_map`. |
| `partner_commission` | enterprise | Resellers commissions on subscription sales; relies on the grade/weight structure added here. |
| `test_crm_full` | community | Test-only dependency bundle that pulls `website_crm_partner_assign` in to cover cross-module CRM tours. |
| `partnership` | community (dependency, not companion) | Supplies the base `res.partner.grade` model and the `partnership.crm_menu_partners` parent menu where Partner Activations is grafted. |
| `base_geolocalize` | community (dependency) | Provides `res.partner._geo_localize(street, zip, city, state, country)` and the geo form view inherited to add the Partner Activation / Partner Review groups. |
| `website_partner` | community (dependency) | Provides `website.published.mixin`, the `partner_detail` template inherited by the public partner page, and the `WebsitePartnerPage` controller overridden here. |
| `website_google_map` | community (dependency) | Provides the `GoogleMap` controller and the `_get_gmap_domains` hook overridden here to filter the embedded map on `/partners`. |

## Demo Highlights

1. **Automatic geo-matching of a new lead** — Create a lead with a country and street; click "Automatic Assignment" on the Assigned Partner page. Odoo geocodes the address (`_geo_localize`) and walks the 6-step search (small → large → extra-large bounding box, then country-wide, then nearest-neighbor via PostgreSQL `point <-> point`), doing a **weighted random pick by `partner_weight`**. Instantly a local reseller is assigned, the partner's salesperson is set as `user_id`, and the partner is subscribed.

2. **Public reseller directory with grade + country facets and Google Map** — Visit `/partners`: partners are grouped by grade and cards show a references counter ("3 references »") linking back to implemented customers. Dropdowns filter by grade and country; a mobile off-canvas panel gives the same filters on touch devices; GeoIP auto-selects the visitor's country; the optional "World Map" block pins resellers on Google Maps.

3. **Partner portal that accepts/declines leads** — Sign in as a portal user whose commercial partner is a reseller. `/my/leads` lists the forwarded leads; each has a "I'm interested" modal (converts to opportunity) and a "Not interested" modal (optionally "mark as spam", records the partner in `partner_declined_ids` so the lead is re-assignable without re-proposing the same partner).

4. **Bulk "Forward to Partner" with geo-assignment** — From the Leads list, select a batch, pick the Action menu's "Forward to partner", choose the "several partners: automatic assignment, using GPS coordinates and partner's grades" mode. The wizard shows one proposed partner per lead, with lead and partner locations side-by-side, then emails each partner via a prebuilt template in a single click.

5. **Partnership Analysis** — CRM > Reporting > Partnerships shows a graph of `#opportunities` and `turnover` per grade/partner sourced from a SQL view that joins `account.invoice.report` and `crm.lead`, with group-by on partnership date / review date / salesperson — a concrete KPI per reseller for a channel-management review.
