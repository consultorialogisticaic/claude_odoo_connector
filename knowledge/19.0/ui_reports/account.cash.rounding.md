# UI Report: account.cash.rounding

**Odoo Version:** 19.0
**Source:** `odoo/addons/account/models/account_cash_rounding.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `account.cash.rounding` |
| `_description` | `Account Cash Rounding` |
| `_rec_name` | `name` (default) |
| `_check_company_auto` | `True` |

## Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Translatable. |
| `rounding` | Float | Yes | 0.01 | Smallest coinage precision (e.g., 0.05 for Switzerland). Must be > 0. |
| `strategy` | Selection | Yes | `add_invoice_line` | `biggest_tax` (Modify tax amount) or `add_invoice_line` (Add a rounding line). |
| `profit_account_id` | Many2one → `account.account` | No | — | Company-dependent. Domain excludes receivable/payable. Required if strategy=`add_invoice_line`. |
| `loss_account_id` | Many2one → `account.account` | No | — | Company-dependent. Same domain. Required if strategy=`add_invoice_line`. |
| `rounding_method` | Selection | Yes | `HALF-UP` | `UP`, `DOWN`, `HALF-UP` (Nearest). |

## Constraints

- `validate_rounding`: `rounding` must be strictly positive (> 0).

## create() / write() Overrides

- No custom `create()` or `write()` overrides. Very simple model.

## Demo Data Patterns

From `l10n_ch/demo/account_cash_rounding.xml`:
```xml
<record id="cash_rounding_CHF_005" model="account.cash.rounding">
    <field name="name">CHF 0.05</field>
    <field name="rounding">0.05</field>
    <field name="strategy">biggest_tax</field>
    <field name="rounding_method">HALF-UP</field>
</record>
```

## CSV Recommendations

- Simple model. All fields can go in a single CSV row.
- `profit_account_id` and `loss_account_id` are company-dependent, meaning they are stored in `ir.property` rather than the model table. The csv_loader should handle these via the standard field write mechanism, but the account must exist first.
- For Colombia (COP), a common rounding is `rounding=1` or `rounding=100` with `rounding_method=HALF-UP`.

## Recommended Identity Key for csv_loader

```
"account.cash.rounding": ["name"]
```
