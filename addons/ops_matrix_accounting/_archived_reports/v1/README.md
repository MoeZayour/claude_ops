# Archived Report Engine v1
**Archived:** 2026-02-09
**Reason:** Clean rewrite to contracted pipeline architecture (v2)
**Total lines archived:** ~25,000

## Archived Files
### Parsers (replaced by single bridge parser)
- ops_financial_report_parser.py (1,420 lines)
- ops_general_ledger_report.py (549 lines)
- ops_financial_matrix_report.py (299 lines)
- ops_asset_register_report.py (68 lines)
- ops_corporate_report_parsers.py (783 lines)

### Excel (replaced by generic renderer)
- ops_xlsx_abstract.py, ops_excel_report_builders.py
- ops_asset_register_xlsx.py, ops_general_ledger_xlsx.py
- ops_financial_matrix_xlsx.py, ops_treasury_report_xlsx.py

### Templates (replaced by shape-based system)
- 11 XML template files totaling ~7,300 lines

### God Wizard (replaced by focused wizards)
- ops_general_ledger_wizard_enhanced.py (2,053 lines)

### Controller (replaced)
- ops_report_controller.py (381 lines)

## Recovery
All code preserved here. Original functionality in git history.
