# Feature Catalog — Project (project)

**Version:** 19.0
**Source:** community
**Category:** Services/Project
**Dependencies:** analytic, base_setup, mail, portal, rating, resource, web, web_tour, digest

## Business Capabilities

- **Project and task lifecycle management:** Create projects with configurable task pipelines, assign tasks to one or many users, track progress through Kanban stages and task states (In Progress, Changes Requested, Approved, Done, Cancelled, Waiting on dependency).
- **Milestone and dependency planning:** Break projects down into milestones with deadlines, link tasks to milestones, and model task dependencies so blocked work is automatically flagged and waiting-state is computed.
- **Collaboration and project sharing:** Share projects with internal teammates as collaborators (Read / Edit limited / Edit) and with portal customers; the customer portal surfaces tasks, status updates, milestones, and ratings.
- **Recurring tasks and project templates:** Define recurring tasks (daily/weekly/monthly/yearly) and convert any project or task into a reusable template with role-to-user mapping for fast provisioning of new engagements.
- **Project status reporting and customer satisfaction:** Publish periodic Project Updates (On Track / At Risk / Off Track / On Hold / Complete) with progress percentage, and collect customer ratings at configurable stages to feed per-project and per-user analytics.

## Feature Inventory

### Menu Structure

| Menu Path | Feature | Description |
|---|---|---|
| Project > Projects | Projects | Kanban/list of all projects with favorites, open/closed task counts, and status color. Switches to a stage-grouped view when Project Stages feature is enabled |
| Project > Tasks > My Tasks | My Tasks | Personal task list filtered to the current user, with personal stages and calendar view |
| Project > Tasks > All Tasks | All Tasks | Cross-project task list/kanban/calendar/pivot/graph/activity/gantt views |
| Project > Reporting > Tasks Analysis | Tasks Analysis | Pivot/graph analysis of tasks: working hours/days to assign and close, ratings, counts, by project/stage/user (`report.project.task.user`) |
| Project > Reporting > Customer Ratings | Customer Ratings | Rating analysis on project tasks with per-project and per-agent breakdowns |
| Project > Configuration > Settings | Settings | Project app settings: Task Logs (Timesheets), Project Stages toggle |
| Project > Configuration > Projects | Projects (Config) | Manager-only project list for configuration, grouped by stage when stages are enabled |
| Project > Configuration > Project Stages | Project Stages | Manage the stage pipeline applied at the project (not task) level |
| Project > Configuration > Task Stages | Task Stages | Global task stage registry (developer mode) |
| Project > Configuration > Tags | Tags | Project/task classification tags with color |
| Project > Configuration > Project Roles | Project Roles | Named roles on tasks used for template role-to-user mapping when creating from template |
| Project > Configuration > Activity Types | Activity Types | Task activity types scoped to project tasks |
| Project > Configuration > Activity Plans | Activity Plans | Pre-defined activity plans that chain multiple follow-ups on tasks |

Sources: `odoo/addons/project/views/project_menus.xml`, `odoo/addons/project/views/project_project_views.xml`, `odoo/addons/project/views/project_task_views.xml`, `odoo/addons/project/report/project_report_views.xml`.

### Settings & Feature Flags

The Project app exposes a small central settings block; most feature toggles are per-project on the project form (they enable a group globally if any project uses them, so they behave like soft feature flags).

| Setting | Technical Field | What it Enables |
|---|---|---|
| Project Stages | `group_project_stages` (implies `project.group_project_stages`) | Enables a project-level stage pipeline on top of task stages; surfaces the Project Stages menu and stage-grouped project views |
| Task Logs (Timesheets) | `module_hr_timesheet` | Installs `hr_timesheet` to log time spent on projects and tasks |
| Task Dependencies | `allow_task_dependencies` (per project) | Adds a Blocked By relation on tasks and computes a Waiting state when upstream tasks are open |
| Milestones | `allow_milestones` (per project) | Adds the Milestones tab on projects, the milestone field on tasks, and milestone progress KPIs |
| Recurring Tasks | `allow_recurring_tasks` (per project) | Unlocks the Recurrence configuration on tasks (interval, unit, end rule) via `project.task.recurrence` |
| Visibility: Invited internal users | `privacy_visibility = 'followers'` | Project and its tasks are visible only to internal followers (assignees auto-follow) |
| Visibility: Invited internal and portal users | `privacy_visibility = 'invited_users'` | Same as above, extended to portal users |
| Visibility: All internal users | `privacy_visibility = 'employees'` | Full access for every internal user of the company |
| Visibility: All internal and invited portal users | `privacy_visibility = 'portal'` | Internal full access; portal customers can be invited as collaborators with configurable edit rights |
| Email Alias | `alias_id` / `alias_name` | Lets incoming emails create tasks in the project automatically (via `mail.alias.mixin`) |
| Customer Ratings on stage | `rating_active` / `rating_status` on `project.task.type` | Sends a rating request email when a task reaches the stage; schedules periodic requests via cron |
| Auto Kanban state on stage | `auto_validation_state` on `project.task.type` | Moves tasks from Changes Requested to Approved automatically on positive rating |

