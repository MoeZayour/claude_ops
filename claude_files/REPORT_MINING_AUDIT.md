# OPS FRAMEWORK - FULL CODE MINING AUDIT: REPORTS
**Generated:** 2026-02-08
**Mode:** Read-only autonomous scan
**Modules Scanned:** ops_matrix_core, ops_matrix_accounting, ops_theme, ops_kpi

---

## TABLE OF CONTENTS
1. [File Inventory Summary](#1-file-inventory-summary)
2. [Wizard Definitions (TransientModels)](#2-wizard-definitions-transientmodels)
3. [Report Classes (AbstractModels)](#3-report-classes-abstractmodels)
4. [Report Actions (ir.actions.report)](#4-report-actions)
5. [QWeb Report Templates](#5-qweb-report-templates)
6. [Menu Items](#6-menu-items)
7. [Manifest & Import Chains](#7-manifest--import-chains)
8. [Database Truth](#8-database-truth)
9. [Security Rules](#9-security-rules)
10. [Company Report Fields & Colors](#10-company-report-fields--colors)

---

## 1. FILE INVENTORY SUMMARY

### Module Overview
| Module | Report .py | Report .xml | Wizard .py | Wizard .xml | Models (report-related) | Controllers |
|--------|-----------|-------------|------------|-------------|------------------------|-------------|
| **ops_matrix_accounting** | 9 | 21 | 14 | 13 | 12 | 1 |
| **ops_matrix_core** | 0 | 6 | 9 | 7 | 5 | 1 |
| **ops_theme** | 0 | 3 | 0 | 0 | 2 | 1 |
| **ops_kpi** | 0 | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | **9** | **30** | **23** | **20** | **19** | **3** |

### ops_matrix_accounting Report Files

**Python Parsers (QWeb):**
- `report/ops_financial_report_parser.py` - Financial Report Parser (P&L, BS, TB, CF, Aged)
- `report/ops_financial_matrix_report.py` - Financial Matrix Report Parser
- `report/ops_general_ledger_report.py` (548 lines) - GL Report (Minimal + Legacy + Corporate)
- `report/ops_asset_register_report.py` - Asset Register Report
- `report/ops_corporate_report_parsers.py` - 14 corporate parsers (Cash/Day/Bank Book, Consolidation, Partner Ledger, Budget)

**Excel Infrastructure:**
- `report/excel_styles.py` - Shared OPSExcelStyles library
- `report/ops_xlsx_abstract.py` (160 lines) - Base XLSX class
- `report/ops_general_ledger_xlsx.py` (158 lines) - GL Excel
- `report/ops_financial_matrix_xlsx.py` - Financial Matrix Excel (8 report types)
- `report/ops_asset_register_xlsx.py` - Asset Intelligence Excel (4 report types)
- `report/ops_treasury_report_xlsx.py` (524 lines) - Treasury Excel (3 report types)

**QWeb XML Templates (21 files):**
- `report/ops_general_ledger_template.xml` (620 lines)
- `report/ops_general_ledger_minimal.xml`
- `report/ops_financial_report_template.xml`
- `report/ops_financial_report_minimal.xml`
- `report/ops_financial_reports_v2.xml` (1,765 lines - 4 templates)
- `report/ops_balance_sheet_v2.xml` (340 lines)
- `report/ops_corporate_report_layout.xml`
- `report/ops_report_layout.xml`
- `report/ops_report_minimal_styles.xml`
- `report/ops_internal_layout_v2.xml`
- `report/ops_report_invoice.xml` (354 lines)
- `report/ops_report_payment.xml`
- `report/ops_inventory_report_templates.xml` (1,903 lines - 4 templates)
- `report/ops_asset_report_templates.xml` (620+ lines)
- `report/ops_treasury_report_templates.xml` (500+ lines - 3 templates)
- `report/ops_consolidated_report_templates.xml` (700+ lines - 4 templates)
- `report/ops_daily_report_templates.xml` (600+ lines - 3 templates)
- `report/ops_partner_ledger_corporate.xml`
- `report/ops_budget_vs_actual_corporate.xml` (500+ lines)
- `report/components/ops_corporate_report_components.xml` (28KB)
- `report/components/REPORT_CATALOG.md`

### ops_matrix_core Report Files
- `report/ops_report_quotation.xml`
- `report/ops_report_purchase.xml`
- `report/ops_report_delivery.xml`
- `reports/ops_products_availability_report.xml`
- `reports/sale_order_availability_report.xml`
- `reports/sale_order_documentation_report.xml`

### ops_theme Report Files
- `report/ops_document_extras.xml` - Layout-level extras for all documents
- `report/ops_external_layout.xml` - Custom document layout
- `report/ops_report_css.xml` - Report CSS controller

### Static Assets
- `ops_matrix_accounting/static/src/css/ops_internal_report.css`
- `ops_matrix_accounting/static/src/css/ops_report.css`
- `ops_matrix_accounting/static/src/scss/ops_corporate_reports.scss`
- `ops_matrix_core/static/src/css/ops_external_report.css`
- `ops_matrix_core/static/src/js/report_action_override.js`

---

## 2. WIZARD DEFINITIONS (TransientModels)

### 2.1 Report Wizards (ops_matrix_accounting)

#### OpsBaseReportWizard (Abstract Base Class)
- **File:** `wizard/ops_base_report_wizard.py` (750 lines)
- **_name:** `ops.base.report.wizard`
- **Inherits:** `ops.intelligence.security.mixin`
- **Key Fields:** `report_template_id`, `company_id`, `currency_id`, `report_title`, `filter_summary`, `record_count`
- **Abstract Methods:** `_get_engine_name()`, `_get_report_titles()`, `_get_scalar_fields_for_template()`, `_get_m2m_fields_for_template()`, `_get_report_data()`, `_return_report_action()`
- **Actions:** `action_generate_report()`, `action_save_template()`, `action_view_report()`

#### OpsGeneralLedgerWizardEnhanced
- **File:** `wizard/ops_general_ledger_wizard_enhanced.py` (2,074 lines)
- **_name:** `ops.general.ledger.wizard.enhanced`
- **Inherits:** `ops.base.report.wizard`
- **Description:** Matrix Financial Intelligence
- **Report Types:** GL, Trial Balance, P&L, Balance Sheet, Cash Flow, Aged Partner, Partner Ledger, Statement of Account
- **Fields:** `report_type` (Selection: 8 types), `date_from`, `date_to`, `target_move`, `account_ids`, `partner_ids`, `branch_ids`, `business_unit_ids`, + many more filters
- **Actions:** `action_generate_report()` → dispatches to type-specific handlers

#### OpsTreasuryReportWizard
- **File:** `wizard/ops_treasury_report_wizard.py` (717 lines)
- **_name:** `ops.treasury.report.wizard`
- **Inherits:** `ops.base.report.wizard`
- **Report Types:** registry, maturity, on_hand
- **Fields:** `report_type`, `date_from`, `date_to`, `as_of_date`, `pdc_type`, `pdc_status`, `branch_ids`

#### OpsAssetReportWizard
- **File:** `wizard/ops_asset_report_wizard.py` (853 lines)
- **_name:** `ops.asset.report.wizard`
- **Inherits:** `ops.base.report.wizard`
- **Report Types:** register, forecast, disposal, movement
- **Fields:** `report_type`, `date_from`, `date_to`, `as_of_date`, `branch_ids`, `business_unit_ids`, `asset_category_ids`, `asset_state`

#### OpsInventoryReportWizard
- **File:** `wizard/ops_inventory_report_wizard.py` (1,266 lines)
- **_name:** `ops.inventory.report.wizard`
- **Inherits:** `ops.base.report.wizard`
- **Report Types:** valuation, aging, negative, movement
- **Fields:** `report_type`, `date_to`, `date_from`, `ops_branch_ids`, `location_ids`, `product_category_ids`, `product_ids`, aging periods, `group_by`
- **Actions:** `action_view_quants()`, `action_export_excel()`

#### OpsDailyReportsWizard
- **File:** `wizard/ops_daily_reports_wizard.py` (1,093 lines)
- **_name:** Three separate models: `ops.cash.book.wizard`, `ops.day.book.wizard`, `ops.bank.book.wizard`
- **Fields:** `date_from`, `date_to`, `journal_ids`, `branch_ids`

#### OpsConsolidationIntelligenceWizard
- **File:** `wizard/ops_consolidation_intelligence_wizard.py` (215 lines)
- **_name:** `ops.consolidation.intelligence.wizard`
- **Report Types:** company_consolidation, branch_pl, bu_report, consolidated_bs
- **Fields:** `report_type`, `company_id`, `date_from`, `date_to`, `branch_ids`, `business_unit_ids`, `report_detail_level`, `compare_with_previous`

#### OpsBudgetVsActualWizard
- **File:** `wizard/ops_budget_vs_actual_wizard.py` (193 lines)
- **_name:** `ops.budget.vs.actual.wizard`
- **Fields:** `date_from`, `date_to`, `budget_ids`, `branch_ids`, `business_unit_ids`

### 2.2 Asset/Period Wizards (ops_matrix_accounting)

| Wizard | _name | File | Lines | Key Actions |
|--------|-------|------|-------|-------------|
| Asset Depreciation | `ops.asset.depreciation.wizard` | `ops_asset_depreciation_wizard.py` | 123 | `action_generate_entries()` |
| Asset Disposal | `ops.asset.disposal.wizard` | `ops_asset_disposal_wizard.py` | 130 | `action_dispose_asset()` |
| Asset Impairment | `ops.asset.impairment.wizard` | `ops_asset_impairment_wizard.py` | 134 | `action_record_impairment()` |
| Period Close | `ops.period.close.wizard` | `ops_period_close_wizard.py` | 182 | `action_close_period()` |
| FX Revaluation | `ops.fx.revaluation.wizard` | `ops_fx_revaluation_wizard.py` | 246 | FX adjustment entries |
| 3-Way Match Override | `ops.three.way.match.override.wizard` | `ops_three_way_match_override_wizard.py` | 189 | `action_request_override()` |

### 2.3 Core Wizards (ops_matrix_core)

| Wizard | _name | File | Key Purpose |
|--------|-------|------|-------------|
| Apply Report Template | `apply.report.template.wizard` | `apply_report_template_wizard.py` | Apply saved template |
| Approval Recall | `ops.approval.recall.wizard` | `ops_approval_recall_wizard.py` | Recall approval |
| Approval Reject | `ops.approval.reject.wizard` | `ops_approval_reject_wizard.py` | Reject approval |
| Audit Evidence | `ops.audit.evidence.wizard` | `ops_audit_evidence_wizard.py` | Export 7+ audit sheets to Excel |
| Governance Violations | `ops.governance.violation.report` | `ops_governance_violation_report.py` | Violation dashboard |
| Persona Drift | `ops.persona.drift.wizard` | `ops_persona_drift_wizard.py` | Drift detection |
| SO Import | `ops.sale.order.import.wizard` | `ops_sale_order_import_wizard.py` | Excel line import |
| PO Import | `ops.purchase.order.import.wizard` | `ops_purchase_order_import_wizard.py` | Excel line import |
| Secure Export | `ops.secure.export.wizard` | `ops_secure_export_wizard.py` | Matrix-filtered export |

---

## 3. REPORT CLASSES (AbstractModels)

### 3.1 Financial Report Parsers

#### OpsFinancialReportParser
- **_name:** `report.ops_matrix_accounting.report_ops_financial_document`
- **File:** `report/ops_financial_report_parser.py`
- **Supports:** GL, P&L, BS, TB, CF, Aged, Partner, SoA
- **Color System:** Meridian Design (Executive Gold #C9A962, Corporate Red #DA291C)
- **Phase 14:** Hierarchical CoA support for P&L and BS
- **Key Methods:** `_get_report_values()`, `_transform_enhanced_data()`, `_build_hierarchy()`
- **Sub-classes (inherit):**
  - `OpsFinancialMinimalReportParser` → `report.ops_matrix_accounting.report_ops_financial_minimal`
  - `OpsBalanceSheetCorporateParser` → `report.ops_matrix_accounting.report_balance_sheet_corporate`
  - `OpsTrialBalanceCorporateParser` → `report.ops_matrix_accounting.report_trial_balance_corporate`
  - `OpsProfitLossCorporateParser` → `report.ops_matrix_accounting.report_profit_loss_corporate`
  - `OpsCashFlowCorporateParser` → `report.ops_matrix_accounting.report_cash_flow_corporate`
  - `OpsAgedPartnerCorporateParser` → `report.ops_matrix_accounting.report_aged_partner_corporate`
  - `OpsGeneralLedgerCorporateParser` → `report.ops_matrix_accounting.report_general_ledger_corporate` (alias)
  - V2 variants: `OpsBalanceSheetV2Parser`, `OpsTrialBalanceV2Parser`, `OpsProfitLossV2Parser`, `OpsCashFlowV2Parser`, `OpsAgedPartnerV2Parser`

#### OpsFinancialMatrixReportParser
- **_name:** `report.ops_matrix_accounting.report_financial_matrix`
- **File:** `report/ops_financial_matrix_report.py`
- **Purpose:** Transform wizard data → template format for all 8 report types

#### OpsGeneralLedgerReportMinimal
- **_name:** `report.ops_matrix_accounting.report_general_ledger_minimal`
- **File:** `report/ops_general_ledger_report.py` (548 lines)
- **Key Features:** Running balance, account type badges, dual-mode (pre-computed OR query fallback)
- **Sub-classes:**
  - `OpsGeneralLedgerReportLegacy` → `report.ops_matrix_accounting.report_general_ledger` (backward compat)
  - `OpsGeneralLedgerReportCorporate` → `report.ops_matrix_accounting.report_general_ledger_corporate`

#### OpsAssetRegisterReport
- **_name:** `report.ops_matrix_accounting.report_asset_register`
- **File:** `report/ops_asset_register_report.py`

### 3.2 Corporate Report Parsers

**File:** `report/ops_corporate_report_parsers.py`

| Class | _name | Purpose |
|-------|-------|---------|
| `OpsCashBookCorporateParser` | `report.ops_matrix_accounting.report_cash_book_corporate` | Cash Book |
| `OpsDayBookCorporateParser` | `report.ops_matrix_accounting.report_day_book_corporate` | Day Book |
| `OpsBankBookCorporateParser` | `report.ops_matrix_accounting.report_bank_book_corporate` | Bank Book |
| `OpsAssetRegisterCorporateParser` | `report.ops_matrix_accounting.report_asset_register_corp` | Asset Register |
| `OpsDepreciationScheduleCorporateParser` | `report.ops_matrix_accounting.report_depreciation_sched_corp` | Depreciation Schedule |
| `OpsPDCRegistryCorporateParser` | `report.ops_matrix_accounting.report_treasury_registry_corporate` | PDC Registry |
| `OpsPDCMaturityCorporateParser` | `report.ops_matrix_accounting.report_treasury_maturity_corporate` | PDC Maturity |
| `OpsPDCsInHandCorporateParser` | `report.ops_matrix_accounting.report_treasury_on_hand_corporate` | PDCs in Hand |
| `OpsCompanyConsolidationCorporateParser` | `report.ops_matrix_accounting.report_company_consol` | Company Consolidation P&L |
| `OpsBranchPLCorporateParser` | `report.ops_matrix_accounting.report_branch_pl_document` | Branch P&L |
| `OpsBUProfitabilityCorporateParser` | `report.ops_matrix_accounting.report_business_unit_document` | BU Profitability |
| `OpsConsolidatedBSCorporateParser` | `report.ops_matrix_accounting.report_consol_balance_sheet` | Consolidated Balance Sheet |
| `OpsPartnerLedgerCorporateParser` | `report.ops_matrix_accounting.report_partner_ledger_corporate` | Partner Ledger |
| `OpsBudgetVsActualCorporateParser` | `report.ops_matrix_accounting.report_budget_vs_actual_corporate` | Budget vs Actual |

### 3.3 Excel Report Generators

| Class | _name | Inherits | Supports |
|-------|-------|----------|----------|
| `OpsFinancialMatrixXlsx` | `report.ops_matrix_accounting.report_financial_matrix_xlsx` | `ops.xlsx.abstract` | GL, TB, P&L, BS, CF, Aged, Partner, SoA |
| `OpsGeneralLedgerXlsx` | `report.ops_matrix_accounting.report_general_ledger_xlsx` | `ops.xlsx.abstract` | General Ledger |
| `AssetIntelligenceXLSX` | `report.ops_matrix_accounting.report_asset_xlsx` | `ops.xlsx.abstract` | Register, Forecast, Disposal, Movement |
| `OpsTreasuryReportXlsx` | `report.ops_matrix_accounting.report_treasury_xlsx` | `ops.xlsx.abstract` | Registry, Maturity, On Hand |

### 3.4 Report Helper Model

#### OpsReportHelpers
- **_name:** `ops.report.helpers`
- **File (accounting):** `models/ops_report_helpers.py`
- **File (theme):** `models/ops_report_helpers.py` -- **CONFLICT: same _name, last-loaded wins!**
- **Methods:** `amount_to_words()`, `get_color_scheme()`, `format_amount()`, `format_percentage()`, `get_value_class()`, `get_aging_class()`, `get_variance_class()`, `classify_margin()`, `verify_balance()`, `get_report_context()`

---

## 4. REPORT ACTIONS

### 4.1 ir.actions.report Records (42 total from database)

#### Financial Intelligence (16 reports, model: `ops.general.ledger.wizard.enhanced`)

| DB ID | Name | report_name |
|-------|------|-------------|
| 649 | General Ledger (Minimal) | `ops_matrix_accounting.report_general_ledger_minimal` |
| 666 | General Ledger (Corporate) | `ops_matrix_accounting.report_general_ledger_corporate` |
| 667 | General Ledger | `ops_matrix_accounting.report_general_ledger_corporate` |
| 660 | OPS Trial Balance Report | `ops_matrix_accounting.report_trial_balance_corporate` |
| 661 | OPS Profit & Loss Statement | `ops_matrix_accounting.report_profit_loss_corporate` |
| 664 | OPS Balance Sheet | `ops_matrix_accounting.report_balance_sheet_corporate` |
| 662 | OPS Cash Flow Statement | `ops_matrix_accounting.report_cash_flow_corporate` |
| 663 | OPS Aged Partner Balance | `ops_matrix_accounting.report_aged_partner_corporate` |
| 681 | Trial Balance (V2) | `ops_matrix_accounting.report_trial_balance_v2` |
| 682 | Profit & Loss (V2) | `ops_matrix_accounting.report_profit_loss_v2` |
| 680 | Balance Sheet (V2) | `ops_matrix_accounting.report_balance_sheet_v2` |
| 683 | Cash Flow Statement (V2) | `ops_matrix_accounting.report_cash_flow_v2` |
| 684 | Aged Partner Balance (V2) | `ops_matrix_accounting.report_aged_partner_v2` |
| 694 | Partner Ledger | `ops_matrix_accounting.report_partner_ledger_corporate` |
| 650 | Financial Report (Minimal) | `ops_matrix_accounting.report_ops_financial_minimal` |
| 665 | Financial Report (Legacy) | `ops_matrix_accounting.report_ops_financial_minimal` |

#### Asset Reports (5 reports, model: `ops.asset.report.wizard`)

| DB ID | Name | report_name |
|-------|------|-------------|
| 651 | Asset Register Report (Corporate) | `ops_matrix_accounting.report_asset_register_corp` |
| 652 | Depreciation Schedule (Corporate) | `ops_matrix_accounting.report_depreciation_sched_corp` |
| 653 | Depreciation Forecast (Corporate) | `ops_matrix_accounting.report_depreciation_sched_corp` |
| 654 | Asset Disposal Analysis (Corporate) | `ops_matrix_accounting.report_asset_register_corp` |
| 655 | Asset Movement Report (Corporate) | `ops_matrix_accounting.report_asset_register_corp` |

#### Daily Reports (3 reports)

| DB ID | Name | Model | report_name |
|-------|------|-------|-------------|
| 675 | Cash Book | `ops.cash.book.wizard` | `report_cash_book_corporate` |
| 676 | Day Book | `ops.day.book.wizard` | `report_day_book_corporate` |
| 677 | Bank Book | `ops.bank.book.wizard` | `report_bank_book_corporate` |

#### Treasury Reports (3 reports, model: `ops.treasury.report.wizard`)

| DB ID | Name | report_name |
|-------|------|-------------|
| 672 | PDC Registry Report (Corporate) | `report_treasury_registry_corporate` |
| 673 | PDC Maturity Analysis (Corporate) | `report_treasury_maturity_corporate` |
| 674 | PDCs in Hand (Corporate) | `report_treasury_on_hand_corporate` |

#### Inventory Reports (4 reports, model: `ops.inventory.report.wizard`)

| DB ID | Name | report_name |
|-------|------|-------------|
| 668 | Stock Valuation Report (Corporate) | `report_inventory_valuation_document_corporate` |
| 669 | Inventory Aging Report (Corporate) | `report_inventory_aging_document_corporate` |
| 670 | Movement Analysis Report (Corporate) | `report_inventory_movement_document_corporate` |
| 671 | Negative Stock Alert (Corporate) | `report_inventory_negative_document_corporate` |

#### Consolidation Reports (4 reports)

| DB ID | Name | Model | report_name |
|-------|------|-------|-------------|
| 656 | Company Consolidation P&L | `ops.company.consolidation` | `report_company_consol` |
| 657 | Branch P&L Report | `ops.branch.report` | `report_branch_pl_document` |
| 658 | BU Profitability Report | `ops.business.unit.report` | `report_business_unit_document` |
| 659 | Consolidated Balance Sheet | `ops.consolidated.balance.sheet` | `report_consol_balance_sheet` |

#### Budget Report (1)

| DB ID | Name | Model | report_name |
|-------|------|-------|-------------|
| 695 | Budget vs Actual | `ops.budget.vs.actual.wizard` | `report_budget_vs_actual_corporate` |

#### Document Reports (8 reports, ops_matrix_core + ops_matrix_accounting)

| DB ID | Name | Model | Module |
|-------|------|-------|--------|
| 581 | Quotation / Order (OPS) | `sale.order` | core |
| 582 | Purchase Order (OPS) | `purchase.order` | core |
| 583 | Delivery Note (OPS) | `stock.picking` | core |
| 584 | Products Availability | `sale.order` | core |
| 585 | SO Documentation | `sale.order` | core |
| 586 | Stock Availability Report | `sale.order` | core |
| 678 | Invoice / Credit Note (OPS) | `account.move` | accounting |
| 679 | Payment Receipt (OPS) | `account.payment` | accounting |

---

## 5. QWEB REPORT TEMPLATES

### Layout Hierarchy
```
Level 1: web.html_container (multi-page wrapper)
Level 2: web.external_layout (customer docs) OR ops_corporate_pdf_layout (internal reports)
Level 3: Custom components (ops_internal_layout_v2, ops_section_header_v2, etc.)
```

### Template Inventory by File

| File | Template Count | Total Lines | Layout Used |
|------|---------------|-------------|-------------|
| `ops_general_ledger_template.xml` | 1 | 620 | ops_corporate_pdf_layout |
| `ops_financial_reports_v2.xml` | 4 | 1,765 | ops_internal_layout_v2 |
| `ops_balance_sheet_v2.xml` | 1 | 340 | ops_internal_layout_v2 |
| `ops_inventory_report_templates.xml` | 4 | 1,903 | web.html_container |
| `ops_consolidated_report_templates.xml` | 4 | 700+ | ops_corporate_pdf_layout |
| `ops_asset_report_templates.xml` | 1+ | 620+ | ops_corporate_pdf_layout |
| `ops_daily_report_templates.xml` | 3 | 600+ | ops_corporate_pdf_layout |
| `ops_treasury_report_templates.xml` | 3 | 500+ | ops_corporate_pdf_layout |
| `ops_budget_vs_actual_corporate.xml` | 1 | 500+ | ops_corporate_pdf_layout |
| `ops_partner_ledger_corporate.xml` | 1 | — | ops_corporate_pdf_layout |
| `ops_report_invoice.xml` | 2 | 354 | web.external_layout |
| `ops_report_payment.xml` | 2 | 200+ | ops_report_css |
| `ops_report_quotation.xml` | 2 | 300+ | web.external_layout |
| `ops_report_delivery.xml` | 2 | 300+ | ops_report_css |
| `ops_report_purchase.xml` | 2 | 300+ | ops_report_css |

### Color Variables Used in Templates
- `pc` - Primary color (brand)
- `tc` - Text on primary
- `pl` - Primary light
- `pd` - Primary dark
- `bt` - Body text color

---

## 6. MENU ITEMS

### Menu Hierarchy (Report-Related)

```
Accounting
├── Operations (seq 20)
│   ├── Bank Reconciliation → action_ops_bank_reconciliation
│   ├── FX Revaluation → action_ops_fx_revaluation_wizard
│   └── Generate Asset Entries → action_ops_asset_depreciation_wizard
│
├── Assets (seq 25)
│   ├── Assets → action_ops_asset
│   ├── Depreciation Lines → action_ops_asset_depreciation
│   └── Asset Categories → action_ops_asset_category
│
├── Analytics & Planning (seq 30)
│   ├── Analytic Items
│   ├── Budgets → action_ops_budget
│   └── Leases (IFRS 16) → action_ops_lease
│
├── Period Close (seq 35)
│   ├── Fiscal Periods
│   ├── Close Checklist
│   └── Branch Period Locks
│
├── Reports
│   ├── Financial Intelligence (seq 10)
│   │   ├── Matrix Financial Intelligence (seq 10) → action_ops_general_ledger_wizard_enhanced
│   │   ├── Consolidation Intelligence (seq 15) → action_ops_consolidation_intelligence_wizard
│   │   ├── Treasury Intelligence (seq 20) → action_ops_treasury_report_wizard
│   │   └── Asset Intelligence (seq 30) → action_ops_asset_report_wizard
│   │
│   ├── Analysis (seq 40)
│   │   ├── Invoice Analysis → account.action_account_invoice_report_all
│   │   └── Analytic Report → account.action_analytic_reporting
│   │
│   ├── PDC Reports (seq 60) → action_ops_pdc_reports
│   │
│   └── Daily Reports (seq 70)
│       ├── Cash Book (seq 10) → action_ops_cash_book_wizard
│       ├── Day Book (seq 20) → action_ops_day_book_wizard
│       └── Bank Book (seq 30) → action_ops_bank_book_wizard
│
├── Configuration
│   ├── Report Structures (BS/PL) (seq 70)
│   │   ├── Balance Sheet Structure → action_ops_financial_report_config_bs
│   │   ├── Profit & Loss Structure → action_ops_financial_report_config_pl
│   │   └── All Report Lines → action_ops_financial_report_config
│   └── Reporting Audit (seq 99) → action_ops_report_audit
│
├── Customers → PDC Receivable (seq 50)
└── Vendors → PDC Payable (seq 50)

Stock
└── Inventory Intelligence (seq 50)
    ├── Inventory Analysis (seq 10) → action_ops_inventory_report_wizard
    ├── Stock Valuation (seq 20) → action_ops_inventory_valuation_quick
    ├── Aging Analysis (seq 30) → action_ops_inventory_aging_quick
    ├── Negative Stock Alerts (seq 40) → action_ops_inventory_negative_quick
    └── Movement Analysis (seq 50) → action_ops_inventory_movement_quick
```

### Security Group Assignments

| Menu Section | Security Groups |
|-------------|-----------------|
| Financial Intelligence | group_ops_cfo, group_ops_finance_manager, group_ops_accountant, group_ops_executive, group_ops_bu_leader, group_ops_branch_manager |
| Consolidation Intelligence | group_ops_cfo, group_ops_finance_manager, group_ops_accountant, group_ops_executive |
| Treasury Intelligence | group_ops_treasury, group_ops_finance_manager, group_ops_cfo |
| Asset Intelligence | group_ops_finance_manager, group_ops_cfo, group_ops_accountant, group_ops_executive |
| Daily Reports | group_ops_cfo, group_ops_finance_manager, group_ops_accountant, group_ops_executive, group_ops_bu_leader, group_ops_branch_manager |
| Bank Book | group_ops_treasury, group_ops_finance_manager, group_ops_cfo |
| Report Configuration | group_ops_admin_power, group_ops_finance_manager |
| Inventory Intelligence | group_ops_inventory_manager, group_ops_finance_manager, group_ops_cfo, group_ops_executive |

### Deprecated Menus (deactivated)
- menu_ops_accounting_root, menu_ops_accounting_management, menu_ops_bank_treasury
- menu_ops_asset_management, menu_ops_asset_configuration, menu_ops_period_end
- menu_ops_fx_revaluation, menu_ops_balance_sheet_wizard, menu_ops_automation
- menu_ops_budget, menu_ops_bank_reconciliation, menu_ops_lease
- menu_ops_accounting_reports, menu_ops_trend_analysis

---

## 7. MANIFEST & IMPORT CHAINS

### 7.1 Module Dependencies
```
ops_theme (base, web, mail)
    ↑
ops_matrix_core (base, mail, analytic, account, sale, sale_management, purchase, stock, stock_account, hr, spreadsheet_dashboard, ops_theme)
    ↑
ops_matrix_accounting (account, purchase, stock, ops_matrix_core, analytic)
    ↑
ops_kpi (base, web, mail, sale, purchase, account, stock, ops_matrix_core, ops_matrix_accounting)
```

### 7.2 Manifest Data Files (Report/Wizard flagged)

**ops_matrix_accounting** (24 report + 8 wizard files in manifest):

Report files:
- `report/ops_corporate_report_layout.xml`
- `report/components/ops_corporate_report_components.xml`
- `report/ops_report_layout.xml`
- `report/ops_report_minimal_styles.xml`
- `report/ops_general_ledger_template.xml`
- `report/ops_general_ledger_minimal.xml`
- `report/ops_financial_report_template.xml`
- `report/ops_financial_report_minimal.xml`
- `report/ops_asset_report_templates.xml`
- `report/ops_consolidated_report_templates.xml`
- `report/ops_inventory_report_templates.xml`
- `report/ops_treasury_report_templates.xml`
- `report/ops_daily_report_templates.xml`
- `report/ops_report_invoice.xml`
- `report/ops_report_payment.xml`
- `report/ops_internal_layout_v2.xml`
- `report/ops_financial_reports_v2.xml`
- `report/ops_balance_sheet_v2.xml`
- `report/ops_partner_ledger_corporate.xml`
- `report/ops_budget_vs_actual_corporate.xml`
- `data/report_templates.xml`
- `data/report_templates_extra.xml`

Wizard files:
- `wizard/ops_asset_depreciation_wizard_views.xml`
- `wizard/ops_asset_disposal_wizard_views.xml`
- `wizard/ops_treasury_report_wizard_views.xml`
- `wizard/ops_period_close_wizard_views.xml`
- `wizard/ops_asset_report_wizard_views.xml`
- `wizard/ops_three_way_match_override_wizard_views.xml`
- `wizard/ops_consolidation_intelligence_wizard_views.xml`
- `wizard/ops_budget_vs_actual_wizard_views.xml`

**ops_matrix_core** (6 report + 7 wizard files):
- `report/ops_report_quotation.xml`, `report/ops_report_purchase.xml`, `report/ops_report_delivery.xml`
- `reports/ops_products_availability_report.xml`, `reports/sale_order_documentation_report.xml`, `reports/sale_order_availability_report.xml`
- 7 wizard view XML files

**ops_theme** (3 report files):
- `report/ops_report_css.xml`, `report/ops_document_extras.xml`, `report/ops_external_layout.xml`

### 7.3 Import Chains

**ops_matrix_accounting/report/__init__.py:**
```python
from . import ops_financial_report_parser     # QWeb parser (P&L, BS, TB, CF, Aged)
from . import ops_financial_matrix_report     # Matrix report parser
from . import ops_general_ledger_report       # GL parser (Minimal + Legacy + Corporate)
from . import ops_asset_register_report       # Asset register parser
from . import ops_corporate_report_parsers    # 14 corporate parsers
from . import excel_styles                    # Shared Excel styles
from . import ops_xlsx_abstract               # Base XLSX class
from . import ops_asset_register_xlsx         # Asset Excel
from . import ops_general_ledger_xlsx         # GL Excel
from . import ops_financial_matrix_xlsx       # Financial Matrix Excel
from . import ops_treasury_report_xlsx        # Treasury Excel
```

**ops_matrix_accounting/wizard/__init__.py:**
```python
from . import ops_base_report_wizard          # MUST BE FIRST (base class)
from . import ops_general_ledger_wizard_enhanced
from . import ops_treasury_report_wizard
from . import ops_asset_report_wizard
from . import ops_asset_depreciation_wizard
from . import ops_asset_disposal_wizard
from . import ops_inventory_report_wizard
from . import ops_period_close_wizard
from . import ops_three_way_match_override_wizard
from . import ops_daily_reports_wizard
from . import ops_asset_impairment_wizard
from . import ops_fx_revaluation_wizard
from . import ops_consolidation_intelligence_wizard
from . import ops_budget_vs_actual_wizard
```

---

## 8. DATABASE TRUTH

### 8.1 Installed Transient Models (37 wizard models)

| Model | Display Name |
|-------|-------------|
| `ops.general.ledger.wizard.enhanced` | Matrix Financial Intelligence |
| `ops.treasury.report.wizard` | Treasury Intelligence - PDC Report Wizard |
| `ops.asset.report.wizard` | Asset Intelligence - Fixed Asset Report Wizard |
| `ops.inventory.report.wizard` | Inventory Intelligence Report Wizard |
| `ops.consolidation.intelligence.wizard` | Consolidation Intelligence Wizard |
| `ops.budget.vs.actual.wizard` | Budget vs Actual Report Wizard |
| `ops.cash.book.wizard` | Cash Book Report |
| `ops.day.book.wizard` | Day Book Report |
| `ops.bank.book.wizard` | Bank Book Report |
| `ops.asset.depreciation.wizard` | Asset Depreciation Batch Wizard |
| `ops.asset.disposal.wizard` | Asset Disposal Wizard |
| `ops.asset.impairment.wizard` | Asset Impairment Wizard |
| `ops.asset.register.wizard` | Asset Register Report Wizard |
| `ops.period.close.wizard` | Period Close Wizard |
| `ops.fx.revaluation.wizard` | Foreign Currency Revaluation |
| `ops.three.way.match.override.wizard` | Three-Way Match Override Wizard |
| `ops.company.consolidation` | Company-Level Consolidated P&L Report |
| `ops.branch.report` | Branch-Level Profit & Loss Report |
| `ops.business.unit.report` | Business Unit Profitability Report |
| `ops.consolidated.balance.sheet` | Group-Level Balance Sheet Consolidation |
| `ops.matrix.profitability.analysis` | Matrix Profitability Analysis (Branch x BU) |
| `ops.trend.analysis` | Trend Analysis & Variance Reporting |
| `ops.approval.recall.wizard` | Recall Approval Request Wizard |
| `ops.approval.reject.wizard` | Reject Approval Request Wizard |
| `ops.audit.evidence.wizard` | Audit Evidence Export Wizard |
| `ops.governance.violation.report` | Governance Violations Dashboard & Reporting |
| `ops.persona.drift.wizard` | Persona Drift Detection Wizard |
| `ops.persona.drift.result` | Persona Drift Analysis Result |
| `ops.sale.order.import.wizard` | Import Sale Order Lines from Excel |
| `ops.purchase.order.import.wizard` | Import Purchase Order Lines from Excel |
| `ops.secure.export.wizard` | OPS Secure Data Export |
| `ops.report.template.save.wizard` | Save Report Template Wizard |
| `ops.journal.template.wizard` | Create Entry from Template |
| `ops.credit.override.wizard` | Credit Override Request |
| `ops.bank.statement.import.wizard` | Import Bank Statement |
| `ops.analytic.setup` | OPS Analytic Accounting Setup Helper |
| `ops.dashboard.config` | OPS Dashboard Configuration |

### 8.2 OPS Menu Tree (62 menu items in database)

All 62 menus under OPS hierarchy confirmed installed and active. See Section 6 for full hierarchy.

---

## 9. SECURITY RULES

### 9.1 ACL Pattern (214 total records for OPS models)

Standard 4-tier pattern:

| Tier | Group | Typical Access |
|------|-------|---------------|
| 1 | OPS Administrator | Full CRUD |
| 2 | OPS Manager | Full CRUD (sometimes no unlink) |
| 3 | OPS User | Read-only |
| 4 | Role / Administrator | Full CRUD (system) |

### 9.2 Notable Security Observations

- **Audit logs are immutable:** `ops.audit.log` and `ops.corporate.audit.log` are read-only even for OPS Administrator
- **KPI models** use separate groups: `KPI Manager` and `KPI User`
- **Wizard ACLs:** Generally permissive (transient models auto-clean)
- **Report template ACLs:** Multiple entries exist for `ops.report.template` (Odoo uses most permissive match)
- **Duplicate model names:** Both `ops.inter.branch.transfer` and `ops.interbranch.transfer` have ACL entries (possible rename artifact)

---

## 10. COMPANY REPORT FIELDS & COLORS

### 10.1 res.company Fields

#### From ops_theme (`res_company_branding.py`):

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `ops_primary_color` | Char | #1e293b | UI brand color |
| `ops_secondary_color` | Char | #3b82f6 | Accent color |
| `ops_success_color` | Char | #10b981 | Success indicators |
| `ops_warning_color` | Char | #f59e0b | Warning messages |
| `ops_danger_color` | Char | #ef4444 | Error/danger |
| `ops_report_logo_position` | Selection | left | Logo placement: left/center/right |
| `ops_amount_words_lang` | Selection | en | Language: en/ar/both |
| `ops_show_external_badge` | Boolean | True | "Powered by OPS" badge |
| `ops_show_bank_details` | Boolean | True | Bank details on docs |
| `ops_show_signature_block` | Boolean | True | Signature lines |
| `ops_signature_label_1` | Char | Prepared By | First signature label |
| `ops_signature_label_2` | Char | Authorized Signatory | Second signature label |
| `ops_signature_label_3` | Char | Customer Acceptance | Third signature label |
| `ops_show_amount_words` | Boolean | True | Amount in words |
| `ops_report_terms` | Html | — | Default T&Cs |
| `ops_theme_preset` | Selection | corporate_blue | Theme preset |

#### From ops_matrix_accounting (`res_company.py`):

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `ops_report_primary_color` | Char | #5B6BBB | Report headers/borders |
| `ops_report_text_on_primary` | Char | #FFFFFF | Text on colored backgrounds |
| `ops_report_body_text_color` | Char | #1a1a1a | Report body text |

### 10.2 Helper Methods

**`company.get_ops_report_settings()`** (ops_theme) returns:
```python
{
    'show_words': bool,
    'show_bank': bool,
    'show_sig': bool,
    'words_lang': 'en'|'ar'|'both',
    'sig1': 'Prepared By',
    'sig2': 'Authorized Signatory',
    'sig3': 'Customer Acceptance',
    'report_terms': html_content,
}
```

**`company.get_report_primary_light()`** (ops_matrix_accounting): 15% opacity blend with white
**`company.get_report_primary_dark()`** (ops_matrix_accounting): 75% of original brightness

### 10.3 Color System (Meridian Standard)

Used by `ops_corporate_report_parsers.py`:
- **Executive Gold:** #C9A962
- **Corporate Red:** #DA291C
- **Primary Black:** #1A1A1A
- **Emerald Green:** #059669
- **Amber Warning:** #d97706
- **Blue Info:** #2563eb
- **Grays:** #94a3b8, #cccccc

### 10.4 Theme Presets

| Preset | Primary | Secondary | Navbar |
|--------|---------|-----------|--------|
| corporate_blue | #1e293b | #3b82f6 | dark |
| modern_dark | #111827 | #6366f1 | dark |
| clean_light | #f8fafc | #0ea5e9 | light |
| enterprise_navy | — | — | dark |
| warm_professional | — | — | dark |

### 10.5 CSS Variable Endpoint

**Route:** `/ops_theme/variables.css` (auth: public, no-cache)
Serves dynamic CSS variables: `--ops-primary`, `--ops-secondary`, `--ops-success`, `--ops-warning`, `--ops-danger`, `--ops-navbar-bg`, `--ops-card-shadow`, `--ops-border-radius`, `--ops-report-header-bg`

---

## REPORT TYPE SUPPORT MATRIX

| Report Type | Wizard | QWeb Parser | QWeb Template | XLSX | Menu Entry |
|-------------|--------|-------------|---------------|------|------------|
| General Ledger | GL Wizard Enhanced | OpsGeneralLedgerReportMinimal | report_general_ledger_corporate | OpsGeneralLedgerXlsx | Matrix Financial Intelligence |
| Trial Balance | GL Wizard Enhanced | OpsFinancialReportParser | report_trial_balance_corporate / v2 | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Profit & Loss | GL Wizard Enhanced | OpsFinancialReportParser | report_profit_loss_corporate / v2 | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Balance Sheet | GL Wizard Enhanced | OpsFinancialReportParser | report_balance_sheet_corporate / v2 | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Cash Flow | GL Wizard Enhanced | OpsFinancialReportParser | report_cash_flow_corporate / v2 | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Aged Partner | GL Wizard Enhanced | OpsFinancialReportParser | report_aged_partner_corporate / v2 | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Partner Ledger | GL Wizard Enhanced | OpsPartnerLedgerCorporateParser | report_partner_ledger_corporate | — | Matrix Financial Intelligence |
| Statement of Account | GL Wizard Enhanced | OpsFinancialMatrixReportParser | — | OpsFinancialMatrixXlsx | Matrix Financial Intelligence |
| Cash Book | OpsCashBookWizard | OpsCashBookCorporateParser | report_cash_book_corporate | — | Daily Reports > Cash Book |
| Day Book | OpsDayBookWizard | OpsDayBookCorporateParser | report_day_book_corporate | — | Daily Reports > Day Book |
| Bank Book | OpsBankBookWizard | OpsBankBookCorporateParser | report_bank_book_corporate | — | Daily Reports > Bank Book |
| Asset Register | OpsAssetReportWizard | OpsAssetRegisterCorporateParser | report_asset_register_corp | AssetIntelligenceXLSX | Asset Intelligence |
| Depreciation Schedule | OpsAssetReportWizard | OpsDepreciationScheduleCorporateParser | report_depreciation_sched_corp | AssetIntelligenceXLSX | Asset Intelligence |
| Asset Disposal | OpsAssetReportWizard | OpsAssetRegisterCorporateParser | report_asset_register_corp | AssetIntelligenceXLSX | Asset Intelligence |
| Asset Movement | OpsAssetReportWizard | OpsAssetRegisterCorporateParser | report_asset_register_corp | AssetIntelligenceXLSX | Asset Intelligence |
| PDC Registry | OpsTreasuryReportWizard | OpsPDCRegistryCorporateParser | report_treasury_registry_corporate | OpsTreasuryReportXlsx | Treasury Intelligence |
| PDC Maturity | OpsTreasuryReportWizard | OpsPDCMaturityCorporateParser | report_treasury_maturity_corporate | OpsTreasuryReportXlsx | Treasury Intelligence |
| PDCs in Hand | OpsTreasuryReportWizard | OpsPDCsInHandCorporateParser | report_treasury_on_hand_corporate | OpsTreasuryReportXlsx | Treasury Intelligence |
| Stock Valuation | OpsInventoryReportWizard | — | report_inventory_valuation_document_corporate | — | Inventory Intelligence |
| Inventory Aging | OpsInventoryReportWizard | — | report_inventory_aging_document_corporate | — | Inventory Intelligence |
| Movement Analysis | OpsInventoryReportWizard | — | report_inventory_movement_document_corporate | — | Inventory Intelligence |
| Negative Stock | OpsInventoryReportWizard | — | report_inventory_negative_document_corporate | — | Inventory Intelligence |
| Company Consolidation P&L | OpsConsolidationWizard | OpsCompanyConsolidationCorporateParser | report_company_consol | — | Consolidation Intelligence |
| Branch P&L | OpsConsolidationWizard | OpsBranchPLCorporateParser | report_branch_pl_document | — | Consolidation Intelligence |
| BU Profitability | OpsConsolidationWizard | OpsBUProfitabilityCorporateParser | report_business_unit_document | — | Consolidation Intelligence |
| Consolidated BS | OpsConsolidationWizard | OpsConsolidatedBSCorporateParser | report_consol_balance_sheet | — | Consolidation Intelligence |
| Budget vs Actual | OpsBudgetVsActualWizard | OpsBudgetVsActualCorporateParser | report_budget_vs_actual_corporate | — | (in Financial Intelligence) |
| Quotation/SO | (document binding) | — | report_ops_quotation | — | Print on sale.order |
| Purchase Order | (document binding) | — | report_ops_purchase | — | Print on purchase.order |
| Delivery Note | (document binding) | — | report_ops_delivery | — | Print on stock.picking |
| Invoice/Credit Note | (document binding) | — | report_ops_invoice | — | Print on account.move |
| Payment Receipt | (document binding) | — | report_ops_payment | — | Print on account.payment |

---

## KNOWN ISSUES

1. **Model _name Conflict:** `ops.report.helpers` defined in BOTH `ops_matrix_accounting` and `ops_theme` without `_inherit`. Last-loaded module wins, losing methods from the other.

2. **Duplicate report_name:** Asset reports (IDs 651, 654, 655) share `report_asset_register_corp` template. Depreciation reports (IDs 652, 653) share `report_depreciation_sched_corp`. Wizard switches template at runtime.

3. **Duplicate ACL entries:** `ops.report.template` has multiple `Role / Administrator` and `Role / User` entries with different permissions.

4. **Deprecated items in codebase:** Several wizards and menus deactivated but files still present.

---

## SUCCESS CHECKLIST

- [x] All 4 modules scanned
- [x] Every wizard identified with fields and actions (23 wizards)
- [x] Every report class identified with _name (27+ AbstractModel classes)
- [x] Every QWeb template identified (50+ templates in 21 files)
- [x] Every menu item mapped (62 active menus)
- [x] Database state captured (42 report actions, 37 transient models, 214 ACLs)
- [x] Report color/company fields documented
- [x] No files modified

---

*End of Report Mining Audit*
