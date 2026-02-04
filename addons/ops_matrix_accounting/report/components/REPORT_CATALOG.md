# OPS Framework - Official Corporate Report Catalog

**Version:** 1.0.0
**Total Reports:** 16
**Status:** All Implemented

---

## Report Mapping

| # | Official Report Name | Template ID | Wizard Model | Pillar |
|---|---------------------|-------------|--------------|--------|
| 1 | Balance Sheet | `report_balance_sheet_corporate` | `ops.balance.sheet.wizard` | Financial |
| 2 | Profit & Loss Statement | `report_profit_loss_matrix` | `ops.general.ledger.wizard.enhanced` (type='pl') | Financial |
| 3 | Cash Flow Statement | `report_cash_flow_matrix` | `ops.general.ledger.wizard.enhanced` (type='cf') | Financial |
| 4 | Trial Balance | `report_trial_balance_matrix` | `ops.general.ledger.wizard.enhanced` (type='tb') | Financial |
| 5 | General Ledger | `report_general_ledger_matrix` | `ops.general.ledger.wizard.enhanced` (type='gl') | Financial |
| 6 | Aged Receivables | `report_aged_partner_matrix` | `ops.general.ledger.wizard.enhanced` (type='aged', partner_type='customer') | Financial |
| 7 | Aged Payables | `report_aged_partner_matrix` | `ops.general.ledger.wizard.enhanced` (type='aged', partner_type='vendor') | Financial |
| 8 | Partner Ledger | `report_partner_ledger_matrix` | `ops.general.ledger.wizard.enhanced` (type='partner') | Financial |
| 9 | Statement of Account | `report_statement_of_account_matrix` | `ops.general.ledger.wizard.enhanced` (type='soa') | Financial |
| 10 | PDC Registry | `report_treasury_registry_pdf` | `ops.treasury.report.wizard` (type='registry') | Treasury |
| 11 | PDC Maturity Analysis | `report_treasury_maturity_pdf` | `ops.treasury.report.wizard` (type='maturity') | Treasury |
| 12 | PDCs in Hand | `report_treasury_on_hand_pdf` | `ops.treasury.report.wizard` (type='on_hand') | Treasury |
| 13 | Fixed Asset Register | `report_asset_register_pdf` | `ops.asset.report.wizard` (type='register') | Asset |
| 14 | Depreciation Schedule | `report_depreciation_schedule_pdf` | `ops.asset.report.wizard` (type='schedule') | Asset |
| 15 | Stock Valuation | `report_inventory_valuation_pdf` | `ops.inventory.report.wizard` (type='valuation') | Inventory |
| 16 | Inventory Aging | `report_inventory_aging_pdf` | `ops.inventory.report.wizard` (type='aging') | Inventory |

---

## Access Paths

### Financial Reports (Menu: Accounting > Reporting > Matrix Financial Intelligence)
- All 9 financial reports accessible via the unified "Big 8" wizard
- Select report type from dropdown: GL, TB, P&L, BS, CF, Aged, Partner, SOA

### Treasury Reports (Menu: Accounting > Reporting > Treasury Intelligence)
- PDC Registry, Maturity Analysis, PDCs in Hand
- Filter by PDC type (Receivable/Payable/Both)

### Asset Reports (Menu: Accounting > Reporting > Asset Intelligence)
- Fixed Asset Register
- Depreciation Schedule

### Inventory Reports (Menu: Accounting > Reporting > Inventory Intelligence)
- Stock Valuation
- Inventory Aging

---

## Corporate Branding Requirements

All reports must include:
1. **Header**: Company logo + name + report metadata
2. **Filter Bar**: Applied filters displayed
3. **Notes Section**: Currency, data scope, generation info
4. **Footer**: "Powered by OPS Framework" badge + page numbers

---

## Deprecated Files (Archived)

| File | Location | Reason |
|------|----------|--------|
| `ops_financial_report_wizard.py` | `deprecated/wizards/` | Superseded by Enhanced GL wizard |
| `ops_general_ledger_wizard.py` | `deprecated/wizards/` | Superseded by Enhanced GL wizard |
| `ops_financial_report_wizard_views.xml` | `deprecated/wizards/` | Corresponding views |
| `ops_general_ledger_wizard_views.xml` | `deprecated/wizards/` | Corresponding views |

---

## Last Updated
- **Date**: 2026-02-01
- **Updated By**: Report Harmonization Process
