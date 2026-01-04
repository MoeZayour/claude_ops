# File: /mnt/extra-addons/ops_matrix_core/data/test_data_seed.py
# -*- coding: utf-8 -*-
"""
OPS Matrix Test Data Seeder
Generates comprehensive test data for all scenarios.
Run via: docker exec -it gemini_odoo19 odoo shell -d mz-db < /path/to/script.py
"""


def seed_test_data(env):
    """Main seeding function."""
    
    print("=" * 60)
    print("OPS MATRIX TEST DATA SEEDER")
    print("=" * 60)
    
    # =========================================
    # 1. CREATE BRANCHES
    # =========================================
    print("\n[1/8] Creating Branches...")
    
    Branch = env['ops.branch']
    branches = {}
    
    branch_data = [
        {'name': 'Headquarters', 'code': 'HQ', 'sequence': 1},
        {'name': 'Dubai Marina Branch', 'code': 'DXB', 'sequence': 2},
        {'name': 'Abu Dhabi Central', 'code': 'AUH', 'sequence': 3},
    ]
    
    for data in branch_data:
        existing = Branch.search([('code', '=', data['code'])], limit=1)
        if existing:
            branches[data['code']] = existing
            print(f"  ✓ Branch exists: {data['name']}")
        else:
            branches[data['code']] = Branch.create(data)
            print(f"  ✓ Created: {data['name']}")
    
    # =========================================
    # 2. CREATE BUSINESS UNITS
    # =========================================
    print("\n[2/8] Creating Business Units...")
    
    BU = env['ops.business.unit']
    business_units = {}
    
    bu_data = [
        {'name': 'Corporate Sales', 'code': 'SALES', 'branch_ids': [(6, 0, [b.id for b in branches.values()])]},
        {'name': 'Finance & Accounting', 'code': 'FIN', 'branch_ids': [(6, 0, [branches['HQ'].id])]},
        {'name': 'Operations', 'code': 'OPS', 'branch_ids': [(6, 0, [b.id for b in branches.values()])]},
        {'name': 'Retail Division', 'code': 'RETAIL', 'branch_ids': [(6, 0, [branches['DXB'].id])]},
        {'name': 'Wholesale Division', 'code': 'WHOLESALE', 'branch_ids': [(6, 0, [branches['AUH'].id])]},
    ]
    
    for data in bu_data:
        existing = BU.search([('code', '=', data['code'])], limit=1)
        if existing:
            business_units[data['code']] = existing
            print(f"  ✓ BU exists: {data['name']}")
        else:
            business_units[data['code']] = BU.create(data)
            print(f"  ✓ Created: {data['name']}")
    
    # =========================================
    # 3. CREATE PERSONAS (if model exists)
    # =========================================
    print("\n[3/8] Creating Personas...")
    
    try:
        Persona = env['ops.matrix.persona']
        personas = {}
        
        persona_data = [
            {
                'name': 'Sales Representative',
                'code': 'SALES_REP',
                'max_discount_percent': 10.0,
                'max_sale_amount': 5000,
                'can_approve_sales': False,
            },
            {
                'name': 'Sales Manager',
                'code': 'SALES_MGR',
                'max_discount_percent': 25.0,
                'max_sale_amount': 50000,
                'can_approve_sales': True,
            },
            {
                'name': 'Accountant',
                'code': 'ACCOUNTANT',
                'can_approve_payments': False,
            },
            {
                'name': 'Finance Manager',
                'code': 'FIN_MGR',
                'can_approve_payments': True,
                'max_payment_amount': 100000,
            },
            {
                'name': 'Branch Manager',
                'code': 'BRANCH_MGR',
                'can_approve_sales': True,
                'can_approve_payments': True,
            },
            {
                'name': 'System Administrator',
                'code': 'ADMIN',
                'can_approve_sales': True,
                'can_approve_payments': True,
            },
        ]
        
        for data in persona_data:
            existing = Persona.search([('code', '=', data['code'])], limit=1)
            if existing:
                personas[data['code']] = existing
                print(f"  ✓ Persona exists: {data['name']}")
            else:
                personas[data['code']] = Persona.create(data)
                print(f"  ✓ Created: {data['name']}")
                
    except KeyError:
        try:
            Persona = env['ops.persona']
            personas = {}

            persona_data = [
                {
                    'name': 'Sales Representative',
                    'code': 'SALES_REP',
                    'max_discount_percent': 10.0,
                    'max_sale_amount': 5000,
                    'can_approve_sales': False,
                },
                {
                    'name': 'Sales Manager',
                    'code': 'SALES_MGR',
                    'max_discount_percent': 25.0,
                    'max_sale_amount': 50000,
                    'can_approve_sales': True,
                },
                {
                    'name': 'Accountant',
                    'code': 'ACCOUNTANT',
                    'can_approve_payments': False,
                },
                {
                    'name': 'Finance Manager',
                    'code': 'FIN_MGR',
                    'can_approve_payments': True,
                    'max_payment_amount': 100000,
                },
                {
                    'name': 'Branch Manager',
                    'code': 'BRANCH_MGR',
                    'can_approve_sales': True,
                    'can_approve_payments': True,
                },
                {
                    'name': 'System Administrator',
                    'code': 'ADMIN',
                    'can_approve_sales': True,
                    'can_approve_payments': True,
                },
            ]

            for data in persona_data:
                existing = Persona.search([('code', '=', data['code'])], limit=1)
                if existing:
                    personas[data['code']] = existing
                    print(f"  ✓ Persona exists: {data['name']}")
                else:
                    personas[data['code']] = Persona.create(data)
                    print(f"  ✓ Created: {data['name']}")
        except KeyError:
            print("  ⚠ Persona model not found - skipping")
            personas = {}
    
    # =========================================
    # 4. CREATE TEST USERS
    # =========================================
    print("\n[4/8] Creating Test Users...")
    
    User = env['res.users']
    users = {}
    
    user_data = [
        {
            'login': 'sales_rep_dxb',
            'name': 'Sarah Sales (Dubai)',
            'password': 'test123',
            'branch_code': 'DXB',
            'bu_code': 'SALES',
            'persona_code': 'SALES_REP',
            'groups': ['base.group_user', 'sales_team.group_sale_salesman'],
        },
        {
            'login': 'sales_mgr_dxb',
            'name': 'Mike Manager (Dubai)',
            'password': 'test123',
            'branch_code': 'DXB',
            'bu_code': 'SALES',
            'persona_code': 'SALES_MGR',
            'groups': ['base.group_user', 'sales_team.group_sale_salesman_all_leads', 'sales_team.group_sale_manager'],
        },
        {
            'login': 'sales_rep_auh',
            'name': 'Ahmed Sales (Abu Dhabi)',
            'password': 'test123',
            'branch_code': 'AUH',
            'bu_code': 'SALES',
            'persona_code': 'SALES_REP',
            'groups': ['base.group_user', 'sales_team.group_sale_salesman'],
        },
        {
            'login': 'accountant_hq',
            'name': 'Fatima Finance (HQ)',
            'password': 'test123',
            'branch_code': 'HQ',
            'bu_code': 'FIN',
            'persona_code': 'ACCOUNTANT',
            'groups': ['base.group_user', 'account.group_account_user'],
        },
        {
            'login': 'fin_mgr_hq',
            'name': 'Omar Finance Manager',
            'password': 'test123',
            'branch_code': 'HQ',
            'bu_code': 'FIN',
            'persona_code': 'FIN_MGR',
            'groups': ['base.group_user', 'account.group_account_manager'],
        },
        {
            'login': 'branch_mgr_dxb',
            'name': 'Khalid Branch Manager (Dubai)',
            'password': 'test123',
            'branch_code': 'DXB',
            'bu_code': None,  # All BUs
            'persona_code': 'BRANCH_MGR',
            'groups': ['base.group_user'],
        },
        {
            'login': 'ops_admin',
            'name': 'System Administrator',
            'password': 'admin123',
            'branch_code': None,  # All branches
            'bu_code': None,  # All BUs
            'persona_code': 'ADMIN',
            'groups': ['base.group_system'],
        },
    ]
    
    for data in user_data:
        existing = User.search([('login', '=', data['login'])], limit=1)
        if existing:
            users[data['login']] = existing
            print(f"  ✓ User exists: {data['login']}")
            continue
        
        # Build user values
        vals = {
            'login': data['login'],
            'name': data['name'],
            'password': data['password'],
        }
        
        # Assign branch
        if data['branch_code']:
            branch = branches.get(data['branch_code'])
            if branch:
                vals['ops_allowed_branch_ids'] = [(6, 0, [branch.id])]
                vals['ops_default_branch_id'] = branch.id
        else:
            vals['ops_allowed_branch_ids'] = [(6, 0, [b.id for b in branches.values()])]
        
        # Assign BU
        if data['bu_code']:
            bu = business_units.get(data['bu_code'])
            if bu:
                vals['ops_allowed_business_unit_ids'] = [(6, 0, [bu.id])]
        else:
            vals['ops_allowed_business_unit_ids'] = [(6, 0, [bu.id for bu in business_units.values()])]
        
        # Assign persona
        if data['persona_code'] and personas.get(data['persona_code']):
            vals['persona_id'] = personas[data['persona_code']].id
        
        # Assign groups
        group_ids = []
        for group_xmlid in data.get('groups', []):
            try:
                group = env.ref(group_xmlid)
                group_ids.append(group.id)
            except:
                pass
        if group_ids:
            vals['groups_id'] = [(6, 0, group_ids)]
        
        try:
            users[data['login']] = User.create(vals)
            print(f"  ✓ Created: {data['login']}")
        except Exception as e:
            print(f"  ✗ Failed to create {data['login']}: {e}")
    
    # =========================================
    # 5. CREATE TEST PARTNERS/CUSTOMERS
    # =========================================
    print("\n[5/8] Creating Test Partners...")
    
    Partner = env['res.partner']
    partners = {}
    
    partner_data = [
        {'name': 'Acme Corporation', 'is_company': True, 'customer_rank': 1, 'branch_code': 'DXB'},
        {'name': 'Global Supplies Ltd', 'is_company': True, 'customer_rank': 1, 'branch_code': 'AUH'},
        {'name': 'Tech Solutions Inc', 'is_company': True, 'customer_rank': 1, 'branch_code': 'HQ'},
        {'name': 'Quick Vendors LLC', 'is_company': True, 'supplier_rank': 1, 'branch_code': 'DXB'},
        {'name': 'Prime Suppliers', 'is_company': True, 'supplier_rank': 1, 'branch_code': 'AUH'},
        {'name': 'John Customer (Dubai)', 'is_company': False, 'customer_rank': 1, 'branch_code': 'DXB'},
        {'name': 'Jane Customer (AbuDhabi)', 'is_company': False, 'customer_rank': 1, 'branch_code': 'AUH'},
    ]
    
    for data in partner_data:
        existing = Partner.search([('name', '=', data['name'])], limit=1)
        if existing:
            partners[data['name']] = existing
            print(f"  ✓ Partner exists: {data['name']}")
            continue
        
        vals = {
            'name': data['name'],
            'is_company': data.get('is_company', False),
            'customer_rank': data.get('customer_rank', 0),
            'supplier_rank': data.get('supplier_rank', 0),
        }
        
        # Assign branch if model supports it
        if data.get('branch_code') and branches.get(data['branch_code']):
            try:
                vals['branch_id'] = branches[data['branch_code']].id
            except:
                pass
        
        partners[data['name']] = Partner.create(vals)
        print(f"  ✓ Created: {data['name']}")
    
    # =========================================
    # 6. CREATE TEST PRODUCTS
    # =========================================
    print("\n[6/8] Creating Test Products...")
    
    Product = env['product.product']
    products = {}
    
    product_data = [
        {'name': 'Standard Widget', 'list_price': 100, 'standard_price': 60, 'type': 'consu'},
        {'name': 'Premium Widget', 'list_price': 250, 'standard_price': 150, 'type': 'consu'},
        {'name': 'Basic Service', 'list_price': 500, 'type': 'service'},
        {'name': 'Premium Service', 'list_price': 1500, 'type': 'service'},
        {'name': 'Stockable Item A', 'list_price': 75, 'standard_price': 40, 'type': 'product'},
        {'name': 'Stockable Item B', 'list_price': 120, 'standard_price': 80, 'type': 'product'},
    ]
    
    for data in product_data:
        existing = Product.search([('name', '=', data['name'])], limit=1)
        if existing:
            products[data['name']] = existing
            print(f"  ✓ Product exists: {data['name']}")
        else:
            products[data['name']] = Product.create(data)
            print(f"  ✓ Created: {data['name']}")
    
    # =========================================
    # 7. CREATE TEST TRANSACTIONS
    # =========================================
    print("\n[7/8] Creating Test Transactions...")
    
    # --- Sales Orders (if module available) ---
    try:
        SaleOrder = env['sale.order']
        
        so_data = [
            {
                'partner': 'Acme Corporation',
                'user': 'sales_rep_dxb',
                'branch_code': 'DXB',
                'lines': [
                    ('Standard Widget', 5),
                    ('Basic Service', 1),
                ],
            },
            {
                'partner': 'Global Supplies Ltd',
                'user': 'sales_rep_auh',
                'branch_code': 'AUH',
                'lines': [
                    ('Premium Widget', 3),
                ],
            },
        ]
        
        for data in so_data:
            partner = partners.get(data['partner'])
            user = users.get(data['user'])
            if not partner or not user:
                continue
            
            so_vals = {
                'partner_id': partner.id,
                'user_id': user.id,
            }
            
            if data.get('branch_code') and branches.get(data['branch_code']):
                try:
                    so_vals['ops_branch_id'] = branches[data['branch_code']].id
                except:
                    pass
            
            so = SaleOrder.create(so_vals)
            
            for product_name, qty in data['lines']:
                product = products.get(product_name)
                if product:
                    env['sale.order.line'].create({
                        'order_id': so.id,
                        'product_id': product.id,
                        'product_uom_qty': qty,
                    })
            
            print(f"  ✓ Created SO: {so.name}")
            
    except Exception as e:
        print(f"  ⚠ Sales orders skipped: {e}")
    
    # --- Invoices ---
    try:
        AccountMove = env['account.move']
        
        inv_data = [
            {
                'partner': 'Tech Solutions Inc',
                'branch_code': 'HQ',
                'move_type': 'out_invoice',
                'amount': 1500,
            },
            {
                'partner': 'Acme Corporation',
                'branch_code': 'DXB',
                'move_type': 'out_invoice',
                'amount': 3200,
            },
            {
                'partner': 'Quick Vendors LLC',
                'branch_code': 'DXB',
                'move_type': 'in_invoice',
                'amount': 2100,
            },
        ]
        
        for data in inv_data:
            partner = partners.get(data['partner'])
            if not partner:
                continue
            
            inv_vals = {
                'partner_id': partner.id,
                'move_type': data['move_type'],
            }
            
            if data.get('branch_code') and branches.get(data['branch_code']):
                try:
                    inv_vals['ops_branch_id'] = branches[data['branch_code']].id
                except:
                    pass
            
            inv = AccountMove.create(inv_vals)
            
            # Add invoice line
            env['account.move.line'].with_context(check_move_validity=False).create({
                'move_id': inv.id,
                'name': f"Test line for {data['partner']}",
                'quantity': 1,
                'price_unit': data['amount'],
            })
            
            print(f"  ✓ Created Invoice: {inv.name}")
            
    except Exception as e:
        print(f"  ⚠ Invoices skipped: {e}")
    
    # =========================================
    # 8. COMMIT AND REPORT
    # =========================================
    print("\n[8/8] Committing data...")
    env.cr.commit()
    
    print("\n" + "=" * 60)
    print("TEST DATA SEEDING COMPLETE")
    print("=" * 60)
    print(f"""
    SUMMARY:
    --------
    Branches Created:       {len(branches)}
    Business Units Created: {len(business_units)}
    Personas Created:       {len(personas)}
    Test Users Created:     {len(users)}
    Partners Created:       {len(partners)}
    Products Created:       {len(products)}
    
    TEST USER CREDENTIALS:
    ----------------------
    Login: sales_rep_dxb     Password: test123
    Login: sales_mgr_dxb     Password: test123
    Login: sales_rep_auh     Password: test123
    Login: accountant_hq     Password: test123
    Login: fin_mgr_hq        Password: test123
    Login: branch_mgr_dxb    Password: test123
    Login: ops_admin         Password: admin123
    
    Access URL: http://localhost:8089
    """)
    
    return True

# Execute
seed_test_data(env)
