# Feature Catalog: Point of Sale (`point_of_sale`)

**Odoo Version:** 19.0
**Client:** Percimon -- Colombian frozen yogurt chain (Medellin, Bogota, Cartagena)
**Module technical name:** `point_of_sale`
**Category:** Sales/Point of Sale
**Dependencies:** resource, stock_account, barcodes, html_editor, digest, phone_validation, partner_autocomplete, iot_base, google_address_autocomplete

---

## 1. Menu Structure

### Top-level menu: Point of Sale

| Menu path | Action / Model | Notes |
|---|---|---|
| Point of Sale > Dashboard | `pos.config` (kanban) | Main landing page -- kanban cards per POS config showing session status, cash balance, orders |
| Point of Sale > Orders > Customers | `res.partner` | Customer list (shared with Accounting) |
| Point of Sale > Reporting > Session Report | `pos.daily.sales.reports.wizard` | Per-session daily sales report |
| Point of Sale > Reporting > Orders | `report.pos.order` (graph/pivot) | Orders Analysis -- pivot/graph with product category, date, amounts |
| Point of Sale > Reporting > Sales Details | `pos.details.wizard` | Date-range sales details report across multiple POS configs |
| Point of Sale > Configuration > Settings | `res.config.settings` | Per-POS-config settings (select which POS config to edit) |
| Point of Sale > Configuration > Products > PoS Product Categories | `pos.category` | Hierarchical categories for POS product display |
| Point of Sale > Configuration > Products > Product Attributes | `product.attribute` | (shared, visible with product variants group) |
| Point of Sale > Configuration > Point of Sales | `pos.config` (list) | List view of all POS configurations |

---

## 2. Settings / Feature Flags

Settings are per `pos.config` record (selected via dropdown in Settings page).

### Block: Point of Sale
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Bar/Restaurant mode | `pos_module_pos_restaurant` | YES -- dine-in stores need tables/floors | YES |
| Presets (Take out / Delivery / Members) | `pos_use_presets` | YES -- take-out vs dine-in tax handling, employee discounts as a preset | YES |
| Available/Default Presets | `pos_available_preset_ids`, `pos_default_preset_id` | Configure "Dine-in", "Take-out", "Employee" presets | YES |

### Block: Payment
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Payment Methods | `pos_payment_method_ids` | YES -- cash, card, QR code payments | YES |
| Automatically validate terminal payment | `pos_auto_validate_terminal_payment` | YES -- speed up checkout | YES |
| Cash Rounding | `pos_cash_rounding` | YES -- Colombian peso rounding (50 COP) | YES |
| Rounding Method | `pos_rounding_method` | Configure for COP | YES |
| Only round cash method | `pos_only_round_cash_method` | YES | YES |
| One-click Payment (Fast Payment) | `pos_use_fast_payment` | YES -- speed up common transactions | YES |
| Fast Payment Methods | `pos_fast_payment_method_ids` | Link to cash method for quick sales | YES |
| Maximum Cash Difference | `pos_set_maximum_difference` | YES -- cash discrepancy threshold for shift closing | YES |
| Authorized Difference Amount | `pos_amount_authorized_diff` | Set tolerance (e.g., 5000 COP) | YES |
| Tips | `pos_iface_tipproduct` | Optional -- frozen yogurt shops may not need tips | NO |

### Block: PoS Interface
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Log in with Employees | `pos_module_pos_hr` | YES -- employee login per shift, track who sold what | YES |
| Large Scrollbars | `pos_iface_big_scrollbars` | Useful for touchscreen terminals | MAYBE |
| Share Open Orders (Trusted POS) | `pos_trusted_config_ids` | YES -- share orders between registers in same store | YES |
| Show Product Images | `pos_show_product_images` | YES -- frozen yogurt products look appealing | YES |
| Show Category Images | `pos_show_category_images` | YES | YES |
| Booking (Online Appointment) | `pos_module_pos_appointment` | NO -- not relevant for yogurt chain | NO |
| Group products by categories | `pos_iface_group_by_categ` | YES -- organize by Yogurt, Toppings, Drinks, etc. | YES |

