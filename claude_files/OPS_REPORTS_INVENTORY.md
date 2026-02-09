# OPS REPORTS — COMPLETE CODEBASE INVENTORY
**Date:** 2026-02-06
**Mode:** Discovery only — nothing modified

---

## 1. FILE INVENTORY

### ops_matrix_core/report/ (4 files)
| File | Lines | Purpose |
|------|-------|---------|
| ops_external_layout.xml | 80 | Base external layout for all OPS reports |
| ops_report_quotation.xml | 313 | Sale order quotation/order PDF |
| ops_report_purchase.xml | 250 | Purchase order PDF |
| ops_report_delivery.xml | 245 | Stock picking delivery note PDF |

### ops_matrix_core/reports/ (3 files — note: different dir from report/)
| File | Lines | Purpose |
|------|-------|---------|
| ops_products_availability_report.xml | ~500 | Products availability report |
| sale_order_availability_report.xml | ~400 | Stock availability report |
| sale_order_documentation_report.xml | ~100 | SO documentation report |

### ops_matrix_accounting/report/ (28 files)
| File | Lines | Type | Purpose |
|------|-------|------|---------|
| __init__.py | 15 | py | Import chain (3 XLSX commented out!) |
| excel_styles.py | 749 | py | Shared Excel style definitions |
| ops_xlsx_abstract.py | 160 | py | Base XLSX abstract model |
| ops_asset_register_report.py | 62 | py | Asset register QWeb parser |
| ops_asset_register_xlsx.py | 519 | py | Asset XLSX generator |
| ops_financial_matrix_report.py | 293 | py | Financial matrix QWeb parser |
| ops_financial_matrix_xlsx.py | 520 | py | Financial matrix XLSX (DISABLED in __init__) |
| ops_financial_report_parser.py | 1,475 | py | Main financial report parser (+ minimal) |
| ops_general_ledger_report.py | 297 | py | General ledger QWeb parser (minimal + legacy) |
| ops_general_ledger_xlsx.py | 158 | py | General ledger XLSX (DISABLED in __init__) |
| ops_treasury_report_xlsx.py | 524 | py | Treasury XLSX (DISABLED in __init__) |
| ops_report_layout.xml | 1,803 | xml | MEGA file: all layout templates, styles, headers, footers |
| ops_report_minimal_styles.xml | 400 | xml | Minimal report styles |
| ops_financial_report_template.xml | 1,401 | xml | Corporate financial reports (TB, P&L, CF, Aged, BS) |
| ops_financial_report_minimal.xml | 467 | xml | Minimal financial reports |
| ops_general_ledger_template.xml | 331 | xml | Corporate general ledger |
| ops_general_ledger_minimal.xml | 328 | xml | Minimal general ledger |
| ops_consolidated_report_templates.xml | 936 | xml | 4 consolidation reports |
| ops_daily_report_templates.xml | 518 | xml | Cash book, day book, bank book |
| ops_treasury_report_templates.xml | 765 | xml | Treasury: registry, maturity, on-hand |
| ops_asset_report_templates.xml | 411 | xml | Asset reports + XLSX action |
| ops_inventory_report_templates.xml | 726 | xml | 4 inventory reports |
| ops_report_invoice.xml | 315 | xml | Invoice/credit note |
| ops_report_payment.xml | 222 | xml | Payment receipt |
| components/ | dir | | Reusable corporate components |
| components/ops_corporate_report_components.xml | 505 | xml | 20 reusable template components |
| components/REPORT_CATALOG.md | - | md | Documentation |

### CSS/SCSS (3 files, 3,030 lines total)
| File | Lines | Bundle |
|------|-------|--------|
| ops_matrix_accounting/static/src/css/ops_report.css | 1,684 | web.assets_backend |
| ops_matrix_accounting/static/src/scss/ops_corporate_reports.scss | 651 | web.assets_backend |
| ops_matrix_core/static/src/css/ops_external_report.css | 695 | web.report_assets_common |

