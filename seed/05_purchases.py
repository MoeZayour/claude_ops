import sys
from datetime import date

def log(msg):
    sys.stderr.write(f"{msg}\n")

log("=" * 50)
log("SEED 05: Purchase Orders")
log("=" * 50)

try:
    PO = env['purchase.order']
    POL = env['purchase.order.line']
    Partner = env['res.partner']
    Product = env['product.product']
    Branch = env['ops.branch']
    BU = env['ops.business.unit']

    def find_partner(name):
        return Partner.search([('name', 'ilike', name), ('supplier_rank', '>', 0)], limit=1) or \
               Partner.search([('name', 'ilike', name)], limit=1)

    def find_product(name):
        return Product.search([('name', 'ilike', name)], limit=1)

    def find_branch(name):
        return Branch.search([('name', 'ilike', name)], limit=1)

    def find_bu(name):
        return BU.search([('name', 'ilike', name)], limit=1)

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

    suppliers = {
        'apple': find_partner('Apple Distribution'),
        'samsung': find_partner('Samsung Gulf'),
        'nestle': find_partner('Nestlé') or find_partner('Nestle'),
        'mokha': find_partner('Mokha'),
        'rolex': find_partner('Rolex'),
        'herman': find_partner('Herman Miller'),
        'microsoft': find_partner('Microsoft'),
        'marai': find_partner('Marai'),
    }

    for k, v in suppliers.items():
        if not v:
            log(f"WARNING: Supplier '{k}' not found")

    orders = [
        {
            'ref': 'SEED-PO-001', 'partner': 'apple', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2025, 11, 25), 'confirm': True,
            'lines': [('iPhone 15 Pro', 100, 3000), ('MacBook Pro', 40, 6000)],
        },
        {
            'ref': 'SEED-PO-002', 'partner': 'nestle', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2025, 11, 28), 'confirm': True,
            'lines': [('Basmati Rice', 200, 15), ('White Sugar', 500, 5)],
        },
        {
            'ref': 'SEED-PO-003', 'partner': 'rolex', 'branch': 'dubai', 'bu': 'luxury',
            'date': date(2025, 12, 1), 'confirm': True,
            'lines': [('Rolex', 10, 22000), ('Designer Handbag', 10, 3500)],
        },
        {
            'ref': 'SEED-PO-004', 'partner': 'samsung', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2025, 12, 5), 'confirm': True,
            'lines': [('Samsung', 50, 2200), ('AirPods', 200, 750)],
        },
        {
            'ref': 'SEED-PO-005', 'partner': 'mokha', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2025, 12, 8), 'confirm': True,
            'lines': [('Arabic Coffee', 300, 50), ('Turkish Coffee', 300, 40)],
        },
        {
            'ref': 'SEED-PO-006', 'partner': 'microsoft', 'branch': 'dubai', 'bu': 'it',
            'date': date(2025, 12, 10), 'confirm': True,
            'lines': [('Business Software', 50, 1500)],
        },
        {
            'ref': 'SEED-PO-007', 'partner': 'herman', 'branch': 'abudhabi', 'bu': 'electronics',
            'date': date(2025, 12, 12), 'confirm': True,
            'lines': [('Ergonomic Office Chair', 50, 750), ('Executive Office Desk', 30, 1600)],
        },
        {
            'ref': 'SEED-PO-008', 'partner': 'apple', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2026, 1, 2), 'confirm': True,
            'lines': [('iPhone 15 Pro', 80, 3000), ('MacBook Pro', 30, 6000)],
        },
        {
            'ref': 'SEED-PO-009', 'partner': 'mokha', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2026, 1, 5), 'confirm': True,
            'lines': [('Espresso Machine', 100, 5500)],
        },
        {
            'ref': 'SEED-PO-010', 'partner': 'rolex', 'branch': 'dubai', 'bu': 'luxury',
            'date': date(2026, 1, 8), 'confirm': True,
            'lines': [('Rolex', 5, 22000)],
        },
        {
            'ref': 'SEED-PO-011', 'partner': 'samsung', 'branch': 'dubai', 'bu': 'electronics',
            'date': date(2026, 1, 15), 'confirm': False,
            'lines': [('Samsung', 30, 2200)],
        },
        {
            'ref': 'SEED-PO-012', 'partner': 'nestle', 'branch': 'sharjah', 'bu': 'fb',
            'date': date(2026, 1, 20), 'confirm': False,
            'lines': [('White Sugar', 1000, 5), ('Basmati Rice', 200, 15)],
        },
        {
            'ref': 'SEED-PO-013', 'partner': 'apple', 'branch': 'riyadh', 'bu': 'electronics',
            'date': date(2026, 1, 25), 'confirm': False,
            'lines': [('iPhone 15 Pro', 30, 3000), ('AirPods', 10, 750)],
        },
        {
            'ref': 'SEED-PO-014', 'partner': 'microsoft', 'branch': 'dubai', 'bu': 'it',
            'date': date(2026, 2, 1), 'confirm': False,
            'lines': [('Business Software', 30, 1500), ('Monthly System', 20, 900)],
        },
        {
            'ref': 'SEED-PO-015', 'partner': 'mokha', 'branch': 'dubai', 'bu': 'fb',
            'date': date(2026, 2, 4), 'confirm': False,
            'lines': [('Arabic Coffee', 100, 50), ('Coffee Cups', 100, 70)],
        },
    ]

    created = 0
    skipped = 0

    for o in orders:
        existing = PO.search([('partner_ref', '=', o['ref'])], limit=1)
        if existing:
            log(f"= Exists: {o['ref']}")
            skipped += 1
            continue

        partner = suppliers.get(o['partner'])
        branch = branches.get(o['branch'])
        bu = bus.get(o['bu'])

        if not partner:
            log(f"! Skip {o['ref']}: supplier '{o['partner']}' not found")
            continue

        order_lines = []
        for prod_name, qty, cost in o['lines']:
            product = find_product(prod_name)
            if not product:
                log(f"  WARNING: Product '{prod_name}' not found")
                continue
            order_lines.append((0, 0, {
                'product_id': product.id,
                'product_qty': qty,
                'price_unit': cost,
                'name': product.name,
            }))

        if not order_lines:
            log(f"! Skip {o['ref']}: no valid lines")
            continue

        po_vals = {
            'partner_id': partner.id,
            'partner_ref': o['ref'],
            'date_order': o['date'],
            'order_line': order_lines,
            'company_id': 1,
        }
        if branch:
            po_vals['ops_branch_id'] = branch.id
        if bu:
            po_vals['ops_business_unit_id'] = bu.id

        po = PO.create(po_vals)
        log(f"+ Created: {o['ref']} ({po.name}) - {partner.name}")

        if o['confirm']:
            try:
                po.button_confirm()
                log(f"  Confirmed: {po.name}")
            except Exception as e:
                log(f"  WARNING: Could not confirm {po.name}: {e}")

        created += 1

    env.cr.commit()
    log(f"\nSEED 05 COMPLETE - Created: {created}, Skipped: {skipped}")

except Exception as e:
    env.cr.rollback()
    log(f"ERROR: {e}")
    import traceback
    sys.stderr.write(traceback.format_exc())
