# Feature Catalog: Inventory (stock) -- Odoo 19.0

**App**: Inventory (`stock`)
**Version**: 19.0
**Category**: Supply Chain/Inventory
**Dependencies**: `product`, `barcodes_gs1_nomenclature`, `digest`

---

## 1. Menu Structure

```
Inventory (menu_stock_root)
+-- Operations (menu_stock_warehouse_mgmt)
|   +-- Transfers (menu_stock_transfers)
|   |   +-- Receipts (in_picking)                   -> action_picking_tree_incoming
|   |   +-- Deliveries (out_picking)                -> action_picking_tree_outgoing
|   |   +-- Internal (int_picking)                  -> action_picking_tree_internal
|   +-- Adjustments (menu_stock_adjustments)
|   |   +-- Physical Inventory (menu_action_inventory_tree) -> action_view_inventory_tree
|   |   +-- Scrap (menu_stock_scrap)                -> action_stock_scrap
|   +-- Procurement (menu_stock_procurement)
|       +-- Replenishment (menu_reordering_rules_replenish) -> action_orderpoint_form
|       +-- Run Scheduler (menu_procurement_compute)
+-- Products (menu_stock_inventory_control)
|   +-- Products (menu_product_variant_config_stock) -> product_template_action_product
|   +-- Product Variants (product_product_menu)      -> stock_product_normal_action
|   +-- Stock (menu_product_stock)                   -> action_product_stock_view
|   +-- Lots/Serial Numbers (menu_action_production_lot_form) -> action_production_lot_form
|   +-- Packages (menu_package)                      -> action_package_view [group_tracking_lot]
+-- Reporting (menu_warehouse_report)
|   +-- Moves History (stock_move_line_menu)         -> stock_move_line_action
|   +-- Moves Analysis (stock_move_menu)             -> stock_move_action
+-- Configuration (menu_stock_config_settings)
    +-- Settings (menu_stock_general_settings)       -> action_stock_config_settings
    +-- Warehouse Management (menu_warehouse_config)
    |   +-- Warehouses (menu_action_warehouse_form)  -> action_warehouse_form
    |   +-- Operations Types (menu_pickingtype)       -> action_picking_type_list
    |   +-- Locations (menu_action_location_form)    -> action_location_form [group_stock_multi_locations]
    |   +-- Routes (menu_routes_config)              -> action_routes_form [group_adv_location]
    |   +-- Rules (menu_action_rules_form)           -> action_rules_form [group_adv_location]
    |   +-- Putaway Rules (menu_putaway)             -> action_putaway_form [group_stock_multi_locations]
    |   +-- Storage Categories (menu_storage_categoty_config) -> action_storage_category [group_stock_multi_locations]
    +-- Delivery (menu_delivery)
    |   +-- Package Types (menu_packaging_types)     -> action_package_type_view [group_tracking_lot]
    +-- Products (menu_product_in_config_stock)
        +-- Product Categories
        +-- Attributes [group_product_variant]
        +-- Units & Packagings [group_uom]
        +-- Barcode Nomenclatures [group_no_one]
```

---

## 2. Settings (res.config.settings)

### Operations
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Packages | `group_stock_tracking_lot` | Put products in packs and track them | LOW -- yogurt shipped in thermal containers but not individually tracked |
| Batch Transfers | `module_stock_picking_batch` | Group operations and assign to workers | MEDIUM -- useful for batching store transfers |
| Partner-Specific Instructions | `group_warning_stock` | Display instructions on stock operations | LOW |
| Quality Control | `module_quality_control` (Enterprise) | Add quality checks to transfers | MEDIUM -- cold chain quality checks |
| Annual Inventory Day | `annual_inventory_day`, `annual_inventory_month` | Schedule annual counts | MEDIUM |
| Reception Report | `group_stock_reception_report` | View and allocate received quantities | HIGH -- partial receipts at stores |

### Barcode
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Barcode Scanner | `module_stock_barcode` (Enterprise) | Process operations with barcodes | MEDIUM |
| Barcode Database | `module_stock_barcode_barcodelookup` | Create products by scanning | LOW |

### Shipping
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Delivery Methods | `module_delivery` | Compute shipping costs | LOW -- internal fleet only |
| Fleet | `module_stock_fleet` | Transport management | MEDIUM -- own delivery vehicles |
| Email Confirmation | `stock_move_email_validation` | Auto-email on delivery done | LOW |
| Text Confirmation | `stock_text_confirmation` | Auto-SMS on delivery done | LOW |
| Signature on Delivery | `group_stock_sign_delivery` | Require signature on DO | MEDIUM -- store managers sign |

