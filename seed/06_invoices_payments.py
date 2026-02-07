# -*- coding: utf-8 -*-
"""
Seed Script 06: Customer Invoices, Vendor Bills, and Payments
=============================================================
Usage:
    cat seed/06_invoices_payments.py | docker exec -i gemini_odoo19 \
        odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http

Idempotent: checks for existing records before creating.
"""
import sys

def log(msg):
    sys.stderr.write(f"[06_invoices_payments] {msg}\n")

log("Starting invoices & payments seed...")

# ============================================================================
# HELPER: Lookup branch/BU/partner/journal with error handling
# ============================================================================

def get_branch(name):
    """Find branch by name (partial match)."""
    branch = env['ops.branch'].search([('name', 'ilike', name)], limit=1)
    if not branch:
        log(f"  WARNING: Branch '{name}' not found, trying broader search...")
        branch = env['ops.branch'].search([], limit=1)
    return branch

def get_bu(name):
    """Find business unit by name (partial match)."""
    bu = env['ops.business.unit'].search([('name', 'ilike', name)], limit=1)
    if not bu:
        log(f"  WARNING: Business Unit '{name}' not found, trying broader search...")
        bu = env['ops.business.unit'].search([], limit=1)
    return bu

def get_partner(name, is_customer=True, is_company=True):
    """Find or create a partner by name."""
    partner = env['res.partner'].search([('name', '=', name)], limit=1)
    if not partner:
        vals = {
            'name': name,
            'is_company': is_company,
            'customer_rank': 1 if is_customer else 0,
            'supplier_rank': 0 if is_customer else 1,
        }
        partner = env['res.partner'].create(vals)
        log(f"  Created partner: {name}")
    else:
        # Ensure rank is set
        if is_customer and partner.customer_rank == 0:
            partner.customer_rank = 1
        if not is_customer and partner.supplier_rank == 0:
            partner.supplier_rank = 1
    return partner

def get_journal(code, journal_type=None):
    """Find journal by code."""
    domain = [('code', '=', code)]
    if journal_type:
        domain.append(('type', '=', journal_type))
    journal = env['account.journal'].search(domain, limit=1)
    if not journal:
        # Try by type
        if journal_type:
            journal = env['account.journal'].search([('type', '=', journal_type)], limit=1)
        if not journal:
            log(f"  WARNING: Journal code='{code}' not found!")
    return journal

def invoice_exists(partner_id, move_type, invoice_date, amount_hint):
    """Check if an invoice already exists (by partner + type + date)."""
    existing = env['account.move'].search([
        ('partner_id', '=', partner_id),
        ('move_type', '=', move_type),
        ('invoice_date', '=', invoice_date),
    ], limit=1)
    return existing

def payment_exists(partner_id, payment_type, amount, date):
    """Check if a payment already exists."""
    existing = env['account.payment'].search([
        ('partner_id', '=', partner_id),
        ('payment_type', '=', payment_type),
        ('amount', '=', amount),
        ('date', '=', date),
    ], limit=1)
    return existing

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

log(f"  Branches: Dubai={branch_dubai.id}, Riyadh={branch_riyadh.id}, "
    f"Sharjah={branch_sharjah.id}, AbuDhabi={branch_abudhabi.id}, Doha={branch_doha.id}")
log(f"  BUs: Electronics={bu_electronics.id}, F&B={bu_fb.id}, "
    f"Luxury={bu_luxury.id}, IT={bu_it.id}")

# ============================================================================
# LOOKUP JOURNALS
# ============================================================================
log("Looking up journals...")

sales_journal = get_journal('INV', 'sale')
if not sales_journal:
    sales_journal = env['account.journal'].search([('type', '=', 'sale')], limit=1)
    log(f"  Fallback sales journal: {sales_journal.name} (code={sales_journal.code})")
else:
    log(f"  Sales journal: {sales_journal.name} (code={sales_journal.code})")

purchase_journal = get_journal('BILL', 'purchase')
if not purchase_journal:
    purchase_journal = env['account.journal'].search([('type', '=', 'purchase')], limit=1)
    log(f"  Fallback purchase journal: {purchase_journal.name} (code={purchase_journal.code})")
else:
    log(f"  Purchase journal: {purchase_journal.name} (code={purchase_journal.code})")