### ops_theme/report/ — DOES NOT EXIST
### ops_dashboard/report/ — DOES NOT EXIST

---

## 2. PYTHON MODELS

### Wizard Models (TransientModel) — 15 models
| _name | File | Lines | Purpose |
|-------|------|-------|---------|
| ops.general.ledger.wizard.enhanced | wizard/ops_general_ledger_wizard_enhanced.py | 2,071 | MAIN: All financial reports |
| ops.inventory.report.wizard | wizard/ops_inventory_report_wizard.py | 1,266 | Inventory reports |
| ops.cash.book.wizard | wizard/ops_daily_reports_wizard.py | 320 | Cash book |
| ops.day.book.wizard | wizard/ops_daily_reports_wizard.py | 290 | Day book |
| ops.bank.book.wizard | wizard/ops_daily_reports_wizard.py | 260 | Bank book |
| ops.asset.report.wizard | wizard/ops_asset_report_wizard.py | 853 | Asset reports |
| ops.base.report.wizard | wizard/ops_base_report_wizard.py | 750 | Abstract base for all wizards |
| ops.treasury.report.wizard | wizard/ops_treasury_report_wizard.py | 717 | Treasury reports |
| ops.consolidation.intelligence.wizard | wizard/ops_consolidation_intelligence_wizard.py | 215 | Consolidation reports |
| ops.asset.register.wizard | report/ops_asset_register_report.py | 28 | Asset register |
| ops.asset.depreciation.wizard | wizard/ops_asset_depreciation_wizard.py | 123 | Asset depreciation |
| ops.asset.disposal.wizard | wizard/ops_asset_disposal_wizard.py | 130 | Asset disposal |
| ops.asset.impairment.wizard | wizard/ops_asset_impairment_wizard.py | 134 | Asset impairment |
| ops.fx.revaluation.wizard | wizard/ops_fx_revaluation_wizard.py | 246 | FX revaluation |
| ops.period.close.wizard | wizard/ops_period_close_wizard.py | 182 | Period close |

### Parser Models (AbstractModel) — 11 models
| _name | File | Status |
|-------|------|--------|
| report.ops_matrix_accounting.report_ops_financial_document | ops_financial_report_parser.py | OK |
| report.ops_matrix_accounting.report_ops_financial_minimal | ops_financial_report_parser.py | OK |
| report.ops_matrix_accounting.report_general_ledger_minimal | ops_general_ledger_report.py | OK |
| report.ops_matrix_accounting.report_general_ledger | ops_general_ledger_report.py | OK |
| report.ops_matrix_accounting.report_asset_register | ops_asset_register_report.py | OK |
| report.ops_matrix_accounting.report_financial_matrix | ops_financial_matrix_report.py | OK |
| report.ops_matrix_accounting.report_financial_matrix_xlsx | ops_financial_matrix_xlsx.py | DISABLED (import commented out) |
| report.ops_matrix_accounting.report_asset_xlsx | ops_asset_register_xlsx.py | OK |
| report.ops_matrix_accounting.report_general_ledger_xlsx | ops_general_ledger_xlsx.py | DISABLED (import commented out) |
| report.ops_matrix_accounting.report_treasury_xlsx | ops_treasury_report_xlsx.py | DISABLED (import commented out) |
| ops.xlsx.abstract | ops_xlsx_abstract.py | OK |

---

## 3. QWEB TEMPLATES — 84 Total in DB

### Accounting Templates (73 in DB)
#### Layout/Style Templates (26)
- ops_consulting_layout
- ops_equation_bar_template
- ops_external_layout
- ops_format_amount
- ops_header_split_template
- ops_info_box_template
- ops_legacy_header (inherits ops_report_header_template)
- ops_meridian_header_template
- ops_meta_bar_template
- ops_minimal_external_layout
- ops_minimal_footer
- ops_minimal_format_amount
- ops_minimal_header
- ops_minimal_layout
- ops_minimal_notes
- ops_minimal_report_styles
- ops_notes_template
- ops_report_footer_template
- ops_report_header_template
- ops_report_styles