Sources: `odoo/addons/project/models/res_config_settings.py`, `odoo/addons/project/views/res_config_settings_views.xml`, `odoo/addons/project/models/project_project.py`, `odoo/addons/project/models/project_task_type.py`, `odoo/addons/project/security/project_security.xml`.

### Key Models

| Model | Type | Purpose | User-Facing? |
|---|---|---|---|
| `project.project` | Primary | Projects with manager, customer, analytic account, stage, collaborators, milestones, updates, visibility, alias, feature toggles | Yes |
| `project.task` | Primary | Tasks with title, assignees, priority (Low/Medium/High/Urgent), state machine, stage, parent/sub-tasks, dependencies, recurrence, milestone, deadline, allocated hours, rating, properties | Yes |
| `project.task.type` | Configuration | Task stages shared across projects with folding, mail template on enter, rating template/period, rotting threshold, auto kanban state | Yes |
| `project.project.stage` | Configuration | Project-level stages (To Do, In Progress, Done, Cancelled) with mail template on change | Yes (under Configuration when stages enabled) |
| `project.tags` | Configuration | Color-coded tags reusable across projects and tasks | Yes |
| `project.role` | Configuration | Named roles on tasks, used by the template wizard to map roles to users when creating from template | Yes |
| `project.milestone` | Transactional | Project milestones with deadline, reached flag, linked tasks, done/total counts, deadline-exceeded flag | Yes (embedded in project + own view) |
| `project.update` | Transactional | Periodic project status posts with status (On Track/At Risk/Off Track/On Hold/Complete), progress %, description, date, author | Yes |
| `project.collaborator` | Transactional | Per-partner portal sharing rows on a project with `limited_access` boolean; activates portal sharing ACL when first row is created | Yes (embedded in project share wizard) |
| `project.task.recurrence` | Transactional | Holds the recurrence definition (interval, unit, type, end date) for a chain of recurring tasks | Indirect (configured via task form) |
| `project.task.stage.personal` | Transactional | Per-user personal Kanban stage for a task (My Tasks view) | Yes (embedded in My Tasks) |
| `report.project.task.user` | Reporting | SQL view powering Tasks Analysis: creation/assign/end dates, working hours/days, rating, priority, state, stage, tags, milestone, dependencies | Yes (pivot/graph) |
| `project.task.burndown.chart.report` | Reporting | Burndown / burn-up line chart model grouping tasks by date and stage / is_closed | Yes (graph) |

Sources: `odoo/addons/project/models/project_project.py`, `odoo/addons/project/models/project_task.py`, `odoo/addons/project/models/project_task_type.py`, `odoo/addons/project/models/project_project_stage.py`, `odoo/addons/project/models/project_tags.py`, `odoo/addons/project/models/project_role.py`, `odoo/addons/project/models/project_milestone.py`, `odoo/addons/project/models/project_update.py`, `odoo/addons/project/models/project_collaborator.py`, `odoo/addons/project/models/project_task_recurrence.py`, `odoo/addons/project/models/project_task_stage_personal.py`, `odoo/addons/project/report/project_report.py`, `odoo/addons/project/report/project_task_burndown_chart_report.py`.

### Reports & Analytics

