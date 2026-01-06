#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORRECTED OPS FRAMEWORK DATA SEEDING SCRIPT
Fixed relationship: Business Units -> Branches (not the other way around)
"""

import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

def seed_comprehensive_data():
    """Create comprehensive test data for OPS Framework."""
    
    print("=" * 80)
    print("CORRECTED OPS FRAMEWORK DATA SEEDING")
    print("=" * 80)
    
    try:
        # Phase 1: Create Branches FIRST (without business_unit_id)
        print("\n[PHASE 1] Creating Branches...")
        Branch = env['ops.branch']
        
        branch_hq = Branch.create({
            'name': 'Headquarters',
            'code': 'BR-HQ',
            'is_headquarters': True,
            'address': '123 Main Street, Downtown, City 12345',
            'phone': '+1-555-0001',
            'email': 'hq@matrix.com',
        })
        
        branch_north = Branch.create({
            'name': 'North Branch',
            'code': 'BR-NORTH',
            'address': '456 North Ave, Uptown, City 12346',
            'phone': '+1-555-0002',
            'email': 'north@matrix.com',
        })
        
        print(f"✓ Branches: {branch_hq.name}, {branch_north.name}")
        
        # Phase 2: Create Business Units WITH branch_ids
        print("\n[PHASE 2] Creating Business Units...")
        BU = env['ops.business.unit']
        
        bu_retail = BU.create({
            'name': 'Retail Division',
            'code': 'BU-RETAIL',
            'branch_ids': [(6, 0, [branch_hq.id, branch_north.id])],
            'primary_branch_id': branch_hq.id,
        })
        
        bu_wholesale = BU.create({
            'name': 'Wholesale Division',
            'code': 'BU-WHOLESALE',
            'branch_ids': [(6, 0, [branch_hq.id])],
            'primary_branch_id': branch_hq.id,
        })
        
        print(f"✓ BUs: {bu_retail.name}, {bu_wholesale.name}")
        
        # Phase 3: Create Customers
        print("\n[PHASE 3] Creating Customers...")
        Partner = env['res.partner']
        
        customer1 = Partner.create({
            'name': 'Acme Corporation',
            'customer_rank': 1,
            'email': 'contact@acme.com',
            'phone': '+1-555-1001',
        })
        
        customer2 = Partner.create({
            'name': 'TechStart Inc',
            'customer_rank': 1,
            'email': 'info@techstart.com',
            'phone': '+1-555-1002',
        })
        
        customer3 = Partner.create({
            'name': 'Global Solutions Ltd',
            'customer_rank': 1,
            'email': 'sales@globalsolutions.com',
            'phone': '+1-555-1003',
        })
        
        print(f"✓ Customers: {customer1.name}, {customer2.name}, {customer3.name}")
        
        # Phase 4: Create Vendors
        print("\n[PHASE 4] Creating Vendors...")
        
        vendor1 = Partner.create({
            'name': 'ElectroSupply Co',
            'supplier_rank': 1,
            'email': 'orders@electrosupply.com',
            'phone': '+1-555-2001',
        })
        
        vendor2 = Partner.create({
            'name': 'Components Direct',
            'supplier_rank': 1,
            'email': 'sales@componentsdirect.com',
            'phone': '+1-555-2002',
        })
        
        print(f"✓ Vendors: {vendor1.name}, {vendor2.name}")
        
        # Phase 5: Create Products
        print("\n[PHASE 5] Creating Products...")
        Product = env['product.product']
        
        laptop = Product.create({
            'name': 'Business Laptop Pro',
            'default_code': 'LAP-001',
            'list_price': 1200.00,
            'standard_price': 800.00,
        })
        
        mouse = Product.create({
            'name': 'Wireless Mouse',
            'default_code': 'MSE-001',
            'list_price': 25.00,
            'standard_price': 15.00,
        })
        
        keyboard = Product.create({
            'name': 'Mechanical Keyboard',
            'default_code': 'KEY-001',
            'list_price': 80.00,
            'standard_price': 50.00,
        })
        
        monitor = Product.create({
            'name': '27" 4K Monitor',
            'default_code': 'MON-001',
            'list_price': 450.00,
            'standard_price': 300.00,
        })
        
        headset = Product.create({
            'name': 'Noise-Cancelling Headset',
            'default_code': 'HDS-001',
            'list_price': 120.00,
            'standard_price': 70.00,
        })
        
        print(f"✓ Products: {laptop.name}, {mouse.name}, {keyboard.name}, {monitor.name}, {headset.name}")
        
        # Phase 6: Create Sales Orders
        print("\n[PHASE 6] Creating Sales Orders...")
        SaleOrder = env['sale.order']
        
        so1 = SaleOrder.create({
            'partner_id': customer1.id,
            'ops_branch_id': branch_hq.id,
            'ops_business_unit_id': bu_retail.id,
            'order_line': [
                (0, 0, {
                    'product_id': laptop.id,
                    'product_uom_qty': 5,
                    'price_unit': laptop.list_price,
                }),
                (0, 0, {
                    'product_id': mouse.id,
                    'product_uom_qty': 5,
                    'price_unit': mouse.list_price,
                }),
            ],
        })
        
        so2 = SaleOrder.create({
            'partner_id': customer2.id,
            'ops_branch_id': branch_north.id,
            'ops_business_unit_id': bu_retail.id,
            'order_line': [
                (0, 0, {
                    'product_id': monitor.id,
                    'product_uom_qty': 10,
                    'price_unit': monitor.list_price,
                }),
            ],
        })
        
        so3 = SaleOrder.create({
            'partner_id': customer3.id,
            'ops_branch_id': branch_hq.id,
            'ops_business_unit_id': bu_wholesale.id,
            'order_line': [
                (0, 0, {
                    'product_id': laptop.id,
                    'product_uom_qty': 20,
                    'price_unit': laptop.list_price * 0.9,  # Wholesale discount
                }),
                (0, 0, {
                    'product_id': keyboard.id,
                    'product_uom_qty': 20,
                    'price_unit': keyboard.list_price * 0.9,
                }),
            ],
        })
        
        print(f"✓ Sales Orders: SO-{so1.id}, SO-{so2.id}, SO-{so3.id}")
        
        # Phase 7: Create Purchase Orders
        print("\n[PHASE 7] Creating Purchase Orders...")
        PurchaseOrder = env['purchase.order']
        
        po1 = PurchaseOrder.create({
            'partner_id': vendor1.id,
            'ops_branch_id': branch_hq.id,
            'ops_business_unit_id': bu_retail.id,
            'order_line': [
                (0, 0, {
                    'product_id': laptop.id,
                    'product_qty': 50,
                    'price_unit': laptop.standard_price,
                }),
            ],
        })
        
        po2 = PurchaseOrder.create({
            'partner_id': vendor2.id,
            'ops_branch_id': branch_north.id,
            'ops_business_unit_id': bu_retail.id,
            'order_line': [
                (0, 0, {
                    'product_id': mouse.id,
                    'product_qty': 100,
                    'price_unit': mouse.standard_price,
                }),
                (0, 0, {
                    'product_id': headset.id,
                    'product_qty': 30,
                    'price_unit': headset.standard_price,
                }),
            ],
        })
        
        print(f"✓ Purchase Orders: PO-{po1.id}, PO-{po2.id}")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("✅ SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"Business Units: {BU.search_count([])}")
        print(f"Branches: {Branch.search_count([])}")
        print(f"Customers: {Partner.search_count([('customer_rank', '>', 0)])}")
        print(f"Vendors: {Partner.search_count([('supplier_rank', '>', 0)])}")
        print(f"Products: {Product.search_count([('default_code', 'like', 'LAP-%')]) + Product.search_count([('default_code', 'like', 'MSE-%')]) + Product.search_count([('default_code', 'like', 'KEY-%')]) + Product.search_count([('default_code', 'like', 'MON-%')]) + Product.search_count([('default_code', 'like', 'HDS-%')])}")
        print(f"Sales Orders: {SaleOrder.search_count([])}")
        print(f"Purchase Orders: {PurchaseOrder.search_count([])}")
        print("=" * 80)
        
        env.cr.commit()
        
    except Exception as e:
        print(f"\n❌ SEEDING FAILED: {e}")
        import traceback
        traceback.print_exc()
        env.cr.rollback()
        raise

# Execute
seed_comprehensive_data()
