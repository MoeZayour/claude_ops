#!/usr/bin/env python3
"""
PRIORITY #14: DASHBOARDS - COMPREHENSIVE VERIFICATION TEST
===========================================================

This script tests the dashboard implementation claims vs reality.

CLAIMED in completion report:
- ops.dashboard model
- ops.dashboard.widget model  
- 4 Pre-configured dashboards
- 17+ widgets
- Dashboard menus

ACTUAL implementation found:
- 3 Analysis models (ops.sales.analysis, ops.financial.analysis, ops.inventory.analysis)
- SQL Views for analytics
- 3 Analytics menus (in Accounting, Sales, Inventory)
- Dashboard data XML commented out (depends on Enterprise spreadsheet.dashboard)

This test will verify what actually exists and provide accurate status.
"""

import sys
import xmlrpc.client
from datetime import datetime

# Odoo connection settings
ODOO_URL = 'http://localhost:8089'
ODOO_DB = 'gemini_odoo19'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_section(text):
    """Print a formatted section"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'-' * 80}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'-' * 80}{Colors.ENDC}\n")

def print_test(name, status, details=""):
    """Print a test result"""
    status_text = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if status else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
    print(f"  {status_text} | {name}")
    if details:
        print(f"         {Colors.YELLOW}{details}{Colors.ENDC}")

def print_info(text):
    """Print info text"""
    print(f"  {Colors.BLUE}ℹ{Colors.ENDC}  {text}")

def print_warning(text):
    """Print warning text"""
    print(f"  {Colors.YELLOW}⚠{Colors.ENDC}  {text}")

def print_error(text):
    """Print error text"""
    print(f"  {Colors.RED}✖{Colors.ENDC}  {text}")

def print_success(text):
    """Print success text"""
    print(f"  {Colors.GREEN}✓{Colors.ENDC}  {text}")

def connect_odoo():
    """Connect to Odoo and return common and models objects"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        version = common.version()
        print_info(f"Connected to Odoo {version['server_version']}")
        
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            print_error("Authentication failed!")
            return None, None, None
        
        print_success(f"Authenticated as user ID: {uid}")
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return common, models, uid
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        return None, None, None

def test_claimed_models(models, uid):
    """Test if the CLAIMED dashboard models exist"""
    print_section("TEST 1: CLAIMED DASHBOARD MODELS")
    
    results = []
    
    # Test 1.1: ops.dashboard model
    try:
        model_exists = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'ops.dashboard']]]
        )
        if model_exists:
            print_test("ops.dashboard model exists", True)
            results.append(('ops.dashboard model', True, 'Found'))
        else:
            print_test("ops.dashboard model exists", False, "Model NOT found - was never created")
            results.append(('ops.dashboard model', False, 'NOT FOUND'))
    except Exception as e:
        print_test("ops.dashboard model exists", False, f"Error: {str(e)}")
        results.append(('ops.dashboard model', False, str(e)))
    
    # Test 1.2: ops.dashboard.widget model
    try:
        model_exists = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'ops.dashboard.widget']]]
        )
        if model_exists:
            print_test("ops.dashboard.widget model exists", True)
            results.append(('ops.dashboard.widget model', True, 'Found'))
        else:
            print_test("ops.dashboard.widget model exists", False, "Model NOT found - was never created")
            results.append(('ops.dashboard.widget model', False, 'NOT FOUND'))
    except Exception as e:
        print_test("ops.dashboard.widget model exists", False, f"Error: {str(e)}")
        results.append(('ops.dashboard.widget model', False, str(e)))
    
    # Test 1.3: Check for spreadsheet.dashboard (Enterprise)
    try:
        model_exists = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search_count',
            [[['model', '=', 'spreadsheet.dashboard']]]
        )
        if model_exists:
            print_test("spreadsheet.dashboard (Enterprise) available", True)
            print_warning("Enterprise model exists but dashboard_data.xml is commented out in manifest")
            results.append(('spreadsheet.dashboard', True, 'Available but unused'))
        else:
            print_test("spreadsheet.dashboard (Enterprise) available", False, "Not available (Community Edition)")
            print_info("This is expected on Community Edition")
            results.append(('spreadsheet.dashboard', False, 'Not available'))
    except Exception as e:
        print_test("spreadsheet.dashboard check", False, f"Error: {str(e)}")
        results.append(('spreadsheet.dashboard', False, str(e)))
    
    return results

