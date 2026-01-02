#!/usr/bin/env python3
"""
Module Installation Script via XML-RPC
Installs required modules in the mz-db database
"""

import xmlrpc.client
import time

URL = "http://localhost:8089"
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"

def install_modules():
    print("🔗 Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return False
    
    print(f"✅ Connected as user ID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    def execute(model, method, *args):
        return models.execute_kw(DB, uid, PASSWORD, model, method, args, {})
    
    print("\n📦 Updating module list...")
    try:
        execute('ir.module.module', 'update_list')
        print("✅ Module list updated")
        time.sleep(3)
    except Exception as e:
        print(f"⚠ Update list error: {str(e)[:100]}")
    
    # Modules to install in order
    modules_to_install = [
        'sale_management',
        'purchase',
        'stock',
        'account',
        'ops_matrix_core',
        'ops_matrix_accounting',
        'ops_matrix_reporting',
    ]
    
    print("\n📦 Installing modules...")
    for module_name in modules_to_install:
        try:
            print(f"\n   → Searching for {module_name}...")
            module_ids = execute('ir.module.module', 'search', [('name', '=', module_name)])
            
            if not module_ids:
                print(f"   ⚠ Module {module_name} not found")
                continue
            
            module_data = execute('ir.module.module', 'read', [module_ids[0]], ['state', 'name'])
            state = module_data[0]['state']
            
            if state == 'installed':
                print(f"   ✅ {module_name} already installed")
            elif state in ('uninstalled', 'to install', 'to upgrade'):
                print(f"   → Installing {module_name}...")
                execute('ir.module.module', 'button_immediate_install', module_ids)
                print(f"   ✅ {module_name} installed!")
                time.sleep(5)  # Wait for installation
            else:
                print(f"   ⚠ {module_name} state: {state}")
                
        except Exception as e:
            print(f"   ❌ Error with {module_name}: {str(e)[:150]}")
    
    print("\n✅ Module installation complete!")
    return True

if __name__ == "__main__":
    install_modules()
