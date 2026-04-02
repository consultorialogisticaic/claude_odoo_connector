# UI Report -- pos.payment.method

---

## 1. Model Identity

| Field | Value |
|---|---|
| **Technical name** | `pos.payment.method` |
| **Defining module** | `point_of_sale` (addons/point_of_sale/models/pos_payment_method.py) |
| **`_rec_name`** | `name` (default) |
| **`_rec_names_search`** | Not set (default) |
| **Inheriting modules** | None significant for CSV loading |

---

## 2. Required Fields at Creation

| Field | Type | Source | Notes |
|---|---|---|---|
| `name` | Char | Python required=True (line 23) | e.g. "Cash", "Bank", "Credit Card" |
| `payment_method_type` | Selection | Python required=True (line 61) | Values: `'none'`, `'terminal'`, `'qr_code'`. Default: `'none'` |

Conditionally required:
| Field | Condition | Notes |
|---|---|---|
| `journal_id` | `not split_transactions` | Form view: `required="not split_transactions"` (line 23 of view) |
| `outstanding_account_id` | `type == 'bank'` | Form view: `required="type == 'bank'"` |
| `qr_code_method` | `payment_method_type == 'qr_code'` | Form view: `required="payment_method_type == 'qr_code'"` |

---

## 3. Onchange Chains

| Trigger Field | Computed Fields | Notes |
|---|---|---|
| `journal_id` | `type`, `is_cash_count` | type = journal.type ('cash'/'bank') or 'pay_later'. is_cash_count = (type == 'cash'). |
| `journal_id` | `outstanding_account_id` | For bank journals, auto-sets to transfer account. |
| `payment_method_type` | `use_payment_terminal`, `qr_code_method` | Setting to 'none' clears both. |

**Critical for CSV:** `type` is computed from `journal_id`. Do NOT set `type` in CSV -- it is a computed stored field. Set `journal_id` instead to control cash/bank behavior.

---

## 4. Constraint Rules

### Python Constraints (`@api.constrains`)

- `_check_payment_method` (line 202): If `payment_method_type == 'qr_code'`, journal must be type 'bank' with a `bank_account_id`, and `qr_code_method` must be set.
- `_check_company_config` (line 214): All linked pos.config records must belong to the same company as the payment method.

### SQL Constraints

- None defined.

---

## 5. create() / write() Side Effects

- **create()**: Calls `_force_payment_method_type_values()` to clear incompatible fields based on `payment_method_type`. E.g., if type is 'terminal', clears `qr_code_method`; if 'none', clears both `use_payment_terminal` and `qr_code_method`. (line 143)
- **write()**: Raises `UserError` if modifying a payment method that has open POS sessions (except for `sequence` field). (line 150)

---

## 6. FK Resolution Strategy

| Field | Resolution Method | Notes |
|---|---|---|
| `journal_id` | name_search on account.journal | Must be type 'cash' or 'bank' |
| `company_id` | name_search on res.company | Defaults to current company |
| `config_ids` | name_search on pos.config | Many2many -- comma-separated names |

**Identity keys for deduplication:** `["name"]`

---

## 7. Odoo Demo Data Patterns

**Demo files found:**
- Payment methods are created programmatically by `_create_journal_and_payment_methods()` in pos.config scenario loaders.
- No standalone XML demo data for payment methods.

**Key patterns:**
- Each POS config typically gets its own cash journal/payment method.
- Bank payment methods can be shared across configs.
- Cash payment methods are exclusive to one config (enforced by constraint).

---

## 8. CSV Generation Recommendations

- For a simple cash method: set `name`, `journal_id` (cash journal), `payment_method_type=none`.
- For a simple bank/card method: set `name`, `journal_id` (bank journal), `payment_method_type=none` (or `terminal` if terminal integration).
- For customer account (pay later): set `name`, `split_transactions=True`, leave `journal_id` empty.
- Do NOT set `type` or `is_cash_count` in CSV -- they are computed from `journal_id`.
- Ensure each cash journal is only linked to ONE payment method.
- Load payment methods BEFORE pos.config so they can be referenced.
