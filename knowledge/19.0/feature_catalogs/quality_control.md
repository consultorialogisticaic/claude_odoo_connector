# Feature Catalog: quality_control (Quality)

**Odoo version:** 19.0
**Module technical name:** `quality_control`
**Display name:** Quality
**Category:** Supply Chain/Quality
**License:** Enterprise (OEEL-1)
**Dependencies:** `quality` (base), `spreadsheet_edition`
**Transitive deps:** `stock` (via `quality`)

---

## 1. Menu Structure

```
Quality (root menu, icon: quality_control)
  |-- Overview                          -> quality.alert.team kanban dashboard
  |-- Quality Control
  |     |-- Control Points              -> quality.point list/kanban/form  [Manager only]
  |     |-- Quality Checks              -> quality.check list/kanban/form/pivot/graph/activity
  |     |-- Quality Alerts              -> quality.alert kanban/list/form/pivot/graph/calendar/activity
  |-- Reporting                         [Manager only]
  |     |-- Quality Check Analysis      -> quality.check graph/pivot
  |     |-- Quality Alerts Analysis     -> quality.alert graph/pivot
  |-- Configuration                     [Manager only]
  |     |-- Quality Teams               -> quality.alert.team list/form
  |     |-- Quality Alert Stages        -> quality.alert.stage list  [Debug mode]
  |     |-- Quality Tags                -> quality.tag list  [Debug mode]
  |     |-- Quality Spreadsheet Templ.  -> quality.spreadsheet.template list
```

---

## 2. Settings

No `res.config.settings` fields in this module. The module is activated by installing it. Configuration is done through the Configuration menu items above (teams, stages, tags, spreadsheet templates).

---

## 3. Key Models

### 3.1 quality.point (Control Point)

Defines WHERE and HOW quality checks are automatically generated.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Auto-sequence QCP00001 |
| `title` | Char | Human-readable title |
| `team_id` | M2O quality.alert.team | Required |
| `product_ids` | M2M product.product | Filter: storable products. Empty = all products |
| `product_category_ids` | M2M product.category | Alternative to product filter |
| `picking_type_ids` | M2M stock.picking.type | **Required** -- which operations trigger checks |
| `measure_on` | Selection | `operation` / `product` (default) / `move_line` (Quantity) |
| `measure_frequency_type` | Selection | `all` (default) / `random` / `periodical` / `on_demand` |
| `measure_frequency_value` | Float | % probability (for random) |
| `measure_frequency_unit_value` | Integer | Interval value (for periodical) |
| `measure_frequency_unit` | Selection | `day` / `week` / `month` |
| `testing_percentage_within_lot` | Float | Partial lot testing (default 100%) |
| `test_type_id` | M2O quality.point.test_type | See test types below |
| `norm` | Float | Expected measure value |
| `tolerance_min` / `tolerance_max` | Float | Acceptable range for measure type |
| `norm_unit` | Char | Unit label (default "mm") |
| `failure_message` | Html | Shown when check fails |
| `failure_location_ids` | M2M stock.location | Where to route failed products |
| `spreadsheet_template_id` | M2O quality.spreadsheet.template | For spreadsheet test type |
| `note` | Html | Instructions |
| `user_id` | M2O res.users | Responsible |

### 3.2 quality.check (Quality Check)

Individual check instance, auto-created from control points on stock moves.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Auto-sequence QC00001 |
| `title` | Char | Computed from point_id |
| `point_id` | M2O quality.point | Source control point |
| `quality_state` | Selection | `none` (To do) / `pass` / `fail` |
| `product_id` | M2O product.product | Checked product |
| `picking_id` | M2O stock.picking | Related transfer |
| `lot_ids` | M2M stock.lot | Lot/serial traceability |
| `measure` | Float | Measured value (for measure type) |
| `measure_success` | Selection | Computed: `none` / `pass` / `fail` |
| `measure_on` | Selection | Inherited from point |
| `move_line_id` | M2O stock.move.line | For per-quantity checks |
| `qty_line` / `qty_tested` / `qty_passed` / `qty_failed` | Float | Quantity tracking |
| `test_type_id` | M2O quality.point.test_type | |
| `picture` | Binary | Photo evidence (for picture type) |
| `additional_note` | Text | Inspector notes |
| `team_id` | M2O quality.alert.team | |
| `user_id` | M2O res.users | Who performed the check |
| `control_date` | Datetime | When checked |
| `failure_location_id` | M2O stock.location | Where failed qty was routed |
| `spreadsheet_id` | M2O quality.check.spreadsheet | |
| `alert_ids` | O2M quality.alert | Alerts created from this check |

