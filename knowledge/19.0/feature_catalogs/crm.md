# Feature Catalog — CRM (crm)

**Version:** 19.0
**Source:** community
**Category:** Sales/CRM
**Dependencies:** base_setup, sales_team, mail, calendar, resource, utm, web_tour, contacts, digest, phone_validation

## Business Capabilities

- **Lead-to-opportunity pipeline:** Capture unqualified leads (optional), qualify them, convert to opportunities, move through configurable kanban stages (New, Qualified, Proposition, Won), and track lost reasons with closing notes.
- **Sales team organization:** Multiple sales teams with per-team pipelines, email aliases that create leads/opportunities from inbound messages, per-team stages, and team-scoped lead properties.
- **Predictive Lead Scoring (PLS):** Statistical Won/Lost probability computed from configurable frequency fields (stage plus selectable criteria like country, language, tags, source); probabilities are recomputed via cron and can be manually refreshed from the settings panel.
- **Rule-based lead assignment:** Automatic distribution of unassigned leads to salespersons based on team assignment domains, per-member capacity (monthly lead quota) and domain filters; can run manually or via recurring cron.
- **Revenue forecasting and recurring revenue:** Expected revenue, prorated revenue based on probability, and optional recurring revenue with monthly plans (MRR) feeding a dedicated Forecast analysis view.
- **Activity-driven follow-up:** Built-in mail activities, activity plans scoped to leads, meeting integration (`calendar.event.opportunity_id`), and an Activity Analysis SQL report for follow-up KPIs.
- **Lead deduplication and merge:** Duplicate detection on email domain/phone plus a merge wizard that consolidates selected leads/opportunities into a single record, preserving history.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| CRM > Sales > My Pipeline | My Pipeline | Kanban of opportunities assigned to the current user, grouped by stage (`crm_lead_action_pipeline`) |
| CRM > Sales > My Activities | My Activities | Activity-centric list of leads and opportunities with scheduled actions for the current user |
| CRM > Sales > Teams | Teams | Team pipeline kanban inherited from `sales_team` (`sales_team.crm_team_action_pipeline`) |
| CRM > Sales > Customers | Customers | Standard contacts/partners list scoped for sales use (`base.action_partner_form`) |
| CRM > Leads | Leads | All leads list/kanban; visible only when the "Leads" feature group is active (`crm.group_use_lead`) |
| CRM > Reporting > Forecast | Forecast | Kanban/graph/pivot of opportunities by expected closing date, including prorated and recurring revenue |
| CRM > Reporting > Pipeline | Pipeline Analysis | Graph/pivot/list analysis of opportunities (won/lost, by stage, salesperson, team, UTM) |
| CRM > Reporting > Leads | Leads Analysis | Leads creation trends, active/inactive analysis, conversion rate (visible when Leads are enabled) |
| CRM > Reporting > Activities | Activities | Activity Analysis pivot: completed activities per type, author, lead, stage |
| CRM > Configuration > Settings | Settings | CRM feature toggles (`crm.crm_config_settings_action`) |
| CRM > Configuration > Sales Teams | Sales Teams | Team setup: members, alias, assignment, lead/pipeline toggles |
| CRM > Configuration > Teams Members | Teams Members | Membership between salespersons and teams with per-member capacity (developer mode) |
| CRM > Configuration > Activities > Activity Types | Activity Types | Custom activity types available on leads and opportunities |
| CRM > Configuration > Activities > Activity Plans | Activity Plans | Predefined sequences of activities that can be launched on a lead/opportunity |
| CRM > Configuration > Recurring Plans | Recurring Plans | Monthly plans used to compute MRR on opportunities (visible when Recurring Revenues is enabled) |
| CRM > Configuration > Pipeline > Stages | Stages | Pipeline stages with won flag, rotting threshold, team scoping (developer mode) |
| CRM > Configuration > Pipeline > Tags | Tags | Opportunity classification tags (model `crm.tag`, defined in `sales_team`) |
| CRM > Configuration > Pipeline > Lost Reasons | Lost Reasons | Reasons used to close an opportunity as lost |
| CRM > Import & Synchronize | Import & Synchronize | Placeholder menu populated by companion modules (IAP, website, livechat) |

### Settings & Feature Flags

Defined on `res.config.settings` in `odoo/addons/crm/models/res_config_settings.py` and surfaced by `odoo/addons/crm/views/res_config_settings_views.xml`.

| Setting | Technical Field | What it Enables |
|---|---|---|
| Leads | `group_use_lead` | Adds a qualification step: unqualified `crm.lead` records appear before conversion to opportunities; grants `crm.group_use_lead` and shows the Leads menu |
| Recurring Revenues | `group_use_recurring_revenues` | Exposes recurring revenue, recurring plan, and MRR fields on opportunities; unlocks the Recurring Plans config menu |
| Multi Teams | `is_membership_multi` | Allows a salesperson to belong to several sales teams (writes `sales_team.membership_multi`) |
| Membership / Partnership | `module_partnership` | Installs `partnership` to manage members/partners, member grades, commission plans |
| Rule-Based Assignment | `crm_use_auto_assignment` | Activates lead assignment across teams using team assignment domains and per-member capacity |
| Auto Assignment Action | `crm_auto_assignment_action` | `manual` = assignment button on team; `auto` = enable the `ir_cron_crm_lead_assign` cron |
| Auto Assignment Interval | `crm_auto_assignment_interval_type` / `_interval_number` | Cron cadence (minutes/hours/days/weeks) written back to the assignment cron |
| Lead Enrichment | `module_crm_iap_enrich` | Installs `crm_iap_enrich` to enrich leads with company data from their email domain (IAP credits) |
| Enrich Automatically | `lead_enrich_auto` | `manual` vs `auto` enrichment of newly created leads (config parameter `crm.iap.lead.enrich.setting`) |
| Lead Mining | `module_crm_iap_mine` | Installs `crm_iap_mine` for generating leads by country, industry, company size via IAP |
| Visits to Leads | `module_website_crm_iap_reveal` | Installs `website_crm_iap_reveal` to convert anonymous website visitors into leads via IP resolution |
| Lead Mining in Pipeline | `lead_mining_in_pipeline` | Adds a Lead Mining request action directly on the opportunity pipeline (config parameter `crm.lead_mining_in_pipeline`) |
| Predictive Lead Scoring Fields | `predictive_lead_scoring_fields` | Fields used by PLS to compute Won/Lost frequency (stored comma-separated in `crm.pls_fields`) |
| Predictive Lead Scoring Start Date | `predictive_lead_scoring_start_date` | Earliest lead creation date included in PLS training (stored in `crm.pls_start_date`) |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `crm.lead` | Primary | Unified lead and opportunity record (`type` = lead/opportunity) with pipeline, revenues, contact, probability, won/lost status | Yes |
| `crm.team` | Configuration | Sales team (defined in `sales_team`, extended here with `use_leads`, `use_opportunities`, assignment settings, `lead_properties_definition`, mail alias) | Yes |
| `crm.team.member` | Configuration | Membership of a user in a sales team (defined in `sales_team`, extended here with assignment capacity and warnings) | Yes (embedded in team) |
| `crm.tag` | Configuration | Classification tags for leads and opportunities (defined in `sales_team`) | Yes |
| `crm.stage` | Configuration | Pipeline stages with sequence, won flag, fold, rotting threshold, optional team scoping | Yes |
| `crm.lost.reason` | Configuration | Reasons attached to an opportunity when marked lost, with leads count drill-down | Yes |
| `crm.recurring.plan` | Configuration | Named plan (N months) used to compute recurring revenue on opportunities | Yes |
| `crm.lead.scoring.frequency` | Transactional | Per-team Won/Lost frequency counts per (variable, value) pair that drive PLS | No (internal) |
| `crm.lead.scoring.frequency.field` | Configuration | Whitelist of `crm.lead` fields eligible as PLS variables | Yes (selected in settings) |
| `crm.activity.report` | Reporting | SQL view joining `mail.message` with `crm.lead` to analyze completed activities per lead/stage/team | Yes (pivot/graph) |
| `calendar.event` | Transactional (extended) | Meetings linked to opportunities via `opportunity_id`; drives "next meeting" display on the lead | Yes |
| `res.partner` | Primary (extended) | Partners gain lead/opportunity counts and lead-related smart buttons | Yes |
| `utm.campaign` | Configuration (extended) | Campaign records show linked leads/opportunities and revenue attribution | Yes |
| `digest.digest` | Reporting (extended) | Adds CRM KPIs (new leads, opportunities won) to the periodic digest | Yes |
| `mail.activity.plan` | Configuration (extended) | Activity plans scoped to the `crm.lead` model | Yes |

