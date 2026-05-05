# Feature Catalog — Documents for Project (documents_project + _sale + _sign) — Sub-catalog

Sub-catalog — Integrates `documents` with `project`: attach documents to tasks/projects, workflow automations, signing integrations. See `project.md` for mainline.

**Version:** 19.0
**Source:** enterprise
**Category:** Productivity/Documents
**Dependencies (aggregated):** `documents`, `project`, `sale_project` (via `documents_project_sale`), `documents_sign` (via `documents_project_sign`)

## Business Capabilities

- **Per-project document folders:** Every `project.project` automatically gets a dedicated `documents.document` folder under the company's root "Projects" folder, so all files, meeting notes, and plans for the project land in a predictable, permissioned workspace.
- **Attachments funnelled to the right folder:** When users drop files on a project or a task (via the standard chatter/attachment UI), the `ir.attachment` bridge routes them to the project's documents folder as the default "add to Documents" destination, eliminating the decision of where to file them.
- **Service-product folder templates (sale bridge):** In `documents_project_sale`, a service product configured with `service_tracking='project_only'` and a `project_template_id` becomes a folder-template product — confirming a sale order clones the template project *and* its documents folder structure (Plans, Photos, Miscellaneous, …) for the customer.
- **Signature workflows on project documents:** `documents_project_sign` exposes the "Create a Signature Template" server action directly on the Projects root folder, so any document filed there can be turned into a Sign template and dispatched for signature without leaving the Documents app.
- **Portal document sharing for service projects:** The sale demo wires a `portal` `privacy_visibility` project with a customer as follower and a seeded Plans/Photos subfolder structure, so the end customer sees the project's documents in their portal — the flagship "architect sharing renovation plans" scenario.

## Feature Inventory

### Menu Structure

These modules add no top-level menus. Features appear as: (1) a "Documents" embedded action on the project form/dashboard, (2) a "Documents" entry in the project kanban card menu, (3) a setting in the `documents` settings page, and (4) server actions attached to folders.

| Menu Path | Feature | Description |
|---|---|---|
| Project > (project form) > Settings tab | Documents Folder | Picks the `documents.document` folder that backs this project; defaulted per company and auto-created on project create |
| Project > (project form) > Embedded action bar | Documents | Opens the project's documents folder directly (kanban/list), scoped via `searchpanel_default_user_folder_id` |
| Project > Project Updates > Embedded action bar | Documents | Same documents view, reachable from the Project Updates dashboard |
| Project > Kanban > (card three-dot menu) | Documents | Card-level shortcut to `action_view_documents_project`, hidden when the user has no permission on the folder |
| Settings > Documents > Centralized Files | Default Project Folder | Selects the company-level `documents_project_folder_id`; children of this folder are where new projects' folders are created |
| Documents > (any folder, actions menu) | Create a Signature Template (via `documents_project_sign`) | Embedded on the `document_project_folder` root so sign-template creation is available on project-filed documents |

Source: `enterprise/documents_project/views/project_views.xml`, `enterprise/documents_project/views/res_config_settings.xml`, `enterprise/documents_project_sign/data/ir_actions_server_data.xml`.

### Settings & Feature Flags

| Setting | Technical Field | What it Enables |
|---|---|---|
| Default Project Folder | `res.company.documents_project_folder_id` (related on `res.config.settings.documents_project_folder_id`) | Per-company root folder under which each project's auto-created folder is nested; must be a real folder (no shortcut) with matching company |
| Project → Documents Folder | `project.project.documents_folder_id` | Picks/overrides the backing folder for a specific project; domain forces `type='folder'` and `shortcut_document_id=False`; uses the `documents_folder_many2one` widget with `documents_project` context |

There are no `res.config.settings` toggles that install companion modules — `documents_project`, `documents_project_sale`, and `documents_project_sign` are all `auto_install=True` and activate automatically when their dependencies are present.