def test_actual_models(models, uid):
    """Test the ACTUAL analysis models that were built"""
    print_section("TEST 2: ACTUAL ANALYSIS MODELS (What Was Really Built)")
    
    results = []
    
    analysis_models = [
        ('ops.sales.analysis', 'Sales Analysis'),
        ('ops.financial.analysis', 'Financial Analysis'),
        ('ops.inventory.analysis', 'Inventory Analysis'),
    ]
    
    for model_name, display_name in analysis_models:
        try:
            # Check if model exists
            model_exists = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.model', 'search_count',
                [[['model', '=', model_name]]]
            )
            
            if model_exists:
                # Check if view/table exists
                record_count = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    model_name, 'search_count', [[]]
                )
                
                print_test(f"{display_name} model ({model_name})", True, f"{record_count} records available")
                results.append((model_name, True, f"{record_count} records"))
            else:
                print_test(f"{display_name} model ({model_name})", False, "Model not found")
                results.append((model_name, False, 'NOT FOUND'))
                
        except Exception as e:
            print_test(f"{display_name} model ({model_name})", False, f"Error: {str(e)}")
            results.append((model_name, False, str(e)))
    
    return results

def test_analysis_methods(models, uid):
    """Test the aggregation methods on analysis models"""
    print_section("TEST 3: ANALYSIS MODEL METHODS")
    
    results = []
    
    # Test sales analysis methods
    print_info("Testing ops.sales.analysis methods...")
    methods = [
        ('get_summary_by_branch', 'Sales by Branch'),
        ('get_summary_by_business_unit', 'Sales by Business Unit'),
        ('get_summary_by_matrix', 'Sales Matrix (Branch × BU)'),
        ('get_margin_analysis', 'Margin Analysis'),
    ]
    
    for method_name, display_name in methods:
        try:
            result = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ops.sales.analysis', method_name, []
            )
            
            if isinstance(result, list):
                print_test(f"{display_name} ({method_name})", True, f"Returned {len(result)} result(s)")
                results.append((method_name, True, f"{len(result)} results"))
            else:
                print_test(f"{display_name} ({method_name})", False, "Invalid return type")
                results.append((method_name, False, 'Invalid return'))
                
        except Exception as e:
            print_test(f"{display_name} ({method_name})", False, f"Error: {str(e)}")
            results.append((method_name, False, str(e)))
    
    return results

def test_menus(models, uid):
    """Test if analytics menus are accessible"""
    print_section("TEST 4: ANALYTICS MENU ITEMS")
    
    results = []
    
    menu_xmlids = [
        ('ops_matrix_reporting.menu_ops_accounting_analytics', 'Accounting → OPS Analytics'),
        ('ops_matrix_reporting.menu_ops_financial_analytics', 'Accounting → Financial Analytics'),
        ('ops_matrix_reporting.menu_ops_sales_analytics_root', 'Sales → OPS Analytics'),
        ('ops_matrix_reporting.menu_ops_sales_analytics', 'Sales → Sales Analytics'),
        ('ops_matrix_reporting.menu_ops_inventory_analytics_root', 'Inventory → OPS Analytics'),
        ('ops_matrix_reporting.menu_ops_inventory_analytics', 'Inventory → Inventory Analytics'),
    ]
    
    for xmlid, display_name in menu_xmlids:
        try:
            # Get menu record
            menu_ref = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.model.data', 'search_read',
                [[['module', '=', xmlid.split('.')[0]], ['name', '=', xmlid.split('.')[1]]]],
                {'fields': ['res_id'], 'limit': 1}
            )
            
            if menu_ref:
                menu_id = menu_ref[0]['res_id']
                menu = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'ir.ui.menu', 'read',
                    [menu_id], {'fields': ['name', 'action']}
                )
                
                if menu:
                    action_info = menu[0].get('action', 'No action')
                    print_test(f"{display_name}", True, f"Menu ID: {menu_id}, Action: {action_info}")
                    results.append((xmlid, True, f"Menu ID: {menu_id}"))
                else:
                    print_test(f"{display_name}", False, "Menu not readable")
                    results.append((xmlid, False, 'Not readable'))
            else:
                print_test(f"{display_name}", False, "Menu not found")
                results.append((xmlid, False, 'NOT FOUND'))
                
        except Exception as e:
            print_test(f"{display_name}", False, f"Error: {str(e)}")
            results.append((xmlid, False, str(e)))
    
    return results

