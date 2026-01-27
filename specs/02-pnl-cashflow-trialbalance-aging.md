# OPS Framework Financial Intelligence Reports
## Part 2 (Continued): Trial Balance, Aged Receivables, Aged Payables

---

## 📊 REPORT 5: Trial Balance (Continued)

### Layout: Multi-Column Balance Verification

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Trial Balance                                                                  │
│  ═════════════                                                                  │
│  ADJUSTED TRIAL BALANCE                                                         │
│  As at 31 December 2024                                                         │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │   Total Debits    12,458,920   =   Total Credits   12,458,920      ✓     │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                              │    OPENING     │    MOVEMENT    │  CLOSING  │ │
│  │ Code    Account Name         │   Debit Credit │  Debit  Credit │ Debit Cr  │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │ ASSETS                                                                    │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ 100000  Cash & Bank          │ 142,350    —   │ 856,420 841,880│ 156,890—│ │
│  │ 110000  Accounts Receivable  │  76,280    —   │ 1,420,600 1,407,540│ 89,340—│ │
│  │ 115000  Provision for Doubt. │     —   (4,200)│    —     3,500 │    —(7,700)│ │
│  │ 120000  Inventory            │  58,920    —   │ 772,000  763,470│ 67,450—│ │
│  │ 150000  Property, Plant & Eq │ 165,000    —   │  62,200    —   │227,200—│ │
│  │ 155000  Accumulated Deprec.  │     —  (36,660)│    —    45,200 │    —(81,860)│ │
│  │ 160000  Intangible Assets    │  38,900    —   │   8,400    —   │ 47,300—│ │
│  │ 165000  Accum. Amortization  │     —      —   │    —     2,100 │    —(2,100)│ │
│  │                                                                           │ │
│  │ LIABILITIES                                                               │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ 200000  Accounts Payable     │     —   24,890 │ 698,420  702,090│    —28,560│ │
│  │ 210000  Accrued Expenses     │     —    3,650 │  18,200   18,750│    —4,200│ │
│  │ 220000  Short-term Borrowings│     —    7,000 │   7,000    7,000│    —7,000│ │
│  │ 250000  Long-term Borrowings │     —   52,000 │  17,000   10,000│    —45,000│ │
│  │                                                                           │ │
│  │ EQUITY                                                                    │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ 300000  Share Capital        │     —  200,000 │    —       —   │    —200,000│ │
│  │ 310000  Legal Reserve        │     —   38,200 │    —     4,300 │    —42,500│ │
│  │ 320000  Retained Earnings    │     —  156,780 │ 205,690  247,360│    —198,450│ │
│  │                                                                           │ │
│  │ REVENUE                                                                   │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ 400000  Sales Revenue        │     —      —   │    —  1,380,000│    —1,380,000│ │
│  │ 410000  Other Income         │     —      —   │    —     55,000│    —55,000│ │
│  │                                                                           │ │
│  │ EXPENSES                                                                  │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ 500000  Cost of Goods Sold   │     —      —   │ 772,000    —   │772,000—│ │
│  │ 600000  Distribution Expenses│     —      —   │  50,000    —   │ 50,000—│ │
│  │ 610000  Admin Expenses       │     —      —   │ 325,000    —   │325,000—│ │
│  │ 620000  Other Op. Expenses   │     —      —   │  15,500    —   │ 15,500—│ │
│  │ 700000  Finance Costs        │     —      —   │   5,500    —   │  5,500—│ │
│  │ 710000  Finance Income       │     —      —   │    —      2,500│    —2,500│ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTALS                       │ 481,450 481,450│5,234,930 5,234,930│5,756,380 5,756,380│ │
│  │                                        ✓ BAL          ✓ BAL           ✓ BAL │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### QWeb Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="ops_report_trial_balance_document">
        <t t-call="web.external_layout">
            <div class="ops-financial-report ops-trial-balance">
                
                <!-- Report Title Block -->
                <div class="ops-report-title-block">
                    <div class="ops-document-type">Trial Balance</div>
                    <h1 class="ops-report-title">
                        <t t-if="doc.trial_balance_type == 'adjusted'">ADJUSTED </t>
                        <t t-if="doc.trial_balance_type == 'unadjusted'">UNADJUSTED </t>
                        <t t-if="doc.trial_balance_type == 'post_closing'">POST-CLOSING </t>
                        TRIAL BALANCE
                    </h1>
                    <div class="ops-report-meta">
                        <span class="ops-period">
                            As at <t t-esc="doc.as_at_date.strftime('%d %B %Y')"/>
                        </span>
                    </div>
                </div>
                
                <!-- Balance Verification Banner -->
                <div t-attf-class="ops-balance-verification #{('ops-balanced' if doc.is_balanced else 'ops-unbalanced')}">
                    <div class="ops-verification-item">
                        <span class="ops-verification-label">Total Debits</span>
                        <span class="ops-verification-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_debit)"/>
                        </span>
                    </div>
                    <span class="ops-verification-equals">=</span>
                    <div class="ops-verification-item">
                        <span class="ops-verification-label">Total Credits</span>
                        <span class="ops-verification-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_credit)"/>
                        </span>
                    </div>
                    <div class="ops-verification-status">
                        <t t-if="doc.is_balanced">
                            <span class="ops-status-icon">✓</span>
                            <span class="ops-status-text">Balanced</span>
                        </t>
                        <t t-else="">
                            <span class="ops-status-icon ops-error">✗</span>
                            <span class="ops-status-text ops-error">
                                Difference: <t t-esc="'{:,.0f}'.format(doc.difference)"/>
                            </span>
                        </t>
                    </div>
                </div>
                
                <!-- Trial Balance Table -->
                <table class="ops-data-table ops-trial-balance-table">
                    <thead>
                        <tr class="ops-header-row-main">
                            <th class="ops-col-code" rowspan="2">Code</th>
                            <th class="ops-col-name" rowspan="2">Account Name</th>
                            <th class="ops-col-group" colspan="2">Opening</th>
                            <th class="ops-col-group" colspan="2">Movement</th>
                            <th class="ops-col-group" colspan="2">Closing</th>
                        </tr>
                        <tr class="ops-header-row-sub">
                            <th class="ops-col-amount">Debit</th>
                            <th class="ops-col-amount">Credit</th>
                            <th class="ops-col-amount">Debit</th>
                            <th class="ops-col-amount">Credit</th>
                            <th class="ops-col-amount">Debit</th>
                            <th class="ops-col-amount">Credit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Group by Account Type -->
                        <t t-set="current_type" t-value="''"/>
                        <t t-foreach="doc.accounts" t-as="line">
                            <!-- Section Header when type changes -->
                            <t t-if="line.account_type != current_type">
                                <t t-set="current_type" t-value="line.account_type"/>
                                <tr class="ops-row-type-header">
                                    <td colspan="8">
                                        <t t-esc="line.account_type.upper()"/>
                                    </td>
                                </tr>
                            </t>
                            
                            <tr class="ops-row-item">
                                <td class="ops-col-code">
                                    <t t-esc="line.account_code"/>
                                </td>
                                <td class="ops-col-name">
                                    <t t-esc="line.account_name"/>
                                </td>
                                <td class="ops-col-amount">
                                    <t t-if="line.opening_debit">
                                        <t t-esc="'{:,.0f}'.format(line.opening_debit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                                <td class="ops-col-amount">
                                    <t t-if="line.opening_credit">
                                        <t t-esc="'{:,.0f}'.format(line.opening_credit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                                <td class="ops-col-amount">
                                    <t t-if="line.period_debit">
                                        <t t-esc="'{:,.0f}'.format(line.period_debit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                                <td class="ops-col-amount">
                                    <t t-if="line.period_credit">
                                        <t t-esc="'{:,.0f}'.format(line.period_credit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                                <td class="ops-col-amount ops-col-closing">
                                    <t t-if="line.closing_debit">
                                        <t t-esc="'{:,.0f}'.format(line.closing_debit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                                <td class="ops-col-amount ops-col-closing">
                                    <t t-if="line.closing_credit">
                                        <t t-esc="'{:,.0f}'.format(line.closing_credit)"/>
                                    </t>
                                    <t t-else="">
                                        <span class="ops-value-zero">—</span>
                                    </t>
                                </td>
                            </tr>
                        </t>
                        
                        <!-- Totals Row -->
                        <tr class="ops-row-grand-total">
                            <td class="ops-col-code"></td>
                            <td class="ops-col-name">TOTALS</td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_opening_debit)"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_opening_credit)"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_period_debit)"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_period_credit)"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_debit)"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_credit)"/>
                            </td>
                        </tr>
                        
                        <!-- Balance Check Row -->
                        <tr class="ops-row-balance-check">
                            <td colspan="2"></td>
                            <td colspan="2" class="ops-check-cell">
                                <t t-if="doc.opening_balanced">✓ BAL</t>
                                <t t-else="">✗ DIFF</t>
                            </td>
                            <td colspan="2" class="ops-check-cell">
                                <t t-if="doc.movement_balanced">✓ BAL</t>
                                <t t-else="">✗ DIFF</t>
                            </td>
                            <td colspan="2" class="ops-check-cell">
                                <t t-if="doc.is_balanced">✓ BAL</t>
                                <t t-else="">✗ DIFF</t>
                            </td>
                        </tr>
                    </tbody>
                </table>
                
            </div>
        </t>
    </template>
