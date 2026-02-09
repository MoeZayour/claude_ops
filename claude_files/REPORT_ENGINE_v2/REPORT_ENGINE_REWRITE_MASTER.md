# OPS Report Engine v2 — Clean Rewrite Master Specification

## STATUS: EXECUTION READY
## Date: 2026-02-09
## Scope: Replace ~25,000 lines of organic report code with ~4,500 lines of contracted, dynamic code

---

## TABLE OF CONTENTS
1. Architecture Overview
2. What to KEEP (Do Not Touch)
3. What to ARCHIVE (Move to _archived_reports/)
4. Data Contracts
5. Report Catalog (29 Reports)
6. Security Architecture
7. Color & Branding System
8. Template System
9. Wizard Architecture
10. Bridge Parser
11. Excel Renderer
12. HTML View Controller
13. Execution Phases

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

Pipeline components:

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

One bridge parser: `report.ops_matrix_accounting.report_document`
Three base QWeb templates: ops_report_shape_lines.xml, ops_report_shape_hierarchy.xml, ops_report_shape_matrix.xml
One generic Excel renderer: ops_excel_renderer.py

---

## 2. What to KEEP (Do Not Touch)

### Models:
- models/ops_intelligence_security_mixin.py (380 lines) — IT Admin Blindness + branch validation
- models/ops_report_template.py (287 lines) — Template save/load
- models/ops_report_audit.py (295 lines) — Audit trail logging
- models/ops_report_helpers.py (668 lines) — Formatting utilities
- models/res_company.py — Report color fields
- models/ops_financial_report_config.py (819 lines) — Report configuration model
- report/excel_styles.py (749 lines) — Keep for reference

### Wizards (keep base):
- wizard/ops_base_report_wizard.py (751 lines) — Abstract base. Minor updates only.

### Non-report wizards:
- ops_asset_depreciation_wizard.py, ops_asset_disposal_wizard.py, ops_asset_impairment_wizard.py
- ops_period_close_wizard.py, ops_three_way_match_override_wizard.py, ops_fx_revaluation_wizard.py

### Transactional templates:
- report/ops_report_invoice.xml, report/ops_report_payment.xml

---

## 3. What to ARCHIVE

Move ALL to `_archived_reports/v1/`:

### Parsers: ops_financial_report_parser.py, ops_general_ledger_report.py, ops_financial_matrix_report.py, ops_asset_register_report.py, ops_corporate_report_parsers.py
### Excel: ops_xlsx_abstract.py, ops_excel_report_builders.py, ops_asset_register_xlsx.py, ops_general_ledger_xlsx.py, ops_financial_matrix_xlsx.py, ops_treasury_report_xlsx.py
### Templates: ops_financial_report_template.xml, ops_general_ledger_template.xml, ops_consolidated_report_templates.xml, ops_daily_report_templates.xml, ops_inventory_report_templates.xml, ops_treasury_report_templates.xml, ops_asset_report_templates.xml, ops_partner_ledger_corporate.xml, ops_budget_vs_actual_corporate.xml, components/ops_corporate_report_components.xml
### God wizard: ops_general_ledger_wizard_enhanced.py + views
### Controller: controllers/ops_report_controller.py

---

## 4. Data Contracts

### 4.1 ReportMeta (all shapes)
- report_type, report_title, shape, company_name, company_vat, currency_symbol, currency_name, currency_position
- date_from, date_to, as_of_date, generated_at, generated_by
- filters: Dict — dynamically built from wizard fields (branches, bus, journals, accounts, partners, target_move)

### 4.2 ReportColors
- primary (#5B6BBB), primary_dark, primary_light, text_on_primary (#FFFFFF), body_text (#1a1a1a)
- Semantic: success (#059669), danger (#dc2626), warning (#d97706), zero (#94a3b8), border (#e5e7eb)

### 4.3 Shape A — Line-Based
- LineEntry: date, entry, journal, account_code, account_name, label, ref, partner, branch, bu, debit, credit, balance, currency, amount_currency
- LineGroup: group_key, group_name, group_meta, opening_balance, lines[], total_debit, total_credit, closing_balance
- ShapeAReport: meta, colors, groups[], grand_totals, visible_columns[]

### 4.4 Shape B — Hierarchy-Based
- HierarchyNode: code, name, level (0-3), style (section|group|detail|total|grand_total), values dict, children[]
- ShapeBReport: meta, colors, value_columns[], sections[], net_result

### 4.5 Shape C — Matrix/Table-Based
- ColumnDef: key, label, col_type (string|number|currency|date|percentage), width, align, subtotal
- MatrixRow: level, style (header|detail|subtotal|total|grand_total), values dict
- ShapeCReport: meta, colors, columns[], rows[], totals dict

### Helpers
- build_report_meta(wizard, report_type, title, shape) → ReportMeta
- build_report_colors(company) → ReportColors
- to_dict(dataclass) → dict (for QWeb consumption)

---

## 5. Report Catalog (29 Reports)

### Financial (9): GL(A), TB(C), P&L(B), BS(B), CF(B), Aged AR(C), Aged AP(C), Partner Ledger(A), SOA(A)
### Daily Books (3): Cash Book(A), Day Book(A), Bank Book(A)
### Treasury (3): PDC Registry(C), PDC Maturity(C), PDCs in Hand(C)
### Asset (5): Register(C), Depreciation Schedule(C), Disposal(C), Forecast(C), Movement(C)
### Inventory (4): Valuation(C), Aging(C), Movement(C), Negative Stock(C)
### Consolidation (4): Company(B), Branch P&L(B), BU Report(B), Consolidated BS(B)
### Budget (1): Budget vs Actual(B)

---

## 6. Security Architecture

### 23 Groups from ops_matrix_core:
group_ops_user, group_ops_manager, group_ops_admin_power, group_ops_it_admin (BLIND),
group_ops_branch_manager, group_ops_bu_leader, group_ops_cross_branch_bu_leader,
group_ops_executive (read-only), group_ops_cfo (full), group_ops_finance_manager,
group_ops_accountant, group_ops_cost_controller, group_ops_compliance_officer,
group_ops_treasury, group_ops_inventory_manager, group_ops_sales_manager,
group_ops_purchase_manager, group_ops_product_approver, group_ops_matrix_administrator,
group_ops_see_cost, group_ops_see_margin, group_ops_see_valuation, group_ops_can_export

### Rules:
1. IT Admin Blindness: _check_intelligence_access() before ALL report generation
2. Branch Isolation: _get_branch_filter_domain() on ALL move line queries
3. Export Control: group_ops_can_export required for Excel
4. Cost/Margin: group_ops_see_cost/margin/valuation checked before column inclusion

---

## 7. Color & Branding

Company fields: ops_report_primary_color (#5B6BBB), ops_report_text_on_primary (#FFFFFF), ops_report_body_text_color (#1a1a1a)
Computed: get_report_primary_light() (15% blend), get_report_primary_dark() (75% darken)
Templates use inline t-attf-style with colors dict — NEVER hardcode hex in templates.

---

## 8-13. See phase files for implementation details.

## CRITICAL RULES
1. NEVER sudo() in report code
2. ALWAYS _check_intelligence_access() before _get_report_data()
3. ALWAYS running balance PER GROUP, never global
4. ALWAYS branch isolation domain in queries
5. NEVER hardcode colors in templates
6. ALWAYS check group_ops_can_export before Excel
7. ALWAYS check see_cost/margin/valuation before columns
8. ALWAYS _log_intelligence_report() after generation
