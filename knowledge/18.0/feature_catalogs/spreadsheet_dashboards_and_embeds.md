# Odoo 18 — Spreadsheet Dashboards and Embedded Pivot/Graph Views

Technical reference compiled from `odoo/odoo@18.0` and `odoo/enterprise@18.0` source.

## 1. Data Model

### 1.1 Core models

**`spreadsheet.dashboard`** — `addons/spreadsheet_dashboard/models/spreadsheet_dashboard.py`
- Inherits `spreadsheet.mixin` (binary/JSON storage)
- Fields:
  - `name` (Char, required, translatable)
  - `dashboard_group_id` (M2o `spreadsheet.dashboard.group`, required)
  - `sequence` (Integer)
  - `sample_dashboard_file_path` (Char) — fallback JSON shown when target models are empty
  - `is_published` (Boolean, default True)
  - `company_id` (M2o `res.company`)
  - `group_ids` (M2m `res.groups`) — access control
  - `main_data_model_ids` (M2m `ir.model`) — emptiness check for sample fallback
  - Inherited from `spreadsheet.mixin`:
    - `spreadsheet_binary_data` (Binary) — base64-encoded JSON
    - `spreadsheet_data` (Text, computed) — decoded JSON string
    - `thumbnail` (Binary)

**`spreadsheet.dashboard.group`** — `addons/spreadsheet_dashboard/models/spreadsheet_dashboard_group.py`
- Categorizes dashboards (Sales, Finance, HR, …)
- Fields: `name`, `dashboard_ids` (O2m), `published_dashboard_ids` (filtered), `sequence`
- Pre-defined groups in `addons/spreadsheet_dashboard/data/dashboard.xml`:
  Sales (100), Finance (300), Logistics (400), Services/Project (500), Marketing (600), Website (700), HR (800)

**`spreadsheet.dashboard.share`** — `addons/spreadsheet_dashboard/models/spreadsheet_dashboard_share.py`
- Public share copy with token
- Fields: `dashboard_id`, `excel_export` (Binary, XLSX), `access_token` (UUID), `full_url` (computed)

**`spreadsheet.mixin`** — `addons/spreadsheet/models/spreadsheet_mixin.py`
- AbstractModel for Binary↔JSON conversion
- Methods:
  - `_empty_spreadsheet_data()` (line 128) — returns minimal `{version, sheets, settings, revisionId}`
  - `_compute_spreadsheet_data()` (line 75) — base64 → JSON
  - `_inverse_spreadsheet_data()` (line 88) — JSON → base64
  - `_check_spreadsheet_data()` (line 29) — validates model/field references and XML IDs

### 1.2 Security

`addons/spreadsheet_dashboard/security/security.xml`:
- `ir_rule_spreadsheet_dashboard` (line 4): `[('group_ids', 'in', user.groups_id.ids)]`
- `spreadsheet_dashboard_rule_company` (line 11): `[('company_id', 'in', company_ids + [False])]`
- Group `spreadsheet_dashboard.group_dashboard_manager` (line 23) — gates "Insert in Spreadsheet" via session_info `can_insert_in_spreadsheet`

## 2. Pre-built Dashboard Delivery

### 2.1 Module pattern

Modules `spreadsheet_dashboard_<app>` follow a common shape:

`__manifest__.py`:
```python
'depends': ['spreadsheet_dashboard', 'sale'],
'data': ['data/dashboards.xml'],
'auto_install': ['sale'],
```

`data/dashboards.xml` example (`addons/spreadsheet_dashboard_sale/data/dashboards.xml`, line 4):
```xml
<record id="spreadsheet_dashboard_sales" model="spreadsheet.dashboard">
  <field name="name">Sales</field>
  <field name="spreadsheet_binary_data" type="base64"
         file="spreadsheet_dashboard_sale/data/files/sales_dashboard.json"/>
  <field name="main_data_model_ids" eval="[(4, ref('sale.model_sale_order'))]"/>
  <field name="sample_dashboard_file_path">
    spreadsheet_dashboard_sale/data/files/sales_sample_dashboard.json
  </field>
  <field name="dashboard_group_id" ref="spreadsheet_dashboard.spreadsheet_dashboard_group_sales"/>
  <field name="group_ids" eval="[Command.link(ref('sales_team.group_sale_manager'))]"/>
  <field name="sequence">100</field>
  <field name="is_published">True</field>
</record>
```

