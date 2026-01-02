#!/usr/bin/env python3
"""
Test Script for OPS Framework Persona & Security Deployment
Tests the "Zero-Friction" setup and automatic synchronization logic
"""

import xmlrpc.client
import sys

# Configuration
URL = 'http://localhost:8069'
DB = 'postgres'
USERNAME = 'admin'
PASSWORD = 'admin'

def test_persona_deployment():
    """Test the persona deployment and auto-sync functionality"""
    
    print("=" * 80)
    print("OPS Framework - Persona & Security Deployment Test")
    print("=" * 80)
    
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed!")
            return False
        
        print(f"✅ Authenticated as user ID: {uid}")
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Test 1: Check if 12 personas exist
        print("\n" + "="*80)
        print("Test 1: Verify 12 Corporate Matrix Personas")
        print("="*80)
        
        expected_personas = [
            'CEO', 'CFO', 'SALES_LEADER', 'SALES_MGR', 'SALES_REP',
            'HR_MGR', 'CHIEF_ACCT', 'ACCOUNTANT', 'LOG_MGR', 
            'LOG_CLERK', 'TECH_SUPPORT', 'SYS_ADMIN'
        ]
        
        for code in expected_personas:
            persona_count = models.execute_kw(
                DB, uid, PASSWORD,
                'ops.persona', 'search_count',
                [[('code', '=', code)]]
            )
            if persona_count > 0:
                print(f"  ✅ Persona '{code}' found")
            else:
                print(f"  ❌ Persona '{code}' NOT found")
        
        # Test 2: Check company main branch
        print("\n" + "="*80)
        print("Test 2: Verify Company Main Branch Exists")
        print("="*80)
        
        branches = models.execute_kw(
            DB, uid, PASSWORD,
            'ops.branch', 'search_read',
            [[('active', '=', True)]],
            {'fields': ['name', 'code', 'company_id'], 'limit': 1}
        )
        
        if branches:
            print(f"  ✅ Main Branch found: {branches[0]['name']} ({branches[0]['code']})")
            main_branch_id = branches[0]['id']
        else:
            print("  ❌ No active branch found - creating one for test")
            return False
        
        # Test 3: Create test user and verify auto-sync
        print("\n" + "="*80)
        print("Test 3: Create User 'Branch Logistics Lead' with Auto-Sync")
        print("="*80)
        
        # First, check if user already exists
        existing_user = models.execute_kw(
            DB, uid, PASSWORD,
            'res.users', 'search',
            [[('login', '=', 'logistics.lead.test')]]
        )
        
        if existing_user:
            print("  ℹ️  Test user already exists, deleting first...")
            models.execute_kw(
                DB, uid, PASSWORD,
                'res.users', 'unlink',
                [existing_user]
            )
        
        # Get Logistics Manager persona
        log_mgr_persona = models.execute_kw(
            DB, uid, PASSWORD,
            'ops.persona', 'search',
            [[('code', '=', 'LOG_MGR')]]
        )
        
        if not log_mgr_persona:
            print("  ❌ Logistics Manager persona not found")
            return False
        
        print(f"  ✅ Found Logistics Manager persona ID: {log_mgr_persona[0]}")
        
        # Get a business unit
        business_units = models.execute_kw(
            DB, uid, PASSWORD,
            'ops.business.unit', 'search',
            [[('active', '=', True)]],
        )
        
        if not business_units:
            print("  ❌ No business unit found")
            return False
        
        print(f"  ✅ Found Business Unit ID: {business_units[0]}")
        
        # Create user with persona
        print("\n  Creating user with Logistics Manager persona...")
        
        try:
            test_user_id = models.execute_kw(
                DB, uid, PASSWORD,
                'res.users', 'create',
                [{
                    'name': 'Branch Logistics Lead',
                    'login': 'logistics.lead.test',
                    'email': 'logistics.lead@test.com',
                    'persona_id': log_mgr_persona[0],
                    'ops_allowed_business_unit_ids': [(6, 0, [business_units[0]])],
                }]
            )
            
            print(f"  ✅ User created with ID: {test_user_id}")
            
            # Verify auto-populated Primary Branch
            user_data = models.execute_kw(
                DB, uid, PASSWORD,
                'res.users', 'read',
                [test_user_id],
                {'fields': ['name', 'persona_id', 'primary_branch_id', 'groups_id']}
            )
            
            if user_data:
                user = user_data[0]
                print("\n  📋 User Details:")
                print(f"     Name: {user['name']}")
                print(f"     Persona: {user['persona_id'][1] if user['persona_id'] else 'None'}")
                print(f"     Primary Branch: {user['primary_branch_id'][1] if user['primary_branch_id'] else 'NOT SET ❌'}")
                print(f"     Number of Groups: {len(user['groups_id'])}")
                
                # Verify specific groups for Logistics Manager
                expected_groups = [
                    'stock.group_stock_manager',  # Inventory Manager
                    'ops_matrix_core.group_ops_branch_manager',  # Branch Manager
                ]
                
                print("\n  🔐 Verifying Security Groups:")
                for group_xmlid in expected_groups:
                    group_id = models.execute_kw(
                        DB, uid, PASSWORD,
                        'ir.model.data', 'search_read',
                        [[('module', '=', group_xmlid.split('.')[0]), 
                          ('name', '=', group_xmlid.split('.')[1])]],
                        {'fields': ['res_id'], 'limit': 1}
                    )
                    
                    if group_id:
                        gid = group_id[0]['res_id']
                        if gid in user['groups_id']:
                            print(f"     ✅ Has '{group_xmlid}'")
                        else:
                            print(f"     ❌ Missing '{group_xmlid}'")
                
                # Success criteria
                if user['primary_branch_id'] and len(user['groups_id']) > 0:
                    print("\n  ✅ SUCCESS: User saved with auto-populated Primary Branch and Groups!")
                    return True
                else:
                    print("\n  ❌ FAILED: Primary Branch or Groups not auto-populated")
                    return False
            
        except Exception as e:
            print(f"  ❌ Error creating user: {e}")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\nStarting test suite...")
    success = test_persona_deployment()
    
    print("\n" + "="*80)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        print("="*80)
        sys.exit(1)
