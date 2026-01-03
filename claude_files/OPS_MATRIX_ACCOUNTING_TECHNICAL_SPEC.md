# OPS Matrix Accounting - Technical Specification

## Module: OPS Matrix Accounting

### 1. General Info
- **Technical Name:** `ops_matrix_accounting`
- **Version:** 19.0.1.0.0
- **Category:** Accounting/Accounting
- **Application:** Yes (Installable)
- **License:** LGPL-3
- **Author:** Gemini-3.0-Pro
- **Website:** http://www.yourcompany.com

#### Dependencies:
- `ops_matrix_core` (Required - matrix structure, analytic sync)
- `account` (Standard Odoo accounting)

#### Summary:
Transforms standard Odoo Invoicing into enterprise Accounting suite:
1. **PDC Management:** Post-Dated Checks with workflow (register â†’ deposit â†’ clear)
2. **Budget Control:** Multi-dimensional budgets with real-time availability checks
3. **Professional Reports:** GL, Trial Balance, P&L, Balance Sheet
4. **Excel Export Engine:** In-memory generation, zero DB bloat

---

## 2. Data Models & Fields

### Model: `ops.budget`
**Technical Name:** `ops.budget`
**Description:** Matrix-aware budget for branch/business unit with line-item cost control.
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `date_from desc, id desc`

#### Fields:

##### Budget Header
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Tracking | Budget display name |
| `active` | Boolean | Default=True | Soft delete flag |
| `branch_id` | Many2one (`ops.branch`) | Required, Tracking | Budget applies to branch |
| `business_unit_id` | Many2one (`ops.business.unit`) | Required, Tracking | Budget applies to BU |
| `date_from` | Date | Required, Tracking | Budget start date |
| `date_to` | Date | Required, Tracking | Budget end date |
| `state` | Selection | Default='draft', Tracking | Status: draft, confirmed, done, cancelled |

##### Budget Totals (Computed)
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `total_planned` | Monetary | Computed, Stored | Sum of line planned amounts |
| `total_practical` | Monetary | Computed, Stored | Sum of line actual amounts |
| `total_committed` | Monetary | Computed, Stored | Sum of line committed amounts |
| `available_balance` | Monetary | Computed, Stored | planned - actual - committed |
| `currency_id` | Many2one (`res.currency`) | Required, Default=company currency | Budget currency |

##### Budget Lines
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `line_ids` | One2many (`ops.budget.line`, 'budget_id') | Readonly | Line items (one per GL account) |

#### Constraints:
- **SQL:** `UNIQUE(branch_id, business_unit_id, date_from, date_to)` - No overlapping budgets for same matrix dimension
- **Python:**
  - `_check_dates()`: date_to â‰¥ date_from
  - `_check_dates()` (continued): Check no overlapping date ranges for same branch/BU

#### Computed Fields:
**`_compute_totals()`**:
- `total_planned` = SUM(line_ids.planned_amount)
- `total_practical` = SUM(line_ids.practical_amount)
- `total_committed` = SUM(line_ids.committed_amount)
- `available_balance` = total_planned - total_practical - total_committed

#### Key Methods:

**`action_confirm()`**:
- **Logic:** Write state='confirmed'
- **Purpose:** Lock budget for execution

**`action_done()`**:
- **Logic:** Write state='done'
- **Purpose:** Close budget period

**`action_cancel()`**:
- **Logic:** Write state='cancelled'
- **Purpose:** Void budget

**`action_draft()`**:
- **Logic:** Write state='draft'
- **Purpose:** Reset to draft for editing

**`check_budget_availability(account_id, branch_id, business_unit_id, amount)`** [Class]:
- **Parameters:** GL account, branch, BU, proposed amount
- **Logic:**
  1. Search active confirmed budget for branch/BU/date-range
  2. If found: find line for account
  3. Calculate available = planned - actual - committed
  4. Return True if available â‰¥ amount, else False
- **Purpose:** Pre-check before committing purchases/expenses

