# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - General Ledger Demo Data Loader
Generates sample journal entries for testing the GL report.
"""

from datetime import date, timedelta
from random import choice, randint, uniform

def load_demo_data(env):
    """Load comprehensive demo data for General Ledger testing."""

    print("\n" + "="*60)
    print("OPS MATRIX - GENERAL LEDGER DEMO DATA LOADER")
    print("="*60 + "\n")

    company = env.company
    print(f"Company: {company.name}")

    # Get or create accounts
    accounts = _ensure_accounts(env, company)
    if not accounts:
        print("ERROR: Could not create/find accounts. Aborting.")
        return False

    # Get or create journal
    journal = _ensure_journal(env, company)
    if not journal:
        print("ERROR: Could not create/find journal. Aborting.")
        return False

    # Get or create branches and business units
    branches, bus = _ensure_matrix_dimensions(env, company)

    # Generate journal entries
    _create_journal_entries(env, company, accounts, journal, branches, bus)

    print("\n" + "="*60)
    print("DEMO DATA LOADING COMPLETE")
    print("="*60)
    print("\nYou can now access the General Ledger report at:")
    print("  Accounting > Reports > Matrix Financial Reports > General Ledger")
    print("\nOr use the Enhanced Report Wizard:")
    print("  Accounting > Reports > Matrix Financial Intelligence")

    return True


def _ensure_accounts(env, company):
    """Ensure sample accounts exist for demo transactions."""

    print("Checking/Creating chart of accounts...")

    Account = env['account.account']
    accounts = {}

    # Account definitions with Odoo 19 account_type values
    account_defs = [
        # Assets
        ('100000', 'Cash', 'asset_cash'),
        ('110000', 'Bank Account', 'asset_cash'),
        ('120000', 'Accounts Receivable', 'asset_receivable'),
        ('130000', 'Inventory', 'asset_current'),
        ('150000', 'Fixed Assets', 'asset_fixed'),
        ('159000', 'Accumulated Depreciation', 'asset_fixed'),
        # Liabilities
        ('200000', 'Accounts Payable', 'liability_payable'),
        ('210000', 'Accrued Expenses', 'liability_current'),
        ('250000', 'Long-term Debt', 'liability_non_current'),
        # Equity
        ('300000', 'Share Capital', 'equity'),
        ('310000', 'Retained Earnings', 'equity_unaffected'),
        # Revenue
        ('400000', 'Sales Revenue', 'income'),
        ('410000', 'Service Revenue', 'income'),
        ('420000', 'Other Income', 'income_other'),
        # Expenses
        ('500000', 'Cost of Goods Sold', 'expense'),
        ('600000', 'Salaries & Wages', 'expense'),
        ('610000', 'Rent Expense', 'expense'),
        ('620000', 'Utilities Expense', 'expense'),
        ('630000', 'Marketing Expense', 'expense'),
        ('640000', 'Office Supplies', 'expense'),
        ('680000', 'Depreciation Expense', 'expense_depreciation'),
        ('690000', 'Interest Expense', 'expense'),
    ]

    for code, name, acc_type in account_defs:
        # Check if exists
        account = Account.search([
            ('code', '=', code),
            ('company_id', '=', company.id)
        ], limit=1)

        if not account:
            try:
                account = Account.create({
                    'code': code,
                    'name': name,
                    'account_type': acc_type,
                    'company_id': company.id,
                    'reconcile': acc_type in ('asset_receivable', 'liability_payable'),
                })
                print(f"  Created: {code} - {name}")
            except Exception as e:
                print(f"  Warning: Could not create {code}: {e}")
                continue
        else:
            print(f"  Exists: {code} - {name}")

        accounts[code] = account

    return accounts


def _ensure_journal(env, company):
    """Ensure a general journal exists."""

    print("\nChecking/Creating journal...")

    Journal = env['account.journal']

    # Look for existing general journal
    journal = Journal.search([
        ('type', '=', 'general'),
        ('company_id', '=', company.id)
    ], limit=1)

    if not journal:
        journal = Journal.create({
            'name': 'General Journal',
            'code': 'GEN',
            'type': 'general',
            'company_id': company.id,
        })
        print(f"  Created: {journal.name} ({journal.code})")
    else:
        print(f"  Exists: {journal.name} ({journal.code})")

    return journal


def _ensure_matrix_dimensions(env, company):
    """Create sample branches and business units for matrix filtering."""

    print("\nChecking/Creating matrix dimensions...")

    branches = []
    bus = []

    # Check if ops.branch model exists
    if 'ops.branch' in env:
        Branch = env['ops.branch']
        branch_names = ['HQ Dubai', 'Abu Dhabi Office', 'Sharjah Branch']

        for name in branch_names:
            branch = Branch.search([('name', '=', name)], limit=1)
            if not branch:
                try:
                    branch = Branch.create({
                        'name': name,
                        'code': name[:3].upper(),
                        'company_id': company.id,
                    })
                    print(f"  Created Branch: {name}")
                except Exception as e:
                    print(f"  Warning: Could not create branch {name}: {e}")
                    continue
            else:
                print(f"  Branch Exists: {name}")
            branches.append(branch)
    else:
        print("  ops.branch model not found, skipping branch creation")

    # Check if ops.business.unit model exists
    if 'ops.business.unit' in env:
        BU = env['ops.business.unit']
        bu_names = ['Retail Division', 'Wholesale Division', 'Online Sales']

        for name in bu_names:
            bu = BU.search([('name', '=', name)], limit=1)
            if not bu:
                try:
                    bu = BU.create({
                        'name': name,
                        'code': name[:3].upper(),
                        'company_id': company.id,
                    })
                    print(f"  Created BU: {name}")
                except Exception as e:
                    print(f"  Warning: Could not create BU {name}: {e}")
                    continue
            else:
                print(f"  BU Exists: {name}")
            bus.append(bu)
    else:
        print("  ops.business.unit model not found, skipping BU creation")

    return branches, bus


def _create_journal_entries(env, company, accounts, journal, branches, bus):
    """Create sample journal entries for the past 3 months."""

    print("\nCreating sample journal entries...")

    Move = env['account.move']

    today = date.today()
    start_date = today - timedelta(days=90)

    # Transaction templates
    transactions = [
        # Sales transactions
        {
            'name': 'Customer Invoice Payment',
            'debit_acc': '100000',  # Cash
            'credit_acc': '400000',  # Sales Revenue
            'amount_range': (1000, 25000),
        },
        {
            'name': 'Service Revenue',
            'debit_acc': '110000',  # Bank
            'credit_acc': '410000',  # Service Revenue
            'amount_range': (500, 15000),
        },
        # Expense transactions
        {
            'name': 'Salary Payment',
            'debit_acc': '600000',  # Salaries
            'credit_acc': '110000',  # Bank
            'amount_range': (5000, 35000),
        },
        {
            'name': 'Rent Payment',
            'debit_acc': '610000',  # Rent
            'credit_acc': '110000',  # Bank
            'amount_range': (3000, 12000),
        },
        {
            'name': 'Utility Bill',
            'debit_acc': '620000',  # Utilities
            'credit_acc': '110000',  # Bank
            'amount_range': (200, 2000),
        },
        {
            'name': 'Marketing Campaign',
            'debit_acc': '630000',  # Marketing
            'credit_acc': '110000',  # Bank
            'amount_range': (1000, 8000),
        },
        {
            'name': 'Office Supplies Purchase',
            'debit_acc': '640000',  # Supplies
            'credit_acc': '100000',  # Cash
            'amount_range': (100, 1500),
        },
        # AP/AR transactions
        {
            'name': 'Vendor Payment',
            'debit_acc': '200000',  # AP
            'credit_acc': '110000',  # Bank
            'amount_range': (2000, 20000),
        },
        {
            'name': 'Customer Collection',
            'debit_acc': '110000',  # Bank
            'credit_acc': '120000',  # AR
            'amount_range': (1500, 18000),
        },
        # Inventory
        {
            'name': 'Inventory Purchase',
            'debit_acc': '130000',  # Inventory
            'credit_acc': '200000',  # AP
            'amount_range': (5000, 50000),
        },
        {
            'name': 'Cost of Goods Sold',
            'debit_acc': '500000',  # COGS
            'credit_acc': '130000',  # Inventory
            'amount_range': (3000, 30000),
        },
        # Fixed assets
        {
            'name': 'Equipment Purchase',
            'debit_acc': '150000',  # Fixed Assets
            'credit_acc': '110000',  # Bank
            'amount_range': (10000, 100000),
        },
        {
            'name': 'Monthly Depreciation',
            'debit_acc': '680000',  # Depreciation Exp
            'credit_acc': '159000',  # Accum Depr
            'amount_range': (500, 5000),
        },
    ]

    entries_created = 0
    entries_by_month = {}

    # Generate entries for the past 90 days
    current_date = start_date
    while current_date <= today:
        # 2-5 transactions per day
        num_transactions = randint(2, 5)

        for _ in range(num_transactions):
            txn = choice(transactions)

            debit_acc = accounts.get(txn['debit_acc'])
            credit_acc = accounts.get(txn['credit_acc'])

            if not debit_acc or not credit_acc:
                continue

            amount = round(uniform(*txn['amount_range']), 2)

            # Prepare move values
            move_vals = {
                'journal_id': journal.id,
                'date': current_date,
                'ref': f"DEMO-{current_date.strftime('%Y%m%d')}-{entries_created+1:04d}",
                'move_type': 'entry',
                'line_ids': [
                    (0, 0, {
                        'account_id': debit_acc.id,
                        'name': txn['name'],
                        'debit': amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'account_id': credit_acc.id,
                        'name': txn['name'],
                        'debit': 0.0,
                        'credit': amount,
                    }),
                ],
            }

            # Add matrix dimensions if available
            if branches:
                branch = choice(branches)
                for line in move_vals['line_ids']:
                    if hasattr(env['account.move.line'], 'ops_branch_id'):
                        line[2]['ops_branch_id'] = branch.id

            if bus:
                bu = choice(bus)
                for line in move_vals['line_ids']:
                    if hasattr(env['account.move.line'], 'ops_business_unit_id'):
                        line[2]['ops_business_unit_id'] = bu.id

            try:
                move = Move.create(move_vals)
                move.action_post()  # Post the entry
                entries_created += 1

                # Track by month
                month_key = current_date.strftime('%Y-%m')
                entries_by_month[month_key] = entries_by_month.get(month_key, 0) + 1

            except Exception as e:
                print(f"  Warning: Failed to create entry: {e}")

        current_date += timedelta(days=1)

    # Commit the transaction
    env.cr.commit()

    print(f"\n  Total entries created: {entries_created}")
    print("  Entries by month:")
    for month, count in sorted(entries_by_month.items()):
        print(f"    {month}: {count} entries")

    # Summary of account balances
    print("\n  Account balance summary:")
    for code, account in sorted(accounts.items()):
        # Get balance
        balance = sum(env['account.move.line'].search([
            ('account_id', '=', account.id),
            ('parent_state', '=', 'posted')
        ]).mapped(lambda l: l.debit - l.credit))
        if abs(balance) > 0.01:
            print(f"    {code} {account.name}: {balance:,.2f}")


# Main execution
if __name__ == '__main__' or True:
    try:
        result = load_demo_data(self.env)
        if result:
            print("\nDemo data loaded successfully!")
        else:
            print("\nDemo data loading failed.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
