# Corporate Reporting Requirements Audit
## OPS Matrix Accounting - Deep Functional Analysis
**Audit Date:** 2026-01-24
**Auditor:** Claude Code (CPA/IFRS Functional Consultant)

---

## EXECUTIVE SUMMARY

The `ops_matrix_accounting` module contains a **mature data architecture** with rich dimensional tagging (Branch/Business Unit) across all financial transactions. However, there is a significant **gap between available data and exposed reports**.

| Category | Data Models | Reports Exposed | Gap |
|----------|-------------|-----------------|-----|
| Treasury/PDC | 2 models (Receivable + Payable) | 0 | **CRITICAL** |
| Assets | 3 models (Asset, Category, Depreciation) | 1 wizard (internal) | **HIGH** |
| Budgets | 2 models (Budget, Budget Line) | 0 | **CRITICAL** |
| Core Financial | Extensions to account.move.line | 2 wizards | Moderate |
| Consolidated Reports | 5 TransientModels | 0 menus (purged) | **CRITICAL** |
| Snapshots/Analytics | 2 models | 0 | **HIGH** |

---

## 1. DATA MODEL INVENTORY

### A. Treasury/PDC Models

| Model | Fields | Matrix Dimension | Status |
|-------|--------|------------------|--------|
| `ops.pdc.receivable` | partner_id, amount, check_number, check_date, maturity_date, deposit_date, clearance_date, state | `branch_id` | **DATA EXISTS** |
| `ops.pdc.payable` | partner_id, amount, check_number, check_date, maturity_date, issue_date, clearance_date, state | `branch_id` | **DATA EXISTS** |

**State Machines:**
- Receivable: `draft` -> `deposited` -> `cleared` / `bounced` / `cancelled`
- Payable: `draft` -> `issued` -> `presented` -> `cleared` / `cancelled`

**Implication:** System can track:
- PDCs in hand (state = draft/deposited)
- PDC maturity calendar
- Cleared/bounced status
- Branch-level cash position from PDCs

### B. Asset Models

| Model | Fields | Matrix Dimension | Status |
|-------|--------|------------------|--------|
| `ops.asset` | purchase_value, salvage_value, accumulated_depreciation (computed), book_value (computed), fully_depreciated (computed) | `ops_branch_id`, `ops_business_unit_id` | **DATA EXISTS** |
| `ops.asset.category` | depreciation_method, depreciation_duration, asset_account_id, depreciation_account_id, expense_account_id | None | **DATA EXISTS** |
| `ops.asset.depreciation` | asset_id, depreciation_date, amount (computed), state, move_id | `branch_id` (related), `business_unit_id` (related) | **DATA EXISTS** |

**Depreciation Methods:**
- Straight-line: `amount = depreciable_value / total_periods`
- Declining-balance: `amount = book_value × (2 / total_periods)`

**Implication:** System can generate:
- Fixed Asset Register with book values
- Depreciation Schedule by period
- Depreciation by Branch/BU (segment allocation)

### C. Budget Models

| Model | Fields | Matrix Dimension | Status |
|-------|--------|------------------|--------|
| `ops.budget` | date_from, date_to, total_planned (computed), total_practical (computed), total_committed (computed), available_balance (computed), budget_utilization (computed), is_over_budget (computed) | `ops_branch_id` (required), `ops_business_unit_id` (required) | **DATA EXISTS** |
| `ops.budget.line` | general_account_id, planned_amount, practical_amount (computed from invoices), committed_amount (computed from POs), available_amount (computed) | Inherited from parent | **DATA EXISTS** |

**Budget Control Logic:**
- Practical = Actual spend from posted vendor invoices
- Committed = PO amounts not yet invoiced
- Available = Planned - Practical - Committed
- Real-time check: `check_budget_availability(account, branch, bu, amount)`

**Implication:** System can generate:
- Budget vs Actual reports by Branch/BU
- Variance analysis (absolute and %)
- Commitment tracking

### D. Core Financial Extensions

| Model | New Fields | Indexed | Status |
|-------|------------|---------|--------|
| `account.move` | `ops_branch_id`, `ops_business_unit_id` | Yes | **ACTIVE** |
| `account.move.line` | `ops_branch_id`, `ops_business_unit_id` | Yes | **ACTIVE** |
| `sale.order` | `ops_branch_id`, `ops_business_unit_id` | - | **ACTIVE** |
| `purchase.order` | `ops_branch_id`, `ops_business_unit_id` | - | **ACTIVE** |
| `stock.picking` | `ops_branch_id`, `ops_business_unit_id` | - | **ACTIVE** |

**Propagation Flow:**
```
SO/PO -> Invoice/Bill -> Journal Entry -> Move Lines
         ↓
    (branch_id, business_unit_id propagate automatically)
```

**Implication:**
- Every financial transaction is tagged with Branch + BU
- Can generate IFRS 8 Operating Segment reports
- Can create side-by-side Branch comparisons

### E. Consolidated Reporting Models (TransientModel)

