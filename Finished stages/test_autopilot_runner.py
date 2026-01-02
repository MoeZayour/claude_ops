#!/usr/bin/env python3
"""
Autopilot Test Runner - Direct validation of all OPS Matrix features
"""

def run_tests(env):
    """Execute all autopilot tests"""
    results = []
    
    print('='*80)
    print('AUTOPILOT TEST EXECUTION - OPS MATRIX FRAMEWORK')
    print('='*80)
    
    # Test Feature #1-2: Branch Code Generation & Analytic Account
    print('\n[TEST 1] Branch Code Generation & Analytic Account Creation')
    print('-'*80)
    try:
        branch = env['ops.branch'].create({
            'name': 'Autopilot Test Branch Alpha',
            'company_id': env.company.id
        })
        assert branch.code != 'New', "Branch code should not be 'New'"
        assert branch.code, "Branch code must exist"
        assert branch.analytic_account_id, "Analytic account should be created"
        expected = f"[{branch.code}] {branch.name}"
        assert branch.analytic_account_id.name == expected, f"Analytic name mismatch"
        print(f'✅ PASSED - Branch: {branch.name}, Code: {branch.code}')
        results.append(('Branch Creation', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('Branch Creation', False, str(e)))
    
    # Test Feature #3-4: Business Unit
    print('\n[TEST 2] Business Unit Code Generation & Analytic Account')
    print('-'*80)
    try:
        bu = env['ops.business.unit'].create({
            'name': 'Autopilot Test BU Alpha',
            'company_id': env.company.id
        })
        assert bu.code != 'New', "BU code should not be 'New'"
        assert bu.analytic_account_id, "BU analytic account should be created"
        print(f'✅ PASSED - BU: {bu.name}, Code: {bu.code}')
        results.append(('Business Unit Creation', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('Business Unit Creation', False, str(e)))
    
    # Test Feature #5: Persona Code Generation
    print('\n[TEST 3] Persona Code Generation')
    print('-'*80)
    try:
        user = env['res.users'].create({
            'name': 'Autopilot Test User',
            'login': f'autopilot_test_{env.cr.dbname}@example.com'
        })
        persona = env['ops.persona'].create({
            'name': 'Autopilot Test Persona',
            'user_id': user.id
        })
        assert persona.code != 'New', "Persona code should not be 'New'"
        print(f'✅ PASSED - Persona: {persona.name}, Code: {persona.code}')
        results.append(('Persona Creation', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('Persona Creation', False, str(e)))
    
    # Test Feature #19: Partner State Transitions
    print('\n[TEST 4] Partner State Transitions')
    print('-'*80)
    try:
        partner = env['res.partner'].create({
            'name': 'Autopilot Test Partner',
            'ops_state': 'draft'
        })
        assert partner.ops_state == 'draft', "Partner should start in draft"
        
        partner.action_approve()
        assert partner.ops_state == 'approved', "Partner should be approved"
        assert partner.ops_verification_date, "Verification date should be set"
        
        partner.action_block()
        assert partner.ops_state == 'blocked', "Partner should be blocked"
        
        partner.action_unblock()
        assert partner.ops_state == 'approved', "Partner should return to approved"
        
        print(f'✅ PASSED - Partner workflow: draft→approved→blocked→approved')
        results.append(('Partner State Transitions', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('Partner State Transitions', False, str(e)))
    
    # Test Feature #14: Product Request Workflow
    print('\n[TEST 5] Product Request Workflow')
    print('-'*80)
    try:
        from datetime import datetime, timedelta
        product = env['product.product'].create({
            'name': 'Autopilot Test Product',
            'type': 'product'
        })
        request = env['ops.product.request'].create({
            'product_id': product.id,
            'quantity': 10.0,
            'required_date': (datetime.now() + timedelta(days=30)).date(),
            'branch_id': branch.id,
        })
        assert request.state == 'draft', "Request should start as draft"
        
        request.action_submit()
        assert request.state == 'submitted', "Request should be submitted"
        
        request.action_approve()
        assert request.state == 'approved', "Request should be approved"
        
        request.action_start()
        assert request.state == 'in_progress', "Request should be in progress"
        
        request.action_receive()
        assert request.state == 'received', "Request should be received"
        
        print(f'✅ PASSED - Request workflow: draft→submitted→approved→in_progress→received')
        results.append(('Product Request Workflow', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('Product Request Workflow', False, str(e)))
    
    # Test Feature #11: SLA Template
    print('\n[TEST 6] SLA Template Deadline Computation')
    print('-'*80)
    try:
        model_sale = env['ir.model'].search([('model', '=', 'sale.order')], limit=1)
        sla_template = env['ops.sla.template'].create({
            'name': 'Autopilot Test SLA',
            'model_id': model_sale.id,
            'target_duration': 24.0
        })
        start_time = datetime.now()
        deadline = sla_template._compute_deadline(start_time)
        assert deadline, "Deadline should be computed"
        assert deadline > start_time, "Deadline should be after start time"
        print(f'✅ PASSED - SLA deadline computed: {deadline}')
        results.append(('SLA Template', True, None))
    except Exception as e:
        print(f'❌ FAILED - {str(e)}')
        results.append(('SLA Template', False, str(e)))
    
    # Print Summary
    print('\n' + '='*80)
    print('AUTOPILOT TEST SUMMARY')
    print('='*80)
    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    
    for feature, success, error in results:
        status = '✅ PASSED' if success else f'❌ FAILED: {error}'
        print(f'{feature}: {status}')
    
    print('='*80)
    print(f'Total: {len(results)} tests | Passed: {passed} | Failed: {failed}')
    print('='*80)
    
    return failed == 0

if __name__ == '__main__':
    import sys
    # This will be called from odoo shell context where 'env' is available
    success = run_tests(env)
    sys.exit(0 if success else 1)
