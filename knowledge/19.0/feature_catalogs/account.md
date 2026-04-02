# Feature Catalog: account + accountant (Invoicing + Accounting)

- **Technical names:** `account` (community), `accountant` (enterprise), `account_accountant` (enterprise bridge), `account_reports` (enterprise)
- **Version:** 19.0
- **Category:** Accounting/Accounting
- **Application:** Yes (both `account` and `accountant`)
- **Depends:** `account` -> base_setup, onboarding, product, analytic, portal, digest | `account_accountant` -> account, mail_enterprise | `accountant` -> account_reports -> account_accountant
- **Summary:** Full-stack accounting: invoicing, payments, bank reconciliation, financial reports, tax returns, budgets, audit trail

---

## 1. Menus (Backend)

### 1.1 Top-Level: Invoicing / Accounting

When `accountant` is installed, the app label changes from "Invoicing" to "Accounting".

| Menu path | Action / Model | Source module | Notes |
|---|---|---|---|
| **Dashboard** | `open_account_journal_dashboard_kanban` | account | Kanban cards per journal: bank, cash, sales, purchases. POS sessions appear here after closing. |
| **Customers > Invoices** | `account.move` (out_invoice) | account | Create/post/send customer invoices |
| **Customers > Credit Notes** | `account.move` (out_refund) | account | Customer credit notes |
| **Customers > Payments** | `account.payment` (inbound) | account | Receive customer payments |
| **Customers > Products** | `product.product` (sellable) | account | Products for sale |
| **Customers > Customers** | `res.partner` (customer) | account | Customer list |
| **Vendors > Bills** | `account.move` (in_invoice) | account | Vendor bills |
| **Vendors > Refunds** | `account.move` (in_refund) | account | Vendor refunds / debit notes |
| **Vendors > Payments** | `account.payment` (outbound) | account | Vendor payment registration |
| **Vendors > Products** | `product.product` (purchasable) | account | Products for purchase |
| **Vendors > Vendors** | `res.partner` (supplier) | account | Vendor list |
| **Accounting > Transactions > Journal Entries** | `account.move` (entry) | account | All journal entries (manual, auto-generated) |
| **Accounting > Transactions > Analytic Items** | `account.analytic.line` | account | Analytic line items (requires analytic accounting feature) |
| **Accounting > Closing > Secure Entries** | wizard `account.secure.entries.wizard` | account | Hash posted entries for inalterability |
| **Accounting > Closing > Reconcile** | `account.move.line` (unreconciled) | account_accountant | Bank/partner reconciliation |
| **Accounting > Closing > Lock Dates** | wizard `account.change.lock.date` | account_accountant | Set lock dates for non-advisers / all users / tax returns |
| **Accounting > Closing > Tax Returns** | `account.return` | account_reports | Period-based tax return management |
| **Accounting > Assets & Liabilities** | (parent menu) | accountant | Asset depreciation, deferred rev/exp (via `account_asset` if installed) |
| **Review > Control > Journal Items** | `account.move.line` | account | All journal items flat view |
| **Review > Control > Journal Audit** | report action | account_reports | Drillable journal audit report |
| **Review > Audit > Working Files** | `account.audit` | account_reports | Working file management for auditors |
| **Review > Inventory** | (parent menu) | account_reports | Inventory-related audit entries |
| **Review > Regularization Entries > Unrealized Currencies** | multicurrency revaluation report | account_reports | FX revaluation |
| **Review > Regularization Entries > Deferred Revenues** | deferred revenue report | account_reports | Deferred revenue entries |
| **Review > Regularization Entries > Deferred Expenses** | deferred expense report | account_reports | Deferred expense entries |
| **Review > Logs** | (parent menu) | account | Audit log entries |
| **Reporting > Statement Reports > Balance Sheet** | dynamic report | account_reports | IFRS/local balance sheet |
| **Reporting > Statement Reports > Profit and Loss** | dynamic report | account_reports | P&L statement |
| **Reporting > Statement Reports > Cash Flow Statement** | dynamic report | account_reports | Cash flow (indirect method) |
| **Reporting > Ledgers > Trial Balance** | dynamic report | account_reports | CoA trial balance |
| **Reporting > Ledgers > General Ledger** | dynamic report | account_reports | Full general ledger |
| **Reporting > Partner Reports > Partner Ledger** | dynamic report | account_reports | Per-partner ledger |
| **Reporting > Partner Reports > Aged Receivable** | dynamic report | account_reports | Aging buckets receivable |
| **Reporting > Partner Reports > Aged Payable** | dynamic report | account_reports | Aging buckets payable |
| **Reporting > Taxes & Fiscal > Tax Report** | dynamic report | account_reports | Generic tax report (adapts to localization) |
| **Reporting > Management > Invoice Analysis** | pivot `account.invoice.report` | account | Invoice analytics pivot/graph |
| **Reporting > Management > Executive Summary** | dynamic report | account_reports | KPI executive dashboard |
| **Reporting > Management > Analytic Report** | pivot report | account | Analytic accounting pivot |
| **Configuration > Settings** | `res.config.settings` | account | All accounting settings |
| **Configuration > Accounting > Chart of Accounts** | `account.account` | account | CoA management |
| **Configuration > Accounting > Taxes** | `account.tax` | account | Tax configuration |
| **Configuration > Accounting > Journals** | `account.journal` | account | Journal definitions (sales, purchase, bank, cash, misc) |
| **Configuration > Accounting > Currencies** | `res.currency` | account | Currency management |
| **Configuration > Accounting > Fiscal Positions** | `account.fiscal.position` | account | Tax/account mapping rules |
| **Configuration > Accounting > Multi-Ledger** | `account.journal.group` | account | Group journals for multi-ledger reporting |
| **Configuration > Accounting > Cash Roundings** | `account.cash.rounding` | account | Cash rounding rules (relevant for POS) |
| **Configuration > Accounting > Fiscal Years** | `account.fiscal.year` | account_accountant | Fiscal year definitions |
| **Configuration > Invoicing > Payment Terms** | `account.payment.term` | account | Payment term definitions |
| **Configuration > Invoicing > Product Categories** | `product.category` | account | Category-level income/expense accounts |
| **Configuration > Analytic > Distribution Models** | `account.analytic.distribution.model` | account | Auto-distribution rules |
| **Configuration > Analytic > Analytic Accounts** | `account.analytic.account` | account | Cost/revenue centers |
| **Configuration > Analytic > Analytic Plans** | `account.analytic.plan` | account | Plan structure (dimensions) |

