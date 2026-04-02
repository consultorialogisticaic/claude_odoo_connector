# Feature Catalog — Manufacturing (mrp)

**Version:** 19.0
**Source:** community
**Category:** Supply Chain/Manufacturing
**Dependencies:** product, stock, resource

## Business Capabilities

- **Bill of Materials (BOM) management** — define product recipes with exact component quantities, units of measure, and multi-level sub-assemblies. Supports both "Manufacture" and "Kit" BOM types.
- **Manufacturing Order execution** — plan, schedule, and track production orders from draft through completion, with component availability checking and backorder support.
- **Work Center and Operations routing** — model your production floor: define work centers with capacity, cost per hour, and OEE targets; attach operation sequences to BOMs.
- **Unbuild / disassembly** — reverse a manufacturing order to recover components from finished products.
- **Production traceability** — full lot/serial number tracking from raw materials through finished goods, integrated with Inventory's traceability engine.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| Manufacturing > Operations > Manufacturing Orders | Manufacturing Orders | Create, plan, and process production orders (list, kanban, calendar, pivot, graph views) |
| Manufacturing > Operations > Work Orders | Work Orders | Track individual work order steps within manufacturing orders (requires Work Orders setting) |
| Manufacturing > Operations > Unbuild Orders | Unbuild Orders | Disassemble finished products back into components |
| Manufacturing > Operations > Scrap | Scrap | Record scrapped materials during production |
| Manufacturing > Planning > Run Scheduler | Run Scheduler | Trigger the procurement scheduler to generate planned MOs (technical/debug mode) |
| Manufacturing > Products > Products | Products | Product catalog filtered for manufactured items |
| Manufacturing > Products > Product Variants | Product Variants | Variant-level view (requires Product Variants setting) |
| Manufacturing > Products > Bills of Materials | Bills of Materials | Define and manage BOMs with components, operations, and by-products |
| Manufacturing > Products > Lots/Serial Numbers | Lots/Serial Numbers | Traceability for manufactured goods |
| Manufacturing > Reporting > Work Orders | Work Orders Analysis | Pivot/graph analysis of work order durations and performance (requires Work Orders setting) |
| Manufacturing > Reporting > OEE | Overall Equipment Effectiveness | Work center productivity reporting (requires Work Orders setting) |
| Manufacturing > Configuration > Settings | Settings | Enable/disable MRP features |
| Manufacturing > Configuration > Work Centers | Work Centers | Define production work centers with capacity and costs (requires Work Orders setting) |
| Manufacturing > Configuration > Operations | Operations | Manage reusable operation templates (requires Work Orders setting) |

### Settings & Feature Flags

| Setting | Technical Field | What it Enables |
|---|---|---|
| Work Orders | `group_mrp_routings` | Enables work centers, operations/routing on BOMs, work order tracking, OEE reporting. Central to modeling a production floor. |
| Operation Dependencies | `group_mrp_workorder_dependencies` | Set the order that work orders should be processed in (sub-setting of Work Orders). Activated per-BOM in Miscellaneous tab. |
| Subcontracting | `module_mrp_subcontracting` | Installs `mrp_subcontracting` module to delegate part of production to external subcontractors. |
| Barcode | `module_stock_barcode` | Process manufacturing orders from the barcode scanning app (enterprise). |
| Quality Control | `module_quality_control` | Add quality checks to work orders (enterprise). |
| Quality Control Worksheets | `module_quality_control_worksheet` | Customizable worksheets for quality checks (enterprise, sub-setting of Quality Control). |
| Unlock Consumption | `group_unlocked_by_default` | Allow manufacturing users to modify consumed quantities without prior approval. |
| By-Products | `group_mrp_byproducts` | Produce residual/secondary products from a BOM (A + B -> C + D). |
| Reception Report | `group_mrp_reception_report` | View and allocate production output to customer orders or downstream MOs. |
| Master Production Schedule | `module_mrp_mps` | Plan manufacturing/purchase orders based on demand forecasts (enterprise). |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `mrp.production` | Primary | Manufacturing Order — the main production document | Yes |
| `mrp.production.group` | Transactional | Groups related manufacturing orders together | No (internal) |
| `mrp.bom` | Configuration | Bill of Materials — defines product recipe | Yes |
| `mrp.bom.line` | Transactional | BOM component line (product, qty, UoM) | Yes (embedded in BOM form) |
| `mrp.bom.byproduct` | Transactional | By-product line on a BOM | Yes (embedded, requires By-Products setting) |
| `mrp.workcenter` | Configuration | Work center definition (capacity, cost, OEE target) | Yes (requires Work Orders) |
| `mrp.workcenter.tag` | Configuration | Tags for work centers | Yes (embedded) |
| `mrp.workcenter.capacity` | Configuration | Product-specific capacity overrides per work center | Yes (embedded) |
| `mrp.workcenter.productivity` | Transactional | Productivity log entries (time tracking per work center) | Yes (reporting) |
| `mrp.workcenter.productivity.loss` | Configuration | Loss reasons for productivity tracking | Yes (configuration) |
| `mrp.workcenter.productivity.loss.type` | Configuration | Loss type categories (productive, performance, quality, availability) | No (seed data) |
| `mrp.workorder` | Transactional | Individual work order step within an MO | Yes (requires Work Orders) |
| `mrp.routing.workcenter` | Configuration | Operation definition on a BOM (work center + duration) | Yes (embedded in BOM) |
| `mrp.unbuild` | Primary | Unbuild/disassembly order | Yes |
| `stock.move` | Transactional (extended) | Component consumption and finished product moves | Yes (embedded in MO) |

