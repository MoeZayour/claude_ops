# OPS Framework Financial Intelligence Reports
## Complete Design System Documentation v1.0

---

# DESIGN SYSTEM OVERVIEW

## Philosophy: The Meridian Standard

These reports follow the **Meridian Executive Design Standard**—a philosophy that commands authority through restraint, clarity, and precision. Every element earns its place. Numbers are treated with respect. White space is intentional.

---

## Global Design Tokens

### Color Palette

```css
/* Primary - Corporate Authority */
--ops-black: #1a1a1a;
--ops-charcoal: #2d2d2d;
--ops-slate: #4a4a4a;

/* Accent - Subtle Sophistication */
--ops-gold: #c9a962;
--ops-gold-muted: #a8935a;

/* Semantic - Financial Context */
--ops-positive: #2d5a3d;      /* Muted green for profits */
--ops-negative: #8b3a3a;       /* Muted red for losses */
--ops-warning: #8b6914;        /* Muted amber for attention */

/* Neutral Scale */
--ops-gray-100: #fafafa;
--ops-gray-200: #f5f5f5;
--ops-gray-300: #e5e5e5;
--ops-gray-400: #d4d4d4;
--ops-gray-500: #a3a3a3;
--ops-gray-600: #737373;
--ops-gray-700: #525252;
--ops-gray-800: #404040;

/* Background */
--ops-paper: #ffffff;
--ops-highlight-row: #fafaf8;
```

### Typography Scale

```css
/* Font Families */
--font-display: 'Georgia', 'Times New Roman', serif;
--font-body: 'DejaVu Sans', 'Arial', sans-serif;
--font-mono: 'DejaVu Sans Mono', 'Consolas', monospace;

/* Font Sizes */
--text-xs: 7pt;      /* Footer notes, page numbers */
--text-sm: 8pt;      /* Column headers, captions */
--text-base: 9pt;    /* Body text, line items */
--text-md: 10pt;     /* Subtotals, emphasis */
--text-lg: 11pt;     /* Section totals */
--text-xl: 13pt;     /* Grand totals */
--text-2xl: 18pt;    /* Report title */
--text-3xl: 24pt;    /* Company name */

/* Line Heights */
--leading-tight: 1.2;
--leading-normal: 1.5;
--leading-relaxed: 1.7;

/* Letter Spacing */
--tracking-tight: -0.5px;
--tracking-normal: 0;
--tracking-wide: 1px;
--tracking-wider: 2px;
--tracking-widest: 3px;
```

### Spacing System

```css
/* Base unit: 4px */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

### Border Styles

```css
/* Standard borders */
--border-light: 1px solid var(--ops-gray-300);
--border-medium: 1px solid var(--ops-gray-400);
--border-dark: 1px solid var(--ops-black);
--border-section: 2px solid var(--ops-black);
--border-total: 3px double var(--ops-black);

/* Accent borders */
--border-gold: 4px solid var(--ops-gold);
```

---

## Page Layout Standards

### A4 Page Setup

```css
@page {
    size: A4 portrait;  /* 210mm × 297mm */
    margin: 20mm 15mm 25mm 15mm;
    
    @top-left {
        content: element(company-header-left);
    }
    @top-right {
        content: element(company-header-right);
    }
    @bottom-left {
        content: element(footer-left);
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 8pt;
        color: #737373;
    }
    @bottom-right {
        content: element(footer-right);
    }
}

