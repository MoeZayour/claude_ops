#!/usr/bin/env python3
"""
OPS Framework Comprehensive Seed Data Script
Creates realistic test data for UAT testing
"""
print("="*60)
print("OPS FRAMEWORK COMPREHENSIVE SEED DATA")
print("="*60)

# Get environment
env = cr.execute("SELECT current_database()").fetchone()
print(f"Database: {env[0] if env else 'unknown'}")

# 1. COMPANIES & STRUCTURE
print("\n[1/6] Creating Companies and Structure...")

# Check if companies exist
company_count = env['res.company'].search_count([])
if company_count == 0:
    # Create Matrix Group company
    company = env['res.company'].create({
        'name': 'Matrix Group',
        'street': 'Business Bay',
        'city': 'Dubai',
        'country_id': env.ref('base.ae').id,
        'currency_id': env.ref('base.AED').id,
        'email': 'info@matrixgroup.ae',
        'phone': '+971 4 123 4567',
    })
    print(f"  ✓ Created company: {company.name}")
else:
    company = env['res.company'].search([], limit=1)
    print(f"  ✓ Using existing company: {company.name}")

# 2. BUSINESS UNITS
print("\n[2/6] Creating Business Units...")
bu_count = env['ops.business.unit'].search_count([])
if bu_count == 0:
    # Retail BU
    retail_bu = env['ops.business.unit'].create({
        'name': 'Retail Division',
        'code': 'RETAIL',
        'description': 'Retail sales operations - electronics, appliances, accessories',
        'company_id': company.id,
        'active': True,
    })
    print(f"  ✓ Created BU: {retail_bu.name}")
    
    # Wholesale BU
    wholesale_bu = env['ops.business.unit'].create({
        'name': 'Wholesale Division',
        'code': 'WHOLESALE',
        'description': 'B2B bulk sales to retailers and distributors',
        'company_id': company.id,
        'active': True,
    })
    print(f"  ✓ Created BU: {wholesale_bu.name}")
    
    # Electronics BU
    electronics_bu = env['ops.business.unit'].create({
        'name': 'Electronics',
        'code': 'ELECTRONICS',
        'description': 'Consumer and commercial electronics',
        'company_id': company.id,
        'active': True,
    })
    print(f"  ✓ Created BU: {electronics_bu.name}")
else:
    retail_bu = env['ops.business.unit'].search([('code', '=', 'RETAIL')], limit=1) or env['ops.business.unit'].search([], limit=1)
    wholesale_bu = env['ops.business.unit'].search([('code', '=', 'WHOLESALE')], limit=1)
    print(f"  ✓ Using existing BUs")

# 3. BRANCHES
print("\n[3/6] Creating Branches...")
branch_count = env['ops.branch'].search_count([])
if branch_count == 0:
    # Dubai HQ
    dubai_branch = env['ops.branch'].create({
        'name': 'Dubai HQ',
        'code': 'DXB-HQ',
        'company_id': company.id,
        'address': 'Business Bay, Dubai',
        'active': True,
    })
    print(f"  ✓ Created branch: {dubai_branch.name}")
    
    # Abu Dhabi
    ad_branch = env['ops.branch'].create({
        'name': 'Abu Dhabi',
        'code': 'AD-MAIN',
        'company_id': company.id,
        'address': 'Corniche Road, Abu Dhabi',
        'active': True,
    })
    print(f"  ✓ Created branch: {ad_branch.name}")
    
    # Sharjah
    sharjah_branch = env['ops.branch'].create({
        'name': 'Sharjah',
        'code': 'SHJ-MAIN',
        'company_id': company.id,
        'address': 'Al Majaz, Sharjah',
        'active': True,
    })
    print(f"  ✓ Created branch: {sharjah_branch.name}")
else:
    dubai_branch = env['ops.branch'].search([('code', '=', 'DXB-HQ')], limit=1) or env['ops.branch'].search([], limit=1)
    ad_branch = env['ops.branch'].search([('code', '=', 'AD-MAIN')], limit=1)
    sharjah_branch = env['ops.branch'].search([('code', '=', 'SHJ-MAIN')], limit=1)
    print(f"  ✓ Using existing branches")