`type="base64" file="..."` makes Odoo read the JSON file from disk and base64-encode it into the binary field.

### 2.2 Dashboard JSON top-level schema

```json
{
  "version": 21,
  "sheets": [
    {
      "id": "sheet1",
      "name": "Dashboard",
      "colNumber": 7,
      "rowNumber": 96,
      "rows": { "5": { "size": 40 } },
      "cols": { "0": { "size": 349 } },
      "cells": {
        "A6": { "content": "[Monthly Sales](odoo://view/{...})" }
      },
      "figures": [{ "id": "uuid", "x": 0, "y": 11, "tag": "chart", "data": {...} }],
      "tables": [],
      "comments": {}
    }
  ],
  "pivots": {
    "3": {
      "type": "ODOO",
      "model": "sale.report",
      "domain": [["country_id", "!=", false]],
      "context": {},
      "measures": [...],
      "columns": [...],
      "rows": [...]
    }
  },
  "revisions": [],
  "styles": {}
}
```

## 3. Pivot & Graph Embedding

### 3.1 "Insert in Spreadsheet" action chain

Frontend entry — `enterprise/spreadsheet_edition/static/src/assets/pivot_view/pivot_view.js` line 37:
- `onInsertInSpreadsheet()`:
  1. Collects pivot metadata (title, groupbys, measures, domain, context).
  2. Resolves XML ID via `actionService.loadAction()`.
  3. Opens `SpreadsheetSelectorDialog` (line 86) with `actionOptions`:
     ```javascript
     {
       preProcessingAsyncAction: "insertPivot",
       preProcessingAsyncActionData: {
         metaData: this.model.metaData,
         searchParams: { domain, context },
         name: pivotTitle,
         actionXmlId: xml_id,
       },
     }
     ```

Server-side button visibility — `addons/spreadsheet/models/ir_http.py` line 15 (default False), enhanced in `enterprise/spreadsheet_dashboard_edition/models/ir_http.py` line 11 (True iff user has `group_dashboard_manager`).

### 3.2 Pivot insertion handler (enterprise)

`enterprise/spreadsheet_edition/static/src/bundle/pivot/pivot_init_callback.js` — `insertPivot(pivotData)` (line 38):
1. Maps Odoo pivot metadata to o-spreadsheet definition:
   ```javascript
   const pivot = {
     type: "ODOO",
     domain: new Domain(pivotData.searchParams.domain).toJson(),
     context: pivotData.searchParams.context,
     model: pivotData.metaData.resModel,
     measures: [...],
     columns: addEmptyGranularity(pivotData.metaData.fullColGroupBys, fields),
     rows: addEmptyGranularity(pivotData.metaData.fullRowGroupBys, fields),
     name: pivotData.name,
     actionXmlId: pivotData.actionXmlId,
   };
   ```
2. Generates UUID, dispatches `ADD_PIVOT`, awaits `pivot.load()`, then `INSERT_PIVOT_WITH_TABLE`.
3. Auto-resizes columns and opens pivot side panel.

### 3.3 List view embedding

`enterprise/spreadsheet_edition/static/src/assets/list_view/list_renderer.js` follows the same flow with `viewType: "list"` and `insertList()` callback in `list_init_callback.js`.

## 4. Runtime Evaluation

### 4.1 Formulas

- `=ODOO.PIVOT(pivotId, rowOffset, colOffset)`
- `=PIVOT.HEADER(pivotId, dimension, index)`
- `=PIVOT.VALUE(pivotId, measure, dimension, index)`
- `=ODOO.LIST(listId, rowIndex, field)`
- `=ODOO.FILTER.VALUE(filterName)`

### 4.2 Data loading

`addons/spreadsheet/static/src/pivot/odoo_pivot.js` — `OdooPivot` (line 35):
- Constructor (line 44) stores definition, instantiates `OdooPivotLoader` (line 63).
- Filters out user context keys (line 72) to avoid duplication.
- `load()` (line 179) → `OdooPivotLoader.load()` → `OdooPivotModel` (line 186) → server RPC.

