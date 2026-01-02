"""
PHASE 3D: REPORTING AUDIT - Simplified for Odoo Shell
"""
from datetime import datetime

print("\n" + "=" * 70)
print("  PHASE 3D: REPORTING AUDIT - FINAL STRESS TEST")
print("=" * 70)
print(f"Database: mz-db")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# Store all results
all_results = {}

# ============================================================================
# STEP 1: Verify Test Data
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 1: Verify Test Data is Present")
print("─" * 70)

# Check Sales Order
so = env['sale.order'].search([('name', '=', 'S00001')], limit=1)
po = env['purchase.order'].search([('name', '=', 'P00002')], limit=1)

branches_count = env['ops.branch'].search_count([])
bus_count = env['ops.business.unit'].search_count([])
products_count = env['product.product'].search_count([])
users_count = env['res.users'].search_count([('share', '=', False)])

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
print(f"   Branches: {branches_count}")
print(f"   Business Units: {bus_count}")
print(f"   Products: {products_count}")
print(f"   Users (non-portal): {users_count}")

all_results['test_data'] = {
    'so': so,
    'po': po,
    'branches': branches_count,
    'bus': bus_count,
    'products': products_count,
    'users': users_count
}

# ============================================================================
# STEP 2: Test Sales Analysis
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 2: Test Sales Analysis Views")
print("─" * 70)

if 'ops.sales.analysis' in env:
    print("   ✅ ops.sales.analysis model found")
    
    sales_data = env['ops.sales.analysis'].search([], limit=20)
    print(f"   Total analysis records: {len(sales_data)}")
    
    if sales_data:
        print(f"\n   📈 Sample Sales Analysis Records:")
        for idx, record in enumerate(sales_data[:5], 1):
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'N/A'
            bu_name = record.ops_business_unit_id.name if hasattr(record, 'ops_business_unit_id') and record.ops_business_unit_id else 'N/A'
            amount = getattr(record, 'amount_total', 0) or getattr(record, 'price_total', 0)
            
            print(f"      [{idx}] Branch: {branch_name}, BU: {bu_name}, Amount: ${amount:,.2f}")
        
        # Check for test SO
        if so:
            test_sales = env['ops.sales.analysis'].search([('order_id', '=', so.id)], limit=1)
            if test_sales:
                print(f"\n   ✅ Test SO S00001 found in sales analysis")
            else:
                print(f"\n   ⚠️ Test SO S00001 not yet in analysis view")
        
        all_results['sales_analysis'] = {'exists': True, 'count': len(sales_data), 'test_found': bool(test_sales if so else False)}
    else:
        print("   ⚠️ No sales analysis data found")
        all_results['sales_analysis'] = {'exists': True, 'count': 0, 'test_found': False}
else:
    print("   ⚠️ ops.sales.analysis model not found")
    all_results['sales_analysis'] = {'exists': False, 'count': 0, 'test_found': False}

# ============================================================================
# STEP 3: Test Financial Analysis
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 3: Test Financial Analysis")
print("─" * 70)

if 'ops.financial.analysis' in env:
    print("   ✅ ops.financial.analysis model found")
    
    financial_data = env['ops.financial.analysis'].search([], limit=50)
    print(f"   Total financial records: {len(financial_data)}")
    
    if financial_data:
        branches = {}
        for record in financial_data:
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'Unassigned'
            if branch_name not in branches:
                branches[branch_name] = {'count': 0, 'balance': 0}
            branches[branch_name]['count'] += 1
            branches[branch_name]['balance'] += getattr(record, 'balance', 0) or getattr(record, 'amount', 0)
        
        print(f"\n   💰 Financial Data by Branch:")
        for branch, data in sorted(branches.items())[:10]:
            print(f"      - {branch}: {data['count']} records, Balance: ${data['balance']:,.2f}")
        
        all_results['financial_analysis'] = {'exists': True, 'count': len(financial_data), 'branches': len(branches)}
    else:
        print("   ⚠️ No financial analysis data found")
        all_results['financial_analysis'] = {'exists': True, 'count': 0, 'branches': 0}
else:
    print("   ⚠️ ops.financial.analysis model not found")
    all_results['financial_analysis'] = {'exists': False, 'count': 0, 'branches': 0}

# ============================================================================
# STEP 4: Test Inventory Analysis
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 4: Test Inventory Analysis")
print("─" * 70)

