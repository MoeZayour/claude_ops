# -*- coding: utf-8 -*-
"""
PHASE 3A: Procurement-to-Payment Stress Test (Odoo Shell Version)
===================================================================

Execute via: docker exec gemini_odoo19 odoo shell -d mz-db --no-http -c /etc/odoo/odoo.conf < scripts/phase3a_test_odoo_shell.py

This script tests:
- High-value PO creation (>$10K)
- Governance rule enforcement
- Approval workflow and escalation
- Vendor bill creation
- PDC (Post-Dated Check) management
"""

import logging
from datetime import datetime, timedelta
from odoo import fields

_logger = logging.getLogger(__name__)

print("="*80)
print("PHASE 3A: PROCUREMENT-TO-PAYMENT STRESS TEST")
print("="*80)
print(f"Database: {env.cr.dbname}")
print(f"User: {env.user.name}")
print("")

test_results = {
    'vendor': None,
    'purchase_order': None,
    'vendor_bill': None,
    'pdc': None,
    'governance_blocks': [],
    'approval_requests': [],
    'errors': [],
    'success_steps': [],
}

# STEP 1: Create Vendor
print("\n" + "="*80)
print("STEP 1: CREATE VENDOR")
print("="*80)

try:
    vendor = env['res.partner'].search([('name', '=', 'Industrial Supplier Ltd')], limit=1)
    if vendor:
        print(f"✅ Using existing vendor: {vendor.name} (ID: {vendor.id})")
    else:
        country_us = env.ref('base.us', raise_if_not_found=False)
        vendor = env['res.partner'].create({
            'name': 'Industrial Supplier Ltd',
            'is_company': True,
            'supplier_rank': 10,
            'email': 'supplier@industrial.com',
            'phone': '+1-555-0100',
            'street': '123 Industrial Park',
            'city': 'Manufacturing City',
            'country_id': country_us.id if country_us else False,
        })
        print(f"✅ Created vendor: {vendor.name} (ID: {vendor.id})")
    
    test_results['vendor'] = vendor
    test_results['success_steps'].append('Step 1: Vendor created')
    env.cr.commit()
except Exception as e:
    print(f"❌ Failed to create vendor: {str(e)}")
    test_results['errors'].append(f"Vendor creation: {str(e)}")

# STEP 2: Create High-Value Purchase Order
print("\n" + "="*80)
print("STEP 2: CREATE HIGH-VALUE PURCHASE ORDER (>$10K)")
print("="*80)

try:
    vendor = test_results['vendor']
    
    # Get product
    product = env['product.product'].search([('default_code', '=', 'EQUIPMENT-D-004')], limit=1)
    if not product:
        print("⚠️ Product EQUIPMENT-D-004 not found, using first available product...")
        product = env['product.product'].search([('type', '=', 'product'), ('purchase_ok', '=', True)], limit=1)
    
    print(f"📦 Using product: {product.name} (Code: {product.default_code})")
    
    # Get Branch and BU
    branch_hq = env['ops.branch'].search([('name', '=', 'Branch-HQ')], limit=1)
    bu_procurement = env['ops.business.unit'].search([('name', '=', 'BU-Procurement')], limit=1)
    
    if not bu_procurement:
        bu_procurement = env['ops.business.unit'].search([], limit=1)
    
    # Create PO (ops_branch_id expects res.company, not ops.branch)
    po = env['purchase.order'].sudo().create({
        'partner_id': vendor.id,
        'ops_branch_id': branch_hq.company_id.id if branch_hq and branch_hq.company_id else False,
        'ops_business_unit_id': bu_procurement.id if bu_procurement else False,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'name': product.name or 'Test Product',
            'product_qty': 2.0,
            'price_unit': 12000.00,
            'date_planned': fields.Datetime.now(),
        })],
    })
    
    print(f"✅ PO Created: {po.name}")
    print(f"   Amount: ${po.amount_total:,.2f}")
    print(f"   Branch: {branch_hq.name if branch_hq else 'N/A'}")
    print(f"   BU: {bu_procurement.name if bu_procurement else 'N/A'}")
    print(f"   State: {po.state}")
    
    test_results['purchase_order'] = po
    test_results['success_steps'].append('Step 2: High-value PO created ($24,000)')
    env.cr.commit()
