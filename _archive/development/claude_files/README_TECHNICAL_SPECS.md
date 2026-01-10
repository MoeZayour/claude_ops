# OPS Matrix Technical Specification - Complete Index

## Overview

This documentation package contains **exhaustive technical specifications** for three Odoo 19 modules that comprise the OPS Matrix framework. Each specification is designed to be detailed enough for a developer (or AI) to **reconstruct the module from scratch** without seeing the original code.

---

## Documentation Files

### 1. [OPS_MATRIX_CORE_TECHNICAL_SPEC.md](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md)
**Core Module:** The foundational operational structure

**Key Topics:**
- **Models:** ops.branch, ops.business.unit, ops.persona, ops.governance.rule, ops.approval.request, ops.sla.template, ops.sla.instance
- **Mixins:** ops.matrix.mixin (dimensional awareness), ops.governance.mixin (approval workflows), ops.sla.mixin
- **Extensions:** sale.order, account.move, stock.move, stock.picking, product.template, res.partner, res.users
- **Engines:**
  - **Matrix Structure:** Geographic branches + strategic business units
  - **Persona Engine:** Role-based matrix assignments with delegation capability
  - **Governance Engine:** Dynamic rules for approvals, blocks, and warnings
  - **SLA Engine:** Time-based deadline tracking and status monitoring

**Document Structure:**
1. General Info & Dependencies
2. Data Models & Fields (detailed field tables)
3. Key Methods & Business Logic (step-by-step workflows)
4. XML Views & Interface (form/tree/kanban layouts)
5. Security (groups, access rights, record rules)
6. Data & Configuration Files
7. Standard Model Extensions
8. Static Assets (JS, CSS, components)
9. Modules Workflow Summary
10. Key Design Patterns
11. Integration Points
12. Customization Hooks

**File Size:** ~5,000 lines (comprehensive)

---

### 2. [OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md)
**Accounting Module:** Enterprise financial management

**Key Topics:**
- **Models:** ops.budget, ops.budget.line, ops.pdc (Post-Dated Checks)
- **Wizards:** ops.financial.report.wizard, ops.general.ledger.wizard
- **Extensions:** product.category, product.template
- **Features:**
  - **Budget Control:** Multi-dimensional budgets with real-time availability checks
  - **PDC Management:** Post-dated check workflow (register â†’ deposit â†’ clear)
  - **Financial Reports:** GL, P&L, Balance Sheet, Aged AR/AP
  - **Excel Export:** In-memory generation, zero DB bloat

**Document Structure:**
1. General Info & Dependencies
2. Data Models & Fields
3. Key Methods & Business Logic
4. XML Views & Interface
5. Security & Access Control
6. Data & Configuration Files
7. Reports (GL, Financial, XLSX)
8. Integration Points
9. Workflow Examples
10. Key Design Patterns
11. Future Extensibility Hooks

**File Size:** ~2,500 lines

---

### 3. [OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md)
**Reporting Module:** High-performance SQL-based analytics

**Key Topics:**
- **Models:** ops.sales.analysis, ops.financial.analysis, ops.inventory.analysis
- **Type:** Read-only PostgreSQL views (materialized-style)
- **Features:**
  - **Sales Analysis:** Branch/BU-aware metrics with margin tracking
  - **Financial Analysis:** Multi-dimensional GL reporting
  - **Inventory Analysis:** Stock segregation by BU, health monitoring

**Document Structure:**
1. General Info & Dependencies
2. Data Models & Fields (view columns)
3. Key Methods & Business Logic (SQL views, aggregation queries)
4. Security & Access Control
5. XML Views & Interface (tree/pivot/search views)
6. Data & Configuration Files
7. Static Assets (CSS)
8. Integration Points
9. Performance Characteristics
10. Key Design Patterns
11. Reporting Examples
12. Future Extensibility
13. SQL View Creation & Maintenance

**File Size:** ~2,000 lines

---

## How to Use This Documentation

### For Developers Building from Scratch:

1. **Start with Core Module:**
   - Read sections 1-5 of [OPS_MATRIX_CORE_TECHNICAL_SPEC.md](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md)
   - Understand the matrix structure, persona model, and governance rule engine
   - Implement models in order: Branch â†’ Business Unit â†’ Persona â†’ Governance â†’ Approval â†’ SLA

2. **Then Add Accounting:**
   - Read [OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md)
   - Implement budget and PDC models
   - Add wizards for financial reporting

3. **Finally Add Reporting:**
   - Read [OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md)
   - Create PostgreSQL views for sales, financial, and inventory analysis
   - Configure dashboard views and security

### For Code Review & Validation:

