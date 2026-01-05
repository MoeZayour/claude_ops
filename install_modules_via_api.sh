#!/bin/bash

# Direct module installation via Odoo API
# This approach avoids the --stop-after-init issue

set -e

echo "════════════════════════════════════════════════════════════"
echo "INSTALLING MODULES VIA ODOO API"
echo "Time: $(date)"
echo "════════════════════════════════════════════════════════════"

cd /opt/gemini_odoo19

# Wait for Odoo to be ready
echo ""
echo "Waiting for Odoo to be ready..."
for i in {1..30}; do
  if docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT 1;" &>/dev/null; then
    echo "✓ Database is responsive"
    break
  fi
  echo "  Attempt $i/30..."
  sleep 2
done

sleep 5

# Install modules via Python script
echo ""
echo "Installing modules..."

docker exec -i gemini_odoo19 python3 << 'PYTHON_SCRIPT'
import xmlrpc.client
import sys
import time

try:
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common', allow_none=True)
    models = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object', allow_none=True)
    
    # Login
    uid = common.authenticate('mz-db', 'admin', 'admin', {})
    if not uid:
        print("ERROR: Authentication failed")
        sys.exit(1)
    
    print(f"✓ Authenticated as user {uid}")
    
    # List of modules to install
    modules_to_install = [
        'sale_management',
        'purchase',
        'stock',
        'account',
        'ops_matrix_core',
        'ops_matrix_accounting',
        'ops_matrix_reporting',
        'ops_matrix_asset_management'
    ]
    
    # Install each module
    for module in modules_to_install:
        print(f"\n  Installing {module}...")
        try:
            # Get module
            module_id = models.execute_kw('mz-db', uid, 'admin', 
                'ir.module.module', 'search', 
                [['name', '=', module]])
            
            if module_id:
                # Click install
                models.execute_kw('mz-db', uid, 'admin',
                    'ir.module.module', 'button_immediate_install',
                    module_id)
                print(f"  ✓ {module} installed")
                time.sleep(2)
            else:
                print(f"  ✗ {module} not found")
        except Exception as e:
            print(f"  ✗ Error installing {module}: {e}")
    
    print("\n✓ Module installation complete!")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Module installation completed at: $(date)"
echo "════════════════════════════════════════════════════════════"
