#!/usr/bin/env python3
"""
Autopilot Test Runner for OPS Matrix Framework
Executes all test files and reports results
"""
import subprocess
import sys

def run_test_module(module_name):
    """Run a specific test module using odoo-bin"""
    print(f"\n{'='*80}")
    print(f"Running: {module_name}")
    print('='*80)
    
    cmd = [
        'docker', 'exec', 'gemini_odoo19',
        'python3', '-c',
        f'''
import odoo
from odoo.tests.loader import get_test_modules
from odoo.tests.common import get_db_name
import logging

logging.basicConfig(level=logging.INFO)

# Initialize Odoo
odoo.tools.config.parse_config([
    '-c', '/etc/odoo/odoo.conf',
    '-d', 'mz-db'
])

# Get registry
registry = odoo.registry('mz-db')
with registry.cursor() as cr:
    # Load environment
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {{}})
    
    # Import and run test
    try:
        test_module = env['ir.module.module'].search([('name', '=', 'ops_matrix_core')])
        if test_module:
            from odoo.addons.ops_matrix_core.tests.{module_name} import *
            import unittest
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(sys.modules['odoo.addons.ops_matrix_core.tests.{module_name}'])
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            sys.exit(0 if result.wasSuccessful() else 1)
    except Exception as e:
        print(f"Error: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == '__main__':
    tests = [
        'test_01_branch_creation',
    ]
    
    results = {}
    for test in tests:
        success = run_test_module(test)
        results[test] = '✅ PASSED' if success else '❌ FAILED'
    
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print('='*80)
    for test, result in results.items():
        print(f"{test}: {result}")
    
    failed = sum(1 for r in results.values() if 'FAILED' in r)
    sys.exit(failed)
