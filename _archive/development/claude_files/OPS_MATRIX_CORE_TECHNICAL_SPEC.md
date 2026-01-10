# OPS Matrix Core - Technical Specification

## Module: OPS Matrix Core

### 1. General Info
- **Technical Name:** `ops_matrix_core`
- **Version:** 19.0.1.4.0
- **Category:** Operations/Management
- **Application:** Yes (Installable, non-auto-install)
- **License:** LGPL-3
- **Author:** Gemini Agent
- **Website:** https://www.example.com

#### Dependencies:
- `base` (Odoo core)
- `mail` (Chatter, activity)
- `web` (UI)
- `account` (Accounting)
- `analytic` (Analytic accounts)
- `sale` (Sale orders)
- `stock` (Warehouse/Stock rules)
- `purchase` (Product requests â†’ PO line linking)
- `hr` (Persona-Employee Link)
- `product` (Products)

#### Summary:
Establishes the Matrix Operational Structure with four core engines:
1. **Organizational Structure:** Branches (geographic) & Business Units (strategic)
2. **Governance Engine:** Dynamic rules for approvals, blocking, and warnings
3. **Persona Engine:** Role-based matrix assignment with delegation
4. **SLA Management:** Time-based deadlines and status tracking

---

## 2. Data Models & Fields

### Model: `ops.branch`
**Technical Name:** `ops.branch`
**Description:** Operational Branch - represents a geographic or physical location within the organization.
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `sequence, id`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Tracking | Branch display name |
| `code` | Char | Required, Unique, Tracking, Copy=False | Auto-generated unique branch code via ir.sequence |
| `sequence` | Integer | Default=10 | Ordering priority |
| `active` | Boolean | Default=True | Soft delete flag |
| `color` | Integer | Optional | Kanban card color index |
| `company_id` | Many2one (`res.company`) | Required, Index, Check_company_auto | Company owner (default=current) |
| `manager_id` | Many2one (`res.users`) | Optional, Tracking, Domain | Branch manager (share=False users only) |
| `analytic_account_id` | Many2one (`account.analytic.account`) | Readonly, Copy=False | Auto-linked analytic account for GL tracking |

#### Constraints:
- **SQL:** `unique(code)` - Branch codes must be globally unique
- **Python:** `_check_code_unique()` - Validation: raise ValidationError if code exists

#### CRUD Logic:
- **Create:** Auto-generates `code` via sequence 'ops.branch' â†’ calls `_create_analytic_accounts()`
- **Write:** If `name` or `code` change â†’ syncs analytic account name via `_sync_analytic_account_name()`
- **Delete:** Cascades (soft via active field)

#### Key Methods:
- `_create_analytic_accounts()`: Creates linked account.analytic.account with naming pattern `[CODE] Name` in "Matrix Operations" plan
- `_sync_analytic_account_name()`: Updates analytic account name when branch name/code changes
- `_get_default_analytic_plan()`: Helper to find/create "Matrix Operations" analytic plan (reused by Business Units)

---

### Model: `ops.business.unit`
**Technical Name:** `ops.business.unit`
**Description:** Strategic Business Unit - represents a logical/business division (e.g., product line, region, customer segment).
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `sequence, id`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Tracking | Business unit display name |
| `code` | Char | Required, Tracking, Copy=False, Default='New' | Auto-generated unique code via ir.sequence |
| `sequence` | Integer | Default=10 | Ordering priority |
| `active` | Boolean | Default=True | Soft delete flag |
| `color` | Integer | Optional | Kanban color index |
| `company_id` | Many2one (`res.company`) | Required, Default=current | Company owner |
| `leader_id` | Many2one (`res.users`) | Optional, Tracking | Unit leader |
| `analytic_account_id` | Many2one (`account.analytic.account`) | Readonly, Copy=False | Auto-linked analytic account |

#### CRUD Logic:
- **Create:** Auto-generates `code` via sequence 'ops.business.unit' â†’ calls `_create_analytic_accounts()`
- **Write:** If `name` or `code` change â†’ syncs analytic account via `_sync_analytic_account_name()`

#### Key Methods:
- `_create_analytic_accounts()`: Reuses `ops.branch._get_default_analytic_plan()` to ensure branch and BU land in same plan
- `_sync_analytic_account_name()`: Updates analytic account name pattern `[CODE] Name`

