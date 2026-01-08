#!/usr/bin/env python3
"""System check script for OPS Framework"""
import sys

# Check installed modules
modules = env['ir.module.module'].search([('name', 'in', ['ops_matrix_core', 'ops_matrix_accounting', 'ops_matrix_asset_management', 'ops_matrix_reporting'])])
print("=== INSTALLED MODULES ===")
for m in modules:
    print(f"{m.name}: state={m.state}, version={m.latest_version or 'N/A'}")

# Check menu counts
print("\n=== MENU COUNT ===")
menus = env['ir.ui.menu'].search([])
print(f"Total menus: {len(menus)}")

# Check if OPS menus exist
ops_menus = env['ir.ui.menu'].search([('name', 'ilike', 'OPS')])
print(f"OPS menus: {len(ops_menus)}")
for menu in ops_menus[:30]:
    print(f"  - {menu.name}")

# Check model definitions
print("\n=== OPS MODELS ===")
models = ['ops.company', 'ops.business_unit', 'ops.branch', 'ops.persona',
          'ops.approval_category', 'ops.approval_request', 'ops.sob_rule',
          'ops.asset', 'ops.asset_category', 'ops.asset_depreciation',
          'ops.budget', 'ops.budget_line']
for model in models:
    try:
        model_exists = env['ir.model'].search([('model', '=', model)])
        if model_exists:
            print(f"  ✓ {model}")
        else:
            print(f"  ✗ {model} - MISSING")
    except Exception as e:
        print(f"  ✗ {model} - ERROR: {e}")

# Check views
print("\n=== VIEWS ===")
view_types = ['tree', 'form', 'kanban', 'pivot', 'graph']
for view_type in view_types:
    count = env['ir.ui.view'].search_count([('type', '=', view_type), ('name', 'ilike', 'ops.')])
    print(f"  {view_type} views for ops: {count}")

# Check wizards
print("\n=== WIZARDS ===")
wizards = env['ir.model'].search([('model', 'ilike', 'wizard')])
for w in wizards[:20]:
    print(f"  - {w.model}: {w.name}")

print("\n=== CHECK COMPLETE ===")
