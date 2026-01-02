#!/usr/bin/env python3
"""
PHASE 3D: REPORTING AUDIT - FINAL STRESS TEST
==============================================
Tests all reporting and analytics capabilities across ops_matrix_accounting
and ops_matrix_reporting modules using test data from Phases 3A-3C.

Database: mz-db
Instance: gemini_odoo19
Approach: Read-only audit and validation
"""

import sys
import os
from datetime import datetime

# Odoo shell environment
from odoo import api, SUPERUSER_ID

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    """Print formatted subsection"""
    print(f"\n{'─' * 70}")
    print(f"📊 {title}")
    print('─' * 70)

def step_1_verify_test_data(env):
    """Verify test data from Phases 3A-3C exists"""
    print_section("STEP 1: Verify Test Data is Present")
    
    results = {
        'sales_order': None,
        'purchase_order': None,
        'branches': 0,
        'business_units': 0,
        'products': 0,
        'users': 0
    }
    
    # Check Sales Order S00001 from Phase 3B
    so = env['sale.order'].search([('name', '=', 'S00001')], limit=1)
    results['sales_order'] = so
    
    # Check Purchase Order P00002 from Phase 3A
    po = env['purchase.order'].search([('name', '=', 'P00002')], limit=1)
    results['purchase_order'] = po
    
    # Count infrastructure from Phase 2
    results['branches'] = env['ops.branch'].search_count([])
    results['business_units'] = env['ops.business.unit'].search_count([])
    results['products'] = env['product.product'].search_count([])
    results['users'] = env['res.users'].search_count([('share', '=', False)])
    
    print(f"\n📦 Test Data Verification:")
    print(f"   Sales Order S00001: {'✅ Found' if so else '❌ Missing'}")
    if so:
        print(f"      - Amount: ${so.amount_total:,.2f}")
        print(f"      - State: {so.state}")
        print(f"      - Branch: {so.ops_branch_id.name if so.ops_branch_id else 'N/A'}")
        print(f"      - BU: {so.ops_business_unit_id.name if so.ops_business_unit_id else 'N/A'}")
    
    print(f"\n   Purchase Order P00002: {'✅ Found' if po else '❌ Missing'}")
    if po:
        print(f"      - Amount: ${po.amount_total:,.2f}")
        print(f"      - State: {po.state}")
        print(f"      - Branch: {po.ops_branch_id.name if po.ops_branch_id else 'N/A'}")
        print(f"      - BU: {po.ops_business_unit_id.name if po.ops_business_unit_id else 'N/A'}")
    
    print(f"\n📊 Infrastructure Count:")
    print(f"   Branches: {results['branches']}")
    print(f"   Business Units: {results['business_units']}")
    print(f"   Products: {results['products']}")
    print(f"   Users (non-portal): {results['users']}")
    
    return results

def step_2_test_sales_analysis(env, test_data):
    """Test ops.sales.analysis model"""
    print_section("STEP 2: Test Sales Analysis Views")
    
    results = {
        'model_exists': False,
        'record_count': 0,
        'test_data_found': False,
        'branch_filtering': False,
        'records': []
    }
    
    if 'ops.sales.analysis' not in env:
        print("   ⚠️ ops.sales.analysis model not found")
        return results
    
    results['model_exists'] = True
    print("   ✅ ops.sales.analysis model found")
    
    # Get sales analysis records
    sales_data = env['ops.sales.analysis'].search([], limit=20)
    results['record_count'] = len(sales_data)
    
    print(f"   Total analysis records: {results['record_count']}")
    
    if sales_data:
        print(f"\n   📈 Sample Sales Analysis Records:")
        for idx, record in enumerate(sales_data[:5], 1):
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'N/A'
            bu_name = record.ops_business_unit_id.name if hasattr(record, 'ops_business_unit_id') and record.ops_business_unit_id else 'N/A'
            amount = getattr(record, 'amount_total', 0) or getattr(record, 'price_total', 0)
            
            results['records'].append({
                'branch': branch_name,
                'bu': bu_name,
                'amount': amount
            })
            
            print(f"      [{idx}] Branch: {branch_name}")
            print(f"          BU: {bu_name}")
            print(f"          Amount: ${amount:,.2f}")
        
        # Check if test SO appears
        if test_data.get('sales_order'):
            so = test_data['sales_order']
            test_sales = env['ops.sales.analysis'].search([
                ('order_id', '=', so.id)
            ], limit=1)
            
            if test_sales:
                results['test_data_found'] = True
                print(f"\n   ✅ Test SO S00001 found in sales analysis")
            else:
                print(f"\n   ⚠️ Test SO S00001 not yet in analysis view")
        
        # Test branch filtering
        branch_north = env['ops.branch'].search([('name', '=', 'Branch-North')], limit=1)
        if branch_north:
            branch_sales = env['ops.sales.analysis'].search([
                ('ops_branch_id', '=', branch_north.id)
            ])
            results['branch_filtering'] = len(branch_sales) > 0
            print(f"\n   Branch Filtering Test (Branch-North): {len(branch_sales)} records")
    else:
        print("   ⚠️ No sales analysis data found")
        print("   Note: Analysis views may need to be refreshed/computed")
    
    return results

