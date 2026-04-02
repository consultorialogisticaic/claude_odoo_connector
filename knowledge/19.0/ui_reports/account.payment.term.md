# UI Report: account.payment.term

**Odoo Version:** 19.0
**Source:** `odoo/addons/account/models/account_payment_term.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `account.payment.term` |
| `_description` | `Payment Terms` |
| `_rec_name` | `name` (default) |
| `_order` | `sequence, id` |
| `_check_company_domain` | `check_company_domain_parent_of` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `active` | Boolean | No | `True` | |
| `note` | Html | No | — | Description shown on invoice. Translatable. |
| `sequence` | Integer | Yes | 10 | |
| `company_id` | Many2one → `res.company` | No | — | Empty = available for all companies. |
| `display_on_invoice` | Boolean | No | `True` | Show installment dates on invoice. |
| `early_discount` | Boolean | No | `False` | Enable early payment discount. |
| `discount_percentage` | Float | No | 2.0 | Only used if `early_discount=True`. |
| `discount_days` | Integer | No | 10 | Only used if `early_discount=True`. |
| `early_pay_discount_computation` | Selection | No | computed from country | `included`, `excluded`, `mixed`. Auto-computed based on company country (BE=mixed, NL=excluded, else=included). |
| `line_ids` | One2many → `account.payment.term.line` | — | default 1 line 100% | See sub-model below. |

### Sub-model: account.payment.term.line

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `value` | Selection | Yes | `percent` | `percent` or `fixed`. |
| `value_amount` | Float | — | computed | For percent: 0-100. For fixed: amount. |
| `nb_days` | Integer | — | computed | Days offset. Auto-increments by 30 for additional lines. |
| `delay_type` | Selection | Yes | `days_after` | `days_after`, `days_after_end_of_month`, `days_after_end_of_next_month`, `days_end_of_month_on_the`. |
| `days_next_month` | Char | No | `10` | Only used with `days_end_of_month_on_the`. Must be 0-31. |
| `payment_id` | Many2one → `account.payment.term` | Yes | — | Parent FK. |

## Constraints

- `_check_lines`: Sum of percent lines must equal 100%. Single line required for early discount. Discount percentage and days must be > 0.
- `_check_percent` (line): Percent value must be between 0 and 100.
- `_check_valid_char_value` (line): `days_next_month` must be numeric 0-31.

## create() / write() Overrides

- No custom `create()` or `write()` overrides.
- `_unlink_except_referenced_terms`: Cannot delete if referenced by `account.move`.

## Demo Data Patterns

Standard Odoo installs payment terms via chart template data (`account.payment.term` records like "Immediate Payment", "30 Days", "30/60/90 Days", etc.). These are created by the localization module, not demo data.

## CSV Recommendations

- Since payment term lines are a sub-model, they cannot be loaded in the same CSV. **Load `account.payment.term` first**, then use the default line (100% at 0 days). For complex terms, use RPC to create lines programmatically, or create separate CSV rows for `account.payment.term.line` with `payment_id` FK.
- Better approach: Create payment terms via `account.payment.term` CSV with just `name`, `sequence`, `note`. The default `_default_line_ids` creates a single 100% line automatically. Then update lines via a second pass if needed.

## Recommended Identity Key for csv_loader

```
"account.payment.term": ["name"]
```