- Use the **"Key Methods & Business Logic"** sections to verify implementation correctness
- Cross-reference the **"Security"** section to ensure access control matches
- Check **"Integration Points"** to identify dependencies

### For Customization & Enhancement:

- Refer to **"Future Extensibility Hooks"** section in each spec
- Use **"Design Patterns"** section to maintain architectural consistency
- Follow **"Workflow Examples"** as templates for new processes

### For Documentation & Knowledge Transfer:

- Share the **"General Info"** section with stakeholders
- Present **"Workflow Examples"** to end users
- Use **"Integration Points"** to onboard IT teams

---

## Key Architectural Concepts

### 1. Matrix Dimensions
Every transactional record is tagged with:
- **Branch** (geographic/operational location)
- **Business Unit** (strategic/product line)

This enables:
- Multi-dimensional reporting (slice by branch, BU, or intersection)
- Segregated data access (users see only their branch/BU)
- Distributed operations (each branch/BU has autonomous control)

### 2. Governance by Rules
Dynamic rule engine allows conditional actions:
- **Warning:** Log message to chatter
- **Block:** Prevent operation with exception
- **Approval:** Route to designated approvers

Examples:
- High-value orders require approval
- Cross-BU product sales blocked
- High-margin sales tracked

### 3. Persona-Based Access Control
User â†’ Persona â†’ Matrix Assignments + Delegation

- One persona per user (unique constraint)
- Persona contains: branch, BU, job level, approval limits, security groups
- Delegation allows temporary authority transfer (with time window)
- `effective_user_id` computed field resolves actual power holder

### 4. Zero DB Bloat Reporting
- No intermediate fact tables
- No ETL pipelines
- Views query base tables directly
- Aggregation pushdown to database (SQL GROUP BY)
- Lightweight wizards (transient, auto-delete)

### 5. SQL View-Based Analytics
- Read-only PostgreSQL views for high-performance reporting
- Calculated fields (margin, balance) at view level
- Security applied at row level (ir.rule)
- Spreadsheet dashboard integration

---

## Field Naming Conventions

| Pattern | Usage | Example |
| --- | --- | --- |
| `ops_*_id` | Matrix dimensions (branch, BU) | ops_branch_id, ops_business_unit_id |
| `*_ids` | Many2many collections | allowed_branch_ids, access_group_ids |
| `*_request_ids` | One2many approval/request lists | approval_request_ids |
| `*_line_ids` | One2many line items | line_ids (budget lines) |
| `*_count` | Computed count fields | approval_request_count |
| `is_*` | Boolean status fields | is_delegated |
| `can_*` | Permission flags | can_approve_orders |

---

## Sequence Definitions

Auto-generated codes are created via ir.sequence:
- `ops.branch` â†’ Branch code (e.g., "NORTH")
- `ops.business.unit` â†’ BU code (e.g., "SALES")
- `ops.persona.code` â†’ Persona code (e.g., "PSN0001")
- `ops.governance.rule.code` â†’ Rule code (e.g., "GR0001")
- `ops.approval.request` â†’ Approval reference (e.g., "APP/0001")
- `ops.pdc` â†’ PDC reference (e.g., "PDC/0001")

---

## Security Model

### Three-Tier Access Control:

**1. Functional Groups** (`res.groups`):
- `group_ops_user` - Read-only base user
- `group_ops_manager` - Read/write/create (no delete)
- `group_ops_admin` - Full CRUD including delete
- `group_ops_product_approver` - Product request approval
- `group_ops_cost_controller` - Cost analysis reporting

**2. Record Rules** (`ir.rule`):
- Matrix intersection: User sees only records where Branch AND BU in allowed lists
- Branch visibility: User sees only allowed branches
- BU visibility: User sees only allowed business units
- Admin bypass: System admins (group_system) see all records

**3. Field-Level (via Views)**:
- Readonly fields: code (auto-generated), move_id (links to GL)
- Computeds: is_delegated, effective_user_id, totals
- Tracking fields: record changes logged to chatter

---

## Integration Workflows

### Setup Workflow (Day 1):
1. Admin creates branches (North, South)
2. Admin creates business units (Sales, Operations)
3. Admin creates personas:
   - Sales Manager (North branch, Sales BU, can approve $50K)
   - Ops Manager (South branch, Operations BU, can approve $10K)
4. Admin links personas to users (alice â†’ Sales Manager, bob â†’ Ops Manager)
5. User access rules auto-applied via persona

### Transaction Workflow (Daily):
1. Alice (Sales Manager - North) creates sales order for $30K
2. System checks: ops_branch_id=North, ops_business_unit_id=Sales
3. System evaluates governance rules:
   - If amount > $50K: require approval (none triggered)
   - If cross-BU products: block (none triggered)
   - If margin < 20%: warning (if triggered, post message)
