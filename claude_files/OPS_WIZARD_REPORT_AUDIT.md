# OPS Framework — Wizard & Report Template Audit Report

**Generated**: 2026-02-05
**Scope**: ops_matrix_core, ops_matrix_accounting, ops_dashboard, ops_theme

---

## SUMMARY

| Category | Count |
|----------|-------|
| Wizard Models (TransientModel) | 51 |
| Wizard Views | 18 |
| Wizard Actions | 12 |
| QWeb Report Actions | 30 |
| QWeb Template Files | 14 |
| QWeb Templates (total) | 61 |

---

## PHASE 1: WIZARD MODEL INVENTORY

### ops_matrix_core (21 wizards)

| Model Name | Class | Description |
|------------|-------|-------------|
| `apply.report.template.wizard` | ApplyReportTemplateWizard | Apply Report Template Wizard |
| `ops.sale.order.import.wizard` | OpsSaleOrderImportWizard | Import Sale Order Lines from Excel |
| `ops.approval.recall.wizard` | OpsApprovalRecallWizard | Recall Approval Request Wizard |
| `ops.audit.evidence.wizard` | OpsAuditEvidenceWizard | Audit Evidence Export Wizard |
| `ops.governance.violation.report` | OpsGovernanceViolationReport | Governance Violations Dashboard & Reporting |
| `ops.secure.export.wizard` | OpsSecureExportWizard | OPS Secure Data Export |
| `ops.purchase.order.import.wizard` | OpsPurchaseOrderImportWizard | Import Purchase Order Lines from Excel |
| `sale.order.import.wizard` | SaleOrderImportWizard | Sale Order Import from Excel Wizard |
| `ops.approval.reject.wizard` | OpsApprovalRejectWizard | Reject Approval Request Wizard |
| `three.way.match.override.wizard` | ThreeWayMatchOverrideWizard | Three-Way Match Override Wizard |
| `ops.welcome.wizard` | OpsWelcomeWizard | OPS Matrix Setup Wizard |
| `ops.welcome.wizard.branch` | OpsWelcomeWizardBranch | Welcome Wizard - Branch Line |
| `ops.welcome.wizard.business.unit` | OpsWelcomeWizardBusinessUnit | Welcome Wizard - Business Unit Line |
| `ops.persona.drift.wizard` | OpsPersonaDriftWizard | Persona Drift Detection Wizard |
| `ops.persona.drift.result` | OpsPersonaDriftResult | Persona Drift Analysis Result |
| `ops.dashboard.config` | OpsDashboardConfig | OPS Dashboard Configuration |
| `ops.security.resolve.wizard` | OpsSecurityResolveWizard | Resolve Security Event |
| `ops.ip.test.wizard` | OpsIpTestWizard | Test IP Rule |
| `ops.analytic.setup` | OpsAnalyticSetup | OPS Analytic Accounting Setup Helper |

### ops_matrix_accounting (30 wizards)

| Model Name | Class | Description |
|------------|-------|-------------|
| `ops.balance.sheet.wizard` | OpsBalanceSheetWizard | Corporate Balance Sheet Wizard |
| `ops.inventory.report.wizard` | OpsInventoryReportWizard | Inventory Intelligence Report Wizard |
| `ops.asset.disposal.wizard` | OpsAssetDisposalWizard | Asset Disposal Wizard |
| `ops.fx.revaluation.wizard` | OpsFxRevaluationWizard | Foreign Currency Revaluation |
| `ops.fx.revaluation.line` | OpsFxRevaluationLine | FX Revaluation Line |
| `ops.three.way.match.override.wizard` | OpsThreeWayMatchOverrideWizard | Three-Way Match Override Wizard |
| `ops.asset.impairment.wizard` | OpsAssetImpairmentWizard | Asset Impairment Wizard |
| `ops.period.close.wizard` | OpsPeriodCloseWizard | Period Close Wizard |
| `ops.general.ledger.wizard.enhanced` | OpsGeneralLedgerWizardEnhanced | Matrix Financial Intelligence |
| `ops.cash.book.wizard` | OpsCashBookWizard | Cash Book Report |
| `ops.day.book.wizard` | OpsDayBookWizard | Day Book Report |
| `ops.bank.book.wizard` | OpsBankBookWizard | Bank Book Report |
| `ops.treasury.report.wizard` | OpsTreasuryReportWizard | Treasury Intelligence - PDC Report Wizard |
| `ops.asset.depreciation.wizard` | OpsAssetDepreciationWizard | Asset Depreciation Batch Wizard |
| `ops.asset.report.wizard` | OpsAssetReportWizard | Asset Intelligence - Fixed Asset Report Wizard |
| `ops.asset.register.wizard` | AssetRegisterWizard | Asset Register Report Wizard |
| `ops.general.ledger.wizard` | OpsGeneralLedgerWizard | General Ledger Report Wizard |
| `ops.financial.report.wizard` | OpsFinancialReportWizard | Financial Report Wizard (DEPRECATED) |
| `ops.report.template.save.wizard` | OpsReportTemplateSaveWizard | Save Report Template Wizard |
| `ops.company.consolidation` | OpsCompanyConsolidation | Company-Level Consolidated P&L Report |
| `ops.branch.report` | OpsBranchReport | Branch-Level Profit & Loss Report |
| `ops.business.unit.report` | OpsBusinessUnitReport | Business Unit Profitability Report |
| `ops.consolidated.balance.sheet` | OpsConsolidatedBalanceSheet | Group-Level Balance Sheet Consolidation |
| `ops.matrix.profitability.analysis` | OpsMatrixProfitabilityAnalysis | Matrix Profitability Analysis (Branch x BU) |
| `ops.bank.statement.import.wizard` | OpsBankStatementImportWizard | Import Bank Statement |
| `ops.credit.override.wizard` | OpsCreditOverrideWizard | Credit Override Request |
| `ops.trend.analysis` | OpsTrendAnalysis | Trend Analysis & Variance Reporting |
| `ops.journal.template.wizard` | OpsJournalTemplateWizard | Create Entry from Template |

