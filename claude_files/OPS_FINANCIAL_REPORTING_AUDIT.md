# OPS Framework — Financial Reporting Audit
### Produced by Financial Reporter Skill | 2026-02-09

---

## Executive Summary

The OPS Framework contains a **substantial financial reporting infrastructure** spanning 4 modules, **27+ distinct report types**, **15 report wizards**, **37 KPI definitions**, and **10 persona-based dashboards**. The system supports PDF, XLSX, and screen output with corporate branding, multi-branch/BU filtering, and a full audit trail.

However, when measured against the Financial Reporter skill's 4 core workflows (P&L, Balance Sheet, Cash Flow, Financial Analysis), there are meaningful **gaps in ratio analysis, cash flow statement generation, trend reporting, and executive narrative output**.

---

## 1. INVENTORY OF EXISTING CAPABILITIES

### 1.1 Report Types by Category

| Category | Report | Wizard | PDF | XLSX | Screen | Budget Comparison |
|----------|--------|--------|-----|------|--------|-------------------|
| **Daily Operations** | | | | | | |
| Cash Book | ops.cash.book.wizard | Yes | Yes | — | Yes | No |
| Day Book | ops.day.book.wizard | Yes | Yes | — | Yes | No |
| Bank Book | ops.bank.book.wizard | Yes | Yes | — | Yes | No |
| **General Ledger** | | | | | | |
| General Ledger | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| Partner Ledger | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| Statement of Account | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| **Financial Statements** | | | | | | |
| Trial Balance | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| Profit & Loss | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| Balance Sheet | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| **Consolidation** | | | | | | |
| Company Consolidation P&L | ops.consolidation.intelligence.wizard | Yes | Yes | — | Yes | Yes (prior period) |
| Branch P&L | ops.consolidation.intelligence.wizard | Yes | Yes | — | Yes | No |
| BU Profitability | ops.consolidation.intelligence.wizard | Yes | Yes | — | Yes | No |
| Consolidated Balance Sheet | ops.consolidation.intelligence.wizard | Yes | Yes | — | Yes | No |
| **Asset Management** | | | | | | |
| Asset Register | ops.asset.report.wizard | Yes | Yes | Yes | Yes | No |
| Depreciation Schedule | ops.asset.report.wizard | Yes | Yes | Yes | Yes | No |
| Depreciation Forecast | ops.asset.report.wizard | Yes | — | Yes | Yes | No |
| Asset Disposal Report | ops.asset.report.wizard | Yes | — | Yes | Yes | No |
| Asset Movement Report | ops.asset.report.wizard | Yes | — | Yes | Yes | No |
| **Treasury (PDC)** | | | | | | |
| PDC Registry | ops.treasury.report.wizard | Yes | Yes | Yes | Yes | No |
| PDC Maturity Analysis | ops.treasury.report.wizard | Yes | Yes | Yes | Yes | No |
| PDCs in Hand | ops.treasury.report.wizard | Yes | Yes | Yes | Yes | No |
| **Budget** | | | | | | |
| Budget vs Actual | ops.budget.vs.actual.wizard | Yes | Yes | Yes | Yes | Yes |
| **Inventory** | | | | | | |
| Inventory Valuation | ops.inventory.report.wizard | Yes | — | Yes | Yes | No |
| Inventory Aging | ops.inventory.report.wizard | Yes | — | Yes | Yes | No |
| Inventory Movement | ops.inventory.report.wizard | Yes | — | Yes | Yes | No |
| Negative Stock | ops.inventory.report.wizard | Yes | — | Yes | Yes | No |
| **Analytical** | | | | | | |
| Aged Partner Balance | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |
| Cash Flow (indirect) | ops.general.ledger.wizard.enhanced | Yes | Yes | Yes | Yes | No |

**Total: 27 report types across 8 categories**

### 1.2 Document Reports (QWeb PDF — Non-Wizard)

| Report | Model | Module |
|--------|-------|--------|
| Quotation / Sales Order | sale.order | ops_matrix_core |
| Purchase Order / RFQ | purchase.order | ops_matrix_core |
| Delivery Note / GRN | stock.picking | ops_matrix_core |
| Stock Availability Report | sale.order | ops_matrix_core |
| Products Availability (alt) | sale.order | ops_matrix_core |
| SO Documentation | sale.order | ops_matrix_core |
| Invoice / Credit Note | account.move | ops_matrix_accounting |
| Payment Receipt | account.payment | ops_matrix_accounting |

### 1.3 KPI Center (ops_kpi)

