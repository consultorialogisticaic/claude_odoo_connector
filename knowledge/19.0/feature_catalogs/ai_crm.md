# Feature Catalog — AI CRM (ai_crm + ai_crm_livechat) — Sub-catalog

Sub-catalog — AI-powered lead qualification and livechat-to-lead flows introduced in 19.0.

**Version:** 19.0
**Source:** enterprise
**Category:** Hidden (auto-installed bridge)
**Dependencies:**
- `ai_crm` → `ai_app`, `crm`
- `ai_crm_livechat` → `ai_crm`, `ai_livechat` (transitively pulls `im_livechat`)

Both modules are `auto_install=True`: they activate automatically when their dependency set is present (AI app + CRM for `ai_crm`; AI app + CRM + Livechat for `ai_crm_livechat`). They contain no menus of their own — the user-facing surface is the existing CRM and AI Agent views, extended with AI tools and a livechat-origin link on leads.

## Business Capabilities

- **Conversational lead capture:** An AI agent (LLM-backed, default `gpt-4o`) can collect a prospect's name, email, phone, job position, and address through natural conversation and register a qualified `crm.lead` with the right team, tags, and priority — no form-filling by the prospect.
- **Tool-calling CRM integration:** Ships two `ir.actions.server` tools exposed to the AI runtime (`use_in_ai=True`): one to enumerate available CRM teams/tags/priorities/countries/states, and one to actually create the lead. The agent discovers the tenant's taxonomy at runtime instead of relying on hardcoded values.
- **Website livechat → CRM pipeline:** When the Odoo Livechat widget routes a visitor to an AI agent, unresolved or escalation-worthy conversations become `crm.lead` records linked back to the originating `discuss.channel` and (when `website` is installed) to the `website.visitor` — so salespeople see the full chat transcript behind every AI-generated lead.
- **Per-agent lead attribution via UTM:** Each `ai.agent` gets its own `utm.source` (via the `utm.source.mixin`), and every lead it creates is stamped with `source_id = <agent's source>` and `medium_id = "Website"`. This gives out-of-the-box UTM reporting on which AI agent generated which pipeline.
- **Operator-visible AI productivity:** The AI Agent form shows a "Leads" smart button with a live count of leads the agent has created, drilling into a pre-filtered `crm.lead` view (kanban/list/graph/pivot/form/calendar/activity).

## Feature Inventory

### Menu Structure

Neither module adds menu entries. All user-facing surface is grafted onto existing menus:

| Menu Path (host app) | Surface Added By | Description |
|---|---|---|
| AI > Agents > _(form)_ | `ai_crm_livechat` | "Leads" smart button on the `ai.agent` form shows count of leads this agent has generated and opens a filtered `crm.lead` view (source: `enterprise/ai_crm_livechat/views/ai_agent_views.xml`). |
| AI > Agents > Livechat Agent | `ai_crm_livechat` | Default livechat agent (`ai_livechat.ai_agent_livechat`) is auto-configured with system prompt + "Create Leads" topic so it can qualify leads out-of-the-box (source: `enterprise/ai_crm_livechat/data/ai_agent.xml`). |
| CRM > Pipeline > _(lead form)_ | `ai_crm` / `ai_crm_livechat` | Leads created by AI carry `source_id` of the agent and (from livechat) `origin_channel_id` + `visitor_ids`, reusing existing CRM fields/widgets. |

### Settings & Feature Flags

Neither module exposes `res.config.settings` toggles. Activation is implicit:

| Condition | Effect |
|---|---|
| Install `ai_app` + `crm` | `ai_crm` auto-installs, registers the two AI tools and the "Create Leads" topic. |
| Install `ai_app` + `crm` + `im_livechat` | `ai_crm_livechat` auto-installs, extends the livechat AI agent with the lead topic and adds livechat-origin tracking on leads. |
| Install `website` alongside the above | Livechat-sourced leads additionally capture the `website.visitor` via `visitor_ids` (handled by a soft runtime check in `_ai_prepare_lead_creation_values`, no explicit bridge module). |

