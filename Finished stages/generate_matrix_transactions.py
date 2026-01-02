#!/usr/bin/env python3
"""
Generate test transactions for OPS Matrix visual inspection.
Creates Customer Invoice and Vendor Bill with Branch/BU assignments.
"""
import xmlrpc.client
import logging
from datetime import date

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Connection parameters
URL = 'http://localhost:8089'
DB = 'mz-db'
USERNAME = 'admin'
PASSWORD = 'admin'

def connect():
    """Connect to Odoo and return uid."""
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        raise Exception("Authentication failed")
    logger.info(f"✓ Connected as user ID: {uid}")
    return uid

def execute(uid, model, method, *args, **kwargs):
    """Execute model method via XML-RPC."""
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)

def main():
    logger.info("=== OPS Matrix Transaction Generator ===\n")
    
    # Connect
    uid = connect()
    
    # Step 1: Get the main company (acts as Branch in Odoo 19)
    logger.info("\n1. Setting up Branch...")
    company = execute(uid, 'res.company', 'search_read',
                     [],
                     fields=['id', 'name', 'ops_code'], limit=1)
    
    if not company:
        logger.error("✗ No company found!")
        return
    
    main_company = company[0]
    branch_id = main_company['id']
    current_name = main_company['name']
    logger.info(f"✓ Found company: {current_name} (OPS Code: {main_company.get('ops_code', 'N/A')})")
    
    # Rename to "West Region" if not already
    if current_name != 'West Region':
        try:
            execute(uid, 'res.company', 'write', [branch_id], {'name': 'West Region'})
            logger.info(f"✓ Renamed company to 'West Region' (Branch ID: {branch_id})")
        except Exception as e:
            logger.warning(f"Could not rename company: {e}")
    else:
        logger.info(f"✓ Company already named 'West Region' (Branch ID: {branch_id})")
    
    # Step 2: Use existing Business Unit
    logger.info("\n2. Setting up Business Unit...")
    
    # Get the first existing BU (created by hooks)
    existing_bus = execute(uid, 'ops.business.unit', 'search_read',
                          [],
                          fields=['id', 'name', 'code'], limit=1)
    
    if not existing_bus:
        logger.error("✗ No Business Unit found! Please create one via the UI first.")
        logger.error("Go to: OPS Matrix > Configuration > Business Units > Create")
        return
    
    bu_id = existing_bus[0]['id']
    bu_name = existing_bus[0]['name']
    bu_code = existing_bus[0]['code']
    logger.info(f"✓ Using existing BU: {bu_name} ({bu_code}, ID: {bu_id})")
    
    # Step 3: Get or create Customer
    logger.info("\n3. Setting up Customer...")
    customer = execute(uid, 'res.partner', 'search_read',
                      [('name', '=', 'Acme Corporation')],
                      fields=['id', 'name'], limit=1)
    
    if customer:
        customer_id = customer[0]['id']
        logger.info(f"✓ Found customer: {customer[0]['name']}")
    else:
        customer_id = execute(uid, 'res.partner', 'create', {
            'name': 'Acme Corporation',
            'customer_rank': 1,
            'email': 'contact@acmecorp.com',
        })
        logger.info(f"✓ Created customer: Acme Corporation (ID: {customer_id})")
    
    # Step 4: Get or create Vendor
    logger.info("\n4. Setting up Vendor...")
    vendor = execute(uid, 'res.partner', 'search_read',
                    [('name', '=', 'Tech Supplies Inc')],
                    fields=['id', 'name'], limit=1)
    
    if vendor:
        vendor_id = vendor[0]['id']
        logger.info(f"✓ Found vendor: {vendor[0]['name']}")
    else:
        vendor_id = execute(uid, 'res.partner', 'create', {
            'name': 'Tech Supplies Inc',
            'supplier_rank': 1,
            'email': 'sales@techsupplies.com',
        })
        logger.info(f"✓ Created vendor: Tech Supplies Inc (ID: {vendor_id})")
    
    # Step 5: Get income and expense accounts
    logger.info("\n5. Looking up accounts...")
    
    # Find income account
    income_accounts = execute(uid, 'account.account', 'search_read',
                             [('account_type', '=', 'income')],
                             fields=['id', 'code', 'name'], limit=1)
    if not income_accounts:
        logger.error("✗ No income account found! Please install a Chart of Accounts.")
        return
    income_account_id = income_accounts[0]['id']
    logger.info(f"✓ Income account: {income_accounts[0]['code']} - {income_accounts[0]['name']}")
    
    # Find expense account
    expense_accounts = execute(uid, 'account.account', 'search_read',
                              [('account_type', '=', 'expense')],
                              fields=['id', 'code', 'name'], limit=1)
    if not expense_accounts:
        logger.error("✗ No expense account found! Please install a Chart of Accounts.")
        return
    expense_account_id = expense_accounts[0]['id']
    logger.info(f"✓ Expense account: {expense_accounts[0]['code']} - {expense_accounts[0]['name']}")
    
    # Step 6: Create Customer Invoice
    logger.info("\n6. Creating Customer Invoice...")
    try:
        invoice_id = execute(uid, 'account.move', 'create', {
            'move_type': 'out_invoice',
            'partner_id': customer_id,
            'ops_branch_id': branch_id,
            'ops_business_unit_id': bu_id,
            'invoice_date': str(date.today()),
            'invoice_line_ids': [(0, 0, {
                'name': 'Professional Services - Q4 2025',
                'quantity': 1,
                'price_unit': 5000.00,
                'account_id': income_account_id,
            })],
        })
        logger.info(f"✓ Created Customer Invoice (ID: {invoice_id})")
        
        # Read back to verify
        invoice = execute(uid, 'account.move', 'read', [invoice_id],
                         fields=['name', 'ops_branch_id', 'ops_business_unit_id',
                                    'analytic_distribution', 'amount_total'])
        logger.info(f"  - Invoice Number: {invoice[0]['name']}")
        logger.info(f"  - Branch: {invoice[0].get('ops_branch_id', ['N/A'])[1] if invoice[0].get('ops_branch_id') else 'N/A'}")
        logger.info(f"  - Business Unit: {invoice[0].get('ops_business_unit_id', ['N/A'])[1] if invoice[0].get('ops_business_unit_id') else 'N/A'}")
        logger.info(f"  - Amount: ${invoice[0]['amount_total']}")
        if invoice[0].get('analytic_distribution'):
            logger.info(f"  - Analytic Distribution: {invoice[0]['analytic_distribution']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to create invoice: {e}")
    
    # Step 7: Create Vendor Bill
    logger.info("\n7. Creating Vendor Bill...")
    try:
        bill_id = execute(uid, 'account.move', 'create', {
            'move_type': 'in_invoice',
            'partner_id': vendor_id,
            'ops_branch_id': branch_id,
            'ops_business_unit_id': bu_id,
            'invoice_date': str(date.today()),
            'invoice_line_ids': [(0, 0, {
                'name': 'Office Equipment - Laptops',
                'quantity': 5,
                'price_unit': 1200.00,
                'account_id': expense_account_id,
            })],
        })
        logger.info(f"✓ Created Vendor Bill (ID: {bill_id})")
        
        # Read back to verify
        bill = execute(uid, 'account.move', 'read', [bill_id],
                      fields=['name', 'ops_branch_id', 'ops_business_unit_id',
                                 'analytic_distribution', 'amount_total'])
        logger.info(f"  - Bill Number: {bill[0]['name']}")
        logger.info(f"  - Branch: {bill[0].get('ops_branch_id', ['N/A'])[1] if bill[0].get('ops_branch_id') else 'N/A'}")
        logger.info(f"  - Business Unit: {bill[0].get('ops_business_unit_id', ['N/A'])[1] if bill[0].get('ops_business_unit_id') else 'N/A'}")
        logger.info(f"  - Amount: ${bill[0]['amount_total']}")
        if bill[0].get('analytic_distribution'):
            logger.info(f"  - Analytic Distribution: {bill[0]['analytic_distribution']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to create bill: {e}")
    
    logger.info("\n=== Transaction Generation Complete ===")
    logger.info("\nVisual Validation Guide:")
    logger.info("1. Login to Odoo at http://localhost:8089")
    logger.info("2. Go to: Invoicing > Customers > Invoices")
    logger.info("3. Open the 'Professional Services' invoice")
    logger.info("4. Verify Branch = 'West Region' and BU = 'Technology Services'")
    logger.info("5. Go to: Invoicing > Vendors > Bills")
    logger.info("6. Open the 'Office Equipment' bill")
    logger.info("7. Verify Branch = 'West Region' and BU = 'Technology Services'")
    logger.info("8. Check 'Analytic Distribution' tab shows correct allocation\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
