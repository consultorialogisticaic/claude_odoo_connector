# Odoo 18 Spreadsheet Dashboards UI/UX Analysis Report

## Executive Summary

Odoo 18 Spreadsheet Dashboards provide a rich, interactive dashboard experience built on the o-spreadsheet engine. The UI is designed for both desktop and mobile users, with distinct modes for viewing (read-only), editing (admin-only in enterprise), and sharing (public readonly). The implementation leverages OWL components, XML templates, and a sophisticated plugin architecture for managing global filters, pivots, charts, and lists.

---

## 1. Navigation & Entry Points

### Menu Structure
- **Menu ID**: `spreadsheet_dashboard_menu_root`
- **Location**: Main Odoo menu (sequence 37, typically between Settings and Reports)
- **Display**: "Dashboards" with icon from `spreadsheet_dashboard,static/description/icon.png`
- **XML File**: `/addons/spreadsheet_dashboard/views/menu_views.xml`

Two submenu items appear:
1. **Dashboards** (id: `spreadsheet_dashboard_menu_dashboard`)
   - Links to action: `ir_actions_dashboard_action`
   - Displays the main dashboard viewer

2. **Configuration > Dashboards** (id: `spreadsheet_dashboard_menu_configuration_dashboards`)
   - Admin-only access for managing dashboard groups and permissions
   - Uses `spreadsheet_dashboard_action_configuration_dashboards` (model: `spreadsheet.dashboard.group`)

### Main Action
- **Action XML ID**: `ir_actions_dashboard_action`
- **Action Type**: `ir.actions.client`
- **Tag**: `action_spreadsheet_dashboard`
- **OWL Component**: `SpreadsheetDashboardAction`
- **Component File**: `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.js`

**User Visible Behavior**: Clicking "Dashboards" in the menu launches the main dashboard viewer with a sidebar listing all available dashboards grouped by access groups, and the main canvas showing the currently selected dashboard.

---

## 2. Dashboard View Layout (Desktop & Responsive)

### OWL Component Tree

```
SpreadsheetDashboardAction (top-level action)
├── ControlPanel (top bar with filters and share button)
│   ├── FilterValue (for each global filter)
│   └── SpreadsheetShareButton
├── o_content (main layout container)
│   ├── [Mobile]: DashboardMobileSearchPanel (portal-rendered dropdown)
│   ├── [Desktop - Expanded]: Sidebar (expanded dashboard list)
│   │   └── Dashboard groups with list items
│   ├── [Desktop - Collapsed]: Sidebar toggle button
│   └── Main content area
│       ├── [Mobile]: MobileFigureContainer (charts only)
│       └── [Desktop]: SpreadsheetComponent
│           └── Spreadsheet (from o-spreadsheet)
```

### Component Files & Templates

| Component | File | Template ID | Responsibility |
|-----------|------|------------|-----------------|
| **SpreadsheetDashboardAction** | `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.js` | `spreadsheet_dashboard.DashboardAction` | Main orchestration, state management, sidebar toggle, dashboard selection |
| **DashboardMobileSearchPanel** | `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_search_panel/mobile_search_panel.js` | `spreadsheet_dashboard.DashboardMobileSearchPanel` | Mobile dashboard selection via dropdown overlay |
| **MobileFigureContainer** | `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_figure_container/mobile_figure_container.js` | `documents_spreadsheet.MobileFigureContainer` | Mobile rendering of chart/figure elements (non-spreadsheet) |
| **SpreadsheetComponent** | `/addons/spreadsheet/static/src/actions/spreadsheet_component.js` | `spreadsheet.SpreadsheetComponent` | Wraps o-spreadsheet's `<Spreadsheet>` with Odoo integrations |

### Layout Structure (Desktop)

**Template**: `spreadsheet_dashboard.DashboardAction` in `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.xml`

**Key CSS Classes**:
- `o_action` – main action container
- `o_spreadsheet_dashboard_action` – dashboard-specific styling
- `o_component_with_search_panel` – enables sidebar layout
- `o_mobile_dashboard` – (conditional) applied when `env.isSmall` is true

