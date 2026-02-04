# OPS Framework - Reporting Wizard Comprehensive Audit Report

**Audit Date:** 2026-02-01
**Auditor:** Claude Code
**Scope:** READ-ONLY Analysis of OPS Reporting Wizard Architecture

---

## EXECUTIVE SUMMARY

The OPS Framework implements a **sophisticated four-pillar reporting architecture** with:
- **31 wizard models** across two modules
- **Unified base class** (`ops.base.report.wizard`) for shared functionality
- **Smart template system** for saving/loading configurations
- **IT Admin Blindness** and branch isolation security
- **Dynamic account fetching** (no hardcoded accounts)
- **Company-branded PDF/Excel exports**

---

## PHASE 1: WIZARD INVENTORY

### Total Wizard Count: 31 Wizards

#### A. Main Reporting Wizards (4 Pillars)

| Wizard | Model | Engine | Reports |
|--------|-------|--------|---------|
| **Financial Intelligence** | `ops.general.ledger.wizard.enhanced` | financial | GL, TB, P&L, BS, CF, Aged, Partner, SoA |
| **Treasury Intelligence** | `ops.treasury.report.wizard` | treasury | PDC Registry, Maturity, On-Hand |
| **Asset Intelligence** | `ops.asset.report.wizard` | asset | Register, Forecast, Disposal, Movement |
| **Inventory Intelligence** | `ops.inventory.report.wizard` | inventory | Valuation, Aging, Negative, Movement |
| **Balance Sheet (Standalone)** | `ops.balance.sheet.wizard` | N/A | IAS 1 Balance Sheet |

#### B. Daily Book Wizards (3)

| Wizard | Model | Purpose |
|--------|-------|---------|
| Cash Book | `ops.cash.book.wizard` | Cash journal transactions |
| Day Book | `ops.day.book.wizard` | All transactions for a day |
| Bank Book | `ops.bank.book.wizard` | Bank journal transactions |

#### C. Operational Wizards (23)

**ops_matrix_core:**
- `ops.approval.reject.wizard`
- `ops.approval.recall.wizard`
- `ops.welcome.wizard` (+ child wizards for branch/BU)
- `ops.secure.export.wizard`
- `ops.sale.order.import.wizard`
- `ops.purchase.order.import.wizard`
- `ops.persona.drift.wizard`
- `ops.audit.evidence.wizard`
- `apply.report.template.wizard`
- `sale.order.import.wizard`
- `three.way.match.override.wizard`
- `ops.ip.test.wizard`
- `ops.security.resolve.wizard`

**ops_matrix_accounting:**
- `ops.asset.depreciation.wizard`
- `ops.asset.disposal.wizard`
- `ops.asset.impairment.wizard`
- `ops.period.close.wizard`
- `ops.fx.revaluation.wizard`
- `ops.three.way.match.override.wizard`
- `ops.asset.register.wizard` (in reports/)
- `ops.credit.override.wizard`
- `ops.journal.template.wizard`
- `ops.bank.statement.import.wizard`
- `ops.report.template.save.wizard`

---

## PHASE 2: ARCHITECTURE ANALYSIS

### Base Class: `ops.base.report.wizard`

**Location:** [ops_matrix_accounting/wizard/ops_base_report_wizard.py](addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py)
**Lines:** 703
**Type:** AbstractModel

**Provided Features:**
1. Template loading/saving (`report_template_id`, `_onchange_report_template_id`, `action_save_template`)
2. Common computed fields (`report_title`, `filter_summary`, `record_count`, `currency_id`)
3. Validation framework (`_validate_filters`, `_validate_filters_extra`)
4. Security enforcement (`_check_intelligence_access`, `_validate_branch_access`)
5. Audit logging (`_log_report_audit`)
6. Number formatting helpers (`_format_amount`, `_format_percentage`)
7. Company color scheme (`get_color_scheme`, `_get_company_primary_color`)

**Abstract Methods (Must Override):**
```python
def _get_engine_name(self) -> str
def _get_report_titles(self) -> dict
def _get_scalar_fields_for_template(self) -> list
def _get_m2m_fields_for_template(self) -> list
def _get_report_data(self) -> dict
def _return_report_action(self, data) -> dict
```

**Optional Hooks:**
```python
def _apply_template_date_modes(self, config) -> None
def _add_filter_summary_parts(self, parts) -> None
def _validate_filters_extra(self) -> bool|dict
def _estimate_record_count(self) -> int
```

---

## PHASE 3: TEMPLATE SYSTEM

### Template Model: `ops.report.template`

