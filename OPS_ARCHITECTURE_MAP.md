# OPS Framework Architecture Map

**Generated:** 2026-01-19
**Module:** ops_matrix_core v19.0.1.5.0
**Purpose:** Deep Architectural Audit & Data Dependency Mapping for Plug & Play Deployment

---

## 1. MODULE HIERARCHY (Correct Install Sequence)

```
1. base, mail, analytic, account, sale, purchase, stock, hr  (Odoo Core)
   │
2. ops_matrix_core                     (REQUIRED - Foundation)
   │
3. ops_matrix_accounting               (Depends on ops_matrix_core)
   │
4. ops_matrix_reporting                (Depends on ops_matrix_core)
   │
5. ops_matrix_asset_management         (Depends on ops_matrix_core)
```

### OPS Matrix Core Dependencies
```python
'depends': [
    'base',      # Odoo Foundation
    'mail',      # Messaging & Chatter
    'analytic',  # Cost Centers
    'account',   # Accounting
    'sale',      # Sales Orders
    'purchase',  # Purchase Orders
    'stock',     # Inventory
    'hr',        # HR/Employees
]
```

---

## 2. DATA ASSET INVENTORY

### Currently ENABLED Data Files (Loading Order)

| Seq | File | Purpose | Dependencies |
|-----|------|---------|--------------|
| 1 | `ir_module_category.xml` | Module categories | None |
| 2 | `res_groups.xml` | Security groups (22 groups) | `base.group_user`, `base.group_system` |
| 3 | `ir_sequence_data.xml` | Sequence generators | None |
| 4 | `product_request_sequence.xml` | Product request sequences | Sequences |
| 5 | `ops_account_templates.xml` | Account templates | Account module |
| 6 | `ir_cron_data.xml` | Scheduled jobs | Models must exist |
| 7 | `ir_cron_archiver.xml` | Archive cron jobs | `ops.archive.policy` |
| 8 | `ir_cron_escalation.xml` | Escalation cron | `ops.approval.request`, `ops.sla.instance` |
| 9 | `sale_order_actions.xml` | Sale order server actions | `sale.order` |
| 10 | `email_templates.xml` | Email templates | Mail module |
| 11 | `ops_report_templates.xml` | Report templates | `ops.report.template` |
| 12 | `ops_archive_templates.xml` | Archive policies | `ops.archive.policy` |

### COMMENTED OUT Data Files (Analysis)

| File | Status | Dependencies | Why Commented | Safe to Enable? |
|------|--------|--------------|---------------|-----------------|
| `ops_persona_templates.xml` | **COMMENTED** | None (self-contained) | "Require personas created first" | **YES - FIRST** |
| `ops_governance_rule_templates.xml` | **COMMENTED** | `ops.persona` records | References `persona_sales_manager`, `persona_sales_director`, etc. | AFTER Personas |
| `ops_governance_templates.xml` | **COMMENTED** | `ops.governance.rule` | Additional governance rules | AFTER Personas |
| `ops_governance_templates_extended.xml` | **COMMENTED** | `ops.governance.rule` | Extended governance rules | AFTER Personas |
| `ops_sla_templates.xml` | **COMMENTED** | None (uses model refs) | SLA templates for sale.order, stock.picking | **YES - SAFE** |
| `ops_sod_default_rules.xml` | **COMMENTED** | None (self-contained) | SoD rules (all inactive by default) | **YES - SAFE** |
| `field_visibility_rules.xml` | **COMMENTED** | Security groups | Field visibility rules | **YES - SAFE** |
| `ops_product_templates.xml` | **COMMENTED** | `product.category`, `product.product` | Demo products | Optional (Demo) |
| `ops_default_data.xml` | **COMMENTED** | None | Empty placeholder | N/A |
| `ops_default_data_clean.xml` | **COMMENTED** | None | Clean install data | N/A |
| `product_rules.xml` | **COMMENTED** | Unknown | Product rules | Review First |
| `ops_governance_rule_three_way_match.xml` | **COMMENTED** | `ops.three.way.match` | 3-way match rules | Review First |

