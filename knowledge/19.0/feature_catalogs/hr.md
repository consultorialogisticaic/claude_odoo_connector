# Feature Catalog: hr (Employees)

- **Technical name:** hr
- **Version:** 19.0
- **Category:** Human Resources/Employees
- **Application:** Yes
- **License:** LGPL-3 (Community)
- **Depends:** base_setup, digest, phone_validation, resource_mail, web
- **Summary:** Centralize employee information

---

## 1. Menus (Backend)

| Menu path | Action / Model | Notes |
|---|---|---|
| Employees (top-level) | — | Root menu; sequence 185 |
| Employees > Employees | `open_view_employee_list_my` — `hr.employee` | HR Officers only (`group_hr_user`); full employee records |
| Employees > Directory | `hr_employee_public_action` — `hr.employee.public` | All internal users; public (limited) employee view |
| Employees > Departments | `hr_department_kanban_action` — `hr.department` | Kanban view of departments with employee counts |
| Employees > Reporting | — | Container for HR reports; HR Officers only |
| Employees > Configuration | — | Container; HR Administrators only |
| Employees > Configuration > Settings | `hr_config_settings_action` — `res.config.settings` | System admins only |
| Employees > Configuration > Employee > Onboarding / Offboarding | `mail_activity_plan_action` — `mail.activity.plan` | Activity plan templates |
| Employees > Configuration > Employee > Work Locations | `hr_work_location_action` — `hr.work.location` | Home, Office, Other |
| Employees > Configuration > Employee > Working Schedules | `resource.action_resource_calendar_form` — `resource.calendar` | Company working hours |
| Employees > Configuration > Employee > Departure Reasons | `hr_departure_reason_action` — `hr.departure.reason` | Fired, Resigned, Retired + custom |
| Employees > Configuration > Employee > Tags | `open_view_categ_form` — `hr.employee.category` | Debug mode only |
| Employees > Configuration > Recruitment > Job Positions | `action_hr_job` — `hr.job` | Job positions with recruitment targets |
| Employees > Configuration > Recruitment > Contract Templates | `action_hr_contract_templates` — `hr.contract.template` | HR Administrators only |
| Employees > Configuration > Recruitment > Contract Types | `hr_contract_type_action` — `hr.contract.type` | Hidden by default (active=0) |

---

## 2. Settings / Feature Flags

Settings in Employees > Configuration > Settings:

| Setting | Technical field | Default | Description |
|---|---|---|---|
| Attendance (Presence Display) | `module_hr_attendance` (related `company_id.hr_presence_control_attendance`) | False | Install `hr_attendance` for attendance tracking |
| Login-based Presence | `hr_presence_control_login` (related `company_id.hr_presence_control_login`) | False | Show presence based on Odoo login |
| Advanced Presence Control | `module_hr_presence` | False | Install `hr_presence` for email/IP-based detection |
| Email-based Presence | `hr_presence_control_email` (related) | False | Requires `module_hr_presence`; track presence by sent emails |
| IP-based Presence | `hr_presence_control_ip` (related) | False | Requires `module_hr_presence`; track presence by IP address |
| Sent Emails Threshold | `hr_presence_control_email_amount` (related) | — | Min emails to mark as present |
| IP Addresses | `hr_presence_control_ip_list` (related) | — | Comma-separated allowed IPs |
| Skills Management | `module_hr_skills` | False | Install `hr_skills` for employee skills/resumes |
| Company Working Hours | `resource_calendar_id` (related `company_id.resource_calendar_id`) | Standard 40h | Default schedule for employees |
| Contract Expiration Notice Period | `contract_expiration_notice_period` (related) | — | Days before contract end to trigger warning |
| Work Permit Expiration Notice Period | `work_permit_expiration_notice_period` (related) | — | Days before work permit expiry to trigger warning |

---

## 3. Key Models

### 3.1 hr.employee