---

### Model: `ops.persona`
**Technical Name:** `ops.persona`
**Description:** User role with matrix assignments, delegation capabilities, and approval authority. Core identity bridge between Users, Employees, and Matrix (Branch/BU).
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `name`
**Rec Name:** `name`

#### Fields:

##### 1. Basic Identity
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Tracking | Persona display name (e.g., 'Sales Manager - North') |
| `code` | Char | Required, Readonly, Copy=False, Default='New' | Auto-generated unique code via sequence 'ops.persona.code' |
| `description` | Text | Optional | Detailed role description |
| `user_id` | Many2one (`res.users`) | Required, Ondelete='cascade', Tracking, Unique (SQL) | The system user owning this persona |
| `employee_id` | Many2one (`hr.employee`) | Optional, Tracking | Related HR employee (for hierarchy) |
| `active` | Boolean | Default=True, Tracking | Soft delete flag |

##### 2. Hierarchy & Job Function
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `parent_id` | Many2one (`ops.persona`) | Optional | Reporting line (parent persona) |
| `child_ids` | One2many (`ops.persona`, 'parent_id') | Readonly | Direct reports |
| `job_level` | Selection | Default='mid', Tracking | Career level: entry, junior, mid, senior, lead, manager, director, executive |

##### 3. Matrix Assignments (Dimensional Scope)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `branch_id` | Many2one (`ops.branch`) | Optional, Tracking | Primary branch (physical location) |
| `primary_branch_id` | Many2one (`ops.branch`) | Related to `branch_id`, Readonly=False | Aliased primary branch for access rules |
| `allowed_branch_ids` | Many2many (`ops.branch`) | M2M rel='persona_branch_allowed_rel' | All branches this persona can access |
| `business_unit_ids` | Many2many (`ops.business.unit`) | M2M rel='persona_business_unit_rel' | Strategic units assigned to this persona |
| `allowed_business_unit_ids` | Many2many (`ops.business.unit`) | M2M rel='persona_bu_allowed_rel' | All BUs this persona can access |

##### 4. Governance & Permissions
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `access_group_ids` | Many2many (`res.groups`) | M2M rel='ops_persona_groups_rel' | Odoo security groups assigned |
| `approval_limit` | Monetary | Currency_field='currency_id', Tracking | Max amount this persona can approve |
| `currency_id` | Many2one (`res.currency`) | Default=company currency | Currency for approval limit |
| `can_approve_orders` | Boolean | Default=False | Fast-check permission flag |
| `can_approve_expenses` | Boolean | Default=False | Fast-check permission flag |
| `can_approve_leave` | Boolean | Default=False | Fast-check permission flag |
| `can_manage_team` | Boolean | Default=False | Fast-check permission flag |

##### 5. Delegation Engine (Temporal Authority Transfer)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `can_be_delegated` | Boolean | Default=True | Enable delegation capability |
| `delegate_id` | Many2one (`res.users`) | Optional, Tracking | Current delegate user (temporary authority holder) |
| `delegation_start` | Datetime | Optional, Tracking | Delegation start timestamp |
| `delegation_end` | Datetime | Optional, Tracking | Delegation end timestamp |
| `is_delegated` | Boolean | Computed, Stored | Is currently delegated (time-based check) |
| `effective_user_id` | Many2one (`res.users`) | Computed, Stored | Current power holder (owner or delegate) |
| `user_count` | Integer | Computed | Count of users assigned to this persona |
| `user_ids` | One2many (`res.users`, 'persona_id') | Readonly | All users assigned to this persona |

#### Constraints:
- **SQL:** `user_uniq UNIQUE(user_id)` - Each user can have only one operational persona
- **Python:** 
  - `_check_delegation_dates()`: End date must be > start date
  - `_check_delegate_not_owner()`: Delegate cannot be the owner user

#### Computed Fields Logic:
- **`_compute_is_delegated()`**: 
  1. Get current timestamp
  2. Check if `delegate_id` set AND delegation_start â‰¤ now â‰¤ delegation_end
  3. Return boolean

