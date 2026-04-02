# UI Report: account.reconcile.model

**Odoo Version:** 19.0
**Source:** `odoo/addons/account/models/account_reconcile_model.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `account.reconcile.model` |
| `_description` | `Preset to create journal entries during a invoices and payments matching` |
| `_inherit` | `mail.thread` |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, id` |
| `_check_company_auto` | `True` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `active` | Boolean | No | `True` | |
| `sequence` | Integer | Yes | 10 | |
| `company_id` | Many2one → `res.company` | Yes | current company | Required, readonly. |
| `trigger` | Selection | Yes | `manual` | `manual` or `auto_reconcile`. |
| `match_journal_ids` | Many2many → `account.journal` | No | — | Filter by journals (bank/cash/credit). |
| `match_amount` | Selection | No | — | `lower`, `greater`, `between`. |
| `match_amount_min` | Float | No | — | |
| `match_amount_max` | Float | No | — | |
| `match_label` | Selection | No | — | `contains`, `not_contains`, `match_regex`. |
| `match_label_param` | Char | No | — | String or regex pattern. |
| `match_partner_ids` | Many2many → `res.partner` | No | — | |

### Sub-model: account.reconcile.model.line

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `model_id` | Many2one → `account.reconcile.model` | Yes | — | Parent FK. Readonly. |
| `sequence` | Integer | Yes | 10 | |
| `account_id` | Many2one → `account.account` | No | — | Domain excludes off_balance. |
| `partner_id` | Many2one → `res.partner` | No | — | |
| `label` | Char | No | — | Translatable. |
| `amount_type` | Selection | Yes | `percentage` | `fixed`, `percentage`, `percentage_st_line`, `regex`. |
| `amount_string` | Char | Yes | `100` | Amount value as string. |
| `tax_ids` | Many2many → `account.tax` | No | — | |

## Constraints

- `_check_match_label_param`: If `match_label=match_regex`, the regex must compile.
- `_validate_amount` (line): Fixed amount cannot be 0. Percentage cannot be 0. Regex must compile.

## create() / write() Overrides

- No custom `create()` or `write()` overrides.
- `copy_data`: Appends " (copy)" and ensures unique name.

## Demo Data Patterns

No specific demo data file found for reconcile models. They are typically created manually by accountants.

## CSV Recommendations

- Load the parent `account.reconcile.model` first, then load `account.reconcile.model.line` with `model_id` FK.
- For simple reconciliation rules (e.g., "Bank Fees", "Interest Income"), create the model with `trigger=manual` and a single line with `amount_type=percentage`, `amount_string=100`, and the target `account_id`.
- `company_id` is required and readonly -- set it explicitly.

## Recommended Identity Key for csv_loader

```
"account.reconcile.model": ["name", "company_id"]
```
