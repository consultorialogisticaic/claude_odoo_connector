# Feature Catalog — CRM Enterprise (crm_enterprise) — Sub-catalog

Sub-catalog for the enterprise companion to the base `crm` app — see `crm.md` for the mainline catalog.

**Version:** 19.0
**Source:** enterprise
**Category:** Sales/CRM
**Dependencies:** crm, web_cohort, web_map

## Business Capabilities

- **Advanced pipeline analytics views:** Adds cohort, map, pivot, and graph views to the CRM pipeline so sales managers can slice opportunities by retention, geography, stage, and salesperson alongside the community kanban/list/calendar.
- **Pipeline Analysis dashboard:** Rewires the CRM reporting menu to a multi-view dashboard (graph + pivot + cohort + list) focused on opportunities, replacing the community report action.
- **Geographic pipeline map:** Plots opportunities on a map using the linked customer (`partner_id`), with routing enabled so a salesperson can build a visit itinerary from the pipeline view.
- **Churn / retention cohort analysis:** Tracks opportunities from creation to closing in weekly cohorts (churn mode), enabling managers to see how quickly cohorts of leads are lost or converted.
- **Business card scanner for lead capture:** Adds a cog-menu action on the opportunity list/kanban that uploads phone photos of business cards, runs them through OpenAI GPT-4o-mini (or Odoo IAP as fallback) to OCR contact/company/address data, and auto-creates opportunities linked to the scanned image.
- **Conversion/overshoot KPIs on leads:** Adds stored computed fields `days_to_convert` (create → conversion) and `days_exceeding_closing` (deadline vs. actual close) for use in reports and search filters.

## Feature Inventory

### Menu Structure

`crm_enterprise` does not introduce top-level menus. It retargets the existing CRM reporting menu to its richer dashboard action.

| Menu Path | Feature | Description |
|---|---|---|
| CRM > Reporting > Pipeline | Pipeline Analysis (retargeted) | The community `crm.crm_opportunity_report_menu` is rebound to `crm_enterprise.crm_opportunity_action_dashboard`, a multi-view analysis window (graph, pivot, cohort, list, form) pre-filtered to opportunities created within the current period. |

Source: `enterprise/crm_enterprise/views/crm_lead_views.xml` (the `<record id="crm.crm_opportunity_report_menu" model="ir.ui.menu">` rewrite).

### Settings & Feature Flags

`crm_enterprise` does not add a `res.config.settings` toggle. It exposes one system parameter for the AI scanner:

| Setting | Technical Key | What it Enables |
|---|---|---|
| Business Card Scanner — OpenAI API key | `ir.config_parameter: crm_enterprise.business_card_reader.openai_key` | If set, business-card OCR calls OpenAI GPT-4o-mini directly with this key; if empty, the scanner falls back to Odoo IAP (`html_editor.olg_api_endpoint`). Source: `enterprise/crm_enterprise/tools/business_card_scanner.py`. |

Module install itself is a feature flag: it is declared `auto_install: ['crm']`, so every database with `crm` installed gets the enterprise views automatically.

### Key Models

Only one model is touched — `crm.lead` is extended with reporting fields and the scanner entry point. No new models are defined.

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `crm.lead` (extension) | Primary | Adds `days_to_convert` (stored, compute on `date_conversion` / `create_date`) and `days_exceeding_closing` (stored, compute on `date_deadline` / `date_closed`) as measurable KPIs for the forecast/pivot/graph views. Adds `action_ocr_business_cards(attachment_ids)` which invokes `BusinessCardScanner` and returns an `ir.actions.act_window` pointing to the generated opportunities. | Yes |

Source: `enterprise/crm_enterprise/models/crm_lead.py`.

### Reports & Analytics

All report/analysis surfaces on `crm.lead` that this module adds or reshapes:

- **Pipeline Analysis dashboard** (`crm_enterprise.crm_opportunity_action_dashboard`): multi-view action with `view_mode="graph,pivot,cohort,list,form"`, default filters `filter_opportunity` + `filter_create_date`, reusing `crm.crm_opportunity_report_view_search`.
- **Opportunities graph** (`crm_enterprise.crm_opportunity_view_graph`): graph keyed by `stage_id` × `date_deadline` (monthly).
- **Leads graph** (`crm_enterprise.crm_lead_view_graph`): line graph on `create_date` by week.
- **Leads pivot** (`crm_enterprise.crm_lead_view_pivot`): rows = `user_id`; measures = `expected_revenue`, `prorated_revenue`, `day_close`.
- **Opportunities cohort** (`crm_enterprise.crm_lead_view_cohort`): date_start = `create_date`, date_stop = `date_closed`, weekly interval, churn mode.
- **Opportunities map** (`crm_enterprise.crm_lead_view_map`): `res_partner="partner_id"` with `routing="1"`, added as a view on `crm.crm_lead_action_pipeline`.
- **Forecast view patches**: `days_to_convert` is injected into the inherited forecast pivot (`crm.crm_lead_view_pivot_forecast`) and forecast graph (`crm.crm_lead_view_graph_forecast`).
- **Action rewrites**: `crm.action_report_crm_lead_salesteam` gets `view_mode="graph,pivot,list,form,cohort"`; `crm.crm_opportunity_report_action_lead` gets `view_mode="graph,pivot,list"`; `crm.crm_lead_opportunities` gains a cohort view via `crm_opportunity_partner_add_cohort`.

