#!/usr/bin/env python3
"""
OPS Seed Data Coverage Validator
================================

Run inside Odoo shell to verify that all seed data loaded correctly.

Usage:
    docker exec gemini_odoo19 odoo shell -d mz-db < seed/validate_seed_coverage.py

The script writes results to /tmp/seed_validation.json for easy extraction:
    docker exec gemini_odoo19 cat /tmp/seed_validation.json
"""
import json
import logging

_logger = logging.getLogger(__name__)

EXPECTED = {
    # Structure
    'companies': {'model': 'res.company', 'min': 1, 'field': None},
    'branches': {'model': 'ops.branch', 'min': 5, 'field': None},
    'business_units': {'model': 'ops.business.unit', 'min': 8, 'field': None},

    # Partners
    'customers': {'model': 'res.partner', 'min': 20, 'domain': [('customer_rank', '>', 0)]},
    'vendors': {'model': 'res.partner', 'min': 15, 'domain': [('supplier_rank', '>', 0)]},

    # Products
    'product_categories': {'model': 'product.category', 'min': 8, 'domain': [('name', 'like', '%')]},
    'products': {'model': 'product.product', 'min': 50, 'field': None},

    # Users (18 personas x 2 = 36, plus admin/default)
    'active_users': {'model': 'res.users', 'min': 36, 'domain': [('active', '=', True), ('login', '!=', '__system__')]},

    # Personas
    'personas': {'model': 'ops.persona', 'min': 18, 'field': None},

    # Governance
    'approval_rules': {'model': 'ops.approval.rule', 'min': 4, 'field': None},
    'sla_templates': {'model': 'ops.sla.template', 'min': 3, 'field': None},

    # Fiscal (accounting module)
    'fiscal_periods': {'model': 'ops.fiscal.period', 'min': 12, 'field': None},

    # Transactional (from post_init_hook)
    'sale_orders': {'model': 'sale.order', 'min': 10, 'field': None},
    'purchase_orders': {'model': 'purchase.order', 'min': 10, 'field': None},
    'customer_invoices': {'model': 'account.move', 'min': 10, 'domain': [('move_type', '=', 'out_invoice')]},
    'vendor_bills': {'model': 'account.move', 'min': 5, 'domain': [('move_type', '=', 'in_invoice')]},
}

# Optional models (may not be installed)
OPTIONAL = {
    'budgets': {'model': 'ops.budget', 'min': 1, 'field': None},
    'pdc_receivable': {'model': 'ops.pdc.receivable', 'min': 1, 'field': None},
    'pdc_payable': {'model': 'ops.pdc.payable', 'min': 1, 'field': None},
}


