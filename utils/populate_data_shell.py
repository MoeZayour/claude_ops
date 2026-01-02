#!/usr/bin/env python3
"""
Data Population Script - Runs inside Odoo Shell
This bypasses permission issues by running as SUPERUSER
"""

import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

def populate_data(env):
    """Populate database with comprehensive demo data"""
    
    stats = {
        'branches': 0,
        'business_units': 0,
        'users': 0,
        'personas': 0,
        'products': 0,
        'partners': 0,
        'purchase_orders': 0,
        'sales_orders': 0,
        'invoices': 0,
        'payments': 0,
        'stock_moves': 0,
        'revenue': 0.0,
        'expenses': 0.0
    }
    
    print("\n" + "="*70)
    print("🚀 STARTING DATA POPULATION - OPS FRAMEWORK FULL DEMO")
    print("="*70)
    
    company = env.company
    
    # Phase 1: Branch Structure
    print("\n📍 Phase 1: Creating Branch Hierarchy...")
    branches = {}
    
    try:
        # Check existing branches from post_init_hook
        existing_hq = env['ops.branch'].search([('code', '=', 'HQ')], limit=1)
        if existing_hq:
            branches['main'] = existing_hq
            print(f"   ✓ Main Branch exists (ID: {existing_hq.id})")
            stats['branches'] += 1
        
        # Create additional branches
        branch_configs = [
            ('North Region', 'NORTH'),
            ('South Region', 'SOUTH'),
            ('West Branch', 'WEST'),
            ('East Branch', 'EAST'),
        ]
        
        for name, code in branch_configs:
            existing = env['ops.branch'].search([('code', '=', code)], limit=1)
            if existing:
                branches[code.lower()] = existing
                print(f"   ✓ {name} already exists")
                continue
            
            branch = env['ops.branch'].create({
                'name': name,
                'code': code,
                'company_id': company.id,
                'active': True
            })
            branches[code.lower()] = branch
            print(f"   ✓ Created {name} (ID: {branch.id})")
            stats['branches'] += 1
        
    except Exception as e:
        print(f"   ⚠ Error in branch creation: {str(e)[:150]}")
    
    # Phase 1b: Business Units
    print("\n🏢 Phase 1b: Creating Business Units...")
    business_units = {}
    
    try:
        existing_corp = env['ops.business.unit'].search([('code', '=', 'CORP')], limit=1)
        if existing_corp:
            business_units['corp'] = existing_corp
            print(f"   ✓ Corporate Operations exists")
            stats['business_units'] += 1
        
        bu_configs = [
            ('Sales Division', 'SALES'),
            ('Operations Division', 'OPS'),
            ('Finance Division', 'FIN'),
            ('IT Division', 'IT'),
        ]
        
        for name, code in bu_configs:
            existing = env['ops.business.unit'].search([('code', '=', code)], limit=1)
            if existing:
                business_units[code.lower()] = existing
                print(f"   ✓ {name} already exists")
                continue
            
            bu = env['ops.business.unit'].create({
                'name': name,
                'code': code,
                'company_id': company.id,
                'active': True
            })
            business_units[code.lower()] = bu
            print(f"   ✓ Created {name} (ID: {bu.id})")
            stats['business_units'] += 1
        
    except Exception as e:
        print(f"   ⚠ Error in business unit creation: {str(e)[:150]}")
    
    # Phase 2: Users & Personas
    print("\n👥 Phase 2: Creating Users & Personas...")
    users = {}
    
    user_configs = [
        ('user_sales', 'Sales Manager', 'Sales Operations Manager'),
        ('user_logistics', 'Warehouse Manager', 'Logistics Coordinator'),
        ('user_accountant', 'Senior Accountant', 'Financial Controller'),
        ('user_purchaser', 'Purchasing Officer', 'Procurement Specialist'),
        ('user_approver', 'Operations Approver', 'Operations Director'),
    ]
    
    for login, name, persona_name in user_configs:
        try:
            # Check if user exists
            user = env['res.users'].search([('login', '=', login)], limit=1)
            if user:
                users[login] = user
                # Update password
                user.password = '123'
                print(f"   ✓ User {login} exists (password updated)")
            else:
                user = env['res.users'].create({
                    'name': name,
                    'login': login,
                    'password': '123',
                    'email': f'{login}@opsdemo.com',
                    'company_id': company.id,
                })
                users[login] = user
                print(f"   ✓ Created {name} (Login: {login} / Password: 123)")
                stats['users'] += 1
            
            # Create Persona
            persona_exists = env['ops.persona'].search([('code', '=', login.upper())], limit=1)
            if not persona_exists:
                persona_data = {
                    'name': persona_name,
                    'code': login.upper(),
                    'user_id': user.id,
                    'active': True,
                }
                
                if 'main' in branches:
                    persona_data['branch_id'] = branches['main'].id
                
                env['ops.persona'].create(persona_data)
                print(f"      → Created Persona: {persona_name}")
                stats['personas'] += 1
                
        except Exception as e:
            print(f"   ⚠ Error with user {login}: {str(e)[:100]}")
    
    # Phase 3: Products
    print("\n📦 Phase 3: Creating Master Products...")
    products = {}
    
    # Get defaults
    try:
        default_categ = env['product.category'].search([], limit=1)
        unit_uom = env['uom.uom'].search([('name', '=', 'Units')], limit=1)
        if not unit_uom:
            unit_uom = env.ref('uom.product_uom_unit')
    except:
        unit_uom = env['uom.uom'].search([], limit=1)
    
    product_configs = [
        ('Laptop Pro X1', 'product', 2500.0, 1500.0),
        ('Wireless Mouse', 'consu', 25.0, 10.0),
        ('IT Support Contract', 'service', 1200.0, 800.0),
        ('Office Desk Premium', 'product', 650.0, 350.0),
        ('Consulting Hour', 'service', 150.0, 100.0),
        ('Network Router', 'product', 450.0, 250.0),
        ('Software License', 'service', 300.0, 200.0),
        ('LED Monitor 27"', 'product', 350.0, 200.0),
        ('Wireless Keyboard', 'consu', 45.0, 20.0),
        ('Cloud Storage 1TB', 'service', 120.0, 80.0),
    ]
    
    for name, prod_type, sale_price, cost_price in product_configs:
        try:
            existing = env['product.product'].search([('name', '=', name)], limit=1)
            if existing:
                products[name] = existing
                print(f"   ✓ {name} already exists")
                continue
            
            product = env['product.product'].create({
                'name': name,
                'type': prod_type,
                'list_price': sale_price,
                'standard_price': cost_price,
                'purchase_ok': True,
                'sale_ok': True,
                'uom_id': unit_uom.id,
                'categ_id': default_categ.id if default_categ else False,
                'company_id': company.id,
            })
            products[name] = product
            print(f"   ✓ Created {name} (${sale_price})")
            stats['products'] += 1
            
        except Exception as e:
            print(f"   ⚠ Error creating {name}: {str(e)[:100]}")
    
    # Phase 4: Partners
    print("\n🤝 Phase 4: Creating Business Partners...")
    partners = {'vendors': [], 'customers': []}
    
    # Vendors
    vendor_configs = [
        'Tech Supplies Global',
        'Office Furniture Direct',
        'IT Equipment Corp',
        'Software Solutions Ltd',
    ]
    
    for vendor_name in vendor_configs:
        try:
            existing = env['res.partner'].search([('name', '=', vendor_name)], limit=1)
            if existing:
                partners['vendors'].append(existing)
                print(f"   ✓ Vendor {vendor_name} exists")
                continue
            
            vendor = env['res.partner'].create({
                'name': vendor_name,
                'is_company': True,
                'email': f'{vendor_name.lower().replace(" ", "")[:20]}@vendor.com',
                'phone': '+1-555-0100',
                'company_type': 'company',
                'company_id': company.id,
            })
            partners['vendors'].append(vendor)
            print(f"   ✓ Created Vendor: {vendor_name}")
            stats['partners'] += 1
            
        except Exception as e:
            print(f"   ⚠ Error creating vendor: {str(e)[:80]}")
    
    # Customers
    customer_configs = [
        'Acme Corporation Ltd',
        'Global Industries Inc',
        'Tech Innovators LLC',
        'Enterprise Solutions Co',
        'Digital Services Group',
        'Manufacturing Plus Inc',
        'Retail Chain Express',
        'Finance Solutions Ltd',
    ]
    
    for customer_name in customer_configs:
        try:
            existing = env['res.partner'].search([('name', '=', customer_name)], limit=1)
            if existing:
                partners['customers'].append(existing)
                print(f"   ✓ Customer {customer_name} exists")
                continue
            
            customer = env['res.partner'].create({
                'name': customer_name,
                'is_company': True,
                'email': f'{customer_name.lower().replace(" ", "")[:20]}@customer.com',
                'phone': '+1-555-0200',
                'company_type': 'company',
                'company_id': company.id,
            })
            partners['customers'].append(customer)
            print(f"   ✓ Created Customer: {customer_name}")
            stats['partners'] += 1
            
        except Exception as e:
            print(f"   ⚠ Error creating customer: {str(e)[:80]}")
    
    # Phase 5: Purchase Orders
    print("\n🛒 Phase 5: Creating Purchase Orders...")
    
    if products and partners['vendors']:
        purchaser = users.get('user_purchaser', env.user)
        
        # Get storable products
        storable_prods = [(k, v) for k, v in products.items() 
                          if v.type in ('product', 'consu')]
        
        po_configs = [
            (0, 25, 1500.0),
            (1, 15, 350.0),
            (2, 30, 200.0),
        ]
        
        for idx, (prod_idx, qty, price) in enumerate(po_configs, 1):
            if prod_idx >= len(storable_prods):
                continue
            
            try:
                product_name, product = storable_prods[prod_idx]
                vendor = partners['vendors'][idx % len(partners['vendors'])]
                
                po = env['purchase.order'].create({
                    'partner_id': vendor.id,
                    'user_id': purchaser.id,
                    'company_id': company.id,
                    'order_line': [(0, 0, {
                        'product_id': product.id,
                        'product_qty': qty,
                        'price_unit': price,
                    })]
                })
                
                po.button_confirm()
                total = qty * price
                print(f"   ✓ PO #{idx}: {qty}x {product_name} = ${total:,.2f}")
                stats['purchase_orders'] += 1
                stats['expenses'] += total
                
                # Receive stock
                if idx <= 2:
                    for picking in po.picking_ids:
                        if picking.state not in ('done', 'cancel'):
                            for move in picking.move_ids:
                                move.quantity_done = move.product_uom_qty
                            picking.button_validate()
                            stats['stock_moves'] += qty
                            print(f"      → Received {qty} units")
                
            except Exception as e:
                print(f"   ⚠ Error in PO #{idx}: {str(e)[:80]}")
    
    # Phase 6: Sales Orders
    print("\n💰 Phase 6: Creating Sales Orders...")
    
    if products and partners['customers']:
        sales_user = users.get('user_sales', env.user)
        product_list = list(products.items())
        
        for i in range(1, 21):
            try:
                customer = partners['customers'][i % len(partners['customers'])]
                product_name, product = product_list[i % len(product_list)]
                
                qty = (i % 5) + 1
                price = product.list_price
                
                so = env['sale.order'].create({
                    'partner_id': customer.id,
                    'user_id': sales_user.id,
                    'company_id': company.id,
                    'order_line': [(0, 0, {
                        'product_id': product.id,
                        'product_uom_qty': qty,
                        'price_unit': price,
                    })]
                })
                
                so.action_confirm()
                order_total = price * qty
                stats['sales_orders'] += 1
                stats['revenue'] += order_total
                
                print(f"   ✓ SO #{i}: {qty}x {product_name[:25]} = ${order_total:,.2f}")
                
                # Deliver first 15
                if i <= 15:
                    for picking in so.picking_ids:
                        if picking.state not in ('done', 'cancel'):
                            for move in picking.move_ids:
                                move.quantity_done = move.product_uom_qty
                            picking.button_validate()
                            stats['stock_moves'] += qty
                    
                    # Create Invoice
                    try:
                        invoice_ids = so._create_invoices()
                        for invoice in invoice_ids:
                            invoice.action_post()
                            stats['invoices'] += 1
                            
                            # Register payment for first 10
                            if i <= 10:
                                bank_journal = env['account.journal'].search([('type', '=', 'bank')], limit=1)
                                if bank_journal:
                                    payment = env['account.payment'].create({
                                        'payment_type': 'inbound',
                                        'partner_type': 'customer',
                                        'partner_id': customer.id,
                                        'amount': order_total,
                                        'journal_id': bank_journal.id,
                                        'date': datetime.now().date(),
                                    })
                                    payment.action_post()
                                    stats['payments'] += 1
                    except:
                        pass
                
            except Exception as e:
                print(f"   ⚠ Error in SO #{i}: {str(e)[:60]}")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 DATA POPULATION COMPLETE")
    print("="*70)
    
    print("\n📊 INFRASTRUCTURE:")
    print(f"   • Branches: {stats['branches']}")
    print(f"   • Business Units: {stats['business_units']}")
    print(f"   • Users: {stats['users']}")
    print(f"   • Personas: {stats['personas']}")
    print(f"   • Products: {stats['products']}")
    print(f"   • Partners: {stats['partners']}")
    
    print("\n📈 TRANSACTIONS:")
    print(f"   • Purchase Orders: {stats['purchase_orders']}")
    print(f"   • Sales Orders: {stats['sales_orders']}")
    print(f"   • Invoices: {stats['invoices']}")
    print(f"   • Payments: {stats['payments']}")
    print(f"   • Stock Moves: {stats['stock_moves']}")
    
    print("\n💰 FINANCIAL:")
    print(f"   • Revenue: ${stats['revenue']:,.2f}")
    print(f"   • Expenses: ${stats['expenses']:,.2f}")
    print(f"   • Net Income: ${stats['revenue'] - stats['expenses']:,.2f}")
    
    print("\n👤 USER LOGINS (Password: 123 for all):")
    print("   • admin / admin")
    print("   • user_sales / 123")
    print("   • user_logistics / 123")
    print("   • user_accountant / 123")
    print("   • user_purchaser / 123")
    print("   • user_approver / 123")
    
    print("\n✅ Database fully populated and ready for inspection!")
    print("="*70 + "\n")
    
    env.cr.commit()
    return stats

# Entry point for Odoo shell
if __name__ == "__main__":
    populate_data(env)