### Templates Directory (NON-EXISTENT)
```
data/templates/ops_persona_templates.xml        - FILE DELETED
data/templates/ops_governance_rule_templates.xml - FILE DELETED
data/templates/ops_user_templates.xml           - FILE DELETED
data/templates/ops_sla_templates.xml            - FILE DELETED
```
**Status:** These files are referenced in manifest but the `templates/` directory is empty (files were deleted per git status).

---

## 3. PERFECT LOAD ORDER (Recommended Uncomment Sequence)

```
PHASE 1: Foundation Templates (No Dependencies)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. data/ops_persona_templates.xml       ✅ SAFE - Self-contained persona definitions

PHASE 2: Governance & SLA (Depends on Personas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. data/ops_sla_templates.xml           ✅ SAFE - Uses model refs only
3. data/ops_sod_default_rules.xml       ✅ SAFE - All rules inactive by default
4. data/field_visibility_rules.xml      ✅ SAFE - Uses existing security groups
5. data/ops_governance_templates.xml    ⚠️ AFTER personas load

PHASE 3: Extended Rules (Depends on Phase 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. data/ops_governance_rule_templates.xml    ⚠️ REFERENCES: persona_sales_manager,
                                                persona_sales_director, persona_purchasing_manager,
                                                persona_operations_director, persona_finance_manager,
                                                persona_warehouse_manager, persona_finance_director

   GAP ANALYSIS: The following personas are referenced but NOT defined:
   - persona_sales_director (MISSING - use persona_sales_leader?)
   - persona_purchasing_manager (MISSING - use persona_purchase_manager?)
   - persona_operations_director (MISSING)
   - persona_finance_manager (MISSING - use persona_cfo?)
   - persona_warehouse_manager (MISSING - use persona_logistics_manager?)
   - persona_finance_director (MISSING - use persona_cfo?)

7. data/ops_governance_templates_extended.xml  ⚠️ AFTER governance templates

PHASE 4: Optional/Demo Data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. data/ops_product_templates.xml       📦 DEMO - Product categories & products
```

---

## 4. FUNCTIONAL LOGIC MAP (The "Brain")

### 4.1 GOVERNANCE SYSTEM (`ops.governance.mixin`, `ops.governance.rule`)