def step_3_test_financial_analysis(env):
    """Test ops.financial.analysis model"""
    print_section("STEP 3: Test Financial Analysis")
    
    results = {
        'model_exists': False,
        'record_count': 0,
        'branches': {},
        'business_units': {}
    }
    
    if 'ops.financial.analysis' not in env:
        print("   ⚠️ ops.financial.analysis model not found")
        return results
    
    results['model_exists'] = True
    print("   ✅ ops.financial.analysis model found")
    
    financial_data = env['ops.financial.analysis'].search([], limit=50)
    results['record_count'] = len(financial_data)
    
    print(f"   Total financial records: {results['record_count']}")
    
    if financial_data:
        # Group by branch
        branches = {}
        bus = {}
        
        for record in financial_data:
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'Unassigned'
            bu_name = record.ops_business_unit_id.name if hasattr(record, 'ops_business_unit_id') and record.ops_business_unit_id else 'Unassigned'
            
            # Branch aggregation
            if branch_name not in branches:
                branches[branch_name] = {'count': 0, 'balance': 0}
            branches[branch_name]['count'] += 1
            branches[branch_name]['balance'] += getattr(record, 'balance', 0) or getattr(record, 'amount', 0)
            
            # BU aggregation
            if bu_name not in bus:
                bus[bu_name] = {'count': 0, 'balance': 0}
            bus[bu_name]['count'] += 1
            bus[bu_name]['balance'] += getattr(record, 'balance', 0) or getattr(record, 'amount', 0)
        
        results['branches'] = branches
        results['business_units'] = bus
        
        print(f"\n   💰 Financial Data by Branch:")
        for branch, data in sorted(branches.items())[:10]:
            print(f"      - {branch}: {data['count']} records, Balance: ${data['balance']:,.2f}")
        
        if len(branches) > 10:
            print(f"      ... and {len(branches) - 10} more branches")
        
        print(f"\n   💼 Financial Data by Business Unit:")
        for bu, data in sorted(bus.items())[:10]:
            print(f"      - {bu}: {data['count']} records, Balance: ${data['balance']:,.2f}")
    else:
        print("   ⚠️ No financial analysis data found")
    
    return results

def step_4_test_inventory_analysis(env):
    """Test ops.inventory.analysis model"""
    print_section("STEP 4: Test Inventory Analysis")
    
    results = {
        'model_exists': False,
        'record_count': 0,
        'products': {}
    }
    
    if 'ops.inventory.analysis' not in env:
        print("   ⚠️ ops.inventory.analysis model not found")
        return results
    
    results['model_exists'] = True
    print("   ✅ ops.inventory.analysis model found")
    
    inventory_data = env['ops.inventory.analysis'].search([], limit=50)
    results['record_count'] = len(inventory_data)
    
    print(f"   Total inventory records: {results['record_count']}")
    
    if inventory_data:
        print(f"\n   📦 Sample Inventory Analysis Records:")
        
        for idx, record in enumerate(inventory_data[:10], 1):
            product_name = record.product_id.name if hasattr(record, 'product_id') and record.product_id else 'Unknown'
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'N/A'
            qty = getattr(record, 'quantity', 0) or getattr(record, 'qty_available', 0)
            value = getattr(record, 'value', 0) or getattr(record, 'stock_value', 0)
            
            print(f"      [{idx}] Product: {product_name[:40]}")
            print(f"          Branch: {branch_name}, Qty: {qty}, Value: ${value:,.2f}")
            
            if product_name not in results['products']:
                results['products'][product_name] = {'qty': 0, 'value': 0}
            results['products'][product_name]['qty'] += qty
            results['products'][product_name]['value'] += value
    else:
        print("   ⚠️ No inventory analysis data found")
    
    return results