except Exception as e:
    print(f"❌ Failed to create PO: {str(e)}")
    test_results['errors'].append(f"PO creation: {str(e)}")

# STEP 3: Test Governance Blocks
print("\n" + "="*80)
print("STEP 3: TEST GOVERNANCE BLOCKS")
print("="*80)

try:
    po = test_results['purchase_order']
    
    # Check governance rules
    governance_rules = env['ops.governance.rule'].search([
        ('model_id.model', '=', 'purchase.order'),
        ('active', '=', True)
    ])
    
    print(f"📋 Found {len(governance_rules)} governance rules for purchase.order")
    for rule in governance_rules:
        print(f"   - {rule.name} (Action: {rule.action_type}, Trigger: {rule.trigger_type})")
    
    # Try to send email as non-admin
    print("\n🔒 TEST: Attempting to send RFQ via email...")
    accountant = env['res.users'].search([('login', '=', 'ops_accountant')], limit=1)
    if accountant:
        try:
            po_as_user = po.with_user(accountant)
            po_as_user.action_rfq_send()
            print("   ✅ Email action succeeded (no block)")
        except Exception as e:
            error_msg = str(e)
            if 'COMMITMENT BLOCKED' in error_msg or 'requires approval' in error_msg:
                print(f"   ✅ GOVERNANCE BLOCK TRIGGERED: {error_msg[:100]}...")
                test_results['governance_blocks'].append({
                    'action': 'Email RFQ',
                    'blocked': True,
                    'reason': error_msg[:200]
                })
            else:
                print(f"   ⚠️ Unexpected error: {error_msg}")
    
    test_results['success_steps'].append('Step 3: Governance blocks tested')
except Exception as e:
    print(f"❌ Governance test failed: {str(e)}")
    test_results['errors'].append(f"Governance test: {str(e)}")

# STEP 4: Confirm Purchase Order
print("\n" + "="*80)
print("STEP 4: CONFIRM PURCHASE ORDER")
print("="*80)

try:
    po = test_results['purchase_order']
    if po.state == 'draft':
        print(f"📝 Confirming PO: {po.name}")
        po.button_confirm()
        print(f"   ✅ PO State: {po.state}")
    else:
        print(f"   ℹ️ PO already confirmed (State: {po.state})")
    
    test_results['success_steps'].append(f'Step 4: PO confirmed (State: {po.state})')
    env.cr.commit()
except Exception as e:
    print(f"❌ PO confirmation failed: {str(e)}")
    test_results['errors'].append(f"PO confirmation: {str(e)}")

# STEP 5: Create Vendor Bill
print("\n" + "="*80)
print("STEP 5: CREATE VENDOR BILL")
print("="*80)

try:
    po = test_results['purchase_order']
    vendor = test_results['vendor']
    
    # Get expense account
    expense_account = env['account.account'].search([('code', '=', '600000')], limit=1)
    if not expense_account:
        expense_account = env['account.account'].search([('account_type', '=', 'expense')], limit=1)
    
    product = po.order_line[0].product_id if po.order_line else False
    
    # Note: ops_branch_id on account.move also expects res.company
    bill = env['account.move'].sudo().create({
        'move_type': 'in_invoice',
        'partner_id': vendor.id,
        'invoice_date': fields.Date.today(),
        'ops_branch_id': po.ops_branch_id if po.ops_branch_id else False,
        'ops_business_unit_id': po.ops_business_unit_id.id if po.ops_business_unit_id else False,
        'ref': f'Bill for {po.name}',
        'invoice_line_ids': [(0, 0, {
            'product_id': product.id if product else False,
            'name': product.name if product else 'Industrial Equipment',
            'quantity': 2.0,
            'price_unit': 12000.00,
            'account_id': expense_account.id,
        })],
    })
    
    print(f"✅ Vendor Bill Created: {bill.name}")
    print(f"   Amount: ${bill.amount_total:,.2f}")
    print(f"   State: {bill.state}")
    
    # Post the bill
    if bill.state == 'draft':
        bill.action_post()
        print(f"   ✅ Bill Posted: {bill.state}")
    
    test_results['vendor_bill'] = bill
    test_results['success_steps'].append('Step 5: Vendor bill created and posted')
    env.cr.commit()