@page :first {
    margin-top: 15mm;  /* Reduced top margin for first page */
}
```

### Document Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [ODOO COMPANY HEADER - From document layout settings]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  REPORT TITLE BLOCK                                  │   │
│  │  • Document type label (small caps)                  │   │
│  │  • Report name (large, light weight)                 │   │
│  │  • Period/Date (subtle)                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SUMMARY BLOCK (Optional)                            │   │
│  │  • Key totals, equation verification, KPIs           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MAIN DATA SECTION                                   │   │
│  │  • Section headers                                   │   │
│  │  • Data tables                                       │   │
│  │  • Subtotals and totals                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  NOTES / SIGNATURES (Optional)                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [ODOO COMPANY FOOTER - From document layout settings]      │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Library

### 1. Report Title Block

```html
<div class="ops-report-title-block">
    <div class="ops-document-type">Consolidated Statement of Financial Position</div>
    <h1 class="ops-report-title">BALANCE SHEET</h1>
    <div class="ops-report-meta">
        <span class="ops-period">As at 31 December 2024</span>
        <span class="ops-currency">Expressed in QAR '000</span>
    </div>
</div>
```

```css
.ops-report-title-block {
    margin-bottom: var(--space-8);
    padding-bottom: var(--space-6);
    border-bottom: 1px solid var(--ops-gray-300);
}

.ops-document-type {
    font-family: var(--font-body);
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    margin-bottom: var(--space-2);
}

.ops-report-title {
    font-family: var(--font-display);
    font-size: var(--text-3xl);
    font-weight: 300;
    color: var(--ops-black);
    letter-spacing: var(--tracking-tight);
    margin: 0 0 var(--space-3) 0;
    line-height: var(--leading-tight);
}

.ops-report-meta {
    display: flex;
    justify-content: space-between;
    font-size: var(--text-base);
    color: var(--ops-gray-600);
}

.ops-period {
    font-weight: 500;
}

.ops-currency {
    font-style: italic;
}
```

### 2. Section Header

```html
<div class="ops-section-header">
    <span class="ops-section-title">ASSETS</span>
</div>
```

```css
.ops-section-header {
    font-family: var(--font-body);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--ops-black);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--space-3) 0;
    border-bottom: var(--border-section);
    margin-top: var(--space-6);
    margin-bottom: var(--space-4);
}
```

### 3. Sub-Section Header

```html
<div class="ops-subsection-header">Non-Current Assets</div>
```

```css
.ops-subsection-header {
    font-family: var(--font-body);
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--ops-gray-700);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    padding: var(--space-2) 0;
    margin-top: var(--space-4);
    margin-bottom: var(--space-2);
}
```

### 4. Data Table

```html
<table class="ops-data-table">
    <thead>
        <tr>
            <th class="ops-col-label">Description</th>
            <th class="ops-col-note">Note</th>
            <th class="ops-col-amount">2024</th>
            <th class="ops-col-amount ops-col-prior">2023</th>
        </tr>
    </thead>
    <tbody>
        <tr class="ops-row-item">
            <td class="ops-col-label ops-indent-1">Property, Plant & Equipment</td>
            <td class="ops-col-note">5</td>
            <td class="ops-col-amount">142,850</td>
            <td class="ops-col-amount ops-col-prior">128,340</td>
        </tr>
        <tr class="ops-row-subtotal">
            <td class="ops-col-label">Total Non-Current Assets</td>
            <td class="ops-col-note"></td>
            <td class="ops-col-amount">222,510</td>
            <td class="ops-col-amount ops-col-prior">204,580</td>
        </tr>
        <tr class="ops-row-total">
            <td class="ops-col-label">TOTAL ASSETS</td>
            <td class="ops-col-note"></td>
            <td class="ops-col-amount">548,840</td>
            <td class="ops-col-amount ops-col-prior">491,070</td>
        </tr>
    </tbody>
</table>
```

```css
.ops-data-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: var(--text-base);
}

/* Column Headers */
.ops-data-table thead th {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-normal);
    padding: var(--space-2) var(--space-3);
    border-bottom: 1px solid var(--ops-gray-400);
    vertical-align: bottom;
}

.ops-col-label {
    text-align: left;
    width: auto;
}

.ops-col-note {
    text-align: center;
    width: 40px;
}

.ops-col-amount {
    text-align: right;
    width: 90px;
    font-family: var(--font-display);
}

.ops-col-prior {
    color: var(--ops-gray-500);
}