- **`_compute_effective_user()`**:
  1. Get current timestamp
  2. If delegation is active (start â‰¤ now â‰¤ end), return `delegate_id`
  3. Else return `user_id`

#### Key Methods:
- `_compute_user_count()`: Returns count of res.users with persona_id = this.id
- `_get_active_user()`: Helper to fetch the real user object (owner or delegate)
- `get_active_persona_for_user(user_id)`: 
  - **Logic:**
    1. Check if user is a delegate for any active persona (by delegation date window)
    2. If yes, return that delegated persona
    3. Else, check if user owns a persona
    4. Return owned persona or None
  - **Purpose:** Static method for backend to determine which persona a user is currently wielding

#### CRUD:
- **Create:** Auto-generates `code` via sequence 'ops.persona.code'

---

### Model: `ops.governance.rule`
**Technical Name:** `ops.governance.rule`
**Description:** Dynamic rule engine for conditional governance actions (warnings, blocks, approval triggers).
**Order:** `sequence, name`

#### Fields:

##### Rule Definition
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required | Rule display name |
| `code` | Char | Required, Readonly, Copy=False, Default='New' | Auto-generated via sequence 'ops.governance.rule.code' |
| `sequence` | Integer | Default=10 | Evaluation order |
| `active` | Boolean | Default=True | Enable/disable rule |
| `model_id` | Many2one (`ir.model`) | Required, Ondelete='cascade' | Target model for this rule |
| `trigger_type` | Selection | Default='on_write', Required | Event: on_create, on_write, on_unlink |

##### Conditions (Evaluation)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `condition_domain` | Text | Optional | Odoo domain expression [('field', 'operator', value)] |
| `condition_code` | Text | Optional | Python code returning True/False (variables: self, record, user, env) |

##### Actions (Consequence)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `action_type` | Selection | Default='warning', Required | Action: warning, block, require_approval |
| `error_message` | Char | Required | Message for user (warning/error) |
| `approval_user_ids` | Many2many (`res.users`) | Optional | Users who can approve |
| `approval_persona_ids` | Many2many (`ops.persona`) | M2M rel='rule_approval_persona_rel' | Personas authorized to approve |
| `lock_on_approval_request` | Boolean | Default=True | Lock record during approval |

##### Legacy Fields (Backward Compatibility - Sales Rules)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `min_margin_percent` | Float | Optional | [LEGACY] Min margin % to trigger approval |
| `max_discount_percent` | Float | Optional | [LEGACY] Max discount % to trigger approval |
| `business_unit_id` | Many2one (`ops.business.unit`) | Optional | Rule scope (empty = global) |

#### Constraints:
- **Python:**
  - `_check_percentages()`: Margin/discount must be 0-100
  - `_check_condition_provided()`: At least condition_domain OR condition_code required

#### Key Methods:

**`_evaluate_condition(record)`**:
- **Parameters:** record (BaseModel instance)
- **Logic:**
  1. If `condition_domain` set: Parse domain string â†’ use `filtered_domain()` â†’ match check
  2. If `condition_code` set: Use `safe_eval()` with safe locals (self, record, user, env)
  3. Return boolean match result
- **Returns:** Boolean (True if condition matches)

**`_parse_domain_string(domain_str)`**:
- Parse string representation of domain using `ast.literal_eval()`
- Return parsed list or raise ValidationError

**`_trigger_approval_if_needed(record)`**:
- **Logic:**
  1. Check if rule is active
  2. Evaluate condition via `_evaluate_condition(record)`
  3. If condition matches:
     - **Action: warning** â†’ Post message to record â†’ Return False
     - **Action: block** â†’ Raise ValidationError â†’ Block operation
     - **Action: require_approval** â†’ Create ops.approval.request â†’ Lock record if configured â†’ Return True
- **Returns:** Boolean (True if approval created)

**`evaluate_rules_for_record(record, trigger_type='on_write')`** [Class Method]:
- **Logic:**
  1. Search for all active rules matching: model_id.model = record._name, trigger_type matching
  2. Order by sequence ASC
  3. For each rule, call `_trigger_approval_if_needed(record)`
- **Purpose:** Called from model hooks to enforce governance

#### CRUD:
- **Create:** Auto-generates `code` via sequence

---