</odoo>
```

### Trial Balance Specific CSS

```css
/* Trial Balance Specific Styles */
.ops-trial-balance-table {
    font-size: var(--text-sm);
}

.ops-trial-balance-table .ops-col-code {
    width: 70px;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
}

.ops-trial-balance-table .ops-col-name {
    width: auto;
    text-align: left;
}

.ops-trial-balance-table .ops-col-amount {
    width: 75px;
    text-align: right;
    font-family: var(--font-display);
    font-variant-numeric: tabular-nums;
}

.ops-trial-balance-table .ops-col-group {
    text-align: center;
    background-color: var(--ops-gray-100);
    border-bottom: 1px solid var(--ops-gray-400);
}

.ops-header-row-main th {
    padding: var(--space-2) var(--space-2);
    font-size: var(--text-sm);
    font-weight: 600;
    border-bottom: none;
}

.ops-header-row-sub th {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--ops-gray-600);
    border-bottom: var(--border-section);
}

.ops-row-type-header td {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--ops-gray-700);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    padding: var(--space-4) var(--space-2) var(--space-2);
    border-bottom: 1px solid var(--ops-gray-400);
    background: transparent;
}

.ops-col-closing {
    background-color: var(--ops-gray-100);
}

.ops-row-balance-check td {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
    text-align: center;
    border: none;
    background: transparent;
}

