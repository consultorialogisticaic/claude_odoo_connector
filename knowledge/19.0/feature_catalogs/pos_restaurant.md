# Feature Catalog: pos_restaurant (Restaurant)

- **Technical name:** pos_restaurant
- **Version:** 19.0
- **Category:** Sales/Point of Sale
- **Application:** Yes
- **Depends:** point_of_sale
- **Summary:** Restaurant extensions for the Point of Sale

---

## 1. Menus (Backend)

| Menu path | Action / Model | Notes |
|---|---|---|
| Point of Sale > Configuration > Floor Plans | `restaurant.floor` (list/kanban/form) | Create/manage floors + inline table editor |

The module does not add top-level menus. All configuration is under POS Settings and the Floor Plans submenu.

---

## 2. Settings / Feature Flags

All settings are per-POS-config (accessed via Point of Sale > Configuration > Settings, per shop):

| Setting | Technical field (`pos.config`) | Default | Description |
|---|---|---|---|
| Is a Bar/Restaurant | `module_pos_restaurant` | False | Master toggle; enables all restaurant features for this POS |
| Floors & Tables Map | `floor_ids` (M2M to `restaurant.floor`) | Auto-created | Assign floor plans to the POS; visual table map in frontend |
| Bill Splitting | `iface_splitbill` | False | Allow splitting an order across multiple bills/guests |
| Early Receipt Printing | `iface_printbill` | True (when restaurant) | Print a receipt (bill) before payment |
| Set Tip After Payment | `set_tip_after_payment` | False | Add tip after the card payment is authorized (requires tip product) |
| Default Screen | `default_screen` | `tables` | Start POS session on table map (`tables`) or register (`register`) |
| Use Presets (Dine In/Takeout/Delivery) | `use_presets` | True (when restaurant scenario) | Enable order-type presets |

### Presets (installed via restaurant scenario)

| Preset | XML ID | Identification | Timing |
|---|---|---|---|
| Dine In | `pos_restaurant.pos_takein_preset` | None | No |
| Takeout | `pos_restaurant.pos_takeout_preset` | Name | Yes (opening hours) |
| Delivery | `pos_restaurant.pos_delivery_preset` | Address | No |

Presets extend `pos.preset` with a `use_guest` boolean (force guest count selection).

---

## 3. Key Models

### 3.1 restaurant.floor

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required |
| `pos_config_ids` | Many2many(`pos.config`) | Which POS shops use this floor |
| `table_ids` | One2many(`restaurant.table`) | Tables on this floor |
| `background_color` | Char | CSS color |
| `floor_background_image` | Image | Upload a floor plan image |
| `sequence` | Integer | Ordering |
| `active` | Boolean | Archive support |

Constraints: cannot delete/archive a floor while a POS session using it is open.

### 3.2 restaurant.table

| Field | Type | Notes |
|---|---|---|
| `floor_id` | Many2one(`restaurant.floor`) | Parent floor |
| `table_number` | Integer | Displayed on floor map |
| `seats` | Integer | Default guest capacity |
| `shape` | Selection | `square` or `round` |
| `position_h` / `position_v` | Float | Pixel position on floor map |
| `width` / `height` | Float | Pixel dimensions |
| `color` | Char | CSS color |
| `parent_id` | Many2one(`restaurant.table`) | For grouped/merged tables |
| `active` | Boolean | Deactivation support |

### 3.3 restaurant.order.course

Tracks course-based firing to kitchen printers.

| Field | Type | Notes |
|---|---|---|
| `order_id` | Many2one(`pos.order`) | Parent order |
| `line_ids` | One2many(`pos.order.line`) | Lines in this course |
| `fired` | Boolean | Whether the course was sent to kitchen |
| `fired_date` | Datetime | Timestamp of firing |
| `index` | Integer | Course sequence |
| `uuid` | Char | Unique ID for frontend sync |

### 3.4 Inherited models