### Model: `ops.approval.request`
**Technical Name:** `ops.approval.request`
**Description:** Tracks approval requests triggered by governance rules or manual action.
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `create_date desc`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Readonly, Default='New' | Auto-generated reference via sequence 'ops.approval.request' |
| `rule_id` | Many2one (`ops.governance.rule`) | Required | Governance rule that triggered this |
| `model_name` | Char | Required | Target model name (string) |
| `res_id` | Integer | Required | Record ID of target |
| `res_name` | Char | Computed, Stored | Display name of target record (computed from model/res_id) |
| `notes` | Text | Optional | Additional context |
| `response_notes` | Text | Optional | Approver response message |
| `requested_by` | Many2one (`res.users`) | Required, Default=current user, Readonly | Who initiated approval |
| `requested_date` | Datetime | Required, Default=now, Readonly | When approval requested |
| `approved_by` | Many2one (`res.users`) | Optional, Readonly | Who approved |
| `approved_date` | Datetime | Optional, Readonly | When approved |
| `branch_id` | Many2one (`ops.branch`) | Required | Branch from source record |
| `business_unit_id` | Many2one (`ops.business.unit`) | Required | BU from source record |
| `state` | Selection | Default='pending', Tracking | Status: pending, approved, rejected, cancelled |
| `approver_ids` | Many2many (`res.users`) | Computed, Stored | Users authorized to approve |

#### Computed Fields:
**`_compute_res_name()`**:
- Browse `env[model_name].browse(res_id)`
- Return `display_name` or "ModelName#ID (Deleted)" if record missing

**`_compute_approvers()`**:
- If `rule_id.required_persona_id` set: find users with that persona
- Else: clear field

#### CRUD Logic:
- **Create:**
  1. If model_name and res_id provided: inherit branch_id and business_unit_id from source record
  2. Auto-generate name via sequence

#### Key Methods:

**`action_approve()`**:
- **Logic:**
  1. Check state == 'pending'
  2. Write state='approved'
  3. Unlock source record if it has 'approval_locked' field
- **Returns:** Boolean

**`action_reject()`**:
- **Logic:**
  1. Check state == 'pending'
  2. Write state='rejected', set approved_by and approved_date
  3. Unlock source record
- **Returns:** Boolean

**`action_cancel()`**:
- **Logic:**
  1. Check state == 'pending'
  2. Write state='cancelled'
  3. Unlock source record
- **Returns:** Boolean

---

### Model: `ops.sla.template`
**Technical Name:** `ops.sla.template`
**Description:** Service Level Agreement template defining target response/resolution time.

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required | Template name |
| `model_id` | Many2one (`ir.model`) | Required, Ondelete='cascade' | Target model |
| `calendar_id` | Many2one (`resource.calendar`) | Required, Default=company calendar | Working calendar (respects business hours) |
| `target_duration` | Float | Required | Target duration in hours |
| `active` | Boolean | Default=True | Enable/disable |

#### Key Methods:

**`_compute_deadline(start_dt: datetime)`**:
- **Logic:**
  1. Use `calendar_id.plan_hours(target_duration, start_dt)`
  2. Returns deadline datetime respecting calendar working intervals
- **Returns:** Datetime

---

### Model: `ops.sla.instance`
**Technical Name:** `ops.sla.instance`
**Description:** Individual SLA tracking for a specific record instance.
**Order:** `deadline asc`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `template_id` | Many2one (`ops.sla.template`) | Required, Ondelete='cascade' | Template to follow |
| `res_model` | Char | Related to `template_id.model_id.model`, Stored | Target model name (denormalized) |
| `res_id` | Integer | Required, Index | Record ID of target |
| `start_datetime` | Datetime | Required, Default=now | When SLA started |
| `deadline` | Datetime | Computed, Stored | Deadline (computed from template) |
| `status` | Selection | Computed, Stored, Default='running' | Status: running, warning, critical, violated, completed |
| `progress` | Float | Computed | Time elapsed percentage (0-100) |

#### Status Computation Logic (`_compute_status()`):
1. If status already='completed': skip
2. If no deadline: status='running'
3. If now > deadline: status='violated'
4. Else calculate elapsed %:
   - percent = (elapsed_time / total_time) Ã— 100
   - If percent > 90: 'critical'
   - Else if percent > 75: 'warning'
   - Else: 'running'

