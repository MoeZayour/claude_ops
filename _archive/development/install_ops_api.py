#!/usr/bin/env python3
"""Install OPS modules via Odoo XML-RPC API"""
import xmlrpc.client
import time
import sys

def install_modules():
    try:
        print("=" * 70)
        print("OPS MODULE INSTALLATION VIA API")
        print("=" * 70)
        
        # Connect to Odoo
        print("\n[1] Connecting to Odoo...")
        common = xmlrpc.client.ServerProxy('http://localhost:8089/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy('http://localhost:8089/xmlrpc/2/object')
        
        # Authenticate
        print("[2] Authenticating...")
        uid = common.authenticate('mz-db', 'admin', 'admin', {})
        print(f"    ✓ Authenticated (UID: {uid})")
        
        # Modules to install
        modules = [
            'ops_matrix_core',
            'ops_matrix_accounting',
            'ops_matrix_reporting',
            'ops_matrix_asset_management'
        ]
        
        # Install each module
        print(f"\n[3] Installing {len(modules)} modules...")
        for module_name in modules:
            print(f"\n    Processing: {module_name}")
            
            # Search for module
            domain = [('name', '=', module_name)]
            module_ids = models.execute_kw('mz-db', uid, 'admin', 
                'ir.module.module', 'search', [domain])
            
            if not module_ids:
                print(f"    ✗ Module not found in system")
                continue
            
            module_id = module_ids[0]
            
            # Get current state
            module_data = models.execute_kw('mz-db', uid, 'admin',
                'ir.module.module', 'read', [module_id], ['name', 'state'])
            
            state = module_data[0]['state']
            print(f"    Current state: {state}")
            
            if state == 'uninstalled':
                print(f"    Installing...")
                models.execute_kw('mz-db', uid, 'admin',
                    'ir.module.module', 'button_immediate_install', [module_id])
                print(f"    ✓ Installation triggered")
                time.sleep(3)
            else:
                print(f"    ✓ Already in state: {state}")
        
        print("\n" + "=" * 70)
        print("INSTALLATION COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    install_modules()