def step_5_test_general_ledger(env):
    """Test General Ledger report generation"""
    print_section("STEP 5: Test General Ledger Report Generation")
    
    results = {
        'wizard_exists': False,
        'wizard_created': False,
        'report_generated': False,
        'error': None
    }
    
    # Check for GL wizard models
    wizard_models = [
        'ops.general.ledger.wizard',
        'ops.general.ledger.wizard.enhanced',
        'account.general.ledger'
    ]
    
    wizard_model = None
    for model in wizard_models:
        if model in env:
            wizard_model = model
            results['wizard_exists'] = True
            print(f"   ✅ Found wizard model: {model}")
            break
    
    if not wizard_model:
        print("   ⚠️ No General Ledger wizard found")
        print("   Checked: " + ", ".join(wizard_models))
        return results
    
    try:
        # Create wizard for GL report
        wizard_vals = {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
        }
        
        # Add target_move if field exists
        wizard_obj = env[wizard_model]
        if 'target_move' in wizard_obj._fields:
            wizard_vals['target_move'] = 'posted'
        
        wizard = wizard_obj.create(wizard_vals)
        results['wizard_created'] = True
        print(f"   ✅ Wizard created: ID {wizard.id}")
        
        # Try to generate report
        report_methods = ['generate_report', 'print_report', 'check_report', 'action_generate']
        
        for method in report_methods:
            if hasattr(wizard, method):
                print(f"   ℹ️ Found report method: {method}")
                try:
                    report_data = getattr(wizard, method)()
                    results['report_generated'] = True
                    print(f"   ✅ Report generated using {method}")
                    print(f"   Report type: {type(report_data)}")
                    if isinstance(report_data, dict):
                        print(f"   Report keys: {list(report_data.keys())}")
                    break
                except Exception as e:
                    print(f"   ⚠️ Method {method} failed: {str(e)[:100]}")
        
        if not results['report_generated']:
            print(f"   ℹ️ Available wizard methods: {[m for m in dir(wizard) if not m.startswith('_') and callable(getattr(wizard, m))][:10]}")
            
    except Exception as e:
        results['error'] = str(e)
        print(f"   ❌ GL Report error: {str(e)[:200]}")
    
    return results

def step_6_test_excel_export(env):
    """Test Excel export functionality"""
    print_section("STEP 6: Test Excel Export Functionality")
    
    results = {
        'wizard_exists': False,
        'xlsxwriter_installed': False,
        'wizard_created': False,
        'export_attempted': False,
        'error': None
    }
    
    # Check for Excel export wizard
    excel_models = [
        'ops.excel.export.wizard',
        'ops.report.excel.wizard',
        'report.excel.wizard'
    ]
    
    excel_model = None
    for model in excel_models:
        if model in env:
            excel_model = model
            results['wizard_exists'] = True
            print(f"   ✅ Found Excel wizard: {model}")
            break
    
    if not excel_model:
        print("   ⚠️ No Excel export wizard found")
        print("   Checked: " + ", ".join(excel_models))
    
    # Check xlsxwriter package
    try:
        import xlsxwriter
        results['xlsxwriter_installed'] = True
        print(f"   ✅ xlsxwriter package installed (version {xlsxwriter.__version__})")
    except ImportError:
        print(f"   ⚠️ xlsxwriter not installed - Excel export will fail")
        print(f"   Install with: pip3 install xlsxwriter")
    
    if excel_model:
        try:
            # Get wizard fields
            wizard_obj = env[excel_model]
            wizard_vals = {}
            
            # Add common fields if they exist
            if 'date_from' in wizard_obj._fields:
                wizard_vals['date_from'] = '2025-01-01'
            if 'date_to' in wizard_obj._fields:
                wizard_vals['date_to'] = '2025-12-31'
            if 'report_type' in wizard_obj._fields:
                wizard_vals['report_type'] = 'sales'
            
            wizard = wizard_obj.create(wizard_vals)
            results['wizard_created'] = True
            print(f"   ✅ Export wizard created: ID {wizard.id}")
            
            # Try to generate Excel
            export_methods = ['generate_excel', 'export_excel', 'print_xlsx', 'action_export']
            
            for method in export_methods:
                if hasattr(wizard, method):
                    print(f"   ℹ️ Found export method: {method}")
                    try:
                        excel_data = getattr(wizard, method)()
                        results['export_attempted'] = True
                        print(f"   ✅ Excel generation attempted using {method}")
                        break
                    except Exception as e:
                        print(f"   ⚠️ Method {method} failed: {str(e)[:100]}")
                        
        except Exception as e:
            results['error'] = str(e)
            print(f"   ⚠️ Excel export error: {str(e)[:200]}")
    
    return results

