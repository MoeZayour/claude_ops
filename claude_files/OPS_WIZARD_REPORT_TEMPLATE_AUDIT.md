# OPS Framework — Wizard & Report Template Audit

**Generated**: 2026-02-05
**Scope**: ops_matrix_core, ops_matrix_accounting, ops_dashboard, ops_theme

---

## EXECUTIVE SUMMARY

| Category | Count |
|----------|-------|
| Wizard Models (TransientModel) | 32 |
| Wizard Views | 17 |
| Wizard Actions | 13 |
| Report Actions (ir.actions.report) | 27 |
| QWeb Templates | 45+ |

---

## PHASE 1: WIZARD MODEL INVENTORY

### ops_matrix_core (16 wizards)

| Model Name | File | Purpose |
|------------|------|---------|
| `apply.report.template.wizard` | wizard/apply_report_template_wizard.py | Apply report templates |
| `ops.approval.recall.wizard` | wizard/ops_approval_recall_wizard.py | Recall approvals |
| `ops.approval.reject.wizard` | wizard/ops_approval_reject_wizard.py | Reject approvals |
| `ops.audit.evidence.wizard` | wizard/ops_audit_evidence_wizard.py | Audit evidence collection |
| `ops.persona.drift.wizard` | wizard/ops_persona_drift_wizard.py | Persona drift analysis |
| `ops.purchase.order.import.wizard` | wizard/ops_purchase_order_import_wizard.py | Import purchase orders |
| `ops.sale.order.import.wizard` | wizard/ops_sale_order_import_wizard.py | Import sale orders |
| `ops.secure.export.wizard` | wizard/ops_secure_export_wizard.py | Secure data export |
| `ops.welcome.wizard` | wizard/ops_welcome_wizard.py | Welcome/onboarding |
| `sale.order.import.wizard` | wizard/sale_order_import_wizard.py | Legacy SO import |
| `three.way.match.override.wizard` | wizard/three_way_match_override_wizard.py | 3-way match override |
| `ops.analytic.setup` | models/ops_analytic_setup.py | Analytic setup (wizard-like) |
| `ops.dashboard.config` | models/ops_dashboard_config.py | Dashboard config |
| `ops.governance.violation.report` | wizard/ops_governance_violation_report.py | Governance violations |
| `ops.ip.whitelist` | models/ops_ip_whitelist.py | IP whitelist management |
| `ops.security.audit` | models/ops_security_audit.py | Security audit |

### ops_matrix_accounting (16 wizards)

| Model Name | File | Purpose |
|------------|------|---------|
| `ops.asset.depreciation.wizard` | wizard/ops_asset_depreciation_wizard.py | Run depreciation |
| `ops.asset.disposal.wizard` | wizard/ops_asset_disposal_wizard.py | Dispose assets |
| `ops.asset.impairment.wizard` | wizard/ops_asset_impairment_wizard.py | Asset impairment |
| `ops.asset.report.wizard` | wizard/ops_asset_report_wizard.py | Asset reports |
| `ops.balance.sheet.wizard` | wizard/ops_balance_sheet_wizard.py | Balance sheet |
| `ops.bank.reconciliation` | models/ops_bank_reconciliation.py | Bank reconciliation |
| `ops.cash.book.wizard` | wizard/ops_daily_reports_wizard.py | Cash/Day/Bank book |
| `ops.company.consolidation` | models/ops_consolidated_reporting.py | Company consolidation |
| `ops.followup` | models/ops_followup.py | Payment followup |
| `ops.fx.revaluation.wizard` | wizard/ops_fx_revaluation_wizard.py | FX revaluation |
| `ops.general.ledger.wizard.enhanced` | wizard/ops_general_ledger_wizard_enhanced.py | **Master financial wizard** |
| `ops.inventory.report.wizard` | wizard/ops_inventory_report_wizard.py | Inventory reports |
| `ops.journal.template` | models/ops_journal_template.py | Journal templates |
| `ops.period.close.wizard` | wizard/ops_period_close_wizard.py | Period close |
| `ops.three.way.match.override.wizard` | wizard/ops_three_way_match_override_wizard.py | 3-way match |
| `ops.treasury.report.wizard` | wizard/ops_treasury_report_wizard.py | Treasury/PDC reports |

---

## PHASE 2: WIZARD VIEW INVENTORY

### ops_matrix_core Wizard Views

