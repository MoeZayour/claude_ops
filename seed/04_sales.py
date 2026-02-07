import sys
from datetime import date

def log(msg):
    sys.stderr.write(f"{msg}\n")

log("=" * 50)
log("SEED 04: Sales Orders")
log("=" * 50)

try:
    SO = env['sale.order']
    SOL = env['sale.order.line']
    Partner = env['res.partner']
    Product = env['product.product']
    Branch = env['ops.branch']
    BU = env['ops.business.unit']

    def find_partner(name):
        return Partner.search([('name', 'ilike', name)], limit=1)

    def find_product(name):
        return Product.search([('name', 'ilike', name)], limit=1)

    def find_branch(name):
        return Branch.search([('name', 'ilike', name)], limit=1)

    def find_bu(name):
        return BU.search([('name', 'ilike', name)], limit=1)

    # Cache lookups
    branches = {
        'dubai': find_branch('Dubai'),
        'abudhabi': find_branch('Abu Dhabi'),
        'sharjah': find_branch('Sharjah'),
        'riyadh': find_branch('Riyadh'),
        'doha': find_branch('Doha'),
    }

    bus = {
        'electronics': find_bu('Electronics'),
        'fb': find_bu('Food'),
        'luxury': find_bu('Luxury'),
        'it': find_bu('IT Solutions'),
    }

    customers = {
        'gulf_elec': find_partner('Gulf Electronics'),
        'jazeera': find_partner('Jazeera Hospitality'),
        'royal_luxury': find_partner('Royal Luxury'),
        'techvision': find_partner('TechVision'),
        'emirates_food': find_partner('Emirates Food'),
        'qatar_digital': find_partner('Qatar Digital'),
        'futtaim': find_partner('Futtaim'),
        'saudi_gourmet': find_partner('Saudi Gourmet'),
        'prestige': find_partner('Prestige Watch'),
        'smart_office': find_partner('Smart Office'),
        'crescent': find_partner('Crescent'),
        'riyadh_souk': find_partner('Riyadh Electronics'),
    }

    # Verify lookups
    for k, v in {**branches, **bus}.items():
        if not v:
            log(f"WARNING: Could not find {k}")

    orders = [
        {
            'ref': 'SEED-SO-001', 'partner': 'gulf_elec', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2025, 12, 5), 'confirm': True, 'discount': 0,
            'lines': [('iPhone 15 Pro', 5), ('MacBook Pro', 3)],
        },
        {
            'ref': 'SEED-SO-002', 'partner': 'jazeera', 'branch': 'dubai', 'bu': 'fb',
            'date': date(2025, 12, 10), 'confirm': True, 'discount': 0,
            'lines': [('Arabic Coffee', 10), ('Espresso Machine', 5)],
        },
        {
            'ref': 'SEED-SO-003', 'partner': 'royal_luxury', 'branch': 'dubai', 'bu': 'luxury',
            'date': date(2025, 12, 15), 'confirm': True, 'discount': 5,
            'lines': [('Rolex', 2), ('Designer Handbag', 3)],
        },
        {
            'ref': 'SEED-SO-004', 'partner': 'techvision', 'branch': 'riyadh', 'bu': 'it',
            'date': date(2025, 12, 18), 'confirm': True, 'discount': 0,
            'lines': [('Business Software', 20), ('Monthly System', 10)],
        },
        {
            'ref': 'SEED-SO-005', 'partner': 'emirates_food', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2025, 12, 20), 'confirm': True, 'discount': 0,
            'lines': [('Basmati Rice', 100), ('White Sugar', 200)],
        },
        {
            'ref': 'SEED-SO-006', 'partner': 'qatar_digital', 'branch': 'doha', 'bu': 'electronics',
            'date': date(2025, 12, 22), 'confirm': True, 'discount': 0,
            'lines': [('Samsung', 10), ('AirPods', 20)],
        },
        {
            'ref': 'SEED-SO-007', 'partner': 'futtaim', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2026, 1, 5), 'confirm': True, 'discount': 10,
            'lines': [('iPhone 15 Pro', 50), ('MacBook Pro', 20)],
        },
        {
            'ref': 'SEED-SO-008', 'partner': 'saudi_gourmet', 'branch': 'riyadh', 'bu': 'fb',
            'date': date(2026, 1, 8), 'confirm': True, 'discount': 0,
            'lines': [('Arabic Coffee', 50), ('Turkish Coffee', 30)],
        },
        {
            'ref': 'SEED-SO-009', 'partner': 'prestige', 'branch': 'abudhabi', 'bu': 'luxury',
            'date': date(2026, 1, 10), 'confirm': True, 'discount': 5,
            'lines': [('Rolex', 5)],
        },
        {
            'ref': 'SEED-SO-010', 'partner': 'smart_office', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2026, 1, 12), 'confirm': True, 'discount': 0,
            'lines': [('Ergonomic Office Chair', 30), ('Executive Office Desk', 15)],
        },
        {
            'ref': 'SEED-SO-011', 'partner': 'crescent', 'branch': 'doha', 'bu': 'it',
            'date': date(2026, 1, 15), 'confirm': True, 'discount': 0,
            'lines': [('IT Consulting', 40), ('Cloud Migration', 5)],
        },
        {
            'ref': 'SEED-SO-012', 'partner': 'riyadh_souk', 'branch': 'riyadh', 'bu': 'electronics',
            'date': date(2026, 1, 18), 'confirm': True, 'discount': 0,
            'lines': [('AirPods', 100), ('Samsung', 30)],
        },
        {
            'ref': 'SEED-SO-013', 'partner': 'gulf_elec', 'branch': 'abudhabi', 'bu': 'electronics',
            'date': date(2026, 1, 20), 'confirm': True, 'discount': 0,
            'lines': [('MacBook Pro', 10), ('Home Office Bundle', 5)],
        },
        {
            'ref': 'SEED-SO-014', 'partner': 'jazeera', 'branch': 'dubai', 'bu': 'fb',
            'date': date(2026, 1, 22), 'confirm': True, 'discount': 0,
            'lines': [('Turkish Coffee', 200), ('Coffee Cups', 50)],
        },
        {
            'ref': 'SEED-SO-015', 'partner': 'royal_luxury', 'branch': 'abudhabi', 'bu': 'luxury',
            'date': date(2026, 1, 25), 'confirm': True, 'discount': 5,
            'lines': [('Rolex', 1), ('Designer Handbag', 5)],
        },
        {
            'ref': 'SEED-SO-016', 'partner': 'techvision', 'branch': 'riyadh', 'bu': 'it',
            'date': date(2026, 1, 28), 'confirm': False, 'discount': 0,
            'lines': [('Monthly System', 10), ('Cloud Migration', 3)],
        },
        {
            'ref': 'SEED-SO-017', 'partner': 'futtaim', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2026, 2, 1), 'confirm': False, 'discount': 0,
            'lines': [('Samsung', 20), ('MacBook Pro', 10)],
        },
        {
            'ref': 'SEED-SO-018', 'partner': 'emirates_food', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2026, 2, 3), 'confirm': False, 'discount': 0,
            'lines': [('White Sugar', 500), ('Basmati Rice', 100)],
        },
        {
            'ref': 'SEED-SO-019', 'partner': 'prestige', 'branch': 'dubai', 'bu': 'luxury',
            'date': date(2026, 2, 5), 'confirm': False, 'discount': 5,
            'lines': [('Rolex', 3), ('Designer Handbag', 2)],
        },
        {
            'ref': 'SEED-SO-020', 'partner': 'qatar_digital', 'branch': 'doha', 'bu': 'electronics',
            'date': date(2026, 2, 6), 'confirm': False, 'discount': 0,
            'lines': [('iPhone 15 Pro', 15), ('AirPods', 5)],
        },
    ]

    created = 0
    skipped = 0

    for o in orders:
        # Idempotency check by client_order_ref
        existing = SO.search([('client_order_ref', '=', o['ref'])], limit=1)
        if existing:
            log(f"= Exists: {o['ref']}")
            skipped += 1
            continue

        partner = customers.get(o['partner'])
        branch = branches.get(o['branch'])
        bu = bus.get(o['bu'])

        if not partner:
            log(f"! Skip {o['ref']}: partner '{o['partner']}' not found")
            continue

        # Build order lines
        order_lines = []
        for prod_name, qty in o['lines']:
            product = find_product(prod_name)
            if not product:
                log(f"  WARNING: Product '{prod_name}' not found, skipping line")
                continue
            line_vals = {
                'product_id': product.id,
                'product_uom_qty': qty,
            }
            if o['discount']:
                line_vals['discount'] = o['discount']
            order_lines.append((0, 0, line_vals))

        if not order_lines:
            log(f"! Skip {o['ref']}: no valid product lines")
            continue

        so_vals = {
            'partner_id': partner.id,
            'client_order_ref': o['ref'],
            'date_order': o['date'],
            'order_line': order_lines,
            'company_id': 1,
        }
        if branch:
            so_vals['ops_branch_id'] = branch.id
        if bu:
            so_vals['ops_business_unit_id'] = bu.id

        so = SO.create(so_vals)
        log(f"+ Created: {o['ref']} ({so.name}) - {partner.name}")

        if o['confirm']:
            try:
                so.action_confirm()
                log(f"  Confirmed: {so.name}")
            except Exception as e:
                log(f"  WARNING: Could not confirm {so.name}: {e}")

        created += 1

    env.cr.commit()
    log(f"\nSEED 04 COMPLETE - Created: {created}, Skipped: {skipped}")

except Exception as e:
    env.cr.rollback()
    log(f"ERROR: {e}")
    import traceback
    sys.stderr.write(traceback.format_exc())