- **Tasks Analysis** (`report.project.task.user`): Pivot and graph view (custom JS classes `project_task_analysis_pivot` / `project_task_analysis_graph`) with measures for Working Hours/Days to Assign, Working Hours/Days to Close, Days to Deadline, Rating Last/Avg, and task count. Group by project, stage, assignee, milestone, tags, priority, state. Source: `odoo/addons/project/report/project_report_views.xml`.
- **Burndown Chart** (`project.task.burndown.chart.report`): Line graph (`burndown_chart` JS class) with filters for My Tasks, Unassigned, Open, Closed and default grouping by date (weekly) and stage; supports Burn-up view by grouping on `is_closed`. Source: `odoo/addons/project/report/project_task_burndown_chart_report_views.xml`.
- **Customer Ratings on Projects** (`rating.rating`): Dedicated report action `rating_rating_action_project_report` showing satisfaction results per project/assignee with comments. Source: `odoo/addons/project/views/rating_rating_views.xml`.
- **Project Updates status wall:** Kanban of `project.update` records per project, color-coded by status, with average progress and per-update task counts. Source: `odoo/addons/project/views/project_update_views.xml`.
- **Digest KPI:** `kpi_project_task_opened` on `digest.digest` — count of open tasks for the periodic digest email. Source: `odoo/addons/project/models/digest_digest.py`, `odoo/addons/project/data/digest_data.xml`.
- **Scheduled actions:** `ir_cron_rating_project` periodically sends stage-driven rating requests on tasks where the stage deadline has elapsed. Source: `odoo/addons/project/data/ir_cron_data.xml`.

### Wizards & Advanced Actions

| Wizard / Action | Model | Purpose |
|---|---|---|
| Share Project | `project.share.wizard` (inherits `portal.share`) | Build the collaborator list on a project, set per-partner access mode (Read / Edit limited / Edit), generate a portal share link, and sync followers vs collaborators |
| Share Project Collaborator row | `project.share.collaborator.wizard` | Line model for the share wizard: one row per invited partner with access mode and send-invitation flag |
| Share Task | `task.share.wizard` (inherits `portal.share`) | Share an individual task via portal link and subscribe the partner as follower |
| Portal Share (extended) | `portal.share` | Base portal share extended for projects; auto-subscribes shared partners as followers |
| Create from Template | `project.template.create.wizard` + `project.template.role.to.users.map` | Wizard opened when instantiating a project from a template: asks name, start/end dates, alias, and maps each role discovered on the template's tasks to concrete users |
| Delete Project Stage | `project.project.stage.delete.wizard` | Safely delete project stages by deciding whether to archive projects in them or move them to another stage; triggered by `unlink_project_stage_action` server action |
| Delete Task Stage | `project.task.type.delete.wizard` | Same safety dance for task stages shared across multiple projects; triggered by `unlink_task_type_action` server action |
| Convert to Sub-Task | `ir.actions.server` `action_server_convert_to_subtask` | Form-binding action on `project.task` to convert a task into (or out of) a sub-task of another |
| Convert Task to Template | `ir.actions.server` `action_server_convert_to_template` | Manager-only form action that flips `is_template` on a task so it can seed future tasks |
| Convert Project to Template | `ir.actions.server` `action_server_convert_project_to_template` | Manager-only form action that toggles template mode on a project, making it selectable in the Create-from-Template wizard |

Sources: `odoo/addons/project/wizard/*.py`, `odoo/addons/project/views/project_project_views.xml`, `odoo/addons/project/views/project_task_views.xml`, `odoo/addons/project/views/project_project_stage_views.xml`, `odoo/addons/project/views/project_task_type_views.xml`.

### Companion Modules

