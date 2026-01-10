#!/usr/bin/env python3
"""Comprehensive OPS Framework Testing Script"""
import sys

def test_menu(env, menu_name_pattern, expected_model=None):
    """Test a single menu"""
    try:
        # Find menu
        menu = env['ir.ui.menu'].search([
            ('name', 'ilike', menu_name_pattern),
            ('active', '=', True)
        ], limit=1)
        
        if not menu:
            print(f"❌ MENU NOT FOUND: {menu_name_pattern}")
            return False
        
        print(f"✅ Menu: {menu.name} (ID: {menu.id})")
        
        # Check action
        if not menu.action:
            print(f"   ⚠️  No action linked")
            return True
        
        action_ref = menu.action
        action_type = action_ref.split(',')[0]
        action_id = int(action_ref.split(',')[1])
        
        if action_type == 'ir.actions.act_window':
            action = env['ir.actions.act_window'].browse(action_id)
            print(f"   ✅ Action: {action.name}")
            print(f"   ✅ Model: {action.res_model}")
            
            # Check model exists
            if action.res_model not in env:
                print(f"   ❌ MODEL NOT FOUND: {action.res_model}")
                return False
            
            # Check views
            if action.view_id:
                print(f"   ✅ View: {action.view_id.name}")
            else:
                # Check if any views exist for model
                views = env['ir.ui.view'].search([
                    ('model', '=', action.res_model)
                ], limit=1)
                if views:
                    print(f"   ✅ Views available for model")
                else:
                    print(f"   ❌ NO VIEWS for {action.res_model}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing {menu_name_pattern}: {str(e)}")
        return False

# Main execution
env = self.env
results = {}

print("=" * 60)
print("OPS FRAMEWORK COMPREHENSIVE TESTING")
print("=" * 60)

# Priority 1: Security Critical
print("\n🔴 PRIORITY 1: SECURITY CRITICAL")
print("-" * 60)
results['excel_export'] = test_menu(env, 'Excel Export', 'ops.excel.export.wizard')

# Priority 2: Asset Management
print("\n🔴 PRIORITY 2: ASSET MANAGEMENT")
print("-" * 60)
results['asset_categories'] = test_menu(env, 'Asset Categor')
results['depreciation_lines'] = test_menu(env, 'Depreciation Line')
results['assets'] = test_menu(env, 'Assets')

# Priority 3: Reports
print("\n🟡 PRIORITY 3: REPORTS")
print("-" * 60)
results['three_way_match'] = test_menu(env, 'Three-Way Match')
results['budget_reports'] = test_menu(env, 'Budget')
results['general_ledger'] = test_menu(env, 'General Ledger')
results['asset_register'] = test_menu(env, 'Asset Register')

# Priority 4: Wizards
print("\n🟡 PRIORITY 4: WIZARDS")
print("-" * 60)
results['import_wizard'] = test_menu(env, 'Import')

# Priority 5: Core Features
print("\n🟢 PRIORITY 5: CORE FEATURES")
print("-" * 60)
results['pdc'] = test_menu(env, 'Post-Dated')

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

passed = sum(1 for v in results.values() if v)
total = len(results)
percentage = (passed / total * 100) if total > 0 else 0

print(f"\nPassed: {passed}/{total} ({percentage:.0f}%)")
print("\nDetailed Results:")
for name, result in results.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status}: {name}")

# Model Functionality Tests
print("\n" + "=" * 60)
print("MODEL FUNCTIONALITY TESTS")
print("=" * 60)

# Test Excel Export Wizard
print("\n1. Excel Export Wizard Model")
try:
    if 'ops.excel.export.wizard' in env:
        print("   ✅ Model exists")
        wizard = env['ops.excel.export.wizard'].create({
            'report_type': 'products',
        })
        print(f"   ✅ Wizard created: ID {wizard.id}")
        
        # Check methods
        methods = ['action_generate_excel', '_get_secure_domain', '_get_visible_fields']
        for method in methods:
            if hasattr(wizard, method):
                print(f"   ✅ Method {method} exists")
            else:
                print(f"   ❌ Method {method} MISSING")
    else:
        print("   ❌ Model NOT FOUND")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test Asset Category
print("\n2. Asset Category Model")
try:
    if 'ops.asset.category' in env:
        print("   ✅ Model exists")
        category = env['ops.asset.category'].create({
            'name': 'Test Category',
            'code': 'TEST',
        })
        print(f"   ✅ Category created: {category.name}")
        category.unlink()
        print("   ✅ CRUD operations work")
    else:
        print("   ❌ Model NOT FOUND")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test Asset Model
print("\n3. Asset Model")
try:
    if 'ops.asset' in env:
        print("   ✅ Model exists")
        required_fields = ['name', 'acquisition_value', 'book_value', 'fully_depreciated']
        for field in required_fields:
            if field in env['ops.asset']._fields:
                print(f"   ✅ Field {field} exists")
            else:
                print(f"   ❌ Field {field} MISSING")
    else:
        print("   ❌ Model NOT FOUND")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)

if passed == total:
    print("\n✅ ALL MENU TESTS PASSED!")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} menu tests failed")
    sys.exit(1)