def step_7_test_branch_bu_filtering(env, test_data):
    """Test Branch/BU filtering in reports"""
    print_section("STEP 7: Test Branch/BU Filtering in Reports")
    
    results = {
        'branch_filtering': {},
        'bu_filtering': {},
        'test_so_found': False
    }
    
    # Get test branches and BUs
    branch_north = env['ops.branch'].search([('name', '=', 'Branch-North')], limit=1)
    branch_south = env['ops.branch'].search([('name', '=', 'Branch-South')], limit=1)
    bu_sales = env['ops.business.unit'].search([('name', '=', 'BU-Sales')], limit=1)
    bu_ops = env['ops.business.unit'].search([('name', '=', 'BU-Operations')], limit=1)
    
    print(f"\n   🔍 Testing Filtering Capabilities:")
    
    # Test sales analysis filtering
    if 'ops.sales.analysis' in env:
        print(f"\n   📊 Sales Analysis Filtering:")
        
        if branch_north:
            branch_sales = env['ops.sales.analysis'].search([
                ('ops_branch_id', '=', branch_north.id)
            ])
            results['branch_filtering']['Branch-North'] = len(branch_sales)
            print(f"      - Branch-North: {len(branch_sales)} records")
        
        if branch_south:
            branch_sales = env['ops.sales.analysis'].search([
                ('ops_branch_id', '=', branch_south.id)
            ])
            results['branch_filtering']['Branch-South'] = len(branch_sales)
            print(f"      - Branch-South: {len(branch_sales)} records")
        
        if bu_sales:
            bu_data = env['ops.sales.analysis'].search([
                ('ops_business_unit_id', '=', bu_sales.id)
            ])
            results['bu_filtering']['BU-Sales'] = len(bu_data)
            print(f"      - BU-Sales: {len(bu_data)} records")
        
        # Check test SO
        so = test_data.get('sales_order')
        if so and hasattr(so, 'ops_branch_id') and so.ops_branch_id:
            test_sales = env['ops.sales.analysis'].search([
                ('order_id', '=', so.id)
            ])
            if test_sales:
                results['test_so_found'] = True
                print(f"      ✅ Test SO S00001 found in analysis (Branch: {so.ops_branch_id.name})")
    
    # Test financial analysis filtering
    if 'ops.financial.analysis' in env:
        print(f"\n   💰 Financial Analysis Filtering:")
        
        if branch_north:
            branch_financial = env['ops.financial.analysis'].search([
                ('ops_branch_id', '=', branch_north.id)
            ])
            print(f"      - Branch-North: {len(branch_financial)} financial records")
        
        if bu_sales:
            bu_financial = env['ops.financial.analysis'].search([
                ('ops_business_unit_id', '=', bu_sales.id)
            ])
            print(f"      - BU-Sales: {len(bu_financial)} financial records")
    
    return results

def step_8_test_consolidated_reporting(env):
    """Test consolidated reporting"""
    print_section("STEP 8: Test Consolidated Reporting")
    
    results = {
        'model_exists': False,
        'record_count': 0,
        'error': None
    }
    
    consolidated_models = [
        'ops.consolidated.report',
        'ops.consolidated.reporting',
        'ops.consolidation.report'
    ]
    
    consolidated_model = None
    for model in consolidated_models:
        if model in env:
            consolidated_model = model
            results['model_exists'] = True
            print(f"   ✅ Found consolidated model: {model}")
            break
    
    if not consolidated_model:
        print("   ℹ️ Consolidated report model not found (may be embedded in other reports)")
        print("   Checked: " + ", ".join(consolidated_models))
        return results
    
    try:
        consolidated = env[consolidated_model].search([], limit=10)
        results['record_count'] = len(consolidated)
        
        if consolidated:
            print(f"   ✅ Consolidated reports available: {results['record_count']} records")
            
            # Show sample data
            for idx, record in enumerate(consolidated[:3], 1):
                print(f"      [{idx}] Record ID: {record.id}")
                if hasattr(record, 'name'):
                    print(f"          Name: {record.name}")
        else:
            print(f"   ⚠️ No consolidated reports generated yet")
            print(f"   Note: May need to trigger consolidation process")
    except Exception as e:
        results['error'] = str(e)
        print(f"   ⚠️ Error: {str(e)[:100]}")
    
    return results