The core employee model. Inherits `mail.thread`, `mail.activity.mixin`, `resource.mixin`, `avatar.mixin`. Uses `_inherits = {'hr.version': 'version_id'}` for contract versioning.

**Identity & Organization:**

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Employee name (stored, related to `resource_id.name`) |
| `user_id` | Many2one(`res.users`) | Linked user account |
| `company_id` | Many2one(`res.company`) | Required |
| `department_id` | Many2one(`hr.department`) | Department assignment |
| `job_id` | Many2one(`hr.job`) | Job position |
| `job_title` | Char | Free-text job title |
| `parent_id` | Many2one(`hr.employee`) | Manager (coach) |
| `coach_id` | Many2one(`hr.employee`) | Coach |
| `work_location_id` | Many2one(`hr.work.location`) | Work location |
| `work_email` | Char | Computed from user |
| `work_phone` | Char | Work phone |
| `mobile_phone` | Char | Work mobile |
| `category_ids` | Many2many(`hr.employee.category`) | Employee tags |
| `active` | Boolean | Archive support |

**Private Information (HR Officers only):**

| Field | Type | Notes |
|---|---|---|
| `private_phone` | Char | Personal phone |
| `private_email` | Char | Personal email |
| `birthday` | Date | Date of birth |
| `place_of_birth` | Char | Birthplace |
| `country_of_birth` | Many2one(`res.country`) | Country of birth |
| `sex` | Selection | Gender |
| `certificate` | Selection | Education level |
| `study_field` | Char | Field of study |
| `study_school` | Char | School name |
| `emergency_contact` | Char | Emergency contact name |
| `emergency_phone` | Char | Emergency contact phone |
| `permit_no` | Char | Work permit number |
| `visa_no` | Char | Visa number |
| `visa_expire` | Date | Visa expiration |
| `work_permit_expiration_date` | Date | Work permit expiration |
| `bank_account_ids` | Many2many(`res.partner.bank`) | Salary bank accounts |
| `private_street` / `private_city` / `private_zip` / `private_country_id` / `private_state_id` | Various | Private address fields |

**Contract / Version (via `_inherits hr.version`):**

| Field | Type | Notes |
|---|---|---|
| `contract_date_start` | Date | Contract start (HR Administrators) |
| `contract_date_end` | Date | Contract end (HR Administrators) |
| `trial_date_end` | Date | Trial period end |
| `structure_type_id` | Many2one(`hr.payroll.structure.type`) | Salary structure type |
| `wage` | Monetary | Salary |
| `contract_type_id` | Many2one(`hr.contract.type`) | Employment type |
| `resource_calendar_id` | Many2one(`resource.calendar`) | Working schedule |

**Presence:**

| Field | Type | Notes |
|---|---|---|
| `hr_presence_state` | Selection | present / absent / archive / out_of_working_hour |
| `hr_icon_display` | Selection | Icon to show in directory |
| `last_activity` | Date (computed) | Last login activity date |
| `newly_hired` | Boolean (computed) | Within first 3 months |

### 3.2 hr.employee.public

Read-only public view of employees. Accessible to all internal users. Exposes only non-sensitive fields (name, department, job, photo, work contact info). No private information.

### 3.3 hr.department

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, translatable |
| `complete_name` | Char (computed) | Full hierarchy path |
| `parent_id` | Many2one(`hr.department`) | Parent department |
| `child_ids` | One2many | Child departments |
| `manager_id` | Many2one(`hr.employee`) | Department manager |
| `member_ids` | One2many(`hr.employee`) | Department members |
| `total_employee` | Integer (computed) | Employee count |
| `jobs_ids` | One2many(`hr.job`) | Job positions in department |
| `company_id` | Many2one(`res.company`) | Company |
| `color` | Integer | Kanban card color |

