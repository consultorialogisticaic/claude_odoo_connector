# UI Report: hr.job

## Model Summary
- **Model:** `hr.job`
- **Description:** Job Position
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/hr/models/hr_job.py`
- **Inherits:** `mail.thread`
- **_rec_name:** `name` (default)
- **_order:** `sequence`

## Key Fields for CSV Loading

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes | Job Position name, translatable, trigram-indexed |
| `department_id` | Many2one → hr.department | No | FK lookup by department name |
| `company_id` | Many2one → res.company | No | Defaults to current company |
| `contract_type_id` | Many2one → hr.contract.type | No | Employment type (Permanent, Interim, etc.) |
| `sequence` | Integer | No | Default 10 |
| `no_of_recruitment` | Integer | No | Target new hires, default 1 |
| `description` | Html | No | Job description |
| `requirements` | Text | No | Job requirements (groups: hr.group_hr_user) |
| `active` | Boolean | No | Default True |

## SQL Constraints
- **`_name_company_uniq`**: `unique(name, company_id, department_id)` -- job name must be unique per department per company.
- **`_no_of_recruitment_positive`**: `CHECK(no_of_recruitment >= 0)`.

## create() Override
- Calls `super().create()` with `mail_create_nosubscribe=True` context.

## write() Override
- Handles `description` history divergence (collaborative editing).

## Demo Data Patterns (Odoo 19.0)
```
name: Chief Technical Officer, department_id: Research & Development, contract_type_id: Permanent
name: Consultant, department_id: Professional Services, contract_type_id: Interim, no_of_recruitment: 5
name: Experienced Developer, department_id: Research & Development, contract_type_id: Permanent, no_of_recruitment: 5
name: Human Resources Manager, department_id: Administration, contract_type_id: Permanent
name: Marketing and Community Manager, department_id: Sales
name: Trainee (no department set)
```

## Identity Key Recommendation
- **`name`** -- unique per company+department by SQL constraint. Since the loader typically operates within a single company, `name` alone is sufficient for dedup.

## CSV Loading Notes
- `department_id` resolves by `complete_name` (hr.department._rec_name).
- `contract_type_id` resolves by name (e.g., "Permanent", "Interim").
- Set `no_of_recruitment` to 0 if you don't want recruitment targets shown.
- The `company_id` can be set to False to make a job visible to all companies.
