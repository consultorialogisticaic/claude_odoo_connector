# UI Report: project.tags

**Odoo Version:** 19.0
**Source:** `odoo/addons/project/models/project_tags.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `project.tags` |
| `_description` | `Project Tags` |
| `_inherit` | — (no inheritance) |
| `_rec_name` | `name` (default) |
| `_order` | `name` |

No other module in the workspace extends `project.tags` via `_inherit`.

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. Unique (see SQL constraint). |
| `color` | Integer | No | random 1–11 | Kanban color index. Transparent tags are not visible in kanban views. |
| `project_ids` | Many2many → `project.project` | No | — | Relation table `project_project_project_tags_rel`. `export_string_translation=False`. Reverse side — normally populated from `project.project`. |
| `task_ids` | Many2many → `project.task` | No | — | `export_string_translation=False`. Reverse side of `project.task.tag_ids` (the primary consumer of this model). |

## Constraints

- **SQL constraint `_name_uniq`**: `unique (name)` — error message: *"A tag with the same name already exists."* Enforced at the database level, case-sensitive. Matches `name_create`'s case-insensitive (`=ilike`) pre-check that silently returns the existing tag instead of raising.

No `@api.constrains` Python constraints are defined.

## Form View

`odoo/addons/project/views/project_tags_views.xml`:

```xml
<record model="ir.ui.view" id="project_tags_form_view">
    <field name="model">project.tags</field>
    <field name="arch" type="xml">
        <form string="Tags">
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="color" widget="color_picker"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

List view is editable-inline (`editable="top"`, `multi_edit="1"`, `default_order="name"`) with `name` and `color` (widget `color_picker`, `optional="show"`). Search view exposes only `name`.

There are no buttons, no header, no state machine — this is a pure config model.

## create() / write() Overrides

No `create()` or `write()` overrides. The only method overrides relevant to CSV loading are:

- **`name_create(name)`**: If a tag with the same name (stripped, case-insensitive via `=ilike`) already exists, returns `(existing.id, existing.display_name)` instead of creating a new one. Silent deduplication — callers do not get an error on duplicates via this entry point. CSV loader using `create()` directly will still hit the SQL `unique(name)` constraint and raise.
- **`name_search(name, ...)`**: When context has `project_id`, first returns tags already used on the last 1000 tasks of that project, then completes from a fallback search. Order-sensitive results.
- **`search_read` / `formatted_read_group`**: When `project_id` is in context, filter domain to the tag IDs returned by `name_search()`.

## Demo Data Patterns

From `odoo/addons/project/data/project_demo.xml` (lines 24–74): 17 demo tags `project_tags_00` … `project_tags_16`, each setting only `name`:

```xml
<record id="project_tags_00" model="project.tags">
    <field name="name">Bug</field>
</record>
<record id="project_tags_01" model="project.tags">
    <field name="name">New Feature</field>
</record>
<!-- Experiment, Usability, Internal, External, Construction, Architecture,
     Design, Interior, Office, Finance, Social, Home, Work, Meeting, Priority -->
```

`color` is never set in demo data — every demo tag gets a random color (1–11) via `_get_default_color`. The tags are consumed via `Command.set(...)` / `Command.link(...)` on `project.task.tag_ids` and `project.project.tag_ids` throughout the same file.

## CSV Recommendations

- Only `name` is strictly required. `color` is optional; omit to get a random color, or set an integer 1–11 for a deterministic kanban color.
- `name` must be unique (SQL-enforced). Trim whitespace and normalize case before loading, since `name_create`'s `=ilike` dedup does NOT run on direct `create()` — duplicates will raise `A tag with the same name already exists.`
- Do not set `project_ids` or `task_ids` here — populate them from the owning side (`project.project.tag_ids`, `project.task.tag_ids`).
- This model has demo data on module install. If loading in a demo database, either reuse the demo XML IDs (`project.project_tags_00` … `project_tags_16`) or ensure your names do not collide with `Bug`, `New Feature`, `Experiment`, `Usability`, `Internal`, `External`, `Construction`, `Architecture`, `Design`, `Interior`, `Office`, `Finance`, `Social`, `Home`, `Work`, `Meeting`, `Priority`.
- Many2many references from `project.task.tag_ids` resolve via `name_search`, which is `project_id`-context-aware — in non-project contexts the default `_search_display_name` (ilike on `name`) is used.

## Recommended Identity Key for csv_loader

```
"project.tags": ["name"]
```

`name` is the sole unique key in the schema (SQL `unique(name)`), so it is sufficient and correct for deduplication.
