# OPS Matrix Accounting - Development TODO List

**Date**: January 29, 2026  
**Environment**: Claude Code → VSCode SSH → Docker Host  
**Repository**: `/opt/gemini_odoo19/addons/ops_matrix_accounting/`  
**Reference**: OM Account Accountant v19.0.1.0.3 (analyzed)

---

## 📋 DEVELOPMENT PHASES

### PHASE 1: CRITICAL FIXES (Priority: IMMEDIATE)
> These must be completed before any production use

- [ ] **1.1 PDC Journal Entry Integration**
  - [ ] Add `journal_id`, `deposit_move_id`, `clearance_move_id`, `bounce_move_id` fields to PDC models
  - [ ] Add company-level `pdc_clearing_account_id` setting
  - [ ] Implement `action_deposit()` with JE creation (Dr: PDC Clearing, Cr: AR)
  - [ ] Implement `action_clear()` with JE creation (Dr: Bank, Cr: PDC Clearing)
  - [ ] Implement `action_bounce()` with reversal JE
  - [ ] Add PDC Payable mirror logic (Dr: AP, Cr: PDC Clearing on issue)
  - [ ] Create PDC settings view in Accounting Configuration
  - **Source**: OPS original + accounting best practice

- [ ] **1.2 Branch Isolation Record Rules**
  - [ ] Create `security/ops_accounting_rules.xml`
  - [ ] Add record rule for `ops.pdc.receivable` (branch isolation)
  - [ ] Add record rule for `ops.pdc.payable` (branch isolation)
  - [ ] Add record rule for `ops.budget` (branch isolation)
  - [ ] Add record rule for `ops.asset` (branch isolation)
  - [ ] Add record rule for `ops.asset.depreciation` (branch isolation)
  - [ ] Add to `__manifest__.py` data list
  - **Source**: OPS Framework security architecture

- [ ] **1.3 Budget Warning UI Display**
  - [ ] Create `views/account_move_views.xml`
  - [ ] Add alert banner for `budget_warning` field on vendor bill form
  - [ ] Add to `__manifest__.py` data list
  - **Source**: OPS original (field exists, UI missing)

- [ ] **1.4 Budget Committed Amount SQL Optimization**
  - [ ] Replace `filtered()` with raw SQL query in `_compute_committed_amount()`
  - [ ] Add branch filtering to query
  - [ ] Add proper index recommendations
  - **Source**: OM Account Budget pattern (SQL performance)

---

### PHASE 2: CORE ACCOUNTING FEATURES (Priority: HIGH) ✅ COMPLETE
> Enterprise accounting essentials from OM + OPS requirements

- [x] **2.1 Period Locking System** *(Adopt from OM Fiscal Year + Enhance)* ✅
  - [x] Create `ops.fiscal.period` model with soft/hard lock states
  - [x] Add period lock fields to `res.company`
  - [x] Create period close wizard with checklist
  - [x] Add validation on `account.move` posting against locked periods
  - [x] Add branch-level period locking
  - [x] Create period close checklist template
  - **Source**: `om_fiscal_year` + OPS enhancement (branch + checklist)
  - **Completed**: Session 2 - v19.0.10.0.0

- [x] **2.2 Three-Way Match Enforcement** ✅
  - [x] Add `three_way_match_status` field to `account.move`
  - [x] Add `matched_po_ids`, `matched_picking_ids` computed fields
  - [x] Implement `_compute_three_way_match()` logic
  - [x] Add match status banner to vendor bill form
  - [x] Optional: Block posting of unmatched bills (configurable)
  - [x] Override wizard for authorized users
  - **Source**: OPS original requirement (enterprise control)
  - **Completed**: Session 2 - v19.0.11.0.0

- [x] **2.3 Auto-Depreciation Cron Job** ✅
  - [x] Create `data/cron_depreciation.xml`
  - [x] Add `cron_post_due_depreciation()` method to `ops.asset.depreciation`
  - [x] Add error handling and logging
  - [x] Add configuration option to enable/disable (category-level)
  - [x] Monthly reminder cron for pending depreciation
  - [x] Period lock integration (skip hard-locked periods)
  - **Source**: `om_account_asset` pattern + OPS enhancement
  - **Completed**: Session 2 - v19.0.12.0.0

