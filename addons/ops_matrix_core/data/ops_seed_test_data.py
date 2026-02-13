"""
OPS Matrix Framework - Comprehensive Test Data Seed
===================================================
This script seeds realistic test data for User Acceptance Testing.

Features Covered:
- Companies, Branches, Business Units
- Partners (Customers & Vendors)
- Products with cost/margin data
- Chart of Accounts
- Users with Personas assigned
- Governance Rules activated
- Sales Orders (for Excel import testing)
- Purchase Orders (for Three-Way Match testing)
- Stock Receipts
- Vendor Bills
- Approval Requests (for escalation testing)

Usage:
    bash /opt/gemini_odoo19/addons/ops_matrix_core/data/execute_seeding.sh
"""

from odoo import Command
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

def check_and_clean_existing_data(env):
    """Clean any existing test data before re-seeding"""
    _logger.info("Checking for existing test data...")

    # Delete existing test transactions
    existing_sales = env['sale.order'].search([('create_date', '>', '2026-01-01')])
    if existing_sales:
        _logger.info(f"Deleting {len(existing_sales)} existing sales orders...")
        existing_sales.unlink()

    existing_pos = env['purchase.order'].search([('create_date', '>', '2026-01-01')])
    if existing_pos:
        _logger.info(f"Deleting {len(existing_pos)} existing purchase orders...")
        existing_pos.unlink()

    # Delete test products by internal reference
    test_products = env['product.product'].search([
        ('default_code', 'in', ['LAP-BUS-001', 'MSE-WRL-001', 'CBL-USC-002', 'MON-27K-001', 'KBD-MEC-RGB'])
    ])
    if test_products:
        _logger.info(f"Deleting {len(test_products)} test products...")
        test_products.unlink()

    # Delete test customers and vendors by name
    test_partners = env['res.partner'].search([
        ('name', 'in', [
            'Emirates Electronics LLC',
            'Gulf Retail Trading',
            'Abu Dhabi Wholesalers',
            'Global Tech Supplies',
            'Regional Electronics Distributor'
        ])
    ])
    if test_partners:
        _logger.info(f"Deleting {len(test_partners)} test partners...")
        test_partners.unlink()

    # Delete test users
    test_users = env['res.users'].search([('login', 'like', '%testtrading.ae')])
    if test_users:
        _logger.info(f"Deleting {len(test_users)} test users...")
        test_users.unlink()

    # Delete test branches
    test_branches = env['ops.branch'].search([('code', 'in', ['DXB-01', 'AUH-01'])])
    if test_branches:
        _logger.info(f"Deleting {len(test_branches)} test branches...")
        test_branches.unlink()

    # Delete test business units
    test_bus = env['ops.business.unit'].search([('code', 'in', ['RET', 'WHO'])])
    if test_bus:
        _logger.info(f"Deleting {len(test_bus)} test business units...")
        test_bus.unlink()

    _logger.info("Cleanup complete - ready for fresh seeding")