#### Reusable Components (20 — from components/ops_corporate_report_components.xml)
- balance_check_badge
- format_corporate_amount
- format_corporate_percentage
- format_corporate_variance
- grand_total_row
- kpi_card
- report_corporate_footer
- report_corporate_header
- report_corporate_title
- report_filter_bar
- report_notes_section
- section_header_asset / _equity / _expense / _financial / _liability / _revenue / _treasury
- subtotal_row
- table_header_row

#### Report Templates (27)
- report_aged_partner_corporate
- report_asset_register_document_corporate
- report_balance_sheet_corporate
- report_bank_book_corporate
- report_branch_pl_document
- report_business_unit_document
- report_cash_book_corporate
- report_cash_flow_corporate
- report_company_consolidation_document
- report_consolidated_balance_sheet_document
- report_day_book_corporate
- report_depreciation_schedule_document_corporate
- report_general_ledger_corporate
- report_general_ledger_minimal
- report_inventory_aging_document_corporate
- report_inventory_movement_document_corporate
- report_inventory_negative_document_corporate
- report_inventory_valuation_document_corporate
- report_minimal_balance_sheet_content / _cash_flow / _generic / _profit_loss / _trial_balance
- report_ops_financial_minimal
- report_ops_invoice / report_ops_invoice_document
- report_ops_payment / report_ops_payment_document
- report_profit_loss_corporate
- report_treasury_maturity_corporate / _on_hand / _registry
- report_trial_balance_corporate

### Core Templates (11 in DB)
- ops_external_layout
- ops_external_continuation_header
- report_ops_quotation / report_ops_quotation_document
- report_ops_purchase / report_ops_purchase_document
- report_ops_delivery / report_ops_delivery_document
- report_products_availability_document
- report_sale_order_availability
- report_sale_order_documentation

---

## 4. REPORT ACTIONS (ir.actions.report) — 37 Total in DB

### PDF Reports (37 registered, 0 XLSX)

#### Financial (bound to ops.general.ledger.wizard.enhanced) — 10
| XML ID | report_name | Name |
|--------|-------------|------|
| action_report_trial_balance_corporate | report_trial_balance_corporate | OPS Trial Balance Report |
| action_report_profit_loss_corporate | report_profit_loss_corporate | OPS Profit & Loss Statement |
| action_report_balance_sheet_corporate | report_balance_sheet_corporate | OPS Balance Sheet |
| action_report_cash_flow_corporate | report_cash_flow_corporate | OPS Cash Flow Statement |
| action_report_aged_partner_corporate | report_aged_partner_corporate | OPS Aged Partner Balance |
| action_report_general_ledger_corporate | report_general_ledger_corporate | General Ledger (Corporate) |
| action_report_general_ledger | report_general_ledger_corporate | General Ledger |
| action_report_general_ledger_minimal | report_general_ledger_minimal | General Ledger (Minimal) |
| action_report_ops_financial_minimal | report_ops_financial_minimal | Financial Report (Minimal) |
| action_report_ops_financial | report_ops_financial_minimal | Financial Report (Legacy) |

#### Daily Books (unbound) — 3
| XML ID | report_name | Name |
|--------|-------------|------|
| action_report_cash_book | report_cash_book_corporate | Cash Book |
| action_report_day_book | report_day_book_corporate | Day Book |
| action_report_bank_book | report_bank_book_corporate | Bank Book |

#### Asset Reports (bound to ops.asset.report.wizard) — 6
| XML ID | report_name | Name |
|--------|-------------|------|
| report_asset_register_pdf | report_asset_register_document_corporate | Asset Register Report (Corporate) |
| report_depreciation_schedule_pdf | report_depreciation_schedule_document_corporate | Depreciation Schedule Report (Corporate) |
| report_asset_forecast_pdf | report_depreciation_schedule_document_corporate | Depreciation Forecast (Corporate) |
| report_asset_disposal_pdf | report_asset_register_document_corporate | Asset Disposal Analysis (Corporate) |
| report_asset_movement_pdf | report_asset_register_document_corporate | Asset Movement Report (Corporate) |
| report_asset_xlsx | report_asset_xlsx | Asset Intelligence XLSX |

