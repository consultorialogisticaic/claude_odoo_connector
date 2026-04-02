# Feature Catalog: Purchase

- **App**: Purchase
- **Technical name**: `purchase`
- **Version**: 19.0 (module v1.2)
- **Category**: Supply Chain / Purchase
- **Summary**: Purchase orders, tenders and agreements
- **Depends**: `account`
- **Source**: Community (odoo/odoo)

---

## 1. Menu Structure

```
Purchase (menu_purchase_root)
├── Orders (menu_procurement_management)
│   ├── Requests for Quotation        → purchase.order (domain: quotation_only context)
│   ├── Purchase Orders               → purchase.order (domain: state = purchase)
│   └── Vendors                       → res.partner (supplier action from account)
├── Products (menu_purchase_products)
│   ├── Products                      → product.template (filter: Can be Purchased)
│   └── Product Variants              → product.product (group: product.group_product_variant)
├── Reporting (purchase_report_main)   [group: group_purchase_manager]
│   └── Purchase                      → purchase.report (pivot/graph)
└── Configuration (menu_purchase_config) [group: group_purchase_manager]
    ├── Settings                      → res.config.settings
    ├── Vendor Pricelists             → product.supplierinfo
    └── Products
        ├── Attributes                → product.attribute (group: group_product_variant)
        ├── Product Categories        → product.category
        └── Units & Packagings        → uom.uom (group: group_uom)
```

---

## 2. Settings (res.config.settings)

### Orders
| Setting | Field / Module | Description | Percimon relevance |
|---|---|---|---|
| Purchase Order Approval | `po_order_approval` + `po_double_validation_amount` | Require manager approval above a threshold | HIGH -- control large raw-material orders |
| Lock Confirmed Orders | `lock_confirmed_po` | Auto-lock confirmed POs to prevent edits | MEDIUM |
| Warnings | `group_warning_purchase` | Warnings on products or vendors in orders | LOW |
| Purchase Agreements | `module_purchase_requisition` | Blanket orders and purchase templates | MEDIUM -- recurring supplier contracts for fruit/packaging |
| Receipt Reminders | `group_send_reminder` | Auto email vendors before expected receipt date | HIGH -- perishable goods need timely delivery |

### Invoicing
| Setting | Field / Module | Description | Percimon relevance |
|---|---|---|---|
| 3-Way Matching | `module_account_3way_match` (Enterprise) | Only pay bills for received goods | HIGH -- verify fruit/topping receipts before payment |

### Products
| Setting | Field / Module | Description | Percimon relevance |
|---|---|---|---|
| Product Variants | `group_product_variant` | Purchase variants using attributes | LOW -- raw materials unlikely to have variants |
| Variant Grid Entry | `module_purchase_product_matrix` | Add variants via grid in PO | LOW |
| Units of Measure | `group_uom` | Purchase in different UoMs | HIGH -- kg, liters, units, boxes |

---

## 3. Key Models

### Core transactional models

| Model | Description | Key fields for Percimon |
|---|---|---|
| `purchase.order` | Purchase order / RFQ | `partner_id`, `date_order`, `date_planned`, `state` (draft/sent/to approve/purchase/cancel), `order_line`, `currency_id`, `fiscal_position_id`, `payment_term_id`, `incoterm_id`, `amount_untaxed`, `amount_tax`, `amount_total`, `invoice_status`, `priority`, `origin`, `partner_ref`, `locked`, `note` |
| `purchase.order.line` | PO line items | `product_id`, `name`, `product_qty`, `product_uom_id`, `price_unit`, `discount`, `tax_ids`, `date_planned`, `price_subtotal`, `price_total`, `qty_invoiced`, `invoice_lines` |

### Analytical / reporting models

| Model | Description |
|---|---|
| `purchase.report` | Pivot/graph analysis -- date, vendor, product, category, buyer, amounts, days-to-confirm, days-to-receive |
| `purchase.bill.union` | Union view of POs + vendor bills for cross-reference |
| `purchase.bill.line.match` | PO line vs. bill line matching view (qty, amounts, state) |

### Extended models (purchase adds fields)

| Model | Fields added |
|---|---|
| `res.partner` | `property_purchase_currency_id`, `receipt_reminder_email`, `reminder_date_before_receipt`, `buyer_id`, `purchase_warn_msg`, `purchase_order_count` |
| `product.template` | `purchased_product_qty`, `purchase_method` (on ordered / on received quantities), `purchase_line_warn_msg` |
| `account.move` | Purchase-related invoice fields (vendor bill link) |

---

## 4. Workflows and State Machine

### Purchase Order lifecycle

```
Draft (RFQ)  ──Send──▸  RFQ Sent  ──Confirm──▸  Purchase Order
                                   └─(approval required)──▸  To Approve ──Approve──▸ Purchase Order
Purchase Order ──Create Bill──▸  Vendor Bill (account.move)

Any state ──Cancel──▸  Cancelled
```

### Invoice status (on confirmed PO)
- `no` -- Nothing to Bill
- `to invoice` -- Waiting Bills
- `invoiced` -- Fully Billed

### Product control policy (`purchase_method`)
- **On ordered quantities** -- bill matches ordered qty (services default)
- **On received quantities** -- bill matches received qty (stockable/consumable default)

