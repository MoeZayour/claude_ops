# OPS Framework — Menu & Persona Authority Audit Report

**Audit Date:** 2026-02-05
**Auditor:** Claude Code
**Module Version:** ops_matrix_core v19.0.x, ops_matrix_accounting v19.0.18.0.0
**Database:** mz-db

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| Top-Level Menus | 12 | Audited |
| OPS Security Groups | 23 | Documented |
| Personas Defined | 18 | Active |
| IT Admin Blindness Rules | 22 | Implemented |
| Branch Isolation Rules | 36 | Implemented |
| SoD Rules | 4 | Active |
| **Ungrouped Menus (Risk)** | **180** | **Needs Review** |

**Overall Assessment:** The OPS Framework implements comprehensive security controls including IT Admin Blindness, Branch/BU isolation, and Segregation of Duties. However, **180 menus lack explicit security groups**, relying on inherited access or ACL-only protection. This represents a potential governance gap.

---

## SECTION 1: COMPLETE MENU TREE

### Top-Level Applications (Sequence Order)

| Seq | App Name | Groups | Status |
|-----|----------|--------|--------|
| 5 | Discuss | Role / User | ACTIVE |
| 10 | **Approvals** | OPS User, Role / Administrator | ACTIVE |
| 20 | Sales | ALL USERS | ACTIVE |
| 30 | Purchase | Purchase / User, Administrator | ACTIVE |
| 37 | Dashboards | ALL USERS | ACTIVE |
| 40 | Inventory | Inventory / User, Administrator | ACTIVE |
| 50 | **Accounting** | Accounting / Invoicing, Show Accounting Features | ACTIVE |
| 70 | Employees | Employees / Officer, Administrator | ACTIVE |
| 80 | **Settings** | Access Rights, Role / Administrator | ACTIVE |
| 270 | Link Tracker | Technical Features | ACTIVE |
| 500 | Apps | ALL USERS | ACTIVE |
| 1000 | Tests | ALL USERS | ACTIVE |

### OPS-Specific Menu Structure

```
📁 Approvals (seq=10) — groups: OPS User, Administrator
   ├── My Approvals          → ops.approval.dashboard     [OPS User]
   ├── Pending Approvals     → ops.approval.request       [OPS User]
   ├── Approval History      → ops.approval.request       [OPS User]
   ├── SLA Tracking          → ops.sla.instance           [OPS Manager]
   └── Violations & Alerts   → ops.segregation.of.duties.log [OPS Admin]

📁 Dashboards/OPS Matrix — groups: Executive/CEO, OPS Manager, OPS User
   ├── Executive Dashboard   → ops.executive.dashboard    [Executive, CFO]
   ├── Branch Performance    → ops.branch.dashboard       [Branch Manager, BU Leader]
   ├── BU Performance        → ops.bu.dashboard           [BU Leader, Executive, CFO]
   └── Sales Performance     → ops.sales.dashboard        [OPS Manager, Sales Manager]

📁 Inventory — groups: Inventory / User, Administrator
   └── Inter-Branch Transfers → ops.inter.branch.transfer [OPS User]

📁 Accounting — groups: Accounting / Invoicing
   ├── Asset Management/
   │   ├── Assets                → ops.asset
   │   ├── Depreciation Lines    → ops.asset.depreciation
   │   ├── Generate Entries      → ops.asset.depreciation.wizard
   │   └── Configuration/Asset Categories → ops.asset.category
   ├── Management/
   │   ├── Analytic Items        → account.analytic.line
   │   ├── Budgets               → ops.budget
   │   └── Leases (IFRS 16)      → ops.lease
   ├── Bank & Treasury/
   │   ├── Bank Reconciliation   → ops.bank.reconciliation
   │   └── Bank Statements       → account.bank.statement
   ├── Period End/
   │   ├── Fiscal Periods        → ops.fiscal.period
   │   ├── Close Checklist       → ops.period.checklist
   │   └── Branch Period Locks   → ops.fiscal.period.branch.lock
   ├── Reporting/
   │   ├── Matrix Financial Intelligence → ops.general.ledger.wizard.enhanced
   │   ├── Treasury Intelligence → ops.treasury.report.wizard
   │   ├── Asset Intelligence    → ops.asset.report.wizard
   │   ├── Balance Sheet Wizard  → ops.balance.sheet.wizard
   │   ├── PDC Reports           → ops.pdc.*
   │   └── Daily Reports/        → ops.daily.report.*
   └── Customers/Vendors/
       ├── PDC Receivable        → ops.pdc.receivable
       ├── PDC Payable           → ops.pdc.payable
       └── Follow-ups            → ops.partner.followup

📁 Settings/OPS Framework — groups: Role / Administrator
   ├── Company Structure/
   │   ├── Business Units    → ops.business.unit    [Admin, OPS Admin]
   │   ├── Branches          → ops.branch           [Admin, OPS Admin]
   │   └── Companies         → res.company          [Admin only]
   ├── Security & Governance/
   │   ├── Personas          → ops.persona          [Admin, OPS Admin]
   │   ├── Delegations       → ops.persona.delegation [Admin, OPS Admin]
   │   ├── SoD Rules         → ops.segregation.of.duties [Admin, OPS Admin]
   │   ├── Field Visibility  → ops.field.visibility.rule [Admin, OPS Admin]
   │   ├── Governance Rules  → ops.governance.rule  [Admin, OPS Manager]
   │   └── Archive Policies  → ops.archive.policy   [Admin only]
   ├── Workflow Configuration/
   │   ├── SLA Templates     → ops.sla.template     [Admin, OPS Admin]
   │   └── Dashboard Widgets → ops.dashboard.widget [Admin only]
   └── Governance/           → [OPS Manager]
       ├── Governance Rules  → ops.governance.rule
       ├── Approval Requests → ops.approval.request
       ├── SLA Tracking      → ops.sla.instance
       └── Violations Report → ops.governance.violation.report [Matrix Admin]
```