**Location:** [ops_matrix_accounting/models/ops_report_template.py](addons/ops_matrix_accounting/models/ops_report_template.py)
**Lines:** 288

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Template name |
| `engine` | Selection | financial/treasury/asset/inventory |
| `config_data` | Text | JSON-encoded wizard configuration |
| `is_global` | Boolean | Shared with all users |
| `user_id` | Many2one | Creator (for private templates) |
| `usage_count` | Integer | Usage tracking |
| `last_used` | Datetime | Last applied timestamp |

**Template Features:**
- **YES**: Users can save configurations as templates
- **YES**: Users can load saved templates
- **YES**: Global (shared) and Private (user-only) templates
- **YES**: Per-engine filtering (financial, treasury, asset, inventory)
- **YES**: Usage tracking and "favorites" via usage_count
- **YES**: Dynamic date modes (last_month, current_month, ytd, next_30_days, etc.)

**Save Wizard:** `ops.report.template.save.wizard`
- Located in same file
- Opens via `action_save_template` button on wizards
- Saves current configuration to `config_data` as JSON

---

## PHASE 4: ACCOUNT FETCHING LOGIC

### Dynamic Account Loading

**CONFIRMATION: NO HARDCODED ACCOUNT CODES FOUND**

All wizards use **dynamic account type filtering** based on Odoo's `account_type` field:

```python
# Example from ops_general_ledger_wizard_enhanced.py
def _get_account_type_domain(self):
    if self.report_type == 'pl':
        return [('account_id.account_type', 'in', [
            'income', 'income_other',
            'expense', 'expense_depreciation', 'expense_direct_cost'
        ])]
    elif self.report_type == 'bs':
        return [('account_id.account_type', 'in', [
            'asset_receivable', 'asset_cash', 'asset_current',
            'asset_non_current', 'asset_prepayments', 'asset_fixed',
            'liability_payable', 'liability_credit_card',
            'liability_current', 'liability_non_current',
            'equity', 'equity_unaffected'
        ])]
```

**Account Discovery Methods:**
1. `_build_domain()` - Builds complete domain for account.move.line
2. `_get_account_type_domain()` - Returns account type filters per report
3. `_build_matrix_domain()` - Adds branch/BU dimension filters
4. `_get_hierarchical_financial_data()` - Builds CoA hierarchy dynamically

**NEW ACCOUNTS AUTO-INCLUDED: YES**
- Any new account with the correct `account_type` will automatically appear in reports
- No manual configuration required

---

## PHASE 5: MENU STRUCTURE

### Report Navigation Paths

| Path | Wizard |
|------|--------|
| Accounting > Reporting > **Matrix Financial Intelligence** | `ops.general.ledger.wizard.enhanced` |
| Accounting > Reporting > **Treasury Intelligence** | `ops.treasury.report.wizard` |
| Accounting > Reporting > **Asset Intelligence** | `ops.asset.report.wizard` |
| Accounting > Reporting > **Inventory Intelligence** | `ops.inventory.report.wizard` |
| Accounting > Reporting > Daily Reports > **Cash Book** | `ops.cash.book.wizard` |
| Accounting > Reporting > Daily Reports > **Day Book** | `ops.day.book.wizard` |
| Accounting > Reporting > Daily Reports > **Bank Book** | `ops.bank.book.wizard` |
| Accounting > Reporting > **PDC Reports** | PDC-specific actions |

### Menu Hierarchy:
```
Accounting (root - renamed from "Invoicing")
├── Customers
├── Vendors
├── Asset Management
│   ├── Assets
│   ├── Depreciation Lines
│   └── Configuration > Asset Categories
├── Management
│   ├── Analytic Items
│   ├── Budgets
│   └── Leases (IFRS 16)
├── Bank & Treasury
│   ├── Bank Reconciliation
│   └── Bank Statements
├── Period End
│   ├── Fiscal Periods
│   ├── Close Checklist
│   └── Branch Period Locks
├── Reporting
│   ├── Matrix Financial Intelligence (seq 10)
│   ├── Treasury Intelligence (seq 20)
│   ├── Asset Intelligence (seq 30)
│   ├── Invoice Analysis (seq 40)
│   ├── Analytic Report (seq 50)
│   ├── PDC Reports (seq 60)
│   └── Daily Reports (seq 70)
│       ├── Cash Book
│       ├── Day Book
│       └── Bank Book
└── Configuration
    ├── Fiscal Periods
    ├── Follow-up Configuration
    └── Financial Report Structure
```

---

## PHASE 6: DEFAULT VALUES & AUTO-LOADING

### Auto-Populated Fields by Wizard