---

## 2. Settings / Feature Flags

All settings via Configuration > Settings (Accounting section):

| Setting | Technical field | Default | Percimon relevance | Notes |
|---|---|---|---|---|
| **Fiscal Localization Package** | `chart_template` | — | HIGH: must select `co` (Colombia) | Loads Colombian CoA, taxes (IVA 19%, ICA, retention), fiscal positions |
| **Fiscal Country** | `account_fiscal_country_id` | per company | HIGH: Colombia | Determines tax report structure |
| **Default Sales Tax** | `sale_tax_id` | from localization | HIGH: IVA 19% | Applied to all new products |
| **Default Purchase Tax** | `purchase_tax_id` | from localization | HIGH: IVA 19% | Applied to all new purchases |
| **Prices Include Taxes** | `account_price_include` | `tax_excluded` | MEDIUM: POS may use tax-included | Locked after first journal entry |
| **Tax Rounding Method** | `tax_calculation_rounding_method` | `round_globally` | MEDIUM | `round_per_line` for tax-included pricing |
| **Cash Basis Taxes** | `tax_exigibility` | False | LOW | Enable if using cash-basis IVA |
| **Main Currency** | `currency_id` | COP | HIGH | Colombian Peso |
| **Cash Rounding** | `group_cash_rounding` | False | MEDIUM: POS cash rounding | Define smallest coinage for COP |
| **Credit Limit** | `account_use_credit_limit` | False | LOW | Alert on customer credit overrun |
| **Invoice Terms & Conditions** | `use_invoice_terms` | False | LOW | Add T&C footer to invoices |
| **Amount in Words** | `display_invoice_amount_total_words` | False | MEDIUM: Colombian invoices often show this | Spanish amount text |
| **Taxes in Company Currency** | `display_invoice_tax_company_currency` | False | LOW | Relevant if multi-currency |
| **Delivery Address** | `group_sale_delivery_address` | False | MEDIUM: multi-branch chain | Separate invoice/delivery addresses |
| **Online Payments** | `module_account_payment` | False | LOW | Customer online payment portal |
| **Batch Payments** | `module_account_batch_payment` | False | LOW | Enterprise: group payments |
| **QR Codes on Invoices** | `qr_code` | False | LOW | QR code for payment |
| **Auto-post Bills** | `autopost_bills` | False | LOW | AI auto-validation for vendor bills |
| **Check Printing** | `module_account_check_printing` | False | LOW | Print checks |
| **OCR Digitization** | `module_account_extract` | False | MEDIUM | AI bill scanning |
| **Analytic Accounting** | `group_analytic_accounting` | False | HIGH: cost center tracking per store | Track costs/revenue by store/branch |
| **Budget Management** | `module_account_budget` | False | HIGH: budget compliance reports | Enterprise: compare actual vs planned |
| **Margin Analysis** | `module_product_margin` | False | MEDIUM: COGS tracking | Product margin from invoices |
| **Dynamic Reports** | `module_account_reports` | False | HIGH: auto-installed with accountant | Financial reporting engine |
| **Restrictive Audit Trail** | `restrictive_audit_trail` | False | MEDIUM | Immutable change log on posted entries |
| **Accounting Firms Mode** | `quick_edit_mode` | Disabled | LOW | Speed encoding for accountants |
| **Storno Accounting** | `account_storno` | False | LOW | Negative reversal entries |
| **Units & Packagings** | `group_uom` | False | MEDIUM: kg, units, liters | UoM for frozen yogurt products |