/* Data Rows */
.ops-data-table tbody td {
    padding: var(--space-2) var(--space-3);
    border-bottom: 1px solid var(--ops-gray-200);
    vertical-align: middle;
}

.ops-data-table tbody td.ops-col-amount {
    font-family: var(--font-display);
    font-variant-numeric: tabular-nums;
}

.ops-data-table tbody td.ops-col-note {
    font-size: var(--text-sm);
    color: var(--ops-gray-500);
}

/* Indentation */
.ops-indent-1 { padding-left: var(--space-6) !important; }
.ops-indent-2 { padding-left: var(--space-10) !important; color: var(--ops-gray-600); }
.ops-indent-3 { padding-left: var(--space-12) !important; color: var(--ops-gray-500); font-style: italic; }

/* Row Types */
.ops-row-item td {
    font-weight: 400;
}

.ops-row-subtotal td {
    font-weight: 600;
    background-color: var(--ops-gray-100);
    border-top: 1px solid var(--ops-gray-400);
    padding-top: var(--space-3);
    padding-bottom: var(--space-3);
}

.ops-row-total td {
    font-weight: 700;
    font-size: var(--text-md);
    background-color: var(--ops-gray-100);
    border-top: var(--border-section);
    border-bottom: var(--border-total);
    padding-top: var(--space-3);
    padding-bottom: var(--space-3);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
}

.ops-row-grand-total td {
    font-weight: 700;
    font-size: var(--text-lg);
    background-color: var(--ops-black);
    color: var(--ops-paper);
    border: none;
    padding: var(--space-4) var(--space-3);
}

/* Value States */
.ops-value-zero {
    color: var(--ops-gray-400);
}

.ops-value-negative {
    color: var(--ops-negative);
}

.ops-value-positive {
    color: var(--ops-positive);
}
```

### 5. Summary Equation Block

```html
<div class="ops-equation-block">
    <div class="ops-equation-item">
        <span class="ops-equation-label">Assets</span>
        <span class="ops-equation-value">548,840</span>
    </div>
    <span class="ops-equation-operator">=</span>
    <div class="ops-equation-item">
        <span class="ops-equation-label">Equity</span>
        <span class="ops-equation-value">440,950</span>
    </div>
    <span class="ops-equation-operator">+</span>
    <div class="ops-equation-item">
        <span class="ops-equation-label">Liabilities</span>
        <span class="ops-equation-value">107,890</span>
    </div>
    <div class="ops-equation-status">
        <span class="ops-status-icon">✓</span>
        <span class="ops-status-text">Balanced</span>
    </div>
</div>
```

```css
.ops-equation-block {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--space-6);
    padding: var(--space-5) 0;
    margin: var(--space-6) 0;
    border-top: 1px solid var(--ops-gray-300);
    border-bottom: 1px solid var(--ops-gray-300);
}

.ops-equation-item {
    text-align: center;
}

.ops-equation-label {
    display: block;
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    margin-bottom: var(--space-1);
}

.ops-equation-value {
    font-family: var(--font-display);
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--ops-black);
}

.ops-equation-operator {
    font-size: var(--text-lg);
    color: var(--ops-gray-400);
    font-weight: 300;
}

.ops-equation-status {
    margin-left: var(--space-6);
    padding: var(--space-2) var(--space-4);
    background-color: var(--ops-gray-100);
    border-radius: 4px;
}

.ops-status-icon {
    color: var(--ops-positive);
    margin-right: var(--space-1);
}

.ops-status-text {
    font-size: var(--text-sm);
    color: var(--ops-gray-700);
}
```

### 6. Signature Block

```html
<div class="ops-signature-block">
    <div class="ops-signature-item">
        <div class="ops-signature-line"></div>
        <div class="ops-signature-title">Chairman</div>
        <div class="ops-signature-name">Name</div>
    </div>
    <div class="ops-signature-item">
        <div class="ops-signature-line"></div>
        <div class="ops-signature-title">Chief Executive Officer</div>
        <div class="ops-signature-name">Name</div>
    </div>
    <div class="ops-signature-item">
        <div class="ops-signature-line"></div>
        <div class="ops-signature-title">Chief Financial Officer</div>
        <div class="ops-signature-name">Name</div>
    </div>
</div>
```

```css
.ops-signature-block {
    display: flex;
    justify-content: space-between;
    gap: var(--space-8);
    margin-top: var(--space-12);
    padding-top: var(--space-8);
    border-top: 1px solid var(--ops-gray-300);
}

.ops-signature-item {
    flex: 1;
}

.ops-signature-line {
    border-bottom: 1px solid var(--ops-black);
    height: 40px;
    margin-bottom: var(--space-2);
}

.ops-signature-title {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--ops-gray-700);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
}

.ops-signature-name {
    font-size: var(--text-sm);
    color: var(--ops-gray-500);
    margin-top: var(--space-1);
}
```

### 7. Notes Reference

```html
<div class="ops-notes-reference">
    The accompanying notes form an integral part of these financial statements.
</div>
```

```css
.ops-notes-reference {
    font-size: var(--text-xs);
    color: var(--ops-gray-500);
    font-style: italic;
    margin-top: var(--space-8);
    padding-top: var(--space-4);
    border-top: 1px solid var(--ops-gray-200);
}
```

---

## Utility Classes

```css
/* Text Alignment */
.ops-text-left { text-align: left; }
.ops-text-center { text-align: center; }
.ops-text-right { text-align: right; }

/* Font Weight */
.ops-font-normal { font-weight: 400; }
.ops-font-medium { font-weight: 500; }
.ops-font-semibold { font-weight: 600; }
.ops-font-bold { font-weight: 700; }

/* Text Transform */
.ops-uppercase { text-transform: uppercase; }
.ops-capitalize { text-transform: capitalize; }

/* Display */
.ops-hidden { display: none; }
.ops-block { display: block; }

/* Page Break Control */
.ops-page-break-before { page-break-before: always; }
.ops-page-break-after { page-break-after: always; }
.ops-avoid-break { page-break-inside: avoid; }

/* Print Colors */
@media print {
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
}
```

---

# REPORT SPECIFICATIONS

---

## 📊 REPORT 1: Statement of Financial Position (Balance Sheet)

### Report ID: `OPS-FIN-001`
### Priority: Critical
### Category: Financial Intelligence Engine

---

### Purpose
Present the company's financial position at a specific point in time, showing the balance between assets, equity, and liabilities.

### Data Requirements

```python
class BalanceSheetData:
    # Header Info
    company_name: str
    report_date: date
    currency_code: str
    currency_scale: str  # e.g., "'000" or "millions"
    comparative_date: date  # Prior period
    
    # Assets
    non_current_assets: List[AccountLine]
    current_assets: List[AccountLine]
    
    # Equity
    equity_items: List[AccountLine]
    
    # Liabilities
    non_current_liabilities: List[AccountLine]
    current_liabilities: List[AccountLine]
    
    # Calculated
    total_non_current_assets: Decimal
    total_current_assets: Decimal
    total_assets: Decimal
    total_equity: Decimal
    total_non_current_liabilities: Decimal
    total_current_liabilities: Decimal
    total_liabilities: Decimal
    total_equity_and_liabilities: Decimal
    
    # Validation
    is_balanced: bool  # assets == equity + liabilities

class AccountLine:
    code: str
    name: str
    note_ref: Optional[int]
    current_balance: Decimal
    prior_balance: Decimal
    indent_level: int  # 0, 1, 2, 3