bank_journal = env['account.journal'].search([('type', '=', 'bank')], limit=1)
if bank_journal:
    log(f"  Bank journal: {bank_journal.name} (code={bank_journal.code})")
else:
    log("  WARNING: No bank journal found!")

# ============================================================================
# CREATE/FIND PARTNERS
# ============================================================================
log("Setting up partners...")

# Customers
cust_gulf_electronics = get_partner('Gulf Electronics', is_customer=True)
cust_al_jazeera = get_partner('Al Jazeera Hospitality', is_customer=True)
cust_royal_luxury = get_partner('Royal Luxury', is_customer=True)
cust_techvision = get_partner('TechVision', is_customer=True)
cust_emirates_food = get_partner('Emirates Food', is_customer=True)
cust_qatar_digital = get_partner('Qatar Digital', is_customer=True)
cust_al_futtaim = get_partner('Al Futtaim', is_customer=True)
cust_saudi_gourmet = get_partner('Saudi Gourmet', is_customer=True)
cust_prestige_watch = get_partner('Prestige Watch', is_customer=True)
cust_smart_office = get_partner('Smart Office', is_customer=True)

# Vendors
vend_apple = get_partner('Apple Distribution', is_customer=False)
vend_nestle = get_partner('Nestl\u00e9', is_customer=False)
vend_rolex = get_partner('Rolex MENA', is_customer=False)
vend_samsung = get_partner('Samsung Gulf', is_customer=False)
vend_al_mokha = get_partner('Al Mokha', is_customer=False)
vend_microsoft = get_partner('Microsoft Gulf', is_customer=False)
vend_herman_miller = get_partner('Herman Miller', is_customer=False)

log("Partners ready.")

# ============================================================================
# CUSTOMER INVOICES (10)
# ============================================================================
log("Creating customer invoices...")