`addons/spreadsheet/static/src/data_sources/server_data.js`:
- `ServerData` (line 89), constructor at line 95 receives ORM service.
- `_getBatchItem()` (line 121): builds `Request {model, method, args}`, caches by `${resModel}/${method}(${JSON.stringify(args)})`.
- Throws `LoadingDataError` on cache miss to trigger async fetch; resolves via `orm.call()`.
- `ListRequestBatch` (line 44): groups concurrent reads into a single RPC call.

### 4.3 Caching/invalidation

- `this.cache` (sync results) and `this.asyncCache` (in-flight Promises) at `server_data.js` line 101.
- `OdooDataProvider` (`odoo_data_provider.js` line 38) emits `data-source-updated`; spreadsheet model re-evaluates affected cells; 10s timeout (line 43).

## 5. JS Architecture

### 5.1 Plugins

Base classes — `addons/spreadsheet/static/src/plugins.js`: `OdooCorePlugin` (state/commands), `OdooUIPlugin` (UI events).

Pivot plugins — `addons/spreadsheet/static/src/pivot/plugins/`:
- `pivot_odoo_core_plugin.js` (line 7): handles legacy `UPDATE_ODOO_PIVOT_DOMAIN`, exports domains via `Domain.toJson()`.
- `pivot_ui_global_filter_plugin.js`: applies global filters to pivot domain.

Chart plugins — `addons/spreadsheet/static/src/chart/plugins/`:
- `odoo_chart_core_plugin.js`, `chart_odoo_menu_plugin.js`, `odoo_chart_ui_plugin.js`.

List plugins — `addons/spreadsheet/static/src/list/plugins/`:
- `list_core_plugin.js`, `list_ui_plugin.js`.

### 5.2 Components

`addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/dashboard_action.js` line 22 — `SpreadsheetDashboardAction` OWL component. Children: `ControlPanel`, `SpreadsheetComponent`, `FilterValue`, `DashboardMobileSearchPanel`, `MobileFigureContainer`, `SpreadsheetShareButton`.

`dashboard_loader.js` — state mixin loading dashboard list and preserving model state across navigation.

### 5.3 Asset bundles

`addons/spreadsheet/__manifest__.py` line 15:
- `spreadsheet.dependencies` — Chart.js + chartjs-luxon adapter
- `spreadsheet.o_spreadsheet` — o-spreadsheet core + pivot/chart/list/menu plugins + XML templates
- `spreadsheet.public_spreadsheet` — public/readonly bundle
- `web.assets_backend` — SCSS/backend assets

`enterprise/spreadsheet_edition/__manifest__.py` line 18:
- Adds pivot/chart/list/comments edition under `spreadsheet.o_spreadsheet`
- Lazy-loads graph/pivot view patches under `web.assets_backend_lazy`

## 6. Authoring a Custom Dashboard Module

### 6.1 Boilerplate

```
spreadsheet_dashboard_myapp/
  __manifest__.py
  data/
    dashboards.xml
    files/
      myapp_dashboard.json
      myapp_sample_dashboard.json
```

`__manifest__.py`:
```python
{
  'name': "Spreadsheet Dashboard for My App",
  'category': 'Hidden',
  'depends': ['spreadsheet_dashboard', 'my_app'],
  'data': ['data/dashboards.xml'],
  'auto_install': ['my_app'],
  'license': 'LGPL-3',
}
```

`data/dashboards.xml`:
```xml
<odoo>
  <record id="spreadsheet_dashboard_group_myapp" model="spreadsheet.dashboard.group">
    <field name="name">My App</field>
    <field name="sequence">450</field>
  </record>

  <record id="spreadsheet_dashboard_myapp" model="spreadsheet.dashboard">
    <field name="name">My App Dashboard</field>
    <field name="spreadsheet_binary_data" type="base64"
           file="spreadsheet_dashboard_myapp/data/files/myapp_dashboard.json"/>
    <field name="main_data_model_ids" eval="[(4, ref('my_app.model_my_model'))]"/>
    <field name="sample_dashboard_file_path">
      spreadsheet_dashboard_myapp/data/files/myapp_sample_dashboard.json
    </field>
    <field name="dashboard_group_id" ref="spreadsheet_dashboard_group_myapp"/>
    <field name="group_ids" eval="[Command.link(ref('base.group_user'))]"/>
    <field name="sequence">100</field>
    <field name="is_published">True</field>
  </record>
</odoo>
```