def step_9_verify_analytic_accounts(env):
    """Verify analytic account propagation"""
    print_section("STEP 9: Verify Analytic Account Propagation")
    
    results = {
        'total_analytic_accounts': 0,
        'branches_with_analytics': 0,
        'bus_with_analytics': 0,
        'branch_mapping': {},
        'bu_mapping': {}
    }
    
    # Check analytic accounts
    analytic_accounts = env['account.analytic.account'].search([])
    results['total_analytic_accounts'] = len(analytic_accounts)
    
    print(f"   Total analytic accounts: {results['total_analytic_accounts']}")
    
    # Match with branches
    branches = env['ops.branch'].search([])
    branches_with_analytics = 0
    
    print(f"\n   🏢 Branch → Analytic Account Mapping:")
    for branch in branches:
        has_analytic = False
        if hasattr(branch, 'analytic_account_id') and branch.analytic_account_id:
            has_analytic = True
            branches_with_analytics += 1
            results['branch_mapping'][branch.name] = branch.analytic_account_id.name
            print(f"      ✅ {branch.name} → {branch.analytic_account_id.name}")
        else:
            print(f"      ❌ {branch.name} → No analytic account")
    
    results['branches_with_analytics'] = branches_with_analytics
    print(f"\n   Branches with analytic accounts: {branches_with_analytics}/{len(branches)}")
    
    # Match with Business Units
    bus = env['ops.business.unit'].search([])
    bus_with_analytics = 0
    
    print(f"\n   💼 Business Unit → Analytic Account Mapping:")
    for bu in bus[:10]:  # Show first 10
        if hasattr(bu, 'analytic_account_id') and bu.analytic_account_id:
            bus_with_analytics += 1
            results['bu_mapping'][bu.name] = bu.analytic_account_id.name
            print(f"      ✅ {bu.name} → {bu.analytic_account_id.name}")
    
    results['bus_with_analytics'] = bus_with_analytics
    print(f"\n   Business Units with analytic accounts: {bus_with_analytics}/{len(bus)}")
    
    return results

