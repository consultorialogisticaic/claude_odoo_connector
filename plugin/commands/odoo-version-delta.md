---
name: odoo-version-delta
description: Version change tracking skill. Documents breaking changes, renamed fields/models, and new features between Odoo versions.
---

You have been invoked as the Odoo version delta expert. Use the methodology below.

## How to find version changes

### 1. Check the module HISTORY or CHANGELOG
```
cat odoo-workspace/<version>/odoo/addons/<module>/HISTORY
```

### 2. Check migration scripts
```
ls odoo-workspace/<version>/odoo/addons/<module>/migrations/
```
Each subdirectory is a version. Read `pre-migrate.py` and `post-migrate.py`.

### 3. Compare manifests
```
cat odoo-workspace/<from_version>/odoo/addons/<module>/__manifest__.py
cat odoo-workspace/<to_version>/odoo/addons/<module>/__manifest__.py
```

### 4. GitHub comparison (when repos not local)
URL pattern: `https://github.com/odoo/odoo/compare/<from>...<to> -- addons/<module>/`

### 5. OCA migration guides
Search: `https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md`
And: `site:github.com odoo migration <version>`

## Known breaking changes reference

See `subagents/technical_expert.md` § Skill 2 for the curated version delta knowledge base.

## Output format

Structure your answer as:

### Breaking changes (migration required)
| Change | From | To | Impact |
|---|---|---|---|
| Field renamed | `invoice_line_ids` | `line_ids` | All code referencing old name breaks |

### New features
- Feature name: brief description

### Deprecated (still works, will be removed)
- API / field name: replacement

### Migration steps
1. Step one
2. Step two