.ops-check-cell {
    font-weight: 600;
    color: var(--ops-positive);
}

/* Balance Verification Banner */
.ops-balance-verification {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--space-6);
    padding: var(--space-4) var(--space-6);
    margin-bottom: var(--space-6);
    border: 1px solid var(--ops-gray-300);
    background-color: var(--ops-gray-100);
}

.ops-balance-verification.ops-balanced {
    border-color: var(--ops-positive);
    background-color: rgba(45, 90, 61, 0.05);
}

.ops-balance-verification.ops-unbalanced {
    border-color: var(--ops-negative);
    background-color: rgba(139, 58, 58, 0.05);
}

.ops-verification-item {
    text-align: center;
}

.ops-verification-label {
    display: block;
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    margin-bottom: var(--space-1);
}

.ops-verification-value {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--ops-black);
}

.ops-verification-equals {
    font-size: var(--text-lg);
    color: var(--ops-gray-500);
}

.ops-verification-status {
    margin-left: var(--space-6);
    padding: var(--space-2) var(--space-4);
    background-color: white;
    border-radius: 4px;
}
```

---

## 📊 REPORT 6: Aged Receivables

### Report ID: `OPS-FIN-006`
### Priority: Critical
### Category: Financial Intelligence Engine

---

### Purpose
Analyze outstanding customer invoices by age buckets to identify collection risks and manage cash flow.

### Data Requirements

```python
class AgedReceivablesData:
    # Header Info
    company_name: str
    as_at_date: date
    aging_method: str  # 'invoice_date' or 'due_date'
    
    # Aging Buckets Configuration
    buckets: List[AgingBucket]  # e.g., Current, 1-30, 31-60, 61-90, 90+
    
    # Customer Data
    customers: List[CustomerAging]
    
    # Summary
    total_receivable: Decimal
    total_by_bucket: Dict[str, Decimal]
    collection_risk_score: str  # 'Low', 'Medium', 'High', 'Critical'
    overdue_percentage: Decimal
    dso: Decimal  # Days Sales Outstanding

class AgingBucket:
    name: str  # e.g., "Current", "1-30 Days"
    days_from: int
    days_to: int
    risk_level: str  # 'normal', 'warning', 'danger', 'critical'

class CustomerAging:
    partner_id: int
    partner_name: str
    partner_code: str
    credit_limit: Decimal
    current: Decimal
    bucket_1_30: Decimal
    bucket_31_60: Decimal
    bucket_61_90: Decimal
    bucket_90_plus: Decimal
    total: Decimal
    oldest_invoice_date: date
    overdue_pct: Decimal