---

## SECTION 2: SECURITY GROUPS

### OPS Framework Security Groups (23 Groups)

| Group ID | Name | Purpose | Users |
|----------|------|---------|-------|
| `group_ops_user` | OPS User | Basic OPS access | 0 |
| `group_ops_manager` | OPS Manager | Branch/BU operations management | 1 |
| `group_ops_admin_power` | OPS Administrator | Full system authority | 0 |
| `group_ops_matrix_administrator` | Matrix Administrator | Dashboard/widget management | 0 |
| `group_ops_it_admin` | IT Administrator | System config, NO business data | 0 |
| `group_ops_executive` | Executive / CEO | Cross-entity read-only oversight | 0 |
| `group_ops_cfo` | CFO / Owner | Full financial access | 0 |
| `group_ops_branch_manager` | Branch Manager | Single branch operations | 0 |
| `group_ops_bu_leader` | BU Leader | Multi-branch within BU | 0 |
| `group_ops_cross_branch_bu_leader` | Cross-Branch BU Leader | All branches in BU | 0 |
| `group_ops_sales_manager` | Sales Manager | Sales + cost/margin visibility | 0 |
| `group_ops_purchase_manager` | Purchase Manager | Purchase + cost visibility | 0 |
| `group_ops_inventory_manager` | Inventory Manager | Stock + valuation visibility | 0 |
| `group_ops_finance_manager` | Finance Manager | Full financial visibility | 0 |
| `group_ops_cost_controller` | Cost Controller | Cost/margin controls | 0 |
| `group_ops_accountant` | Accountant / Controller | Full accounting access | 0 |
| `group_ops_treasury` | Treasury Officer | Cash flow, payments, PDC | 0 |
| `group_ops_compliance_officer` | Compliance Officer | Governance oversight | 0 |
| `group_ops_can_export` | Can Export Data | Secure export permission | 0 |
| `group_ops_see_cost` | Can See Product Costs | Cost price visibility | 0 |
| `group_ops_see_margin` | Can See Profit Margins | Margin data visibility | 0 |
| `group_ops_see_valuation` | Can See Stock Valuation | Inventory valuation access | 0 |
| `group_ops_product_approver` | Product Approver | Approve product requests | 0 |

### Group → Menu Access Matrix

| Group | Menus Assigned |
|-------|----------------|
| OPS User | 7 menus (Approvals, Inter-Branch Transfers, Dashboards) |
| OPS Manager | 9 menus (SLA, Dashboards, Governance) |
| OPS Administrator | 12 menus (Settings, Security, SoD, Corporate Audit) |
| OPS Branch Manager | 1 menu (Branch Performance Dashboard) |
| OPS Cost Controller | 0 menus (access via ACL only) |

---

