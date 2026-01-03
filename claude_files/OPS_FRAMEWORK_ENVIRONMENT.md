# OPS Framework - Development Environment Context

**Purpose**: Single source of truth for all development sessions  
**Version**: 1.0  
**Last Updated**: January 3, 2026  
**Project Status**: Active Development - Phase 1  

---

## PROJECT IDENTITY

**Name**: OPS Matrix Framework for Odoo 19 Community Edition  
**Version**: 19.0.1.3 (next: 19.0.1.4)  
**Tagline**: Enterprise-grade multi-branch management for companies with zero technical knowledge  
**Classification**: Production Ready, Production Hardened  

---

## DEVELOPMENT APPROACH

### Code Location Strategy

**CRITICAL DECISION** (as of Jan 3, 2026):
- **Codebase**: Lives on HOST SERVER at `/home/claude/ops-framework-dev-main/`
- **Documentation**: Lives in CLAUDE.AI PROJECT for easy reference
- **Reason**: Direct access to code for development, but docs in chat for quick lookup

### File Organization

```
HOST SERVER: /home/claude/ops-framework-dev-main/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ addons/
Ã¢"â€š   Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_matrix_core/              # Core framework
Ã¢"â€š   Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_matrix_reporting/         # Analytics & dashboards  
Ã¢"â€š   Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_matrix_api/               # RESTful API
Ã¢"â€š   Ã¢""Ã¢"â‚¬Ã¢"â‚¬ ops_matrix_governance/        # Approval workflows
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ [...other files...]

CLAUDE.AI PROJECT: 
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ OPS_FRAMEWORK_ENVIRONMENT.md     # THIS FILE (master context)
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ Comprehensive_Review             # Marketing-style overview
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ OPS_FRAMEWORK_USER_EXPERIENCE_v1_2.md  # Complete UX spec
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ OPS_FRAMEWORK_TODO_v1_1.md       # Development tracking
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ OPS_FRAMEWORK_HANDOFF_v1_0.md    # Session handoff notes
```

---

## CORE PHILOSOPHY

### The Four Pillars

1. **LITE** - Zero configuration needed, works out of the box
2. **DYNAMIC** - Personas can be combined for small companies
3. **PLUG-AND-PLAY** - Preloaded data, archived templates to activate
4. **ZERO-TECH** - Designed for users with no technical knowledge

### Security-First Principles

```
LOCKED BY DEFAULT:
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ Cost prices     Ã¢â€ ' Requires explicit grant
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ Profit margins  Ã¢â€ ' Requires explicit grant  
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ Stock valuation Ã¢â€ ' Requires explicit grant
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ Data export     Ã¢â€ ' Limited to viewed document only
```

### Critical Architectural Distinctions

**System Admin vs IT Admin** (THE KEY DIFFERENTIATOR):

| Aspect | System Admin (P00) | IT Admin (P01) |
|--------|-------------------|----------------|
| **Purpose** | Break-glass emergency access | Daily IT operations |
| **Business Data** | Ã¢Å“â€¦ Can see everything | Ã¢Å’ BLIND to all business data |
| **Odoo Group** | base.group_system | ops.group_it_admin |
| **Use Case** | External consultant, Owner | Internal IT staff |
| **Frequency** | Emergency only | Daily use |

**Why This Matters**: Internal IT staff should NOT see invoices, orders, payments, bank balances. They configure the system but don't access sensitive business information.

---

## ARCHITECTURE OVERVIEW

### The Three Pillars

```
Ã¢"Å’Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"  Ã¢"Å’Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"  Ã¢"Å’Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"
Ã¢"â€š   BRANCHES    Ã¢"â€š  Ã¢"â€š BUSINESS UNITSÃ¢"â€š  Ã¢"â€š   PERSONAS    Ã¢"â€š
Ã¢"â€š  (Data Silos) Ã¢"â€š  Ã¢"â€š (Oversight)   Ã¢"â€š  Ã¢"â€š (Identity)    Ã¢"â€š
Ã¢""Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Â¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Ëœ  Ã¢""Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Â¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Ëœ  Ã¢""Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Â¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Ëœ
        Ã¢"â€š                  Ã¢"â€š                  Ã¢"â€š
        Ã¢""Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Â¼Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Ëœ
                           Ã¢"â€š
                  Ã¢"Å’Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢â€“Â¼Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"
                  Ã¢"â€š   GOVERNANCE    Ã¢"â€š
                  Ã¢"â€š   ENGINE        Ã¢"â€š
                  Ã¢""Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"â‚¬Ã¢"Ëœ
```