### Products
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Product Variants | `group_product_variant` | Manage variants (size, flavor) | HIGH -- yogurt flavors, topping sizes |
| Units of Measure | `group_uom` | Sell/purchase in different UoM | HIGH -- kg, L, units |

### Traceability
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Lots & Serial Numbers | `group_stock_production_lot` | Full traceability vendors to customers | **CRITICAL** -- lot tracking for toppings, sauces, coatings |
| GS1 Barcodes on Lots | `group_stock_lot_print_gs1` | GS1 datamatrix for lot barcodes | LOW |
| Expiration Dates | `module_product_expiry` | Set expiration on lots/SNs | **CRITICAL** -- frozen/perishable products |
| Lots on Delivery Slip | `group_lot_on_delivery_slip` | Show lots on delivery slip | HIGH -- traceability on remisiones |
| Consignment | `group_stock_tracking_owner` | Set owner on stored products | LOW |

### Warehouse
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Storage Locations | `group_stock_multi_locations` | Track product location in warehouse | **CRITICAL** -- bodega central zones (congelado, seco, refrigerado) |
| Multi-Step Routes | `group_stock_adv_location` | Custom routes for warehouse operations | **CRITICAL** -- transit warehouses, inter-warehouse transfers |

### Advanced Scheduling
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Replenishment Horizon | `horizon_days` | Days ahead to trigger reordering rules | HIGH -- lead time for frozen goods |

### Logistics
| Setting | Field / Group | Description | Percimon relevance |
|---|---|---|---|
| Dropshipping | `module_stock_dropshipping` | Vendor delivers directly to customer | LOW |
| Replenish on Order (MTO) | `replenish_on_order` | Auto PO when sold | MEDIUM |

---

## 3. Key Models

| Model | Description | Percimon relevance |
|---|---|---|
| `stock.warehouse` | Warehouse definition (name, code, reception/delivery steps, routes) | **CRITICAL** -- Bodega Central + one warehouse per store |
| `stock.location` | Hierarchical locations; types: internal, transit, supplier, customer, inventory, production, view | **CRITICAL** -- transit locations for remisiones, zones within bodega |
| `stock.picking.type` | Operation types (receipts, deliveries, internal transfers) per warehouse | **CRITICAL** -- internal transfer type for remisiones |
| `stock.picking` | Transfer document grouping stock moves | **CRITICAL** -- every receipt, delivery, inter-warehouse transfer |
| `stock.move` | Planned product movement (product, qty, source/dest location) | HIGH |
| `stock.move.line` | Detailed move line with lot/serial, package, owner | HIGH -- lot assignment |
| `stock.lot` | Lot/serial number per product | **CRITICAL** -- lot tracking for toppings/sauces/coatings |
| `stock.quant` | Current on-hand inventory per product/location/lot | **CRITICAL** -- real-time stock visibility |
| `stock.warehouse.orderpoint` | Min/max reordering rules (trigger auto/manual, min qty, max qty) | **CRITICAL** -- min/max stock rules with alerts |
| `stock.scrap` | Scrap/shrinkage records (product, qty, source, scrap location) | **CRITICAL** -- shrinkage tracking for perishables |
| `stock.rule` | Procurement/push/pull rules driving automated stock moves | HIGH -- inter-warehouse replenishment rules |
| `stock.route` | Named collection of rules (e.g. "Buy", "Resupply WH2 from WH1") | HIGH -- resupply routes between warehouses |
| `stock.package` | Physical package containing products | LOW |
| `stock.package.type` | Package type (Pallet, Box) with dimensions and weight | LOW |
| `stock.storage.category` | Storage category with weight limits | MEDIUM -- cold storage categories |
| `product.strategy` | Putaway rules (product -> location) | MEDIUM -- putaway to cold zones |
| `stock.package.history` | Package movement history | LOW |
| `stock.reference` | Reference documents linked to pickings | LOW |

---

## 4. Reports