## SECTION 3: PERSONA DEFINITIONS (18 Personas)

### Persona Hierarchy with SoD Authorities

| Code | Name | Level | Is Approver | Key Authorities |
|------|------|-------|-------------|-----------------|
| **CEO** | Chief Executive Officer | Executive | ✅ | Full authority |
| **CFO** | Chief Financial Officer | Executive | ✅ | Full financial |
| **FIN_CTRL** | Financial Controller | Executive | ✅ | Validate invoices, Post JE, Manage PDC |
| **SALES_LEADER** | Sales Leader | Director | ✅ | Cost prices, Team management |
| **SALES_MGR** | Sales Manager | Manager | ✅ | Approve orders, NO cost access |
| **PURCHASE_MGR** | Purchase Manager | Manager | ✅ | Modify products, Cost prices |
| **LOG_MGR** | Logistics Manager | Manager | ✅ | Adjust inventory |
| **TREASURY_OFF** | Treasury Officer | Manager | ✅ | Execute payments, Manage PDC |
| **CHIEF_ACCT** | Chief Accountant | Manager | ✅ | Validate invoices, Post JE |
| **HR_MGR** | HR Manager | Manager | ✅ | Leave approval only |
| **SYS_ADMIN** | System Administrator | Senior | ❌ | NO business authorities |
| **SALES_REP** | Sales Representative | Mid | ❌ | Basic sales |
| **PURCHASE_OFF** | Purchase Officer | Mid | ❌ | Create POs, Modify products |
| **LOG_CLERK** | Logistics Clerk | Mid | ❌ | Stock handling |
| **ACCOUNTANT** | Accountant | Mid | ❌ | Cost access only |
| **AR_CLERK** | AR Clerk | Mid | ❌ | Customer invoices |
| **AP_CLERK** | AP Clerk | Mid | ❌ | Vendor bills |
| **TECH_SUPPORT** | Technical Support | Mid | ❌ | No authorities |

### SoD Authority Matrix

| Authority | CEO | CFO | FIN_CTRL | TREASURY | CHIEF_ACCT | PURCHASE_MGR | LOG_MGR |
|-----------|-----|-----|----------|----------|------------|--------------|---------|
| Modify Product Master | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Access Cost Prices | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Validate Invoices | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Post Journal Entries | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Execute Payments | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Adjust Inventory | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage PDC | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## SECTION 4: SECURITY RULES

### IT Admin Blindness Rules (22 Rules)

The IT Administrator group (`group_ops_it_admin`) is **explicitly blocked** from accessing business transaction data:

| # | Model | Rule |
|---|-------|------|
| 1 | `sale.order` | IT Admin Blindness: Sale Orders |
| 2 | `sale.order.line` | IT Admin Blindness: Sale Order Lines |
| 3 | `purchase.order` | IT Admin Blindness: Purchase Orders |
| 4 | `purchase.order.line` | IT Admin Blindness: Purchase Order Lines |
| 5 | `account.move` | IT Admin Blindness: Invoices/Journal Entries |
| 6 | `account.move.line` | IT Admin Blindness: Journal Items |
| 7 | `account.payment` | IT Admin Blindness: Payments |
| 8 | `account.bank.statement` | IT Admin Blindness: Bank Statements |
| 9 | `account.bank.statement.line` | IT Admin Blindness: Bank Statement Lines |
| 10 | `account.analytic.line` | IT Admin Blindness: Analytic Lines |
| 11 | `stock.picking` | IT Admin Blindness: Stock Transfers |
| 12 | `stock.move` | IT Admin Blindness: Stock Moves |
| 13 | `stock.move.line` | IT Admin Blindness: Stock Move Lines |
| 14 | `product.pricelist` | IT Admin Blindness: Pricelists |
| 15 | `product.pricelist.item` | IT Admin Blindness: Pricelist Items |
| 16 | `ops.pdc.receivable` | IT Admin Blindness: PDC Receivable |
| 17 | `ops.pdc.payable` | IT Admin Blindness: PDC Payable |
| 18 | `ops.budget` | IT Admin Blindness: Budgets |
| 19 | `ops.budget.line` | IT Admin Blindness: Budget Lines |
| 20 | `ops.asset` | IT Admin Blindness: Assets |
| 21 | `ops.asset.category` | IT Admin Blindness: Asset Categories |
| 22 | `ops.asset.depreciation` | IT Admin Blindness: Asset Depreciation |