---

### Model: `ops.budget.line`
**Technical Name:** `ops.budget.line`
**Description:** Single GL account budget line with actual/committed tracking.
**Order:** `general_account_id`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `budget_id` | Many2one (`ops.budget`) | Required, Ondelete='cascade' | Parent budget |
| `general_account_id` | Many2one (`account.account`) | Required, Domain=[('account_type', '=', 'expense')] | GL account (expense only) |
| `planned_amount` | Monetary | Required | Budgeted amount |
| `practical_amount` | Monetary | Computed, Stored | Actual invoiced amount |
| `committed_amount` | Monetary | Computed, Stored | Committed (PO) amount |
| `available_amount` | Monetary | Computed, Stored | planned - actual - committed |
| `currency_id` | Many2one | Related to budget_id.currency_id | Currency (denormalized) |
| `company_id` | Many2one | Related to budget_id.branch_id.company_id | Company (denormalized) |

#### Constraints:
- **SQL:** `UNIQUE(budget_id, general_account_id)` - Only one line per account per budget

#### Computed Fields:

**`_compute_practical_amount()`**:
- **Logic:**
  1. Search `account.move.line` where:
     - account_id = this.general_account_id
     - branch_id = budget.branch_id
     - business_unit_id = budget.business_unit_id
     - date between budget.date_from and date_to
     - move.state = 'posted'
     - move.move_type in ['in_invoice', 'in_refund']
  2. Sum debit amount from results
  3. Store as practical_amount

**`_compute_committed_amount()`**:
- **Logic:**
  1. Search `purchase.order.line` where:
     - account_id = this.general_account_id
     - order.branch_id = budget.branch_id
     - order.business_unit_id = budget.business_unit_id
     - order.date_order between date_from and date_to
     - order.state in ['purchase', 'done']
     - invoice_status != 'invoiced' (not yet invoiced)
  2. Sum price_total from results
  3. Store as committed_amount

**`_compute_available_amount()`**:
- planned_amount - practical_amount - committed_amount

---

### Model: `ops.pdc` (Post-Dated Check)
**Technical Name:** `ops.pdc`
**Description:** Post-Dated Check management - track customer/vendor checks with maturity dates.
**Inheritance:** `mail.thread`, `mail.activity.mixin`
**Order:** `maturity_date desc, id desc`

#### Fields:

##### Identification & Dates
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Readonly, Default='New' | Auto-generated reference via sequence 'ops.pdc' |
| `partner_id` | Many2one (`res.partner`) | Required | Check issuer/receiver |
| `date` | Date | Required, Tracking | Check issue date |
| `maturity_date` | Date | Required, Tracking | When check is due/clearable |
| `amount` | Monetary | Required | Check amount |
| `currency_id` | Many2one (`res.currency`) | Required, Default=company | Check currency |
| `payment_type` | Selection | Required | 'inbound' (customer check) or 'outbound' (vendor check) |

##### Check Details
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `bank_id` | Many2one (`res.bank`) | Required | Check issuing bank |
| `check_number` | Char | Required | Physical check number |
| `state` | Selection | Default='draft', Tracking | Workflow: draft, registered, deposited, cleared, bounced, cancelled |

##### Matrix Dimensions
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `branch_id` | Many2one (`ops.branch`) | Required | Check branch (for reporting) |
| `business_unit_id` | Many2one (`ops.business.unit`) | Required | Check BU (for reporting) |

##### Accounting
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `journal_id` | Many2one (`account.journal`) | Required, Domain=[('type', '=', 'bank')] | Bank journal for registration |
| `holding_account_id` | Many2one (`account.account`) | Required | Interim account while check pending |
| `move_id` | Many2one (`account.move`) | Readonly | Journal entry for registration (draftâ†’registered) |
| `deposit_move_id` | Many2one (`account.move`) | Readonly | Journal entry for deposit (registeredâ†’deposited) |