**Location:** [ops_governance_mixin.py](addons/ops_matrix_core/models/ops_governance_mixin.py), [ops_governance_rule.py](addons/ops_matrix_core/models/ops_governance_rule.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **Record Locking** | `approval_locked` field on mixin | ✅ Working |
| **Admin Bypass** | `env.su` or `base.group_system` check | ✅ Working |
| **Create/Write/Unlink Hooks** | Overridden in mixin | ✅ Working |
| **Condition Evaluation** | `safe_eval` with Python code or domain | ✅ Working |
| **Action Types** | `warning`, `block`, `require_approval` | ✅ Working |
| **Four-Eyes Principle** | SoD check prevents self-approval | ✅ Working |
| **Vertical Escalation** | Auto-escalates to parent persona | ✅ Working |
| **Executive Deadlock** | Detects when no higher authority exists | ✅ Working |

**Rule Types:**
```python
rule_type = Selection([
    ('matrix_validation', 'Matrix Validation'),     # Branch/BU enforcement
    ('discount_limit', 'Discount Limit'),           # Max discount control
    ('margin_protection', 'Margin Protection'),     # Min margin enforcement
    ('price_override', 'Price Override'),           # Price variance control
    ('approval_workflow', 'Approval Workflow'),     # Multi-level approval
    ('notification', 'Notification'),               # Alert without blocking
    ('legacy', 'Legacy'),                           # Backward compatibility
])
```

**Trigger Events:**
```python
trigger_event = Selection([
    ('always', 'Always'),           # Every create/write
    ('on_create', 'On Create'),     # Only on creation
    ('on_write', 'On Write'),       # Only on update
    ('on_state_change', 'On State Change'),  # Status transitions
])
```

---

### 4.2 APPROVAL ENGINE (`ops.approval.rule`, `ops.approval.request`)

**Location:** [ops_approval_rule.py](addons/ops_matrix_core/models/ops_approval_rule.py), [ops_approval_request.py](addons/ops_matrix_core/models/ops_approval_request.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **Multi-Level Approval** | `escalation_level` field (0-3) | ✅ Working |
| **Persona-Based Approvers** | `approver_persona_ids` M2M | ✅ Working |
| **Group-Based Approvers** | `approver_group_ids` M2M | ✅ Working |
| **User-Based Approvers** | `approver_user_ids` M2M | ✅ Working |
| **Auto-Escalation** | Cron job `_cron_escalate_overdue_approvals` | ✅ Working |
| **Escalation Timeout** | `escalation_timeout_hours` config | ✅ Working |
| **Recall Logic** | Wizard `ops.approval.recall.wizard` | ✅ Working |
| **Reject with Reason** | Wizard `ops.approval.reject.wizard` | ✅ Working |
| **Matrix Inheritance** | Inherits Branch/BU from source record | ✅ Working |
| **Violation Tracking** | `violation_type`, `violation_details` | ✅ Working |

**Approval States:**
```python
state = Selection([
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
])
```

**Escalation Chain:**
```
Level 0 → Level 1 (Direct Manager)
      → Level 2 (Manager's Manager / BU Leader)
      → Level 3 (Executive - CEO/CFO)
      → FAILED (Max escalation reached)
```

---

### 4.3 PERSONA SYSTEM (`ops.persona`)

**Location:** [ops_persona.py](addons/ops_matrix_core/models/ops_persona.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **Matrix Access** | `branch_ids`, `business_unit_ids` M2M | ✅ Working |
| **Job Hierarchy** | `parent_id`, `child_ids` | ✅ Working |
| **Job Levels** | 8 levels (entry → executive) | ✅ Working |
| **Odoo Group Sync** | `_sync_user_groups()` method | ✅ Working |
| **User Assignment** | `user_id` field | ✅ Working |
| **Secondary Users** | `secondary_user_ids` M2M | ✅ Working |
| **Delegation System** | `ops.persona.delegation` model | ✅ Working |
| **Effective User** | `get_effective_user()` considers delegation | ✅ Working |
| **Date Validity** | `start_date`, `end_date` | ✅ Working |
| **Activation** | Creates `res.groups` record | ✅ Working |

**Segregation of Duties (SoD) Authority Fields:**
```python
can_modify_product_master = Boolean   # Procurement/Finance only
can_access_cost_prices = Boolean      # Hidden from Sales
can_validate_invoices = Boolean       # Accountant+
can_post_journal_entries = Boolean    # Accountant/CFO only
can_execute_payments = Boolean        # Treasury only
can_adjust_inventory = Boolean        # Inventory Manager only
can_manage_pdc = Boolean              # Treasury/Finance
```

**Persona-to-Odoo Group Mapping:**
| Persona Flag | Odoo Group |
|-------------|------------|
| `is_branch_manager` | `group_ops_branch_manager` |
| `is_bu_leader` | `group_ops_bu_leader` |
| `is_matrix_administrator` | `group_ops_matrix_administrator` |

---

### 4.4 SLA SYSTEM (`ops.sla.template`, `ops.sla.instance`)

**Location:** [ops_sla_template.py](addons/ops_matrix_core/models/ops_sla_template.py), [ops_sla_instance.py](addons/ops_matrix_core/models/ops_sla_instance.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **Template Definition** | `target_duration` in hours | ✅ Working |
| **Working Calendar** | `calendar_id` for business hours | ✅ Working |
| **Deadline Calculation** | `_compute_deadline()` uses `plan_hours()` | ✅ Working |
| **Progress Tracking** | `elapsed_hours`, `remaining_hours`, `progress` | ✅ Working |
| **Status Detection** | `running`, `warning`, `critical`, `violated` | ✅ Working |
| **Auto-Escalation** | `action_escalate()` method | ✅ Working |
| **Cron Monitoring** | `_cron_check_escalations` every 15 min | ✅ Working |
| **Email Notifications** | Warning, Escalation, Failed templates | ✅ Working |

**SLA States:**
```python
state = Selection([
    ('running', 'Running'),
    ('completed', 'Completed'),
    ('failed', 'Failed (Timeout)'),
    ('escalated', 'Escalated'),
])

status = Selection([  # Computed status for dashboards
    ('running', 'Running'),
    ('warning', 'Warning'),       # >75% elapsed
    ('critical', 'Critical'),     # >90% elapsed
    ('violated', 'Violated'),     # Past deadline
    ('completed', 'Completed'),
])
```

---

### 4.5 SEGREGATION OF DUTIES (`ops.segregation.of.duties`)

**Location:** [ops_segregation_of_duties.py](addons/ops_matrix_core/models/ops_segregation_of_duties.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **Rule Definition** | `action_1` vs `action_2` prevention | ✅ Working |
| **Document Types** | sale.order, purchase.order, account.move, account.payment, stock.picking | ✅ Working |
| **Threshold Support** | `threshold_amount` for conditional enforcement | ✅ Working |
| **Block/Warn Mode** | `block_violation` toggle | ✅ Working |
| **Company Scoping** | `company_id` optional filter | ✅ Working |
| **Violation Logging** | `ops.segregation.of.duties.log` audit trail | ✅ Working |
| **Compliance Reporting** | `get_violations_report()` method | ✅ Working |

**Default SoD Rules (All INACTIVE by default):**
| Rule | Actions | Threshold | Purpose |
|------|---------|-----------|---------|
| Sales Create+Confirm | create → confirm | $5,000 | Independent review of sales |
| Purchase Create+Confirm | create → confirm | $5,000 | Authorization controls |
| Invoice Create+Post | create → post | $0 (all) | AP/AR controls |
| Payment Create+Post | create → post | $2,000 | Dual control disbursements |

---

### 4.6 THREE-WAY MATCH (`ops.three.way.match`)

**Location:** [ops_three_way_match.py](addons/ops_matrix_core/models/ops_three_way_match.py)

**Capabilities:**
| Feature | Implementation | Status |
|---------|---------------|--------|
| **PO-Receipt-Invoice Match** | Links purchase.order.line to moves & invoices | ✅ Working |
| **Variance Calculation** | `qty_variance`, `qty_variance_percent` | ✅ Working |
| **Tolerance Support** | `company.three_way_match_tolerance` | ✅ Working |
| **Blocking Logic** | `is_blocked`, `blocking_reason` | ✅ Working |

**Match States:**
```python
match_state = Selection([
    ('matched', 'Matched'),           # All quantities align
    ('under_billed', 'Under Billed'), # Billed < Received
    ('over_billed', 'Over Billed'),   # Billed > Received (BLOCKS)
    ('no_receipt', 'No Receipt'),     # Nothing received (BLOCKS)
    ('partial_receipt', 'Partial Receipt'),  # Partially received
])
```

---

## 5. SECURITY GROUPS INVENTORY

### OPS Security Group Hierarchy

```
base.group_user
├── group_ops_user (Basic OPS access)
│   ├── group_ops_manager (Branch/BU management)
│   │   ├── group_ops_bu_leader (Multi-branch BU access)
│   │   │   └── group_ops_cross_branch_bu_leader
│   │   ├── group_ops_sales_manager
│   │   ├── group_ops_purchase_manager
│   │   ├── group_ops_inventory_manager
│   │   └── group_ops_finance_manager
│   │       └── group_ops_cost_controller
│   ├── group_ops_branch_manager (Single branch)
│   ├── group_ops_executive (CEO - Read-only oversight)
│   ├── group_ops_cfo (Full financial access)
│   ├── group_ops_accountant (Accounting operations)
│   ├── group_ops_treasury (Cash management)
│   └── group_ops_product_approver
│
base.group_system
└── group_ops_admin_power (Full system authority)
    └── group_ops_matrix_administrator

group_ops_it_admin (SEPARATE - No business data)
```

### Data Visibility Groups (Additive)
| Group | Grants |
|-------|--------|
| `group_ops_see_cost` | Product cost prices |
| `group_ops_see_margin` | Profit margin data (implies see_cost) |
| `group_ops_see_valuation` | Stock valuation amounts (implies see_cost) |

---

## 6. GAP ANALYSIS

### 6.1 Missing Persona References in Governance Templates

The file `ops_governance_rule_templates.xml` references personas that don't exist in `ops_persona_templates.xml`:

| Referenced Persona | Actual Persona Available | Fix Required |
|-------------------|-------------------------|--------------|
| `persona_sales_director` | `persona_sales_leader` | **Rename reference** |
| `persona_purchasing_manager` | `persona_purchase_manager` | **Rename reference** |
| `persona_operations_director` | None | **Add persona or remove rule** |
| `persona_finance_manager` | `persona_cfo` / `persona_financial_controller` | **Rename reference** |
| `persona_warehouse_manager` | `persona_logistics_manager` | **Rename reference** |
| `persona_finance_director` | `persona_cfo` | **Rename reference** |

### 6.2 Deleted Template Files

Files referenced in manifest but deleted from filesystem:
```
data/templates/ops_persona_templates.xml        ❌ DELETED
data/templates/ops_governance_rule_templates.xml ❌ DELETED
data/templates/ops_user_templates.xml           ❌ DELETED
data/templates/ops_sla_templates.xml            ❌ DELETED
```
**Action:** Remove these lines from manifest (already commented out).

### 6.3 Phase 5 Views (Disabled)

The following views are disabled due to "minor view issues":
```xml
<!-- 'views/ops_session_manager_views.xml' -->
<!-- 'views/ops_ip_whitelist_views.xml' -->
<!-- 'views/ops_security_audit_enhanced_views.xml' -->
<!-- 'views/ops_data_archival_views.xml' -->
<!-- 'views/ops_performance_monitor_views.xml' -->
```
**Note:** Models ARE loaded, only views disabled. Functionality available via ORM.

---

## 7. FEATURE INVENTORY SUMMARY

### Governance & Compliance
| Feature | Model | Status |
|---------|-------|--------|
| Strict Record Locking | `ops.governance.mixin` | ✅ Working |
| Multi-Level Approval | `ops.approval.request` | ✅ Working |
| Recall Logic | `ops.approval.recall.wizard` | ✅ Working |
| Four-Eyes Principle | `ops.governance.mixin` | ✅ Working |
| Vertical Escalation | `ops.approval.request` | ✅ Working |
| SLA Tracking | `ops.sla.instance` | ✅ Working |
| Three-Way Match | `ops.three.way.match` | ✅ Working |
| Segregation of Duties | `ops.segregation.of.duties` | ✅ Working |
| Field Visibility Control | `ops.field.visibility.rule` | ✅ Working |

### Matrix Organization
| Feature | Model | Status |
|---------|-------|--------|
| Multi-Branch Support | `ops.branch` | ✅ Working |
| Business Unit Structure | `ops.business.unit` | ✅ Working |
| Persona Management | `ops.persona` | ✅ Working |
| Delegation System | `ops.persona.delegation` | ✅ Working |
| User-Matrix Sync | `ops.persona._sync_user_access()` | ✅ Working |

### Security & Audit
| Feature | Model | Status |
|---------|-------|--------|
| API Key Management | `ops.api.key` | ✅ Working |
| Audit Logging | `ops.audit.log` | ✅ Working |
| SoD Violation Log | `ops.segregation.of.duties.log` | ✅ Working |
| Security Audit | `ops.security.audit` | ✅ Working |
| Session Management | `ops.session.manager` | ✅ Models (Views disabled) |
| IP Whitelist | `ops.ip.whitelist` | ✅ Models (Views disabled) |

---

## 8. RECOMMENDED DEPLOYMENT STEPS

### Step 1: Enable Core Personas
```xml
<!-- Uncomment in __manifest__.py -->
'data/ops_persona_templates.xml',
```
This loads 21 pre-defined personas with complete SoD authority matrix.

### Step 2: Enable Standalone Rules
```xml
<!-- Safe to enable - no persona dependencies -->
'data/ops_sla_templates.xml',
'data/ops_sod_default_rules.xml',
'data/field_visibility_rules.xml',
```

### Step 3: Fix Governance Rule References
Edit `ops_governance_rule_templates.xml`:
- Replace `persona_sales_director` → `persona_sales_leader`
- Replace `persona_purchasing_manager` → `persona_purchase_manager`
- Replace `persona_warehouse_manager` → `persona_logistics_manager`
- Replace `persona_finance_manager` → `persona_cfo`
- Replace `persona_finance_director` → `persona_cfo`
- Remove or stub `persona_operations_director` references

Then enable:
```xml
'data/ops_governance_templates.xml',
'data/ops_governance_rule_templates.xml',
```

### Step 4: Clean Up Deleted Files
Remove from manifest:
```xml
<!-- DELETE THESE LINES - Files don't exist -->
# 'data/templates/ops_persona_templates.xml',
# 'data/templates/ops_governance_rule_templates.xml',
# 'data/templates/ops_user_templates.xml',
# 'data/templates/ops_sla_templates.xml',
```

### Step 5: Post-Deployment Verification
```bash
# Test persona loading
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
personas = env['ops.persona'].search([])
print(f"Loaded {len(personas)} personas")
for p in personas[:5]:
    print(f"  - {p.code}: {p.name}")
PYTHON

# Test governance rules
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
rules = env['ops.governance.rule'].search([])
print(f"Loaded {len(rules)} governance rules")
for r in rules[:5]:
    print(f"  - {r.code}: {r.name} ({r.rule_type})")
PYTHON
```

---

## 9. MANIFEST REFERENCE (Current State)

### Data Files - ENABLED
```python
'data': [
    'data/ir_module_category.xml',
    'data/res_groups.xml',
    'security/ir.model.access.csv',
    'security/ir_rule.xml',
    'views/ops_menus.xml',
    'data/ir_sequence_data.xml',
    'data/product_request_sequence.xml',
    'data/ops_account_templates.xml',
    # ... views ...
    'data/ir_cron_data.xml',
    'data/ir_cron_archiver.xml',
    'data/sale_order_actions.xml',
    'data/ir_cron_escalation.xml',
    'data/email_templates.xml',
    'data/ops_report_templates.xml',
    'data/ops_archive_templates.xml',
    # ... reports and wizards ...
]
```

### Data Files - COMMENTED OUT (Ready to Enable)
```python
# PHASE 1: Enable these first
# 'data/ops_persona_templates.xml',

# PHASE 2: Enable after personas
# 'data/ops_sla_templates.xml',
# 'data/ops_sod_default_rules.xml',
# 'data/field_visibility_rules.xml',

# PHASE 3: Fix references then enable
# 'data/ops_governance_templates.xml',
# 'data/ops_governance_rule_templates.xml',
# 'data/ops_governance_templates_extended.xml',
# 'data/ops_governance_rule_three_way_match.xml',

# OPTIONAL: Demo data
# 'data/ops_product_templates.xml',
# 'data/product_rules.xml',

# REMOVE: Files don't exist
# 'data/templates/ops_persona_templates.xml',
# 'data/templates/ops_governance_rule_templates.xml',
# 'data/templates/ops_user_templates.xml',
# 'data/templates/ops_sla_templates.xml',
```

---

**End of Architecture Map**

*Document generated by Claude Code CLI - Comprehensive architectural audit for OPS Framework plug-and-play deployment.*