---

## PHASE 2: WIZARD VIEW INVENTORY

### ops_matrix_core Wizard Views

| File | View ID | Model |
|------|---------|-------|
| `wizard/ops_sale_order_import_wizard_views.xml` | `view_ops_sale_order_import_wizard_form` | ops.sale.order.import.wizard |
| | `view_order_form_import_button` | sale.order |
| | ACTION: `action_ops_sale_order_import_wizard` | ops.sale.order.import.wizard |
| `wizard/ops_approval_recall_wizard_views.xml` | `view_ops_approval_recall_wizard_form` | ops.approval.recall.wizard |
| `wizard/three_way_match_override_wizard_views.xml` | `three_way_match_override_wizard_form_view` | three.way.match.override.wizard |
| `wizard/ops_purchase_order_import_wizard_views.xml` | `view_ops_purchase_order_import_wizard_form` | ops.purchase.order.import.wizard |
| | `view_purchase_order_form_import_button` | purchase.order |
| | ACTION: `action_ops_purchase_order_import_wizard` | ops.purchase.order.import.wizard |
| `wizard/sale_order_import_wizard_views.xml` | `view_sale_order_import_wizard_form` | sale.order.import.wizard |
| | `view_sale_order_import_error_form` | sale.order.import.wizard |
| | `view_sale_order_import_success_form` | sale.order.import.wizard |
| | ACTION: `action_sale_order_import_wizard` | sale.order.import.wizard |
| `wizard/ops_secure_export_wizard_views.xml` | `ops_secure_export_wizard_form` | ops.secure.export.wizard |
| | ACTION: `action_ops_secure_export_wizard` | ops.secure.export.wizard |
| `wizard/ops_approval_reject_wizard_views.xml` | `view_ops_approval_reject_wizard_form` | ops.approval.reject.wizard |
| `wizard/apply_report_template_wizard_views.xml` | `view_apply_report_template_wizard` | apply.report.template.wizard |
| | ACTION: `action_apply_report_template_wizard` | apply.report.template.wizard |

### ops_matrix_accounting Wizard Views