#### Constraints:
- **Python:** `_check_dates()`: maturity_date â‰¥ date (cannot mature before issue)

#### Key Methods:

**`action_register()`**:
- **Trigger:** Button "Register PDC"
- **Precondition:** state='draft'
- **Logic:**
  1. Determine accounts based on payment_type:
     - **Inbound:** debit=holding_account, credit=partner_account_receivable
     - **Outbound:** debit=partner_account_payable, credit=holding_account
  2. Create account.move with lines:
     - Line 1: debit to one account, credit zero, with branch/BU
     - Line 2: credit to other account, debit zero, with branch/BU
  3. Auto-post the move (no manual approval needed)
  4. Write: state='registered', move_id=created_move
- **Effect:** PDC recorded in GL; money held in suspense account pending maturity

**`action_deposit()`**:
- **Trigger:** Button "Deposit PDC"
- **Precondition:** state='registered'
- **Logic:**
  1. Get journal default bank account
  2. Create move with lines:
     - **Inbound:** debit=bank_account, credit=holding_account
     - **Outbound:** debit=holding_account, credit=bank_account
  3. Auto-post move
  4. Write: state='deposited', deposit_move_id=created_move
- **Effect:** PDC moved from holding to bank; assumed cleared on maturity

**`_prepare_move_line_vals(account_id, debit, credit, name_suffix)`**:
- **Purpose:** Helper to create consistent move line values with matrix dimensions
- **Returns:** Dict with account_id, partner_id, name, debit, credit, branch_id, business_unit_id

---

### Model: `ops.general.ledger.wizard` (Transient)
**Technical Name:** `ops.general.ledger.wizard`
**Description:** UI wizard for General Ledger report generation.
**Inheritance:** `ops.financial.report.wizard`

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `account_ids` | Many2many (`account.account`) | Optional | Specific accounts to include (empty=all) |

#### Key Methods:

**`action_print_pdf()`**:
- **Logic:**
  1. Build data dict: date_from, date_to, target_move, journal_ids, account_ids, company_id
  2. Call report action 'ops_matrix_accounting.action_report_general_ledger'
  3. Return report action
- **Purpose:** Generate PDF GL report

**`action_export_xlsx()`**:
- **Logic:**
  1. Build data dict (convert dates to strings)
  2. Call report action 'ops_matrix_accounting.action_report_general_ledger_xlsx'
  3. Return report action
- **Purpose:** Export GL to Excel

---

### Model: `ops.financial.report.wizard` (Transient)
**Technical Name:** `ops.financial.report.wizard`
**Description:** Base financial report wizard with lightweight, in-memory design (Zero DB Bloat).

#### Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `report_type` | Selection | Default='gl', Required | Report: pl, bs, gl, aged |
| `date_from` | Date | Required | Period start (default=1st of current month) |
| `date_to` | Date | Required | Period end (default=last of current month) |
| `branch_id` | Many2one (`ops.branch`) | Optional | Filter by branch (via analytic account) |
| `target_move` | Selection | Default='posted', Required | 'posted' or 'all' moves |
| `company_id` | Many2one (`res.company`) | Required, Default=current | Company filter |
| `journal_ids` | Many2many (`account.journal`) | Optional | Specific journals (empty=all) |

#### Key Methods:

**`default_get(fields_list)`** [Class]:
- **Logic:**
  1. Calculate first day of current month
  2. Calculate last day of current month
  3. Set date_from and date_to defaults
  4. Return merged defaults
- **Purpose:** Auto-populate date range to current month

**`_get_domain()`**:
- **Logic:**
  1. Start: [('date', '>=', date_from), ('date', '<=', date_to), ('company_id', '=', company_id)]
  2. If target_move='posted': add ('move_id.state', '=', 'posted')
  3. If branch_id set: add analytic_account_id filter
  4. Return domain
- **Purpose:** Build account.move.line filter for on-screen/export

