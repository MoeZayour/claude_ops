#!/usr/bin/env python3
"""
Fixed Data Factory Script for OPS Framework - Complete Edition
Handles all constraints and creates complete test data
"""

import xmlrpc.client
import sys
from datetime import datetime, timedelta
import time

# Connection Configuration
URL = "http://localhost:8089"
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"

class OdooDataFactory:
    def __init__(self):
        self.url = URL
        self.db = DB
        self.username = USERNAME
        self.password = PASSWORD
        self.uid = None
        self.common = None
        self.models = None
        
        # Track created data
        self.stats = {
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
        
    def connect(self):
        """Establish XML-RPC connection"""
        print(f"🔗 Connecting to {self.url} (DB: {self.db})...")
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                raise Exception("Authentication failed!")
            
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            print(f"✅ Connected as user ID: {self.uid}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def execute(self, model, method, *args, **kwargs):
        """Execute XML-RPC call with error handling"""
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except xmlrpc.client.Fault as e:
            print(f"      ⚠ Fault: {str(e)[:200]}")
            raise
        except Exception as e:
            print(f"      ⚠ Error: {str(e)[:200]}")
            raise
    
    def get_company_id(self):
        """Get the main company ID"""
        try:
            company_ids = self.execute('res.company', 'search', [], {'limit': 1})
            return company_ids[0] if company_ids else 1
        except:
            return 1
    
    def create_branch_structure(self):
        """Phase 1: Create Branch Hierarchy with analytic accounts"""
        print("\n📍 Phase 1: Creating Branch Hierarchy...")
        
        branches = {}
        company_id = self.get_company_id()
        
        try:
            # Check if Main Branch already exists from post_init_hook
            existing_branches = self.execute('ops.branch', 'search', [('code', '=', 'HQ')])
            if existing_branches:
                branches['main'] = existing_branches[0]
                print(f"   ✓ Main Branch exists (ID: {branches['main']})")
                self.stats['branches'] += 1
            
            # Create additional branches
            branch_configs = [
                ('North Region', 'NORTH', None),
                ('South Region', 'SOUTH', None),
                ('West Branch', 'WEST', None),
            ]
            
            for name, code, parent_code in branch_configs:
                # Check if exists
                existing = self.execute('ops.branch', 'search', [('code', '=', code)])
                if existing:
                    branches[code.lower()] = existing[0]
                    print(f"   ✓ {name} already exists (ID: {branches[code.lower()]})")
                    continue
                
                # Create analytic account first
                analytic_id = self.execute('account.analytic.account', 'create', {
                    'name': name,
                    'code': code,
                    'company_id': company_id,
                })
                
                # Create branch
                branch_data = {
                    'name': name,
                    'code': code,
                    'company_id': company_id,
                    'analytic_account_id': analytic_id,
                    'active': True
                }
                
                if parent_code and parent_code.lower() in branches:
                    branch_data['parent_id'] = branches[parent_code.lower()]
                
                branch_id = self.execute('ops.branch', 'create', branch_data)
                branches[code.lower()] = branch_id
                print(f"   ✓ Created {name} (ID: {branch_id})")
                self.stats['branches'] += 1
            
            return branches
            
        except Exception as e:
            print(f"   ⚠ Error in branch creation: {str(e)[:150]}")
            return branches if branches else None
    
    def create_business_units(self):
        """Phase 1b: Create Business Units"""
        print("\n🏢 Phase 1b: Creating Business Units...")
        
        business_units = {}
        company_id = self.get_company_id()
        
        try:
            # Check if Corporate Operations exists from post_init_hook
            existing_bu = self.execute('ops.business.unit', 'search', [('code', '=', 'CORP')])
            if existing_bu:
                business_units['corp'] = existing_bu[0]
                print(f"   ✓ Corporate Operations exists (ID: {business_units['corp']})")
                self.stats['business_units'] += 1
            
            # Create additional business units
            bu_configs = [
                ('Sales Division', 'SALES'),
                ('Operations Division', 'OPS'),
                ('Finance Division', 'FIN'),
            ]
            
            for name, code in bu_configs:
                existing = self.execute('ops.business.unit', 'search', [('code', '=', code)])
                if existing:
                    business_units[code.lower()] = existing[0]
                    print(f"   ✓ {name} already exists")
                    continue
                
                bu_id = self.execute('ops.business.unit', 'create', {
                    'name': name,
                    'code': code,
                    'company_id': company_id,
                    'active': True
                })
                business_units[code.lower()] = bu_id
                print(f"   ✓ Created {name} (ID: {bu_id})")
                self.stats['business_units'] += 1
            
            return business_units
            
        except Exception as e:
            print(f"   ⚠ Error in business unit creation: {str(e)[:150]}")
            return business_units if business_units else None
    
    def create_users_and_personas(self, branches):
        """Phase 2: Create User Personas"""
        print("\n👥 Phase 2: Creating User Personas...")
        
        users = {}
        company_id = self.get_company_id()
        
        user_configs = [
            ('user_sales', 'Sales Manager', 'Sales Operations'),
            ('user_logistics', 'Warehouse Manager', 'Logistics Coordinator'),
            ('user_accountant', 'Senior Accountant', 'Financial Controller'),
            ('user_purchaser', 'Purchasing Officer', 'Procurement Specialist'),
            ('user_approver', 'Operations Approver', 'Operations Director'),
        ]
        
        for login, name, persona_name in user_configs:
            try:
                # Check if user exists
                existing = self.execute('res.users', 'search', [('login', '=', login)])
                if existing:
                    users[login] = existing[0]
                    print(f"   ✓ User {login} exists (updating password)")
                    self.execute('res.users', 'write', [existing[0]], {'password': '123'})
                else:
                    user_data = {
                        'name': name,
                        'login': login,
                        'password': '123',
                        'email': f'{login}@opsdemo.com',
                        'company_id': company_id,
                    }
                    
                    users[login] = self.execute('res.users', 'create', user_data)
                    print(f"   ✓ Created {name} (Login: {login} / Password: 123)")
                    self.stats['users'] += 1
                
                # Create OPS Persona
                persona_existing = self.execute('ops.persona', 'search', 
                                                [('code', '=', login.upper())])
                if not persona_existing:
                    persona_data = {
                        'name': persona_name,
                        'code': login.upper(),
                        'user_id': users[login],
                        'active': True,
                    }
                    
                    # Add branch if available
                    if branches and 'main' in branches:
                        persona_data['branch_id'] = branches['main']
                    
                    self.execute('ops.persona', 'create', persona_data)
                    print(f"      → Created OPS Persona: {persona_name}")
                    self.stats['personas'] += 1
                    
            except Exception as e:
                print(f"   ⚠ Error with user {login}: {str(e)[:100]}")
        
        return users
    
    def create_products(self):
        """Phase 3: Create Master Products with proper fields"""
        print("\n📦 Phase 3: Creating Master Products...")
        
        products = {}
        company_id = self.get_company_id()
        
        # Get default category
        try:
            categ_ids = self.execute('product.category', 'search', [], {'limit': 1})
            default_categ = categ_ids[0] if categ_ids else False
        except:
            default_categ = False
        
        # Get default UOM
        try:
            uom_ids = self.execute('uom.uom', 'search', [('name', '=', 'Units')], {'limit': 1})
            default_uom = uom_ids[0] if uom_ids else 1
        except:
            default_uom = 1
        
        product_configs = [
            ('Laptop Pro X1', 'product', 2500.0, 1500.0, 'High-end business laptop'),
            ('Wireless Mouse', 'consu', 25.0, 10.0, 'Ergonomic wireless mouse'),
            ('IT Support Contract', 'service', 1200.0, 800.0, 'Annual IT support'),
            ('Office Desk Premium', 'product', 650.0, 350.0, 'Premium office furniture'),
            ('Consulting Hour', 'service', 150.0, 100.0, 'Professional consulting'),
            ('Network Router', 'product', 450.0, 250.0, 'Enterprise network equipment'),
            ('Software License', 'service', 300.0, 200.0, 'Annual software license'),
            ('LED Monitor 27"', 'product', 350.0, 200.0, 'Full HD LED monitor'),
            ('Wireless Keyboard', 'consu', 45.0, 20.0, 'Bluetooth keyboard'),
            ('Cloud Storage 1TB', 'service', 120.0, 80.0, 'Annual cloud storage'),
        ]
        
        for name, prod_type, sale_price, cost_price, description in product_configs:
            try:
                # Check if product exists
                existing = self.execute('product.product', 'search', 
                                       [('name', '=', name)], {'limit': 1})
                if existing:
                    products[name] = existing[0]
                    print(f"   ✓ {name} already exists")
                    continue
                
                product_data = {
                    'name': name,
                    'type': prod_type,
                    'list_price': sale_price,
                    'standard_price': cost_price,
                    'description': description,
                    'purchase_ok': True,
                    'sale_ok': True,
                    'uom_id': default_uom,
                    'uom_po_id': default_uom,
                    'company_id': company_id,
                }
                
                if default_categ:
                    product_data['categ_id'] = default_categ
                
                product_id = self.execute('product.product', 'create', product_data)
                products[name] = product_id
                print(f"   ✓ Created {name} (${sale_price})")
                self.stats['products'] += 1
                
            except Exception as e:
                print(f"   ⚠ Error creating {name}: {str(e)[:100]}")
        
        return products
    
    def create_partners(self, branches):
        """Phase 4: Create Partners (Vendors & Customers)"""
        print("\n🤝 Phase 4: Creating Business Partners...")
        
        partners = {'vendors': [], 'customers': []}
        company_id = self.get_company_id()
        
        # Create Vendors
        vendor_configs = [
            ('Tech Supplies Global', True),
            ('Office Furniture Direct', True),
            ('IT Equipment Corp', True),
            ('Software Solutions Ltd', True),
        ]
        
        for vendor_name, is_company in vendor_configs:
            try:
                # Check if exists
                existing = self.execute('res.partner', 'search', 
                                       [('name', '=', vendor_name)], {'limit': 1})
                if existing:
                    partners['vendors'].append(existing[0])
                    print(f"   ✓ Vendor {vendor_name} exists")
                    continue
                
                vendor_data = {
                    'name': vendor_name,
                    'is_company': is_company,
                    'email': f'{vendor_name.lower().replace(" ", "")[:20]}@vendor.com',
                    'phone': '+1-555-0100',
                    'company_type': 'company' if is_company else 'person',
                    'company_id': company_id,
                }
                
                vendor_id = self.execute('res.partner', 'create', vendor_data)
                partners['vendors'].append(vendor_id)
                print(f"   ✓ Created Vendor: {vendor_name}")
                self.stats['partners'] += 1
                
            except Exception as e:
                print(f"   ⚠ Error creating vendor {vendor_name}: {str(e)[:80]}")
        
        # Create Customers
        customer_configs = [
            ('Acme Corporation Ltd', True),
            ('Global Industries Inc', True),
            ('Tech Innovators LLC', False),
            ('Enterprise Solutions Co', True),
            ('Digital Services Group', False),
            ('Manufacturing Plus Inc', True),
            ('Retail Chain Express', True),
            ('Finance Solutions Ltd', True),
        ]
        
        for customer_name, is_company in customer_configs:
            try:
                existing = self.execute('res.partner', 'search', 
                                       [('name', '=', customer_name)], {'limit': 1})
                if existing:
                    partners['customers'].append(existing[0])
                    print(f"   ✓ Customer {customer_name} exists")
                    continue
                
                customer_data = {
                    'name': customer_name,
                    'is_company': is_company,
                    'email': f'{customer_name.lower().replace(" ", "")[:20]}@customer.com',
                    'phone': '+1-555-0200',
                    'company_type': 'company' if is_company else 'person',
                    'company_id': company_id,
                }
                
                customer_id = self.execute('res.partner', 'create', customer_data)
                partners['customers'].append(customer_id)
                print(f"   ✓ Created Customer: {customer_name}")
                self.stats['partners'] += 1
                
            except Exception as e:
                print(f"   ⚠ Error creating customer {customer_name}: {str(e)[:80]}")
        
        return partners
    
    def create_purchase_flow(self, products, partners, users):
        """Phase 5: Purchasing Flow"""
        print("\n🛒 Phase 5: Creating Purchase Orders...")
        
        if not products or not partners.get('vendors'):
            print("   ⚠ Missing products or vendors, skipping...")
            return
        
        company_id = self.get_company_id()
        purchaser = users.get('user_purchaser', self.uid)
        
        # Get product storable products
        storable_products = {k: v for k, v in products.items() 
                            if 'Laptop' in k or 'Desk' in k or 'Router' in k or 'Monitor' in k}
        
        if not storable_products:
            print("   ⚠ No storable products found")
            return
        
        # Create 3 Purchase Orders
        po_configs = [
            ('Laptop Pro X1', 25, 1500.0),
            ('Office Desk Premium', 15, 350.0),
            ('LED Monitor 27"', 30, 200.0),
        ]
        
        for idx, (product_name, qty, price) in enumerate(po_configs, 1):
            if product_name not in products:
                continue
            
            try:
                vendor = partners['vendors'][idx % len(partners['vendors'])]
                
                po_id = self.execute('purchase.order', 'create', {
                    'partner_id': vendor,
                    'user_id': purchaser,
                    'company_id': company_id,
                    'order_line': [(0, 0, {
                        'product_id': products[product_name],
                        'product_qty': qty,
                        'price_unit': price,
                    })]
                })
                
                # Confirm PO
                self.execute('purchase.order', 'button_confirm', [[po_id]])
                total = qty * price
                print(f"   ✓ PO #{idx}: {qty}x {product_name} = ${total:,.2f}")
                self.stats['purchase_orders'] += 1
                self.stats['expenses'] += total
                
                # Receive stock for first 2 POs
                if idx <= 2:
                    po_data = self.execute('purchase.order', 'read', [po_id], ['picking_ids'])
                    if po_data[0].get('picking_ids'):
                        for picking_id in po_data[0]['picking_ids']:
                            try:
                                picking = self.execute('stock.picking', 'read', 
                                                      [picking_id], ['move_ids', 'state'])
                                if picking[0]['state'] not in ('done', 'cancel'):
                                    for move_id in picking[0]['move_ids']:
                                        self.execute('stock.move', 'write', 
                                                   [[move_id]], {'quantity_done': qty})
                                    self.execute('stock.picking', 'button_validate', [[picking_id]])
                                    self.stats['stock_moves'] += qty
                                    print(f"      → Received {qty} units")
                            except Exception as e:
                                print(f"      ⚠ Receipt error: {str(e)[:60]}")
                
            except Exception as e:
                print(f"   ⚠ Error in PO #{idx}: {str(e)[:80]}")
    
    def create_sales_flow(self, products, partners, users):
        """Phase 6: Sales Orders"""
        print("\n💰 Phase 6: Creating Sales Orders...")
        
        if not products or not partners.get('customers'):
            print("   ⚠ Missing products or customers, skipping...")
            return
        
        company_id = self.get_company_id()
        sales_user = users.get('user_sales', self.uid)
        customers = partners['customers']
        product_list = list(products.items())
        
        # Create 20 sales orders
        for i in range(1, 21):
            try:
                customer = customers[i % len(customers)]
                product_name, product_id = product_list[i % len(product_list)]
                
                # Get product price
                prod_data = self.execute('product.product', 'read', 
                                        [product_id], ['list_price'])
                price = prod_data[0]['list_price']
                qty = (i % 5) + 1  # Quantities from 1 to 5
                
                # Create SO
                so_id = self.execute('sale.order', 'create', {
                    'partner_id': customer,
                    'user_id': sales_user,
                    'company_id': company_id,
                    'order_line': [(0, 0, {
                        'product_id': product_id,
                        'product_uom_qty': qty,
                        'price_unit': price,
                    })]
                })
                
                # Confirm SO
                self.execute('sale.order', 'action_confirm', [[so_id]])
                order_total = price * qty
                self.stats['sales_orders'] += 1
                self.stats['revenue'] += order_total
                
                print(f"   ✓ SO #{i}: {qty}x {product_name[:25]} = ${order_total:,.2f}")
                
                # Deliver first 15 orders
                if i <= 15:
                    so_data = self.execute('sale.order', 'read', [so_id], ['picking_ids'])
                    if so_data[0].get('picking_ids'):
                        for picking_id in so_data[0]['picking_ids']:
                            try:
                                picking = self.execute('stock.picking', 'read', 
                                                      [picking_id], ['move_ids', 'state'])
                                if picking[0]['state'] not in ('done', 'cancel'):
                                    for move_id in picking[0]['move_ids']:
                                        self.execute('stock.move', 'write', 
                                                   [[move_id]], {'quantity_done': qty})
                                    self.execute('stock.picking', 'button_validate', [[picking_id]])
                                    self.stats['stock_moves'] += qty
                            except:
                                pass  # Service products don't have pickings
                    
                    # Create Invoice for first 15
                    try:
                        result = self.execute('sale.order', '_create_invoices', [[so_id]])
                        if result:
                            invoice_ids = result if isinstance(result, list) else [result]
                            for invoice_id in invoice_ids:
                                self.execute('account.move', 'action_post', [[invoice_id]])
                                self.stats['invoices'] += 1
                                
                                # Register payment for first 10
                                if i <= 10:
                                    journals = self.execute('account.journal', 'search', 
                                                          [('type', '=', 'bank')], {'limit': 1})
                                    if journals:
                                        payment_id = self.execute('account.payment', 'create', {
                                            'payment_type': 'inbound',
                                            'partner_type': 'customer',
                                            'partner_id': customer,
                                            'amount': order_total,
                                            'journal_id': journals[0],
                                            'date': datetime.now().strftime('%Y-%m-%d'),
                                        })
                                        self.execute('account.payment', 'action_post', [[payment_id]])
                                        self.stats['payments'] += 1
                    except Exception as e:
                        pass  # Invoice might fail for services
                        
            except Exception as e:
                print(f"   ⚠ Error in SO #{i}: {str(e)[:60]}")
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*70)
        print("🎉 DATA FACTORY EXECUTION COMPLETE")
        print("="*70)
        
        print("\n📊 INFRASTRUCTURE STATISTICS:")
        print(f"   • Branches Created: {self.stats['branches']}")
        print(f"   • Business Units Created: {self.stats['business_units']}")
        print(f"   • Users Created: {self.stats['users']}")
        print(f"   • Personas Created: {self.stats['personas']}")
        print(f"   • Products Created: {self.stats['products']}")
        print(f"   • Partners Created: {self.stats['partners']}")
        
        print("\n📈 TRANSACTIONAL DATA:")
        print(f"   • Purchase Orders: {self.stats['purchase_orders']}")
        print(f"   • Sales Orders: {self.stats['sales_orders']}")
        print(f"   • Invoices Generated: {self.stats['invoices']}")
        print(f"   • Payments Received: {self.stats['payments']}")
        print(f"   • Stock Moves Processed: {self.stats['stock_moves']}")
        
        print("\n💰 FINANCIAL SUMMARY:")
        print(f"   • Total Revenue: ${self.stats['revenue']:,.2f}")
        print(f"   • Total Expenses: ${self.stats['expenses']:,.2f}")
        print(f"   • Net Income: ${self.stats['revenue'] - self.stats['expenses']:,.2f}")
        print(f"   • Unpaid Invoices: {self.stats['invoices'] - self.stats['payments']}")
        
        print("\n👤 USER CREDENTIALS (Password: 123 for all):")
        print("   • admin / admin - System Administrator")
        print("   • user_accountant / 123 - Financial Reports")
        print("   • user_sales / 123 - Sales Management")
        print("   • user_logistics / 123 - Warehouse Operations")
        print("   • user_purchaser / 123 - Purchase Management")
        print("   • user_approver / 123 - Approval Workflows")
        
        print("\n🌐 ACCESS:")
        print(f"   URL: {self.url}")
        print("   Database: mz-db")
        
        print("\n" + "="*70)

def main():
    """Main execution"""
    factory = OdooDataFactory()
    
    if not factory.connect():
        sys.exit(1)
    
    try:
        print("\n" + "="*70)
        print("🚀 STARTING DATA FACTORY - OPS FRAMEWORK FULL DEMO")
        print("="*70)
        
        # Phase 1: Infrastructure
        branches = factory.create_branch_structure()
        business_units = factory.create_business_units()
        
        # Phase 2: Users & Personas
        users = factory.create_users_and_personas(branches)
        
        # Phase 3: Master Data
        products = factory.create_products()
        partners = factory.create_partners(branches)
        
        # Phase 4-6: Transactional Data
        factory.create_purchase_flow(products, partners, users)
        factory.create_sales_flow(products, partners, users)
        
        # Final Summary
        factory.print_summary()
        
        print("\n✅ SUCCESS: Database populated with comprehensive demo data!")
        print("   You can now log in and explore the fully functional system.")
        print("   All data is visible and ready for inspection.\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