| Model | Added fields | Purpose |
|---|---|---|
| `pos.order` | `table_id` (M2O), `customer_count` (Int), `course_ids` (O2M) | Link order to table, track guest count, track courses |
| `pos.order.line` | `course_id` (M2O to `restaurant.order.course`) | Assign line to a course |
| `pos.config` | `iface_splitbill`, `iface_printbill`, `floor_ids`, `set_tip_after_payment`, `default_screen` | Restaurant-specific config |
| `pos.preset` | `use_guest` (Boolean) | Force guest count on preset |
| `pos.payment` | method `_update_payment_line_for_tip()` | Adjust payment amount for post-payment tip |
| `pos.session` | loads `restaurant.floor`, `restaurant.table`, `restaurant.order.course` | Data loading for restaurant POS |
| `res.config.settings` | `pos_floor_ids`, `pos_iface_printbill`, `pos_iface_splitbill`, `pos_set_tip_after_payment`, `pos_default_screen` | Settings UI delegation |

---

## 4. Frontend Screens (JS/OWL)

| Screen | Path | Purpose |
|---|---|---|
| Floor Screen | `app/screens/floor_screen/` | Visual table map; select/create/merge tables |
| Product Screen (override) | `app/screens/product_screen/` | Actionpad adds Transfer, Note, Guests buttons |
| Split Bill Screen | `app/screens/split_bill_screen/` | Split order lines across multiple bills |
| Payment Screen (override) | `app/screens/payment_screen/` | Tip support, bill printing |
| Tip Screen | `app/screens/tip_screen/` | Post-payment tip entry |
| Receipt Screen (override) | `app/screens/receipt_screen/` | Restaurant-specific receipt template |
| Ticket Screen (override) | `app/screens/ticket_screen/` | Shows table info on order tickets |
| Feedback Screen | `app/screens/feedback_screen/` | Customer feedback after payment |

### Additional components

| Component | Purpose |
|---|---|
| `order_course` | Course grouping UI in order display |
| `order_tabs` | Tab navigation between orders on a table |
| `tip_receipt` | Tip receipt template |
| `edit_order_name_popup` | Rename order popup |
| `order_change_receipt_template` | Kitchen order ticket (preparation changes) |
| `numpad_dropdown` | Extended numpad with guest count |

---

## 5. Demo Data

### 5.1 Onboarding scenarios (loaded via `load_onboarding_*_scenario`)

**Restaurant scenario** (`load_onboarding_restaurant_scenario`):
- Creates a POS config named "Restaurant" with bill splitting enabled
- Creates 2 floors: Main Floor (12 tables, background image) + Patio (12 tables)
- Loads POS categories: Food, Drinks
- Demo products with images:
  - **Food:** Bacon Burger (with Sides attribute), Cheese Burger (with Sides), Pizza Margherita (with Extras), Pizza Vegetarian (with Extras), Pasta 4 Formaggi (with Extras), Funghi, Pasta Bolognese, Chicken Curry Sandwich, Spicy Tuna Sandwich, Mozzarella Sandwich, Club Sandwich, Lunch Maki 18pc, Lunch Salmon 20pc, Lunch Temaki mix 3pc, Salmon and Avocado
  - **Drinks:** Coca-Cola, Water, Minute Maid, Espresso, Green Tea, Milkshake Banana, Ice Tea, Schweppes, Fanta
  - **Combos:** Burger Menu Combo (burger + drink), Sushi Lunch Combo (sushi choice + drink)
- Product attributes: Sides (pills, 5 values), Extras (multi-select, 5 values with extra prices)

**Bar scenario** (`load_onboarding_bar_scenario`):
- Creates a POS config named "Bar" with `default_screen=register`
- Shares same 2 floors as restaurant
- Loads POS categories: Cocktails, Soft drinks
- Demo products: 10 cocktails (Cosmopolitan, Margarita, Moscow Mule, Pina Colada, Aperol Spritz, Old Fashioned, Mojito, Mai Tai, Whiskey Sour, Negroni) + 7 soft drinks