# 4. USERS
print("\n[4/6] Creating Users...")
user_count = env['res.users'].search_count([])
if user_count <= 3:  # Only admin exists
    # System Admin
    admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
    
    # CEO
    ceo_user = env['res.users'].create({
        'name': 'Sarah Al Mansouri',
        'login': 'ceo@matrixgroup.ae',
        'email': 'ceo@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id, env.ref('base.group_system').id])],
    })
    print(f"  ✓ Created user: {ceo_user.name}")
    
    # CFO
    cfo_user = env['res.users'].create({
        'name': 'Ahmed Al Ketbi',
        'login': 'cfo@matrixgroup.ae',
        'email': 'cfo@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id, env.ref('account.group_account_manager').id])],
    })
    print(f"  ✓ Created user: {cfo_user.name}")
    
    # Branch Manager - Dubai
    bm_dubai_user = env['res.users'].create({
        'name': 'Khalid Al Otaibi',
        'login': 'bm.dubai@matrixgroup.ae',
        'email': 'bm.dubai@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id])],
    })
    print(f"  ✓ Created user: {bm_dubai_user.name}")
    
    # Branch Manager - Abu Dhabi
    bm_ad_user = env['res.users'].create({
        'name': 'Mohammed Al Habsi',
        'login': 'bm.abudhabi@matrixgroup.ae',
        'email': 'bm.abudhabi@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id])],
    })
    print(f"  ✓ Created user: {bm_ad_user.name}")
    
    # Sales Reps
    sales1_user = env['res.users'].create({
        'name': 'Ali Hassan',
        'login': 'sales1@matrixgroup.ae',
        'email': 'sales1@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id])],
    })
    print(f"  ✓ Created user: {sales1_user.name}")
    
    sales2_user = env['res.users'].create({
        'name': 'Fatima Al Zaabi',
        'login': 'sales2@matrixgroup.ae',
        'email': 'sales2@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id])],
    })
    print(f"  ✓ Created user: {sales2_user.name}")
    
    # Accountant
    accountant_user = env['res.users'].create({
        'name': 'Rashid Al Marsi',
        'login': 'accountant@matrixgroup.ae',
        'email': 'accountant@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id, env.ref('account.group_account_user').id])],
    })
    print(f"  ✓ Created user: {accountant_user.name}")
    
    # Warehouse Manager
    warehouse_user = env['res.users'].create({
        'name': 'Saeed Al Rashdi',
        'login': 'warehouse@matrixgroup.ae',
        'email': 'warehouse@matrixgroup.ae',
        'company_id': company.id,
        'company_ids': [(6, 0, [company.id])],
        'groups_id': [(6, 0, [env.ref('base.group_user').id])],
    })
    print(f"  ✓ Created user: {warehouse_user.name}")
else:
    print(f"  ✓ Users already exist ({user_count} users)")