**Desktop Expanded Sidebar** (`spreadsheet_dashboard.DashboardAction.Expanded`):
- Class: `o_spreadsheet_dashboard_search_panel o_search_panel`
- Contains sections (groups) with list items for each dashboard
- Each dashboard item is clickable, showing `dashboard.displayName`
- Admin/editor button appears on hover (placeholder for dashboard editor button)
- Collapse button (angle-left icon) in top-right

**Desktop Collapsed Sidebar** (`spreadsheet_dashboard.DashboardAction.Collapsed`):
- Shows only breadcrumb and expand button
- Displays group name / dashboard name vertically
- Clicking anywhere toggles to expanded state

**Main Content**:
- For Desktop: Renders `SpreadsheetComponent` with active dashboard's model
- For Mobile: Renders `MobileFigureContainer` showing only charts/figures
- Loading states: Shows "Loading..." text during fetch
- Error states: Shows error message if dashboard fails to load

### Responsive Breakpoints
- **Mobile** (`env.isSmall === true`): Uses portal-based search panel overlay, MobileFigureContainer for charts
- **Desktop** (`env.isSmall === false`): Sidebar with two states (expanded/collapsed), full SpreadsheetComponent

---

## 3. Global Filters Bar

### In Dashboard View Mode (Read-Only)

**Location**: Control Panel, left side (`layout-actions` slot)

**Template**: `spreadsheet_edition.FilterValue` (community)

**Component**: `FilterValue` from `/addons/spreadsheet/static/src/global_filters/components/filter_value/filter_value.js`

**Behavior**:
- Filters are displayed horizontally in the control panel
- Each filter shows a `FilterValue` sub-component based on type:
  - **Date**: Dropdown (relative) or date range picker (from/to) or period selector
  - **Relation**: Multi-record selector dropdown
  - **Text**: Text input with optional allowed values
- Each filter has a clear (×) button if a value is active
- Filters are applied immediately to all data sources on change
- Filtering is read-only in dashboard view (users can select values but not edit filter definitions)

**Visible Elements**:
- Filter label (from `filter.label`)
- Type-specific input (dropdown, date picker, relation selector)
- Clear button (×) if active

### In Dashboard Edit Mode (Enterprise)

**Location**: Right-side panel (Global Filters tab)

**Template**: `spreadsheet_edition.GlobalFiltersSidePanel` in `/enterprise/spreadsheet_edition/static/src/bundle/global_filters/global_filter_side_panel.xml`

**Component**: `GlobalFiltersSidePanel` from `/enterprise/spreadsheet_edition/static/src/bundle/global_filters/global_filters_side_panel.js`

**Behavior** (Admin/Editor only):
- Displays all global filters in a scrollable list on right sidebar
- Each filter shows:
  - Drag handle (move to reorder)
  - Filter label
  - Current filter value (using same `FilterValue` component)
  - Cog icon (edit button) to open filter configuration side panel
- Below filters: "Add a new filter..." section with three buttons:
  - Date (opens `DATE_FILTER_SIDE_PANEL`)
  - Relation (opens `RELATION_FILTER_SIDE_PANEL`)
  - Text (opens `TEXT_FILTER_SIDE_PANEL`)
- Drag-and-drop reordering with visual feedback (dragging class applied)

**Filter Configuration Side Panels** (edit mode):
- **Date**: `date_filter_editor_side_panel.xml` – choose range type (relative/from_to/period), disable certain periods
- **Relation**: `relation_filter_editor_side_panel.xml` – select model, define domain, field matching
- **Text**: `text_filter_editor_side_panel.xml` – define allowed values, default value

---

## 4. Insert in Spreadsheet Dialog (Enterprise)

### Trigger Point
When a user clicks an action (e.g., "Insert in Spreadsheet") from a pivot, graph, or list view in an Odoo module.

### Dialog Component