| File | View ID | Model |
|------|---------|-------|
| `wizard/ops_balance_sheet_wizard_views.xml` | `view_ops_balance_sheet_wizard_form` | ops.balance.sheet.wizard |
| | ACTION: `action_ops_balance_sheet_wizard` | ops.balance.sheet.wizard |
| `wizard/ops_treasury_report_wizard_views.xml` | `view_ops_treasury_report_wizard_form` | ops.treasury.report.wizard |
| | ACTION: `action_ops_treasury_report_wizard` | ops.treasury.report.wizard |
| `wizard/ops_asset_report_wizard_views.xml` | `view_ops_asset_report_wizard_form` | ops.asset.report.wizard |
| | ACTION: `action_ops_asset_report_wizard` | ops.asset.report.wizard |
| `wizard/ops_asset_depreciation_wizard_views.xml` | `view_ops_asset_depreciation_wizard_form` | ops.asset.depreciation.wizard |
| | ACTION: `action_ops_asset_depreciation_wizard` | ops.asset.depreciation.wizard |
| `wizard/ops_asset_disposal_wizard_views.xml` | `view_ops_asset_disposal_wizard_form` | ops.asset.disposal.wizard |
| `wizard/ops_three_way_match_override_wizard_views.xml` | `view_ops_three_way_match_override_wizard_form` | ops.three.way.match.override.wizard |
| `wizard/ops_period_close_wizard_views.xml` | `view_ops_period_close_wizard_form` | ops.period.close.wizard |
| | ACTION: `action_ops_period_close_wizard` | ops.period.close.wizard |
| `wizard/ops_asset_report_wizard.xml` | `ops_asset_register_report_view_form` | ops.asset.register.report |
| | ACTION: `action_ops_asset_register_report` | ops.asset.register.report |

---

## PHASE 3: QWEB REPORT ACTIONS

### ops_matrix_core Reports (4)

| Report ID | Name | Model | Template | Type |
|-----------|------|-------|----------|------|
| `action_report_sale_order_availability` | Availability Report (Legacy) | sale.order | `ops_matrix_core.report_sale_order_availability` | qweb-pdf |
| `action_report_sale_order_documentation` | SO Documentation | sale.order | `ops_matrix_core.report_sale_order_documentation` | qweb-pdf |
| `action_report_products_availability` | Products Availability | sale.order | `ops_matrix_core.report_products_availability_document` | qweb-pdf |

### ops_matrix_accounting Reports (26)

| Report ID | Name | Model | Template | Type |
|-----------|------|-------|----------|------|
| `action_report_cash_flow_corporate` | OPS Cash Flow Statement | ops.general.ledger.wizard.enhanced | `report_cash_flow_corporate` | qweb-pdf |
| `action_report_trial_balance_corporate` | OPS Trial Balance Report | ops.general.ledger.wizard.enhanced | `report_trial_balance_corporate` | qweb-pdf |
| `action_report_profit_loss_corporate` | OPS Profit & Loss Statement | ops.general.ledger.wizard.enhanced | `report_profit_loss_corporate` | qweb-pdf |
| `action_report_aged_partner_corporate` | OPS Aged Partner Balance | ops.general.ledger.wizard.enhanced | `report_aged_partner_corporate` | qweb-pdf |
| `action_report_ops_financial` | Financial Report (Legacy) | ops.general.ledger.wizard.enhanced | `report_ops_financial_minimal` | qweb-pdf |
| `report_treasury_registry_pdf` | PDC Registry Report | ops.treasury.report.wizard | `report_treasury_registry_corporate` | qweb-pdf |
| `report_treasury_maturity_pdf` | PDC Maturity Analysis | ops.treasury.report.wizard | `report_treasury_maturity_corporate` | qweb-pdf |
| `report_treasury_xlsx` | Treasury Report (Excel) | ops.treasury.report.wizard | `report_treasury_xlsx` | xlsx |
| `report_treasury_on_hand_pdf` | PDCs in Hand | ops.treasury.report.wizard | `report_treasury_on_hand_corporate` | qweb-pdf |
| `report_company_consolidation_pdf` | Company Consolidation Report | ops.company.consolidation | `report_company_consolidation_document` | qweb-pdf |
| `report_branch_pl_pdf` | Branch P&L Report | ops.branch.report | `report_branch_pl_document` | qweb-pdf |
| `report_business_unit_pdf` | Business Unit Report | ops.business.unit.report | `report_business_unit_document` | qweb-pdf |
| `report_consolidated_balance_sheet_pdf` | Consolidated Balance Sheet | ops.consolidated.balance.sheet | `report_consolidated_balance_sheet_document` | qweb-pdf |
| `action_report_cash_book` | Cash Book | ops.cash.book.wizard | `report_cash_book_corporate` | qweb-pdf |
| `action_report_day_book` | Day Book | ops.day.book.wizard | `report_day_book_corporate` | qweb-pdf |
| `action_report_bank_book` | Bank Book | ops.bank.book.wizard | `report_bank_book_corporate` | qweb-pdf |
| `action_report_ops_financial_minimal` | Financial Report (Minimal) | ops.general.ledger.wizard.enhanced | `report_ops_financial_minimal` | qweb-pdf |
| `action_report_balance_sheet_corporate` | Balance Sheet (Corporate) | ops.balance.sheet.wizard | `report_balance_sheet_corporate_document` | qweb-pdf |
| `action_report_general_ledger_minimal` | General Ledger (Minimal) | ops.general.ledger.wizard.enhanced | `report_general_ledger_minimal` | qweb-pdf |
| `action_report_general_ledger` | General Ledger | ops.general.ledger.wizard.enhanced | `report_general_ledger_corporate` | qweb-pdf |
| `action_report_general_ledger_corporate` | General Ledger (Corporate) | ops.general.ledger.wizard.enhanced | `report_general_ledger_corporate` | qweb-pdf |
| `report_inventory_negative_pdf` | Negative Stock Alert | ops.inventory.report.wizard | `report_inventory_negative_document_corporate` | qweb-pdf |
| `report_inventory_movement_pdf` | Movement Analysis Report | ops.inventory.report.wizard | `report_inventory_movement_document_corporate` | qweb-pdf |
| `report_inventory_valuation_pdf` | Stock Valuation Report | ops.inventory.report.wizard | `report_inventory_valuation_document_corporate` | qweb-pdf |
| `report_inventory_aging_pdf` | Inventory Aging Report | ops.inventory.report.wizard | `report_inventory_aging_document_corporate` | qweb-pdf |
| `report_asset_register_pdf` | Asset Register Report | ops.asset.report.wizard | `report_asset_register_document_corporate` | qweb-pdf |
| `report_asset_xlsx` | Asset Intelligence Report (Excel) | ops.asset.report.wizard | `report_asset_xlsx` | xlsx |
| `report_depreciation_schedule_pdf` | Depreciation Schedule Report | ops.asset.report.wizard | `report_depreciation_schedule_document_corporate` | qweb-pdf |