```

### Layout: Risk-Highlighted Aging Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Accounts Receivable Analysis                                                   │
│  ════════════════════════════                                                   │
│  AGED RECEIVABLES                                                               │
│  As at 31 December 2024                            Aging by: Due Date           │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │   Total Receivable          DSO              Overdue         Risk Level   │ │
│  │   ━━━━━━━━━━━━━━━━━         ━━━━━━━          ━━━━━━━━━       ━━━━━━━━━━   │ │
│  │      245,800               42 Days           26.9%           ▓ MEDIUM     │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  AGING DISTRIBUTION                                                             │
│  ──────────────────                                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Current    │██████████████████████████████████████████░░░░░░│ 179,700 73.1%│ │
│  │ 1-30 Days  │████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  35,400 14.4%│ │
│  │ 31-60 Days │██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│  17,600  7.2%│ │
│  │ 61-90 Days │██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   4,200  1.7%│ │
│  │ Over 90    │███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   8,900  3.6%│ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  DETAIL BY CUSTOMER                                                             │
│  ──────────────────                                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Customer           │ Current │ 1-30  │ 31-60 │ 61-90 │  90+  │   Total   │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │ ▓ HIGH RISK (Overdue > 50%)                                               │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ ABC Trading Co.    │  12,500 │ 8,200 │ 6,400 │ 2,100 │▓4,800 │   34,000  │ │
│  │   Credit: 30,000   │         │       │       │       │       │  ⚠ 113%   │ │
│  │                                                                           │ │
│  │ ▒ MEDIUM RISK (Overdue 25-50%)                                            │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ Gulf Enterprises   │  28,400 │12,500 │ 4,200 │   —   │   —   │   45,100  │ │
│  │   Credit: 50,000   │         │       │       │       │       │    90%    │ │
│  │                                                                           │ │
│  │ XYZ Industries     │  18,200 │ 6,800 │ 3,400 │ 1,200 │   —   │   29,600  │ │
│  │   Credit: 40,000   │         │       │       │       │       │    74%    │ │
│  │                                                                           │ │
│  │ ░ NORMAL RISK (Overdue < 25%)                                             │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ Premier Holdings   │  45,600 │ 3,200 │ 1,800 │   —   │   —   │   50,600  │ │
│  │   Credit: 75,000   │         │       │       │       │       │    67%    │ │
│  │                                                                           │ │
│  │ National Corp.     │  38,000 │ 2,400 │   —   │   —   │   —   │   40,400  │ │
│  │   Credit: 60,000   │         │       │       │       │       │    67%    │ │
│  │                                                                           │ │
│  │ [Additional customers...]                                                 │ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│  │ TOTAL              │ 179,700 │35,400 │17,600 │ 4,200 │ 8,900 │  245,800  │ │
│  │ % of Total         │   73.1% │ 14.4% │  7.2% │  1.7% │  3.6% │   100.0%  │ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### QWeb Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="ops_report_aged_receivables_document">
        <t t-call="web.external_layout">
            <div class="ops-financial-report ops-aged-receivables">
                
                <!-- Report Title Block -->
                <div class="ops-report-title-block">
                    <div class="ops-document-type">
                        Accounts Receivable Analysis
                    </div>
                    <h1 class="ops-report-title">AGED RECEIVABLES</h1>
                    <div class="ops-report-meta">
                        <span class="ops-period">
                            As at <t t-esc="doc.as_at_date.strftime('%d %B %Y')"/>
                        </span>
                        <span class="ops-aging-method">
                            Aging by: <t t-esc="'Due Date' if doc.aging_method == 'due_date' else 'Invoice Date'"/>
                        </span>
                    </div>
                </div>
                
                <!-- KPI Summary Bar -->
                <div class="ops-ar-summary-bar">
                    <div class="ops-ar-kpi">
                        <span class="ops-ar-kpi-label">Total Receivable</span>
                        <span class="ops-ar-kpi-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_receivable)"/>
                        </span>
                    </div>
                    <div class="ops-ar-kpi">
                        <span class="ops-ar-kpi-label">DSO</span>
                        <span class="ops-ar-kpi-value">
                            <t t-esc="'{:.0f}'.format(doc.dso)"/> Days
                        </span>
                    </div>
                    <div class="ops-ar-kpi">
                        <span class="ops-ar-kpi-label">Overdue</span>
                        <span class="ops-ar-kpi-value">
                            <t t-esc="'{:.1f}%'.format(doc.overdue_percentage)"/>
                        </span>
                    </div>
                    <div t-attf-class="ops-ar-risk-badge ops-risk-#{doc.collection_risk_score.lower()}">
                        <span class="ops-risk-label">Risk Level</span>
                        <span class="ops-risk-value">
                            <t t-esc="doc.collection_risk_score"/>
                        </span>
                    </div>
                </div>
                
                <!-- Aging Distribution Chart -->
                <div class="ops-aging-distribution">
                    <div class="ops-subsection-header">Aging Distribution</div>
                    <div class="ops-aging-bars">
                        <t t-foreach="doc.buckets" t-as="bucket">
                            <div class="ops-aging-bar-row">
                                <span class="ops-aging-bar-label">
                                    <t t-esc="bucket.name"/>
                                </span>
                                <div class="ops-aging-bar-container">
                                    <div t-attf-class="ops-aging-bar ops-risk-#{bucket.risk_level}"
                                         t-attf-style="width: #{(doc.total_by_bucket[bucket.name] / doc.total_receivable * 100) if doc.total_receivable else 0}%">
                                    </div>
                                </div>
                                <span class="ops-aging-bar-amount">
                                    <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get(bucket.name, 0))"/>
                                </span>
                                <span class="ops-aging-bar-pct">
                                    <t t-esc="'{:.1f}%'.format((doc.total_by_bucket.get(bucket.name, 0) / doc.total_receivable * 100) if doc.total_receivable else 0)"/>
                                </span>
                            </div>
                        </t>
                    </div>
                </div>
                
                <!-- Customer Detail Table -->
                <div class="ops-subsection-header">Detail by Customer</div>
                
                <table class="ops-data-table ops-ar-table">
                    <thead>
                        <tr>
                            <th class="ops-col-customer">Customer</th>
                            <th class="ops-col-amount">Current</th>
                            <th class="ops-col-amount">1-30</th>
                            <th class="ops-col-amount">31-60</th>
                            <th class="ops-col-amount">61-90</th>
                            <th class="ops-col-amount ops-col-critical">90+</th>
                            <th class="ops-col-amount ops-col-total">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Group: High Risk -->
                        <t t-set="high_risk" t-value="[c for c in doc.customers if c.overdue_pct > 50]"/>
                        <t t-if="high_risk">
                            <tr class="ops-row-risk-header ops-risk-high">
                                <td colspan="7">▓ HIGH RISK (Overdue > 50%)</td>
                            </tr>
                            <t t-foreach="high_risk" t-as="customer">
                                <t t-call="ops_reports.ops_ar_customer_row"/>
                            </t>
                        </t>
                        
                        <!-- Group: Medium Risk -->
                        <t t-set="medium_risk" t-value="[c for c in doc.customers if 25 &lt; c.overdue_pct &lt;= 50]"/>
                        <t t-if="medium_risk">
                            <tr class="ops-row-risk-header ops-risk-medium">
                                <td colspan="7">▒ MEDIUM RISK (Overdue 25-50%)</td>
                            </tr>
                            <t t-foreach="medium_risk" t-as="customer">
                                <t t-call="ops_reports.ops_ar_customer_row"/>
                            </t>
                        </t>
                        
                        <!-- Group: Normal Risk -->
                        <t t-set="normal_risk" t-value="[c for c in doc.customers if c.overdue_pct &lt;= 25]"/>
                        <t t-if="normal_risk">
                            <tr class="ops-row-risk-header ops-risk-normal">
                                <td colspan="7">░ NORMAL RISK (Overdue &lt; 25%)</td>
                            </tr>
                            <t t-foreach="normal_risk" t-as="customer">
                                <t t-call="ops_reports.ops_ar_customer_row"/>
                            </t>
                        </t>
                        
                        <!-- Totals -->
                        <tr class="ops-row-grand-total">
                            <td class="ops-col-customer">TOTAL</td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get('Current', 0))"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get('1-30', 0))"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get('31-60', 0))"/>
                            </td>
                            <td class="ops-col-amount">
                                <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get('61-90', 0))"/>
                            </td>
                            <td class="ops-col-amount ops-col-critical">
                                <t t-esc="'{:,.0f}'.format(doc.total_by_bucket.get('90+', 0))"/>
                            </td>
                            <td class="ops-col-amount ops-col-total">
                                <t t-esc="'{:,.0f}'.format(doc.total_receivable)"/>
                            </td>
                        </tr>
                        <tr class="ops-row-percentage">
                            <td class="ops-col-customer">% of Total</td>
                            <t t-foreach="doc.buckets" t-as="bucket">
                                <td class="ops-col-amount">
                                    <t t-esc="'{:.1f}%'.format((doc.total_by_bucket.get(bucket.name, 0) / doc.total_receivable * 100) if doc.total_receivable else 0)"/>
                                </td>
                            </t>
                            <td class="ops-col-amount ops-col-total">100.0%</td>
                        </tr>
                    </tbody>
                </table>
                
            </div>
        </t>
    </template>
    
    <!-- Customer Row Sub-template -->
    <template id="ops_ar_customer_row">
        <tr class="ops-row-item">
            <td class="ops-col-customer">
                <div class="ops-customer-name"><t t-esc="customer.partner_name"/></div>
                <div class="ops-customer-credit">
                    Credit: <t t-esc="'{:,.0f}'.format(customer.credit_limit)"/>
                </div>
            </td>
            <td class="ops-col-amount">
                <t t-if="customer.current">
                    <t t-esc="'{:,.0f}'.format(customer.current)"/>
                </t>
                <t t-else=""><span class="ops-value-zero">—</span></t>
            </td>
            <td class="ops-col-amount">
                <t t-if="customer.bucket_1_30">
                    <t t-esc="'{:,.0f}'.format(customer.bucket_1_30)"/>
                </t>
                <t t-else=""><span class="ops-value-zero">—</span></t>
            </td>
            <td class="ops-col-amount">
                <t t-if="customer.bucket_31_60">
                    <t t-esc="'{:,.0f}'.format(customer.bucket_31_60)"/>
                </t>
                <t t-else=""><span class="ops-value-zero">—</span></t>
            </td>
            <td class="ops-col-amount">
                <t t-if="customer.bucket_61_90">
                    <t t-esc="'{:,.0f}'.format(customer.bucket_61_90)"/>
                </t>
                <t t-else=""><span class="ops-value-zero">—</span></t>
            </td>
            <td t-attf-class="ops-col-amount ops-col-critical #{('ops-value-critical' if customer.bucket_90_plus else '')}">
                <t t-if="customer.bucket_90_plus">
                    <t t-esc="'{:,.0f}'.format(customer.bucket_90_plus)"/>
                </t>
                <t t-else=""><span class="ops-value-zero">—</span></t>
            </td>
            <td class="ops-col-amount ops-col-total">
                <t t-esc="'{:,.0f}'.format(customer.total)"/>
                <div t-attf-class="ops-credit-usage #{('ops-over-limit' if customer.total > customer.credit_limit else '')}">
                    <t t-if="customer.credit_limit">
                        <t t-esc="'{:.0f}%'.format(customer.total / customer.credit_limit * 100)"/>
                    </t>
                </div>
            </td>
        </tr>
    </template>
</odoo>
```

