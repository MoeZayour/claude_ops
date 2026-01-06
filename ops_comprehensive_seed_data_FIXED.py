#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPS Framework - FIXED Comprehensive Seed Data Script
====================================================
Fixes ORM issues with foreign key constraints
"""

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

def seed_comprehensive_data(env):
    """Fixed seeding with proper dependency handling"""
    
    _logger.info("=" * 80)
    _logger.info("FIXED OPS FRAMEWORK DATA SEEDING")
    _logger.info("=" * 80)
    
    # Get company first
    company = env['res.company'].browse(1)
    if not company:
        _logger.error("No company found!")
        return False
    
    # =========================================================================
    # PHASE 1: BUSINESS UNITS
    # =========================================================================
    _logger.info("\n[PHASE 1] Creating Business Units...")
    
    BU = env['ops.business.unit']
    
    bu_retail = BU.search([('code', '=', 'RET')], limit=1)
    if not bu_retail:
        bu_retail = BU.create({
            'name': 'Retail Division',
            'code': 'RET',
            'active': True,
        })
    
    bu_wholesale = BU.search([('code', '=', 'WHO')], limit=1)
    if not bu_wholesale:
        bu_wholesale = BU.create({
            'name': 'Wholesale Division',
            'code': 'WHO',
            'active': True,
        })
    
    env.cr.commit()
    _logger.info(f"✓ BUs: {bu_retail.name}, {bu_wholesale.name}")
    
    # =========================================================================
    # PHASE 2: BRANCHES
    # =========================================================================
    _logger.info("\n[PHASE 2] Creating Branches...")
    
    Branch = env['ops.branch']
    
    branch_dubai = Branch.search([('code', '=', 'DXB-01')], limit=1)
    if not branch_dubai:
        branch_dubai = Branch.create({
            'name': 'Dubai Main Branch',
            'code': 'DXB-01',
            'business_unit_id': bu_retail.id,
            'company_id': company.id,
            'active': True,
        })
    
    branch_abudhabi = Branch.search([('code', '=', 'AUH-01')], limit=1)
    if not branch_abudhabi:
        branch_abudhabi = Branch.create({
            'name': 'Abu Dhabi Branch',
            'code': 'AUH-01',
            'business_unit_id': bu_wholesale.id,
            'company_id': company.id,
            'active': True,
        })
    
    env.cr.commit()
    _logger.info(f"✓ Branches: {branch_dubai.name}, {branch_abudhabi.name}")
    
    # =========================================================================
    # PHASE 3: CUSTOMERS
    # =========================================================================
    _logger.info("\n[PHASE 3] Creating Customers...")
    
    Partner = env['res.partner']
    
    customer1 = Partner.search([('name', '=', 'Emirates Electronics LLC')], limit=1)
    if not customer1:
        customer1 = Partner.create({
            'name': 'Emirates Electronics LLC',
            'customer_rank': 1,
            'supplier_rank': 0,
            'email': 'contact@emirates-electronics.ae',
            'phone': '+971-4-1234567',
            'street': 'Sheikh Zayed Road',
            'city': 'Dubai',
            'country_id': env.ref('base.ae').id,
            'credit_limit': 50000.0,
        })
    
    customer2 = Partner.search([('name', '=', 'Gulf Retail Trading')], limit=1)
    if not customer2:
        customer2 = Partner.create({
            'name': 'Gulf Retail Trading',
            'customer_rank': 1,
            'supplier_rank': 0,
            'email': 'sales@gulf-retail.ae',
            'phone': '+971-4-7654321',
            'street': 'Al Maktoum Street',
            'city': 'Dubai',
            'country_id': env.ref('base.ae').id,
            'credit_limit': 75000.0,
        })
    
    customer3 = Partner.search([('name', '=', 'Abu Dhabi Wholesalers')], limit=1)
    if not customer3:
        customer3 = Partner.create({
            'name': 'Abu Dhabi Wholesalers',
            'customer_rank': 1,
            'supplier_rank': 0,
            'email': 'info@ad-wholesalers.ae',
            'phone': '+971-2-9876543',
            'street': 'Corniche Road',
            'city': 'Abu Dhabi',
            'country_id': env.ref('base.ae').id,
            'credit_limit': 100000.0,
        })
    
    env.cr.commit()
    _logger.info(f"✓ Customers: {customer1.name}, {customer2.name}, {customer3.name}")
    
    # =========================================================================
    # PHASE 4: VENDORS
    # =========================================================================
    _logger.info("\n[PHASE 4] Creating Vendors...")
    
    vendor1 = Partner.search([('name', '=', 'Global Tech Supplies')], limit=1)
    if not vendor1:
        vendor1 = Partner.create({
            'name': 'Global Tech Supplies',
            'customer_rank': 0,
            'supplier_rank': 1,
            'email': 'export@global-tech.cn',
            'phone': '+86-755-12345678',
            'street': 'Shenzhen Tech Park',
            'city': 'Shenzhen',
            'country_id': env.ref('base.cn').id,
        })
    
    vendor2 = Partner.search([('name', '=', 'Regional Electronics Distributor')], limit=1)
    if not vendor2:
        vendor2 = Partner.create({
            'name': 'Regional Electronics Distributor',
            'customer_rank': 0,
            'supplier_rank': 1,
            'email': 'sales@regional-electronics.ae',
            'phone': '+971-4-5555555',
            'street': 'Deira Industrial Area',
            'city': 'Dubai',
            'country_id': env.ref('base.ae').id,
        })
    
    env.cr.commit()
    _logger.info(f"✓ Vendors: {vendor1.name}, {vendor2.name}")
    
    # =========================================================================
    # PHASE 5: PRODUCTS
    # =========================================================================
    _logger.info("\n[PHASE 5] Creating Products...")
    
    Product = env['product.product']
    
    # Get or create category
    categ = env['product.category'].search([('name', '=', 'Electronics')], limit=1)
    if not categ:
        categ = env['product.category'].create({'name': 'Electronics'})
    
    products_data = [
        {
            'name': 'Business Laptop Pro',
            'default_code': 'LAP-BUS-001',
            'list_price': 3500.0,
            'standard_price': 2100.0,
        },
        {
            'name': 'Wireless Mouse',
            'default_code': 'MSE-WRL-001',
            'list_price': 85.0,
            'standard_price': 45.0,
        },
        {
            'name': 'USB-C Cable 2m',
            'default_code': 'CBL-USC-002',
            'list_price': 25.0,
            'standard_price': 10.0,
        },
        {
            'name': '27" 4K Monitor',
            'default_code': 'MON-27K-001',
            'list_price': 1200.0,
            'standard_price': 750.0,
        },
        {
            'name': 'Mechanical Keyboard RGB',
            'default_code': 'KBD-MEC-RGB',
            'list_price': 350.0,
            'standard_price': 180.0,
        },
    ]
    
    products = []
    for pdata in products_data:
        product = Product.search([('default_code', '=', pdata['default_code'])], limit=1)
        if not product:
            product = Product.create({
                'name': pdata['name'],
                'default_code': pdata['default_code'],
                'type': 'product',
                'categ_id': categ.id,
                'list_price': pdata['list_price'],
                'standard_price': pdata['standard_price'],
                'uom_id': env.ref('uom.product_uom_unit').id,
                'uom_po_id': env.ref('uom.product_uom_unit').id,
            })
        products.append(product)
    
    env.cr.commit()
    _logger.info(f"✓ Products: {len(products)} created")
    
    # =========================================================================
    # PHASE 6: SALES ORDERS
    # =========================================================================
    _logger.info("\n[PHASE 6] Creating Sales Orders...")
    
    SaleOrder = env['sale.order']
    
    # SO1: Small order
    so1 = SaleOrder.search([('partner_id', '=', customer1.id), ('state', '=', 'draft')], limit=1)
    if not so1:
        so1 = SaleOrder.create({
            'partner_id': customer1.id,
            'date_order': datetime.now(),
        })
        
        env['sale.order.line'].create({
            'order_id': so1.id,
            'product_id': products[1].id,  # Mouse
            'product_uom_qty': 2,
            'price_unit': 85.0,
        })
        
        env['sale.order.line'].create({
            'order_id': so1.id,
            'product_id': products[2].id,  # Cable
            'product_uom_qty': 3,
            'price_unit': 25.0,
        })
    
    # SO2: Large order
    so2 = SaleOrder.search([('partner_id', '=', customer2.id), ('state', '=', 'draft')], limit=1)
    if not so2:
        so2 = SaleOrder.create({
            'partner_id': customer2.id,
            'date_order': datetime.now(),
        })
        
        env['sale.order.line'].create({
            'order_id': so2.id,
            'product_id': products[0].id,  # Laptop
            'product_uom_qty': 50,
            'price_unit': 3500.0,
        })
    
    # SO3: Empty for Excel import
    so3 = SaleOrder.search([('partner_id', '=', customer3.id), ('state', '=', 'draft')], limit=1)
    if not so3:
        so3 = SaleOrder.create({
            'partner_id': customer3.id,
            'date_order': datetime.now(),
        })
    
    env.cr.commit()
    _logger.info(f"✓ Sales Orders: {so1.name}, {so2.name}, {so3.name}")
    
    # =========================================================================
    # PHASE 7: PURCHASE ORDERS
    # =========================================================================
    _logger.info("\n[PHASE 7] Creating Purchase Orders...")
    
    PurchaseOrder = env['purchase.order']
    
    po1 = PurchaseOrder.search([('partner_id', '=', vendor1.id), ('state', '=', 'draft')], limit=1)
    if not po1:
        po1 = PurchaseOrder.create({
            'partner_id': vendor1.id,
            'date_order': datetime.now(),
        })
        
        env['purchase.order.line'].create({
            'order_id': po1.id,
            'product_id': products[0].id,
            'product_qty': 100,
            'price_unit': 2100.0,
            'date_planned': datetime.now(),
        })
    
    po2 = PurchaseOrder.search([('partner_id', '=', vendor2.id), ('state', '=', 'draft')], limit=1)
    if not po2:
        po2 = PurchaseOrder.create({
            'partner_id': vendor2.id,
            'date_order': datetime.now(),
        })
        
        env['purchase.order.line'].create({
            'order_id': po2.id,
            'product_id': products[3].id,
            'product_qty': 50,
            'price_unit': 750.0,
            'date_planned': datetime.now(),
        })
    
    env.cr.commit()
    _logger.info(f"✓ Purchase Orders: {po1.name}, {po2.name}")
    
    # =========================================================================
    # PHASE 8: SOD RULES
    # =========================================================================
    _logger.info("\n[PHASE 8] Creating SoD Rules...")
    
    SoD = env['ops.segregation.of.duties']
    
    sod_rules = [
        {
            'name': 'Sales Order: Create + Confirm Separation',
            'model_name': 'sale.order',
            'action_1': 'create',
            'action_2': 'confirm',
            'threshold_amount': 5000.0,
            'block_violation': True,
            'active': False,
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
            'threshold_amount': 0.0,
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
        existing = SoD.search([('name', '=', rule_data['name'])], limit=1)
        if not existing:
            SoD.create(rule_data)
    
    env.cr.commit()
    _logger.info(f"✓ SoD Rules: 4 created")
    
    # =========================================================================
    # PHASE 9: FIELD VISIBILITY RULES
    # =========================================================================
    _logger.info("\n[PHASE 9] Creating Field Visibility Rules...")
    
    FieldVis = env['ops.field.visibility.rule']
    
    group_sale = env.ref('sales_team.group_sale_salesman')
    group_purchase = env.ref('purchase.group_purchase_user')
    group_stock = env.ref('stock.group_stock_user')
    
    visibility_rules = [
        {'name': 'Hide Cost from Sales', 'model_name': 'product.product', 
         'field_name': 'standard_price', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        {'name': 'Hide Purchase Price from Sales', 'model_name': 'product.template', 
         'field_name': 'standard_price', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        {'name': 'Hide Margin from Sales', 'model_name': 'sale.order.line', 
         'field_name': 'margin', 'restricted_group_ids': [(6, 0, [group_sale.id])]},
        {'name': 'Hide Sale Price from Purchase', 'model_name': 'product.product', 
         'field_name': 'list_price', 'restricted_group_ids': [(6, 0, [group_purchase.id])]},
        {'name': 'Hide Cost from Warehouse', 'model_name': 'stock.move', 
         'field_name': 'price_unit', 'restricted_group_ids': [(6, 0, [group_stock.id])]},
        {'name': 'Hide Value from Warehouse', 'model_name': 'stock.quant', 
         'field_name': 'value', 'restricted_group_ids': [(6, 0, [group_stock.id])]},
    ]
    
    for rule_data in visibility_rules:
        existing = FieldVis.search([('name', '=', rule_data['name'])], limit=1)
        if not existing:
            FieldVis.create(rule_data)
    
    env.cr.commit()
    _logger.info(f"✓ Field Visibility Rules: {len(visibility_rules)} created")
    
    # =========================================================================
    # FINAL VERIFICATION
    # =========================================================================
    _logger.info("\n[FINAL VERIFICATION]")
    
    counts = {
        'Business Units': len(BU.search([])),
        'Branches': len(Branch.search([])),
        'Customers': len(Partner.search([('customer_rank', '>', 0)])),
        'Vendors': len(Partner.search([('supplier_rank', '>', 0)])),
        'Products': len(Product.search([('default_code', 'in', ['LAP-BUS-001', 'MSE-WRL-001', 'CBL-USC-002', 'MON-27K-001', 'KBD-MEC-RGB'])])),
        'Sales Orders': len(SaleOrder.search([('id', 'in', [so1.id, so2.id, so3.id])])),
        'Purchase Orders': len(PurchaseOrder.search([('id', 'in', [po1.id, po2.id])])),
        'SoD Rules': len(SoD.search([])),
        'Field Visibility': len(FieldVis.search([])),
    }
    
    _logger.info("\n" + "=" * 80)
    _logger.info("SEEDING COMPLETE - FINAL COUNTS:")
    _logger.info("=" * 80)
    for item, count in counts.items():
        _logger.info(f"  {item}: {count}")
    _logger.info("=" * 80)
    
    return counts

# =============================================================================
# EXECUTION
# =============================================================================
try:
    result = seed_comprehensive_data(env)
    
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE SEEDING SUCCESSFUL!")
    print("=" * 80)
    print(f"Total records created: {sum(result.values())}")
    print("\nSystem ready for UAT testing!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ SEEDING FAILED: {e}")
    import traceback
    traceback.print_exc()
    raise
