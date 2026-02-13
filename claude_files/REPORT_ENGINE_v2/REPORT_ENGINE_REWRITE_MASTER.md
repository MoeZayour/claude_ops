# OPS Report Engine v2 — Clean Rewrite Master Specification

## STATUS: EXECUTION READY
## Date: 2026-02-09
## Scope: Replace ~25,000 lines of organic report code with ~4,500 lines of contracted, dynamic code

---

## TABLE OF CONTENTS
1. [Architecture Overview](#1-architecture-overview)
2. [What to KEEP (Do Not Touch)](#2-what-to-keep)
3. [What to ARCHIVE (Move to _archived_reports/)](#3-what-to-archive)
4. [Data Contracts](#4-data-contracts)
5. [Report Catalog (29 Reports)](#5-report-catalog)
6. [Security Architecture](#6-security-architecture)
7. [Color & Branding System](#7-color--branding-system)
8. [Template System](#8-template-system)
9. [Wizard Architecture](#9-wizard-architecture)
10. [Bridge Parser](#10-bridge-parser)
11. [Excel Renderer](#11-excel-renderer)
12. [HTML View Controller](#12-html-view-controller)
13. [Execution Phases](#13-execution-phases)

---

## 1. Architecture Overview

Every report follows this 5-layer pipeline:

```
USER INPUT → FILTERS → DATA ENGINE → FORMATTER → OUTPUT
 (Wizard)   (Domain)    (Query)      (Shape)     (Render)
```

Three data shapes cover all 29 reports:

| Shape | Name | Used By |
|-------|------|---------|
| A | Line-based | GL, Partner Ledger, SOA, Cash Book, Day Book, Bank Book |
| B | Hierarchy-based | P&L, BS, CF, Budget vs Actual, Branch P&L, BU Report, Consolidation |
| C | Matrix/Table-based | TB, Aged, Asset Register, Depreciation, Treasury, Inventory |

The pipeline components:

```
ops.base.report.wizard (abstract, EXISTING — keep)
├── ops.gl.report.wizard (NEW)
├── ops.tb.report.wizard (NEW)
├── ops.pnl.report.wizard (NEW)
├── ops.bs.report.wizard (NEW)
├── ops.cf.report.wizard (NEW)
├── ops.aged.report.wizard (NEW)
├── ops.partner.ledger.wizard (NEW)
├── ops.cash.book.wizard (EXISTING — refactor)
├── ops.day.book.wizard (EXISTING — refactor)
├── ops.bank.book.wizard (EXISTING — refactor)
├── ops.asset.report.wizard (EXISTING — refactor)
├── ops.inventory.report.wizard (EXISTING — refactor)
├── ops.treasury.report.wizard (EXISTING — refactor)
├── ops.budget.vs.actual.wizard (EXISTING — refactor)
└── ops.consolidation.intelligence.wizard (EXISTING — refactor)
```

One bridge parser (replaces 15+ parsers):
```
report.ops_matrix_accounting.report_document (NEW — single bridge)
```

Three base QWeb templates (replace 12 templates):
```
ops_report_base.xml          → Header, footer, filter bar, page setup
ops_report_shape_lines.xml   → Shape A renderer
ops_report_shape_hierarchy.xml → Shape B renderer
ops_report_shape_matrix.xml  → Shape C renderer
+ per-report configuration templates (small, ~20-40 lines each)
```

One generic Excel renderer (replaces 7 files):
```
ops_excel_renderer.py (NEW)
```

---

## 2. What to KEEP (Do Not Touch)

These files are correct and must NOT be modified unless explicitly stated:

### Models (keep as-is):
- `models/ops_intelligence_security_mixin.py` (380 lines) — IT Admin Blindness + branch validation
- `models/ops_report_template.py` (287 lines) — Template save/load
- `models/ops_report_audit.py` (295 lines) — Audit trail logging
- `models/ops_report_helpers.py` (668 lines) — Formatting utilities (amount_to_words, colors, etc.)
- `models/res_company.py` — Report color fields (ops_report_primary_color, etc.)
- `models/ops_financial_report_config.py` (819 lines) — Report configuration model
- `report/excel_styles.py` (749 lines) — Keep for reference, merge into new renderer

### Wizards (keep base, refactor children):
- `wizard/ops_base_report_wizard.py` (751 lines) — Abstract base. Keep. Minor updates only.

### Non-report wizards (keep as-is):
- `wizard/ops_asset_depreciation_wizard.py` — Asset ops, not a report
- `wizard/ops_asset_disposal_wizard.py` — Asset ops, not a report
- `wizard/ops_asset_impairment_wizard.py` — Asset ops, not a report
- `wizard/ops_period_close_wizard.py` — Period close, not a report
- `wizard/ops_three_way_match_override_wizard.py` — 3-way match, not a report
- `wizard/ops_fx_revaluation_wizard.py` — FX reval, not a report

### Transactional document templates (keep as-is):
- `report/ops_report_invoice.xml` (354 lines) — Invoice template
- `report/ops_report_payment.xml` (226 lines) — Payment receipt template

### Data files (keep as-is):
- `data/ops_paperformat.xml` — Paper formats
- All non-report data files

---

## 3. What to ARCHIVE (Move to _archived_reports/)

Move ALL of these into `_archived_reports/v1/` with a README:

### Parsers (all replaced by bridge):
- `report/ops_financial_report_parser.py` (1,420 lines)
- `report/ops_general_ledger_report.py` (549 lines)
- `report/ops_financial_matrix_report.py` (299 lines)
- `report/ops_asset_register_report.py` (68 lines)
- `report/ops_corporate_report_parsers.py` (783 lines)

### Excel files (replaced by generic renderer):
- `report/ops_xlsx_abstract.py` (160 lines)
- `report/ops_excel_report_builders.py` (432 lines)
- `report/ops_asset_register_xlsx.py` (519 lines)
- `report/ops_general_ledger_xlsx.py` (158 lines)
- `report/ops_financial_matrix_xlsx.py` (520 lines)
- `report/ops_treasury_report_xlsx.py` (524 lines)

### Templates (replaced by shape-based system):
- `report/ops_financial_report_template.xml` (1,395 lines)
- `report/ops_general_ledger_template.xml` (444 lines)
- `report/ops_consolidated_report_templates.xml` (1,196 lines)
- `report/ops_daily_report_templates.xml` (1,031 lines)
- `report/ops_inventory_report_templates.xml` (746 lines)
- `report/ops_treasury_report_templates.xml` (642 lines)
- `report/ops_asset_report_templates.xml` (498 lines)
- `report/ops_partner_ledger_corporate.xml` (355 lines)
- `report/ops_budget_vs_actual_corporate.xml` (410 lines)
- `report/components/ops_corporate_report_components.xml` (520 lines)

### God wizard (replaced by focused wizards):
- `wizard/ops_general_ledger_wizard_enhanced.py` (2,053 lines)
- `views/ops_general_ledger_wizard_enhanced_views.xml` (256 lines)

### Old controller (replaced):
- `controllers/ops_report_controller.py` (381 lines)

---

## 4. Data Contracts

### 4.1 Common Meta Block (all shapes)

```python
# In report/ops_report_contracts.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import date, datetime


@dataclass
class ReportMeta:
    """Common metadata for all report shapes."""
    report_type: str           # 'gl', 'tb', 'pl', 'bs', etc.
    report_title: str          # Human-readable: "General Ledger"
    shape: str                 # 'lines', 'hierarchy', 'matrix'
    company_name: str
    company_vat: str = ''
    company_logo: str = ''     # Base64 or URL
    currency_symbol: str = ''
    currency_name: str = ''
    currency_position: str = 'before'  # 'before' or 'after'
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    as_of_date: Optional[str] = None
    generated_at: str = ''     # ISO datetime
    generated_by: str = ''     # User display name
    filters: Dict[str, Any] = field(default_factory=dict)
    # filters contains: branches[], bus[], journals[], accounts[], partners[], target_move, etc.
    # Template renders these dynamically — no hardcoded filter display


@dataclass
class ReportColors:
    """Company branding colors for report rendering."""
    primary: str = '#5B6BBB'
    primary_dark: str = '#44508c'
    primary_light: str = '#edeef5'
    text_on_primary: str = '#FFFFFF'
    body_text: str = '#1a1a1a'
    success: str = '#059669'
    danger: str = '#dc2626'
    warning: str = '#d97706'
    zero: str = '#94a3b8'
    border: str = '#e5e7eb'
```

### 4.2 Shape A — Line-Based Reports

Used by: GL, Partner Ledger, SOA, Cash Book, Day Book, Bank Book

```python
@dataclass
class LineEntry:
    """Single journal entry line."""
    date: str
    entry: str            # Move name (JV/2026/0001)
    journal: str          # Journal code
    account_code: str
    account_name: str
    label: str            # Line narration
    ref: str = ''
    partner: str = ''
    branch: str = ''
    bu: str = ''
    debit: float = 0.0
    credit: float = 0.0
    balance: float = 0.0   # Running balance (cumulative within group)
    currency: str = ''      # Foreign currency code
    amount_currency: float = 0.0
    reconciled: bool = False


@dataclass
class LineGroup:
    """Group of lines (by account, partner, bank, etc.)."""
    group_key: str        # Account code, partner ref, bank name
    group_name: str       # Display name
    group_meta: Dict[str, Any] = field(default_factory=dict)  # Type badge, category, etc.
    opening_balance: float = 0.0
    lines: List[LineEntry] = field(default_factory=list)
    total_debit: float = 0.0
    total_credit: float = 0.0
    closing_balance: float = 0.0


@dataclass
class ShapeAReport:
    """Line-based report data."""
    meta: ReportMeta = None
    colors: ReportColors = None
    groups: List[LineGroup] = field(default_factory=list)
    grand_totals: Dict[str, float] = field(default_factory=dict)
    # grand_totals: opening_balance, total_debit, total_credit, closing_balance
    # Column visibility (wizard sets these based on report type):
    visible_columns: List[str] = field(default_factory=lambda: [
        'date', 'entry', 'journal', 'account_code', 'account_name',
        'label', 'partner', 'branch', 'bu', 'debit', 'credit', 'balance'
    ])
```

### 4.3 Shape B — Hierarchy-Based Reports

Used by: P&L, BS, CF, Budget vs Actual, Branch P&L, BU Report, Consolidated BS

```python
@dataclass
class HierarchyNode:
    """Single node in a financial hierarchy."""
    code: str = ''
    name: str = ''
    level: int = 0          # 0=section, 1=group, 2=account, 3=detail
    style: str = 'detail'   # 'section' | 'group' | 'detail' | 'total' | 'grand_total'
    values: Dict[str, float] = field(default_factory=dict)
    # values keys depend on report: 'current', 'previous', 'budget', 'variance', 'variance_pct'
    # For multi-branch: 'branch_1', 'branch_2', etc.
    children: List['HierarchyNode'] = field(default_factory=list)


@dataclass
class ShapeBReport:
    """Hierarchy-based report data."""
    meta: ReportMeta = None
    colors: ReportColors = None
    value_columns: List[Dict[str, str]] = field(default_factory=list)
    # value_columns: [{'key': 'current', 'label': 'Current Period'}, {'key': 'previous', ...}]
    sections: List[HierarchyNode] = field(default_factory=list)
    net_result: Optional[HierarchyNode] = None  # Net Profit, Total A=L+E, Net CF
```

### 4.4 Shape C — Matrix/Table-Based Reports

Used by: TB, Aged, Asset Register, Depreciation, Treasury, Inventory

```python
@dataclass
class ColumnDef:
    """Dynamic column definition."""
    key: str              # Dict key in row values
    label: str            # Header display text
    col_type: str = 'string'  # 'string' | 'number' | 'currency' | 'date' | 'percentage'
    width: int = 0        # Relative width hint (0 = auto)
    align: str = 'left'   # 'left' | 'center' | 'right'
    subtotal: bool = False # Include in subtotals


@dataclass
class MatrixRow:
    """Single row in a matrix report."""
    level: int = 0        # For indentation / grouping
    style: str = 'detail' # 'header' | 'detail' | 'subtotal' | 'total' | 'grand_total'
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShapeCReport:
    """Matrix/table-based report data."""
    meta: ReportMeta = None
    colors: ReportColors = None
    columns: List[ColumnDef] = field(default_factory=list)
    rows: List[MatrixRow] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)
```

### 4.5 Helper: Building Meta + Colors

```python
def build_report_meta(wizard, report_type, report_title, shape):
    """Build standard ReportMeta from any wizard instance."""
    company = wizard.company_id
    currency = company.currency_id

    # Build filter dict dynamically from wizard fields
    filters = {}
    if hasattr(wizard, 'branch_ids') and wizard.branch_ids:
        filters['branches'] = wizard.branch_ids.mapped('name')
    if hasattr(wizard, 'business_unit_ids') and wizard.business_unit_ids:
        filters['business_units'] = wizard.business_unit_ids.mapped('name')
    if hasattr(wizard, 'journal_ids') and wizard.journal_ids:
        filters['journals'] = wizard.journal_ids.mapped('name')
    if hasattr(wizard, 'account_ids') and wizard.account_ids:
        filters['accounts'] = wizard.account_ids.mapped('display_name')
    if hasattr(wizard, 'partner_ids') and wizard.partner_ids:
        filters['partners'] = wizard.partner_ids.mapped('name')
    if hasattr(wizard, 'target_move'):
        filters['target_move'] = 'All Entries' if wizard.target_move == 'all' else 'Posted Only'

    return ReportMeta(
        report_type=report_type,
        report_title=report_title,
        shape=shape,
        company_name=company.name,
        company_vat=company.vat or '',
        currency_symbol=currency.symbol or '',
        currency_name=currency.name or '',
        currency_position=currency.position or 'before',
        date_from=str(wizard.date_from) if hasattr(wizard, 'date_from') and wizard.date_from else None,
        date_to=str(wizard.date_to) if hasattr(wizard, 'date_to') and wizard.date_to else None,
        as_of_date=str(wizard.as_of_date) if hasattr(wizard, 'as_of_date') and wizard.as_of_date else None,
        generated_at=fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        generated_by=wizard.env.user.name,
        filters=filters,
    )


def build_report_colors(company):
    """Build ReportColors from company settings."""
    primary = (company.ops_report_primary_color or '#5B6BBB').strip()
    return ReportColors(
        primary=primary,
        primary_dark=company.get_report_primary_dark() if hasattr(company, 'get_report_primary_dark') else '#44508c',
        primary_light=company.get_report_primary_light() if hasattr(company, 'get_report_primary_light') else '#edeef5',
        text_on_primary=(company.ops_report_text_on_primary or '#FFFFFF').strip(),
        body_text=(company.ops_report_body_text_color or '#1a1a1a').strip(),
    )
```

**CRITICAL: These dataclasses are documentation and validation aids. The actual data passed to QWeb templates are plain dicts (QWeb cannot consume Python dataclasses). Each wizard's `_get_report_data()` returns `asdict(shape_report)` — a plain nested dict matching the contract.**

---

## 5. Report Catalog (29 Reports)

### Financial Pillar (9 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 1 | General Ledger | A | `ops.gl.report.wizard` | Per-account grouping, opening balance, running balance, detailed/summary format |
| 2 | Trial Balance | C | `ops.tb.report.wizard` | Initial + Period + Ending columns, debit/credit split |
| 3 | Profit & Loss | B | `ops.pnl.report.wizard` | Revenue/Expense hierarchy, comparative period, % of revenue |
| 4 | Balance Sheet | B | `ops.bs.report.wizard` | Assets/Liabilities/Equity hierarchy, as-of-date, comparative |
| 5 | Cash Flow Statement | B | `ops.cf.report.wizard` | Operating/Investing/Financing sections, indirect method |
| 6 | Aged Receivables | C | `ops.aged.report.wizard` | Customer aging buckets (Current/30/60/90/120+), partner_type=customer |
| 7 | Aged Payables | C | `ops.aged.report.wizard` | Same wizard, partner_type=vendor |
| 8 | Partner Ledger | A | `ops.partner.ledger.wizard` | Per-partner grouping, opening balance, running balance |
| 9 | Statement of Account | A | `ops.partner.ledger.wizard` | Same wizard, report_type=soa, single partner focus |

### Daily Books Pillar (3 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 10 | Cash Book | A | `ops.cash.book.wizard` | Cash journal lines, grouped by date or account |
| 11 | Day Book | A | `ops.day.book.wizard` | All journals, grouped by journal |
| 12 | Bank Book | A | `ops.bank.book.wizard` | Bank journal lines, per-bank grouping |

### Treasury Pillar (3 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 13 | PDC Registry | C | `ops.treasury.report.wizard` | All PDCs, status column, amount, dates |
| 14 | PDC Maturity | C | `ops.treasury.report.wizard` | Maturity date buckets, inflow/outflow |
| 15 | PDCs in Hand | C | `ops.treasury.report.wizard` | Currently held PDCs only |

### Asset Pillar (5 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 16 | Asset Register | C | `ops.asset.report.wizard` | All assets, cost/depreciation/NBV columns |
| 17 | Depreciation Schedule | C | `ops.asset.report.wizard` | Periodic depreciation entries |
| 18 | Asset Disposal | C | `ops.asset.report.wizard` | Disposed assets, gain/loss |
| 19 | Asset Forecast | C | `ops.asset.report.wizard` | Future depreciation projection |
| 20 | Asset Movement | C | `ops.asset.report.wizard` | Additions/disposals/transfers in period |

### Inventory Pillar (4 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 21 | Stock Valuation | C | `ops.inventory.report.wizard` | Current stock value by product/category |
| 22 | Inventory Aging | C | `ops.inventory.report.wizard` | Age buckets by last movement date |
| 23 | Inventory Movement | C | `ops.inventory.report.wizard` | IN/OUT/balance for period |
| 24 | Negative Stock | C | `ops.inventory.report.wizard` | Products with negative qty |

### Consolidation Pillar (4 reports)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 25 | Company Consolidation | B | `ops.consolidation.intelligence.wizard` | Multi-company rollup |
| 26 | Branch P&L | B | `ops.consolidation.intelligence.wizard` | P&L per branch, side-by-side |
| 27 | BU Report | B | `ops.consolidation.intelligence.wizard` | P&L per BU |
| 28 | Consolidated Balance Sheet | B | `ops.consolidation.intelligence.wizard` | Multi-branch BS |

### Budget Pillar (1 report)

| # | Report | Shape | Wizard | Key Features |
|---|--------|-------|--------|-------------|
| 29 | Budget vs Actual | B | `ops.budget.vs.actual.wizard` | Budget/Actual/Variance per account hierarchy |

---

## 6. Security Architecture

### 23 Security Groups (XML IDs from ops_matrix_core)

```
group_ops_user                   → OPS User (base access)
group_ops_manager                → OPS Manager
group_ops_admin_power            → OPS Administrator
group_ops_it_admin               → IT Administrator (BLIND to all reports)
group_ops_branch_manager         → Branch Manager
group_ops_bu_leader              → Business Unit Leader
group_ops_cross_branch_bu_leader → Cross-Branch BU Leader
group_ops_executive              → Executive / CEO (read-only)
group_ops_cfo                    → CFO / Owner (full access)
group_ops_finance_manager        → Finance Manager
group_ops_accountant             → Accountant / Controller
group_ops_cost_controller        → Cost Controller
group_ops_compliance_officer     → Compliance Officer
group_ops_treasury               → Treasury Officer
group_ops_inventory_manager      → Inventory Manager
group_ops_sales_manager          → Sales Manager
group_ops_purchase_manager       → Purchase Manager
group_ops_product_approver       → Product Approver
group_ops_matrix_administrator   → Matrix Administrator
group_ops_see_cost               → Can See Product Costs
group_ops_see_margin             → Can See Profit Margins
group_ops_see_valuation          → Can See Stock Valuation
group_ops_can_export             → Can Export Data
```

### Report Access Rules

Each wizard TransientModel needs ACL entries. Pattern:

```csv
id,name,model_id/id,group_id/id,perm_read,perm_write,perm_create,perm_unlink
access_gl_wizard_accountant,GL Wizard Accountant,model_ops_gl_report_wizard,ops_matrix_core.group_ops_accountant,1,1,1,1
access_gl_wizard_finance,GL Wizard Finance Manager,model_ops_gl_report_wizard,ops_matrix_core.group_ops_finance_manager,1,1,1,1
access_gl_wizard_cfo,GL Wizard CFO,model_ops_gl_report_wizard,ops_matrix_core.group_ops_cfo,1,1,1,1
```

### IT Admin Blindness (Non-negotiable)

Every wizard inherits `ops.intelligence.security.mixin`. Every wizard's `action_generate_report()` calls `self._check_intelligence_access(engine_name)` BEFORE generating data. `group_ops_it_admin` is BLOCKED from ALL report data via `[(0,'=',1)]` record rules.

### Branch Isolation

Every wizard that queries `account.move.line` must add branch domain: `[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]`. The intelligence security mixin provides `_get_branch_filter_domain()` and `_validate_branch_access()`.

### SoD: Export Control

Only users in `group_ops_can_export` can use Excel export. The `action_export_to_excel()` method must check this:

```python
def action_export_to_excel(self):
    if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
        raise AccessError(_("You do not have permission to export data."))
    ...
```

### Cost/Margin Visibility

- `group_ops_see_cost`: Can see cost columns in Inventory reports
- `group_ops_see_margin`: Can see margin columns
- `group_ops_see_valuation`: Can see stock valuation

These must be checked dynamically when building `visible_columns` for Shape C inventory reports.

---

## 7. Color & Branding System

### Company-Level Color Fields (in res.company)

| Field | Default | Purpose |
|-------|---------|---------|
| `ops_report_primary_color` | `#5B6BBB` | Headers, borders, section accents |
| `ops_report_text_on_primary` | `#FFFFFF` | Text on primary-colored backgrounds |
| `ops_report_body_text_color` | `#1a1a1a` | Main body text |

### Computed Colors

| Color | Method | Purpose |
|-------|--------|---------|
| `primary_light` | `company.get_report_primary_light()` | 15% opacity blend with white — light backgrounds |
| `primary_dark` | `company.get_report_primary_dark()` | 75% darkened — text on light backgrounds |

### Semantic Colors (hardcoded, not per-company)

| Token | Value | Usage |
|-------|-------|-------|
| `success` | `#059669` | Positive values, revenue |
| `danger` | `#dc2626` | Negative values, expenses, overdue |
| `warning` | `#d97706` | Warnings, amber aging |
| `zero` | `#94a3b8` | Zero-value text |
| `border` | `#e5e7eb` | Table borders |

### Template Usage

Templates receive `colors` dict and use inline styles (wkhtmltopdf does not support CSS variables):

```xml
<th t-attf-style="background-color: #{colors['primary']}; color: #{colors['text_on_primary']};">
    Account
</th>
<td t-attf-style="color: #{line['balance'] >= 0 and colors.get('success', '#059669') or colors.get('danger', '#dc2626')};">
    <t t-out="helpers.format_amount(line['balance'])"/>
</td>
```

---

## 8. Template System

### 8.1 Base Layout — `report/ops_report_base.xml`

The master layout for ALL reports (except Invoice/Payment which keep their own).

Contains:
- `ops_report_base`: QWeb template with company header, filter summary, content slot, footer
- `ops_corporate_pdf_layout`: wkhtmltopdf header/footer (keep existing, but integrate)
- Paper format assignment

Structure:
```xml
<template id="ops_report_base">
    <!-- Page setup -->
    <div class="ops-report" t-attf-style="font-family: Arial, Helvetica, sans-serif; color: #{colors['body_text']};">

        <!-- HEADER: Company logo + report title + date range -->
        <div class="ops-report-header" t-attf-style="border-bottom: 3px solid #{colors['primary']}; padding-bottom: 12px; margin-bottom: 16px;">
            <!-- Company name, logo, VAT -->
            <!-- Report title, date range -->
            <!-- Generated timestamp -->
        </div>

        <!-- FILTER BAR: Dynamic rendering of active filters -->
        <div class="ops-report-filters" t-if="data['meta']['filters']"
             t-attf-style="background: #{colors['primary_light']}; padding: 8px 12px; margin-bottom: 16px; border-radius: 4px;">
            <t t-foreach="data['meta']['filters'].items()" t-as="filter_item">
                <span style="font-size: 9pt;">
                    <strong><t t-out="filter_item[0]"/>:</strong>
                    <t t-if="isinstance(filter_item[1], list)">
                        <t t-out="', '.join(filter_item[1])"/>
                    </t>
                    <t t-else="">
                        <t t-out="filter_item[1]"/>
                    </t>
                    <t t-if="not filter_item_last"> | </t>
                </span>
            </t>
        </div>

        <!-- CONTENT SLOT: Shape-specific renderer fills this -->
        <t t-out="0"/>

        <!-- NOTES: Currency, scope, generation info -->
        <div class="ops-report-notes" style="margin-top: 16px; font-size: 8pt; color: #94a3b8;">
            <p>All amounts in <t t-out="data['meta']['currency_name']"/> unless otherwise stated.</p>
            <p>Generated by <t t-out="data['meta']['generated_by']"/> on <t t-out="data['meta']['generated_at']"/></p>
        </div>
    </div>
</template>
```

### 8.2 Shape A Template — `report/ops_report_shape_lines.xml`

Renders grouped line-based reports. Used by GL, Partner Ledger, SOA, Cash/Day/Bank Book.

```xml
<template id="ops_report_shape_lines" inherit_id="ops_report_base">
    <t t-call="ops_matrix_accounting.ops_report_base">
        <!-- For each group (account/partner/bank) -->
        <t t-foreach="data['groups']" t-as="group">
            <!-- Group header with opening balance -->
            <!-- Lines table with dynamic column visibility -->
            <!-- Group totals -->
        </t>
        <!-- Grand totals -->
    </t>
</template>
```

Column visibility is driven by `data['visible_columns']` list. The template loops through columns dynamically — no hardcoded column set.

### 8.3 Shape B Template — `report/ops_report_shape_hierarchy.xml`

Renders hierarchical financial statements. Recursive rendering of sections.

### 8.4 Shape C Template — `report/ops_report_shape_matrix.xml`

Renders tabular reports with dynamic columns. The `data['columns']` list defines headers. Rows are rendered with appropriate styling per `row['style']`.

### 8.5 Per-Report Configuration

Each report type has a SMALL template that:
1. Calls the appropriate shape template
2. Sets report-specific display options

Example:
```xml
<template id="report_general_ledger">
    <t t-call="ops_matrix_accounting.ops_report_shape_lines">
        <!-- GL shows: date, entry, journal, account, label, partner, branch, bu, debit, credit, balance -->
        <!-- Opening balance: YES -->
        <!-- Running balance: YES -->
    </t>
</template>
```

---

## 9. Wizard Architecture

### 9.1 Base Wizard Updates

`ops_base_report_wizard.py` needs minor updates:

1. Add `output_format` field: `Selection([('pdf','PDF'),('excel','Excel'),('html','View in Browser')], default='pdf')`
2. Add `action_generate_report()` that dispatches to PDF/Excel/HTML based on output_format
3. Ensure `_get_report_data()` is abstract and returns a dict matching one of the 3 shapes
4. Add `_get_report_shape()` abstract method returning 'lines', 'hierarchy', or 'matrix'

### 9.2 Individual Wizard Pattern

Every wizard follows this exact pattern:

```python
class OpsGLReportWizard(models.TransientModel):
    _name = 'ops.gl.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'General Ledger Report'

    # Report-specific fields only
    account_ids = fields.Many2many('account.account', string='Accounts')
    journal_ids = fields.Many2many('account.journal', string='Journals')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    include_initial_balance = fields.Boolean(default=True)
    target_move = fields.Selection([('posted', 'Posted'), ('all', 'All')], default='posted')
    display_account = fields.Selection([('all', 'All'), ('movement', 'With Movements'), ('balance', 'With Balance')], default='movement')
    sort_by = fields.Selection([('date', 'Date'), ('account', 'Account'), ('partner', 'Partner')], default='date')
    report_format = fields.Selection([('detailed', 'Detailed'), ('summary', 'Summary')], default='detailed')

    def _get_engine_name(self):
        return 'Financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {'gl': 'General Ledger'}

    def _get_report_data(self):
        """Build Shape A report data for General Ledger."""
        self.ensure_one()
        self._check_intelligence_access('Financial')

        meta = build_report_meta(self, 'gl', 'General Ledger', 'lines')
        colors = build_report_colors(self.company_id)

        # Query data
        domain = self._build_gl_domain()
        initial_balances = self._compute_initial_balances() if self.include_initial_balance else {}
        move_lines = self.env['account.move.line'].search(domain, order='account_id, date, id')

        # Build groups (per-account with running balance)
        groups = self._build_account_groups(move_lines, initial_balances)

        # Grand totals
        grand_totals = self._compute_grand_totals(groups)

        return asdict(ShapeAReport(
            meta=meta,
            colors=colors,
            groups=groups,
            grand_totals=grand_totals,
            visible_columns=['date', 'entry', 'journal', 'label', 'partner', 'branch', 'bu', 'debit', 'credit', 'balance'],
        ))

    def _return_report_action(self, data):
        """Return ir.actions.report action for PDF."""
        report = self.env.ref('ops_matrix_accounting.action_report_gl')
        return report.report_action(self, data={'wizard_id': self.id, 'wizard_model': self._name})
```

### 9.3 Wizard Field Matrix

Fields inherited from base (DO NOT redeclare):
- `company_id`, `currency_id`, `report_template_id`
- `date_from`, `date_to` (if base has them — check; if not, add to base)
- `branch_ids`, `business_unit_ids`, `matrix_filter_mode`

Fields per wizard type — see Section 5 catalog for details.

---

## 10. Bridge Parser

### Single parser for ALL reports:

```python
# report/ops_report_bridge.py

class OpsReportBridge(models.AbstractModel):
    """Universal bridge parser for all OPS reports.

    Thin layer between ir.actions.report and wizard._get_report_data().
    The wizard owns the data logic. This bridge just connects them.
    """
    _name = 'report.ops_matrix_accounting.report_document'
    _description = 'OPS Report Bridge Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data or 'wizard_model' not in data:
            return {'doc_ids': docids, 'docs': [], 'data': {}, 'helpers': self.env['ops.report.helpers']}

        wizard = self.env[data['wizard_model']].browse(data.get('wizard_id') or docids[0])
        if not wizard.exists():
            raise UserError(_("Report wizard record not found."))

        report_data = wizard._get_report_data()

        return {
            'doc_ids': docids,
            'doc_model': data['wizard_model'],
            'docs': wizard,
            'data': report_data,
            'helpers': self.env['ops.report.helpers'],
            'colors': report_data.get('colors', {}),
        }
```

### ir.actions.report records

One record per report type, all pointing to the same bridge parser but different QWeb templates:

```xml
<record id="action_report_gl" model="ir.actions.report">
    <field name="name">General Ledger</field>
    <field name="model">ops.gl.report.wizard</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">ops_matrix_accounting.report_general_ledger</field>
    <field name="report_file">ops_matrix_accounting.report_general_ledger</field>
    <field name="paperformat_id" ref="ops_matrix_accounting.ops_landscape_paperformat"/>
</record>
```

---

## 11. Excel Renderer

### Single generic renderer: `report/ops_excel_renderer.py`

```python
class OpsExcelRenderer:
    """Generic Excel renderer that reads data contracts and produces .xlsx files.

    No report-specific code. Reads column definitions from the data contract
    and renders accordingly.
    """

    def __init__(self, workbook, company_name, report_title, colors, helpers):
        self.wb = workbook
        self.company_name = company_name
        self.report_title = report_title
        self.colors = colors
        self.helpers = helpers
        self._init_formats()

    def _init_formats(self):
        """Create all Excel formats from color config."""
        primary = self.colors.get('primary', '#5B6BBB')
        # header_format, detail_format, total_format, currency_format, etc.
        # All derived from colors dict — fully dynamic

    def render_shape_a(self, data):
        """Render line-based report to Excel."""
        # Header sheet info
        # For each group: group header row, line rows, group total row
        # Grand totals row

    def render_shape_b(self, data):
        """Render hierarchy report to Excel."""
        # Recursive section rendering with indentation

    def render_shape_c(self, data):
        """Render matrix report to Excel."""
        # Dynamic columns from data['columns']
        # Rows with styling based on row['style']

    def render(self, data):
        """Auto-dispatch to correct shape renderer."""
        shape = data.get('meta', {}).get('shape', 'matrix')
        if shape == 'lines':
            return self.render_shape_a(data)
        elif shape == 'hierarchy':
            return self.render_shape_b(data)
        else:
            return self.render_shape_c(data)
```

---

## 12. HTML View Controller

### Single controller: `controllers/ops_report_controller.py`

```python
class OpsReportController(http.Controller):

    @http.route('/ops/report/html/<string:wizard_model>/<int:wizard_id>', type='http', auth='user')
    def report_html_view(self, wizard_model, wizard_id, **kwargs):
        """Render any OPS report as HTML for browser viewing."""
        # 1. Validate wizard_model is an allowed report wizard
        # 2. Load wizard, check access
        # 3. Call wizard._get_report_data()
        # 4. Determine shape, select template
        # 5. Render QWeb template with data
        # 6. Wrap in HTML chrome (toolbar with Print/Export/Close buttons)
```

---

## 13. Execution Phases

### Phase 0: Archive Old Code
- Move all files from Section 3 to `_archived_reports/v1/`
- Create `_archived_reports/v1/README.md` with timestamp and file list
- Update `__init__.py` files to remove old imports
- Update `__manifest__.py` to remove old data files
- **DO NOT update module yet** — just move files

### Phase 1: Data Contracts + Bridge Parser
- Create `report/ops_report_contracts.py` with all dataclasses and helpers
- Create `report/ops_report_bridge.py` with universal bridge parser
- Update `report/__init__.py`

### Phase 2: Base Templates
- Create `report/ops_report_base.xml` — master layout
- Create `report/ops_report_shape_lines.xml` — Shape A
- Create `report/ops_report_shape_hierarchy.xml` — Shape B
- Create `report/ops_report_shape_matrix.xml` — Shape C
- Create `report/ops_report_actions.xml` — all ir.actions.report records

### Phase 3: Financial Wizards (Core 7)
- Create `wizard/ops_gl_wizard.py` + views
- Create `wizard/ops_tb_wizard.py` + views
- Create `wizard/ops_pnl_wizard.py` + views
- Create `wizard/ops_bs_wizard.py` + views
- Create `wizard/ops_cf_wizard.py` + views
- Create `wizard/ops_aged_wizard.py` + views
- Create `wizard/ops_partner_ledger_wizard.py` + views
- Create per-report QWeb config templates
- Update menus

### Phase 4: Daily Books + Treasury + Assets + Inventory
- Refactor `wizard/ops_daily_reports_wizard.py` to use contracts
- Refactor `wizard/ops_treasury_report_wizard.py`
- Refactor `wizard/ops_asset_report_wizard.py`
- Refactor `wizard/ops_inventory_report_wizard.py`
- Create per-report QWeb config templates

### Phase 5: Consolidation + Budget + Excel
- Refactor `wizard/ops_consolidation_intelligence_wizard.py`
- Refactor `wizard/ops_budget_vs_actual_wizard.py`
- Create `report/ops_excel_renderer.py`
- Create new `controllers/ops_report_controller.py`

### Phase 6: ACLs, Menus, Manifest, Testing
- Update `security/ir.model.access.csv` for new wizard models
- Update menu XML files
- Update `__manifest__.py` with all new files
- Module upgrade + smoke test all 29 reports

---

## CRITICAL RULES FOR IMPLEMENTATION

1. **NEVER use `sudo()` in report code** — reports must respect record rules
2. **ALWAYS call `_check_intelligence_access()` before `_get_report_data()`**
3. **ALWAYS compute running balance PER GROUP, not globally**
4. **ALWAYS include `ops_branch_id` domain in move line queries**
5. **ALWAYS use `_read_group()` for aggregations, `search()` for line details**
6. **NEVER hardcode company name, currency, or colors**
7. **ALWAYS pass colors from company settings, never hardcode hex values in templates**
8. **ALWAYS check `group_ops_can_export` before Excel generation**
9. **ALWAYS check `group_ops_see_cost/margin/valuation` before including those columns**
10. **ALWAYS log report generation via `_log_intelligence_report()`**

---

## FILE STRUCTURE (Final State)

```
ops_matrix_accounting/
├── report/
│   ├── __init__.py
│   ├── ops_report_contracts.py        # Data contracts (NEW)
│   ├── ops_report_bridge.py           # Universal bridge parser (NEW)
│   ├── ops_excel_renderer.py          # Generic Excel renderer (NEW)
│   ├── excel_styles.py                # KEEP — referenced by renderer
│   ├── ops_report_base.xml            # Master layout (NEW)
│   ├── ops_report_shape_lines.xml     # Shape A template (NEW)
│   ├── ops_report_shape_hierarchy.xml # Shape B template (NEW)
│   ├── ops_report_shape_matrix.xml    # Shape C template (NEW)
│   ├── ops_report_actions.xml         # All ir.actions.report records (NEW)
│   ├── ops_report_configs.xml         # Per-report config templates (NEW)
│   ├── ops_report_invoice.xml         # KEEP — not part of rewrite
│   └── ops_report_payment.xml         # KEEP — not part of rewrite
├── wizard/
│   ├── __init__.py
│   ├── ops_base_report_wizard.py      # KEEP — minor updates
│   ├── ops_gl_wizard.py               # NEW
│   ├── ops_tb_wizard.py               # NEW
│   ├── ops_pnl_wizard.py              # NEW
│   ├── ops_bs_wizard.py               # NEW
│   ├── ops_cf_wizard.py               # NEW
│   ├── ops_aged_wizard.py             # NEW
│   ├── ops_partner_ledger_wizard.py   # NEW
│   ├── ops_daily_reports_wizard.py    # REFACTORED
│   ├── ops_treasury_report_wizard.py  # REFACTORED
│   ├── ops_asset_report_wizard.py     # REFACTORED
│   ├── ops_inventory_report_wizard.py # REFACTORED
│   ├── ops_consolidation_intelligence_wizard.py  # REFACTORED
│   ├── ops_budget_vs_actual_wizard.py # REFACTORED
│   ├── ops_wizard_views.xml           # All wizard views (NEW, consolidated)
│   ├── ops_period_close_wizard.py     # KEEP — not a report
│   ├── ops_three_way_match_override_wizard.py  # KEEP
│   ├── ops_asset_depreciation_wizard.py  # KEEP
│   ├── ops_asset_disposal_wizard.py      # KEEP
│   ├── ops_asset_impairment_wizard.py    # KEEP
│   └── ops_fx_revaluation_wizard.py      # KEEP
├── controllers/
│   ├── __init__.py
│   └── ops_report_controller.py       # NEW (replaces old)
├── _archived_reports/
│   └── v1/                            # All archived files
└── ...
```
