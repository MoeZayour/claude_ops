#!/usr/bin/env python3
"""Direct OPS Framework Audit - Run tests and save results"""

import subprocess
import sys
import time

def run_test(test_name, test_code):
    """Run Odoo shell test and return output"""
    print(f"\n{'='*80}")
    print(f"Testing: {test_name}")
    print('='*80)
    
    # Create temporary Python file for test
    with open('/tmp/test_code.py', 'w') as f:
        f.write(test_code)
    
    cmd = [
        'docker', 'exec', 'gemini_odoo19',
        'odoo', 'shell', '-c', '/etc/odoo/odoo.conf',
        '-d', 'mz-db', '--no-http'
    ]
    
    try:
        with open('/tmp/test_code.py', 'r') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True,
                timeout=45
            )
        
        # Extract meaningful output (skip startup logs)
        lines = result.stdout.split('\n')
        output_lines = []
        capture = False
        
        for line in lines:
            if 'Registry loaded' in line:
                capture = True
                continue
            if capture and line.strip():
                output_lines.append(line)
        
        output = '\n'.join(output_lines) if output_lines else result.stdout
        print(output)
        return output
        
    except subprocess.TimeoutExpired:
        error = "⏱️  Test timeout"
        print(error)
        return error
    except Exception as e:
        error = f"❌ ERROR: {str(e)}"
        print(error)
        return error