### Block: Product & PoS Categories
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Restrict Categories | `pos_limit_categories` | YES -- limit categories per store type | MAYBE |
| Available PoS Product Categories | `pos_iface_available_categ_ids` | Per-store category filtering | MAYBE |
| Show Margins & Costs | `pos_is_margins_costs_accessible_to_every_user` | Manager-only feature | NO |

### Block: Accounting
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Default Sales Tax | `sale_tax_id` | YES -- Colombian IVA (19%) | YES |
| Flexible Taxes (Fiscal Positions) | `pos_tax_regime_selection` | YES -- dine-in vs take-out tax (or use Presets instead) | MAYBE |
| Default Journals (Orders / Invoices) | `pos_journal_id`, `pos_invoice_journal_id` | Standard setup | YES |
| Closing Entry by Product | `pos_is_closing_entry_by_product` | YES -- breakdown sales by product in closing entry | YES |
| Order Edit Tracking | `pos_order_edit_tracking` | YES -- audit trail for corrections | YES |

### Block: Pricing
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Flexible Pricelists | `pos_use_pricelist` | YES -- employee discount pricelist, happy hour pricing | YES |
| Available/Default Pricelist | `pos_available_pricelist_ids`, `pos_pricelist_id` | "Employee Discount", "Regular" pricelists | YES |
| Price Control (restrict to managers) | `pos_restrict_price_control` | YES -- prevent cashiers from changing prices | YES |
| Product Prices (Tax-Included/Excluded) | `pos_iface_tax_included` | YES -- Colombia typically shows tax-included | YES |
| Manual Discount (per line) | `pos_manual_discount` | YES -- employee discounts, loyalty | YES |
| Global Discounts | `pos_module_pos_discount` | YES -- apply % discount to entire order | YES |
| Promotions, Coupons, Gift Cards & Loyalty | `module_loyalty` (installs `pos_loyalty`) | YES -- loyalty program for repeat customers | YES |

### Block: Bills & Receipts
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Custom Header & Footer | `pos_is_header_or_footer` | YES -- store branding on receipts | YES |
| Receipt Header/Footer | `pos_receipt_header`, `pos_receipt_footer` | "Percimon -- Frozen Yogurt" + return policy | YES |
| Automatic Receipt Printing | `pos_iface_print_auto` | YES -- speed up checkout | YES |
| SMS Receipt | `pos_module_pos_sms` | MAYBE -- digital receipt option | MAYBE |
| Ticket QR Code (Portal) | `point_of_sale_use_ticket_qr_code` | YES -- digital invoice access | YES |
| Basic Receipt (gift mode) | `pos_basic_receipt` | NO | NO |

### Block: Payment Terminals
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Mercado Pago | `module_pos_mercado_pago` | YES -- popular in Colombia/LatAm for QR payments | YES |
| Stripe | `module_pos_stripe` | MAYBE -- alternative terminal | MAYBE |
| Adyen | `module_pos_adyen` | NO -- not common in Colombia | NO |

### Block: Connected Devices
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| ePos Printer | `pos_other_devices` | YES -- receipt printers without IoT Box | YES |
| Customer Display | `pos_customer_display_bg_img` | YES -- show order to customer on second screen | YES |
| IoT Box | `pos_is_posbox` | MAYBE -- if stores use barcode scanners/scales | MAYBE |

### Block: Preparation
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Preparation Printers (Order Printer) | `pos_is_order_printer` | YES -- send topping/combo orders to prep station | YES |
| Printer configuration | `pos_printer_ids` | Link to kitchen/prep printer | YES |
| Internal Notes | (always available) | YES -- "extra chocolate", "no nuts" modifiers | YES |
| Note Models | `pos_note_ids` | Pre-defined notes: "Sin azucar", "Extra toppings", "Sin lactosa" | YES |