**Template**: `spreadsheet_edition.SpreadsheetSelectorDialog` in `/enterprise/spreadsheet_edition/static/src/assets/components/spreadsheet_selector_dialog/spreadsheet_selector_dialog.xml`

**Component**: `SpreadsheetSelectorDialog` from `/enterprise/spreadsheet_edition/static/src/assets/components/spreadsheet_selector_dialog/spreadsheet_selector_dialog.js`

**Child Components**:
- `SpreadsheetSelectorPanel` (per model tab) – displays grid of available spreadsheets/dashboards for insertion

### Dialog Behavior

**Flow**:
1. Dialog opens with title: "Select a spreadsheet to insert your [PIVOT/GRAPH/LIST]."
2. User enters name for the object (e.g., "Sales by Region")
3. If inserting from a list, user specifies record threshold ("Insert the first N records...")
4. Notebook widget shows tabs for each spreadsheet model (e.g., "Spreadsheet", "Dashboard")
5. Each tab displays a grid of available spreadsheets with thumbnails
6. User can:
   - Select existing spreadsheet/dashboard
   - Double-click to confirm immediately
   - Click "Create new spreadsheet" or "Create new dashboard" option (if allowed)
7. Confirm button inserts the data and optionally opens the created spreadsheet

**User-Visible Elements**:
- Name input field (required)
- Threshold input (for lists)
- Spreadsheet/Dashboard selector tabs
- Grid of available items (name, thumbnail, last modified)
- Confirm and Cancel buttons

---

## 5. Dashboard Editing UI (Enterprise)

### Entry Point
Clicking the pencil icon (edit button) in the dashboard sidebar (when user is admin).

### Edit Action

**Action XML ID**: `action_edit_dashboard`

**OWL Component**: `DashboardEditAction` from `/enterprise/spreadsheet_dashboard_edition/static/src/bundle/action/dashboard_edit_action.js`

**Template**: `spreadsheet_dashboard_edition.DashboardEditAction` in `/enterprise/spreadsheet_dashboard_edition/static/src/bundle/action/dashboard_edit_action.xml`

**Component Hierarchy**:
```
DashboardEditAction
├── SpreadsheetNavbar (enterprise navbar with breadcrumb and name editor)
└── SpreadsheetComponent (full editing interface)
    └── Spreadsheet (o-spreadsheet engine)
        ├── Toolbar (insert pivot, chart, list, shapes, images)
        ├── Right side panels
        │   ├── Global Filters panel (GlobalFiltersSidePanel)
        │   ├── Pivot configuration panel
        │   ├── Chart configuration panel
        │   └── List configuration panel
        └── Canvas (spreadsheet cells + figures)
```

### Navbar Components (Enterprise)

**File**: `/enterprise/spreadsheet_edition/static/src/bundle/components/spreadsheet_navbar/spreadsheet_navbar.xml`

**Component**: `SpreadsheetNavbar` extends `EnterpriseNavBar`

**Features**:
- Spreadsheet icon (left) + brand text "Spreadsheet"
- Breadcrumb (parent action name, e.g., "Dashboards")
- Spreadsheet name editor (inline edit or read-only)
- Optional navbar action slots (e.g., Share button, Save status)
- Back button on mobile

### Edit Mode Features

**Toolbar Integration**:
- Insert menu: Pivot, Chart, List, Image, Link, Shapes
- Edit toolbar (from o-spreadsheet): formula bar, font formatting, borders, alignment

**Right-Side Panels** (managed by side panel registry):
1. **Global Filters Panel** – add/edit/delete/reorder global filters (drag-and-drop)
2. **Pivot Configuration Panel** – layout, measures, filters for selected pivot
3. **Chart Configuration Panel** – chart type, series, axes, styling
4. **List Configuration Panel** – fields, sorting, grouping, domain filters

**Publishing Control**:
- Button/toggle to publish/unpublish dashboard (if `isDashboardPublished` env variable is set)
- Published dashboards are visible to groups in read-only mode