---

## 5. Reports (PDF)

| Report | Template | When printed |
|---|---|---|
| Purchase Order | `purchase.report_purchaseorder` | State = purchase (confirmed PO) |
| Request for Quotation | `purchase.report_purchasequotation` | State = draft or sent (RFQ) |

---

## 6. Wizards

| Wizard | Model | Purpose |
|---|---|---|
| Bill to PO | `bill.to.po.wizard` | Create or link a vendor bill line to a PO; also handles down-payments |

---

## 7. Security Groups

| Group | XML ID | Description |
|---|---|---|
| Purchase User | `purchase.group_purchase_user` | Basic purchase access |
| Purchase Administrator | `purchase.group_purchase_manager` | Full purchase config + reporting |
| Purchase Warnings | `purchase.group_warning_purchase` | Enable product/vendor warnings |
| Receipt Reminders | `purchase.group_send_reminder` | Enable auto-receipt reminder emails |

---

## 8. Companion Modules

### Community (odoo/odoo)

| Module | Technical name | Depends on | Percimon relevance |
|---|---|---|---|
| **Purchase Stock** | `purchase_stock` | `stock_account`, `purchase` | **CRITICAL** -- links POs to stock receipts (picking), enables receive flow, partial receipts |
| Purchase Agreements | `purchase_requisition` | `purchase` | MEDIUM -- blanket orders for recurring raw-material suppliers |
| Purchase Requisition Stock | `purchase_requisition_stock` | `purchase_requisition`, `purchase_stock` | MEDIUM -- agreements + stock integration |
| Purchase Matrix | `purchase_product_matrix` | `purchase`, `product_matrix` | LOW -- variant grid entry |
| Purchase MRP | `purchase_mrp` | `mrp`, `purchase_stock` | LOW (unless Percimon uses MRP for yogurt production) |
| Purchase Repair | `purchase_repair` | `repair`, `purchase_stock` | NOT NEEDED |
| Purchase EDI UBL BIS3 | `purchase_edi_ubl_bis3` | `purchase`, `account_edi_ubl_cii` | NOT NEEDED for Colombia |

### Enterprise (odoo/enterprise)

| Module | Technical name | Depends on | Percimon relevance |
|---|---|---|---|
| Purchase Accountant | `purchase_accountant` | `purchase`, `account_accountant` | MEDIUM -- bridge for full accounting |
| Purchase Intrastat | `purchase_intrastat` | `purchase`, `account_intrastat` | NOT NEEDED (intra-EU only) |

---

## 9. Demo Data Patterns

The `purchase_demo.xml` creates:

- **10 purchase orders** (purchase_order_1 through purchase_order_10):
  - Orders 1-7: state `draft` (RFQs), various vendors (res_partner_1, 3, 4, 12, 2), 1-3 lines each
  - Order 4: state overridden to `sent`
  - Orders 8-10: state `purchase` (confirmed), with `date_approve` and `create_date` set in the past
- **4 mail activities** on orders 2, 5, 6, 7 (reminders, to-dos)
- **3 partners** updated with `receipt_reminder_email = True`
- Line items reference standard Odoo demo products (`product_delivery_01`, `product_product_25`, etc.)
- Prices range from 25.50 to 2010.00; quantities from 3 to 20
- UoMs: `product_uom_unit`, `product_uom_hour`, `product_uom_dozen`
- `date_planned` offsets: today, +1d, +3d, +5d

---

## 10. Percimon-Specific Recommendations

### Features to demo
1. **Vendor creation** with purchase currency (COP), receipt reminders, buyer assignment, tax attributes
2. **RFQ workflow** -- create RFQ for fruit supplier, send, receive response, confirm to PO
3. **Purchase Order confirmation** with approval threshold (e.g., orders above 5M COP need manager approval)
4. **Vendor bills** -- create bill from PO, show billing status progression
5. **Purchase reporting** -- pivot by vendor, product category, time period
6. **Units of Measure** -- buy fruit in kg, toppings in units, sauces in liters, packaging in boxes

### Settings to enable
- `group_uom` = True (units of measure)
- `group_send_reminder` = True (receipt reminders -- perishable goods)
- `po_order_approval` = True, `po_double_validation_amount` = 5000000 (COP threshold)
- `lock_confirmed_po` = True

### Critical companion: `purchase_stock`
Without `purchase_stock`, the purchase app handles only financial flow (PO to bill). For Percimon's need to receive fruit, toppings, and packaging into warehouse, `purchase_stock` is mandatory. It adds:
- Receipt (stock.picking) creation from confirmed PO
- Partial receipt support
- Incoming shipment tracking
- Stock valuation on receipt

### Models to populate for demo

| Priority | Model | Example data |
|---|---|---|
| 1 | `res.partner` (vendors) | Frutas del Valle, Empaques Colombia, Salsas y Toppings SAS |
| 2 | `product.category` | Raw Materials / Fruits, Raw Materials / Toppings, Packaging |
| 3 | `product.template` | Strawberry Pulp (kg), Mango Pulp (kg), Yogurt Cups 12oz (unit), Chocolate Sauce (liter) |
| 4 | `product.supplierinfo` | Vendor pricelists with lead times |
| 5 | `purchase.order` | Mix of RFQs and confirmed POs across vendors |