def validate(env):
    """Run all validation checks and return results."""
    results = {'pass': [], 'fail': [], 'skip': [], 'summary': {}}

    all_checks = list(EXPECTED.items()) + list(OPTIONAL.items())

    for name, spec in all_checks:
        model_name = spec['model']
        min_count = spec['min']
        domain = spec.get('domain', [])
        is_optional = name in OPTIONAL

        try:
            Model = env[model_name]
        except KeyError:
            if is_optional:
                results['skip'].append({'name': name, 'model': model_name, 'reason': 'model not available'})
            else:
                results['fail'].append({'name': name, 'model': model_name, 'expected': min_count, 'actual': 0, 'reason': 'model not found'})
            continue

        try:
            count = Model.sudo().search_count(domain)
        except Exception as e:
            if is_optional:
                results['skip'].append({'name': name, 'model': model_name, 'reason': str(e)})
            else:
                results['fail'].append({'name': name, 'model': model_name, 'expected': min_count, 'actual': 0, 'reason': str(e)})
            continue

        entry = {'name': name, 'model': model_name, 'expected': min_count, 'actual': count}

        if count >= min_count:
            results['pass'].append(entry)
        else:
            if is_optional:
                results['skip'].append({**entry, 'reason': f'below minimum (optional)'})
            else:
                results['fail'].append({**entry, 'reason': f'expected >= {min_count}, got {count}'})

    # Persona coverage check: verify all 18 persona codes exist
    persona_codes = [
        'CEO', 'CFO', 'FIN_CTRL', 'SALES_LEADER', 'SALES_MGR', 'PURCHASE_MGR',
        'LOG_MGR', 'TREASURY_OFF', 'HR_MGR', 'CHIEF_ACCT', 'SYS_ADMIN',
        'SALES_REP', 'PURCHASE_OFF', 'LOG_CLERK', 'ACCOUNTANT', 'AR_CLERK',
        'AP_CLERK', 'TECH_SUPPORT',
    ]
    try:
        existing_codes = set(env['ops.persona'].sudo().search([]).mapped('code'))
        missing_personas = [c for c in persona_codes if c not in existing_codes]
        if missing_personas:
            results['fail'].append({
                'name': 'persona_coverage',
                'expected': 18,
                'actual': len(existing_codes),
                'reason': f'missing codes: {missing_personas}'
            })
        else:
            results['pass'].append({'name': 'persona_coverage', 'expected': 18, 'actual': len(existing_codes)})
    except Exception as e:
        results['fail'].append({'name': 'persona_coverage', 'reason': str(e)})

    # Branch coverage: all 5 branches in at least 1 user's allowed branches
    try:
        branches = env['ops.branch'].sudo().search([])
        users = env['res.users'].sudo().search([('login', 'like', '@ops-demo.com')])
        branch_coverage = set()
        for u in users:
            branch_coverage.update(u.ops_allowed_branch_ids.ids)
        uncovered = branches.filtered(lambda b: b.id not in branch_coverage)
        if uncovered:
            results['fail'].append({
                'name': 'branch_user_coverage',
                'reason': f'branches with no users: {uncovered.mapped("name")}'
            })
        else:
            results['pass'].append({'name': 'branch_user_coverage', 'expected': len(branches), 'actual': len(branch_coverage)})
    except Exception as e:
        results['skip'].append({'name': 'branch_user_coverage', 'reason': str(e)})

    # Security group check: IT Admin users exist (for blindness testing)
    try:
        it_admin_group = env.ref('ops_matrix_core.group_ops_it_admin', raise_if_not_found=False)
        if it_admin_group:
            it_admins = env['res.users'].sudo().search([
                ('group_ids', 'in', [it_admin_group.id]),
                ('active', '=', True),
            ])
            if len(it_admins) >= 2:
                results['pass'].append({'name': 'it_admin_blindness_users', 'expected': 2, 'actual': len(it_admins)})
            else:
                results['fail'].append({'name': 'it_admin_blindness_users', 'expected': 2, 'actual': len(it_admins)})
    except Exception as e:
        results['skip'].append({'name': 'it_admin_blindness_users', 'reason': str(e)})

    # Summary
    results['summary'] = {
        'total': len(results['pass']) + len(results['fail']) + len(results['skip']),
        'passed': len(results['pass']),
        'failed': len(results['fail']),
        'skipped': len(results['skip']),
    }

    return results


def main():
    results = validate(env)  # noqa: F821 — 'env' is provided by Odoo shell

    # Write JSON
    with open('/tmp/seed_validation.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    # Print summary
    s = results['summary']
    print(f"\n{'='*60}")
    print(f"  OPS Seed Data Validation Results")
    print(f"{'='*60}")
    print(f"  PASSED:  {s['passed']}")
    print(f"  FAILED:  {s['failed']}")
    print(f"  SKIPPED: {s['skipped']}")
    print(f"{'='*60}")

    if results['fail']:
        print("\n  FAILURES:")
        for f in results['fail']:
            print(f"    - {f['name']}: {f.get('reason', 'unknown')}")

    if results['skip']:
        print("\n  SKIPPED:")
        for sk in results['skip']:
            print(f"    - {sk['name']}: {sk.get('reason', 'optional')}")

    print(f"\n  Full results: /tmp/seed_validation.json")
    print(f"{'='*60}\n")


main()
