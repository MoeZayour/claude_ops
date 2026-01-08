print("=== SYSTEM CHECK ===")
# Check installed modules
modules = env['ir.module.module'].search([('name', 'in', ['ops_matrix_core', 'ops_matrix_accounting', 'ops_matrix_asset_management', 'ops_matrix_reporting'])])
print("=== INSTALLED MODULES ===")
for m in modules:
    print(f"{m.name}: state={m.state}")

# Check menu counts
print("\n=== MENU COUNT ===")
menus = env['ir.ui.menu'].search([])
print(f"Total menus: {len(menus)}")

# Check if OPS menus exist
ops_menus = env['ir.ui.menu'].search([('name', 'ilike', 'OPS')])
print(f"OPS menus: {len(ops_menus)}")

# Check model definitions
print("\n=== OPS MODELS ===")
models = ['ops.company', 'ops.business_unit', 'ops.branch', 'ops.persona',
          'ops.approval_category', 'ops.approval_request', 'ops.sob_rule',
          'ops.asset', 'ops.asset_category', 'ops.asset_depreciation']
for model in models:
    model_exists = env['ir.model'].search([('model', '=', model)])
    if model_exists:
        print(f"  OK: {model}")
    else:
        print(f"  MISSING: {model}")

print("\n=== CHECK COMPLETE ===")