---

## 3. Key Models

### 3.1 account.move (Journal Entry / Invoice)

The central model for all accounting documents.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Sequence number (e.g., INV/2026/0001) |
| `move_type` | Selection | `entry`, `out_invoice`, `out_refund`, `in_invoice`, `in_refund`, `out_receipt`, `in_receipt` |
| `state` | Selection | `draft`, `posted`, `cancel` |
| `partner_id` | Many2one(`res.partner`) | Customer/vendor |
| `invoice_date` | Date | Invoice date |
| `date` | Date | Accounting date |
| `journal_id` | Many2one(`account.journal`) | Journal (sales, purchase, bank, cash, misc) |
| `currency_id` | Many2one(`res.currency`) | Transaction currency |
| `amount_total` | Monetary | Total with taxes |
| `amount_residual` | Monetary | Remaining to pay |
| `payment_state` | Selection | `not_paid`, `in_payment`, `paid`, `partial`, `reversed` |
| `invoice_line_ids` | One2many(`account.move.line`) | Invoice lines |
| `line_ids` | One2many(`account.move.line`) | All journal items |
| `fiscal_position_id` | Many2one(`account.fiscal.position`) | Tax mapping |
| `payment_reference` | Char | Payment reference (bank transfer ref) |
| `ref` | Char | External reference |

**POS integration:** When a POS session closes, it creates `account.move` entries — one combined entry per session with lines for sales, taxes, payments, and cash discrepancy (difference). The POS journal is linked to the session.

### 3.2 account.move.line (Journal Item)

