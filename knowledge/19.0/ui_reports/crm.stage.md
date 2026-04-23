# UI Report: crm.stage

**Odoo Version:** 19.0
**Source:** `odoo/addons/crm/models/crm_stage.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `crm.stage` |
| `_description` | `CRM Stages` |
| `_inherit` | — (no inheritance; no extensions in community or enterprise) |
| `_rec_name` | `name` |
| `_order` | `sequence, name, id` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. Stage label (e.g. "New", "Qualified", "Won"). |
| `sequence` | Integer | No | `1` | Ordering key. Lower = earlier in the pipeline. |
| `is_won` | Boolean | No | `False` | Marks the closed-won stage. See "Side effects" below. |
| `rotting_threshold_days` | Integer | No | `0` | Days after which opportunities in this stage are flagged as rotting. `0` disables. Hidden in the form when `is_won=True`. |
| `requirements` | Text | No | — | Free-text internal checklist; surfaces as a tooltip on the stage name. |
| `team_ids` | Many2many → `crm.team` | No | — | Sales teams this stage belongs to. **Empty = shared across all teams.** `ondelete='restrict'`. |
| `fold` | Boolean | No | `False` | When `True`, the stage is collapsed in the kanban pipeline when empty. |
| `color` | Integer | No | `0` | Color index; `export_string_translation=False`. |
| `team_count` | Integer | No | computed | UI-only (`compute='_compute_team_count'`, not stored). Counts total `crm.team` records; drives whether `team_ids` is visible in the form. Do not set in CSV. |

## Form View

`odoo/addons/crm/views/crm_stage_views.xml` (`crm_stage_form`):

- `name` is rendered as the title (`<h1>`).
- `team_ids` uses `widget="many2many_tags"` with `no_open` and `no_create` options, and a placeholder "Shared with all teams". It is hidden when `team_count <= 1` (single-team installs never see it).
- `rotting_threshold_days` is invisible when `is_won=True` (a won stage cannot rot).
- `requirements` is shown under a "Requirements" separator as a full-width text area.
- No `<header>` / state buttons — creation is a plain save.

List view (`crm_stage_tree`) is `multi_edit="1"` with `sequence` as a handle widget.

## Side Effects and Semantics

**`is_won` is the single source of truth for "closed-won" stages.** It is referenced throughout `crm.lead` and drives automatic lead lifecycle changes:

- On `crm.lead.create()` (`odoo/addons/crm/models/crm_lead.py:802-804`): if a lead is created directly in an `is_won=True` stage, `date_closed` is set to `now()`.
- On `crm.lead.write()` when `stage_id` changes to an `is_won=True` stage (`crm_lead.py:841-845`): the lead is forced to `active=True`, `probability=100`, `automated_probability=100`, and `date_closed` is set to `now()` (`crm_lead.py:856-857`). Moving between two won stages does not reset `date_closed` (`crm_lead.py:874-881`).
- On `crm.lead` lost/won bookkeeping (`crm_lead.py:1128-1133`, `2252`): won leads are resolved via `crm.stage` records where `is_won=True`.
- There is **no hardcoded won stage** — any `crm.stage` with `is_won=True` qualifies. Multiple won stages are supported.

**`crm.stage.write()` override (`crm_stage.py:52-67`):** when `is_won` is toggled in `vals`, all leads currently in the affected stage are recomputed:
- If `is_won` flipped to `True`: leads get `probability=100` and `automated_probability=100`.
- If `is_won` flipped to `False`: leads have `_compute_probabilities()` re-run.
- Any manual probability on those leads is lost.
- An `@api.onchange('is_won')` warning is raised in the UI to surface this cost before save.

**Team scoping:** `team_ids` empty means the stage is shared across every `crm.team`. A non-empty `team_ids` restricts the stage to those teams' pipelines. `ondelete='restrict'` prevents deleting a `crm.team` that is still referenced by a stage.

## Constraints

- No `@api.constrains` methods on `crm.stage`.
- No `_sql_constraints`.
- No uniqueness constraint on `name` — the same stage name can legitimately repeat across teams.

## create() / write() Overrides

- **create()**: not overridden on `crm.stage`. Side effects come from `crm.lead` reading `stage_id.is_won` (see above).
- **write()**: overridden to recompute lead probabilities when `is_won` flips (see "Side Effects").
- **unlink()**: not overridden. Deletion is blocked indirectly via `team_ids` `ondelete='restrict'` only on the team side, not the stage side.

## Demo / Default Data Patterns

From `odoo/addons/crm/data/crm_stage_data.xml` (module data, `noupdate="1"`, `forcecreate="False"`):

```xml
<record model="crm.stage" id="stage_lead1">
    <field name="name">New</field>
    <field name="sequence">1</field>
    <field name="color">11</field>
</record>
<record model="crm.stage" id="stage_lead4">
    <field name="name">Won</field>
    <field name="fold" eval="False"/>
    <field name="is_won">True</field>
    <field name="sequence">70</field>
    <field name="color">10</field>
</record>
```

Four default shared stages are shipped: `New` (seq 1), `Qualified` (seq 2), `Proposition` (seq 3), `Won` (seq 70, `is_won=True`). None have `team_ids` set — all are shared. `forcecreate="False"` means re-installing does not recreate them if the user deleted them.

From `odoo/addons/crm/data/crm_stage_demo.xml`: only bumps `stage_lead3.rotting_threshold_days` to `5`.

## UI Creation Flow

1. Click "New" in Sales → Configuration → Stages.
2. Fill `name` (required, becomes the title).
3. Optionally toggle `fold`, pick a `color`, and (if the install has more than one team) select `team_ids`. Leave `team_ids` empty to share across all teams.
4. Toggle `is_won` if this is a closed-won stage — an onchange warning appears about recomputation cost on save.
5. If `is_won` is `False`, optionally set `rotting_threshold_days` (the field is hidden once `is_won=True`).
6. Fill `requirements` free text (optional).
7. Save.

No onchange sets any field value silently — the only onchange is the `is_won` confirmation warning, which does not mutate the record. CSV `create()` therefore does not need to replay any onchange-driven defaults.

## CSV Recommendations

- Four default shared stages already exist after `crm` installs. Prefer updating them (by XML ID or by `(name, team_ids=[])` lookup) rather than creating duplicates.
- `team_ids` is Many2many — to share a stage across all teams, leave the column empty. To scope to specific teams, resolve team names via `name_search` and use the CSV Many2many syntax.
- Only set `is_won=True` on the stages that actually close-won leads. Every `is_won=True` stage will pull leads' `probability` to 100 on write, and every transition into one will stamp `date_closed`.
- `sequence` ordering matters functionally (pipeline order) — keep gaps (1, 2, 3, … 70 in the defaults) so later inserts don't require renumbering.
- `team_count` is compute-only; never include it in CSV.
- `color` is an integer palette index (0–11 in practice), not a hex code.

## Recommended Identity Key for csv_loader

Stage names are not unique across teams (Odoo explicitly allows the same name under different `team_ids`), so `["name"]` alone is unsafe. Use a compound key:

```
"crm.stage": ["name", "team_ids"]
```

For the shared default stages (`team_ids` empty), the compound key still resolves uniquely because `("New", [])` is distinct from `("New", [<team_id>])`.
