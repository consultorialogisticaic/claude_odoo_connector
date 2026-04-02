# UI Report: knowledge.article

**Odoo Version:** 19.0
**Source:** `enterprise/knowledge/models/knowledge_article.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `knowledge.article` |
| `_description` | `Knowledge Article` |
| `_inherit` | `mail.thread`, `mail.activity.mixin`, `html.field.history.mixin` |
| `_rec_name` | `name` (default) |
| `_order` | `favorite_count desc, write_date desc, id desc` |
| `_parent_store` | `True` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | No | — | Title. Indexed (trigram). |
| `body` | Html | No | auto-generated `<h1>` | Prefetch=False (large field). Auto-set from `name` on create if not provided. |
| `icon` | Char | No | — | Emoji character. |
| `is_locked` | Boolean | No | `False` | Prevents body/title editing. |
| `full_width` | Boolean | No | `False` | |
| `internal_permission` | Selection | No* | — | `write`, `read`, `none`. *Required for root articles (no parent). |
| `parent_id` | Many2one → `knowledge.article` | No | — | Parent article. Hierarchical. ondelete=cascade. |
| `is_desynchronized` | Boolean | No | `False` | If True, stops inheriting parent permissions. Requires `internal_permission`. |
| `sequence` | Integer | No | 0 | Within same parent. Auto-set on create if not provided. |
| `is_article_item` | Boolean | No | `False` | Items must have a parent. |
| `category` | Selection | — | computed, stored | `workspace`, `private`, `shared`. Computed from permissions. |
| `is_article_visible_by_everyone` | Boolean | No | computed | |
| `article_member_ids` | One2many → `knowledge.article.member` | No | — | Copy=True. |

## SQL Constraints

- `_check_permission_on_root`: Root articles (no parent) MUST have `internal_permission`.
- `_check_permission_on_desync`: Desynchronized articles MUST have `internal_permission`.
- `_check_desync_on_root`: Root articles CANNOT be desynchronized.
- `_check_article_item_parent`: Article items MUST have a parent.
- `_check_trash`: Trashed articles must be archived.
- `_check_template_category_on_root`: Root templates must have a category.
- `_check_template_name_required`: Templates must have a template_name.

## Python Constraints

- `_check_is_writable`: Articles must always have at least one writer (either via `internal_permission=write` or a member with write access).
- `_check_parent_id_recursion`: No cycles in parent hierarchy.
- `_check_template_hierarchy`: Templates can only be children of templates; articles can only be children of articles.

## create() / write() Overrides

- **create()**: Complex logic:
  - Auto-sets `body` to `<h1>name</h1>` if not provided.
  - Sets `last_edition_date` and `last_edition_uid`.
  - Forces `internal_permission=write` for root articles without permission.
  - Auto-sequences articles to be last child of parent.
  - Supports sudo creation for private articles (non-admin users creating their own private articles).
  - Non-internal users can only create under existing parents or private articles.
- **write()**:
  - Templates can only be modified by system users.
  - Updates `last_edition_date`/`last_edition_uid` when body changes.
  - Moving under a new parent requires write access on the new parent.
  - Auto-resequences when parent changes.

## Demo Data Patterns

From `knowledge/demo/knowledge_article_demo.xml`:
```xml
<record id="knowledge_demo_article" model="knowledge.article">
    <field name="internal_permission">none</field>
    <field name="article_member_ids" eval="[
        (0, 0, {'partner_id': ref('base.partner_admin'), 'permission': 'write'}),
        (0, 0, {'partner_id': ref('base.partner_demo_portal'), 'permission': 'write'})]"/>
</record>
<!-- Then applies a template to it -->
```

## CSV Recommendations

- **Root articles** must have `internal_permission` set (typically `write` for workspace articles).
- **Hierarchy**: Load parent articles first, then children. Use `parent_id` FK by name.
- **Body content**: HTML field. Can be set via CSV but large HTML blocks are unwieldy. Consider creating articles with just `name` + `internal_permission` and populating body via RPC.
- **Members**: Cannot be loaded in the same CSV. Create articles first, then add members via `knowledge.article.member` CSV.
- For workspace articles visible to all: set `internal_permission=write`.
- For private articles: set `internal_permission=none` and add a member with `permission=write`.

## Recommended Identity Key for csv_loader

```
"knowledge.article": ["name"]
```

Note: Article names are NOT unique in Odoo (no SQL constraint). However, for demo data purposes, using `name` as identity key is practical since we control the data. For hierarchical articles, a compound key of `parent_id` + `name` would be more precise but harder to manage in CSV.