**`_get_context_groupings()`**:
- **Logic:**
  1. Based on report_type, return context dict with pivot groupings:
     - **P&L:** Group by account_id, measures=debit/credit/balance
     - **BS:** Group by account_id, measures=debit/credit/balance
     - **GL:** Group by account_id and date, measures=debit/credit/balance
     - **Aged:** Group by partner_id, measures=debit/credit/balance
  2. Return context
- **Purpose:** Set default pivot/tree view groupings

**`action_view_data()`**:
- **Logic:**
  1. Get domain from `_get_domain()`
  2. Get context from `_get_context_groupings()`
  3. Return ir.actions.act_window to account.move.line with pivot/tree views
  4. Domain and context passed in action
- **Purpose:** Open account.move.line in on-screen pivot view (zero intermediate records)

**`action_print_pdf()`**:
- **Logic:**
  1. Call report action 'ops_matrix_accounting.action_report_ops_financial'
  2. Return report action
- **Purpose:** Generate PDF report

**`action_export_xlsx()`**:
- **Logic:**
  1. In-memory generation of Excel file (see reports section)
  2. Return binary download
- **Purpose:** Export to Excel

---

### Model: `product.category` [Extension]
**Technical Name:** `product.category`
**Description:** Product category extended with default accounting method enforcement.
**Inheritance:** `product.category`

#### Modified Fields:
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `property_cost_method` | Selection | Readonly=True, Default='fifo' | Costing: FIFO enforced (no override) |
| `property_valuation` | Selection | Readonly=True, Default='real_time' | Valuation: Real-time enforced (no override) |

#### Key Methods:

**`default_get(fields_list)`** [Override]:
- **Logic:**
  1. Call parent default_get()
  2. Attempt to find/populate accounting accounts:
     - property_account_income_categ_id (search account_type='income')
     - property_account_expense_categ_id (search account_type='expense')
     - property_stock_valuation_account_id (search account_type='asset_current')
     - property_stock_account_input_categ_id (search account_type='asset_current')
     - property_stock_account_output_categ_id (search account_type='asset_current')
  3. Gracefully fall back if lookup fails
  4. Return merged defaults
- **Purpose:** Auto-populate accounting accounts to prevent blank fields

---

### Model: `product.template` [Extension]
**Technical Name:** `product.template`
**Description:** Product template extended to ensure accounting defaults inherited from category.
**Inheritance:** `product.template`

#### Key Methods:

**`default_get(fields_list)`** [Override]:
- **Logic:**
  1. Call parent default_get()
  2. If no categ_id:
     - Search for "All" category (root)
     - If not found: create it
     - Set categ_id to that category
  3. Return merged defaults
- **Purpose:** Ensure every product has a category (avoids nulls)

**`_onchange_categ_id()`**:
- **Logic:**
  1. When category changes, ensure accounting fields inherited
  2. (Not fully implemented, but intent is to sync from category)
- **Purpose:** Keep product accounting fields in sync with category defaults

---

## 3. Key Methods & Business Logic

### OPS Budget

**`check_budget_availability(account_id, branch_id, business_unit_id, amount)`** [Class]:
- **Trigger:** Called from purchase order workflow before confirmation
- **Logic:**
  1. Search for confirmed budget: branch+BU+active date range
  2. If none found: return False (no budget = no spend allowed)
  3. Find budget line for GL account
  4. If no line: return False (account not budgeted)
  5. Calculate available = planned - actual - committed
  6. Return True if available â‰¥ amount
- **Return:** Boolean

---

### OPS PDC Workflow

**State Machine:**
```
draft â†’ registered â†’ deposited â†’ cleared
         â†“            â†“            â†“
      (action_register)  (action_deposit)  (auto on maturity)
      creates move1    creates move2     (optional cron)
      GL: xx â†’ holding  GL: holding â†’ bank
```

**`action_register()`**:
- **When:** User clicks "Register PDC" button
- **Effect:** GL entry moves money from partner account to holding account
- **Uses:** journal_id, holding_account_id, partner receivable/payable accounts