#### Treasury (bound to ops.treasury.report.wizard) — 4
| XML ID | report_name | Name |
|--------|-------------|------|
| report_treasury_registry_pdf | report_treasury_registry_corporate | PDC Registry Report |
| report_treasury_maturity_pdf | report_treasury_maturity_corporate | PDC Maturity Analysis |
| report_treasury_on_hand_pdf | report_treasury_on_hand_corporate | PDCs in Hand |
| report_treasury_xlsx | report_treasury_xlsx | Treasury XLSX |

#### Inventory (bound to ops.inventory.report.wizard) — 4
| XML ID | report_name | Name |
|--------|-------------|------|
| report_inventory_valuation_pdf | report_inventory_valuation_document_corporate | Stock Valuation Report |
| report_inventory_aging_pdf | report_inventory_aging_document_corporate | Inventory Aging Report |
| report_inventory_movement_pdf | report_inventory_movement_document_corporate | Movement Analysis Report |
| report_inventory_negative_pdf | report_inventory_negative_document_corporate | Negative Stock Alert |

#### Consolidation — 4
| XML ID | report_name | Bound To |
|--------|-------------|----------|
| report_company_consolidation_pdf | report_company_consolidation_document | ops.company.consolidation |
| report_branch_pl_pdf | report_branch_pl_document | ops.branch.report |
| report_business_unit_pdf | report_business_unit_document | ops.business.unit.report |
| report_consolidated_balance_sheet_pdf | report_consolidated_balance_sheet_document | ops.consolidated.balance.sheet |

#### Transaction Documents — 6
| XML ID | report_name | Bound To |
|--------|-------------|----------|
| action_report_ops_invoice | report_ops_invoice | account.move |
| action_report_ops_payment | report_ops_payment | account.payment |
| action_report_ops_quotation | report_ops_quotation | sale.order |
| action_report_ops_purchase | report_ops_purchase | purchase.order |
| action_report_ops_delivery | report_ops_delivery | stock.picking |
| + 3 sale.order reports | (availability, documentation, products) | sale.order |

---

## 5. TEMPLATE DEPENDENCY GRAPH (t-call chains)

### Accounting Report Templates call:
```
web.html_container
  └── ops_matrix_accounting.ops_external_layout    (corporate reports)
  └── ops_matrix_accounting.ops_minimal_external_layout (minimal reports)
      ├── ops_matrix_accounting.ops_report_styles / ops_minimal_report_styles
      ├── ops_matrix_accounting.report_corporate_header  (component)
      ├── ops_matrix_accounting.report_corporate_title   (component)
      ├── ops_matrix_accounting.report_filter_bar        (component)
      ├── ops_matrix_accounting.format_corporate_amount  (component)
      ├── ops_matrix_accounting.section_header_*         (components)
      ├── ops_matrix_accounting.report_corporate_footer  (component)
      └── ops_matrix_accounting.ops_minimal_header / ops_minimal_footer
```

### Core Report Templates call:
```
web.html_container
  └── (uses web.external_layout — NOT ops_matrix_core.ops_external_layout directly)
```

---

## 6. MANIFEST LOAD ORDER