### 6.2 Minimal dashboard JSON

```json
{
  "version": 21,
  "sheets": [{
    "id": "sheet1",
    "name": "Dashboard",
    "colNumber": 3,
    "rowNumber": 10,
    "cells": {
      "A1": {"content": "Sales Overview"},
      "A2": {"content": "=PIVOT.HEADER(1, \"#state\", 1)"},
      "B2": {"content": "=PIVOT.VALUE(1, \"amount:sum\", \"#state\", 1)"}
    },
    "figures": [{
      "id": "fig-1", "x": 0, "y": 3, "width": 400, "height": 300,
      "tag": "chart",
      "data": { "type": "odoo_bar", "title": {"text": "Sales by State"}, "dataSourceId": 1 }
    }],
    "tables": [], "comments": {}
  }],
  "pivots": {
    "1": {
      "type": "ODOO",
      "model": "my.model",
      "domain": [],
      "context": {},
      "measures": [{"id": "amount:sum", "fieldName": "amount", "aggregator": "sum"}],
      "rows": [{"fieldName": "state"}],
      "columns": []
    }
  },
  "revisions": [], "styles": {}
}
```

### 6.3 Schemas

**Pivot definition**:
```json
{
  "type": "ODOO",
  "model": "model.name",
  "domain": [["field", "=", "value"]],
  "context": {"group_by": []},
  "name": "Pivot Name",
  "actionXmlId": "module.action_id",
  "measures": [{"id": "field:agg", "fieldName": "field", "aggregator": "sum|avg|count|max|min"}],
  "rows":    [{"fieldName": "field", "granularity": "year|quarter|month|week|day"}],
  "columns": [{"fieldName": "field", "granularity": "..."}]
}
```

**Figure (chart) definition**:
```json
{
  "id": "uuid",
  "x": 0, "y": 0, "width": 400, "height": 300,
  "tag": "chart",
  "data": {
    "type": "scorecard|odoo_bar|odoo_line|odoo_pie",
    "title": {"text": "Title", "bold": true},
    "keyValue": "Sheet!A1",
    "baseline": "Sheet!A2",
    "baselineDescr": "vs last month"
  }
}
```

### 6.4 Sample fallback

A separate `..._sample_dashboard.json` (same shape) is rendered when all `main_data_model_ids` are empty in the user's company.

## 7. File Reference Summary

| Path | Purpose |
|---|---|
| `addons/spreadsheet/__manifest__.py` | Core module, asset bundles |
| `addons/spreadsheet/models/spreadsheet_mixin.py` | Binary↔JSON, validation |
| `addons/spreadsheet/static/src/pivot/` | Pivot plugin, formulas, runtime |
| `addons/spreadsheet/static/src/chart/` | Chart plugin |
| `addons/spreadsheet/static/src/list/` | List data source |
| `addons/spreadsheet/static/src/data_sources/` | RPC, batching, caching |
| `addons/spreadsheet_dashboard/__manifest__.py` | Base dashboard module |
| `addons/spreadsheet_dashboard/models/spreadsheet_dashboard.py` | Dashboard model + sample loading |
| `addons/spreadsheet_dashboard/models/spreadsheet_dashboard_group.py` | Group/categorization |
| `addons/spreadsheet_dashboard/models/spreadsheet_dashboard_share.py` | Public sharing |
| `addons/spreadsheet_dashboard/security/security.xml` | Access control |
| `addons/spreadsheet_dashboard/data/dashboard.xml` | Pre-built groups |
| `addons/spreadsheet_dashboard/static/src/bundle/dashboard_action/` | OWL dashboard UI |
| `addons/spreadsheet_dashboard_sale/...` | Reference example: full dashboard module |
| `enterprise/spreadsheet_edition/__manifest__.py` | Edition bundle (enterprise) |
| `enterprise/spreadsheet_edition/static/src/bundle/pivot/pivot_init_callback.js` | Pivot insertion handler |
| `enterprise/spreadsheet_edition/static/src/assets/pivot_view/pivot_view.js` | "Insert in Spreadsheet" button |
| `enterprise/spreadsheet_dashboard_edition/__manifest__.py` | Dashboard editing (enterprise) |
| `enterprise/spreadsheet_dashboard_edition/models/ir_http.py` | session_info `can_insert_in_spreadsheet` |