customer_invoices_data = [
    {
        'ref': 'INV/2025/001',
        'partner': cust_gulf_electronics,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2025-12-08',
        'lines': [
            {'name': 'iPhone 15 Pro', 'quantity': 5, 'price_unit': 4500},
            {'name': 'MacBook Pro 14"', 'quantity': 3, 'price_unit': 8500},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2025/002',
        'partner': cust_al_jazeera,
        'branch': branch_dubai,
        'bu': bu_fb,
        'date': '2025-12-12',
        'lines': [
            {'name': 'Arabic Coffee Blend (kg)', 'quantity': 10, 'price_unit': 85},
            {'name': 'Commercial Espresso Machine', 'quantity': 5, 'price_unit': 8500},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2025/003',
        'partner': cust_royal_luxury,
        'branch': branch_dubai,
        'bu': bu_luxury,
        'date': '2025-12-18',
        'lines': [
            {'name': 'Rolex Submariner', 'quantity': 2, 'price_unit': 35000},
            {'name': 'Designer Handbag', 'quantity': 3, 'price_unit': 5500},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2025/004',
        'partner': cust_techvision,
        'branch': branch_riyadh,
        'bu': bu_it,
        'date': '2025-12-22',
        'lines': [
            {'name': 'Enterprise Software License', 'quantity': 20, 'price_unit': 2500},
            {'name': 'Annual Maintenance Contract', 'quantity': 10, 'price_unit': 1500},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2025/005',
        'partner': cust_emirates_food,
        'branch': branch_sharjah,
        'bu': bu_fb,
        'date': '2025-12-28',
        'lines': [
            {'name': 'Premium Basmati Rice (bag)', 'quantity': 100, 'price_unit': 25},
            {'name': 'Refined Sugar (bag)', 'quantity': 200, 'price_unit': 8},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2026/001',
        'partner': cust_qatar_digital,
        'branch': branch_doha,
        'bu': bu_electronics,
        'date': '2026-01-05',
        'lines': [
            {'name': 'Samsung QLED TV 65"', 'quantity': 10, 'price_unit': 3500},
            {'name': 'AirPods Pro', 'quantity': 20, 'price_unit': 1200},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2026/002',
        'partner': cust_al_futtaim,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2026-01-10',
        'lines': [
            {'name': 'iPhone 15 Pro (Bulk)', 'quantity': 50, 'price_unit': 4500},
            {'name': 'MacBook Pro 14" (Bulk)', 'quantity': 20, 'price_unit': 8500},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2026/003',
        'partner': cust_saudi_gourmet,
        'branch': branch_riyadh,
        'bu': bu_fb,
        'date': '2026-01-15',
        'lines': [
            {'name': 'Arabic Coffee Blend (kg)', 'quantity': 50, 'price_unit': 85},
            {'name': 'Turkish Coffee Blend (kg)', 'quantity': 30, 'price_unit': 65.0 + 1.0/3},
        ],
        'post': True,
    },
    {
        'ref': 'INV/2026/004',
        'partner': cust_prestige_watch,
        'branch': branch_abudhabi,
        'bu': bu_luxury,
        'date': '2026-01-18',
        'lines': [
            {'name': 'Rolex Submariner', 'quantity': 5, 'price_unit': 35000},
        ],
        'post': False,  # Draft
    },
    {
        'ref': 'INV/2026/005',
        'partner': cust_smart_office,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2026-01-22',
        'lines': [
            {'name': 'Ergonomic Office Chair', 'quantity': 30, 'price_unit': 1200},
            {'name': 'Standing Desk', 'quantity': 15, 'price_unit': 2500},
        ],
        'post': False,  # Draft
    },
]

invoices_created = 0
invoices_skipped = 0

for inv_data in customer_invoices_data:
    partner = inv_data['partner']
    existing = invoice_exists(partner.id, 'out_invoice', inv_data['date'], 0)
    if existing:
        log(f"  SKIP: Invoice for {partner.name} on {inv_data['date']} already exists ({existing.name})")
        invoices_skipped += 1
        continue

    invoice_lines = []
    for line in inv_data['lines']:
        invoice_lines.append((0, 0, {
            'name': line['name'],
            'quantity': line['quantity'],
            'price_unit': line['price_unit'],
        }))

    vals = {
        'move_type': 'out_invoice',
        'partner_id': partner.id,
        'journal_id': sales_journal.id,
        'invoice_date': inv_data['date'],
        'date': inv_data['date'],
        'ref': inv_data['ref'],
        'ops_branch_id': inv_data['branch'].id if inv_data['branch'] else False,
        'ops_business_unit_id': inv_data['bu'].id if inv_data['bu'] else False,
        'invoice_line_ids': invoice_lines,
    }

    try:
        invoice = env['account.move'].create(vals)
        if inv_data['post']:
            invoice.action_post()
            log(f"  CREATED & POSTED: {invoice.name} - {partner.name} - {inv_data['ref']}")
        else:
            log(f"  CREATED (DRAFT): {invoice.name} - {partner.name} - {inv_data['ref']}")
        invoices_created += 1
    except Exception as e:
        log(f"  ERROR creating invoice for {partner.name}: {e}")

log(f"Customer invoices: {invoices_created} created, {invoices_skipped} skipped")

# ============================================================================
# VENDOR BILLS (8)
# ============================================================================
log("Creating vendor bills...")

vendor_bills_data = [
    {
        'ref': 'BILL/2025/001',
        'partner': vend_apple,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2025-11-28',
        'lines': [
            {'name': 'iPhone 15 Pro (Wholesale)', 'quantity': 100, 'price_unit': 3000},
            {'name': 'MacBook Pro 14" (Wholesale)', 'quantity': 40, 'price_unit': 6000},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2025/002',
        'partner': vend_nestle,
        'branch': branch_sharjah,
        'bu': bu_fb,
        'date': '2025-12-02',
        'lines': [
            {'name': 'Basmati Rice (Bulk)', 'quantity': 200, 'price_unit': 15},
            {'name': 'Refined Sugar (Bulk)', 'quantity': 500, 'price_unit': 5},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2025/003',
        'partner': vend_rolex,
        'branch': branch_dubai,
        'bu': bu_luxury,
        'date': '2025-12-05',
        'lines': [
            {'name': 'Rolex Submariner (Wholesale)', 'quantity': 10, 'price_unit': 22000},
            {'name': 'Designer Handbag (Wholesale)', 'quantity': 10, 'price_unit': 3500},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2025/004',
        'partner': vend_samsung,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2025-12-08',
        'lines': [
            {'name': 'Samsung QLED TV (Wholesale)', 'quantity': 50, 'price_unit': 2200},
            {'name': 'AirPods Pro (Wholesale)', 'quantity': 200, 'price_unit': 750},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2025/005',
        'partner': vend_al_mokha,
        'branch': branch_sharjah,
        'bu': bu_fb,
        'date': '2025-12-12',
        'lines': [
            {'name': 'Arabic Coffee Beans (Bulk)', 'quantity': 300, 'price_unit': 50},
            {'name': 'Turkish Coffee Beans (Bulk)', 'quantity': 300, 'price_unit': 40},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2026/001',
        'partner': vend_microsoft,
        'branch': branch_dubai,
        'bu': bu_it,
        'date': '2025-12-15',
        'lines': [
            {'name': 'Microsoft 365 Enterprise License', 'quantity': 50, 'price_unit': 1500},
        ],
        'post': True,
    },
    {
        'ref': 'BILL/2026/002',
        'partner': vend_herman_miller,
        'branch': branch_abudhabi,
        'bu': bu_electronics,
        'date': '2025-12-18',
        'lines': [
            {'name': 'Aeron Chair (Wholesale)', 'quantity': 50, 'price_unit': 750},
            {'name': 'Standing Desk (Wholesale)', 'quantity': 30, 'price_unit': 1600},
        ],
        'post': False,  # Draft
    },
    {
        'ref': 'BILL/2026/003',
        'partner': vend_apple,
        'branch': branch_dubai,
        'bu': bu_electronics,
        'date': '2026-01-05',
        'lines': [
            {'name': 'iPhone 15 Pro (Restock)', 'quantity': 80, 'price_unit': 3000},
            {'name': 'MacBook Pro 14" (Restock)', 'quantity': 30, 'price_unit': 6000},
        ],
        'post': False,  # Draft
    },
]

bills_created = 0
bills_skipped = 0

for bill_data in vendor_bills_data:
    partner = bill_data['partner']
    existing = invoice_exists(partner.id, 'in_invoice', bill_data['date'], 0)
    if existing:
        log(f"  SKIP: Bill for {partner.name} on {bill_data['date']} already exists ({existing.name})")
        bills_skipped += 1
        continue

    bill_lines = []
    for line in bill_data['lines']:
        bill_lines.append((0, 0, {
            'name': line['name'],
            'quantity': line['quantity'],
            'price_unit': line['price_unit'],
        }))

    vals = {
        'move_type': 'in_invoice',
        'partner_id': partner.id,
        'journal_id': purchase_journal.id,
        'invoice_date': bill_data['date'],
        'date': bill_data['date'],
        'ref': bill_data['ref'],
        'ops_branch_id': bill_data['branch'].id if bill_data['branch'] else False,
        'ops_business_unit_id': bill_data['bu'].id if bill_data['bu'] else False,
        'invoice_line_ids': bill_lines,
    }

    try:
        bill = env['account.move'].create(vals)
        if bill_data['post']:
            bill.action_post()
            log(f"  CREATED & POSTED: {bill.name} - {partner.name} - {bill_data['ref']}")
        else:
            log(f"  CREATED (DRAFT): {bill.name} - {partner.name} - {bill_data['ref']}")
        bills_created += 1
    except Exception as e:
        log(f"  ERROR creating bill for {partner.name}: {e}")

log(f"Vendor bills: {bills_created} created, {bills_skipped} skipped")

# ============================================================================
# CUSTOMER PAYMENTS (5)
# ============================================================================
log("Creating customer payments...")

customer_payments_data = [
    {
        'partner': cust_gulf_electronics,
        'amount': 48000,
        'date': '2026-01-05',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'memo': 'Payment for INV/2025/001',
    },
    {
        'partner': cust_al_jazeera,
        'amount': 30000,
        'date': '2026-01-08',
        'branch': branch_dubai,
        'bu': bu_fb,
        'memo': 'Partial payment for INV/2025/002',
    },
    {
        'partner': cust_royal_luxury,
        'amount': 86500,
        'date': '2026-01-10',
        'branch': branch_dubai,
        'bu': bu_luxury,
        'memo': 'Payment for INV/2025/003',
    },
    {
        'partner': cust_techvision,
        'amount': 65000,
        'date': '2026-01-15',
        'branch': branch_riyadh,
        'bu': bu_it,
        'memo': 'Payment for INV/2025/004',
    },
    {
        'partner': cust_al_futtaim,
        'amount': 200000,
        'date': '2026-01-25',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'memo': 'Partial payment for INV/2026/002',
    },
]

cust_payments_created = 0
cust_payments_skipped = 0

for pay_data in customer_payments_data:
    partner = pay_data['partner']
    existing = payment_exists(partner.id, 'inbound', pay_data['amount'], pay_data['date'])
    if existing:
        log(f"  SKIP: Customer payment from {partner.name} for {pay_data['amount']} already exists")
        cust_payments_skipped += 1
        continue

    vals = {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': partner.id,
        'amount': pay_data['amount'],
        'date': pay_data['date'],
        'journal_id': bank_journal.id,
        'ref': pay_data['memo'],
    }

    # Set branch/BU if the fields exist on account.payment
    if 'ops_branch_id' in env['account.payment']._fields:
        vals['ops_branch_id'] = pay_data['branch'].id if pay_data['branch'] else False
    if 'ops_business_unit_id' in env['account.payment']._fields:
        vals['ops_business_unit_id'] = pay_data['bu'].id if pay_data['bu'] else False

    try:
        payment = env['account.payment'].create(vals)
        payment.action_post()
        log(f"  CREATED & POSTED: Customer payment from {partner.name} = {pay_data['amount']}")
        cust_payments_created += 1
    except Exception as e:
        log(f"  ERROR creating customer payment from {partner.name}: {e}")

log(f"Customer payments: {cust_payments_created} created, {cust_payments_skipped} skipped")

# ============================================================================
# VENDOR PAYMENTS (4)
# ============================================================================
log("Creating vendor payments...")

vendor_payments_data = [
    {
        'partner': vend_apple,
        'amount': 300000,
        'date': '2026-01-02',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'memo': 'Partial payment for BILL/2025/001',
    },
    {
        'partner': vend_nestle,
        'amount': 5500,
        'date': '2026-01-05',
        'branch': branch_sharjah,
        'bu': bu_fb,
        'memo': 'Full payment for BILL/2025/002',
    },
    {
        'partner': vend_rolex,
        'amount': 255000,
        'date': '2026-01-10',
        'branch': branch_dubai,
        'bu': bu_luxury,
        'memo': 'Payment for BILL/2025/003',
    },
    {
        'partner': vend_samsung,
        'amount': 260000,
        'date': '2026-01-12',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'memo': 'Payment for BILL/2025/004',
    },
]

vend_payments_created = 0
vend_payments_skipped = 0

for pay_data in vendor_payments_data:
    partner = pay_data['partner']
    existing = payment_exists(partner.id, 'outbound', pay_data['amount'], pay_data['date'])
    if existing:
        log(f"  SKIP: Vendor payment to {partner.name} for {pay_data['amount']} already exists")
        vend_payments_skipped += 1
        continue

    vals = {
        'payment_type': 'outbound',
        'partner_type': 'supplier',
        'partner_id': partner.id,
        'amount': pay_data['amount'],
        'date': pay_data['date'],
        'journal_id': bank_journal.id,
        'ref': pay_data['memo'],
    }

    # Set branch/BU if the fields exist on account.payment
    if 'ops_branch_id' in env['account.payment']._fields:
        vals['ops_branch_id'] = pay_data['branch'].id if pay_data['branch'] else False
    if 'ops_business_unit_id' in env['account.payment']._fields:
        vals['ops_business_unit_id'] = pay_data['bu'].id if pay_data['bu'] else False

    try:
        payment = env['account.payment'].create(vals)
        payment.action_post()
        log(f"  CREATED & POSTED: Vendor payment to {partner.name} = {pay_data['amount']}")
        vend_payments_created += 1
    except Exception as e:
        log(f"  ERROR creating vendor payment to {partner.name}: {e}")

log(f"Vendor payments: {vend_payments_created} created, {vend_payments_skipped} skipped")

# ============================================================================
# COMMIT
# ============================================================================
env.cr.commit()
log("=" * 60)
log("SEED 06 COMPLETE")
log(f"  Customer Invoices: {invoices_created} created, {invoices_skipped} skipped")
log(f"  Vendor Bills:      {bills_created} created, {bills_skipped} skipped")
log(f"  Customer Payments: {cust_payments_created} created, {cust_payments_skipped} skipped")
log(f"  Vendor Payments:   {vend_payments_created} created, {vend_payments_skipped} skipped")
log("=" * 60)
