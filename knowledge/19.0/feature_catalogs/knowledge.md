# Feature Catalog: Knowledge (Enterprise)

**Module:** `knowledge`
**Version:** 19.0 | **Category:** Productivity/Knowledge
**License:** OEEL-1 (Enterprise)
**Dependencies:** `web`, `digest`, `html_editor`, `mail`, `portal`, `web_unsplash`, `web_hierarchy`

---

## 1. Menu Structure

| Menu Path | Action / Model | Access Groups |
|---|---|---|
| Knowledge | Root menu | All internal users |
| Knowledge > Home | `ir_actions_server_knowledge_home_page` | All |
| Knowledge > Articles | `knowledge.article` (list/kanban/form) | All |
| Knowledge > Configuration > Members | `knowledge.article.member` | `base.group_system` (debug mode) |
| Knowledge > Configuration > Favorites | `knowledge.article.favorite` | `base.group_system` (debug mode) |
| Knowledge > Configuration > Trashed | `knowledge.article` (trashed filter) | `base.group_system` (debug mode) |
| Knowledge > Configuration > Stages | `knowledge.article.stage` | Debug mode |
| Settings > Technical > Knowledge > Templates | `knowledge.article` (templates) | `base.group_system` |
| Settings > Technical > Knowledge > Template Categories | `knowledge.article.template.category` | `base.group_system` |
| Settings > Technical > Knowledge > Template Stages | `knowledge.article.stage` (templates) | `base.group_system` |

---

## 2. Settings

Knowledge has **no dedicated Settings page** under res.config.settings. Configuration is done directly inside articles (permissions, members, stages) and via the Configuration menu in debug mode.

---

## 3. Key Models

| Model | Description | Key Fields |
|---|---|---|
| `knowledge.article` | Core content entity: article with HTML body, hierarchy, permissions | `name`, `body`, `icon`, `parent_id`, `internal_permission`, `category` (workspace/private/shared), `is_article_item`, `stage_id`, `is_locked`, `full_width`, `cover_image_id`, `article_properties_definition`, `article_properties`, `is_template` |
| `knowledge.article.member` | Per-article access grants | `article_id`, `partner_id`, `permission` (write/read/none) |
| `knowledge.article.favorite` | User-specific bookmarks | `article_id`, `user_id`, `sequence` |
| `knowledge.article.stage` | Kanban stages for article items (per parent) | `name`, `sequence`, `fold`, `parent_id` |
| `knowledge.article.template.category` | Groups built-in templates (Productivity, Sales, etc.) | `name`, `sequence` |
| `knowledge.cover` | Cover image catalog for articles | `attachment_url` |
| `knowledge.article.thread` | Comment threads on articles | (inherits mail.thread) |

### Hierarchy & Items
- Articles support **parent/child hierarchy** (`parent_id`, `child_ids`, `parent_path`).
- **Article Items** (`is_article_item=True`) are lightweight child records that can be displayed as embedded Kanban/List views inside the parent article body.
- Items use **Stages** scoped to the parent article (`knowledge.article.stage.parent_id`).
- **Properties** (`article_properties_definition` on parent, `article_properties` on items) allow custom typed fields (date, selection, tags) on article items without code.

### Permissions Model
- **Internal Permission** on root articles: `write` / `read` / `none` (members only).
- Permission **inherits down** the hierarchy (computed `inherited_permission`).
- **Members** override inherited permission per partner.
- **Categories** are computed: `workspace` (all can access), `private` (only creator), `shared` (mixed members).
- `is_desynchronized` breaks inheritance for a sub-article.

---

## 4. Views

| View Type | Key Features |
|---|---|
| **Form** (custom JS: `knowledge_article_view_form`) | Full-page rich text editor; top bar with sharing, favoriting, locking; embedded item views (Kanban/List); cover image; property fields on items |
| **List** | Standard article list with title, category, last edition |
| **Kanban** | Card view for articles |
| **Hierarchy** | Tree visualization of article parent/child structure (lazy-loaded) |
| **Portal** | Public/portal read-only view of shared articles |

---

## 5. Reports

Knowledge has **no printable QWeb reports**. The module provides a **print stylesheet** (`knowledge_print.scss`) for browser-based article printing.

---

## 6. Wizards

| Wizard | Model | Purpose |
|---|---|---|
| **Invite Members** | `knowledge.invite` | Invite partners to an article with a specific permission level and optional message. Fields: `article_id`, `partner_ids`, `permission`, `message`. |

---

## 7. Built-in Article Templates

Pre-loaded template articles grouped by category:

| Category | Template Examples |
|---|---|
| Productivity | Shared To-Do List (with embedded item Kanban, priority/tags properties) |
| Sales | Product Catalog |
| Marketing | (various) |
| Company Organization | (various) |
| Product Management | (various) |

Templates are applied via `knowledge.article.apply_template()` method.

---

## 8. Demo Data

File: `demo/knowledge_article_demo.xml`

- Creates one demo article (`knowledge_demo_article`) with `internal_permission=none` (members only).
- Adds `partner_admin` and `partner_demo_portal` as write members.
- Applies the **Product Catalog** template to it.

**Minimal demo** -- for Percimon, custom articles will need to be created via the UI or data loading.

---

## 9. Companion Modules

| Module | Source | Purpose |
|---|---|---|
| `website_knowledge` | Enterprise | Publish knowledge articles on the website |
| `website_helpdesk_knowledge` | Enterprise | Link knowledge articles to helpdesk tickets |
| `accountant_knowledge` | Enterprise | Accounting-specific knowledge templates |
| `ai_knowledge` | Enterprise | AI-assisted article writing/completion |

---

## 10. Percimon Relevance

For a Colombian frozen yogurt chain, Knowledge is ideal for:

- **SOPs (Standard Operating Procedures):** Opening/closing checklists, food handling protocols, equipment maintenance steps. Use parent article "SOPs" with child article items as checklist steps, tracked via Kanban stages (Draft > Review > Approved).
- **Recipes:** Yogurt base recipes, topping prep instructions, seasonal specials. Rich HTML body supports images, tables, embedded videos.
- **BPM / Cleaning Protocols:** Daily, weekly, and monthly cleaning schedules. Use article items with date properties for tracking.
- **Demo Instructions:** Training articles for new staff on how to demo products to customers, use the POS, etc.
- **Workspace Organization:** Top-level workspace articles per store location or per department (Kitchen, Front-of-House, Management).
- **Permission Tiers:** Managers get write access to SOPs; staff get read-only. Use `internal_permission=read` on root with manager members set to `write`.

### Key models for demo data
- `knowledge.article` -- the articles themselves (loaded via RPC, not CSV, due to HTML body field)
- `knowledge.article.member` -- access grants
- `knowledge.article.stage` -- Kanban stages for item tracking