| Field | Type | Notes |
|---|---|---|
| `move_id` | Many2one(`account.move`) | Parent entry |
| `account_id` | Many2one(`account.account`) | GL account |
| `debit` / `credit` | Monetary | Debit/credit amounts |
| `balance` | Monetary | Signed balance (debit - credit) |
| `partner_id` | Many2one(`res.partner`) | Partner on line |
| `product_id` | Many2one(`product.product`) | Product reference |
| `quantity` | Float | Line quantity |
| `price_unit` | Float | Unit price |
| `tax_ids` | Many2many(`account.tax`) | Taxes applied |
| `analytic_distribution` | JSON | Analytic distribution dict {plan_id: percentage} |
| `reconciled` | Boolean | Whether reconciled |
| `full_reconcile_id` | Many2one(`account.full.reconcile`) | Reconciliation group |

### 3.3 account.account (Chart of Accounts)

| Field | Type | Notes |
|---|---|---|
| `code` | Char | Account code (e.g., 110505 for Caja General in Colombian CoA) |
| `name` | Char | Account name |
| `account_type` | Selection | `asset_receivable`, `asset_bank`, `asset_cash`, `asset_current`, `asset_non_current`, `asset_prepayments`, `asset_fixed`, `liability_payable`, `liability_credit_card`, `liability_current`, `liability_non_current`, `equity`, `equity_unaffected`, `income`, `income_other`, `expense`, `expense_depreciation`, `expense_direct_cost`, `off_balance` |
| `reconcile` | Boolean | Allow reconciliation |
| `tax_ids` | Many2many(`account.tax`) | Default taxes |
| `tag_ids` | Many2many(`account.account.tag`) | Report tags |
| `currency_id` | Many2one(`res.currency`) | Force currency |

Colombian CoA follows PUC (Plan Unico de Cuentas) — 6-digit codes.

### 3.4 account.tax

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Tax name (e.g., "IVA 19%") |
| `type_tax_use` | Selection | `sale`, `purchase`, `all` |
| `amount_type` | Selection | `percent`, `fixed`, `group`, `division` |
| `amount` | Float | Tax rate (19.0 for IVA) |
| `tax_group_id` | Many2one(`account.tax.group`) | Grouping for reports |
| `price_include_override` | Selection | Tax-included pricing override |
| `invoice_repartition_line_ids` | One2many | How tax distributes on invoices |
| `refund_repartition_line_ids` | One2many | How tax distributes on refunds |
| `cash_basis_transition_account_id` | Many2one | Cash basis intermediate account |
| `country_id` | Many2one(`res.country`) | Country scope |

Colombian taxes loaded by `l10n_co`: IVA 19%, IVA 5%, IVA 0% (exempt), retention at source (Retefuente), ICA, Reteiva.

### 3.5 account.journal

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Journal name |
| `code` | Char(5) | Short code |
| `type` | Selection | `sale`, `purchase`, `cash`, `bank`, `general`, `credit` |
| `default_account_id` | Many2one(`account.account`) | Default debit/credit account |
| `company_id` | Many2one(`res.company`) | Company |
| `currency_id` | Many2one(`res.currency`) | Journal currency |
| `bank_account_id` | Many2one(`res.partner.bank`) | Linked bank account |

**POS integration:** Each POS config creates/uses a dedicated journal (type=`general` or `sale`) for session closing entries. Cash and bank payment methods each link to their own journal.

### 3.6 account.payment

| Field | Type | Notes |
|---|---|---|
| `payment_type` | Selection | `inbound` (customer), `outbound` (vendor) |
| `partner_type` | Selection | `customer`, `supplier` |
| `amount` | Monetary | Payment amount |
| `journal_id` | Many2one(`account.journal`) | Bank/cash journal |
| `payment_method_id` | Many2one(`account.payment.method`) | Method (manual, check, etc.) |
| `partner_id` | Many2one(`res.partner`) | Partner |
| `date` | Date | Payment date |
| `state` | Selection | `draft`, `posted`, `cancel` |

### 3.7 account.bank.statement / account.bank.statement.line

