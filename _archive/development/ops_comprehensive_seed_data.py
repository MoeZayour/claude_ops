#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPS Framework Comprehensive Seed Data Script
===========================================

This script seeds comprehensive test data for UAT testing of the OPS Framework.
It handles all dependencies correctly and creates realistic test scenarios.

Usage:
    python3 ops_comprehensive_seed_data.py

Or via Odoo shell:
    odoo shell -d mz-db < ops_comprehensive_seed_data.py
"""

import logging
from datetime import datetime, timedelta
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def seed_comprehensive_data(env):
    """
    Comprehensive data seeding for OPS Framework UAT testing
    """
    
    _logger.info("=" * 80)
    _logger.info("STARTING COMPREHENSIVE OPS FRAMEWORK DATA SEEDING")
    _logger.info("=" * 80)
    
    # =========================================================================
    # PHASE 1: CLEANUP - Remove existing test data
    # =========================================================================
    _logger.info("\n[PHASE 1] Cleaning existing test data...")
    
    try:
        # Delete in reverse dependency order
        env['sale.order'].search([('name', 'ilike', 'S0000')]).unlink()
        env['purchase.order'].search([('name', 'ilike', 'P0000')]).unlink()
        env['account.move'].search([('name', 'ilike', 'INV/TEST')]).unlink()
        env['res.partner'].search([('name', 'in', [
            'Emirates Electronics LLC',
            'Gulf Retail Trading',
            'Abu Dhabi Wholesalers',
            'Global Tech Supplies',
            'Regional Electronics Distributor'
        ])]).unlink()
        env['product.product'].search([('default_code', 'in', [
            'LAP-BUS-001', 'MSE-WRL-001', 'CBL-USC-002', 
            'MON-27K-001', 'KBD-MEC-RGB'
        ])]).unlink()
        env['ops.branch'].search([('code', 'in', ['DXB-01', 'AUH-01'])]).unlink()
        env['ops.business.unit'].search([('code', 'in', ['RET', 'WHO'])]).unlink()
        
        _logger.info("✓ Cleanup complete")
    except Exception as e:
        _logger.warning(f"Cleanup warnings (expected on first run): {e}")
    
    # =========================================================================
    # PHASE 2: SECURITY FRAMEWORK (Tier 1)
    # =========================================================================
    _logger.info("\n[PHASE 2] Loading Security Framework Data...")
    
    # 2.1 Segregation of Duties Rules
    _logger.info("Loading SoD Rules...")
    
    SoD = env['ops.segregation.of.duties']
    
    sod_rules = [
        {
            'name': 'Sales Order: Create + Confirm Separation',
            'model_name': 'sale.order',
            'action_1': 'create',
            'action_2': 'confirm',
            'threshold_amount': 5000.0,
            'block_violation': True,
            'active': False,  # Admin must enable
        },
        {
            'name': 'Purchase Order: Create + Confirm Separation',
            'model_name': 'purchase.order',
            'action_1': 'create',
            'action_2': 'confirm',
            'threshold_amount': 5000.0,
            'block_violation': True,
            'active': False,
        },
        {
            'name': 'Invoice: Create + Post Separation',
            'model_name': 'account.move',
            'action_1': 'create',
            'action_2': 'post',
            'threshold_amount': 0.0,  # Always enforce
            'block_violation': True,
            'active': False,
        },
        {
            'name': 'Payment: Create + Post Separation',
            'model_name': 'account.payment',
            'action_1': 'create',
            'action_2': 'post',
            'threshold_amount': 2000.0,
            'block_violation': True,
            'active': False,
        },
    ]
    
    for rule_data in sod_rules:
        SoD.create(rule_data)
    
    _logger.info(f"✓ Created {len(sod_rules)} SoD rules")
    
    # 2.2 Field Visibility Rules
    _logger.info("Loading Field Visibility Rules...")
    
    FieldVis = env['ops.field.visibility.rule']
    
    # Get security groups
    group_sale = env.ref('sales_team.group_sale_salesman')
    group_purchase = env.ref('purchase.group_purchase_user')
    group_stock = env.ref('stock.group_stock_user')
    
    field_visibility_rules = [
        # Hide from Sales Reps
        {'name': 'Hide Cost Price from Sales', 'model_name': 'product.product', 
         'field_name': 'standard_price', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        {'name': 'Hide Purchase Price from Sales', 'model_name': 'product.template', 
         'field_name': 'standard_price', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        {'name': 'Hide Margin from Sales', 'model_name': 'sale.order.line', 
         'field_name': 'margin', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        
        # Hide from Purchase Officers
        {'name': 'Hide Customer from Purchase', 'model_name': 'purchase.order', 
         'field_name': 'partner_id', 'restricted_group_ids': [(6, 0, [group_purchase.id])]},
        {'name': 'Hide Sale Price from Purchase', 'model_name': 'product.product', 
         'field_name': 'list_price', 'restricted_group_ids': [(6, 0, [group_purchase.id])]},
        
        # Hide from Warehouse
        {'name': 'Hide Cost from Warehouse', 'model_name': 'stock.move', 
         'field_name': 'price_unit', 'restricted_group_ids': [(6, 0, [group_stock.id])]},
        {'name': 'Hide Value from Warehouse', 'model_name': 'stock.quant', 
         'field_name': 'value', 'restricted_group_ids': [(6, 0, [group_stock.id])]},
    ]
    
    for rule_data in field_visibility_rules:
        FieldVis.create(rule_data)
    
    _logger.info(f"✓ Created {len(field_visibility_rules)} Field Visibility rules")
    
    # =========================================================================
    # PHASE 3: ORGANIZATIONAL STRUCTURE
    # =========================================================================
    _logger.info("\n[PHASE 3] Creating Organizational Structure...")
    
    # 3.1 Business Units
    _logger.info("Creating Business Units...")
    
    BU = env['ops.business.unit']
    
    bu_retail = BU.create({
        'name': 'Retail Division',
        'code': 'RET',
        'active': True,
    })
    
    bu_wholesale = BU.create({
        'name': 'Wholesale Division',
        'code': 'WHO',
        'active': True,
    })
    
    _logger.info("✓ Created 2 Business Units")
    
    # 3.2 Branches
    _logger.info("Creating Branches...")
    
    Branch = env['ops.branch']
    
    # Get default company
    company = env['res.company'].browse(1)
    
    branch_dubai = Branch.create({
        'name': 'Dubai Main Branch',
        'code': 'DXB-01',
        'business_unit_id': bu_retail.id,
        'company_id': company.id,
        'active': True,
    })
    
    branch_abudhabi = Branch.create({
        'name': 'Abu Dhabi Branch',
        'code': 'AUH-01',
        'business_unit_id': bu_wholesale.id,
        'company_id': company.id,
        'active': True,
    })
    
    _logger.info("✓ Created 2 Branches")
    
    # =========================================================================
    # PHASE 4: MASTER DATA
    # =========================================================================
    _logger.info("\n[PHASE 4] Creating Master Data...")
    
    # 4.1 Customers
    _logger.info("Creating Customers...")
    
    Partner = env['res.partner']
    
    customer1 = Partner.create({
        'name': 'Emirates Electronics LLC',
        'customer_rank': 1,
        'email': 'contact@emirates-electronics.ae',
        'phone': '+971-4-1234567',
        'street': 'Sheikh Zayed Road',
        'city': 'Dubai',
        'country_id': env.ref('base.ae').id,
        'credit_limit': 50000.0,
        'ops_branch_id': branch_dubai.id,
    })
    
    customer2 = Partner.create({
        'name': 'Gulf Retail Trading',
        'customer_rank': 1,
        'email': 'sales@gulf-retail.ae',
        'phone': '+971-4-7654321',
        'street': 'Al Maktoum Street',
        'city': 'Dubai',
        'country_id': env.ref('base.ae').id,
        'credit_limit': 75000.0,
        'ops_branch_id': branch_dubai.id,
    })
    
    customer3 = Partner.create({
        'name': 'Abu Dhabi Wholesalers',
        'customer_rank': 1,
        'email': 'info@ad-wholesalers.ae',
        'phone': '+971-2-9876543',
        'street': 'Corniche Road',
        'city': 'Abu Dhabi',
        'country_id': env.ref('base.ae').id,
        'credit_limit': 100000.0,
        'ops_branch_id': branch_abudhabi.id,
    })
    
    _logger.info("✓ Created 3 Customers")
    
    # 4.2 Vendors
    _logger.info("Creating Vendors...")
    
    vendor1 = Partner.create({
        'name': 'Global Tech Supplies',
        'supplier_rank': 1,
        'email': 'export@global-tech.cn',
        'phone': '+86-755-12345678',
        'street': 'Shenzhen Tech Park',
        'city': 'Shenzhen',
        'country_id': env.ref('base.cn').id,
    })
    
    vendor2 = Partner.create({
        'name': 'Regional Electronics Distributor',
        'supplier_rank': 1,
        'email': 'sales@regional-electronics.ae',
        'phone': '+971-4-5555555',
        'street': 'Deira Industrial Area',
        'city': 'Dubai',
        'country_id': env.ref('base.ae').id,
    })
    
    _logger.info("✓ Created 2 Vendors")
    
    # 4.3 Products
    _logger.info("Creating Products...")
    
    Product = env['product.product']
    
    # Get product category
    categ = env['product.category'].search([('name', '=', 'All')], limit=1)
    if not categ:
        categ = env['product.category'].create({'name': 'Electronics'})
    
    product1 = Product.create({
        'name': 'Business Laptop Pro',
        'default_code': 'LAP-BUS-001',
        'type': 'product',
        'categ_id': categ.id,
        'list_price': 3500.0,
        'standard_price': 2100.0,
        'uom_id': env.ref('uom.product_uom_unit').id,
        'uom_po_id': env.ref('uom.product_uom_unit').id,
    })
    
    product2 = Product.create({
        'name': 'Wireless Mouse',
        'default_code': 'MSE-WRL-001',
        'type': 'product',
        'categ_id': categ.id,
        'list_price': 85.0,
        'standard_price': 45.0,
        'uom_id': env.ref('uom.product_uom_unit').id,
        'uom_po_id': env.ref('uom.product_uom_unit').id,
    })
    
    product3 = Product.create({
        'name': 'USB-C Cable 2m',
        'default_code': 'CBL-USC-002',
        'type': 'product',
        'categ_id': categ.id,
        'list_price': 25.0,
        'standard_price': 10.0,
        'uom_id': env.ref('uom.product_uom_unit').id,
        'uom_po_id': env.ref('uom.product_uom_unit').id,
    })
    
    product4 = Product.create({
        'name': '27" 4K Monitor',
        'default_code': 'MON-27K-001',
        'type': 'product',
        'categ_id': categ.id,
        'list_price': 1200.0,
        'standard_price': 750.0,
        'uom_id': env.ref('uom.product_uom_unit').id,
        'uom_po_id': env.ref('uom.product_uom_unit').id,
    })
    
    product5 = Product.create({
        'name': 'Mechanical Keyboard RGB',
        'default_code': 'KBD-MEC-RGB',
        'type': 'product',
        'categ_id': categ.id,
        'list_price': 350.0,
        'standard_price': 180.0,
        'uom_id': env.ref('uom.product_uom_unit').id,
        'uom_po_id': env.ref('uom.product_uom_unit').id,
    })
    
    _logger.info("✓ Created 5 Products")
    
    # =========================================================================
    # PHASE 5: TEST TRANSACTIONS
    # =========================================================================
    _logger.info("\n[PHASE 5] Creating Test Transactions...")
    
    # 5.1 Sales Orders
    _logger.info("Creating Sales Orders...")
    
    SaleOrder = env['sale.order']
    
    # SO1: Small order (no approval needed)
    so1 = SaleOrder.create({
        'partner_id': customer1.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_dubai.id,
    })
    
    env['sale.order.line'].create({
        'order_id': so1.id,
        'product_id': product2.id,
        'product_uom_qty': 2,
        'price_unit': 85.0,
    })
    
    env['sale.order.line'].create({
        'order_id': so1.id,
        'product_id': product3.id,
        'product_uom_qty': 3,
        'price_unit': 25.0,
    })
    
    # SO2: Large order (requires approval - SoD test)
    so2 = SaleOrder.create({
        'partner_id': customer2.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_dubai.id,
    })
    
    env['sale.order.line'].create({
        'order_id': so2.id,
        'product_id': product1.id,
        'product_uom_qty': 50,
        'price_unit': 3500.0,
    })
    
    env['sale.order.line'].create({
        'order_id': so2.id,
        'product_id': product2.id,
        'product_uom_qty': 50,
        'price_unit': 85.0,
    })
    
    env['sale.order.line'].create({
        'order_id': so2.id,
        'product_id': product3.id,
        'product_uom_qty': 100,
        'price_unit': 25.0,
    })
    
    # SO3: Empty order for Excel import testing
    so3 = SaleOrder.create({
        'partner_id': customer3.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_abudhabi.id,
    })
    
    _logger.info(f"✓ Created 3 Sales Orders: {so1.name}, {so2.name}, {so3.name}")
    
    # 5.2 Purchase Orders
    _logger.info("Creating Purchase Orders...")
    
    PurchaseOrder = env['purchase.order']
    
    # PO1: Perfect match scenario
    po1 = PurchaseOrder.create({
        'partner_id': vendor1.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_dubai.id,
    })
    
    env['purchase.order.line'].create({
        'order_id': po1.id,
        'product_id': product1.id,
        'product_qty': 100,
        'price_unit': 2100.0,
        'date_planned': datetime.now(),
    })
    
    # PO2: Partial receipt scenario
    po2 = PurchaseOrder.create({
        'partner_id': vendor2.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_dubai.id,
    })
    
    env['purchase.order.line'].create({
        'order_id': po2.id,
        'product_id': product4.id,
        'product_qty': 50,
        'price_unit': 750.0,
        'date_planned': datetime.now(),
    })
    
    # PO3: Over-billing test scenario
    po3 = PurchaseOrder.create({
        'partner_id': vendor1.id,
        'date_order': datetime.now(),
        'ops_branch_id': branch_abudhabi.id,
    })
    
    env['purchase.order.line'].create({
        'order_id': po3.id,
        'product_id': product5.id,
        'product_qty': 100,
        'price_unit': 180.0,
        'date_planned': datetime.now(),
    })
    
    _logger.info(f"✓ Created 3 Purchase Orders: {po1.name}, {po2.name}, {po3.name}")
    
    # =========================================================================
    # PHASE 6: FINAL VERIFICATION
    # =========================================================================
    _logger.info("\n[PHASE 6] Final Verification...")
    
    counts = {
        'Business Units': len(BU.search([])),
        'Branches': len(Branch.search([])),
        'Customers': len(Partner.search([('customer_rank', '>', 0)])),
        'Vendors': len(Partner.search([('supplier_rank', '>', 0)])),
        'Products': len(Product.search([('default_code', 'in', [
            'LAP-BUS-001', 'MSE-WRL-001', 'CBL-USC-002', 
            'MON-27K-001', 'KBD-MEC-RGB'
        ])])),
        'Sales Orders': len(SaleOrder.search([('name', 'ilike', 'S0')])),
        'Purchase Orders': len(PurchaseOrder.search([('name', 'ilike', 'P0')])),
        'SoD Rules': len(SoD.search([])),
        'Field Visibility Rules': len(FieldVis.search([])),
    }
    
    _logger.info("\n" + "=" * 80)
    _logger.info("SEEDING COMPLETE - FINAL COUNTS:")
    _logger.info("=" * 80)
    for item, count in counts.items():
        _logger.info(f"  {item}: {count}")
    _logger.info("=" * 80)
    
    return counts

# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == '__main__':
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        try:
            result = seed_comprehensive_data(env)
            env.cr.commit()
            
            print("\n" + "=" * 80)
            print("✅ COMPREHENSIVE SEEDING SUCCESSFUL!")
            print("=" * 80)
            print(f"Total records created: {sum(result.values())}")
            print("\nSystem is ready for UAT testing at: https://dev.mz-im.com/")
            print("Login: admin / admin")
            print("=" * 80)
            
        except Exception as e:
            env.cr.rollback()
            print(f"\n❌ SEEDING FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise

