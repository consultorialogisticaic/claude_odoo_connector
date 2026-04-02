# Feature Catalog: stock_barcode (Barcode)

- **Technical name:** stock_barcode
- **Version:** 19.0
- **Category:** Supply Chain/Inventory
- **Application:** Yes (auto_install: True when `stock` is installed)
- **License:** OEEL-1 (Enterprise)
- **Depends:** stock, web_tour, web_mobile
- **Summary:** Use barcode scanners to process logistics operations

---

## 1. Menus (Backend)

| Menu path | Action / Model | Notes |
|---|---|---|
| Barcode (top-level) | `stock_barcode_action_main_menu` — client action `stock_barcode_main_menu` | Fullscreen mobile-optimized launcher; groups: `stock.group_stock_user` |
| (Main menu) > Operations | `stock_picking_type_action_kanban` — kanban of `stock.picking.type` | Shows Receipts, Delivery Orders, Internal Transfers with ready-count badges |
| (Per operation type) > Pickings | `stock_picking_action_kanban` — kanban of `stock.picking` | Filtered: available + to-do transfers |
| Settings > Inventory > Barcode Scanner | Inherits `stock.res_config_settings_view_form` | Barcode nomenclature, separator regex, RFID timer, print sheets |
| Settings > Inventory > Barcode Scanner > Configure Product Barcodes | `product_action_barcodes` — editable list of `product.product` | Quick barcode assignment |

---

## 2. Settings / Feature Flags

Settings are added to Inventory > Configuration > Settings under the "Barcode Scanner" section:

| Setting | Technical field | Default | Description |
|---|---|---|---|
| Barcode Nomenclature | `barcode_nomenclature_id` (related to `company_id.nomenclature_id`) | Default nomenclature | Choose between Default and GS1 nomenclature |
| Barcode Separator Regex | `barcode_separator_regex` (config_parameter) | `[;,]` | Regex to split aggregate/multi-barcodes |
| RFID Batch Time | `barcode_rfid_batch_time` (config_parameter) | 1000 ms | Time before processing an RFID batch |
| Mute Sound Notifications | `stock_barcode_mute_sound_notifications` (config_parameter) | False | Disable scan sound effects (debug mode) |
| Max Time Between Keys | `barcode_max_time_between_keys_in_ms` (config_parameter) | 100 ms | Max delay between keystrokes for barcode scanner detection (debug mode) |

### Per-Operation-Type Settings (Barcode App tab on `stock.picking.type`)

| Setting | Technical field | Default | Description |
|---|---|---|---|
| Show Reserved Lots/SN | `show_reserved_sns` | — | Display reserved lot/serial numbers to picker |
| Allow Extra Products | `barcode_allow_extra_product` | True | Allow adding non-reserved products to planned transfers |
| Force Product Scan | `restrict_scan_product` | False | Product barcode must be scanned before editing line |
| Force Lot/Serial Scan | `restrict_scan_tracking_number` | `optional` | `mandatory` or `optional` |
| Force Source Location Scan | `restrict_scan_source_location` | `no` (outgoing: `mandatory`) | `no` or `mandatory` |
| Force Destination Location Scan | `restrict_scan_dest_location` | `optional` | `mandatory`, `optional` (after group), or `no` |
| Force Put in Pack | `restrict_put_in_pack` | `optional` | `mandatory` (after each product), `optional` (after group), or `no` |
| Allow Full Picking Validation | `barcode_validation_full` | True | Allow validating without scanning (immediate transfer) |
| Force All Products Packed | `barcode_validation_all_product_packed` | False | Block validation until all lines packed |
| Force Dest for All Products | `barcode_validation_after_dest_location` | False | Block validation until all lines have destination |
| Card Color | `color` (color_picker widget) | — | Visual differentiation of operation type cards |

---

## 3. Key Models

### 3.1 stock.picking (extended)

Added fields/methods for barcode client action:

| Field / Method | Type | Notes |
|---|---|---|
| `_barcode_field` | Class attr | `'name'` — picking name is the scannable barcode |
| `action_open_picking_client_action()` | Method | Opens the fullscreen barcode picking form |
| `action_cancel_from_barcode()` | Method | Opens cancel confirmation wizard |
| `action_create_return_picking()` | Method | Creates a return picking and opens it in barcode app |
| `action_print_barcode()` | Method | Print barcode labels |
| `action_print_delivery_slip()` | Method | Print delivery report |
| `filter_on_barcode(barcode)` | Model method | Searches ready pickings by product/package/lot/packaging barcode |
| `_get_stock_barcode_data()` | Method | Prefetches all data needed by the JS client action (products, locations, packages, lots, UoMs, config) |

### 3.2 stock.picking.type (extended)

All barcode-specific selection/boolean fields listed in Settings section above. Key methods:

| Method | Notes |
|---|---|
| `get_action_picking_tree_ready_kanban()` | Returns kanban action for ready pickings |
| `_get_barcode_config()` | Returns dict of all barcode settings for the JS client |

### 3.3 stock.move.line (extended)

| Field | Type | Notes |
|---|---|---|
| `product_barcode` | Char (related) | Product barcode for display |
| `formatted_product_barcode` | Char (computed) | `[barcode]` or "No Barcode" |
| `location_processed` | Boolean | Tracks if location was scanned |
| `qty_done` | Float (computed/inverse) | Wraps `quantity` + `picked` flag |
| `image_1920` | Image (related) | Product image in barcode form |
| `product_reference_code` | Char (related) | Internal reference |
| `electronic_product_code` | Char (computed) | EPC/RFID tag encoding (SGTIN-96/198) |
| `packaging_uom_id` / `packaging_uom_qty` | Related | Packaging UoM support |
| `outermost_result_package_id` | Many2one (computed/inverse) | Nested package support |
| `hide_lot_name` / `hide_lot` | Boolean (computed) | Control lot/SN field visibility |
| `product_stock_quant_ids` | One2many (computed) | Available quants for the product at source location |

### 3.4 stock.quant (extended)

| Field / Method | Type | Notes |
|---|---|---|
| `dummy_id` | Char | Technical field for barcode form identity |
| `image_1920` | Image (related) | Product image |
| `barcode_write(vals)` | Model method | Handles inventory adjustment saves from barcode app |
| `action_validate()` | Method | Apply inventory adjustment |
| `action_client_action()` | Method | Open barcode inventory client action |
| `_get_stock_barcode_data()` | Method | Prefetches quants, products, locations, packages, lots for JS |

### 3.5 product.product (extended)

| Field / Method | Notes |
|---|---|
| `_barcode_field = 'barcode'` | Product barcode is the scannable field |
| `has_image` | Boolean computed — whether product has an image |
| `_search` override | GS1 nomenclature preprocessing on search |

### 3.6 stock.location (extended)

| Field / Method | Notes |
|---|---|
| `_barcode_field = 'barcode'` | Location barcode is the scannable field |
| `barcode_img` | Binary (computed) — Code128 barcode image for location |
| `get_counted_quant_data_records()` | Returns quant data for a scanned location |

### 3.7 stock.lot (extended)

| Field / Method | Notes |
|---|---|
| `_barcode_field = 'name'` | Lot/serial name is the scannable barcode |
| GS1 search preprocessing | Handles GS1-encoded lot barcodes |

### 3.8 stock.scrap (extended)

| Field / Method | Notes |
|---|---|
| `product_barcode` | Related field for barcode scanning |
| `on_barcode_scanned(barcode)` | Scan product or lot to populate scrap form |

### 3.9 stock.package (extended)

| Field / Method | Notes |
|---|---|
| `_barcode_field = 'name'` | Package name is the scannable barcode |
| `action_create_from_barcode(vals_list)` | Create package from barcode app and return data for JS cache |
| `_get_usable_packages()` | Fetches reusable/empty packages for destination selection |

---

## 4. Reports

| Report | Notes |
|---|---|
| Print Barcode Commands & Operation Types | PDF download from Settings — barcode command sheet for handheld scanners |
| Print Storage Locations | PDF of location barcodes (when multi-locations enabled) |
| Print Barcode Demo Sheet | Available when demo data is active |
| Delivery Slip | `stock.action_report_delivery` (from stock) — accessible via barcode app |
| Package Labels | `stock.action_report_picking_packages` (from stock) — accessible via barcode app |

---

## 5. Wizards