### Aged Receivables Specific CSS

```css
/* Aged Receivables Specific Styles */
.ops-ar-summary-bar {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    padding: var(--space-5) var(--space-6);
    margin-bottom: var(--space-6);
    background-color: var(--ops-gray-100);
    border: 1px solid var(--ops-gray-300);
}

.ops-ar-kpi {
    text-align: center;
    padding: 0 var(--space-4);
    border-right: 1px solid var(--ops-gray-300);
}

.ops-ar-kpi:last-of-type {
    border-right: none;
}

.ops-ar-kpi-label {
    display: block;
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    margin-bottom: var(--space-1);
}

.ops-ar-kpi-value {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--ops-black);
}

.ops-ar-risk-badge {
    margin-left: auto;
    padding: var(--space-3) var(--space-5);
    text-align: center;
    border-radius: 4px;
}

.ops-ar-risk-badge .ops-risk-label {
    display: block;
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    margin-bottom: var(--space-1);
}

.ops-ar-risk-badge .ops-risk-value {
    font-size: var(--text-md);
    font-weight: 700;
}

.ops-risk-low {
    background-color: rgba(45, 90, 61, 0.1);
    color: var(--ops-positive);
}

.ops-risk-medium {
    background-color: rgba(139, 105, 20, 0.1);
    color: var(--ops-warning);
}

.ops-risk-high {
    background-color: rgba(139, 58, 58, 0.1);
    color: var(--ops-negative);
}

.ops-risk-critical {
    background-color: rgba(139, 58, 58, 0.2);
    color: var(--ops-negative);
}

/* Aging Distribution Bars */
.ops-aging-distribution {
    margin-bottom: var(--space-6);
}

.ops-aging-bars {
    padding: var(--space-4);
    background-color: var(--ops-gray-100);
    border: 1px solid var(--ops-gray-300);
}

.ops-aging-bar-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-2);
}

.ops-aging-bar-row:last-child {
    margin-bottom: 0;
}

.ops-aging-bar-label {
    width: 80px;
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--ops-gray-700);
}

.ops-aging-bar-container {
    flex: 1;
    height: 20px;
    background-color: var(--ops-gray-200);
    border-radius: 2px;
    overflow: hidden;
}

.ops-aging-bar {
    height: 100%;
    border-radius: 2px;
    transition: width 0.3s ease;
}

.ops-aging-bar.ops-risk-normal {
    background-color: var(--ops-gray-500);
}

.ops-aging-bar.ops-risk-warning {
    background-color: var(--ops-warning);
}

.ops-aging-bar.ops-risk-danger {
    background-color: var(--ops-negative);
}

.ops-aging-bar.ops-risk-critical {
    background-color: #5c1a1a;
}

.ops-aging-bar-amount {
    width: 70px;
    text-align: right;
    font-family: var(--font-display);
    font-size: var(--text-sm);
    font-weight: 500;
}

.ops-aging-bar-pct {
    width: 50px;
    text-align: right;
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
}

/* AR Table */
.ops-ar-table .ops-col-customer {
    width: auto;
    text-align: left;
}

.ops-ar-table .ops-col-amount {
    width: 70px;
    text-align: right;
    font-family: var(--font-display);
}

.ops-ar-table .ops-col-critical {
    background-color: rgba(139, 58, 58, 0.05);
}

.ops-ar-table .ops-col-total {
    background-color: var(--ops-gray-100);
    font-weight: 600;
}

.ops-row-risk-header td {
    font-size: var(--text-sm);
    font-weight: 600;
    padding: var(--space-3) var(--space-2);
    border-bottom: 1px solid var(--ops-gray-400);
    background: transparent;
}

.ops-row-risk-header.ops-risk-high td {
    color: var(--ops-negative);
}

.ops-row-risk-header.ops-risk-medium td {
    color: var(--ops-warning);
}

.ops-row-risk-header.ops-risk-normal td {
    color: var(--ops-gray-600);
}

.ops-customer-name {
    font-weight: 500;
}

.ops-customer-credit {
    font-size: var(--text-xs);
    color: var(--ops-gray-500);
    margin-top: var(--space-1);
}

.ops-credit-usage {
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
    margin-top: var(--space-1);
}

.ops-credit-usage.ops-over-limit {
    color: var(--ops-negative);
    font-weight: 600;
}

.ops-value-critical {
    color: var(--ops-negative);
    font-weight: 600;
}

.ops-row-percentage td {
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
    font-style: italic;
    padding-top: var(--space-1);
    padding-bottom: var(--space-3);
    border: none;
    background: transparent;
}
```

