#!/usr/bin/env python3
# Check if OPS modules are installed

print("Checking installed modules...")
installed_modules = env['ir.module.module'].search([
    ('state', '=', 'installed'),
    ('name', 'like', 'ops')
])

print(f"\nFound {len(installed_modules)} OPS modules:")
for module in installed_modules:
    print(f"  - {module.name}: {module.state}")

if not installed_modules:
    print("\n⚠️  WARNING: No OPS modules found!")
    print("Please install ops_matrix_core, ops_matrix_accounting, ops_matrix_reporting first.")
else:
    print("\n✓ OPS modules are installed")
    
    # Check if models are available
    if 'ops.branch' in env.registry:
        branch_count = env['ops.branch'].search_count([])
        print(f"✓ ops.branch model available ({branch_count} branches)")
    else:
        print("✗ ops.branch model NOT available")
    
    if 'ops.business.unit' in env.registry:
        bu_count = env['ops.business.unit'].search_count([])
        print(f"✓ ops.business.unit model available ({bu_count} BUs)")
    else:
        print("✗ ops.business.unit model NOT available")
    
    if 'ops.persona' in env.registry:
        persona_count = env['ops.persona'].search_count([])
        print(f"✓ ops.persona model available ({persona_count} personas)")
    else:
        print("✗ ops.persona model NOT available")
