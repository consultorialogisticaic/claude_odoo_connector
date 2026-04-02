# Feature Catalog — Helpdesk (helpdesk)

**Version:** 19.0
**Source:** enterprise
**Category:** Services/Helpdesk
**Dependencies:** base_setup, mail, utm, rating, web_tour, web_cohort, resource, portal, digest

## Business Capabilities

- **Ticket lifecycle management:** Create, assign, track, and resolve support tickets through configurable stage pipelines with automatic assignment to team members.
- **SLA policy enforcement:** Define Service Level Agreement deadlines per team, priority, and customer; automatically track compliance with working-hours-aware deadline calculations and freezable stages.
- **Multi-team organization:** Operate multiple support teams with independent pipelines, assignment methods (random, balanced, tag-based dispatch), and dedicated email aliases.
- **Customer satisfaction tracking:** Collect and analyze customer ratings on closed tickets; display satisfaction scores on the team dashboard.
- **Automatic ticket management:** Auto-close inactive tickets after a configurable period, auto-assign tickets to available agents based on workload or tag-matching rules.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| Helpdesk > Overview | Team Dashboard | Kanban dashboard showing all teams with open tickets, SLA success rate, urgent tickets, unassigned count |
| Helpdesk > Tickets > My Tickets | My Tickets | Filtered view of tickets assigned to the current user |
| Helpdesk > Tickets > All Tickets | All Tickets | List/kanban of all tickets across teams |
| Helpdesk > Reporting > Tickets Analysis | Tickets Analysis | Pivot/graph analysis: time to close, time to assign, ratings, SLA status per team/agent |
| Helpdesk > Reporting > SLA Status Analysis | SLA Status Analysis | Detailed SLA compliance reporting: deadline vs. reached, exceeded hours, fail/success rates |
| Helpdesk > Reporting > Customer Ratings | Customer Ratings | Rating analysis across teams and agents (visible when ratings enabled) |
| Helpdesk > Configuration > Helpdesk Teams | Helpdesk Teams | Team setup: members, stages, assignment method, email alias, feature toggles |
| Helpdesk > Configuration > Stages | Stages | Pipeline stages shared across teams (developer mode) |
| Helpdesk > Configuration > SLA Policies | SLA Policies | Define SLA rules: target stage, time limit, priority/tag/customer filters, excluded stages |
| Helpdesk > Configuration > Tags | Tags | Ticket classification tags (developer mode) |
| Helpdesk > Configuration > Canned Responses | Canned Responses | Predefined reply templates for quick ticket responses |
| Helpdesk > Configuration > Activity Types | Activity Types | Custom activity types for ticket follow-ups (developer mode) |

### Settings & Feature Flags

Settings are configured per-team on the Helpdesk Team form, not via a central settings page. Each toggle may auto-install a companion module.

| Setting | Technical Field | What it Enables |
|---|---|---|
| Automatic Assignment | `auto_assignment` | Auto-assigns new tickets to team members based on chosen method |
| Assignment Method: Random | `assign_method = 'randomly'` | Equal distribution of tickets across team members |
| Assignment Method: Balanced | `assign_method = 'balanced'` | Assigns to member with fewest open tickets |
| Assignment Method: Tags | `assign_method = 'tags'` | Dispatches tickets to specific members based on tag-to-user mapping |
| SLA Policies | `use_sla` | Enables SLA deadline tracking, status computation, and SLA reports |
| Customer Ratings | `use_rating` | Sends satisfaction surveys when tickets are closed; adds rating report |
| Automatic Closing | `auto_close_ticket` | Auto-closes tickets inactive for N days by moving them to a target stage |
| Closure by Customers | `allow_portal_ticket_closing` | Lets portal users close their own tickets |
| Website Form | `use_website_helpdesk_form` | Adds a public ticket submission form (installs `website_helpdesk`) |
| Live Chat | `use_website_helpdesk_livechat` | Creates tickets from live chat conversations (installs `website_helpdesk_livechat`) |
| Community Forum | `use_website_helpdesk_forum` | Links helpdesk to a forum for community support (installs `website_helpdesk_forum`) |
| eLearning | `use_website_helpdesk_slides` | Links helpdesk to eLearning courses (installs `website_helpdesk_slides`) |
| Knowledge | `use_website_helpdesk_knowledge` | Links helpdesk to Knowledge base articles (installs `website_helpdesk_knowledge`) |
| Timesheets | `use_helpdesk_timesheet` | Log time on tickets (installs `helpdesk_timesheet`) |
| Time Billing | `use_helpdesk_sale_timesheet` | Bill timesheet hours to customers (installs `helpdesk_sale_timesheet`) |
| Refunds | `use_credit_notes` | Create credit notes from tickets (installs `helpdesk_account`) |
| Returns | `use_product_returns` | Process product returns from tickets (installs `helpdesk_stock`) |
| Replacements | `use_product_replacements` | Send replacement products from tickets (installs `helpdesk_stock`) |
| Repairs | `use_product_repairs` | Create repair orders from tickets (installs `helpdesk_repair`) |
| Coupons | `use_coupons` | Generate discount coupons from tickets (installs `helpdesk_sale_loyalty`) |
| Gift Cards | `use_giftcards` | Generate gift cards from tickets (installs `helpdesk_sale_loyalty`) |
| Field Service | `use_fsm` | Create field service tasks from tickets (installs `helpdesk_fsm`) |
| X (Twitter) | `use_twitter` | Create tickets from X/Twitter messages |
| Visibility | `privacy_visibility` | Controls access: private (invited), company-wide, or portal (public) |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `helpdesk.ticket` | Primary | Support tickets with subject, customer, priority, SLA tracking, assignment | Yes |
| `helpdesk.team` | Configuration | Support teams with members, pipeline stages, feature flags, assignment rules | Yes |
| `helpdesk.stage` | Configuration | Pipeline stages (New, In Progress, Solved, Cancelled) shared across teams | Yes |
| `helpdesk.sla` | Configuration | SLA policies with target stage, time limit, priority/tag/customer criteria | Yes |
| `helpdesk.sla.status` | Transactional | Per-ticket SLA tracking: deadline, reached date, exceeded hours, status (ongoing/reached/failed) | Yes (embedded in ticket) |
| `helpdesk.tag` | Configuration | Classification tags for tickets | Yes |
| `helpdesk.tag.assignment` | Configuration | Maps tags to specific team members for tag-based auto-assignment | Yes (embedded in team) |
| `helpdesk.ticket.report.analysis` | Reporting | SQL view for ticket analysis: time metrics, ratings, SLA success | Yes (pivot/graph) |
| `helpdesk.sla.report.analysis` | Reporting | SQL view for SLA status analysis: per-SLA-policy compliance metrics | Yes (pivot/graph) |

### Reports & Analytics

- **Tickets Analysis** (`helpdesk.ticket.report.analysis`): SQL-based pivot/graph view with measures for working hours to close, hours to assign, hours to first response, average response hours, SLA deadline hours, rating values. Supports cohort view for retention analysis.
- **SLA Status Analysis** (`helpdesk.sla.report.analysis`): Per-SLA-policy breakdown showing fail/success/ongoing counts, exceeded hours, deadline compliance. Filterable by team, agent, priority, tags.
- **Customer Ratings**: Rating analysis view showing satisfaction scores (1-5 scale) per agent and team, with feedback comments.
- **Team Dashboard**: Kanban dashboard with KPIs per team: open tickets, urgent count, SLA failure count, success rate percentage, tickets closed in last 7 days.

### Wizards & Advanced Actions

| Wizard | Model | Purpose |
|---|---|---|
| Stage Delete/Archive | `helpdesk.stage.delete.wizard` | Safely delete or archive stages by handling tickets in those stages (archive tickets or move them). Handles multi-team stage sharing. |
| Portal Share | `portal.share` (extended) | Share tickets with portal users; automatically subscribes shared partners as followers. |

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `website_helpdesk` | enterprise | Public ticket submission form on the website |
| `website_helpdesk_livechat` | enterprise | Create tickets from live chat conversations |
| `website_helpdesk_forum` | enterprise | Link helpdesk to community forum for self-service |
| `website_helpdesk_slides` | enterprise | Link helpdesk to eLearning courses |
| `website_helpdesk_knowledge` | enterprise | Link helpdesk to Knowledge base articles |
| `helpdesk_timesheet` | enterprise | Log work hours on tickets |
| `helpdesk_sale_timesheet` | enterprise | Bill logged timesheet hours to customers |
| `helpdesk_account` | enterprise | Create credit notes/refunds from tickets |
| `helpdesk_stock` | enterprise | Process product returns and replacements from tickets |
| `helpdesk_repair` | enterprise | Create repair orders from tickets |
| `helpdesk_sale_loyalty` | enterprise | Generate coupons and gift cards from tickets |
| `helpdesk_fsm` | enterprise | Create field service tasks from tickets |
| `crm_helpdesk` | enterprise | Convert tickets to/from CRM leads |
| `helpdesk_sale` | enterprise | After-sales features: link tickets to sales orders, projects, tasks |
| `helpdesk_sms` | enterprise | Send SMS notifications on ticket stage changes |
| `helpdesk_holidays` | enterprise | Integration with time-off for assignment availability |
| `helpdesk_mail_plugin` | enterprise | Convert emails to tickets from mail client plugins |
| `project_helpdesk` | enterprise | Create project tasks from tickets |
| `data_merge_helpdesk` | enterprise | Merge duplicate tickets via data cleaning |
| `spreadsheet_dashboard_helpdesk` | enterprise | Pre-built spreadsheet dashboards for helpdesk KPIs |

## Demo Highlights

1. **SLA Policy Tracking with Freeze Stages** -- Define SLAs like "8 hours to resolve for urgent ice-cream-machine tickets." Exclude "Waiting for Parts" as a freeze stage so the clock stops while parts are on order. The live SLA countdown on each ticket is visually compelling.

2. **Tag-Based Auto-Assignment** -- Configure tags like "Maquina de Helado," "Sistema de Pago," "Refrigeracion" and map each to the right technician. New tickets are automatically routed to the specialist, showcasing operational efficiency for Percimon's multi-store support.

3. **Team Dashboard with KPIs** -- The overview screen shows each support team's open tickets, urgent count, SLA success rate, and closed tickets at a glance. For a chain with multiple stores, this gives operations managers immediate visibility into support performance.

4. **Customer Ratings on Resolved Tickets** -- After an internal store manager submits a ticket about a broken machine, they rate the resolution. This creates accountability for the maintenance/IT team and feeds into a satisfaction report.

5. **Automatic Ticket Closing** -- Tickets inactive for N days auto-move to "Solved" or "Cancelled." Prevents ticket backlog buildup across stores, keeping the pipeline clean without manual intervention.