| Field | Default Value | Wizards |
|-------|---------------|---------|
| `company_id` | `self.env.company` | ALL |
| `date_from` | Start of year | Financial Intelligence |
| `date_to` | End of current month | Financial Intelligence |
| `as_of_date` | Today | Balance Sheet, Asset Register |
| `target_move` | `'posted'` | ALL |
| `journal_ids` | All cash/bank journals | Cash Book, Bank Book |
| `period_length` | 30 days | Aged, PDC Maturity |
| `aging_period_1-4` | 30, 60, 90, 180 days | Inventory Aging |
| `movement_period` | 90 days | Inventory Movement |
| `slow_threshold` | 5 moves | Inventory Movement |
| `include_initial_balance` | True | GL |
| `display_account` | `'movement'` | Financial |
| `report_format` | `'detailed'` | Financial |
| `group_by` | `'branch'`/`'category'` | Inventory/Asset |

### Computed Fields:
- `record_count` - Estimated matching records
- `filter_summary` - Human-readable filter description
- `report_title` - Dynamic based on report_type
- `currency_id` - From company
- `total_amount` - Preview totals (where applicable)

---

## PHASE 7: EXPORT OPTIONS

### Export Capabilities by Wizard

| Wizard | PDF | Excel | Screen Preview | View Transactions |
|--------|-----|-------|----------------|-------------------|
| Financial Intelligence | ✅ | ✅ | ✅ | ✅ |
| Treasury Intelligence | ✅ | ✅ | ✅ | ✅ |
| Asset Intelligence | ✅ | ✅ | ✅ | ✅ |
| Inventory Intelligence | ✅ | ✅ | ✅ | ✅ |
| Balance Sheet | ✅ | ❌ (Coming soon) | ✅ | ❌ |
| Cash Book | ✅ | ✅ | N/A | N/A |
| Day Book | ✅ | ✅ | N/A | N/A |
| Bank Book | ✅ | ✅ | N/A | N/A |

### Excel Export Implementation:
- Uses `xlsxwriter` library
- OPS Corporate branded formats
- Color scheme from company settings
- Separate worksheets for grouped data
- Professional formatting with subtotals

### PDF Export Implementation:
- QWeb templates in `report/` directory
- Dynamic colors from `company.primary_color`
- Print-optimized CSS
- Gradient accent lines matching company branding

---

## PHASE 8: SECURITY INTEGRATION

### Security Mixin: `ops.intelligence.security.mixin`

**Location:** [ops_matrix_accounting/models/ops_intelligence_security_mixin.py](addons/ops_matrix_accounting/models/ops_intelligence_security_mixin.py)
**Lines:** 381

### IT Admin Blindness Implementation

**CONFIRMATION: YES - Fully Implemented**

```python
# From _check_intelligence_access():
if user.has_group('ops_matrix_core.group_ops_it_admin'):
    raise AccessError(_(
        "Access Denied: IT Administrators cannot access %s Intelligence reports."
    ) % pillar_name)
```

### Persona-Based Access Control

| Pillar | Allowed Personas |
|--------|------------------|
| Financial | P00, P02, P03, P04, P05, P06, P07, P09, P13, P14, P15, P16 |
| Treasury | P00, P03, P04, P05, P09, P13, P14, P15, P16 |
| Asset | P00, P03, P04, P05, P08, P09, P16 |
| Inventory | P00, P03, P04, P05, P07, P08, P12, P16 |

### Branch Isolation

**Method:** `_validate_branch_access(requested_branch_ids)`

- Full access roles bypass: `base.group_system`, `group_ops_cfo`, `group_ops_executive`, `group_ops_manager`
- BU Leaders: Access to branches in their assigned business units
- Standard users: Only `ops_allowed_branch_ids`
- No branch assignment = No data access

### Security Enforcement Per Wizard

| Wizard | IT Admin Block | Branch Isolation | Audit Log |
|--------|----------------|------------------|-----------|
| Financial Intelligence | ✅ | ✅ | ✅ |
| Treasury Intelligence | ✅ | ✅ | ✅ |
| Asset Intelligence | ✅ | ✅ | ✅ |
| Inventory Intelligence | ✅ | ✅ | ✅ |
| Balance Sheet | ✅ | ✅ | ✅ |
| Daily Books | ❌ | ✅ (branch filter only) | ❌ |

---

## PHASE 9: THEME INTEGRATION

### Company Primary Color Usage

**CONFIRMATION: YES - Fully Integrated**

**Python Support:**
```python
# ops_base_report_wizard.py:601
def _get_company_primary_color(self):
    company = getattr(self, 'company_id', None) or self.env.company
    return getattr(company, 'primary_color', None) or '#C9A962'
```

**PDF Templates:**
All report templates dynamically load company colors:
```xml
<t t-set="primary_color" t-value="company.primary_color or '#1a2744'"/>
<t t-set="secondary_color" t-value="company.secondary_color or '#5B6BBB'"/>
```

### Theme-Branded Reports:
- Asset Register/Forecast/Disposal
- Treasury PDC Registry/Maturity/On-Hand
- Inventory Valuation/Aging/Movement
- Financial P&L/BS (minimal style)
- Consolidated Reports