| XML ID | Model | File |
|--------|-------|------|
| `view_ops_sale_order_import_wizard_form` | ops.sale.order.import.wizard | wizard/ops_sale_order_import_wizard_views.xml |
| `view_ops_approval_recall_wizard_form` | ops.approval.recall.wizard | wizard/ops_approval_recall_wizard_views.xml |
| `three_way_match_override_wizard_form_view` | three.way.match.override.wizard | wizard/three_way_match_override_wizard_views.xml |
| `view_ops_purchase_order_import_wizard_form` | ops.purchase.order.import.wizard | wizard/ops_purchase_order_import_wizard_views.xml |
| `view_sale_order_import_wizard_form` | sale.order.import.wizard | wizard/sale_order_import_wizard_views.xml |
| `ops_secure_export_wizard_form` | ops.secure.export.wizard | wizard/ops_secure_export_wizard_views.xml |
| `view_ops_approval_reject_wizard_form` | ops.approval.reject.wizard | wizard/ops_approval_reject_wizard_views.xml |
| `view_apply_report_template_wizard` | apply.report.template.wizard | wizard/apply_report_template_wizard_views.xml |

### ops_matrix_accounting Wizard Views

| XML ID | Model | File |
|--------|-------|------|
| `view_ops_balance_sheet_wizard_form` | ops.balance.sheet.wizard | wizard/ops_balance_sheet_wizard_views.xml |
| `view_ops_treasury_report_wizard_form` | ops.treasury.report.wizard | wizard/ops_treasury_report_wizard_views.xml |
| `view_ops_asset_report_wizard_form` | ops.asset.report.wizard | wizard/ops_asset_report_wizard_views.xml |
| `view_ops_asset_depreciation_wizard_form` | ops.asset.depreciation.wizard | wizard/ops_asset_depreciation_wizard_views.xml |
| `view_ops_asset_disposal_wizard_form` | ops.asset.disposal.wizard | wizard/ops_asset_disposal_wizard_views.xml |
| `view_ops_three_way_match_override_wizard_form` | ops.three.way.match.override.wizard | wizard/ops_three_way_match_override_wizard_views.xml |
| `view_ops_period_close_wizard_form` | ops.period.close.wizard | wizard/ops_period_close_wizard_views.xml |
| `ops_asset_register_report_view_form` | ops.asset.report.wizard | wizard/ops_asset_report_wizard.xml |

---

## PHASE 3: REPORT ACTIONS (ir.actions.report)

### ops_matrix_core Reports (3)

| XML ID | Name | Model | Template |
|--------|------|-------|----------|
| `action_report_sale_order_availability` | Availability Report | sale.order | `ops_matrix_core.report_sale_order_availability` |
| `action_report_sale_order_documentation` | SO Documentation | sale.order | `ops_matrix_core.report_sale_order_documentation` |
| `action_report_products_availability` | Products Availability | sale.order | `ops_matrix_core.report_products_availability_document` |

### ops_matrix_accounting Reports (24)

#### Financial Reports (via ops.general.ledger.wizard.enhanced)

| XML ID | Name | Template |
|--------|------|----------|
| `action_report_general_ledger_corporate` | General Ledger | `report_general_ledger_corporate` |
| `action_report_trial_balance_corporate` | Trial Balance | `report_trial_balance_corporate` |
| `action_report_profit_loss_corporate` | P&L Statement | `report_profit_loss_corporate` |
| `action_report_cash_flow_corporate` | Cash Flow | `report_cash_flow_corporate` |
| `action_report_aged_partner_corporate` | Aged Partner | `report_aged_partner_corporate` |
| `action_report_balance_sheet_corporate` | Balance Sheet | `report_balance_sheet_corporate_document` |
| `action_report_general_ledger_minimal` | GL (Minimal) | `report_general_ledger_minimal` |
| `action_report_ops_financial_minimal` | Financial (Minimal) | `report_ops_financial_minimal` |

#### Treasury Reports (via ops.treasury.report.wizard)

| XML ID | Name | Template |
|--------|------|----------|
| `report_treasury_registry_pdf` | PDC Registry | `report_treasury_registry_corporate` |
| `report_treasury_maturity_pdf` | PDC Maturity | `report_treasury_maturity_corporate` |
| `report_treasury_on_hand_pdf` | PDCs in Hand | `report_treasury_on_hand_corporate` |
| `report_treasury_xlsx` | Treasury (Excel) | `report_treasury_xlsx` |

#### Daily Reports (via ops.cash.book.wizard)