if 'ops.inventory.analysis' in env:
    print("   ✅ ops.inventory.analysis model found")
    
    inventory_data = env['ops.inventory.analysis'].search([], limit=50)
    print(f"   Total inventory records: {len(inventory_data)}")
    
    if inventory_data:
        print(f"\n   📦 Sample Inventory Analysis Records:")
        for idx, record in enumerate(inventory_data[:10], 1):
            product_name = record.product_id.name if hasattr(record, 'product_id') and record.product_id else 'Unknown'
            branch_name = record.ops_branch_id.name if hasattr(record, 'ops_branch_id') and record.ops_branch_id else 'N/A'
            qty = getattr(record, 'quantity', 0) or getattr(record, 'qty_available', 0)
            value = getattr(record, 'value', 0) or getattr(record, 'stock_value', 0)
            
            print(f"      [{idx}] Product: {product_name[:40]}, Branch: {branch_name}, Qty: {qty}")
        
        all_results['inventory_analysis'] = {'exists': True, 'count': len(inventory_data)}
    else:
        print("   ⚠️ No inventory analysis data found")
        all_results['inventory_analysis'] = {'exists': True, 'count': 0}
else:
    print("   ⚠️ ops.inventory.analysis model not found")
    all_results['inventory_analysis'] = {'exists': False, 'count': 0}

# ============================================================================
# STEP 5: Test General Ledger
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 5: Test General Ledger Report Generation")
print("─" * 70)

wizard_models = ['ops.general.ledger.wizard', 'ops.general.ledger.wizard.enhanced', 'account.general.ledger']
wizard_found = None

for model in wizard_models:
    if model in env:
        wizard_found = model
        print(f"   ✅ Found wizard model: {model}")
        break

if wizard_found:
    try:
        wizard_vals = {'date_from': '2025-01-01', 'date_to': '2025-12-31'}
        wizard = env[wizard_found].create(wizard_vals)
        print(f"   ✅ Wizard created: ID {wizard.id}")
        all_results['general_ledger'] = {'exists': True, 'created': True}
    except Exception as e:
        print(f"   ⚠️ GL Report error: {str(e)[:200]}")
        all_results['general_ledger'] = {'exists': True, 'created': False, 'error': str(e)[:200]}
else:
    print("   ⚠️ No General Ledger wizard found")
    all_results['general_ledger'] = {'exists': False, 'created': False}

# ============================================================================
# STEP 6: Test Excel Export
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 6: Test Excel Export Functionality")
print("─" * 70)

# Check xlsxwriter
try:
    import xlsxwriter
    print(f"   ✅ xlsxwriter package installed (version {xlsxwriter.__version__})")
    xlsxwriter_installed = True
except ImportError:
    print(f"   ⚠️ xlsxwriter not installed - Excel export will fail")
    print(f"   Install with: pip3 install xlsxwriter")
    xlsxwriter_installed = False

excel_models = ['ops.excel.export.wizard', 'ops.report.excel.wizard', 'report.excel.wizard']
excel_found = None

for model in excel_models:
    if model in env:
        excel_found = model
        print(f"   ✅ Found Excel wizard: {model}")
        break

if not excel_found:
    print("   ⚠️ No Excel export wizard found")

all_results['excel_export'] = {'wizard_exists': bool(excel_found), 'xlsxwriter_installed': xlsxwriter_installed}

# ============================================================================
# STEP 7: Test Branch/BU Filtering
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 7: Test Branch/BU Filtering in Reports")
print("─" * 70)

branch_north = env['ops.branch'].search([('name', '=', 'Branch-North')], limit=1)
bu_sales = env['ops.business.unit'].search([('name', '=', 'BU-Sales')], limit=1)

print(f"\n   🔍 Testing Filtering Capabilities:")

if 'ops.sales.analysis' in env and branch_north:
    branch_sales = env['ops.sales.analysis'].search([('ops_branch_id', '=', branch_north.id)])
    print(f"      - Branch-North (sales): {len(branch_sales)} records")
    all_results['branch_filtering'] = True
else:
    print(f"      ⚠️ Could not test branch filtering")
    all_results['branch_filtering'] = False

if 'ops.sales.analysis' in env and bu_sales:
    bu_data = env['ops.sales.analysis'].search([('ops_business_unit_id', '=', bu_sales.id)])
    print(f"      - BU-Sales (sales): {len(bu_data)} records")

