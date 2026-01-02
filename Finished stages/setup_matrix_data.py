# setup_matrix_data.py
import logging
from odoo import api, SUPERUSER_ID

def init_matrix_data(env):
    """
    Initializes OPS Matrix:
    - Structure: HQ -> (North, South) -> (Retail, B2B, Service, Export)
    - Master Data: Products, Partners, Governance Rules
    - Personas: Sales Rep, Manager, Logistics, CFO
    """
    logger = logging.getLogger(__name__)
    logger.info(">>> STARTING OPS MATRIX DEEP SETUP <<<")

    # 1. Organizational Structure (1 Main -> 2 Sub-Branches)
    hq = env['ops.branch'].create({'name': 'Global HQ', 'code': 'GHQ'})
    br_north = env['ops.branch'].create({'name': 'North Branch', 'code': 'NOR', 'sequence': 10})
    br_south = env['ops.branch'].create({'name': 'South Branch', 'code': 'SOU', 'sequence': 20})
    
    # 2. Business Units (2 per Branch logic)
    bu_retail = env['ops.business.unit'].create({'name': 'Retail Div', 'code': 'BU-RET'})
    bu_corp = env['ops.business.unit'].create({'name': 'Corporate Div', 'code': 'BU-CORP'})
    bu_logistics = env['ops.business.unit'].create({'name': 'Logistics Div', 'code': 'BU-LOG'})
    bu_service = env['ops.business.unit'].create({'name': 'Service Div', 'code': 'BU-SRV'})

    # 3. Products (Critical for Sales/Purchase Tests)
    prod_vals = [
        {'name': 'Matrix Laptop', 'type': 'consu', 'list_price': 1200, 'standard_price': 800},
        {'name': 'Consulting Hour', 'type': 'service', 'list_price': 150, 'standard_price': 0},
        {'name': 'Office Desk', 'type': 'consu', 'list_price': 500, 'standard_price': 300},
    ]
    products = [env['product.product'].create(p) for p in prod_vals]

    # 4. Partners
    cust_1 = env['res.partner'].create({'name': 'MegaCorp Customer', 'email': 'cust@test.com'})
    vend_1 = env['res.partner'].create({'name': 'Global Supplier', 'email': 'supp@test.com'})

    # 5. Governance Rules (The "Test Rules" Requirement)
    # Rule 1: Warn if discount > 10%
    env['ops.governance.rule'].create({
        'name': 'High Discount Warning',
        'model_id': env.ref('sale.model_sale_order').id,
        'action_type': 'warning',
        'error_message': 'High order value detected! Please review discount policy.',
        'condition_code': "result = record.amount_total > 1000" # Simplified for test
    })
    # Rule 2: Block if Credit Limit Exceeded (Requires Manager)
    env['ops.governance.rule'].create({
        'name': 'Credit Limit Block',
        'model_id': env.ref('sale.model_sale_order').id,
        'action_type': 'block',
        'error_message': 'Credit Limit Exceeded! Manager Approval Required.',
        'condition_code': "result = record.partner_id.credit > 5000"
    })

    # 6. Personas (Users)
    def create_persona(name, login, branch, bus, role):
        u = env['res.users'].create({
            'name': name, 'login': login, 'password': 'admin',
            'groups_ids': [(6,0, [env.ref('base.group_user').id])]
        })
        env['ops.persona'].create({
            'name': f"{role} - {branch.code}",
            'user_id': u.id,
            'branch_id': branch.id,
            'business_unit_ids': [(6,0, [b.id for b in bus])],
            'job_level': 'manager' if 'Manager' in role else 'mid',
            'can_approve_orders': True if 'Manager' in role else False
        })
        return u

    # Sales Rep (North / Retail)
    create_persona('Sales Rep North', 'rep_north', br_north, [bu_retail], 'Sales Rep')
    # Sales Manager (North / All BUs)
    create_persona('Manager North', 'mgr_north', br_north, [bu_retail, bu_corp], 'Branch Manager')
    # Logistics User (South)
    create_persona('Logistics User', 'log_south', br_south, [bu_logistics], 'Logistics Officer')
    # CFO (HQ)
    create_persona('CFO', 'cfo_hq', hq, [bu_retail, bu_corp, bu_logistics, bu_service], 'CFO')

    logger.info(">>> MATRIX DATA SETUP COMPLETE <<<")

if __name__ == "__main__":
    init_matrix_data(env)
    env.cr.commit()