- [x] **2.4 Degressive Depreciation Fix** ✅
  - [x] Add `method_progress_factor` field to `ops.asset.category`
  - [x] Add `method_number` and `method_period` for flexible scheduling
  - [x] Update `generate_depreciation_schedule()` in `ops.asset` for degressive method
  - [x] Add prorata temporis support
  - [x] Add `date_first_depreciation` option
  - [x] Implement `_compute_linear_depreciation()` method
  - [x] Implement `_compute_degressive_depreciation()` method
  - [x] Implement `_compute_degressive_then_linear()` method
  - [x] Add `sequence` and `remaining_value` to depreciation lines
  - **Source**: `om_account_asset` (complete implementation)
  - **Completed**: Session 2 - v19.0.13.0.0

---

### PHASE 3: RECURRING & AUTOMATION (Priority: MEDIUM)
> Journal automation framework from OM + OPS governance

- [ ] **3.1 Recurring Journal Framework** *(Adopt from OM Recurring Payments)*
  - [ ] Create `ops.recurring.template` model (from `account.recurring.template`)
  - [ ] Create `ops.recurring.entry` model (from `recurring.payment`)
  - [ ] Create `ops.recurring.entry.line` model
  - [ ] Add branch/BU assignment
  - [ ] Add approval workflow option
  - [ ] Add auto-reversal flag for accruals
  - [ ] Create cron job for scheduled execution
  - **Source**: `om_recurring_payments` + OPS governance layer

- [ ] **3.2 Journal Entry Templates**
  - [ ] Create `ops.journal.template` model
  - [ ] Create `ops.journal.template.line` model
  - [ ] Add quick-create action from template
  - [ ] Add branch/BU defaults
  - **Source**: OPS original requirement

- [ ] **3.3 Auto-Reversal Entries**
  - [ ] Add `auto_reverse` boolean to `account.move`
  - [ ] Add `reversal_date` field
  - [ ] Create reversal cron job
  - [ ] Add to recurring template options
  - **Source**: OPS original + accounting best practice

---

### PHASE 4: FINANCIAL REPORTS ENHANCEMENT (Priority: MEDIUM)
> Adopt OM report hierarchy + enhance with OPS features

- [ ] **4.1 Configurable Financial Report Structure** *(Adopt from OM)*
  - [ ] Create `ops.financial.report` model (from `account.financial.report`)
  - [ ] Implement hierarchical report structure (parent/children)
  - [ ] Add report types: sum, accounts, account_type, report_value
  - [ ] Migrate existing Balance Sheet/P&L to use this structure
  - [ ] Add branch filtering to report generation
  - **Source**: `accounting_pdf_reports` model structure

- [ ] **4.2 Customer Follow-up System** *(Adopt from OM)*
  - [ ] Create `ops.followup` model (from `followup.followup`)
  - [ ] Create `ops.followup.line` model (from `followup.line`)
  - [ ] Add delay-based escalation levels
  - [ ] Add email template integration
  - [ ] Add branch assignment
  - [ ] Add approval override for credit release
  - **Source**: `om_account_followup` + OPS governance

- [ ] **4.3 Daily Cash/Bank Reports** *(Adopt from OM)*
  - [ ] Add Cash Book report wizard
  - [ ] Add Day Book report wizard
  - [ ] Add Bank Book report wizard
  - [ ] Add branch filtering
  - [ ] Add Excel export
  - **Source**: `om_account_daily_reports` + OPS Excel export

---

### PHASE 5: ADVANCED FEATURES (Priority: LOW)
> Future enhancements after core stabilization

- [ ] **5.1 Inter-Branch Transfer Accounting**
  - [ ] Create `ops.interbranch.transfer` model
  - [ ] Add transit account configuration
  - [ ] Auto-create mirror entries in receiving branch
  - [ ] Add reconciliation workflow
  - **Source**: OPS original requirement