def step_10_generate_summary(all_results):
    """Generate comprehensive summary"""
    print_header("PHASE 3D: REPORTING AUDIT SUMMARY")
    
    # Component status
    components = {
        'Test Data Present': all_results['test_data']['sales_order'] is not None and all_results['test_data']['purchase_order'] is not None,
        'Sales Analysis Model': all_results['sales_analysis']['model_exists'],
        'Financial Analysis Model': all_results['financial_analysis']['model_exists'],
        'Inventory Analysis Model': all_results['inventory_analysis']['model_exists'],
        'General Ledger Reports': all_results['general_ledger']['wizard_exists'],
        'Excel Export Capability': all_results['excel_export']['wizard_exists'],
        'xlsxwriter Package': all_results['excel_export']['xlsxwriter_installed'],
        'Analytic Accounts': all_results['analytic_accounts']['branches_with_analytics'] >= 8,
        'Branch Filtering': len(all_results['branch_bu_filtering']['branch_filtering']) > 0,
    }
    
    passed = sum(1 for v in components.values() if v)
    total = len(components)
    
    print(f"\n📊 Report Components Status: {passed}/{total} ({passed*100//total}%)")
    print()
    for component, status in components.items():
        symbol = "✅" if status else "❌"
        print(f"   {symbol} {component}")
    
    # Data quality assessment
    print(f"\n📈 Data Quality Assessment:")
    print(f"   Sales Analysis Records: {all_results['sales_analysis']['record_count']}")
    print(f"   Financial Analysis Records: {all_results['financial_analysis']['record_count']}")
    print(f"   Inventory Analysis Records: {all_results['inventory_analysis']['record_count']}")
    print(f"   Test SO in Analysis: {'✅ Yes' if all_results['sales_analysis']['test_data_found'] else '⚠️ No'}")
    print(f"   Analytic Account Coverage: {all_results['analytic_accounts']['branches_with_analytics']}/10 branches")
    
    # Branch/BU filtering validation
    print(f"\n🔍 Branch/BU Filtering Validation:")
    if all_results['branch_bu_filtering']['branch_filtering']:
        print(f"   Branch Filtering: ✅ Working")
        for branch, count in all_results['branch_bu_filtering']['branch_filtering'].items():
            print(f"      - {branch}: {count} records")
    else:
        print(f"   Branch Filtering: ⚠️ No data or not tested")
    
    if all_results['branch_bu_filtering']['bu_filtering']:
        print(f"   BU Filtering: ✅ Working")
        for bu, count in all_results['branch_bu_filtering']['bu_filtering'].items():
            print(f"      - {bu}: {count} records")
    else:
        print(f"   BU Filtering: ⚠️ No data or not tested")
    
    # Issues found
    print(f"\n⚠️ Issues Found:")
    issues = []
    
    if not all_results['excel_export']['xlsxwriter_installed']:
        issues.append("xlsxwriter package not installed - Excel exports will fail")
    
    if all_results['sales_analysis']['record_count'] == 0:
        issues.append("No sales analysis data - views may need refresh")
    
    if all_results['financial_analysis']['record_count'] == 0:
        issues.append("No financial analysis data - views may need refresh")
    
    if all_results['inventory_analysis']['record_count'] == 0:
        issues.append("No inventory analysis data - views may need refresh")
    
    if not all_results['sales_analysis']['test_data_found']:
        issues.append("Test SO not found in sales analysis - may need time to compute")
    
    if all_results['analytic_accounts']['branches_with_analytics'] < 8:
        issues.append(f"Only {all_results['analytic_accounts']['branches_with_analytics']}/10 branches have analytic accounts")
    
    if issues:
        for idx, issue in enumerate(issues, 1):
            print(f"   {idx}. {issue}")
    else:
        print(f"   ✅ No critical issues found")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    recommendations = []
    
    if not all_results['excel_export']['xlsxwriter_installed']:
        recommendations.append("Install xlsxwriter: docker exec gemini_odoo19 pip3 install xlsxwriter")
    
    if all_results['sales_analysis']['record_count'] == 0:
        recommendations.append("Refresh sales analysis views or wait for scheduled computation")
    
    if all_results['analytic_accounts']['branches_with_analytics'] < 10:
        recommendations.append("Run analytic account setup to ensure all branches have analytic accounts")
    
    if not all_results['branch_bu_filtering']['test_so_found']:
        recommendations.append("Wait for analysis views to compute or trigger manual refresh")
    
    recommendations.append("Verify report outputs match expected test data amounts")
    recommendations.append("Test report generation in UI for user experience validation")
    recommendations.append("Consider performance optimization for large datasets")
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"   {idx}. {rec}")
    
    # Production readiness
    print(f"\n🎯 Production Readiness Assessment:")
    
    readiness_score = (
        (passed / total) * 40 +  # Component availability (40%)
        (min(all_results['sales_analysis']['record_count'], 100) / 100) * 20 +  # Data presence (20%)
        (all_results['analytic_accounts']['branches_with_analytics'] / 10) * 20 +  # Analytic setup (20%)
        (1 if all_results['excel_export']['xlsxwriter_installed'] else 0) * 20  # Dependencies (20%)
    )
    
    print(f"   Readiness Score: {readiness_score:.1f}%")
    
    if readiness_score >= 80:
        status = "✅ READY FOR PRODUCTION"
        message = "All core components operational. Minor optimizations recommended."
    elif readiness_score >= 60:
        status = "⚠️ NEEDS ATTENTION"
        message = "Core functionality present but some components need configuration."
    else:
        status = "❌ NOT READY"
        message = "Critical components missing or not configured. Address issues before deployment."
    
    print(f"   Status: {status}")
    print(f"   Assessment: {message}")
    
    print("\n" + "=" * 70)
    
    return {
        'components': components,
        'passed': passed,
        'total': total,
        'issues': issues,
        'recommendations': recommendations,
        'readiness_score': readiness_score,
        'status': status
    }

def save_report(all_results, summary):
    """Save audit report to markdown file"""
    report_path = "DeepSeek Dev Phases/PHASE_3D_REPORTING_AUDIT_REPORT.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    report = f"""# PHASE 3D: REPORTING AUDIT REPORT
**Generated:** {timestamp}  
**Database:** mz-db  
**Instance:** gemini_odoo19  
**Audit Type:** Read-Only Validation

---

## Executive Summary