#### Progress Computation (`_compute_progress()`):
- If completed: 100%
- Else: (elapsed_time / total_time) Ã— 100, clamped 0-100

#### Key Methods:

**`action_complete()`**:
- Set status='completed'

**`_cron_check_sla_status()`** [Cron Job]:
- **Logic:**
  1. Search for all non-completed SLAs (status in running/warning/critical)
  2. Re-compute status for each
  3. If status changed: post message to target record chatter
  4. Continue on errors

---

### Model: `ops.governance.mixin`
**Technical Name:** `ops.governance.mixin`
**Description:** Abstract mixin to add governance rule enforcement to any model.
**Inheritance:** Not a model itself - use `_name = 'ops.governance.mixin'` as abstract model

#### Fields Added by Mixin:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `approval_locked` | Boolean | Default=False, Copy=False | Record locked pending approval |
| `approval_request_ids` | One2many (`ops.approval.request`) | Computed | Related approval requests |
| `approval_request_count` | Integer | Computed | Count of approval requests |

#### Computed Fields:

**`_compute_approval_requests()`**:
- Search `ops.approval.request` where model_name=this._name, res_id=this.id
- Set approval_request_ids and approval_request_count

#### Key Methods:

**`action_view_approvals()`**:
- **Returns:** Window action to list approval requests for this record

**`action_request_approval()`**:
- **Logic:**
  1. Find rules for this model with action_type='require_approval'
  2. If none found: raise UserError
  3. For first matching rule: call `_apply_governance_rule(rule, 'manual')`
  - **Purpose:** Manual approval trigger button

---

### Model: `ops.matrix.mixin`
**Technical Name:** `ops.matrix.mixin`
**Description:** Abstract mixin for matrix awareness. Inherit to add branch/BU dimensions.

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `ops_branch_id` | Many2one (`ops.branch`) | Optional, Index, Tracking, Check_company | Primary branch assignment |
| `ops_business_unit_id` | Many2one (`ops.business.unit`) | Optional, Index, Tracking, Check_company | Primary BU assignment |

#### Helper Methods:
- `_get_default_ops_branch()`: Hook to fetch default branch from user context/settings

---

### Model: `sale.order` [Extension]
**Technical Name:** `sale.order`
**Description:** Standard Sale Order extended with governance, credit checks, and matrix dimensions.
**Inheritance:** `sale.order`, `ops.governance.mixin`

#### Added Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `ops_branch_id` | Many2one (`ops.branch`) | Optional, Tracking | Sale order branch |
| `ops_business_unit_id` | Many2one (`ops.business.unit`) | Optional, Tracking | Sale order BU |
| `ops_credit_check_passed` | Boolean | Default=False, Readonly | Credit firewall pass flag |
| `ops_credit_check_notes` | Text | Readonly | Credit check evaluation notes |

#### Key Methods:

**`_check_business_unit_silo()`**:
- **Trigger:** @api.constrains on order_line
- **Logic:**
  1. Skip if superuser
  2. Get user's allowed BUs from persona
  3. For each line: check if product.business_unit_id in allowed list
  4. If not: raise ValidationError (SILO VIOLATION)
- **Purpose:** Enforce product segregation by BU

**`_get_products_availability_data()`**:
- **Logic:**
  1. For each storable product in order_line
  2. Calculate: stock_on_hand = product.qty_available
  3. Calculate: display_qty = min(ordered_qty, stock_on_hand)
  4. Flag: is_insufficient if stock < ordered
  5. Return list of dicts with {sku, product_name, ordered_qty, stock_on_hand, display_qty, is_insufficient}
- **Purpose:** Prepare data for availability report

**`_check_partner_credit_firewall()`**:
- **Returns:** (bool, str) = (passed, message)
- **Logic:**
  1. Skip if superuser
  2. Check: partner.ops_state in ['approved'] (if field exists)
  3. Check: partner.active == True
  4. Check: (partner.ops_total_outstanding + order.amount_total) â‰¤ partner.ops_credit_limit
  5. Check: partner.ops_confirmation_restrictions is False (if field exists)
  6. Return (True, 'Credit check passed') or (False, reason_message)