**Branches**: Physical/operational locations - enforces data isolation  
**Business Units**: Logical divisions - enables consolidated oversight  
**Personas**: Role templates - defines access rights dynamically  

---

## PERSONAS (18 Total)

### System Level (2)
- **P00** - System Admin (break-glass, bypasses all rules)
- **P01** - IT Admin (BLIND to business data, config only)

### Executive Level (2)  
- **P02** - Executive/CEO (read-only oversight)
- **P03** - CFO/Owner (full financial access)

### BU Level (1)
- **P04** - BU Leader (cross-branch within BU)

### Branch Management (5)
- **P05** - Branch Manager
- **P06** - Sales Manager
- **P07** - Purchase Manager
- **P08** - Inventory Manager  
- **P09** - Finance Manager

### User Level (8)
- **P10** - Sales Representative
- **P11** - Purchase Officer
- **P12** - Warehouse Operator
- **P13** - AR Clerk
- **P14** - AP Clerk
- **P15** - Treasury Officer
- **P16** - Accountant/Controller
- **P17** - HR/Payroll Specialist

**Persona Combinations**: For small companies, personas can be combined (e.g., P07 Purchase Manager + P08 Inventory Manager assigned to one person).

---

## SECURITY GROUPS (18 Total)

### Base Groups (3)
- `group_ops_user` - Basic OPS access
- `group_ops_manager` - Branch/BU management
- `group_ops_admin` - OPS configuration

### Admin Groups (2)
- `group_ops_it_admin` - IT Admin (BLIND to business data)
- `group_ops_matrix_administrator` - Full matrix config

### Data Visibility Groups (3)  
- `group_ops_see_cost` - Can see product costs
- `group_ops_see_margin` - Can see profit margins
- `group_ops_see_valuation` - Can see stock valuation

### Executive Groups (3)
- `group_ops_executive` - Executive/CEO
- `group_ops_cfo` - CFO/Owner
- `group_ops_bu_leader` - BU Leader

### Functional Groups (7)
- `group_ops_product_approver`
- `group_ops_sales_manager`
- `group_ops_purchase_manager`
- `group_ops_inventory_manager`
- `group_ops_finance_manager`
- `group_ops_accountant`
- `group_ops_treasury`

---

## GOVERNANCE RULES (25 Templates)

All rules stored as **archived templates** - users activate what they need.

### Categories:
- **Sales Order**: Discount thresholds, amount thresholds
- **Margin**: Minimum margin enforcement
- **Purchase Order**: Amount-based approvals
- **Payment**: Multi-level authorization
- **Inventory**: Adjustment and scrap approvals
- **Invoice**: Credit note controls
- **Master Data**: Credit limits, payment terms, blocks
- **User Management**: Creation and permission changes
- **Transfers**: Cross-BU, inter-branch
- **Assets**: Disposal approvals

---

## CURRENT STATE (as of Jan 3, 2026)

### Ã¢Å“â€¦ COMPLETED

1. **18 Persona Templates** - All defined in `ops_persona_templates.xml`
2. **25 Governance Rules** - All defined in `ops_governance_rule_templates.xml`  
3. **IT Admin Blindness** - 20 record rules blocking business data access
4. **Cost/Margin Lock** - All views updated with group restrictions

### Ã°Å¸"Â´ NEXT PRIORITY

5. **Complete Document Lock During Approval**
   - No edit, no print while pending
   - Recall with reason
   - Reject with mandatory reason
   - Workflow visible in chatter

