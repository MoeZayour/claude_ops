#!/usr/bin/env python3
"""
Manual test script for ops.branch creation
Run with: docker exec gemini_odoo19 python3 /mnt/extra-addons/../../test_branch_manual.py
"""
import sys
import os

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID

def test_branch_creation():
    print("\n" + "="*70)
    print("TESTING: ops.branch Auto-Code Generation")
    print("="*70)
    
    # Connect to database
    db_name = 'mz-db'
    
    try:
        # Get registry and environment
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Test 1: Check if sequence exists
            print("\n[Test 1] Checking if ir.sequence exists...")
            sequence = env['ir.sequence'].search([('code', '=', 'ops.branch')])
            if sequence:
                print(f"✅ PASS: Sequence exists")
                print(f"   Name: {sequence.name}")
                print(f"   Code: {sequence.code}")
                print(f"   Prefix: {sequence.prefix}")
                print(f"   Next Number: {sequence.number_next}")
            else:
                print("❌ FAIL: Sequence 'ops.branch' not found!")
                return False
            
            # Test 2: Create a branch
            print("\n[Test 2] Creating a new branch...")
            Branch = env['ops.branch']
            
            # Get or create a company
            company = env['res.company'].search([], limit=1)
            if not company:
                print("❌ FAIL: No company found in database")
                return False
            
            branch = Branch.create({
                'name': 'Test Branch Auto',
                'company_id': company.id,
            })
            
            print(f"✅ PASS: Branch created with ID: {branch.id}")
            print(f"   Name: {branch.name}")
            print(f"   Code: {branch.code}")
            
            # Test 3: Verify code is not 'New'
            print("\n[Test 3] Verifying code auto-generation...")
            if branch.code == 'New':
                print(f"❌ FAIL: Code is still 'New'! Auto-generation failed.")
                return False
            elif branch.code.startswith('BR'):
                print(f"✅ PASS: Code auto-generated successfully: {branch.code}")
            else:
                print(f"⚠️  WARNING: Code generated but doesn't start with 'BR': {branch.code}")
            
            # Test 4: Create another branch to test sequence increment
            print("\n[Test 4] Testing sequence increment...")
            branch2 = Branch.create({
                'name': 'Test Branch Auto 2',
                'company_id': company.id,
            })
            
            if branch2.code != 'New' and branch.code != branch2.code:
                print(f"✅ PASS: Second branch has unique code: {branch2.code}")
            else:
                print(f"❌ FAIL: Code uniqueness issue!")
                print(f"   Branch 1: {branch.code}")
                print(f"   Branch 2: {branch2.code}")
                return False
            
            # Rollback to not pollute the database
            cr.rollback()
            
            print("\n" + "="*70)
            print("ALL TESTS PASSED! ✅")
            print("="*70 + "\n")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_branch_creation()
    sys.exit(0 if success else 1)