---

## 6. Sharing UI

### Share Button Location
- In dashboard view (read-only): Control panel, right side (`control-panel-navigation-additional` slot)
- In edit mode: Top-right corner via `TopbarShareButton`

### Share Button Component

**File**: `/addons/spreadsheet/static/src/components/share_button/share_button.js`

**Template**: `spreadsheet.ShareButton`

**OWL Component**: `SpreadsheetShareButton`

### Share Dialog Behavior

1. **Closed State**: Shows "Share" button with icon
2. **Open State**: Dropdown menu displays:
   - If URL is ready:
     - Icon (globe) + text: "Spreadsheet published" / "Frozen version - Anyone can view"
     - URL field (copy-to-clipboard button)
   - If generating:
     - Spinner + text: "Generating sharing link"
3. **URL Generation**:
   - Freezes current Odoo data (global filters, locale, cell contents)
   - Calls backend: `spreadsheet.dashboard.share / action_get_share_url`
   - Returns public readonly URL
4. **Automatic Copy**: URL is automatically copied to clipboard (silent, no notification)

### Public Readonly View

**Component**: `PublicReadonlySpreadsheet` from `/addons/spreadsheet/static/src/public_readonly_app/public_readonly.js`

**Template**: `spreadsheet.PublicReadonlySpreadsheet`

**Features**:
- Read-only mode (no editing allowed)
- Dashboard mode: displays global filters in a collapsible filter panel
- Filter button appears if filters exist and are not shown
- Shows frozen data (from share time) + current global filter values
- Export to Excel support (if enabled)

**Visible Elements**:
- Optional filter button (top-left): "Show Filters" with icon
- Filter panel (collapsible): Lists all active filters with labels and values
- Spreadsheet canvas (read-only, interactive charts/figures)

---

## 7. Mobile Experience

