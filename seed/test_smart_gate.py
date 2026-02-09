#!/usr/bin/env python3
"""
Smart Corporate Governance Test Suite
Tests the "Speed at Quote, Governance at Credit" logic
"""
from odoo.exceptions import UserError

def run_tests(env):
    """Run all Smart Gate tests."""
    results = []

    # Get models
    Branch = env['ops.branch']
    BU = env['ops.business.unit']
    Partner = env['res.partner']
    SaleOrder = env['sale.order']
    Product = env['product.product']
    PaymentTerm = env['account.payment.term']

    # Setup
    branch = Branch.sudo().search([], limit=1)
    bu = BU.sudo().search([], limit=1)
    product = Product.sudo().search([('sale_ok', '=', True)], limit=1)

    # Get/create payment terms
    immediate_term = PaymentTerm.sudo().search([('name', 'ilike', 'immediate')], limit=1)
    if not immediate_term:
        immediate_term = PaymentTerm.sudo().create({
            'name': 'Immediate Payment',
            'line_ids': [(0, 0, {'value': 'balance', 'nb_days': 0})],
        })
        env.cr.commit()

    credit_term = PaymentTerm.sudo().search([('name', 'ilike', '30')], limit=1)
    if not credit_term:
        credit_term = PaymentTerm.sudo().create({
            'name': '30 Days Credit',
            'line_ids': [(0, 0, {'value': 'balance', 'nb_days': 30})],
        })
        env.cr.commit()

    results.append("=" * 60)
    results.append("SMART CORPORATE GOVERNANCE TEST RESULTS")
    results.append("=" * 60)
    results.append(f"Branch: {branch.name}")
    results.append(f"BU: {bu.name}")
    results.append(f"Immediate Term: {immediate_term.name}")
    results.append(f"Credit Term: {credit_term.name}")
    results.append("-" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Create Prospect without CR
    results.append("TEST 1: Create Prospect without CR Number")
    try:
        p = Partner.sudo().create({
            'name': 'Prospect John Test',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        results.append(f"  PASS: Created '{p.name}', CR={p.ops_cr_number}, Verified={p.ops_master_verified}")
        tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Test 2: Create Quote for Prospect
    results.append("TEST 2: Create Quote for Prospect (Speed Test)")
    try:
        p = Partner.sudo().create({
            'name': 'Quote Test Partner',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        o = SaleOrder.sudo().create({
            'partner_id': p.id,
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id,
            'payment_term_id': credit_term.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 5,
                'price_unit': 1000.0,
            })],
        })
        results.append(f"  PASS: Quote {o.name} created, Total={o.amount_total}, State={o.state}")
        tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Test 3: Credit Transaction BLOCKED
    results.append("TEST 3: Credit Transaction BLOCKED (Unverified Customer)")
    try:
        p = Partner.sudo().create({
            'name': 'Credit Block Test',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        o = SaleOrder.sudo().create({
            'partner_id': p.id,
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id,
            'payment_term_id': credit_term.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 5,
                'price_unit': 1000.0,
            })],
        })
        try:
            o.action_confirm()
            results.append("  FAIL: Order confirmed - should have been BLOCKED!")
            tests_failed += 1
        except UserError as e:
            results.append(f"  PASS: BLOCKED - Smart Gate working!")
            tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Test 4: Cash Transaction ALLOWED
    results.append("TEST 4: Cash Transaction ALLOWED (Unverified Customer)")
    try:
        p = Partner.sudo().create({
            'name': 'Cash Allow Test',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        o = SaleOrder.sudo().create({
            'partner_id': p.id,
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id,
            'payment_term_id': immediate_term.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 5,
                'price_unit': 1000.0,
            })],
        })
        o.action_confirm()
        results.append(f"  PASS: ALLOWED - Order {o.name} confirmed, State={o.state}")
        tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Test 5: Corporate with CR Number
    results.append("TEST 5: Create Corporate with CR Number")
    try:
        c = Partner.sudo().create({
            'name': 'Corp BigCo Test',
            'company_type': 'company',
            'ops_cr_number': 'CR-BIGCO-TEST-001',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        results.append(f"  PASS: Created '{c.name}', CR={c.ops_cr_number}")
        tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Test 6: Verified Corporate Credit PROCEEDS
    results.append("TEST 6: Verified Corporate Credit PROCEEDS")
    try:
        c = Partner.sudo().create({
            'name': 'Corp Verified Test',
            'company_type': 'company',
            'ops_cr_number': 'CR-VERIFIED-TEST-001',
            'ops_master_verified': False,
            'customer_rank': 1,
        })
        # CFO verifies the customer
        c.action_verify_master()

        o = SaleOrder.sudo().create({
            'partner_id': c.id,
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id,
            'payment_term_id': credit_term.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 50,
                'price_unit': 1000.0,
            })],
        })
        o.action_confirm()
        results.append(f"  PASS: CONFIRMED - Order {o.name}, State={o.state}, Total={o.amount_total}")
        tests_passed += 1
    except Exception as e:
        results.append(f"  FAIL: {str(e)[:100]}")
        tests_failed += 1
    env.cr.rollback()

    # Summary
    results.append("-" * 60)
    results.append("SUMMARY")
    results.append(f"Total Tests: {tests_passed + tests_failed}")
    results.append(f"Passed: {tests_passed}")
    results.append(f"Failed: {tests_failed}")
    results.append("=" * 60)

    return results, tests_passed, tests_failed


if __name__ == '__main__':
    # This will be called from Odoo shell
    pass