| Model | Purpose | Caching | Snapshot Support | Status |
|-------|---------|---------|------------------|--------|
| `ops.company.consolidation` | Company-level P&L | 15-min TTL | Yes | **CODE EXISTS, NO MENU** |
| `ops.branch.report` | Branch P&L with BU breakdown | - | - | **CODE EXISTS, NO MENU** |
| `ops.business.unit.report` | BU profitability with trends | - | Yes | **CODE EXISTS, NO MENU** |
| `ops.consolidated.balance.sheet` | Multi-company BS with eliminations | - | - | **CODE EXISTS, NO MENU** |
| `ops.matrix.profitability.analysis` | Branch × BU heatmap | Yes | - | **CODE EXISTS, NO MENU** |
| `ops.trend.analysis` | MoM/QoQ/YoY variance | - | Yes | **CODE EXISTS, NO MENU** |

### F. Snapshot Model

| Model | Purpose | Metrics | Status |
|-------|---------|---------|--------|
| `ops.matrix.snapshot` | Pre-computed financial aggregates | revenue, cogs, gross_profit, operating_expense, ebitda, depreciation, ebit, interest_expense, tax_expense, net_income, total_assets, total_liabilities, gross_margin_pct, operating_margin_pct, net_margin_pct, projected_revenue | **DATA CAN BE GENERATED** |

**Performance:** 100-600x faster than real-time aggregation for historical periods.

---

## 2. MATRIX CAPABILITY ANALYSIS

### Current Implementation (account.move.line)

```python
# Fields on every journal entry line
ops_branch_id = fields.Many2one('ops.branch', index=True)
ops_business_unit_id = fields.Many2one('ops.business.unit', index=True)
```

### Segmented P&L Capability

**Can we generate "Columns = Business Units" report?**

**YES** - The codebase already has optimized grouped queries:

```python
# Single O(1) query for entire matrix (from ops.matrix.profitability.analysis)
MoveLine._read_group(
    domain=[...],
    groupby=['ops_branch_id', 'ops_business_unit_id', 'account_id.account_type'],
    aggregates=['credit:sum', 'debit:sum']
)
```

**IFRS 8 Compliance:** The data structure supports:
- Segment Revenue
- Segment Expenses
- Segment Profit/Loss
- Segment Assets (via ops.asset tagging)
- Segment Liabilities (via account tagging)

---

## 3. GAP ANALYSIS

### Current Exposed Reports

| Report | Wizard | Menu | Status |
|--------|--------|------|--------|
| Financial Reports (P&L, BS, GL, TB, CF, Aged) | `ops.financial.report.wizard` | Yes | **WORKING** |
| General Ledger (Matrix Enhanced) | `ops.general.ledger.wizard.enhanced` | Yes | **WORKING** |

### Feature Comparison: Enhanced GL vs. Requirements

| Feature | Enhanced GL | Required | Gap |
|---------|-------------|----------|-----|
| Branch filtering | Yes | Yes | None |
| BU filtering | Yes | Yes | None |
| Matrix mode (AND/OR/EXACT) | Yes | Yes | None |
| Initial balance | Yes | Yes | None |
| Reconciliation filter | Yes | Yes | None |
| Partner filter | Yes | Yes | None |
| Consolidation by Branch | Yes | Yes | None |
| Consolidation by BU | Yes | Yes | None |
| PDC Integration | **NO** | Yes | **GAP** |
| Asset Integration | **NO** | Yes | **GAP** |
| Budget vs Actual | **NO** | Yes | **GAP** |
| Side-by-Side Comparison | **NO** | Yes | **GAP** |
| Trend Analysis (MoM/YoY) | **NO** | Yes | **GAP** |

### Missing Report Menus

The following **already-built** functionality has **NO menu access**:

| Report | Model | Why Missing |
|--------|-------|-------------|
| Company Consolidation | `ops.company.consolidation` | Purged in Phase 1 |
| Branch P&L | `ops.branch.report` | Purged in Phase 1 |
| BU Profitability | `ops.business.unit.report` | Purged in Phase 1 |
| Consolidated Balance Sheet | `ops.consolidated.balance.sheet` | Purged in Phase 1 |
| Matrix Heatmap | `ops.matrix.profitability.analysis` | Never had menu |
| Trend Analysis | `ops.trend.analysis` | Never had menu |

---

## 4. DEFINITIVE REPORT LIST (MANDATORY)

Based on data models and corporate standards, here is the **required report suite**:

### A. Financial Statements (The Big 5)

| # | Report | Model/Source | Priority |
|---|--------|--------------|----------|
| A1 | **Profit & Loss Statement** | `ops.financial.report.wizard` (exists) | P1 - WORKING |
| A2 | **Balance Sheet** | `ops.financial.report.wizard` (exists) | P1 - WORKING |
| A3 | **Cash Flow Statement** | `ops.financial.report.wizard` (exists) | P1 - WORKING |
| A4 | **Trial Balance** | `ops.financial.report.wizard` (exists) | P1 - WORKING |
| A5 | **General Ledger (Matrix)** | `ops.general.ledger.wizard.enhanced` (exists) | P1 - WORKING |

