# -*- coding: utf-8 -*-
"""
Seed Script 07: Post-Dated Checks (PDC) and Budgets
====================================================
Usage:
    cat seed/07_pdc_budgets.py | docker exec -i gemini_odoo19 \
        odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http

Idempotent: checks for existing records before creating.
"""
import sys

def log(msg):
    sys.stderr.write(f"[07_pdc_budgets] {msg}\n")

log("Starting PDC & budgets seed...")

# ============================================================================
# HELPERS
# ============================================================================

def get_branch(name):
    """Find branch by name (partial match)."""
    branch = env['ops.branch'].search([('name', 'ilike', name)], limit=1)
    if not branch:
        log(f"  WARNING: Branch '{name}' not found, using first available")
        branch = env['ops.branch'].search([], limit=1)
    return branch

def get_bu(name):
    """Find business unit by name (partial match)."""
    bu = env['ops.business.unit'].search([('name', 'ilike', name)], limit=1)
    if not bu:
        log(f"  WARNING: Business Unit '{name}' not found, using first available")
        bu = env['ops.business.unit'].search([], limit=1)
    return bu

def get_partner(name, is_customer=True):
    """Find or create partner."""
    partner = env['res.partner'].search([('name', '=', name)], limit=1)
    if not partner:
        partner = env['res.partner'].create({
            'name': name,
            'is_company': True,
            'customer_rank': 1 if is_customer else 0,
            'supplier_rank': 0 if is_customer else 1,
        })
        log(f"  Created partner: {name}")
    return partner

def get_account(code_prefix, account_type=None):
    """Find account by code prefix or type."""
    if code_prefix:
        account = env['account.account'].search([
            ('code', '=like', code_prefix + '%')
        ], limit=1)
        if account:
            return account
    if account_type:
        account = env['account.account'].search([
            ('account_type', '=', account_type)
        ], limit=1)
        if account:
            return account
    return env['account.account']

# ============================================================================
# LOOKUP BRANCHES AND BUSINESS UNITS
# ============================================================================
log("Looking up branches and business units...")

branch_dubai = get_branch('Dubai')
branch_riyadh = get_branch('Riyadh')
branch_sharjah = get_branch('Sharjah')
branch_abudhabi = get_branch('Abu Dhabi')
branch_doha = get_branch('Doha')

bu_electronics = get_bu('Electronics')
bu_fb = get_bu('F&B')
bu_luxury = get_bu('Luxury')
bu_it = get_bu('IT Solutions')

# ============================================================================
# PDC RECEIVABLE (5)
# ============================================================================
log("Creating PDC Receivables...")

# Look up partners (should exist from seed 06)
cust_al_futtaim = get_partner('Al Futtaim', is_customer=True)
cust_al_jazeera = get_partner('Al Jazeera Hospitality', is_customer=True)
cust_qatar_digital = get_partner('Qatar Digital', is_customer=True)
cust_prestige_watch = get_partner('Prestige Watch', is_customer=True)
cust_saudi_gourmet = get_partner('Saudi Gourmet', is_customer=True)

pdc_recv_data = [
    {
        'check_number': 'CHK-RCV-001',
        'partner': cust_al_futtaim,
        'amount': 195000,
        'maturity_date': '2026-03-15',
        'check_date': '2026-01-25',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'notes': 'Post-dated check from Al Futtaim for remaining balance on bulk electronics order',
        'deposit': True,
    },
    {
        'check_number': 'CHK-RCV-002',
        'partner': cust_al_jazeera,
        'amount': 13350,
        'maturity_date': '2026-02-28',
        'check_date': '2026-01-08',
        'branch': branch_dubai,
        'bu': bu_fb,
        'notes': 'Post-dated check from Al Jazeera Hospitality for remaining invoice balance',
        'deposit': True,
    },
    {
        'check_number': 'CHK-RCV-003',
        'partner': cust_qatar_digital,
        'amount': 59000,
        'maturity_date': '2026-03-01',
        'check_date': '2026-01-05',
        'branch': branch_doha,
        'bu': bu_electronics,
        'notes': 'Post-dated check from Qatar Digital for full invoice amount',
        'deposit': False,
    },
    {
        'check_number': 'CHK-RCV-004',
        'partner': cust_prestige_watch,
        'amount': 175000,
        'maturity_date': '2026-04-15',
        'check_date': '2026-01-18',
        'branch': branch_abudhabi,
        'bu': bu_luxury,
        'notes': 'Post-dated check from Prestige Watch for Rolex order',
        'deposit': False,
    },
    {
        'check_number': 'CHK-RCV-005',
        'partner': cust_saudi_gourmet,
        'amount': 6200,
        'maturity_date': '2026-02-20',
        'check_date': '2026-01-15',
        'branch': branch_riyadh,
        'bu': bu_fb,
        'notes': 'Post-dated check from Saudi Gourmet for coffee order',
        'deposit': False,
    },
]

pdc_recv_created = 0
pdc_recv_skipped = 0