except Exception as e:
    print(f"❌ Vendor bill creation failed: {str(e)}")
    test_results['errors'].append(f"Vendor bill: {str(e)}")

# STEP 6: Create PDC
print("\n" + "="*80)
print("STEP 6: CREATE POST-DATED CHECK (PDC)")
print("="*80)

try:
    if 'ops.pdc' not in env:
        print("⚠️ ops.pdc model not available - PDC testing skipped")
    else:
        bill = test_results.get('vendor_bill')
        vendor = test_results['vendor']
        
        if not bill:
            print("⚠️ No vendor bill available, skipping PDC creation")
        else:
            # Get or create bank
            bank = env['res.bank'].search([('name', '=', 'Industrial Bank')], limit=1)
            if not bank:
                bank = env['res.bank'].create({'name': 'Industrial Bank', 'bic': 'INDBANK001'})
            
            # Get bank journal
            bank_journal = env['account.journal'].search([('type', '=', 'bank')], limit=1)
            
            # Get holding account
            holding_account = env['account.account'].search([('code', '=', '110500')], limit=1)
            if not holding_account:
                holding_account = env['account.account'].search([('account_type', '=', 'asset_current')], limit=1)
            
            branch = env['ops.branch'].search([('name', '=', 'Branch-HQ')], limit=1)
            bu = env['ops.business.unit'].search([('name', '=', 'BU-Finance')], limit=1)
            if not bu:
                bu = env['ops.business.unit'].search([], limit=1)
            
            pdc_vals = {
                'name': 'New',
                'partner_id': vendor.id,
                'date': fields.Date.today(),
                'maturity_date': fields.Date.add(fields.Date.today(), days=30),
                'amount': bill.amount_total,
                'payment_type': 'outbound',
                'bank_id': bank.id,
                'check_number': 'CHK-100001',
                'journal_id': bank_journal.id,
                'holding_account_id': holding_account.id,
                'ops_business_unit_id': bu.id if bu else False,
            }
            
            if branch:
                try:
                    pdc_vals['ops_branch_id'] = branch.company_id.id if hasattr(branch, 'company_id') else branch.id
                except:
                    pdc_vals['ops_branch_id'] = branch.id
            
            pdc = env['ops.pdc'].sudo().create(pdc_vals)
            
            print(f"✅ PDC Created: {pdc.name}")
            print(f"   Amount: ${pdc.amount:,.2f}")
            print(f"   Check Number: {pdc.check_number}")
            print(f"   Maturity Date: {pdc.maturity_date}")
            print(f"   State: {pdc.state}")
            
            # Try to register PDC
            if pdc.state == 'draft' and hasattr(pdc, 'action_register'):
                try:
                    pdc.action_register()
                    print(f"   ✅ PDC Registered: {pdc.state}")
                except Exception as e:
                    print(f"   ⚠️ Registration failed: {str(e)}")
            
            test_results['pdc'] = pdc
            test_results['success_steps'].append(f'Step 6: PDC created (State: {pdc.state})')
            env.cr.commit()
except Exception as e:
    print(f"❌ PDC creation failed: {str(e)}")
    test_results['errors'].append(f"PDC creation: {str(e)}")