### Branch Isolation Rules (36 Rules)

Matrix intersection logic (Branch AND Business Unit) applied to:

| Model | Rule Type |
|-------|-----------|
| `sale.order` | Branch-level, BU Manager, Branch Manager isolation |
| `sale.order.line` | Matrix intersection (AND logic) |
| `purchase.order` | Branch-level, BU Manager, Branch Manager isolation |
| `account.move` | Branch-level, BU Manager access |
| `account.move.line` | Matrix intersection (AND logic) |
| `stock.picking` | Matrix intersection, Write restrictions |
| `stock.move` | Matrix intersection (AND logic) |
| `stock.quant` | Company-level visibility |
| `stock.warehouse` | Branch access |
| `ops.inter.branch.transfer` | Source/Dest branch visibility |
| `ops.approval.request` | Branch AND BU intersection |
| `ops.matrix.snapshot` | Branch isolation |
| `ops.budget.line` | Branch isolation via parent |
| `ops.asset.depreciation` | Branch isolation via asset |
| `product.template` | BU silo visibility |
| `product.pricelist` | Matrix pricelist visibility |

### Segregation of Duties Rules (4 Active)

| Rule | Separation |
|------|------------|
| Invoice: Create + Post Separation | Creator cannot post |
| Payment: Create + Post Separation | Creator cannot post |
| Purchase Order: Create + Confirm | Creator cannot confirm |
| Sales Order: Create + Confirm | Creator cannot confirm |

---

## SECTION 5: FINDINGS & RECOMMENDATIONS

### 🔴 CRITICAL FINDINGS

#### C1. 180 Menus Without Security Groups

**Issue:** 180 menus with actions have no explicit `groups=` assignment, meaning they rely solely on ACL protection.

**Risk:** Menu visibility is inherited from parent or defaults to all users. Users may see menus they shouldn't access, even if ACL blocks the action.

**Affected Areas:**
- All Accounting sub-menus (Asset Management, Bank & Treasury, Period End, etc.)
- Configuration menus (Fiscal Periods, Financial Report Structure, Follow-up Config)
- Customer/Vendor follow-up menus
- Automation menus (Recurring Templates, Journal Templates)

**Sample Ungrouped Menus:**
```
⚠️ Accounting/Asset Management/Assets                         → ops.asset
⚠️ Accounting/Bank & Treasury/Bank Reconciliation             → ops.bank.reconciliation
⚠️ Accounting/Configuration/Fiscal Periods                    → ops.fiscal.period
⚠️ Accounting/Customers/PDC Receivable                        → ops.pdc.receivable
⚠️ Accounting/Reporting/Daily Reports/Cash Book               → ops.daily.report
```

**Recommendation:** Add explicit `groups=` attributes to all menus with sensitive business data actions. Minimum grouping:
- Financial reports: `account.group_account_manager`
- Assets/PDC: `ops_matrix_core.group_ops_finance_manager`
- Configuration: `base.group_system`

---

### 🟡 MEDIUM FINDINGS

#### M1. Low User Assignment to OPS Groups

**Issue:** Most OPS security groups have 0 users assigned.

**Impact:** Security model is defined but not actively used in production.

**Recommendation:** Assign users to appropriate OPS groups based on their persona mapping. Create group-persona assignment documentation.

#### M2. OPS Cost Controller Has No Menu Access

**Issue:** `group_ops_cost_controller` grants 0 menu items.

**Impact:** Users with this role must rely on other implied groups for navigation.

**Recommendation:** Add relevant cost/margin reporting menus to this group.

#### M3. System Administrator Persona Has is_approver=False

**Issue:** SYS_ADMIN persona correctly has no business authorities but may need technical approval capabilities.

**Assessment:** By design - IT Admin should not approve business transactions.

---

### 🟢 LOW FINDINGS

#### L1. Duplicate Menu Definitions

Some menu items appear in multiple locations:
- SoD Rules: `Settings/OPS Framework/Security & Governance/SoD Rules` AND `Settings/OPS Framework/Security & Governance/SoD Rules/SoD Rules`
- Governance Rules: Duplicated under multiple parents

**Recommendation:** Consolidate duplicate menus for cleaner navigation.

#### L2. Disabled Legacy Menus Still in XML

