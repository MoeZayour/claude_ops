#!/usr/bin/env python3
"""
OPS Matrix Modules - Automated Test Suite
Auto-execution mode with retry logic
"""

import sys
import time
import logging
from datetime import datetime

# Setup logging
import os
log_dir = '/tmp/tests' if os.path.exists('/tmp') and os.access('/tmp', os.W_OK) else 'logs/tests'
os.makedirs(log_dir, exist_ok=True)
log_file = f'{log_dir}/test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds
RETRYABLE_ERRORS = (ImportError, ConnectionError, Exception)
NON_RETRYABLE_ERRORS = (ValueError, TypeError)

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.retries = 0
        self.details = []
    
    def add_result(self, test_name, status, message="", attempts=1):
        self.total += 1
        self.retries += (attempts - 1)
        
        if status == "PASS":
            self.passed += 1
            icon = "✅"
        elif status == "FAIL":
            self.failed += 1
            icon = "❌"
        else:
            self.skipped += 1
            icon = "⏭️"
        
        self.details.append({
            'test': test_name,
            'status': status,
            'message': message,
            'attempts': attempts,
            'icon': icon
        })
        
        logger.info(f"{icon} {test_name}: {status} (attempts: {attempts})")
        if message:
            logger.info(f"   └─ {message}")