### B. Treasury & Cash Management

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| B1 | **PDC Registry (Receivable)** | `ops.pdc.receivable` | P1 - **BUILD** |
| B2 | **PDC Registry (Payable)** | `ops.pdc.payable` | P1 - **BUILD** |
| B3 | **PDC Maturity Analysis** | `ops.pdc.receivable/payable` with date grouping | P1 - **BUILD** |
| B4 | **PDC Aging by Status** | `ops.pdc.*` grouped by state | P2 - **BUILD** |
| B5 | **Cleared PDC Summary** | `ops.pdc.*` where state='cleared' | P2 - **BUILD** |

### C. Asset Management (Capex)

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| C1 | **Fixed Asset Register** | `ops.asset` with book values | P1 - **BUILD** |
| C2 | **Depreciation Schedule** | `ops.asset.depreciation` | P1 - **BUILD** |
| C3 | **Asset Additions/Disposals** | `ops.asset` state changes by period | P2 - **BUILD** |
| C4 | **Asset by Category Summary** | `ops.asset` grouped by category_id | P2 - **BUILD** |
| C5 | **Asset by Branch/BU** | `ops.asset` with matrix dimensions | P2 - **BUILD** |

### D. Partner Management

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| D1 | **Aged Receivables** | `ops.financial.report.wizard` (type=aged) | P1 - WORKING |
| D2 | **Aged Payables** | `ops.financial.report.wizard` (needs extension) | P1 - **ENHANCE** |
| D3 | **Statement of Account** | `account.move.line` by partner | P2 - **BUILD** |
| D4 | **Partner Balance Summary** | `account.move.line` grouped by partner | P2 - **BUILD** |

### E. Matrix Performance (Segment Reporting)

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| E1 | **Segmented P&L (Columns = BU)** | `ops.company.consolidation` (exists) | P1 - **EXPOSE** |
| E2 | **Branch P&L** | `ops.branch.report` (exists) | P1 - **EXPOSE** |
| E3 | **BU Profitability** | `ops.business.unit.report` (exists) | P1 - **EXPOSE** |
| E4 | **Branch × BU Matrix Heatmap** | `ops.matrix.profitability.analysis` (exists) | P1 - **EXPOSE** |
| E5 | **Branch Comparison (Side-by-Side)** | New wizard needed | P2 - **BUILD** |

### F. Budget & Variance

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| F1 | **Budget vs Actual (Matrix)** | `ops.budget` + `ops.budget.line` | P1 - **BUILD** |
| F2 | **Commitment Report** | `ops.budget.line.committed_amount` | P2 - **BUILD** |
| F3 | **Budget Utilization Dashboard** | `ops.budget.budget_utilization` | P2 - **BUILD** |

### G. Trend & Analytics

| # | Report | Data Source | Priority |
|---|--------|-------------|----------|
| G1 | **MoM Trend Analysis** | `ops.trend.analysis` (exists) | P1 - **EXPOSE** |
| G2 | **YoY Comparison** | `ops.trend.analysis` (exists) | P1 - **EXPOSE** |
| G3 | **Financial Snapshot Dashboard** | `ops.matrix.snapshot` | P2 - **BUILD** |

---

## 5. PRIORITY SUMMARY

### Priority 1 (Critical - Immediate)

| Action | Count | Reports |
|--------|-------|---------|
| WORKING | 5 | A1-A5 (Core Financial) |
| EXPOSE (menu only) | 6 | E1-E4, G1-G2 |
| BUILD | 6 | B1-B3, C1-C2, F1 |
| ENHANCE | 1 | D2 (Aged Payables) |

**Total P1:** 18 reports

### Priority 2 (Important - Next Phase)

| Action | Count | Reports |
|--------|-------|---------|
| BUILD | 11 | B4-B5, C3-C5, D3-D4, E5, F2-F3, G3 |

**Total P2:** 11 reports

---

## 6. RECOMMENDATIONS

### Phase 2A: Expose Existing Reports (Quick Wins)
1. Create menu items for consolidated reports (TransientModels exist)
2. Wire up trend analysis wizard
3. Add matrix heatmap to dashboard

### Phase 2B: Build PDC Reports
1. Create `ops.pdc.report.wizard` TransientModel
2. Implement PDC maturity calendar view
3. Add PDC status dashboard widget

### Phase 2C: Build Asset Reports
1. Create `ops.asset.report.wizard` TransientModel
2. Integrate with existing depreciation schedule
3. Add asset movement report

### Phase 2D: Build Budget Reports
1. Create `ops.budget.report.wizard` TransientModel
2. Implement variance analysis with charts
3. Add commitment tracking

### Architectural Note
The existing snapshot model (`ops.matrix.snapshot`) should be leveraged for all historical reports to achieve 100-600x performance improvement.

---

## 7. INTER-BRANCH LOGIC

**Current State:** No explicit inter-branch transaction model exists.

**Recommendation:** For IFRS compliance (inter-segment eliminations), consider:
1. Adding `is_intercompany` flag to `account.move`
2. Creating `ops.intercompany.transaction` model
3. Building Inter-Branch Reconciliation Matrix report

---

**END OF AUDIT**

*Report generated by Claude Code - CPA/IFRS Functional Consultant*
