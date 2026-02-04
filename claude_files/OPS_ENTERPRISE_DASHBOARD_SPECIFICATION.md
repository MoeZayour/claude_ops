# OPS Framework - Enterprise Dashboard System

## Complete Persona-Based Dashboard Specification

**Document Type:** Implementation Specification  
**Author:** Enterprise Architecture Team  
**Date:** January 31, 2026  
**Target:** Corporate-Grade Dashboard for Trading Companies

---

## EXECUTIVE SUMMARY

This specification defines a complete dashboard system for the OPS Framework's 18 personas, ensuring:

1. **Role-Based Visibility** - Each persona sees only their relevant KPIs
2. **Security Enforcement** - IT Admin blindness, cost/margin locks, branch isolation
3. **Hierarchical Data** - CEO sees company-wide, Branch Manager sees their branch only
4. **Segregation of Duties** - Reflected in dashboard metrics (approvals, pending actions)
5. **Real-World Trading Company Focus** - Sales, Purchase, AR, AP, Inventory, PDC

---

## THE 18 PERSONAS & THEIR DASHBOARDS

### PERSONA HIERARCHY

```
┌─────────────────────────────────────────────────────────────────┐
│ COMPANY-WIDE VISIBILITY                                         │
│  P00 System Admin    - ALL (Break-glass)                        │
│  P02 CEO/Executive   - ALL (Read-only, No Cost)                 │
│  P03 CFO/Owner       - ALL (Full Financial)                     │
├─────────────────────────────────────────────────────────────────┤
│ BUSINESS UNIT VISIBILITY                                        │
│  P04 BU Leader       - All Branches in BU (Cost visible)        │
├─────────────────────────────────────────────────────────────────┤
│ BRANCH VISIBILITY                                               │
│  P05 Branch Manager  - Own Branch (Full)                        │
│  P06 Sales Manager   - Own Branch (Sales + Margin)              │
│  P07 Purchase Mgr    - Own Branch (Purchase + Cost)             │
│  P08 Inventory Mgr   - Own Branch (Stock + Valuation)           │
│  P09 Finance Mgr     - Own Branch (Full Financial)              │
├─────────────────────────────────────────────────────────────────┤
│ OPERATIONAL (Own Records)                                        │
│  P10 Sales Rep       - Own Sales Only (No Cost/Margin)          │
│  P11 Purchase Officer - Own POs (Cost visible)                  │
│  P12 Warehouse Op    - Own Pickings (No Cost)                   │
│  P13 AR Clerk        - Receivables Only                         │
│  P14 AP Clerk        - Payables Only                            │
│  P15 Treasury        - Payments + PDC                           │
│  P16 Accountant      - Journal Entries + Reports                │
│  P17 HR Specialist   - NO Dashboard (not business data)         │
├─────────────────────────────────────────────────────────────────┤
│ SYSTEM ONLY (DATA BLIND)                                        │
│  P01 IT Admin        - System Health ONLY (No business data)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## DASHBOARD DEFINITIONS BY PERSONA

### P00 - System Admin Dashboard
**Visibility:** COMPANY-WIDE  
**Purpose:** Emergency break-glass, full visibility  
**Note:** Uses P03 CFO dashboard (not separate)

---

### P01 - IT Administrator Dashboard
**Visibility:** SYSTEM ONLY (DATA BLIND)  
**Purpose:** Monitor system health without business data access

| KPI Code | KPI Name | Format | Source | Notes |
|----------|----------|--------|--------|-------|
| SYS_USERS_ACTIVE | Active Users | Integer | res.users | Count logged in |
| SYS_USERS_TOTAL | Total Users | Integer | res.users | Total count |
| SYS_SESSIONS | Active Sessions | Integer | ops.session.manager | Current sessions |
| SYS_API_CALLS | API Calls Today | Integer | ops.audit.log | Today's calls |
| SYS_FAILED_LOGINS | Failed Logins (24h) | Integer | Security log | Security alert |
| SYS_PENDING_APPROVALS | Pending Approvals | Integer | ops.approval.request | Count only, no details |
| SYS_SLA_BREACHED | SLA Breaches | Integer | ops.sla.instance | Count only |
| SYS_SOD_VIOLATIONS | SoD Violations (30d) | Integer | ops.segregation.of.duties.log | Count only |

**Security:** CANNOT see amounts, customers, vendors, transactions - COUNT ONLY

---

### P02 - CEO/Executive Dashboard
**Visibility:** COMPANY-WIDE READ-ONLY  
**Purpose:** High-level business performance overview  
**Cost/Margin:** NO (Cannot see cost prices or margins)

| KPI Code | KPI Name | Format | Source | Security |
|----------|----------|--------|--------|----------|
| EXEC_REVENUE_MTD | Revenue MTD | Currency | sale.order | All branches |
| EXEC_REVENUE_YTD | Revenue YTD | Currency | sale.order | All branches |
| EXEC_ORDERS_MTD | Orders This Month | Integer | sale.order | All branches |
| EXEC_AR_TOTAL | Total Receivables | Currency | account.move | All branches |
| EXEC_AR_OVERDUE | Overdue Receivables | Currency | account.move | > 30 days |
| EXEC_AP_TOTAL | Total Payables | Currency | account.move | All branches |
| EXEC_CASH_BALANCE | Cash Balance | Currency | account.account | Bank accounts |
| EXEC_PDC_HOLDING | PDC Holding (Recv) | Currency | ops.pdc.receivable | Registered + Deposited |
| EXEC_PENDING_APPROVALS | My Pending Approvals | Integer | ops.approval.request | Own queue |
| EXEC_BRANCH_COUNT | Active Branches | Integer | ops.branch | Count |
| EXEC_EMPLOYEE_COUNT | Total Employees | Integer | res.users | Active only |

**Widgets:**
- Revenue trend chart (12 months)
- Top 5 branches by revenue (bar chart)
- AR aging summary (pie chart)
- Cash position gauge

---

### P03 - CFO/Owner Dashboard
**Visibility:** COMPANY-WIDE FULL ACCESS  
**Purpose:** Complete financial oversight with margins  
**Cost/Margin:** YES (Full financial visibility)

| KPI Code | KPI Name | Format | Source | Security |
|----------|----------|--------|--------|----------|
| CFO_REVENUE_MTD | Revenue MTD | Currency | sale.order | All |
| CFO_REVENUE_YTD | Revenue YTD | Currency | sale.order | All |
| CFO_COGS_MTD | Cost of Goods MTD | Currency | account.move | Requires cost access |
| CFO_GROSS_MARGIN | Gross Margin % | Percentage | Calculated | Revenue - COGS |
| CFO_NET_PROFIT | Net Profit MTD | Currency | account.move | P&L bottom line |
| CFO_AR_TOTAL | Total Receivables | Currency | account.move | All |
| CFO_AR_OVERDUE | Overdue Receivables | Currency | account.move | > 30 days |
| CFO_AP_TOTAL | Total Payables | Currency | account.move | All |
| CFO_AP_OVERDUE | Overdue Payables | Currency | account.move | > 30 days |
| CFO_CASH_BALANCE | Cash Balance | Currency | account.account | All banks |
| CFO_PDC_RECV | PDC Receivable Total | Currency | ops.pdc.receivable | All states |
| CFO_PDC_PAY | PDC Payable Total | Currency | ops.pdc.payable | All states |
| CFO_BUDGET_UTIL | Budget Utilization | Percentage | ops.budget | (Actual/Planned) |
| CFO_INVENTORY_VALUE | Inventory Value | Currency | stock.quant | Requires valuation |
| CFO_ASSET_NBV | Total Asset NBV | Currency | ops.asset | Net book value |
| CFO_3WAY_EXCEPTIONS | 3-Way Match Issues | Integer | ops.three.way.match | Exceptions only |

**Widgets:**
- P&L summary (current month vs prior)
- Cash flow forecast (next 30 days)
- Revenue by branch (horizontal bar)
- Margin by BU (bar chart)
- PDC maturity calendar
- Budget vs Actual by department

---

### P04 - BU Leader Dashboard
**Visibility:** ALL BRANCHES WITHIN OWN BU  
**Purpose:** Cross-branch business unit performance  
**Cost/Margin:** YES

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| BU_REVENUE_MTD | BU Revenue MTD | Currency | sale.order | BU branches only |
| BU_REVENUE_YTD | BU Revenue YTD | Currency | sale.order | BU branches only |
| BU_MARGIN_PCT | BU Gross Margin % | Percentage | Calculated | Cost access req |
| BU_ORDERS_MTD | BU Orders MTD | Integer | sale.order | BU branches only |
| BU_AR_TOTAL | BU Receivables | Currency | account.move | BU branches only |
| BU_AR_OVERDUE | BU Overdue AR | Currency | account.move | BU branches only |
| BU_PURCHASE_MTD | BU Purchases MTD | Currency | purchase.order | BU branches only |
| BU_INVENTORY | BU Inventory Value | Currency | stock.quant | BU warehouses |
| BU_PENDING_SO | Pending SO Approval | Integer | sale.order | BU, pending state |
| BU_PENDING_PO | Pending PO Approval | Integer | purchase.order | BU, pending state |

**Widgets:**
- Branch comparison table (all branches in BU)
- BU revenue trend (6 months)
- Top customers in BU
- Pending approvals list

---

### P05 - Branch Manager Dashboard
**Visibility:** OWN BRANCH ONLY  
**Purpose:** Complete branch operations oversight  
**Cost/Margin:** YES

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| BR_REVENUE_MTD | Branch Revenue MTD | Currency | sale.order | Own branch |
| BR_REVENUE_YTD | Branch Revenue YTD | Currency | sale.order | Own branch |
| BR_MARGIN_PCT | Branch Margin % | Percentage | Calculated | Own branch |
| BR_ORDERS_TODAY | Orders Today | Integer | sale.order | Own branch |
| BR_ORDERS_MTD | Orders MTD | Integer | sale.order | Own branch |
| BR_AR_TOTAL | Branch Receivables | Currency | account.move | Own branch |
| BR_AR_OVERDUE | Branch Overdue AR | Currency | account.move | Own branch |
| BR_AP_TOTAL | Branch Payables | Currency | account.move | Own branch |
| BR_PURCHASE_MTD | Branch Purchases MTD | Currency | purchase.order | Own branch |
| BR_INVENTORY | Branch Inventory | Currency | stock.quant | Own warehouse |
| BR_PENDING_PICKINGS | Pending Deliveries | Integer | stock.picking | Own branch |
| BR_PENDING_RECEIPTS | Pending Receipts | Integer | stock.picking | Own branch |
| BR_PDC_HOLDING | PDC Holding | Currency | ops.pdc.receivable | Own branch |
| BR_PENDING_APPROVALS | My Pending Approvals | Integer | ops.approval.request | Own queue |
| BR_TEAM_SIZE | Team Members | Integer | res.users | Assigned to branch |

**Widgets:**
- Daily sales chart (last 7 days)
- Top 10 customers
- Pending tasks list
- Team activity feed

---

### P06 - Sales Manager Dashboard
**Visibility:** OWN BRANCH - SALES FOCUS  
**Purpose:** Sales team performance management  
**Cost/Margin:** YES (Can see margin for pricing decisions)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| SM_REVENUE_TODAY | Sales Today | Currency | sale.order | Own branch |
| SM_REVENUE_MTD | Sales MTD | Currency | sale.order | Own branch |
| SM_REVENUE_TARGET | Monthly Target | Currency | Configured | Target |
| SM_TARGET_PCT | Target Achievement | Percentage | Calculated | Actual/Target |
| SM_ORDERS_MTD | Orders MTD | Integer | sale.order | Own branch |
| SM_AVG_ORDER_VALUE | Avg Order Value | Currency | sale.order | Own branch |
| SM_MARGIN_PCT | Avg Margin % | Percentage | Calculated | Own branch |
| SM_QUOTATIONS | Open Quotations | Integer | sale.order | Draft state |
| SM_QUOTATION_VALUE | Quotation Pipeline | Currency | sale.order | Draft state |
| SM_PENDING_APPROVAL | SO Awaiting Approval | Integer | sale.order | Pending state |
| SM_AR_OVERDUE | Customer Overdue | Currency | account.move | Own branch |
| SM_TOP_REP | Top Sales Rep Today | Text | sale.order | Calculated |
| SM_CREDIT_HOLDS | Credit Limit Holds | Integer | sale.order | Blocked |

**Widgets:**
- Sales funnel (quotations → orders)
- Sales rep leaderboard
- Customer concentration (top 10)
- Margin analysis by product category

---

### P07 - Purchase Manager Dashboard
**Visibility:** OWN BRANCH - PURCHASE FOCUS  
**Purpose:** Procurement operations management  
**Cost/Margin:** YES (Cost visibility for procurement)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| PM_PURCHASE_MTD | Purchases MTD | Currency | purchase.order | Own branch |
| PM_PURCHASE_YTD | Purchases YTD | Currency | purchase.order | Own branch |
| PM_PO_COUNT_MTD | PO Count MTD | Integer | purchase.order | Own branch |
| PM_PENDING_RFQ | Pending RFQs | Integer | purchase.order | Draft state |
| PM_PO_AWAITING | PO Awaiting Approval | Integer | purchase.order | Pending state |
| PM_PENDING_RECEIPTS | Pending Receipts | Integer | stock.picking | Incoming |
| PM_LATE_RECEIPTS | Late Deliveries | Integer | stock.picking | Overdue |
| PM_3WAY_PENDING | Pending 3-Way Match | Integer | ops.three.way.match | Pending status |
| PM_3WAY_EXCEPTION | Match Exceptions | Integer | ops.three.way.match | Exception status |
| PM_AP_COMING_DUE | AP Due (7 days) | Currency | account.move | Coming due |
| PM_PDC_ISSUED | PDC Issued (Unpaid) | Currency | ops.pdc.payable | Issued state |
| PM_TOP_VENDOR | Top Vendor MTD | Text | purchase.order | Calculated |

**Widgets:**
- Purchase trend (6 months)
- Vendor spend analysis
- Receipt schedule (next 7 days)
- 3-way match exception list

---

### P08 - Inventory Manager Dashboard
**Visibility:** OWN BRANCH - INVENTORY FOCUS  
**Purpose:** Stock and warehouse management  
**Cost/Margin:** COST + VALUATION (No margin)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| IM_INVENTORY_VALUE | Total Inventory Value | Currency | stock.quant | Own warehouse |
| IM_SKU_COUNT | Active SKUs | Integer | product.product | In stock |
| IM_LOW_STOCK | Low Stock Items | Integer | stock.quant | Below reorder |
| IM_OUT_OF_STOCK | Out of Stock | Integer | stock.quant | Zero qty |
| IM_OVERSTOCK | Overstock Items | Integer | stock.quant | Above max |
| IM_PENDING_RECEIPTS | Incoming Shipments | Integer | stock.picking | In transit |
| IM_PENDING_DELIVERY | Outgoing Shipments | Integer | stock.picking | Ready to ship |
| IM_PICKS_TODAY | Picks Completed Today | Integer | stock.picking | Done today |
| IM_RECEIPTS_TODAY | Receipts Today | Integer | stock.picking | Done today |
| IM_TURNOVER_RATIO | Inventory Turnover | Number | Calculated | COGS / Avg Inv |
| IM_DAYS_INVENTORY | Days of Inventory | Number | Calculated | Avg stock days |

**Widgets:**
- Stock value by category
- Low stock alerts list
- Daily operations summary
- Warehouse utilization gauge

---

### P09 - Finance Manager Dashboard
**Visibility:** OWN BRANCH - FULL FINANCIAL  
**Purpose:** Branch financial management  
**Cost/Margin:** YES (Full financial visibility)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| FM_REVENUE_MTD | Revenue MTD | Currency | sale.order | Own branch |
| FM_EXPENSE_MTD | Expenses MTD | Currency | account.move | Own branch |
| FM_PROFIT_MTD | Profit MTD | Currency | Calculated | Rev - Exp |
| FM_AR_TOTAL | Total Receivables | Currency | account.move | Own branch |
| FM_AR_CURRENT | AR Current (0-30) | Currency | account.move | Own branch |
| FM_AR_30_60 | AR 31-60 Days | Currency | account.move | Own branch |
| FM_AR_60_90 | AR 61-90 Days | Currency | account.move | Own branch |
| FM_AR_OVER_90 | AR Over 90 Days | Currency | account.move | Own branch |
| FM_AP_TOTAL | Total Payables | Currency | account.move | Own branch |
| FM_AP_COMING_DUE | AP Due (7 days) | Currency | account.move | Own branch |
| FM_PDC_RECV | PDC Receivable | Currency | ops.pdc.receivable | Own branch |
| FM_PDC_PAY | PDC Payable | Currency | ops.pdc.payable | Own branch |
| FM_BANK_BALANCE | Bank Balance | Currency | account.account | Own branch |
| FM_PENDING_JE | Pending JE Approval | Integer | account.move | Own branch |
| FM_UNRECONCILED | Unreconciled Items | Integer | account.bank.statement.line | Own branch |

**Widgets:**
- AR aging chart
- AP due calendar
- Cash flow summary
- PDC maturity schedule

---

### P10 - Sales Representative Dashboard
**Visibility:** OWN RECORDS ONLY  
**Purpose:** Personal sales performance  
**Cost/Margin:** NO (Cannot see cost or margin)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| SR_MY_SALES_TODAY | My Sales Today | Currency | sale.order | Own orders |
| SR_MY_SALES_MTD | My Sales MTD | Currency | sale.order | Own orders |
| SR_MY_SALES_TARGET | My Monthly Target | Currency | Configured | Personal target |
| SR_TARGET_PCT | Target Achievement | Percentage | Calculated | Own only |
| SR_MY_ORDERS_MTD | My Orders MTD | Integer | sale.order | Own orders |
| SR_MY_QUOTATIONS | My Open Quotations | Integer | sale.order | Own drafts |
| SR_MY_QUOTATION_VALUE | My Quotation Value | Currency | sale.order | Own drafts |
| SR_MY_PENDING | My Pending Approval | Integer | sale.order | Own pending |
| SR_MY_CUSTOMERS | My Active Customers | Integer | res.partner | Own assigned |
| SR_CUSTOMER_OVERDUE | My Customers Overdue | Currency | account.move | Own customers |

**Widgets:**
- Personal sales chart (30 days)
- My quotation pipeline
- My top customers
- My activity feed

**Security Notes:**
- CANNOT see other reps' data
- CANNOT see cost prices on products
- CANNOT see margin calculations
- ONLY sees own orders and assigned customers

---

### P11 - Purchase Officer Dashboard
**Visibility:** OWN RECORDS ONLY  
**Purpose:** Personal procurement tasks  
**Cost/Margin:** COST ONLY (No margin)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| PO_MY_PO_MTD | My POs MTD | Currency | purchase.order | Own POs |
| PO_MY_PO_COUNT | My PO Count MTD | Integer | purchase.order | Own POs |
| PO_MY_DRAFTS | My Draft RFQs | Integer | purchase.order | Own drafts |
| PO_MY_PENDING | My Pending Approval | Integer | purchase.order | Own pending |
| PO_MY_RECEIPTS_DUE | My Receipts Due | Integer | stock.picking | Own POs |
| PO_MY_LATE_RECEIPTS | My Late Receipts | Integer | stock.picking | Own POs |
| PO_MY_VENDORS | My Active Vendors | Integer | res.partner | Vendors I work with |

**Widgets:**
- My PO timeline
- My pending receipts
- My vendor list

---

### P12 - Warehouse Operator Dashboard
**Visibility:** OWN RECORDS ONLY  
**Purpose:** Daily warehouse tasks  
**Cost/Margin:** NO

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| WO_MY_PICKS_TODAY | My Picks Today | Integer | stock.picking | Assigned to me |
| WO_MY_PICKS_PENDING | My Pending Picks | Integer | stock.picking | Assigned to me |
| WO_MY_RECEIPTS_TODAY | My Receipts Today | Integer | stock.picking | Assigned to me |
| WO_MY_RECEIPTS_PENDING | My Pending Receipts | Integer | stock.picking | Assigned to me |
| WO_MY_COMPLETED_TODAY | Total Completed Today | Integer | stock.picking | Done by me |

**Widgets:**
- My task queue
- Daily completion stats

**Security Notes:**
- CANNOT see cost prices
- CANNOT see order values
- ONLY sees stock movements assigned to them

---

### P13 - AR Clerk Dashboard
**Visibility:** RECEIVABLES ONLY  
**Purpose:** Collections and AR management  
**Cost/Margin:** NO

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| AR_TOTAL | Total Receivables | Currency | account.move | Own branch |
| AR_CURRENT | Current (0-30) | Currency | account.move | Own branch |
| AR_30_60 | 31-60 Days | Currency | account.move | Own branch |
| AR_60_90 | 61-90 Days | Currency | account.move | Own branch |
| AR_OVER_90 | Over 90 Days | Currency | account.move | Own branch |
| AR_COLLECTED_MTD | Collected MTD | Currency | account.payment | Own branch |
| AR_PDC_REGISTERED | PDC Registered | Currency | ops.pdc.receivable | Own branch |
| AR_PDC_DEPOSITED | PDC Deposited | Currency | ops.pdc.receivable | Own branch |
| AR_PDC_CLEARED | PDC Cleared MTD | Currency | ops.pdc.receivable | Own branch |
| AR_PDC_BOUNCED | PDC Bounced | Currency | ops.pdc.receivable | Active bounced |
| AR_FOLLOWUP_DUE | Follow-ups Due | Integer | ops.partner.followup | Today |

**Widgets:**
- AR aging pie chart
- Collection trend (30 days)
- PDC status summary
- Overdue customer list

---

### P14 - AP Clerk Dashboard
**Visibility:** PAYABLES ONLY  
**Purpose:** Vendor payments and AP management  
**Cost/Margin:** NO

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| AP_TOTAL | Total Payables | Currency | account.move | Own branch |
| AP_CURRENT | Current (0-30) | Currency | account.move | Own branch |
| AP_30_60 | 31-60 Days | Currency | account.move | Own branch |
| AP_60_90 | 61-90 Days | Currency | account.move | Own branch |
| AP_OVER_90 | Over 90 Days | Currency | account.move | Own branch |
| AP_DUE_TODAY | Due Today | Currency | account.move | Own branch |
| AP_DUE_7_DAYS | Due Next 7 Days | Currency | account.move | Own branch |
| AP_PAID_MTD | Paid MTD | Currency | account.payment | Own branch |
| AP_PDC_ISSUED | PDC Issued | Currency | ops.pdc.payable | Own branch |
| AP_PDC_PRESENTED | PDC Presented | Currency | ops.pdc.payable | Own branch |
| AP_3WAY_PENDING | Pending 3-Way Match | Integer | ops.three.way.match | Own branch |

**Widgets:**
- AP aging pie chart
- Payment schedule (next 14 days)
- PDC status summary
- 3-way match exceptions

---

### P15 - Treasury Officer Dashboard
**Visibility:** PAYMENTS + PDC  
**Purpose:** Cash management and PDC handling  
**Cost/Margin:** COST (For payment planning)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| TR_CASH_BALANCE | Total Cash Balance | Currency | account.account | All banks |
| TR_CASH_IN_MTD | Cash In MTD | Currency | account.payment | Receipts |
| TR_CASH_OUT_MTD | Cash Out MTD | Currency | account.payment | Payments |
| TR_PDC_RECV_HOLDING | PDC Holding (Recv) | Currency | ops.pdc.receivable | Registered |
| TR_PDC_RECV_DEPOSITED | PDC Deposited | Currency | ops.pdc.receivable | Deposited |
| TR_PDC_RECV_MATURE_7D | PDC Maturing (7 days) | Currency | ops.pdc.receivable | Coming due |
| TR_PDC_PAY_ISSUED | PDC Issued | Currency | ops.pdc.payable | Issued |
| TR_PDC_PAY_MATURE_7D | PDC Clearing (7 days) | Currency | ops.pdc.payable | Coming due |
| TR_AR_DUE_7D | AR Due (7 days) | Currency | account.move | Coming due |
| TR_AP_DUE_7D | AP Due (7 days) | Currency | account.move | Coming due |
| TR_NET_CASH_FLOW_7D | Net Cash Flow (7 days) | Currency | Calculated | In - Out |

**Widgets:**
- Cash position gauge
- 7-day cash forecast
- PDC maturity calendar
- Bank balance breakdown

---

### P16 - Accountant/Controller Dashboard
**Visibility:** FULL ACCOUNTING  
**Purpose:** Journal entries, reconciliation, reporting  
**Cost/Margin:** YES (Full)

| KPI Code | KPI Name | Format | Source | Scope |
|----------|----------|--------|--------|-------|
| AC_JE_POSTED_MTD | JE Posted MTD | Integer | account.move | Own branch |
| AC_JE_PENDING | Pending JE Approval | Integer | account.move | Own branch |
| AC_UNRECONCILED | Unreconciled Items | Integer | account.bank.statement.line | Own branch |
| AC_PERIOD_STATUS | Period Status | Text | ops.fiscal.period | Current period |
| AC_AR_TOTAL | Total Receivables | Currency | account.move | Own branch |
| AC_AP_TOTAL | Total Payables | Currency | account.move | Own branch |
| AC_DEPRECIATION_DUE | Depreciation Due | Integer | ops.asset.depreciation | Unposted |
| AC_RECURRING_DUE | Recurring JE Due | Integer | ops.recurring.template | Today |
| AC_INVENTORY_VALUE | Inventory Value | Currency | stock.quant | Own branch |
| AC_ASSET_NBV | Asset NBV | Currency | ops.asset | Own branch |

**Widgets:**
- Period close checklist
- Trial balance summary
- Unreconciled items list
- Depreciation schedule

---

### P17 - HR/Payroll Specialist
**Visibility:** NO BUSINESS DATA DASHBOARD  
**Purpose:** Not applicable to business dashboards  
**Note:** Uses native Odoo HR module dashboards

---

## KPI SECURITY MATRIX

| KPI Category | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 | P11 | P12 | P13 | P14 | P15 | P16 |
|--------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Revenue | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓* | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Cost/COGS | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Margin | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| AR/AP | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Inventory | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓* | ✗ | ✗ | ✗ | ✓ |
| Valuation | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| PDC | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Cash | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Budget | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Assets | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| System | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Legend:** ✓ = Full access, ✓* = Own records only, ✗ = No access

---

## BRANCH/BU SCOPE MATRIX

| Persona | Scope | Domain Filter |
|---------|-------|---------------|
| P00-P03 | Company-wide | No filter |
| P04 | All branches in BU | `('ops_branch_id.business_unit_id', '=', user_bu_id)` |
| P05-P09 | Own branch | `('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)` |
| P10-P16 | Own records in branch | `('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)` + `('create_uid', '=', user.id)` |

---

## IMPLEMENTATION SUMMARY

### Total KPIs by Persona

| Persona | Dashboard Name | KPI Count | Widgets |
|---------|----------------|-----------|---------|
| P01 IT Admin | System Health | 8 | 2 |
| P02 CEO | Executive Overview | 11 | 4 |
| P03 CFO | Financial Command | 16 | 6 |
| P04 BU Leader | Business Unit | 10 | 4 |
| P05 Branch Mgr | Branch Operations | 15 | 4 |
| P06 Sales Mgr | Sales Performance | 13 | 4 |
| P07 Purchase Mgr | Procurement | 12 | 4 |
| P08 Inventory Mgr | Warehouse | 11 | 4 |
| P09 Finance Mgr | Branch Finance | 15 | 4 |
| P10 Sales Rep | My Sales | 10 | 4 |
| P11 Purchase Officer | My Purchases | 7 | 3 |
| P12 Warehouse Op | My Tasks | 5 | 2 |
| P13 AR Clerk | Receivables | 11 | 4 |
| P14 AP Clerk | Payables | 11 | 4 |
| P15 Treasury | Cash Management | 11 | 4 |
| P16 Accountant | Accounting | 10 | 4 |
| **TOTAL** | | **~176 KPIs** | **~61 Widgets** |

---

## NEXT STEPS

1. **Phase 1:** Update ops_kpi model with all 176 KPIs
2. **Phase 2:** Create 16 persona-specific dashboards
3. **Phase 3:** Implement security in `_get_secure_domain()` method
4. **Phase 4:** Add widget types (bar, line, pie, list)
5. **Phase 5:** Test with persona-based users
6. **Phase 6:** Performance optimization (caching, snapshots)

---

**SPECIFICATION COMPLETE**

**Version:** 1.0  
**Date:** January 31, 2026  
**Author:** Enterprise Architecture Team
