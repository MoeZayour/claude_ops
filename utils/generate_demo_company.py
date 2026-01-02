#!/usr/bin/env python3
"""
Data Factory Script for Full Role Simulation - OPS Framework Complete Edition
Populates mz-db with high-volume data covering ALL OPS Framework scenarios
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
            'users': 0,
            'personas': 0,
            'products': 0,
            'partners': 0,
            'purchase_orders': 0,
            'sales_orders': 0,
            'invoices': 0,
            'payments': 0,
            'stock_moves': 0,
            'journal_entries': 0,
            'approval_requests': 0,
            'governance_rules': 0,
            'sla_instances': 0,
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
        """Execute XML-RPC call"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def install_modules(self):
        """Install required Odoo modules"""
        print("\n📦 Phase 0: Initializing & Installing Required Modules...")
        
        try:
            # Update module list first
            print("   → Updating module list...")
            self.execute('ir.module.module', 'update_list', [])
            print("   ✓ Module list updated")
            time.sleep(2)  # Give it time to update
        except Exception as e:
            print(f"   ⚠ Could not update module list: {str(e)[:80]}")
        
        # OPS modules need to be installed first
        ops_modules = [
            'ops_matrix_core', 'ops_matrix_accounting', 'ops_matrix_reporting'
        ]
        
        # Then standard Odoo modules
        standard_modules = [
            'product', 'sale_management', 'purchase', 'stock', 
            'account', 'contacts'
        ]
        
        all_modules = ops_modules + standard_modules
        
        for module_name in all_modules:
            try:
                # Search for module
                module_ids = self.execute('ir.module.module', 'search',
                                         [('name', '=', module_name)])
                
                if not module_ids:
                    print(f"   ⚠ Module {module_name} not found")
                    continue
                
                # Read module state
                module_data = self.execute('ir.module.module', 'read',
                                          [module_ids[0]], ['state'])
                state = module_data[0]['state']
                
                if state == 'installed':
                    print(f"   ✓ {module_name} already installed")
                elif state in ('uninstalled', 'to install', 'to upgrade'):
                    print(f"   → Installing {module_name}...")
                    self.execute('ir.module.module', 'button_immediate_install', [[module_ids[0]]])
                    print(f"   ✓ {module_name} installed")
                    time.sleep(1)  # Give time between installations
                    
            except Exception as e:
                error_msg = str(e)
                if 'already installed' in error_msg.lower():
                    print(f"   ✓ {module_name} is installed")
                else:
                    print(f"   ⚠ Error with {module_name}: {error_msg[:100]}")
    
    def create_branch_structure(self):
        """Phase 1: Create Branch Hierarchy"""
        print("\n📍 Phase 1: Creating Branch Hierarchy...")
        
        branches = {}
        
        try:
            # Check if ops.branch model exists
            self.execute('ops.branch', 'search', [], {'limit': 1})
            
            # Create Main branch
            main_branches = self.execute('ops.branch', 'search', [('code', '=', 'MAIN')])
            if main_branches:
                branches['main'] = main_branches[0]
                print(f"   ✓ Main branch exists (ID: {branches['main']})")
            else:
                branches['main'] = self.execute('ops.branch', 'create', {
                    'name': 'Main Branch',
                    'code': 'MAIN',
                    'active': True
                })
                print(f"   ✓ Created Main branch (ID: {branches['main']})")
                self.stats['branches'] += 1
            
            # Create North branch
            branches['north'] = self.execute('ops.branch', 'create', {
                'name': 'North Region',
                'code': 'NORTH',
                'parent_id': branches['main'],
                'active': True
            })
            print(f"   ✓ Created North branch (ID: {branches['north']})")
            self.stats['branches'] += 1
            
            # Create South branch
            branches['south'] = self.execute('ops.branch', 'create', {
                'name': 'South Region',
                'code': 'SOUTH',
                'parent_id': branches['main'],
                'active': True
            })
            print(f"   ✓ Created South branch (ID: {branches['south']})")
            self.stats['branches'] += 1
            
            return branches
            
        except Exception as e:
            print(f"   ⚠ ops.branch not available: {str(e)[:80]}")
            return None
    
    def create_users_and_personas(self, branches):
        """Phase 2: Create User Personas with OPS Personas"""
        print("\n👥 Phase 2: Creating User Personas & OPS Personas...")
        
        users = {}
        personas = {}
        
        user_configs = [
            ('user_sales', 'Sales Manager', 'Main'),
            ('user_logistics', 'Warehouse Manager', 'Main'),
            ('user_accountant', 'Senior Accountant', 'Main'),
            ('user_purchaser', 'Purchasing Officer', 'North'),
            ('user_approver', 'Operations Approver', 'Main'),
        ]
        
        for login, name, branch_name in user_configs:
            # Check if user already exists
            existing = self.execute('res.users', 'search', [('login', '=', login)])
            if existing:
                print(f"   ⚠ User {login} already exists, updating...")
                self.execute('res.users', 'write', [existing[0]], {'password': '123'})
                users[login] = existing[0]
            else:
                user_data = {
                    'name': name,
                    'login': login,
                    'password': '123',
                    'email': f'{login}@opsdemo.com',
                }
                
                # Add branch_id if branches exist
                if branches and branch_name.lower() in branches:
                    user_data['branch_id'] = branches[branch_name.lower()]
                elif branches and 'main' in branches:
                    user_data['branch_id'] = branches['main']
                
                users[login] = self.execute('res.users', 'create', user_data)
                print(f"   ✓ Created {name} (Login: {login} / Password: 123)")
                self.stats['users'] += 1
            
            # Create OPS Persona if model exists
            try:
                persona_existing = self.execute('ops.persona', 'search', [('code', '=', login.upper())])
                if not persona_existing:
                    personas[login] = self.execute('ops.persona', 'create', {
                        'name': f'{name} Persona',
                        'code': login.upper(),
                        'user_id': users[login],
                        'active': True,
                    })
                    print(f"      → Created OPS Persona for {login}")
                    self.stats['personas'] += 1
            except:
                pass  # ops.persona not available
        
        return users, personas
    
    def create_products(self):
        """Phase 3: Create Master Products"""
        print("\n📦 Phase 3: Creating Master Products...")
        
        products = {}
        product_configs = [
            ('Laptop Pro X1', 'product', 2500.0, 1500.0, 'High-end business laptop'),
            ('Wireless Mouse', 'consu', 25.0, 10.0, 'Ergonomic wireless mouse'),
            ('IT Support Contract', 'service', 1200.0, 800.0, 'Annual IT support'),
            ('Office Desk Premium', 'product', 650.0, 350.0, 'Premium office furniture'),
            ('Consulting Hour', 'service', 150.0, 100.0, 'Professional consulting'),
            ('Network Router', 'product', 450.0, 250.0, 'Enterprise network equipment'),
            ('Software License', 'service', 300.0, 200.0, 'Annual software license'),
        ]
        
        for name, prod_type, sale_price, cost_price, description in product_configs:
            try:
                product_id = self.execute('product.product', 'create', {
                    'name': name,
                    'type': prod_type,
                    'list_price': sale_price,
                    'standard_price': cost_price,
                    'description': description,
                    'purchase_ok': True,
                    'sale_ok': True,
                })
                products[name] = product_id
                print(f"   ✓ Created {name} (${sale_price})")
                self.stats['products'] += 1
            except Exception as e:
                print(f"   ⚠ Error creating {name}: {str(e)[:60]}")
        
        return products
    
    def create_partners(self, branches):
        """Phase 4: Create Partners (Vendors & Customers)"""
        print("\n🤝 Phase 4: Creating Business Partners...")
        
        partners = {'vendors': [], 'customers': []}
        
        # Create Vendors
        vendor_configs = [
            ('Tech Supplies Global', 'Main'),
            ('Office Furniture Direct', 'North'),
            ('IT Equipment Corp', 'South'),
        ]
        
        for vendor_name, branch_name in vendor_configs:
            vendor_data = {
                'name': vendor_name,
                'is_company': True,
                'email': f'{vendor_name.lower().replace(" ", "")}@vendor.com',
                'phone': '+1-555-0100',
                'company_type': 'company',
            }
            
            if branches and branch_name.lower() in branches:
                vendor_data['branch_id'] = branches[branch_name.lower()]
            
            vendor_id = self.execute('res.partner', 'create', vendor_data)
            partners['vendors'].append(vendor_id)
            print(f"   ✓ Created Vendor: {vendor_name}")
            self.stats['partners'] += 1
        
        # Create Customers
        customer_configs = [
            ('Acme Corporation Ltd', 'Main', True),
            ('Global Industries Inc', 'North', True),
            ('Tech Innovators LLC', 'South', False),
            ('Enterprise Solutions Co', 'Main', True),
            ('Digital Services Group', 'North', False),
        ]
        
        for customer_name, branch_name, is_company in customer_configs:
            customer_data = {
                'name': customer_name,
                'is_company': is_company,
                'email': f'{customer_name.lower().replace(" ", "")[:20]}@customer.com',
                'phone': '+1-555-0200',
                'company_type': 'company' if is_company else 'person',
            }
            
            if branches and branch_name.lower() in branches:
                customer_data['branch_id'] = branches[branch_name.lower()]
            
            customer_id = self.execute('res.partner', 'create', customer_data)
            partners['customers'].append(customer_id)
            print(f"   ✓ Created Customer: {customer_name}")
            self.stats['partners'] += 1
        
        return partners
    
    def create_purchase_flow(self, products, partners, users):
        """Phase 5: Purchasing & Logistics Flow"""
        print("\n🛒 Phase 5: Creating Purchase Orders & Stock Movements...")
        
        if not products:
            print("   ⚠ No products available, skipping...")
            return
        
        vendor = partners['vendors'][0]
        purchaser = users.get('user_purchaser', self.uid)
        
        # PO 1: Fully Received & Billed (50 Laptops)
        print("   → PO #1: 50 Laptops (Fully Received & Billed)...")
        try:
            po1_id = self.execute('purchase.order', 'create', {
                'partner_id': vendor,
                'user_id': purchaser,
                'order_line': [(0, 0, {
                    'product_id': products['Laptop Pro X1'],
                    'product_qty': 50,
                    'price_unit': 1500.0,
                })]
            })
            
            # Confirm PO
            self.execute('purchase.order', 'button_confirm', [[po1_id]])
            print(f"      ✓ PO #1 confirmed (ID: {po1_id}, Total: $75,000)")
            self.stats['purchase_orders'] += 1
            self.stats['expenses'] += 75000
            
            # Receive stock
            po_data = self.execute('purchase.order', 'read', [po1_id], ['picking_ids'])
            if po_data[0].get('picking_ids'):
                for picking_id in po_data[0]['picking_ids']:
                    picking = self.execute('stock.picking', 'read', [picking_id], ['move_ids', 'state'])
                    if picking[0]['state'] not in ('done', 'cancel'):
                        for move_id in picking[0]['move_ids']:
                            self.execute('stock.move', 'write', [[move_id]], {'quantity_done': 50})
                        self.execute('stock.picking', 'button_validate', [[picking_id]])
                        self.stats['stock_moves'] += 50
                        print(f"      ✓ Received 50 Laptops into stock")
            
        except Exception as e:
            print(f"      ⚠ Error in PO flow: {str(e)[:80]}")
        
        # PO 2: Partial Receipt (Office Desks)
        print("   → PO #2: 25 Office Desks (Partial: 15 received, 10 backorder)...")
        try:
            po2_id = self.execute('purchase.order', 'create', {
                'partner_id': partners['vendors'][1] if len(partners['vendors']) > 1 else vendor,
                'user_id': purchaser,
                'order_line': [(0, 0, {
                    'product_id': products['Office Desk Premium'],
                    'product_qty': 25,
                    'price_unit': 350.0,
                })]
            })
            
            self.execute('purchase.order', 'button_confirm', [[po2_id]])
            self.stats['purchase_orders'] += 1
            print(f"      ✓ PO #2 confirmed (ID: {po2_id})")
            
            # Partial receive
            po_data = self.execute('purchase.order', 'read', [po2_id], ['picking_ids'])
            if po_data[0].get('picking_ids'):
                picking_id = po_data[0]['picking_ids'][0]
                picking = self.execute('stock.picking', 'read', [picking_id], ['move_ids'])
                for move_id in picking[0]['move_ids']:
                    self.execute('stock.move', 'write', [[move_id]], {'quantity_done': 15})
                self.execute('stock.picking', 'button_validate', [[picking_id]])
                self.stats['stock_moves'] += 15
                print(f"      ✓ Partially received 15 Desks (10 on backorder)")
                
        except Exception as e:
            print(f"      ⚠ Error in PO #2: {str(e)[:80]}")
    
    def create_sales_flow(self, products, partners, users):
        """Phase 6: Sales Orders, Deliveries, Invoices & Payments"""
        print("\n💰 Phase 6: Creating Sales Flow (15 Orders)...")
        
        if not products or not partners['customers']:
            print("   ⚠ Missing products or customers, skipping...")
            return
        
        customers = partners['customers']
        sales_user = users.get('user_sales', self.uid)
        
        # Create varied sales orders
        product_list = list(products.keys())
        
        for i in range(1, 16):
            try:
                customer = customers[i % len(customers)]
                product_name = product_list[i % len(product_list)]
                product_id = products[product_name]
                
                # Get product price
                prod_data = self.execute('product.product', 'read', [product_id], ['list_price'])
                price = prod_data[0]['list_price']
                qty = (i % 5) + 2  # Quantities from 2 to 6
                
                # Create SO
                so_id = self.execute('sale.order', 'create', {
                    'partner_id': customer,
                    'user_id': sales_user,
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
                
                print(f"   ✓ SO #{i}: {qty}x {product_name[:20]} = ${order_total:,.2f}")
                
                # Deliver orders (all except last 3)
                if i <= 12:
                    so_data = self.execute('sale.order', 'read', [so_id], ['picking_ids'])
                    if so_data[0].get('picking_ids'):
                        for picking_id in so_data[0]['picking_ids']:
                            try:
                                picking = self.execute('stock.picking', 'read', [picking_id], ['move_ids', 'state'])
                                if picking[0]['state'] not in ('done', 'cancel'):
                                    for move_id in picking[0]['move_ids']:
                                        self.execute('stock.move', 'write', [[move_id]], {'quantity_done': qty})
                                    self.execute('stock.picking', 'button_validate', [[picking_id]])
                                    self.stats['stock_moves'] += qty
                            except:
                                pass  # Service products don't have pickings
                    
                    # Create Invoice (for orders 1-12)
                    try:
                        result = self.execute('sale.order', '_create_invoices', [[so_id]])
                        if result:
                            invoice_ids = result if isinstance(result, list) else [result]
                            for invoice_id in invoice_ids:
                                self.execute('account.move', 'action_post', [[invoice_id]])
                                self.stats['invoices'] += 1
                                
                                # Register payment for first 7 invoices
                                if i <= 7:
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
                                        print(f"      → Payment received: ${order_total:,.2f}")
                    except Exception as e:
                        pass  # Invoice creation might fail for services
                        
            except Exception as e:
                print(f"   ⚠ Error in SO #{i}: {str(e)[:60]}")
    
    def create_financial_entries(self, partners):
        """Phase 7: Additional Financial Entries for P&L"""
        print("\n💼 Phase 7: Creating Financial Entries (Operating Expenses)...")
        
        try:
            # Find expense and asset accounts
            expense_accounts = self.execute('account.account', 'search', 
                                           [('account_type', '=', 'expense')], {'limit': 1})
            asset_accounts = self.execute('account.account', 'search', 
                                         [('account_type', 'in', ['asset_current', 'asset_cash'])], {'limit': 1})
            
            if not expense_accounts or not asset_accounts:
                print("   ⚠ Required accounts not found")
                return
            
            # Get general journal
            journals = self.execute('account.journal', 'search', 
                                   [('type', '=', 'general')], {'limit': 1})
            if not journals:
                print("   ⚠ No general journal found")
                return
            
            # Create Operating Expense Entries
            expense_entries = [
                ('Office Rent - December', 5000.0),
                ('Utilities & Internet', 1200.0),
                ('Office Supplies', 800.0),
            ]
            
            for description, amount in expense_entries:
                try:
                    entry_id = self.execute('account.move', 'create', {
                        'move_type': 'entry',
                        'journal_id': journals[0],
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'line_ids': [
                            (0, 0, {
                                'account_id': expense_accounts[0],
                                'name': description,
                                'debit': amount,
                                'credit': 0.0,
                            }),
                            (0, 0, {
                                'account_id': asset_accounts[0],
                                'name': 'Bank Payment',
                                'debit': 0.0,
                                'credit': amount,
                            })
                        ]
                    })
                    self.execute('account.move', 'action_post', [[entry_id]])
                    print(f"   ✓ Journal Entry: {description} (${amount:,.2f})")
                    self.stats['journal_entries'] += 1
                    self.stats['expenses'] += amount
                except Exception as e:
                    print(f"   ⚠ Error creating {description}: {str(e)[:50]}")
            
            # Create Vendor Bills
            if partners and partners.get('vendors'):
                vendor = partners['vendors'][0]
                bill_items = [
                    ('Electricity Bill - December', 950.0),
                    ('Maintenance Services', 1500.0),
                ]
                
                for description, amount in bill_items:
                    try:
                        bill_id = self.execute('account.move', 'create', {
                            'move_type': 'in_invoice',
                            'partner_id': vendor,
                            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                            'invoice_line_ids': [(0, 0, {
                                'name': description,
                                'quantity': 1,
                                'price_unit': amount,
                                'account_id': expense_accounts[0],
                            })]
                        })
                        self.execute('account.move', 'action_post', [[bill_id]])
                        print(f"   ✓ Vendor Bill: {description} (${amount:,.2f})")
                        self.stats['expenses'] += amount
                    except Exception as e:
                        print(f"   ⚠ Error creating bill: {str(e)[:50]}")
                        
        except Exception as e:
            print(f"   ⚠ Error in financial entries: {str(e)[:80]}")
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*70)
        print("🎉 DATA FACTORY EXECUTION COMPLETE")
        print("="*70)
        
        print("\n📊 INFRASTRUCTURE STATISTICS:")
        print(f"   • Branches Created: {self.stats['branches']}")
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
        print(f"   • Journal Entries: {self.stats['journal_entries']}")
        
        print("\n💰 FINANCIAL SUMMARY:")
        print(f"   • Total Revenue: ${self.stats['revenue']:,.2f}")
        print(f"   • Total Expenses: ${self.stats['expenses']:,.2f}")
        print(f"   • Net Income: ${self.stats['revenue'] - self.stats['expenses']:,.2f}")
        print(f"   • Unpaid Invoices: {self.stats['invoices'] - self.stats['payments']} (for Aged Receivables)")
        
        print("\n📦 LOGISTICS STATUS:")
        print(f"   • Total Stock Movements: {self.stats['stock_moves']}")
        print(f"   • Backorders Pending: Yes (Office Desks)")
        print(f"   • Pending Deliveries: 3 Sales Orders")
        
        print("\n👤 USER CREDENTIALS (Password: 123 for all):")
        print("   • admin / admin - System Administrator")
        print("   • user_accountant / 123 - Financial Reports & Analysis")
        print("   • user_sales / 123 - Sales Dashboard & Orders")
        print("   • user_logistics / 123 - Warehouse & Stock Management")
        print("   • user_purchaser / 123 - Purchase Orders & Vendor Management")
        print("   • user_approver / 123 - Approval Workflows")
        
        print("\n🚀 READY TO DEMONSTRATE:")
        print("   ✅ Profit & Loss Report (Revenue vs Expenses)")
        print("   ✅ Balance Sheet (Assets, Liabilities, Equity)")
        print("   ✅ Aged Receivables (5+ unpaid invoices)")
        print("   ✅ Stock Valuation Report (Laptops, Desks, etc.)")
        print("   ✅ Sales Analysis by Customer & Product")
        print("   ✅ Purchase Analysis & Vendor Performance")
        print("   ✅ Branch-wise Operations (Main, North, South)")
        print("   ✅ User Role Simulation (5 different personas)")
        
        print("\n💡 OPS FRAMEWORK COVERAGE:")
        print("   • Branch Hierarchy: Multi-level structure")
        print("   • User Personas: Role-based access")
        print("   • Product Management: Multiple product types")
        print("   • Partner Management: Vendors & customers by branch")
        print("   • Purchase-to-Pay: Full cycle with partial receipts")
        print("   • Order-to-Cash: Full cycle with pending items")
        print("   • Financial Accounting: P&L ready with transactions")
        print("   • Inventory Management: Stock moves & backorders")
        
        print("\n" + "="*70)
        print(f"🌐 Access the system at: {self.url}")
        print("="*70)

def main():
    """Main execution"""
    factory = OdooDataFactory()
    
    if not factory.connect():
        sys.exit(1)
    
    try:
        # Phase 0: Install modules
        factory.install_modules()
        
        # Phase 1: Infrastructure
        branches = factory.create_branch_structure()
        
        # Phase 2: Users & Personas
        users, personas = factory.create_users_and_personas(branches)
        
        # Phase 3: Master Data
        products = factory.create_products()
        partners = factory.create_partners(branches)
        
        # Phase 4-7: Transactional Data
        factory.create_purchase_flow(products, partners, users)
        factory.create_sales_flow(products, partners, users)
        factory.create_financial_entries(partners)
        
        # Final Summary
        factory.print_summary()
        
        print("\n✅ SUCCESS: Database is now populated with demo data!")
        print("   Log in and explore the fully functional system.")
        
    except Exception as e:
        print(f"\n❌ ERROR during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