```

### Layout: Two-Column Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    [ODOO COMPANY HEADER]                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Consolidated Statement of Financial Position                       │
│  ════════════════════════════════════════════                       │
│  BALANCE SHEET                                                      │
│  As at 31 December 2024                    Expressed in QAR '000    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │   Assets          548,840    =    Equity     440,950        │   │
│  │                              +    Liabilities 107,890   ✓   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │ ASSETS                   │  │ EQUITY & LIABILITIES         │   │
│  ├──────────────────────────┤  ├──────────────────────────────┤   │
│  │                          │  │                              │   │
│  │ NON-CURRENT ASSETS       │  │ SHAREHOLDERS' EQUITY         │   │
│  │   PPE              5  XX │  │   Share Capital        14 XX │   │
│  │   Intangibles      6  XX │  │   Legal Reserve        15 XX │   │
│  │   Investments      7  XX │  │   Retained Earnings       XX │   │
│  │ ─────────────────────────│  │ ─────────────────────────────│   │
│  │ Total Non-Current     XX │  │ Total Equity              XX │   │
│  │                          │  │                              │   │
│  │ CURRENT ASSETS           │  │ NON-CURRENT LIABILITIES      │   │
│  │   Inventories     10  XX │  │   Long-term Debt       16 XX │   │
│  │   Receivables     11  XX │  │   Provisions           17 XX │   │
│  │   Cash            12  XX │  │ ─────────────────────────────│   │
│  │ ─────────────────────────│  │ Total Non-Current         XX │   │
│  │ Total Current         XX │  │                              │   │
│  │                          │  │ CURRENT LIABILITIES          │   │
│  │                          │  │   Payables             18 XX │   │
│  │                          │  │   Short-term Debt      19 XX │   │
│  │                          │  │ ─────────────────────────────│   │
│  │                          │  │ Total Current             XX │   │
│  │                          │  │                              │   │
│  ├══════════════════════════┤  ├══════════════════════════════┤   │
│  │ TOTAL ASSETS          XX │  │ TOTAL EQUITY & LIAB.      XX │   │
│  └──────────────────────────┘  └──────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  _______________    _______________    _______________      │   │
│  │  Chairman           CEO                CFO                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  The accompanying notes form an integral part of these statements.  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    [ODOO COMPANY FOOTER]                            │
└─────────────────────────────────────────────────────────────────────┘
```

