# OPS Framework - Complete Model Registry

**Generated:** 2026-02-13
**Modules:** ops_matrix_core, ops_matrix_accounting, ops_kpi
**Odoo Version:** 19.0 Community Edition

---

## Table of Contents

1. [Summary Statistics](#summary-statistics)
2. [Module 1: ops_matrix_core](#module-1-ops_matrix_core)
   - [Core Structure Models](#core-structure-models)
   - [Security Engine Models](#security-engine-models)
   - [Persona & User Models](#persona--user-models)
   - [Governance & Approval Models](#governance--approval-models)
   - [SLA Engine Models](#sla-engine-models)
   - [Dashboard Models](#dashboard-models)
   - [Standard Model Extensions (Core)](#standard-model-extensions-core)
   - [Mixin / Abstract Models (Core)](#mixin--abstract-models-core)
3. [Module 2: ops_matrix_accounting](#module-2-ops_matrix_accounting)
   - [PDC & Budget Models](#pdc--budget-models)
   - [Asset Management Models](#asset-management-models)
   - [Fiscal Period Models](#fiscal-period-models)
   - [Recurring & Template Models](#recurring--template-models)
   - [Follow-up & Credit Models](#follow-up--credit-models)
   - [Inter-Branch & Reconciliation Models](#inter-branch--reconciliation-models)
   - [Lease Accounting Models](#lease-accounting-models)
   - [Reporting Models](#reporting-models)
   - [Consolidation / Analytics Models](#consolidation--analytics-models)
   - [Standard Model Extensions (Accounting)](#standard-model-extensions-accounting)
   - [Mixin / Abstract Models (Accounting)](#mixin--abstract-models-accounting)
4. [Module 3: ops_kpi](#module-3-ops_kpi)
5. [Inheritance Chain Map](#inheritance-chain-map)
6. [Cross-Module Relationship Map](#cross-module-relationship-map)

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total distinct _name models** | 95 |
| **Total _inherit extensions** | 33 |
| **ops_matrix_core models** | 53 (39 new _name + 14 _inherit) |
| **ops_matrix_accounting models** | 37 (22 new _name + 15 _inherit) |
| **ops_kpi models** | 6 (4 new _name + 2 _inherit) |
| **AbstractModel mixins** | 8 |
| **TransientModel wizards** | 8 |
| **SQL View models (_auto=False)** | 5 |
| **Models with mail.thread** | 30+ |
| **Models with ops.matrix.mixin** | 15+ |
| **Total Many2one relationships** | 200+ |
| **Total One2many relationships** | 60+ |
| **Total Many2many relationships** | 40+ |

---

## Module 1: ops_matrix_core

**Source:** `/opt/gemini_odoo19/addons/ops_matrix_core/models/`

### Core Structure Models

---

#### ops.branch
**File:** `ops_branch.py`
**Description:** Operational Branch
**Inherits:** `mail.thread`, `mail.activity.mixin`
**Order:** `sequence, name`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Branch name |
| code | Char | Yes | Yes | Unique code (e.g., BR-DOH) |
| company_id | Many2one(res.company) | Yes | No | Parent legal entity |
| business_unit_id | Many2one(ops.business.unit) | No | Yes | Parent BU |
| manager_id | Many2one(res.users) | No | Yes | Branch manager |
| active | Boolean | No | No | Default: True |
| sequence | Integer | No | No | Default: 10 |
| ops_analytic_account_id | Many2one(account.analytic.account) | No | Yes | Auto-generated analytic |
| member_ids | Many2many(res.users) | No | No | Branch members |

**Constraints:**
- `UNIQUE(code, company_id)` - Code unique per company
- `UNIQUE(name, company_id)` - Name unique per company

**Key Methods:**
- `_create_ops_analytic_account()` - Auto-creates analytic account on save
- `_compute_member_count()` - Counts branch members

**Relationships:**
- company_id -> res.company (Many2one)
- business_unit_id -> ops.business.unit (Many2one)
- manager_id -> res.users (Many2one)
- member_ids -> res.users (Many2many)

---

#### ops.business.unit
**File:** `ops_business_unit.py`
**Description:** Business Unit
**Inherits:** `mail.thread`, `mail.activity.mixin`
**Order:** `sequence, name`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | BU name |
| code | Char | Yes | Yes | Unique code |
| company_id | Many2one(res.company) | Yes | No | Parent company |
| manager_id | Many2one(res.users) | No | Yes | BU leader |
| branch_ids | One2many(ops.branch) | No | No | Branches in this BU |
| active | Boolean | No | No | Default: True |
| sequence | Integer | No | No | Default: 10 |
| ops_analytic_account_id | Many2one(account.analytic.account) | No | Yes | Auto-generated analytic |

**Constraints:**
- `UNIQUE(code, company_id)` - Code unique per company

**Key Methods:**
- `_create_ops_analytic_account()` - Auto-creates analytic account
- `_compute_branch_count()` - Counts branches

---

#### ops.matrix.config
**File:** `ops_matrix_config.py`
**Description:** OPS Matrix Configuration
**Type:** Singleton model (one record per company)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| company_id | Many2one(res.company) | Yes | One config per company |
| enable_branch_isolation | Boolean | No | Default: True |
| enable_bu_isolation | Boolean | No | Default: False |
| enforce_sod | Boolean | No | Default: True |
| default_approval_levels | Integer | No | Default: 2 |
| sla_working_hours_start | Float | No | Default: 8.0 |
| sla_working_hours_end | Float | No | Default: 17.0 |
| sla_working_days | Char | No | Default: '1,2,3,4,5' |

**Constraints:**
- `UNIQUE(company_id)` - One config per company

---

#### res.company (_inherit in ops_matrix_core)
**File:** `res_company.py`
**Description:** Extends res.company with OPS Matrix fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| ops_code | Char | Yes | Auto-generated (e.g., CP-0001). Readonly, unique |
| ops_manager_id | Many2one(res.users) | No | Country Manager |
| ops_analytic_account_id | Many2one(account.analytic.account) | No | Auto-generated analytic |
| branch_ids | One2many(ops.branch) | No | Operational branches |
| branch_count | Integer (computed) | No | Count of branches |
| enable_three_way_match | Boolean | No | Default: True |
| three_way_match_tolerance | Float | No | Default: 5.0% |
| three_way_match_block_validation | Boolean | No | Default: True |

**Constraints:**
- `UNIQUE(ops_code)` - OPS code globally unique

**Key Methods:**
- `create()` - Governance: Only group_system can create companies. Auto-generates ops_code and analytic account.
- `write()` - Auto-generates ops_code if still 'New', syncs analytic name on company rename
- `_generate_ops_code()` - Uses ir.sequence 'res.company.ops'
- `_create_ops_analytic_accounts()` - Auto-creates analytic account
- `_get_or_create_ops_analytic_plan()` - Gets/creates 'OPS Company' analytic plan

---

### Security Engine Models

---

#### ops.security.rule
**File:** `ops_security_rules.py`
**Description:** Dynamic Security Rule Engine

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Rule name |
| model_id | Many2one(ir.model) | Yes | Target model |
| group_id | Many2one(res.groups) | Yes | Security group |
| domain_filter | Char | Yes | Domain expression |
| active | Boolean | No | Default: True |
| rule_type | Selection | Yes | branch_isolation, bu_isolation, admin_override, it_blindness |

**Key Methods:**
- `_apply_rules()` - Applies dynamic record rules at runtime
- `_generate_ir_rules()` - Creates/updates ir.rule records

---

#### ops.security.audit
**File:** `ops_security_audit.py`
**Description:** Security Audit Log

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | Many2one(res.users) | Yes | User who triggered event |
| action | Selection | Yes | login, logout, access_denied, sudo_use, export, etc. |
| resource_model | Char | No | Affected model |
| resource_id | Integer | No | Affected record ID |
| ip_address | Char | No | Client IP |
| details | Text | No | JSON details |
| severity | Selection | No | info, warning, critical |
| timestamp | Datetime | Yes | Event time |

**Security:** Immutable - write/unlink blocked for non-admin.

---

#### ops.security.compliance
**File:** `ops_security_compliance.py`
**Description:** Security Compliance Dashboard
**Type:** SQL View (`_auto = False`)

| Field | Type | Notes |
|-------|------|-------|
| compliance_category | Char | Category of compliance check |
| check_name | Char | Name of compliance check |
| status | Selection | pass, warning, fail |
| details | Text | Check result details |

**Key Methods:**
- `init()` - Creates SQL view for compliance dashboard
- `_run_compliance_checks()` - Executes all compliance checks

---

#### ops.session.manager
**File:** `ops_session_manager.py`
**Description:** Session Management and Tracking

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | Many2one(res.users) | Yes | Session owner |
| session_id | Char | Yes | HTTP session identifier |
| login_date | Datetime | Yes | Login timestamp |
| last_activity | Datetime | No | Last activity time |
| ip_address | Char | No | Client IP |
| user_agent | Char | No | Browser user agent |
| is_active | Boolean | No | Currently active |

**Key Methods:**
- `cron_cleanup_sessions()` - Removes expired sessions
- `_force_logout()` - Force-terminate a session

---

#### ops.ip.whitelist
**File:** `ops_ip_whitelist.py`
**Description:** IP Address Whitelist

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Description |
| ip_address | Char | Yes | IP or CIDR |
| user_id | Many2one(res.users) | No | Specific user (null = all) |
| active | Boolean | No | Default: True |
| expiry_date | Date | No | Optional expiry |

---

#### ops.data.archival
**File:** `ops_data_archival.py`
**Description:** Data Archival for Scalability

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Policy name |
| model_id | Many2one(ir.model) | Yes | Target model |
| retention_days | Integer | Yes | Days before archival |
| archive_method | Selection | Yes | deactivate, delete |
| domain_filter | Char | No | Additional filter |
| last_run | Datetime | No | Last execution |

**Key Methods:**
- `cron_archive_data()` - Runs archival based on policies

---

#### ops.performance.monitor
**File:** `ops_performance_monitor.py`
**Description:** Performance Monitoring and Alerts

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Monitor name |
| metric_type | Selection | Yes | query_time, memory, cpu, record_count |
| threshold_warning | Float | No | Warning threshold |
| threshold_critical | Float | No | Critical threshold |
| current_value | Float (computed) | No | Current metric value |
| status | Selection (computed) | No | ok, warning, critical |

---

#### ops.api.key
**File:** `ops_api_key.py`
**Description:** API Key Management

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Key name/description |
| key_hash | Char | Yes | Hashed API key (never stored plaintext) |
| user_id | Many2one(res.users) | Yes | Key owner |
| scope | Selection | Yes | read, write, admin |
| expires_at | Datetime | No | Key expiry |
| active | Boolean | No | Default: True |
| last_used | Datetime | No | Last usage timestamp |

**Key Methods:**
- `generate_key()` - Creates new API key, returns plaintext once
- `validate_key()` - Validates key hash and checks expiry/scope

---

#### ops.audit.log
**File:** `ops_audit_log.py`
**Description:** API Audit Logging

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| api_key_id | Many2one(ops.api.key) | No | API key used |
| user_id | Many2one(res.users) | Yes | User |
| endpoint | Char | Yes | API endpoint called |
| method | Selection | Yes | GET, POST, PUT, DELETE |
| request_body | Text | No | Sanitized request |
| response_code | Integer | No | HTTP response code |
| ip_address | Char | No | Client IP |
| timestamp | Datetime | Yes | Request time |

---

#### ops.corporate.audit.log
**File:** `ops_corporate_audit_log.py`
**Description:** Corporate Audit Trail (SOX/ISO/GDPR)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| sequence_number | Char | Yes | Auto-generated sequential number |
| user_id | Many2one(res.users) | Yes | User who performed action |
| action_type | Selection | Yes | create, write, unlink, approve, reject, override, etc. |
| model_name | Char | Yes | Target model |
| record_id | Integer | No | Target record ID |
| record_name | Char | No | Display name at time of action |
| old_values | Text | No | JSON of old values |
| new_values | Text | No | JSON of new values |
| ip_address | Char | No | Client IP |
| company_id | Many2one(res.company) | Yes | Company context |
| timestamp | Datetime | Yes | Action timestamp |

**Security:** Immutable - write/unlink blocked for all non-admin users.

---

#### ir.exports (_inherit)
**File:** `ir_exports_override.py`
**Description:** Restricts native data export functionality

**Key Methods:**
- Overrides export to enforce OPS security checks before allowing data export.

---

#### ir.actions.report (_inherit)
**File:** `ir_actions_report.py`
**Description:** Governance enforcement on PDF generation

**Key Methods:**
- `_render_qweb_pdf()` override - Enforces governance checks before report generation
- Validates user has appropriate permissions for the report being generated

---

### Persona & User Models

---

#### ops.persona
**File:** `ops_persona.py`
**Description:** Role-Based Persona Definition
**Inherits:** `mail.thread`
**Order:** `sequence, name`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Persona name (e.g., "Chief Financial Officer") |
| code | Char | Yes | Yes | Unique code (e.g., CEO, CFO, SYS_ADMIN) |
| description | Text | No | No | Role description |
| sequence | Integer | No | No | Display order |
| active | Boolean | No | No | Default: True |
| persona_level | Selection | Yes | No | executive, director, manager, user, system |
| can_access_cost_prices | Boolean | No | No | Cost Shield authority |
| can_approve_orders | Boolean | No | No | Approval authority |
| can_create_users | Boolean | No | No | User creation authority |
| max_approval_amount | Float | No | No | Maximum approval amount |
| group_ids | Many2many(res.groups) | No | No | Mapped security groups |

**Constraints:**
- `UNIQUE(code)` - Persona code globally unique

**18 Standard Personas:** CEO, CFO, FIN_CTRL, SALES_LEADER, SALES_MGR, PURCHASE_MGR, LOG_MGR, TREASURY_OFF, HR_MGR, CHIEF_ACCT, SYS_ADMIN, SALES_REP, PURCHASE_OFF, LOG_CLERK, ACCOUNTANT, AR_CLERK, AP_CLERK, TECH_SUPPORT

---

#### ops.persona.delegation
**File:** `ops_persona_delegation.py`
**Description:** Persona Delegation (temporary authority transfer)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| delegator_id | Many2one(res.users) | Yes | User granting delegation |
| delegate_id | Many2one(res.users) | Yes | User receiving delegation |
| persona_id | Many2one(ops.persona) | Yes | Persona being delegated |
| date_from | Date | Yes | Start date |
| date_to | Date | Yes | End date |
| reason | Text | Yes | Delegation reason |
| state | Selection | Yes | draft, active, expired, revoked |

**Key Methods:**
- `action_activate()` - Activates delegation
- `action_revoke()` - Revokes delegation
- `cron_expire_delegations()` - Auto-expires past-due delegations

---

#### res.users (_inherit - main)
**File:** `res_users.py`
**Description:** Core user extensions for Matrix dimensions

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| persona_id | Many2one(ops.persona) | No | Primary persona |
| ops_persona_ids | Many2many(ops.persona) | No | All assigned personas |
| primary_branch_id | Many2one(ops.branch) | No | Home branch |
| ops_allowed_branch_ids | Many2many(ops.branch) | No | All accessible branches |
| ops_business_unit_id | Many2one(ops.business.unit) | No | Primary BU |
| is_matrix_administrator | Boolean | No | Matrix admin flag |
| is_cross_branch_bu_leader | Boolean | No | Cross-branch access |
| ops_color_mode | Selection | No | light, dark, system |

**Key Methods:**
- `_check_primary_branch()` - Validates primary branch is in allowed branches
- `has_ops_authority()` - Checks persona-based authority flags

---

#### res.users (_inherit - authority)
**File:** `res_users_authority.py`
**Description:** Authority checking methods

**Key Methods:**
- `has_ops_authority(authority_field)` - Checks if user's persona grants a specific authority
- `get_authority_level()` - Returns authority level based on persona_level

---

#### res.users (_inherit - SoD)
**File:** `res_users_sod.py`
**Description:** Segregation of Duties enforcement

**Key Methods:**
- `_check_sod_conflicts()` - Checks for SoD rule violations on group assignment
- `write()` override - Validates SoD before saving group changes

---

#### res.users (_inherit - group mapper)
**File:** `res_users_group_mapper.py`
**Description:** Persona-to-Group automatic mapping

**Key Methods:**
- `_onchange_persona_id()` - Auto-sync logic: adds persona to ops_persona_ids, auto-populates primary branch, maps security groups
- `_map_persona_to_groups()` - Maps 18 persona codes to appropriate Odoo security groups
- `_onchange_is_matrix_administrator()` - Syncs boolean with group membership
- `_onchange_is_cross_branch_bu_leader()` - Syncs boolean with group membership

---

#### res.users (_inherit - API)
**File:** `res_users_api.py`
**Description:** API authentication extensions

**Key Methods:**
- `api_authenticate()` - Validates API key and returns user context
- `_check_api_permissions()` - Checks scope-based permissions

---

### Governance & Approval Models

---

#### ops.governance.rule
**File:** `ops_governance_rule.py`
**Description:** Configurable Governance Rule
**Inherits:** `mail.thread`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Rule name |
| code | Char | Yes | Unique code |
| model_name | Selection | Yes | Target model (sale.order, purchase.order, account.move, etc.) |
| rule_type | Selection | Yes | amount_threshold, field_required, approval_required, state_transition, custom |
| active | Boolean | No | Visible in UI (catalog mode) |
| enabled | Boolean | No | Actually enforced (catalog mode) |
| threshold_amount | Float | No | Amount trigger |
| required_field | Char | No | Field that must have value |
| required_group_id | Many2one(res.groups) | No | Group required for action |
| company_id | Many2one(res.company) | Yes | Company scope |
| limit_ids | One2many(ops.governance.limit) | No | Amount limits by persona |
| branch_ids | Many2many(ops.branch) | No | Branch scope |

**Constraints:**
- `UNIQUE(code, company_id)` - Code unique per company

---

#### ops.governance.limit
**File:** `ops_governance_limits.py`
**Description:** Governance amount limits by persona/group

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| rule_id | Many2one(ops.governance.rule) | Yes | Parent rule |
| persona_id | Many2one(ops.persona) | No | Target persona |
| group_id | Many2one(res.groups) | No | Target group |
| min_amount | Float | No | Minimum amount trigger |
| max_amount | Float | No | Maximum amount cap |
| requires_approval | Boolean | No | Forces approval |
| approval_group_id | Many2one(res.groups) | No | Who must approve |

---

#### ops.governance.limit.line
**File:** `ops_governance_limits.py`
**Description:** Governance limit escalation line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| limit_id | Many2one(ops.governance.limit) | Yes | Parent limit |
| sequence | Integer | No | Escalation order |
| min_amount | Float | No | Min trigger |
| max_amount | Float | No | Max trigger |
| approver_group_id | Many2one(res.groups) | No | Approver group |

---

#### ops.approval.rule
**File:** `ops_approval_rule.py`
**Description:** Lightweight Approval Rule

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Rule name |
| model_name | Selection | Yes | Target model |
| min_amount | Float | No | Minimum amount trigger |
| approver_group_id | Many2one(res.groups) | Yes | Who can approve |
| sequence | Integer | No | Priority/order |
| active | Boolean | No | Default: True |
| company_id | Many2one(res.company) | Yes | Company scope |

---

#### ops.approval.request
**File:** `ops_approval_request.py`
**Description:** Approval Request Instance
**Inherits:** `mail.thread`, `mail.activity.mixin`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Auto-generated sequence |
| model_name | Char | Yes | Source model |
| record_id | Integer | Yes | Source record ID |
| record_ref | Reference | No | Polymorphic reference |
| requester_id | Many2one(res.users) | Yes | Who requested |
| approver_id | Many2one(res.users) | No | Who approved/rejected |
| state | Selection | Yes | pending, approved, rejected, recalled |
| amount | Float | No | Approval amount |
| notes | Text | No | Requester notes |
| response_notes | Text | No | Approver notes |
| rule_id | Many2one(ops.approval.rule) | No | Triggering rule |

**Key Methods:**
- `action_approve()` - Approves request, triggers callback on source record
- `action_reject()` - Rejects request with reason
- `action_recall()` - Requester recalls pending request

---

#### ops.approval.dashboard
**File:** `ops_approval_dashboard.py`
**Description:** Approval Dashboard
**Type:** SQL View (`_auto = False`)

| Field | Type | Notes |
|-------|------|-------|
| model_name | Char | Source model |
| state | Selection | Approval state |
| count | Integer | Number of requests |
| avg_days | Float | Average approval time |

---

#### ops.governance.violation.report
**File:** `ops_governance_violation_report.py`
**Description:** Governance Violation Report
**Type:** SQL View (`_auto = False`)

| Field | Type | Notes |
|-------|------|-------|
| rule_id | Many2one(ops.governance.rule) | Violated rule |
| model_name | Char | Model where violation occurred |
| violation_count | Integer | Count of violations |
| last_violation_date | Datetime | Most recent violation |

---

#### ops.archive.policy
**File:** `ops_archive_policy.py`
**Description:** Record Archival Policy

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Policy name |
| model_id | Many2one(ir.model) | Yes | Target model |
| days_before_archive | Integer | Yes | Retention period |
| archive_condition | Char | No | Additional domain |
| active | Boolean | No | Default: True |

---

#### ops.three.way.match
**File:** `ops_three_way_match.py`
**Description:** Three-Way Match Configuration/Log

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| invoice_id | Many2one(account.move) | Yes | Vendor bill |
| purchase_order_id | Many2one(purchase.order) | Yes | PO |
| picking_id | Many2one(stock.picking) | No | GRN |
| match_status | Selection | Yes | pending, matched, partial, unmatched, override |
| po_amount | Float | No | PO total |
| receipt_amount | Float | No | Receipt total |
| invoice_amount | Float | No | Invoice total |
| variance | Float (computed) | No | Amount variance |
| override_reason | Text | No | Override justification |
| override_user_id | Many2one(res.users) | No | Who overrode |

---

#### ops.segregation.of.duties
**File:** `ops_segregation_of_duties.py`
**Description:** SoD Rule Definition

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Rule name |
| model_name | Selection | Yes | Target model |
| action_1 | Selection | Yes | First conflicting action (create, confirm, approve, validate, cancel, post, reconcile) |
| action_2 | Selection | Yes | Second conflicting action |
| group_1_id | Many2one(res.groups) | No | Group for action 1 |
| group_2_id | Many2one(res.groups) | No | Group for action 2 |
| severity | Selection | Yes | warning, block |
| active | Boolean | No | Default: True |

**Key Methods:**
- `check_sod_violation()` - Checks if user violates this SoD rule for a given action

---

### SLA Engine Models

---

#### ops.sla.template
**File:** `ops_sla_template.py`
**Description:** SLA Template Definition

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Template name |
| code | Char | Yes | Unique code |
| model_name | Selection | Yes | Target model |
| trigger_field | Char | No | Field that triggers SLA start |
| trigger_value | Char | No | Value that triggers start |
| deadline_hours | Float | Yes | SLA deadline in business hours |
| escalation_hours | Float | No | Hours before escalation |
| escalation_user_id | Many2one(res.users) | No | Who to escalate to |
| active | Boolean | No | Default: True |
| company_id | Many2one(res.company) | Yes | Company scope |

---

#### ops.sla.instance
**File:** `ops_sla_instance.py`
**Description:** SLA Instance (active tracking)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | Many2one(ops.sla.template) | Yes | SLA template |
| model_name | Char | Yes | Source model |
| record_id | Integer | Yes | Source record ID |
| start_date | Datetime | Yes | SLA start time |
| deadline_date | Datetime (computed) | No | Calculated deadline (business hours aware) |
| completion_date | Datetime | No | When completed |
| state | Selection | Yes | active, met, breached, escalated |
| elapsed_hours | Float (computed) | No | Business hours elapsed |

**Key Methods:**
- `_compute_deadline()` - Calculates deadline using business hours from ops.matrix.config
- `cron_check_sla_breaches()` - Checks for breached SLAs, triggers escalation
- `action_complete()` - Marks SLA as met

---

### Dashboard Models

---

#### ops.dashboard.config
**File:** `ops_dashboard_config.py`
**Description:** Dashboard Configuration

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Dashboard name |
| code | Char | Yes | Unique code |
| dashboard_type | Selection | Yes | executive, branch, bu, sales, purchase, inventory |
| persona_ids | Many2many(ops.persona) | No | Target personas |
| widget_ids | One2many(ops.dashboard.widget) | No | Dashboard widgets |
| company_id | Many2one(res.company) | Yes | Company scope |
| active | Boolean | No | Default: True |

---

#### ops.dashboard.widget
**File:** `ops_dashboard_widget.py`
**Description:** Dashboard Widget Configuration

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| dashboard_id | Many2one(ops.dashboard.config) | Yes | Parent dashboard |
| name | Char | Yes | Widget title |
| widget_type | Selection | Yes | counter, chart, list, gauge, table |
| model_name | Char | No | Source model |
| measure_field | Char | No | Field to aggregate |
| domain_filter | Char | No | Domain expression |
| sequence | Integer | No | Display order |
| width | Integer | No | Grid width (1-12) |

---

### Standard Model Extensions (Core)

---

#### sale.order (_inherit)
**File:** `sale_order.py`
**Description:** Matrix dimensions, governance enforcement, customer verification

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_branch_id | Many2one(ops.branch) | From ops.matrix.mixin |
| ops_business_unit_id | Many2one(ops.business.unit) | From ops.matrix.mixin |
| can_edit_unit_price | Boolean (computed) | Price Protection flag |
| master_verification_status | Char (computed) | Customer MDM status |

**Key Methods:**
- `action_confirm()` override - Enforces: master data verification (HARD BLOCK), SoD check, governance rule check, SLA tracking start
- `_check_credit_firewall()` - Warning at confirmation, HARD BLOCK at delivery
- `_check_customer_verified()` - Validates ops_master_verified on partner

---

#### sale.order (_inherit - approval)
**File:** `sale_order_approval.py`
**Description:** Approval workflow for sale orders

**Key Methods:**
- `action_request_approval()` - Creates ops.approval.request
- `action_approve()` - Handles approval callback
- `_check_approval_required()` - Checks governance rules for amount thresholds

---

#### sale.order.line (_inherit)
**File:** `sale_order_line.py`
**Description:** Price protection, cost shield, margin calculations, branch activation
**Inherits:** `sale.order.line`, `ops.matrix.mixin`, `ops.field.visibility.mixin`

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| can_edit_unit_price | Boolean (computed) | Only Price Managers can edit |
| can_user_access_cost_prices | Boolean (computed) | Cost Shield |
| purchase_price | Float | Stored, groups restricted |
| margin | Float | Stored, groups restricted |
| margin_percent | Float | Stored, groups restricted |

**Key Methods:**
- `write()` override - PRICE PROTECTION: blocks price_unit changes for non-authorized users
- `_check_product_branch_activation()` - BRANCH ACTIVATION GOVERNANCE: verifies Global Master products are activated for the order's branch

---

#### purchase.order (_inherit)
**File:** `purchase_order.py`
**Description:** Matrix dimensions, SoD, governance on PO

**Key Methods:**
- `button_confirm()` override - SoD check, governance rule validation
- `button_approve()` override - Approval workflow integration

---

#### account.move (_inherit - core)
**File:** `account_move.py`
**Description:** Matrix dimensions on journal entries

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_branch_id | Many2one(ops.branch) | From ops.matrix.mixin |
| ops_business_unit_id | Many2one(ops.business.unit) | From ops.matrix.mixin |

**Key Methods:**
- `action_post()` override - Governance checks before posting

---

#### account.payment (_inherit)
**File:** `account_payment.py`
**Description:** Matrix dimensions on payments

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_branch_id | Many2one(ops.branch) | From ops.matrix.mixin |
| ops_business_unit_id | Many2one(ops.business.unit) | From ops.matrix.mixin |

---

#### stock.picking (_inherit)
**File:** `stock_picking.py`
**Description:** Matrix dimensions, credit firewall enforcement on delivery

**Key Methods:**
- `button_validate()` override - Credit Firewall HARD BLOCK at delivery for unverified customers
- Propagates branch/BU from source document

---

#### stock.move (_inherit)
**File:** `stock_move.py`
**Description:** Matrix dimensions on stock moves

**Added Fields:** ops_branch_id, ops_business_unit_id (from mixin)

---

#### stock.quant (_inherit)
**File:** `stock_quant.py`
**Description:** Matrix dimensions on stock quantities

**Added Fields:** ops_branch_id (derived from warehouse location)

---

#### stock.warehouse (_inherit)
**File:** `stock_warehouse.py`
**Description:** Branch linkage for warehouses

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_branch_id | Many2one(ops.branch) | Branch that owns the warehouse |

---

#### stock.warehouse.orderpoint (_inherit)
**File:** `stock_warehouse_orderpoint.py`
**Description:** Matrix dimensions on reorder rules

**Added Fields:** ops_branch_id (derived from warehouse)

---

#### res.partner (_inherit)
**File:** `partner.py`
**Description:** Master Data Governance, Customer Verification, Credit Control

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_cr_number | Char | Company Registration Number (unique when provided) |
| ops_master_verified | Boolean | Master Data Verification flag |
| ops_state | Selection | draft, approved, blocked, archived |
| ops_verification_date | Date | When verified |
| ops_verified_by_id | Many2one(res.users) | Who verified |
| ops_credit_limit | Monetary | OPS credit limit |
| ops_total_outstanding | Monetary (computed) | Total outstanding invoices |
| ops_confirmation_restrictions | Text (computed) | Active restrictions |
| ops_approval_notes | Text | Approval notes |
| company_currency_id | Many2one(res.currency) | Related from company |

**Constraints:**
- `UNIQUE(ops_cr_number)` - CR number unique (NULL allowed)

**Key Methods:**
- `can_confirm_orders()` - Returns (bool, reason) tuple for order confirmation eligibility
- `action_verify_master()` / `action_unverify_master()` - MDM verification toggle
- `action_approve()` / `action_block()` / `action_unblock()` / `action_reset_to_draft()` - State workflow
- `_notify_draft_customer_creation()` - Notifies approvers when customer created in draft

---

#### product.template (_inherit)
**File:** `product.py`
**Description:** Global Master and Branch Activation governance

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_is_global_master | Boolean | Global Master flag |
| ops_branch_activation_ids | Many2many(ops.branch) | Branches where product is activated |
| ops_business_unit_id | Many2one(ops.business.unit) | Product silo BU |
| ops_product_category | Selection | standard, service, consumable, asset |

---

#### product.product (_inherit)
**File:** `product.py`
**Description:** Branch activation on product variants

---

#### product.pricelist (_inherit)
**File:** `pricelist.py`
**Description:** Branch-scoped pricelists

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_branch_ids | Many2many(ops.branch) | Branches using this pricelist |

---

#### mail.message (_inherit)
**File:** `mail_message.py`
**Description:** Audit logging for messages

**Key Methods:**
- Adds branch context to message tracking

---

#### account.report (_inherit)
**File:** `account_report.py`
**Description:** Financial report extensions

**Key Methods:**
- Adds branch filtering capabilities to standard Odoo financial reports

---

#### ops.report.template
**File:** `ops_report_template.py`
**Description:** Report Template Configuration

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Template name |
| code | Char | Yes | Unique code |
| model_name | Char | No | Target model |
| report_type | Selection | Yes | pdf, xlsx, html |
| template_data | Text | No | Template configuration (JSON) |
| active | Boolean | No | Default: True |
| company_id | Many2one(res.company) | Yes | Company scope |

---

#### ops.report.template.line
**File:** `ops_report_template_line.py`
**Description:** Report Template Line Items

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | Many2one(ops.report.template) | Yes | Parent template |
| sequence | Integer | No | Display order |
| field_name | Char | Yes | Field to include |
| label | Char | No | Display label override |
| width | Integer | No | Column width |

---

#### ops.product.request
**File:** `ops_product_request.py`
**Description:** Product Request Workflow
**Inherits:** `mail.thread`, `mail.activity.mixin`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Auto-sequence |
| product_name | Char | Yes | Requested product name |
| requester_id | Many2one(res.users) | Yes | Requester |
| ops_branch_id | Many2one(ops.branch) | Yes | Branch |
| state | Selection | Yes | draft, submitted, approved, rejected, created |
| category_id | Many2one(product.category) | No | Product category |

---

#### ops.inter.branch.transfer (core)
**File:** `ops_inter_branch_transfer.py`
**Description:** Inter-Branch Transfer (core, non-accounting)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Auto-sequence |
| source_branch_id | Many2one(ops.branch) | Yes | From branch |
| dest_branch_id | Many2one(ops.branch) | Yes | To branch |
| transfer_type | Selection | Yes | stock, document |
| state | Selection | Yes | draft, confirmed, done, cancelled |

---

### Mixin / Abstract Models (Core)

---

#### ops.matrix.mixin
**File:** `ops_matrix_mixin.py`
**Type:** AbstractModel
**Description:** Core dimension propagation mixin. Inherited by all transactional models.

| Field | Type | Notes |
|-------|------|-------|
| ops_branch_id | Many2one(ops.branch) | Operational branch |
| ops_business_unit_id | Many2one(ops.business.unit) | Business unit (auto from branch) |
| ops_company_id | Many2one(res.company) | Related from branch |
| ops_analytic_distribution | Json | Auto-populated analytic distribution |

**Key Methods:**
- `_get_default_ops_branch()` - Returns user's primary branch
- `_get_default_ops_business_unit()` - Returns user's primary BU
- `_onchange_ops_branch_id()` - Auto-populates BU when branch changes
- `_compute_ops_analytic_distribution()` - Auto-sets analytic from branch/BU

---

#### ops.approval.mixin
**File:** `ops_approval_mixin.py`
**Type:** AbstractModel
**Description:** Approval locking mixin. Adds approval state and locked field behavior.

| Field | Type | Notes |
|-------|------|-------|
| approval_state | Selection | none, pending, approved, rejected |
| approval_locked | Boolean (computed) | True when approval is pending |

**Key Methods:**
- `_is_approval_locked()` - Returns True if pending approval (blocks edits)
- `write()` override - Prevents modification of locked records

---

#### ops.governance.mixin
**File:** `ops_governance_mixin.py`
**Type:** AbstractModel
**Description:** Governance rule enforcement mixin.

**Key Methods:**
- `_check_governance_rules()` - Evaluates all enabled governance rules for the model/action
- `_get_applicable_rules()` - Finds rules matching model and action
- `_evaluate_rule()` - Evaluates a single governance rule

---

#### ops.segregation.of.duties.mixin
**File:** `ops_segregation_of_duties_mixin.py`
**Type:** AbstractModel
**Description:** SoD enforcement mixin.

**Key Methods:**
- `_check_sod()` - Checks if current user violates any SoD rule for the given action
- `_get_sod_violations()` - Returns list of violated SoD rules

---

#### ops.field.visibility.mixin
**File:** `field_visibility.py`
**Type:** AbstractModel
**Description:** Dynamic field visibility based on rules.

**Related Model: ops.field.visibility.rule**
| Field | Type | Notes |
|-------|------|-------|
| name | Char | Rule name |
| model_name | Selection | Target model |
| field_name | Char | Field to control |
| visibility_mode | Selection | hidden, readonly, required |
| group_ids | Many2many(res.groups) | Groups affected |
| active | Boolean | Visible in catalog (catalog mode) |
| enabled | Boolean | Actually enforced (catalog mode) |

---

#### ops.sla.mixin
**File:** `ops_sla_mixin.py`
**Type:** AbstractModel
**Description:** SLA tracking integration mixin.

**Key Methods:**
- `_start_sla_tracking()` - Creates ops.sla.instance when SLA conditions met
- `_complete_sla_tracking()` - Marks SLA as met
- `_get_applicable_sla_templates()` - Finds matching SLA templates

---

#### ops.analytic.mixin
**File:** `ops_analytic_mixin.py`
**Type:** AbstractModel
**Description:** Analytic distribution mixin for financial models.

| Field | Type | Notes |
|-------|------|-------|
| ops_analytic_account_id | Many2one(account.analytic.account) | Direct analytic account |

**Key Methods:**
- `_get_analytic_from_branch()` - Gets analytic account from branch

---

#### ops.analytic.setup (wizard)
**File:** `ops_analytic_setup.py`
**Type:** TransientModel
**Description:** Analytic accounting setup wizard.

**Key Methods:**
- `action_setup_analytics()` - Creates analytic plan and accounts for all branches/BUs

---

#### ops.performance.indexes
**File:** `ops_performance_indexes.py`
**Description:** Performance optimization index management.

**Key Methods:**
- `_create_indexes()` - Creates database indexes for frequently queried fields
- Called during module install/upgrade

---

---

## Module 2: ops_matrix_accounting

**Source:** `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/`

### PDC & Budget Models

---

#### ops.pdc.receivable
**File:** `ops_pdc.py`
**Description:** Post-Dated Check - Receivable
**Inherits:** `mail.thread`, `mail.activity.mixin`, `ops.matrix.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Auto-sequence (PDC/RCV/YYYY/XXXX) |
| partner_id | Many2one(res.partner) | Yes | Yes | Customer |
| check_number | Char | Yes | Yes | Check number |
| check_date | Date | Yes | Yes | Check maturity date |
| amount | Float | Yes | Yes | Check amount |
| currency_id | Many2one(res.currency) | Yes | No | Currency |
| journal_id | Many2one(account.journal) | Yes | No | PDC journal |
| state | Selection | Yes | Yes | draft, registered, deposited, collected, returned, cancelled |
| ops_branch_id | Many2one(ops.branch) | Yes | Yes | Branch |
| collection_move_id | Many2one(account.move) | No | No | Collection JE |
| return_move_id | Many2one(account.move) | No | No | Return JE |
| return_reason | Text | No | Yes | Return reason |

**Key Methods:**
- `action_register()` - Creates Dr PDC Receivable, Cr Customer Receivable JE
- `action_deposit()` - Creates Dr Bank (in clearing), Cr PDC Receivable JE
- `action_collect()` - Creates Dr Bank, Cr Clearing JE
- `action_return()` - Creates reversal + penalty JE
- `action_cancel()` - Reverses all JEs

---

#### ops.pdc.payable
**File:** `ops_pdc.py`
**Description:** Post-Dated Check - Payable
**Inherits:** `mail.thread`, `mail.activity.mixin`, `ops.matrix.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Auto-sequence (PDC/PAY/YYYY/XXXX) |
| partner_id | Many2one(res.partner) | Yes | Yes | Vendor |
| check_number | Char | Yes | Yes | Check number |
| check_date | Date | Yes | Yes | Check date |
| amount | Float | Yes | Yes | Amount |
| state | Selection | Yes | Yes | draft, issued, presented, cleared, voided, cancelled |
| ops_branch_id | Many2one(ops.branch) | Yes | Yes | Branch |

**Key Methods:**
- `action_issue()` - Creates Dr Vendor Payable, Cr PDC Payable JE
- `action_present()` - Creates Dr PDC Payable, Cr Bank (clearing) JE
- `action_clear()` - Creates Dr Clearing, Cr Bank JE
- `action_void()` - Reverses all JEs

---

#### ops.budget
**File:** `ops_budget.py`
**Description:** Budget Header
**Inherits:** `mail.thread`, `mail.activity.mixin`, `ops.matrix.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Budget name |
| date_from | Date | Yes | Yes | Period start |
| date_to | Date | Yes | Yes | Period end |
| ops_branch_id | Many2one(ops.branch) | Yes | Yes | Branch |
| ops_business_unit_id | Many2one(ops.business.unit) | No | Yes | BU |
| state | Selection | Yes | Yes | draft, confirmed, validated, done, cancelled |
| line_ids | One2many(ops.budget.line) | No | No | Budget lines |
| total_planned | Float (computed) | No | No | Sum of planned |
| total_actual | Float (computed) | No | No | Sum of actual |
| total_committed | Float (computed) | No | No | Sum of committed (from POs) |
| total_variance | Float (computed) | No | No | Planned - (Actual + Committed) |

**Key Methods:**
- `action_confirm()` / `action_validate()` / `action_done()` - State workflow
- `check_budget_availability()` - Checks if amount available in budget (used by PO confirm)

---

#### ops.budget.line
**File:** `ops_budget.py`
**Description:** Budget Line Item

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| budget_id | Many2one(ops.budget) | Yes | Parent budget |
| account_id | Many2one(account.account) | Yes | GL account |
| analytic_account_id | Many2one(account.analytic.account) | No | Analytic |
| planned_amount | Float | Yes | Budgeted amount |
| actual_amount | Float (computed) | No | From posted JEs |
| committed_amount | Float (computed) | No | From confirmed POs |
| available_amount | Float (computed) | No | Planned - Actual - Committed |
| variance_percent | Float (computed) | No | Variance percentage |

---

### Asset Management Models

---

#### ops.asset.category
**File:** `ops_asset_category.py`
**Description:** Fixed Asset Category
**Inherits:** `mail.thread`, `mail.activity.mixin`
**Features:** `_parent_store = True` (hierarchical)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Category name |
| parent_id | Many2one(ops.asset.category) | No | Parent category |
| parent_path | Char | No | For _parent_store |
| journal_id | Many2one(account.journal) | Yes | Asset journal |
| asset_account_id | Many2one(account.account) | Yes | Asset account |
| depreciation_account_id | Many2one(account.account) | Yes | Accumulated depr. account |
| expense_account_id | Many2one(account.account) | Yes | Depreciation expense account |
| method | Selection | Yes | straight_line, declining_balance, degressive_then_linear |
| method_number | Integer | Yes | Number of depreciations |
| method_period | Integer | Yes | Period in months (1, 3, 6, 12) |
| method_progress_factor | Float | No | Degressive factor (default: 0.3) |
| prorata | Boolean | No | Prorata temporis |
| auto_post_depreciation | Boolean | No | Auto-post depreciation entries |
| company_id | Many2one(res.company) | Yes | Company |

**Constraints:**
- Case-insensitive unique name per company
- Degressive factor between 0 and 1
- method_number > 0, method_period in (1,3,6,12)

---

#### ops.asset
**File:** `ops_asset.py`
**Description:** Fixed Asset
**Inherits:** `mail.thread`, `mail.activity.mixin`, `ops.matrix.mixin`, `ops.analytic.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Asset name |
| code | Char | No | Yes | Auto-sequence (ASSET/YYYY/XXXX) |
| category_id | Many2one(ops.asset.category) | Yes | Yes | Asset category |
| purchase_date | Date | Yes | Yes | Acquisition date |
| purchase_value | Float | Yes | Yes | Original cost |
| salvage_value | Float | No | No | Salvage/residual value |
| depreciable_value | Float (computed) | No | No | purchase_value - salvage_value |
| book_value | Float (computed) | No | No | purchase_value - accumulated_depreciation |
| accumulated_depreciation | Float (computed) | No | No | Sum of posted depreciation |
| fully_depreciated | Boolean (computed) | No | No | book_value <= salvage_value |
| state | Selection | Yes | Yes | draft, running, paused, sold, disposed |
| depreciation_ids | One2many(ops.asset.depreciation) | No | No | Depreciation schedule |
| ops_branch_id | Many2one(ops.branch) | Yes | Yes | Branch (Zero-Trust required) |
| partner_id | Many2one(res.partner) | No | No | Vendor |
| invoice_id | Many2one(account.move) | No | No | Source vendor bill |
| impaired | Boolean | No | Yes | IAS 36 impairment flag |
| impairment_date | Date | No | No | Impairment date |
| recoverable_amount | Float | No | No | IAS 36 recoverable amount |
| impairment_loss | Float (computed) | No | No | book_value - recoverable_amount |
| impairment_move_id | Many2one(account.move) | No | No | Impairment JE |

**Constraints:**
- `_check_asset_branch_required` - ops_branch_id always required (Zero-Trust)

**Key Methods:**
- `action_run()` - Activates asset, generates depreciation schedule
- `generate_depreciation_schedule()` - Dispatches to linear/degressive/combined methods
- `_compute_linear_depreciation()` - Straight-line with optional prorata
- `_compute_degressive_depreciation()` - Declining balance method
- `_compute_degressive_then_linear()` - Switches to linear when linear > degressive
- `action_impair()` - IAS 36 impairment with JE generation
- `action_sell()` / `action_dispose()` - Asset disposal with gain/loss JE

---

#### ops.asset.depreciation
**File:** `ops_asset_depreciation.py`
**Description:** Depreciation Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| asset_id | Many2one(ops.asset) | Yes | Parent asset |
| sequence | Integer | No | Line number |
| depreciation_date | Date | Yes | Scheduled date |
| amount | Float | Yes | Depreciation amount |
| remaining_value | Float | No | Book value after this depreciation |
| cumulative_depreciation | Float (computed) | No | Running total |
| move_id | Many2one(account.move) | No | Posted JE |
| state | Selection | Yes | draft, posted, failed |
| auto_posted | Boolean | No | Posted by cron |
| auto_post_error | Text | No | Error message on failure |

**Key Methods:**
- `action_post()` - Creates depreciation JE (Dr Expense, Cr Accumulated Depr.)
- `cron_auto_post_depreciation()` - Daily cron for auto-posting
- `cron_send_depreciation_reminder()` - Monthly reminder for pending items
- `_is_period_locked()` - Checks fiscal period lock before posting

---

### Fiscal Period Models

---

#### ops.fiscal.period
**File:** `ops_fiscal_period.py`
**Description:** Fiscal Period with Soft/Hard Lock
**Inherits:** `mail.thread`, `mail.activity.mixin`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Period name (e.g., "Jan 2026") |
| date_from | Date | Yes | Period start |
| date_to | Date | Yes | Period end |
| company_id | Many2one(res.company) | Yes | Company |
| lock_state | Selection | Yes | open, soft_lock, hard_lock |
| branch_lock_ids | One2many(ops.fiscal.period.branch.lock) | No | Branch-level locks |
| checklist_ids | One2many(ops.period.close.checklist) | No | Close checklist |
| checklist_progress | Float (computed) | No | Percentage complete |

**Constraints:**
- `CHECK(date_from < date_to)` - Date ordering
- `UNIQUE(company_id, date_from, date_to)` - Unique period per company
- `_check_dates_overlap` - Python constraint preventing period overlap

**Key Methods:**
- `action_soft_lock()` / `action_hard_lock()` / `action_reopen()` - Lock state transitions
- `is_locked()` - Checks if period is locked (for move posting)
- `is_branch_locked()` - Checks branch-specific lock

---

#### ops.fiscal.period.branch.lock
**File:** `ops_fiscal_period.py`
**Description:** Branch-Level Period Lock

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| period_id | Many2one(ops.fiscal.period) | Yes | Parent period |
| branch_id | Many2one(ops.branch) | Yes | Branch |
| locked | Boolean | Yes | Lock status |
| locked_by_id | Many2one(res.users) | No | Who locked |
| locked_date | Datetime | No | When locked |

**Constraints:**
- `UNIQUE(period_id, branch_id)` - One lock per branch per period

---

#### ops.period.close.checklist
**File:** `ops_fiscal_period.py`
**Description:** Period Close Checklist Item

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| period_id | Many2one(ops.fiscal.period) | Yes | Parent period |
| name | Char | Yes | Checklist item |
| category | Selection | Yes | cutoff, reconciliation, accruals, review, reporting, approval |
| is_complete | Boolean | No | Completion flag |
| completed_by_id | Many2one(res.users) | No | Who completed |
| completed_date | Datetime | No | When completed |
| notes | Text | No | Notes |
| sequence | Integer | No | Display order |

**Key Methods:**
- `generate_for_period()` - Creates 19 standard checklist items across 6 categories

---

### Recurring & Template Models

---

#### ops.recurring.template
**File:** `ops_recurring.py`
**Description:** Recurring Journal Entry Template
**Inherits:** `mail.thread`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Template name |
| journal_id | Many2one(account.journal) | Yes | Journal |
| ops_branch_id | Many2one(ops.branch) | No | Branch |
| ops_business_unit_id | Many2one(ops.business.unit) | No | BU |
| recurring_period | Selection | Yes | daily, weekly, monthly, quarterly, yearly |
| recurring_interval | Integer | Yes | Interval multiplier |
| next_date | Date | No | Next generation date |
| auto_reverse | Boolean | No | Auto-reverse entries |
| reverse_days | Integer | No | Days after posting to reverse |
| require_approval | Boolean | No | Require approval before posting |
| line_ids | One2many(ops.recurring.template.line) | No | Template lines |
| entry_ids | One2many(ops.recurring.entry) | No | Generated entries |
| state | Selection | Yes | draft, active, paused, done |
| company_id | Many2one(res.company) | Yes | Company |

**Key Methods:**
- `action_activate()` / `action_pause()` / `action_done()` - State workflow
- `cron_generate_recurring_entries()` - Generates entries per schedule
- `_generate_entry()` - Creates single ops.recurring.entry from template

---

#### ops.recurring.template.line
**File:** `ops_recurring.py`
**Description:** Recurring Template Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | Many2one(ops.recurring.template) | Yes | Parent |
| sequence | Integer | No | Order |
| account_id | Many2one(account.account) | Yes | GL account |
| name | Char | No | Line description |
| debit | Float | No | Debit amount |
| credit | Float | No | Credit amount |
| analytic_account_id | Many2one(account.analytic.account) | No | Analytic |
| partner_id | Many2one(res.partner) | No | Partner |

---

#### ops.recurring.entry
**File:** `ops_recurring.py`
**Description:** Generated Recurring Entry Instance
**Inherits:** `mail.thread`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Auto-sequence |
| template_id | Many2one(ops.recurring.template) | Yes | Source template |
| date | Date | Yes | Entry date |
| move_id | Many2one(account.move) | No | Generated JE |
| reversal_move_id | Many2one(account.move) | No | Reversal JE |
| line_ids | One2many(ops.recurring.entry.line) | No | Entry lines |
| state | Selection | Yes | draft, pending_approval, approved, posted, reversed, cancelled |

**Key Methods:**
- `action_create_move()` - Creates account.move from entry
- `action_post_move()` - Posts the JE
- `action_reverse()` - Creates reversal JE
- `cron_process_auto_reversals()` - Auto-reverses after configured days

---

#### ops.recurring.entry.line
**File:** `ops_recurring.py`
**Description:** Recurring Entry Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| entry_id | Many2one(ops.recurring.entry) | Yes | Parent |
| account_id | Many2one(account.account) | Yes | GL account |
| debit | Float | No | Debit |
| credit | Float | No | Credit |
| partner_id | Many2one(res.partner) | No | Partner |

---

#### ops.journal.template
**File:** `ops_journal_template.py`
**Description:** One-Click Journal Entry Template (manual trigger)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Template name |
| code | Char | Yes | Unique code |
| journal_id | Many2one(account.journal) | Yes | Journal |
| ops_branch_id | Many2one(ops.branch) | No | Branch |
| category | Selection | Yes | accrual, provision, adjustment, reclassification, closing, depreciation, other |
| description | Text | No | Template description |
| line_ids | One2many(ops.journal.template.line) | No | Template lines |
| use_count | Integer | No | Usage counter |
| active | Boolean | No | Default: True |
| company_id | Many2one(res.company) | Yes | Company |

**Constraints:**
- `UNIQUE(code, company_id)` - Code unique per company

---

#### ops.journal.template.line
**File:** `ops_journal_template.py`
**Description:** Journal Template Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | Many2one(ops.journal.template) | Yes | Parent |
| sequence | Integer | No | Order |
| account_id | Many2one(account.account) | Yes | GL account |
| name | Char | No | Description |
| amount_type | Selection | Yes | fixed, percentage |
| debit | Float | No | Fixed debit (or % of base) |
| credit | Float | No | Fixed credit (or % of base) |
| partner_id | Many2one(res.partner) | No | Partner |

---

#### ops.journal.template.wizard
**File:** `ops_journal_template.py`
**Type:** TransientModel
**Description:** Create JE from Template

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| template_id | Many2one(ops.journal.template) | Yes | Template |
| date | Date | Yes | JE date |
| ref | Char | No | Reference |
| base_amount | Float | No | Base for percentage lines |

**Key Methods:**
- `action_create_entry()` - Creates account.move from template

---

### Follow-up & Credit Models

---

#### ops.followup
**File:** `ops_followup.py`
**Description:** Company-Level Follow-up Configuration

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Config name |
| company_id | Many2one(res.company) | Yes | Company |
| line_ids | One2many(ops.followup.line) | No | Escalation levels |

**Constraints:**
- `UNIQUE(company_id)` - One config per company

---

#### ops.followup.line
**File:** `ops_followup.py`
**Description:** Follow-up Escalation Level

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| followup_id | Many2one(ops.followup) | Yes | Parent config |
| name | Char | Yes | Level name |
| sequence | Integer | No | Escalation order |
| delay | Integer | Yes | Days overdue to trigger |
| send_email | Boolean | No | Send reminder email |
| create_activity | Boolean | No | Create activity for collector |
| block_credit | Boolean | No | Block credit at this level |
| description | Text | No | Level description |
| email_template_id | Many2one(mail.template) | No | Email template |

---

#### ops.partner.followup
**File:** `ops_followup.py`
**Description:** Partner Follow-up Status
**Inherits:** `mail.thread`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| partner_id | Many2one(res.partner) | Yes | Customer |
| company_id | Many2one(res.company) | Yes | Company |
| followup_level_id | Many2one(ops.followup.line) | No | Current level |
| max_overdue_days | Integer (computed) | No | Max days overdue |
| total_overdue_amount | Float (computed) | No | Total overdue amount |
| credit_blocked | Boolean | No | Credit blocked flag |
| credit_override | Boolean | No | Override active |
| credit_override_date | Date | No | Override expiry |
| credit_override_user_id | Many2one(res.users) | No | Who overrode |
| credit_override_reason | Text | No | Override reason |
| history_ids | One2many(ops.partner.followup.history) | No | Action history |
| last_followup_date | Date | No | Last action date |
| state | Selection | Yes | normal, warning, blocked |

**Constraints:**
- `UNIQUE(partner_id, company_id)` - One status per partner per company

**Key Methods:**
- `cron_process_followups()` - Automated follow-up processing
- `action_process()` - Manual follow-up execution
- `_compute_overdue_details()` - Calculates overdue days and amounts from open invoices

---

#### ops.partner.followup.history
**File:** `ops_followup.py`
**Description:** Follow-up Action History

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| followup_id | Many2one(ops.partner.followup) | Yes | Parent |
| date | Datetime | Yes | Action date |
| action_type | Selection | Yes | email, call, letter, activity, block, unblock |
| user_id | Many2one(res.users) | Yes | Who performed |
| notes | Text | No | Action notes |
| level_id | Many2one(ops.followup.line) | No | Level at time of action |

---

#### ops.credit.override.wizard
**File:** `ops_followup.py`
**Type:** TransientModel
**Description:** Credit Override Request

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| followup_id | Many2one(ops.partner.followup) | Yes | Target follow-up |
| reason | Text | Yes | Override reason |
| override_days | Integer | Yes | Duration in days |

**Key Methods:**
- `action_override()` - Applies temporary credit override

---

#### res.partner (_inherit - followup)
**File:** `ops_followup.py`
**Description:** Adds follow-up computed fields to partner

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| followup_status_id | Many2one(ops.partner.followup) (computed) | Current follow-up status |
| credit_blocked | Boolean (computed) | Is credit blocked |
| overdue_amount | Float (computed) | Total overdue amount |

---

### Inter-Branch & Reconciliation Models

---

#### ops.interbranch.transfer
**File:** `ops_interbranch_transfer.py`
**Description:** Inter-Branch Transfer with Accounting
**Inherits:** `mail.thread`, `mail.activity.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Auto-sequence |
| transfer_type | Selection | Yes | Yes | inventory, asset, funds, expense |
| source_branch_id | Many2one(ops.branch) | Yes | Yes | Source branch |
| dest_branch_id | Many2one(ops.branch) | Yes | Yes | Destination branch |
| amount | Float | Yes | Yes | Transfer amount |
| transit_account_id | Many2one(account.account) | Yes | No | Inter-branch transit account |
| source_account_id | Many2one(account.account) | Yes | No | Source account |
| dest_account_id | Many2one(account.account) | Yes | No | Destination account |
| source_move_id | Many2one(account.move) | No | No | Source JE |
| dest_move_id | Many2one(account.move) | No | No | Destination JE |
| journal_id | Many2one(account.journal) | Yes | No | Journal |
| state | Selection | Yes | Yes | draft, pending, received, reconciled, cancelled |
| company_id | Many2one(res.company) | Yes | No | Company |

**Key Methods:**
- `action_send()` - Creates source JE: Dr Transit, Cr Source Account
- `action_receive()` - Creates dest JE: Dr Dest Account, Cr Transit
- `action_reconcile()` - Reconciles transit account entries
- `action_cancel()` - Reverses all JEs

---

#### res.company (_inherit - interbranch)
**File:** `ops_interbranch_transfer.py`
**Description:** Adds default interbranch accounts to company

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| interbranch_transit_account_id | Many2one(account.account) | Default transit account |
| interbranch_journal_id | Many2one(account.journal) | Default interbranch journal |

---

#### ops.bank.reconciliation
**File:** `ops_bank_reconciliation.py`
**Description:** Bank Reconciliation Session
**Inherits:** `mail.thread`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Auto-sequence |
| journal_id | Many2one(account.journal) | Yes | Bank journal |
| ops_branch_id | Many2one(ops.branch) | No | Branch |
| date | Date | Yes | Reconciliation date |
| balance_start | Float | Yes | Opening balance |
| balance_end_statement | Float | Yes | Statement ending balance |
| balance_end_computed | Float (computed) | No | Computed from lines |
| difference | Float (computed) | No | Statement - Computed |
| line_ids | One2many(ops.bank.reconciliation.line) | No | Statement lines |
| state | Selection | Yes | draft, in_progress, reconciled, cancelled |
| match_statistics | Text (computed) | No | Match summary |

**Key Methods:**
- `action_auto_match()` - 3-pass matching: (1) reference+amount, (2) amount+date range, (3) partner+amount
- `action_reconcile()` - Finalizes reconciliation
- `action_import_statement()` - Opens CSV import wizard

---

#### ops.bank.reconciliation.line
**File:** `ops_bank_reconciliation.py`
**Description:** Bank Statement Line for Reconciliation

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| reconciliation_id | Many2one(ops.bank.reconciliation) | Yes | Parent |
| date | Date | Yes | Transaction date |
| name | Char | Yes | Description |
| ref | Char | No | Reference |
| amount | Float | Yes | Amount |
| partner_id | Many2one(res.partner) | No | Partner |
| match_status | Selection | Yes | unmatched, matched, manual |
| matched_move_line_id | Many2one(account.move.line) | No | Matched JE line |

---

#### ops.bank.statement.import.wizard
**File:** `ops_bank_reconciliation.py`
**Type:** TransientModel
**Description:** CSV Statement Import

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| reconciliation_id | Many2one(ops.bank.reconciliation) | Yes | Target session |
| file | Binary | Yes | CSV file |
| file_name | Char | No | File name |
| date_column | Integer | Yes | Date column index |
| description_column | Integer | Yes | Description column index |
| amount_column | Integer | Yes | Amount column index |
| reference_column | Integer | No | Reference column index |

**Key Methods:**
- `action_import()` - Parses CSV and creates reconciliation lines

---

### Lease Accounting Models

---

#### ops.lease
**File:** `ops_lease.py`
**Description:** IFRS 16 Lease
**Inherits:** `mail.thread`, `mail.activity.mixin`

| Field | Type | Required | Tracking | Notes |
|-------|------|----------|----------|-------|
| name | Char | Yes | Yes | Lease name |
| code | Char | No | No | Auto-sequence |
| lessor_id | Many2one(res.partner) | Yes | Yes | Lessor |
| lease_type | Selection | Yes | Yes | operating, finance |
| commencement_date | Date | Yes | Yes | Start date |
| end_date | Date | Yes | Yes | End date |
| payment_amount | Float | Yes | Yes | Per-period payment |
| payment_frequency | Selection | Yes | No | monthly, quarterly, semi_annual, annual |
| payment_timing | Selection | No | No | beginning, end |
| discount_rate | Float | Yes | No | Incremental borrowing rate |
| rou_asset_value | Float (computed) | No | No | PV of future payments |
| lease_liability | Float (computed) | No | No | PV of future payments |
| rou_asset_account_id | Many2one(account.account) | Yes | No | ROU asset account |
| lease_liability_account_id | Many2one(account.account) | Yes | No | Liability account |
| interest_expense_account_id | Many2one(account.account) | Yes | No | Interest expense account |
| depreciation_expense_account_id | Many2one(account.account) | Yes | No | Depreciation expense account |
| payment_account_id | Many2one(account.account) | Yes | No | Cash/bank account |
| journal_id | Many2one(account.journal) | Yes | No | Journal |
| payment_schedule_ids | One2many(ops.lease.payment.schedule) | No | No | Payment schedule |
| depreciation_ids | One2many(ops.lease.depreciation) | No | No | ROU depreciation schedule |
| state | Selection | Yes | Yes | draft, active, expired, terminated |
| company_id | Many2one(res.company) | Yes | No | Company |
| ops_branch_id | Many2one(ops.branch) | No | Yes | Branch |

**Key Methods:**
- `_compute_lease_values()` - PV annuity formula (with beginning/end timing adjustment)
- `action_activate()` - Creates initial recognition JE (Dr ROU Asset, Cr Lease Liability)
- `_generate_payment_schedule()` - Interest/principal amortization schedule
- `_generate_depreciation_schedule()` - Straight-line ROU depreciation

---

#### ops.lease.payment.schedule
**File:** `ops_lease.py`
**Description:** Lease Payment Schedule Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| lease_id | Many2one(ops.lease) | Yes | Parent lease |
| sequence | Integer | No | Payment number |
| date | Date | Yes | Payment date |
| payment_amount | Float | Yes | Total payment |
| interest_amount | Float | No | Interest portion |
| principal_amount | Float | No | Principal portion |
| balance_after | Float | No | Liability balance after |
| move_id | Many2one(account.move) | No | Payment JE |
| state | Selection | Yes | scheduled, paid |

**Key Methods:**
- `action_record_payment()` - Creates payment JE (Dr Liability + Dr Interest Expense, Cr Cash)

---

#### ops.lease.depreciation
**File:** `ops_lease.py`
**Description:** ROU Asset Depreciation Line

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| lease_id | Many2one(ops.lease) | Yes | Parent lease |
| sequence | Integer | No | Line number |
| date | Date | Yes | Depreciation date |
| amount | Float | Yes | Depreciation amount |
| remaining_value | Float | No | Book value after |
| move_id | Many2one(account.move) | No | Depreciation JE |
| state | Selection | Yes | draft, posted |

**Key Methods:**
- `action_post()` - Creates depreciation JE (Dr Depr. Expense, Cr ROU Accum. Depr.)

---

### Reporting Models

---

#### ops.financial.report.config
**File:** `ops_financial_report_config.py`
**Description:** Configurable Financial Report Structure
**Features:** `_parent_store = True` (hierarchical)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Line name |
| code | Char | No | Report line code |
| parent_id | Many2one(ops.financial.report.config) | No | Parent line |
| parent_path | Char | No | For _parent_store |
| sequence | Integer | No | Display order |
| type | Selection | Yes | sum, accounts, account_type, report_value |
| account_ids | Many2many(account.account) | No | Specific accounts |
| account_type_selection | Selection | No | Account type filter |
| sign | Integer | No | 1 or -1 (invert sign) |
| display_detail | Selection | No | no_detail, detail_flat, detail_with_hierarchy |
| style | Selection | No | normal, bold, italic, total |
| report_type | Selection | Yes | BS, PL, CF, Custom |
| company_id | Many2one(res.company) | Yes | Company |

**Key Methods:**
- `get_balance()` - Recursive balance computation with branch filtering
- `get_report_lines_data()` - Hierarchical data with comparison period
- `generate_default_balance_sheet()` - Creates standard BS structure (15+ lines)
- `generate_default_profit_loss()` - Creates standard P&L structure (20+ lines)

---

#### ops.report.audit
**File:** `ops_report_audit.py`
**Description:** Report Audit Log ("The Black Box")
**Security:** Immutable (write/unlink blocked for non-admin)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | Many2one(res.users) | Yes | Report generator |
| action_date | Datetime | Yes | Timestamp |
| report_engine | Selection | Yes | financial, treasury, asset, inventory |
| report_name | Char | Yes | Human-readable name |
| report_type | Char | No | Internal type code |
| parameters | Text | No | JSON of filters/parameters |
| export_format | Selection | No | screen, pdf, excel, html |
| ip_address | Char | No | Client IP |
| company_id | Many2one(res.company) | No | Company context |
| wizard_model | Char | No | Wizard model used |
| record_count | Integer | No | Records in report |
| display_name | Char (computed, stored) | No | Descriptive name |

**Key Methods:**
- `log_report()` - Class method: creates audit entry silently (never blocks report generation)
- `_clean_params_for_json()` - Safely serializes parameters including recordsets and dates
- `write()` / `unlink()` overrides - Block modification/deletion for non-admin

---

#### ops.report.template (_inherit - accounting)
**File:** `ops_report_template.py`
**Description:** Smart Report Templates with JSON config

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| engine | Selection | financial, treasury, asset, inventory |
| config_data | Text | JSON configuration |
| is_global | Boolean | Available to all users |
| user_id | Many2one(res.users) | Template owner (if private) |
| usage_count | Integer | Times used |
| last_used | Datetime | Last usage |

**Additional Model: ops.report.template.save.wizard (TransientModel)**
- Saves current wizard state as a reusable template

---

#### ops.report.helpers (_inherit)
**File:** `ops_report_helpers.py`
**Type:** AbstractModel (_inherit)
**Description:** Corporate report utility functions

**Key Methods:**
- `amount_to_words()` - Multi-currency (QAR/AED/SAR/USD/EUR/GBP) with Arabic support
- `get_primary_light()` / `get_primary_dark()` / `get_color_scheme()` - Color generation
- `format_amount()` / `format_amount_with_sign()` / `format_percentage()` - Number formatting
- `get_value_class()` / `get_value_color()` - CSS class based on value (positive/negative)
- `get_aging_class()` / `get_aging_color()` - Aging classification (current/30/60/90/120+)
- `get_variance_class()` / `format_variance()` / `classify_margin()` - Financial analysis helpers
- `get_report_context()` - Standard report context builder

---

### Consolidation / Analytics Models

---

#### ops.company.consolidation
**File:** `ops_company_consolidation.py`
**Type:** TransientModel
**Description:** Multi-Company Consolidation Report Wizard

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| company_ids | Many2many(res.company) | Yes | Companies to consolidate |
| date_from | Date | Yes | Start date |
| date_to | Date | Yes | End date |
| report_type | Selection | Yes | bs, pl, tb, aging |
| branch_ids | Many2many(ops.branch) | No | Branch filter |
| business_unit_ids | Many2many(ops.business.unit) | No | BU filter |
| consolidation_data | Json (computed) | No | Report data |

**Key Methods:**
- `_compute_consolidation()` - Aggregates data across selected companies
- `action_generate_excel()` - Excel export
- `action_generate_pdf()` - PDF export

---

#### ops.branch.report
**File:** `ops_branch_report.py`
**Type:** TransientModel
**Description:** Branch-Level Financial Report

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| branch_ids | Many2many(ops.branch) | Yes | Target branches |
| date_from | Date | Yes | Start |
| date_to | Date | Yes | End |
| report_type | Selection | Yes | pl, bs, tb |
| report_data | Json (computed) | No | Report output |

---

#### ops.business.unit.report
**File:** `ops_business_unit_report.py`
**Type:** TransientModel
**Description:** Business Unit Report

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| business_unit_ids | Many2many(ops.business.unit) | Yes | Target BUs |
| date_from | Date | Yes | Start |
| date_to | Date | Yes | End |
| report_type | Selection | Yes | pl, bs, tb |
| report_data | Json (computed) | No | Report output |

---

#### ops.consolidated.balance.sheet
**File:** `ops_consolidated_balance_sheet.py`
**Type:** TransientModel
**Description:** Consolidated Balance Sheet Report

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| company_ids | Many2many(res.company) | No | Companies |
| as_of_date | Date | Yes | Balance sheet date |
| include_unposted | Boolean | No | Include draft entries |
| report_data | Json (computed) | No | Hierarchical BS data |

---

#### ops.matrix.profitability.analysis
**File:** `ops_matrix_profitability_analysis.py`
**Type:** TransientModel
**Description:** Branch x BU Profitability Heatmap

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| company_id | Many2one(res.company) | Yes | Company |
| date_from | Date | Yes | Start |
| date_to | Date | Yes | End |
| matrix_data | Json (computed) | No | Profitability matrix |
| cached_data | Text | No | Cached JSON |
| cache_timestamp | Datetime | No | Cache time |

**Key Methods:**
- `_compute_matrix_data()` - Single 3-dimensional grouped query: O(1) instead of O(N*M), 300x faster

---

#### ops.trend.analysis
**File:** `ops_trend_analysis.py`
**Type:** TransientModel
**Description:** MoM/QoQ/YoY Variance Analysis

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| comparison_type | Selection | Yes | mom, qoq, yoy, custom |
| branch_ids | Many2many(ops.branch) | No | Branch filter |
| business_unit_ids | Many2many(ops.business.unit) | No | BU filter |
| group_by | Selection | Yes | branch, bu, account |
| show_revenue / show_expense / show_margin / etc. | Boolean (x7) | No | Column toggles |
| trend_data | Json (computed) | No | Trend analysis data |
| data_source | Selection (computed) | No | snapshot or realtime |

**Key Methods:**
- `_get_trend_from_snapshots()` - Uses pre-computed snapshots (fast path)
- `_get_trend_from_realtime()` - Falls back to live queries
- `_calculate_variances()` - Computes absolute and percentage variances
- `action_export_excel()` - Excel export with xlsxwriter

---

#### ops.matrix.snapshot
**File:** `ops_matrix_snapshot.py`
**Description:** Pre-Computed Financial Snapshot

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| snapshot_date | Date | Yes | Snapshot date |
| company_id | Many2one(res.company) | Yes | Company |
| ops_branch_id | Many2one(ops.branch) | No | Branch |
| ops_business_unit_id | Many2one(ops.business.unit) | No | BU |
| snapshot_type | Selection | Yes | daily, weekly, monthly, quarterly |
| total_revenue | Float | No | Revenue |
| total_expense | Float | No | Expenses |
| total_cogs | Float | No | COGS |
| gross_profit | Float | No | Revenue - COGS |
| net_profit | Float | No | Revenue - Expense |
| total_assets | Float | No | Total assets |
| total_liabilities | Float | No | Total liabilities |
| total_equity | Float | No | Equity |
| total_receivable | Float | No | AR total |
| total_payable | Float | No | AP total |
| cash_balance | Float | No | Cash balance |
| inventory_value | Float | No | Inventory value |

**Constraints:**
- `UNIQUE(snapshot_date, company_id, ops_branch_id, ops_business_unit_id, snapshot_type)`

**Key Methods:**
- `cron_create_daily_snapshot()` - Daily snapshot creation
- `_create_snapshot()` - Computes all metrics from posted JEs
- Performance: 100-600x faster than realtime queries for reporting

---

### Standard Model Extensions (Accounting)

---

#### res.company (_inherit - accounting)
**File:** `res_company.py`
**Description:** Accounting-specific company fields

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_report_primary_color | Char | Primary color for reports |
| ops_report_secondary_color | Char | Secondary report color |
| ops_report_font_family | Selection | Report font |
| ops_report_show_branch | Boolean | Show branch on reports |
| ops_report_paper_format | Selection | Paper format |
| pdc_receivable_journal_id | Many2one(account.journal) | PDC receivable journal |
| pdc_payable_journal_id | Many2one(account.journal) | PDC payable journal |
| pdc_receivable_account_id | Many2one(account.account) | PDC receivable account |
| pdc_payable_account_id | Many2one(account.account) | PDC payable account |
| pdc_clearing_account_id | Many2one(account.account) | PDC clearing account |
| default_budget_warning | Boolean | Budget warning on PO/SO |

**Key Methods:**
- `get_ops_report_settings()` - Crash-proof dict for report templates

---

#### res.config.settings (_inherit - accounting)
**File:** `res_config_settings.py`
**Type:** TransientModel
**Description:** Accounting module settings

**Fields:** Related fields for all res.company accounting settings (PDC journals/accounts, report colors, budget options)

---

#### account.move (_inherit - accounting)
**File:** `account_move.py`
**Description:** Asset management, budget warning, three-way match, period lock

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| asset_id | Many2one(ops.asset) | Source asset |
| asset_depreciation_id | Many2one(ops.asset.depreciation) | Source depreciation line |
| budget_warning | Text (computed) | Budget availability warning |
| three_way_match_status | Selection | 8 states: no_po, pending_receipt, pending_match, matched, partial_match, mismatch, tolerance_match, override |
| three_way_match_details | Text (computed) | Match analysis details |
| matched_po_ids | Many2many(purchase.order) | Matched POs |
| matched_picking_ids | Many2many(stock.picking) | Matched receipts |
| three_way_override | Boolean | Override flag |
| three_way_override_reason | Text | Override reason |
| three_way_override_user_id | Many2one(res.users) | Who overrode |

**Key Methods:**
- `action_post()` override - Enforces: period lock, three-way match, budget validation
- `_check_period_lock()` - Company-level and branch-level fiscal period lock
- `_check_three_way_match()` - Full PO/Receipt/Invoice matching engine
- `_compute_budget_warning()` - Budget availability check
- Blocks cancellation/deletion of asset-related moves

---

#### purchase.order (_inherit - accounting)
**File:** `purchase_order.py`
**Description:** Budget control integration

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| budget_warning | Text (computed) | Budget availability message |
| budget_available | Boolean (computed) | Budget check passed |

**Key Methods:**
- `button_confirm()` override - Budget check with raise_error=True
- `_check_budget_availability()` - Uses ops.budget.check_budget_availability()

---

#### ops.product.category.default
**File:** `ops_product_category_defaults.py`
**Description:** Default Accounts for Product Categories

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| category_id | Many2one(product.category) | Yes | Product category |
| company_id | Many2one(res.company) | Yes | Company |
| income_account_id | Many2one(account.account) | No | Default income account |
| expense_account_id | Many2one(account.account) | No | Default expense account |
| asset_account_id | Many2one(account.account) | No | Default asset account |

---

#### ops.product.category.default.line
**File:** `ops_product_category_defaults.py`
**Description:** Product Category Default Line (branch-specific)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| default_id | Many2one(ops.product.category.default) | Yes | Parent |
| branch_id | Many2one(ops.branch) | Yes | Branch |
| income_account_id | Many2one(account.account) | No | Branch income account |
| expense_account_id | Many2one(account.account) | No | Branch expense account |

---

#### ops.matrix.standard.extensions (5 models)
**File:** `ops_matrix_standard_extensions.py`
**Description:** Standard Odoo model extensions for accounting

Models extended:
- **account.move.line** (_inherit) - Adds ops_branch_id, ops_business_unit_id
- **account.analytic.line** (_inherit) - Adds ops_branch_id
- **account.bank.statement** (_inherit) - Adds ops_branch_id
- **account.bank.statement.line** (_inherit) - Adds ops_branch_id
- **stock.valuation.layer** (_inherit) - Adds ops_branch_id

---

### Mixin / Abstract Models (Accounting)

---

#### ops.intelligence.security.mixin
**File:** `ops_intelligence_security_mixin.py`
**Type:** AbstractModel
**Description:** Security mixin for consolidation/intelligence reports

**Key Methods:**
- `_check_intelligence_access()` - Validates user has executive or manager access for consolidation reports
- `_get_allowed_companies()` - Returns companies user can report on
- `_apply_intelligence_domain()` - Adds security filters to report queries

---

#### ops.segregation.of.duties (_inherit - accounting)
**File:** `ops_sod_accounting.py`
**Description:** Extends SoD selections for accounting models

**Added Selections:**
- model_name: `ops.bank.reconciliation`
- action_1/action_2: `reconcile`

---

---

## Module 3: ops_kpi

**Source:** `/opt/gemini_odoo19/addons/ops_kpi/models/`

---

#### ops.kpi
**File:** `ops_kpi.py`
**Description:** KPI Definition
**Order:** `sequence, name`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | KPI name (translatable) |
| code | Char | Yes | Unique code (e.g., SALES_TOTAL) |
| description | Text | No | Description (translatable) |
| sequence | Integer | No | Default: 10 |
| active | Boolean | No | Default: True |
| category | Selection | Yes | 13 categories: sales, purchase, inventory, finance, receivable, payable, pdc, treasury, budget, asset, governance, system, operations |
| source_model | Char | Yes | Odoo model name |
| calculation_type | Selection | Yes | count, sum, average, custom |
| measure_field | Char | No | Field to sum/average |
| domain_filter | Char | No | Domain expression (default: []) |
| custom_formula | Text | No | Python expression for custom type |
| date_field | Char | No | Date filter field (default: create_date) |
| default_period | Selection | No | 8 periods: today through all_time |
| format_type | Selection | No | number, currency, percentage, integer |
| icon | Char | No | FontAwesome class |
| color | Char | No | Hex color |
| show_trend | Boolean | No | Default: True |
| trend_direction | Selection | No | up_good, down_good, neutral |
| requires_cost_access | Boolean | No | Requires group_ops_see_cost |
| requires_margin_access | Boolean | No | Requires group_ops_see_margin |
| visible_to_it_admin | Boolean | No | Default: False |
| persona_ids | Many2many(ops.persona) | No | Target personas |
| scope_type | Selection | No | company, bu, branch, own |

**Constraints:**
- `UNIQUE(code)` - KPI code globally unique

**Key Methods:**
- `_check_source_model()` - Validates model exists
- `_get_secure_domain()` - Builds security-compliant domain (IT Admin blindness, scope filtering, branch isolation, company filter)
- `_check_user_access()` - Checks IT Admin, cost/margin, persona access
- `compute_value()` - Wrapper for ops.kpi.value.compute_kpi_value()
- `get_time_series()` - Time series data using _read_group (batched aggregation)
- `get_breakdown()` - Breakdown by dimension using _read_group
- `get_comparison()` - MoM and YoY comparison values

---

#### ops.kpi.value
**File:** `ops_kpi_value.py`
**Description:** KPI Computed Value
**Order:** `compute_date desc`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| kpi_id | Many2one(ops.kpi) | Yes | KPI definition |
| company_id | Many2one(res.company) | No | Company scope |
| branch_id | Many2one(ops.branch) | No | Branch scope |
| user_id | Many2one(res.users) | No | User scope |
| value | Float | No | Computed value |
| previous_value | Float | No | Previous period value |
| trend_percentage | Float (computed, stored) | No | % change |
| trend_direction | Selection (computed, stored) | No | up, down, flat |
| period | Selection | Yes | Same 8 periods as ops.kpi |
| compute_date | Datetime | No | Computation timestamp |
| period_start | Date | No | Period start |
| period_end | Date | No | Period end |

**Module-level function:**
- `_get_safe_eval_context(env)` - Builds safe eval context for KPI domain filters

**Key Methods:**
- `_compute_trend()` - Calculates trend from value vs previous_value
- `_get_period_dates()` - Converts period name to date range
- `_get_previous_period_dates()` - Calculates comparison period dates
- `compute_kpi_value()` - Main computation: builds secure domain, evaluates KPI formula, computes trend

---

#### ops.kpi.board
**File:** `ops_kpi_board.py`
**Description:** KPI Dashboard Board
**Inherits:** `mail.thread`
**Order:** `sequence, name`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Dashboard name (translatable) |
| code | Char | Yes | Unique code |
| description | Text | No | Description (translatable) |
| sequence | Integer | No | Default: 10 |
| active | Boolean | No | Default: True |
| dashboard_type | Selection | Yes | 12 types: executive, finance, sales, purchase, inventory, receivable, payable, treasury, branch, bu, system, custom |
| persona_ids | Many2many(ops.persona) | No | Persona access |
| persona_codes | Char | No | Comma-separated codes (alternative) |
| group_ids | Many2many(res.groups) | No | Group access |
| widget_ids | One2many(ops.kpi.widget) | No | Dashboard widgets |
| widget_count | Integer (computed) | No | Widget count |
| auto_refresh | Boolean | No | Default: True |
| refresh_interval | Selection | No | 30s to 10min or Manual |
| columns | Integer | No | Grid columns (default: 4) |
| alert_threshold | Float | No | Default: -10.0% |
| chart_kpi_codes | Char | No | Comma-separated KPI codes for main chart |
| company_id | Many2one(res.company) | No | Company |

**Constraints:**
- `UNIQUE(code, company_id)` - Code unique per company

**Key Methods:**
- `_check_user_dashboard_access()` - Multi-layer access check: admin bypass, IT Admin restriction, persona codes, persona_ids, group_ids, default allow
- `get_user_dashboards()` - Returns accessible dashboards for current user
- `get_dashboard_data()` - Main RPC: fetches all widget data
- `get_chart_data()` - Enhanced RPC: KPI cards with sparklines, trend charts, breakdown charts, comparison data, alerts
- `get_kpi_chart_data()` - Single KPI drill-down chart data
- `get_company_currency_info()` - Currency formatting info for frontend

---

#### ops.kpi.widget
**File:** `ops_kpi_widget.py`
**Description:** KPI Dashboard Widget
**Order:** `sequence, id`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | Char | Yes | Widget name |
| board_id | Many2one(ops.kpi.board) | Yes | Parent board |
| sequence | Integer | No | Default: 10 |
| active | Boolean | No | Default: True |
| widget_type | Selection | Yes | kpi, kpi_group, bar_chart, line_chart, pie_chart, list, metric |
| kpi_id | Many2one(ops.kpi) | No | Single KPI reference |
| kpi_ids | Many2many(ops.kpi) | No | Multiple KPIs (for group) |
| title | Char | No | Display title override |
| subtitle | Char | No | Subtitle |
| icon | Char | No | Icon override |
| color | Char | No | Color override |
| position_x | Integer | No | Grid column |
| position_y | Integer | No | Grid row |
| width | Integer | No | Column span (default: 1) |
| height | Integer | No | Row span (default: 1) |
| period_override | Selection | No | Override default period |
| list_limit | Integer | No | Top N (default: 5) |
| list_model | Char | No | Model for list widget |
| list_fields | Char | No | Comma-separated display fields |
| list_domain | Char | No | List domain filter |
| list_order | Char | No | Sort order |

**Key Methods:**
- `get_widget_data()` - Returns formatted data for frontend (dispatches by widget_type)
- `_get_list_data()` - Fetches list data with branch isolation and company filter
- `cron_refresh_dashboard_data()` - Pre-compute widget data via cron

---

#### res.company (_inherit - KPI)
**File:** `res_company_kpi.py`
**Description:** KPI Center display preferences per company

**Added Fields:**
| Field | Type | Notes |
|-------|------|-------|
| ops_kpi_gradient_headers | Boolean | Gradient section headers (default: True) |
| ops_kpi_sparkline_style | Selection | gradient, line, bar |
| ops_kpi_chart_fill | Selection | gradient, solid, none |
| ops_kpi_animation | Selection | full, reduced, none |
| ops_kpi_card_style | Selection | accent, shadow, border |
| ops_kpi_color_scheme | Selection | default, vibrant, muted, monochrome |
| ops_kpi_refresh_interval | Integer | Default: 120 seconds |

---

#### res.config.settings (_inherit - KPI)
**File:** `res_config_settings.py`
**Type:** TransientModel
**Description:** KPI settings in General Settings

**Fields:** Related fields for all res.company KPI display settings (7 fields, all readonly=False)

---

---

## Inheritance Chain Map

This shows which Odoo base models are extended and by which modules/files.

### res.company
1. `ops_matrix_core/models/res_company.py` - ops_code, branch_ids, three-way match config
2. `ops_matrix_accounting/models/res_company.py` - Report colors, PDC journals/accounts, budget config
3. `ops_matrix_accounting/models/ops_interbranch_transfer.py` - Interbranch transit/journal defaults
4. `ops_kpi/models/res_company_kpi.py` - KPI display preferences

### res.users
1. `ops_matrix_core/models/res_users.py` - Persona, branch, BU assignments
2. `ops_matrix_core/models/res_users_authority.py` - Authority checking
3. `ops_matrix_core/models/res_users_sod.py` - SoD enforcement
4. `ops_matrix_core/models/res_users_group_mapper.py` - Persona-to-group auto-mapping
5. `ops_matrix_core/models/res_users_api.py` - API authentication

### res.partner
1. `ops_matrix_core/models/partner.py` - CR number, master verification, credit control, stewardship state
2. `ops_matrix_accounting/models/ops_followup.py` - Follow-up status computed fields

### res.config.settings
1. `ops_matrix_accounting/models/res_config_settings.py` - Accounting settings
2. `ops_kpi/models/res_config_settings.py` - KPI settings

### sale.order
1. `ops_matrix_core/models/sale_order.py` - Matrix dimensions, governance, customer verification
2. `ops_matrix_core/models/sale_order_approval.py` - Approval workflow

### sale.order.line
1. `ops_matrix_core/models/sale_order_line.py` - Price protection, cost shield, margin, branch activation

### purchase.order
1. `ops_matrix_core/models/purchase_order.py` - Matrix dimensions, SoD, governance
2. `ops_matrix_accounting/models/purchase_order.py` - Budget control integration

### account.move
1. `ops_matrix_core/models/account_move.py` - Matrix dimensions
2. `ops_matrix_accounting/models/account_move.py` - Assets, budget warning, three-way match, period lock

### account.payment
1. `ops_matrix_core/models/account_payment.py` - Matrix dimensions

### stock.picking
1. `ops_matrix_core/models/stock_picking.py` - Matrix dimensions, credit firewall

### stock.move
1. `ops_matrix_core/models/stock_move.py` - Matrix dimensions

### stock.quant
1. `ops_matrix_core/models/stock_quant.py` - Matrix dimensions from warehouse

### stock.warehouse
1. `ops_matrix_core/models/stock_warehouse.py` - Branch linkage

### stock.warehouse.orderpoint
1. `ops_matrix_core/models/stock_warehouse_orderpoint.py` - Branch from warehouse

### ir.actions.report
1. `ops_matrix_core/models/ir_actions_report.py` - Governance on PDF generation

### ir.exports
1. `ops_matrix_core/models/ir_exports_override.py` - Export restriction

### mail.message
1. `ops_matrix_core/models/mail_message.py` - Branch context

### account.report
1. `ops_matrix_core/models/account_report.py` - Branch filtering

### product.template / product.product
1. `ops_matrix_core/models/product.py` - Global Master, branch activation, BU silo

### product.pricelist
1. `ops_matrix_core/models/pricelist.py` - Branch-scoped pricelists

### account.move.line
1. `ops_matrix_accounting/models/ops_matrix_standard_extensions.py` - Branch/BU fields

### account.analytic.line
1. `ops_matrix_accounting/models/ops_matrix_standard_extensions.py` - Branch field

### account.bank.statement / account.bank.statement.line
1. `ops_matrix_accounting/models/ops_matrix_standard_extensions.py` - Branch field

### stock.valuation.layer
1. `ops_matrix_accounting/models/ops_matrix_standard_extensions.py` - Branch field

### ops.report.template
1. `ops_matrix_core/models/ops_report_template.py` - Base report template
2. `ops_matrix_accounting/models/ops_report_template.py` - Engine, config_data, global/private

### ops.report.helpers
1. `ops_matrix_accounting/models/ops_report_helpers.py` - Corporate report utilities

### ops.segregation.of.duties
1. `ops_matrix_core/models/ops_segregation_of_duties.py` - Base SoD model
2. `ops_matrix_accounting/models/ops_sod_accounting.py` - Bank reconciliation SoD extension

---

## Cross-Module Relationship Map

### Central Hub: ops.branch
**Referenced by (Many2one):**
- ops.business.unit.branch_ids (One2many)
- res.company.branch_ids (One2many)
- res.users.primary_branch_id, ops_allowed_branch_ids
- All transactional models via ops.matrix.mixin (sale.order, purchase.order, account.move, stock.picking, etc.)
- ops.budget, ops.pdc.receivable, ops.pdc.payable
- ops.asset, ops.fiscal.period.branch.lock
- ops.recurring.template, ops.journal.template
- ops.interbranch.transfer (source_branch_id, dest_branch_id)
- ops.bank.reconciliation
- ops.lease
- ops.matrix.snapshot
- ops.kpi.value
- ops.governance.rule.branch_ids (Many2many)
- product.template.ops_branch_activation_ids (Many2many)

### Central Hub: ops.persona
**Referenced by:**
- res.users.persona_id (Many2one), ops_persona_ids (Many2many)
- ops.persona.delegation (delegator persona)
- ops.governance.limit.persona_id (Many2one)
- ops.kpi.persona_ids (Many2many)
- ops.kpi.board.persona_ids (Many2many)
- ops.dashboard.config.persona_ids (Many2many)

### Central Hub: ops.business.unit
**Referenced by (Many2one):**
- ops.branch.business_unit_id
- All transactional models via ops.matrix.mixin
- ops.budget
- ops.matrix.snapshot
- ops.recurring.template, ops.journal.template

### Financial Chain: account.move
**Created by:**
- ops.pdc.receivable / ops.pdc.payable (all lifecycle transitions)
- ops.asset.depreciation.action_post()
- ops.asset.action_impair() / action_sell() / action_dispose()
- ops.recurring.entry.action_create_move()
- ops.journal.template.wizard.action_create_entry()
- ops.interbranch.transfer.action_send() / action_receive()
- ops.lease.action_activate()
- ops.lease.payment.schedule.action_record_payment()
- ops.lease.depreciation.action_post()

### Budget Chain:
ops.budget -> ops.budget.line -> account.account
purchase.order.button_confirm() -> ops.budget.check_budget_availability()
account.move.action_post() -> budget validation

### Asset Chain:
ops.asset.category -> ops.asset -> ops.asset.depreciation -> account.move

### Lease Chain:
ops.lease -> ops.lease.payment.schedule -> account.move
ops.lease -> ops.lease.depreciation -> account.move

### Follow-up Chain:
ops.followup -> ops.followup.line (escalation levels)
ops.partner.followup -> ops.partner.followup.history
ops.partner.followup -> ops.credit.override.wizard

### Reporting Chain:
ops.report.audit (logs all report generation)
ops.report.template (saves report configurations)
ops.financial.report.config (defines BS/PL structure)
ops.matrix.snapshot (pre-computed data for fast reporting)

### KPI Chain:
ops.kpi.board -> ops.kpi.widget -> ops.kpi -> ops.kpi.value
ops.kpi uses _get_secure_domain() for branch/BU/company/IT-blindness filtering

---

*End of Model Registry*
*Total models documented: 95+ (including all _inherit extensions)*
*Generated from direct source code analysis of all model files across ops_matrix_core, ops_matrix_accounting, and ops_kpi modules.*