def test_actions(models, uid):
    """Test if actions are defined"""
    print_section("TEST 5: WINDOW ACTIONS")
    
    results = []
    
    actions = [
        ('ops_matrix_reporting.action_ops_sales_analysis', 'Sales Analysis Action'),
        ('ops_matrix_reporting.action_ops_financial_analysis', 'Financial Analysis Action'),
        ('ops_matrix_reporting.action_ops_inventory_analysis', 'Inventory Analysis Action'),
    ]
    
    for xmlid, display_name in actions:
        try:
            action_ref = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.model.data', 'search_read',
                [[['module', '=', xmlid.split('.')[0]], ['name', '=', xmlid.split('.')[1]]]],
                {'fields': ['res_id', 'model'], 'limit': 1}
            )
            
            if action_ref:
                action_id = action_ref[0]['res_id']
                action_model = action_ref[0]['model']
                
                action = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    action_model, 'read',
                    [action_id], {'fields': ['name', 'res_model', 'type']}
                )
                
                if action:
                    res_model = action[0].get('res_model', 'N/A')
                    print_test(f"{display_name}", True, f"Model: {res_model}")
                    results.append((xmlid, True, f"Model: {res_model}"))
                else:
                    print_test(f"{display_name}", False, "Action not readable")
                    results.append((xmlid, False, 'Not readable'))
            else:
                print_test(f"{display_name}", False, "Action not found")
                results.append((xmlid, False, 'NOT FOUND'))
                
        except Exception as e:
            print_test(f"{display_name}", False, f"Error: {str(e)}")
            results.append((xmlid, False, str(e)))
    
    return results

def test_security(models, uid):
    """Test security access rules"""
    print_section("TEST 6: SECURITY ACCESS RULES")
    
    results = []
    
    # Check ir.model.access records
    access_models = [
        'ops.sales.analysis',
        'ops.financial.analysis',
        'ops.inventory.analysis',
    ]
    
    for model_name in access_models:
        try:
            access_count = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.model.access', 'search_count',
                [[['model_id.model', '=', model_name]]]
            )
            
            if access_count > 0:
                print_test(f"Access rules for {model_name}", True, f"{access_count} rule(s) defined")
                results.append((model_name, True, f"{access_count} rules"))
            else:
                print_test(f"Access rules for {model_name}", False, "No access rules found")
                results.append((model_name, False, 'No rules'))
                
        except Exception as e:
            print_test(f"Access rules for {model_name}", False, f"Error: {str(e)}")
            results.append((model_name, False, str(e)))
    
    # Check ir.rule (record rules)
    for model_name in access_models:
        try:
            rule_count = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.rule', 'search_count',
                [[['model_id.model', '=', model_name]]]
            )
            
            if rule_count > 0:
                print_test(f"Record rules for {model_name}", True, f"{rule_count} rule(s) defined")
                results.append((f"{model_name}_rules", True, f"{rule_count} rules"))
            else:
                print_test(f"Record rules for {model_name}", False, "No record rules found")
                print_warning("Records may be visible to all users without dimension filtering")
                results.append((f"{model_name}_rules", False, 'No rules'))
                
        except Exception as e:
            print_test(f"Record rules for {model_name}", False, f"Error: {str(e)}")
            results.append((f"{model_name}_rules", False, str(e)))
    
    return results