| Report | Template / Model | Description | Percimon relevance |
|---|---|---|---|
| Picking Operations | `report_stockpicking_operations` | Detailed picking slip with operations | HIGH -- printed for each remision |
| Delivery Slip | `report_deliveryslip` | Summary delivery note | HIGH -- accompanies store transfers |
| Stock Inventory | `report_stockinventory` | Physical inventory count sheet | MEDIUM |
| Package Barcode | `report_package_barcode` | Barcode labels for packages | LOW |
| Lot Barcode | `report_lot_barcode` | Barcode labels for lots | HIGH -- lot labels for toppings |
| Location Barcode | `report_location_barcode` | Barcode labels for locations | MEDIUM |
| Stock Reception | `report_stock_reception` | Reception report (allocate received qty) | HIGH -- partial receipt tracking |
| Return Slip | `report_return_slip` | Return document | MEDIUM |
| Stock Rules | `report_stock_rule` | Visual representation of procurement rules | MEDIUM |
| Traceability | `stock_traceability` (controller) | Upstream/downstream traceability | HIGH -- lot recall capability |
| Product Labels | `product_label_report` | Product barcode labels | MEDIUM |
| Packaging Barcode | `packaging_barcode` | Packaging barcode labels | LOW |
| Stock Quantity (pivot) | `report.stock.quantity` | Stock quantity analysis over time | HIGH -- stock level trends |
| Forecasted Report | `stock_forecasted` | Forecasted availability per product | HIGH -- anticipate shortages |
| Moves Analysis (pivot) | `stock.move` action | Pivot/graph of stock moves | MEDIUM |

---

## 5. Wizards

| Wizard | Model | Description | Percimon relevance |
|---|---|---|---|
| Return Picking | `stock.return.picking` | Create return transfer from a picking | MEDIUM -- return defective goods to bodega |
| Backorder Confirmation | `stock.backorder.confirmation` | Confirm creation of backorder for partial transfers | **CRITICAL** -- partial receipts at stores |
| Inventory Adjustment Name | `stock.inventory.adjustment.name` | Set reference for inventory adjustments | LOW |
| Inventory Conflict | `stock.inventory.conflict` | Resolve concurrent inventory count conflicts | LOW |
| Inventory Warning | `stock.inventory.warning` | Warning before applying inventory | LOW |
| Quantity History | `stock.quantity.history` | View stock at a past date | MEDIUM |
| Request Count | `stock.request.count` | Request inventory count for specific products | MEDIUM |
| Replenishment Info | `stock.replenishment.info` | Show replenishment details for an orderpoint | HIGH |
| Rules Report | `stock.rules.report` | Simulate procurement rules for a product | MEDIUM |
| Insufficient Qty Warning | `stock.warn.insufficient.qty.scrap` | Warning when scrapping more than available | HIGH -- shrinkage validation |
| Product Replenish | `product.replenish` | Manually trigger replenishment | HIGH -- manual resupply to stores |
| Product Label Layout | `product.label.layout` | Configure product label printing | LOW |
| Orderpoint Snooze | `stock.orderpoint.snooze` | Snooze a reordering rule | LOW |
| Package Destination | `stock.package.destination` | Set destination for a package | LOW |
| Label Type | `stock.label.type` | Choose label type for printing | LOW |
| Lot Label Layout | `stock.lot.label.layout` | Configure lot label printing | MEDIUM |
| Quant Relocate | `stock.quant.relocate` | Move quants between locations | MEDIUM |
| Put in Pack | `stock.put.in.pack` | Put selected move lines into a package | LOW |

---

## 6. Companion Modules

### Community (odoo/odoo)
| Module | Description | Percimon relevance |
|---|---|---|
| `stock_account` | Inventory valuation, Anglo-Saxon accounting, landed costs link | HIGH -- cost tracking for frozen goods |
| `stock_picking_batch` | Batch transfers: group pickings for processing | MEDIUM |
| `stock_dropshipping` | Drop shipping route | LOW |
| `stock_fleet` | Link pickings to fleet vehicles | MEDIUM -- own delivery trucks |
| `stock_landed_costs` | Allocate landed costs to products | MEDIUM -- import/transport costs |
| `stock_maintenance` | Link equipment to warehouse | LOW |
| `stock_sms` | SMS notifications on stock operations | LOW |
| `stock_delivery` | Delivery methods integration | LOW |
| `product_expiry` | Expiration dates on lots (best before, removal, end of life, alert) | **CRITICAL** -- perishable frozen yogurt, toppings |
| `mrp` | Manufacturing (depends on stock) | MEDIUM -- if yogurt is produced in-house |