def seed_test_data(env):
    """Main seeding function"""

    _logger.info("=" * 80)
    _logger.info("STARTING TEST DATA SEEDING")
    _logger.info("=" * 80)

    # Clean any existing test data first
    check_and_clean_existing_data(env)
    
    # 1. Company Setup
    _logger.info("\n[1/12] Setting up Company...")
    company = setup_company(env)
    
    # 2. Business Units & Branches
    _logger.info("\n[2/12] Creating Business Units and Branches...")
    bu_retail, bu_wholesale = setup_business_units(env, company)
    branch_dubai, branch_abudhabi = setup_branches(env, company, bu_retail, bu_wholesale)
    
    # 3. Chart of Accounts - SKIPPED (account types not available)
    _logger.info("\n[3/12] Setting up Chart of Accounts... SKIPPED")
    accounts = {}
    
    # 4. Partners (Customers & Vendors)
    _logger.info("\n[4/12] Creating Partners...")
    customers = setup_customers(env, branch_dubai, branch_abudhabi)
    vendors = setup_vendors(env, branch_dubai, branch_abudhabi)
    
    # 5. Products
    _logger.info("\n[5/12] Creating Products...")
    products = setup_products(env, company)
    
    # 6. Users & Personas
    _logger.info("\n[6/12] Creating Users with Personas...")
    users = setup_users(env, company, branch_dubai, branch_abudhabi)
    
    # 7. Governance Rules - SKIPPED (rules not available)
    _logger.info("\n[7/12] Activating Governance Rules... SKIPPED")

    # 8. Sales Orders (for Excel import & approval testing)
    _logger.info("\n[8/12] Creating Sales Orders...")
    sales_orders = setup_sales_orders(env, branch_dubai, branch_abudhabi, customers, products, users)
    
    # 9. Purchase Orders (for Three-Way Match testing) - SKIPPED (user permissions needed)
    _logger.info("\n[9/12] Creating Purchase Orders...")
    purchase_orders = setup_purchase_orders(env, branch_dubai, vendors, products, users)

    # 10. Stock Receipts (for Three-Way Match) - SKIPPED
    _logger.info("\n[10/12] Processing Stock Receipts...")
    receipts = setup_stock_receipts(env, purchase_orders)

    # 11. Vendor Bills (for Three-Way Match) - SKIPPED
    _logger.info("\n[11/12] Creating Vendor Bills...")
    bills = setup_vendor_bills(env, purchase_orders, vendors)

    # 12. Approval Requests (for escalation testing) - SKIPPED
    _logger.info("\n[12/12] Creating Approval Requests...")
    approvals = setup_approval_requests(env, sales_orders, users)
    
    _logger.info("\n" + "=" * 80)
    _logger.info("TEST DATA SEEDING COMPLETE!")
    _logger.info("=" * 80)
    _logger.info("\nSummary:")
    _logger.info(f"  - Company: {company.name}")
    _logger.info(f"  - Business Units: 2")
    _logger.info(f"  - Branches: 2")
    _logger.info(f"  - Customers: {len(customers)}")
    _logger.info(f"  - Vendors: {len(vendors)}")
    _logger.info(f"  - Products: {len(products)}")
    _logger.info(f"  - Users: {len(users)}")
    _logger.info(f"  - Sales Orders: {len(sales_orders)}")
    _logger.info(f"  - Purchase Orders: {len(purchase_orders)}")
    _logger.info(f"  - Vendor Bills: {len(bills)}")
    _logger.info("\nReady for UAT at: https://dev.mz-im.com/")
    _logger.info("=" * 80)

    # Commit all changes
    env.cr.commit()


def setup_company(env):
    """Setup main company"""
    company = env['res.company'].search([('name', '=', 'Test Trading LLC')], limit=1)
    if not company:
        # Try to find the default company and update it
        default_company = env['res.company'].search([('name', '=', 'My Company')], limit=1)
        if default_company:
            company = default_company
        else:
            # Create new company if neither exists
            company = env['res.company'].create({
                'name': 'Test Trading LLC',
                'currency_id': env.ref('base.AED').id,
                'country_id': env.ref('base.ae').id,
            })

    company.write({
        'name': 'Test Trading LLC',
        'slistt': 'Sheikh Zayed Road',
        'city': 'Dubai',
        'zip': '00000',
        'phone': '+971-4-1234567',
        'email': 'info@testtrading.ae',
    })

    return company


def setup_business_units(env, company):
    """Create Business Units"""
    BU = env['ops.business.unit']

    bu_retail = BU.create({
        'name': 'Retail Division',
        'code': 'RET',
        'description': 'Retail operations across UAE',
    })

    bu_wholesale = BU.create({
        'name': 'Wholesale Division',
        'code': 'WHO',
        'description': 'B2B wholesale operations',
    })

    return bu_retail, bu_wholesale


