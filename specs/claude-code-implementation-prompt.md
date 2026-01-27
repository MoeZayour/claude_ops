# Claude Code Implementation Prompt
## OPS Framework Financial Reports — Meridian Executive Standard

---

## MISSION

Implement a complete financial reporting system for Odoo 19 CE using the **Meridian Executive Standard** design system. The system consists of 18 professional financial reports organized into 4 Intelligence Engines, all sharing a centralized styling architecture.

---

## ARCHITECTURE OVERVIEW

```
ops_matrix_reports/
├── __manifest__.py
├── __init__.py
├── report/
│   ├── __init__.py
│   │
│   ├── # ═══════════════════════════════════════════════════════
│   ├── # MERIDIAN ENGINE (Centralized Master Layout)
│   ├── # ═══════════════════════════════════════════════════════
│   ├── ops_report_layout.xml              # Master CSS + Header/Footer
│   ├── paper_format.xml                   # A4 paper format definition
│   │
│   ├── # ═══════════════════════════════════════════════════════
│   ├── # INTELLIGENCE VIEWS (Report Templates)
│   ├── # ═══════════════════════════════════════════════════════
│   ├── ops_financial_report_templates.xml  # P&L, Balance Sheet, Cash Flow, Trial Balance
│   ├── ops_ledger_report_templates.xml     # General Ledger, Partner Ledger, Aged AR/AP
│   ├── ops_asset_report_templates.xml      # Fixed Assets, Depreciation, CAPEX
│   ├── ops_inventory_report_templates.xml  # Stock Valuation, Dead Stock, Movement
│   ├── ops_treasury_report_templates.xml   # Cash Forecast, PDC Registry
│   ├── ops_consolidated_report_templates.xml # Consolidated Statements
│   │
│   └── report_actions.xml                  # Report action definitions
│
├── models/
│   ├── __init__.py
│   └── report_models.py                    # Abstract report model + mixins
│
├── wizards/
│   ├── __init__.py
│   ├── financial_report_wizard.py
│   ├── ledger_report_wizard.py
│   ├── asset_report_wizard.py
│   ├── inventory_report_wizard.py
│   └── treasury_report_wizard.py
│
└── views/
    └── report_wizard_views.xml
```

---

## PHASE 1: MERIDIAN ENGINE (Master Layout)

### Task 1.1: Create `ops_report_layout.xml`

This is the **centralized master controller**. All 18 reports inherit from this.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ═══════════════════════════════════════════════════════════════════
         MERIDIAN EXECUTIVE STANDARD — MASTER REPORT LAYOUT
         OPS Framework Financial Intelligence Reports
         
         This file contains:
         1. CSS Design Tokens (colors, typography, spacing)
         2. Base report structure
         3. Reusable components (tables, headers, totals)
         
         To change the entire report suite styling, modify this file ONLY.
    ═══════════════════════════════════════════════════════════════════ -->

    <!-- ═══════════════════════════════════════════════════════════════════
         ASSET: MERIDIAN CSS STYLESHEET
    ═══════════════════════════════════════════════════════════════════ -->
    <template id="ops_report_assets">
        <style>
            /* ════════════════════════════════════════════════════════════
               DESIGN TOKENS — MERIDIAN EXECUTIVE STANDARD
               Change these values to rebrand the entire report suite
            ════════════════════════════════════════════════════════════ */
            
            :root {
                /* ─────────────────────────────────────────────────────────
                   PRIMARY BRAND COLORS
                ───────────────────────────────────────────────────────── */
                --ops-black: #1a1a1a;
                --ops-charcoal: #2d2d2d;
                --ops-gold: #c9a962;
                --ops-gold-muted: #a8935a;
                
                /* ─────────────────────────────────────────────────────────
                   SEMANTIC COLORS (Financial Context)
                ───────────────────────────────────────────────────────── */
                --ops-positive: #2d5a3d;      /* Profits, gains */
                --ops-negative: #8b3a3a;       /* Losses, expenses */
                --ops-warning: #8b6914;        /* Attention items */
                
                /* ─────────────────────────────────────────────────────────
                   NEUTRAL SCALE
                ───────────────────────────────────────────────────────── */
                --ops-gray-50: #fafafa;
                --ops-gray-100: #f5f5f5;
                --ops-gray-200: #e5e5e5;
                --ops-gray-300: #d4d4d4;
                --ops-gray-400: #a3a3a3;
                --ops-gray-500: #737373;
                --ops-gray-600: #525252;
                --ops-gray-700: #404040;
                --ops-gray-800: #262626;
                
                /* ─────────────────────────────────────────────────────────
                   TYPOGRAPHY
                ───────────────────────────────────────────────────────── */
                --font-display: Georgia, 'Times New Roman', serif;
                --font-body: 'DejaVu Sans', Arial, Helvetica, sans-serif;
                --font-mono: 'DejaVu Sans Mono', Consolas, monospace;
                
                /* ─────────────────────────────────────────────────────────
                   SPACING (Base unit: 4px)
                ───────────────────────────────────────────────────────── */
                --space-1: 4px;
                --space-2: 8px;
                --space-3: 12px;
                --space-4: 16px;
                --space-5: 20px;
                --space-6: 24px;
                --space-8: 32px;
                --space-10: 40px;
                --space-12: 48px;
            }
            
            /* ════════════════════════════════════════════════════════════
               BASE STYLES
            ════════════════════════════════════════════════════════════ */
            
            .ops-report {
                font-family: var(--font-body);
                font-size: 9pt;
                color: var(--ops-black);
                line-height: 1.4;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            /* ════════════════════════════════════════════════════════════
               TOP ACCENT BAR — The signature Meridian element
            ════════════════════════════════════════════════════════════ */
            
            .ops-accent-bar {
                height: 4px;
                background: linear-gradient(90deg, 
                    var(--ops-black) 0%, 
                    var(--ops-black) 75%, 
                    var(--ops-gold) 75%, 
                    var(--ops-gold) 100%
                );
                margin-bottom: var(--space-8);
            }
            
            /* ════════════════════════════════════════════════════════════
               REPORT TITLE BLOCK
            ════════════════════════════════════════════════════════════ */
            
            .ops-title-block {
                margin-bottom: var(--space-8);
            }
            
            .ops-document-type {
                font-size: 9px;
                color: var(--ops-gray-500);
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-bottom: var(--space-2);
            }
            
            .ops-report-title {
                font-family: var(--font-display);
                font-size: 28pt;
                font-weight: 300;
                color: var(--ops-black);
                letter-spacing: -0.5px;
                margin: 0 0 var(--space-2) 0;
                line-height: 1.1;
            }
            
            .ops-report-meta {
                display: flex;
                justify-content: space-between;
                font-size: 10px;
                color: var(--ops-gray-500);
            }
            
            .ops-report-period {
                font-weight: 500;
                color: var(--ops-gray-600);
            }
            
            .ops-report-currency {
                font-style: italic;
            }
            
            /* ════════════════════════════════════════════════════════════
               ACCOUNTING EQUATION BLOCK (Balance Sheet)
            ════════════════════════════════════════════════════════════ */
            
            .ops-equation-block {
                display: table;
                width: 100%;
                padding: var(--space-5) 0;
                margin: var(--space-6) 0;
                border-top: 1px solid var(--ops-gray-200);
                border-bottom: 1px solid var(--ops-gray-200);
                background: linear-gradient(180deg, var(--ops-gray-50) 0%, white 100%);
                text-align: center;
            }
            
            .ops-equation-inner {
                display: table-row;
            }
            
            .ops-equation-item {
                display: table-cell;
                text-align: center;
                vertical-align: middle;
                padding: 0 var(--space-4);
            }
            
            .ops-equation-label {
                display: block;
                font-size: 8px;
                color: var(--ops-gray-500);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: var(--space-1);
            }
            
            .ops-equation-value {
                font-family: var(--font-display);
                font-size: 18pt;
                font-weight: 600;
                color: var(--ops-black);
            }
            
            .ops-equation-operator {
                display: table-cell;
                font-size: 16pt;
                color: var(--ops-gray-300);
                font-weight: 300;
                vertical-align: middle;
                padding: 0 var(--space-2);
            }
            
            .ops-balanced-badge {
                display: table-cell;
                vertical-align: middle;
                padding-left: var(--space-6);
            }
            
            .ops-balanced-badge-inner {
                display: inline-block;
                padding: var(--space-2) var(--space-4);
                background: rgba(45, 90, 61, 0.08);
                border: 1px solid rgba(45, 90, 61, 0.2);
                border-radius: 4px;
            }
            
            .ops-balanced-badge-inner span {
                color: var(--ops-positive);
                font-size: 10px;
                font-weight: 600;
            }
            
            /* ════════════════════════════════════════════════════════════
               KPI SUMMARY BAR
            ════════════════════════════════════════════════════════════ */
            
            .ops-kpi-bar {
                display: table;
                width: 100%;
                padding: var(--space-4) var(--space-6);
                margin-bottom: var(--space-6);
                background-color: var(--ops-gray-50);
                border: 1px solid var(--ops-gray-200);
            }
            
            .ops-kpi-bar-inner {
                display: table-row;
            }
            
            .ops-kpi-item {
                display: table-cell;
                text-align: center;
                vertical-align: middle;
                padding: 0 var(--space-4);
                border-right: 1px solid var(--ops-gray-200);
            }
            
            .ops-kpi-item:last-child {
                border-right: none;
            }
            
            .ops-kpi-label {
                display: block;
                font-size: 7px;
                color: var(--ops-gray-500);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: var(--space-1);
            }
            
            .ops-kpi-value {
                font-family: var(--font-display);
                font-size: 14pt;
                font-weight: 600;
                color: var(--ops-black);
            }
            
            /* ════════════════════════════════════════════════════════════
               SECTION HEADERS
            ════════════════════════════════════════════════════════════ */
            
            .ops-section-header {
                font-size: 10px;
                font-weight: 600;
                color: var(--ops-black);
                text-transform: uppercase;
                letter-spacing: 2px;
                padding-bottom: var(--space-2);
                border-bottom: 2px solid var(--ops-black);
                margin-top: var(--space-6);
                margin-bottom: var(--space-4);
            }
            
            .ops-subsection-header {
                font-size: 8px;
                font-weight: 600;
                color: var(--ops-gray-600);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: var(--space-4);
                margin-bottom: var(--space-2);
            }
            
            /* ════════════════════════════════════════════════════════════
               DATA TABLES — The Core Component
            ════════════════════════════════════════════════════════════ */
            
            .ops-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 9pt;
            }
            
            /* Column Headers */
            .ops-table thead th {
                font-size: 7px;
                font-weight: 600;
                color: var(--ops-gray-500);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: var(--space-2) var(--space-3);
                border-bottom: 1px solid var(--ops-gray-300);
                text-align: left;
                vertical-align: bottom;
            }
            
            .ops-table thead th.ops-col-amount,
            .ops-table thead th.ops-col-note {
                text-align: right;
            }
            
            .ops-table thead th.ops-col-note {
                text-align: center;
                width: 35px;
            }
            
            .ops-table thead th.ops-col-amount {
                width: 75px;
            }
            
            /* Data Cells */
            .ops-table tbody td {
                padding: var(--space-2) var(--space-3);
                border-bottom: 1px solid var(--ops-gray-100);
                vertical-align: middle;
            }
            
            .ops-table tbody td.ops-col-amount {
                text-align: right;
                font-family: var(--font-display);
                font-variant-numeric: tabular-nums;
            }
            
            .ops-table tbody td.ops-col-note {
                text-align: center;
                font-size: 7px;
                color: var(--ops-gray-400);
            }
            
            .ops-table tbody td.ops-col-code {
                font-family: var(--font-mono);
                font-size: 7px;
                color: var(--ops-gray-500);
            }
            
            /* Indentation */
            .ops-indent-1 { padding-left: var(--space-6) !important; }
            .ops-indent-2 { padding-left: var(--space-10) !important; color: var(--ops-gray-600); }
            .ops-indent-3 { padding-left: var(--space-12) !important; color: var(--ops-gray-500); font-style: italic; }
            
            /* Value States */
            .ops-value-zero { color: var(--ops-gray-300); }
            .ops-value-prior { color: var(--ops-gray-400); }
            .ops-value-positive { color: var(--ops-positive); }
            .ops-value-negative { color: var(--ops-negative); }
            
            /* ════════════════════════════════════════════════════════════
               ROW TYPES
            ════════════════════════════════════════════════════════════ */
            
            /* Standard Row */
            .ops-row-item td {
                font-weight: 400;
            }
            
            /* Subtotal Row */
            .ops-row-subtotal td {
                font-weight: 600;
                background-color: var(--ops-gray-50);
                border-top: 1px solid var(--ops-gray-300);
                padding-top: var(--space-3);
                padding-bottom: var(--space-3);
            }
            
            /* Major Total (EBIT, Gross Profit) */
            .ops-row-major-total td {
                font-weight: 700;
                background-color: var(--ops-gray-50);
                border-top: 2px solid var(--ops-black);
                border-bottom: 2px solid var(--ops-black);
                padding: var(--space-3);
            }
            
            /* Grand Total (Final row - inverted) */
            .ops-row-grand-total td {
                font-weight: 700;
                font-size: 10pt;
                background-color: var(--ops-black);
                color: white;
                border: none;
                padding: var(--space-4) var(--space-3);
            }
            
            .ops-row-grand-total td.ops-col-amount {
                font-size: 11pt;
            }
            
            /* Section Header Row (inline) */
            .ops-row-section-header td {
                font-size: 8px;
                font-weight: 600;
                color: var(--ops-gray-600);
                text-transform: uppercase;
                letter-spacing: 1px;
                padding-top: var(--space-5);
                padding-bottom: var(--space-2);
                border-bottom: none;
                background: transparent;
            }
            
            /* Margin Row (percentages) */
            .ops-row-margin td {
                font-size: 8px;
                font-style: italic;
                color: var(--ops-gray-500);
                padding-top: var(--space-1);
                padding-bottom: var(--space-4);
                border-bottom: none;
            }
            
            /* ════════════════════════════════════════════════════════════
               TWO-COLUMN LAYOUT (Balance Sheet)
            ════════════════════════════════════════════════════════════ */
            
            .ops-two-column {
                display: table;
                width: 100%;
                table-layout: fixed;
            }
            
            .ops-column {
                display: table-cell;
                width: 50%;
                vertical-align: top;
                padding-right: var(--space-5);
            }
            
            .ops-column:last-child {
                padding-right: 0;
                padding-left: var(--space-5);
            }
            
            /* ════════════════════════════════════════════════════════════
               SIGNATURE BLOCK
            ════════════════════════════════════════════════════════════ */
            
            .ops-signature-block {
                display: table;
                width: 100%;
                margin-top: var(--space-12);
                padding-top: var(--space-6);
                border-top: 1px solid var(--ops-gray-200);
            }
            
            .ops-signature-row {
                display: table-row;
            }
            
            .ops-signature-item {
                display: table-cell;
                width: 33.33%;
                padding: 0 var(--space-4);
            }
            
            .ops-signature-line {
                border-bottom: 1px solid var(--ops-black);
                height: 36px;
                margin-bottom: var(--space-2);
            }
            
            .ops-signature-title {
                font-size: 7px;
                font-weight: 600;
                color: var(--ops-gray-600);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* ════════════════════════════════════════════════════════════
               NOTES REFERENCE
            ════════════════════════════════════════════════════════════ */
            
            .ops-notes-reference {
                font-size: 7px;
                color: var(--ops-gray-400);
                font-style: italic;
                margin-top: var(--space-8);
                padding-top: var(--space-4);
                border-top: 1px solid var(--ops-gray-100);
            }
            
            /* ════════════════════════════════════════════════════════════
               AGING DISTRIBUTION BARS
            ════════════════════════════════════════════════════════════ */
            
            .ops-aging-bars {
                padding: var(--space-4);
                background-color: var(--ops-gray-50);
                border: 1px solid var(--ops-gray-200);
                margin-bottom: var(--space-6);
            }
            
            .ops-aging-bar-row {
                display: table;
                width: 100%;
                margin-bottom: var(--space-2);
            }
            
            .ops-aging-bar-row:last-child {
                margin-bottom: 0;
            }
            
            .ops-aging-bar-label {
                display: table-cell;
                width: 80px;
                font-size: 8px;
                font-weight: 500;
                color: var(--ops-gray-600);
                vertical-align: middle;
            }
            
            .ops-aging-bar-container {
                display: table-cell;
                vertical-align: middle;
                padding: 0 var(--space-3);
            }
            
            .ops-aging-bar-track {
                height: 16px;
                background-color: var(--ops-gray-200);
                border-radius: 2px;
                overflow: hidden;
            }
            
            .ops-aging-bar-fill {
                height: 100%;
                background-color: var(--ops-gray-500);
                border-radius: 2px;
            }
            
            .ops-aging-bar-fill.ops-risk-warning {
                background-color: var(--ops-warning);
            }
            
            .ops-aging-bar-fill.ops-risk-danger {
                background-color: var(--ops-negative);
            }
            
            .ops-aging-bar-amount {
                display: table-cell;
                width: 70px;
                text-align: right;
                font-family: var(--font-display);
                font-size: 9px;
                font-weight: 500;
                vertical-align: middle;
            }
            
            .ops-aging-bar-pct {
                display: table-cell;
                width: 50px;
                text-align: right;
                font-size: 8px;
                color: var(--ops-gray-500);
                vertical-align: middle;
            }
            
            /* ════════════════════════════════════════════════════════════
               RISK BADGES
            ════════════════════════════════════════════════════════════ */
            
            .ops-risk-badge {
                display: inline-block;
                padding: var(--space-2) var(--space-4);
                font-size: 9px;
                font-weight: 600;
                border-radius: 4px;
            }
            
            .ops-risk-badge.ops-risk-low {
                background-color: rgba(45, 90, 61, 0.1);
                color: var(--ops-positive);
            }
            
            .ops-risk-badge.ops-risk-medium {
                background-color: rgba(139, 105, 20, 0.1);
                color: var(--ops-warning);
            }
            
            .ops-risk-badge.ops-risk-high {
                background-color: rgba(139, 58, 58, 0.1);
                color: var(--ops-negative);
            }
            
            /* ════════════════════════════════════════════════════════════
               VARIANCE COLUMN
            ════════════════════════════════════════════════════════════ */
            
            .ops-col-variance {
                width: 55px;
                text-align: right;
                font-size: 8px;
            }
            
            .ops-var-positive {
                color: var(--ops-positive);
            }
            
            .ops-var-negative {
                color: var(--ops-negative);
            }
            
            /* ════════════════════════════════════════════════════════════
               PAGE BREAK CONTROL
            ════════════════════════════════════════════════════════════ */
            
            .ops-page-break-before {
                page-break-before: always;
            }
            
            .ops-page-break-after {
                page-break-after: always;
            }
            
            .ops-avoid-break {
                page-break-inside: avoid;
            }
            
            /* ════════════════════════════════════════════════════════════
               PRINT OPTIMIZATION
            ════════════════════════════════════════════════════════════ */
            
            @media print {
                .ops-report {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
                
                .ops-row-grand-total td {
                    background-color: var(--ops-black) !important;
                    color: white !important;
                }
            }
        </style>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════
         BASE REPORT DOCUMENT TEMPLATE
         All reports inherit from this structure
    ═══════════════════════════════════════════════════════════════════ -->
    <template id="ops_report_base_document">
        <t t-call="web.external_layout">
            <t t-call="ops_matrix_reports.ops_report_assets"/>
            
            <div class="ops-report">
                <!-- Top Accent Bar -->
                <div class="ops-accent-bar"/>
                
                <!-- Report Content (overridden by child templates) -->
                <t t-raw="0"/>
                
                <!-- Notes Reference (optional) -->
                <t t-if="show_notes_reference">
                    <div class="ops-notes-reference">
                        The accompanying notes form an integral part of these financial statements.
                    </div>
                </t>
            </div>
        </t>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════
         REUSABLE COMPONENTS
    ═══════════════════════════════════════════════════════════════════ -->
    
    <!-- Title Block Component -->
    <template id="ops_component_title_block">
        <div class="ops-title-block">
            <div class="ops-document-type">
                <t t-esc="document_type"/>
            </div>
            <h1 class="ops-report-title">
                <t t-esc="report_title"/>
            </h1>
            <div class="ops-report-meta">
                <span class="ops-report-period">
                    <t t-esc="period_label"/>
                </span>
                <span class="ops-report-currency">
                    Expressed in <t t-esc="currency_name"/>
                    <t t-if="currency_scale"> '<t t-esc="currency_scale"/></t>
                </span>
            </div>
        </div>
    </template>
    
    <!-- Signature Block Component -->
    <template id="ops_component_signature_block">
        <div class="ops-signature-block">
            <div class="ops-signature-row">
                <t t-foreach="signatures" t-as="sig">
                    <div class="ops-signature-item">
                        <div class="ops-signature-line"/>
                        <div class="ops-signature-title">
                            <t t-esc="sig"/>
                        </div>
                    </div>
                </t>
            </div>
        </div>
    </template>

</odoo>
```

### Task 1.2: Create `paper_format.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- A4 Paper Format for OPS Reports -->
    <record id="ops_paperformat_a4" model="report.paperformat">
        <field name="name">OPS A4 Executive</field>
        <field name="default" eval="False"/>
        <field name="format">A4</field>
        <field name="page_height">0</field>
        <field name="page_width">0</field>
        <field name="orientation">Portrait</field>
        <field name="margin_top">20</field>
        <field name="margin_bottom">25</field>
        <field name="margin_left">15</field>
        <field name="margin_right">15</field>
        <field name="header_line" eval="False"/>
        <field name="header_spacing">15</field>
        <field name="dpi">96</field>
    </record>
</odoo>
```

---

## PHASE 2: FINANCIAL INTELLIGENCE ENGINE

### Task 2.1: Create `ops_financial_report_templates.xml`

Contains: Balance Sheet, P&L, Cash Flow, Trial Balance, Executive P&L

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ═══════════════════════════════════════════════════════════════════
         FINANCIAL INTELLIGENCE ENGINE
         Reports: Balance Sheet, P&L, Cash Flow, Trial Balance, Executive P&L
    ═══════════════════════════════════════════════════════════════════ -->

    <!-- ═══════════════════════════════════════════════════════════════════
         REPORT 1: BALANCE SHEET
    ═══════════════════════════════════════════════════════════════════ -->
    <template id="ops_report_balance_sheet">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="ops_matrix_reports.ops_report_balance_sheet_document"/>
            </t>
        </t>
    </template>
    
    <template id="ops_report_balance_sheet_document">
        <t t-call="ops_matrix_reports.ops_report_base_document">
            <t t-set="show_notes_reference" t-value="True"/>
            
            <!-- Title Block -->
            <t t-call="ops_matrix_reports.ops_component_title_block">
                <t t-set="document_type">Consolidated Statement of Financial Position</t>
                <t t-set="report_title">BALANCE SHEET</t>
                <t t-set="period_label">As at <t t-esc="doc.date_to.strftime('%d %B %Y')"/></t>
                <t t-set="currency_name" t-value="doc.company_id.currency_id.name"/>
                <t t-set="currency_scale" t-value="doc.currency_scale"/>
            </t>
            
            <!-- Accounting Equation -->
            <div class="ops-equation-block">
                <div class="ops-equation-inner">
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
                    <div class="ops-balanced-badge">
                        <div class="ops-balanced-badge-inner">
                            <t t-if="doc.is_balanced">
                                <span>✓ Balanced</span>
                            </t>
                            <t t-else="">
                                <span style="color: var(--ops-negative);">✗ Unbalanced</span>
                            </t>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Two Column Layout -->
            <div class="ops-two-column">
                <!-- LEFT: ASSETS -->
                <div class="ops-column">
                    <div class="ops-section-header">Assets</div>
                    
                    <table class="ops-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="ops-col-note">Note</th>
                                <th class="ops-col-amount"><t t-esc="doc.date_to.strftime('%Y')"/></th>
                                <th class="ops-col-amount"><t t-esc="doc.prior_date.strftime('%Y')"/></th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Non-Current Assets -->
                            <tr class="ops-row-section-header">
                                <td colspan="4">Non-Current Assets</td>
                            </tr>
                            <t t-foreach="doc.non_current_assets" t-as="line">
                                <tr class="ops-row-item">
                                    <td class="ops-indent-1"><t t-esc="line.name"/></td>
                                    <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                                    <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_balance)"/></td>
                                    <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_balance)"/></td>
                                </tr>
                            </t>
                            <tr class="ops-row-subtotal">
                                <td>Total Non-Current Assets</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_non_current_assets)"/></td>
                                <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_non_current_assets)"/></td>
                            </tr>
                            
                            <!-- Current Assets -->
                            <tr class="ops-row-section-header">
                                <td colspan="4">Current Assets</td>
                            </tr>
                            <t t-foreach="doc.current_assets" t-as="line">
                                <tr class="ops-row-item">
                                    <td class="ops-indent-1"><t t-esc="line.name"/></td>
                                    <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                                    <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_balance)"/></td>
                                    <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_balance)"/></td>
                                </tr>
                            </t>
                            <tr class="ops-row-subtotal">
                                <td>Total Current Assets</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_current_assets)"/></td>
                                <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_current_assets)"/></td>
                            </tr>
                            
                            <!-- TOTAL ASSETS -->
                            <tr class="ops-row-grand-total">
                                <td style="text-transform: uppercase; letter-spacing: 1px;">Total Assets</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_assets)"/></td>
                                <td class="ops-col-amount" style="color: var(--ops-gray-400);"><t t-esc="'{:,.0f}'.format(doc.prior_total_assets)"/></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- RIGHT: EQUITY & LIABILITIES -->
                <div class="ops-column">
                    <div class="ops-section-header">Equity &amp; Liabilities</div>
                    
                    <table class="ops-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="ops-col-note">Note</th>
                                <th class="ops-col-amount"><t t-esc="doc.date_to.strftime('%Y')"/></th>
                                <th class="ops-col-amount"><t t-esc="doc.prior_date.strftime('%Y')"/></th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Shareholders' Equity -->
                            <tr class="ops-row-section-header">
                                <td colspan="4">Shareholders' Equity</td>
                            </tr>
                            <t t-foreach="doc.equity_items" t-as="line">
                                <tr class="ops-row-item">
                                    <td class="ops-indent-1"><t t-esc="line.name"/></td>
                                    <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                                    <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_balance)"/></td>
                                    <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_balance)"/></td>
                                </tr>
                            </t>
                            <tr class="ops-row-subtotal">
                                <td>Total Equity</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_equity)"/></td>
                                <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_equity)"/></td>
                            </tr>
                            
                            <!-- Non-Current Liabilities -->
                            <tr class="ops-row-section-header">
                                <td colspan="4">Non-Current Liabilities</td>
                            </tr>
                            <t t-foreach="doc.non_current_liabilities" t-as="line">
                                <tr class="ops-row-item">
                                    <td class="ops-indent-1"><t t-esc="line.name"/></td>
                                    <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                                    <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_balance)"/></td>
                                    <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_balance)"/></td>
                                </tr>
                            </t>
                            <tr class="ops-row-subtotal">
                                <td>Total Non-Current Liabilities</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_non_current_liabilities)"/></td>
                                <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_non_current_liabilities)"/></td>
                            </tr>
                            
                            <!-- Current Liabilities -->
                            <tr class="ops-row-section-header">
                                <td colspan="4">Current Liabilities</td>
                            </tr>
                            <t t-foreach="doc.current_liabilities" t-as="line">
                                <tr class="ops-row-item">
                                    <td class="ops-indent-1"><t t-esc="line.name"/></td>
                                    <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                                    <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_balance)"/></td>
                                    <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_balance)"/></td>
                                </tr>
                            </t>
                            <tr class="ops-row-subtotal">
                                <td>Total Current Liabilities</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_current_liabilities)"/></td>
                                <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_current_liabilities)"/></td>
                            </tr>
                            
                            <!-- TOTAL EQUITY & LIABILITIES -->
                            <tr class="ops-row-grand-total">
                                <td style="text-transform: uppercase; letter-spacing: 1px; font-size: 8pt;">Total Equity &amp; Liabilities</td>
                                <td class="ops-col-note"></td>
                                <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_equity_and_liabilities)"/></td>
                                <td class="ops-col-amount" style="color: var(--ops-gray-400);"><t t-esc="'{:,.0f}'.format(doc.prior_total_equity_and_liabilities)"/></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Signature Block -->
            <t t-call="ops_matrix_reports.ops_component_signature_block">
                <t t-set="signatures" t-value="['Chairman', 'Chief Executive Officer', 'Chief Financial Officer']"/>
            </t>
        </t>
    </template>

    <!-- ═══════════════════════════════════════════════════════════════════
         REPORT 2: PROFIT & LOSS STATEMENT
    ═══════════════════════════════════════════════════════════════════ -->
    <template id="ops_report_profit_loss">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="ops_matrix_reports.ops_report_profit_loss_document"/>
            </t>
        </t>
    </template>
    
    <template id="ops_report_profit_loss_document">
        <t t-call="ops_matrix_reports.ops_report_base_document">
            <t t-set="show_notes_reference" t-value="True"/>
            
            <!-- Title Block -->
            <t t-call="ops_matrix_reports.ops_component_title_block">
                <t t-set="document_type">Statement of Comprehensive Income</t>
                <t t-set="report_title">PROFIT &amp; LOSS</t>
                <t t-set="period_label">For the Year Ended <t t-esc="doc.date_to.strftime('%d %B %Y')"/></t>
                <t t-set="currency_name" t-value="doc.company_id.currency_id.name"/>
                <t t-set="currency_scale" t-value="doc.currency_scale"/>
            </t>
            
            <!-- KPI Summary Bar -->
            <div class="ops-kpi-bar">
                <div class="ops-kpi-bar-inner">
                    <div class="ops-kpi-item">
                        <span class="ops-kpi-label">Revenue</span>
                        <span class="ops-kpi-value"><t t-esc="'{:,.0f}'.format(doc.total_revenue)"/></span>
                    </div>
                    <div class="ops-kpi-item">
                        <span class="ops-kpi-label">Gross Margin</span>
                        <span class="ops-kpi-value"><t t-esc="'{:.1f}%'.format(doc.gross_margin_pct)"/></span>
                    </div>
                    <div class="ops-kpi-item">
                        <span class="ops-kpi-label">Net Profit</span>
                        <span class="ops-kpi-value"><t t-esc="'{:,.0f}'.format(doc.net_profit)"/></span>
                    </div>
                    <div class="ops-kpi-item">
                        <span class="ops-kpi-label">Net Margin</span>
                        <span class="ops-kpi-value"><t t-esc="'{:.1f}%'.format(doc.net_profit_margin_pct)"/></span>
                    </div>
                </div>
            </div>
            
            <!-- Main P&L Table -->
            <table class="ops-table">
                <thead>
                    <tr>
                        <th></th>
                        <th class="ops-col-note">Note</th>
                        <th class="ops-col-amount"><t t-esc="doc.date_to.strftime('%Y')"/></th>
                        <th class="ops-col-amount"><t t-esc="doc.prior_date_to.strftime('%Y')"/></th>
                        <th class="ops-col-variance">Var %</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- REVENUE -->
                    <tr class="ops-row-section-header">
                        <td colspan="5">Revenue</td>
                    </tr>
                    <t t-foreach="doc.revenue_lines" t-as="line">
                        <tr class="ops-row-item">
                            <td class="ops-indent-1"><t t-esc="line.name"/></td>
                            <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                            <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(line.current_amount)"/></td>
                            <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(line.prior_amount)"/></td>
                            <td t-attf-class="ops-col-variance #{('ops-var-positive' if line.variance_pct &gt;= 0 else 'ops-var-negative')}">
                                <t t-if="line.variance_pct &gt;= 0"><t t-esc="'{:.1f}%'.format(line.variance_pct)"/></t>
                                <t t-else="">(<t t-esc="'{:.1f}%'.format(abs(line.variance_pct))"/>)</t>
                            </td>
                        </tr>
                    </t>
                    <tr class="ops-row-subtotal">
                        <td>Total Revenue</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.total_revenue)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_total_revenue)"/></td>
                        <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(doc.revenue_variance_pct)"/></td>
                    </tr>
                    
                    <!-- COST OF SALES -->
                    <tr class="ops-row-section-header">
                        <td colspan="5">Cost of Sales</td>
                    </tr>
                    <t t-foreach="doc.cost_of_sales_lines" t-as="line">
                        <tr class="ops-row-item">
                            <td class="ops-indent-1"><t t-esc="line.name"/></td>
                            <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                            <td class="ops-col-amount">(<t t-esc="'{:,.0f}'.format(abs(line.current_amount))"/>)</td>
                            <td class="ops-col-amount ops-value-prior">(<t t-esc="'{:,.0f}'.format(abs(line.prior_amount))"/>)</td>
                            <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(line.variance_pct)"/></td>
                        </tr>
                    </t>
                    <tr class="ops-row-subtotal">
                        <td>Total Cost of Sales</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount">(<t t-esc="'{:,.0f}'.format(abs(doc.total_cost_of_sales))"/>)</td>
                        <td class="ops-col-amount ops-value-prior">(<t t-esc="'{:,.0f}'.format(abs(doc.prior_total_cost_of_sales))"/>)</td>
                        <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(doc.cos_variance_pct)"/></td>
                    </tr>
                    
                    <!-- GROSS PROFIT -->
                    <tr class="ops-row-major-total">
                        <td>GROSS PROFIT</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.gross_profit)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_gross_profit)"/></td>
                        <td class="ops-col-variance ops-var-positive"><t t-esc="'{:.1f}%'.format(doc.gross_profit_variance_pct)"/></td>
                    </tr>
                    <tr class="ops-row-margin">
                        <td class="ops-indent-1">Gross Margin</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:.1f}%'.format(doc.gross_margin_pct)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:.1f}%'.format(doc.prior_gross_margin_pct)"/></td>
                        <td class="ops-col-variance"></td>
                    </tr>
                    
                    <!-- OPERATING EXPENSES -->
                    <tr class="ops-row-section-header">
                        <td colspan="5">Operating Expenses</td>
                    </tr>
                    <t t-foreach="doc.operating_expense_lines" t-as="line">
                        <tr class="ops-row-item">
                            <td class="ops-indent-1"><t t-esc="line.name"/></td>
                            <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                            <td class="ops-col-amount">(<t t-esc="'{:,.0f}'.format(abs(line.current_amount))"/>)</td>
                            <td class="ops-col-amount ops-value-prior">(<t t-esc="'{:,.0f}'.format(abs(line.prior_amount))"/>)</td>
                            <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(line.variance_pct)"/></td>
                        </tr>
                    </t>
                    <tr class="ops-row-subtotal">
                        <td>Total Operating Expenses</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount">(<t t-esc="'{:,.0f}'.format(abs(doc.total_operating_expenses))"/>)</td>
                        <td class="ops-col-amount ops-value-prior">(<t t-esc="'{:,.0f}'.format(abs(doc.prior_total_operating_expenses))"/>)</td>
                        <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(doc.opex_variance_pct)"/></td>
                    </tr>
                    
                    <!-- OPERATING PROFIT -->
                    <tr class="ops-row-major-total">
                        <td>OPERATING PROFIT (EBIT)</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.operating_profit)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_operating_profit)"/></td>
                        <td class="ops-col-variance ops-var-positive"><t t-esc="'{:.1f}%'.format(doc.ebit_variance_pct)"/></td>
                    </tr>
                    <tr class="ops-row-margin">
                        <td class="ops-indent-1">Operating Margin</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:.1f}%'.format(doc.operating_margin_pct)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:.1f}%'.format(doc.prior_operating_margin_pct)"/></td>
                        <td class="ops-col-variance"></td>
                    </tr>
                    
                    <!-- FINANCE COSTS -->
                    <tr class="ops-row-section-header">
                        <td colspan="5">Finance Costs</td>
                    </tr>
                    <t t-foreach="doc.finance_lines" t-as="line">
                        <tr class="ops-row-item">
                            <td class="ops-indent-1"><t t-esc="line.name"/></td>
                            <td class="ops-col-note"><t t-if="line.note_ref" t-esc="line.note_ref"/></td>
                            <td class="ops-col-amount">
                                <t t-if="line.current_amount &lt; 0">(<t t-esc="'{:,.0f}'.format(abs(line.current_amount))"/>)</t>
                                <t t-else=""><t t-esc="'{:,.0f}'.format(line.current_amount)"/></t>
                            </td>
                            <td class="ops-col-amount ops-value-prior">
                                <t t-if="line.prior_amount &lt; 0">(<t t-esc="'{:,.0f}'.format(abs(line.prior_amount))"/>)</t>
                                <t t-else=""><t t-esc="'{:,.0f}'.format(line.prior_amount)"/></t>
                            </td>
                            <td class="ops-col-variance"><t t-esc="'{:.1f}%'.format(line.variance_pct)"/></td>
                        </tr>
                    </t>
                    <tr class="ops-row-subtotal">
                        <td>Net Finance Costs</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount">(<t t-esc="'{:,.0f}'.format(abs(doc.net_finance_cost))"/>)</td>
                        <td class="ops-col-amount ops-value-prior">(<t t-esc="'{:,.0f}'.format(abs(doc.prior_net_finance_cost))"/>)</td>
                        <td class="ops-col-variance"></td>
                    </tr>
                    
                    <!-- PROFIT BEFORE TAX -->
                    <tr class="ops-row-major-total">
                        <td>PROFIT BEFORE TAX</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.profit_before_tax)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:,.0f}'.format(doc.prior_profit_before_tax)"/></td>
                        <td class="ops-col-variance ops-var-positive"><t t-esc="'{:.1f}%'.format(doc.pbt_variance_pct)"/></td>
                    </tr>
                    
                    <!-- TAX -->
                    <tr class="ops-row-item">
                        <td class="ops-indent-1">Income Tax Expense</td>
                        <td class="ops-col-note">13</td>
                        <td class="ops-col-amount">
                            <t t-if="doc.tax_expense">(<t t-esc="'{:,.0f}'.format(abs(doc.tax_expense))"/>)</t>
                            <t t-else=""><span class="ops-value-zero">—</span></t>
                        </td>
                        <td class="ops-col-amount ops-value-prior">
                            <t t-if="doc.prior_tax_expense">(<t t-esc="'{:,.0f}'.format(abs(doc.prior_tax_expense))"/>)</t>
                            <t t-else=""><span class="ops-value-zero">—</span></t>
                        </td>
                        <td class="ops-col-variance"></td>
                    </tr>
                    
                    <!-- NET PROFIT -->
                    <tr class="ops-row-grand-total">
                        <td style="text-transform: uppercase; letter-spacing: 1px;">Net Profit for the Period</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount"><t t-esc="'{:,.0f}'.format(doc.net_profit)"/></td>
                        <td class="ops-col-amount" style="color: var(--ops-gray-400);"><t t-esc="'{:,.0f}'.format(doc.prior_net_profit)"/></td>
                        <td class="ops-col-variance" style="color: white;"><t t-esc="'{:.1f}%'.format(doc.net_profit_variance_pct)"/></td>
                    </tr>
                    <tr class="ops-row-margin" style="background: var(--ops-gray-100);">
                        <td style="font-weight: 600; font-style: normal; color: var(--ops-black);">Net Profit Margin</td>
                        <td class="ops-col-note"></td>
                        <td class="ops-col-amount" style="font-weight: 600; font-style: normal; color: var(--ops-black);"><t t-esc="'{:.1f}%'.format(doc.net_profit_margin_pct)"/></td>
                        <td class="ops-col-amount ops-value-prior"><t t-esc="'{:.1f}%'.format(doc.prior_net_profit_margin_pct)"/></td>
                        <td class="ops-col-variance"></td>
                    </tr>
                </tbody>
            </table>
        </t>
    </template>

    <!-- Additional reports (Trial Balance, Cash Flow, Executive P&L) follow same pattern -->
    <!-- Implement remaining reports following the design specs in the markdown files -->

</odoo>
```

---

## PHASE 3: REMAINING INTELLIGENCE ENGINES

### Task 3.1: Create `ops_ledger_report_templates.xml`

Implement: General Ledger, Partner Ledger, Aged Receivables, Aged Payables

### Task 3.2: Create `ops_asset_report_templates.xml`

Implement: Fixed Asset Register, Depreciation Schedule, CAPEX Analysis

### Task 3.3: Create `ops_inventory_report_templates.xml`

Implement: Stock Valuation, Dead Stock Analysis, Movement Analysis

### Task 3.4: Create `ops_treasury_report_templates.xml`

Implement: Cash Outflow Forecast, PDC Registry

### Task 3.5: Create `ops_consolidated_report_templates.xml`

Implement: Consolidated Financial Statements

---

## PHASE 4: REPORT ACTIONS & WIZARDS

### Task 4.1: Create `report_actions.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ═══════════════════════════════════════════════════════════════════
         REPORT ACTIONS — All 18 Reports
    ═══════════════════════════════════════════════════════════════════ -->

    <!-- Balance Sheet -->
    <record id="action_ops_report_balance_sheet" model="ir.actions.report">
        <field name="name">Balance Sheet</field>
        <field name="model">ops.balance.sheet.report</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">ops_matrix_reports.ops_report_balance_sheet</field>
        <field name="report_file">ops_matrix_reports.ops_report_balance_sheet</field>
        <field name="paperformat_id" ref="ops_paperformat_a4"/>
        <field name="binding_type">report</field>
    </record>
    
    <!-- Profit & Loss -->
    <record id="action_ops_report_profit_loss" model="ir.actions.report">
        <field name="name">Profit &amp; Loss Statement</field>
        <field name="model">ops.profit.loss.report</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">ops_matrix_reports.ops_report_profit_loss</field>
        <field name="report_file">ops_matrix_reports.ops_report_profit_loss</field>
        <field name="paperformat_id" ref="ops_paperformat_a4"/>
        <field name="binding_type">report</field>
    </record>
    
    <!-- Add remaining 16 report actions following same pattern -->

</odoo>
```

---

## DESIGN SPECIFICATIONS REFERENCE

Read the following design specification files for complete details on each report:

1. **`01-design-system-and-balance-sheet.md`**
   - Complete CSS design tokens
   - Typography scale
   - Color palette
   - Component library
   - Balance Sheet full specification

2. **`02-pnl-cashflow-trialbalance-aging.md`**
   - Profit & Loss Statement
   - Statement of Cash Flows
   - Executive P&L (Segment Analysis)
   - Trial Balance
   - Aged Receivables
   - Aged Payables

3. **`03-assets-inventory-treasury-consolidated.md`**
   - General Ledger
   - Partner Ledger
   - Fixed Asset Register
   - Depreciation Schedule
   - CAPEX Analysis
   - Stock Valuation
   - Dead Stock Analysis
   - Movement Analysis
   - Cash Outflow Forecast
   - PDC Registry
   - Consolidated Financial Statements

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Meridian Engine
- [ ] Create `ops_report_layout.xml` with complete CSS
- [ ] Create `paper_format.xml` with A4 definition
- [ ] Test base layout renders correctly

### Phase 2: Financial Intelligence Engine
- [ ] Balance Sheet template
- [ ] Profit & Loss template
- [ ] Cash Flow Statement template
- [ ] Trial Balance template
- [ ] Executive P&L template
- [ ] Create wizards for report parameters

### Phase 3: Ledger Intelligence Engine
- [ ] General Ledger template
- [ ] Partner Ledger template
- [ ] Aged Receivables template
- [ ] Aged Payables template

### Phase 4: Asset Intelligence Engine
- [ ] Fixed Asset Register template
- [ ] Depreciation Schedule template
- [ ] CAPEX Analysis template

### Phase 5: Inventory Intelligence Engine
- [ ] Stock Valuation template
- [ ] Dead Stock Analysis template
- [ ] Movement Analysis template

### Phase 6: Treasury Intelligence Engine
- [ ] Cash Outflow Forecast template
- [ ] PDC Registry template

### Phase 7: Consolidated Intelligence
- [ ] Consolidated Financial Statements template

### Phase 8: Integration
- [ ] Create report actions for all 18 reports
- [ ] Create menu items
- [ ] Test PDF generation with wkhtmltopdf
- [ ] Verify company header/footer from Odoo document layout
- [ ] Test print color accuracy

---

## CRITICAL REMINDERS

1. **Use `display: table` instead of flexbox** — wkhtmltopdf has limited flexbox support
2. **Use web-safe fonts** — DejaVu Sans, Arial, Georgia
3. **Include `-webkit-print-color-adjust: exact`** — Ensures colors print correctly
4. **Test with actual PDF generation** — Don't just preview in browser
5. **Use `t-call="web.external_layout"`** — This pulls in company header/footer
6. **All templates inherit from `ops_report_base_document`** — Ensures consistent styling
7. **Prior year values use `ops-value-prior` class** — Muted gray color

---

## EXAMPLE USAGE

After implementation, generate a Balance Sheet PDF:

```python
# In Odoo shell or code
report = self.env['ops.balance.sheet.report'].create({
    'date_to': fields.Date.today(),
    'company_id': self.env.company.id,
})
report.action_generate_pdf()
```

Or via the menu: **Accounting → Reports → OPS Financial Intelligence → Balance Sheet**