| Category | KPI Count | Key Metrics |
|----------|-----------|-------------|
| Sales | 8 | Revenue MTD/YTD, Orders, Avg Order Value, Gross Margin %, Pipeline |
| Purchase | 5 | Purchases MTD, PO Count, Pending RFQs, Pending Receipts |
| Accounts Receivable | 3 | Total AR, Overdue AR, Collected MTD |
| Accounts Payable | 3 | Total AP, Overdue AP, AP Due 7 Days |
| PDC/Treasury | 7 | PDC Holding, Deposited, Bounced, Issued, Cash Balance, Cash In/Out |
| Inventory | 4 | Inventory Value, Active SKUs, Low Stock, Pending Deliveries |
| Budget | 1 | Budget Utilization % |
| Assets | 2 | Total NBV, Depreciation Due |
| Governance | 2 | 3-Way Match Pending/Exceptions |
| System | 3 | Active Users, Sessions, Pending Approvals |
| Personal (My) | 8 | My Sales/Orders/Quotations/POs/Picks |

**Total: 37 KPIs across 10 persona-based dashboards with ApexCharts visualization**

### 1.4 Supporting Infrastructure

| Component | Description |
|-----------|-------------|
| **ops.financial.report.config** | Hierarchical report builder — custom P&L/BS structures with 18 account type filters |
| **ops.report.template** | Configurable template system with section/line definitions |
| **ops.report.audit** | Immutable compliance log tracking every report generation |
| **OPS External Layout** | Corporate-branded PDF layout with dynamic colors, signatures, amount-in-words |
| **OPS Report CSS** | ~650 lines of inline CSS for wkhtmltopdf rendering |
| **Secure Export Wizard** | Audited XLSX/CSV export with matrix-filtered field visibility |
| **Governance Enforcement** | PDF printing blocked for documents with pending approvals |

---

## 2. GAP ANALYSIS — Financial Reporter Skill vs OPS Framework

### Workflow 1: P&L Statement (Income Statement)

| Step | Skill Requirement | OPS Status | Gap |
|------|-------------------|------------|-----|
| Revenue Collection | Gather all revenue streams | **COVERED** — P&L via GL wizard, Branch P&L, Company Consolidation | — |
| COGS | Direct costs tied to revenue | **COVERED** — ops.financial.report.config supports expense/direct_cost account types | — |
| Gross Margin | Gross profit calculation | **PARTIAL** — KPI exists (SALES_GROSS_MARGIN) but P&L report doesn't show gross margin as a separate line by default | Template config needed |
| Operating Expenses | SG&A breakdown | **COVERED** — Configurable report sections via ops.financial.report.config | — |
| EBITDA / EBIT | Operating income calculations | **MISSING** — No dedicated EBITDA/EBIT computation | **GAP** |
| Net Income | Bottom line | **COVERED** — Consolidation P&L calculates net profit | — |
| Variance Analysis | Budget vs prior period | **PARTIAL** — Budget vs Actual wizard exists; Company Consolidation supports prior period comparison; but P&L doesn't do inline variance | Needs inline variance |

**Coverage: ~70%**

### Workflow 2: Balance Sheet

| Step | Skill Requirement | OPS Status | Gap |
|------|-------------------|------------|-----|
| Current Assets | Cash, receivables, inventory | **COVERED** — Balance Sheet via GL wizard + ops.financial.report.config (18 account types) | — |
| Fixed Assets | PP&E, intangibles | **COVERED** — Asset Register + Depreciation Schedule reports | — |
| Current Liabilities | Payables, accrued, ST debt | **COVERED** — Balance Sheet report with account type filtering | — |
| Long-term Liabilities | LT debt, deferred tax | **COVERED** — ops.financial.report.config has non_current_liabilities type | — |
| Equity | Retained earnings, capital | **COVERED** — equity + unaffected_earnings account types | — |
| Balance Check | A = L + E verification | **MISSING** — No automated balance verification or alert | **GAP** |
| Ratio Analysis | Current, quick, D/E, ROE, ROA | **MISSING** — No financial ratio calculations anywhere | **CRITICAL GAP** |

**Coverage: ~65%**

### Workflow 3: Cash Flow Statement