### Reports & Analytics

- **Pipeline Analysis** (`crm.crm_opportunity_report_action`, model `crm.lead`): graph/pivot/list over opportunities with measures for expected revenue, prorated revenue, recurring revenue, probability, days to close/assign; default filters for current period and opportunity type.
- **Leads Analysis** (`crm.crm_opportunity_report_action_lead`): same underlying model filtered to `type = lead`, with defaults on active/inactive and create date, used to track lead volume and conversion.
- **Forecast** (`crm.crm_lead_action_forecast`): forecast kanban/graph/pivot grouped by expected closing date (`date_deadline`) with prorated and recurring revenue; backend assets load dedicated forecast graph and pivot renderers (`crm/static/src/views/forecast_graph`, `forecast_pivot`).
- **Activities Analysis** (`crm.crm_activity_report_action`, model `crm.activity.report`): SQL view (`crm/report/crm_activity_report.py`) aggregating completed mail activities on leads, filterable by team, salesperson, stage, country, activity type, won/lost status.
- **Dashboards per team:** `crm.team` form exposes smart buttons for unassigned leads, opportunities, pipeline value, and "assigned this month vs. capacity" (`lead_all_assigned_month_count` / `assignment_max`).
- **Digest KPIs:** `crm/models/digest.py` extends `digest.digest` to report new leads and won opportunities in the standard periodic digest email.

### Wizards & Advanced Actions

| Wizard | Model | Purpose |
|---|---|---|
| Mark Lost | `crm.lead.lost` | Set one or more leads/opportunities as lost with a lost reason and a rich-text closing note that is logged in the chatter |
| Convert to Opportunity | `crm.lead2opportunity.partner` | Convert a single lead to an opportunity: create or link a customer, detect duplicates, optionally merge with existing opportunities, force-assign a salesperson/team |
| Mass Convert to Opportunity | `crm.lead2opportunity.partner.mass` | Apply the conversion above to many leads at once with deduplication across the batch |
| Merge Opportunities | `crm.merge.opportunity` | Merge selected leads/opportunities into one, preserving chatter, activities, followers, tags; uses the merge template in `data/crm_lead_merge_template.xml` |
| Update Probabilities | `crm.lead.pls.update` | Recompute Predictive Lead Scoring across all open opportunities using the current PLS fields and start date (exposed via button on the settings panel) |
| Assign Leads (action) | `crm.team.action_assign_leads` | Server action on teams that runs rule-based assignment immediately; also exposed in settings via "Update now" refresh button |
| CRM: Lead Assignment (cron) | `ir.cron` `crm.ir_cron_crm_lead_assign` | Scheduled recurring execution of `crm.team._cron_assign_leads()`; activated and rescheduled from the auto-assignment settings |

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `crm_iap_enrich` | community | Enrich leads with company data (industry, size, social links) from the email domain using IAP credits |
| `crm_iap_mine` | community | Lead mining: generate new leads by country, industry, company size via IAP |
| `iap_crm` | community | Internal bridge between IAP and CRM used by mining/enrichment/reveal modules |
| `crm_livechat` | community | Create a lead automatically from a livechat conversation |
| `crm_mail_plugin` | community | Turn emails received in Outlook/Gmail into leads via the mail plugin, logging the conversation |
| `crm_sms` | community | Send SMS from leads/opportunities and schedule SMS activities |
| `sale_crm` | community | Quote from an opportunity: create sales orders directly from `crm.lead`, smart button back to the opportunity, pipeline-to-sales KPIs |
| `event_crm` | community | Automatically create leads from event registrations using registration-based rules |
| `event_crm_sale` | community | Adds event-specific sale order information to the auto-created event leads |
| `survey_crm` | community | Generate leads from survey responses |
| `gamification_sale_crm` | community | Preconfigured sales gamification challenges and badges tied to CRM KPIs |
| `mass_mailing_crm` | community | Attach UTM info from mass mailings to leads/opportunities and measure campaign performance on CRM |
| `mass_mailing_crm_sms` | community | Same as above for SMS mass mailings |
| `website_crm` | community | Public "Contact Us" form on the website that creates a lead |
| `website_crm_iap_reveal` | community | Convert anonymous website visitors into leads by resolving IP to company data |
| `website_crm_livechat` | community | Show livechat sessions on the lead form |
| `website_crm_partner_assign` | community | Publish resellers/partners on the website and forward leads to them (sub-catalog available) |
| `website_crm_sms` | community | Send SMS to identified website visitors tied to a lead |
| `website_event_crm` | community | Create leads from website event registrations using registration rules |
| `ai_crm` | enterprise | Automatically create leads using AI scoring/classification (sub-catalog available) |
| `ai_crm_livechat` | enterprise | AI-powered lead creation from livechat transcripts (sub-catalog available) |
| `appointment_crm` | enterprise | Generate a lead whenever a prospect books an appointment |
| `website_appointment_crm` | enterprise | Enrich appointment-generated leads with gathered website visitor information |
| `crm_enterprise` | enterprise | Advanced CRM features: cohort/spreadsheet views, enhanced dashboards, extra analytics (sub-catalog available) |
| `crm_enterprise_partner_assign` | enterprise | Enterprise counterpart of Resellers with extended partner assignment features |
| `crm_helpdesk` | enterprise | Convert helpdesk tickets from/to CRM leads |
| `crm_sale_subscription` | enterprise | Link opportunities to subscriptions and convert opportunities directly into subscription quotations |
| `sale_renting_crm` | enterprise | Convert an opportunity into a rental quotation |
| `data_merge_crm` | enterprise | Deduplicate leads/opportunities using the Data Cleaning tool |
| `marketing_automation_crm` | enterprise | Target and react to leads/opportunities from Marketing Automation workflows |
| `social_crm` | enterprise | Attach CRM UTM info to social posts and generate leads from social interactions |
| `spreadsheet_dashboard_crm` | enterprise | Pre-built spreadsheet dashboards for CRM KPIs |
| `voip_crm` | enterprise | VoIP integration: call from a lead, log calls, create call-based activities |
| `website_crm_iap_reveal_enterprise` | enterprise | Enterprise counterpart of Visits-to-Leads with extended visitor analytics |