---

## 📊 REPORT 7: Aged Payables

### Report ID: `OPS-FIN-007`
### Priority: Critical
### Category: Financial Intelligence Engine

---

### Purpose
Analyze outstanding vendor invoices by age buckets to manage payment schedules and maintain vendor relationships.

### Data Requirements

```python
class AgedPayablesData:
    # Header Info
    company_name: str
    as_at_date: date
    aging_method: str  # 'invoice_date' or 'due_date'
    
    # Aging Buckets
    buckets: List[AgingBucket]
    
    # Vendor Data
    vendors: List[VendorAging]
    
    # Summary
    total_payable: Decimal
    total_by_bucket: Dict[str, Decimal]
    liquidity_status: str  # 'Comfortable', 'Tight', 'Strained', 'Critical'
    overdue_percentage: Decimal
    dpo: Decimal  # Days Payable Outstanding
    
    # Cash Flow Impact
    cash_available: Decimal
    coverage_ratio: Decimal  # cash / total_payable

class VendorAging:
    partner_id: int
    partner_name: str
    partner_code: str
    payment_terms: str
    current: Decimal
    bucket_1_30: Decimal
    bucket_31_60: Decimal
    bucket_61_90: Decimal
    bucket_90_plus: Decimal
    total: Decimal
    oldest_invoice_date: date
    priority: str  # 'Critical', 'High', 'Normal'
```