**`action_confirm()`** [Override]:
- **Logic:**
  1. Perform `_check_partner_credit_firewall()`
  2. If failed: set ops_credit_check_passed=False, write notes, continue (or raise based on config)
  3. Evaluate governance rules via `ops.governance.rule.evaluate_rules_for_record()`
  4. Call parent `action_confirm()`

---

## 3. Key Methods & Business Logic

### OPS Branch Methods

**`_create_analytic_accounts()`**:
- **Trigger:** Called from create() after record creation
- **Logic:**
  1. Get/create "Matrix Operations" analytic plan
  2. For each branch without analytic_account_id:
     - Create account.analytic.account with name `[CODE] Name`
     - Set company_id from branch
     - Link via analytic_account_id
  3. Commit

**`_sync_analytic_account_name()`**:
- **Trigger:** Called from write() if name/code change
- **Logic:**
  1. For each branch with analytic_account_id:
     - Update AA name to `[CODE] Name`

---

### OPS Persona Methods

**`get_active_persona_for_user(user_id)`** [Static]:
- **Trigger:** Backend static method to lookup
- **Logic:**
  1. Convert user_id to user object if needed
  2. Check if user is active delegate: search delegation records with delegation_start â‰¤ now â‰¤ delegation_end
  3. If found: return delegated persona
  4. Check if user owns a persona: search user_id=user
  5. Return owned persona or None
- **Purpose:** Determine which persona user is currently wielding (prioritizes delegation)

---

### OPS Governance Rule Methods

**`evaluate_rules_for_record(record, trigger_type='on_write')`** [Class]:
- **Trigger:** Called from model hooks (create, write, unlink)
- **Logic:**
  1. Search active rules: model_id.model = record._name, trigger_type matching
  2. Order by sequence
  3. For each rule: call `_trigger_approval_if_needed(record)`
  4. Continue even if some rules trigger (allow multiple approvals)

---

### OPS Approval Request Methods

**`action_approve()`**:
- **Trigger:** Button click
- **Logic:**
  1. Validate state='pending'
  2. Write: state='approved', approved_by=current user, approved_date=now
  3. Unlock source record if approval_locked field exists
  4. Unlock via `record.write({'approval_locked': False})`

---

### OPS SLA Methods

**`_cron_check_sla_status()`**:
- **Trigger:** Scheduled action (ir_cron)
- **Logic:**
  1. Search non-completed SLAs (status in running/warning/critical)
  2. Iterate: re-compute status â†’ if changed, post chatter message
  3. Continue on errors

---

## 4. XML Views & Interface

### OPS Branch Views

**Form View (`view_ops_branch_form`)**:
- **Header:** Standard save/close buttons
- **Sheet:**
  - Title group: `name` (editable heading)
  - Field group 1: `code` (readonly), `manager_id` (Many2one popup)
  - Field group 2: `company_id` (multi-company context)

**Tree View (`view_ops_branch_list`)**:
- Columns: `sequence` (handle widget), `code` (readonly), `name`, `manager_id`, `company_id`
- Editable: bottom (add rows at bottom)

**Kanban View (`view_ops_branch_kanban`)**:
- Color field: `color` (Kanban color picker)
- Card display: name, code, manager_id (avatar widget)
- Dropdown: color picker menu

**Search View (`view_ops_branch_search`)**:
- Fields: name, code, manager_id, company_id
- Filters: Archived (active=False), Manager (group_by), Company (group_by)

---

### OPS Persona Views

**Form View:**
- **Header:** State bar (if any), action buttons
- **Tabs:**
  1. **Matrix Tab:** branch_id, business_unit_ids, allowed_branch_ids, allowed_business_unit_ids
  2. **Permissions Tab:** access_group_ids, approval_limit, can_approve_* flags
  3. **Delegation Tab:** can_be_delegated, delegate_id, delegation_start/end, is_delegated, effective_user_id
  4. **Team Tab:** user_ids (One2many list)

---

### OPS Governance Rule Views

**Form View:**
- **Group 1:** name, code, sequence, active, model_id
- **Group 2:** trigger_type (Selection)
- **Conditions Notebook:**
  - Tab 1: condition_domain (textarea)
  - Tab 2: condition_code (textarea)