## Demo Highlights

1. **Kanban pipeline with drag-and-drop, prorated revenue and rotting flags** — The opportunity kanban shows priority, expected revenue, prorated revenue (revenue * probability), and highlights "rotting" opportunities that have not been updated within the stage's `rotting_threshold_days`. It is the canonical Odoo CRM screen and immediately communicates pipeline health.

2. **Predictive Lead Scoring with manual "Update Probabilities"** — Configure the PLS fields (stage, country, language, tags, source) and start date in Settings, then click "Update Probabilities" to recompute Won likelihood on every open opportunity using historical frequency data. The probability drives the `prorated_revenue` shown on every card.

3. **Rule-based Lead Assignment with capacity and domain filters** — Each team member has a monthly `assignment_max` capacity; each team has an `assignment_domain`. Enable auto-assignment, set the cron cadence (e.g. every day), and watch unassigned leads flow to the right salespersons without manual triage. The "Update now" button in settings makes this instant in a demo.

4. **Lead-to-Opportunity conversion with duplicate detection and merge** — From a lead, open "Convert to Opportunity": the wizard detects duplicates on email domain and phone, offers to merge them into a single opportunity, and lets you create or link an existing customer in one step. Mass convert runs the same flow on many selected leads.

5. **Recurring revenue and Forecast view** — Enable "Recurring Revenues", create recurring plans (e.g. "Monthly", "Annual"), and opportunities gain MRR and prorated MRR fields. The Forecast menu visualizes expected revenue per closing month, which is compelling for SaaS or subscription-oriented prospects.

6. **Team email alias creating leads from inbound email** — Each `crm.team` has a mail alias; emails sent to it automatically create leads assigned to the team, with the conversation threaded on the lead. Combined with `crm_mail_plugin`, inbound sales traffic is captured without manual entry.