4. Order confirmed, creates GL entry tagged with North + Sales
5. Budget line tracks actual vs. committed vs. available

### Reporting Workflow (Month-End):
1. Finance manager opens Sales Analysis
2. System shows pivot: branch on rows, product on columns
3. Metric: total revenue, total margin
4. Manager drills down to North branch: sees $500K revenue, 18% margin
5. Manager opens Financial Analysis
6. Shows GL by account, sliced by branch
7. Opens Inventory Analysis: shows stock position per BU
8. Exports all to spreadsheet for board presentation

---

## Module Dependencies Graph

```
Odoo Core Modules (base, mail, account, sale, stock, hr, product)
        â†“
ops_matrix_core (Matrix structure, Persona, Governance, SLA)
        â†“
   â”œâ”€â†’ ops_matrix_accounting (Budget, PDC, Financial Reports)
   â”‚
   â””â”€â†’ ops_matrix_reporting (Sales, Financial, Inventory Analysis)
```

**Dependency Rules:**
- Accounting **requires** Core
- Reporting **requires** Core (but not Accounting)
- Both Accounting and Reporting are **optional** (Core is the only mandatory module)

---

## Data Model Relationships

### Core Relationships:
```
User (res.users) â† 1:1 â†’ Persona â† M:N â†’ Branch, Business Unit
                              â†“
                       Persona Delegation â† Temporary Authority Transfer
                              â†“
                        Job Level, Approval Limits, Security Groups
```

### Governance Relationships:
```
Governance Rule â† N â†’ Model (target)
      â†“
   Condition (Domain OR Python Code)
      â†“
   Action (Warning, Block, Require Approval)
      â†“
Approval Request â† N â†’ Approver Users/Personas
      â†“
   State (Pending, Approved, Rejected, Cancelled)
```

### Accounting Relationships:
```
Budget â† 1:N â†’ Budget Lines â† M â†’ GL Accounts
  â†“
Branch, Business Unit (Matrix Dimensions)
  â†“
Practical Amount (from Posted Invoices)
Committed Amount (from Open POs)
Available = Planned - Practical - Committed
```

### Reporting Relationships:
```
sales_order_line â† SQL View â†’ Sales Analysis (Branch, BU, Margin)
account_move_line â† SQL View â†’ Financial Analysis (GL, Debit, Credit, Balance)
stock_quant â† SQL View â†’ Inventory Analysis (Stock, BU, Location, Value)
```

---

## Common Customization Patterns

### Add a New Governance Rule Type:
1. Add new ACTION_TYPE to `ops.governance.rule` selection
2. Implement logic in `_trigger_approval_if_needed()` method
3. Update condition evaluation in `_evaluate_condition()` (if needed)
4. Add UI button to trigger rule evaluation

### Extend Budget to Analytic Dimension:
1. Add `analytic_account_id` field to `ops.budget`
2. Modify `_compute_practical_amount()` to filter by analytic account
3. Add analytic_account_id to budget line domain
4. Update views to show analytic account selector

### Add Sales Report by Customer Segment:
1. Create new view in reporting module
2. Extend sales_analysis view to include customer segment
3. Add new method `get_summary_by_segment()` in ops.sales.analysis
4. Create tree/pivot views for segment analysis

### Implement Budget Approval Workflow:
1. Create approval workflow step: draft â†’ pending_approval â†’ confirmed â†’ done
2. Add approver_ids field to ops.budget
3. Implement action_request_approval() method
4. Add approval request creation in action_confirm()
5. Update views with approval statusbar

---

## Testing Strategy

### Unit Tests:
- **Models:** Test field constraints, computed fields, CRUD operations
- **Methods:** Test business logic (budget availability, persona delegation, rule evaluation)
- **Constraints:** Test SQL constraints, Python constrains validation

### Integration Tests:
- **Workflows:** Test complete workflows (PO â†’ Budget Check â†’ Approval â†’ GL Entry)
- **Security:** Test access control (users see only allowed data)
- **Reports:** Test view aggregation accuracy

### Performance Tests:
- **View Performance:** Query time for large recordsets (10K+ GL lines)
- **Aggregation:** Test GROUP BY performance with many dimensions
- **Scalability:** Test with multiple branches/BUs (100+)

---

## Troubleshooting Guide

### Issue: Users cannot see approved sales orders
**Likely Cause:** ir.rule domain too restrictive
**Solution:** Check `rule_sale_order_branch_visibility` in core; verify user.ops_allowed_branch_ids populated

### Issue: Budget lines show zero actual amount
**Likely Cause:** GL entries not tagged with branch/BU
**Solution:** Verify account.move.line includes branch_id, business_unit_id; check move_type = 'in_invoice'