**`action_deposit()`**:
- **When:** User clicks "Deposit PDC" button (after maturity passed)
- **Effect:** GL entry moves money from holding to bank
- **Uses:** journal_id default account

---

### Financial Report Wizard

**Zero DB Bloat Design:**
- **No intermediate records:** All reports query account.move.line directly
- **In-memory processing:** Excel generation uses Python io module
- **Lightweight:** Wizard is transient (auto-delete after use)
- **Flexible:** Pivot/tree views allow user-driven analysis without report coding

---

## 4. XML Views & Interface

### Budget Views

**Form View:**
- **Header:** state (statusbar), action buttons (confirm, done, cancel, draft)
- **Group 1:** name (editable heading), active
- **Group 2:** branch_id, business_unit_id, date_from, date_to
- **Totals Group:** total_planned (readonly), total_practical (readonly), total_committed (readonly), available_balance (readonly)
- **Tab - Budget Lines:**
  - Editable list: general_account_id, planned_amount
  - Computed columns: practical_amount, committed_amount, available_amount (all readonly)

**Tree View:**
- Columns: name, branch_id, business_unit_id, date_from, date_to, state, total_planned, available_balance
- Decoration: state (draft=blue, confirmed=green, done=gray, cancelled=red)

**Search View:**
- Fields: name, branch_id, business_unit_id, state
- Filters: Active (default), Drafted, Confirmed, Closed

---

### PDC Views

**Form View:**
- **Header:** state (statusbar), action buttons (register, deposit, bounce, cancel)
- **Group 1:** name, partner_id, date, maturity_date
- **Group 2:** amount, currency_id, payment_type
- **Group 3:** bank_id, check_number, state
- **Accounting Group:** journal_id, holding_account_id, move_id (readonly), deposit_move_id (readonly)
- **Matrix Group:** branch_id, business_unit_id

**Tree View:**
- Columns: name, partner_id, check_number, maturity_date, amount, state, branch_id
- Decoration: state (draft=blue, registered=orange, cleared=green, bounced=red)

**Search View:**
- Fields: name, partner_id, check_number, payment_type, state
- Filters: Draft, Registered, Cleared, Bounced

---

### General Ledger Wizard Views

**Form View:**
- **Header:** title
- **Group 1:** date_from, date_to, target_move
- **Group 2:** branch_id, company_id, journal_ids, account_ids
- **Footer Buttons:** "View Data" (pivot), "Print PDF", "Export Excel"

---

### Financial Report Wizard Views

**Form View:**
- **Header:** title
- **Group 1:** report_type, date_from, date_to, target_move
- **Group 2:** branch_id, company_id, journal_ids
- **Footer Buttons:** "View Data" (pivot), "Print PDF", "Export Excel"

---

## 5. Security

### Access Control (`security/ir.model.access.csv`):

| Model | User Group | Read | Write | Create | Delete |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ops.budget` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.budget` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.budget.line` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.budget.line` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.pdc` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ— |
| `ops.pdc` | group_ops_manager | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.general.ledger.wizard` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ“ |
| `ops.financial.report.wizard` | group_ops_user | âœ“ | âœ“ | âœ“ | âœ“ |

---

## 6. Data & Configuration Files

### Menus (`ops_accounting_menus.xml`):
- **Root Menu:** "Matrix Accounting"
  - Submenu: "PDC Management" â†’ Action: PDC list/form
  - Submenu: "Budget Control" â†’ Action: Budget list/form
  - Submenu: "Reports"
    - Action: "General Ledger Wizard"
    - Action: "Financial Report Wizard"

---

## 7. Reports

### General Ledger Report (`ops_general_ledger_template.xml`):
- **Input:** account.move.line recordset filtered by wizard domain
- **Columns:** Date, Account, Description, Debit, Credit, Balance
- **Group By:** Account (subtotals per account)
- **Format:** Qweb HTML â†’ PDF