| Field | Type | Notes |
|---|---|---|
| `journal_id` | Many2one(`account.journal`) | Bank journal |
| `date` | Date | Statement date |
| `balance_start` / `balance_end_real` | Monetary | Opening/closing balance |
| `line_ids` | One2many(`account.bank.statement.line`) | Statement lines |

Bank reconciliation widget (account_accountant) matches statement lines with journal items.

### 3.8 account.reconcile.model

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Model name |
| `rule_type` | Selection | `writeoff_button`, `writeoff_suggestion`, `invoice_matching` |
| `match_journal_ids` | Many2many | Journals to apply |
| `line_ids` | One2many | Write-off lines template |

Used to automate reconciliation (e.g., bank fees, POS cash discrepancies).

### 3.9 account.fiscal.position

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Position name |
| `tax_ids` | One2many(`account.fiscal.position.tax`) | Tax mapping rules |
| `account_ids` | One2many(`account.fiscal.position.account`) | Account mapping rules |
| `auto_apply` | Boolean | Auto-detect by country/state |
| `country_id` | Many2one(`res.country`) | Target country |

Colombian setup: fiscal positions for exempt sales, exports, and special regimes.

### 3.10 account.payment.term

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Term name (e.g., "30 Days", "Immediate") |
| `line_ids` | One2many(`account.payment.term.line`) | Lines defining due date computation |

### 3.11 account.analytic.account / account.analytic.plan

Used for per-store cost tracking:

| Field (account) | Type | Notes |
|---|---|---|
| `name` | Char | Account name (e.g., "Tienda Norte", "Tienda Centro") |
| `plan_id` | Many2one(`account.analytic.plan`) | Parent plan |
| `code` | Char | Reference code |

| Field (plan) | Type | Notes |
|---|---|---|
| `name` | Char | Plan name (e.g., "Sucursales") |
| `parent_id` | Many2one | Hierarchical plans |

### 3.12 account.cash.rounding

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Rounding name |
| `rounding` | Float | Smallest denomination (e.g., 50 COP) |
| `strategy` | Selection | `biggest_tax` or `add_invoice_line` |
| `rounding_method` | Selection | `UP`, `DOWN`, `HALF-UP` |

---

## 4. Reports

### 4.1 Financial Reports (account_reports — dynamic, drillable)

| Report | Menu location | Percimon relevance | Notes |
|---|---|---|---|
| **Balance Sheet** | Reporting > Statement Reports | HIGH | Assets, liabilities, equity snapshot |
| **Profit and Loss** | Reporting > Statement Reports | HIGH | Revenue vs expense for period |
| **Cash Flow Statement** | Reporting > Statement Reports | HIGH | Cash movements (indirect method) |
| **Trial Balance** | Reporting > Ledgers | HIGH | Account balance summary |
| **General Ledger** | Reporting > Ledgers | HIGH | All transactions per account |
| **Partner Ledger** | Reporting > Partner Reports | MEDIUM | Per-partner transaction history |
| **Aged Receivable** | Reporting > Partner Reports | MEDIUM | Customer aging buckets |
| **Aged Payable** | Reporting > Partner Reports | MEDIUM | Vendor aging buckets |
| **Tax Report** | Reporting > Taxes & Fiscal | HIGH | Adapts to Colombian tax structure (IVA, ICA, Retefuente) |
| **Executive Summary** | Reporting > Management | MEDIUM | KPI dashboard (revenue, margin, cash) |
| **Invoice Analysis** | Reporting > Management | MEDIUM | Pivot view on invoices (revenue, count, avg) |
| **Journal Audit** | Review > Control | MEDIUM | Journal entry audit drilldown |
| **Bank Reconciliation** | (embedded in bank journal) | HIGH | Match bank lines with entries |
| **Deferred Revenues** | Review > Regularization | LOW | Revenue recognition over time |
| **Deferred Expenses** | Review > Regularization | MEDIUM | Expense recognition over time (e.g., rent) |
| **Multicurrency Revaluation** | Review > Regularization | LOW | FX gain/loss recognition |
| **Customer Statement** | (sent to partners) | MEDIUM | Partner-facing statement |
| **Follow-up Report** | (automated or manual) | MEDIUM | Overdue payment follow-up |

