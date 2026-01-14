#!/usr/bin/env python3
"""
OPS Framework v1.5.0 - Production Data Seeding Script
Executes comprehensive data seeding for CEO review and UAT
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta
import random

def seed_data(env):
    """Execute comprehensive data seeding"""

    print("="*80)
    print("OPS FRAMEWORK v1.5.0 - PRODUCTION DATA SEEDING")
    print("="*80)

    # PHASE 1: Organizational Structure
    print("\n[PHASE 1] Creating Organizational Structure...")

    # Create parent company
    company = env['res.company'].search([('name', '=', 'Matrix Enterprises')], limit=1)
    if not company:
        company = env['res.company'].create({
            'name': 'Matrix Enterprises',
            'currency_id': env.ref('base.AED').id,
            'country_id': env.ref('base.ae').id,
        })
    print(f"✅ Company: {company.name} (ID: {company.id})")

    # Create branches
    Branch = env['ops.branch']
    branches = {}
    branch_data = [
        ('BR-DXB', 'HQ - Dubai', 'Dubai HQ - Main Office'),
        ('BR-AUH', 'Branch - Abu Dhabi', 'Abu Dhabi Branch'),
        ('BR-SHJ', 'Branch - Sharjah', 'Sharjah Branch'),
    ]

    for code, name, desc in branch_data:
        branch = Branch.search([('code', '=', code)], limit=1)
        if not branch:
            branch = Branch.create({
                'code': code,
                'name': name,
                'description': desc,
                'company_id': company.id,
            })
        branches[code] = branch
        print(f"✅ Branch: {name} ({code})")

    # Create business units
    BU = env['ops.business.unit']
    bus = {}
    bu_data = [
        ('BU-SALES', 'Sales', 'Sales Operations'),
        ('BU-OPS', 'Operations', 'Operational Activities'),
        ('BU-FIN', 'Finance', 'Financial Management'),
    ]

    for code, name, desc in bu_data:
        bu = BU.search([('code', '=', code)], limit=1)
        if not bu:
            bu = BU.create({
                'code': code,
                'name': name,
                'description': desc,
            })
        bus[code] = bu
        print(f"✅ Business Unit: {name} ({code})")

    env.cr.commit()

    # PHASE 2: Create Test Users
    print("\n[PHASE 2] Creating Test Users...")

    User = env['res.users']
    users = {}

    # IT Administrator - ZERO business data visibility (CRITICAL TEST)
    it_admin = User.search([('login', '=', 'it.admin')], limit=1)
    if not it_admin:
        it_admin = User.create({
            'name': 'IT Administrator',
            'login': 'it.admin',
            'password': 'test123',
            'groups_id': [(6, 0, [
                env.ref('base.group_system').id,
                env.ref('ops_matrix_core.group_ops_it_admin').id,
            ])],
            'ops_allowed_branch_ids': [(5, 0, 0)],  # ZERO branches
            'ops_allowed_business_unit_ids': [(5, 0, 0)],  # ZERO BUs
        })
    users['it_admin'] = it_admin
    print(f"✅ IT Admin: {it_admin.login} (ZERO branch/BU access)")

    # Sales User Dubai - Branch isolated
    sales_dxb = User.search([('login', '=', 'sales.dxb')], limit=1)
    if not sales_dxb:
        sales_dxb = User.create({
            'name': 'Sales User Dubai',
            'login': 'sales.dxb',
            'password': 'test123',
            'groups_id': [(6, 0, [
                env.ref('base.group_user').id,
                env.ref('ops_matrix_core.group_ops_user').id,
                env.ref('sales_team.group_sale_salesman').id,
            ])],
            'ops_allowed_branch_ids': [(6, 0, [branches['BR-DXB'].id])],
            'ops_allowed_business_unit_ids': [(6, 0, [bus['BU-SALES'].id])],
        })
    users['sales_dxb'] = sales_dxb
    print(f"✅ Sales Dubai: {sales_dxb.login} (Dubai branch only)")

    # Sales User Abu Dhabi - Branch isolated
    sales_auh = User.search([('login', '=', 'sales.auh')], limit=1)
    if not sales_auh:
        sales_auh = User.create({
            'name': 'Sales User Abu Dhabi',
            'login': 'sales.auh',
            'password': 'test123',
            'groups_id': [(6, 0, [
                env.ref('base.group_user').id,
                env.ref('ops_matrix_core.group_ops_user').id,
                env.ref('sales_team.group_sale_salesman').id,
            ])],
            'ops_allowed_branch_ids': [(6, 0, [branches['BR-AUH'].id])],
            'ops_allowed_business_unit_ids': [(6, 0, [bus['BU-SALES'].id])],
        })
    users['sales_auh'] = sales_auh
    print(f"✅ Sales Abu Dhabi: {sales_auh.login} (Abu Dhabi branch only)")

    # Manager - Multi-branch access
    manager = User.search([('login', '=', 'manager.ops')], limit=1)
    if not manager:
        manager = User.create({
            'name': 'Operations Manager',
            'login': 'manager.ops',
            'password': 'test123',
            'groups_id': [(6, 0, [
                env.ref('base.group_user').id,
                env.ref('ops_matrix_core.group_ops_manager').id,
                env.ref('sales_team.group_sale_manager').id,
            ])],
            'ops_allowed_branch_ids': [(6, 0, [b.id for b in branches.values()])],
            'ops_allowed_business_unit_ids': [(6, 0, [bu.id for bu in bus.values()])],
        })
    users['manager'] = manager
    print(f"✅ Manager: {manager.login} (All branches)")

    env.cr.commit()

    # PHASE 3: Create Customers and Products
    print("\n[PHASE 3] Creating Customers and Products...")

    Partner = env['res.partner']
    customers = []
    for i in range(1, 6):
        customer = Partner.search([('name', '=', f'Customer {i}')], limit=1)
        if not customer:
            customer = Partner.create({
                'name': f'Customer {i}',
                'customer_rank': 1,
                'ops_branch_id': random.choice(list(branches.values())).id,
            })
        customers.append(customer)
    print(f"✅ Created {len(customers)} customers")

    Product = env['product.product']
    products = []
    for i in range(1, 11):
        product = Product.search([('name', '=', f'Product {i}')], limit=1)
        if not product:
            product = Product.create({
                'name': f'Product {i}',
                'type': 'consu',
                'list_price': random.uniform(100, 1000),
                'standard_price': random.uniform(50, 500),
            })
        products.append(product)
    print(f"✅ Created {len(products)} products")

    env.cr.commit()

    # PHASE 4: Create Sales Orders
    print("\n[PHASE 4] Creating Sales Orders...")

    SaleOrder = env['sale.order']
    sales_orders = []

    # Create orders for different branches
    for branch_code, branch in branches.items():
        for i in range(7):  # 7 orders per branch = 21 total
            order = SaleOrder.create({
                'partner_id': random.choice(customers).id,
                'ops_branch_id': branch.id,
                'ops_business_unit_id': bus['BU-SALES'].id,
                'date_order': datetime.now() - timedelta(days=random.randint(1, 90)),
                'order_line': [(0, 0, {
                    'product_id': random.choice(products).id,
                    'product_uom_qty': random.randint(1, 10),
                    'price_unit': random.uniform(100, 1000),
                })],
            })
            sales_orders.append(order)

    print(f"✅ Created {len(sales_orders)} sales orders across branches")
    env.cr.commit()

    # PHASE 5: Summary
    print("\n" + "="*80)
    print("DATA SEEDING COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\nOrganizational Structure:")
    print(f"  - Branches: {len(branches)}")
    print(f"  - Business Units: {len(bus)}")
    print(f"  - Test Users: {len(users)}")
    print(f"\nTransactional Data:")
    print(f"  - Customers: {len(customers)}")
    print(f"  - Products: {len(products)}")
    print(f"  - Sales Orders: {len(sales_orders)}")

    print(f"\n🔐 SECURITY TEST USERS:")
    print(f"  - IT Admin (BLIND): it.admin / test123")
    print(f"  - Sales Dubai: sales.dxb / test123")
    print(f"  - Sales Abu Dhabi: sales.auh / test123")
    print(f"  - Manager (All): manager.ops / test123")

    return {
        'branches': len(branches),
        'users': len(users),
        'sales_orders': len(sales_orders),
    }


if __name__ == '__main__':
    odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf'])

    with api.Environment.manage():
        registry = odoo.registry('mz-db')
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            try:
                result = seed_data(env)
                env.cr.commit()
                print("\n✅ ALL DATA COMMITTED TO DATABASE")
                sys.exit(0)
            except Exception as e:
                env.cr.rollback()
                print(f"\n❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
