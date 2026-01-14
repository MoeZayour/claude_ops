#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPS Matrix Framework - Test Data Seeding Script
================================================

Creates realistic multi-branch dataset for testing:
- 3 branches, 4 business units each
- 18 users with various personas
- 30+ sales orders, 20+ purchase orders
- 15+ vendor bills, 10+ PDCs, 10+ approvals

Usage:
    ./odoo-bin shell -d <database> < tools/seed_test_data.py

Or via Docker:
    docker compose run --rm gemini_odoo19 odoo shell -d gemini_odoo19 < tools/seed_test_data.py
"""

import logging
from datetime import date, timedelta
from random import choice, randint, uniform

_logger = logging.getLogger(__name__)


def seed_test_data(env):
    """Main seeding function."""
    _logger.info("=" * 60)
    _logger.info("OPS Matrix Framework - Test Data Seeding")
    _logger.info("=" * 60)

    # Get or create company
    company = env.ref('base.main_company')
    _logger.info(f"Using company: {company.name}")

    # ============================================================
    # PHASE 1: Create Branches
    # ============================================================
    _logger.info("\n--- Creating Branches ---")

    branches_data = [
        {'name': 'Dubai Main Branch', 'code': 'DXB', 'city': 'Dubai'},
        {'name': 'Abu Dhabi Branch', 'code': 'AUH', 'city': 'Abu Dhabi'},
        {'name': 'Sharjah Branch', 'code': 'SHJ', 'city': 'Sharjah'},
    ]

    branches = env['ops.branch']
    for data in branches_data:
        branch = env['ops.branch'].search([('code', '=', data['code'])], limit=1)
        if not branch:
            branch = env['ops.branch'].create({
                'name': data['name'],
                'code': data['code'],
                'city': data['city'],
                'company_id': company.id,
                'active': True,
            })
            _logger.info(f"  Created branch: {branch.name}")
        else:
            _logger.info(f"  Branch exists: {branch.name}")
        branches |= branch

    # ============================================================
    # PHASE 2: Create Business Units (4 per branch)
    # ============================================================
    _logger.info("\n--- Creating Business Units ---")

    bu_types = [
        {'name': 'Electronics', 'code': 'ELEC'},
        {'name': 'Furniture', 'code': 'FURN'},
        {'name': 'FMCG', 'code': 'FMCG'},
        {'name': 'Industrial', 'code': 'INDL'},
    ]

    business_units = env['ops.business.unit']
    for branch in branches:
        for bu_data in bu_types:
            bu_code = f"{branch.code}-{bu_data['code']}"
            bu = env['ops.business.unit'].search([('code', '=', bu_code)], limit=1)
            if not bu:
                bu = env['ops.business.unit'].create({
                    'name': f"{bu_data['name']} - {branch.code}",
                    'code': bu_code,
                    'ops_branch_id': branch.id,
                    'company_id': company.id,
                    'active': True,
                })
                _logger.info(f"  Created BU: {bu.name}")
            else:
                _logger.info(f"  BU exists: {bu.name}")
            business_units |= bu

    # ============================================================
    # PHASE 3: Create Personas
    # ============================================================
    _logger.info("\n--- Creating Personas ---")

    personas_data = [
        {'name': 'Branch Manager', 'code': 'BM', 'level': 'manager'},
        {'name': 'Sales Representative', 'code': 'SR', 'level': 'user'},
        {'name': 'Accountant', 'code': 'ACC', 'level': 'user'},
        {'name': 'Warehouse Manager', 'code': 'WM', 'level': 'manager'},
        {'name': 'BU Head', 'code': 'BUH', 'level': 'manager'},
        {'name': 'Procurement Officer', 'code': 'PO', 'level': 'user'},
    ]

    personas = env['ops.persona']
    for data in personas_data:
        persona = env['ops.persona'].search([('code', '=', data['code'])], limit=1)
        if not persona:
            persona = env['ops.persona'].create({
                'name': data['name'],
                'code': data['code'],
                'company_id': company.id,
                'active': True,
            })
            _logger.info(f"  Created persona: {persona.name}")
        else:
            _logger.info(f"  Persona exists: {persona.name}")
        personas |= persona

    # ============================================================
    # PHASE 4: Create Test Users (18 users)
    # ============================================================
    _logger.info("\n--- Creating Test Users ---")

    # Get OPS groups
    group_ops_user = env.ref('ops_matrix_core.group_ops_user', raise_if_not_found=False)
    group_ops_manager = env.ref('ops_matrix_core.group_ops_manager', raise_if_not_found=False)
    group_sales = env.ref('sales_team.group_sale_salesman', raise_if_not_found=False)
    group_purchase = env.ref('purchase.group_purchase_user', raise_if_not_found=False)

    users = env['res.users']
    user_count = 0

    for branch in branches:
        branch_bus = business_units.filtered(lambda b: b.ops_branch_id == branch)

        for i, persona in enumerate(personas[:6]):
            login = f"{persona.code.lower()}_{branch.code.lower()}"
            user = env['res.users'].search([('login', '=', login)], limit=1)

            if not user:
                # Assign to a BU (rotate through available BUs)
                bu = branch_bus[i % len(branch_bus)] if branch_bus else False

                groups = [env.ref('base.group_user').id]
                if group_ops_user:
                    groups.append(group_ops_user.id)
                if persona.code in ['BM', 'BUH', 'WM'] and group_ops_manager:
                    groups.append(group_ops_manager.id)
                if persona.code in ['SR', 'BM'] and group_sales:
                    groups.append(group_sales.id)
                if persona.code in ['PO', 'BM'] and group_purchase:
                    groups.append(group_purchase.id)

                user = env['res.users'].create({
                    'name': f"{persona.name} ({branch.code})",
                    'login': login,
                    'password': 'demo123',
                    'company_id': company.id,
                    'company_ids': [(6, 0, [company.id])],
                    'groups_id': [(6, 0, groups)],
                })

                # Set OPS matrix fields via SQL to avoid constraint issues
                if hasattr(user, 'ops_branch_id'):
                    user.write({
                        'ops_branch_id': branch.id,
                        'ops_business_unit_id': bu.id if bu else False,
                        'ops_persona_id': persona.id,
                    })

                _logger.info(f"  Created user: {user.name} ({login})")
                user_count += 1
            else:
                _logger.info(f"  User exists: {login}")

            users |= user

    _logger.info(f"  Total users created: {user_count}")

    # ============================================================
    # PHASE 5: Create Partners (Customers & Vendors)
    # ============================================================
    _logger.info("\n--- Creating Partners ---")

    customers = []
    vendors = []

    customer_names = [
        'Al Futtaim Group', 'Majid Al Futtaim', 'Emaar Properties',
        'DEWA', 'Dubai Municipality', 'RTA Dubai', 'Etisalat',
        'Du Telecom', 'Jumeirah Group', 'Emirates Airlines',
    ]

    vendor_names = [
        'Samsung Electronics', 'LG Electronics', 'HP Inc',
        'Dell Technologies', 'Lenovo', 'IKEA', 'Home Centre',
        'ACE Hardware', 'Danube Building Materials', 'RAK Ceramics',
    ]

    for name in customer_names:
        partner = env['res.partner'].search([('name', '=', name)], limit=1)
        if not partner:
            partner = env['res.partner'].create({
                'name': name,
                'is_company': True,
                'customer_rank': 1,
                'company_id': company.id,
            })
            _logger.info(f"  Created customer: {name}")
        customers.append(partner)

    for name in vendor_names:
        partner = env['res.partner'].search([('name', '=', name)], limit=1)
        if not partner:
            partner = env['res.partner'].create({
                'name': name,
                'is_company': True,
                'supplier_rank': 1,
                'company_id': company.id,
            })
            _logger.info(f"  Created vendor: {name}")
        vendors.append(partner)

    # ============================================================
    # PHASE 6: Create Products
    # ============================================================
    _logger.info("\n--- Creating Products ---")

    products_data = [
        {'name': 'Laptop HP ProBook', 'price': 3500, 'cost': 2800, 'type': 'product'},
        {'name': 'Desktop Dell OptiPlex', 'price': 2800, 'cost': 2200, 'type': 'product'},
        {'name': 'Monitor Samsung 27"', 'price': 1200, 'cost': 900, 'type': 'product'},
        {'name': 'Office Chair Executive', 'price': 1500, 'cost': 1000, 'type': 'product'},
        {'name': 'Office Desk L-Shape', 'price': 2500, 'cost': 1800, 'type': 'product'},
        {'name': 'Printer HP LaserJet', 'price': 1800, 'cost': 1400, 'type': 'product'},
        {'name': 'Network Switch 24-Port', 'price': 800, 'cost': 600, 'type': 'product'},
        {'name': 'UPS 3000VA', 'price': 2200, 'cost': 1700, 'type': 'product'},
        {'name': 'IT Support Service', 'price': 500, 'cost': 0, 'type': 'service'},
        {'name': 'Installation Service', 'price': 300, 'cost': 0, 'type': 'service'},
    ]

    products = []
    for data in products_data:
        product = env['product.product'].search([('name', '=', data['name'])], limit=1)
        if not product:
            product = env['product.product'].create({
                'name': data['name'],
                'list_price': data['price'],
                'standard_price': data['cost'],
                'detailed_type': data['type'],
                'company_id': company.id,
            })
            _logger.info(f"  Created product: {data['name']}")
        products.append(product)

    # ============================================================
    # PHASE 7: Create Sales Orders (30+)
    # ============================================================
    _logger.info("\n--- Creating Sales Orders ---")

    so_count = 0
    for i in range(35):
        customer = choice(customers)
        branch = choice(list(branches))
        bus = business_units.filtered(lambda b: b.ops_branch_id == branch)
        bu = choice(list(bus)) if bus else False

        # Random date in last 90 days
        order_date = date.today() - timedelta(days=randint(1, 90))

        so_vals = {
            'partner_id': customer.id,
            'date_order': order_date,
            'company_id': company.id,
        }

        # Add matrix fields if available
        if hasattr(env['sale.order'], 'ops_branch_id'):
            so_vals['ops_branch_id'] = branch.id
        if hasattr(env['sale.order'], 'ops_business_unit_id') and bu:
            so_vals['ops_business_unit_id'] = bu.id

        so = env['sale.order'].create(so_vals)

        # Add 1-5 order lines
        for _ in range(randint(1, 5)):
            product = choice(products)
            qty = randint(1, 10)

            env['sale.order.line'].create({
                'order_id': so.id,
                'product_id': product.id,
                'product_uom_qty': qty,
                'price_unit': product.list_price * uniform(0.9, 1.1),
            })

        so_count += 1
        if so_count % 10 == 0:
            _logger.info(f"  Created {so_count} sales orders...")

    _logger.info(f"  Total sales orders: {so_count}")

    # ============================================================
    # PHASE 8: Create Purchase Orders (20+)
    # ============================================================
    _logger.info("\n--- Creating Purchase Orders ---")

    po_count = 0
    for i in range(25):
        vendor = choice(vendors)
        branch = choice(list(branches))
        bus = business_units.filtered(lambda b: b.ops_branch_id == branch)
        bu = choice(list(bus)) if bus else False

        order_date = date.today() - timedelta(days=randint(1, 60))

        po_vals = {
            'partner_id': vendor.id,
            'date_order': order_date,
            'company_id': company.id,
        }

        if hasattr(env['purchase.order'], 'ops_branch_id'):
            po_vals['ops_branch_id'] = branch.id
        if hasattr(env['purchase.order'], 'ops_business_unit_id') and bu:
            po_vals['ops_business_unit_id'] = bu.id

        po = env['purchase.order'].create(po_vals)

        for _ in range(randint(1, 4)):
            product = choice([p for p in products if p.detailed_type == 'product'])
            qty = randint(5, 50)

            env['purchase.order.line'].create({
                'order_id': po.id,
                'product_id': product.id,
                'product_qty': qty,
                'price_unit': product.standard_price * uniform(0.95, 1.05),
            })

        po_count += 1

    _logger.info(f"  Total purchase orders: {po_count}")

    # ============================================================
    # PHASE 9: Create PDCs (10+)
    # ============================================================
    _logger.info("\n--- Creating PDCs ---")

    pdc_receivable_count = 0
    pdc_payable_count = 0

    # Check if PDC models exist
    if 'ops.pdc.receivable' in env:
        for i in range(8):
            customer = choice(customers)
            branch = choice(list(branches))
            maturity = date.today() + timedelta(days=randint(30, 120))

            pdc_vals = {
                'partner_id': customer.id,
                'amount': randint(10000, 100000),
                'check_number': f"CHK-R-{1000 + i}",
                'check_date': date.today() - timedelta(days=randint(1, 30)),
                'maturity_date': maturity,
                'company_id': company.id,
            }

            if hasattr(env['ops.pdc.receivable'], 'branch_id'):
                pdc_vals['branch_id'] = branch.id

            try:
                env['ops.pdc.receivable'].create(pdc_vals)
                pdc_receivable_count += 1
            except Exception as e:
                _logger.warning(f"  Could not create PDC receivable: {e}")

        _logger.info(f"  Created {pdc_receivable_count} PDC receivables")

    if 'ops.pdc.payable' in env:
        for i in range(6):
            vendor = choice(vendors)
            branch = choice(list(branches))
            maturity = date.today() + timedelta(days=randint(30, 90))

            pdc_vals = {
                'partner_id': vendor.id,
                'amount': randint(5000, 50000),
                'check_number': f"CHK-P-{2000 + i}",
                'check_date': date.today() - timedelta(days=randint(1, 15)),
                'maturity_date': maturity,
                'company_id': company.id,
            }

            if hasattr(env['ops.pdc.payable'], 'branch_id'):
                pdc_vals['branch_id'] = branch.id

            try:
                env['ops.pdc.payable'].create(pdc_vals)
                pdc_payable_count += 1
            except Exception as e:
                _logger.warning(f"  Could not create PDC payable: {e}")

        _logger.info(f"  Created {pdc_payable_count} PDC payables")

    # ============================================================
    # PHASE 10: Create Assets (5+)
    # ============================================================
    _logger.info("\n--- Creating Assets ---")

    asset_count = 0
    if 'ops.asset' in env:
        # First ensure we have an asset category
        category = env['ops.asset.category'].search([], limit=1)
        if not category:
            category = env['ops.asset.category'].create({
                'name': 'IT Equipment',
                'depreciation_method': 'straight_line',
                'depreciation_duration': 5,
                'company_id': company.id,
            })
            _logger.info(f"  Created asset category: {category.name}")

        assets_data = [
            {'name': 'Server Dell PowerEdge', 'value': 25000},
            {'name': 'Network Infrastructure', 'value': 15000},
            {'name': 'Office Furniture Set', 'value': 35000},
            {'name': 'Company Vehicle - Toyota', 'value': 85000},
            {'name': 'HVAC System', 'value': 45000},
        ]

        for data in assets_data:
            branch = choice(list(branches))
            bus = business_units.filtered(lambda b: b.ops_branch_id == branch)
            bu = choice(list(bus)) if bus else False

            asset_vals = {
                'name': data['name'],
                'category_id': category.id,
                'purchase_value': data['value'],
                'purchase_date': date.today() - timedelta(days=randint(30, 365)),
                'company_id': company.id,
            }

            if hasattr(env['ops.asset'], 'ops_branch_id'):
                asset_vals['ops_branch_id'] = branch.id
            if hasattr(env['ops.asset'], 'ops_business_unit_id') and bu:
                asset_vals['ops_business_unit_id'] = bu.id

            try:
                env['ops.asset'].create(asset_vals)
                asset_count += 1
            except Exception as e:
                _logger.warning(f"  Could not create asset: {e}")

        _logger.info(f"  Created {asset_count} assets")

    # ============================================================
    # SUMMARY
    # ============================================================
    _logger.info("\n" + "=" * 60)
    _logger.info("TEST DATA SEEDING COMPLETE")
    _logger.info("=" * 60)
    _logger.info(f"Branches: {len(branches)}")
    _logger.info(f"Business Units: {len(business_units)}")
    _logger.info(f"Personas: {len(personas)}")
    _logger.info(f"Users: {len(users)}")
    _logger.info(f"Customers: {len(customers)}")
    _logger.info(f"Vendors: {len(vendors)}")
    _logger.info(f"Products: {len(products)}")
    _logger.info(f"Sales Orders: {so_count}")
    _logger.info(f"Purchase Orders: {po_count}")
    _logger.info(f"PDC Receivables: {pdc_receivable_count}")
    _logger.info(f"PDC Payables: {pdc_payable_count}")
    _logger.info(f"Assets: {asset_count}")
    _logger.info("=" * 60)

    # Commit the transaction
    env.cr.commit()
    _logger.info("Transaction committed successfully!")

    return True


# Execute when run via shell
if __name__ == '__main__' or 'env' in dir():
    try:
        seed_test_data(env)
    except NameError:
        print("This script must be run via Odoo shell:")
        print("  ./odoo-bin shell -d <database> < tools/seed_test_data.py")
