# PHASE 3: Financial Report Wizards (9 Reports)
# Run with: claude -p "$(cat PHASE_3_FINANCIAL_WIZARDS.md)"
# Prerequisite: Phases 0-2 completed
# Estimated: ~45 minutes (largest phase)

## CONTEXT
You are building the financial report wizards for OPS Framework v2 in `/opt/gemini_odoo19/addons/ops_matrix_accounting/`.

Read FIRST:
1. Master spec: `cat /opt/gemini_odoo19/addons/claude_files/REPORT_ENGINE_REWRITE_MASTER.md`
2. Data contracts: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_report_contracts.py`
3. Base wizard: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py`
4. Security mixin: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_intelligence_security_mixin.py`
5. Archived God wizard (reference for query logic): `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/wizard/ops_general_ledger_wizard_enhanced.py`

## CRITICAL DATA RULES

### Running Balance: ALWAYS per-group
```python
for group in groups:
    running = group.opening_balance
    for line in group.lines:
        running += (line.debit - line.credit)
        line.balance = running
    group.closing_balance = running
```
NEVER compute a global running balance across groups.

### Opening Balance: Sum all posted moves BEFORE date_from
```python
def _compute_initial_balances(self, groupby_field='account_id'):
    domain = [
        ('date', '<', self.date_from),
        ('company_id', '=', self.company_id.id),
        ('move_id.state', '=', 'posted'),
    ]
    domain += self._get_branch_filter_domain()
    # Additional filters (accounts, journals, partners) as needed
    data = self.env['account.move.line']._read_group(
        domain=domain,
        groupby=[groupby_field],
        aggregates=['debit:sum', 'credit:sum', 'balance:sum']
    )
    return {item[0].id: {'debit': item[1] or 0, 'credit': item[2] or 0, 'balance': item[3] or 0}
            for item in data if item[0]}
```

### Branch isolation: ALWAYS include in domain
```python
def _get_base_domain(self):
    domain = [
        ('company_id', '=', self.company_id.id),
    ]
    if self.target_move == 'posted':
        domain.append(('move_id.state', '=', 'posted'))
    if self.date_from:
        domain.append(('date', '>=', self.date_from))
    if self.date_to:
        domain.append(('date', '<=', self.date_to))
    # Branch isolation via mixin
    domain += self._get_branch_filter_domain()
    return domain
```

### Matrix filtering
```python
def _build_matrix_domain(self):
    """Build domain for branch + BU matrix filtering."""
    domain = []
    if self.branch_ids:
        domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
    if self.business_unit_ids:
        domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
    return domain
