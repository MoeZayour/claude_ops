#!/bin/bash
# Verify module installation status

DB_NAME="mz-db"
CONTAINER="gemini_odoo19"

echo "=========================================="
echo "VERIFYING MODULE INSTALLATION STATUS"
echo "=========================================="

# Query module status from database
docker exec $CONTAINER odoo shell -d $DB_NAME --http-port=0 << 'PYTHON'
import sys
from odoo import api, SUPERUSER_ID

modules = [
    'ops_matrix_core',
    'ops_matrix_reporting', 
    'ops_matrix_accounting',
    'ops_matrix_asset_management'
]

env = api.Environment(self.env.cr, SUPERUSER_ID, {})

print("\n" + "="*60)
print("MODULE INSTALLATION STATUS")
print("="*60)

for module_name in modules:
    module = env['ir.module.module'].search([('name', '=', module_name)])
    if module:
        status = "✅" if module.state == 'installed' else "❌"
        print(f"{status} {module_name}: {module.state}")
    else:
        print(f"❌ {module_name}: NOT FOUND")

print("="*60)
PYTHON