### Mobile Detection
Responsive UI triggered by `env.isSmall` property (Odoo's standard mobile breakpoint, typically < 768px or touch device).

### Dashboard View (Mobile)

**Key Changes**:
1. **Search Panel**: Replaced with `DashboardMobileSearchPanel`
   - Shows as button: "FILTER_ICON + Current Dashboard Name"
   - Clicking opens full-screen portal-rendered panel
   - Panel shows all groups and dashboards in a list with checkmarks
   - "BACK" button to dismiss

2. **Main Content**: Replaced with `MobileFigureContainer`
   - Only displays chart/figure elements (no spreadsheet cells)
   - Figures displayed as full-width cards (height per figure config)
   - Figures sorted by position (x, y coordinates)
   - Clicking a figure with Odoo menu navigates to related menu item

3. **Control Panel**: Same filter bar as desktop
4. **Sidebar**: Hidden (no expanded/collapsed sidebar on mobile)

### Mobile Search Panel Template
**File**: `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_search_panel/mobile_search_panel.xml`

- Uses `<t t-portal="'body'">` to render outside component hierarchy
- Full-screen overlay with:
  - Header: BACK button + title "BACK"
  - Content: Scrollable group/dashboard list
  - Each item shows active state (bold, text-900) if current dashboard
  - Clicking dismisses panel and loads dashboard

### Mobile Figure Container
**File**: `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_figure_container/mobile_figure_container.xml`

- Renders only chart/figure elements
- Each figure: `<div>` with calculated width (window.innerWidth) and height
- Figure component determined by figure registry (bar, line, pie, etc.)
- Click handler navigates to Odoo menu if figure has `ChartOdooMenu`

---

## 8. Global Filter Types & UI

### Date Filters

**Three Range Types**:

1. **Relative** (`rangeType: 'relative'`)
   - UI: `<select>` dropdown with predefined periods
   - Options include: Today, This Week, This Month, Last Month, This Quarter, This Year, etc.
   - Component: `FilterValue` with `<select>`

2. **From/To** (`rangeType: 'from_to'`)
   - UI: Two date pickers (from and to)
   - Component: `DateFromToValue` from `/addons/spreadsheet/static/src/global_filters/components/filter_date_from_to_value/filter_date_from_to_value.js`
   - Displays from/to inputs side-by-side

3. **Period** (`rangeType: 'period'`)
   - UI: Period selector (month/quarter/year) + optional year offset
   - Component: `DateFilterValue` from `/addons/spreadsheet/static/src/global_filters/components/filter_date_value/filter_date_value.js`

### Relation Filters

**UI**: Multi-record selector dropdown

**Component**: `MultiRecordSelector` (from Odoo web core) in `FilterValue`

**Features**:
- Model name comes from `filter.modelName`
- Domain filtering via `filter.domainOfAllowedValues`
- Tag-based selection (can select multiple records)
- Placeholder: "{ filter.label }"
- Validation: Shows error if model not found

### Text Filters

**UI**: Text input or dropdown with allowed values

**Component**: `TextFilterValue` from `/addons/spreadsheet/static/src/global_filters/components/filter_text_value/filter_text_value.js`

**Features**:
- Free text input or select from predefined options (`filter.allowedValues`)
- Optional default value

---

## 9. Sample Dashboards

### Sample Dashboard Mechanism

If a dashboard is empty (no data in main models), a sample dashboard file can be displayed:

**Python Model**: `SpreadsheetDashboard` in `/addons/spreadsheet_dashboard/models/spreadsheet_dashboard.py`

**Fields**:
- `sample_dashboard_file_path` – path to sample JSON file (e.g., from module's data folder)
- `main_data_model_ids` – models to check for empty data
- `is_published` – toggle to show/hide in dashboard menu

**Behavior**:
- If all main models are empty, load and display sample dashboard
- Dashboard marked with `is_sample: True` in response
- UI renders with special styling (`o-sample-dashboard` class)

---

## 10. Data Flow & State Management

### DashboardLoader (State Manager)

**File**: `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_loader.js`

**Responsibilities**:
1. Load dashboard groups and dashboards from ORM
2. Create Model instances on demand (lazy loading)
3. Cache models in component state
4. Support breadcrumb navigation (save/restore state)

**Public Methods**:
- `load()` – fetch groups and dashboard metadata
- `getDashboardGroups()` – return all groups with published dashboards
- `getDashboard(id)` – get or create dashboard model
- `getState()` – serialize state for navigation
- `restoreFromState()` – restore state from breadcrumb

**Model Creation**:
- Uses `OdooDataProvider` to connect to server data sources
- Creates o-spreadsheet `Model` instances with dashboard snapshot
- Applies user locale and company currency

---

## 11. Form Views & Backend Configuration

### Dashboard Group Form

**Model**: `spreadsheet.dashboard.group`

**View ID**: `spreadsheet_dashboard_container_view_form`

**File**: `/addons/spreadsheet_dashboard/views/spreadsheet_dashboard_views.xml`

**Fields Visible**:
- `name` – group name
- `dashboard_ids` – many2many field showing nested dashboard list

### Dashboard List View

**Model**: `spreadsheet.dashboard`

**View ID**: `spreadsheet_dashboard_view_list`

**Fields Editable Inline**:
- `sequence` – drag-to-reorder handle
- `name` – dashboard display name
- `group_ids` – many2many tags (access control)
- `company_id` – multi-company selector
- `spreadsheet_binary_data` – binary field with spreadsheet file upload widget
- `is_published` – boolean toggle (show/hide from menu)
- `dashboard_group_id` – hidden (optional)

**Features**:
- Inline editing (editable="bottom")
- Binary spreadsheet widget for file upload
- Access control via `group_ids`

---

## 12. Action Registry & Extension Points

### Dashboard Action Registry

**Registry**: `dashboardActionRegistry` from `/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.js`

**Purpose**: Register additional buttons/components in the dashboard sidebar

**Usage**:
```javascript
dashboardActionRegistry.add("edit_button", DashboardEditComponent);
```

The first registered component (`dashboardActionRegistry.getAll()[0]`) appears as a button next to each dashboard name in the sidebar.

### Global Filters Side Panel Registry (Enterprise)

**Registry**: Side panel registry (o-spreadsheet plugin system)

**Panels**:
- `TEXT_FILTER_SIDE_PANEL`
- `DATE_FILTER_SIDE_PANEL`
- `RELATION_FILTER_SIDE_PANEL`

**Triggered**: Via `env.openSidePanel(panelId, options)`

---

## 13. CSS Classes & Styling

### Dashboard-Specific Classes

| Class | Purpose |
|-------|---------|
| `o_spreadsheet_dashboard_action` | Main dashboard action container |
| `o_spreadsheet_dashboard_search_panel` | Expanded sidebar |
| `o_search_panel_sidebar` | Collapsed sidebar (cursor-pointer) |
| `o_dashboard_name` | Dashboard list item text |
| `o_mobile_dashboard` | Applied on mobile breakpoint |
| `o-sample-dashboard` | Applied to sample (demo) dashboards |
| `o_filter_value_container` | Container for each filter in control panel |
| `o-filter-value` | Individual filter display |
| `o_side_panel_filter_icon` | Cog icon for filter edit |
| `o-spreadsheet-filter-button` | "Show Filters" button in public readonly mode |
| `o-public-spreadsheet-filters` | Filter panel in public readonly view |

---

## 14. Key Interactions & User Workflows

### Workflow 1: View Dashboard (Viewer)
1. Click "Dashboards" in main menu
2. SpreadsheetDashboardAction loads
3. First dashboard in first group auto-loads
4. User sees:
   - Sidebar with grouped dashboard list
   - Global filters in control panel
   - Spreadsheet canvas with data
   - Share button (if sharing is enabled)
5. User can:
   - Click dashboard name to switch
   - Change filter values
   - Click figures to navigate to related records
   - Print/download spreadsheet (if enabled)
   - Share (generates public readonly URL)

### Workflow 2: Edit Dashboard (Admin/Editor - Enterprise)
1. Click pencil icon next to dashboard name in sidebar
2. DashboardEditAction opens
3. User sees:
   - SpreadsheetNavbar (editable name, breadcrumb)
   - Toolbar (Insert Pivot/Chart/List/Image/Shapes)
   - Right side panels (Global Filters, Pivot Config, Chart Config, List Config)
   - Spreadsheet canvas (editable)
4. User can:
   - Edit name
   - Add/remove/configure global filters
   - Insert and configure pivots, charts, lists
   - Insert images and shapes
   - Drag and drop figures
   - Publish/unpublish dashboard
   - Share
   - Undo/Redo (via o-spreadsheet)

### Workflow 3: Share Dashboard (Any User - Enterprise)
1. In dashboard view or edit mode, click Share button
2. Share dropdown opens
3. If first time:
   - Generates frozen snapshot (global filters + locale + cell content)
   - Calls backend ORM to create share record
   - Returns public readonly URL
   - Copies to clipboard
4. User can:
   - Share URL with anyone
   - Link opens PublicReadonlySpreadsheet (no login required)
   - Viewers can see data + filter and apply filters (but not edit)

### Workflow 4: Insert Pivot/Chart/List into Spreadsheet
1. In pivot/chart/list view, click "Insert in Spreadsheet" action
2. SpreadsheetSelectorDialog opens
3. User enters name, selects target spreadsheet/dashboard
4. Dialog inserts data and (optionally) opens target
5. Data appears in spreadsheet as new pivot/chart/list figure

---

## 15. Summary of File Locations

### Community Edition (Odoo Core)

| Component | File |
|-----------|------|
| Dashboard Action | `/odoo/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.{js,xml}` |
| Dashboard Loader | `/odoo/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_loader.js` |
| Mobile Search Panel | `/odoo/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_search_panel/mobile_search_panel.{js,xml}` |
| Mobile Figure Container | `/odoo/addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/mobile_figure_container/mobile_figure_container.{js,xml}` |
| Menu & Views | `/odoo/addons/spreadsheet_dashboard/views/{menu_views,spreadsheet_dashboard_views}.xml` |
| Models | `/odoo/addons/spreadsheet_dashboard/models/spreadsheet_dashboard.{py,group,share}.py` |
| Filter Value | `/odoo/addons/spreadsheet/static/src/global_filters/components/filter_value/filter_value.{js,xml}` |
| Share Button | `/odoo/addons/spreadsheet/static/src/components/share_button/share_button.{js,xml}` |
| Public Readonly | `/odoo/addons/spreadsheet/static/src/public_readonly_app/public_readonly.{js,xml}` |

### Enterprise Edition (Odoo Enterprise)

| Component | File |
|-----------|------|
| Dashboard Edit Action | `/enterprise/spreadsheet_dashboard_edition/static/src/bundle/action/dashboard_edit_action.{js,xml}` |
| Dashboard Edit Component | `/enterprise/spreadsheet_dashboard_edition/static/src/bundle/components/dashboard_edit/dashboard_edit.{js,xml}` |
| Spreadsheet Selector Dialog | `/enterprise/spreadsheet_edition/static/src/assets/components/spreadsheet_selector_dialog/spreadsheet_selector_dialog.{js,xml}` |
| Spreadsheet Selector Panel | `/enterprise/spreadsheet_edition/static/src/assets/components/spreadsheet_selector_dialog/spreadsheet_selector_panel.{js,xml}` |
| Spreadsheet Navbar | `/enterprise/spreadsheet_edition/static/src/bundle/components/spreadsheet_navbar/spreadsheet_navbar.{js,xml}` |
| Global Filters Side Panel | `/enterprise/spreadsheet_edition/static/src/bundle/global_filters/{global_filters_side_panel.js,global_filter_side_panel.xml}` |
| Filter Editors | `/enterprise/spreadsheet_edition/static/src/bundle/global_filters/components/filter_editor/{date,relation,text}_filter_editor_side_panel.{js,xml}` |
| Topbar Share Button | `/enterprise/spreadsheet_edition/static/src/bundle/components/topbar_share_button/topbar_share_button.{js,xml}` |

---

## 16. Performance & Caching Considerations

- **Lazy Model Loading**: Dashboard models are created only when accessed (not preloaded)
- **State Preservation**: Models cached in component state to survive breadcrumb navigation
- **ORM Service Reuse**: Uses non-protected `this.env.services.orm` to preserve models across action transitions
- **Share URL Caching**: Share button checks if data has changed (revision ID, global filter values) before regenerating URL

---

## 17. Accessibility & Localization

- **Locale Support**: Dashboard applies user locale from `res.lang._get_user_spreadsheet_locale()`
- **Currency**: Company currency fetched for display
- **Translations**: `_t()` used throughout for UI text
- **ARIA Labels**: Edit button has `aria-label="Edit"` and `data-tooltip="Edit"`
- **Keyboard Navigation**: Sidebar items and buttons use standard HTML inputs/buttons
- **Mobile Accessibility**: Full-screen portal overlay for mobile search panel prevents layout shifts

---

## Conclusion

The Odoo 18 Spreadsheet Dashboards UI/UX is a sophisticated, modular system that balances simplicity for end-users with powerful customization capabilities for administrators. The use of OWL components, o-spreadsheet engine, and a plugin architecture allows for extensibility while maintaining a consistent user experience across desktop, mobile, and shared/readonly modes.

Key design principles:
- **Progressive Disclosure**: Viewers see simple dashboard view; editors access side panels for config
- **Responsive Design**: Same codebase serves desktop, tablet, and mobile with appropriate layout adjustments
- **Modular Architecture**: Each concern (filters, pivots, charts, sharing) encapsulated in reusable components
- **Non-Invasive Editing**: Dashboards maintain separate edit mode (enterprise) to avoid accidental changes by viewers