**Accent Elements:**
- Header gradient bars
- Logo icon backgrounds
- Section headers
- Footer branding

---

## PHASE 10: SUMMARY & RECOMMENDATIONS

### WIZARD AUDIT SUMMARY

```
1. WIZARD INVENTORY
   - Total wizards: 31
   - Reporting wizards: 8
   - Operational wizards: 23

2. TEMPLATE SYSTEM
   - Template model exists: YES
   - User can save configurations: YES
   - User can load favorites: YES (via usage_count sorting)

3. ACCOUNT HANDLING
   - Dynamic account loading: YES
   - Hardcoded accounts found: NO
   - New accounts auto-included: YES

4. DEFAULT VALUES
   - Company auto-populated: YES
   - Dates auto-set: YES
   - Journals auto-loaded: YES (for daily books)

5. EXPORT OPTIONS
   - PDF: 8/8 wizards
   - Excel: 7/8 wizards
   - Web preview: 5/8 wizards

6. SECURITY
   - IT Admin blindness: 5/8 wizards
   - Branch isolation: 8/8 wizards
   - Audit logging: 5/8 wizards

7. THEME INTEGRATION
   - Uses company primary color: YES
   - Consistent styling: YES

8. ARCHITECTURE
   - Base class abstraction: EXCELLENT
   - Code duplication: MINIMAL
   - Inheritance pattern: WELL-DESIGNED
```

### ISSUES FOUND

1. **Daily Books Missing Security Mixin**
   - `ops.cash.book.wizard`, `ops.day.book.wizard`, `ops.bank.book.wizard` do NOT inherit `ops.intelligence.security.mixin`
   - No IT Admin Blindness on these reports
   - No audit logging

2. **Balance Sheet Excel Export**
   - `action_generate_xlsx()` returns `UserError("Excel export coming soon!")`
   - Incomplete implementation

3. **Deprecated Wizards Present**
   - `/deprecated/wizards/` folder contains old wizard versions
   - `ops.general.ledger.wizard` (replaced by enhanced)
   - `ops.financial.report.wizard` (consolidated into enhanced)

4. **Dual Report Template Models**
   - Core: `ops_matrix_core/models/ops_report_template.py` (basic)
   - Accounting: `ops_matrix_accounting/models/ops_report_template.py` (extended with `_inherit`)
   - May cause confusion but is architecturally correct

### RECOMMENDATIONS

1. **Add Security Mixin to Daily Books**
   ```python
   class OpsCashBookWizard(models.TransientModel):
       _inherit = ['ops.intelligence.security.mixin']  # ADD THIS
   ```

2. **Implement Balance Sheet Excel Export**
   - Extend from base class `action_export_excel` pattern
   - Use same xlsxwriter approach as other wizards

3. **Archive Deprecated Wizards**
   - Move deprecated folder to `_archive/`
   - Or remove if no longer referenced

4. **Consider Splitting Large Wizard**
   - `ops_general_ledger_wizard_enhanced.py` is 1,896 lines
   - Could split into separate report-specific mixins

---

## FILE REFERENCES

### Main Wizard Files (with line counts)

| File | Lines | Purpose |
|------|-------|---------|
| `wizard/ops_base_report_wizard.py` | 703 | Abstract base class |
| `wizard/ops_general_ledger_wizard_enhanced.py` | 1,896 | Financial "Big 8" |
| `wizard/ops_treasury_report_wizard.py` | 650 | PDC Reports |
| `wizard/ops_asset_report_wizard.py` | 794 | Asset Reports |
| `wizard/ops_inventory_report_wizard.py` | 1,253 | Inventory Reports |
| `wizard/ops_balance_sheet_wizard.py` | 461 | IAS 1 Balance Sheet |
| `wizard/ops_daily_reports_wizard.py` | 759 | Cash/Day/Bank Books |
| `models/ops_report_template.py` | 288 | Smart Templates |
| `models/ops_intelligence_security_mixin.py` | 381 | Security Mixin |

### View Files

| File | Purpose |
|------|---------|
| `views/ops_general_ledger_wizard_enhanced_views.xml` | Financial wizard form |
| `wizard/ops_treasury_report_wizard_views.xml` | Treasury wizard form |
| `wizard/ops_asset_report_wizard_views.xml` | Asset wizard form |
| `views/ops_inventory_report_views.xml` | Inventory wizard form |
| `wizard/ops_balance_sheet_wizard_views.xml` | Balance sheet form |
| `views/accounting_menus.xml` | Menu structure |

---

**END OF AUDIT REPORT**

*Generated by Claude Code on 2026-02-01*
*Read-Only Audit - No Changes Made*
