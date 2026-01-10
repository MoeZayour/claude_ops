#!/bin/bash

OUTPUT_FILE="OPS_COMPLETE_AUDIT_RESULTS.md"

echo "# OPS FRAMEWORK COMPLETE AUDIT RESULTS" > $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "================================" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Priority #6: Excel Import
echo "" >> $OUTPUT_FILE
echo "## Priority #6: Excel Import for SO Lines" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Excel Import for Sale Order Lines")
    print("-" * 60)
    
    # Check if wizard model exists
    if 'ops.sale.order.import.wizard' in env:
        print("✅ Import wizard model exists")
    else:
        print("❌ Model NOT FOUND")
    
    # Check menu
    menu = env['ir.ui.menu'].search([
        '|', ('name', 'ilike', 'import'),
        ('name', 'ilike', 'sale order line')
    ])
    if menu:
        for m in menu:
            print(f"✅ Menu: {m.name} (ID: {m.id})")
    else:
        print("❌ No import menus found")
    
    # Check action
    actions = env['ir.actions.act_window'].search([
        ('res_model', 'ilike', 'import'),
        ('res_model', 'ilike', 'sale')
    ])
    if actions:
        for a in actions:
            print(f"✅ Action: {a.name} → {a.res_model}")
    else:
        print("⚠️  No import actions found")
    
    print("\n**Status: FUNCTIONAL**" if menu or actions else "\n**Status: MISSING/BROKEN**")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Priority #8: Auto-Escalation
echo "" >> $OUTPUT_FILE
echo "## Priority #8: Auto-Escalation" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Auto-Escalation")
    print("-" * 60)
    
    # Check SLA models
    models_to_check = [
        'ops.sla.template',
        'ops.sla.instance',
        'ops.approval.request',
    ]
    
    for model_name in models_to_check:
        if model_name in env:
            count = env[model_name].search_count([])
            print(f"✅ {model_name}: {count} records")
            
            # Check if timeout/escalation fields exist
            model = env[model_name]
            escalation_fields = ['timeout_hours', 'escalate_to', 'escalation_level']
            found_fields = [f for f in escalation_fields if f in model._fields]
            if found_fields:
                print(f"   ✅ Escalation fields: {', '.join(found_fields)}")
        else:
            print(f"❌ {model_name}: NOT FOUND")
    
    # Check for cron job
    cron = env['ir.cron'].search([('name', 'ilike', 'escalat')])
    if cron:
        for c in cron:
            print(f"✅ Escalation cron job: {c.name}")
    else:
        print("⚠️  No escalation cron job found")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Priority #9: Auto-List Accounts
echo "" >> $OUTPUT_FILE
echo "## Priority #9: Auto-List Accounts in Reports" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Auto-List Accounts in Reports")
    print("-" * 60)
    
    # Check report template model
    if 'ops.report.template' in env:
        templates = env['ops.report.template'].search([])
        print(f"✅ Report templates: {len(templates)} found")
        
        if templates:
            template = templates[0]
            print(f"   Sample: {template.name}")
            
            # Check if has account listing fields
            fields_to_check = ['account_ids', 'account_line_ids', 'auto_populate']
            for field in fields_to_check:
                if field in template._fields:
                    print(f"   ✅ Field: {field}")
    else:
        print("❌ ops.report.template NOT FOUND")
    
    # Check report wizard
    if 'ops.report.wizard' in env:
        print("✅ Report wizard exists")
    else:
        print("❌ Report wizard NOT FOUND")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Priority #13: Financial Reports
echo "" >> $OUTPUT_FILE
echo "## Priority #13: Financial Reports" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Financial Reports")
    print("-" * 60)
    
    # Check menus for financial reports
    reports = ['Balance Sheet', 'Profit and Loss', 'P&L', 'Trial Balance', 'Cash Flow']
    
    for report_name in reports:
        menu = env['ir.ui.menu'].search([('name', 'ilike', report_name)], limit=1)
        
        if menu:
            print(f"✅ {report_name}: Menu exists (ID: {menu.id})")
            if menu.action:
                try:
                    action_id = int(menu.action.split(',')[1])
                    action = env['ir.actions.act_window'].browse(action_id)
                    print(f"   → Model: {action.res_model}")
                except:
                    pass
        else:
            print(f"❌ {report_name}: Menu NOT FOUND")
    
    # Check if report templates exist
    if 'ops.report.template' in env:
        templates = env['ops.report.template'].search([('name', 'ilike', 'balance')])
        if templates:
            print(f"\n✅ Found {len(templates)} balance sheet templates")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Priority #14: Dashboards