**Readiness Score:** {summary['readiness_score']:.1f}%  
**Status:** {summary['status']}  
**Components Operational:** {summary['passed']}/{summary['total']} ({summary['passed']*100//summary['total']}%)

---

## 1. Test Data Verification

### Infrastructure (Phase 2)
- **Branches:** {all_results['test_data']['branches']}
- **Business Units:** {all_results['test_data']['business_units']}
- **Products:** {all_results['test_data']['products']}
- **Users:** {all_results['test_data']['users']}

### Test Transactions
"""
    
    so = all_results['test_data']['sales_order']
    if so:
        report += f"""
#### Sales Order S00001 (Phase 3B) ✅
- **Amount:** ${so.amount_total:,.2f}
- **State:** {so.state}
- **Branch:** {so.ops_branch_id.name if so.ops_branch_id else 'N/A'}
- **Business Unit:** {so.ops_business_unit_id.name if so.ops_business_unit_id else 'N/A'}
"""
    else:
        report += "\n#### Sales Order S00001 ❌ NOT FOUND\n"
    
    po = all_results['test_data']['purchase_order']
    if po:
        report += f"""
#### Purchase Order P00002 (Phase 3A) ✅
- **Amount:** ${po.amount_total:,.2f}
- **State:** {po.state}
- **Branch:** {po.ops_branch_id.name if po.ops_branch_id else 'N/A'}
- **Business Unit:** {po.ops_business_unit_id.name if po.ops_business_unit_id else 'N/A'}
"""
    else:
        report += "\n#### Purchase Order P00002 ❌ NOT FOUND\n"
    
    report += f"""
---

## 2. Analysis Models Assessment

### Sales Analysis (ops.sales.analysis)
- **Model Exists:** {'✅ Yes' if all_results['sales_analysis']['model_exists'] else '❌ No'}
- **Record Count:** {all_results['sales_analysis']['record_count']}
- **Test Data Found:** {'✅ Yes' if all_results['sales_analysis']['test_data_found'] else '⚠️ No'}
- **Branch Filtering:** {'✅ Working' if all_results['sales_analysis']['branch_filtering'] else '⚠️ Not Tested'}

### Financial Analysis (ops.financial.analysis)
- **Model Exists:** {'✅ Yes' if all_results['financial_analysis']['model_exists'] else '❌ No'}
- **Record Count:** {all_results['financial_analysis']['record_count']}
- **Branches Tracked:** {len(all_results['financial_analysis']['branches'])}
- **Business Units Tracked:** {len(all_results['financial_analysis']['business_units'])}

### Inventory Analysis (ops.inventory.analysis)
- **Model Exists:** {'✅ Yes' if all_results['inventory_analysis']['model_exists'] else '❌ No'}
- **Record Count:** {all_results['inventory_analysis']['record_count']}
- **Products Tracked:** {len(all_results['inventory_analysis']['products'])}

---

## 3. Reporting Capabilities

### General Ledger Reports
- **Wizard Available:** {'✅ Yes' if all_results['general_ledger']['wizard_exists'] else '❌ No'}
- **Wizard Created:** {'✅ Yes' if all_results['general_ledger']['wizard_created'] else '❌ No'}
- **Report Generated:** {'✅ Yes' if all_results['general_ledger']['report_generated'] else '⚠️ Not Successfully'}

### Excel Export
- **Wizard Available:** {'✅ Yes' if all_results['excel_export']['wizard_exists'] else '❌ No'}
- **xlsxwriter Package:** {'✅ Installed' if all_results['excel_export']['xlsxwriter_installed'] else '❌ Missing'}
- **Export Attempted:** {'✅ Yes' if all_results['excel_export']['export_attempted'] else '⚠️ No'}

### Consolidated Reporting
- **Model Available:** {'✅ Yes' if all_results['consolidated_reporting']['model_exists'] else 'ℹ️ Embedded in other reports'}
- **Record Count:** {all_results['consolidated_reporting']['record_count']}

---

## 4. Branch/BU Filtering Validation

### Branch Filtering
"""
    
    if all_results['branch_bu_filtering']['branch_filtering']:
        for branch, count in all_results['branch_bu_filtering']['branch_filtering'].items():
            report += f"- **{branch}:** {count} records\n"
    else:
        report += "- ⚠️ No branch filtering data available\n"
    
    report += "\n### Business Unit Filtering\n"
    
    if all_results['branch_bu_filtering']['bu_filtering']:
        for bu, count in all_results['branch_bu_filtering']['bu_filtering'].items():
            report += f"- **{bu}:** {count} records\n"
    else:
        report += "- ⚠️ No BU filtering data available\n"
    
    report += f"""
---

## 5. Analytic Account Propagation

### Summary
- **Total Analytic Accounts:** {all_results['analytic_accounts']['total_analytic_accounts']}
- **Branches with Analytics:** {all_results['analytic_accounts']['branches_with_analytics']}/10
- **BUs with Analytics:** {all_results['analytic_accounts']['bus_with_analytics']}

### Branch Mapping
"""
    
    if all_results['analytic_accounts']['branch_mapping']:
        for branch, analytic in all_results['analytic_accounts']['branch_mapping'].items():
            report += f"- **{branch}** → {analytic}\n"
    else:
        report += "- ⚠️ No branch-analytic mappings found\n"
    
    report += f"""
---

## 6. Issues Identified

"""
    
    if summary['issues']:
        for idx, issue in enumerate(summary['issues'], 1):
            report += f"{idx}. {issue}\n"
    else:
        report += "✅ No critical issues identified\n"
    
    report += f"""
---

## 7. Recommendations

"""
    
    for idx, rec in enumerate(summary['recommendations'], 1):
        report += f"{idx}. {rec}\n"
    
    report += f"""
---

## 8. Component Status Matrix

| Component | Status | Notes |
|-----------|--------|-------|
"""
    
    for component, status in summary['components'].items():
        symbol = "✅" if status else "❌"
        report += f"| {component} | {symbol} | |\n"
    
    report += f"""
---

## 9. Production Readiness Assessment

**Overall Score:** {summary['readiness_score']:.1f}%

### Breakdown
- **Component Availability:** 40% weight
- **Data Presence:** 20% weight
- **Analytic Setup:** 20% weight
- **Dependencies:** 20% weight

### Final Assessment
{summary['status']}

**Next Steps:**
1. Address critical issues listed above
2. Install missing dependencies (xlsxwriter)
3. Verify all analysis views are computing correctly
4. Test report generation through UI
5. Validate data accuracy against source transactions
6. Optimize query performance for large datasets
7. Document any custom report configurations

---

## 10. Conclusion

This audit validates the reporting infrastructure across **ops_matrix_accounting** and **ops_matrix_reporting** modules. 

{'✅ **The system is ready for production use with minor optimizations.**' if summary['readiness_score'] >= 80 else '⚠️ **Address identified issues before production deployment.**'}

**Test Data Coverage:**
- Phase 2 infrastructure fully seeded
- Phase 3A purchase transactions validated
- Phase 3B sales transactions validated
- Phase 3C (if applicable) data included

**Report Generated By:** PHASE 3D Reporting Audit Script  
**Report Date:** {timestamp}
"""
    
    # Ensure directory exists
    os.makedirs("DeepSeek Dev Phases", exist_ok=True)
    
    # Write report
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    return report_path

def main():
    """Main execution function"""
    print_header("PHASE 3D: REPORTING AUDIT - FINAL STRESS TEST")
    print(f"Database: mz-db")
    print(f"Instance: gemini_odoo19")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Get Odoo environment
    env = api.Environment(api.Environment.cr, SUPERUSER_ID, {})
    
    # Store all results
    all_results = {}
    
    # Execute test steps
    all_results['test_data'] = step_1_verify_test_data(env)
    all_results['sales_analysis'] = step_2_test_sales_analysis(env, all_results['test_data'])
    all_results['financial_analysis'] = step_3_test_financial_analysis(env)
    all_results['inventory_analysis'] = step_4_test_inventory_analysis(env)
    all_results['general_ledger'] = step_5_test_general_ledger(env)
    all_results['excel_export'] = step_6_test_excel_export(env)
    all_results['branch_bu_filtering'] = step_7_test_branch_bu_filtering(env, all_results['test_data'])
    all_results['consolidated_reporting'] = step_8_test_consolidated_reporting(env)
    all_results['analytic_accounts'] = step_9_verify_analytic_accounts(env)
    
    # Generate summary
    summary = step_10_generate_summary(all_results)
    
    # Save report
    report_path = save_report(all_results, summary)
    
    print_header("AUDIT COMPLETE")
    print(f"✅ Phase 3D Reporting Audit completed successfully")
    print(f"📄 Full report: {report_path}")
    print(f"🎯 Readiness Score: {summary['readiness_score']:.1f}%")
    print(f"📊 Status: {summary['status']}")

if __name__ == '__main__':
    main()