| XML ID | Name | Template |
|--------|------|----------|
| `action_report_cash_book` | Cash Book | `report_cash_book_corporate` |
| `action_report_day_book` | Day Book | `report_day_book_corporate` |
| `action_report_bank_book` | Bank Book | `report_bank_book_corporate` |

#### Inventory Reports (via ops.inventory.report.wizard)

| XML ID | Name | Template |
|--------|------|----------|
| `report_inventory_valuation_pdf` | Stock Valuation | `report_inventory_valuation_document_corporate` |
| `report_inventory_aging_pdf` | Inventory Aging | `report_inventory_aging_document_corporate` |
| `report_inventory_movement_pdf` | Movement Analysis | `report_inventory_movement_document_corporate` |
| `report_inventory_negative_pdf` | Negative Stock | `report_inventory_negative_document_corporate` |

#### Asset Reports (via ops.asset.report.wizard)

| XML ID | Name | Template |
|--------|------|----------|
| `report_asset_register_pdf` | Asset Register | `report_asset_register_document_corporate` |
| `report_depreciation_schedule_pdf` | Depreciation Schedule | `report_depreciation_schedule_document_corporate` |
| `report_asset_xlsx` | Asset (Excel) | `report_asset_xlsx` |

#### Consolidation Reports

| XML ID | Name | Template |
|--------|------|----------|
| `report_company_consolidation_pdf` | Company Consolidation | `report_company_consolidation_document` |
| `report_branch_pl_pdf` | Branch P&L | `report_branch_pl_document` |
| `report_business_unit_pdf` | Business Unit | `report_business_unit_document` |
| `report_consolidated_balance_sheet_pdf` | Consolidated BS | `report_consolidated_balance_sheet_document` |

---

## PHASE 4: QWEB TEMPLATE FILES

### ops_matrix_core Templates

| File | Templates |
|------|-----------|
| reports/sale_order_availability_report.xml | `report_sale_order_availability` |
| reports/sale_order_documentation_report.xml | `report_sale_order_documentation` |
| reports/ops_products_availability_report.xml | `report_products_availability_document` |

### ops_matrix_accounting Templates

#### Layout Templates (report/ops_report_layout.xml)
- `ops_report_styles` - Corporate CSS styles
- `ops_external_layout` - External layout wrapper
- `ops_minimal_layout` - Minimal layout
- `ops_consulting_layout` - Consulting layout
- `ops_meridian_header_template` - Meridian header
- `ops_header_split_template` - Split header
- `ops_equation_bar_template` - Equation bar
- `ops_meta_bar_template` - Meta bar
- `ops_format_amount` - Amount formatting
- `ops_report_footer_template` - Footer
- `ops_notes_template` - Notes section
- `ops_report_header_template` - Header
- `ops_info_box_template` - Info box

#### Financial Templates (report/ops_financial_report_template.xml)
- `report_trial_balance_corporate`
- `report_profit_loss_corporate`
- `report_cash_flow_corporate`
- `report_aged_partner_corporate`

#### General Ledger (report/ops_general_ledger_template.xml)
- `report_general_ledger_corporate`

#### Balance Sheet (report/ops_balance_sheet_template.xml)
- `report_balance_sheet_corporate_document`

#### Minimal Templates (report/ops_financial_report_minimal.xml)
- `report_ops_financial_minimal`
- `report_minimal_balance_sheet_content`
- `report_minimal_profit_loss_content`
- `report_minimal_trial_balance_content`
- `report_minimal_cash_flow_content`
- `report_minimal_generic_content`

#### Treasury Templates (report/ops_treasury_report_templates.xml)
- `report_treasury_registry_corporate`
- `report_treasury_maturity_corporate`
- `report_treasury_on_hand_corporate`

#### Daily Report Templates (report/ops_daily_report_templates.xml)
- `report_cash_book_corporate`
- `report_day_book_corporate`
- `report_bank_book_corporate`

#### Inventory Templates (report/ops_inventory_report_templates.xml)
- `report_inventory_valuation_document_corporate`
- `report_inventory_aging_document_corporate`
- `report_inventory_movement_document_corporate`
- `report_inventory_negative_document_corporate`

#### Asset Templates (report/ops_asset_report_templates.xml)
- `report_asset_register_document_corporate`
- `report_depreciation_schedule_document_corporate`

#### Consolidation Templates (report/ops_consolidated_report_templates.xml)
- `report_company_consolidation_document`
- `report_branch_pl_document`
- `report_business_unit_document`
- `report_consolidated_balance_sheet_document`

