# UI Report: stock.scrap (Odoo 19.0)

## Model Metadata

| Attribute | Value |
|---|---|
| `_name` | `stock.scrap` |
| `_inherit` | `mail.thread` |
| `_description` | "Scrap" |
| `_order` | `id desc` |
| `_rec_name` | `name` (default) |

## Key Fields for CSV Loading

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | `'New'` | Reference, auto-generated on `do_scrap()`. Read-only. |
| `product_id` | Many2one (product.product) | Yes | -- | Product (domain: `type == 'consu'`) |
| `scrap_qty` | Float | Yes | `1.0` | Quantity to scrap |
| `product_uom_id` | Many2one (uom.uom) | Yes | product's UoM | Auto-computed from product |
| `location_id` | Many2one (stock.location) | Yes | computed | Source location (auto from warehouse or picking) |
| `scrap_location_id` | Many2one (stock.location) | Yes | computed | Scrap destination (auto: first `usage='inventory'` location) |
| `lot_id` | Many2one (stock.lot) | No | -- | Lot/Serial for tracked products |
| `company_id` | Many2one (res.company) | Yes | current company | |
| `origin` | Char | No | -- | Source document reference |
| `picking_id` | Many2one (stock.picking) | No | -- | Related picking |
| `state` | Selection | Read-only | `'draft'` | `draft` or `done` |
| `should_replenish` | Boolean | No | `False` | Trigger replenishment after scrap |
| `scrap_reason_tag_ids` | Many2many | No | -- | Scrap reason tags |

## Constraints

1. **Cannot delete done scraps**: `_unlink_except_done()` raises UserError.
2. **Scrap reason tag name unique**: `unique(name)` on `stock.scrap.reason.tag`.

## create() / write() Overrides

- No custom `create()` override.
- `location_id` is auto-computed from company warehouse or picking.
- `scrap_location_id` is auto-computed (first inventory-loss location for company).

## State Transitions

| From | To | Method |
|---|---|---|
| `draft` | `done` | `action_validate()` / `do_scrap()` |

`do_scrap()`:
1. Generates sequence number for `name`.
2. Creates a `stock.move` with move lines.
3. Executes the move (`_action_done()`).
4. Sets state to `done` and `date_done`.
5. Optionally triggers replenishment.

## CSV Loading Recommendations

### Recommended CSV Headers
```
product_id,scrap_qty,lot_id
```

### Important Notes
1. **Scraps are typically created via UI**, not CSV. They involve state transitions.
2. If loading via CSV, records will be in `draft` state. You need to call `action_validate()` via RPC to confirm them.
3. `location_id` and `scrap_location_id` auto-compute -- do not set in CSV.
4. `name` auto-generates on validation -- do not set in CSV.
5. `product_uom_id` auto-computes from product -- do not set.
6. Use `_target_state: done` pseudo-column if the CSV loader supports post-create state transitions (via `action_validate`).

## Identity Key

**`name`** -- The scrap reference is auto-generated and unique. However, since `name` defaults to "New" until validation, for CSV loading use **`product_id` + `lot_id`** as a practical compound key for dedup during creation.