### Block: Inventory
| Setting | Field | Percimon relevance | Demo? |
|---|---|---|---|
| Operation Type | `pos_picking_type_id` | Standard inventory deduction | YES |
| Ship Later | `pos_ship_later` | NO -- immediate consumption | NO |
| Barcodes | `barcode_nomenclature_id` | YES -- barcode scanning for products | YES |

---

## 3. Key Models

| Model | Description | Key fields | Percimon relevance |
|---|---|---|---|
| `pos.config` | POS terminal configuration | name, payment_method_ids, use_presets, module_pos_hr, cash_control, amount_authorized_diff, manual_discount, use_pricelist, is_order_printer, printer_ids, note_ids | Core -- one config per store (or register) |
| `pos.session` | Daily session (open/close) | config_id, state (opening_control/opened/closing_control/closed), cash_register_balance_start, cash_register_balance_end_real, cash_register_difference, opening_notes, closing_notes | Core -- shift management, cash control |
| `pos.order` | Sales transaction | session_id, partner_id, date_order, amount_total, state, payment_ids, lines, fiscal_position_id, preset_id | Core -- every sale |
| `pos.order.line` | Order line | order_id, product_id, qty, price_unit, discount, price_subtotal_incl, combo_id | Core |
| `pos.payment` | Payment record per order | pos_order_id, amount, payment_method_id, card_type, card_brand, transaction_id | Core -- split payments (card + QR) |
| `pos.payment.method` | Payment method definition | name, is_cash_count, journal_id, split_transactions, use_payment_terminal, type (cash/bank/pay_later), image | Core -- Cash, Card, QR Code |
| `pos.category` | Product categories for POS display | name, parent_id, sequence, image_512, color, hour_after, hour_until | Core -- Yogurt, Toppings, Combos, Drinks |
| `pos.preset` | Order presets (dine-in/take-out/etc.) | name, pricelist_id, fiscal_position_id, identification, is_return, color, use_timing, slots_per_interval | YES -- "Dine-in", "Take-out", "Employee Discount" |
| `pos.note` | Pre-defined order line notes | name, sequence, color | YES -- preparation instructions |
| `pos.bill` | Cash denomination definitions | name, value | YES -- COP bills (1000, 2000, 5000, 10000, 20000, 50000, 100000) |
| `pos.printer` | Order printers (kitchen/prep) | name, proxy_ip, product_categories_ids | YES -- prep station printers |
| `product.combo` | Combo group (POS-extended) | name, combo_item_ids, base_price, qty_max, qty_free | YES -- frozen yogurt combos with toppings |
| `product.combo.item` | Combo item | combo_id, product_id, extra_price | YES -- individual topping choices |
| `report.pos.order` | Orders Analysis (SQL view) | date, product_id, price_total, margin, payment_method_id, config_id, session_id | YES -- sales reporting |

---

## 4. Reports

| Report | Type | Access | Percimon relevance |
|---|---|---|---|
| **Orders Analysis** | Pivot/Graph (BI view `report.pos.order`) | Reporting > Orders | YES -- sales by product, category, payment method, date |
| **Sales Details** | Wizard-generated PDF (`pos.details.wizard`) | Reporting > Sales Details | YES -- date range, multi-POS summary |
| **Session Report** | Per-session PDF (`pos.daily.sales.reports.wizard`) | Reporting > Session Report | YES -- daily closing report |
| **Sale Details Report** | QWeb PDF (`point_of_sale.sale_details_report`) | From wizard | YES -- printed session closing report |
| **POS Invoice** | QWeb PDF (`report.point_of_sale.report_invoice`) | From order | YES -- customer invoices |
| **Receipt** | POS UI receipt (JS-rendered) | Printed at POS | YES -- customer receipt with header/footer |
| **User Labels** | QWeb PDF (`report_userlabel`) | From product | MAYBE -- price tags |

---

## 5. Wizards