### Financial Report Template (`ops_financial_report_template.xml`):
- **Dynamic:** Template adapts based on report_type selected in wizard
- **P&L:** Summarize income/expense accounts with comparisons
- **BS:** Show assets/liabilities/equity
- **GL:** Full drill-down by date and account
- **Aged:** Aged AR/AP by partner

### General Ledger XLSX (`ops_general_ledger_xlsx.py`):
- **Logic:**
  1. Query account.move.line with wizard filters
  2. Use Python openpyxl to build workbook in memory
  3. Add sheets: Summary, Detailed GL, Trial Balance
  4. Format: Headers, subtotals, styling
  5. Return as binary attachment
- **Returns:** Binary (base64 encoded Excel file)

---

## 8. Integration Points

### With ops_matrix_core:
- **Branch & BU:** Budget and PDC scoped to matrix dimensions
- **Analytic Accounts:** Financial reports filter by branch analytic
- **Sequences:** Auto-generated PDC names, budget codes

### With Odoo Account:
- **Moves:** PDC creates account.move with posted state
- **Journals:** PDC uses bank journal for registration/deposit
- **GL Accounts:** Budget lines control against specific GL accounts
- **Partners:** PDC tracks customer/vendor receivables/payables

### With Odoo Stock:
- **Budget Integration:** Budget committed amount computed from PO lines
- **Landed Costs:** PDC can represent post-dated vendor invoices

---

## 9. Workflow Examples

### Budget Management Workflow:
1. Finance creates budget for Q1 2024: branch="North", BU="Sales"
2. Adds lines: Office Supplies $5K, Travel $10K, etc.
3. Sets state='confirmed' to activate budget controls
4. During Q1, purchase orders checked against `check_budget_availability()`
5. System tracks: planned (budget line), practical (invoices posted), committed (PO lines not yet invoiced)
6. Manager can view available balance at any time
7. At quarter end: state='done' to close budget

### PDC Workflow:
1. Customer gives company a post-dated check: $10K check #1234, maturity=30 days
2. Accounting creates PDC record, state='draft'
3. Clicks "Register PDC":
   - GL: Dr. PDC Holding Account, Cr. Customer A/R
   - state='registered'
4. After maturity date, accounting clicks "Deposit PDC":
   - GL: Dr. Bank Account, Cr. PDC Holding Account
   - state='deposited'
5. Eventually marked as "cleared" when bank confirms

---

## 10. Key Design Patterns

### 1. Zero DB Bloat (Financial Reports)
- Transient wizards query account.move.line directly
- No intermediate report records stored
- Export generation in memory
- Lightweight, scalable design

### 2. Real-Time Budget Tracking
- Practical amount computed from posted invoices (exact)
- Committed amount computed from open POs (forward-looking)
- Available = planned - practical - committed (accurate spend capacity)

### 3. Multi-Dimensional Budget Scope
- Budget scoped to Branch + Business Unit pair
- Prevents overlapping budgets for same organization unit
- Enables distributed budgeting (each branch/BU owns their budget)

### 4. Matrix-Aware GL Entries
- Every account.move created by PDC includes branch_id, business_unit_id
- Enables multi-dimensional financial reporting
- Supports consolidation by organizational structure

### 5. Controlled Costing Method
- Product categories enforce FIFO + Real-Time valuation (no user override)
- Ensures consistent inventory costing across organization

---

## 11. Future Extensibility Hooks

### Budget Extensions:
- Approval workflows (budget requires CFO sign-off)
- Variance analysis (actual vs. planned trends)
- Rolling forecast (re-forecast as new actuals arrive)

### PDC Extensions:
- Endorsement tracking (check can be endorsed to third party)
- Reconciliation workflow (auto-clear on bank statement match)
- Multi-currency PDCs with FX gain/loss

### Report Extensions:
- Drill-down to transaction level (GL line â†’ source document)
- Consolidated reporting (across multiple branches/BUs)
- Intercompany transactions (branch/BU can be different company)

---