- [ ] **5.2 Bank Reconciliation Module**
  - [ ] Study `om_account_bank_statement_import` code
  - [ ] Create `ops.bank.reconciliation` wizard
  - [ ] Add statement import (CSV/OFX)
  - [ ] Add auto-matching logic
  - [ ] Add branch filtering
  - **Source**: OM bank import + OPS enhancement

- [ ] **5.3 IFRS 16 Lease Accounting**
  - [ ] Create `ops.lease` model
  - [ ] Create `ops.lease.payment.schedule` model
  - [ ] Implement ROU asset recognition
  - [ ] Implement lease liability calculation
  - [ ] Add interest expense amortization
  - **Source**: OPS original requirement

- [ ] **5.4 Asset Impairment**
  - [ ] Add impairment fields to `ops.asset`
  - [ ] Create impairment wizard
  - [ ] Auto-adjust depreciation schedule after impairment
  - **Source**: OPS original requirement

- [ ] **5.5 FX Revaluation**
  - [ ] Create `ops.fx.revaluation.wizard`
  - [ ] Auto-calculate unrealized gain/loss
  - [ ] Create revaluation JE
  - [ ] Add to period close checklist
  - **Source**: OPS original requirement

---

## 🔄 ADOPTION MATRIX: OM → OPS

| OM Module | OM Feature | OPS Adoption | Enhancement |
|-----------|------------|--------------|-------------|
| `om_fiscal_year` | Fiscal Year model | ✅ Adopt | + Branch locking |
| `om_fiscal_year` | Period date validation | ✅ Adopt | + Soft/Hard close |
| `om_account_asset` | Asset categories | ⏭️ Skip (OPS has) | - |
| `om_account_asset` | Degressive depreciation | ✅ Adopt logic | Fix in OPS |
| `om_account_asset` | Prorata temporis | ✅ Adopt | Add to OPS |
| `om_account_asset` | Grouped JE creation | ✅ Adopt pattern | Add to OPS |
| `om_account_budget` | Budget model | ⏭️ Skip (OPS has) | - |
| `om_account_budget` | SQL practical amount | ✅ Adopt pattern | Fix OPS query |
| `om_account_budget` | Analytic integration | ✅ Adopt | Add to OPS |
| `om_recurring_payments` | Recurring templates | ✅ Adopt & Enhance | + Approval workflow |
| `om_recurring_payments` | Payment scheduling | ✅ Adopt & Enhance | + JE (not just payments) |
| `om_account_followup` | Follow-up levels | ✅ Adopt & Enhance | + Branch assignment |
| `om_account_followup` | Email templates | ✅ Adopt | - |
| `om_account_followup` | Manual actions | ✅ Adopt | + Approval override |
| `om_account_daily_reports` | Cash Book | ✅ Adopt & Enhance | + Branch + Excel |
| `om_account_daily_reports` | Day Book | ✅ Adopt & Enhance | + Branch + Excel |
| `om_account_daily_reports` | Bank Book | ✅ Adopt & Enhance | + Branch + Excel |
| `accounting_pdf_reports` | Report hierarchy model | ✅ Adopt | + Branch filter |
| `accounting_pdf_reports` | Report types | ✅ Adopt | - |

---

## 📁 FILES TO CREATE/MODIFY