| Step | Skill Requirement | OPS Status | Gap |
|------|-------------------|------------|-----|
| Operating Activities | Net income adjustments | **PARTIAL** — Cash Flow report exists via GL wizard but uses indirect method with limited adjustments | Needs enhancement |
| Investing Activities | CapEx, asset sales | **PARTIAL** — Asset module tracks purchases/disposals but not linked to cash flow statement | Not integrated |
| Financing Activities | Debt, equity, dividends | **MISSING** — No financing activities categorization | **GAP** |
| Net Cash Change | Opening → closing reconciliation | **PARTIAL** — Cash Book shows opening/closing but not in FASB/IAS 7 format | Format gap |
| Free Cash Flow | FCF and FCF yield | **MISSING** — No FCF calculation | **GAP** |

**Coverage: ~30%**

### Workflow 4: Financial Analysis & Commentary

| Step | Skill Requirement | OPS Status | Gap |
|------|-------------------|------------|-----|
| Trend Analysis | Multi-period trends | **PARTIAL** — KPI Center has MoM/YoY comparison and sparklines, but no multi-period financial statement trending | Formal trend reports missing |
| Ratio Dashboard | Liquidity, profitability, leverage | **MISSING** — KPI Center has operational KPIs but no financial ratios | **CRITICAL GAP** |
| Peer Comparison | Industry benchmarks | **MISSING** — No benchmark data or comparison capability | **GAP** |
| Risk Assessment | Financial red flags | **PARTIAL** — KPI alerts flag threshold breaches; 3-Way Match governance exists | No formal risk scoring |
| Executive Summary | Narrative financial health | **MISSING** — No narrative report generation | **GAP** |

**Coverage: ~15%**

---

## 3. CRITICAL GAPS — PRIORITY RANKING

### Priority 1 — High Impact, Missing Entirely

| # | Gap | Impact | Complexity |
|---|-----|--------|------------|
| 1 | **Financial Ratio Analysis** | No current/quick/D-E/ROE/ROA ratios anywhere in the system. CFO and CEO dashboards lack fundamental financial health metrics. | Medium — data exists in GL, needs computation layer |
| 2 | **IAS 7 Cash Flow Statement** | Current cash flow is a basic account summary, not a proper statement of cash flows with operating/investing/financing classification. | High — requires account mapping and classification rules |
| 3 | **EBITDA/EBIT Calculation** | No operating income metric. P&L stops at net income without intermediate profitability measures. | Low — derive from existing P&L data |

### Priority 2 — Partially Covered, Needs Enhancement

| # | Gap | Current State | Enhancement Needed |
|---|-----|---------------|-------------------|
| 4 | **Inline Variance on P&L/BS** | Budget vs Actual is a separate report; Consolidation has prior-period comparison | Add variance columns (budget, prior period, %) directly on P&L and BS reports |
| 5 | **Balance Sheet Verification** | Balance Sheet renders but doesn't validate A=L+E | Add automated check with warning banner if out of balance |
| 6 | **Multi-Period Trend Statements** | KPI sparklines show trends; no formal multi-period financial statements | Add comparative columns (3/6/12 months) on financial statements |
| 7 | **Cash Flow — Investing/Financing** | Asset module tracks CapEx; PDC tracks debt-like instruments | Integrate asset purchases, disposals, and PDC movements into cash flow |

### Priority 3 — Nice to Have

| # | Gap | Description |
|---|-----|-------------|
| 8 | **Executive Narrative Summary** | Auto-generated written analysis accompanying financial statements |
| 9 | **Free Cash Flow (FCF)** | FCF = Operating Cash Flow - CapEx; FCF Yield = FCF / Enterprise Value |
| 10 | **Peer Benchmarking** | Industry ratio comparison (would need external data source) |
| 11 | **Risk Scoring Model** | Composite financial health score from ratios + trends |

---

## 4. NOTED KPI GAPS (Documented in Seed Data)

The following KPIs are referenced in dashboard specifications but **not yet implemented**:

| KPI Code | Dashboard | Description |
|----------|-----------|-------------|
| NET_PROFIT | CEO, CFO | Net Profit amount |
| TOP_CUSTOMERS | Sales Manager | Top customers by revenue |
| CONVERSION_RATE | Sales Manager | Quote-to-order conversion |
| VENDOR_COUNT | Purchase Manager | Active vendor count |
| AR_AGING_30/60/90 | AR Clerk | Aging buckets |
| COLLECTION_RATE | AR Clerk | Collection efficiency % |
| AP_AGING_30/60 | AP Clerk | Payable aging buckets |
| MY_COMMISSION | Sales Rep | Personal commission |
| BANK_BALANCE | Treasury | Per-bank balances |

---

## 5. STRENGTHS — What OPS Does Well