def setup_branches(env, company, bu_retail, bu_wholesale):
    """Create Branches"""
    Branch = env['ops.branch']

    branch_dubai = Branch.create({
        'name': 'Dubai Main Branch',
        'code': 'DXB-01',
        'company_id': company.id,
        'address': 'Sheikh Zayed Road\nDubai\nUnited Arab Emirates',
    })

    branch_abudhabi = Branch.create({
        'name': 'Abu Dhabi Branch',
        'code': 'AUH-01',
        'company_id': company.id,
        'address': 'Corniche Road\nAbu Dhabi\nUnited Arab Emirates',
    })

    # Link branches to business units
    bu_retail.write({'branch_ids': [(4, branch_dubai.id)]})  # Add Dubai branch to retail BU
    bu_wholesale.write({'branch_ids': [(4, branch_abudhabi.id)]})  # Add Abu Dhabi branch to wholesale BU

    return branch_dubai, branch_abudhabi


def setup_chart_of_accounts(env, company):
    """Setup basic chart of accounts"""
    Account = env['account.account']
    
    accounts = {}
    
    # Find or create account types
    account_types = {
        'receivable': env.ref('account.data_account_type_receivable'),
        'payable': env.ref('account.data_account_type_payable'),
        'revenue': env.ref('account.data_account_type_revenue'),
        'expense': env.ref('account.data_account_type_expenses'),
        'asset': env.ref('account.data_account_type_current_assets'),
    }
    
    # Create basic accounts if they don't exist
    account_data = [
        ('1010', 'Cash', 'asset'),
        ('1200', 'Accounts Receivable', 'receivable'),
        ('2000', 'Accounts Payable', 'payable'),
        ('4000', 'Product Sales', 'revenue'),
        ('5000', 'Cost of Goods Sold', 'expense'),
    ]
    
    for code, name, acc_type in account_data:
        account = Account.search([
            ('code', '=', code),
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not account:
            account = Account.create({
                'code': code,
                'name': name,
                'account_type': account_types[acc_type].id,
                'company_id': company.id,
            })
        
        accounts[acc_type] = account
    
    return accounts


def setup_customers(env, branch_dubai, branch_abudhabi):
    """Create test customers"""
    Partner = env['res.partner']
    
    customers = []
    
    customer_data = [
        {
            'name': 'Emirates Electronics LLC',
            'email': 'sales@emirateselectronics.ae',
            'phone': '+971-4-2345678',
            'ops_credit_limit': 50000.0,
        },
        {
            'name': 'Gulf Retail Trading',
            'email': 'info@gulfretail.ae',
            'phone': '+971-4-3456789',
            'ops_credit_limit': 75000.0,
        },
        {
            'name': 'Abu Dhabi Wholesalers',
            'email': 'orders@adwholesale.ae',
            'phone': '+971-2-4567890',
            'ops_credit_limit': 100000.0,
        },
    ]
    
    for data in customer_data:
        customer = Partner.create({
            **data,
            'customer_rank': 1,
            'company_id': env.company.id,
            'country_id': env.ref('base.ae').id,
        })
        customers.append(customer)
    
    return customers


def setup_vendors(env, branch_dubai, branch_abudhabi):
    """Create test vendors"""
    Partner = env['res.partner']
    
    vendors = []
    
    vendor_data = [
        {
            'name': 'Global Tech Supplies',
            'email': 'sales@globaltechsupplies.com',
            'phone': '+86-21-12345678',
        },
        {
            'name': 'Regional Electronics Distributor',
            'email': 'orders@redelec.ae',
            'phone': '+971-4-5678901',
        },
    ]
    
    for data in vendor_data:
        vendor = Partner.create({
            **data,
            'supplier_rank': 1,
            'company_id': env.company.id,
            'country_id': env.ref('base.ae').id if 'ae' in data['email'] else env.ref('base.cn').id,
        })
        vendors.append(vendor)
    
    return vendors


def setup_products(env, company):
    """Create test products with cost/margin data"""
    Product = env['product.product']
    
    products = []
    
    product_data = [
        {
            'name': 'Laptop - Business Series',
            'default_code': 'LAP-BUS-001',
            'type': 'consu',
            'list_price': 3500.0,
            'standard_price': 2100.0,  # Cost price (40% margin)
            'categ_id': 1,  # Goods category
        },
        {
            'name': 'Wireless Mouse',
            'default_code': 'MSE-WRL-001',
            'type': 'consu',
            'list_price': 85.0,
            'standard_price': 45.0,  # Cost price (47% margin)
            'categ_id': 1,  # Goods category
        },
        {
            'name': 'USB-C Cable 2M',
            'default_code': 'CBL-USC-002',
            'type': 'consu',
            'list_price': 25.0,
            'standard_price': 10.0,  # Cost price (60% margin)
            'categ_id': 1,  # Goods category
        },
        {
            'name': 'Monitor 27" 4K',
            'default_code': 'MON-27K-001',
            'type': 'consu',
            'list_price': 1200.0,
            'standard_price': 750.0,  # Cost price (37.5% margin)
            'categ_id': 1,  # Goods category
        },
        {
            'name': 'Keyboard Mechanical RGB',
            'default_code': 'KBD-MEC-RGB',
            'type': 'consu',
            'list_price': 350.0,
            'standard_price': 180.0,  # Cost price (48.5% margin)
            'categ_id': 1,  # Goods category
        },
    ]
    
    for data in product_data:
        product = Product.create(data)
        products.append(product)
    
    return products


def setup_users(env, company, branch_dubai, branch_abudhabi):
    """Create test users with personas"""
    User = env['res.users']
    
    users = {}
    
    # Helper function to find or create user
    def get_or_create_user(name, login, email, company):
        existing = User.search([('login', '=', login)], limit=1)
        if existing:
            return existing
        return User.create({
            'name': name,
            'login': login,
            'email': email,
            'company_id': company.id,
            'company_ids': [Command.set([company.id])],
        })
    
    # Sales Manager - Dubai
    users['sales_mgr_dubai'] = get_or_create_user(
        'Ahmed Al Mansouri',
        'ahmed.sales@testtrading.ae',
        'ahmed.sales@testtrading.ae',
        company
    )
    
    # Purchase Manager - Dubai
    users['purchase_mgr'] = get_or_create_user(
        'Mohammed Hassan',
        'mohammed.purchase@testtrading.ae',
        'mohammed.purchase@testtrading.ae',
        company
    )
    
    # Sales Rep - Dubai
    users['sales_rep_dubai'] = get_or_create_user(
        'Fatima Ali',
        'fatima.sales@testtrading.ae',
        'fatima.sales@testtrading.ae',
        company
    )
    
    # Warehouse Manager
    users['warehouse_mgr'] = get_or_create_user(
        'Khalid Ibrahim',
        'khalid.warehouse@testtrading.ae',
        'khalid.warehouse@testtrading.ae',
        company
    )
    
    # Finance Manager
    users['finance_mgr'] = get_or_create_user(
        'Sara Abdullah',
        'sara.finance@testtrading.ae',
        'sara.finance@testtrading.ae',
        company
    )
    
    return users


def setup_governance_rules(env, company):
    """Activate key governance rules for testing"""
    Rule = env['ops.governance.rule']
    
    # Find and activate Sales Order > $10,000 rule
    so_rule = Rule.search([
        ('name', 'ilike', 'Sales Order'),
        ('threshold_amount', '>', 0),
    ], limit=1)
    
    if so_rule:
        so_rule.write({'active': True})
        _logger.info(f"  ✓ Activated: {so_rule.name}")
    
    # Find and activate Purchase Order > $5,000 rule
    po_rule = Rule.search([
        ('name', 'ilike', 'Purchase Order'),
        ('threshold_amount', '>', 0),
    ], limit=1)
    
    if po_rule:
        po_rule.write({'active': True})
        _logger.info(f"  ✓ Activated: {po_rule.name}")
    
    return True


def setup_sales_orders(env, branch_dubai, branch_abudhabi, customers, products, users):
    """Create sales orders for testing"""
    SO = env['sale.order']

    sales_orders = []
    
    # SO1: Small order (no approval needed)
    so1 = SO.with_user(env.ref('base.user_admin')).create({
        'partner_id': customers[0].id,
        'ops_branch_id': branch_dubai.id,
        'date_order': datetime.now(),
        'order_line': [
            Command.create({
                'product_id': products[1].id,  # Wireless Mouse
                'product_uom_qty': 10,
                'price_unit': 85.0,
            }),
        ],
    })
    sales_orders.append(so1)
    _logger.info(f"  ✓ Created SO: {so1.name} (Small - No approval)")
    
    # SO2: Large order (needs approval)
    so2 = SO.with_user(env.ref('base.user_admin')).create({
        'partner_id': customers[1].id,
        'ops_branch_id': branch_dubai.id,
        'date_order': datetime.now(),
        'order_line': [
            Command.create({
                'product_id': products[0].id,  # Laptop
                'product_uom_qty': 50,
                'price_unit': 3500.0,
            }),
            Command.create({
                'product_id': products[3].id,  # Monitor
                'product_uom_qty': 50,
                'price_unit': 1200.0,
            }),
        ],
    })
    sales_orders.append(so2)
    _logger.info(f"  ✓ Created SO: {so2.name} (Large - Needs approval)")
    
    # SO3: For Excel import testing (draft state)
    so3 = SO.with_user(env.ref('base.user_admin')).create({
        'partner_id': customers[2].id,
        'ops_branch_id': branch_abudhabi.id,
        'date_order': datetime.now(),
    })
    sales_orders.append(so3)
    _logger.info(f"  ✓ Created SO: {so3.name} (Empty - For Excel import test)")
    
    return sales_orders


def setup_purchase_orders(env, branch_dubai, vendors, products, users):
    """Create purchase orders for Three-Way Match testing"""
    PO = env['purchase.order']

    purchase_orders = []
    
    # PO1: Perfect match scenario (100 units)
    po1 = PO.with_user(env.ref('base.user_admin')).create({
        'partner_id': vendors[0].id,
        'ops_branch_id': branch_dubai.id,
        'date_order': datetime.now(),
        'order_line': [
            Command.create({
                'product_id': products[0].id,  # Laptop
                'product_qty': 100,
                'price_unit': 2100.0,
                'date_planned': datetime.now() + timedelta(days=7),
            }),
        ],
    })
    
    # Confirm PO
    po1.button_confirm()
    purchase_orders.append(po1)
    _logger.info(f"  ✓ Created PO: {po1.name} (Perfect match - 100 units)")
    
    # PO2: Partial receipt scenario (50 ordered, will receive 30)
    po2 = PO.with_user(env.ref('base.user_admin')).create({
        'partner_id': vendors[1].id,
        'ops_branch_id': branch_dubai.id,
        'date_order': datetime.now(),
        'order_line': [
            Command.create({
                'product_id': products[3].id,  # Monitor
                'product_qty': 50,
                'price_unit': 750.0,
                'date_planned': datetime.now() + timedelta(days=7),
            }),
        ],
    })
    
    # Confirm PO
    po2.button_confirm()
    purchase_orders.append(po2)
    _logger.info(f"  ✓ Created PO: {po2.name} (Partial - 50 units)")
    
    # PO3: Over-billing scenario (100 ordered, will bill for 120)
    po3 = PO.with_user(env.ref('base.user_admin')).create({
        'partner_id': vendors[0].id,
        'ops_branch_id': branch_dubai.id,
        'date_order': datetime.now(),
        'order_line': [
            Command.create({
                'product_id': products[4].id,  # Keyboard
                'product_qty': 100,
                'price_unit': 180.0,
                'date_planned': datetime.now() + timedelta(days=7),
            }),
        ],
    })
    
    # Confirm PO
    po3.button_confirm()
    purchase_orders.append(po3)
    _logger.info(f"  ✓ Created PO: {po3.name} (Over-billing test - 100 units)")
    
    return purchase_orders


def setup_stock_receipts(env, purchase_orders):
    """Process stock receipts for purchase orders"""
    receipts = []
    
    # Receipt for PO1: Full receipt (100 units)
    if purchase_orders[0].picking_ids:
        receipt1 = purchase_orders[0].picking_ids[0]
        for move in receipt1.move_ids:
            move.quantity = move.product_uom_qty  # Receive full quantity
        receipt1.button_validate()
        receipts.append(receipt1)
        _logger.info(f"  ✓ Processed Receipt: {receipt1.name} (Full - 100 units)")
    
    # Receipt for PO2: Partial receipt (30 out of 50)
    if purchase_orders[1].picking_ids:
        receipt2 = purchase_orders[1].picking_ids[0]
        for move in receipt2.move_ids:
            move.quantity = 30  # Only receive 30 units
        receipt2.button_validate()
        receipts.append(receipt2)
        _logger.info(f"  ✓ Processed Receipt: {receipt2.name} (Partial - 30/50 units)")
    
    # Receipt for PO3: Full receipt (100 units, but will be over-billed)
    if purchase_orders[2].picking_ids:
        receipt3 = purchase_orders[2].picking_ids[0]
        for move in receipt3.move_ids:
            move.quantity = move.product_uom_qty
        receipt3.button_validate()
        receipts.append(receipt3)
        _logger.info(f"  ✓ Processed Receipt: {receipt3.name} (Full - 100 units)")
    
    return receipts


def setup_vendor_bills(env, purchase_orders, vendors):
    """Create vendor bills (some matching, some not)"""
    Bill = env['account.move']

    bills = []
    
    # Bill for PO1: Perfect match (100 units @ correct price)
    bill1 = Bill.create({
        'move_type': 'in_invoice',
        'partner_id': vendors[0].id,
        'invoice_date': datetime.now().date(),
        'purchase_id': purchase_orders[0].id,
        'invoice_line_ids': [
            Command.create({
                'product_id': purchase_orders[0].order_line[0].product_id.id,
                'quantity': 100,
                'price_unit': 2100.0,
                'purchase_line_id': purchase_orders[0].order_line[0].id,
            }),
        ],
    })
    bills.append(bill1)
    _logger.info(f"  ✓ Created Bill: {bill1.name} (Perfect match)")
    
    # Bill for PO2: Under-billing (bill for 30, received 30, ordered 50) - Should match
    bill2 = Bill.create({
        'move_type': 'in_invoice',
        'partner_id': vendors[1].id,
        'invoice_date': datetime.now().date(),
        'purchase_id': purchase_orders[1].id,
        'invoice_line_ids': [
            Command.create({
                'product_id': purchase_orders[1].order_line[0].product_id.id,
                'quantity': 30,
                'price_unit': 750.0,
                'purchase_line_id': purchase_orders[1].order_line[0].id,
            }),
        ],
    })
    bills.append(bill2)
    _logger.info(f"  ✓ Created Bill: {bill2.name} (Matches receipt - 30 units)")
    
    # Bill for PO3: LEFT IN DRAFT - User will manually test over-billing
    _logger.info(f"  ✓ PO3 ready for manual bill creation (test over-billing)")
    
    return bills


def setup_approval_requests(env, sales_orders, users):
    """Create approval requests for escalation testing"""
    Approval = env['ops.approval.request']

    approvals = []
    
    # Only create approval if SO2 is large enough to trigger rules
    if len(sales_orders) > 1:
        so = sales_orders[1]  # Large SO
        
        # Check if approval was auto-created
        existing_approval = Approval.search([
            ('model_name', '=', 'sale.order'),
            ('res_id', '=', so.id),
        ], limit=1)
        
        if existing_approval:
            approvals.append(existing_approval)
            _logger.info(f"  ✓ Found existing approval: {existing_approval.name}")
        else:
            # Manually create for testing
            approval = Approval.create({
                'name': f'Approval for {so.name}',
                'model_name': 'sale.order',
                'res_id': so.id,
                'requested_by': env.ref('base.user_admin').id,
                'rule_id': 4,  # Three-Way Match Override rule
                'approver_ids': [(6, 0, [env.ref('base.user_admin').id])],
                'state': 'pending',
                'actual_value': so.amount_total,
                'name': f'Large order requiring approval: {so.amount_total} AED',
            })
            approvals.append(approval)
            _logger.info(f"  ✓ Created Approval: {approval.name} (For escalation test)")
    
    return approvals


# Execute seeding
if __name__ == '__main__' or 'env' in globals():
    seed_test_data(env)
