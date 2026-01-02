#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 2B: Create Personas and Test Users
=========================================
Creates 4 personas with proper authority flags and 4 test users with matrix assignments.
Database: mz-db
"""

import sys
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

# ============================================
# PERSONA SPECIFICATIONS
# ============================================
PERSONA_SPECS = {
    'SALES_REP': {
        'name': 'Sales Rep',
        'code': 'SALES_REP',
        'description': 'Sales representative with basic order creation rights',
        'authorities': {
            'is_approver': False,
            'can_access_cost_prices': False,
            'can_modify_product_master': False,
            'can_validate_invoices': False,
            'can_post_journal_entries': False,
            'can_execute_payments': False,
            'can_adjust_inventory': False,
            'can_manage_pdc': False,
        }
    },
    'SALES_MGR': {
        'name': 'Sales Manager',
        'code': 'SALES_MGR',
        'description': 'Sales manager with approval authority',
        'authorities': {
            'is_approver': True,
            'is_bu_leader': True,
            'can_access_cost_prices': False,
            'can_modify_product_master': False,
            'can_validate_invoices': False,
            'can_post_journal_entries': False,
            'can_execute_payments': False,
            'can_adjust_inventory': False,
            'can_manage_pdc': False,
            'approval_limit': 50000.0,
        }
    },
    'FIN_CTRL': {
        'name': 'Financial Controller',
        'code': 'FIN_CTRL',
        'description': 'Financial controller with accounting and invoice validation rights',
        'authorities': {
            'is_approver': True,
            'can_access_cost_prices': True,
            'can_modify_product_master': False,
            'can_validate_invoices': True,
            'can_post_journal_entries': True,
            'can_execute_payments': False,
            'can_adjust_inventory': False,
            'can_manage_pdc': False,
            'approval_limit': 100000.0,
        }
    },
    'TREASURY': {
        'name': 'Treasury Officer',
        'code': 'TREASURY',
        'description': 'Treasury officer with payment execution and PDC management rights',
        'authorities': {
            'is_approver': True,
            'can_access_cost_prices': True,
            'can_modify_product_master': False,
            'can_validate_invoices': False,
            'can_post_journal_entries': False,
            'can_execute_payments': True,
            'can_adjust_inventory': False,
            'can_manage_pdc': True,
            'approval_limit': 200000.0,
        }
    }
}

# ============================================
# USER SPECIFICATIONS
# ============================================
USER_SPECS = {
    'ops_sales_rep': {
        'login': 'ops_sales_rep',
        'name': 'OPS Sales Representative',
        'email': 'ops_sales_rep@test.com',
        'password': '123456',
        'persona_code': 'SALES_REP',
        'branch_name': 'Branch-North',
        'bu_name': 'BU-Sales',
    },
    'ops_sales_mgr': {
        'login': 'ops_sales_mgr',
        'name': 'OPS Sales Manager',
        'email': 'ops_sales_mgr@test.com',
        'password': '123456',
        'persona_code': 'SALES_MGR',
        'branch_name': 'Branch-North',
        'bu_name': 'BU-Sales',
    },
    'ops_accountant': {
        'login': 'ops_accountant',
        'name': 'OPS Financial Controller',
        'email': 'ops_accountant@test.com',
        'password': '123456',
        'persona_code': 'FIN_CTRL',
        'branch_name': 'Branch-HQ',
        'bu_name': 'BU-Finance',
    },
    'ops_treasury': {
        'login': 'ops_treasury',
        'name': 'OPS Treasury Officer',
        'email': 'ops_treasury@test.com',
        'password': '123456',
        'persona_code': 'TREASURY',
        'branch_name': 'Branch-HQ',
        'bu_name': 'BU-Finance',
    }
}


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_existing_personas(env):
    """Check what personas currently exist."""
    print_header("STEP 1: Check Existing Personas")
    
    personas = env['ops.persona'].search([])
    print(f"Found {len(personas)} existing personas:")
    for p in personas:
        print(f"  - {p.name} (Code: {p.code}, ID: {p.id})")
    
    return {p.code: p for p in personas}


def lookup_matrix_dimensions(env):
    """Look up branch and BU IDs."""
    print_header("STEP 2: Look Up Matrix Dimensions")
    
    # Look up branches
    branches = {}
    for branch_name in ['Branch-North', 'Branch-HQ']:
        branch = env['ops.branch'].search([('name', '=', branch_name)], limit=1)
        if branch:
            branches[branch_name] = branch
            print(f"  ✓ Found {branch_name}: ID={branch.id}, Company={branch.company_id.name}")
        else:
            print(f"  ✗ ERROR: Branch '{branch_name}' not found!")
            return None, None
    
    # Look up business units
    bus = {}
    for bu_name in ['BU-Sales', 'BU-Finance']:
        bu = env['ops.business.unit'].search([('name', '=', bu_name)], limit=1)
        if bu:
            bus[bu_name] = bu
            print(f"  ✓ Found {bu_name}: ID={bu.id}")
        else:
            print(f"  ✗ ERROR: Business Unit '{bu_name}' not found!")
            return None, None
    
    return branches, bus


def create_or_update_persona(env, persona_code, spec, branches, bus):
    """Create or update a persona."""
    existing = env['ops.persona'].search([('code', '=', persona_code)], limit=1)
    
    if existing:
        print(f"  → Persona {persona_code} already exists (ID: {existing.id}), updating...")
        persona = existing
    else:
        print(f"  → Creating persona {persona_code}...")
        persona = None
    
    # Prepare persona values
    vals = {
        'name': spec['name'],
        'code': persona_code,
        'description': spec['description'],
        'active': True,
    }
    
    # Add authority flags
    vals.update(spec['authorities'])
    
    # For Sales personas: assign Branch-North and BU-Sales
    # For Finance personas: assign Branch-HQ and BU-Finance
    if persona_code in ['SALES_REP', 'SALES_MGR']:
        vals['branch_ids'] = [(6, 0, [branches['Branch-North'].id])]
        vals['business_unit_ids'] = [(6, 0, [bus['BU-Sales'].id])]
        vals['default_branch_id'] = branches['Branch-North'].id
        vals['default_business_unit_id'] = bus['BU-Sales'].id
    else:  # Finance personas
        vals['branch_ids'] = [(6, 0, [branches['Branch-HQ'].id])]
        vals['business_unit_ids'] = [(6, 0, [bus['BU-Finance'].id])]
        vals['default_branch_id'] = branches['Branch-HQ'].id
        vals['default_business_unit_id'] = bus['BU-Finance'].id
    
    if persona:
        persona.write(vals)
    else:
        persona = env['ops.persona'].create(vals)
    
    print(f"  ✓ Persona {persona_code} ready: ID={persona.id}, Name='{persona.name}'")
    return persona


def create_personas(env, branches, bus):
    """Create all required personas."""
    print_header("STEP 3: Create/Update Personas")
    
    personas = {}
    for code, spec in PERSONA_SPECS.items():
        personas[code] = create_or_update_persona(env, code, spec, branches, bus)
    
    # Commit after personas
    env.cr.commit()
    print("\n  ✓ Personas committed to database")
    
    return personas


def create_or_update_user(env, login, spec, personas):
    """Create or update a user."""
    existing = env['res.users'].search([('login', '=', login)], limit=1)
    
    if existing:
        print(f"  → User {login} already exists (ID: {existing.id}), updating...")
        user = existing
    else:
        print(f"  → Creating user {login}...")
        user = None
    
    # Get persona
    persona = personas.get(spec['persona_code'])
    if not persona:
        print(f"  ✗ ERROR: Persona {spec['persona_code']} not found!")
        return None
    
    # Prepare user values
    vals = {
        'login': login,
        'name': spec['name'],
        'email': spec['email'],
        'active': True,
        'persona_id': persona.id,
    }
    
    # Only set password on creation (Odoo hashes it automatically)
    if not user:
        vals['password'] = spec['password']
    
    if user:
        user.write(vals)
    else:
        user = env['res.users'].create(vals)
    
    print(f"  ✓ User {login} ready: ID={user.id}, Persona={persona.name}")
    return user


def create_users(env, personas):
    """Create all required users."""
    print_header("STEP 4: Create/Update Users")
    
    users = {}
    for login, spec in USER_SPECS.items():
        users[login] = create_or_update_user(env, login, spec, personas)
    
    # Commit after users
    env.cr.commit()
    print("\n  ✓ Users committed to database")
    
    return users


def generate_verification_report(env):
    """Generate verification report."""
    print_header("STEP 5: Verification Report")
    
    # Verify personas
    print("\n📋 PERSONAS:")
    print("-" * 80)
    personas = env['ops.persona'].search([('code', 'in', list(PERSONA_SPECS.keys()))])
    for p in personas:
        print(f"\nPersona: {p.name} (Code: {p.code}, ID: {p.id})")
        print(f"  Branches: {', '.join(p.branch_ids.mapped('name'))}")
        print(f"  Business Units: {', '.join(p.business_unit_ids.mapped('name'))}")
        print(f"  Authorities:")
        if p.is_approver:
            print(f"    - Approver (Limit: {p.approval_limit})")
        if p.is_bu_leader:
            print(f"    - BU Leader")
        if p.can_validate_invoices:
            print(f"    - Can Validate Invoices")
        if p.can_post_journal_entries:
            print(f"    - Can Post Journal Entries")
        if p.can_execute_payments:
            print(f"    - Can Execute Payments")
        if p.can_manage_pdc:
            print(f"    - Can Manage PDC")
    
    # Verify users
    print("\n\n👥 USERS:")
    print("-" * 80)
    print(f"{'Login':<20} {'Name':<30} {'Persona':<20} {'Branch':<15} {'BU':<15}")
    print("-" * 80)
    
    for login in USER_SPECS.keys():
        user = env['res.users'].search([('login', '=', login)], limit=1)
        if user:
            persona = user.persona_id
            branch = persona.default_branch_id.name if persona.default_branch_id else 'N/A'
            bu = persona.default_business_unit_id.name if persona.default_business_unit_id else 'N/A'
            print(f"{login:<20} {user.name:<30} {persona.name:<20} {branch:<15} {bu:<15}")
        else:
            print(f"{login:<20} {'NOT FOUND':<30} {'-':<20} {'-':<15} {'-':<15}")
    
    print("\n" + "=" * 80)
    print("✅ PHASE 2B COMPLETE")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Database: mz-db")
    print(f"Personas Created: {len(personas)}")
    print(f"Users Created: {len(USER_SPECS)}")
    print("\n✓ All data committed to database")
    print("✓ Ready for Phase 3 stress tests")


def main():
    """Main execution function."""
    try:
        print_header("PHASE 2B: Create Personas and Test Users")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Database: mz-db")
        
        # Get environment
        import odoo
        from odoo import api, SUPERUSER_ID
        
        # Verify we're in Odoo shell context
        if not hasattr(odoo, 'api'):
            print("ERROR: This script must be run in Odoo shell context")
            sys.exit(1)
        
        # Use the global env from Odoo shell
        global env
        
        # Step 1: Check existing personas
        existing_personas = check_existing_personas(env)
        
        # Step 2: Look up matrix dimensions
        branches, bus = lookup_matrix_dimensions(env)
        if not branches or not bus:
            print("\n❌ ERROR: Required matrix dimensions not found!")
            print("Please ensure Branch-North, Branch-HQ, BU-Sales, and BU-Finance exist.")
            sys.exit(1)
        
        # Step 3: Create personas
        personas = create_personas(env, branches, bus)
        
        # Step 4: Create users
        users = create_users(env, personas)
        
        # Step 5: Generate verification report
        generate_verification_report(env)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