| Strength | Detail |
|----------|--------|
| **Report Infrastructure** | Mature base: 15 wizards, PDF+XLSX+Screen output, corporate branding, dynamic colors |
| **Matrix Filtering** | Every report supports branch + BU filtering — rare in Odoo ecosystems |
| **Audit Compliance** | Every report generation is logged immutably (user, time, IP, parameters, format) |
| **Security Integration** | Governance blocks printing pending-approval docs; cost/margin field gating on KPIs; IT Admin blindness |
| **Configurable Statements** | ops.financial.report.config allows custom P&L/BS structures with 18 account types |
| **KPI Visualization** | ApexCharts-based dashboards with 11 chart types, sparklines, drill-down, auto-refresh |
| **Consolidation** | 4 consolidation reports (Company P&L, Branch P&L, BU Profitability, Consolidated BS) |
| **Treasury/PDC** | Full PDC lifecycle with 3 dedicated reports — uncommon in standard Odoo |
| **Amount in Words** | 12-currency support with English + Arabic |
| **Export Security** | Native exports locked down; Secure Export Wizard with field-level visibility rules |

---

## 6. MODULE OWNERSHIP MAP

```
ops_theme (Visual Layer)
├── External layout (header/footer/paper format)
├── Report CSS (~650 lines)
├── Helper templates (address, signature, terms, amount-in-words)
├── Company report settings (logo position, languages, toggles)
└── ops.report.helpers (amount_to_words — 12 currencies)

ops_matrix_core (Business Logic Layer)
├── Document reports (SO, PO, Delivery, Availability × 2, Documentation)
├── ops.report.template + ops.report.template.line (configurable templates)
├── Governance-enforced PDF rendering
├── Secure Export Wizard (XLSX/CSV with audit)
├── Availability Report controller (ReportLab PDF)
└── Sales Analysis + Stock Levels API endpoints

ops_matrix_accounting (Financial Engine)
├── 12 corporate PDF report parsers
├── 5 XLSX report generators
├── 8 financial statement types via Matrix Financial Intelligence
├── 4 consolidation reports
├── 5 asset reports, 3 treasury reports, 3 daily books
├── Budget vs Actual, Partner Ledger, Cash Flow
├── ops.financial.report.config (hierarchical statement builder)
├── ops.report.audit (compliance trail)
└── Report color fields on res.company

ops_kpi (Dashboard & Analytics)
├── 37 KPI definitions across 11 categories
├── 10 persona-based dashboards
├── 11 ApexCharts chart components
├── Real-time computation + trend/breakdown/comparison
├── Security: IT Admin blindness, cost/margin gates, persona filtering
└── Company-level display preferences (7 settings)
```

---

## 7. OVERALL SCORECARD

| Financial Reporter Workflow | Coverage | Grade |
|----------------------------|----------|-------|
| P&L Statement | 70% | B |
| Balance Sheet | 65% | B- |
| Cash Flow Statement | 30% | D |
| Financial Analysis & Commentary | 15% | F |
| **Overall** | **45%** | **C** |

### Interpretation

The OPS Framework excels at **transactional reporting** (daily books, ledgers, document printing) and **operational dashboards** (KPIs by persona). It has solid foundations for **financial statements** (configurable P&L/BS with branch filtering).

The critical weakness is in **analytical and interpretive reporting** — the system generates raw financial data effectively but lacks the layer that transforms data into **insights**: ratios, trends, narratives, and compliance-standard cash flow statements. This is the gap the Financial Reporter skill is designed to fill.

---

## 8. RECOMMENDATIONS

### Quick Wins (Low effort, high value)
1. Add **EBITDA/EBIT lines** to the standard P&L template in ops.financial.report.config seed data
2. Implement the **9 missing KPIs** (NET_PROFIT, AR_AGING, etc.) — definitions are already documented
3. Add **A=L+E balance check** banner on Balance Sheet output

### Medium-Term (1-2 sprints)
4. Build a **Financial Ratios KPI category** — 8-10 standard ratios computed from GL balances
5. Add **variance columns** (prior period + budget) directly on P&L and BS reports
6. Enhance Cash Flow to classify transactions into **Operating/Investing/Financing** per IAS 7

### Strategic (Roadmap items)
7. Build an **Executive Financial Package** wizard — single action generating P&L + BS + Cash Flow + Ratios + Narrative
8. Add **multi-period comparative statements** (3/6/12 month columns)
9. Develop a **Financial Health Score** composite metric for CEO/CFO dashboards

---

*Report generated by Financial Reporter skill audit*
*Audit date: 2026-02-09*
*Modules audited: ops_matrix_core, ops_matrix_accounting, ops_kpi, ops_theme*