**Key methods:**
- `do_pass()` / `do_fail()` -- state transitions, sets user + timestamp
- `do_measure()` -- auto-passes or auto-fails based on tolerance
- `do_alert()` -- creates a quality.alert from a failed check
- `action_open_quality_check_wizard()` -- batch wizard for multiple checks
- `action_open_spreadsheet()` -- opens spreadsheet check

### 3.3 quality.alert

Issue tracking for quality problems. Kanban-based workflow with stages.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Auto-sequence QA00001 |
| `title` | Char | Alert title |
| `product_tmpl_id` / `product_id` | M2O | Affected product |
| `lot_ids` | M2M stock.lot | |
| `picking_id` | M2O stock.picking | |
| `check_id` | M2O quality.check | Source check |
| `stage_id` | M2O quality.alert.stage | Kanban stages |
| `team_id` | M2O quality.alert.team | |
| `user_id` | M2O res.users | Assigned to |
| `tag_ids` | M2M quality.tag | |
| `reason_id` | M2O quality.reason | Root cause |
| `priority` | Selection | Priority widget |
| `description` | Html | Issue description |
| `action_corrective` | Html | Corrective actions taken |
| `action_preventive` | Html | Preventive actions taken |
| `partner_id` | M2O res.partner | |
| `date_assign` / `date_close` | Datetime | |

**Email integration:** Alerts can be created via email alias (configured per team).

### 3.4 Supporting Models

| Model | Purpose |
|---|---|
| `quality.alert.team` | Teams that own checks/alerts. Has email alias. Dashboard shows counts. |
| `quality.alert.stage` | Kanban stages for alerts (New, Confirmed, Action Proposed, Solved) |
| `quality.point.test_type` | Test type definitions (see below) |
| `quality.reason` | Root causes (Workcenter Failure, Parts Quality, Work Operation, Others) |
| `quality.tag` | Free-form tags for alerts |
| `quality.check.wizard` | Wizard for batch check execution from pickings |
| `quality.check.spreadsheet` | Spreadsheet data linked to a check |
| `quality.spreadsheet.template` | Reusable spreadsheet templates for checks |

---

## 4. Test Types (quality.point.test_type)

Defined across `quality` base and `quality_control`:

| Name | Technical Name | Source |
|---|---|---|
| Instructions | `instructions` | quality (base) |
| Take a Picture | `picture` | quality (base) |
| Pass - Fail | `passfail` | quality_control |
| Measure | `measure` | quality_control |
| Spreadsheet | `spreadsheet` | quality_control |

Additional test types added by companion modules (see section 8).

---

## 5. Stock Integration (Auto-Check Generation)

**Critical mechanism for Percimon:**

1. `stock.move._action_confirm()` calls `_create_quality_checks()`
2. For each confirmed picking, the system searches `quality.point` records matching:
   - The picking's `picking_type_id` (operation type)
   - The move's `product_id` (or product category, or all products)
   - The `measure_on` setting (operation / product / quantity)
   - The frequency rules (all, random %, periodical, on-demand)
3. Creates `quality.check` records linked to the picking
4. **Blocking validation:** `stock.picking._action_done()` raises `UserError` if pending checks exist
5. Wizard (`quality.check.wizard`) pops up during picking validation for batch check execution

**Failure routing:** When a check fails with `failure_location_ids` configured, failed quantities can be automatically routed to a scrap/quarantine location.

### stock.picking extensions

- `check_ids` (O2M) -- all quality checks for this transfer
- `quality_check_todo` / `quality_check_fail` -- computed booleans
- `quality_alert_ids` / `quality_alert_count` -- linked alerts
- `check_quality()` -- opens wizard for pending checks
- Buttons: "Quality Check" on picking form, "Quality Alert" button

### stock.move.line extensions

- `check_ids` (O2M) -- checks linked to specific move lines (for per-quantity control)

---

## 6. Reports

| Report | Model | Format | Notes |
|---|---|---|---|
| Worksheet Report - External (PDF) | quality.check | qweb-pdf | `quality_control.quality_worksheet` -- customer-facing |
| Worksheet Report - Internal (PDF) | quality.check | qweb-pdf | `quality_control.quality_worksheet_internal` -- internal layout |

Report template shows: check name, state, transfer, product, lot, tester, date, test type, measure value/warning, picture if applicable.

---

## 7. Wizard

**quality.check.wizard** -- Multi-check execution wizard

- Navigates through multiple checks (Previous / Next buttons)
- Shows position counter (e.g., "2 / 5")
- Per-check actions: Pass, Fail, Validate (measure), Open Spreadsheet
- Failure dialog: quantity failed, lot/SN, failure location selection
- Supports partial lot testing (`qty_to_test`, `qty_tested`)

---

## 8. Companion Modules