| Wizard | Model | Purpose | Percimon relevance |
|---|---|---|---|
| Sales Details | `pos.details.wizard` | Generate sales detail report for date range + selected POS configs | YES -- daily/weekly review |
| Session Report | `pos.daily.sales.reports.wizard` | Generate report for a specific session | YES -- shift closing |
| Close Session | `pos.close.session.wizard` | Handle cash difference at closing (balance amount, destination account) | YES -- cash discrepancy workflow |
| Payment | `pos.payment.wizard` (via `pos_payment.xml`) | Register payment from backend | Standard |
| Make Invoice | `pos.make.invoice` (via `pos_make_invoice.xml`) | Create invoice from POS order | YES -- for B2B customers |
| Confirmation | `pos.confirmation.wizard` | Generic confirmation dialog | Standard |

---

## 6. Companion Modules (relevant to Percimon)

### Must-install

| Module | Technical name | Why |
|---|---|---|
| **POS - HR (Employee Login)** | `pos_hr` | Employee login with PIN/badge, track sales per employee, per-employee sales reports. Auto-installs with HR. |
| **POS Discounts** | `pos_discount` | Global percentage discount button (employee discounts). |
| **POS Loyalty** | `pos_loyalty` | Loyalty programs, coupons, gift cards for repeat customers. Auto-installs with `loyalty`. |
| **Restaurant** | `pos_restaurant` | Floor plans, table management for dine-in stores (Medellin, Cartagena). |
| **POS Self Order** | `pos_self_order` | QR-code self-ordering from phone (auto-installs with `pos_restaurant`). Customer scans QR at table to order. |
| **Colombian POS Localization** | `l10n_co_pos` | Colombian fiscal compliance. Auto-installs with `l10n_co` + `point_of_sale`. |

### Recommended

| Module | Technical name | Why |
|---|---|---|
| **POS - Sales** | `pos_sale` | Link POS orders to Sales module, quotation-to-POS flow. Auto-installs. |
| **POS Online Payment** | `pos_online_payment` | Accept online payments (Nequi, Daviplata via payment providers). Auto-installs with `account_payment`. |
| **POS Mercado Pago** | `pos_mercado_pago` | QR-based payment terminal -- popular in LatAm. |

### Not needed

| Module | Why skip |
|---|---|
| `pos_adyen`, `pos_stripe`, `pos_razorpay`, `pos_pine_labs`, `pos_qfpay`, `pos_viva_com` | Not used in Colombia |
| `pos_appointment` | No booking needed for yogurt shops |
| `pos_mrp` | No manufacturing at POS |
| `pos_repair` | No repair service |
| `pos_event`, `pos_event_sale` | No event ticketing |

---

## 7. Demo Data & Scenarios

The module ships with three demo scenarios loaded via `load_onboarding_*_scenario` methods on `pos.config`:
- **Furniture scenario** -- furniture store with products
- **Clothes scenario** -- clothing store
- **Bakery scenario** -- bakery with categories and products

Each scenario has its own category data (`*_category_data.xml`) and product data (`*_data.xml`) under `data/scenarios/`.

**For Percimon demo, we will NOT use the built-in scenarios.** Instead we create custom data:
- POS categories: Yogurt Base, Toppings, Sauces, Combos, Drinks, Snacks
- Products: Small/Medium/Large yogurt, 15+ toppings, combo meals
- Combos: "Classic Combo" (yogurt + 3 toppings), "Premium Combo" (yogurt + 5 toppings + drink)
- Payment methods: Cash (COP), Card (Visa/MC), QR (Nequi/Daviplata)
- Presets: "Dine-in", "Take-out", "Employee Discount"
- Notes: "Sin azucar", "Extra toppings", "Sin lactosa", "Sin frutos secos"
- Bills: 1000, 2000, 5000, 10000, 20000, 50000, 100000 COP

---

## 8. Features to Demo (Percimon-specific)