6. **Excel Import for SO Lines**
   - Section|Model|Qty format
   - All-or-nothing validation
   - Template download
   - Error reporting

---

## KEY FILES & LOCATIONS

### Core Module (`ops_matrix_core`)

**Data Files**:
```
data/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ res_groups.xml                       # 18 security groups
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir_module_category.xml               # Module categories
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir_sequence_data.xml                 # Sequences
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir_cron_data.xml                     # Scheduled jobs
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_asset_data.xml                   # Asset categories
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ templates/
    Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_persona_templates.xml        # 18 personas (archived)
    Ã¢""Ã¢"â‚¬Ã¢"â‚¬ ops_governance_rule_templates.xml # 25 rules (archived)
```

**Security Files**:
```
security/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir.model.access.csv                  # Model access rights
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir_rule_branch.xml                   # Branch isolation rules
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ir_rule_bu.xml                       # BU aggregation rules
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ ir_rule_it_admin.xml                 # IT Admin blindness (20 rules)
```

**Key Models**:
```
models/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_branch.py                        # Branch master
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_business_unit.py                 # BU master
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_persona.py                       # Persona definitions
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_governance_rule.py               # Approval rules
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_approval_request.py              # Approval workflow
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ res_users.py                         # User extensions (has_ops_authority)
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ [...other models...]
```

### Views Modified for Security

```
views/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ sale_order_views.xml                 # Cost/margin restricted
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ product_views.xml                    # Cost restricted + tree/kanban
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ [...other views...]

../ops_matrix_reporting/views/
Ã¢"Å“Ã¢"â‚¬Ã¢"â‚¬ ops_inventory_analysis_views.xml     # Valuation restricted
Ã¢""Ã¢"â‚¬Ã¢"â‚¬ ops_sales_analysis_views.xml         # Margin restricted
```

---

## DEVELOPMENT WORKFLOW

### Starting a New Session

1. **Read this file first** - Get current state
2. **Check TODO_v1_1.md** - See priority items
3. **Reference USER_EXPERIENCE_v1_2.md** - For UX requirements
4. **Code location**: `/home/claude/ops-framework-dev-main/`

### Before Coding

1. Use `view` tool to read relevant SKILL.md files
2. Understand which personas are affected
3. Check if security groups need updates
4. Plan record rule changes

### After Coding

1. Update TODO with completed items
2. Test with multiple personas
3. Create/update handoff document
4. Bump version in `__manifest__.py`

---

## INSTALLATION BLOCKERS (RESOLVED)

### Ã¢Å“â€¦ Fixed Issues

1. **Missing data files** - All created (11 files)
2. **Enterprise dependency** - Removed `spreadsheet_dashboard`
3. **Manifest data loading order** - Fixed sequence
4. **Missing personas** - All 18 now defined
5. **Missing governance rules** - All 25 now defined

### Current Installation Status

**Should install cleanly** with:
```bash
odoo-bin -d DATABASE -i ops_matrix_core --stop-after-init
```

---

## CRITICAL FEATURES ALREADY IMPLEMENTED

These exist in codebase and should be **verified/enhanced**, not rewritten:

1. **SLA Management** - ops_sla_template.py, ops_sla_instance.py, ops_sla_mixin.py
2. **Delegation of Authority** - ops_persona_delegation.py
3. **PDC Management** - ops_pdc.py (Post-Dated Checks)
4. **Approval Workflow** - ops_approval_request.py (has basic approval_locked field)
5. **Branch/BU Isolation** - ir_rule_branch.xml, ir_rule_bu.xml
6. **Audit Logging** - ops_audit_log.py

---

## PLANNED FEATURES (NOT YET STARTED)

### High Priority
- Ã¢Å’ Complete document lock during approval
- Ã¢Å’ Excel import for Sales/Purchase order lines
- Ã¢Å’ Three-way match enforcement (PO Ã¢â€ " Receipt Ã¢â€ " Bill)
- Ã¢Å’ Auto-escalation of approvals
- Ã¢Å’ Data export security hooks