### 4.2 Colombian-Specific Reports (l10n_co_reports)

| Report | Description | Percimon relevance |
|---|---|---|
| **Certificado de Retenciones** | Retention certificate report | HIGH: required by tax law |
| **IVA Report** | Colombian IVA tax declaration | HIGH: bimonthly IVA filing |
| **ICA Report** | Industria y Comercio tax | MEDIUM: municipality-level tax |
| **Retefuente Report** | Retention at source | HIGH: withholding tax report |
| **Libro Diario** | Official daily journal book | HIGH: legal requirement |
| **Libro de Inventarios y Balances** | Inventory & balance book | MEDIUM: annual requirement |
| **Balance Sheet PYMES** | Balance sheet for SMEs (NIIF PYMES) | HIGH: Colombian IFRS for SMEs |
| **P&L PYMES** | P&L for SMEs | HIGH: Colombian IFRS for SMEs |
| **Trial Balance per Partner** | Trial balance broken down by partner | MEDIUM: audit support |

### 4.3 Print Reports (QWeb/PDF)

| Report | Model | Notes |
|---|---|---|
| **Invoice PDF** | `account.move` | Standard invoice layout (customizable) |
| **Payment Receipt** | `account.payment` | Payment confirmation |
| **Hash Integrity** | `account.move` | Inalterability verification report |
| **Bank Statement** | `account.bank.statement` | Statement summary |

---

## 5. Wizards

| Wizard | Technical model | Trigger | Percimon relevance |
|---|---|---|---|
| **Register Payment** | `account.payment.register` | Invoice form > Register Payment | HIGH: record customer/vendor payments |
| **Credit Note** (Reversal) | `account.move.reversal` | Invoice form > Credit Note | HIGH: refund/correction |
| **Lock Dates** | `account.change.lock.date` | Accounting > Closing | HIGH: period closing |
| **Send Invoice** | `account.move.send` | Invoice form > Send & Print | HIGH: email/print invoices |
| **Batch Send** | `account.move.send.batch` | Invoice list > Send batch | MEDIUM: bulk invoice sending |
| **Automatic Entries** | `account.automatic.entry.wizard` | Journal items > Automatic Entries | MEDIUM: deferrals, accruals |
| **Accrued Orders** | `account.accrued.orders.wizard` | Purchase/sale orders | MEDIUM: accrual entries |
| **Validate Entries** | `account.validate.account.move` | Journal entries list > Validate | MEDIUM: bulk posting |
| **Resequence** | `account.resequence.wizard` | Journal entries > Resequence | LOW: renumber entries |
| **Secure Entries** | `account.secure.entries.wizard` | Accounting > Closing | MEDIUM: hash chain entries |
| **Auto Reconcile** | `account.auto.reconcile.wizard` | Closing > Reconcile | MEDIUM: auto-match entries |
| **Reconcile** | `account.reconcile.wizard` | Manual reconciliation | HIGH: match payments to invoices |
| **Fiscal Year** | `account.fiscal.year` | Configuration | MEDIUM: define fiscal year dates |
| **Multicurrency Revaluation** | `account.multicurrency.revaluation.wizard` | Review > Regularization | LOW |
| **Report Export** | `account_reports.export.wizard` | Any dynamic report > Export | HIGH: export reports to Excel/PDF |
| **Merge Accounts** | `account.merge.wizard` | Chart of Accounts > Merge | LOW: consolidate duplicate accounts |
| **Return Creation** | `account.return.creation.wizard` | Tax Returns | HIGH: create/file tax returns |
| **Return Submission** | `account.return.submission.wizard` | Tax Returns | HIGH: submit returns |
| **Budget Split** | `budget.split.wizard` | Budget module | MEDIUM: split budget periods |