### Reports & Analytics

| Report | Type | Model | Description |
|---|---|---|---|
| Production Order | PDF | `mrp.production` | Printable production order with components and operations |
| BoM Overview | PDF + Interactive | `mrp.bom` | Multi-level BOM structure with cost breakdown (interactive client-side report + PDF export) |
| MO Overview | PDF + Interactive | `mrp.production` | Manufacturing order overview with component availability and scheduling |
| Finished Product Label (PDF) | PDF Label | `mrp.production` | Product labels for finished goods |
| Finished Product Label (ZPL) | ZPL | `mrp.production` | Zebra printer label for finished goods |
| Work Order | PDF | `mrp.workorder` | Printable work order instructions |
| OEE Report | Pivot/Graph | `mrp.workcenter.productivity` | Overall Equipment Effectiveness analysis by work center |
| Work Orders Analysis | Pivot/Graph | `mrp.workorder` | Duration and performance analysis of work orders |
| Stock Forecasted | Dashboard | `stock.move` | Forecasted stock levels considering planned production |

### Wizards & Advanced Actions

| Wizard | Model | Purpose |
|---|---|---|
| Change Production Qty | `change.production.qty` | Modify quantity on a confirmed MO (recalculates components) |
| Work Center Block | (wizard view) | Block/unblock a work center for maintenance or scheduling |
| Insufficient Qty Warning | `stock.warn.insufficient.qty.scrap` | Warning when scrapping exceeds available stock |
| Production Backorder | `mrp.production.backorder` | Create backorder for partially completed MOs |
| Consumption Warning | `mrp.consumption.warning` | Alert when consumed quantities deviate from BOM specifications |
| Production Split | `mrp.production.split` | Split a manufacturing order into multiple smaller orders |
| Serial Number Assignment | (wizard) | Bulk assign serial numbers to produced units |
| Stock Replenishment Info | `stock.replenishment.info` | View replenishment details for components |
| MRP Display (Shop Floor) | Client Action | Full-screen tablet-friendly interface for shop floor operators (`mrp_display` tag) |

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `mrp_account` | community + enterprise | Manufacturing cost accounting, WIP valuation, cost analysis |
| `mrp_landed_costs` | community | Allocate landed costs to manufacturing orders |
| `mrp_product_expiry` | community | Expiry date management for manufactured products (lot-based) |
| `mrp_repair` | community | Repair orders linked to manufacturing |
| `mrp_subcontracting` | community | Subcontracting workflow — send components to vendors who manufacture on your behalf |
| `mrp_subcontracting_purchase` | community | Link subcontracting to purchase orders |
| `mrp_subcontracting_dropshipping` | community | Drop-ship subcontracted products directly to customers |
| `mrp_mps` | enterprise | Master Production Schedule — demand-driven planning with forecasts |
| `mrp_plm` | enterprise | Product Lifecycle Management — engineering change orders, version control for BOMs |
| `mrp_workorder` | enterprise | Enhanced work order UI with tablet view, step-by-step instructions, time tracking |
| `mrp_maintenance` | enterprise | Link work centers to maintenance equipment and schedules |
| `mrp_account_enterprise` | enterprise | Advanced manufacturing cost reporting and dashboards |
| `mrp_accountant` | enterprise | Journal entries and accounting integration for manufacturing |
| `mrp_zebra` | enterprise | Zebra printer integration for production labels |
| `purchase_mrp` | community | Link purchase orders to manufacturing (auto-buy components) |
| `sale_mrp` | community | Link sales orders to manufacturing (MTO flow) |
| `pos_mrp` | community | POS integration — trigger manufacturing from point of sale |
| `quality_mrp` | enterprise | Quality checks on manufacturing orders |
| `stock_barcode_mrp` | enterprise | Barcode scanning for manufacturing operations |

## Demo Highlights

> **Client context:** Percimon -- Colombian frozen yogurt chain. Central production facility making frozen yogurt recipes (base yogurt + fruits, toppings, sauces, coatings). BOMs define ingredient quantities in grams. Distributes to retail stores.

1. **Bill of Materials as Recipes** -- Create a BOM for "Frozen Yogurt - Mango" with base yogurt (500g), mango puree (200g), sugar (50g), stabilizer (10g). Use the gram UoM for precise recipe control. The interactive BoM Overview report shows the full ingredient tree with cost per serving -- perfect for demonstrating recipe cost analysis to Percimon's production manager.

2. **Kit BOMs for Combo Products** -- Define a Kit-type BOM for a "Yogurt Combo Pack" (3 flavors + toppings container). When sold, the kit auto-explodes into individual finished products for picking -- ideal for Percimon's store distribution packs.

3. **Manufacturing Orders for Batch Production** -- Create an MO to produce 200 units of "Frozen Yogurt - Strawberry" at the central facility. Show component availability checking (do we have enough strawberries?), quantity adjustment mid-production, and the backorder flow when only partial ingredients are available.

4. **Multi-Level BOMs (Base + Flavors)** -- Define a sub-BOM for "Base Yogurt Mix" (milk, cultures, sugar, cream) and reference it as a component in each flavor BOM. This mirrors Percimon's actual process: make the base first, then add flavor-specific ingredients. The BoM Overview report visualizes this hierarchy beautifully.

5. **By-Products for Whey Recovery** -- Enable the By-Products setting to track whey (a by-product of yogurt straining) as a secondary output. This shows Percimon that Odoo can track their full production output, including residual materials that may be sold or reused.