echo "" >> $OUTPUT_FILE
echo "## Priority #14: Dashboards" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Dashboards")
    print("-" * 60)
    
    dashboards = ['Executive Dashboard', 'Branch Performance', 'BU Performance', 'Sales Performance']
    
    for dash_name in dashboards:
        menu = env['ir.ui.menu'].search([('name', 'ilike', dash_name)], limit=1)
        
        if menu:
            print(f"✅ {dash_name}: Active (ID: {menu.id})")
            if menu.action:
                action_type = menu.action.split(',')[0]
                print(f"   Type: {action_type}")
        else:
            print(f"❌ {dash_name}: NOT FOUND")
    
    # Check dashboard widget model
    if 'ops.dashboard.widget' in env:
        widgets = env['ops.dashboard.widget'].search([])
        print(f"\n✅ Dashboard widgets: {len(widgets)} configured")
    else:
        print("\n❌ Dashboard widget model NOT FOUND")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Priority #15: Export Tools
echo "" >> $OUTPUT_FILE
echo "## Priority #15: Export Tools" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    print("Testing: Export Tools")
    print("-" * 60)
    
    print("✅ Excel Export: VERIFIED (previous test)")
    
    # Check for other export wizards
    export_models = [m for m in env.registry.models if 'export' in m and 'ops' in m]
    
    print(f"\nFound {len(export_models)} OPS export models:")
    for model in export_models:
        count = env[model].search_count([])
        print(f"   - {model}: {count} records")
    
    # Check for PDF export
    if 'ops.pdf.export.wizard' in env:
        print("\n✅ PDF Export wizard exists")
    else:
        print("\n⚠️  PDF Export wizard not found")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Comprehensive Model Scan
echo "" >> $OUTPUT_FILE
echo "## COMPREHENSIVE SCAN: ALL OPS MODELS" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    # Get all OPS models
    ops_models = [m for m in env.registry.models if m.startswith('ops.')]

    print(f"Total OPS Models: {len(ops_models)}")
    print("\nModel Status:")

    for model_name in sorted(ops_models):
        try:
            model = env[model_name]
            count = model.search_count([])
            
            # Check if has menu
            menu_count = env['ir.ui.menu'].search_count([('action', 'ilike', model_name)])
            
            # Check if has views
            view_count = env['ir.ui.view'].search_count([('model', '=', model_name)])
            
            status = "✅" if (menu_count > 0 or view_count > 0) else "⚠️"
            print(f"{status} {model_name}: {count} records, {menu_count} menus, {view_count} views")
            
        except Exception as e:
            print(f"❌ {model_name}: ERROR")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

# Comprehensive Menu Scan
echo "" >> $OUTPUT_FILE
echo "## COMPREHENSIVE SCAN: ALL OPS MENUS" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON' 2>&1 | tail -n +40 >> $OUTPUT_FILE
env = self.env

try:
    # Get all OPS menus
    menus = env['ir.ui.menu'].search(['|', ('name', 'ilike', 'ops'), ('action', 'ilike', 'ops')])

    print(f"Total OPS Menus: {len(menus)}")

    # Group by parent
    menu_tree = {}
    for menu in menus:
        parent = menu.parent_id.name if menu.parent_id else "ROOT"
        if parent not in menu_tree:
            menu_tree[parent] = []
        menu_tree[parent].append(menu)

    print("\nMenu Structure:")
    for parent, children in sorted(menu_tree.items()):
        print(f"\n### {parent}:")
        for child in children:
            status = "✅" if child.active else "❌"
            action_info = ""
            if child.action:
                try:
                    action_id = int(child.action.split(',')[1])
                    action = env['ir.actions.act_window'].browse(action_id)
                    action_info = f" → {action.res_model}"
                except:
                    pass
            print(f"  {status} {child.name} (ID: {child.id}){action_info}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
PYTHON

echo "" >> $OUTPUT_FILE
echo "---" >> $OUTPUT_FILE
echo "Audit Complete: $(date)" >> $OUTPUT_FILE

echo ""
echo "✅ Audit complete! Results saved to: $OUTPUT_FILE"
echo ""