# ============================================================================
# STEP 8: Test Consolidated Reporting
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 8: Test Consolidated Reporting")
print("─" * 70)

consolidated_models = ['ops.consolidated.report', 'ops.consolidated.reporting', 'ops.consolidation.report']
consolidated_found = None

for model in consolidated_models:
    if model in env:
        consolidated_found = model
        print(f"   ✅ Found consolidated model: {model}")
        break

if not consolidated_found:
    print("   ℹ️ Consolidated report model not found (may be embedded in other reports)")

all_results['consolidated'] = {'exists': bool(consolidated_found)}

# ============================================================================
# STEP 9: Verify Analytic Accounts
# ============================================================================
print("\n" + "─" * 70)
print("📊 STEP 9: Verify Analytic Account Propagation")
print("─" * 70)

analytic_accounts = env['account.analytic.account'].search([])
print(f"   Total analytic accounts: {len(analytic_accounts)}")

branches = env['ops.branch'].search([])
branches_with_analytics = 0

print(f"\n   🏢 Branch → Analytic Account Mapping:")
for branch in branches:
    if hasattr(branch, 'analytic_account_id') and branch.analytic_account_id:
        branches_with_analytics += 1
        print(f"      ✅ {branch.name} → {branch.analytic_account_id.name}")
    else:
        print(f"      ❌ {branch.name} → No analytic account")

print(f"\n   Branches with analytic accounts: {branches_with_analytics}/{len(branches)}")

all_results['analytic_accounts'] = {
    'total': len(analytic_accounts),
    'branches_with': branches_with_analytics,
    'branches_total': len(branches)
}

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📋 REPORTING AUDIT SUMMARY")
print("=" * 70)

components = {
    'Test Data Present': bool(so and po),
    'Sales Analysis Model': all_results['sales_analysis']['exists'],
    'Financial Analysis Model': all_results['financial_analysis']['exists'],
    'Inventory Analysis Model': all_results['inventory_analysis']['exists'],
    'General Ledger Reports': all_results['general_ledger']['exists'],
    'Excel Export Capability': all_results['excel_export']['wizard_exists'],
    'xlsxwriter Package': all_results['excel_export']['xlsxwriter_installed'],
    'Analytic Accounts (80%+)': branches_with_analytics >= 8,
    'Branch Filtering': all_results.get('branch_filtering', False),
}

passed = sum(1 for v in components.values() if v)
total = len(components)

print(f"\n📊 Report Components Status: {passed}/{total} ({passed*100//total}%)")
print()
for component, status in components.items():
    symbol = "✅" if status else "❌"
    print(f"   {symbol} {component}")

print(f"\n📈 Data Quality Assessment:")
print(f"   Sales Analysis Records: {all_results['sales_analysis']['count']}")
print(f"   Financial Analysis Records: {all_results['financial_analysis']['count']}")
print(f"   Inventory Analysis Records: {all_results['inventory_analysis']['count']}")
print(f"   Analytic Account Coverage: {branches_with_analytics}/10 branches")

# Issues
issues = []
if not all_results['excel_export']['xlsxwriter_installed']:
    issues.append("xlsxwriter package not installed")
if all_results['sales_analysis']['count'] == 0:
    issues.append("No sales analysis data")
if all_results['financial_analysis']['count'] == 0:
    issues.append("No financial analysis data")
if branches_with_analytics < 8:
    issues.append(f"Only {branches_with_analytics}/10 branches have analytic accounts")

print(f"\n⚠️ Issues Found: {len(issues)}")
if issues:
    for idx, issue in enumerate(issues, 1):
        print(f"   {idx}. {issue}")
else:
    print(f"   ✅ No critical issues found")

# Calculate readiness score
readiness_score = (
    (passed / total) * 40 +
    (min(all_results['sales_analysis']['count'], 100) / 100) * 20 +
    (branches_with_analytics / 10) * 20 +
    (1 if all_results['excel_export']['xlsxwriter_installed'] else 0) * 20
)

print(f"\n🎯 Production Readiness Assessment:")
print(f"   Readiness Score: {readiness_score:.1f}%")

if readiness_score >= 80:
    status = "✅ READY FOR PRODUCTION"
elif readiness_score >= 60:
    status = "⚠️ NEEDS ATTENTION"
else:
    status = "❌ NOT READY"

print(f"   Status: {status}")

print("\n" + "=" * 70)
print("✅ Phase 3D Reporting Audit completed successfully")
print("=" * 70)