### QWeb Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="ops_report_balance_sheet">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="ops_reports.ops_report_balance_sheet_document"/>
            </t>
        </t>
    </template>
    
    <template id="ops_report_balance_sheet_document">
        <t t-call="web.external_layout">
            <div class="ops-financial-report ops-balance-sheet">
                
                <!-- Report Title Block -->
                <div class="ops-report-title-block">
                    <div class="ops-document-type">
                        Consolidated Statement of Financial Position
                    </div>
                    <h1 class="ops-report-title">BALANCE SHEET</h1>
                    <div class="ops-report-meta">
                        <span class="ops-period">
                            As at <t t-esc="doc.date_to.strftime('%d %B %Y')"/>
                        </span>
                        <span class="ops-currency">
                            Expressed in <t t-esc="doc.company_id.currency_id.name"/>
                            <t t-if="doc.currency_scale"> '<t t-esc="doc.currency_scale"/></t>
                        </span>
                    </div>
                </div>
                
                <!-- Equation Summary -->
                <div class="ops-equation-block">
                    <div class="ops-equation-item">
                        <span class="ops-equation-label">Assets</span>
                        <span class="ops-equation-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_assets)"/>
                        </span>
                    </div>
                    <span class="ops-equation-operator">=</span>
                    <div class="ops-equation-item">
                        <span class="ops-equation-label">Equity</span>
                        <span class="ops-equation-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_equity)"/>
                        </span>
                    </div>
                    <span class="ops-equation-operator">+</span>
                    <div class="ops-equation-item">
                        <span class="ops-equation-label">Liabilities</span>
                        <span class="ops-equation-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_liabilities)"/>
                        </span>
                    </div>
                    <div class="ops-equation-status">
                        <t t-if="doc.is_balanced">
                            <span class="ops-status-icon">✓</span>
                            <span class="ops-status-text">Balanced</span>
                        </t>
                        <t t-else="">
                            <span class="ops-status-icon ops-error">✗</span>
                            <span class="ops-status-text ops-error">Unbalanced</span>
                        </t>
                    </div>
                </div>
                
                <!-- Two Column Layout -->
                <div class="ops-two-column-layout">
                    
                    <!-- LEFT COLUMN: ASSETS -->
                    <div class="ops-column ops-column-left">
                        <div class="ops-section-header">Assets</div>
                        
                        <!-- Column Headers -->
                        <table class="ops-data-table">
                            <thead>
                                <tr>
                                    <th class="ops-col-label"></th>
                                    <th class="ops-col-note">Note</th>
                                    <th class="ops-col-amount">
                                        <t t-esc="doc.date_to.strftime('%Y')"/>
                                    </th>
                                    <th class="ops-col-amount ops-col-prior">
                                        <t t-esc="doc.date_from_prior.strftime('%Y')"/>
                                    </th>
                                </tr>
                            </thead>
                        </table>
                        
                        <!-- Non-Current Assets -->
                        <div class="ops-subsection-header">Non-Current Assets</div>
                        <table class="ops-data-table">
                            <tbody>
                                <t t-foreach="doc.non_current_assets" t-as="line">
                                    <tr class="ops-row-item">
                                        <td t-attf-class="ops-col-label ops-indent-#{line.indent_level}">
                                            <t t-esc="line.name"/>
                                        </td>
                                        <td class="ops-col-note">
                                            <t t-if="line.note_ref" t-esc="line.note_ref"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(line.current_balance)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-prior">
                                            <t t-esc="'{:,.0f}'.format(line.prior_balance)"/>
                                        </td>
                                    </tr>
                                </t>
                                <tr class="ops-row-subtotal">
                                    <td class="ops-col-label">Total Non-Current Assets</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_non_current_assets)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_non_current_assets)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- Current Assets -->
                        <div class="ops-subsection-header">Current Assets</div>
                        <table class="ops-data-table">
                            <tbody>
                                <t t-foreach="doc.current_assets" t-as="line">
                                    <tr class="ops-row-item">
                                        <td t-attf-class="ops-col-label ops-indent-#{line.indent_level}">
                                            <t t-esc="line.name"/>
                                        </td>
                                        <td class="ops-col-note">
                                            <t t-if="line.note_ref" t-esc="line.note_ref"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(line.current_balance)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-prior">
                                            <t t-esc="'{:,.0f}'.format(line.prior_balance)"/>
                                        </td>
                                    </tr>
                                </t>
                                <tr class="ops-row-subtotal">
                                    <td class="ops-col-label">Total Current Assets</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_current_assets)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_current_assets)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- Total Assets -->
                        <table class="ops-data-table">
                            <tbody>
                                <tr class="ops-row-total">
                                    <td class="ops-col-label">TOTAL ASSETS</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_assets)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_assets)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- RIGHT COLUMN: EQUITY & LIABILITIES -->
                    <div class="ops-column ops-column-right">
                        <div class="ops-section-header">Equity &amp; Liabilities</div>
                        
                        <!-- Column Headers -->
                        <table class="ops-data-table">
                            <thead>
                                <tr>
                                    <th class="ops-col-label"></th>
                                    <th class="ops-col-note">Note</th>
                                    <th class="ops-col-amount">
                                        <t t-esc="doc.date_to.strftime('%Y')"/>
                                    </th>
                                    <th class="ops-col-amount ops-col-prior">
                                        <t t-esc="doc.date_from_prior.strftime('%Y')"/>
                                    </th>
                                </tr>
                            </thead>
                        </table>
                        
                        <!-- Shareholders' Equity -->
                        <div class="ops-subsection-header">Shareholders' Equity</div>
                        <table class="ops-data-table">
                            <tbody>
                                <t t-foreach="doc.equity_items" t-as="line">
                                    <tr class="ops-row-item">
                                        <td t-attf-class="ops-col-label ops-indent-#{line.indent_level}">
                                            <t t-esc="line.name"/>
                                        </td>
                                        <td class="ops-col-note">
                                            <t t-if="line.note_ref" t-esc="line.note_ref"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(line.current_balance)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-prior">
                                            <t t-esc="'{:,.0f}'.format(line.prior_balance)"/>
                                        </td>
                                    </tr>
                                </t>
                                <tr class="ops-row-subtotal">
                                    <td class="ops-col-label">Total Equity</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_equity)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_equity)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- Non-Current Liabilities -->
                        <div class="ops-subsection-header">Non-Current Liabilities</div>
                        <table class="ops-data-table">
                            <tbody>
                                <t t-foreach="doc.non_current_liabilities" t-as="line">
                                    <tr class="ops-row-item">
                                        <td t-attf-class="ops-col-label ops-indent-#{line.indent_level}">
                                            <t t-esc="line.name"/>
                                        </td>
                                        <td class="ops-col-note">
                                            <t t-if="line.note_ref" t-esc="line.note_ref"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(line.current_balance)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-prior">
                                            <t t-esc="'{:,.0f}'.format(line.prior_balance)"/>
                                        </td>
                                    </tr>
                                </t>
                                <tr class="ops-row-subtotal">
                                    <td class="ops-col-label">Total Non-Current Liabilities</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_non_current_liabilities)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_non_current_liabilities)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- Current Liabilities -->
                        <div class="ops-subsection-header">Current Liabilities</div>
                        <table class="ops-data-table">
                            <tbody>
                                <t t-foreach="doc.current_liabilities" t-as="line">
                                    <tr class="ops-row-item">
                                        <td t-attf-class="ops-col-label ops-indent-#{line.indent_level}">
                                            <t t-esc="line.name"/>
                                        </td>
                                        <td class="ops-col-note">
                                            <t t-if="line.note_ref" t-esc="line.note_ref"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(line.current_balance)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-prior">
                                            <t t-esc="'{:,.0f}'.format(line.prior_balance)"/>
                                        </td>
                                    </tr>
                                </t>
                                <tr class="ops-row-subtotal">
                                    <td class="ops-col-label">Total Current Liabilities</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_current_liabilities)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_current_liabilities)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        
                        <!-- Total Equity & Liabilities -->
                        <table class="ops-data-table">
                            <tbody>
                                <tr class="ops-row-total">
                                    <td class="ops-col-label">TOTAL EQUITY &amp; LIABILITIES</td>
                                    <td class="ops-col-note"></td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(doc.total_equity_and_liabilities)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-prior">
                                        <t t-esc="'{:,.0f}'.format(doc.prior_total_equity_and_liabilities)"/>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Signature Block -->
                <div class="ops-signature-block">
                    <div class="ops-signature-item">
                        <div class="ops-signature-line"></div>
                        <div class="ops-signature-title">Chairman</div>
                    </div>
                    <div class="ops-signature-item">
                        <div class="ops-signature-line"></div>
                        <div class="ops-signature-title">Chief Executive Officer</div>
                    </div>
                    <div class="ops-signature-item">
                        <div class="ops-signature-line"></div>
                        <div class="ops-signature-title">Chief Financial Officer</div>
                    </div>
                </div>
                
                <!-- Notes Reference -->
                <div class="ops-notes-reference">
                    The accompanying notes form an integral part of these financial statements.
                </div>
                
            </div>
        </t>
    </template>
</odoo>
```

### Balance Sheet Specific CSS

```css
/* Two Column Layout for Balance Sheet */
.ops-two-column-layout {
    display: flex;
    gap: var(--space-10);
    margin-top: var(--space-6);
}

.ops-column {
    flex: 1;
    min-width: 0;  /* Prevent overflow */
}

/* Ensure columns align at bottom */
.ops-column-left .ops-row-total,
.ops-column-right .ops-row-total {
    margin-top: auto;
}

/* Print: Avoid breaking columns */
@media print {
    .ops-two-column-layout {
        page-break-inside: avoid;
    }
}
```

---

*[Document continues with Reports 2-18 in subsequent files due to length]*