Source: `enterprise/documents_project/models/res_company.py`, `enterprise/documents_project/models/res_config_settings.py`, `enterprise/documents_project/models/project_project.py` (`documents_folder_id`), `enterprise/documents_project/views/res_config_settings.xml`.

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `documents.document` (extended) | Primary | Adds `project_ids` (One2many reverse of `project.project.documents_folder_id`); protects the "Projects" root folder from deletion/archiving; constrains company consistency between a folder and its linked projects; propagates partner from the closest ancestor project when a document is filed | Yes (Documents app) |
| `project.project` (extended) | Primary | Adds `documents_folder_id` (Many2one to the backing folder), computed `document_ids` / `document_count` (binary+url docs that are descendants of the folder), and a "Documents" stat-button entry via `_get_stat_buttons` | Yes (Project app) |
| `project.task` | Primary | No field additions, but attachments uploaded against a task resolve to the parent project's documents folder as the "add to Documents" destination (see `ir.attachment` below) | Yes (consumed indirectly) |
| `ir.attachment` (extended) | Configuration | Overrides `get_documents_operation_add_destination` so attachments on `project.project` or `project.task` default to the project's `documents_folder_id` when surfaced in the Documents "Add" UI | No (internal bridge) |
| `documents.tag` (extended) | Configuration | `_ensure_documents_project_tags_exist` seeds the shared workflow tags (Draft, To validate, Validated, Deprecated) with stable xmlids so project folders can use a consistent validation workflow | Yes (via tags) |
| `res.company` (extended) | Configuration | Adds `documents_project_folder_id`, defaulted to the xmlid `documents_project.document_project_folder`; company-folder mismatch is enforced by constraint | Yes (Settings) |
| `res.config.settings` (extended) | Configuration | Surfaces `documents_project_folder_id` as a company-dependent setting in the Documents settings page | Yes |

No new models are defined by `documents_project_sale` or `documents_project_sign` — both modules are pure data/wiring layers (demo records, an embedded action, and the `_data_embed_if_records_exist` hook that exposes the Sign server action on the Projects folder).

Source: `enterprise/documents_project/models/documents_document.py`, `enterprise/documents_project/models/project_project.py`, `enterprise/documents_project/models/ir_attachment.py`, `enterprise/documents_project/models/documents_tag.py`, `enterprise/documents_project/models/res_company.py`, `enterprise/documents_project/models/res_config_settings.py`.

### Reports & Analytics

No new reports, pivot/graph views, or dashboards are introduced. The integration surfaces existing Documents-app views (kanban + list of `documents.document`) filtered to the project's folder via `action_view_documents_project` on `project.project`, and adds a "Documents" stat button with the live `document_count` on the project form.

### Wizards & Advanced Actions

| Wizard / Action | Model | Purpose |
|---|---|---|
| `action_view_documents_project` | `project.project` (method) | Opens `documents.document_action_preference` scoped to the project's folder, seeding `active_id`/`active_model` and `searchpanel_default_user_folder_id` so the Documents app lands inside that project's workspace |
| `project_embedded_action_documents` | `ir.embedded.actions` on `project.project` | Embeds "Documents" in the Project → Tasks action bar (sequence 40) |
| `project_embedded_action_documents_dashboard` | `ir.embedded.actions` on `project.project` | Embeds "Documents" in the Project Updates dashboard action bar |
| `_create_missing_folders` | `project.project` (method) | Idempotently creates a `documents.document` folder for any project missing one, mirroring the project's `company_id`, copying privacy (`edit` for employees/portal, else `none`), and parenting it under the company's `documents_project_folder_id`. Called from `create`, `write`, the post-init hook, and the demo bootstrap |
| Post-init hook `_documents_project_post_init` | Module (Python) | On install: fills `documents_project_folder_id` on any company missing one, then back-fills folders for every existing project |
| Create a Signature Template (embedded) | `ir.actions.server` ref `documents_sign.ir_actions_server_create_sign_template_direct` | `documents_project_sign` calls `_data_embed_if_records_exist` to attach this existing server action to the `document_project_folder`, making "Create Sign Template" a one-click action on any document filed in the Projects folder tree |

Copy/rename behaviour is also worth noting as an advanced action: renaming a project with exactly one linked folder renames the folder too (sudo-bypasses access); copying a project clones the folder (respecting the `no_create_folder` context flag); unlinking all projects pointing at a folder archives that folder. Source: `enterprise/documents_project/models/project_project.py` (`write`, `copy`, `_archive_folder_on_projects_unlinked`), `enterprise/documents_project/models/documents_document.py` (`unlink_except_project_folder`).

### Feature Inventory by Module

#### `documents_project` (base bridge)