### 3.4 hr.job

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, translatable; unique per (company, department) |
| `department_id` | Many2one(`hr.department`) | Department |
| `company_id` | Many2one(`res.company`) | Company |
| `contract_type_id` | Many2one(`hr.contract.type`) | Employment type |
| `no_of_employee` | Integer (computed) | Current employee count |
| `no_of_recruitment` | Integer | Recruitment target (default: 1) |
| `expected_employees` | Integer (computed) | Current + target |
| `description` | Html | Job description |
| `requirements` | Text | Job requirements |
| `user_id` | Many2one(`res.users`) | Recruiter |
| `employee_ids` | One2many(`hr.employee`) | Employees in this position |

### 3.5 hr.work.location

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required (e.g., "Head Office", "Store Norte") |
| `company_id` | Many2one(`res.company`) | Required |
| `location_type` | Selection | `home`, `office`, or `other` |
| `address_id` | Many2one(`res.partner`) | Physical work address |
| `location_number` | Char | Location identifier |

### 3.6 hr.employee.category

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Tag name; unique |
| `color` | Integer | Color index |
| `employee_ids` | Many2many(`hr.employee`) | Tagged employees |

### 3.7 hr.departure.reason

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, translatable |
| `sequence` | Integer | Ordering |
| `country_id` | Many2one(`res.country`) | Country-specific reasons |

Default reasons: Fired, Resigned, Retired (cannot be deleted).

### 3.8 hr.contract.type

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Required, translatable |
| `code` | Char | Auto-computed from name |
| `sequence` | Integer | Ordering |
| `country_id` | Many2one(`res.country`) | Country filter |

Pre-seeded: Permanent, Temporary, Interim, Seasonal, Full-Time, Part-Time, Intern, Student, Apprenticeship, Thesis, Statutory, Employee.

### 3.9 hr.version

Contract version model. Manages employee contract history with date-based versioning. Key fields include `date_version`, `contract_date_start`, `contract_date_end`, `wage`, `structure_type_id`, `resource_calendar_id`. Employees inherit current version fields via `_inherits`.

### 3.10 hr.payroll.structure.type

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Structure type name |
| `default_resource_calendar_id` | Many2one(`resource.calendar`) | Default working hours |
| `country_id` | Many2one(`res.country`) | Country-specific |

Pre-seeded: Employee, Worker, CP200 PFI BE, CP200 BE.

---

## 4. Reports

| Report | Model | Notes |
|---|---|---|
| Print Badge | `hr.employee` | QWeb PDF badge with company logo, employee photo, name, job title, department. Uses custom paper format. Binding action on employee form. |
| Manager Department Report | `hr.manager.department.report` | Abstract model for department-manager access filtering; used by other HR modules for reporting |

---

## 5. Wizards

| Wizard | Model | Purpose |
|---|---|---|
| Departure Wizard | `hr.departure.wizard` | Register employee departure: set reason, end date, optionally archive user. Supports bulk departure. |
| Contract Template Wizard | `hr.contract.template.wizard` | Apply contract template to employee |
| Bank Account Allocation | `hr.bank.account.allocation.wizard` + `hr.bank.account.allocation.wizard.line` | Assign bank accounts to employees for salary distribution |
| Schedule Activity | `mail.activity.schedule` (extended) | Schedule onboarding/offboarding activities from activity plans |

---

## 6. Security

### Groups

| Group | XML ID | Notes |
|---|---|---|
| Officer | `hr.group_hr_user` | Manage all employees; implies `base.group_user` |
| Administrator | `hr.group_hr_manager` | Full HR config + reports; implies `group_hr_user` |

### Key Rules

- Multi-company rules on `hr.employee`, `hr.department`, `hr.job`, `hr.version`
- Employee bank accounts hidden from non-HR users
- Departure reasons filtered by company country
- Activity plans restricted to HR managers

---

## 7. Demo Data

The `hr_demo.xml` file provides:

**Departments (7):**
- Management (root), Administration, Sales, Research & Development, R&D USA, Long Term Projects, Professional Services

**Job Positions (6):**
- Chief Technical Officer, Consultant, Experienced Developer, Human Resources Manager, Marketing and Community Manager, Trainee