---

## 6. Companion Modules (Relevant to Percimon)

| Module | Technical name | Source | Auto-install | Percimon relevance | Notes |
|---|---|---|---|---|---|
| **Colombia - Accounting** | `l10n_co` | community | Yes (with `account` in CO) | CRITICAL | Colombian CoA (PUC), taxes (IVA 19%, 5%, exempt, Retefuente, ICA), fiscal positions, identification types (NIT, CC, CE, etc.) |
| **Colombia - EDI (Carvajal)** | `l10n_co_edi` | enterprise | Yes (with `l10n_co`) | HIGH | Electronic invoicing fields, tax types, UNSPSC product codes, city/state data. Depends on `account_edi`, `l10n_co`, `product_unspsc`, `base_address_extended` |
| **Colombia - DIAN EDI** | `l10n_co_dian` | enterprise | Yes (with `l10n_co_edi`) | HIGH | DIAN electronic invoice submission (UBL 2.1), operation modes, certificates, CUFE/CUDE generation |
| **Colombia - Accounting Reports** | `l10n_co_reports` | enterprise | Yes (with `l10n_co` + `account_reports`) | HIGH | IVA, ICA, Retefuente reports, Libro Diario, Balance PYMES, P&L PYMES |
| **Colombia - POS** | `l10n_co_pos` | community | Yes (with `l10n_co` + POS) | HIGH | Colombian POS receipt requirements |
| **Accounting Reports** | `account_reports` | enterprise | Yes (with `account_accountant`) | CRITICAL | All dynamic financial reports (BS, P&L, Cash Flow, GL, TB, Tax Report) |
| **Invoicing Enterprise** | `account_accountant` | enterprise | Yes (with `account`) | CRITICAL | Bank reconciliation widget, lock dates, fiscal years, reconciliation wizard |
| **Budget Management** | `account_budget` | enterprise | No (manual install) | HIGH | Budget lines vs analytic accounts, budget compliance reports, split wizard |
| **Debit Notes** | `account_debit_note` | community | dep of `l10n_co` | HIGH | Debit note creation (required in Colombian accounting) |
| **LATAM Base** | `l10n_latam_base` | community | dep of `l10n_co` | HIGH | LATAM identification types, document types framework |
| **Product Margin** | `product_margin` | community | No (manual) | MEDIUM | Invoice-based product margin analysis |
| **Account EDI** | `account_edi` | community | dep of `l10n_co_edi` | HIGH | EDI document framework |
| **Payment Follow-up** | (in `account_reports`) | enterprise | auto | MEDIUM | Automated payment reminders |

---

## 7. Security Groups

| Group | XML ID | Role | Percimon mapping |
|---|---|---|---|
| **Invoicing** | `account.group_account_invoice` | Create/edit invoices, payments | Cashiers, Store Managers |
| **Basic** | `account.group_account_basic` | Basic bank recon, additional features | Store Manager |
| **Show Readonly** | `account.group_account_readonly` | View-only accounting access | Regional Manager |
| **Accountant** | `account.group_account_user` | Full accounting (entries, reports, recon) | Accountant |
| **Administrator** | `account.group_account_manager` | Configuration, lock dates, advanced | Finance Director |
| **Show Inalterability** | `account.group_account_secured` | Hash integrity features | Accountant, Auditor |
| **Cash Rounding** | `account.group_cash_rounding` | Cash rounding management | Enabled globally |

With `accountant` installed, the group hierarchy is:
```
group_account_invoice -> group_account_basic -> group_account_readonly -> group_account_user -> group_account_manager
```

---

## 8. POS-to-Accounting Flow (Percimon-Specific)

This is the critical integration path for a frozen yogurt chain:

### 8.1 Session Closing Flow
1. **POS Session Close** -> Creates `account.move` (type=`entry`) in the POS journal
2. **Session entry contains lines for:**
   - Revenue lines (per product category/tax combination) -> income accounts
   - Tax lines (IVA 19%) -> tax payable accounts
   - Payment lines (cash, card, etc.) -> payment method journal accounts
   - Cash difference (over/short) -> cash discrepancy account (configurable on journal)