- Defines the `Projects` root folder (`document_project_folder`) protected from deletion and archiving, with `access_internal='view'` / `access_via_link='view'`, and pins it to `res.company.documents_project_folder_id` for `base.main_company` via `data/res_company_data.xml`.
- Adds `documents_folder_id` + `document_count` + `document_ids` to `project.project`, auto-creates a folder on project creation, and keeps folder name in sync with project name when the folder has a single owning project.
- Embeds the Documents view twice on `project.project` (tasks action bar and project-update dashboard) and adds a kanban-card menu item, all gated on `documents_folder_id.user_permission != 'none'`.
- Bridges `ir.attachment.get_documents_operation_add_destination` for `project.project` and `project.task` so the Documents "Add" UI defaults to the project folder.
- Seeds the shared workflow tags (Draft / To validate / Validated / Deprecated) via `DocumentsTag._ensure_documents_project_tags_exist`.
- Company-level safety: constrains folder/project company alignment both on `project.project` and on `documents.document` (refusing to move a folder into a company other than its linked projects').
- Post-init hook back-fills missing folders on existing companies and projects.

Source: `enterprise/documents_project/__manifest__.py`, `enterprise/documents_project/__init__.py`, `enterprise/documents_project/models/*.py`, `enterprise/documents_project/views/*.xml`, `enterprise/documents_project/data/documents_document_data.xml`, `enterprise/documents_project/data/res_company_data.xml`.

#### `documents_project_sale` (service-product folder templates + portal)

- Pure data/demo add-on (no Python models). Depends on `documents_project` and `sale_project`, so the features it *demonstrates* are: a service product (`service_tracking='project_only'`) with `project_template_id` pointing at a project that has a populated `documents_folder_id` — confirming a sale order cloning the template project and its folder tree.
- Demo data defines a `Renovation Projects` folder with three child folders (`Plans`, `Photos`, `Miscellaneous`) and three tag statuses (`New/Unsorted`, `In Use`, `Done/Archived`), then wires a `Renovation Architect` project with `privacy_visibility='portal'`, a portal partner follower, and demo documents (`plan.jpg`, `welcome.jpg`) — the canonical portal-sharing scenario.
- Seeds an embedded-action visibility/order record on `admin`'s `res.users.settings` so the project form shows Sales Orders → Invoices → Documents → Project Updates in that order, demonstrating Documents as a first-class tab for a customer-facing sale-driven project.
- Confirms the demo sale order to materialize the end-to-end flow (template product → confirmed SO → project + folder tree created).

Source: `enterprise/documents_project_sale/__manifest__.py`, `enterprise/documents_project_sale/data/documents_demo.xml`, `enterprise/documents_project_sale/data/project_sale_demo.xml`, `enterprise/documents_project_sale/data/res_users_settings_embedded_action_demo.xml`.

#### `documents_project_sign` (signature action on project folder)

- Pure data add-on (no Python models, no views). A single XML file calls `documents.document._data_embed_if_records_exist` with the `documents_project.document_project_folder` and `documents_sign.ir_actions_server_create_sign_template_direct` xmlids; when both exist, it invokes `action_folder_embed_action` on the Projects folder so "Create a Signature Template" appears as an embedded action on any document inside that folder tree.
- Practical effect: a user viewing a contract/plan filed under a project's folder can click the embedded action and jump straight into the Sign template editor, without navigating back to the Sign app.

Source: `enterprise/documents_project_sign/__manifest__.py`, `enterprise/documents_project_sign/data/ir_actions_server_data.xml`.

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `documents_project` | enterprise | Per-project `documents.document` folder with auto-creation, protected root folder, attachment-destination bridge, shared workflow tags, and company-consistency constraints |
| `documents_project_sale` | enterprise | Folder-template service products (via `sale_project`), portal-visible project document sharing demo, embedded-action ordering on project form |
| `documents_project_sign` | enterprise | Embeds the "Create a Signature Template" server action on the Projects root folder so documents filed under any project can be sent for signature in one click |

## Demo Highlights

1. **Renovation Architect — template project + folder tree from a sale order** — Configure a service product with `service_tracking='project_only'` and a template project that has a `Plans / Photos / Miscellaneous` folder tree. Confirming a sale order creates the real project *and* clones the folder tree, ready for the customer. This is the flagship `documents_project_sale` demo and maps cleanly to any professional-services client (architects, consultants, agencies).

2. **One-click Sign template from a project document** — With `documents_project_sign` installed, the "Create a Signature Template" action is embedded on the Projects folder. A project manager opens a contract PDF filed under the project, clicks the action, and is in the Sign template editor — no app switching. Great for onboarding/renovation contracts where each project generates a signature round.

3. **Portal-visible project documents** — The `Renovation Architect` demo sets `privacy_visibility='portal'` on the project, adds the customer as a follower, and exposes the folder. The customer sees, in the portal, the exact documents their architect has filed (plans, photos, meeting notes). High-impact for service firms that want a client-portal story without building anything custom.

4. **Attachment funnel: drop-a-file-anywhere → right folder** — Uploading an attachment on a project or task chatter surfaces the project's documents folder as the default "add to Documents" destination. Demonstrates operational tidiness: no more "where did that file go?" — the project is the single filing rule.

5. **Auto-created, rename-synced, archive-safe folders** — Creating a project silently creates its folder; renaming the project renames the folder (when it has a single owning project); unlinking all projects archives the folder; the Projects root folder and its ancestors are deletion-protected. A reassuring "it just works" story for non-technical project managers.