The following menus are marked `active="False"` but remain in code:
- `menu_ops_matrix_root` (OPS Matrix - legacy)
- `menu_ops_reporting` (Reporting - consolidated)
- `menu_ops_financial_reports`, `menu_ops_operational_reports`
- `menu_ops_accounting_reports`

**Recommendation:** Consider removing deprecated menu definitions in a future cleanup.

---

## SECTION 6: COMPLIANCE MATRIX

### IT Admin Blindness Compliance

| Requirement | Status | Coverage |
|-------------|--------|----------|
| Sales Orders/Lines | ✅ Compliant | Blocked |
| Purchase Orders/Lines | ✅ Compliant | Blocked |
| Invoices/Bills | ✅ Compliant | Blocked |
| Payments | ✅ Compliant | Blocked |
| Bank Statements | ✅ Compliant | Blocked |
| Stock Transfers | ✅ Compliant | Blocked |
| Stock Valuation | ✅ Compliant | Blocked |
| PDC Records | ✅ Compliant | Blocked |
| Budgets | ✅ Compliant | Blocked |
| Assets | ✅ Compliant | Blocked |
| Pricelists | ✅ Compliant | Blocked |
| Analytic Lines | ✅ Compliant | Blocked |

### Branch Isolation Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Sale Order Branch Isolation | ✅ Compliant | Matrix AND logic |
| Purchase Order Branch Isolation | ✅ Compliant | Matrix AND logic |
| Invoice Branch Isolation | ✅ Compliant | Matrix AND logic |
| Stock Picking Branch Isolation | ✅ Compliant | Matrix AND logic |
| Cross-Branch BU Leader Access | ✅ Compliant | BU-wide visibility |
| Branch Manager Own-Branch Only | ✅ Compliant | Single branch restriction |

### Segregation of Duties Compliance

| SoD Rule | Status | Notes |
|----------|--------|-------|
| Invoice Create/Post | ✅ Active | Separation enforced |
| Payment Create/Post | ✅ Active | Separation enforced |
| PO Create/Confirm | ✅ Active | Separation enforced |
| SO Create/Confirm | ✅ Active | Separation enforced |
| Inventory Adjustment/Approval | ⚠️ Not Defined | Consider adding |
| Bank Reconciliation | ⚠️ Not Defined | Consider adding |

---

## SECTION 7: REMEDIATION PRIORITY

### Priority 1: Critical (Immediate)
1. **Add security groups to 180 ungrouped menus** - Prevents unauthorized menu visibility
2. **Assign users to OPS security groups** - Activate security model

### Priority 2: Medium (This Week)
1. Add menus to `group_ops_cost_controller`
2. Review and consolidate duplicate menus
3. Add SoD rules for inventory adjustments and bank reconciliation

### Priority 3: Low (Future)
1. Remove deprecated menu definitions
2. Create persona-to-group mapping documentation
3. Implement automated compliance checking

---

## APPENDIX A: Group Inheritance Tree

```
base.group_user (Role / User)
├── ops_matrix_core.group_ops_user
│   ├── ops_matrix_core.group_ops_manager
│   │   ├── ops_matrix_core.group_ops_bu_leader
│   │   │   └── ops_matrix_core.group_ops_cross_branch_bu_leader
│   │   └── ops_matrix_core.group_ops_can_export
│   ├── ops_matrix_core.group_ops_branch_manager
│   │   ├── ops_matrix_core.group_ops_sales_manager (+ see_cost, see_margin)
│   │   ├── ops_matrix_core.group_ops_purchase_manager (+ see_cost)
│   │   └── ops_matrix_core.group_ops_inventory_manager (+ see_valuation)
│   ├── ops_matrix_core.group_ops_executive (+ see_cost, margin, valuation)
│   ├── ops_matrix_core.group_ops_accountant (+ see_cost, margin, valuation)
│   ├── ops_matrix_core.group_ops_treasury
│   ├── ops_matrix_core.group_ops_compliance_officer
│   └── ops_matrix_core.group_ops_product_approver
├── ops_matrix_core.group_ops_cfo (+ manager, see_cost, margin, valuation)
└── ops_matrix_core.group_ops_it_admin (NO business data access)

base.group_system (Role / Administrator)
└── ops_matrix_core.group_ops_admin_power
    └── ops_matrix_core.group_ops_matrix_administrator
```

---

**Report Generated:** 2026-02-05
**Auditor:** Claude Code
**Next Audit:** After remediation of Critical findings