### Layout: Payment Priority Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Accounts Payable Analysis                                                      │
│  ═════════════════════════                                                      │
│  AGED PAYABLES                                                                  │
│  As at 31 December 2024                            Aging by: Due Date           │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │   Total Payable          DPO              Overdue         Liquidity       │ │
│  │   ━━━━━━━━━━━━━━         ━━━━━            ━━━━━━━━        ━━━━━━━━━━━     │ │
│  │      156,420            38 Days           18.2%           COMFORTABLE     │ │
│  │                                                                           │ │
│  │   Cash Available: 156,890    Coverage Ratio: 100.3%                       │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  PAYMENT PRIORITY SCHEDULE                                                      │
│  ─────────────────────────                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │ ▓ IMMEDIATE (Overdue 60+ days)                          Total:   12,400  │ │
│  │   - Vendor A (72 days overdue)                                    8,200  │ │
│  │   - Vendor B (65 days overdue)                                    4,200  │ │
│  │                                                                           │ │
│  │ ▒ THIS WEEK (Due within 7 days)                         Total:   28,500  │ │
│  │   - Vendor C (due in 3 days)                                     15,200  │ │
│  │   - Vendor D (due in 5 days)                                     13,300  │ │
│  │                                                                           │ │
│  │ ░ SCHEDULED (Due 8-30 days)                             Total:   45,800  │ │
│  │   - [Multiple vendors...]                                                │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  DETAIL BY VENDOR                                                               │
│  ────────────────                                                               │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Vendor             Terms  │ Current │ 1-30  │ 31-60 │ 61-90 │  90+  │Total│ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │ Raw Materials Co.  Net 30 │  24,500 │ 8,200 │ 2,100 │   —   │   —   │34,800│ │
│  │ Equipment Supply   Net 45 │  18,200 │12,400 │ 4,500 │ 2,800 │   —   │37,900│ │
│  │ Utilities Provider Net 15 │   5,400 │   —   │   —   │   —   │   —   │ 5,400│ │
│  │ [Additional vendors...]                                                   │ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  │ TOTAL                     │ 112,800 │28,400 │ 9,200 │ 4,200 │ 1,820│156,420│ │
│  │ % of Total                │   72.1% │ 18.2% │  5.9% │  2.7% │  1.2%│100.0%│ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Aged Payables Specific CSS