Per-channel wiring lives on `im_livechat.channel.rule` (provided by the upstream `ai_livechat` module) — that is where an operator picks which `ai.agent` handles which URL/country pattern.

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `ai.agent` (extended by `ai_crm`) | Configuration | Inherits `utm.source.mixin`; `_auto_init` backfills a `utm.source` record for every existing agent so leads can be attributed by agent via UTM. (source: `enterprise/ai_crm/models/ai_agent.py`) | Yes (AI app form) |
| `ai.agent` (extended by `ai_crm_livechat`) | Configuration | Adds computed `created_leads_count` (read_group over `crm.lead` by `source_id`) and `action_view_leads()` returning a pre-filtered CRM action. (source: `enterprise/ai_crm_livechat/models/ai_agent.py`) | Yes (smart button on form) |
| `crm.lead` (extended by `ai_crm`) | Primary | Adds three `@api.model` helpers consumed by the AI tools: `_ai_create_lead(...)`, `_ai_get_lead_create_available_params(country_code)`, `_ai_prepare_lead_creation_values(vals)`. Handles both public-user (email_from / address on lead) and internal-user (partner backfill) cases. (source: `enterprise/ai_crm/models/crm_lead.py`) | Yes (standard lead form) |
| `crm.lead` (extended by `ai_crm_livechat`) | Primary | Overrides `_ai_prepare_lead_creation_values` to set `origin_channel_id` from `self.env.context['discuss_channel']` and, if `website` is installed, links the livechat visitor via `visitor_ids`. (source: `enterprise/ai_crm_livechat/models/crm_lead.py`) | Yes (origin section + chatter on lead) |
| `ai.topic` record `ai_crm.ai_topic_create_lead` | Configuration | "Create Leads" topic bundling the two server-action tools with a detailed natural-language playbook for the LLM (when to trigger, how to collect name/email/phone, single-call constraint, HTML description rules). (source: `enterprise/ai_crm/data/ai_topic.xml`) | Yes (AI > Topics) |
| `ir.actions.server` `ir_actions_server_ai_create_lead` | Configuration | Tool record: `use_in_ai=True`, JSON schema for the LLM, `code` body calls `record.sudo()._ai_create_lead(...)` on `crm.lead`. (source: `enterprise/ai_crm/data/ir_actions_server_tools.xml`) | Yes (AI > Tools) |
| `ir.actions.server` `ir_actions_server_ai_get_lead_create_available_params` | Configuration | Tool record returning teams/tags/priorities/country+states as `{id: display_name}` JSON for the LLM to choose from before creating a lead. (source: `enterprise/ai_crm/data/ir_actions_server_tools.xml`) | Yes (AI > Tools) |
| `discuss.channel` (behavior extended by `ai_crm_livechat`) | Transactional | Controller override ensures livechat channels that produced a lead (`has_crm_lead`) are **not** unlinked on close — so the operator can always re-read the transcript. (source: `enterprise/ai_crm_livechat/controllers/main.py`) | Yes (chatter + lead drill-down) |

No new ORM model is created by either module — both are pure behavior/data bridges.

### Reports & Analytics

No dedicated report views. Analytics are inherited:
- **Leads by source (UTM):** Because each `ai.agent` has a `utm.source` and every AI-created lead has `source_id` set, the standard CRM pivot/graph over `crm.lead` already slices pipeline by agent.
- **Per-agent lead count:** The `created_leads_count` computed field on `ai.agent` (from `ai_crm_livechat`) is rendered as a smart button and can be added to kanban/list views.
- **Lead → chat transcript trail:** Leads from livechat keep `origin_channel_id` pointing at the `discuss.channel`, so the standard Discuss thread acts as the analytics of the conversation.

### Wizards & Advanced Actions

No `TransientModel` wizards. The two exposed actions are AI-runtime tools, not user wizards:

