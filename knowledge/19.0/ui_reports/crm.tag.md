# UI Report: crm.tag

**Odoo Version:** 19.0
**Source:** `odoo/addons/sales_team/models/crm_tag.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.tag` |
| `_description` | `CRM Tag` |
| `_inherit` | — |
| `_rec_name` | `name` (default) |
| `_order` | default (`id`) |

Defined in the `sales_team` module and reused by `crm` and `sale` (no `_inherit` extensions in community or enterprise — all consumers reference it via Many2many only).

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. Tag label (e.g. "Services"). |
| `color` | Integer | No | random 1–11 | `_get_default_color()` returns `randint(1, 11)`. Form view marks it `required="True"` with `widget="color_picker"`. |

No other fields are declared on the model — it is intentionally minimal.

## Constraints

From `odoo/addons/sales_team/models/crm_tag.py:18`:

- `_name_uniq` (`models.Constraint('unique (name)', ...)`): tag `name` must be globally unique. Error: *"Tag name already exists!"*.

No `@api.constrains` methods. No `create()` / `write()` / `unlink()` overrides.

## Form View

`odoo/addons/sales_team/views/crm_tag_views.xml`:

- Form view `sales_team_crm_tag_view_form`: `name` in the title, `color` with `widget="color_picker"` and `required="True"`.
- List view `sales_team_crm_tag_view_tree` is `editable="bottom"` with `name` + `color` (`color_picker` widget).
- Action `sales_team_crm_tag_action` lands on the list view directly (no kanban).

No header buttons, no statusbar, no onchanges — creation is a single atomic write.

## Consumers (Many2many targets)

`crm.tag` has no inbound `_inherit`, but many models point a Many2many at it:

| Model | Field | Relation table | Source |
|---|---|---|---|
| `crm.lead` | `tag_ids` | `crm_tag_rel (lead_id, tag_id)` | `odoo/addons/crm/models/crm_lead.py:136` |
| `sale.order` | `tag_ids` | `sale_order_tag_rel (order_id, tag_id)` | `odoo/addons/sale/models/sale_order.py:287` (gated by `sales_team.group_sale_salesman`) |
| `crm.iap.lead.mining.request` | `tag_ids` | default | `odoo/addons/crm_iap_mine/models/crm_iap_lead_mining_request.py:54` |
| `crm.reveal.rule` | `tag_ids` | default | `odoo/addons/website_crm_iap_reveal/models/crm_reveal_rule.py:57` |
| `event.lead.rule` | `lead_tag_ids` | default | `odoo/addons/event_crm/models/event_lead_rule.py:111` |

The canonical consumer is `crm.lead.tag_ids`. To attach tags in CSV, populate the `tag_ids` column on `crm.lead` with a comma-separated list of tag names (many2many_tags convention) — the CSV loader resolves each entry via `name_search` on `crm.tag`.

## Demo Data Patterns

From `odoo/addons/sales_team/data/crm_tag_demo.xml` (loaded as `demo`, `noupdate="1"`):

```xml
<record id="categ_oppor1" model="crm.tag">
    <field name="name">Product</field>
    <field name="color" eval="1"/>
</record>
```

Eight demo tags ship: Product, Software, Services, Information, Design, Training, Consulting, Other (colors 1–8).

Additional non-demo (module `data`) tags from `odoo/addons/website_crm_partner_assign/data/crm_tag_data.xml`:

- `tag_portal_lead_partner_unavailable` — "No more partner available" (color 3)
- `tag_portal_lead_is_spam` — "Spam" (color 3)
- `tag_portal_lead_own_opp` — "Created by Partner" (color 4)

These are installed as regular data (not demo) when `website_crm_partner_assign` is present.

## CSV Recommendations

- Supply `name` (required, unique). Supply `color` explicitly if you want deterministic output — otherwise each run draws a random 1–11 via `_get_default_color`.
- Do not rely on the default `color`: CSV re-imports that omit `color` will get a new random value on every fresh create, drifting from any prior fixture.
- Tag `name` is translatable. Load the base language value; use `i18n/*.po` or a translation CSV for other languages rather than duplicating rows.
- If the `sales_team` demo data is loaded (dev/test DBs), names like `Product`, `Services`, `Training`, `Consulting`, `Other` already exist — creating them again will fail the `unique(name)` constraint. Either reuse the demo XML IDs or pick distinct names.
- To link tags to leads via CSV, load `crm.tag` rows first, then set `crm.lead.tag_ids` to a comma-separated list of tag names (Many2many widget is `many2many_tags` on lead forms; the CSV loader maps the same convention through `name_search`).

## Recommended Identity Key for csv_loader

```
"crm.tag": ["name"]
```

Matches the SQL `unique(name)` constraint — `name` is the natural key.
