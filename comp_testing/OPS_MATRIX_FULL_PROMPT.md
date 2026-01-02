# OPS MATRIX FRAMEWORK - COMPREHENSIVE TESTING & VALIDATION TASK

## 🎯 MISSION OBJECTIVE
You are an expert Odoo 19 QA Engineer agent. Your mission is to:
1. Analyze ALL OPS Matrix modules in the addons folder
2. Extract ALL testable scenarios, rules, fields, and workflows
3. Generate minimal but complete test data covering every unique scenario ONCE
4. Seed the database with persistent test data for visual inspection
5. Validate all governance rules (Branch, BU, Persona)
6. Fix ANY errors found in SOURCE CODE (never modify database directly for fixes)
7. Generate a comprehensive function and workflow report

## 🖥️ ENVIRONMENT


Container: gemini_odoo19
Port: 8089
Database: mz-db
Odoo Version: 19 CE
Addons Path: /mnt/extra-addons/
Config File: /etc/odoo/odoo.conf
Web URL: http://localhost:8089


## 📚 PHASE 1: MODULE DISCOVERY & ANALYSIS

### Task 1.1: Discover All OPS Matrix Modules


# List all OPS Matrix modules
docker exec -it gemini_odoo19 bash -c "
    find /mnt/extra-addons -name '__manifest__.py' -exec dirname {} \; | sort
"


### Task 1.2: Extract Module Structure

For EACH module discovered, analyze and document:


# For each module, extract:
docker exec -it gemini_odoo19 bash -c "
    for module in /mnt/extra-addons/ops_matrix_*; do
        echo '================================================'
        echo \"MODULE: $(basename $module)\"
        echo '================================================'
        
        echo '--- Models ---'
        grep -r '_name = ' $module/models/*.py 2>/dev/null | grep -v '.pyc'
        
        echo '--- Fields ---'
        grep -rE 'fields\.(Char|Text|Integer|Float|Boolean|Date|Datetime|Many2one|One2many|Many2many|Selection|Binary|Monetary)' $module/models/*.py 2>/dev/null
        
        echo '--- Methods ---'
        grep -rE 'def (action_|_compute_|_onchange_|_check_|_constraint_|create|write|unlink)' $module/models/*.py 2>/dev/null
        
        echo '--- Security Groups ---'
        grep -r 'group_' $module/security/*.xml 2>/dev/null
        
        echo '--- Record Rules ---'
        grep -rA5 'model=\"ir.rule\"' $module/security/*.xml 2>/dev/null
        
        echo '--- Wizards ---'
        ls $module/wizard/*.py 2>/dev/null
        
        echo '--- Reports ---'
        ls $module/report/*.xml 2>/dev/null
        
        echo ''
    done
"


### Task 1.3: Build Scenario Matrix

Create a comprehensive matrix by analyzing:


# Execute in Odoo shell to discover all testable elements
docker exec -it gemini_odoo19 odoo shell -d mz-db -c /etc/odoo/odoo.conf << 'SHELL'

import json
from collections import defaultdict

analysis = {
    'models': {},
    'security_groups': [],
    'record_rules': [],
    'workflows': [],
    'reports': [],
    'wizards': []
}

# 1. Discover all OPS Matrix models
ops_models = env['ir.model'].search([('model', 'like', 'ops.matrix%')])
for model in ops_models:
    model_data = {
        'name': model.model,
        'fields': [],
        'methods': [],
        'constraints': []
    }
    
    # Get fields
    for field in model.field_id:
        if not field.name.startswith('_'):
            model_data['fields'].append({
                'name': field.name,
                'type': field.ttype,
                'required': field.required,
                'readonly': field.readonly,
            })
    
    analysis['models'][model.model] = model_data

# 2. Discover extended models (with branch_id or business_unit_id)
extended_models = env['ir.model.fields'].search([
    ('name', 'in', ['branch_id', 'business_unit_id']),
    ('model_id.model', 'not like', 'ops.matrix%')
])
for field in extended_models:
    if field.model_id.model not in analysis['models']:
        analysis['models'][field.model_id.model] = {
            'name': field.model_id.model,
            'extended': True,
            'ops_fields': []
        }
    analysis['models'][field.model_id.model].setdefault('ops_fields', []).append(field.name)

# 3. Discover security groups
ops_groups = env['res.groups'].search([('full_name', 'ilike', 'ops matrix')])
for group in ops_groups:
    analysis['security_groups'].append({
        'id': group.id,
        'name': group.full_name,
        'users_count': len(group.users),
        'implied_ids': [g.full_name for g in group.implied_ids]
    })

# 4. Discover record rules
ops_rules = env['ir.rule'].search([('name', 'ilike', 'ops')])
for rule in ops_rules:
    analysis['record_rules'].append({
        'name': rule.name,
        'model': rule.model_id.model,
        'domain': rule.domain_force,
        'groups': [g.full_name for g in rule.groups]
    })

# 5. Discover reports
ops_reports = env['ir.actions.report'].search([('report_name', 'ilike', 'ops_matrix')])
for report in ops_reports:
    analysis['reports'].append({
        'name': report.name,
        'model': report.model,
        'report_type': report.report_type
    })

print(json.dumps(analysis, indent=2, default=str))

SHELL


---

## 📊 PHASE 2: TEST DATA ARCHITECTURE

### Task 2.1: Define Test Data Hierarchy

Create test data that covers ALL governance combinations:


TEST_DATA_STRUCTURE = {
    'company': {
        'name': 'OPS Matrix Test Company',
    },
    
    'branches': [
        {'name': 'HQ Branch', 'code': 'HQ', 'is_headquarters': True},
        {'name': 'Dubai Branch', 'code': 'DXB', 'is_headquarters': False},
        {'name': 'Abu Dhabi Branch', 'code': 'AUH', 'is_headquarters': False},
    ],
    
    'business_units': [
        {'name': 'Sales', 'code': 'SALES', 'branch': 'ALL'},
        {'name': 'Finance', 'code': 'FIN', 'branch': 'ALL'},
        {'name': 'Operations', 'code': 'OPS', 'branch': 'ALL'},
        {'name': 'Retail', 'code': 'RETAIL', 'branch': 'DXB'},  # Dubai only
        {'name': 'Wholesale', 'code': 'WHOLESALE', 'branch': 'AUH'},  # Abu Dhabi only
    ],
    
    'personas': [
        {
            'name': 'Sales Representative',
            'code': 'SALES_REP',
            'native_groups': ['sales_team.group_sale_salesman'],
            'max_discount': 10.0,
            'max_order_amount': 5000,
            'can_approve': False,
        },
        {
            'name': 'Sales Manager',
            'code': 'SALES_MGR',
            'native_groups': ['sales_team.group_sale_salesman_all_leads', 'sales_team.group_sale_manager'],
            'max_discount': 25.0,
            'max_order_amount': 50000,
            'can_approve': True,
        },
        {
            'name': 'Accountant',
            'code': 'ACCOUNTANT',
            'native_groups': ['account.group_account_user'],
            'can_post_entries': True,
            'can_approve_payments': False,
        },
        {
            'name': 'Finance Manager',
            'code': 'FIN_MGR',
            'native_groups': ['account.group_account_manager'],
            'can_post_entries': True,
            'can_approve_payments': True,
            'max_payment_amount': 100000,
        },
        {
            'name': 'Branch Manager',
            'code': 'BRANCH_MGR',
            'native_groups': ['base.group_system'],
            'all_bu_access': True,
            'can_approve': True,
        },
        {
            'name': 'Administrator',
            'code': 'ADMIN',
            'native_groups': ['base.group_system'],
            'all_branch_access': True,
            'all_bu_access': True,
        },
    ],
    
    'test_users': [
        # Sales Team - Dubai
        {'login': 'sales_rep_dxb', 'name': 'Sarah Sales (Dubai)', 'branch': 'DXB', 'bu': 'SALES', 'persona': 'SALES_REP'},
        {'login': 'sales_mgr_dxb', 'name': 'Mike Manager (Dubai)', 'branch': 'DXB', 'bu': 'SALES', 'persona': 'SALES_MGR'},
        
        # Sales Team - Abu Dhabi
        {'login': 'sales_rep_auh', 'name': 'Ahmed Sales (AbuDhabi)', 'branch': 'AUH', 'bu': 'SALES', 'persona': 'SALES_REP'},
        
        # Finance Team - HQ
        {'login': 'accountant_hq', 'name': 'Fatima Finance (HQ)', 'branch': 'HQ', 'bu': 'FIN', 'persona': 'ACCOUNTANT'},
        {'login': 'fin_mgr_hq', 'name': 'Omar Finance Mgr (HQ)', 'branch': 'HQ', 'bu': 'FIN', 'persona': 'FIN_MGR'},
        
        # Branch Managers
        {'login': 'branch_mgr_dxb', 'name': 'Khalid Branch Mgr (Dubai)', 'branch': 'DXB', 'bu': 'ALL', 'persona': 'BRANCH_MGR'},
        {'login': 'branch_mgr_auh', 'name': 'Mariam Branch Mgr (AbuDhabi)', 'branch': 'AUH', 'bu': 'ALL', 'persona': 'BRANCH_MGR'},
        
        # Admin
        {'login': 'ops_admin', 'name': 'System Admin', 'branch': 'ALL', 'bu': 'ALL', 'persona': 'ADMIN'},
    ],
}


### Task 2.2: Create Test Data Seeding Script


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
    
    Branch = env['res.branch']
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
    
    BU = env['res.business.unit']
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
            'groups': ['sales_team.group_sale_salesman'],
        },
        {
            'login': 'sales_mgr_dxb',
            'name': 'Mike Manager (Dubai)',
            'password': 'test123',
            'branch_code': 'DXB',
            'bu_code': 'SALES',
            'persona_code': 'SALES_MGR',
            'groups': ['sales_team.group_sale_salesman_all_leads', 'sales_team.group_sale_manager'],
        },
        {
            'login': 'sales_rep_auh',
            'name': 'Ahmed Sales (Abu Dhabi)',
            'password': 'test123',
            'branch_code': 'AUH',
            'bu_code': 'SALES',
            'persona_code': 'SALES_REP',
            'groups': ['sales_team.group_sale_salesman'],
        },
        {
            'login': 'accountant_hq',
            'name': 'Fatima Finance (HQ)',
            'password': 'test123',
            'branch_code': 'HQ',
            'bu_code': 'FIN',
            'persona_code': 'ACCOUNTANT',
            'groups': ['account.group_account_user'],
        },
        {
            'login': 'fin_mgr_hq',
            'name': 'Omar Finance Manager',
            'password': 'test123',
            'branch_code': 'HQ',
            'bu_code': 'FIN',
            'persona_code': 'FIN_MGR',
            'groups': ['account.group_account_manager'],
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
                vals['branch_ids'] = [(6, 0, [branch.id])]
                vals['default_branch_id'] = branch.id
        else:
            vals['branch_ids'] = [(6, 0, [b.id for b in branches.values()])]
        
        # Assign BU
        if data['bu_code']:
            bu = business_units.get(data['bu_code'])
            if bu:
                vals['business_unit_ids'] = [(6, 0, [bu.id])]
        else:
            vals['business_unit_ids'] = [(6, 0, [bu.id for bu in business_units.values()])]
        
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
                    so_vals['branch_id'] = branches[data['branch_code']].id
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
                    inv_vals['branch_id'] = branches[data['branch_code']].id
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


---

## 🧪 PHASE 3: TEST SCENARIO EXECUTION

### Task 3.1: Governance Test Matrix

Execute these tests to validate record rules:


# File: test_governance.py
"""
Governance Validation Tests
Tests branch and BU filtering for all personas
"""

def test_governance(env):
    """Execute governance tests for all user levels."""
    
    results = []
    
    # Get test users
    users = {
        'sales_rep_dxb': env['res.users'].search([('login', '=', 'sales_rep_dxb')], limit=1),
        'sales_rep_auh': env['res.users'].search([('login', '=', 'sales_rep_auh')], limit=1),
        'branch_mgr_dxb': env['res.users'].search([('login', '=', 'branch_mgr_dxb')], limit=1),
        'ops_admin': env['res.users'].search([('login', '=', 'ops_admin')], limit=1),
    }
    
    # Models to test
    test_models = [
        ('sale.order', 'Sales Orders'),
        ('account.move', 'Invoices'),
        ('res.partner', 'Partners'),
        ('crm.lead', 'Leads'),
    ]
    
    for model_name, model_label in test_models:
        try:
            Model = env[model_name]
            
            print(f"\n{'='*50}")
            print(f"TESTING: {model_label} ({model_name})")
            print('='*50)
            
            for user_login, user in users.items():
                if not user:
                    continue
                
                # Switch to user context
                model_as_user = Model.with_user(user)
                
                # Count accessible records
                count = model_as_user.search_count([])
                
                # Get user's branch
                branch_names = ', '.join(user.branch_ids.mapped('name')) or 'ALL'
                
                result = {
                    'user': user_login,
                    'model': model_name,
                    'accessible_records': count,
                    'user_branches': branch_names,
                }
                results.append(result)
                
                print(f"  {user_login:20s} | Branches: {branch_names:30s} | Records: {count}")
                
        except KeyError:
            print(f"  ⚠ Model {model_name} not available")
        except Exception as e:
            print(f"  ✗ Error testing {model_name}: {e}")
    
    return results

# Execute
test_governance(env)


### Task 3.2: Workflow Validation Tests


# Test specific workflow scenarios

def test_workflows(env):
    """Test business workflows with governance."""
    
    print("\n" + "="*60)
    print("WORKFLOW VALIDATION TESTS")
    print("="*60)
    
    # -----------------------------------------------
    # TEST 1: Sales Rep creates order in own branch
    # -----------------------------------------------
    print("\n[TEST 1] Sales Rep creates order in own branch")
    
    sales_rep = env['res.users'].search([('login', '=', 'sales_rep_dxb')], limit=1)
    if sales_rep:
        try:
            partner = env['res.partner'].search([('name', 'ilike', 'Acme')], limit=1)
            
            so = env['sale.order'].with_user(sales_rep).create({
                'partner_id': partner.id,
            })
            
            print(f"  ✅ PASS: Created {so.name}")
            print(f"     Branch: {so.branch_id.name if hasattr(so, 'branch_id') else 'N/A'}")
            
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
    
    # -----------------------------------------------
    # TEST 2: Sales Rep tries to access other branch
    # -----------------------------------------------
    print("\n[TEST 2] Sales Rep tries to view other branch records")
    
    sales_rep_dxb = env['res.users'].search([('login', '=', 'sales_rep_dxb')], limit=1)
    auh_branch = env['res.branch'].search([('code', '=', 'AUH')], limit=1)
    
    if sales_rep_dxb and auh_branch:
        try:
            # Try to find records from other branch
            other_records = env['sale.order'].with_user(sales_rep_dxb).search([
                ('branch_id', '=', auh_branch.id)
            ])
            
            if len(other_records) == 0:
                print(f"  ✅ PASS: Cannot see other branch records (correct)")
            else:
                print(f"  ❌ FAIL: Can see {len(other_records)} records from other branch")
                
        except Exception as e:
            print(f"  ✅ PASS: Access denied - {e}")
    
    # -----------------------------------------------
    # TEST 3: Branch Manager can see all BU records
    # -----------------------------------------------
    print("\n[TEST 3] Branch Manager sees all BU records in branch")
    
    branch_mgr = env['res.users'].search([('login', '=', 'branch_mgr_dxb')], limit=1)
    if branch_mgr:
        try:
            records = env['sale.order'].with_user(branch_mgr).search([])
            print(f"  ℹ Branch Manager can see {len(records)} orders")
            
            # Verify all are from their branch
            invalid = records.filtered(lambda r: hasattr(r, 'branch_id') and r.branch_id.code != 'DXB')
            
            if len(invalid) == 0:
                print(f"  ✅ PASS: All records are from manager's branch")
            else:
                print(f"  ❌ FAIL: Found {len(invalid)} records from other branches")
                
        except Exception as e:
            print(f"  ⚠ Test error: {e}")
    
    # -----------------------------------------------
    # TEST 4: Admin can see all records
    # -----------------------------------------------
    print("\n[TEST 4] Admin can see all records")
    
    admin = env['res.users'].search([('login', '=', 'ops_admin')], limit=1)
    if admin:
        try:
            all_orders = env['sale.order'].with_user(admin).search([])
            all_invoices = env['account.move'].with_user(admin).search([('move_type', '!=', 'entry')])
            
            print(f"  ✅ PASS: Admin sees {len(all_orders)} orders, {len(all_invoices)} invoices")
            
        except Exception as e:
            print(f"  ⚠ Test error: {e}")
    
    print("\n" + "="*60)
    print("WORKFLOW TESTS COMPLETE")
    print("="*60)

# Execute
test_workflows(env)


---

## 🔧 PHASE 4: ERROR FIXING PROTOCOL

### Task 4.1: Error Detection & Fixing

When ANY error is encountered during testing:


ERROR FIXING RULES:
==================

1. ALWAYS fix errors in SOURCE CODE files, never in database
2. Document each error and fix in the error log
3. After fixing, re-run the specific test
4. If fix requires module upgrade, run:
   docker exec -it gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u <module_name> --stop-after-init

ERROR LOG FORMAT:
-----------------
[ERROR_ID] YYYY-MM-DD HH:MM:SS
File: /path/to/file.py
Line: XXX
Error Type: <type>
Error Message: <message>
Root Cause: <analysis>
Fix Applied: <description>
Test Result After Fix: PASS/FAIL


### Task 4.2: Common Fix Patterns


# Pattern 1: Missing field on model
# Error: "Field 'branch_id' does not exist on model 'xxx'"
# Fix: Add field to model extension

# Pattern 2: Record rule prevents access
# Error: "AccessError: ... due to record rules"
# Fix: Review and correct ir.rule domain_force

# Pattern 3: Security group missing
# Error: "AccessError: ... due to security groups"
# Fix: Add missing group to security XML and assign to users

# Pattern 4: Method signature mismatch
# Error: "TypeError: xxx() takes X positional arguments"
# Fix: Update method signature to match Odoo 19 API


---

## 📊 PHASE 5: GENERATE FINAL REPORT

### Task 5.1: Test Results Report

After all tests complete, generate this report:


# OPS MATRIX FRAMEWORK TEST REPORT
Generated: [TIMESTAMP]
Database: mz-db
Odoo Version: 19 CE

## 1. EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total Tests Executed | XX |
| Tests Passed | XX |
| Tests Failed | XX |
| Errors Fixed | XX |
| Pass Rate | XX% |

## 2. MODULE COVERAGE

### ops_matrix_core
| Component | Tested | Status |
|-----------|--------|--------|
| res.branch model | ✅ | PASS |
| res.business.unit model | ✅ | PASS |
| Branch Mixin | ✅ | PASS |
| Record Rules | ✅ | PASS |

### ops_matrix_accounting
| Component | Tested | Status |
|-----------|--------|--------|
| account.move extension | ✅ | PASS |
| Branch filtering | ✅ | PASS |
| Report generation | ✅ | PASS |

### ops_matrix_reporting
| Component | Tested | Status |
|-----------|--------|--------|
| Balance Sheet | ✅ | PASS |
| P&L Report | ✅ | PASS |
| GL Report | ✅ | PASS |
| Aged Reports | ✅ | PASS |

## 3. GOVERNANCE VALIDATION

### Branch Filtering
| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| User sees own branch only | Own | Own | ✅ |
| Manager sees branch only | Branch | Branch | ✅ |
| Admin sees all | All | All | ✅ |

### Business Unit Filtering
| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| User sees own BU | Own | Own | ✅ |
| Manager sees all BU in branch | All in branch | All in branch | ✅ |

## 4. WORKFLOW VALIDATION

### Sales Workflow

[User: sales_rep_dxb]
1. Create Lead ✅
2. Convert to Opportunity ✅
3. Create Quotation ✅
4. Apply Discount (within limit) ✅
5. Apply Discount (over limit) → BLOCKED ✅
6. Confirm Order (within amount) ✅
7. Confirm Order (over amount) → APPROVAL NEEDED ✅


### Finance Workflow

[User: accountant_hq]
1. View Invoices (own branch) ✅
2. Post Journal Entry ✅
3. View Other Branch → BLOCKED ✅


### Approval Workflow

[User: sales_mgr_dxb]
1. Receive Approval Request ✅
2. Approve Order ✅
3. Reject Order ✅


## 5. ERRORS FIXED

| # | File | Error | Fix Applied |
|---|------|-------|-------------|
| 1 | xxx.py | <error> | <fix> |
| 2 | xxx.py | <error> | <fix> |

## 6. DATA CREATED FOR INSPECTION

### Test Users (Password: test123)
| Login | Name | Branch | BU | Persona |
|-------|------|--------|----|---------| 
| sales_rep_dxb | Sarah Sales | Dubai | Sales | Sales Rep |
| ... | ... | ... | ... | ... |

### Test Documents
| Type | Count | Branches |
|------|-------|----------|
| Sales Orders | X | DXB, AUH |
| Invoices | X | HQ, DXB |
| ...

## 7. RECOMMENDATIONS

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## 8. CONCLUSION

The OPS Matrix Framework has been validated with XX% pass rate.
All critical governance rules are functioning correctly.


### Task 5.2: Save Report


# Save report to file
docker exec -it gemini_odoo19 bash -c "
    cat > /mnt/extra-addons/TEST_REPORT_$(date +%Y%m%d_%H%M%S).md << 'EOF'
    [GENERATED REPORT CONTENT]
    EOF
"


---

## 🏁 PHASE 6: FINAL STEPS

### Task 6.1: Restart Container


docker restart gemini_odoo19


### Task 6.2: Verify System Ready


# Wait for startup
sleep 15

# Check health
curl -s http://localhost:8089/web/login | grep -q "Login" && echo "✅ System Ready" || echo "❌ System Not Ready"

# Check logs for errors
docker logs gemini_odoo19 --tail 20 | grep -i error


### Task 6.3: Print Access Information


╔═══════════════════════════════════════════════════════════════╗
║              OPS MATRIX TESTING COMPLETE                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Access URL: http://localhost:8089                            ║
║  Database:   mz-db                                            ║
║                                                               ║
║  TEST ACCOUNTS:                                               ║
║  ─────────────────────────────────────────────────────────    ║
║  sales_rep_dxb / test123    - Sales Rep (Dubai)               ║
║  sales_mgr_dxb / test123    - Sales Manager (Dubai)           ║
║  sales_rep_auh / test123    - Sales Rep (Abu Dhabi)           ║
║  accountant_hq / test123    - Accountant (HQ)                 ║
║  fin_mgr_hq / test123       - Finance Manager (HQ)            ║
║  branch_mgr_dxb / test123   - Branch Manager (Dubai)          ║
║  ops_admin / admin123       - System Administrator            ║
║                                                               ║
║  Report saved to: /mnt/extra-addons/TEST_REPORT_*.md          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝


---

## ✅ SUCCESS CRITERIA

Before completing, verify:

| # | Criteria | Required |
|---|----------|----------|
| 1 | All modules analyzed | ✅ |
| 2 | Test data seeded | ✅ |
| 3 | Governance tests pass | ✅ |
| 4 | Workflow tests pass | ✅ |
| 5 | All errors fixed in source | ✅ |
| 6 | Data persists for inspection | ✅ |
| 7 | Report generated | ✅ |
| 8 | System accessible | ✅ |


---