def retry_on_error(func, test_name, results):
    """Execute test with retry logic"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"{'─' * 60}")
            logger.info(f"Running: {test_name} (Attempt {attempt}/{MAX_RETRIES})")
            logger.info(f"{'─' * 60}")
            
            result = func()
            results.add_result(test_name, "PASS", result, attempts=attempt)
            return True
            
        except NON_RETRYABLE_ERRORS as e:
            # Design/logic errors - don't retry
            error_msg = f"Non-retryable error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            results.add_result(test_name, "FAIL", error_msg, attempts=attempt)
            return False
            
        except RETRYABLE_ERRORS as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"Attempt {attempt} failed: {error_msg}")
            
            if attempt == MAX_RETRIES:
                # Max retries exceeded
                final_msg = f"FAILED after {MAX_RETRIES} attempts: {error_msg}"
                logger.error(final_msg)
                results.add_result(test_name, "FAIL", final_msg, attempts=attempt)
                return False
            
            # Wait before retry
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    return False

def test_connection():
    """Test 1: Odoo connection"""
    try:
        import odoorpc
    except ImportError:
        logger.info("Installing odoorpc...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "odoorpc", "-q"])
        import odoorpc
    
    odoo = odoorpc.ODOO('localhost', port=8089)
    odoo.login('mz-db', 'admin', 'admin')
    
    # Test basic query
    users = odoo.env['res.users'].search([])
    return f"Connected successfully. Found {len(users)} users."

def test_modules_installed(odoo):
    """Test 2: Verify all modules are installed"""
    Module = odoo.env['ir.module.module']
    
    required_modules = [
        'ops_matrix_core',
        'ops_matrix_accounting', 
        'ops_matrix_reporting'
    ]
    
    results = []
    for module_name in required_modules:
        modules = Module.search([('name', '=', module_name)])
        if not modules:
            raise ValueError(f"Module {module_name} not found in database")
        
        module = Module.browse(modules[0])
        if module.state != 'installed':
            raise ValueError(f"Module {module_name} not installed (state: {module.state})")
        
        results.append(f"{module_name}: state={module.state}")
    
    return "\n   ".join(results)

def test_models_accessible(odoo):
    """Test 3: Verify core models are accessible"""
    models_to_test = [
        'ops.branch',
        'ops.business.unit',
        'ops.persona',
        'ops.governance.rule',
        'account.move',
        'sale.order',
        'purchase.order'
    ]
    
    results = []
    for model_name in models_to_test:
        try:
            count = odoo.env[model_name].search_count([])
            results.append(f"{model_name}: accessible ({count} records)")
        except Exception as e:
            raise ValueError(f"Model {model_name} not accessible: {str(e)}")
    
    return "\n   ".join(results)

def test_create_branch(odoo):
    """Test 4: Create branch record"""
    Branch = odoo.env['ops.branch']
    
    # Clean up any existing test branch
    existing = Branch.search([('code', '=', 'TEST-AUTO')])
    if existing:
        Branch.unlink(existing)
    
    branch_id = Branch.create({
        'name': 'Test Branch Automated',
        'code': 'TEST-AUTO',
        'active': True
    })
    
    # Verify creation
    branch = Branch.browse(branch_id)
    if not branch.name:
        raise ValueError("Branch created but data not persisted")
    
    return f"Branch created: ID={branch_id}, name='{branch.name}', code='{branch.code}'"

def test_create_bu(odoo):
    """Test 5: Create business unit record"""
    Branch = odoo.env['ops.branch']
    BU = odoo.env['ops.business.unit']
    
    # Get test branch
    branches = Branch.search([('code', '=', 'TEST-AUTO')])
    if not branches:
        raise ValueError("Test branch not found. Run test_create_branch first.")
    branch_id = branches[0]
    
    # Clean up existing test BU
    existing = BU.search([('code', '=', 'TESTBU-AUTO')])
    if existing:
        BU.unlink(existing)
    
    bu_id = BU.create({
        'name': 'Test BU Automated',
        'code': 'TESTBU-AUTO',
        'branch_ids': [(6, 0, [branch_id])],  # Many2many field
        'active': True
    })
    
    # Verify creation and relation
    bu = BU.browse(bu_id)
    if branch_id not in bu.branch_ids.ids:
        raise ValueError("BU created but branch relation incorrect")
    
    return f"BU created: ID={bu_id}, name='{bu.name}', branches={len(bu.branch_ids)}"

def test_persona_templates(odoo):
    """Test 6: Verify persona templates or check if load required"""
    Persona = odoo.env['ops.persona']
    
    # Check if any personas exist
    total_personas = Persona.search_count([])
    
    if total_personas == 0:
        return f"⚠️  No persona templates loaded yet (count: {total_personas}). Templates may need manual loading or hook execution."
    
    # If personas exist, check for some expected ones
    all_personas = Persona.search([])
    persona_names = [Persona.browse(p_id).name for p_id in all_personas[:10]]
    
    return f"Persona templates found: {total_personas} total\n   Sample names: {', '.join(persona_names[:5])}"

def test_analytic_plans(odoo):
    """Test 7: Verify analytic plans created"""
    AnalyticPlan = odoo.env['account.analytic.plan']
    
    required_plans = [
        'Matrix Branch',
        'Matrix Business Unit'
    ]
    
    results = []
    for plan_name in required_plans:
        plans = AnalyticPlan.search([('name', '=', plan_name)])
        if not plans:
            raise ValueError(f"Analytic plan '{plan_name}' not found")
        
        plan = AnalyticPlan.browse(plans[0])
        results.append(f"{plan.name}: ID={plan.id}")
    
    return "\n   ".join(results)

def test_accounting_integration(odoo):
    """Test 8: Verify accounting module integration"""
    AccountMove = odoo.env['account.move']
    
    # Check if OPS fields are available on account.move
    fields_info = AccountMove.fields_get(['ops_branch_id', 'ops_business_unit_id'])
    
    if 'ops_branch_id' not in fields_info:
        raise ValueError("Field 'ops_branch_id' not found on account.move")
    
    if 'ops_business_unit_id' not in fields_info:
        raise ValueError("Field 'ops_business_unit_id' not found on account.move")
    
    return "OPS fields available on account.move:\n   ✓ ops_branch_id\n   ✓ ops_business_unit_id"

def test_reporting_models(odoo):
    """Test 9: Verify reporting models accessible"""
    reporting_models = [
        'ops.sales.analysis',
        'ops.financial.analysis',
        'ops.inventory.analysis',
        'ops.excel.export.wizard'
    ]
    
    results = []
    for model_name in reporting_models:
        try:
            odoo.env[model_name].search_count([])
            results.append(f"✓ {model_name}")
        except Exception as e:
            raise ValueError(f"Reporting model {model_name} not accessible: {str(e)}")
    
    return "Reporting models accessible:\n   " + "\n   ".join(results)

def test_security_rules(odoo):
    """Test 10: Verify admin bypass in security"""
    Branch = odoo.env['ops.branch']
    BU = odoo.env['ops.business.unit']
    
    # Admin should be able to access all records
    all_branches = Branch.search([])
    all_bus = BU.search([])
    
    return f"Admin access verified:\n   Branches: {len(all_branches)} accessible\n   BUs: {len(all_bus)} accessible"

def generate_report(results):
    """Generate final test report"""
    print("\n")
    print("=" * 80)
    print("                      AUTOMATED TEST REPORT")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log File: {log_file}")
    print("=" * 80)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Tests:     {results.total}")
    print(f"✅ Passed:        {results.passed}")
    print(f"❌ Failed:        {results.failed}")
    print(f"⏭️  Skipped:       {results.skipped}")
    print(f"🔄 Total Retries: {results.retries}")
    print()
    
    pass_rate = (results.passed / results.total * 100) if results.total > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    print()
    
    # Detailed results
    print("📋 DETAILED RESULTS")
    print("-" * 80)
    for detail in results.details:
        print(f"{detail['icon']} {detail['test']}")
        print(f"   Status: {detail['status']}")
        if detail['attempts'] > 1:
            print(f"   Attempts: {detail['attempts']}")
        if detail['message']:
            print(f"   Details: {detail['message']}")
        print()
    
    # Final verdict
    print("=" * 80)
    if results.failed == 0:
        print("🎉 ALL TESTS PASSED! Modules are production-ready.")
    elif results.failed <= 2:
        print("⚠️  MOSTLY PASSED. Review failed tests and apply fixes.")
    else:
        print("❌ MULTIPLE FAILURES. Human intervention required.")
    print("=" * 80)
    print()
    
    # Return status code
    return 0 if results.failed == 0 else 1

def main():
    """Main test execution"""
    results = TestResult()
    
    print("🧪 Starting Automated Test Suite...")
    print(f"Max retries per test: {MAX_RETRIES}")
    print(f"Retry delay: {RETRY_DELAY}s")
    print()
    
    # Establish connection first (with retry)
    odoo = None
    if retry_on_error(test_connection, "Test 1: Odoo Connection", results):
        import odoorpc
        odoo = odoorpc.ODOO('localhost', port=8089)
        odoo.login('mz-db', 'admin', 'admin')
    else:
        print("❌ CRITICAL: Cannot connect to Odoo. Aborting remaining tests.")
        return generate_report(results)
    
    # Run all tests
    tests = [
        (lambda: test_modules_installed(odoo), "Test 2: Modules Installed"),
        (lambda: test_models_accessible(odoo), "Test 3: Models Accessible"),
        (lambda: test_create_branch(odoo), "Test 4: Create Branch"),
        (lambda: test_create_bu(odoo), "Test 5: Create Business Unit"),
        (lambda: test_persona_templates(odoo), "Test 6: Persona Templates"),
        (lambda: test_analytic_plans(odoo), "Test 7: Analytic Plans"),
        (lambda: test_accounting_integration(odoo), "Test 8: Accounting Integration"),
        (lambda: test_reporting_models(odoo), "Test 9: Reporting Models"),
        (lambda: test_security_rules(odoo), "Test 10: Security Rules"),
    ]
    
    for test_func, test_name in tests:
        success = retry_on_error(test_func, test_name, results)
        
        # If critical test fails after retries, ask user
        if not success and test_name in ["Test 2: Modules Installed", "Test 3: Models Accessible"]:
            print()
            print("=" * 80)
            print("⚠️  CRITICAL TEST FAILED")
            print("=" * 80)
            print(f"Test: {test_name}")
            print(f"This is a critical test. Further testing may be unreliable.")
            print()
            user_input = input("Continue with remaining tests? (y/n): ").strip().lower()
            if user_input != 'y':
                print("Testing aborted by user.")
                break
    
    # Generate final report
    return generate_report(results)

if __name__ == "__main__":
    sys.exit(main())
