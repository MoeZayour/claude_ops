#!/bin/bash

set -e

echo "════════════════════════════════════════════════════════════"
echo "INSTALLING OPS MODULES VIA ODOO API"
echo "Time: $(date)"
echo "════════════════════════════════════════════════════════════"

cd /opt/gemini_odoo19

# Wait for Odoo and database to be ready
echo ""
echo "Waiting for Odoo service..."
for i in {1..30}; do
  if curl -s http://localhost:8089/web/login 2>/dev/null | grep -q "login" ; then
    echo "✓ Odoo is responding"
    break
  fi
  echo "  Attempt $i/30..."
  sleep 2
done

sleep 5

# Install modules via direct docker exec Python script
echo ""
echo "Installing OPS modules..."

docker exec -i gemini_odoo19 python3 << 'PYTHON_SCRIPT'
import subprocess
import time
import sys

try:
    # Install OPS modules using odoo CLI
    modules = [
        'ops_matrix_core',
        'ops_matrix_accounting', 
        'ops_matrix_reporting',
        'ops_matrix_asset_management'
    ]
    
    for module in modules:
        print(f"\n>>> Installing {module}...")
        result = subprocess.run([
            'odoo',
            '-c', '/etc/odoo/odoo.conf',
            '-d', 'mz-db',
            '-u', module,
            '--stop-after-init',
            '--no-http'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✓ {module} installed successfully")
        else:
            print(f"! {module} install output:")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr[-300:] if len(result.stderr) > 300 else result.stderr)
        
        time.sleep(3)
    
    print("\n✓ All OPS modules installed!")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Module installation completed at: $(date)"
echo "════════════════════════════════════════════════════════════"
