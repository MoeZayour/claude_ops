# OPS Framework Security Matrix

> **Generated**: 2026-02-13
> **Scope**: ops_matrix_core, ops_matrix_accounting, ops_kpi, ops_theme
> **Odoo Version**: 19.0 Community Edition

---

## Table of Contents

1. [Security Groups](#1-security-groups)
2. [Group Implication Chains](#2-group-implication-chains)
3. [IT Admin Blindness Matrix](#3-it-admin-blindness-matrix)
4. [Branch Isolation Matrix](#4-branch-isolation-matrix)
5. [Company Isolation Matrix](#5-company-isolation-matrix)
6. [System Admin Bypass Rules](#6-system-admin-bypass-rules)
7. [ACL Summary](#7-acl-summary)
8. [Field-Level Security](#8-field-level-security)
9. [Segregation of Duties (SoD)](#9-segregation-of-duties-sod)
10. [Menu Restrictions](#10-menu-restrictions)
11. [Corporate Audit Log Rules](#11-corporate-audit-log-rules)
12. [Statistics Summary](#12-statistics-summary)

---

## 1. Security Groups

### 1.1 Module Category

| XML ID | Name | Description |
|--------|------|-------------|
| `ops_matrix_core.module_category_ops_matrix` | OPS Matrix | Multi-Branch and Business Unit Management Framework |

### 1.2 Complete OPS Group Registry (22 groups)

All groups defined in `ops_matrix_core/data/res_groups.xml`:

| # | XML ID | Display Name | Implied Groups | Purpose |
|---|--------|-------------|----------------|---------|
| 1 | `group_ops_user` | OPS User | `base.group_user` | Basic OPS Matrix access, view branch/BU info, create requests |
| 2 | `group_ops_manager` | OPS Manager | `group_ops_user` | Manage operations within assigned branches and BUs |
| 3 | `group_ops_admin_power` | OPS Administrator | `group_ops_manager` | Top-level OPS authority. Full access to all OPS features. Does NOT imply `group_system` |
| 4 | `group_ops_product_approver` | Product Approver | `group_ops_user` | Approve product requests from other users/branches |
| 5 | `group_ops_matrix_administrator` | Matrix Administrator | `group_ops_admin_power` | Full access to matrix configuration including dashboard widgets |
| 6 | `group_ops_it_admin` | IT Administrator | `base.group_user` | System administration with NO business data access. Blind to transactions |
| 7 | `group_ops_see_cost` | Can See Product Costs | _(none)_ | Visibility to product cost prices |
| 8 | `group_ops_see_margin` | Can See Profit Margins | `group_ops_see_cost` | Visibility to profit margin data |
| 9 | `group_ops_see_valuation` | Can See Stock Valuation | `group_ops_see_cost` | Visibility to inventory valuation amounts |
| 10 | `group_ops_price_manager` | Price Manager | _(none)_ | Can modify unit prices on sale order lines |
| 11 | `group_ops_executive` | Executive / CEO | `group_ops_user`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` | Read-only executive oversight |
| 12 | `group_ops_cfo` | CFO / Owner | `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` | Full financial access across all entities |
| 13 | `group_ops_branch_manager` | OPS Branch Manager | `group_ops_user` | Single-branch operations management |
| 14 | `group_ops_bu_leader` | Business Unit Leader | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_margin` | Multi-branch within BU |
| 15 | `group_ops_cross_branch_bu_leader` | Cross-Branch BU Leader | `group_ops_bu_leader` | BU visibility across all branches |
| 16 | `group_ops_sales_manager` | Sales Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin` | Sales operations, approve discounts |
| 17 | `group_ops_purchase_manager` | Purchase Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_cost` | Purchase operations, approve POs |
| 18 | `group_ops_inventory_manager` | Inventory Manager | `group_ops_branch_manager`, `group_ops_manager`, `group_ops_see_valuation` | Inventory operations, stock valuation |
| 19 | `group_ops_finance_manager` | Finance Manager | `group_ops_manager`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` | Full financial operations |
| 20 | `group_ops_cost_controller` | OPS Cost Controller | `group_ops_finance_manager` | Cost and margin controls |
| 21 | `group_ops_accountant` | Accountant / Controller | `group_ops_user`, `group_ops_see_cost`, `group_ops_see_margin`, `group_ops_see_valuation` | Full accounting access |
| 22 | `group_ops_treasury` | Treasury Officer | `group_ops_user` | Cash flow, payments, banking |
| 23 | `group_ops_compliance_officer` | Compliance Officer | `group_ops_user` | Governance oversight, audit logs, SoD violations (read) |
| 24 | `group_ops_can_export` | Can Export Data | `group_ops_manager` | Secure Export Wizard access. Exports are logged |

### 1.3 External Groups Referenced

These Odoo standard groups are used in OPS ACLs and record rules:

| External Group | Module | Used For |
|---------------|--------|----------|
| `base.group_user` | base | Internal User (base level) |
| `base.group_system` | base | System Administrator (Settings) |
| `base.group_no_one` | base | Technical Features (restricted to IT/System admin) |
| `account.group_account_user` | account | Accountant |
| `account.group_account_manager` | account | Account Manager |
| `account.group_account_invoice` | account | Invoicing |
| `sales_team.group_sale_salesman` | sales_team | Salesperson |
| `sales_team.group_sale_manager` | sales_team | Sales Manager |
| `purchase.group_purchase_user` | purchase | Purchase User |
| `purchase.group_purchase_manager` | purchase | Purchase Manager |
| `stock.group_stock_user` | stock | Stock User |
| `stock.group_stock_manager` | stock | Stock Manager |

---

## 2. Group Implication Chains

### 2.1 Core Hierarchy

```
base.group_user
 |
 +-- group_ops_user
 |    |
 |    +-- group_ops_manager
 |    |    |
 |    |    +-- group_ops_admin_power
 |    |    |    |
 |    |    |    +-- group_ops_matrix_administrator
 |    |    |
 |    |    +-- group_ops_can_export
 |    |    |
 |    |    +-- group_ops_cfo (+ see_cost, see_margin, see_valuation)
 |    |    |
 |    |    +-- group_ops_finance_manager (+ see_cost, see_margin, see_valuation)
 |    |    |    |
 |    |    |    +-- group_ops_cost_controller
 |    |    |
 |    |    +-- group_ops_bu_leader (+ branch_manager, see_margin)
 |    |         |
 |    |         +-- group_ops_cross_branch_bu_leader
 |    |
 |    +-- group_ops_branch_manager
 |    |    |
 |    |    +-- group_ops_bu_leader (also via manager)
 |    |    +-- group_ops_sales_manager (+ manager, see_cost, see_margin)
 |    |    +-- group_ops_purchase_manager (+ manager, see_cost)
 |    |    +-- group_ops_inventory_manager (+ manager, see_valuation)
 |    |
 |    +-- group_ops_product_approver
 |    +-- group_ops_executive (+ see_cost, see_margin, see_valuation)
 |    +-- group_ops_accountant (+ see_cost, see_margin, see_valuation)
 |    +-- group_ops_treasury
 |    +-- group_ops_compliance_officer
 |
 +-- group_ops_it_admin   <-- ISOLATED: NO implied OPS groups
```

### 2.2 Data Visibility Hierarchy

```
group_ops_see_cost
 |
 +-- group_ops_see_margin (implies see_cost)
 +-- group_ops_see_valuation (implies see_cost)
```

**Groups that inherit ALL three visibility groups** (see_cost + see_margin + see_valuation):
- `group_ops_executive`
- `group_ops_cfo`
- `group_ops_finance_manager` (and therefore `group_ops_cost_controller`)
- `group_ops_accountant`

**Groups that inherit see_cost + see_margin only**:
- `group_ops_sales_manager`
- `group_ops_bu_leader` (see_margin only, which implies see_cost)

**Groups that inherit see_cost only**:
- `group_ops_purchase_manager`

**Groups that inherit see_valuation only** (which implies see_cost):
- `group_ops_inventory_manager`

---

## 3. IT Admin Blindness Matrix

### 3.1 Mechanism

IT Admin Blindness rules use domain `[('id', '=', 0)]` which always returns zero records.
Rules are applied to `group_ops_it_admin` to block ALL business data access.

> **Design Note**: The `ir_rule_it_blind.xml` file uses an older global rule pattern with `[(user.has_group(...), '=', False)]`. The `ir_rule.xml` file contains the newer, more explicit per-group rules with `[('id', '=', 0)]` domain. Both files cover the same models. The newer pattern in `ir_rule.xml` is the authoritative implementation.

### 3.2 Blocked Models - ops_matrix_core (22 rules in ir_rule.xml)

| # | XML ID | Model | Odoo Module |
|---|--------|-------|-------------|
| 1 | `rule_it_admin_blind_sale_order` | sale.order | sale |
| 2 | `rule_it_admin_blind_sale_order_line` | sale.order.line | sale |
| 3 | `rule_it_admin_blind_purchase_order` | purchase.order | purchase |
| 4 | `rule_it_admin_blind_purchase_order_line` | purchase.order.line | purchase |
| 5 | `rule_it_admin_blind_account_move` | account.move | account |
| 6 | `rule_it_admin_blind_account_move_line` | account.move.line | account |
| 7 | `rule_it_admin_blind_account_payment` | account.payment | account |
| 8 | `rule_it_admin_blind_bank_statement` | account.bank.statement | account |
| 9 | `rule_it_admin_blind_bank_statement_line` | account.bank.statement.line | account |
| 10 | `rule_it_admin_blind_stock_picking` | stock.picking | stock |
| 11 | `rule_it_admin_blind_stock_move` | stock.move | stock |
| 12 | `rule_it_admin_blind_stock_move_line` | stock.move.line | stock |
| 13 | `rule_it_admin_blind_pricelist` | product.pricelist | product |
| 14 | `rule_it_admin_blind_pricelist_item` | product.pricelist.item | product |
| 15 | `rule_it_admin_blind_analytic_line` | account.analytic.line | analytic |
| 16 | `rule_it_admin_blind_stock_quant` | stock.quant | stock |
| 17 | `rule_it_admin_blind_stock_valuation_report` | stock.account.stock.valuation.report | stock_account |

### 3.3 Blocked Models - ops_matrix_accounting (7 rules in ops_accounting_rules.xml)

| # | XML ID | Model | Notes |
|---|--------|-------|-------|
| 18 | `rule_it_admin_blind_pdc_receivable` | ops.pdc.receivable | PDC Receivable |
| 19 | `rule_it_admin_blind_pdc_payable` | ops.pdc.payable | PDC Payable |
| 20 | `rule_it_admin_blind_budget` | ops.budget | Budget |
| 21 | `rule_it_admin_blind_budget_line` | ops.budget.line | Budget Line |
| 22 | `rule_it_admin_blind_asset` | ops.asset | Asset |
| 23 | `rule_it_admin_blind_asset_category` | ops.asset.category | Asset Category |
| 24 | `rule_it_admin_blind_asset_depreciation` | ops.asset.depreciation | Asset Depreciation |

### 3.4 Blocked Models - ops_kpi (1 rule in ops_kpi_security.xml)

| # | XML ID | Model | Notes |
|---|--------|-------|-------|
| 25 | `rule_kpi_value_it_admin_blind` | ops.kpi.value | KPI values (financial data) |

**Total IT Admin Blindness Rules: 25**

> **Important**: IT Admin CAN access KPI definitions (`ops.kpi`), KPI boards (`ops.kpi.board`), and KPI widgets (`ops.kpi.widget`) because these are administrative/configuration items, not business data. Only `ops.kpi.value` (the actual numerical data) is blocked.

### 3.5 Legacy Global Rules (ir_rule_it_blind.xml)

These are older global rules in `ir_rule_it_blind.xml` that use the pattern:
```
[(user.has_group('ops_matrix_core.group_ops_it_admin'), '=', False)]
```

| XML ID | Model |
|--------|-------|
| `rule_it_admin_blind_sale_order` | sale.order |
| `rule_it_admin_blind_purchase_order` | purchase.order |
| `rule_it_admin_blind_account_move` | account.move |
| `rule_it_admin_blind_account_payment` | account.payment |
| `rule_it_admin_blind_account_bank_statement` | account.bank.statement |
| `rule_it_admin_blind_stock_quant` | stock.quant |
| `rule_it_admin_blind_sale_order_line` | sale.order.line |
| `rule_it_admin_blind_purchase_order_line` | purchase.order.line |
| `rule_it_admin_blind_account_move_line` | account.move.line |
| `rule_it_admin_blind_stock_picking` | stock.picking |
| `rule_it_admin_blind_stock_move` | stock.move |
| `rule_it_admin_blind_stock_valuation_layer` | stock.valuation.layer |

Note: These overlap with the newer rules in `ir_rule.xml`. The same XML IDs are reused in `ir_rule.xml` which means the newer definitions override the older ones.

---

## 4. Branch Isolation Matrix

### 4.1 ops_matrix_core Branch Isolation Rules

| XML ID | Model | Domain | Groups | Perms |
|--------|-------|--------|--------|-------|
| `rule_ops_branch_access` | ops.branch | `[('id', 'in', user.ops_allowed_branch_ids.ids)]` | `base.group_user` | Read |
| `rule_ops_sale_order_branch_user` | sale.order | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `sales_team.group_sale_salesman` | RWCD |
| `rule_ops_sale_order_line_user` | sale.order.line | `['&', ('order_id.ops_branch_id', 'in', user.ops_allowed_branch_ids.ids), ('order_id.ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)]` | `sales_team.group_sale_salesman` | RWCD |
| `rule_ops_purchase_order_branch_user` | purchase.order | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `purchase.group_purchase_user` | RWCD |
| `rule_ops_account_move_branch_user` | account.move | `['|', non-invoice types, '&' branch + company filter]` | `account.group_account_user`, `account.group_account_manager` | RWCD |
| `rule_ops_account_move_line_user` | account.move.line | `['&', ('move_id.ops_branch_id', 'in', ...), ('move_id.ops_business_unit_id', 'in', ...)]` | `account.group_account_invoice` | RWCD |
| `rule_ops_account_payment_branch_user` | account.payment | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `account.group_account_user`, `account.group_account_manager` | RWCD |
| `rule_ops_stock_picking_user` | stock.picking | `['|', ('ops_branch_id', '=', False), '&', branch AND BU filter]` | `stock.group_stock_user` | Read |
| `rule_ops_stock_picking_write` | stock.picking | `[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `stock.group_stock_user` | Write/Create/Delete |
| `rule_ops_stock_move_user` | stock.move | `['|', ('picking_id.ops_branch_id', '=', False), '&', branch AND BU filter]` | `stock.group_stock_user` | RWCD |
| `rule_ops_inter_branch_transfer_access` | ops.inter.branch.transfer | `['|','|', source_branch, dest_branch, company]` | `stock.group_stock_user` | RWCD |
| `rule_matrix_intersection` | ops.approval.request | `['&', branch AND BU intersection]` | `base.group_user` | RWCD |
| `rule_product_request_branch` | ops.product.request | `[('branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `base.group_user` | RWCD |
| `rule_warehouse_manager_branch_only` | stock.warehouse | `['|', branch filter, company filter]` | `stock.group_stock_user` | RWCD |
| `rule_pricelist_matrix_visibility` | product.pricelist | `['|', not matrix, '&' branch AND BU]` | `base.group_user` | RWCD |
| `rule_sale_order_branch_manager_isolation` | sale.order | `[('ops_branch_id', '=', user.default_branch_id.id)]` | `group_ops_branch_manager` | RWC (no D) |
| `rule_purchase_order_branch_manager_isolation` | purchase.order | `[('ops_branch_id', '=', user.default_branch_id.id)]` | `group_ops_branch_manager` | RWC (no D) |

### 4.2 ops_matrix_accounting Branch Isolation Rules

| XML ID | Model | Domain | Groups | Perms |
|--------|-------|--------|--------|-------|
| `rule_ops_pdc_receivable_branch_isolation` | ops.pdc.receivable | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', ...)]` | `group_ops_user` | RWC (no D) |
| `rule_ops_pdc_payable_branch_isolation` | ops.pdc.payable | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', ...)]` | `group_ops_user` | RWC (no D) |
| `rule_ops_budget_branch_isolation` | ops.budget | `[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]` | `group_ops_user` | R only |
| `rule_ops_budget_line_branch_isolation` | ops.budget.line | `[('budget_id.ops_branch_id', 'in', ...)]` | `group_ops_user` | R only |
| `rule_ops_asset_branch_isolation` | ops.asset | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', ...)]` | `group_ops_user` | R only |
| `rule_ops_asset_depreciation_branch_isolation` | ops.asset.depreciation | `['|', ('branch_id', '=', False), ('branch_id', 'in', ...)]` | `group_ops_user` | R only |
| `rule_ops_matrix_snapshot_branch_isolation` | ops.matrix.snapshot | `['|', ('branch_id', '=', False), ('branch_id', 'in', ...)]` | `group_ops_user` | R only |
| `rule_ops_report_template_branch_isolation` | ops.report.template | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', ...)]` | `base.group_user` | RWC (no D) |
| `rule_ops_period_branch_lock_branch_isolation` | ops.fiscal.period.branch.lock | `['|', ('ops_branch_id', '=', False), ('ops_branch_id', 'in', ...)]` | `group_ops_user` | R only |

### 4.3 Corporate Audit Log Branch Rules

| XML ID | Model | Domain | Groups |
|--------|-------|--------|--------|
| `ops_corporate_audit_log_branch_rule` | ops.corporate.audit.log | `['|','|', ('branch_id', '=', False), ('branch_id', 'in', user.ops_allowed_branch_ids.ids), ('user_id', '=', user.id)]` | `group_ops_user`, `group_ops_manager` |

---

## 5. Company Isolation Matrix

| XML ID | Model | Domain | Groups | File |
|--------|-------|--------|--------|------|
| `rule_ops_company_access` | res.company | `[('id', 'in', user.company_ids.ids)]` | `base.group_user` | ir_rule.xml |
| `rule_ops_stock_quant_access` | stock.quant | `[('company_id', 'in', user.company_ids.ids)]` | `stock.group_stock_user` | ir_rule.xml |
| `rule_ops_governance_rule_access` | ops.governance.rule | `[('company_id', 'in', user.company_ids.ids)]` | `group_ops_manager` | ir_rule.xml |
| `ops_asset_user_rule` | ops.asset | `[('company_id', '=', user.company_id.id)]` | `group_ops_user` | ops_asset_security.xml |
| `ops_asset_company_rule` | ops.asset | `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` | _(global)_ | ops_asset_security.xml |
| `ops_asset_category_company_rule` | ops.asset.category | `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` | _(global)_ | ops_asset_security.xml |
| `ops_asset_depreciation_company_rule` | ops.asset.depreciation | `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` | _(global)_ | ops_asset_security.xml |
| `rule_ops_fiscal_period_company_isolation` | ops.fiscal.period | `[('company_id', '=', user.company_id.id)]` | `group_ops_user` | ops_accounting_rules.xml |
| `rule_ops_period_checklist_company_isolation` | ops.period.close.checklist | `[('period_id.company_id', '=', user.company_id.id)]` | `group_ops_user` | ops_accounting_rules.xml |
| `ops_corporate_audit_log_company_rule` | ops.corporate.audit.log | `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` | `base.group_user` | ops_corporate_audit_rules.xml |
| `rule_kpi_board_company` | ops.kpi.board | `[('company_id', 'in', company_ids)]` | `base.group_user` | ops_kpi_security.xml |
| `rule_kpi_value_company` | ops.kpi.value | `[('company_id', 'in', company_ids)]` | `base.group_user` | ops_kpi_security.xml |

---

## 6. System Admin Bypass Rules

These rules grant `base.group_system` full access `[(1, '=', 1)]` to prevent lockout:

| XML ID | Model | File |
|--------|-------|------|
| `ops_branch_admin_full_access` | ops.branch | ir_rule.xml |
| `ops_business_unit_admin_full_access` | ops.business.unit | ir_rule.xml |
| `ops_sale_order_line_admin_override` | sale.order.line | ir_rule.xml |
| `ops_account_move_line_admin_override` | account.move.line | ir_rule.xml |
| `ops_account_payment_admin_full_access` | account.payment | ir_rule.xml |
| `ops_sale_order_admin_full_access` | sale.order | ir_rule.xml |
| `ops_sale_order_line_admin_full_access` | sale.order.line | ir_rule.xml |
| `ops_purchase_order_admin_full_access` | purchase.order | ir_rule.xml |
| `ops_account_move_admin_full_access` | account.move | ir_rule.xml |
| `ops_account_move_line_admin_full_access` | account.move.line | ir_rule.xml |
| `ops_stock_picking_admin_full_access` | stock.picking | ir_rule.xml |
| `ops_stock_move_admin_full_access` | stock.move | ir_rule.xml |
| `ops_stock_quant_admin_full_access` | stock.quant | ir_rule.xml |
| `ops_persona_admin_full_access` | ops.persona | ir_rule.xml |
| `ops_persona_delegation_admin_full_access` | ops.persona.delegation | ir_rule.xml |
| `ops_governance_rule_admin_full_access` | ops.governance.rule | ir_rule.xml |
| `ops_inter_branch_transfer_admin_full_access` | ops.inter.branch.transfer | ir_rule.xml |
| `ops_approval_request_admin_full_access` | ops.approval.request | ir_rule.xml |
| `ops_product_template_admin_full_access` | product.template | ir_rule.xml |
| `ops_product_product_admin_full_access` | product.product | ir_rule.xml |
| `ops_product_request_admin_full_access` | ops.product.request | ir_rule.xml |
| `ops_warehouse_admin_full_access` | stock.warehouse | ir_rule.xml |
| `ops_pricelist_admin_full_access` | product.pricelist | ir_rule.xml |
| `rule_ops_pdc_receivable_admin_override` | ops.pdc.receivable | ops_accounting_rules.xml |
| `rule_ops_pdc_payable_admin_override` | ops.pdc.payable | ops_accounting_rules.xml |
| `rule_ops_budget_admin_override` | ops.budget | ops_accounting_rules.xml |
| `rule_ops_budget_line_admin_override` | ops.budget.line | ops_accounting_rules.xml |
| `rule_ops_asset_admin_override` | ops.asset | ops_accounting_rules.xml |
| `rule_ops_asset_category_admin_override` | ops.asset.category | ops_accounting_rules.xml |
| `rule_ops_asset_depreciation_admin_override` | ops.asset.depreciation | ops_accounting_rules.xml |
| `rule_ops_matrix_snapshot_admin_override` | ops.matrix.snapshot | ops_accounting_rules.xml |
| `rule_ops_report_template_admin_override` | ops.report.template | ops_accounting_rules.xml |
| `rule_ops_fiscal_period_admin_override` | ops.fiscal.period | ops_accounting_rules.xml |
| `rule_ops_period_branch_lock_admin_override` | ops.fiscal.period.branch.lock | ops_accounting_rules.xml |
| `rule_ops_period_checklist_admin_override` | ops.period.close.checklist | ops_accounting_rules.xml |
| `ops_corporate_audit_log_system_rule` | ops.corporate.audit.log | ops_corporate_audit_rules.xml |

**Total System Admin Bypass Rules: 36**

---

## 7. ACL Summary

### 7.1 ops_matrix_core (165 ACL rules)

| Model | group_ops_user | group_ops_manager | group_ops_admin_power | base.group_system | Other Groups |
|-------|:---:|:---:|:---:|:---:|-----|
| ops.branch | R | RWC | RWCD | RWCD | purchase.user(R), stock.user(R), sale.salesman(R) |
| ops.business.unit | R | RWC | RWCD | RWCD | purchase.user(R), stock.user(R), sale.salesman(R) |
| ops.persona | R | RWCD | RWCD | RWCD | |
| ops.persona.delegation | RWC | - | RWCD | RWCD | |
| ops.inter.branch.transfer | RWC | RWCD | RWCD | RWCD | |
| ops.governance.rule | R | RWCD | RWCD | RWCD | |
| ops.approval.rule | R | RWCD | RWCD | RWCD | |
| ops.governance.discount.limit | R | RWCD | RWCD | RWCD | |
| ops.governance.margin.rule | R | RWCD | RWCD | RWCD | |
| ops.governance.price.authority | R | RWCD | RWCD | RWCD | |
| ops.approval.workflow | R | RWCD | RWCD | RWCD | |
| ops.approval.workflow.step | R | RWCD | RWCD | RWCD | |
| ops.approval.request | RWC | RWCD | RWCD | RWCD | sale.salesman(RWC), purchase.user(RWC) |
| ops.approval.dashboard | R | - | RWCD | RWCD | |
| ops.sla.template | R | RWCD | RWCD | RWCD | |
| ops.sla.instance | RWC | - | RWCD | RWCD | |
| ops.archive.policy | - | - | RWCD | RWCD | |
| ops.product.request | RWC | RWCD | RWCD | RWCD | product_approver(RWCD), sale.salesman(RWC) |
| ops.security.audit | R | R | R | R | |
| ops.dashboard.config | - | - | RWCD | RWCD | base.user(RWCD) |
| ops.dashboard.widget | R | RW | RWCD | RWCD | base.user(R) |
| ops.api.key | - | - | RWCD | RWCD | |
| ops.audit.log | - | - | R | R | |
| ops.three.way.match | - | - | RWCD | RWCD | purchase.user(RWC), purchase.manager(RWCD) |
| ops.report.template | - | - | RWCD | RWCD | base.user(RWCD) |
| ops.report.template.line | - | - | RWCD | RWCD | base.user(RWCD) |
| ops.segregation.of.duties | R | RWC | RWCD | RWCD | |
| ops.segregation.of.duties.log | R | R | R | R | |
| ops.field.visibility.rule | R | RWC | RWCD | RWCD | |
| ops.session.manager | - | - | - | RWCD | base.user(R) |
| ops.ip.whitelist | - | - | RWC | RWCD | |
| ops.data.archival | - | - | R | RWCD | |
| ops.archived.record | - | - | R | RWCD | |
| ops.performance.monitor | - | - | R | RWCD | |
| ops.matrix.config | - | - | - | RWCD | account.user(R), account.invoice(R) |
| ops.secure.export.wizard | - | - | - | RWCD | can_export(RWCD) |
| ops.security.compliance.check | - | R | RWCD | RWCD | |
| ops.security.compliance.result | - | R | RWCD | RWCD | |
| ops.persona.drift.wizard | - | - | RWCD | RWCD | |
| ops.persona.drift.result | - | - | RWCD | RWCD | |
| ops.audit.evidence.wizard | - | - | RWCD | RWCD | |
| ops.corporate.audit.log | - | - | R | R | compliance_officer(RW) |
| ops.sale.order.import.wizard | - | - | RWCD | RWCD | sale.salesman(RWC), sale.manager(RWCD) |
| ops.security.resolve.wizard | - | - | - | RWCD | |
| ops.ip.test.wizard | - | - | - | RWCD | |

### 7.2 ops_matrix_accounting (246 ACL rules)

| Model | group_ops_user | group_ops_manager | group_ops_admin_power | base.group_system | Other Groups |
|-------|:---:|:---:|:---:|:---:|-----|
| ops.pdc.receivable | - | - | RWCD | RWCD | base.user(RWC), account.manager(RWCD) |
| ops.pdc.payable | - | - | RWCD | RWCD | base.user(RWC), account.manager(RWCD) |
| ops.budget | R | RWCD | RWCD | RWCD | |
| ops.budget.line | R | RWCD | RWCD | RWCD | |
| ops.company.consolidation | RWCD | RWCD | RWCD | RWCD | |
| ops.branch.report | RWCD | RWCD | RWCD | RWCD | |
| ops.business.unit.report | RWCD | RWCD | RWCD | RWCD | |
| ops.consolidated.balance.sheet | RWCD | RWCD | RWCD | RWCD | |
| ops.matrix.profitability.analysis | RWCD | RWCD | RWCD | RWCD | |
| ops.asset | R | RWCD | RWCD | RWCD | |
| ops.asset.category | R | RWCD | RWCD | RWCD | |
| ops.asset.depreciation | R | RWCD | RWCD | RWCD | |
| ops.matrix.snapshot | R | R | RWCD | RWCD | |
| ops.trend.analysis | RWCD | RWCD | RWCD | RWCD | |
| ops.report.template | - | RWCD | RWCD | RWCD | base.user(RWC) |
| ops.report.audit | - | - | R | RWCD | account.manager(R) |
| ops.fiscal.period | R | RWCD | RWCD | RWCD | |
| ops.fiscal.period.branch.lock | R | RWCD | RWCD | RWCD | |
| ops.period.close.checklist | RW | RWCD | RWCD | RWCD | |
| ops.recurring.template | R | RWCD | RWCD | RWCD | |
| ops.recurring.template.line | R | RWCD | RWCD | RWCD | |
| ops.recurring.entry | R | RWCD | RWCD | RWCD | |
| ops.recurring.entry.line | R | RWCD | RWCD | RWCD | |
| ops.journal.template | R | RWCD | RWCD | RWCD | |
| ops.journal.template.line | R | RWCD | RWCD | RWCD | |
| ops.financial.report.config | R | RWCD | RWCD | RWCD | |
| ops.followup | R | RWCD | RWCD | RWCD | |
| ops.followup.line | R | RWCD | RWCD | RWCD | |
| ops.partner.followup | R | RWCD | RWCD | RWCD | |
| ops.partner.followup.history | R | RWC | RWCD | RWCD | |
| ops.interbranch.transfer | R | RWCD | RWCD | RWCD | |
| ops.bank.reconciliation | R | RWCD | RWCD | RWCD | |
| ops.bank.reconciliation.line | R | RWCD | RWCD | RWCD | |
| ops.lease | R | RWCD | RWCD | RWCD | |
| ops.lease.payment.schedule | R | RWCD | RWCD | RWCD | |
| ops.lease.depreciation | R | RWCD | RWCD | RWCD | |
| ops.gl.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.tb.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.pnl.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.bs.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.cf.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.aged.report.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| ops.partner.ledger.wizard | - | - | - | RWCD | accountant(RWCD), finance_mgr(RWCD), cfo(RWCD), executive(R), compliance(R) |
| _(+20 more wizard models)_ | | | | | |

### 7.3 ops_kpi (13 ACL rules)

| Model | base.group_user | group_ops_admin_power | group_ops_it_admin |
|-------|:---:|:---:|:---:|
| ops.kpi | R | RWCD | RWCD |
| ops.kpi.value | R | RWCD | R (blind by record rule) |
| ops.kpi.board | R | RWCD | RWCD |
| ops.kpi.widget | R | RWCD | RWCD |

### 7.4 ACL Totals

| Module | ACL Rules |
|--------|-----------|
| ops_matrix_core | 165 |
| ops_matrix_accounting | 246 |
| ops_kpi | 13 |
| **TOTAL** | **424** |

---

## 8. Field-Level Security

### 8.1 Python Field Groups (groups= attribute)

#### sale.order.line (ops_matrix_core/models/sale_order_line.py)

| Field | Groups | Purpose |
|-------|--------|---------|
| `purchase_price` | `base.group_system`, `group_ops_manager` | Cost price - hidden from regular users |
| `margin` | `base.group_system`, `group_ops_manager` | Gross margin amount - hidden from regular users |
| `margin_percent` | `base.group_system`, `group_ops_manager` | Gross margin percentage - hidden from regular users |

#### res.users API fields (ops_matrix_core/models/res_users_api.py)

| Field | Groups | Purpose |
|-------|--------|---------|
| `ops_api_key_ids` | `base.group_system` | API keys - system admin only |
| `ops_api_rate_limit` | `base.group_system` | Rate limit config - system admin only |
| `ops_api_allowed_ips` | `base.group_system` | IP whitelist - system admin only |

### 8.2 Programmatic Group Checks (has_group())

These are runtime checks in Python code that enforce field/action visibility:

| Check | File | Purpose |
|-------|------|---------|
| `has_group('group_ops_price_manager')` | sale_order_line.py | Controls who can edit unit prices |
| `has_group('group_ops_see_cost')` | ops_kpi.py, secure_export_wizard.py, asset_report_wizard.py, inventory_report_wizard.py | Filter out cost KPIs, hide cost columns in exports |
| `has_group('group_ops_see_margin')` | ops_kpi.py, secure_export_wizard.py | Filter out margin KPIs, hide margin columns |
| `has_group('group_ops_see_valuation')` | inventory_report_wizard.py | Control stock valuation visibility |
| `has_group('group_ops_can_export')` | secure_export_wizard.py, ops_base_report_wizard.py, ops_excel_renderer.py | Gate all data export operations |

---

## 9. Segregation of Duties (SoD)

### 9.1 Hardcoded SoD Conflict Pairs

Defined in `ops_matrix_core/models/res_users_sod.py` as `SOD_CONFLICT_PAIRS`:

| # | Group 1 | Group 2 | Conflict Description |
|---|---------|---------|---------------------|
| 1 | `group_ops_it_admin` | `group_ops_admin_power` | IT Admin cannot have OPS Admin Power rights |
| 2 | `group_ops_it_admin` | `group_ops_see_cost` | IT Admin cannot see cost data |
| 3 | `group_ops_it_admin` | `account.group_account_manager` | IT Admin cannot be Account Manager |
| 4 | `group_ops_it_admin` | `purchase.group_purchase_manager` | IT Admin cannot be Purchase Manager |
| 5 | `group_ops_it_admin` | `sales_team.group_sale_manager` | IT Admin cannot be Sales Manager |
| 6 | `group_ops_it_admin` | `stock.group_stock_manager` | IT Admin cannot be Stock Manager |

### 9.2 SoD Enforcement

- Conflicts are **detected** via `_compute_sod_conflicts()` on `res.users`
- Violations are **logged** to `ops.segregation.of.duties.log` model
- The `ops.security.compliance.check` model can run automated SoD audits (`_check_sod_conflicts()`)
- Conflicts generate `critical` severity results in compliance checks

### 9.3 Design Principle

All 6 SoD pairs enforce the **IT Admin Isolation Principle**: the IT Administrator role must remain completely separated from any business data access or management capability. This prevents a single individual from having both system administration privileges and business transaction authority.

---

## 10. Menu Restrictions

### 10.1 Technical Menu

| Menu | Restricted To | File |
|------|---------------|------|
| `base.menu_administration` (Settings) | `group_ops_it_admin`, `base.group_system` | technical_menu_restrictions.xml |

### 10.2 KPI Module Menus

| Menu | Groups | File |
|------|--------|------|
| KPI Configuration menus (4 items) | `group_ops_admin_power`, `group_ops_it_admin` | ops_kpi_menus.xml |
| KPI Center Settings | `group_ops_admin_power`, `group_ops_it_admin` | res_config_settings_views.xml |

### 10.3 Accounting Module Menu Groups

The accounting menus in `ops_matrix_accounting/views/accounting_menus.xml` use granular OPS group restrictions. Summary of access patterns:

| Menu Section | Accessible By |
|-------------|---------------|
| **Operations** (Invoicing, Bills, Payments) | accountant, finance_manager, cfo, treasury, executive, branch_manager |
| **Journals & Templates** | accountant, finance_manager, cfo |
| **Assets** (Assets, Categories, Depreciation) | accountant, finance_manager, cfo, branch_manager |
| **Analytics & Planning** (GL, TB, P&L, BS, CF, Aged, Partner Ledger, Daily Reports) | accountant, finance_manager, cfo, executive |
| **Budget vs Actual, Consolidation Reports** | cfo, executive, finance_manager, bu_leader, branch_manager |
| **Treasury** (PDC, Cash Forecast) | treasury, finance_manager, cfo, accountant |
| **Inventory Reports** | inventory_manager, finance_manager, cfo |
| **Period Close** | finance_manager, accountant, cfo |
| **Configuration** (Financial Reports, Report Templates, Followup, Fiscal Periods, Recurring, Bank Reconciliation) | admin_power, finance_manager |
| **Audit & Compliance** | cfo, compliance_officer |
| **PDC Payable** (special menu) | treasury, finance_manager, cfo, accountant |

---

## 11. Corporate Audit Log Rules

The `ops.corporate.audit.log` model has specialized security for SOX/ISO 27001/GDPR compliance:

| Rule | Domain | Groups | Perms | Purpose |
|------|--------|--------|-------|---------|
| Company Isolation | `company_id in company_ids` | `base.group_user` | R only | Multi-tenant security |
| No Deletion | `[(0, '=', 1)]` (always false) | ALL groups | Unlink only | **Immutability enforcement** - nobody can delete |
| No Direct Creation | `[(0, '=', 1)]` (always false) | ALL groups | Create only | Only via model methods (sudo) |
| Compliance Review | `company_id in company_ids` | `group_ops_compliance_officer` | RW | Review and annotate |
| Branch Access | branch + user filter | `group_ops_user`, `group_ops_manager` | R only | Branch-level filtering |
| System Admin Read | `[(1, '=', 1)]` | `base.group_system` | R only | Full read, no write/delete |

> **Key Design**: Even `base.group_system` cannot delete or directly create audit logs. The `[(0, '=', 1)]` domain applies to ALL groups including system admin for unlink and create operations.

---

## 12. Statistics Summary

### 12.1 Overall Counts

| Metric | Count |
|--------|-------|
| **OPS Security Groups** | 24 |
| **External Groups Referenced** | 12 |
| **Total ACL Rules** | 424 |
| **IT Admin Blindness Rules** | 25 (17 core + 7 accounting + 1 KPI) |
| **Branch Isolation Rules** | 18+ |
| **Company Isolation Rules** | 12 |
| **System Admin Bypass Rules** | 36 |
| **SoD Conflict Pairs** | 6 |
| **Corporate Audit Log Rules** | 6 |
| **Field-Level Security (Python groups=)** | 6 fields |
| **Programmatic Group Checks (has_group)** | 10+ locations |
| **Menu Restrictions** | 60+ menus with group filters |

### 12.2 Security Layers Summary

The OPS Framework implements a **7-layer security model**:

```
Layer 1: ACL (ir.model.access.csv)     - 424 rules across 3 modules
Layer 2: Record Rules (ir.rule)         - 100+ rules with branch/company/matrix isolation
Layer 3: IT Admin Blindness             - 25 rules blocking IT from business data
Layer 4: Field-Level Security           - groups= on Python fields
Layer 5: Programmatic Checks            - has_group() runtime enforcement
Layer 6: Segregation of Duties          - 6 conflict detection pairs
Layer 7: Menu Restrictions              - 60+ granular menu group filters
```

### 12.3 Unique Models with Security Rules

| Module | Unique Models Covered by ACLs | Unique Models with Record Rules |
|--------|---:|---:|
| ops_matrix_core | 44 | 26+ |
| ops_matrix_accounting | 48 | 18+ |
| ops_kpi | 4 | 4 |
| **TOTAL** | **96** | **48+** |

---

## Appendix A: IT Admin Allowed Access

For completeness, what the IT Admin CAN do:

| Area | Access Level | Notes |
|------|-------------|-------|
| User management | Full | Create/modify users, assign groups |
| System configuration | Full | Settings, technical parameters |
| Module management | Full | Install/update modules |
| KPI Definitions | Full CRUD | `ops.kpi` model (admin config) |
| KPI Boards | Full CRUD | `ops.kpi.board` model (admin config) |
| KPI Widgets | Full CRUD | `ops.kpi.widget` model (admin config) |
| KPI Values | **BLOCKED** | `ops.kpi.value` - financial data |
| Technical menu | Visible | `base.menu_administration` |
| Debug mode | Available | `base.group_no_one` |
| All business data | **BLOCKED** | 25 models completely hidden |

## Appendix B: Cross-Branch BU Leader Rules

Special rules that allow BU Leaders to see data across branches within their business unit:

| XML ID | Model | Groups |
|--------|-------|--------|
| `rule_ops_cross_branch_bu_leader_sales` | sale.order | `group_ops_cross_branch_bu_leader` |
| `rule_ops_cross_branch_bu_leader_purchases` | purchase.order | `group_ops_cross_branch_bu_leader` |
| `rule_ops_cross_branch_bu_leader_invoices` | account.move | `group_ops_cross_branch_bu_leader` |
| `rule_sale_order_bu_leader_isolation` | sale.order | `group_ops_bu_leader` |
| `rule_purchase_order_bu_leader_isolation` | purchase.order | `group_ops_bu_leader` |
| `rule_ops_sale_order_bu_manager` | sale.order | `group_ops_manager` |
| `rule_ops_purchase_order_bu_manager` | purchase.order | `group_ops_manager` |
| `rule_ops_account_move_bu_manager` | account.move | `group_ops_manager` |

## Appendix C: Matrix Administrator Special Rules

| XML ID | Model | Purpose |
|--------|-------|---------|
| `rule_ops_matrix_admin_bu` | ops.business.unit | See all business units |
| `rule_ops_matrix_admin_governance` | ops.governance.rule | See all governance rules |

## Appendix D: Product/Catalog Security

| XML ID | Model | Domain | Groups |
|--------|-------|--------|--------|
| `rule_product_business_unit_silo` | product.template | `['|','|', no BU, user's BUs, user's companies]` | `base.group_user` |
| `rule_product_product_bu_silo` | product.product | `['|','|', no BU on template, user's BUs, user's companies]` | `base.group_user` |

---

_End of OPS Security Matrix_