### ops_matrix_accounting (report-related entries only)
```
data/report_templates.xml                              # Preset templates data
data/report_templates_extra.xml                        # Phase 10 extra templates
views/ops_pdc_reports_menus.xml                        # Menu definitions
views/ops_general_ledger_wizard_enhanced_views.xml     # Main wizard form view
views/ops_report_template_views.xml                    # Report template CRUD views
views/ops_inventory_report_views.xml                   # Inventory wizard views
views/ops_report_audit_views.xml                       # Audit views
views/ops_financial_report_config_views.xml            # Config views
views/ops_daily_reports_views.xml                      # Daily book wizard views
wizard/ops_asset_depreciation_wizard_views.xml
wizard/ops_asset_disposal_wizard_views.xml
wizard/ops_treasury_report_wizard_views.xml
wizard/ops_period_close_wizard_views.xml
wizard/ops_asset_report_wizard_views.xml
wizard/ops_three_way_match_override_wizard_views.xml
wizard/ops_consolidation_intelligence_wizard_views.xml
report/components/ops_corporate_report_components.xml  # Reusable components
report/ops_report_layout.xml                           # 1,803 lines MEGA layout
report/ops_report_minimal_styles.xml
report/ops_general_ledger_minimal.xml
report/ops_financial_report_minimal.xml
report/ops_asset_report_templates.xml
report/ops_consolidated_report_templates.xml
report/ops_financial_report_template.xml
report/ops_general_ledger_template.xml
report/ops_inventory_report_templates.xml
report/ops_treasury_report_templates.xml
report/ops_daily_report_templates.xml
report/ops_report_invoice.xml
report/ops_report_payment.xml
```

---

## 7. ISSUES FOUND (Discovery Only)

### CRITICAL: 3 XLSX Parsers Disabled
In `report/__init__.py`, three XLSX generators are **commented out**:
```python
# from . import ops_general_ledger_xlsx  # TODO: Update to use ops.xlsx.abstract
# from . import ops_financial_matrix_xlsx  # TODO: Update to use ops.xlsx.abstract
# from . import ops_treasury_report_xlsx  # TODO: Update to use ops.xlsx.abstract
```
**Result:** 0 XLSX actions registered in DB. Only `report_asset_xlsx` works.

### DUPLICATES: 4 Sets of Duplicate report_name
Multiple ir.actions.report records share the same `report_name`:
1. `report_asset_register_document_corporate` → 3 actions (Register, Disposal, Movement)
2. `report_depreciation_schedule_document_corporate` → 2 actions (Schedule, Forecast)
3. `report_general_ledger_corporate` → 2 actions (named "General Ledger" and "General Ledger (Corporate)")
4. `report_ops_financial_minimal` → 2 actions (named "Financial Report (Minimal)" and "Financial Report (Legacy)")

### MEGA FILE: ops_report_layout.xml = 1,803 lines
Contains ALL of: styles, headers, footers, layout templates, format helpers, notes, equations, info boxes.
This is the largest single file and a prime refactoring target.

### Missing Wizard Model
`ops.financial.report.wizard` — NOT FOUND in DB (likely deprecated, replaced by `ops.general.ledger.wizard.enhanced`)

---

## 8. SIZE SUMMARY

| Category | Files | Total Lines |
|----------|-------|-------------|
| Report XML (accounting) | 13 | 8,623 |
| Report XML (core) | 4 | 888 |
| Report Components XML | 1 | 505 |
| Report Python (parsers) | 8 | 4,772 |
| Wizard Python | 14+1 | 7,986 |
| CSS/SCSS | 3 | 3,030 |
| Core reports/ dir | 3 | ~1,000 |
| **TOTAL** | **~47** | **~26,804** |

### Top 5 Largest Files
1. ops_report_layout.xml — 1,803 lines
2. ops_general_ledger_wizard_enhanced.py — 2,071 lines
3. ops_financial_report_parser.py — 1,475 lines
4. ops_financial_report_template.xml — 1,401 lines
5. ops_inventory_report_wizard.py — 1,266 lines

---

## 9. TEMPLATE COUNT SUMMARY

| Metric | Count |
|--------|-------|
| QWeb templates in DB | 84 |
| Report actions in DB (PDF) | 37 |
| Report actions in DB (XLSX) | 0 |
| Wizard models (transient) | 15 |
| Parser models (abstract) | 11 (3 disabled) |
| Reusable components | 20 |
| Layout/style templates | 26 |
| Actual report templates | 27 |
| Core report templates | 11 |

---

*INVENTORY COMPLETE — NO FILES MODIFIED*