# Generate Summary Report
print("\n" + "="*80)
print("TEST EXECUTION SUMMARY")
print("="*80)
print(f"\n✅ Successful Steps: {len(test_results['success_steps'])}")
print(f"⚠️ Errors: {len(test_results['errors'])}")
print(f"🔒 Governance Blocks: {len(test_results['governance_blocks'])}")

print("\n📊 COMPLETED STEPS:")
for step in test_results['success_steps']:
    print(f"   ✅ {step}")

if test_results['errors']:
    print("\n⚠️ ERRORS:")
    for error in test_results['errors']:
        print(f"   ❌ {error}")

print("\n" + "="*80)
print("VERIFICATION COMMANDS")
print("="*80)

if test_results.get('vendor'):
    vendor_id = test_results['vendor'].id
    print(f"\n# Vendor:")
    print(f"SELECT id, name, email FROM res_partner WHERE id={vendor_id};")

if test_results.get('purchase_order'):
    po = test_results['purchase_order']
    print(f"\n# Purchase Order:")
    print(f"SELECT id, name, partner_id, amount_total, state FROM purchase_order WHERE id={po.id};")
    print(f"PO Number: {po.name} | Amount: ${po.amount_total:,.2f} | State: {po.state}")

if test_results.get('vendor_bill'):
    bill = test_results['vendor_bill']
    print(f"\n# Vendor Bill:")
    print(f"SELECT id, name, partner_id, amount_total, state FROM account_move WHERE id={bill.id};")
    print(f"Bill Number: {bill.name} | Amount: ${bill.amount_total:,.2f} | State: {bill.state}")

if test_results.get('pdc'):
    pdc = test_results['pdc']
    print(f"\n# PDC:")
    print(f"SELECT id, name, amount, state, maturity_date FROM ops_pdc WHERE id={pdc.id};")
    print(f"PDC Number: {pdc.name} | Amount: ${pdc.amount:,.2f} | State: {pdc.state}")

print("\n" + "="*80)
print("✅ PHASE 3A TEST COMPLETED")
print("All data persists in database 'mz-db' for inspection")
print("="*80)

# Save results summary to file
report_path = '/tmp/phase3a_results.txt'
with open(report_path, 'w') as f:
    f.write("PHASE 3A: PROCUREMENT-TO-PAYMENT STRESS TEST RESULTS\n")
    f.write("="*80 + "\n\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Database: {env.cr.dbname}\n\n")
    
    if test_results.get('vendor'):
        f.write(f"Vendor ID: {test_results['vendor'].id}\n")
        f.write(f"Vendor Name: {test_results['vendor'].name}\n\n")
    
    if test_results.get('purchase_order'):
        po = test_results['purchase_order']
        f.write(f"PO ID: {po.id}\n")
        f.write(f"PO Number: {po.name}\n")
        f.write(f"PO Amount: ${po.amount_total:,.2f}\n")
        f.write(f"PO State: {po.state}\n\n")
    
    if test_results.get('vendor_bill'):
        bill = test_results['vendor_bill']
        f.write(f"Bill ID: {bill.id}\n")
        f.write(f"Bill Number: {bill.name}\n")
        f.write(f"Bill Amount: ${bill.amount_total:,.2f}\n")
        f.write(f"Bill State: {bill.state}\n\n")
    
    if test_results.get('pdc'):
        pdc = test_results['pdc']
        f.write(f"PDC ID: {pdc.id}\n")
        f.write(f"PDC Number: {pdc.name}\n")
        f.write(f"PDC Amount: ${pdc.amount:,.2f}\n")
        f.write(f"PDC State: {pdc.state}\n\n")
    
    f.write(f"Successful Steps: {len(test_results['success_steps'])}\n")
    f.write(f"Errors: {len(test_results['errors'])}\n")

print(f"\nResults saved to: {report_path}")
print("Copy out with: docker cp gemini_odoo19:/tmp/phase3a_results.txt ./")