```css
/* Aged Payables - Additional/Override Styles */
.ops-ap-summary-bar {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--space-5) var(--space-6);
    margin-bottom: var(--space-6);
    background-color: var(--ops-gray-100);
    border: 1px solid var(--ops-gray-300);
}

.ops-ap-kpi-row {
    display: flex;
    align-items: center;
    gap: var(--space-6);
}

.ops-ap-cash-row {
    display: flex;
    gap: var(--space-8);
    padding-top: var(--space-3);
    border-top: 1px dashed var(--ops-gray-400);
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
}

.ops-liquidity-comfortable { color: var(--ops-positive); }
.ops-liquidity-tight { color: var(--ops-warning); }
.ops-liquidity-strained { color: var(--ops-negative); }
.ops-liquidity-critical { color: #5c1a1a; font-weight: 700; }

/* Payment Priority Schedule */
.ops-payment-priority {
    margin-bottom: var(--space-6);
    padding: var(--space-4);
    background-color: var(--ops-gray-100);
    border: 1px solid var(--ops-gray-300);
}

.ops-priority-group {
    margin-bottom: var(--space-4);
}

.ops-priority-group:last-child {
    margin-bottom: 0;
}

.ops-priority-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    margin-bottom: var(--space-2);
}

.ops-priority-header.ops-immediate {
    color: var(--ops-negative);
}

.ops-priority-header.ops-this-week {
    color: var(--ops-warning);
}

.ops-priority-header.ops-scheduled {
    color: var(--ops-gray-600);
}

.ops-priority-items {
    padding-left: var(--space-6);
    font-size: var(--text-sm);
    color: var(--ops-gray-700);
}

.ops-priority-item {
    display: flex;
    justify-content: space-between;
    padding: var(--space-1) 0;
}

.ops-ap-table .ops-col-terms {
    width: 60px;
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
    text-align: center;
}
```

---

*[Continue to Part 3: Ledger Intelligence Engine, Asset Intelligence Engine]*
