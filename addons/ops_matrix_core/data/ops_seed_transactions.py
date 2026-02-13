# -*- coding: utf-8 -*-
"""
OPS Seed Transactions — Creates transactional demo data using ORM workflows.

Called from post_init_hook AFTER all XML data files have been loaded.
This function creates sale orders, purchase orders, invoices, payments,
PDC records, budgets (with account refs), and approval test data.

Idempotent: checks for a sentinel record before running.
"""
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

SEED_SENTINEL = 'ops_seed_transactions_loaded'


def seed_transactions(env):
    """Main entry point — create transactional seed data."""

    # Idempotency: skip if already seeded
    existing = env['ir.config_parameter'].sudo().get_param(SEED_SENTINEL)
    if existing:
        _logger.info("OPS Seed Transactions: Already loaded — skipping.")
        return

    _logger.info("=== OPS Seed Transactions: Starting ===")

    try:
        _seed_budgets(env)
        _seed_sale_orders(env)
        _seed_purchase_orders(env)
        _seed_invoices(env)
        _seed_pdc_records(env)

        # Mark as seeded
        env['ir.config_parameter'].sudo().set_param(SEED_SENTINEL, 'true')
        env.cr.commit()
        _logger.info("=== OPS Seed Transactions: Complete ===")
    except Exception as e:
        _logger.warning("OPS Seed Transactions: Error during seeding: %s", e)
        env.cr.rollback()


# ======================================================================
# HELPER: resolve XML IDs safely
# ======================================================================

def _ref(env, xmlid):
    """Resolve an XML ID or return False."""
    try:
        return env.ref(xmlid, raise_if_not_found=False)
    except Exception:
        return False


def _find_expense_account(env, company):
    """Find an expense account for budget lines."""
    Account = env['account.account']
    acc = Account.search([
        ('company_id', '=', company.id),
        ('account_type', '=', 'expense'),
    ], limit=5, order='code')
    return acc


def _find_income_account(env, company):
    """Find an income account for invoices."""
    Account = env['account.account']
    acc = Account.search([
        ('company_id', '=', company.id),
        ('account_type', '=', 'income'),
    ], limit=1, order='code')
    return acc


def _find_sale_journal(env, company):
    """Find the sale journal."""
    return env['account.journal'].search([
        ('company_id', '=', company.id),
        ('type', '=', 'sale'),
    ], limit=1)


def _find_purchase_journal(env, company):
    """Find the purchase journal."""
    return env['account.journal'].search([
        ('company_id', '=', company.id),
        ('type', '=', 'purchase'),
    ], limit=1)


# ======================================================================
# BUDGETS
# ======================================================================

def _seed_budgets(env):
    """Create 5 budgets (one per branch) with budget lines."""
    _logger.info("Seeding budgets...")

    Budget = env.get('ops.budget')
    if Budget is None:
        _logger.warning("ops.budget model not available — skipping budgets")
        return

    company = env.company
    branches = env['ops.branch'].search([('company_id', '=', company.id)], limit=5)
    bus = env['ops.business.unit'].search([], limit=2)
    expense_accounts = _find_expense_account(env, company)

    if not branches or not bus or not expense_accounts:
        _logger.warning("Missing branches/BUs/accounts — skipping budgets")
        return

    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)

    for idx, branch in enumerate(branches):
        bu = bus[idx % len(bus)]
        budget_name = "FY%s Budget — %s" % (today.year, branch.name)

        existing = Budget.search([('name', '=', budget_name)], limit=1)
        if existing:
            continue

        lines = []
        for acc_idx, account in enumerate(expense_accounts):
            planned = (50000 + acc_idx * 25000) * (1 + idx * 0.2)
            lines.append((0, 0, {
                'general_account_id': account.id,
                'planned_amount': planned,
            }))

        budget = Budget.create({
            'name': budget_name,
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id,
            'date_from': year_start,
            'date_to': year_end,
            'state': 'confirmed' if idx < 3 else 'draft',
            'line_ids': lines,
        })
        _logger.info("Created budget: %s (ID: %s)", budget.name, budget.id)


# ======================================================================
# SALE ORDERS
# ======================================================================