| Module | Source | Features Added |
|---|---|---|
| `sale_project` | community | Generates project tasks automatically from confirmed sales order lines (service products with a Task delivery policy) |
| `project_account` | community | Computes project profitability items from analytic account entries |
| `project_hr_expense` | community | Links employee expenses to projects and rolls them into profitability |
| `project_hr_skills` | community | Surfaces assignees' skills on tasks for skill-based allocation |
| `project_mail_plugin` | community | Creates tasks from emails through the Gmail/Outlook mail client plugins |
| `project_mrp` | community | Monitors manufacturing orders linked to a project on the project dashboard |
| `project_mrp_account` | community | Adds MRP cost analytics to project profitability |
| `project_mrp_sale` | community | Technical bridge between project, MRP, and sale flows |
| `project_mrp_stock_landed_costs` | community | Technical bridge for landed costs on MRP-driven projects |
| `project_purchase` | community | Monitors purchase orders and RFQs tied to a project |
| `project_purchase_stock` | community | Bridges purchase-stock flows into project profitability |
| `project_sale_expense` | community | Rebills employee expenses to customers through the attached sales order |
| `project_sms` | community | Sends SMS notifications when a project or task changes stage |
| `project_stock` | community | Links stock pickings (deliveries/receipts) to projects |
| `project_stock_account` | community | Handles analytic accounting on stock pickings linked to projects |
| `project_stock_landed_costs` | community | Technical bridge for landed costs on stock-driven projects |
| `project_timesheet_holidays` | community | Auto-generates timesheet lines covering approved time-off periods |
| `project_todo` | community | Personal To-Do app built on `project.task` with a private default project per user |
| `sale_project_stock` | community | Adds full inventory-operation traceability to the sale-project profitability report |
| `sale_project_stock_account` | community | Technical bridge for sale-project-stock analytics |
| `sale_purchase_project` | community | Technical bridge wiring sale -> purchase -> project flows |
| `website_project` | community | Publishes a public task submission form on the website |
| `data_merge_project` | enterprise | Adds a Merge action to the contextual menu of tasks and tags for duplicate cleanup |
| `documents_project` | enterprise | Attach/manage task documents through the Documents app with per-project workspaces (sub-catalog available) |
| `documents_project_sale` | enterprise | Product-driven folder templates when a sale order generates a project (sub-catalog available) |
| `documents_project_sign` | enterprise | Adds a Sign action on documents attached to tasks (sub-catalog available) |
| `esg_project` | enterprise | Creates ESG initiative projects to plan and measure sustainability impact |
| `project_account_asset` | enterprise | Links fixed-asset depreciation to project profitability |
| `project_account_budget` | enterprise | Tracks budgets per project with variance vs actuals |
| `project_enterprise` | enterprise | Bridge enabling the Gantt view, map view, and progress bars on tasks (sub-catalog available) |
| `project_enterprise_hr` | enterprise | Bridges project_enterprise with HR (employee availability in Gantt) |
| `project_enterprise_hr_skills` | enterprise | Surfaces employee skills in the enterprise task planner |
| `project_forecast` | enterprise | Plan resources on project tasks using the Planning app (sub-catalog available) |
| `project_helpdesk` | enterprise | Creates project tasks from helpdesk tickets |
| `project_holidays` | enterprise | Integrates task planning with approved time off so assignees on leave are flagged |
| `project_hr_payroll_account` | enterprise | Posts payroll analytics to project profitability |
| `project_mrp_workorder_account` | enterprise | Technical bridge routing workorder costs to the project |
| `project_sale_subscription` | enterprise | Tracks recurring subscription revenue on projects |
| `project_timesheet_forecast` | enterprise | Compares planned hours (Planning) with logged timesheets per project/task (sub-catalog available) |
| `project_timesheet_forecast_sale` | enterprise | Adds sales revenue to the timesheet-vs-forecast comparison (sub-catalog available) |
| `sale_project_forecast` | enterprise | Generates Planning shifts from sold project tasks (sub-catalog available) |
| `sale_renting_project` | enterprise | Technical bridge between rental orders and projects |
| `website_appointment_sale_project` | enterprise | Automatically stamps task dates from online appointment bookings |

Sources: `odoo/addons/<module>/__manifest__.py` and `enterprise/<module>/__manifest__.py` for each row.

## Demo Highlights

1. **Project templates with role-to-user mapping** — Turn any finished project into a template via Convert to Template, then re-instantiate it with the Create from Template wizard: the wizard detects every `project.role` used across the template's tasks and lets the PM map each role to a concrete employee on the new engagement. Great for productized services and standardized onboardings.

2. **Milestones + task dependencies + Waiting state** — On a project with `allow_milestones` and `allow_task_dependencies` enabled, tasks chain via Blocked By; downstream tasks automatically flip to the Waiting state and exit it the moment their upstream is closed. Combined with milestone deadlines and the milestone-exceeded flag, this visualizes blockers without manual status chasing.

3. **Burndown and Burn-up chart out of the box** — The Burndown Chart action ships with default weekly grouping by stage and a Burn-up toggle (group by `is_closed`), giving PMs an instantly-demoable sprint-style progress view with no setup.

4. **Project Updates with On Track / At Risk / Off Track status** — Project managers post periodic updates carrying progress %, description, and one of five statuses. The project card and portal surface the latest status with color, so customers and execs see health at a glance without opening a single task.

5. **Portal sharing with Edit / Edit limited / Read** — The Share Project wizard invites customers or external teammates as collaborators with three access grades. Combined with `privacy_visibility = 'portal'`, this turns the customer portal into a usable co-working surface — tasks, status updates, ratings, and attachments all honor the chosen access mode.

6. **Stage-driven customer ratings with auto-approval** — Enable `rating_active` on a task stage (e.g., "Delivered") and set a rating template; customers get a satisfaction survey automatically on entry, and `auto_validation_state` can flip the task from Changes Requested to Approved on a positive rating. Results flow into the Customer Ratings report.