### Enterprise (odoo/enterprise)
| Module | Description | Percimon relevance |
|---|---|---|
| `stock_barcode` | Mobile barcode scanning for warehouse operations | MEDIUM |
| `quality_control` | Quality checks on transfers | MEDIUM -- cold chain verification |
| `spreadsheet_dashboard_stock` | Stock dashboard spreadsheets | LOW |
| `l10n_pe_edi_stock` / `l10n_ec_edi_stock` | LatAm e-dispatch (not Colombia-specific) | LOW |

---

## 7. Demo Data Patterns

The stock module's demo data (in `data/stock_demo*.xml`) provides these patterns:

1. **Products set to storable** (`is_storable=True`) -- ~20 products converted from consumable
2. **Lot tracking enabled** -- `product_product_27` set to `tracking=lot`; Cable Management Box also lot-tracked
3. **Stock lots created** -- `lot_product_27` (barcode `0000000000029`), plus `LOT-000001`, `CM-BOX-00001`, `CM-BOX-00002`
4. **Package types** -- Pallet (4000 kg max, 800x1200x130mm) and Box (30 kg max, 362x562x374mm)
5. **Initial inventory via `stock.quant`** -- 15 quant records with `inventory_quantity`, applied via `action_apply_inventory`
6. **Locations** -- Shelf 1, Shelf 2 (under default warehouse stock), Order Processing, Dispatch Zone, Gate A, Gate B, Small Refrigerator
7. **Outgoing pickings** -- 7 delivery orders in various states (draft, confirmed, assigned, done) with staggered dates
8. **Incoming pickings** -- 5 receipts from suppliers in draft/confirmed states
9. **Reordering rules** -- 3 `stock.warehouse.orderpoint` records with min/max quantities (e.g. min=5/max=10)
10. **Storage categories** -- 6 categories by frequency and size (High/Medium/Low x Small/Big) with max_weight
11. **Multi-company** -- Chicago subsidiary warehouse for multi-company demo

---

## 8. Features to Demo (Percimon Recommendations)

### MUST DEMO
- **Multi-warehouse setup**: Bodega Central + at least 2 store warehouses
- **Internal transfers (remisiones)**: Bodega Central -> Store via transit warehouse
- **Transit locations**: Inter-warehouse transit for in-flight visibility
- **Lot tracking**: Lots on toppings, sauces, coatings with full traceability
- **Expiration dates** (`product_expiry`): Best-before and removal dates on lots
- **Min/max reordering rules**: Auto-replenishment alerts per store per product
- **Scrap/shrinkage**: Record expired/damaged product with scrap orders
- **Partial receipts with backorders**: Store receives partial shipment, backorder auto-created
- **Physical inventory**: Count sheets for periodic store counts
- **Stock valuation** (`stock_account`): Cost tracking on inventory movements

### SHOULD DEMO
- **Multi-step routes**: 2-step receipt (receive + store) at bodega for quality check
- **Putaway rules**: Auto-route incoming goods to cold storage zones (Congelado, Refrigerado, Seco)
- **Storage categories**: Temperature-based categories with capacity limits
- **Reception report**: Allocate received goods against pending orders
- **Forecasted availability**: Anticipate stock-outs per product per location
- **Replenishment info**: Visibility into when/how reordering rules will trigger
- **Delivery slip**: Printed document accompanying each remision

### NICE TO HAVE
- **Batch transfers**: Group multiple store remisiones for same-day delivery
- **Fleet integration**: Link deliveries to company vehicles
- **Signature on delivery**: Store manager signs on delivery receipt

---

## 9. Settings to Enable

```python
# res.config.settings values for Percimon
{
    "group_stock_production_lot": True,         # Lots & Serial Numbers
    "module_product_expiry": True,              # Expiration Dates
    "group_stock_multi_locations": True,        # Storage Locations
    "group_stock_adv_location": True,           # Multi-Step Routes
    "group_uom": True,                          # Units of Measure
    "group_product_variant": True,              # Product Variants (flavors)
    "group_stock_reception_report": True,       # Reception Report
    "group_lot_on_delivery_slip": True,         # Lots on Delivery Slip
    "group_stock_sign_delivery": True,          # Signature on DO
    "annual_inventory_month": "12",             # Annual inventory in December
    "annual_inventory_day": 15,                 # Mid-December count
}
```
