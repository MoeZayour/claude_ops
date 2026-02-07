# -*- coding: utf-8 -*-
"""
OPS Matrix Seed Script - Partners (Customers, Suppliers, Contacts)
=================================================================
Run via:
    cat seed/03_partners.py | docker exec -i gemini_odoo19 odoo shell \
        -c /etc/odoo/odoo.conf -d mz-db --no-http

Creates:
    - 12 realistic customer companies (UAE, KSA, Qatar)
    - 8 supplier companies
    - 5 contact persons linked to key customers

Idempotent: searches by name before creating; safe to run multiple times.
"""

import sys


def log(msg):
    """Print progress to stderr (stdout is swallowed by Odoo shell)."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def get_or_create_partner(env, vals, search_field='name'):
    """Search for an existing partner by name; create if missing.

    Returns:
        (record, created): tuple of the partner record and a boolean flag
    """
    Partner = env['res.partner']
    domain = [(search_field, '=', vals[search_field])]
    existing = Partner.search(domain, limit=1)
    if existing:
        return existing, False
    record = Partner.create(vals)
    return record, True


def resolve_country(env, code, _cache={}):
    """Resolve a country record by its ISO code. Results are cached."""
    if code not in _cache:
        country = env['res.country'].search([('code', '=', code)], limit=1)
        if not country:
            log(f"  WARNING: Country code '{code}' not found!")
        _cache[code] = country
    return _cache[code]


def resolve_payment_term(env, _cache=[]):
    """Find a suitable payment term (prefer '30 Days', else first available)."""
    if _cache:
        return _cache[0]
    PaymentTerm = env['account.payment.term']
    # Try common names for a 30-day term
    for name_pattern in ['30 Days', '30 days', '30 Net Days', 'Net 30']:
        term = PaymentTerm.search([('name', 'ilike', name_pattern)], limit=1)
        if term:
            _cache.append(term)
            return term
    # Fallback: first payment term that exists
    term = PaymentTerm.search([], limit=1)
    if term:
        _cache.append(term)
        return term
    _cache.append(PaymentTerm)  # empty recordset
    return _cache[0]


# =============================================================================
# MAIN SEEDING LOGIC
# =============================================================================

log("=" * 70)
log("  OPS MATRIX SEED: 03_partners.py")
log("  Creating Customers, Suppliers, and Contact Persons")
log("=" * 70)

# ---------------------------------------------------------------------------
# Resolve common lookups
# ---------------------------------------------------------------------------
country_ae = resolve_country(env, 'AE')
country_sa = resolve_country(env, 'SA')
country_qa = resolve_country(env, 'QA')
payment_term = resolve_payment_term(env)

log(f"\n  Payment term: {payment_term.name if payment_term else 'NONE FOUND'}")
log(f"  Countries: AE={country_ae.id if country_ae else '?'}, "
    f"SA={country_sa.id if country_sa else '?'}, "
    f"QA={country_qa.id if country_qa else '?'}")

# ---------------------------------------------------------------------------
# CUSTOMERS (12)
# ---------------------------------------------------------------------------
log("\n" + "-" * 70)
log("  [1/3] Creating Customers")
log("-" * 70)

customers_data = [
    {
        'name': 'Gulf Electronics LLC',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 500000.0,
        'vat': 'AE100371946200003',
        'street': 'Sheikh Zayed Road, Tower 3, Office 1205',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 338 8001',
        'email': 'procurement@gulfelectronics.ae',
        'website': 'https://www.gulfelectronics.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Al Jazeera Hospitality Group',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 300000.0,
        'vat': 'AE100482057300004',
        'street': 'Corniche Road, Al Hosn Tower, Suite 801',
        'city': 'Abu Dhabi',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 2 445 6100',
        'email': 'purchasing@aljazeera-hospitality.ae',
        'website': 'https://www.aljazeera-hospitality.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Royal Luxury Trading',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 1000000.0,
        'vat': 'AE100593168400005',
        'street': 'DIFC, Gate Avenue, Unit 402',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 509 7200',
        'email': 'orders@royalluxurytrading.ae',
        'website': 'https://www.royalluxurytrading.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'TechVision Solutions',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 200000.0,
        'vat': 'SA3104728593001',
        'street': 'King Fahd Road, Al Faisaliah Tower, Floor 18',
        'city': 'Riyadh',
        'country_id': country_sa.id if country_sa else False,
        'phone': '+966 11 217 4500',
        'email': 'procurement@techvision.sa',
        'website': 'https://www.techvision.sa',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Emirates Food Distribution',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 250000.0,
        'vat': 'AE100704279500006',
        'street': 'Industrial Area 12, Warehouse Complex B',
        'city': 'Sharjah',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 6 534 2800',
        'email': 'supply@emiratesfood.ae',
        'website': 'https://www.emiratesfood.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Qatar Digital Solutions',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 400000.0,
        'vat': 'QA100283746500',
        'street': 'West Bay, Tornado Tower, Floor 22',
        'city': 'Doha',
        'country_id': country_qa.id if country_qa else False,
        'phone': '+974 4423 8100',
        'email': 'info@qatardigital.qa',
        'website': 'https://www.qatardigital.qa',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Al Futtaim Retail Group',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 750000.0,
        'vat': 'AE100815380600007',
        'street': 'Dubai Festival City, Office Block C, Floor 5',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 213 6000',
        'email': 'procurement@alfuttaim-retail.ae',
        'website': 'https://www.alfuttaim-retail.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Saudi Gourmet Co.',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 150000.0,
        'vat': 'SA3215839604002',
        'street': 'Olaya District, Al Rashid Mega Mall Road',
        'city': 'Riyadh',
        'country_id': country_sa.id if country_sa else False,
        'phone': '+966 11 463 7200',
        'email': 'orders@saudigourmet.sa',
        'website': 'https://www.saudigourmet.sa',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Prestige Watch Gallery',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 2000000.0,
        'vat': 'AE100926491700008',
        'street': 'The Galleria, Al Maryah Island, Shop G-14',
        'city': 'Abu Dhabi',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 2 671 3400',
        'email': 'buying@prestigewatch.ae',
        'website': 'https://www.prestigewatch.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Smart Office Interiors',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 300000.0,
        'vat': 'AE100037502800009',
        'street': 'Business Bay, Prism Tower, Office 702',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 876 5300',
        'email': 'procurement@smartoffice.ae',
        'website': 'https://www.smartoffice.ae',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Crescent Consulting',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 100000.0,
        'vat': 'QA100394857600',
        'street': 'Lusail Marina, Tower 8, Floor 12',
        'city': 'Doha',
        'country_id': country_qa.id if country_qa else False,
        'phone': '+974 4412 5700',
        'email': 'admin@crescentconsulting.qa',
        'website': 'https://www.crescentconsulting.qa',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Riyadh Electronics Souk',
        'is_company': True,
        'customer_rank': 1,
        'company_id': 1,
        'ops_credit_limit': 350000.0,
        'vat': 'SA3326940715003',
        'street': 'Al Batha District, Electronics Market Road',
        'city': 'Riyadh',
        'country_id': country_sa.id if country_sa else False,
        'phone': '+966 11 405 8900',
        'email': 'purchasing@riyadhsouk.sa',
        'website': 'https://www.riyadhsouk.sa',
        'property_payment_term_id': payment_term.id if payment_term else False,
    },
]

customers = {}  # name -> record, used later for contacts
created_count = 0
existed_count = 0

for data in customers_data:
    partner, created = get_or_create_partner(env, data)
    customers[data['name']] = partner
    if created:
        created_count += 1
        log(f"  + Created customer: {data['name']} ({data['city']})")
    else:
        existed_count += 1
        log(f"  = Exists:           {data['name']} ({data['city']})")

log(f"\n  Customers: {created_count} created, {existed_count} already existed")

# ---------------------------------------------------------------------------
# SUPPLIERS (8)
# ---------------------------------------------------------------------------
log("\n" + "-" * 70)
log("  [2/3] Creating Suppliers")
log("-" * 70)

suppliers_data = [
    {
        'name': 'Apple Distribution MENA',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100148613900010',
        'street': 'Dubai Internet City, Building 14',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 366 4400',
        'email': 'distribution-mena@apple.com',
        'website': 'https://www.apple.com/ae',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Samsung Gulf FZE',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100259724000011',
        'street': 'Jebel Ali Free Zone, LOB 17',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 881 9000',
        'email': 'b2b-gulf@samsung.com',
        'website': 'https://www.samsung.com/ae',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Nestle Middle East',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100360835100012',
        'street': 'Dubai Production City, Block B',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 404 5100',
        'email': 'trade-me@nestle.com',
        'website': 'https://www.nestle-me.com',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Al Mokha Coffee Traders',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100471946200013',
        'street': 'Industrial Area 4, Warehouse 22',
        'city': 'Sharjah',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 6 542 1800',
        'email': 'sales@almokha.ae',
        'website': 'https://www.almokha.ae',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Rolex MENA',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100582057300014',
        'street': 'DIFC, The Exchange, Tower 2, Floor 30',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 425 0800',
        'email': 'wholesale-mena@rolex.com',
        'website': 'https://www.rolex.com',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Herman Miller Gulf',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100693168400015',
        'street': 'Al Raha Beach, Canal District, Unit 5',
        'city': 'Abu Dhabi',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 2 558 2200',
        'email': 'orders-gulf@hermanmiller.com',
        'website': 'https://www.hermanmiller.com',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Microsoft Gulf',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'AE100804279500016',
        'street': 'Dubai Internet City, Building 8',
        'city': 'Dubai',
        'country_id': country_ae.id if country_ae else False,
        'phone': '+971 4 364 9600',
        'email': 'licensing-gulf@microsoft.com',
        'website': 'https://www.microsoft.com/ae',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
    {
        'name': 'Al Marai Company',
        'is_company': True,
        'supplier_rank': 1,
        'company_id': 1,
        'vat': 'SA3437051826004',
        'street': 'Exit 7, Prince Turki Al Awwal Road',
        'city': 'Riyadh',
        'country_id': country_sa.id if country_sa else False,
        'phone': '+966 11 470 0005',
        'email': 'b2b@almarai.com',
        'website': 'https://www.almarai.com',
        'property_supplier_payment_term_id': payment_term.id if payment_term else False,
    },
]

created_count = 0
existed_count = 0

for data in suppliers_data:
    partner, created = get_or_create_partner(env, data)
    if created:
        created_count += 1
        log(f"  + Created supplier: {data['name']} ({data['city']})")
    else:
        existed_count += 1
        log(f"  = Exists:           {data['name']} ({data['city']})")

log(f"\n  Suppliers: {created_count} created, {existed_count} already existed")

# ---------------------------------------------------------------------------
# CONTACT PERSONS (5) - linked to key customers
# ---------------------------------------------------------------------------
log("\n" + "-" * 70)
log("  [3/3] Creating Contact Persons")
log("-" * 70)

contacts_data = [
    {
        'name': 'Ibrahim Al Rashid',
        'is_company': False,
        'type': 'contact',
        'function': 'Procurement Manager',
        'parent_company': 'Gulf Electronics LLC',
        'phone': '+971 50 881 2345',
        'email': 'ibrahim.rashid@gulfelectronics.ae',
    },
    {
        'name': 'Mohammed Al Hashimi',
        'is_company': False,
        'type': 'contact',
        'function': 'Procurement Manager',
        'parent_company': 'Al Jazeera Hospitality Group',
        'phone': '+971 55 774 6789',
        'email': 'mohammed.hashimi@aljazeera-hospitality.ae',
    },
    {
        'name': 'Fatima Al Suwaidi',
        'is_company': False,
        'type': 'contact',
        'function': 'Procurement Manager',
        'parent_company': 'Royal Luxury Trading',
        'phone': '+971 56 903 4567',
        'email': 'fatima.suwaidi@royalluxurytrading.ae',
    },
    {
        'name': 'Salman Al Otaibi',
        'is_company': False,
        'type': 'contact',
        'function': 'Procurement Manager',
        'parent_company': 'TechVision Solutions',
        'phone': '+966 55 312 8901',
        'email': 'salman.otaibi@techvision.sa',
    },
    {
        'name': 'Hamad Al Thani',
        'is_company': False,
        'type': 'contact',
        'function': 'Procurement Manager',
        'parent_company': 'Qatar Digital Solutions',
        'phone': '+974 5523 4567',
        'email': 'hamad.thani@qatardigital.qa',
    },
]

created_count = 0
existed_count = 0

for data in contacts_data:
    parent_name = data.pop('parent_company')
    parent = customers.get(parent_name)

    if not parent:
        # Try searching in case the customer was created in a prior run
        parent = env['res.partner'].search(
            [('name', '=', parent_name), ('is_company', '=', True)], limit=1
        )

    if parent:
        data['parent_id'] = parent.id
    else:
        log(f"  WARNING: Parent company '{parent_name}' not found for {data['name']}")

    # For contacts, search by name AND parent to allow same name under different companies
    existing = env['res.partner'].search([
        ('name', '=', data['name']),
        ('parent_id', '=', data.get('parent_id', False)),
    ], limit=1)

    if existing:
        existed_count += 1
        log(f"  = Exists:          {data['name']} -> {parent_name}")
    else:
        env['res.partner'].create(data)
        created_count += 1
        log(f"  + Created contact: {data['name']} -> {parent_name}")

log(f"\n  Contacts: {created_count} created, {existed_count} already existed")

# ---------------------------------------------------------------------------
# COMMIT
# ---------------------------------------------------------------------------
env.cr.commit()

log("\n" + "=" * 70)
log("  DONE - All partners committed to database.")
log("=" * 70)