### Priority 1 -- Core workflow
1. **Combo products with toppings as modifiers** -- Create `product.combo` groups with `product.combo.item` entries (yogurt base + topping selections with extra prices). Uses `qty_max` and `qty_free` fields in v19.
2. **Split payments (QR + Card)** -- Configure multiple `pos.payment.method` records. Show a sale split between Nequi QR and card terminal.
3. **Employee login** -- Enable `pos_hr`, configure employees with POS PINs. Show login/switch flow.
4. **Session opening & closing with cash control** -- Open session with starting balance, process orders, close with cash count. Show `cash_register_difference` and `amount_authorized_diff` enforcement.
5. **POS Presets (Dine-in / Take-out / Employee)** -- Configure `pos.preset` records with different pricelists and fiscal positions. Show preset selection at order creation.

### Priority 2 -- Operational
6. **Preparation notes** -- Add notes to order lines ("Sin azucar", custom text). Configure `pos.note` models.
7. **Order printers** -- Configure prep station printer for topping/combo preparation tickets.
8. **Manual & global discounts** -- Line discount for ad-hoc adjustments. Global discount via `pos_discount` module for employee discount scenario.
9. **Pricelist-based employee discount** -- Create "Employee 20%" pricelist, link to "Employee" preset.
10. **Cash rounding** -- Configure COP rounding (50 COP) for cash payments.

### Priority 3 -- Reporting & Management
11. **Session closing report** -- Print/view session closing details showing payments by method, cash balance, discrepancies.
12. **Orders Analysis** -- Pivot/graph report showing sales by product, category, payment method, store (config).
13. **Sales Details report** -- Date-range summary across all stores.
14. **Order edit tracking** -- Enable to track corrections/modifications.
15. **Closing entry by product** -- Enable for granular accounting.

### Priority 4 -- Enhanced experience
16. **Customer Display** -- Configure background image showing Percimon branding.
17. **Receipt customization** -- Header: "Percimon -- Frozen Yogurt", Footer: return policy / social media.
18. **Product & category images** -- Appealing frozen yogurt product photos in POS interface.
19. **Self-ordering (QR at table)** -- For dine-in stores, customers scan QR to browse menu and order from phone (via `pos_self_order`).
20. **Loyalty program** -- Stamp card or points program for repeat customers (via `pos_loyalty`).

---

## 9. Settings to Enable (res.config.settings)

```
# Per POS config
pos_module_pos_hr: True
pos_module_pos_restaurant: True  # dine-in stores only
pos_module_pos_discount: True
pos_use_presets: True
pos_use_pricelist: True
pos_restrict_price_control: True
pos_manual_discount: True
pos_cash_rounding: True
pos_only_round_cash_method: True
pos_set_maximum_difference: True
pos_amount_authorized_diff: 5000  # COP
pos_iface_tax_included: 'total'
pos_is_order_printer: True
pos_is_header_or_footer: True
pos_receipt_header: "Percimon - Frozen Yogurt"
pos_receipt_footer: "Gracias por tu visita! @percimon"
pos_iface_print_auto: True
pos_show_product_images: True
pos_show_category_images: True
pos_iface_group_by_categ: True
pos_is_closing_entry_by_product: True
pos_order_edit_tracking: True
point_of_sale_use_ticket_qr_code: True
pos_use_fast_payment: True

# Global
module_loyalty: True
module_pos_mercado_pago: True  # if using QR payments
```

---

## 10. Identity Keys (for CSV data loading)

| Model | Identity key(s) | Notes |
|---|---|---|
| `pos.config` | `name` | One per store/register |
| `pos.category` | `name` | Category names are unique |
| `pos.payment.method` | `name` | Payment method names |
| `pos.preset` | `name` | Preset names |
| `pos.note` | `name` | DB unique constraint on name |
| `pos.bill` | `value` | Denomination value |
| `pos.printer` | `name` | Printer names |
| `product.combo` | `name` | Combo group names |
| `product.combo.item` | `combo_id` + `product_id` | Compound key |