for pdc_data in pdc_recv_data:
    # Check idempotency by check_number
    existing = env['ops.pdc.receivable'].search([
        ('check_number', '=', pdc_data['check_number'])
    ], limit=1)
    if existing:
        log(f"  SKIP: PDC Receivable {pdc_data['check_number']} already exists ({existing.name})")
        pdc_recv_skipped += 1
        continue

    vals = {
        'check_number': pdc_data['check_number'],
        'partner_id': pdc_data['partner'].id,
        'amount': pdc_data['amount'],
        'maturity_date': pdc_data['maturity_date'],
        'check_date': pdc_data['check_date'],
        'ops_branch_id': pdc_data['branch'].id if pdc_data['branch'] else False,
        'ops_business_unit_id': pdc_data['bu'].id if pdc_data['bu'] else False,
        'notes': pdc_data['notes'],
    }

    try:
        pdc = env['ops.pdc.receivable'].create(vals)
        log(f"  CREATED: PDC Receivable {pdc.name} - {pdc_data['check_number']} - {pdc_data['partner'].name} = {pdc_data['amount']}")

        # Try to deposit if configured (PDC 1 and 2)
        if pdc_data.get('deposit'):
            try:
                pdc.action_deposit()
                log(f"    -> Deposited: {pdc.name}")
            except Exception as dep_err:
                log(f"    -> Could not deposit (config may be missing): {dep_err}")

        pdc_recv_created += 1
    except Exception as e:
        log(f"  ERROR creating PDC Receivable {pdc_data['check_number']}: {e}")

log(f"PDC Receivable: {pdc_recv_created} created, {pdc_recv_skipped} skipped")

# ============================================================================
# PDC PAYABLE (3)
# ============================================================================
log("Creating PDC Payables...")

vend_al_mokha = get_partner('Al Mokha', is_customer=False)
vend_microsoft = get_partner('Microsoft Gulf', is_customer=False)
vend_herman_miller = get_partner('Herman Miller', is_customer=False)

pdc_pay_data = [
    {
        'check_number': 'CHK-PAY-001',
        'partner': vend_al_mokha,
        'amount': 27000,
        'maturity_date': '2026-03-10',
        'check_date': '2026-01-20',
        'branch': branch_sharjah,
        'bu': bu_fb,
        'notes': 'Post-dated check to Al Mokha for coffee beans purchase',
    },
    {
        'check_number': 'CHK-PAY-002',
        'partner': vend_microsoft,
        'amount': 75000,
        'maturity_date': '2026-04-01',
        'check_date': '2026-01-25',
        'branch': branch_dubai,
        'bu': bu_it,
        'notes': 'Post-dated check to Microsoft Gulf for enterprise licenses',
    },
    {
        'check_number': 'CHK-PAY-003',
        'partner': vend_herman_miller,
        'amount': 85500,
        'maturity_date': '2026-03-20',
        'check_date': '2026-01-28',
        'branch': branch_abudhabi,
        'bu': bu_electronics,
        'notes': 'Post-dated check to Herman Miller for office furniture',
    },
]

pdc_pay_created = 0
pdc_pay_skipped = 0

for pdc_data in pdc_pay_data:
    existing = env['ops.pdc.payable'].search([
        ('check_number', '=', pdc_data['check_number'])
    ], limit=1)
    if existing:
        log(f"  SKIP: PDC Payable {pdc_data['check_number']} already exists ({existing.name})")
        pdc_pay_skipped += 1
        continue

    vals = {
        'check_number': pdc_data['check_number'],
        'partner_id': pdc_data['partner'].id,
        'amount': pdc_data['amount'],
        'maturity_date': pdc_data['maturity_date'],
        'check_date': pdc_data['check_date'],
        'ops_branch_id': pdc_data['branch'].id if pdc_data['branch'] else False,
        'ops_business_unit_id': pdc_data['bu'].id if pdc_data['bu'] else False,
        'notes': pdc_data['notes'],
    }

    try:
        pdc = env['ops.pdc.payable'].create(vals)
        log(f"  CREATED: PDC Payable {pdc.name} - {pdc_data['check_number']} - {pdc_data['partner'].name} = {pdc_data['amount']}")
        pdc_pay_created += 1
    except Exception as e:
        log(f"  ERROR creating PDC Payable {pdc_data['check_number']}: {e}")

log(f"PDC Payable: {pdc_pay_created} created, {pdc_pay_skipped} skipped")

# ============================================================================
# BUDGETS (4)
# ============================================================================
log("Creating budgets...")

# Find accounts for budget lines
# Revenue accounts typically start with 4xxxxx, COGS with 5xxxxx, Expenses with 6xxxxx
revenue_account = get_account('4', 'income')
cogs_account = get_account('5', 'expense_direct_cost')
expense_account = get_account('6', 'expense')

if not revenue_account:
    log("  WARNING: No revenue account (4xxxxx) found, searching by type...")
    revenue_account = env['account.account'].search([
        ('account_type', 'in', ['income', 'income_other'])
    ], limit=1)

