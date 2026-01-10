#!/usr/bin/env python3
"""Direct module installation via Odoo Python API"""
import os
import sys

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

# Set up environment
os.environ.setdefault('ODOO_CONFIG', '/etc/odoo/odoo.conf')

import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config

# Initialize Odoo config
config['db_name'] = 'mz-db'

# Load registry
registry = odoo.modules.registry.Registry.new('mz-db', update_module=True)

# Create environment
env = api.Environment(registry.cursor(), SUPERUSER_ID, {})

# Get modules to install
modules_to_install = ['ops_matrix_core', 'ops_matrix_accounting', 'ops_matrix_reporting', 'ops_matrix_asset_management']

print("=" * 70)
print("INSTALLING OPS MODULES VIA DIRECT PYTHON API")
print("=" * 70)

for module_name in modules_to_install:
    print(f"\n[*] Installing {module_name}...")
    try:
        module = env['ir.module.module'].search([('name', '=', module_name)])
        if module:
            if module.state == 'uninstalled':
                module.button_immediate_install()
                print(f"    ✓ {module_name} installed")
            else:
                print(f"    ✓ {module_name} already in state: {module.state}")
        else:
            print(f"    ✗ {module_name} not found")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("INSTALLATION COMPLETE")
print("=" * 70)
