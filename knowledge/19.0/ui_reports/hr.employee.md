# UI Report: hr.employee

## Model Summary
- **Model:** `hr.employee`
- **Description:** Employee
- **Odoo Version:** 19.0
- **Source:** `odoo/addons/hr/models/hr_employee.py`
- **Inherits:** `mail.thread.main.attachment`, `mail.activity.mixin`, `resource.mixin`, `avatar.mixin`
- **_inherits:** `{'hr.version': 'version_id'}` -- many fields are delegated to `hr.version`
- **_rec_name:** `name` (default, from resource.mixin)
- **_order:** `name`

## Key Fields for CSV Loading

### Core Employee Fields (on hr.employee directly)
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | Char | Yes (in view) | Employee name, stored on resource_id |
| `company_id` | Many2one → res.company | Yes | Required, defaults to current company |
| `user_id` | Many2one → res.users | No | Linked user account; unique per company |
| `work_email` | Char | No | Computed from user, can be set manually |
| `work_phone` | Char | No | Work phone |
| `mobile_phone` | Char | No | Work mobile |
| `parent_id` | Many2one → hr.employee | No | Manager |
| `coach_id` | Many2one → hr.employee | No | Coach, computed from department manager |
| `category_ids` | Many2many → hr.employee.category | No | Tags |
| `barcode` | Char | No | Badge ID, must be unique |
| `pin` | Char | No | PIN for POS/Attendance kiosk |
| `color` | Integer | No | Color index, default 0 |
| `image_1920` | Binary | No | Employee photo |
| `active` | Boolean | No | Default True |

### Delegated Fields (from hr.version via _inherits)
| Field | Type | Required | Notes |
|---|---|---|---|
| `department_id` | Many2one → hr.department | No | Stored on hr.version |
| `job_id` | Many2one → hr.job | No | Job position |
| `job_title` | Char | No | Computed from job_id.name, can be overridden |
| `employee_type` | Selection | Yes | Default 'employee'. Options: employee, worker, student, trainee, contractor, freelance |
| `address_id` | Many2one → res.partner | No | Work address, defaults to company partner |
| `work_location_id` | Many2one → hr.work.location | No | Work location |
| `resource_calendar_id` | Many2one → resource.calendar | No | Working hours schedule |
| `sex` | Selection | No | male/female/other (legal gender) |
| `marital` | Selection | No | Default 'single'. Options: single, married, cohabitant, widower, divorced |
| `country_id` | Many2one → res.country | No | Nationality |
| `birthday` | Date | No | On hr.employee directly |
| `contract_date_start` | Date | No | Contract start date (groups: hr.group_hr_manager) |
| `contract_date_end` | Date | No | Contract end date (groups: hr.group_hr_manager) |
| `identification_id` | Char | No | National ID number |
| `departure_reason_id` | Many2one → hr.departure.reason | No | Set when archiving |
| `departure_date` | Date | No | Date of departure |

### Private Info Fields
| Field | Type | Notes |
|---|---|---|
| `private_email` | Char | Personal email |
| `private_phone` | Char | Personal phone |
| `private_street` | Char | Home address |
| `private_city` | Char | Home city |
| `private_zip` | Char | Home ZIP |
| `private_country_id` | Many2one → res.country | Home country |
| `private_state_id` | Many2one → res.country.state | Home state |
| `emergency_contact` | Char | Emergency contact name |
| `emergency_phone` | Char | Emergency phone |

### Planning-related Fields (from planning module)
| Field | Type | Notes |
|---|---|---|
| `default_planning_role_id` | Many2one → planning.role | Default role for planning shifts |
| `planning_role_ids` | Many2many → planning.role | All roles this employee can fill |

## SQL Constraints
- **`_barcode_uniq`**: `unique(barcode)` -- Badge ID must be unique globally.
- **`_user_uniq`**: `unique(user_id, company_id)` -- One employee per user per company.

## create() Override (Complex)
- Groups creation by company_id for correct context.
- If `user_id` is set, syncs name, image, email from the user.
- Auto-creates a `work_contact_id` (res.partner) if not provided.
- Auto-generates SVG avatar if no image provided.
- Subscribes to department channels.
- Logs onboarding plan suggestion.

## write() Override (Complex)
- Syncs user data when `user_id` changes.
- Updates timezone on linked res.users.
- Subscribes to department channels when department changes.
- Delegates version fields to `hr.version.write()`.

## Demo Data Patterns (Odoo 19.0)
```
name: (auto from user_admin)
  department_id: Management, job_id: Chief Technical Officer
  parent_id: (self), sex: male
  work_location_id: Building 1 Second Floor, resource_calendar_id: Standard 38h

name: Jeffrey Kelly
  department_id: Sales, job_id: Marketing and Community Manager
  parent_id: (admin employee), sex: male

name: Marc Demo
  user_id: base.user_demo, department_id: Research & Development
  job_id: Experienced Developer, parent_id: (admin)
  sex: male, distance_home_work: 23

name: Ronnie Hart
  department_id: Research & Development, job_id: Chief Technical Officer
  parent_id: Marc Demo
```
- All demo employees have `category_ids` tags set.
- Most have `work_location_id`, `resource_calendar_id`.
- Private address fields are set for some employees.

## Identity Key Recommendation
- **`name`** -- employee names are unique in practice within a company. The `_user_uniq` constraint enforces one-per-user-per-company but name is the practical lookup key.

## CSV Loading Notes
- The `_inherits` delegation to `hr.version` means fields like `department_id`, `job_id`, `employee_type`, `sex`, `marital` can be set directly on the employee CSV -- the ORM handles creating the version record.
- Load `hr.department` and `hr.job` BEFORE `hr.employee`.
- `parent_id` (manager) references other employees by name -- may need a second pass or careful ordering.
- `user_id` triggers heavy side-effects (name sync, image sync); only set if the employee should be linked to a system user.
- `pin` and `barcode` are useful for POS/Attendance demos.
- `default_planning_role_id` and `planning_role_ids` require the planning module installed.
- Do NOT set `work_contact_id` -- it is auto-created by `create()`.