| Wizard | Model | Purpose |
|---|---|---|
| Cancel Operation | `stock_barcode.cancel.operation` | Confirmation dialog before canceling a picking from barcode app |
| Backorder Confirmation | `stock.backorder.confirmation` (extended) | Shows `empty_move_count` and `partial_move_count` — how many lines were not/partially processed |

---

## 6. Client Actions (JavaScript)

| Action | Tag | Target Model | Notes |
|---|---|---|---|
| Barcode Main Menu | `stock_barcode_main_menu` | — | Fullscreen launcher with operation type tiles |
| Barcode Picking | `stock_barcode_client_action` | `stock.picking` | Fullscreen picking processing with scan/digipad |
| Barcode Inventory | `stock_barcode_client_action` | `stock.quant` | Fullscreen inventory adjustment |

The entire barcode experience is a single-page JS application (OWL components in `static/src/`). Backend views serve only as configuration; all operational work happens in the client actions.

---

## 7. Demo Data

The `demo.xml` file provides:

- **Product barcodes:** Assigns EAN-13 barcodes to ~20 existing stock demo products (e.g., `6016478556387`, `6016478556318`)
- **GS1 demo products:** 3 additional products (`Cable Management Box`, `Customized Cabinet USA/Metric`) with GS1-prefixed barcodes (`06016478556677`, etc.), lot tracking, and UoM variations
- **Demo package:** An empty `stock.package` for pack operations
- **Lot reference:** Adds a barcode-like `ref` to an existing lot
- **Demo barcodes message flag:** Sets `message_demo_barcodes: True` on the main menu action (triggers "print demo sheet" link)

---

## 8. Data (Non-demo)

- **Barcode command aliases:** 4 `barcode.rule` records mapping user-friendly barcodes to short codes (e.g., `WH-RECEIPTS` -> `WHIN`, `O-BTN.validate` -> `OBTVALI`)
- **Default outgoing picking type config:** Sets `restrict_scan_source_location = 'mandatory'` and `restrict_scan_dest_location = 'no'` for all outgoing operation types
- **EPC serial sequence:** `stock_barcode.epc.serial` for RFID tag generation
- **Config parameters:** `barcode_separator_regex` = `[;,]`, `barcode_rfid_batch_time` = `1000`
- **EPC template:** XML template for Electronic Product Code encoding (`epc_template.xml`)

---

## 9. Companion Modules (Enterprise)

| Module | Technical name | Purpose |
|---|---|---|
| Barcode - Barcode Lookup | `stock_barcode_barcodelookup` | Auto-fill product info by scanning unknown barcodes (online lookup) |
| Barcode - MRP | `stock_barcode_mrp` | Manufacturing order processing via barcode app |
| Barcode - MRP Subcontracting | `stock_barcode_mrp_subcontracting` | Subcontractor receipt processing via barcode |
| Barcode - Batch Picking | `stock_barcode_picking_batch` | Process picking batches (wave picking) in barcode app |
| Barcode - Product Expiry | `stock_barcode_product_expiry` | Scan/set expiration dates during barcode operations |
| Barcode - Quality Control | `stock_barcode_quality_control` | Quality checks integrated into barcode picking flow |
| Barcode - Quality MRP | `stock_barcode_quality_mrp` | Quality checks for MRP operations in barcode |

---

## 10. Percimon Relevance

For Percimon (Colombian frozen yogurt chain), `stock_barcode` enables:

- **Warehouse receipts with scanning:** Receive ingredient shipments (fruit, dairy, packaging) by scanning product barcodes — reduces manual entry errors
- **Store transfers:** Process internal transfers between central warehouse and store locations with mandatory source/destination location scanning
- **Inventory counts:** Mobile-friendly inventory adjustments with digipad — scan products and count quantities directly on a phone/tablet
- **Lot/expiry tracking:** Scan lot numbers for perishable ingredients (pairs with `stock_barcode_product_expiry` for expiration dates)
- **Pack operations:** Group products into delivery packages for multi-store distribution

**Recommended settings for Percimon:**
- Enable multi-locations (central warehouse + store locations)
- Set `restrict_scan_source_location = 'mandatory'` on internal transfers
- Enable lot tracking for perishable ingredients
- Consider `stock_barcode_product_expiry` companion module for expiration date scanning