def _seed_sale_orders(env):
    """Create 30 sale orders in various states."""
    _logger.info("Seeding sale orders...")

    SO = env['sale.order']
    branches = env['ops.branch'].search([], limit=5)
    customers = env['res.partner'].search([('customer_rank', '>', 0)], limit=15)
    products = env['product.product'].search([
        ('sale_ok', '=', True),
        ('type', '!=', 'service'),
    ], limit=10)

    if not customers or not products:
        _logger.warning("Missing customers/products — skipping sale orders")
        return

    today = date.today()
    so_count = 0

    for i in range(30):
        customer = customers[i % len(customers)]
        branch = branches[i % len(branches)] if branches else False
        product = products[i % len(products)]

        order_date = today - timedelta(days=60 - i * 2)

        vals = {
            'partner_id': customer.id,
            'date_order': order_date,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1 + (i % 10),
                'price_unit': product.list_price or 100.0,
            })],
        }
        if branch and 'ops_branch_id' in SO._fields:
            vals['ops_branch_id'] = branch.id

        try:
            so = SO.create(vals)
            so_count += 1

            # Confirm some orders (first 20)
            if i < 20:
                try:
                    so.action_confirm()
                except Exception as e:
                    _logger.debug("Could not confirm SO %s: %s", so.name, e)
        except Exception as e:
            _logger.debug("Could not create SO #%d: %s", i, e)

    _logger.info("Created %d sale orders", so_count)


# ======================================================================
# PURCHASE ORDERS
# ======================================================================

def _seed_purchase_orders(env):
    """Create 25 purchase orders in various states."""
    _logger.info("Seeding purchase orders...")

    PO = env['purchase.order']
    branches = env['ops.branch'].search([], limit=5)
    vendors = env['res.partner'].search([('supplier_rank', '>', 0)], limit=10)
    products = env['product.product'].search([
        ('purchase_ok', '=', True),
    ], limit=10)

    if not vendors or not products:
        _logger.warning("Missing vendors/products — skipping purchase orders")
        return

    today = date.today()
    po_count = 0

    for i in range(25):
        vendor = vendors[i % len(vendors)]
        branch = branches[i % len(branches)] if branches else False
        product = products[i % len(products)]

        order_date = today - timedelta(days=50 - i * 2)

        vals = {
            'partner_id': vendor.id,
            'date_order': order_date,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': 5 + (i % 20),
                'price_unit': product.standard_price or 50.0,
                'name': product.name or 'Product',
                'product_uom_id': product.uom_id.id,
                'date_planned': order_date + timedelta(days=7),
            })],
        }
        if branch and 'ops_branch_id' in PO._fields:
            vals['ops_branch_id'] = branch.id

        try:
            po = PO.create(vals)
            po_count += 1

            # Confirm some orders (first 15)
            if i < 15:
                try:
                    po.button_confirm()
                except Exception as e:
                    _logger.debug("Could not confirm PO %s: %s", po.name, e)
        except Exception as e:
            _logger.debug("Could not create PO #%d: %s", i, e)

    _logger.info("Created %d purchase orders", po_count)


# ======================================================================
# INVOICES (Account Moves)
# ======================================================================

def _seed_invoices(env):
    """Create 40 invoices: 25 customer invoices + 15 vendor bills."""
    _logger.info("Seeding invoices...")

    Move = env['account.move']
    branches = env['ops.branch'].search([], limit=5)
    customers = env['res.partner'].search([('customer_rank', '>', 0)], limit=15)
    vendors = env['res.partner'].search([('supplier_rank', '>', 0)], limit=10)
    products = env['product.product'].search([('sale_ok', '=', True)], limit=10)

    company = env.company
    today = date.today()
    inv_count = 0

    # --- Customer Invoices ---
    for i in range(25):
        customer = customers[i % len(customers)]
        branch = branches[i % len(branches)] if branches else False
        product = products[i % len(products)] if products else False
        inv_date = today - timedelta(days=45 - i)

        line_vals = {
            'quantity': 1 + (i % 5),
            'price_unit': 500 + i * 100,
            'name': product.name if product else 'Service Invoice Line',
        }
        if product:
            line_vals['product_id'] = product.id

        vals = {
            'move_type': 'out_invoice',
            'partner_id': customer.id,
            'invoice_date': inv_date,
            'invoice_line_ids': [(0, 0, line_vals)],
        }
        if branch and 'ops_branch_id' in Move._fields:
            vals['ops_branch_id'] = branch.id

        try:
            inv = Move.create(vals)
            inv_count += 1

            # Post some invoices (first 15)
            if i < 15:
                try:
                    inv.action_post()
                except Exception as e:
                    _logger.debug("Could not post invoice %s: %s", inv.name, e)
        except Exception as e:
            _logger.debug("Could not create customer invoice #%d: %s", i, e)

    # --- Vendor Bills ---
    for i in range(15):
        vendor = vendors[i % len(vendors)]
        branch = branches[i % len(branches)] if branches else False
        product = products[i % len(products)] if products else False
        bill_date = today - timedelta(days=40 - i * 2)

        line_vals = {
            'quantity': 2 + (i % 8),
            'price_unit': 200 + i * 50,
            'name': product.name if product else 'Vendor Bill Line',
        }
        if product:
            line_vals['product_id'] = product.id

        vals = {
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_date': bill_date,
            'invoice_line_ids': [(0, 0, line_vals)],
        }
        if branch and 'ops_branch_id' in Move._fields:
            vals['ops_branch_id'] = branch.id

        try:
            bill = Move.create(vals)
            inv_count += 1

            # Post some bills (first 8)
            if i < 8:
                try:
                    bill.action_post()
                except Exception as e:
                    _logger.debug("Could not post bill %s: %s", bill.name, e)
        except Exception as e:
            _logger.debug("Could not create vendor bill #%d: %s", i, e)

    _logger.info("Created %d invoices/bills", inv_count)