#### Component Library (report/components/ops_corporate_report_components.xml)
- `report_corporate_header`
- `report_corporate_title`
- `report_filter_bar`
- `report_notes_section`
- `report_corporate_footer`
- `format_corporate_amount`
- `format_corporate_percentage`
- `format_corporate_variance`
- `section_header_*` (financial, asset, liability, equity, revenue, expense, treasury)
- `table_header_row`
- `subtotal_row`
- `grand_total_row`
- `balance_check_badge`
- `kpi_card`

---

## PHASE 5: WIZARD → REPORT LINKAGE

### ops.general.ledger.wizard.enhanced → Reports

```python
report_xml_ids = {
    'gl': 'ops_matrix_accounting.action_report_general_ledger_corporate',
    'tb': 'ops_matrix_accounting.action_report_trial_balance_corporate',
    'pl': 'ops_matrix_accounting.action_report_profit_loss_corporate',
    'bs': 'ops_matrix_accounting.action_report_balance_sheet_corporate',
    'cf': 'ops_matrix_accounting.action_report_cash_flow_corporate',
    'aged': 'ops_matrix_accounting.action_report_aged_partner_corporate',
    'partner': 'ops_matrix_accounting.action_report_general_ledger_corporate',
    'soa': 'ops_matrix_accounting.action_report_general_ledger_corporate',
}
```

### ops.treasury.report.wizard → Reports

```python
report_refs = {
    'registry': 'ops_matrix_accounting.report_treasury_registry_pdf',
    'maturity': 'ops_matrix_accounting.report_treasury_maturity_pdf',
    'on_hand': 'ops_matrix_accounting.report_treasury_on_hand_pdf',
}
```

### ops.cash.book.wizard → Reports

```python
# Direct references in action methods:
'ops_matrix_accounting.action_report_cash_book'
'ops_matrix_accounting.action_report_day_book'
'ops_matrix_accounting.action_report_bank_book'
```

### ops.inventory.report.wizard → Reports

```python
report_names = {
    'valuation': 'ops_matrix_accounting.report_inventory_valuation_pdf',
    'aging': 'ops_matrix_accounting.report_inventory_aging_pdf',
    'negative': 'ops_matrix_accounting.report_inventory_negative_pdf',
    'movement': 'ops_matrix_accounting.report_inventory_movement_pdf',
}
```

### ops.asset.report.wizard → Reports

```python
report_names = {
    'register': 'ops_matrix_accounting.report_asset_register',
    'forecast': 'ops_matrix_accounting.report_asset_forecast',
    'disposal': 'ops_matrix_accounting.report_asset_disposal',
    'movement': 'ops_matrix_accounting.report_asset_movement',
}
```

---

## IDENTIFIED ISSUES

### 1. Duplicate Wizard Definitions
- `ops.welcome.wizard` defined 3 times in wizard/ops_welcome_wizard.py
- `ops.company.consolidation` defined 5 times in models/ops_consolidated_reporting.py
- `ops.cash.book.wizard` defined 3 times (includes day_book, bank_book variants)

### 2. Missing Views
Some wizards lack dedicated view files:
- `ops.audit.evidence.wizard`
- `ops.persona.drift.wizard`
- `ops.fx.revaluation.wizard`
- `ops.general.ledger.wizard.enhanced` (uses dynamic views)

### 3. Deprecated Files
- `deprecated/wizards/ops_financial_report_wizard.py`
- `deprecated/wizards/ops_general_ledger_wizard.py`
- `deprecated/wizards/ops_report_menu.xml`

### 4. Asset Report Inconsistency
`ops.asset.report.wizard` returns raw dict instead of using `env.ref().report_action()`:
```python
return {
    'type': 'ir.actions.report',
    'report_name': report_names.get(self.report_type),
    ...
}
```

---

## STATISTICS

| Component | ops_matrix_core | ops_matrix_accounting | Total |
|-----------|-----------------|----------------------|-------|
| Wizard Models | 16 | 16 | 32 |
| Wizard Views | 8 | 9 | 17 |
| Wizard Actions | 5 | 8 | 13 |
| Report Actions | 3 | 24 | 27 |
| QWeb Templates | 3 | 42+ | 45+ |
| Layout Templates | 0 | 13 | 13 |
| Component Templates | 0 | 20+ | 20+ |

---

## AUDIT COMPLETE

**Timestamp**: 2026-02-05T19:15:00Z
**Auditor**: Claude Code Agent