### Issue: Margin calculation shows NULL
**Likely Cause:** Product standard_price not set
**Solution:** Ensure product_product.standard_price > 0; check product category defaults

### Issue: SLA deadline not computed
**Likely Cause:** Calendar not configured
**Solution:** Verify company.resource_calendar_id set; check ops.sla.template.calendar_id

### Issue: Persona delegation not active
**Likely Cause:** Delegation date window not inclusive
**Solution:** Ensure delegation_start â‰¤ now â‰¤ delegation_end (check server time zone)

---

## Performance Optimization Tips

### For Large Implementations (1000+ users):
1. Index frequently-filtered fields: ops_branch_id, ops_business_unit_id, date fields
2. Materialize high-volume views: ops_sales_analysis, ops_financial_analysis (nightly refresh)
3. Archive old approval requests (> 90 days) to reduce record count
4. Use batch approval workflows (approve multiple requests in one action)

### For Reporting:
1. Use date filters to reduce query scope (e.g., last 12 months)
2. Pre-compute monthly summaries in separate table for YoY comparison
3. Cache pivot views in spreadsheet dashboard (refresh on-demand)
4. Use PostgreSQL query plans (EXPLAIN ANALYZE) to identify slow queries

### For Budget Control:
1. Cache active budget queries (valid for 1 hour)
2. Use direct SQL for budget availability check (faster than ORM)
3. Batch budget checks in purchase order import wizard

---

## Version History & Compatibility

- **Odoo Version:** 19.0 Community Edition (Odoo 19)
- **Python:** 3.8+
- **Database:** PostgreSQL 12+
- **Module Versions:**
  - ops_matrix_core: 19.0.1.4.0
  - ops_matrix_accounting: 19.0.1.0.0
  - ops_matrix_reporting: 19.0.1.0

### Backward Compatibility Notes:
- ops.governance.rule includes legacy fields (min_margin_percent, max_discount_percent) for sales rules
- ops.persona includes both `primary_branch_id` (related) and `branch_id` (many2one) for compatibility
- product.category defaults attempt graceful fallback if account lookup fails

---

## Support & Documentation

### For Questions on Core Module:
Refer to [OPS_MATRIX_CORE_TECHNICAL_SPEC.md](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md) sections:
- Section 3: Key Methods & Business Logic
- Section 10: Key Design Patterns
- Section 11: Integration Points

### For Questions on Accounting:
Refer to [OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md) sections:
- Section 3: Key Methods & Business Logic
- Section 9: Workflow Examples
- Section 10: Key Design Patterns

### For Questions on Reporting:
Refer to [OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md) sections:
- Section 3: Key Methods & Business Logic
- Section 11: Reporting Examples
- Section 13: SQL View Creation & Maintenance

---

## Document Metadata

| Property | Value |
| --- | --- |
| **Revision Date** | December 2025 |
| **Format** | Markdown (.md) |
| **Total Lines** | ~9,500+ |
| **Total Models** | 15+ (Core, Accounting, Reporting) |
| **Total Fields Documented** | 150+ |
| **Total Methods Documented** | 50+ |
| **Security Rules** | 10+ |
| **Integration Points** | 8+ |
| **Design Patterns** | 15+ |

---

## Quick Navigation

### By Topic:

**Security & Access Control:**
- ops_matrix_core: [Section 5](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md#5-security)
- ops_matrix_accounting: [Section 5](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md#5-security--access-control)
- ops_matrix_reporting: [Section 4](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md#4-security--access-control)

**Models & Fields:**
- ops_matrix_core: [Section 2](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md#2-data-models--fields)
- ops_matrix_accounting: [Section 2](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md#2-data-models--fields)
- ops_matrix_reporting: [Section 2](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md#2-data-models--fields)

**Methods & Logic:**
- ops_matrix_core: [Section 3](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md#3-key-methods--business-logic)
- ops_matrix_accounting: [Section 3](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md#3-key-methods--business-logic)
- ops_matrix_reporting: [Section 3](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md#3-key-methods--business-logic)

**Views & UI:**
- ops_matrix_core: [Section 4](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md#4-xml-views--interface)
- ops_matrix_accounting: [Section 4](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md#4-xml-views--interface)
- ops_matrix_reporting: [Section 5](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md#5-xml-views--interface)

**Design & Patterns:**
- ops_matrix_core: [Section 10](./OPS_MATRIX_CORE_TECHNICAL_SPEC.md#10-key-design-patterns)
- ops_matrix_accounting: [Section 10](./OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md#10-key-design-patterns)
- ops_matrix_reporting: [Section 10](./OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md#10-key-design-patterns)

---

**All specifications are complete and ready for reconstruction or implementation.**