3. **Cash Control:** If enabled on POS config, cashier must declare closing balance. Difference posts to a dedicated P&L account.

### 8.2 Cash Discrepancy Reporting
- Cash differences appear as lines in the POS session closing entry
- Trackable via **General Ledger** filtered on the cash discrepancy account
- Can also be monitored via **Analytic Report** if analytic accounts are set per store
- **Journal Audit** report (account_reports) allows drilling into POS session entries

### 8.3 COGS (Cost of Goods) Management
- Requires `stock_account` (inventory valuation -> accounting)
- Product categories with `property_valuation = 'real_time'` auto-post COGS entries
- COGS appears in P&L under expense accounts
- **Margin Analysis** (product_margin module) compares sale price vs cost from invoices

### 8.4 Budget Compliance
- `account_budget` module: define budget lines per analytic account (store) and account group
- Compare actual (from posted entries) vs budgeted amounts
- Budget report accessible via Reporting menu
- Can set warning thresholds

---

## 9. Colombian Tax Regime Summary

| Tax | Rate | Type | Report |
|---|---|---|---|
| IVA (general) | 19% | Sale + Purchase | IVA Report (bimonthly) |
| IVA (reduced) | 5% | Sale + Purchase | IVA Report |
| IVA (exempt) | 0% | Sale + Purchase | IVA Report |
| Retefuente | 2.5%-11% (varies) | Withholding on purchase | Retefuente Report |
| Reteiva | 15% of IVA | Withholding on IVA | Reteiva section |
| ICA | varies by municipality | Industry & commerce | ICA Report |
| Autorretención | varies | Self-retention (special regime) | Separate declaration |

The `l10n_co` localization pre-configures these taxes. The `l10n_co_reports` module provides the declaration forms.

---

## 10. Features to Demo (Recommended for Percimon)

| Feature | Priority | Why |
|---|---|---|
| Invoice posting (customer invoice with IVA 19%) | HIGH | Core invoicing flow |
| POS session close -> accounting entry | HIGH | Daily operations flow |
| Cash control & discrepancy reporting | HIGH | Cash management per store |
| Bank reconciliation | HIGH | Match bank statements with entries |
| Tax Report (IVA) | HIGH | Bimonthly tax obligation |
| P&L report | HIGH | Profitability analysis |
| Balance Sheet | HIGH | Financial position |
| Budget vs actual (per store) | HIGH | Budget compliance |
| Analytic accounting (per store) | HIGH | Cost/revenue per location |
| Aged Receivable/Payable | MEDIUM | Cash flow management |
| Payment registration & follow-up | MEDIUM | AR management |
| General Ledger | MEDIUM | Audit trail |
| Cash rounding (COP) | MEDIUM | POS cash handling |
| Debit note creation | MEDIUM | Colombian requirement |
| Electronic invoicing (DIAN) | HIGH | Legal requirement for electronic invoices |

## 11. Settings to Enable

| Setting | Value | Notes |
|---|---|---|
| `chart_template` | `co` | Colombian localization |
| `currency_id` | COP | Colombian Peso |
| `account_fiscal_country_id` | Colombia | Tax report structure |
| `sale_tax_id` | IVA 19% (auto from l10n_co) | Default sales tax |
| `purchase_tax_id` | IVA 19% (auto from l10n_co) | Default purchase tax |
| `group_analytic_accounting` | True | Per-store tracking |
| `module_account_budget` | True | Budget management |
| `group_cash_rounding` | True | COP rounding |
| `group_uom` | True | Units of measure |
| `display_invoice_amount_total_words` | True | Amount in words (common in CO) |
| `account_price_include` | `tax_excluded` | Standard B2B; POS handles display separately |
| `module_product_margin` | True | COGS analysis |