- **Action Group:** action_type, error_message
- **Approval Group:** approval_user_ids, approval_persona_ids, lock_on_approval_request
- **Legacy Group:** min_margin_percent, max_discount_percent, business_unit_id

---

### OPS Approval Request Views

**Form View:**
- **Header:** state (Statusbar), action buttons (approve, reject, cancel)
- **Group 1:** name, rule_id, requested_by, requested_date
- **Group 2:** model_name, res_id, res_name (computed, readonly)
- **Group 3:** branch_id, business_unit_id
- **Notes Section:** notes (textarea), response_notes (textarea)

**Tree View:**
- Columns: name, rule_id, res_name, requested_by, state, requested_date
- Color decorator: state (pending=yellow, approved=green, rejected=red)

---

### OPS SLA Instance Views

**Tree View:**
- Columns: res_model, res_id, template_id, start_datetime, deadline, status, progress
- Color: status (running=blue, warning=orange, critical=red, violated=dark red)

---

### Sale Order Extended Views

**Smart Button:** "Approvals" button showing approval_request_count

**Section in Form:** Credit check results (ops_credit_check_passed, ops_credit_check_notes)

---

## 5. Security

### Groups Defined (in `data/res_groups.xml`):
- `group_ops_user` - Base OPS user (read-only matrix structures)
- `group_ops_manager` - OPS manager (read/write/create matrix structures)
- `group_ops_admin` - OPS admin (full CRUD including delete)
- `group_ops_product_approver` - Can approve product requests
- `group_ops_cost_controller` - Cost analysis rights (reporting module)

### Access Control (`security/ir.model.access.csv`):

