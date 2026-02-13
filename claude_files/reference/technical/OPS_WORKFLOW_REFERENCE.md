# OPS Framework -- Workflow & Business Logic Reference

> **Generated**: 2026-02-13
> **Source**: Full code audit of ops_matrix_core and ops_matrix_accounting
> **Odoo Version**: 19.0 Community Edition

---

## Table of Contents

1. [Approval Workflow Engine](#1-approval-workflow-engine)
2. [Governance Rules Catalog](#2-governance-rules-catalog)
3. [Segregation of Duties (SoD)](#3-segregation-of-duties-sod)
4. [Three-Way Matching](#4-three-way-matching)
5. [SLA Tracking](#5-sla-tracking)
6. [Audit Logging](#6-audit-logging)
7. [Accounting Workflows](#7-accounting-workflows)
8. [State Machines](#8-state-machines)
9. [Cross-Cutting Concerns](#9-cross-cutting-concerns)

---

## 1. Approval Workflow Engine

### 1.1 Architecture Overview

The approval system is a mixin-based architecture with five cooperating components:

| Component | Model | Module | File |
|-----------|-------|--------|------|
| Approval Mixin | `ops.approval.mixin` (AbstractModel) | ops_matrix_core | `models/ops_approval_mixin.py` |
| Approval Request | `ops.approval.request` | ops_matrix_core | `models/ops_approval_request.py` |
| Approval Rule | `ops.approval.rule` | ops_matrix_core | `models/ops_approval_rule.py` |
| Approval Dashboard | `ops.approval.dashboard` (SQL View) | ops_matrix_core | `models/ops_approval_dashboard.py` |
| Recall Wizard | `ops.approval.recall.wizard` (TransientModel) | ops_matrix_core | `wizard/ops_approval_recall_wizard.py` |
| Reject Wizard | `ops.approval.reject.wizard` (TransientModel) | ops_matrix_core | `wizard/ops_approval_reject_wizard.py` |

### 1.2 Approval Mixin (`ops.approval.mixin`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_approval_mixin.py`

Any model can inherit this mixin to become approval-lockable. It adds:

**Fields**:
- `approval_locked` (Boolean) -- When True, prevents write/unlink/print
- `approval_request_id` (Many2one -> `ops.approval.request`) -- Link to active request

**Core Method: `_check_approval_lock(operation)`**

```
Parameters:
  operation: str -- 'write', 'unlink', or 'print'

Logic:
  1. If no records have approval_locked=True -> return (no lock)
  2. Admin bypass check:
     - If user has base.group_system OR env.su is True -> allow
     - BUT logs bypass to ops.security.audit with event_type='admin_bypass'
  3. For non-admin users:
     - If operation == 'write':
       - Check if requestor (approval_request_id.requested_by == user)
       - If requestor -> raise UserError("recall instead of edit")
       - Otherwise -> raise UserError("locked, contact approver")
     - If operation == 'unlink' -> raise UserError("cannot delete locked")
     - If operation == 'print' -> raise UserError("cannot print locked")
```

**Override Methods**:
- `write(vals)` -- calls `_check_approval_lock('write')` before `super()`
- `unlink()` -- calls `_check_approval_lock('unlink')` before `super()`

**Action Method: `action_recall_approval()`**
- Only the requestor (approval_request_id.requested_by) can recall
- Opens `ops.approval.recall.wizard` in a modal

### 1.3 Approval Request (`ops.approval.request`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_approval_request.py`

**States**: `pending` -> `approved` | `rejected` | `cancelled`

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Auto-generated description |
| `state` | Selection | pending/approved/rejected/cancelled |
| `rule_id` | Many2one (ops.governance.rule) | Triggering governance rule |
| `approval_rule_id` | Many2one (ops.approval.rule) | Triggering approval rule |
| `model_name` | Char | Source model (e.g., 'sale.order') |
| `res_id` | Integer | Source record ID |
| `requested_by` | Many2one (res.users) | Who triggered the approval |
| `approver_ids` | Many2many (res.users) | Who can approve |
| `approved_by` | Many2one (res.users) | Who approved |
| `priority` | Selection | low/medium/high/urgent |
| `escalation_level` | Integer | 0-3, current escalation tier |
| `escalation_timeout_hours` | Float | Hours before auto-escalation |
| `company_id` | Many2one | Inherited from source record |
| `ops_branch_id` | Many2one | Inherited from source record |
| `ops_business_unit_id` | Many2one | Inherited from source record |

**Violation Tracking Fields** (populated when triggered by governance):
| Field | Type |
|-------|------|
| `violation_type` | Selection: matrix/discount/margin/price/other |
| `violation_severity` | Selection: low/medium/high/critical |
| `discount_percent` | Float |
| `margin_percent` | Float |
| `price_variance_percent` | Float |
| `original_value` | Float |
| `requested_value` | Float |
| `threshold_value` | Float |

**Priority Deadlines**:
| Priority | Response Window |
|----------|----------------|
| low | 5 business days |
| medium | 2 business days |
| high | 1 business day |
| urgent | Same day |

**Method: `action_approve()`**
```
Logic:
  1. Verify state == 'pending'
  2. Check user in approver_ids (or has base.group_system)
  3. Check delegation: _check_delegation_approval(user)
     - Queries ops.persona.delegation for active delegations
     - If delegated, records delegation info
  4. Set state='approved', approved_by=user, approved_date=now
  5. Unlock source record: approval_locked=False
  6. Post to source record chatter (includes delegation info if applicable)
```

**Method: `_check_delegation_approval(user)`**
```
Parameters:
  user: res.users record

Logic:
  1. If user already in approver_ids -> return (True, None)
  2. Search ops.persona.delegation:
     - delegate_user_id = user
     - state = 'active'
     - date_from <= today <= date_to
  3. For each delegation, check if delegating user is in approver_ids
  4. If found -> return (True, delegation_record)
  5. If not found -> return (False, None)
```

**Method: `action_escalate()`**
```
Logic:
  1. Determine next escalation level (current + 1, max 3)
  2. Find current approver's personas via ops_persona_ids
  3. Look up parent persona (parent_id field on ops.persona)
  4. If parent persona found:
     - Get users with that persona
     - Add to approver_ids
     - Increment escalation_level
     - Post escalation message to chatter
  5. If no parent persona -> post "maximum escalation reached" warning
```

**Cron: `_cron_escalate_overdue_approvals()`**
```
Trigger: Scheduled cron job (periodic)

Logic:
  1. Find pending requests past escalation timeout
  2. For each overdue request:
     - Call action_escalate()
     - Log escalation event
```

**Cron: `cron_send_approval_reminders()`**
```
Trigger: Scheduled cron job (periodic)

Logic:
  1. Find pending requests older than 24 hours
  2. Send reminder notifications to approvers
  3. Log reminder sent
```

### 1.4 Approval Rule (`ops.approval.rule`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_approval_rule.py`

A lightweight wrapper for simple approval rules that can optionally link to `ops.governance.rule`.

**Method: `check_requires_approval(record)`**
```
Parameters:
  record: any Odoo record

Returns: bool

Logic:
  1. Check active and model_name match
  2. Evaluate condition_domain via safe_eval + filtered_domain
  3. Evaluate condition_code via safe_eval with {record, user, env}
  4. Return True if all conditions pass
```

**Method: `get_approvers(record)`**
```
Returns: res.users recordset

Logic:
  1. Start with approver_user_ids (direct users)
  2. Add users from approver_persona_ids (via ops_persona_ids field)
  3. Add users from approver_group_ids (via group.users)
  4. Return union of all approvers
```

**Method: `create_approval_request(record, notes='')`**
```
Logic:
  1. Resolve approvers via get_approvers()
  2. If no approvers -> raise ValidationError
  3. Create ops.approval.request with:
     - approval_rule_id = self
     - rule_id = governance_rule_id (if linked)
     - model_name, res_id from record
     - approver_ids = resolved approvers
     - requested_by = current user
```

### 1.5 Recall Wizard (`ops.approval.recall.wizard`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/wizard/ops_approval_recall_wizard.py`

**Method: `action_confirm_recall()`**
```
Validation:
  - reason field required, minimum 10 characters

Logic:
  1. Set approval_request.state = 'cancelled'
  2. Set source record approval_locked = False
  3. Post to source record chatter: "Recall reason: {reason}"
```

### 1.6 Reject Wizard (`ops.approval.reject.wizard`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/wizard/ops_approval_reject_wizard.py`

**Method: `action_confirm_reject()`**
```
Validation:
  - reason field required, minimum 10 characters

Logic:
  1. Set approval_request.state = 'rejected'
  2. Set source record approval_locked = False
  3. Post to source record chatter: "Rejection reason: {reason}"
```

### 1.7 Approval Dashboard (`ops.approval.dashboard`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_approval_dashboard.py`

SQL view (`_auto = False`) joining:
- `ops.approval.request`
- `ops.governance.rule`
- `ops.persona`
- `ops.sla.instance`

Provides: pending request count with SLA status and `time_to_breach` for dashboard widgets.

---

## 2. Governance Rules Catalog

### 2.1 Architecture Overview

| Component | Model | Module | File |
|-----------|-------|--------|------|
| Governance Mixin | `ops.governance.mixin` (AbstractModel) | ops_matrix_core | `models/ops_governance_mixin.py` |
| Governance Rule | `ops.governance.rule` | ops_matrix_core | `models/ops_governance_rule.py` |
| Discount Limits | `ops.governance.discount.limit` | ops_matrix_core | `models/ops_governance_limits.py` |
| Margin Rules | `ops.governance.margin.rule` | ops_matrix_core | `models/ops_governance_limits.py` |
| Price Authority | `ops.governance.price.authority` | ops_matrix_core | `models/ops_governance_limits.py` |
| Approval Workflow | `ops.approval.workflow` | ops_matrix_core | `models/ops_governance_limits.py` |
| Approval Workflow Step | `ops.approval.workflow.step` | ops_matrix_core | `models/ops_governance_limits.py` |
| Violation Report | `ops.governance.violation.report` (TransientModel) | ops_matrix_core | `models/ops_governance_violation_report.py` |

### 2.2 Governance Mixin (`ops.governance.mixin`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_governance_mixin.py`

Any model inheriting this mixin is subject to governance rule enforcement on CRUD operations.

**CRUD Overrides**:

```python
@api.model_create_multi
def create(vals_list):
    records = super().create(vals_list)
    records._enforce_governance_rules(records, 'on_create')
    return records

def write(vals):
    # Pre-write enforcement (simulates post-write state)
    self._enforce_governance_rules_pre_write(self, vals, 'on_write')
    return super().write(vals)

def unlink():
    self._enforce_governance_rules(self, 'on_unlink')
    return super().unlink()
```

**Method: `_enforce_governance_rules(records, trigger_type)`**
```
Logic:
  1. Admin bypass: if user has base.group_system or env.su:
     - Log to ops.security.audit (event_type='admin_bypass')
     - Return immediately (skip all rules)
  2. Find governance rules:
     - active=True, enabled=True
     - model_name matches record._name
     - trigger_type matches rule.trigger_event OR trigger_event='always'
  3. For each rule, call _apply_governance_rule(rule, trigger_type, record)
  4. Accumulate warnings, raise after processing all rules
```

**Method: `_enforce_governance_rules_pre_write(records, vals, trigger_type)`**
```
Purpose: Simulate the post-write state for condition evaluation
         without actually writing to the database.

Logic:
  1. For each record, create a SimulatedRecord:
     - Copy of current record
     - Apply vals on top (simulates what the record would look like)
  2. Evaluate governance rules against simulated state
  3. If violations found, raise BEFORE the write happens
```

**Inner Class: `SimulatedRecord`**
```
Purpose: Lightweight object mimicking a record with proposed changes applied.
Used in pre-write enforcement so governance rules can evaluate
the future state of the record without committing changes.
```

**Method: `_apply_governance_rule(rule, trigger_type, record)`**
```
Parameters:
  rule: ops.governance.rule record
  trigger_type: 'on_create' | 'on_write' | 'on_unlink'
  record: the target record (or SimulatedRecord)

Logic:
  1. Validate rule against record (rule.validate_record())
  2. If validation returns violation:
     a. action_type == 'block':
        - Raise UserError immediately
     b. action_type == 'warning':
        - Accumulate warning message (shown after all rules processed)
     c. action_type == 'require_approval':
        - FOUR-EYES PRINCIPLE CHECK:
          * Get creator: record.create_uid
          * If creator == current user:
            - Cannot self-approve
            - Find approvers from rule._find_approvers()
            - If approvers found -> create approval request + lock record
            - If NO approvers (Executive Deadlock):
              * Escalate to parent persona
              * If no parent -> log "Executive Deadlock" event
        - Create ops.approval.request
        - Set record.approval_locked = True
        - Set record.approval_request_id = new request
```

### 2.3 Governance Rule (`ops.governance.rule`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_governance_rule.py`
(1071 lines)

**Rule Types**:
| Type | Code | Purpose |
|------|------|---------|
| Matrix Validation | `matrix_validation` | Validate branch/BU dimensions |
| Discount Limit | `discount_limit` | Enforce per-role discount caps |
| Margin Protection | `margin_protection` | Enforce minimum profit margins |
| Price Override | `price_override` | Control price variance authority |
| Approval Workflow | `approval_workflow` | Multi-step approval chains |
| Notification | `notification` | Alert without blocking |
| Legacy | `legacy` | Backward compatibility |

**Trigger Types**:
| Trigger Event | Fires On |
|---------------|----------|
| `always` | Every create/write |
| `on_create` | Record creation only |
| `on_write` | Record modification only |
| `on_state_change` | State field changes only |

**Action Types**:
| Action | Effect |
|--------|--------|
| `block` | Raises UserError, prevents operation |
| `warning` | Shows warning, allows operation |
| `require_approval` | Locks record, creates approval request |

**Catalog Mode**:
Rules can be `active=True` but `enabled=False`. This means:
- Visible in the UI for configuration
- NOT enforced during CRUD operations
- Can be enabled per-company when ready

**Master Validation Method: `validate_record(record, trigger_type)`**
```
Dispatches to sub-validators based on rule_type:
  - matrix_validation -> _validate_matrix_dimensions(record)
  - discount_limit -> _validate_discount(record)
  - margin_protection -> _validate_margin(record)
  - price_override -> _validate_price_override(record)
  - approval_workflow -> _validate_approval_workflow(record)
  - notification -> _validate_notification(record)

Returns: dict with {violated: bool, message: str, severity: str, ...}
```

#### 2.3.1 Matrix Validation (`_validate_matrix_dimensions`)

Checks:
- Branch required: record must have `ops_branch_id` set
- BU required: record must have `ops_business_unit_id` set
- Allowed branches/BUs: record dimensions must be in allowed list
- Cross-validation: branch+BU combination must be valid

#### 2.3.2 Discount Validation (`_validate_discount`)

**Method: `_validate_discount(record)`**
```
Logic:
  1. Per-line check: iterate record.order_line (or equivalent)
     - Calculate discount_percent per line
     - Compare against user's discount limit
  2. Per-order check: calculate total order discount
  3. Get user's limit via _get_user_discount_limit()

Returns violation if any discount exceeds user's authority.
```

**Method: `_get_user_discount_limit(user, personas, record)`**
```
Parameters:
  user: res.users record
  personas: user's ops.persona records
  record: the order/document being validated

Logic:
  1. Search ops.governance.discount.limit matching user's personas or groups
  2. Apply scope restrictions:
     - Branch scope: limit only applies if record.ops_branch_id in allowed branches
     - BU scope: limit only applies if record.ops_business_unit_id in allowed BUs
     - Category scope: limit only applies for specific product categories
  3. Return maximum limit from all matching rules
```

#### 2.3.3 Margin Validation (`_validate_margin`)

**Method: `_validate_margin(record)`**
```
Logic:
  1. For each order line: calculate margin = (revenue - cost) / revenue
  2. Determine minimum margin via _get_minimum_margin()
  3. If margin < minimum -> violation

Returns: violation with actual margin, minimum required, and severity
```

**Method: `_get_minimum_margin(category, business_unit, branch)`**
```
Hierarchical lookup (most specific wins):
  1. Category + BU + Branch (most specific)
  2. Category + BU
  3. Category + Branch
  4. Category only
  5. Global default (fallback)

Source: ops.governance.margin.rule records
Each rule has warning_threshold (soft) and critical_threshold (hard).
```

#### 2.3.4 Price Override Validation (`_validate_price_override`)

**Method: `_validate_price_override(record)`**
```
Logic:
  1. For each line: calculate variance = (unit_price - list_price) / list_price * 100
  2. Determine user's price authority via ops.governance.price.authority
  3. Directional limits: separate authority for increases vs decreases
  4. If variance exceeds authority -> violation
```

#### 2.3.5 Approver Resolution (`_find_approvers`)

**Method: `_find_approvers(record, violation_type)`**
```
Parameters:
  record: the document with violation
  violation_type: 'discount' | 'margin' | 'price' | 'matrix' | etc.

Logic:
  1. Find personas with specific approval authority:
     - discount -> can_approve_discounts = True
     - margin -> can_approve_margin_exceptions = True
     - price -> can_approve_price_overrides = True
  2. Resolve persona users
  3. Apply branch/BU filtering (approver must be in same branch or higher)
  4. Escalation: 3-level persona-based hierarchy
     - Level 1: direct manager persona
     - Level 2: manager's manager persona
     - Level 3: CEO/CFO persona

Returns: res.users recordset of valid approvers
```

### 2.4 Supporting Models (`ops_governance_limits.py`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_governance_limits.py`

#### `ops.governance.discount.limit`

Per-role discount limits with scope restrictions.

| Field | Type | Description |
|-------|------|-------------|
| `persona_id` | Many2one (ops.persona) | Target persona |
| `group_id` | Many2one (res.groups) | Target security group |
| `max_discount` | Float | Maximum allowed discount (%) |
| `allowed_branch_ids` | Many2many (ops.branch) | Scope restriction |
| `allowed_bu_ids` | Many2many (ops.business.unit) | Scope restriction |
| `allowed_category_ids` | Many2many (product.category) | Scope restriction |

#### `ops.governance.margin.rule`

Category-specific margin rules.

| Field | Type | Description |
|-------|------|-------------|
| `category_id` | Many2one (product.category) | Product category |
| `business_unit_id` | Many2one (ops.business.unit) | BU dimension |
| `branch_id` | Many2one (ops.branch) | Branch dimension |
| `minimum_margin` | Float | Hard minimum (%) |
| `warning_threshold` | Float | Soft warning (%) |
| `critical_threshold` | Float | Critical alert (%) |

#### `ops.governance.price.authority`

Role-based price variance authority.

| Field | Type | Description |
|-------|------|-------------|
| `persona_id` | Many2one (ops.persona) | Target persona |
| `group_id` | Many2one (res.groups) | Target security group |
| `max_increase_percent` | Float | Max allowed price increase |
| `max_decrease_percent` | Float | Max allowed price decrease |
| `can_override_without_approval` | Boolean | Skip approval for this role |

#### `ops.approval.workflow`

Multi-step approval workflow definition.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Workflow name |
| `step_ids` | One2many (ops.approval.workflow.step) | Ordered steps |
| `parallel` | Boolean | Steps run in parallel (vs sequential) |
| `approval_mode` | Selection | unanimous / threshold |
| `approval_threshold` | Float | Required % for threshold mode |

#### `ops.approval.workflow.step`

Individual approval step.

| Field | Type | Description |
|-------|------|-------------|
| `workflow_id` | Many2one | Parent workflow |
| `sequence` | Integer | Step order |
| `approver_persona_ids` | Many2many | Persona-based approvers |
| `approver_group_ids` | Many2many | Group-based approvers |
| `specific_user_ids` | Many2many | Specific user approvers |
| `min_approvers` | Integer | Minimum required approvals |

### 2.5 Pre-defined Governance Rules

#### Catalog Rules (enabled=False by default)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_rule_templates.xml`

| # | Rule Name | Condition | Action |
|---|-----------|-----------|--------|
| 1 | High Value Order >$50K | `record.amount_total > 50000` | require_approval |
| 2 | Large Discount >20% | `any(l.discount > 20 for l in record.order_line)` | require_approval |
| 3 | Credit Limit Warning | `record.amount_total > record.partner_id.credit_limit * 0.9` | warning |
| 4 | PO >$50K | `record.amount_total > 50000` | require_approval |
| 5 | PO >$100K | `record.amount_total > 100000` | require_approval |
| 6 | Custom Payment Terms | Condition-based | warning |
| 7 | Stock Adjustment >100 units | Quantity threshold | require_approval |
| 8 | Credit Limit Change >$50K | `record.credit_limit > 50000` | require_approval |
| 9 | Cross-Branch Order Warning | Branch mismatch | warning |

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_templates.xml`

5 archived template rules (active=False):
- High-Value PO $10K+
- Geographic Sales Restriction (block action)
- Retail Discount Cap 20%
- BU Expense Lockdown TECH >$1K
- Mandatory Customer VAT for Retail

#### Demo/Extended Rules (active and enabled)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_templates_extended.xml`

**Active Governance Rules**:
| Rule | Type | Condition | Action |
|------|------|-----------|--------|
| Matrix Validation | matrix_validation | All sale.order | require_approval (on violation) |
| Retail Discount 15% | discount_limit | sale.order | require_approval |
| Coffee Discount 10% | discount_limit | sale.order (coffee category) | require_approval |
| Wholesale Discount 25% | discount_limit | sale.order (wholesale BU) | require_approval |
| Retail Margin 20% | margin_protection | sale.order (retail) | require_approval |
| Coffee Margin 35% | margin_protection | sale.order (coffee) | require_approval |
| Price Override 10% | price_override | sale.order | require_approval |
| Services Price 15% | price_override | sale.order (services) | require_approval |

**Discount Limits by Persona**:
| Persona | Max Discount | Scope |
|---------|-------------|-------|
| Sales Representative | 10% | All |
| Dubai Sales | 15% | Dubai branch |
| Doha Manager | 20% | Doha branch |
| Warehouse Manager | 20% | All |
| Coffee Doha | 12% | Doha + Coffee category |

**Margin Rules by Category**:
| Category | Min Margin | Warning | Critical |
|----------|-----------|---------|----------|
| Electronics | 25% | 30% | 25% |
| Furniture | 30% | 35% | 30% |
| Coffee | 40% | 45% | 40% |
| Luxury | 50% | 55% | 50% |
| Commodity | 10% | 15% | 10% |
| Services | 55% | 60% | 55% |

**Price Authorities**:
| Persona | Max Increase | Max Decrease | Override Without Approval |
|---------|-------------|-------------|--------------------------|
| Sales Representative | 5% | 5% | No |
| Doha Manager | 10% | 10% | Yes |
| Dubai Sales | 12% | 12% | No |

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_rule_three_way_match.xml`

Single rule: Three-Way Match Override requiring Purchase Manager approval.

### 2.6 Violation Report Wizard

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_governance_violation_report.py`

TransientModel `ops.governance.violation.report` for generating filtered violation reports.

**Filters**: date range, violation type, severity, model, branch, BU
**Output**: CSV export with full violation details

---

## 3. Segregation of Duties (SoD)

### 3.1 Architecture

| Component | Model | Module | File |
|-----------|-------|--------|------|
| SoD Rule | `ops.segregation.of.duties` | ops_matrix_core | `models/ops_segregation_of_duties.py` |
| SoD Log | `ops.segregation.of.duties.log` | ops_matrix_core | `models/ops_segregation_of_duties.py` |
| SoD Mixin | `ops.segregation.of.duties.mixin` (AbstractModel) | ops_matrix_core | `models/ops_segregation_of_duties_mixin.py` |
| Accounting SoD Extension | extends `ops.segregation.of.duties` | ops_matrix_accounting | `models/ops_sod_accounting.py` |

### 3.2 SoD Rule Model (`ops.segregation.of.duties`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_segregation_of_duties.py`

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Rule name |
| `model_name` | Char | Target model (e.g., 'sale.order') |
| `action_1` | Selection | First action: create/confirm/post/approve/reconcile |
| `action_2` | Selection | Second action: create/confirm/post/approve/reconcile |
| `threshold_amount` | Float | Minimum amount to trigger rule (0 = always) |
| `block_violation` | Boolean | True = block, False = warn + log |
| `active` | Boolean | True = visible in catalog |
| `enabled` | Boolean | True = enforced (default False = Catalog Mode) |
| `company_id` | Many2one | Company scope |

**Catalog Mode**: All default rules ship with `active=True, enabled=False`. They are visible for configuration but not enforced until explicitly enabled.

**Method: `_check_rule_applies(record, action)`**
```
Parameters:
  record: the document being acted upon
  action: str -- 'create', 'confirm', 'post', 'approve', 'reconcile'

Logic:
  1. Verify model_name matches record._name
  2. Verify action matches either action_1 or action_2
  3. Verify company_id matches (if set)
  4. If threshold_amount > 0:
     - Check record.amount_total (or equivalent) >= threshold
  5. Return True if rule applies
```

**Method: `_get_action_1_user(record)`**
```
Resolves who performed the first action:
  - 'create' -> record.create_uid
  - 'confirm' -> record.confirmed_by (or write_uid at confirm time)
  - 'post' -> record.posted_by (or write_uid at post time)
  - 'approve' -> record.approved_by
  - 'reconcile' -> record.reconciled_by
```

### 3.3 SoD Log (`ops.segregation.of.duties.log`)

Immutable violation log.

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | Many2one | Violated rule |
| `user_id` | Many2one | User who triggered violation |
| `action_1_user_id` | Many2one | User who did first action |
| `model_name` | Char | Document model |
| `res_id` | Integer | Document ID |
| `blocked` | Boolean | Whether operation was blocked |
| `company_id` | Many2one | Company context |

**Method: `get_violations_report()`**
Returns compliance reporting data for SoD violations.

### 3.4 SoD Mixin (`ops.segregation.of.duties.mixin`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_segregation_of_duties_mixin.py`

**Method: `_check_sod_violation(action)`**
```
Parameters:
  action: str -- the action being performed (e.g., 'confirm', 'post')

Logic:
  1. Admin bypass: base.group_system or env.su -> log + skip
  2. Find applicable SoD rules:
     - model_name = self._name
     - enabled = True
     - action_2 = action (current action is the second action)
  3. For each rule:
     a. Call rule._check_rule_applies(record, action)
     b. Get action_1_user via rule._get_action_1_user(record)
     c. If action_1_user == current user:
        - SoD VIOLATION DETECTED
        - Call _log_sod_violation(rule, action, action_1_user)
        - Call _notify_sod_violation(rule, action_1_user)
        - If rule.block_violation:
          * Raise UserError (operation blocked)
        - Else:
          * Log warning, allow operation to proceed
```

**Method: `_log_sod_violation(rule, action, action_1_user)`**
```
Creates ops.segregation.of.duties.log entry with:
  - rule_id, user_id (current), action_1_user_id
  - model_name, res_id, blocked flag
```

**Method: `_notify_sod_violation(rule, action_1_user)`**
```
Posts warning to record's chatter:
  "SoD Warning: Same user ({user}) performed both {action_1} and {action_2}"
```

### 3.5 Default SoD Rules

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_sod_default_rules.xml`

All rules ship as `enabled=False` (Catalog Mode):

| # | Rule Name | Model | Action Pair | Threshold | Block |
|---|-----------|-------|-------------|-----------|-------|
| 1 | Sales Order Create+Confirm | sale.order | create + confirm | $5,000 | True |
| 2 | Purchase Order Create+Confirm | purchase.order | create + confirm | $5,000 | True |
| 3 | Invoice Create+Post | account.move | create + post | $0 (always) | True |
| 4 | Payment Create+Post | account.payment | create + post | $2,000 | True |
| 5 | Inventory Adjustment Create+Approve | stock.picking | create + approve | $0 (always) | True |

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/data/ops_sod_bank_rules.xml`

| 6 | Bank Reconciliation Reconcile+Approve | bank.reconciliation | reconcile + approve | $0 | True |

### 3.6 Accounting SoD Extension

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_sod_accounting.py`

Extends the base SoD model to add:
- `bank.reconciliation` as a supported model
- `reconcile` as an additional action type

---

## 4. Three-Way Matching

### 4.1 Model: `ops.three.way.match`

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_three_way_match.py`

**Purpose**: Validates that purchase orders, goods receipts, and vendor invoices agree before allowing payment.

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `purchase_order_id` | Many2one (purchase.order) | Source PO |
| `purchase_line_id` | Many2one (purchase.order.line) | Source PO line |
| `ordered_qty` | Float | Quantity ordered (from PO) |
| `received_qty` | Float | Quantity received (computed from stock.move) |
| `billed_qty` | Float | Quantity billed (computed from account.move.line) |
| `match_state` | Selection | Computed match status |
| `company_id` | Many2one | Company |

**Match States**:
| State | Condition |
|-------|-----------|
| `matched` | All three quantities agree (within tolerance) |
| `under_billed` | Billed < Received (normal pre-invoice state) |
| `over_billed` | Billed > Received + tolerance (**blocks payment**) |
| `no_receipt` | Received = 0 (**blocks payment**) |
| `partial_receipt` | 0 < Received < Ordered |

**Computed Methods**:

**`_compute_received_qty()`**
```
Sums quantities from done stock.move records linked to the PO line.
Domain: move_type='incoming', state='done', purchase_line_id match
```

**`_compute_billed_qty()`**
```
Sums quantities from non-cancelled invoice lines linked to the PO line.
Domain: account.move.line, move_id.state != 'cancel', purchase_line_id match
```

**`_compute_match_state()`**
```
Logic:
  tolerance = company.three_way_match_tolerance (percentage, e.g., 5.0)

  if received_qty == 0:
    state = 'no_receipt' -> BLOCKS PAYMENT
  elif billed_qty > received_qty * (1 + tolerance/100):
    state = 'over_billed' -> BLOCKS PAYMENT
  elif abs(ordered_qty - received_qty) < tolerance AND abs(received_qty - billed_qty) < tolerance:
    state = 'matched'
  elif billed_qty < received_qty:
    state = 'under_billed'
  else:
    state = 'partial_receipt'
```

**Governance Integration**: The three-way match override governance rule (from `ops_governance_rule_three_way_match.xml`) requires Purchase Manager approval to override a blocking three-way match state.

---

## 5. SLA Tracking

### 5.1 Architecture

| Component | Model | Module | File |
|-----------|-------|--------|------|
| SLA Template | `ops.sla.template` | ops_matrix_core | `models/ops_sla_template.py` |
| SLA Instance | `ops.sla.instance` | ops_matrix_core | `models/ops_sla_instance.py` |
| SLA Mixin | `ops.sla.mixin` (AbstractModel) | ops_matrix_core | `models/ops_sla_mixin.py` |

### 5.2 SLA Template (`ops.sla.template`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_sla_template.py`

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Template name |
| `model_id` | Many2one (ir.model) | Applicable model |
| `calendar_id` | Many2one (resource.calendar) | Working hours calendar |
| `target_duration` | Float | Target hours (in working hours) |
| `enabled` | Boolean | Whether template is active |

**Method: `_compute_deadline(start_dt)`**
```
Parameters:
  start_dt: datetime -- when the SLA started

Logic:
  Uses calendar_id.plan_hours(target_duration, start_dt)
  This calculates the deadline in business hours using the resource calendar.

Returns: datetime -- the SLA deadline
```

### 5.3 SLA Instance (`ops.sla.instance`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_sla_instance.py`

**States**: `running` -> `completed` | `failed` | `escalated`

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `template_id` | Many2one (ops.sla.template) | Source template |
| `model_name` | Char | Target model |
| `res_id` | Integer | Target record ID |
| `start_date` | Datetime | When SLA started |
| `deadline` | Datetime | Computed SLA deadline |
| `completion_date` | Datetime | When completed (if applicable) |
| `state` | Selection | running/completed/failed/escalated |
| `escalation_level` | Integer | 0-3 escalation tier |

**Computed Status** (separate from state):
| Status | Condition |
|--------|-----------|
| `running` | < 75% of time elapsed |
| `warning` | 75-90% of time elapsed |
| `critical` | > 90% of time elapsed |
| `violated` | Past deadline |

**Cron: `_cron_check_escalations()`**
```
Frequency: Every 15 minutes

Logic:
  1. Find running SLA instances past deadline -> mark as 'failed'
  2. Find running SLA instances within 1 hour of deadline:
     - If not already escalated -> trigger escalation
  3. For each needing escalation -> call action_escalate()
```

**Method: `action_escalate()`**
```
Logic:
  Escalation Level 0 -> 1: Notify direct manager
  Escalation Level 1 -> 2: Notify manager's manager
  Escalation Level 2 -> 3: Notify CEO/CFO persona

  1. Get current assignee's persona
  2. Look up parent persona (parent_id on ops.persona)
  3. Resolve users with parent persona
  4. Create activity for escalation target
  5. Increment escalation_level
  6. Post message to source record
```

**Method: `action_complete()`**
```
Logic:
  1. Set completion_date = now
  2. If completion_date <= deadline:
     - state = 'completed'
     - Post "SLA met" message
  3. If completion_date > deadline:
     - state = 'failed'
     - Post "SLA missed" message with duration
```

### 5.4 SLA Mixin (`ops.sla.mixin`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_sla_mixin.py`

**Fields**:
- `sla_instance_ids` (One2many -> `ops.sla.instance`) -- linked SLA instances

**Method: `_initiate_sla(template_xml_id)`**
```
Parameters:
  template_xml_id: str -- XML ID of the SLA template (e.g., 'ops_matrix_core.sla_platinum')

Logic:
  1. Resolve template from XML ID
  2. If template enabled:
     - Compute deadline via template._compute_deadline(now)
     - Create ops.sla.instance linked to this record
  3. Return the new SLA instance
```

### 5.5 Default SLA Templates

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/data/ops_sla_templates.xml`

All templates ship as `enabled=False`:

| # | Template | Target Duration | Calendar |
|---|----------|----------------|----------|
| 1 | Platinum Support | 4 hours | Standard working hours |
| 2 | Gold Support | 24 hours | Standard working hours |
| 3 | IT Critical Issue | 8 hours | Standard working hours |
| 4 | Sales Inquiry | 24 hours | Standard working hours |

---

## 6. Audit Logging

### 6.1 Architecture

| Component | Model | Module | File |
|-----------|-------|--------|------|
| Corporate Audit Log | `ops.corporate.audit.log` | ops_matrix_core | `models/ops_corporate_audit_log.py` |
| API Audit Log | `ops.audit.log` | ops_matrix_core | `models/ops_audit_log.py` |

### 6.2 Corporate Audit Log (`ops.corporate.audit.log`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_corporate_audit_log.py`

**Immutability Enforcement**:
- `write()`: Only allows review fields (reviewed_by, review_date, review_notes) for non-system users. Raises UserError for other fields.
- `unlink()`: Blocked entirely for non-system users. Raises UserError.

**Event Types** (30+ categories):

| Category | Event Types |
|----------|-------------|
| Authentication | login, logout, login_failed, password_change, session_timeout |
| CRUD | record_create, record_write, record_delete, record_archive |
| Workflow | state_change, approval_request, approval_granted, approval_rejected, approval_escalated |
| Financial | journal_entry_posted, payment_created, payment_reconciled, budget_exceeded, credit_limit_change |
| Security | role_change, permission_change, sod_violation, admin_bypass, export_data |
| Configuration | settings_change, rule_change, template_change |

**Central Logging Method: `log_event()`**
```python
@api.model
def log_event(event_type, description, model_name=None, res_id=None,
              old_values=None, new_values=None, severity='info'):
```

Captures automatically:
- `user_id`: current user
- `session_id`: current session
- `ip_address`: from request (if available)
- `ops_branch_id`: from user's current branch context
- `persona_id`: from user's active persona
- `timestamp`: now (UTC)
- `company_id`: current company

**Convenience Methods**:
| Method | Shortcut For |
|--------|-------------|
| `log_crud(action, model, record, old_vals, new_vals)` | CRUD events |
| `log_authentication(event, user, details)` | Auth events |
| `log_financial_change(event, model, record, amount, details)` | Financial events |
| `log_approval(event, request, details)` | Approval events |
| `log_export(model, record_count, format, user)` | Data export events |

**Compliance Categories**:
| Category | Examples |
|----------|---------|
| SOX | Financial changes, approval workflows, journal entries |
| GDPR | Data exports, permission changes, record deletions |
| ISO 27001 | Security events, access control, audit trail |
| Financial | All monetary transactions, budget changes |
| Operational | Workflow changes, configuration updates |

**Cleanup Method: `cleanup_old_logs()`**
```
Logic:
  - Compliance-critical logs (SOX, GDPR, financial): NEVER auto-deleted
  - Debug/info severity logs: Deleted after 365 days
  - Warning severity logs: Kept for 730 days (2 years)
```

### 6.3 API Audit Log (`ops.audit.log`)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_core/models/ops_audit_log.py`

**Purpose**: Logs REST API requests made through the OPS API endpoints.

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | Char | API endpoint path |
| `method` | Selection | GET/POST/PUT/DELETE |
| `status_code` | Integer | HTTP response code |
| `response_time_ms` | Float | Response time in milliseconds |
| `api_key_id` | Many2one (ops.api.key) | Which API key was used |
| `user_id` | Many2one | Authenticated user |
| `persona_id` | Many2one | User's active persona |
| `request_body` | Text | Sanitized request payload |
| `response_body` | Text | Sanitized response payload |
| `ip_address` | Char | Client IP |

**Immutability**: Same pattern as corporate audit log -- non-system users cannot write or delete.

**Method: `log_api_request()`**
```python
@api.model
def log_api_request(endpoint, method, status_code, response_time_ms,
                    api_key=None, request_body=None, response_body=None):
```

**Cleanup**: Automatic via cron after 90 days.

---

## 7. Accounting Workflows

### 7.1 Budget Control

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_budget.py`

#### `ops.budget`

**States**: `draft` -> `confirmed` -> `done` | `cancelled`

**Transitions**:
| Action | Method | From | To |
|--------|--------|------|-----|
| Confirm | `action_confirm()` | draft | confirmed |
| Close | `action_done()` | confirmed | done |
| Cancel | `action_cancel()` | any | cancelled |
| Reset | `action_draft()` | any | draft |

**Constraints**:
- Unique per branch + BU + date range (SQL constraint)
- End date must be after start date
- Overlapping date ranges for same branch/BU are blocked

**Computed Fields**:
| Field | Formula |
|-------|---------|
| `total_planned` | sum(line_ids.planned_amount) |
| `total_practical` | sum(line_ids.practical_amount) -- from posted AML |
| `total_committed` | sum(line_ids.committed_amount) -- from confirmed PO lines |
| `available_balance` | total_planned - total_practical - total_committed |
| `variance` | Alias for available_balance |
| `budget_utilization` | (practical + committed) / planned |
| `is_over_budget` | available_balance < 0 |

**Method: `check_budget_availability()`**
```python
@api.model
def check_budget_availability(branch_id=None, business_unit_id=None,
                              amount=0.0, date=None, account_id=None,
                              ops_branch_id=None, ops_business_unit_id=None):
```
```
Parameters:
  branch_id / ops_branch_id: branch to check
  business_unit_id / ops_business_unit_id: BU to check
  amount: amount of planned expense
  date: check date (defaults to today)
  account_id: specific expense account (optional)

Returns: dict with:
  available: bool
  remaining: float
  over_amount: float
  budget_id: int
  budget_name: str
  message: str

Logic:
  1. Find confirmed budget matching branch/BU/date
  2. If account_id specified -> check specific budget line
  3. Otherwise -> check overall budget balance
  4. Return availability result
```

#### `ops.budget.line`

**Computed Fields**:

**`_compute_practical_amount()`** -- Actual spend from posted journal entries
```
Source: account.move.line (sudo)
Filter:
  - account_id matches budget line
  - move_id.state = 'posted'
  - move_id.move_type in ('in_invoice', 'in_refund', 'entry')
  - date within budget period
  - company_id, ops_branch_id, ops_business_unit_id match

Formula: SUM(debit - credit) per account
```

**`_compute_committed_amount()`** -- Committed from confirmed PO lines
```
Source: purchase.order.line (ORM search)
Filter:
  - order_id.state in ('purchase', 'done')
  - order_id dimensions match (branch, BU, company, date range)

Formula per account:
  For each PO line where product's expense account matches:
    uninvoiced = price_subtotal - (qty_invoiced * price_unit)
    committed[account_id] += uninvoiced
```

### 7.2 Asset Management

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_asset.py`

#### `ops.asset`

**States**: `draft` -> `running` -> `paused` | `sold` | `disposed`

**Transitions**:
| Action | Method | From | To |
|--------|--------|------|-----|
| Validate/Start | `action_set_running()` | draft | running |
| Pause | `action_pause()` | running | paused |
| Resume | `action_resume()` | paused | running |
| Sell | `action_sell()` | running | sold |
| Dispose | `action_dispose()` | running | disposed |

**Depreciation Methods**:
| Method | Code | Description |
|--------|------|-------------|
| Straight Line | `straight_line` | Equal amounts each period |
| Declining Balance | `declining_balance` | Fixed rate on remaining value |
| Degressive then Linear | `degressive_then_linear` | Declining until linear is higher, then switches |

**Method: `generate_depreciation_schedule()`**
```
Logic:
  1. Calculate depreciable amount = gross_value - salvage_value
  2. Based on method:
     - straight_line: amount = depreciable / total_periods
     - declining_balance: rate = 1 - (salvage/gross)^(1/years)
     - degressive_then_linear: start with declining, switch when linear > declining
  3. Prorata temporis: if not starting on period boundary,
     first period is proportional
  4. Create ops.asset.depreciation records for each period
```

**IAS 36 Impairment**:
| Field | Type | Description |
|-------|------|-------------|
| `impaired` | Boolean | Whether asset is impaired |
| `recoverable_amount` | Monetary | Fair value or value in use |
| `impairment_loss` | Monetary | Carrying amount - recoverable amount |

**Constraint**: `ops_branch_id` is **required** (zero-trust security policy).

### 7.3 Post-Dated Cheques (PDC)

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_pdc.py`

#### `ops.pdc.receivable` (Customer Cheques)

**States**: `draft` -> `deposited` -> `cleared` | `bounced` -> `cancelled`

**Journal Entries per Transition**:

| Transition | Debit | Credit |
|------------|-------|--------|
| Deposit (`action_deposit`) | PDC Clearing Account | Accounts Receivable |
| Clear (`action_clear`) | Bank Account | PDC Clearing Account |
| Bounce (`action_bounce`) | Accounts Receivable | PDC Clearing Account |
| Cancel (`action_cancel`) | Reverses deposit entry | |

**Key Fields**: `partner_id`, `amount`, `cheque_date`, `cheque_number`, `bank_account_id`, `journal_id`, `pdc_clearing_account_id`, `ops_branch_id`

#### `ops.pdc.payable` (Vendor Cheques)

**States**: `draft` -> `issued` -> `presented` -> `cleared` | `cancelled`

**Journal Entries per Transition**:

| Transition | Debit | Credit |
|------------|-------|--------|
| Issue (`action_issue`) | Accounts Payable | PDC Clearing Account |
| Clear (`action_clear`) | PDC Clearing Account | Bank Account |
| Cancel (`action_cancel`) | Reverses issue entry | |

### 7.4 Recurring Entries

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_recurring.py`

#### `ops.recurring.template`

**States**: `draft` -> `active` -> `paused` -> `done`

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `period_type` | Selection | days/weeks/months/years |
| `period_interval` | Integer | Every N periods |
| `date_start` | Date | First occurrence |
| `date_end` | Date | Last occurrence (optional) |
| `auto_post` | Boolean | Auto-post generated entries |
| `auto_reverse` | Boolean | Auto-reverse after posting |
| `require_approval` | Boolean | Require approval before posting |
| `journal_id` | Many2one | Target journal |
| `line_ids` | One2many | Template lines (account, debit, credit) |

#### `ops.recurring.entry`

**States**: `draft` -> `pending_approval` -> `approved` -> `posted` -> `reversed` | `cancelled`

**Transitions**:
| Action | From | To | Condition |
|--------|------|-----|-----------|
| Submit for approval | draft | pending_approval | require_approval=True |
| Approve | pending_approval | approved | Approver action |
| Auto-post | draft/approved | posted | auto_post=True |
| Post | approved | posted | Manual action |
| Reverse | posted | reversed | auto_reverse or manual |
| Cancel | draft/pending | cancelled | Manual action |

**Cron Jobs**:
| Cron | Method | Frequency |
|------|--------|-----------|
| Generate entries | `cron_generate_recurring_entries()` | Daily |
| Process reversals | `cron_process_auto_reversals()` | Daily |

**`cron_generate_recurring_entries()` Logic**:
```
1. Find active templates where next_date <= today
2. For each template:
   a. Create ops.recurring.entry from template lines
   b. If auto_post and not require_approval:
      - Create account.move and post immediately
   c. If require_approval:
      - Set state = pending_approval
   d. Advance next_date by period_interval * period_type
   e. If next_date > date_end: set template state = done
```

### 7.5 Customer Follow-up

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_followup.py`

#### Models

| Model | Description |
|-------|-------------|
| `ops.followup` | Company-level follow-up configuration |
| `ops.followup.line` | Escalation level definition |
| `ops.partner.followup` | Per-partner follow-up tracking |
| `ops.partner.followup.history` | Action history log |
| `ops.credit.override.wizard` | Credit override request wizard |

#### Follow-up Escalation Levels (`ops.followup.line`)

Each level defines:
| Field | Type | Description |
|-------|------|-------------|
| `delay` | Integer | Days overdue to trigger this level |
| `send_email` | Boolean | Send email notification |
| `email_template_id` | Many2one | Email template to use |
| `send_letter` | Boolean | Generate PDF letter |
| `manual_action` | Boolean | Requires manual intervention |
| `create_activity` | Boolean | Create Odoo activity |
| `block_credit` | Boolean | Block new sales orders |

#### Partner Follow-up States

**States**: `draft` -> `active` -> `resolved` | `blocked`

**Computed Fields**:
| Field | Source | Description |
|-------|--------|-------------|
| `max_overdue_days` | Posted out_invoices past due | Days since oldest overdue invoice |
| `total_overdue_amount` | sum(amount_residual) of overdue invoices | Total overdue balance |
| `total_balance` | sum(amount_residual) of all unpaid invoices | Total outstanding |
| `overdue_invoice_count` | count of overdue invoices | Number of overdue invoices |
| `next_followup_date` | Based on current level + delay differential | When next action is due |

**Method: `action_send_followup()`**
```
Logic:
  1. Get current follow-up level
  2. For each configured action on the level:
     a. Send email (if send_email + template configured)
     b. Create activity (if create_activity + type configured)
     c. Apply credit block (if block_credit AND no credit_override)
  3. Create ops.partner.followup.history record
  4. Update last_followup_date and last_followup_level_id
  5. Advance to next level (next higher sequence)
  6. Post summary to chatter
```

#### Credit Override System

**Fields on `ops.partner.followup`**:
| Field | Type | Description |
|-------|------|-------------|
| `credit_blocked` | Boolean | Whether credit is currently blocked |
| `credit_override` | Boolean | Whether override is active |
| `credit_override_by` | Many2one (res.users) | Who approved the override |
| `credit_override_date` | Datetime | When override was approved |
| `credit_override_reason` | Text | Justification |
| `credit_override_expiry` | Date | Auto-revoke date |

**Override Flow**:
```
1. action_request_credit_override() -> opens wizard
2. Wizard creates activity for account.group_account_manager users
3. Manager calls action_approve_credit_override():
   - Sets credit_override=True
   - Records approver and timestamp
   - Changes state to 'active'
4. Override can be revoked via action_revoke_credit_override()
5. Expired overrides auto-revoked by cron_process_followups()
```

**Cron: `cron_process_followups()`**
```
Logic:
  1. Find all partners with overdue invoices
  2. For each partner:
     a. Get or create ops.partner.followup record
     b. Determine appropriate level based on max_overdue_days
     c. If auto_send_email enabled and level changed -> send followup
  3. Find expired credit overrides -> auto-revoke
```

#### res.partner Extension

Adds computed fields to `res.partner`:
- `followup_status_id` -> link to ops.partner.followup
- `credit_blocked` -> computed from followup status (blocked AND NOT overridden)
- `overdue_amount` -> from followup status

### 7.6 IFRS 16 Lease Accounting

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_lease.py`

#### Models

| Model | Description |
|-------|-------------|
| `ops.lease` | Main lease agreement |
| `ops.lease.payment.schedule` | Amortization schedule lines |
| `ops.lease.depreciation` | ROU asset depreciation schedule |

#### Lease States

**States**: `draft` -> `active` -> `terminated` | `cancelled`

**Transitions**:
| Action | Method | From | To | Creates JE |
|--------|--------|------|-----|------------|
| Generate Schedules | `action_generate_schedules()` | draft | draft (stays) | No |
| Activate | `action_activate()` | draft | active | Yes (initial recognition) |
| Terminate | `action_terminate()` | active | terminated | No |
| Cancel | `action_cancel()` | draft only | cancelled | No |

**Cannot cancel active lease** -- must terminate instead.

#### Financial Calculations

**Present Value Calculation (`_compute_lease_values`)**:
```
Input: payment_amount, frequency, lease_term_months, discount_rate, payment_timing

Rates by frequency:
  monthly: rate = discount_rate / 100 / 12
  quarterly: rate = discount_rate / 100 / 4
  annually: rate = discount_rate / 100

PV factor = (1 - (1 + rate)^(-n_payments)) / rate
If payment_timing == 'beginning': PV factor *= (1 + rate)  (annuity-due)

lease_liability = payment_amount * PV_factor
rou_asset_value = lease_liability + initial_direct_costs
```

**Current/Non-Current Split (`_compute_current_liability`)**:
```
current_liability = sum(principal_amount) for unpaid payments due within 1 year
non_current_liability = lease_liability - current_liability
```

#### Journal Entries

**Initial Recognition** (on activation):
| Debit | Credit |
|-------|--------|
| ROU Asset Account: rou_asset_value | Lease Liability Account: lease_liability |
| | (If initial_direct_costs > 0: additional Cr to payable account) |

**Lease Payment** (per schedule line):
| Debit | Credit |
|-------|--------|
| Lease Liability: principal_amount | Lessor Payable: payment_amount |
| Interest Expense: interest_amount | |

**ROU Depreciation** (per depreciation line):
| Debit | Credit |
|-------|--------|
| Depreciation Expense: amount | Accumulated Depreciation: amount |

**Payment Schedule Generation (`_generate_payment_schedule`)**:
```
For each period until end_date:
  interest = balance * periodic_rate
  principal = payment_amount - interest
  balance -= principal
  Create schedule line with interest/principal split
```

**Depreciation Schedule (`_generate_depreciation_schedule`)**:
```
Method: Straight-line over lease term
monthly_depreciation = rou_asset_value / lease_term_months
Last month: adjusted to ensure total = rou_asset_value (no rounding drift)
```

### 7.7 Period Close

**File**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_period_close_wizard.py`

#### Wizard: `ops.period.close.wizard`

**Wizard Steps**: `overview` -> `checklist` -> `confirm`

**Navigation Flow**:
```
1. Overview: Shows period info, checklist progress
   - If pending items > 0 -> next goes to 'checklist'
   - If all done -> next goes to 'confirm'

2. Checklist: Shows all ops.period.close.checklist items
   - Can bulk mark all as done via action_mark_all_done()
   - Next goes to 'confirm'

3. Confirm: Choose lock type and execute
```

**Lock Options**:
| Lock Type | Effect | Checklist Requirement |
|-----------|--------|----------------------|
| `soft_lock` | Warning only -- users can still post | None |
| `hard_lock` | Blocks all posting in the period | 100% checklist completion required |

**Method: `action_close_period()`**
```
Logic:
  1. Post close notes to period (if provided)
  2. If soft_lock -> call period_id.action_soft_lock()
  3. If hard_lock:
     a. Verify checklist_progress == 100%
     b. If not 100% -> raise UserError
     c. Call period_id.action_hard_lock()
  4. Return success notification
```

---

## 8. State Machines

### 8.1 Complete State Machine Catalog

| Model | States | Initial |
|-------|--------|---------|
| `ops.approval.request` | pending -> approved / rejected / cancelled | pending |
| `ops.budget` | draft -> confirmed -> done / cancelled | draft |
| `ops.asset` | draft -> running -> paused / sold / disposed | draft |
| `ops.pdc.receivable` | draft -> deposited -> cleared / bounced -> cancelled | draft |
| `ops.pdc.payable` | draft -> issued -> presented -> cleared / cancelled | draft |
| `ops.recurring.template` | draft -> active -> paused -> done | draft |
| `ops.recurring.entry` | draft -> pending_approval -> approved -> posted -> reversed / cancelled | draft |
| `ops.partner.followup` | draft -> active -> resolved / blocked | draft |
| `ops.lease` | draft -> active -> terminated / cancelled | draft |
| `ops.lease.payment.schedule` | pending -> paid | pending |
| `ops.lease.depreciation` | draft -> posted | draft |
| `ops.sla.instance` | running -> completed / failed / escalated | running |
| `ops.fiscal.period` (via wizard) | open -> soft_locked -> hard_locked | open |

### 8.2 State Transition Diagrams

#### Approval Request
```
pending ──[approve]──> approved
   │
   ├──[reject]──> rejected
   │
   └──[recall]──> cancelled
```

#### PDC Receivable
```
draft ──[deposit]──> deposited ──[clear]──> cleared
                         │
                         └──[bounce]──> bounced
                                          │
                         draft <──[cancel]─┘
```

#### PDC Payable
```
draft ──[issue]──> issued ──[present]──> presented ──[clear]──> cleared
                      │
                      └──[cancel]──> cancelled
```

#### Recurring Entry
```
draft ──[submit]──> pending_approval ──[approve]──> approved ──[post]──> posted ──[reverse]──> reversed
  │                        │                                                │
  └──[auto_post]──> posted │                                                └──[cancel]──> cancelled
                           └──[reject]──> cancelled
```

#### Lease
```
draft ──[activate]──> active ──[terminate]──> terminated
  │
  └──[cancel]──> cancelled
```
Note: Cannot cancel an active lease; must terminate.

#### SLA Instance
```
running ──[complete on time]──> completed
   │
   ├──[deadline passed]──> failed
   │
   └──[escalate]──> escalated ──[complete]──> completed/failed
```

---

## 9. Cross-Cutting Concerns

### 9.1 Admin Bypass Pattern

**Applies to**: Governance rules, SoD enforcement, Approval locks

**Pattern**:
```python
if self.env.user.has_group('base.group_system') or self.env.su:
    # Log the bypass to ops.security.audit
    self.env['ops.security.audit'].sudo().log_event(
        event_type='admin_bypass',
        description='...',
        model_name=self._name,
        res_id=record.id
    )
    return  # Skip enforcement
```

**Key Point**: Admin bypasses are ALWAYS logged. The system never silently skips controls.

### 9.2 Four-Eyes Principle

**Implemented in**: `ops.governance.mixin._apply_governance_rule()` when `action_type='require_approval'`

**Logic**:
```
1. If record.create_uid == current_user:
   -> Cannot self-approve, must find another approver
2. Find approvers via rule._find_approvers()
3. If approvers found:
   -> Create approval request, lock record
4. If NO approvers found ("Executive Deadlock"):
   -> Attempt escalation to parent persona
   -> If no parent persona exists:
      -> Log "Executive Deadlock" event
      -> Operation may be blocked entirely
```

### 9.3 Persona-Based Escalation

**Used in**: Approval requests, SLA instances, Governance violations

**Escalation Chain** (3 levels max):
```
Level 0: Direct persona (initial approver)
Level 1: Parent persona (parent_id on ops.persona)
Level 2: Parent's parent persona
Level 3: CEO/CFO persona (top of hierarchy)
```

**Timeout-Based**: Each level has configurable timeout hours. When exceeded, auto-escalation occurs via cron job.

### 9.4 Branch Isolation

**Applies to**: All transactional models

**Pattern**: Every model with financial data has `ops_branch_id` field. Record rules ensure:
```xml
<record id="rule_branch_isolation" model="ir.rule">
    <field name="domain_force">[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]</field>
</record>
```

Users can only see records in their allowed branches.

### 9.5 IT Admin Blindness

**Applies to**: 24 sensitive models (17 core + 7 accounting)

**Pattern**: IT Admin group (`group_ops_it_admin`) has record rule `[(0, '=', 1)]` which matches zero records, effectively making all data invisible.

**Core blocked models**: sale.order, purchase.order, account.move, account.payment, stock.picking, stock.move, stock.quant, product.pricelist, account.analytic.line, etc.

**Accounting blocked models**: ops.pdc.receivable, ops.pdc.payable, ops.budget, ops.budget.line, ops.asset, ops.asset.category, ops.asset.depreciation

### 9.6 Chatter Integration

Every workflow action posts to the source record's chatter via `message_post()`:
- Approval requests: creation, approval, rejection, recall, escalation
- SoD violations: warning messages
- Follow-up actions: email sent, activity created, credit blocked
- Period close: lock applied, notes
- Lease: activation, payment recording, depreciation posting
- Asset: state changes, depreciation, impairment

### 9.7 Cron Job Inventory

| Cron | Model | Frequency | Purpose |
|------|-------|-----------|---------|
| Escalate overdue approvals | ops.approval.request | Periodic | Auto-escalate past timeout |
| Send approval reminders | ops.approval.request | Periodic | Remind after 24h |
| Check SLA escalations | ops.sla.instance | Every 15 min | Detect approaching/past deadlines |
| Generate recurring entries | ops.recurring.template | Daily | Create scheduled entries |
| Process auto-reversals | ops.recurring.entry | Daily | Reverse flagged entries |
| Process follow-ups | ops.partner.followup | Periodic | Auto-send follow-ups, expire overrides |
| Cleanup corporate audit logs | ops.corporate.audit.log | Periodic | Remove old non-critical logs |
| Cleanup API audit logs | ops.audit.log | Periodic | Remove logs > 90 days |

---

## Appendix A: File Index

| File | Models Defined |
|------|---------------|
| `ops_matrix_core/models/ops_approval_mixin.py` | ops.approval.mixin |
| `ops_matrix_core/models/ops_approval_request.py` | ops.approval.request |
| `ops_matrix_core/models/ops_approval_rule.py` | ops.approval.rule |
| `ops_matrix_core/models/ops_approval_dashboard.py` | ops.approval.dashboard |
| `ops_matrix_core/wizard/ops_approval_recall_wizard.py` | ops.approval.recall.wizard |
| `ops_matrix_core/wizard/ops_approval_reject_wizard.py` | ops.approval.reject.wizard |
| `ops_matrix_core/models/ops_governance_mixin.py` | ops.governance.mixin |
| `ops_matrix_core/models/ops_governance_rule.py` | ops.governance.rule |
| `ops_matrix_core/models/ops_governance_limits.py` | ops.governance.discount.limit, ops.governance.margin.rule, ops.governance.price.authority, ops.approval.workflow, ops.approval.workflow.step |
| `ops_matrix_core/models/ops_governance_violation_report.py` | ops.governance.violation.report |
| `ops_matrix_core/models/ops_segregation_of_duties.py` | ops.segregation.of.duties, ops.segregation.of.duties.log |
| `ops_matrix_core/models/ops_segregation_of_duties_mixin.py` | ops.segregation.of.duties.mixin |
| `ops_matrix_core/models/ops_three_way_match.py` | ops.three.way.match |
| `ops_matrix_core/models/ops_sla_template.py` | ops.sla.template |
| `ops_matrix_core/models/ops_sla_instance.py` | ops.sla.instance |
| `ops_matrix_core/models/ops_sla_mixin.py` | ops.sla.mixin |
| `ops_matrix_core/models/ops_corporate_audit_log.py` | ops.corporate.audit.log |
| `ops_matrix_core/models/ops_audit_log.py` | ops.audit.log |
| `ops_matrix_accounting/models/ops_budget.py` | ops.budget, ops.budget.line |
| `ops_matrix_accounting/models/ops_asset.py` | ops.asset |
| `ops_matrix_accounting/models/ops_pdc.py` | ops.pdc.receivable, ops.pdc.payable |
| `ops_matrix_accounting/models/ops_recurring.py` | ops.recurring.template, ops.recurring.entry |
| `ops_matrix_accounting/models/ops_followup.py` | ops.followup, ops.followup.line, ops.partner.followup, ops.partner.followup.history, ops.credit.override.wizard |
| `ops_matrix_accounting/models/ops_lease.py` | ops.lease, ops.lease.payment.schedule, ops.lease.depreciation |
| `ops_matrix_accounting/wizard/ops_period_close_wizard.py` | ops.period.close.wizard |
| `ops_matrix_accounting/models/ops_sod_accounting.py` | extends ops.segregation.of.duties |
| `ops_matrix_core/data/ops_governance_rule_templates.xml` | 9 catalog governance rules |
| `ops_matrix_core/data/ops_governance_templates.xml` | 5 archived template rules |
| `ops_matrix_core/data/ops_governance_templates_extended.xml` | 8 active rules + limits + margins + authorities |
| `ops_matrix_core/data/ops_governance_rule_three_way_match.xml` | Three-way match override rule |
| `ops_matrix_core/data/ops_sod_default_rules.xml` | 5 default SoD rules |
| `ops_matrix_accounting/data/ops_sod_bank_rules.xml` | 1 bank reconciliation SoD rule |
| `ops_matrix_core/data/ops_sla_templates.xml` | 4 SLA templates |

---

## Appendix B: Model Relationship Map

```
ops.governance.rule
  |-- enforced by --> ops.governance.mixin (on CRUD)
  |-- creates --> ops.approval.request (when action=require_approval)
  |-- references --> ops.governance.discount.limit
  |-- references --> ops.governance.margin.rule
  |-- references --> ops.governance.price.authority
  |-- defines --> ops.approval.workflow (multi-step)
  |       |-- contains --> ops.approval.workflow.step

ops.approval.request
  |-- locks --> any model with ops.approval.mixin
  |-- resolved by --> ops.approval.recall.wizard (cancel)
  |                    ops.approval.reject.wizard (reject)
  |-- tracked by --> ops.approval.dashboard (SQL view)
  |-- monitored by --> ops.sla.instance (if SLA template attached)

ops.segregation.of.duties
  |-- enforced by --> ops.segregation.of.duties.mixin
  |-- logs to --> ops.segregation.of.duties.log

ops.three.way.match
  |-- reads from --> purchase.order.line
  |-- reads from --> stock.move (received qty)
  |-- reads from --> account.move.line (billed qty)
  |-- governed by --> ops.governance.rule (override rule)

ops.sla.template
  |-- instantiated as --> ops.sla.instance
  |-- attached via --> ops.sla.mixin

ops.corporate.audit.log <-- written by all enforcement points
ops.audit.log <-- written by API controllers
```