### Medium Priority
- Ã¢Å’ Chart of Accounts preloading
- Ã¢Å’ Report auto-configuration
- Ã¢Å’ Scheduled report delivery
- Ã¢Å’ Auto-create default Branch/BU on company creation

### Low Priority  
- Ã¢Å’ Shipping integrations (DHL, Aramex, FedEx)
- Ã¢Å’ 2FA enforcement per persona
- Ã¢Å’ IP whitelist per user

---

## TESTING CHECKLIST

Before any deployment:

### IT Admin Blindness
- [ ] IT Admin cannot view Sales Orders
- [ ] IT Admin cannot view Purchase Orders  
- [ ] IT Admin cannot view Invoices/Bills
- [ ] IT Admin cannot view Payments
- [ ] IT Admin cannot view Bank Statements
- [ ] IT Admin CAN create/manage users
- [ ] IT Admin CAN configure personas/governance rules

### Cost/Margin Lock
- [ ] Sales Rep CANNOT see cost in SO lines
- [ ] Sales Rep CANNOT see margin columns
- [ ] Sales Manager CAN see cost and margin
- [ ] Warehouse CANNOT see product cost
- [ ] Accountant CAN see all cost/margin/valuation

### Persona Authority
- [ ] User with no personas cannot see cost
- [ ] User with Sales Manager persona CAN see cost/margin  
- [ ] Combined personas grant union of authorities

---

## QUICK REFERENCE COMMANDS

### View Codebase Structure
```bash
view /home/claude/ops-framework-dev-main/addons/ops_matrix_core
```

### Check Current Personas
```bash
view /home/claude/ops-framework-dev-main/addons/ops_matrix_core/data/templates/ops_persona_templates.xml
```

### Check Security Groups
```bash
view /home/claude/ops-framework-dev-main/addons/ops_matrix_core/data/res_groups.xml
```

### Check IT Admin Rules
```bash
view /home/claude/ops-framework-dev-main/addons/ops_matrix_core/security/ir_rule_it_admin.xml
```

---

## COMMON QUESTIONS & ANSWERS

**Q: Where is the code?**  
A: `/home/claude/ops-framework-dev-main/` on the host server. Use `view` tool to access.

**Q: How many personas are there?**  
A: 18 total, spanning System (2), Executive (2), BU (1), Branch Mgmt (5), User (8).

**Q: What's the difference between System Admin and IT Admin?**  
A: System Admin (P00) = break-glass, sees everything. IT Admin (P01) = daily IT ops, BLIND to business data.

**Q: Are cost and margin visible by default?**  
A: NO. Locked by default for EVERYONE. Must be granted via security groups.

**Q: Can personas be combined?**  
A: YES. Small companies can assign multiple personas to one user (e.g., Purchase Manager + Inventory Manager).

**Q: Where are the governance rules?**  
A: In `ops_governance_rule_templates.xml` - 25 rules, all archived. Users activate what they need.

**Q: What's the current version?**  
A: 19.0.1.3 (next will be 19.0.1.4 after current work is deployed).

**Q: What's next to build?**  
A: Priority #5 - Complete Document Lock During Approval. See TODO_v1_1.md.

---

## REMEMBER THESE PRINCIPLES

1. **LITE** - Don't make users configure things
2. **DYNAMIC** - Support persona combinations
3. **SECURITY-FIRST** - Lock by default, grant access explicitly
4. **ZERO-TECH** - Assume users have no technical knowledge
5. **ARCHIVED TEMPLATES** - Provide examples, not enforced defaults

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-03 | Initial environment file created |

---

**END OF ENVIRONMENT CONTEXT**

---

## USAGE IN FUTURE SESSIONS

**Start every session with:**
```
I'm continuing work on the OPS Framework. 

Current state: [brief description]
Working on: [task from TODO]

Code location: /home/claude/ops-framework-dev-main/
Documentation: See project files (OPS_FRAMEWORK_ENVIRONMENT.md, etc.)
```

This ensures context continuity across all development sessions.