**Work Location:**
- Building 1, Second Floor (office type)

**Employee Tags (6):**
- Sales, Trainer, Employee, Consultant, Standard 20 hours/week, High Potential

**Resource Calendar:**
- Standard 20 hours/week (Mon-Fri 8:00-12:00)

**Employees:**
- Admin employee with full profile (department, job, address, schedule, etc.)
- Multiple demo employees (Jeffrey Kelly + others) with work contacts, departments, tags

**Work Locations (data, non-demo):**
- Home, Office, Other (with default company address)

---

## 8. Cron Jobs

| Cron | Interval | Purpose |
|---|---|---|
| Notify Expiring Contract or Work Permit | Daily | Sends notifications when contracts/permits approach expiration |
| Update Current Version | Daily | Recalculates the active contract version for all employees |

---

## 9. Companion Modules

### Community (depend on `hr`)

| Module | Technical name | Purpose |
|---|---|---|
| Attendances | `hr_attendance` | Clock in/out tracking |
| Time Off | `hr_holidays` | Leave management |
| Expenses | `hr_expense` | Employee expense reporting |
| Skills | `hr_skills` | Skills, resumes, courses |
| Recruitment | `hr_recruitment` | Job applications and hiring pipeline |
| Fleet | `hr_fleet` | Company vehicle assignment |
| Maintenance | `hr_maintenance` | Equipment assignment to employees |
| Org Chart | `hr_org_chart` | Organization chart widget |
| Homeworking | `hr_homeworking` | Remote work scheduling |
| Hourly Cost | `hr_hourly_cost` | Employee cost rates |
| Timesheet | `hr_timesheet` | Time tracking on projects |
| Work Entry | `hr_work_entry` | Work entry management (base for payroll) |
| POS HR | `pos_hr` | Employee login for POS (cashier management) |
| Presence | `hr_presence` | Advanced presence detection (email/IP) |
| Gamification | `hr_gamification` | Badges and challenges |

### Enterprise (depend on `hr`)

| Module | Technical name | Purpose |
|---|---|---|
| Planning | `planning` | Shift scheduling and resource planning |
| Gantt | `hr_gantt` | Gantt view for HR |
| Documents HR | `documents_hr` | HR document management |
| Sign HR | `hr_sign` | Digital signature for HR documents |
| Appointment HR | `appointment_hr` | Employee appointment scheduling |
| HR Mobile | `hr_mobile` | Mobile app enhancements |

---

## 10. Percimon Relevance

For Percimon (Colombian frozen yogurt chain), the `hr` module provides the foundational employee base needed for:

- **POS employee discounts:** `pos_hr` depends on `hr` to identify employees at the POS terminal; employee records are required for cashier login and discount authorization
- **Planning shifts:** The `planning` module (enterprise) depends on `hr` for shift scheduling across Percimon's stores — requires employees assigned to departments/work locations
- **Maintenance assignments:** `hr_maintenance` links equipment (frozen yogurt machines, refrigerators) to responsible employees
- **Multi-store organization:** Departments map to store locations (e.g., "Tienda Norte", "Tienda Centro", "Bodega Central"); work locations identify physical addresses

**Recommended data for Percimon:**

| Model | Example records |
|---|---|
| `hr.department` | Administracion, Operaciones, Bodega, Tienda Norte, Tienda Centro, Tienda Sur |
| `hr.job` | Gerente de Tienda, Cajero, Preparador de Yogurt, Auxiliar de Bodega, Repartidor, Gerente General |
| `hr.work.location` | One per store + warehouse (office type, with address) |
| `hr.employee` | 10-15 employees across departments with job titles, work emails, PINs (for POS) |
| `hr.employee.category` | Tiempo Completo, Medio Tiempo, Fin de Semana |
| `hr.contract.type` | Use existing: Permanent, Part-Time, Seasonal (for peak season staff) |