Source: `enterprise/crm_enterprise/views/crm_lead_views.xml`.

### Wizards & Advanced Actions

No `TransientModel` wizards are defined in this module. The advanced actions it adds are:

| Action | Entry Point | Purpose |
|---|---|---|
| Scan Business Cards (cog menu) | `cogMenu` registry entry `crm-business-cards-scanner-menu` in `crm_business_card_scanner_cog_menu.js` — visible on `crm.lead` kanban and list views | Opens a hidden `FileUploader`; after upload, calls `crm.lead.action_ocr_business_cards(attachment_ids)` on the server. |
| Scan Business Cards (list controller) | `crm_business_cards_scanner_list` JS class injected via `<attribute name="js_class">` on `crm.crm_case_tree_view_oppor` | Provides the same upload/scan flow from the opportunities list. |
| Scan Business Cards (kanban controller) | `CrmBusinessCardScannerKanbanController` patched onto `crmKanbanView` | Same flow, embedded in the pipeline kanban. |
| Activity menu view expansion | `activity_menu_patch.js` patch on `mail/core/web/activity_menu` | For `crm.lead` activity groups, expands the openable views to `list, kanban, form, calendar, pivot, cohort, map, activity` (enterprise view types). |
| Business card OCR pipeline | `BusinessCardScanner.business_cards_to_leads` in `enterprise/crm_enterprise/tools/business_card_scanner.py` | Calls OpenAI (or IAP), parses JSON (`partner_name`, `contact_name`, `phone`, `email_from`, `website`, `function`, `street`, `street2`, `zip`, `state_code`, `country_code`, `city`), resolves `res.country` / `res.country.state`, formats the phone via `crm.lead._phone_format`, creates opportunities, links the attachment, and returns an action routed to form (1 result) or list+kanban (many). |

### Companion Modules

Enterprise siblings that build directly on top of `crm_enterprise` (explicitly depend on it):

| Module | Source | Features Added |
|---|---|---|
| `crm_enterprise_partner_assign` | enterprise | Enterprise counterpart for the Resellers / partner-assign flow; adds `crm.lead` view tweaks layered on `website_crm_partner_assign`. |
| `spreadsheet_dashboard_crm` | enterprise | Pre-built spreadsheet dashboards for CRM KPIs, shipped on top of the enterprise pipeline views. |
| `website_crm_iap_reveal_enterprise` | enterprise | Enterprise view layer for Website Visitors → Leads (IAP "Reveal"), layered on `website_crm_iap_reveal`. |

Adjacent enterprise CRM add-ons that enrich the same app but depend only on community `crm` (listed so consultants know they compose with this sub-catalog):

| Module | Source | Features Added |
|---|---|---|
| `social_crm` | enterprise | Adds UTM + lead generation statistics to the Social Marketing app. |
| `voip_crm` | enterprise | Adds "schedule call" button on lead kanban; links VoIP calls to leads. |
| `appointment_crm` | enterprise | Generates leads when prospects book an online appointment. |
| `marketing_automation_crm` | enterprise | Exposes CRM as a target model inside Marketing Automation workflows. |
| `data_merge_crm` | enterprise | Finds and merges duplicate leads/opportunities via data cleaning. |
| `ai_crm` | enterprise | Auto-creates leads from AI agent interactions (auto-install with `ai_app` + `crm`). |
| `ai_crm_livechat` | enterprise | Auto-creates leads from live-chat conversations handled by AI agents. |
| `sale_renting_crm` | enterprise | Converts opportunities into rental orders. |

## Demo Highlights

1. **Scan a business card to create an opportunity** — Open the CRM pipeline, hit the cog menu "Scan Business Cards," snap a photo on mobile, and a few seconds later a filled-in opportunity appears with company, contact, phone (E.164-formatted), email, address, country, and state pre-populated. The original image is attached to the lead and logged in the chatter. This is the single most demoable feature of the module.

2. **Pipeline Analysis with cohort churn** — From Reporting > Pipeline, switch to the cohort view. Weekly cohorts of opportunities are plotted from `create_date` to `date_closed` in churn mode, making it trivial to show "of the 40 opportunities created last month, 30% are still open, 50% were won, 20% were lost."

3. **Map view of the pipeline with routing** — On the opportunity pipeline action, switch to the map view. Opportunities geolocate on their linked customer, and with `routing="1"` a field sales rep can sketch a visit route straight from the pipeline — a strong story for a B2B outside-sales team.

4. **Forecast pivot with `days_to_convert`** — The forecast pivot/graph now includes the stored `days_to_convert` KPI, so a sales manager can measure how long each salesperson takes to turn a lead into a qualified opportunity, per stage.

5. **Cross-view consistency from activity menu** — Clicking a CRM activity group in the top-bar activity menu now opens directly into any enterprise view (pivot, cohort, map, activity, calendar), not just list/kanban. Small UX polish, but a visible "enterprise feel" moment.