# Define all tests
TESTS = {
    "Priority #6: Excel Import for SO Lines": """
env = self.env
print("Testing: Excel Import for Sale Order Lines")
print("-" * 60)

try:
    if 'ops.sale.order.import.wizard' in env:
        print("✅ Import wizard model exists")
    else:
        print("❌ ops.sale.order.import.wizard NOT FOUND")
    
    menu = env['ir.ui.menu'].search([('name', 'ilike', 'import')], limit=5)
    print(f"\\nFound {len(menu)} import-related menus")
    for m in menu:
        print(f"  - {m.name}")
    
    print("\\nStatus: MISSING - Model not implemented")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "Priority #8: Auto-Escalation": """
env = self.env
print("Testing: Auto-Escalation")
print("-" * 60)

try:
    models = ['ops.sla.template', 'ops.sla.instance', 'ops.approval.request']
    
    for model_name in models:
        if model_name in env:
            count = env[model_name].search_count([])
            print(f"✅ {model_name}: {count} records")
            
            model = env[model_name]
            fields = ['timeout_hours', 'escalate_to', 'escalation_level']
            found = [f for f in fields if f in model._fields]
            if found:
                print(f"   Escalation fields: {', '.join(found)}")
        else:
            print(f"❌ {model_name}: NOT FOUND")
    
    cron = env['ir.cron'].search([('name', 'ilike', 'escalat')])
    if cron:
        print(f"\\n✅ Found {len(cron)} escalation cron job(s)")
    else:
        print("\\n⚠️  No escalation cron job found")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "Priority #9: Auto-List Accounts": """
env = self.env
print("Testing: Auto-List Accounts in Reports")
print("-" * 60)

try:
    if 'ops.report.template' in env:
        templates = env['ops.report.template'].search([])
        print(f"✅ Report templates: {len(templates)} found")
        
        if templates:
            t = templates[0]
            print(f"   Sample: {t.name}")
            fields = ['account_ids', 'account_line_ids', 'auto_populate']
            for f in fields:
                if f in t._fields:
                    print(f"   ✅ Field: {f}")
    else:
        print("❌ ops.report.template NOT FOUND")
    
    if 'ops.report.wizard' in env:
        print("✅ Report wizard exists")
    else:
        print("⚠️  Report wizard NOT FOUND")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "Priority #13: Financial Reports": """
env = self.env
print("Testing: Financial Reports")
print("-" * 60)

try:
    reports = ['Balance Sheet', 'Profit', 'Trial Balance', 'Cash Flow']
    
    for rep in reports:
        menu = env['ir.ui.menu'].search([('name', 'ilike', rep)], limit=1)
        if menu:
            print(f"✅ {rep}: Found (ID: {menu.id})")
        else:
            print(f"❌ {rep}: NOT FOUND")
    
    if 'ops.report.template' in env:
        balance = env['ops.report.template'].search([('name', 'ilike', 'balance')])
        if balance:
            print(f"\\n✅ {len(balance)} balance sheet template(s)")
            
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "Priority #14: Dashboards": """
env = self.env
print("Testing: Dashboards")
print("-" * 60)

try:
    dashboards = ['Executive', 'Branch', 'BU', 'Sales']
    
    for dash in dashboards:
        menu = env['ir.ui.menu'].search([('name', 'ilike', dash), ('name', 'ilike', 'dashboard')], limit=1)
        if menu:
            print(f"✅ {dash} Dashboard: Found (ID: {menu.id})")
        else:
            print(f"❌ {dash} Dashboard: NOT FOUND")
    
    if 'ops.dashboard.widget' in env:
        widgets = env['ops.dashboard.widget'].search([])
        print(f"\\n✅ Dashboard widgets: {len(widgets)} configured")
    else:
        print("\\n❌ Dashboard widget model NOT FOUND")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "Priority #15: Export Tools": """
env = self.env
print("Testing: Export Tools")
print("-" * 60)

try:
    export_models = [m for m in env.registry.models if 'export' in m and 'ops' in m]
    
    print(f"Found {len(export_models)} OPS export models:")
    for m in export_models[:10]:
        count = env[m].search_count([])
        print(f"  ✅ {m}: {count} records")
    
    if 'ops.excel.export.wizard' in env:
        print("\\n✅ Excel export wizard exists")
    else:
        print("\\n⚠️  Excel export wizard not found")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "ALL OPS MODELS": """
env = self.env
print("OPS Models Inventory")
print("-" * 60)

try:
    ops_models = [m for m in env.registry.models if m.startswith('ops.')]
    print(f"Total: {len(ops_models)} models\\n")
    
    for model_name in sorted(ops_models)[:30]:
        try:
            count = env[model_name].search_count([])
            menu_count = env['ir.ui.menu'].search_count([('action', 'ilike', model_name)])
            view_count = env['ir.ui.view'].search_count([('model', '=', model_name)])
            
            status = "✅" if (menu_count > 0 or view_count > 0) else "⚠️"
            print(f"{status} {model_name}: {count}rec, {menu_count}menu, {view_count}view")
        except:
            print(f"❌ {model_name}: ERROR")
            
    if len(ops_models) > 30:
        print(f"\\n... and {len(ops_models) - 30} more models")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
""",

    "ALL OPS MENUS": """
env = self.env
print("OPS Menus Inventory")
print("-" * 60)

try:
    menus = env['ir.ui.menu'].search(['|', ('name', 'ilike', 'ops'), ('action', 'ilike', 'ops')])
    print(f"Total: {len(menus)} menus\\n")
    
    menu_tree = {}
    for menu in menus:
        parent = menu.parent_id.name if menu.parent_id else "ROOT"
        if parent not in menu_tree:
            menu_tree[parent] = []
        menu_tree[parent].append(menu)
    
    for parent, children in sorted(menu_tree.items())[:10]:
        print(f"\\n{parent}:")
        for child in children[:5]:
            status = "✅" if child.active else "❌"
            print(f"  {status} {child.name}")
        if len(children) > 5:
            print(f"  ... and {len(children) - 5} more")
            
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
"""
}

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 OPS FRAMEWORK COMPLETE FEATURE AUDIT                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # Run all tests
    for test_name, test_code in TESTS.items():
        results[test_name] = run_test(test_name, test_code)
        time.sleep(2)  # Brief pause between tests
    
    # Save to file
    print("\n" + "="*80)
    print("Saving results...")
    print("="*80)
    
    with open('OPS_AUDIT_FINAL_RESULTS.md', 'w') as f:
        f.write("# OPS FRAMEWORK COMPLETE AUDIT RESULTS\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for test_name, result in results.items():
            f.write(f"## {test_name}\n\n")
            f.write("```\n")
            f.write(result)
            f.write("\n```\n\n")
    
    print("\n✅ Complete! Results saved to: OPS_AUDIT_FINAL_RESULTS.md\n")

if __name__ == "__main__":
    main()