| Action | Model | Purpose |
|---|---|---|
| `AI CRM: Create Lead` (`ir_actions_server_ai_create_lead`) | `crm.lead` | Called by the LLM with a structured JSON payload (name, contact_name, description, email, phone, team_id, tag_ids, priority, optional country_id/state_id/city/zip/street/job_position). `ai_tool_allow_end_message=True` lets the agent follow with a closing message. Description is `html_sanitize`-wrapped before persistence. |
| `AI CRM: Get Lead creation available parameters` (`ir_actions_server_ai_get_lead_create_available_params`) | `crm.lead` | Called by the LLM **immediately before** `Create Lead` to fetch the tenant's CRM teams, tags, priorities, and — if a country code was inferred — the matching country and its states, all returned as `{id: display_name}` JSON. |

Behavioral guardrails (from `ai_topic.xml`):
- The LLM is instructed to call the lead-creation tool **at most once per conversation**.
- It must not reveal internal tool/system names, must collect name/email/phone one-by-one, must validate email format, must produce the lead description as valid HTML in `<p>` tags, and must include the rationale for chosen `tag_ids` inside the description.
- If the caller is the public user, the collected address/email/phone are written onto the lead (`email_from`, `street`, `city`, …); if an internal user, the code backfills the missing fields on their `res.partner` instead — address only when the partner currently has none.

### Companion Modules

| Module | Source | Features Added / Role |
|---|---|---|
| `ai_app` | enterprise | Parent: provides `ai.agent`, `ai.topic`, `ai.composer`, `use_in_ai`/`ai_tool_schema`/`ai_tool_description` fields on `ir.actions.server`, LLM routing, AI menus. `ai_crm` is a functional bridge on top of it. |
| `crm` | community | Source of `crm.lead`, `crm.team`, `crm.tag`, priority selection — the target of every AI-created record. |
| `ai` | enterprise | Low-level AI runtime (used via `ai_app`) — provides `AIController` which `ai_crm_livechat` extends to keep lead-producing channels alive. |
| `ai_livechat` | enterprise | Pulls `im_livechat` into the AI world, defines `ai_livechat.ai_agent_livechat` (the default livechat agent record). `ai_crm_livechat` binds the "Create Leads" topic to that agent. |
| `im_livechat` | community | Source of `discuss.channel` (channel_type `livechat`), `livechat_visitor_id`, `im_livechat.channel.rule`. |
| `website` | community | Optional: when present, the livechat bridge also links `website.visitor` to the created lead via `visitor_ids`. Detected at runtime, no hard dependency. |
| `utm` | community | Provides `utm.source.mixin` and `utm.utm_medium_website` — every AI-created lead ends up with `source_id = agent's utm.source` and `medium_id = Website`. |

No other enterprise module in the workspace depends on `ai_crm` or `ai_crm_livechat` — they sit at the leaves of the dependency tree.

## Demo Highlights

1. **Zero-touch livechat lead qualification** — Drop the Odoo Livechat widget on a public website, point its channel rule at the default AI Livechat agent, and watch the LLM triage visitors: answers simple questions from knowledge, and when it can't, collects name/email/phone conversationally and creates a `crm.lead`. A compelling 30-second demo for any inbound-marketing audience.
2. **"Leads" smart button on the AI agent** — The same agent form now shows, at a glance, how many opportunities it has sourced. One click pivots to a CRM view of those leads. Great for proving AI ROI to a skeptical sales director.
3. **LLM respects the tenant's CRM taxonomy** — Because the `Get Lead creation available parameters` tool returns the real teams, tags, priorities, and country/state IDs, the AI assigns leads to the right team and tags them meaningfully — not to a hardcoded "AI Leads" bucket. This is what separates a toy demo from a production-grade workflow.
4. **Full chat transcript attached to every AI-generated lead** — The lead's `origin_channel_id` keeps the full `discuss.channel` alive (the `_should_unlink_on_close` override guarantees it), so salespeople see exactly what the prospect said before calling back. Closes the "AI black box" objection in one click.
5. **UTM attribution by AI agent, out of the box** — Because each `ai.agent` gets its own `utm.source`, standard CRM pivot/graph by source instantly becomes a per-agent performance dashboard. No custom reporting needed to answer "which of my AI agents is the best SDR?".