# ======================================================================
# PDC RECORDS
# ======================================================================

def _seed_pdc_records(env):
    """Create PDC receivable and payable records in various states."""
    _logger.info("Seeding PDC records...")

    PDCRecv = env.get('ops.pdc.receivable')
    PDCPay = env.get('ops.pdc.payable')

    if PDCRecv is None or PDCPay is None:
        _logger.warning("PDC models not available — skipping")
        return

    branches = env['ops.branch'].search([], limit=5)
    customers = env['res.partner'].search([('customer_rank', '>', 0)], limit=5)
    vendors = env['res.partner'].search([('supplier_rank', '>', 0)], limit=5)

    if not customers or not vendors:
        _logger.warning("Missing partners — skipping PDC")
        return

    today = date.today()
    pdc_count = 0

    # PDC Receivables (10 records)
    pdc_recv_states = [
        'draft', 'draft', 'deposited', 'deposited', 'deposited',
        'cleared', 'cleared', 'cleared', 'bounced', 'cancelled',
    ]
    for i in range(10):
        customer = customers[i % len(customers)]
        branch = branches[i % len(branches)] if branches else False
        maturity = today + timedelta(days=30 + i * 15)
        target_state = pdc_recv_states[i]

        vals = {
            'partner_id': customer.id,
            'amount': 5000 + i * 2500,
            'check_number': 'CHK-RECV-%03d' % (i + 1),
            'check_date': today - timedelta(days=10),
            'maturity_date': maturity,
        }
        if branch and 'ops_branch_id' in PDCRecv._fields:
            vals['ops_branch_id'] = branch.id

        try:
            pdc = PDCRecv.create(vals)
            pdc_count += 1

            # Advance state
            if target_state in ('deposited', 'cleared', 'bounced'):
                try:
                    pdc.write({'state': 'deposited', 'deposit_date': today - timedelta(days=5)})
                except Exception:
                    pass
            if target_state in ('cleared',):
                try:
                    pdc.write({'state': 'cleared', 'clearance_date': today - timedelta(days=2)})
                except Exception:
                    pass
            if target_state == 'bounced':
                try:
                    pdc.write({'state': 'bounced', 'bounce_date': today - timedelta(days=1)})
                except Exception:
                    pass
            if target_state == 'cancelled':
                try:
                    pdc.write({'state': 'cancelled'})
                except Exception:
                    pass
        except Exception as e:
            _logger.debug("Could not create PDC recv #%d: %s", i, e)

    # PDC Payables (8 records)
    pdc_pay_states = [
        'draft', 'draft', 'issued', 'issued', 'cleared', 'cleared', 'bounced', 'cancelled',
    ]
    for i in range(8):
        vendor = vendors[i % len(vendors)]
        branch = branches[i % len(branches)] if branches else False
        maturity = today + timedelta(days=15 + i * 10)
        target_state = pdc_pay_states[i]

        vals = {
            'partner_id': vendor.id,
            'amount': 3000 + i * 1500,
            'check_number': 'CHK-PAY-%03d' % (i + 1),
            'check_date': today - timedelta(days=5),
            'maturity_date': maturity,
        }
        if branch and 'ops_branch_id' in PDCPay._fields:
            vals['ops_branch_id'] = branch.id

        try:
            pdc = PDCPay.create(vals)
            pdc_count += 1

            # Advance state
            if target_state in ('issued', 'cleared', 'bounced'):
                try:
                    pdc.write({'state': 'issued'})
                except Exception:
                    pass
            if target_state == 'cleared':
                try:
                    pdc.write({'state': 'cleared', 'clearance_date': today - timedelta(days=1)})
                except Exception:
                    pass
            if target_state == 'bounced':
                try:
                    pdc.write({'state': 'bounced', 'bounce_date': today})
                except Exception:
                    pass
            if target_state == 'cancelled':
                try:
                    pdc.write({'state': 'cancelled'})
                except Exception:
                    pass
        except Exception as e:
            _logger.debug("Could not create PDC pay #%d: %s", i, e)

    _logger.info("Created %d PDC records", pdc_count)