| Module | Auto-install | Purpose |
|---|---|---|
| `quality_mrp` | Yes (quality_control + mrp) | Adds workcenters to QC, quality checks on manufacturing orders |
| `quality_mrp_workorder` | -- | Quality checks on work orders (shop floor) |
| `quality_mrp_workorder_worksheet` | -- | Custom worksheets on work orders |
| `quality_mrp_workorder_iot` | -- | IoT devices on work order quality checks |
| `quality_control_worksheet` | No | Custom worksheet templates (uses `worksheet` module) |
| `quality_control_iot` | Yes (quality_control + quality_iot) | IoT device integration for checks |
| `quality_control_picking_batch` | -- | Quality checks on batch pickings |
| `quality_iot` | -- | Base IoT quality integration |
| `quality_repair` | Yes (quality_control + repair) | Quality checks on repair orders |
| `stock_barcode_quality_control` | -- | Barcode scanning for quality checks |
| `stock_barcode_quality_control_picking_batch` | -- | Barcode + batch picking quality |
| `stock_barcode_quality_mrp` | -- | Barcode + MRP quality |
| `mrp_subcontracting_quality` | -- | Quality checks on subcontracted MFG |
| `purchase_mrp_workorder_quality` | -- | Purchase + MRP workorder quality |

---

## 9. Demo Data

The `quality_control_demo.xml` creates:

- **quality_point1** -- Pass/fail check on "Drawer" product, triggered on Receipts
- **quality_point2** -- Pass/fail check on "Office Lamp" product, triggered on Receipts
- **quality_spreadsheet_template_cabinet** -- Spreadsheet template "Quality Control Spreadsheet" with check cell B17
- **quality_point_with_spreadsheet** -- Spreadsheet-type check on "Large Cabinet" + "Acoustic Bloc Screen", triggered on Receipts
- Calls `stock.move._create_quality_checks()` for all waiting/confirmed/assigned moves

---

## 10. Security

**Groups (from quality base):**
- `quality.group_quality_user` -- Quality User (read checks, execute checks)
- `quality.group_quality_manager` -- Quality Manager (full CRUD, configuration access)

**Access rules (quality_control additions):**
- `quality.check.wizard` -- User: read/write/create
- `quality.check.spreadsheet` -- User: read/write/create; Manager: +unlink
- `quality.spreadsheet.template` -- User: read only; Manager: full CRUD

**Record rules:** Company-based isolation on spreadsheets and templates.

---

## 11. Percimon Relevance -- Store Opening Checklists

### How to implement "Acto 3" (mandatory store opening checklist)

The `quality_control` module does NOT have a native POS integration. There is no `pos_quality` bridge module in Odoo 19.0. Quality checks are designed around **stock picking operations** (receipts, deliveries, internal transfers, manufacturing).

### Recommended approach for Percimon

**Option A -- Quality Checks on Internal Transfer (recommended for demo):**
1. Create an operation type "Store Opening Check" (internal transfer type)
2. Create quality.point records tied to that operation type:
   - **"Clean Ice Cream Machine"** -- test type: `passfail`, measure_on: `operation`, frequency: `all`
   - **"Record Display Case Temperature"** -- test type: `measure`, measure_on: `operation`, norm: -18, tolerance_min: -22, tolerance_max: -15, norm_unit: C
   - **"Sanitize Serving Area"** -- test type: `passfail`
   - **"Check Topping Freshness"** -- test type: `passfail`
3. Each morning, the store manager creates/confirms the internal transfer, which auto-generates all checks
4. The quality check wizard pops up and must be completed before the transfer can be validated
5. This creates an auditable trail (who checked, when, measure values, pass/fail)

**Option B -- Quality Control Worksheet (richer UX):**
- Install `quality_control_worksheet` companion module
- Create a custom worksheet template with all checklist fields
- Attach to a quality point -- provides a form-like experience

**Key data to create:**
- `quality.alert.team`: "Percimon Store QA"
- `quality.point` records: one per checklist item, all tied to "Store Opening" operation type
- Optionally: `quality.spreadsheet.template` for temperature logging spreadsheet

### Models to load via CSV

| Priority | Model | Purpose |
|---|---|---|
| 1 | `quality.alert.team` | "Percimon Store QA" team |
| 2 | `quality.point` | Control points for each checklist item |
| 3 | `quality.alert.stage` | Custom stages if needed (defaults exist) |

### Identity keys for deduplication

| Model | Identity Key(s) |
|---|---|
| `quality.alert.team` | `name` |
| `quality.point` | `title` + `picking_type_ids` |
| `quality.check` | `name` (auto-sequenced, usually not loaded via CSV) |
| `quality.alert` | `name` (auto-sequenced, usually not loaded via CSV) |