if not cogs_account:
    log("  WARNING: No COGS account (5xxxxx) found, searching by type...")
    cogs_account = env['account.account'].search([
        ('account_type', '=', 'expense_direct_cost')
    ], limit=1)
    if not cogs_account:
        cogs_account = env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)

if not expense_account:
    log("  WARNING: No expense account (6xxxxx) found, searching by type...")
    expense_account = env['account.account'].search([
        ('account_type', '=', 'expense')
    ], limit=1)

# If COGS and expense are the same, try to find a different one for expense
if cogs_account and expense_account and cogs_account.id == expense_account.id:
    alt_expense = env['account.account'].search([
        ('account_type', '=', 'expense'),
        ('id', '!=', cogs_account.id),
    ], limit=1)
    if alt_expense:
        expense_account = alt_expense

log(f"  Budget accounts: Revenue={revenue_account.code if revenue_account else 'N/A'}, "
    f"COGS={cogs_account.code if cogs_account else 'N/A'}, "
    f"Expense={expense_account.code if expense_account else 'N/A'}")

budget_data = [
    {
        'name': 'Electronics BU Budget Q1 2026',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date_from': '2026-01-01',
        'date_to': '2026-03-31',
        'confirm': True,
        'lines': [
            {'account': revenue_account, 'planned': 500000},
            {'account': cogs_account, 'planned': 300000},
            {'account': expense_account, 'planned': 50000},
        ],
    },
    {
        'name': 'F&B BU Budget Q1 2026',
        'branch': branch_dubai,
        'bu': bu_fb,
        'date_from': '2026-01-01',
        'date_to': '2026-03-31',
        'confirm': True,
        'lines': [
            {'account': revenue_account, 'planned': 100000},
            {'account': cogs_account, 'planned': 60000},
            {'account': expense_account, 'planned': 20000},
        ],
    },
    {
        'name': 'Luxury BU Budget Q1 2026',
        'branch': branch_dubai,
        'bu': bu_luxury,
        'date_from': '2026-01-01',
        'date_to': '2026-03-31',
        'confirm': True,
        'lines': [
            {'account': revenue_account, 'planned': 800000},
            {'account': cogs_account, 'planned': 500000},
            {'account': expense_account, 'planned': 30000},
        ],
    },
    {
        'name': 'IT Solutions BU Budget Q1 2026',
        'branch': branch_dubai,
        'bu': bu_it,
        'date_from': '2026-01-01',
        'date_to': '2026-03-31',
        'confirm': False,  # Leave as draft
        'lines': [
            {'account': revenue_account, 'planned': 200000},
            {'account': cogs_account, 'planned': 100000},
            {'account': expense_account, 'planned': 40000},
        ],
    },
]

budgets_created = 0
budgets_skipped = 0

for bud_data in budget_data:
    # Check idempotency by name + branch + BU + dates
    existing = env['ops.budget'].search([
        ('name', '=', bud_data['name']),
        ('ops_branch_id', '=', bud_data['branch'].id if bud_data['branch'] else False),
        ('ops_business_unit_id', '=', bud_data['bu'].id if bud_data['bu'] else False),
    ], limit=1)

    if existing:
        log(f"  SKIP: Budget '{bud_data['name']}' already exists (id={existing.id})")
        budgets_skipped += 1
        continue

    # Build budget line values - only include lines with valid accounts
    line_vals = []
    seen_accounts = set()
    for line in bud_data['lines']:
        acct = line['account']
        if acct and acct.id not in seen_accounts:
            line_vals.append((0, 0, {
                'general_account_id': acct.id,
                'planned_amount': line['planned'],
            }))
            seen_accounts.add(acct.id)
        elif not acct:
            log(f"    WARNING: Skipping budget line - no account found")

    vals = {
        'name': bud_data['name'],
        'ops_branch_id': bud_data['branch'].id if bud_data['branch'] else False,
        'ops_business_unit_id': bud_data['bu'].id if bud_data['bu'] else False,
        'date_from': bud_data['date_from'],
        'date_to': bud_data['date_to'],
        'line_ids': line_vals,
    }

    try:
        budget = env['ops.budget'].create(vals)

        if bud_data['confirm']:
            try:
                budget.action_confirm()
                log(f"  CREATED & CONFIRMED: {budget.name} (id={budget.id})")
            except Exception as conf_err:
                log(f"  CREATED (confirm failed): {budget.name} - {conf_err}")
        else:
            log(f"  CREATED (DRAFT): {budget.name} (id={budget.id})")

        budgets_created += 1
    except Exception as e:
        log(f"  ERROR creating budget '{bud_data['name']}': {e}")

log(f"Budgets: {budgets_created} created, {budgets_skipped} skipped")

# ============================================================================
# COMMIT
# ============================================================================
env.cr.commit()
log("=" * 60)
log("SEED 07 COMPLETE")
log(f"  PDC Receivable: {pdc_recv_created} created, {pdc_recv_skipped} skipped")
log(f"  PDC Payable:    {pdc_pay_created} created, {pdc_pay_skipped} skipped")
log(f"  Budgets:        {budgets_created} created, {budgets_skipped} skipped")
log("=" * 60)