| Model | User Group | Read | Write | Create | Delete |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ops.branch` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.branch` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.branch` | group_ops_admin | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.business.unit` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.business.unit` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.business.unit` | group_ops_admin | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.persona` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.persona` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.governance.rule` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.governance.rule` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.approval.request` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.approval.request` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.sla.template` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.sla.template` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.sla.instance` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.product.request` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.product.request` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |

### Record Rules (`security/ir_rule.xml`):

**1. Matrix Intersection Rule:**
- Model: `ops.approval.request`
- Domain: `['&', ('branch_id', 'in', user.ops_allowed_branch_ids.ids), ('business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)]`
- Purpose: Users only see requests for their allowed Branch AND BU intersection

**2. Branch Visibility Rule:**
- Model: `ops.branch`
- Domain: `[('id', 'in', user.ops_allowed_branch_ids.ids)]`
- Groups: base.group_user (all users)
- Purpose: Users see only their allowed branches
- Admin Override: System admins bypass via `ops_branch_admin_full_access` rule

**3. Business Unit Visibility Rule:**
- Model: `ops.business.unit`
- Domain: `[('id', 'in', user.ops_allowed_business_unit_ids.ids)]`
- Groups: base.group_user
- Purpose: Users see only their allowed business units
- Admin Override: System admins bypass

**4. Sale Order Branch Visibility:**
- Model: `sale.order`
- Domain: `['|', ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids), ('ops_branch_id', '=', False)]`
- Perm: Read only
- Purpose: Users see orders for their branch (or unassigned)

**5. Product Business Unit Silo:**
- Model: `product.template`
- Domain: `['|', ('business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids), ('business_unit_id', '=', False)]`
- Perm: Read only
- Purpose: Users see products for their BU (or unassigned)

**6. Product Request Branch Access:**
- Model: `ops.product.request`
- Domain: Branch-based visibility
- Purpose: Users see requests from their branch only

### User Fields Added (`res_users` extensions):
- `ops_allowed_branch_ids` (Many2many) - Branches user can access
- `ops_allowed_business_unit_ids` (Many2many) - Business units user can access
- `persona_id` (Many2one) - Link to ops.persona if exists

---

## 6. Data & Configuration Files

### Sequences (ir_sequence_data.xml):
- `ops.branch` - Auto-generates branch codes
- `ops.business.unit` - Auto-generates BU codes
- `ops.persona.code` - Auto-generates persona codes
- `ops.governance.rule.code` - Auto-generates rule codes
- `ops.approval.request` - Auto-generates approval references

### Scheduled Actions (ir_cron_data.xml):
- **SLA Status Check:** Runs `ops.sla.instance._cron_check_sla_status()` periodically
- **Archive Policy Executor:** Triggers archive policies (if defined)

### Templates (data/ops_persona_templates.xml):
- Pre-defined persona templates for common roles (Sales Manager, Admin, etc.)

### Templates (data/ops_governance_rule_templates.xml):
- Pre-defined rule templates (discount limits, margin checks, etc.)

---

## 7. Standard Model Extensions

### Models Extended (via inheritance):
- **`sale.order`:** Added ops_branch_id, ops_business_unit_id, credit check fields, governance mixin
- **`account.move`:** Added branch_id, business_unit_id (matrix dimensions)
- **`stock.move`:** Added branch_id, business_unit_id (matrix dimensions)
- **`stock.picking`:** Added branch_id, business_unit_id (matrix dimensions)
- **`stock.warehouse`:** Added branch_id (warehouse-branch link)
- **`product.template`:** Added business_unit_id (product segregation)
- **`res.partner`:** Added ops_* fields (credit state, credit limit, etc.)
- **`res.users`:** Added persona_id, ops_allowed_branch_ids, ops_allowed_business_unit_ids

---

## 8. Static Assets

### JavaScript:
- **`static/src/js/report_action_override.js`:** Overrides report rendering for product availability

### Components:
- **`static/src/components/matrix_availability_tab/`:** Custom UI component for availability matrix
  - `matrix_availability_tab.js` - Component logic
  - `matrix_availability_tab.xml` - Template
  - `matrix_availability_tab.css` - Styling

---

## 9. Modules Workflow Summary

**User Journey:**
1. User logs in with `res.users` account
2. System looks up user's `ops.persona` (if exists)
3. From persona, system determines:
   - Allowed branches (via `ops_allowed_branch_ids`)
   - Allowed business units (via `ops_allowed_business_unit_ids`)
   - Effective user (owner or delegate, if within delegation window)
4. When user creates/modifies records:
   - Record rules filter visibility (branch/BU intersection)
   - Governance rules evaluate conditions
   - If rule triggers "require_approval": creates `ops.approval.request`, locks record
   - Approvers (based on rule) receive approval workflow
5. For financial tracking:
   - Branch/BU auto-create linked analytic accounts
   - All transactions tagged with branch/BU dimensions
   - GL/reports can slice by organizational structure

---

## 10. Key Design Patterns

### 1. Matrix Dimensions Pattern
- Every transactional record inherits `ops.matrix.mixin` or explicitly adds `ops_branch_id`, `ops_business_unit_id`
- Used for multi-dimensional filtering, reporting, security

### 2. Governance by Rules Pattern
- Models inherit `ops.governance.mixin`
- Governance rules dynamically evaluate conditions (domain or Python)
- Actions: warning (log), block (exception), require_approval (workflow)
- Reusable across any model

### 3. Delegation Pattern (Persona)
- User permanently owns a persona
- Persona can be temporarily delegated to another user (with time window)
- `effective_user_id` computed field resolves who truly has the power
- Used for vacation coverage, temporary assignments

### 4. Analytic Synchronization Pattern
- Branch/BU auto-create linked analytic accounts
- Account names synced when parent renamed
- Enables GL drill-down by organizational structure

### 5. Mixin-Based Extensibility
- `ops.matrix.mixin` - add dimensional awareness
- `ops.governance.mixin` - add approval workflows
- `ops.sla.mixin` - add SLA tracking
- Multiple inheritance allows composable features

---

## 11. Integration Points

### With Standard Modules:
- **Sale:** Sale order extended with branch/BU, credit check, governance
- **Account:** Moves tagged with branch/BU, linked to analytic accounts
- **Stock:** Warehouse, picking, move all matrix-aware
- **HR:** Employee linked to persona for hierarchy
- **Mail:** Chatter on governance rules, approval requests, personas (activity history)

### Hooks/Customization:
- `ops.governance.rule.condition_code` - allows custom Python logic
- Model hooks can call `ops.governance.rule.evaluate_rules_for_record()`
- `_get_default_ops_branch()` hook in mixin for custom defaults
- Views can be extended per usual Odoo patterns (inherit, add tabs, etc.)

---