```

## YOUR TASK

### File 1: `wizard/ops_gl_wizard.py` — General Ledger (~300 lines)

Shape A report. Per-account grouping with opening balance and running balance.

Fields:
- account_ids (Many2many account.account)
- journal_ids (Many2many account.journal)
- partner_ids (Many2many res.partner)
- include_initial_balance (Boolean, default=True)
- display_account (Selection: all/movement/balance, default=movement)
- sort_by (Selection: date/account/partner, default=date)
- report_format (Selection: detailed/summary, default=detailed)

`_get_report_data()`:
1. Build domain from base + accounts + journals + partners
2. Compute initial balances per account (if enabled)
3. Search move lines, ordered by account_id, date, id
4. Group lines by account_id
5. For each account group: build LineGroup with opening_balance, iterate lines computing running_balance, compute closing_balance
6. Filter groups based on display_account (skip accounts with no movement or zero balance)
7. Build grand_totals
8. Return ShapeAReport as dict
9. visible_columns: date, entry, journal, label, ref, partner, branch, bu, debit, credit, balance

`_return_report_action()`:
```python
report = self.env.ref('ops_matrix_accounting.action_report_gl')
return report.report_action(self, data={'wizard_id': self.id, 'wizard_model': self._name})
```

### File 2: `wizard/ops_tb_wizard.py` — Trial Balance (~250 lines)

Shape C report. Dynamic columns: Account Code, Account Name, Initial Debit, Initial Credit, Period Debit, Period Credit, Ending Debit, Ending Credit.

Fields:
- account_ids (Many2many account.account)
- include_zero_balance (Boolean, default=False)
- show_hierarchy (Boolean, default=False)

`_get_report_data()`:
1. Compute initial balances per account (before date_from)
2. Compute period movements per account (date_from to date_to via _read_group)
3. Compute ending = initial + period
4. Split ending into debit/credit presentation
5. Build ColumnDef list and MatrixRow list
6. Build totals row
7. Return ShapeCReport as dict

### File 3: `wizard/ops_pnl_wizard.py` — Profit & Loss (~300 lines)

Shape B report. Revenue/Expense hierarchy.

Fields:
- comparative (Boolean, default=False)
- comparative_date_from, comparative_date_to (Date)
- show_percentage (Boolean, default=True — percentage of revenue)

`_get_report_data()`:
1. Query P&L accounts (income + expense types) grouped by account
2. Build hierarchy: Revenue section → Cost of Revenue → Gross Profit → Operating Expenses → Operating Income → Other Income/Expenses → Net Profit
3. Account type mapping to sections (check Odoo 19 account types: `income`, `income_other`, `expense`, `expense_depreciation`, `expense_direct_cost`)
4. If comparative: run same query for comparative period, populate 'previous' values
5. Compute percentages as % of total revenue
6. Return ShapeBReport as dict

### File 4: `wizard/ops_bs_wizard.py` — Balance Sheet (~250 lines)

Shape B report. Assets/Liabilities/Equity hierarchy. Uses `as_of_date` instead of date range.

Fields:
- as_of_date (Date, required=True)
- comparative (Boolean)
- comparative_as_of_date (Date)

`_get_report_data()`:
1. Query all BS accounts (asset/liability/equity types) cumulative to as_of_date
2. Build hierarchy: Current Assets → Non-current Assets → Total Assets / Current Liabilities → Non-current Liabilities → Equity → Total L+E
3. Compute retained earnings = sum of all P&L accounts up to as_of_date
4. Verify Assets = Liabilities + Equity (add verification note)
5. Return ShapeBReport

### File 5: `wizard/ops_cf_wizard.py` — Cash Flow (~300 lines)

Shape B report. Operating/Investing/Financing sections. Indirect method.

Fields:
- method (Selection: indirect/direct, default=indirect)

`_get_report_data()`:
1. For indirect method:
   - Start with Net Income (from P&L accounts)
   - Operating: add back depreciation, changes in working capital
   - Investing: changes in fixed asset accounts
   - Financing: changes in long-term liability and equity accounts
2. Group by section, compute section totals
3. Net Change in Cash = Operating + Investing + Financing
4. Return ShapeBReport

### File 6: `wizard/ops_aged_wizard.py` — Aged Receivables/Payables (~250 lines)

Shape C report. Dynamic aging columns.

Fields:
- partner_type (Selection: customer/vendor, required=True)
- partner_ids (Many2many res.partner)
- aging_type (Selection: by_due_date/by_invoice_date, default=by_due_date)
- period_length (Integer, default=30 — days per bucket)

`_get_report_data()`:
1. Query open (not fully reconciled) invoices/bills for partner_type
2. Compute age of each in days from as_of_date
3. Bucket into: Current, 1-30, 31-60, 61-90, 90+ (configurable via period_length)
4. Group by partner, compute per-partner and grand totals
5. Dynamic columns: Partner, Current, 1-{period}, {period+1}-{2*period}, ..., {3*period}+, Total
6. Return ShapeCReport

### File 7: `wizard/ops_partner_ledger_wizard.py` — Partner Ledger + SOA (~280 lines)

Shape A report. Per-partner grouping.

Fields:
- partner_ids (Many2many res.partner, required=True for SOA)
- partner_type (Selection: customer/vendor/all, default=all)
- report_type (Selection: partner_ledger/soa, default=partner_ledger)
- include_initial_balance (Boolean, default=True)
- reconciled (Selection: all/reconciled/unreconciled, default=all)

`_get_report_data()`:
1. Build domain: base + partner filter + reconciled filter
2. Compute initial balances per partner
3. Search move lines, ordered by partner_id, date, id
4. Group by partner_id
5. Per-partner: opening balance → running balance → closing balance
6. For SOA: filter to single partner, include document references
7. visible_columns: date, entry, journal, account_code, label, ref, debit, credit, balance
8. Return ShapeAReport

### File 8: `wizard/ops_financial_wizard_views.xml` — All wizard views

Create form views for all 7 wizards. Each view follows this pattern:
```xml
<record id="view_ops_gl_wizard_form" model="ir.ui.view">
    <field name="name">ops.gl.report.wizard.form</field>
    <field name="model">ops.gl.report.wizard</field>
    <field name="arch" type="xml">
        <form string="General Ledger">
            <group>
                <group string="Period">
                    <field name="date_from"/>
                    <field name="date_to"/>
                    <field name="target_move"/>
                </group>
                <group string="Filters">
                    <field name="account_ids" widget="many2many_tags"/>
                    <field name="journal_ids" widget="many2many_tags"/>
                    <field name="partner_ids" widget="many2many_tags"/>
                </group>
            </group>
            <group>
                <group string="Matrix Dimensions">
                    <field name="branch_ids" widget="many2many_tags"/>
                    <field name="business_unit_ids" widget="many2many_tags"/>
                    <field name="matrix_filter_mode"/>
                </group>
                <group string="Options">
                    <field name="include_initial_balance"/>
                    <field name="display_account"/>
                    <field name="sort_by"/>
                    <field name="report_format"/>
                    <field name="output_format"/>
                </group>
            </group>
            <group string="Template">
                <field name="report_template_id"/>
            </group>
            <footer>
                <button name="action_generate_report" string="Generate Report" type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>