---

## PHASE 4: QWEB TEMPLATE FILES

### ops_matrix_core Templates (3 files, 3 templates)

| File | Templates |
|------|-----------|
| `reports/sale_order_availability_report.xml` | `report_sale_order_availability` |
| `reports/sale_order_documentation_report.xml` | `report_sale_order_documentation` |
| `reports/ops_products_availability_report.xml` | `report_products_availability_document` |

### ops_matrix_accounting Templates (11 files, 58 templates)

| File | Templates |
|------|-----------|
| `report/ops_report_layout.xml` | `ops_report_styles`, `ops_external_layout`, `ops_minimal_layout`, `ops_consulting_layout`, `ops_meridian_header_template`, `ops_header_split_template`, `ops_equation_bar_template`, `ops_meta_bar_template`, `ops_format_amount`, `ops_report_footer_template`, `ops_notes_template`, `ops_report_header_template`, `ops_info_box_template` |
| `report/ops_financial_report_template.xml` | `report_trial_balance_corporate`, `report_profit_loss_corporate`, `report_cash_flow_corporate`, `report_aged_partner_corporate` |
| `report/ops_treasury_report_templates.xml` | `report_treasury_registry_corporate`, `report_treasury_maturity_corporate`, `report_treasury_on_hand_corporate` |
| `report/ops_consolidated_report_templates.xml` | `report_company_consolidation_document`, `report_branch_pl_document`, `report_business_unit_document`, `report_consolidated_balance_sheet_document` |
| `report/ops_daily_report_templates.xml` | `report_cash_book_corporate`, `report_day_book_corporate`, `report_bank_book_corporate` |
| `report/ops_financial_report_minimal.xml` | `report_ops_financial_minimal`, `report_minimal_balance_sheet_content`, `report_minimal_profit_loss_content`, `report_minimal_trial_balance_content`, `report_minimal_cash_flow_content`, `report_minimal_generic_content` |
| `report/components/ops_corporate_report_components.xml` | `report_corporate_header`, `report_corporate_title`, `report_filter_bar`, `report_notes_section`, `report_corporate_footer`, `format_corporate_amount`, `format_corporate_percentage`, `format_corporate_variance`, `section_header_*` (6), `table_header_row`, `subtotal_row`, `grand_total_row`, `balance_check_badge`, `kpi_card` |
| `report/ops_report_minimal_styles.xml` | `ops_minimal_report_styles`, `ops_minimal_external_layout`, `ops_minimal_format_amount`, `ops_minimal_header`, `ops_minimal_footer`, `ops_minimal_notes` |
| `report/ops_balance_sheet_template.xml` | `report_balance_sheet_corporate_document` |
| `report/ops_general_ledger_minimal.xml` | `report_general_ledger_minimal` |
| `report/ops_general_ledger_template.xml` | `report_general_ledger_corporate` |
| `report/ops_inventory_report_templates.xml` | `report_inventory_valuation_document_corporate`, `report_inventory_aging_document_corporate`, `report_inventory_movement_document_corporate`, `report_inventory_negative_document_corporate` |
| `report/ops_asset_report_templates.xml` | `report_asset_register_document_corporate`, `report_depreciation_schedule_document_corporate` |