# 5. PERSONAS
print("\n[5/6] Creating Personas...")
persona_count = env['ops.persona'].search_count([])
if persona_count == 0:
    # CEO Persona
    ceo_persona = env['ops.persona'].create({
        'name': 'CEO - Executive',
        'code': 'PRS-CEO',
        'user_id': ceo_user.id if 'ceo_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id, ad_branch.id, sharjah_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, wholesale_bu.id, electronics_bu.id])],
        'is_approver': True,
        'approval_limit': 1000000,
        'is_branch_manager': True,
        'is_bu_leader': True,
        'is_matrix_administrator': True,
        'job_level': 'executive',
    })
    print(f"  ✓ Created persona: {ceo_persona.name}")
    
    # CFO Persona
    cfo_persona = env['ops.persona'].create({
        'name': 'CFO - Finance',
        'code': 'PRS-CFO',
        'user_id': cfo_user.id if 'cfo_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id, ad_branch.id, sharjah_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, wholesale_bu.id, electronics_bu.id])],
        'is_approver': True,
        'approval_limit': 500000,
        'can_validate_invoices': True,
        'can_post_journal_entries': True,
        'job_level': 'director',
    })
    print(f"  ✓ Created persona: {cfo_persona.name}")
    
    # Dubai Branch Manager
    bm_dubai_persona = env['ops.persona'].create({
        'name': 'Dubai Branch Manager',
        'code': 'PRS-BM-DXB',
        'user_id': bm_dubai_user.id if 'bm_dubai_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, electronics_bu.id])],
        'is_branch_manager': True,
        'is_approver': True,
        'approval_limit': 50000,
        'can_adjust_inventory': True,
        'job_level': 'manager',
    })
    print(f"  ✓ Created persona: {bm_dubai_persona.name}")
    
    # Abu Dhabi Branch Manager
    bm_ad_persona = env['ops.persona'].create({
        'name': 'Abu Dhabi Branch Manager',
        'code': 'PRS-BM-AD',
        'user_id': bm_ad_user.id if 'bm_ad_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [ad_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, wholesale_bu.id])],
        'is_branch_manager': True,
        'is_approver': True,
        'approval_limit': 50000,
        'job_level': 'manager',
    })
    print(f"  ✓ Created persona: {bm_ad_persona.name}")
    
    # Sales Reps
    sales1_persona = env['ops.persona'].create({
        'name': 'Sales Rep - Dubai',
        'code': 'PRS-SALES-DXB',
        'user_id': sales1_user.id if 'sales1_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id])],
        'can_access_cost_prices': False,
        'max_discount_percent': 5.0,
        'job_level': 'mid',
    })
    print(f"  ✓ Created persona: {sales1_persona.name}")
    
    sales2_persona = env['ops.persona'].create({
        'name': 'Sales Rep - Retail',
        'code': 'PRS-SALES-RET',
        'user_id': sales2_user.id if 'sales2_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id, sharjah_branch.id])],
        'business_unit_ids': [(6, 0, [electronics_bu.id])],
        'can_access_cost_prices': False,
        'max_discount_percent': 5.0,
        'job_level': 'mid',
    })
    print(f"  ✓ Created persona: {sales2_persona.name}")
    
    # Accountant
    accountant_persona = env['ops.persona'].create({
        'name': 'Accountant',
        'code': 'PRS-ACC',
        'user_id': accountant_user.id if 'accountant_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id, ad_branch.id, sharjah_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, wholesale_bu.id])],
        'can_validate_invoices': True,
        'can_access_cost_prices': True,
        'job_level': 'senior',
    })
    print(f"  ✓ Created persona: {accountant_persona.name}")
    
    # Warehouse Manager
    warehouse_persona = env['ops.persona'].create({
        'name': 'Warehouse Manager',
        'code': 'PRS-WH',
        'user_id': warehouse_user.id if 'warehouse_user' in dir() else False,
        'company_id': company.id,
        'branch_ids': [(6, 0, [dubai_branch.id])],
        'business_unit_ids': [(6, 0, [retail_bu.id, wholesale_bu.id, electronics_bu.id])],
        'can_adjust_inventory': True,
        'can_access_cost_prices': True,
        'job_level': 'manager',
    })
    print(f"  ✓ Created persona: {warehouse_persona.name}")
else:
    print(f"  ✓ Personas already exist ({persona_count} personas)")

# 6. SAMPLE TRANSACTIONS
print("\n[6/6] Creating Sample Transactions...")
so_count = env['sale.order'].search_count([])
if so_count == 0:
    # Create some sample products first
    product_obj = env['product.product']
    
    # Check for existing products or create sample
    if product_obj.search_count([]) < 5:
        # Create sample products
        products = []
        for i in range(1, 6):
            product = product_obj.create({
                'name': f'Sample Product {i}',
                'default_code': f'SMP-{i:03d}',
                'type': 'consu',
                'list_price': 100 + i * 50,
                'standard_price': 50 + i * 20,
            })
            products.append(product)
            print(f"  ✓ Created product: {product.name}")
    
    # Create sample sales orders
    products = product_obj.search([], limit=5)
    customers = env['res.partner'].search([('customer_rank', '>', 0)], limit=5)
    
    if customers:
        for i in range(1, 8):
            customer = customers[i % len(customers)]
            so = env['sale.order'].create({
                'partner_id': customer.id,
                'company_id': company.id,
                'date_order': fields.Datetime.now() - timedelta(days=i),
                'state': 'draft' if i > 5 else ('sale' if i > 2 else 'done'),
            })
            
            # Add order lines
            for product in products[:2]:
                env['sale.order.line'].create({
                    'order_id': so.id,
                    'product_id': product.id,
                    'product_uom_qty': 1 + i,
                    'price_unit': product.list_price,
                })
            
            print(f"  ✓ Created SO: {so.name}")
    
    # Create sample purchase orders
    vendors = env['res.partner'].search([('supplier_rank', '>', 0)], limit=5)
    if vendors:
        for i in range(1, 5):
            vendor = vendors[i % len(vendors)]
            po = env['purchase.order'].create({
                '