<record id="action_gl_wizard" model="ir.actions.act_window">
    <field name="name">General Ledger</field>
    <field name="res_model">ops.gl.report.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>
```

Create views + window actions for all 7 wizards.

### File 9: Update `wizard/__init__.py`

Add imports for all new wizards:
```python
from . import ops_gl_wizard
from . import ops_tb_wizard
from . import ops_pnl_wizard
from . import ops_bs_wizard
from . import ops_cf_wizard
from . import ops_aged_wizard
from . import ops_partner_ledger_wizard
```

### File 10: Update `__manifest__.py`

Add new wizard view XML file to data list.

### File 11: Update `security/ir.model.access.csv`

Add ACL entries for ALL new wizard TransientModels. Each wizard needs access for at minimum:
- `group_ops_accountant` (read, write, create, unlink)
- `group_ops_finance_manager` (read, write, create, unlink)
- `group_ops_cfo` (read, write, create, unlink)
- `group_ops_executive` (read only: 1,0,0,0)
- `group_ops_compliance_officer` (read only: 1,0,0,0)

Pattern:
```csv
access_ops_gl_wizard_accountant,ops.gl.report.wizard accountant,model_ops_gl_report_wizard,ops_matrix_core.group_ops_accountant,1,1,1,1
access_ops_gl_wizard_finance,ops.gl.report.wizard finance,model_ops_gl_report_wizard,ops_matrix_core.group_ops_finance_manager,1,1,1,1
access_ops_gl_wizard_cfo,ops.gl.report.wizard cfo,model_ops_gl_report_wizard,ops_matrix_core.group_ops_cfo,1,1,1,1
access_ops_gl_wizard_executive,ops.gl.report.wizard executive,model_ops_gl_report_wizard,ops_matrix_core.group_ops_executive,1,0,0,0
```

## IMPLEMENTATION NOTES

### Odoo 19 Account Types
Check actual account types in the DB before hardcoding:
```bash
docker exec gemini_odoo19 bash -c "PGPASSWORD=odoo psql -U odoo -d mz-db -h gemini_odoo19_db -c \"SELECT DISTINCT account_type FROM account_account ORDER BY account_type;\""
```

### P&L Account Type Mapping (typical Odoo 19):
- `income` → Revenue
- `income_other` → Other Income
- `expense` → Operating Expenses
- `expense_depreciation` → Depreciation
- `expense_direct_cost` → Cost of Revenue/COGS

### BS Account Type Mapping:
- `asset_receivable`, `asset_cash`, `asset_current`, `asset_non_current`, `asset_prepayments`, `asset_fixed` → Assets
- `liability_payable`, `liability_current`, `liability_non_current`, `liability_credit_card` → Liabilities
- `equity`, `equity_unaffected` → Equity

### Query Pattern for _read_group (Odoo 19 syntax):
```python
# Odoo 19 _read_group returns tuples: (groupby_record, agg1, agg2, ...)
data = MoveLine._read_group(
    domain=domain,
    groupby=['account_id'],
    aggregates=['debit:sum', 'credit:sum', 'balance:sum']
)
# data = [(account_record, total_debit, total_credit, total_balance), ...]
```

## VERIFICATION

After creating all files:
```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
echo "=== New wizard files ===" && ls -la wizard/ops_*_wizard.py wizard/ops_financial_wizard_views.xml
echo "=== Python syntax check ===" && python3 -m py_compile wizard/ops_gl_wizard.py && echo "GL OK"
python3 -m py_compile wizard/ops_tb_wizard.py && echo "TB OK"
python3 -m py_compile wizard/ops_pnl_wizard.py && echo "PNL OK"
python3 -m py_compile wizard/ops_bs_wizard.py && echo "BS OK"
python3 -m py_compile wizard/ops_cf_wizard.py && echo "CF OK"
python3 -m py_compile wizard/ops_aged_wizard.py && echo "Aged OK"
python3 -m py_compile wizard/ops_partner_ledger_wizard.py && echo "Partner OK"
echo "=== ACL entries ===" && grep "gl_wizard\|tb_wizard\|pnl_wizard\|bs_wizard\|cf_wizard\|aged_wizard\|partner_ledger_wizard" security/ir.model.access.csv | wc -l
```

## RULES
- Each wizard file must be SELF-CONTAINED — no importing from other wizard files
- Every wizard MUST call `self._check_intelligence_access()` as first line of `_get_report_data()`
- Every domain MUST include branch isolation via `self._get_branch_filter_domain()`
- Running balance MUST be per-group, NEVER global
- Initial/opening balance queries MUST filter `move_id.state = posted` (always, regardless of target_move setting)
- All field strings must be translatable: `string=_('text')` or just `string='text'` (Odoo handles translation)
- Import from contracts: `from ..report.ops_report_contracts import build_report_meta, build_report_colors, to_dict, ShapeAReport, LineGroup, LineEntry` etc.
- Do NOT add sudo() anywhere
- Do NOT run odoo update yet
