# -*- coding: utf-8 -*-
"""
PHASE 2B: Create Personas and Test Users
Execute with: docker exec gemini_odoo19 python3 /mnt/extra-addons/scripts/phase2b_create_users_simple.py
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID
from datetime import datetime

# Initialize Odoo
odoo.tools.config.parse_config(['-d', 'mz-db', '-c', '/etc/odoo/odoo.conf'])
db_name = 'mz-db'

# Get registry properly
from odoo.modules.registry import Registry
registry = Registry.new(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print('=' * 80)
    print('  PHASE 2B: Create Personas and Test Users')
    print('=' * 80)
    print(f'Timestamp: {datetime.now().isoformat()}')
    print(f'Database: {db_name}')
    
    # Check existing personas
    print('\n' + '=' * 80)
    print('  STEP 1: Check Existing Personas')
    print('=' * 80)
    personas = env['ops.persona'].search([])
    print(f'Found {len(personas)} existing personas:')
    for p in personas:
        print(f'  - {p.name} (Code: {p.code}, ID: {p.id})')
    
    # Look up matrix dimensions
    print('\n' + '=' * 80)
    print('  STEP 2: Look Up Matrix Dimensions')
    print('=' * 80)
    
    branches = {}
    for branch_name in ['Branch-North', 'Branch-HQ']:
        branch = env['ops.branch'].search([('name', '=', branch_name)], limit=1)
        if branch:
            branches[branch_name] = branch
            print(f'  ✓ Found {branch_name}: ID={branch.id}, Company={branch.company_id.name}')
        else:
            print(f'  ✗ ERROR: Branch {branch_name} not found!')
            sys.exit(1)
    
    bus = {}
    for bu_name in ['BU-Sales', 'BU-Finance']:
        bu = env['ops.business.unit'].search([('name', '=', bu_name)], limit=1)
        if bu:
            bus[bu_name] = bu
            print(f'  ✓ Found {bu_name}: ID={bu.id}')
        else:
            print(f'  ✗ ERROR: Business Unit {bu_name} not found!')
            sys.exit(1)
    
    # Create personas
    print('\n' + '=' * 80)
    print('  STEP 3: Create/Update Personas')
    print('=' * 80)
    
    persona_specs = {
        'SALES_REP': {
            'name': 'Sales Rep',
            'description': 'Sales representative with basic order creation rights',
            'branch': branches['Branch-North'],
            'bu': bus['BU-Sales'],
            'authorities': {
                'is_approver': False,
                'can_access_cost_prices': False,
                'can_validate_invoices': False,
            }
        },
        'SALES_MGR': {
            'name': 'Sales Manager',
            'description': 'Sales manager with approval authority',
            'branch': branches['Branch-North'],
            'bu': bus['BU-Sales'],
            'authorities': {
                'is_approver': True,
                'is_bu_leader': True,
                'can_access_cost_prices': False,
                'approval_limit': 50000.0,
            }
        },
        'FIN_CTRL': {
            'name': 'Financial Controller',
            'description': 'Financial controller with accounting rights',
            'branch': branches['Branch-HQ'],
            'bu': bus['BU-Finance'],
            'authorities': {
                'is_approver': True,
                'can_access_cost_prices': True,
                'can_validate_invoices': True,
                'can_post_journal_entries': True,
                'approval_limit': 100000.0,
            }
        },
        'TREASURY': {
            'name': 'Treasury Officer',
            'description': 'Treasury officer with payment and PDC rights',
            'branch': branches['Branch-HQ'],
            'bu': bus['BU-Finance'],
            'authorities': {
                'is_approver': True,
                'can_access_cost_prices': True,
                'can_execute_payments': True,
                'can_manage_pdc': True,
                'approval_limit': 200000.0,
            }
        }
    }
    
    created_personas = {}
    for code, spec in persona_specs.items():
        existing = env['ops.persona'].search([('code', '=', code)], limit=1)
        
        vals = {
            'name': spec['name'],
            'code': code,
            'description': spec['description'],
            'active': True,
            'branch_ids': [(6, 0, [spec['branch'].id])],
            'business_unit_ids': [(6, 0, [spec['bu'].id])],
            'default_branch_id': spec['branch'].id,
            'default_business_unit_id': spec['bu'].id,
        }
        vals.update(spec['authorities'])
        
        if existing:
            print(f'  → Updating persona {code} (ID: {existing.id})')
            existing.write(vals)
            created_personas[code] = existing
        else:
            print(f'  → Creating persona {code}')
            created_personas[code] = env['ops.persona'].create(vals)
        
        print(f'  ✓ Persona {code} ready: ID={created_personas[code].id}')
    
    cr.commit()
    print('\n  ✓ Personas committed to database')
    
    # Create users
    print('\n' + '=' * 80)
    print('  STEP 4: Create/Update Users')
    print('=' * 80)
    
    user_specs = {
        'ops_sales_rep': {
            'name': 'OPS Sales Representative',
            'email': 'ops_sales_rep@test.com',
            'persona_code': 'SALES_REP',
        },
        'ops_sales_mgr': {
            'name': 'OPS Sales Manager',
            'email': 'ops_sales_mgr@test.com',
            'persona_code': 'SALES_MGR',
        },
        'ops_accountant': {
            'name': 'OPS Financial Controller',
            'email': 'ops_accountant@test.com',
            'persona_code': 'FIN_CTRL',
        },
        'ops_treasury': {
            'name': 'OPS Treasury Officer',
            'email': 'ops_treasury@test.com',
            'persona_code': 'TREASURY',
        }
    }
    
    created_users = {}
    for login, spec in user_specs.items():
        existing = env['res.users'].search([('login', '=', login)], limit=1)
        persona = created_personas[spec['persona_code']]
        
        vals = {
            'login': login,
            'name': spec['name'],
            'email': spec['email'],
            'active': True,
            'persona_id': persona.id,
        }
        
        if existing:
            print(f'  → Updating user {login} (ID: {existing.id})')
            existing.write(vals)
            created_users[login] = existing
        else:
            print(f'  → Creating user {login}')
            vals['password'] = '123456'
            created_users[login] = env['res.users'].create(vals)
        
        print(f'  ✓ User {login} ready: ID={created_users[login].id}, Persona={persona.name}')
    
    cr.commit()
    print('\n  ✓ Users committed to database')
    
    # Verification report
    print('\n' + '=' * 80)
    print('  STEP 5: Verification Report')
    print('=' * 80)
    
    print('\n📋 PERSONAS:')
    print('-' * 80)
    for code, p in created_personas.items():
        print(f'\nPersona: {p.name} (Code: {p.code}, ID: {p.id})')
        print(f'  Branches: {", ".join(p.branch_ids.mapped("name"))}')
        print(f'  Business Units: {", ".join(p.business_unit_ids.mapped("name"))}')
        print(f'  Authorities:', end='')
        auths = []
        if p.is_approver:
            auths.append(f'Approver (Limit: {p.approval_limit})')
        if p.is_bu_leader:
            auths.append('BU Leader')
        if p.can_validate_invoices:
            auths.append('Validate Invoices')
        if p.can_post_journal_entries:
            auths.append('Post Journal Entries')
        if p.can_execute_payments:
            auths.append('Execute Payments')
        if p.can_manage_pdc:
            auths.append('Manage PDC')
        print(' ' + ', '.join(auths) if auths else ' None')
    
    print('\n\n👥 USERS:')
    print('-' * 80)
    print(f'{"Login":<20} {"Name":<30} {"Persona":<20} {"Branch":<15} {"BU":<15}')
    print('-' * 80)
    
    for login, user in created_users.items():
        persona = user.persona_id
        branch = persona.default_branch_id.name if persona.default_branch_id else 'N/A'
        bu = persona.default_business_unit_id.name if persona.default_business_unit_id else 'N/A'
        print(f'{login:<20} {user.name:<30} {persona.name:<20} {branch:<15} {bu:<15}')
    
    print('\n' + '=' * 80)
    print('✅ PHASE 2B COMPLETE')
    print('=' * 80)
    print(f'\nTimestamp: {datetime.now().isoformat()}')
    print(f'Personas Created: {len(created_personas)}')
    print(f'Users Created: {len(created_users)}')
    print('\n✓ All data committed to database')
    print('✓ Ready for Phase 3 stress tests')
