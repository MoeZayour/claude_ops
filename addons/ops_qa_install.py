#!/usr/bin/env python3
"""
OPS Framework Module Installation Script
Runs via odoo-bin shell to install all OPS modules in correct order
"""

import logging

_logger = logging.getLogger(__name__)

def install_ops_modules(env):
    """Install OPS modules in dependency order"""

    modules_to_install = [
        'ops_matrix_core',
        'ops_matrix_reporting',
        'ops_matrix_accounting',
        'ops_matrix_asset_management'
    ]

    print("\n" + "=" * 80)
    print("OPS FRAMEWORK v1.5.0 - MODULE INSTALLATION")
    print("=" * 80)

    IrModule = env['ir.module.module']

    for module_name in modules_to_install:
        print(f"\n[{module_name}]")

        module = IrModule.search([('name', '=', module_name)], limit=1)

        if not module:
            print(f"  ERROR: Module {module_name} not found!")
            continue

        if module.state == 'installed':
            print(f"  ✓ Already installed")
            continue

        print(f"  Installing...")
        try:
            module.button_immediate_install()
            print(f"  ✓ Successfully installed")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            return False

    print("\n" + "=" * 80)
    print("✅ MODULE INSTALLATION COMPLETED")
    print("=" * 80)
    return True

if __name__ == '__main__':
    install_ops_modules(env)