### New Files to Create
```
ops_matrix_accounting/
├── models/
│   ├── ops_fiscal_period.py          # Period locking
│   ├── ops_recurring.py              # Recurring journals
│   ├── ops_followup.py               # Customer follow-up
│   ├── ops_financial_report_config.py # Report hierarchy
│   ├── ops_interbranch_transfer.py   # Inter-branch (Phase 5)
│   └── res_company.py                # Company settings extension
├── security/
│   └── ops_accounting_rules.xml      # Record rules
├── views/
│   ├── account_move_views.xml        # Budget warning banner
│   ├── ops_fiscal_period_views.xml   # Period locking UI
│   ├── ops_recurring_views.xml       # Recurring journals UI
│   ├── ops_followup_views.xml        # Follow-up UI
│   ├── res_config_settings_views.xml # PDC settings
│   └── ops_daily_reports_views.xml   # Daily reports menu
├── wizard/
│   ├── ops_period_close_wizard.py    # Period close checklist
│   ├── ops_cash_book_wizard.py       # Cash book report
│   ├── ops_day_book_wizard.py        # Day book report
│   └── ops_bank_book_wizard.py       # Bank book report
├── data/
│   ├── cron_depreciation.xml         # Auto-depreciation
│   ├── cron_recurring.xml            # Recurring execution
│   └── followup_data.xml             # Default follow-up levels
└── report/
    ├── ops_cash_book_template.xml    # Cash book QWeb
    ├── ops_day_book_template.xml     # Day book QWeb
    └── ops_bank_book_template.xml    # Bank book QWeb
```

### Existing Files to Modify
```
ops_matrix_accounting/
├── __manifest__.py                   # Add new files
├── models/
│   ├── __init__.py                   # Import new models
│   ├── ops_pdc.py                    # Add JE creation
│   ├── ops_budget.py                 # Fix SQL query
│   ├── ops_asset.py                  # Add degressive
│   ├── ops_asset_category.py         # Add degressive factor
│   ├── ops_asset_depreciation.py     # Add cron method
│   └── account_move.py               # Add 3-way match
├── wizard/
│   └── __init__.py                   # Import new wizards
├── views/
│   └── accounting_menus.xml          # Add new menu items
└── security/
    └── ir.model.access.csv           # Add new model access
```

---

## 🎯 EXECUTION ORDER FOR CLAUDE CODE

### Session 1: Critical Fixes
1. `ops_pdc.py` - Add JE creation
2. `security/ops_accounting_rules.xml` - Create record rules
3. `views/account_move_views.xml` - Budget warning UI
4. `ops_budget.py` - SQL optimization
5. `__manifest__.py` - Add new files

### Session 2: Period Locking
1. `models/ops_fiscal_period.py` - Create model
2. `models/res_company.py` - Add settings
3. `views/ops_fiscal_period_views.xml` - Create UI
4. `wizard/ops_period_close_wizard.py` - Create wizard
5. Update `account_move.py` - Add validation

### Session 3: Three-Way Match + Auto-Depreciation
1. `account_move.py` - Add 3-way match
2. `views/account_move_views.xml` - Add match UI
3. `data/cron_depreciation.xml` - Create cron
4. `ops_asset_depreciation.py` - Add cron method
5. `ops_asset_category.py` - Add degressive factor

### Session 4: Recurring Journals
1. `models/ops_recurring.py` - Create models
2. `views/ops_recurring_views.xml` - Create UI
3. `data/cron_recurring.xml` - Create cron
4. Update menus and security

### Session 5: Follow-up + Daily Reports
1. `models/ops_followup.py` - Create models
2. `views/ops_followup_views.xml` - Create UI
3. Daily report wizards and templates
4. Update menus and security

---

## ✅ ACCEPTANCE CRITERIA

### Phase 1 Complete When:
- [ ] PDC deposit creates posted JE with correct accounts
- [ ] PDC clear creates posted JE with correct accounts
- [ ] PDC bounce creates reversal JE
- [ ] Users only see PDCs from their assigned branches
- [ ] Budget warning shows on vendor bills exceeding budget
- [ ] Budget committed amount calculates in < 1 second

### Phase 2 Complete When: ✅ ALL COMPLETE
- [x] Period can be soft-locked (warning) and hard-locked (blocked)
- [x] Journal entries rejected for hard-locked periods
- [x] Three-way match status shows on vendor bills
- [x] Depreciation posts automatically via cron
- [x] Degressive depreciation calculates correctly

### Phase 3 Complete When:
- [ ] Recurring templates can be created and scheduled
- [ ] Scheduled entries create automatically via cron
- [ ] Auto-reversal creates reversal on specified date
- [ ] Approval workflow works for recurring entries

---

**Ready for Claude Code execution. Start with Session 1: Critical Fixes.**