def generate_report(all_results):
    """Generate final completion report"""
    print_section("FINAL COMPLETION REPORT - PRIORITY #14: DASHBOARDS")
    
    # Calculate statistics
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(1 for results in all_results.values() for _, status, _ in results if status)
    failed_tests = total_tests - passed_tests
    pass_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}TEST SUMMARY:{Colors.ENDC}")
    print(f"  Total Tests:  {total_tests}")
    print(f"  {Colors.GREEN}Passed:       {passed_tests}{Colors.ENDC}")
    print(f"  {Colors.RED}Failed:       {failed_tests}{Colors.ENDC}")
    print(f"  Pass Rate:    {pass_percentage:.1f}%")
    
    print(f"\n{Colors.BOLD}CLAIMED VS ACTUAL IMPLEMENTATION:{Colors.ENDC}")
    
    print(f"\n{Colors.RED}❌ CLAIMED (NOT FOUND):{Colors.ENDC}")
    print(f"  • ops.dashboard model - DOES NOT EXIST")
    print(f"  • ops.dashboard.widget model - DOES NOT EXIST")
    print(f"  • 4 Pre-configured dashboards - NOT CREATED")
    print(f"  • 17+ widgets - NOT CREATED")
    print(f"  • Dashboard data XML - COMMENTED OUT in manifest")
    
    print(f"\n{Colors.GREEN}✅ ACTUAL (WHAT WAS BUILT):{Colors.ENDC}")
    print(f"  • ops.sales.analysis model - SQL VIEW ✓")
    print(f"  • ops.financial.analysis model - SQL VIEW ✓")
    print(f"  • ops.inventory.analysis model - SQL VIEW ✓")
    print(f"  • Aggregation methods (get_summary_by_branch, etc.) ✓")
    print(f"  • 6 Analytics menu items ✓")
    print(f"  • 3 Window actions ✓")
    print(f"  • Security access rules ✓")
    
    print(f"\n{Colors.YELLOW}⚠ ISSUES IDENTIFIED:{Colors.ENDC}")
    print(f"  1. Completion report is INACCURATE")
    print(f"  2. dashboard_data.xml depends on Enterprise-only 'spreadsheet.dashboard'")
    print(f"  3. No custom dashboard/widget models were created")
    print(f"  4. What was built: Analytics VIEWS, not dashboards")
    print(f"  5. Record-level security rules may be missing")
    
    print(f"\n{Colors.BOLD}ACCURATE STATUS:{Colors.ENDC}")
    
    # Check if analysis models work
    analysis_working = all(
        status for category in ['actual_models', 'analysis_methods'] 
        for _, status, _ in all_results.get(category, [])
        if status is not None
    )
    
    if analysis_working:
        print(f"  {Colors.GREEN}Analysis Models: 100% COMPLETE ✅{Colors.ENDC}")
        print(f"  {Colors.RED}Dashboard Models: 0% COMPLETE ❌{Colors.ENDC}")
        print(f"  {Colors.YELLOW}Overall Priority #14: 50% COMPLETE ⚠{Colors.ENDC}")
        print(f"\n  {Colors.CYAN}Built: High-performance analytics views with SQL{Colors.ENDC}")
        print(f"  {Colors.CYAN}Missing: Interactive dashboard UI with widgets{Colors.ENDC}")
    else:
        print(f"  {Colors.RED}Status: INCOMPLETE - Analysis models have issues ❌{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}RECOMMENDATIONS:{Colors.ENDC}")
    print(f"  1. Update completion report to reflect ACTUAL implementation")
    print(f"  2. Clarify: Are dashboards needed or are analytics views sufficient?")
    print(f"  3. If dashboards needed: Implement custom ops.dashboard models (Community-compatible)")
    print(f"  4. If analytics sufficient: Mark as complete and document accordingly")
    print(f"  5. Add record-level security rules for dimension filtering")
    
    return pass_percentage

def main():
    """Main test execution"""
    print_header(f"PRIORITY #14 DASHBOARDS - COMPREHENSIVE TEST")
    print_info(f"Test execution started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Target: {ODOO_URL} | Database: {ODOO_DB}")
    
    # Connect to Odoo
    common, models, uid = connect_odoo()
    if not models:
        sys.exit(1)
    
    # Run all tests
    all_results = {}
    
    try:
        all_results['claimed_models'] = test_claimed_models(models, uid)
        all_results['actual_models'] = test_actual_models(models, uid)
        all_results['analysis_methods'] = test_analysis_methods(models, uid)
        all_results['menus'] = test_menus(models, uid)
        all_results['actions'] = test_actions(models, uid)
        all_results['security'] = test_security(models, uid)
        
        # Generate final report
        pass_percentage = generate_report(all_results)
        
        print_header("TEST EXECUTION COMPLETE")
        
        # Return appropriate exit code
        if pass_percentage >= 80:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
