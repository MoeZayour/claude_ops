import sys

def log(msg):
    sys.stderr.write(f"{msg}\n")

log("=" * 50)
log("SEED 01: Company Structure")
log("=" * 50)

try:
    company = env['res.company'].browse(1)

    # 1. Rename company
    if company.name != 'MZ International Trading LLC':
        company.write({'name': 'MZ International Trading LLC'})
        log("+ Renamed company to MZ International Trading LLC")
    else:
        log("= Company already named correctly")

    # 2. Create or find Dubai HQ branch
    Branch = env['ops.branch']
    main_branch = Branch.search([('name', '=', 'Dubai HQ')], limit=1)
    if not main_branch:
        # Try to find any existing branch to rename
        main_branch = Branch.search([], limit=1, order='id asc')
        if main_branch and main_branch.name != 'Dubai HQ':
            main_branch.write({
                'name': 'Dubai HQ',
                'is_headquarters': True,
                'address': 'Business Bay, Tower 1, Floor 20\nDubai, UAE',
                'phone': '+971-4-555-0100',
                'email': 'hq@mztrading.com',
            })
            log("+ Renamed existing branch to Dubai HQ")
        elif not main_branch:
            # No branches at all — create Dubai HQ
            main_branch = Branch.create({
                'name': 'Dubai HQ',
                'company_id': 1,
                'is_headquarters': True,
                'address': 'Business Bay, Tower 1, Floor 20\nDubai, UAE',
                'phone': '+971-4-555-0100',
                'email': 'hq@mztrading.com',
            })
            log("+ Created Dubai HQ branch")
    else:
        log("= Dubai HQ already exists")

    dubai_branch = main_branch  # Keep reference

    # 3. Create additional branches
    branch_data = [
        {
            'name': 'Abu Dhabi Branch',
            'company_id': 1,
            'parent_id': dubai_branch.id if dubai_branch else False,
            'is_headquarters': False,
            'address': 'Al Maryah Island, ADGM Tower\nAbu Dhabi, UAE',
            'phone': '+971-2-555-0200',
            'email': 'abudhabi@mztrading.com',
        },
        {
            'name': 'Sharjah Branch',
            'company_id': 1,
            'parent_id': dubai_branch.id if dubai_branch else False,
            'is_headquarters': False,
            'address': 'Sharjah Industrial Area 18\nSharjah, UAE',
            'phone': '+971-6-555-0300',
            'email': 'sharjah@mztrading.com',
        },
        {
            'name': 'Riyadh Branch',
            'company_id': 1,
            'parent_id': dubai_branch.id if dubai_branch else False,
            'is_headquarters': False,
            'address': 'King Fahd Road, Olaya District\nRiyadh, Saudi Arabia',
            'phone': '+966-11-555-0400',
            'email': 'riyadh@mztrading.com',
        },
        {
            'name': 'Doha Branch',
            'company_id': 1,
            'parent_id': dubai_branch.id if dubai_branch else False,
            'is_headquarters': False,
            'address': 'West Bay, Al Dafna Tower\nDoha, Qatar',
            'phone': '+974-4-555-0500',
            'email': 'doha@mztrading.com',
        },
    ]

    branches = {'Dubai HQ': dubai_branch}
    for data in branch_data:
        existing = Branch.search([('name', '=', data['name'])], limit=1)
        if existing:
            branches[data['name']] = existing
            log(f"= Exists: {data['name']}")
        else:
            branch = Branch.create(data)
            branches[data['name']] = branch
            log(f"+ Created: {data['name']} ({branch.code})")

    # 4. Create Business Units
    BU = env['ops.business.unit']

    bu_data = [
        {
            'name': 'Electronics & Technology',
            'description': 'Consumer electronics, IT hardware, and technology products',
            'target_margin_percent': 25.0,
            'branch_names': ['Dubai HQ', 'Abu Dhabi Branch', 'Riyadh Branch', 'Doha Branch'],
            'primary': 'Dubai HQ',
        },
        {
            'name': 'Food & Beverage',
            'description': 'Premium coffee, food products, and commercial kitchen equipment',
            'target_margin_percent': 35.0,
            'branch_names': ['Dubai HQ', 'Sharjah Branch', 'Riyadh Branch'],
            'primary': 'Dubai HQ',
        },
        {
            'name': 'Luxury & Lifestyle',
            'description': 'Luxury watches, designer goods, and premium lifestyle products',
            'target_margin_percent': 40.0,
            'branch_names': ['Dubai HQ', 'Abu Dhabi Branch', 'Doha Branch'],
            'primary': 'Dubai HQ',
        },
        {
            'name': 'IT Solutions & Consulting',
            'description': 'Software licensing, cloud services, and IT consulting',
            'target_margin_percent': 50.0,
            'branch_names': ['Dubai HQ', 'Abu Dhabi Branch', 'Riyadh Branch'],
            'primary': 'Dubai HQ',
        },
    ]

    for data in bu_data:
        existing = BU.search([('name', '=', data['name'])], limit=1)
        if existing:
            log(f"= Exists: BU {data['name']}")
        else:
            branch_ids = [branches[bn].id for bn in data['branch_names'] if bn in branches and branches[bn]]
            primary_id = branches.get(data['primary'])
            bu_vals = {
                'name': data['name'],
                'description': data['description'],
                'target_margin_percent': data['target_margin_percent'],
                'branch_ids': [(6, 0, branch_ids)],
            }
            if primary_id and primary_id.id:
                bu_vals['primary_branch_id'] = primary_id.id
            bu = BU.create(bu_vals)
            log(f"+ Created: BU {data['name']} ({bu.code})")

    # 5. Rename default warehouse and create new ones
    WH = env['stock.warehouse']
    default_wh = WH.browse(1)
    if default_wh.exists() and default_wh.name != 'Dubai Main Warehouse':
        default_wh.write({'name': 'Dubai Main Warehouse'})
        log("+ Renamed default warehouse to Dubai Main Warehouse")

    # Link Dubai HQ to default warehouse
    if dubai_branch and not dubai_branch.warehouse_id:
        dubai_branch.write({'warehouse_id': default_wh.id})
        log("+ Linked Dubai HQ to Dubai Main Warehouse")

    wh_data = [
        {'name': 'Abu Dhabi Warehouse', 'code': 'ADWH', 'branch_name': 'Abu Dhabi Branch'},
        {'name': 'Sharjah Distribution Center', 'code': 'SHWH', 'branch_name': 'Sharjah Branch'},
        {'name': 'Riyadh Warehouse', 'code': 'RYWH', 'branch_name': 'Riyadh Branch'},
        {'name': 'Doha Warehouse', 'code': 'DHWH', 'branch_name': 'Doha Branch'},
    ]

    for data in wh_data:
        existing = WH.search([('code', '=', data['code'])], limit=1)
        if existing:
            log(f"= Exists: Warehouse {data['name']}")
            # Link to branch if not linked
            branch = branches.get(data['branch_name'])
            if branch and not branch.warehouse_id:
                branch.write({'warehouse_id': existing.id})
        else:
            wh = WH.create({
                'name': data['name'],
                'code': data['code'],
                'company_id': 1,
            })
            log(f"+ Created: Warehouse {data['name']} ({data['code']})")
            # Link to branch
            branch = branches.get(data['branch_name'])
            if branch:
                branch.write({'warehouse_id': wh.id})
                log(f"  Linked to {data['branch_name']}")

    # 6. Create PDC journal and accounts
    Journal = env['account.journal']
    pdc_journal = Journal.search([('code', '=', 'PDC')], limit=1)
    if not pdc_journal:
        pdc_journal = Journal.create({
            'name': 'Post-Dated Checks',
            'code': 'PDC',
            'type': 'general',
            'company_id': 1,
        })
        log("+ Created PDC journal")
    else:
        log("= PDC journal exists")

    # Cash journal
    cash_journal = Journal.search([('type', '=', 'cash')], limit=1)
    if not cash_journal:
        cash_journal = Journal.create({
            'name': 'Cash',
            'code': 'CSH1',
            'type': 'cash',
            'company_id': 1,
        })
        log("+ Created Cash journal")
    else:
        log(f"= Cash journal exists ({cash_journal.code})")

    # PDC clearing accounts
    Account = env['account.account']
    pdc_recv = Account.search([('code', '=', '1200')], limit=1)
    if not pdc_recv:
        pdc_recv = Account.create({
            'code': '1200',
            'name': 'PDC Receivable Clearing',
            'account_type': 'asset_current',
        })
        log("+ Created account 1200 PDC Receivable Clearing")
    else:
        log("= Account 1200 exists")

    pdc_pay = Account.search([('code', '=', '3200')], limit=1)
    if not pdc_pay:
        pdc_pay = Account.create({
            'code': '3200',
            'name': 'PDC Payable Clearing',
            'account_type': 'liability_current',
        })
        log("+ Created account 3200 PDC Payable Clearing")
    else:
        log("= Account 3200 exists")

    # Configure PDC on company if fields exist
    pdc_fields = {}
    if hasattr(company, 'pdc_receivable_account_id'):
        pdc_fields['pdc_receivable_account_id'] = pdc_recv.id
    if hasattr(company, 'pdc_payable_account_id'):
        pdc_fields['pdc_payable_account_id'] = pdc_pay.id
    if hasattr(company, 'pdc_journal_id'):
        pdc_fields['pdc_journal_id'] = pdc_journal.id
    if pdc_fields:
        company.write(pdc_fields)
        log("+ Configured PDC settings on company")

    env.cr.commit()
    log("")
    log("SEED 01 COMPLETE - Company structure seeded successfully")

except Exception as e:
    env.cr.rollback()
    log(f"ERROR: {e}")
    import traceback
    sys.stderr.write(traceback.format_exc())