### 5.2 Demo data trigger

`data/demo_data.xml` calls `load_onboarding_restaurant_scenario()` and `load_onboarding_bar_scenario()` via `<function>` tags. Both run only when demo data is enabled.

---

## 6. Companion Modules

### Community (auto-install or bridge)

| Module | Depends on | Purpose |
|---|---|---|
| `pos_self_order` | `pos_restaurant`, `http_routing`, `link_tracker` | Self-ordering via QR code at the table (auto-install with pos_restaurant) |
| `pos_restaurant_loyalty` | `pos_restaurant`, `pos_loyalty` | Loyalty programs in restaurant POS |
| `pos_hr_restaurant` | `pos_hr`, `pos_restaurant` | Employee login adapted for restaurant mode |
| `pos_restaurant_stripe` | `pos_stripe`, `pos_restaurant`, `payment_stripe` | Stripe tip adjustment for restaurant |
| `pos_restaurant_adyen` | `pos_adyen`, `pos_restaurant`, `payment_adyen` | Adyen tip adjustment for restaurant |
| `l10n_be_pos_restaurant` | `pos_restaurant`, `l10n_be` | Belgian restaurant POS localization |
| `spreadsheet_dashboard_pos_restaurant` | `spreadsheet_dashboard`, `pos_hr`, `pos_restaurant` | Restaurant POS analytics dashboard |

### Enterprise

| Module | Depends on | Purpose |
|---|---|---|
| `pos_restaurant_preparation_display` | `pos_restaurant`, `pos_enterprise` | Kitchen Display System (KDS) -- shows fired courses on a screen |
| `pos_restaurant_appointment` | `pos_restaurant`, `pos_appointment` | Table reservations linked to appointments |
| `pos_restaurant_urban_piper` | `pos_restaurant`, `pos_urban_piper` | Delivery platform integration (UberEats, etc.) |

---

## 7. Percimon Relevance -- Features to Demo

### High priority (dine-in stores)

| Feature | Why | Demo action |
|---|---|---|
| Floor & Table Map | Percimon dine-in stores need visual table assignment | Create 1 floor "Salon" with 6-8 tables matching a typical yogurt shop layout |
| Guest Count | Track guests per table for bill splitting | Set `seats` per table (2-seat and 4-seat tables) |
| Bill Splitting | Per-guest bill splitting is an explicit requirement | Enable `iface_splitbill`, demo splitting a 4-guest order |
| Presets: Dine In / Takeout | Percimon has both counter and dine-in service | Enable presets; show Dine In vs Takeout flow |
| Early Receipt Printing | Print bill before payment (common in sit-down yogurt cafes) | Enable `iface_printbill`, print a bill then pay |
| Course Firing | Send frozen yogurt prep orders to kitchen/prep area | Demo firing a course to a preparation printer |

### Lower priority

| Feature | Why |
|---|---|
| Tip After Payment | Not standard in Colombian frozen yogurt shops; skip unless client requests |
| Bar Scenario | Not applicable; Percimon is frozen yogurt, not bar |
| Combos | Could be useful for "yogurt + topping + drink" bundles but belongs to base POS |
| Self-Order (pos_self_order) | Auto-installs; could be interesting for QR-code ordering at tables |
| KDS (pos_restaurant_preparation_display) | Enterprise only; valuable if prep station needs a screen |

### Settings to enable for demo

```
pos_config.module_pos_restaurant = True
pos_config.iface_splitbill = True
pos_config.iface_printbill = True
pos_config.default_screen = 'tables'
pos_config.use_presets = True
```

---

## 8. Identity Keys (for CSV loading)

| Model | Identity key(s) |
|---|---|
| `restaurant.floor` | `name` |
| `restaurant.table` | `floor_id` + `table_number` |
