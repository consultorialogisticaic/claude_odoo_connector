# Feature Catalog — Maintenance (maintenance)

**Version:** 19.0
**Source:** community
**Category:** Supply Chain/Maintenance
**Dependencies:** mail

## Business Capabilities

- **Equipment registry:** Catalog all physical assets (ice cream machines, refrigerators, payment terminals) with serial numbers, vendor info, warranty dates, cost, and ownership tracking.
- **Maintenance request management:** Create, assign, and track corrective and preventive maintenance requests through a configurable stage pipeline (New Request > In Progress > Repaired > Scrap).
- **Preventive maintenance scheduling:** Set up recurring maintenance tasks (daily, weekly, monthly, yearly) with automatic creation of follow-up requests when the current one is completed.
- **Reliability metrics (MTBF/MTTR):** Automatically compute Mean Time Between Failure and Mean Time To Repair per equipment, with estimated next failure date based on historical corrective maintenance data.
- **Team-based work organization:** Organize technicians into maintenance teams with email aliases for request intake, dashboard with KPIs (to-do count, blocked, high priority, unscheduled).

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| Maintenance > Dashboard | Team Dashboard | Kanban overview of all maintenance teams with KPIs: to-do count, scheduled, top priorities, blocked, unscheduled requests |
| Maintenance > Maintenance > Maintenance Requests | Maintenance Requests | Kanban/list/form view of all maintenance requests with stage pipeline |
| Maintenance > Maintenance > Maintenance Calendar | Maintenance Calendar | Calendar view of scheduled maintenance tasks with drag-and-drop rescheduling |
| Maintenance > Equipment | Equipment | Kanban/list of all registered equipment with owner, serial number, maintenance count |
| Maintenance > Reporting > Maintenance Requests Analysis | Requests Analysis | Graph/pivot analysis of requests by technician, stage, duration |
| Maintenance > Configuration > Settings | Settings | Module settings (Custom Worksheets toggle) |
| Maintenance > Configuration > Maintenance Teams | Maintenance Teams | Team setup: name, members, email alias, company |
| Maintenance > Configuration > Equipment Categories | Equipment Categories | Category definitions with default technician, custom properties |
| Maintenance > Configuration > Maintenance Stages | Maintenance Stages | Stage pipeline configuration with fold/done flags (developer mode) |

### Settings & Feature Flags

| Setting | Technical Field | What it Enables |
|---|---|---|
| Custom Maintenance Worksheets | `module_maintenance_worksheet` | Installs `maintenance_worksheet` (enterprise) for custom checklist/worksheet templates on maintenance requests |

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `maintenance.request` | Primary | Maintenance requests (corrective or preventive) with scheduling, recurrence, priority, instructions, stage tracking | Yes |
| `maintenance.equipment` | Primary | Physical assets with serial number, model, vendor, warranty, cost, owner, MTBF/MTTR metrics | Yes |
| `maintenance.equipment.category` | Configuration | Equipment categories (e.g., "Ice Cream Machines," "Payment Terminals") with default technician and custom properties definition | Yes |
| `maintenance.team` | Configuration | Maintenance teams with members, email alias, dashboard KPIs (to-do, blocked, high priority, unscheduled) | Yes |
| `maintenance.stage` | Configuration | Pipeline stages: New Request, In Progress, Repaired, Scrap (with done/fold flags) | Yes |
| `maintenance.mixin` | Abstract | Shared fields for maintained items: effective date, MTBF, MTTR, estimated next failure, maintenance team | No (inherited by equipment) |

### Reports & Analytics

- **Maintenance Requests Analysis** (`maintenance.request` with graph/pivot views): Measures include duration (hours), groupable by technician, stage, category, equipment, maintenance type (corrective/preventive), schedule date, request date.
- **Team Dashboard** (kanban): Per-team KPIs showing to-do count, scheduled requests, top priorities, blocked requests, unscheduled count. Quick links to filtered request views.
- **Equipment Maintenance Tab**: Per-equipment statistics showing Expected MTBF, computed MTBF, MTTR, latest failure date, and estimated next failure date.

### Wizards & Advanced Actions

| Action | Type | Purpose |
|---|---|---|
| Cancel Request | Button (`archive_equipment_request`) | Archives a maintenance request and disables its recurrence |
| Reopen Request | Button (`reset_equipment_request`) | Reopens a cancelled request by moving it back to the first pipeline stage |
| Recurring Maintenance Auto-Copy | Write override | When a recurring preventive request reaches a "done" stage, automatically creates the next occurrence with the computed schedule date |

### Key Features Detail

**Recurrence System** (source: `maintenance.py` lines 244-256):
Preventive maintenance requests support recurrence with configurable interval (N days/weeks/months/years) and end condition (forever or until a date). When a recurring request is marked done, Odoo automatically creates the next request with the schedule date advanced by the interval.

**Maintenance Instructions** (source: `maintenance.py` lines 237-243):
Each request supports three instruction formats: PDF upload, Google Slide link, or rich text. This allows technicians to attach checklists, manuals, or visual guides to each maintenance task.

**Equipment Properties** (source: `maintenance.py` line 146):
Equipment categories define custom properties (via `PropertiesDefinition`), and each equipment record carries its own property values. This allows defining category-specific attributes like "Compressor Type," "Refrigerant Gas," "Last Calibration Date" without code changes.

**Email Alias for Teams** (source: `maintenance.py` lines 451-457):
Each maintenance team can have an email alias. Emails sent to the alias automatically create maintenance requests assigned to that team.

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `maintenance_worksheet` | enterprise | Custom worksheet templates for maintenance requests (checklists, forms, inspection reports) |
| `hr_maintenance` | community | Links equipment to employees and departments; employees can request equipment allocation |
| `stock_maintenance` | community | Links maintenance to inventory lot/serial tracking; see which stock lots are used in maintenance |

## Demo Highlights

1. **Preventive Maintenance Scheduling with Recurrence** -- Set up a monthly preventive maintenance schedule for each ice cream machine across all Percimon stores. When a technician completes the current task, the next one is auto-created for the following month. Show the calendar view with all upcoming interventions color-coded by technician.

2. **Equipment Registry with MTBF/MTTR Metrics** -- Register each ice cream machine with serial number, vendor, warranty date, and store assignment. After logging a few corrective maintenance requests, the system automatically computes Mean Time Between Failure and estimates the next likely failure date. This is a powerful predictive maintenance insight for a frozen yogurt chain.

3. **Equipment Category Custom Properties** -- Create an "Ice Cream Machines" category with custom properties: Compressor Type, Refrigerant Gas, Last Calibration Date, Capacity (liters). Each machine inherits these fields. No development needed -- fully configurable.

4. **Team Dashboard with Real-Time KPIs** -- Show the dashboard with teams like "Mantenimiento Tiendas" and "Soporte Sistemas de Pago." Each card shows to-do count, blocked requests, high-priority items, and unscheduled tasks. Operations managers see the full picture at a glance.

5. **Maintenance Instructions with PDF/Text** -- Attach step-by-step PDF checklists to preventive maintenance tasks (e.g., "Monthly Ice Cream Machine Inspection Checklist"). Technicians see the instructions directly on the request form, ensuring consistent maintenance quality across all stores.
