---
name: odoo-orm
description: ORM traversal skill. Answers questions about Odoo model structure, fields, methods, and inheritance by reading source code.
---

You have been invoked as the Odoo ORM expert. Use the methodology below to answer the user's question.

## Source locations (check in order)

1. `odoo-workspace/<version>/odoo/addons/<module>/models/`
2. `odoo-workspace/<version>/enterprise/<module>/models/`
3. GitHub raw URL: `https://raw.githubusercontent.com/odoo/odoo/<version>/addons/<module>/models/<file>.py`

## Investigation steps

### 1. Find the model definition
```
grep -r "_name = '<model.name>'" odoo-workspace/<version>/odoo/addons/
```

### 2. Trace inheritance
```
grep -r "_inherit = '<model.name>'" odoo-workspace/<version>/odoo/addons/
grep -r "_inherit = '<model.name>'" odoo-workspace/<version>/enterprise/
```

### 3. List fields
Read the model file and enumerate all `fields.*` declarations.
Note: `related=` fields read from another model; `compute=` fields may or may not be stored.

### 4. Trace a method
Find the method definition. Check decorators:
- `@api.depends(...)` — recomputed when these fields change
- `@api.onchange(...)` — fires in UI only
- `@api.constrains(...)` — fires on create/write, raises ValidationError
- `@api.model_create_multi` — wraps `create()`, receives list of dicts

### 5. Check views
```
grep -r "model=\"<model.name>\"" odoo-workspace/<version>/odoo/addons/<module>/views/
```

## Output format

Provide:
- **Model:** `<model.name>` — defined in `<module>/models/<file>.py`
- **Inherits:** list of parent models
- **Fields:** table of name / type / notes
- **Key methods:** signatures and decorators
- **SQL constraints:** if any
- **Source reference:** file path + approximate line number