---

## PHASE 5: WIZARD → REPORT LINKAGE

### Confirmed Linkages

| Wizard Model | Report References |
|--------------|-------------------|
| `ops.cash.book.wizard` | `ops_matrix_accounting.action_report_cash_book` |
| `ops.day.book.wizard` | `ops_matrix_accounting.action_report_day_book` |
| `ops.bank.book.wizard` | `ops_matrix_accounting.action_report_bank_book` |

### Implicit Linkages (by Model Match)

| Wizard Model | Report Action | Report Template |
|--------------|---------------|-----------------|
| `ops.general.ledger.wizard.enhanced` | `action_report_general_ledger_corporate` | `report_general_ledger_corporate` |
| `ops.general.ledger.wizard.enhanced` | `action_report_trial_balance_corporate` | `report_trial_balance_corporate` |
| `ops.general.ledger.wizard.enhanced` | `action_report_profit_loss_corporate` | `report_profit_loss_corporate` |
| `ops.general.ledger.wizard.enhanced` | `action_report_cash_flow_corporate` | `report_cash_flow_corporate` |
| `ops.general.ledger.wizard.enhanced` | `action_report_aged_partner_corporate` | `report_aged_partner_corporate` |
| `ops.balance.sheet.wizard` | `action_report_balance_sheet_corporate` | `report_balance_sheet_corporate_document` |
| `ops.treasury.report.wizard` | `report_treasury_registry_pdf` | `report_treasury_registry_corporate` |
| `ops.treasury.report.wizard` | `report_treasury_maturity_pdf` | `report_treasury_maturity_corporate` |
| `ops.treasury.report.wizard` | `report_treasury_on_hand_pdf` | `report_treasury_on_hand_corporate` |
| `ops.company.consolidation` | `report_company_consolidation_pdf` | `report_company_consolidation_document` |
| `ops.branch.report` | `report_branch_pl_pdf` | `report_branch_pl_document` |
| `ops.business.unit.report` | `report_business_unit_pdf` | `report_business_unit_document` |
| `ops.consolidated.balance.sheet` | `report_consolidated_balance_sheet_pdf` | `report_consolidated_balance_sheet_document` |
| `ops.inventory.report.wizard` | Multiple inventory reports | Multiple inventory templates |
| `ops.asset.report.wizard` | `report_asset_register_pdf` | `report_asset_register_document_corporate` |

---

## OBSERVATIONS & ISSUES

### 1. Duplicate Wizard Models
- `ops.governance.violation.report` defined twice in ops_matrix_core
- `sale.order.import.wizard` defined twice with different descriptions
- `ops.asset.register.wizard` (AssetRegisterWizard) defined twice in ops_matrix_accounting

### 2. Wizards Without Views
The following wizard models may be missing dedicated views:
- `ops.audit.evidence.wizard`
- `ops.governance.violation.report`
- `ops.welcome.wizard` (and child models)
- `ops.persona.drift.wizard`
- `ops.dashboard.config`
- `ops.security.resolve.wizard`
- `ops.ip.test.wizard`
- `ops.analytic.setup`
- `ops.fx.revaluation.wizard`
- `ops.asset.impairment.wizard`
- `ops.general.ledger.wizard` (legacy)
- `ops.financial.report.wizard` (deprecated)
- `ops.report.template.save.wizard`
- `ops.matrix.profitability.analysis`
- `ops.bank.statement.import.wizard`
- `ops.credit.override.wizard`
- `ops.trend.analysis`
- `ops.journal.template.wizard`

### 3. Model/View Mismatch
- `ops_asset_register_report_view_form` references `ops.asset.register.report` but wizard is `ops.asset.register.wizard`

### 4. Duplicate Three-Way Match Wizards
- `three.way.match.override.wizard` in ops_matrix_core
- `ops.three.way.match.override.wizard` in ops_matrix_accounting

---

## REMEDIATION PRIORITIES

1. **High**: Resolve duplicate model definitions
2. **High**: Fix model/view mismatches
3. **Medium**: Create views for wizards that need UI access
4. **Medium**: Consolidate duplicate three-way match wizards
5. **Low**: Remove deprecated wizards or mark clearly

---

**Audit Complete**: 2026-02-05
