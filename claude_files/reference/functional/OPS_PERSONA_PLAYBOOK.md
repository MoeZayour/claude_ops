# OPS Persona Playbook

> Comprehensive reference for every persona in the OPS Matrix Framework.
> Generated: 2026-02-13 | Source: `ops_matrix_core/data/ops_persona_templates.xml`

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Persona Hierarchy](#persona-hierarchy)
3. [Security Group Reference](#security-group-reference)
4. [Persona Catalog (18 Personas)](#persona-catalog)
   - [P01 - Financial Controller (FIN_CTRL)](#p01---financial-controller-fin_ctrl)
   - [P02 - Chief Executive Officer (CEO)](#p02---chief-executive-officer-ceo)
   - [P03 - Chief Financial Officer (CFO)](#p03---chief-financial-officer-cfo)
   - [P04 - Sales Leader (SALES_LEADER)](#p04---sales-leader-sales_leader)
   - [P05 - Sales Manager (SALES_MGR)](#p05---sales-manager-sales_mgr)
   - [P06 - Purchase Manager (PURCHASE_MGR)](#p06---purchase-manager-purchase_mgr)
   - [P07 - Logistics Manager (LOG_MGR)](#p07---logistics-manager-log_mgr)
   - [P08 - Treasury Officer (TREASURY_OFF)](#p08---treasury-officer-treasury_off)
   - [P09 - HR Manager (HR_MGR)](#p09---hr-manager-hr_mgr)
   - [P10 - Chief Accountant (CHIEF_ACCT)](#p10---chief-accountant-chief_acct)
   - [P11 - System Administrator (SYS_ADMIN)](#p11---system-administrator-sys_admin)
   - [P12 - Sales Representative (SALES_REP)](#p12---sales-representative-sales_rep)
   - [P13 - Purchase Officer (PURCHASE_OFF)](#p13---purchase-officer-purchase_off)
   - [P14 - Logistics Clerk (LOG_CLERK)](#p14---logistics-clerk-log_clerk)
   - [P15 - Accountant (ACCOUNTANT)](#p15---accountant-accountant)
   - [P16 - Accounts Receivable Clerk (AR_CLERK)](#p16---accounts-receivable-clerk-ar_clerk)
   - [P17 - Accounts Payable Clerk (AP_CLERK)](#p17---accounts-payable-clerk-ap_clerk)
   - [P18 - Technical Support (TECH_SUPPORT)](#p18---technical-support-tech_support)
5. [SoD Authority Matrix](#sod-authority-matrix)
6. [IT Admin Blindness Summary](#it-admin-blindness-summary)
7. [Field Visibility Rules Catalog](#field-visibility-rules-catalog)
8. [Delegation System](#delegation-system)
9. [Golden User Templates](#golden-user-templates)
10. [Governance & Approval Limits](#governance--approval-limits)
11. [Seed Data Requirements](#seed-data-requirements)

---

## Architecture Overview

The OPS Persona system implements a **multi-layered security model**:

1. **Persona Definition** (`ops.persona`) -- Defines role identity, SoD authority flags, and hierarchy
2. **Persona-to-Group Mapping** (`res_users_group_mapper.py`) -- Maps each persona code to Odoo security groups
3. **Security Groups** (`res_groups.xml`) -- OPS-specific groups with inheritance chains
4. **Record Rules** (`ir.rule`) -- Branch isolation, IT Admin blindness, manager overrides
5. **ACL Rules** (`ir.model.access.csv`) -- Model-level CRUD permissions per group
6. **Field Visibility** (`ops.field.visibility.rule`) -- Column-level data hiding
7. **Governance Rules** (`ops.governance.rule`) -- Transaction-level limits, approvals, blocks

**Key principle**: A user's effective authority is the **union** of ALL their assigned personas. If ANY persona grants an authority flag, the user has it.

---

## Persona Hierarchy

```
                    CEO (executive)
                     |
                    CFO (executive)
                     |
            Financial Controller (executive) [ANCHOR - No Parent]
           /    |     |     |     |     |    \
          /     |     |     |     |     |     \
  Sales     Sales   Purchase  Logistics  Treasury  HR     Chief    System
  Leader    Mgr     Mgr       Mgr        Officer   Mgr   Acct     Admin
  (dir)    (mgr)   (mgr)     (mgr)      (mgr)    (mgr)  (mgr)   (senior)
    |                |         |                           |
  Sales            Purchase  Logistics                  Accountant
  Rep              Officer   Clerk                      (mid)
  (mid)            (mid)     (mid)
                                               AR Clerk    AP Clerk
                                               (mid)       (mid)

  Technical Support (mid) -- NO PARENT
```

**Notes**:
- CEO and CFO have NO parent_id set in the template (top-level executives)
- Financial Controller is the SoD Anchor -- all manager personas report to it
- Technical Support has no parent_id (standalone support role)
- AR Clerk and AP Clerk report directly to Financial Controller

---

## Security Group Reference

### OPS Core Groups (Hierarchy)

| Group XML ID | Name | Inherits From |
|---|---|---|
| `group_ops_user` | OPS User | `base.group_user` |
| `group_ops_manager` | OPS Manager | `group_ops_user` |
| `group_ops_admin_power` | OPS Administrator | `group_ops_manager` |
| `group_ops_matrix_administrator` | Matrix Administrator | `group_ops_admin_power` |

### Functional Manager Groups

| Group XML ID | Name | Inherits From |
|---|---|---|
| `group_ops_branch_manager` | OPS Branch Manager | `group_ops_user` |
| `group_ops_bu_leader` | Business Unit Leader | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_margin` |
| `group_ops_cross_branch_bu_leader` | Cross-Branch BU Leader | `group_ops_bu_leader` |
| `group_ops_sales_manager` | Sales Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin` |
| `group_ops_purchase_manager` | Purchase Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_cost` |
| `group_ops_inventory_manager` | Inventory Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_valuation` |
| `group_ops_finance_manager` | Finance Manager | `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` |
| `group_ops_cost_controller` | OPS Cost Controller | `group_ops_finance_manager` |

### Executive Groups

| Group XML ID | Name | Inherits From |
|---|---|---|
| `group_ops_executive` | Executive / CEO | `group_ops_user`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` |
| `group_ops_cfo` | CFO / Owner | `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` |

### Specialized Groups

| Group XML ID | Name | Inherits From |
|---|---|---|
| `group_ops_it_admin` | IT Administrator | `base.group_user` |
| `group_ops_accountant` | Accountant / Controller | `group_ops_user`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` |
| `group_ops_treasury` | Treasury Officer | `group_ops_user` |
| `group_ops_compliance_officer` | Compliance Officer | `group_ops_user` |
| `group_ops_product_approver` | Product Approver | `group_ops_user` |
| `group_ops_see_cost` | Can See Product Costs | (standalone) |
| `group_ops_see_margin` | Can See Profit Margins | `group_ops_see_cost` |
| `group_ops_see_valuation` | Can See Stock Valuation | `group_ops_see_cost` |
| `group_ops_price_manager` | Price Manager | (standalone) |
| `group_ops_can_export` | Can Export Data | `group_ops_manager` |

---

## Persona Catalog

---

### P01 - Financial Controller (FIN_CTRL)

**XML ID**: `ops_matrix_core.persona_financial_controller`

| Field | Value |
|---|---|
| **Code** | `FIN_CTRL` |
| **Job Level** | Executive |
| **Parent** | None (SoD Anchor) |
| **Is Approver** | Yes |
| **Is Matrix Administrator** | No |
| **Can Manage Team** | Yes |

**Description**: Final authority for Finance, Sales, and Purchase operations. Validates invoices and posts journal entries. Cannot execute payments (separation from Treasury).

#### Auto-Mapped Odoo Groups (from `_map_persona_to_groups`)

| Group | Purpose |
|---|---|
| `account.group_account_manager` | Billing Manager |
| `account.group_account_user` | Billing |
| `sale.group_sale_manager` | Sales Administrator |
| `purchase.group_purchase_manager` | Purchase Manager |
| `ops_matrix_core.group_ops_executive` | OPS Executive (implies: see cost, margin, valuation) |
| `ops_matrix_core.group_ops_cost_controller` | Cost Controller (implies: Finance Manager) |
| `ops_matrix_core.group_ops_price_manager` | Price Manager (can modify unit prices) |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | YES |
| Validate Invoices | YES |
| Post Journal Entries | YES |
| Execute Payments | NO |
| Adjust Inventory | NO |
| Manage PDC | YES |

#### Capabilities (CAN DO)

- View and manage all sales, purchase, and accounting operations
- Validate and post customer/vendor invoices
- Post accounting journal entries
- Manage Post Dated Checks (PDC Receivable and Payable)
- Approve orders, expenses, and leave
- Access all financial reports (GL, TB, P&L, BS, Cash Flow, Aged reports)
- Access Assets & Planning (assets, depreciation, budgets, IFRS 16 leases)
- Access Period Close operations (fiscal periods, checklist, branch locks)
- View product cost prices, margins, and stock valuation
- Inter-branch transfers
- Modify unit prices on sale order lines (Price Manager group)
- Run Consolidation Intelligence reports
- Access all accounting configuration

#### Restrictions (CANNOT DO)

- Execute vendor payments (SoD separation from Treasury)
- Adjust inventory quantities (SoD separation from Logistics)
- Modify product master data (cost, suppliers)
- Access Settings > OPS Framework (requires group_system)
- Create/manage users (requires group_system)
- Access KPI Configuration (requires OPS Admin Power or IT Admin)

#### Menu Access

| Menu | Visible? |
|---|---|
| Approvals | Yes |
| Sales | Yes |
| Purchase | Yes |
| Inventory | Yes (limited) |
| Accounting > Operations | Yes (all sub-menus) |
| Accounting > Assets & Planning | Yes (all sub-menus) |
| Accounting > Reporting | Yes (all reports) |
| Accounting > Configuration | Yes |
| Accounting > Customers > PDC | Yes |
| Accounting > Vendors > PDC | Yes |
| KPI Center | Yes (read boards) |
| KPI Configuration | No |
| Settings > OPS Framework | No |
| Dashboards > OPS Matrix | Yes |

#### Delegation

- `can_be_delegated`: True (default)
- Can delegate own persona to another user
- Can receive delegations from other personas

#### Golden User Template

Template: `user_template_financial_controller` (login: `tmpl_finance`)
Groups: `base.group_user`, `account.group_account_manager`

---

### P02 - Chief Executive Officer (CEO)

**XML ID**: `ops_matrix_core.persona_ceo`

| Field | Value |
|---|---|
| **Code** | `CEO` |
| **Job Level** | Executive |
| **Parent** | None |
| **Is Approver** | Yes |
| **Is Matrix Administrator** | Yes |
| **Can Manage Team** | Yes |

**Description**: Highest executive responsible for overall company operations, strategy, and decision-making.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `sales_team.group_sale_manager` | Sales Manager |
| `account.group_account_manager` | Billing Manager |
| `stock.group_stock_manager` | Inventory Manager |
| `purchase.group_purchase_manager` | Purchase Manager |
| `ops_matrix_core.group_ops_executive` | OPS Executive (implies: see cost, margin, valuation) |

**Note**: `group_erp_manager` intentionally excluded -- CEO must NOT create users. Only SYS_ADMIN can create users because user creation requires assigning branch/BU/persona which are locked to group_system.

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | YES |
| Access Cost Prices | YES |
| Validate Invoices | YES |
| Post Journal Entries | YES |
| Execute Payments | YES |
| Adjust Inventory | YES |
| Manage PDC | YES |

**CEO has FULL SoD authority across all domains.**

#### Capabilities (CAN DO)

- Full executive oversight across all branches and business units
- All financial operations (invoices, journal entries, payments, PDC)
- All inventory operations (adjustments, stock management)
- All sales and purchase operations
- Modify product master data
- Approve all transaction types (orders, expenses, leave)
- Access all financial reports
- Matrix Administrator access (configure matrix structure)
- Access all menus available to OPS Executive group

#### Restrictions (CANNOT DO)

- Create/manage users (group_erp_manager intentionally excluded)
- Access Settings > OPS Framework admin configuration (requires group_system)
- Access KPI Configuration (not in OPS Admin Power group by default)

#### Menu Access

All operational menus visible. Reporting fully accessible. No Settings > OPS Framework.

---

### P03 - Chief Financial Officer (CFO)

**XML ID**: `ops_matrix_core.persona_cfo`

| Field | Value |
|---|---|
| **Code** | `CFO` |
| **Job Level** | Executive |
| **Parent** | None |
| **Is Approver** | Yes |
| **Can Manage Team** | Yes |

**Description**: Executive responsible for financial planning, management, reporting, and accounting oversight.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_manager` | Billing Manager |
| `account.group_account_user` | Billing |
| `ops_matrix_core.group_ops_executive` | OPS Executive |
| `ops_matrix_core.group_ops_cost_controller` | Cost Controller (implies Finance Manager) |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |
| `ops_matrix_core.group_ops_see_margin` | See Margins |
| `ops_matrix_core.group_ops_price_manager` | Price Manager |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | YES |
| Access Cost Prices | YES |
| Validate Invoices | YES |
| Post Journal Entries | YES |
| Execute Payments | YES |
| Adjust Inventory | YES |
| Manage PDC | YES |

**CFO has FULL SoD authority across all domains.**

#### Capabilities (CAN DO)

- Full financial authority (invoices, journal entries, payments)
- All accounting operations and reporting
- Budget management and approval
- Asset management and depreciation
- Treasury operations (PDC, cash management)
- Inventory adjustments and valuation oversight
- Product master data modifications
- Consolidation Intelligence reports
- Period close operations
- Approve orders and expenses
- Modify unit prices (Price Manager)
- All financial report access

#### Restrictions (CANNOT DO)

- Not mapped to `sales_team.group_sale_manager` (no direct Sales Manager access)
- Not mapped to `stock.group_stock_manager` (no Inventory Manager)
- Not mapped to `purchase.group_purchase_manager` (no Purchase Manager)
- Cannot create/manage users
- Cannot access Settings > OPS Framework

#### Menu Access

Full Accounting app access including all Operations, Assets & Planning, Reporting, Configuration sub-menus. Consolidation Intelligence visible.

---

### P04 - Sales Leader (SALES_LEADER)

**XML ID**: `ops_matrix_core.persona_sales_leader`

| Field | Value |
|---|---|
| **Code** | `SALES_LEADER` |
| **Job Level** | Director |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Is BU Leader** | Yes |
| **Can Manage Team** | Yes |

**Description**: Senior sales executive responsible for sales strategy, team leadership, and revenue targets.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `sales_team.group_sale_manager` | Sales Manager |
| `sale.group_sale_manager` | Sales Administrator |
| `ops_matrix_core.group_ops_bu_leader` | BU Leader (implies: Branch Manager, OPS Manager, See Margin) |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |
| `ops_matrix_core.group_ops_price_manager` | Price Manager |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | YES |
| Validate Invoices | NO |
| Post Journal Entries | NO |
| Execute Payments | NO |
| Adjust Inventory | NO |
| Manage PDC | NO |

#### Capabilities (CAN DO)

- Full sales management (create, edit, approve sales orders)
- View cost prices and profit margins
- Modify unit prices on sale order lines (Price Manager)
- Approve orders and expenses
- Manage sales team across multiple branches (BU Leader)
- Cross-branch visibility within their business unit
- Access OPS Manager-level features (via BU Leader inheritance)
- Access Daily Books (Day Book via BU Leader group)
- View budgets (read-only via OPS User)

#### Restrictions (CANNOT DO)

- Validate invoices
- Post journal entries
- Execute payments
- Adjust inventory
- Manage PDC
- Modify product master data
- Access Accounting > Operations (journal entries, bank reconciliation)
- Access Assets & Planning
- Access most Accounting Reporting (no accountant/finance_manager/cfo group)

#### Menu Access

| Menu | Visible? |
|---|---|
| Sales | Yes (full) |
| Approvals | Yes |
| Accounting | Limited (no Operations, no Assets) |
| Daily Books > Day Book | Yes (via BU Leader) |
| Inventory | Limited (basic stock) |
| KPI Center | Yes (read boards) |

---

### P05 - Sales Manager (SALES_MGR)

**XML ID**: `ops_matrix_core.persona_sales_manager`

| Field | Value |
|---|---|
| **Code** | `SALES_MGR` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Can Manage Team** | Yes |

**Description**: Manager responsible for sales team coordination, customer relationships, and deal closure. Cannot access cost prices to protect margin confidentiality.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `sales_team.group_sale_manager` | Sales Manager |
| `sale.group_sale_salesman_all_leads` | See All Leads |
| `ops_matrix_core.group_ops_manager` | OPS Manager (implies OPS User) |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | NO |
| Validate Invoices | NO |
| Post Journal Entries | NO |
| Execute Payments | NO |
| Adjust Inventory | NO |
| Manage PDC | NO |

**Sales Manager has NO SoD authorities. Pure sales operational role.**

#### Capabilities (CAN DO)

- Full sales management (create, edit, approve sales orders)
- See all leads/opportunities
- Approve orders
- Manage sales team
- OPS Manager access (full CRUD on most OPS models)
- Manager override on branch-isolated record rules (sees all branches)
- Governance rule management

#### Restrictions (CANNOT DO)

- View cost prices (explicitly blocked for margin confidentiality)
- View profit margins
- View stock valuation
- Validate invoices or post journal entries
- Execute payments
- Manage PDC
- Adjust inventory
- Modify unit prices (no Price Manager group)
- Access Accounting > Operations or Reporting

#### Field Visibility (when rules enabled)

Sales Manager inherits `sales_team.group_sale_manager` but NOT `group_ops_see_cost` or `group_ops_see_margin`. Cost and margin fields are hidden from this persona's view.

#### Menu Access

| Menu | Visible? |
|---|---|
| Sales | Yes (full) |
| Approvals | Yes |
| Accounting | No (Operations, Assets, Reporting all require accounting groups) |
| Inventory | No direct access |
| KPI Center | Yes |
| Settings > OPS Framework > Governance Rules | Yes (OPS Manager) |

#### Golden User Template

Template: `user_template_branch_manager` (login: `tmpl_manager`)
Groups: `base.group_user`, `account.group_account_user`, `sales_team.group_sale_manager`

---

### P06 - Purchase Manager (PURCHASE_MGR)

**XML ID**: `ops_matrix_core.persona_purchase_manager`

| Field | Value |
|---|---|
| **Code** | `PURCHASE_MGR` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Can Manage Team** | Yes |

**Description**: Approves purchase orders and manages procurement strategy. Full access to product costs and suppliers.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `purchase.group_purchase_manager` | Purchase Manager |
| `stock.group_stock_user` | Inventory User |
| `ops_matrix_core.group_ops_manager` | OPS Manager |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | YES |
| Access Cost Prices | YES |
| Validate Invoices | NO |
| Post Journal Entries | NO |
| Execute Payments | NO |
| Adjust Inventory | NO |
| Manage PDC | NO |

#### Capabilities (CAN DO)

- Full purchase management (create, edit, approve POs)
- Modify product master data (costs, suppliers)
- View product cost prices
- Basic inventory operations (stock user)
- Approve orders, expenses, and leave
- OPS Manager access (manager override on branch isolation)

#### Restrictions (CANNOT DO)

- Validate invoices or post journal entries
- Execute payments
- Manage PDC
- Adjust inventory (only stock user, not stock manager)
- View profit margins or stock valuation
- Access Accounting Operations or Reporting

#### Menu Access

| Menu | Visible? |
|---|---|
| Purchase | Yes (full) |
| Inventory | Yes (user-level) |
| Approvals | Yes |
| KPI Center | Yes |
| Accounting | No |

---

### P07 - Logistics Manager (LOG_MGR)

**XML ID**: `ops_matrix_core.persona_logistics_manager`

| Field | Value |
|---|---|
| **Code** | `LOG_MGR` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Is Branch Manager** | Yes |
| **Can Manage Team** | Yes |

**Description**: Manager responsible for warehouse operations, inventory management, and logistics coordination. Authorizes inventory adjustments.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `stock.group_stock_manager` | Inventory Manager |
| `ops_matrix_core.group_ops_branch_manager` | Branch Manager |
| `ops_matrix_core.group_ops_manager` | OPS Manager |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | YES |
| Validate Invoices | NO |
| Post Journal Entries | NO |
| Execute Payments | NO |
| Adjust Inventory | YES |
| Manage PDC | NO |

#### Capabilities (CAN DO)

- Full inventory management (receipts, deliveries, adjustments, scrap)
- Authorize inventory adjustments and write-offs
- View cost prices
- Branch Manager authority (single branch management)
- Approve orders
- OPS Manager access

#### Restrictions (CANNOT DO)

- Validate invoices or post journal entries
- Execute payments or manage PDC
- Modify product master data
- View profit margins
- Access Accounting Operations or Reporting

#### Menu Access

| Menu | Visible? |
|---|---|
| Inventory | Yes (full - Stock Manager) |
| Inventory Intelligence | Yes (via OPS Inventory Manager implied by stock.group_stock_manager alignment) |
| Approvals | Yes |
| Accounting > Operations > Inter-Branch Transfers | Yes (Branch Manager) |
| Accounting > Reporting > Daily Books | Yes (Branch Manager visible) |
| KPI Center | Yes |

---

### P08 - Treasury Officer (TREASURY_OFF)

**XML ID**: `ops_matrix_core.persona_treasury_officer`

| Field | Value |
|---|---|
| **Code** | `TREASURY_OFF` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Can Manage Team** | No |

**Description**: Authorized to execute payments and manage cash flow, PDC operations. Cannot validate invoices or post journal entries (separation from Accounting).

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_user` | Billing |
| `ops_matrix_core.group_ops_manager` | OPS Manager |
| `ops_matrix_core.group_ops_treasury` | Treasury Officer |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | NO |
| Validate Invoices | NO |
| Post Journal Entries | NO |
| Execute Payments | YES |
| Adjust Inventory | NO |
| Manage PDC | YES |

#### Capabilities (CAN DO)

- Execute vendor payments and manage payment registers
- Manage PDC Receivable and PDC Payable
- Bank reconciliation
- Bank statement management
- Treasury Intelligence reports
- Bank Book reports
- Approve expenses

#### Restrictions (CANNOT DO)

- Validate invoices (SoD separation from Accounting)
- Post journal entries (SoD separation from Accounting)
- Access cost prices, margins, or valuation data
- Modify product master data
- Adjust inventory
- Manage team members

#### Menu Access

| Menu | Visible? |
|---|---|
| Accounting > Operations | Yes (Bank Reconciliation, Bank Statements) |
| Accounting > Customers > PDC Receivable | Yes |
| Accounting > Vendors > PDC Payable | Yes |
| Accounting > Reporting > Treasury Intelligence | Yes |
| Accounting > Reporting > Daily Books > Bank Book | Yes |
| Approvals | Yes |
| KPI Center | Yes |

---

### P09 - HR Manager (HR_MGR)

**XML ID**: `ops_matrix_core.persona_hr_manager`

| Field | Value |
|---|---|
| **Code** | `HR_MGR` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Can Manage Team** | Yes |

**Description**: Manager responsible for human resources, recruitment, employee relations, and leave management. No transactional or financial authorities.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `hr.group_hr_manager` | HR Officer (if HR module installed) |
| `ops_matrix_core.group_ops_manager` | OPS Manager |

#### SoD Authority Flags

ALL flags are **NO**. HR Manager has zero transactional or financial authority.

#### Capabilities (CAN DO)

- Full HR management (employees, departments, leave, recruitment)
- Approve leave requests
- Manage team members
- OPS Manager access (governance, approval rules)

#### Restrictions (CANNOT DO)

- Any financial operation (invoices, payments, journal entries)
- Any sales or purchase operation
- Any inventory operation
- View cost prices, margins, or valuation
- Manage PDC
- Access Accounting or Inventory apps

#### Menu Access

| Menu | Visible? |
|---|---|
| HR | Yes (full) |
| Approvals | Yes |
| KPI Center | Yes |
| Accounting | No |
| Sales | No |
| Purchase | No |
| Inventory | No |

---

### P10 - Chief Accountant (CHIEF_ACCT)

**XML ID**: `ops_matrix_core.persona_chief_accountant`

| Field | Value |
|---|---|
| **Code** | `CHIEF_ACCT` |
| **Job Level** | Manager |
| **Parent** | Financial Controller |
| **Is Approver** | Yes |
| **Can Manage Team** | Yes |

**Description**: Senior accountant responsible for financial reporting, compliance, and accounting team leadership. Can validate invoices and post entries.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_manager` | Billing Manager |
| `account.group_account_user` | Billing |
| `ops_matrix_core.group_ops_manager` | OPS Manager |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |
| `ops_matrix_core.group_ops_price_manager` | Price Manager |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | NO |
| Access Cost Prices | YES |
| Validate Invoices | YES |
| Post Journal Entries | YES |
| Execute Payments | NO |
| Adjust Inventory | NO |
| Manage PDC | NO |

#### Capabilities (CAN DO)

- Validate and post customer/vendor invoices
- Post accounting journal entries
- Full accounting management (as Billing Manager)
- View cost prices
- Modify unit prices (Price Manager)
- Approve expenses
- Manage accounting team
- Access all financial reports (as account_manager group holder)
- Asset management, depreciation, period close

#### Restrictions (CANNOT DO)

- Execute payments (SoD separation -- Treasury only)
- Manage PDC
- Modify product master data
- Adjust inventory
- View profit margins or stock valuation (not in those groups explicitly, but OPS Manager group may grant indirect access depending on hierarchy)

#### Menu Access

| Menu | Visible? |
|---|---|
| Accounting > Operations | Yes (all sub-menus) |
| Accounting > Assets & Planning | Yes (all) |
| Accounting > Reporting | Yes (all financial statements, daily books, asset intelligence) |
| Accounting > Configuration | Yes |
| Accounting > Customers > Follow-ups | Yes |
| Accounting > Customers > PDC | Yes (via accountant group) |
| Approvals | Yes |
| KPI Center | Yes |

---

### P11 - System Administrator (SYS_ADMIN)

**XML ID**: `ops_matrix_core.persona_sys_admin`

| Field | Value |
|---|---|
| **Code** | `SYS_ADMIN` |
| **Job Level** | Senior |
| **Parent** | Financial Controller |
| **Is Matrix Administrator** | Yes |
| **Can Manage Team** | Yes |

**Description**: Administrator responsible for system configuration, security, and technical infrastructure. EXPLICITLY RESTRICTED from all transactional and financial authorities to prevent system abuse.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `base.group_system` | Settings (superuser -- bypasses all record rules) |
| `ops_matrix_core.group_ops_matrix_administrator` | Matrix Admin (implies OPS Admin Power, Manager, User) |

**CRITICAL**: `base.group_system` bypasses ALL record rules including branch isolation and IT Admin blindness. This is the only persona with `group_system`.

#### SoD Authority Flags

ALL flags are **NO**. System Admin has zero SoD transactional authority.

#### Capabilities (CAN DO)

- Full system configuration and settings
- Create and manage users (group_erp_manager via group_system)
- Configure matrix structure (branches, BUs, personas)
- Manage security groups, access rights, record rules
- Configure governance rules, SLA templates, field visibility
- Configure KPI boards, widgets, and definitions
- Manage archive policies
- Full access to all OPS Framework administration
- Full access to all models via group_system bypass

#### Restrictions (CANNOT DO via SoD)

Even though group_system technically bypasses record rules, the SoD authority flags on the persona are ALL FALSE, meaning:
- `user.has_ops_authority('can_validate_invoices')` returns False
- `user.has_ops_authority('can_execute_payments')` returns False
- Python-level SoD checks in business logic WILL block the System Admin

However, `user.has_group('base.group_system')` returns True, which bypasses SoD authority checks in `has_authority()` and `has_ops_authority()` methods. **In practice, SYS_ADMIN can do everything.**

The persona flags serve as documentation of INTENDED restrictions.

#### IT Admin Blindness -- DOES NOT APPLY

SYS_ADMIN gets `group_system`, NOT `group_ops_it_admin`. The IT Admin blindness rules do not apply to SYS_ADMIN.

#### Menu Access

ALL menus visible (group_system grants universal access).

| Menu | Visible? |
|---|---|
| Settings > OPS Framework | Yes (all sub-menus) |
| KPI Configuration | Yes |
| All operational menus | Yes |
| All reporting menus | Yes |

---

### P12 - Sales Representative (SALES_REP)

**XML ID**: `ops_matrix_core.persona_sales_rep`

| Field | Value |
|---|---|
| **Code** | `SALES_REP` |
| **Job Level** | Mid |
| **Parent** | Sales Manager |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Sales professional managing customer accounts, quotations, and order processing. Cannot modify product costs or approve own orders.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `sales_team.group_sale_salesman` | Sales User (Own Documents Only) |
| `sale.group_sale_salesman` | Sales User (Own Documents Only) |
| `ops_matrix_core.group_ops_user` | OPS User |

#### SoD Authority Flags

ALL flags are **NO**.

#### Capabilities (CAN DO)

- Create and manage own sales quotations/orders
- View own sales data only (Own Documents restriction)
- Create approval requests
- Create product requests
- Read governance rules, personas, branches (read-only)
- Access KPI Center boards (read-only)

#### Restrictions (CANNOT DO)

- View other users' sales orders
- Approve own orders (no is_approver flag)
- View cost prices, margins, or valuation
- Any accounting, inventory, or purchasing operations
- Modify unit prices (no Price Manager group)
- Access governance configuration

#### Field Visibility (when rules enabled)

The following fields are HIDDEN from Sales Representatives:
- `product.template.standard_price` (Cost Price)
- `product.product.standard_price` (Cost Price on variants)
- `sale.order.line.purchase_price` (Purchase Price)
- `sale.order.line.margin` (Margin)
- `sale.order.line.margin_percent` (Margin %)

#### Governance Limits (from demo data)

- **Max Discount**: 10% (approval required above 5%)
- **Max Price Variance**: 5% (approval required above 2%)
- **Approver**: Doha Manager persona

#### Menu Access

| Menu | Visible? |
|---|---|
| Sales | Yes (own documents only) |
| Approvals | Yes |
| KPI Center | Yes (read) |
| Accounting | No |
| Inventory | No |
| Purchase | No |

#### Golden User Template

Template: `user_template_sales_executive` (login: `tmpl_sales`)
Groups: `base.group_user`, `sales_team.group_sale_manager` (note: template gives higher access than persona auto-mapping)

---

### P13 - Purchase Officer (PURCHASE_OFF)

**XML ID**: `ops_matrix_core.persona_purchase_officer`

| Field | Value |
|---|---|
| **Code** | `PURCHASE_OFF` |
| **Job Level** | Mid |
| **Parent** | Purchase Manager |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Creates purchase orders and manages vendor relationships. Can modify product master data but cannot approve own orders.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `purchase.group_purchase_user` | Purchase User |
| `stock.group_stock_user` | Inventory User |
| `ops_matrix_core.group_ops_user` | OPS User |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Modify Product Master | YES |
| Access Cost Prices | YES |
| All others | NO |

#### Capabilities (CAN DO)

- Create purchase orders (cannot approve own)
- Modify product master data (costs, suppliers)
- View product cost prices
- Basic inventory operations (receiving, stock movements)
- Three-way match operations (purchase user CRUD)
- Create approval requests

#### Restrictions (CANNOT DO)

- Approve own purchase orders
- Validate invoices or post journal entries
- Execute payments
- Adjust inventory
- View margins or valuation
- Access Accounting reports

#### Field Visibility (when rules enabled)

The following fields are HIDDEN from Purchase Officers:
- `purchase.order.customer_id` (Customer information)
- `purchase.order.line.sale_price` (Sale Price)
- `purchase.order.line.margin` (Margin)
- `purchase.order.line.margin_percent` (Margin %)

#### Menu Access

| Menu | Visible? |
|---|---|
| Purchase | Yes (user-level) |
| Inventory | Yes (user-level) |
| Approvals | Yes |
| KPI Center | Yes (read) |

---

### P14 - Logistics Clerk (LOG_CLERK)

**XML ID**: `ops_matrix_core.persona_logistics_clerk`

| Field | Value |
|---|---|
| **Code** | `LOG_CLERK` |
| **Job Level** | Mid |
| **Parent** | Logistics Manager |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Staff responsible for inventory handling, picking, packing, and shipment processing. Cannot post inventory adjustments.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `stock.group_stock_user` | Inventory User |
| `ops_matrix_core.group_ops_user` | OPS User |

#### SoD Authority Flags

ALL flags are **NO**.

#### Capabilities (CAN DO)

- Process receipts, deliveries, and transfers
- Pick, pack, and ship orders
- View stock levels (within branch isolation)
- Create approval requests

#### Restrictions (CANNOT DO)

- Post inventory adjustments (SoD -- Logistics Manager only)
- View cost prices, margins, or valuation
- Any financial operations
- Any sales or purchase operations (beyond inventory movements)

#### Field Visibility (when rules enabled)

The following fields are HIDDEN from Warehouse Staff:
- `stock.move.cost` (Cost)
- `stock.move.value` (Valuation)
- `stock.quant.cost` (Cost)
- `stock.quant.value` (Total Value)

#### Menu Access

| Menu | Visible? |
|---|---|
| Inventory | Yes (user-level operations) |
| Approvals | Yes |
| KPI Center | Yes (read) |

#### Golden User Template

Template: `user_template_logistics_officer` (login: `tmpl_logistics`)
Groups: `base.group_user`, `stock.group_stock_user`

---

### P15 - Accountant (ACCOUNTANT)

**XML ID**: `ops_matrix_core.persona_accountant`

| Field | Value |
|---|---|
| **Code** | `ACCOUNTANT` |
| **Job Level** | Mid |
| **Parent** | Chief Accountant |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Accounting professional handling financial transactions, journal entries, and reconciliations. Cannot validate invoices independently.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_user` | Billing |
| `account.group_account_invoice` | Invoicing |
| `ops_matrix_core.group_ops_user` | OPS User |
| `ops_matrix_core.group_ops_see_cost` | See Cost Prices |

#### SoD Authority Flags

| Authority | Granted? |
|---|---|
| Access Cost Prices | YES |
| All others | NO |

#### Capabilities (CAN DO)

- Create invoices and credit notes (cannot validate)
- View journal entries (read-only via user group)
- View cost prices
- Read financial reports (limited -- OPS User, not Manager)
- Create reconciliation entries
- View assets and depreciation (read-only)

#### Restrictions (CANNOT DO)

- Validate invoices (SoD -- requires Chief Accountant or above)
- Post journal entries (SoD restriction)
- Execute payments
- Manage PDC
- Adjust inventory
- Modify product master data
- View margins or stock valuation (not in those groups)

#### Menu Access

Note: Menu visibility depends on OPS groups. Since Accountant has only `group_ops_user` (not manager/accountant OPS group), some accounting menus may not be visible despite having `account.group_account_user`. The OPS menu groups primarily reference `group_ops_accountant`, `group_ops_finance_manager`, and `group_ops_cfo`.

The Accountant persona does NOT automatically get `ops_matrix_core.group_ops_accountant`. This means many Accounting > Operations and Reporting menus that require `group_ops_accountant` will NOT be visible.

**Recommendation**: Consider adding `ops_matrix_core.group_ops_accountant` to the ACCOUNTANT persona group mapping for full accounting menu visibility.

---

### P16 - Accounts Receivable Clerk (AR_CLERK)

**XML ID**: `ops_matrix_core.persona_ar_clerk`

| Field | Value |
|---|---|
| **Code** | `AR_CLERK` |
| **Job Level** | Mid |
| **Parent** | Financial Controller |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Manages customer invoices and collections. Cannot validate invoices or post journal entries.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_invoice` | Invoicing (customer invoices) |
| `ops_matrix_core.group_ops_user` | OPS User |

#### SoD Authority Flags

ALL flags are **NO**.

#### Capabilities (CAN DO)

- Create customer invoices and credit notes
- Manage customer collections
- View customer payment status
- Basic invoicing operations

#### Restrictions (CANNOT DO)

- Validate invoices
- Post journal entries
- Execute payments
- View cost prices, margins, or valuation
- Any purchase or inventory operations
- Manage PDC

#### Menu Access

Limited Accounting access. Can see customer-related invoicing menus where `account.group_account_invoice` grants access.

---

### P17 - Accounts Payable Clerk (AP_CLERK)

**XML ID**: `ops_matrix_core.persona_ap_clerk`

| Field | Value |
|---|---|
| **Code** | `AP_CLERK` |
| **Job Level** | Mid |
| **Parent** | Financial Controller |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Processes vendor bills and payment requests. Cannot execute payments or validate invoices.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `account.group_account_invoice` | Invoicing (vendor bills) |
| `ops_matrix_core.group_ops_user` | OPS User |

#### SoD Authority Flags

ALL flags are **NO**.

#### Capabilities (CAN DO)

- Create vendor bills and credit notes
- Process payment requests (cannot execute)
- View vendor payment status
- Basic invoicing operations

#### Restrictions (CANNOT DO)

- Validate invoices
- Execute payments (SoD -- Treasury only)
- Post journal entries
- View cost prices, margins, or valuation
- Any sales or inventory operations
- Manage PDC

---

### P18 - Technical Support (TECH_SUPPORT)

**XML ID**: `ops_matrix_core.persona_tech_support`

| Field | Value |
|---|---|
| **Code** | `TECH_SUPPORT` |
| **Job Level** | Mid |
| **Parent** | None |
| **Is Approver** | No |
| **Can Manage Team** | No |

**Description**: Support specialist assisting customers with technical issues and system troubleshooting. No transactional authorities.

#### Auto-Mapped Odoo Groups

| Group | Purpose |
|---|---|
| `base.group_user` | Internal User |
| `base.group_erp_manager` | Access Rights (can create/manage users) |
| `ops_matrix_core.group_ops_it_admin` | IT Admin (BLINDNESS rules block business data) |
| `ops_matrix_core.group_ops_user` | OPS User |

#### SoD Authority Flags

ALL flags are **NO**.

#### IT Admin Blindness -- APPLIES

Technical Support receives `group_ops_it_admin`, which triggers **IT Admin Blindness** record rules. The following models return ZERO records:

**Core Models Blocked (via `ir_rule_it_blind.xml` - global rules)**:
- `sale.order` and `sale.order.line`
- `purchase.order` and `purchase.order.line`
- `account.move` and `account.move.line`
- `account.payment`
- `account.bank.statement`
- `stock.picking` and `stock.move`
- `stock.quant`
- `stock.valuation.layer`

**Accounting Models Blocked (via `ops_accounting_rules.xml`)**:
- `ops.pdc.receivable` and `ops.pdc.payable`
- `ops.budget` and `ops.budget.line`
- `ops.asset`, `ops.asset.category`, `ops.asset.depreciation`

**KPI Data Blocked (via `ops_kpi_security.xml`)**:
- `ops.kpi.value` (blind -- sees nothing)
- But CAN configure: `ops.kpi`, `ops.kpi.board`, `ops.kpi.widget`

#### SoD Conflict Detection

The SoD system will flag conflicts if TECH_SUPPORT is combined with:
- OPS Admin Power
- See Cost Data
- Account Manager
- Purchase Manager
- Sales Manager
- Stock Manager

#### Capabilities (CAN DO)

- Create and manage user accounts (group_erp_manager)
- Configure system settings
- View user access rights and audit logs
- Configure KPI boards, widgets, and definitions (admin task, not data)
- View OPS personas, branches, BUs (read-only via OPS User)
- System troubleshooting and configuration

#### Restrictions (CANNOT DO)

- See ANY business transactions (sales, purchases, invoices, payments)
- See ANY stock data (pickings, moves, quants, valuation)
- See ANY financial data (PDC, budgets, assets)
- See KPI values (blind to actual data)
- Any transactional authority
- Approve anything

#### Menu Access

| Menu | Visible? |
|---|---|
| KPI Center | Yes (sees boards, but data is blank) |
| KPI Configuration | Yes (can configure) |
| Approvals | Yes (but no transactions to approve) |
| Settings | Yes (user management) |
| Sales | Menu visible but ALL records blank (blindness rules) |
| Accounting | Menu visible but ALL records blank |
| Inventory | Menu visible but ALL records blank |

---

## SoD Authority Matrix

Complete matrix of all persona SoD flags:

| Persona | Product Master | Cost Prices | Validate Invoices | Post JE | Execute Payments | Adjust Inventory | Manage PDC |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FIN_CTRL** | - | YES | YES | YES | - | - | YES |
| **CEO** | YES | YES | YES | YES | YES | YES | YES |
| **CFO** | YES | YES | YES | YES | YES | YES | YES |
| **SALES_LEADER** | - | YES | - | - | - | - | - |
| **SALES_MGR** | - | - | - | - | - | - | - |
| **PURCHASE_MGR** | YES | YES | - | - | - | - | - |
| **LOG_MGR** | - | YES | - | - | - | YES | - |
| **TREASURY_OFF** | - | - | - | - | YES | - | YES |
| **HR_MGR** | - | - | - | - | - | - | - |
| **CHIEF_ACCT** | - | YES | YES | YES | - | - | - |
| **SYS_ADMIN** | - | - | - | - | - | - | - |
| **SALES_REP** | - | - | - | - | - | - | - |
| **PURCHASE_OFF** | YES | YES | - | - | - | - | - |
| **LOG_CLERK** | - | - | - | - | - | - | - |
| **ACCOUNTANT** | - | YES | - | - | - | - | - |
| **AR_CLERK** | - | - | - | - | - | - | - |
| **AP_CLERK** | - | - | - | - | - | - | - |
| **TECH_SUPPORT** | - | - | - | - | - | - | - |

**Key SoD Separations**:
1. **Invoice Validation** (FIN_CTRL, CEO, CFO, CHIEF_ACCT) vs **Payment Execution** (CEO, CFO, TREASURY_OFF) -- only CEO and CFO can do both
2. **Product Master Modification** (CEO, CFO, PURCHASE_MGR, PURCHASE_OFF) vs **Sales Operations** (SALES_LEADER, SALES_MGR, SALES_REP) -- completely separated
3. **Inventory Adjustment** (CEO, CFO, LOG_MGR) vs **Financial Posting** (FIN_CTRL, CEO, CFO, CHIEF_ACCT) -- only CEO and CFO overlap
4. **PDC Management** (FIN_CTRL, CEO, CFO, TREASURY_OFF) vs **Invoice Validation** -- Treasury can manage PDC without touching invoices

---

## IT Admin Blindness Summary

The IT Admin Blindness design ensures that the Technical Support / IT Administrator persona CANNOT see business transactions, even though they have system configuration rights.

### Blocked Models (24 total)

**Core (12 models via global rules in `ir_rule_it_blind.xml`)**:
1. `sale.order`
2. `sale.order.line`
3. `purchase.order`
4. `purchase.order.line`
5. `account.move`
6. `account.move.line`
7. `account.payment`
8. `account.bank.statement`
9. `stock.picking`
10. `stock.move`
11. `stock.quant`
12. `stock.valuation.layer`

**Accounting (7 models via group-specific rules in `ops_accounting_rules.xml`)**:
13. `ops.pdc.receivable`
14. `ops.pdc.payable`
15. `ops.budget`
16. `ops.budget.line`
17. `ops.asset`
18. `ops.asset.category`
19. `ops.asset.depreciation`

**KPI (1 model via `ops_kpi_security.xml`)**:
20. `ops.kpi.value` (blind -- `[('id', '=', 0)]`)

### IT Admin CAN Access
- `ops.kpi` (definitions -- CRUD)
- `ops.kpi.board` (boards -- CRUD)
- `ops.kpi.widget` (widgets -- CRUD)
- `res.users` (user management)
- `ops.persona` (read via OPS User)
- `ops.branch` (read via OPS User)
- `ops.business.unit` (read via OPS User)
- System configuration models

---

## Field Visibility Rules Catalog

Field visibility rules are defined in `ops_matrix_core/data/field_visibility_rules.xml`. These are currently in **CATALOG MODE** (`enabled=False`), meaning they are visible but NOT enforced. They can be activated by administrators.

### Sales Staff Restrictions (when enabled)

| Model | Field | Label | Mode |
|---|---|---|---|
| `product.template` | `standard_price` | Cost Price | Hidden |
| `product.product` | `standard_price` | Cost Price | Hidden |
| `sale.order.line` | `purchase_price` | Purchase Price | Hidden |
| `sale.order.line` | `margin` | Margin | Hidden |
| `sale.order.line` | `margin_percent` | Margin % | Hidden |

**Applies to**: `sales_team.group_sale_salesman` (Sales Reps, Sales Managers)

### Purchase Staff Restrictions (when enabled)

| Model | Field | Label | Mode |
|---|---|---|---|
| `purchase.order` | `customer_id` | Customer | Hidden |
| `purchase.order.line` | `sale_price` | Sale Price | Hidden |
| `purchase.order.line` | `margin` | Margin | Hidden |
| `purchase.order.line` | `margin_percent` | Margin % | Hidden |

**Applies to**: `purchase.group_purchase_user` (Purchase Officers)

### Warehouse Staff Restrictions (when enabled)

| Model | Field | Label | Mode |
|---|---|---|---|
| `stock.move` | `cost` | Cost | Hidden |
| `stock.move` | `value` | Valuation | Hidden |
| `stock.quant` | `cost` | Cost | Hidden |
| `stock.quant` | `value` | Total Value | Hidden |

**Applies to**: `stock.group_stock_user` (Logistics Clerks, Purchase Officers)

### Group-Based Data Visibility (via Security Groups)

Beyond field-level rules, cost/margin/valuation visibility is enforced via group membership:

| Group | Can See Cost | Can See Margin | Can See Valuation |
|---|:---:|:---:|:---:|
| `group_ops_see_cost` | YES | - | - |
| `group_ops_see_margin` | YES (inherited) | YES | - |
| `group_ops_see_valuation` | YES (inherited) | - | YES |

Views use `groups="ops_matrix_core.group_ops_see_cost"` to conditionally show/hide fields.

---

## Delegation System

### How Delegation Works

1. A persona owner (delegator) can temporarily delegate their persona to another user (delegate)
2. The delegate inherits ALL authorities of the delegated persona for the delegation period
3. Only ONE active delegation per persona at a time (overlapping delegations are blocked)
4. The `effective_user_id` on the persona automatically switches to the delegate

### Delegation Rules

- **Self-delegation prohibited**: Cannot delegate to yourself
- **Active user required**: Cannot delegate to inactive users
- **Delegation flag**: Persona must have `can_be_delegated=True` (default)
- **Date range required**: Both start and end dates mandatory
- **Auto-expiry**: Cron job deactivates expired delegations
- **Approval support**: Optional `approval_required` flag with `approved_by` tracking
- **Full audit trail**: All delegation CRUD operations logged to `ops.security.audit`

### Authority Resolution

When checking `user.has_ops_authority('can_validate_invoices')`:
1. Check user's own active personas
2. Check active delegations TO this user
3. If ANY persona (own or delegated) has the flag = True, return True
4. System administrators (`base.group_system`) always return True

### Notification Flow

- Delegation created: Both delegator and delegate notified
- Delegation revoked: Both parties notified
- Delegation expiring: Notification 3 days before expiry (cron)

---

## Golden User Templates

Four pre-defined inactive user templates for quick user provisioning:

| Template | Login | Persona | Odoo Groups | Purpose |
|---|---|---|---|---|
| Financial Controller | `tmpl_finance` | `persona_financial_controller` | `group_user`, `group_account_manager` | Full finance access |
| Logistics Officer | `tmpl_logistics` | `persona_logistics_clerk` | `group_user`, `stock.group_stock_user` | Warehouse/stock access |
| Sales Executive | `tmpl_sales` | `persona_sales_rep` | `group_user`, `sales_team.group_sale_manager` | Sales/CRM access |
| Branch Manager | `tmpl_manager` | `persona_sales_manager` | `group_user`, `account.group_account_user`, `sales_team.group_sale_manager` | Multi-department read |

**Usage**: Go to Settings > Users > Show Archived > Select template > Duplicate > Update name/login/password > Assign branch/BU > Activate

---

## Governance & Approval Limits

### Governance Rule Types

1. **Matrix Validation**: Ensures Branch + BU assigned to all transactions
2. **Discount Limit**: Per-persona maximum discount percentages
3. **Margin Protection**: Per-category minimum margin requirements
4. **Price Override**: Per-persona price variance limits
5. **Approval Workflow**: Multi-step approval chains

### Discount Limits by Persona (Demo Data)

| Persona | Max Discount | Approval Required Above | Approver |
|---|---|---|---|
| Sales Rep | 10% | 5% | Doha Manager |
| Dubai Sales Manager | 15% | 10% | Retail Leader |
| Doha Manager | 20% | 15% | Retail Leader |
| Warehouse Manager | 20% | 15% | CEO Qatar |
| Doha Manager (Coffee) | 12% | 8% | CEO Qatar |

### Price Authority by Persona (Demo Data)

| Persona | Max Price Variance | Can Override Without Approval | Approval Above |
|---|---|---|---|
| Sales Rep | 5% | No | 2% |
| Doha Manager | 10% | Yes | 8% |
| Dubai Sales | 12% | Yes | 10% |

### Margin Rules by Category (Demo Data)

| Category | Min Margin | Warning | Critical |
|---|---|---|---|
| Electronics | 25% | 30% | 20% |
| Furniture | 30% | 35% | 25% |
| Coffee | 40% | 45% | 35% |
| Luxury Goods | 50% | 55% | 45% |
| Commodities | 10% | 15% | 5% |
| Services | 55% | 60% | 50% |

---

## Seed Data Requirements

To fully exercise the persona system in testing, the following data is needed per persona:

### Required for Every Persona
- At least 1 active user assigned to the persona
- Primary Branch assigned
- At least 1 Business Unit assigned
- Active persona with valid date range

### Per-Persona Test Accounts

| # | Persona Code | Suggested Login | Required Branches | Required BUs |
|---|---|---|---|---|
| 1 | CEO | `ceo@company.com` | All branches | All BUs |
| 2 | CFO | `cfo@company.com` | All branches | All BUs |
| 3 | FIN_CTRL | `fin.ctrl@company.com` | All branches | All BUs |
| 4 | SALES_LEADER | `sales.leader@company.com` | Multiple branches | Retail BU |
| 5 | SALES_MGR | `sales.mgr@company.com` | 1 branch | 1-2 BUs |
| 6 | PURCHASE_MGR | `purchase.mgr@company.com` | 1 branch | 1-2 BUs |
| 7 | LOG_MGR | `logistics.mgr@company.com` | 1 branch | 1-2 BUs |
| 8 | TREASURY_OFF | `treasury@company.com` | All branches | All BUs |
| 9 | HR_MGR | `hr.mgr@company.com` | 1 branch | All BUs |
| 10 | CHIEF_ACCT | `chief.acct@company.com` | All branches | All BUs |
| 11 | SYS_ADMIN | `sysadmin@company.com` | All branches | All BUs |
| 12 | SALES_REP | `sales.rep@company.com` | 1 branch | 1 BU |
| 13 | PURCHASE_OFF | `purchase.off@company.com` | 1 branch | 1 BU |
| 14 | LOG_CLERK | `warehouse@company.com` | 1 branch | 1 BU |
| 15 | ACCOUNTANT | `accountant@company.com` | 1 branch | All BUs |
| 16 | AR_CLERK | `ar.clerk@company.com` | 1 branch | 1-2 BUs |
| 17 | AP_CLERK | `ap.clerk@company.com` | 1 branch | 1-2 BUs |
| 18 | TECH_SUPPORT | `tech.support@company.com` | 1 branch | 1 BU |

### Test Scenarios per Persona

For each persona, verify:
1. Login succeeds and correct menus are visible
2. Branch isolation works (only sees own branch data)
3. SoD authority checks pass/fail correctly
4. Field visibility rules apply correctly
5. Governance limits enforce correctly
6. Approval workflows route to correct approver
7. Delegation grants and revokes authority correctly
8. IT Admin Blindness works (for TECH_SUPPORT only)

---

## Appendix: Persona-to-Group Complete Mapping

Source: `/opt/gemini_odoo19/addons/ops_matrix_core/models/res_users_group_mapper.py`

```
CEO          -> sales_team.group_sale_manager, account.group_account_manager,
                stock.group_stock_manager, purchase.group_purchase_manager,
                ops_matrix_core.group_ops_executive

CFO          -> account.group_account_manager, account.group_account_user,
                ops_matrix_core.group_ops_executive, ops_matrix_core.group_ops_cost_controller,
                ops_matrix_core.group_ops_see_cost, ops_matrix_core.group_ops_see_margin,
                ops_matrix_core.group_ops_price_manager

FIN_CTRL     -> account.group_account_manager, account.group_account_user,
                sale.group_sale_manager, purchase.group_purchase_manager,
                ops_matrix_core.group_ops_executive, ops_matrix_core.group_ops_cost_controller,
                ops_matrix_core.group_ops_price_manager

SALES_LEADER -> sales_team.group_sale_manager, sale.group_sale_manager,
                ops_matrix_core.group_ops_bu_leader, ops_matrix_core.group_ops_see_cost,
                ops_matrix_core.group_ops_price_manager

SALES_MGR    -> sales_team.group_sale_manager, sale.group_sale_salesman_all_leads,
                ops_matrix_core.group_ops_manager

PURCHASE_MGR -> purchase.group_purchase_manager, stock.group_stock_user,
                ops_matrix_core.group_ops_manager, ops_matrix_core.group_ops_see_cost

LOG_MGR      -> stock.group_stock_manager,
                ops_matrix_core.group_ops_branch_manager, ops_matrix_core.group_ops_manager,
                ops_matrix_core.group_ops_see_cost

TREASURY_OFF -> account.group_account_user,
                ops_matrix_core.group_ops_manager, ops_matrix_core.group_ops_treasury

HR_MGR       -> hr.group_hr_manager,
                ops_matrix_core.group_ops_manager

CHIEF_ACCT   -> account.group_account_manager, account.group_account_user,
                ops_matrix_core.group_ops_manager, ops_matrix_core.group_ops_see_cost,
                ops_matrix_core.group_ops_price_manager

SYS_ADMIN    -> base.group_system,
                ops_matrix_core.group_ops_matrix_administrator

SALES_REP    -> sales_team.group_sale_salesman, sale.group_sale_salesman,
                ops_matrix_core.group_ops_user

PURCHASE_OFF -> purchase.group_purchase_user, stock.group_stock_user,
                ops_matrix_core.group_ops_user, ops_matrix_core.group_ops_see_cost

LOG_CLERK    -> stock.group_stock_user,
                ops_matrix_core.group_ops_user

ACCOUNTANT   -> account.group_account_user, account.group_account_invoice,
                ops_matrix_core.group_ops_user, ops_matrix_core.group_ops_see_cost

AR_CLERK     -> account.group_account_invoice,
                ops_matrix_core.group_ops_user

AP_CLERK     -> account.group_account_invoice,
                ops_matrix_core.group_ops_user

TECH_SUPPORT -> base.group_user, base.group_erp_manager,
                ops_matrix_core.group_ops_it_admin, ops_matrix_core.group_ops_user
```

---

*End of OPS Persona Playbook*
*Total Personas: 18*
*Source files: ops_matrix_core/data/ops_persona_templates.xml, ops_matrix_core/models/res_users_group_mapper.py, ops_matrix_core/data/res_groups.xml*
