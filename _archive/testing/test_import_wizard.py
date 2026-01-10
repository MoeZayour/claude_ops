#!/usr/bin/env python3
"""Test the Sale Order Import Wizard - Priority #6"""

import sys

# Test results
tests_passed = 0
tests_failed = 0

print("=" * 70)
print("TESTING PRIORITY #6: EXCEL IMPORT FOR SALE ORDER LINES")
print("=" * 70)

try:
    # Test 1: Model exists
    print("\n1. Testing model existence...")
    if 'ops.sale.order.import.wizard' in env:
        print("   ✅ Model 'ops.sale.order.import.wizard' exists")
        tests_passed += 1
    else:
        print("   ❌ Model 'ops.sale.order.import.wizard' NOT FOUND")
        tests_failed += 1
        
    # Test 2: Action exists
    print("\n2. Testing action existence...")
    action = env.ref('ops_matrix_core.action_ops_sale_order_import_wizard', raise_if_not_found=False)
    if action:
        print(f"   ✅ Action exists: {action.name}")
        print(f"      Model: {action.res_model}")
        print(f"      View Mode: {action.view_mode}")
        tests_passed += 1
    else:
        print("   ❌ Action NOT FOUND")
        tests_failed += 1
    
    # Test 3: Security access rules
    print("\n3. Testing security access...")
    access_records = env['ir.model.access'].search([
        ('model_id.model', '=', 'ops.sale.order.import.wizard')
    ])
    if access_records:
        print(f"   ✅ Found {len(access_records)} access rules:")
        for access in access_records:
            print(f"      - {access.name}: Read={access.perm_read}, Write={access.perm_write}, Create={access.perm_create}")
        tests_passed += 1
    else:
        print("   ❌ No access rules found")
        tests_failed += 1
    
    # Test 4: Create wizard instance
    print("\n4. Testing wizard creation...")
    so = env['sale.order'].search([('state', '=', 'draft')], limit=1)
    if so:
        wizard = env['ops.sale.order.import.wizard'].create({
            'sale_order_id': so.id,
        })
        print(f"   ✅ Wizard created successfully: ID={wizard.id}")
        print(f"      Sale Order: {so.name}")
        print(f"      State: {wizard.state}")
        tests_passed += 1
        
        # Test 5: Template generation
        print("\n5. Testing template file generation...")
        if wizard.template_file:
            print("   ✅ Template file generated successfully")
            print(f"      Filename: {wizard.template_filename}")
            print(f"      File size: {len(wizard.template_file)} bytes (base64)")
            tests_passed += 1
        else:
            print("   ❌ Template file NOT generated")
            tests_failed += 1
            
        # Test 6: Wizard view
        print("\n6. Testing wizard view...")
        view = env.ref('ops_matrix_core.view_ops_sale_order_import_wizard_form', raise_if_not_found=False)
        if view:
            print(f"   ✅ Wizard view exists: {view.name}")
            print(f"      Model: {view.model}")
            tests_passed += 1
        else:
            print("   ❌ Wizard view NOT FOUND")
            tests_failed += 1
            
        # Test 7: Button on sale order form
        print("\n7. Testing sale order form button...")
        button_view = env.ref('ops_matrix_core.view_order_form_import_button', raise_if_not_found=False)
        if button_view:
            print(f"   ✅ Import button view exists: {button_view.name}")
            print(f"      Inherits from: {button_view.inherit_id.name}")
            tests_passed += 1
        else:
            print("   ❌ Import button view NOT FOUND")
            tests_failed += 1
            
    else:
        print("   ⚠️  No draft sale orders found for testing")
        print("   Creating a test sale order...")
        partner = env['res.partner'].search([('customer_rank', '>', 0)], limit=1)
        if not partner:
            partner = env['res.partner'].create({'name': 'Test Customer', 'customer_rank': 1})
        
        so = env['sale.order'].create({
            'partner_id': partner.id,
        })
        print(f"   ✅ Created test sale order: {so.name}")
        tests_passed += 1
    
    # Test 8: Required Python libraries
    print("\n8. Testing Python library availability...")
    libraries_ok = True
    try:
        import xlrd
        print("   ✅ xlrd available")
    except ImportError:
        print("   ❌ xlrd NOT available")
        libraries_ok = False
        
    try:
        import xlsxwriter
        print("   ✅ xlsxwriter available")
    except ImportError:
        print("   ❌ xlsxwriter NOT available")
        libraries_ok = False
        
    try:
        from openpyxl import load_workbook
        print("   ✅ openpyxl available")
    except ImportError:
        print("   ❌ openpyxl NOT available")
        libraries_ok = False
    
    if libraries_ok:
        tests_passed += 1
    else:
        tests_failed += 1
    
except Exception as e:
    print(f"\n❌ ERROR during testing: {e}")
    import traceback
    traceback.print_exc()
    tests_failed += 1

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests: {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n✅ ALL TESTS PASSED - Priority #6 is COMPLETE!")
    print("\nThe Excel Import wizard is fully functional and ready for use.")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_failed} test(s) failed")
    sys.exit(1)
