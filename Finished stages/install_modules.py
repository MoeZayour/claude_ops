#!/usr/bin/env python3
"""
Script to install OPS Matrix modules via XML-RPC
"""
import xmlrpc.client
import sys
import time

# Configuration
URL = "http://localhost:8089"
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"

# Modules to install in order
MODULES = [
    "ops_matrix_core",
    "ops_matrix_accounting", 
    "ops_matrix_reporting"
]

def connect():
    """Connect to Odoo and return common and models objects"""
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    
    # Authenticate
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print(f"❌ Authentication failed for user '{USERNAME}'")
        return None, None, None
    
    print(f"✓ Authenticated as user ID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return common, models, uid

def get_module_info(models, uid, module_name):
    """Get module information"""
    module_ids = models.execute_kw(DB, uid, PASSWORD,
        'ir.module.module', 'search',
        [[('name', '=', module_name)]])
    
    if not module_ids:
        return None
    
    module = models.execute_kw(DB, uid, PASSWORD,
        'ir.module.module', 'read',
        [module_ids], {'fields': ['name', 'state', 'latest_version']})
    
    return module[0] if module else None

def update_module_list(models, uid):
    """Update the modules list"""
    print("\n📋 Updating module list...")
    try:
        models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'update_list', [])
        print("✓ Module list updated")
        return True
    except Exception as e:
        print(f"❌ Failed to update module list: {e}")
        return False

def install_module(models, uid, module_name):
    """Install a single module"""
    print(f"\n{'='*60}")
    print(f"📦 Processing: {module_name}")
    print(f"{'='*60}")
    
    # Get module info
    module_info = get_module_info(models, uid, module_name)
    
    if not module_info:
        print(f"❌ Module '{module_name}' not found in module list")
        return False
    
    state = module_info['state']
    print(f"Current state: {state}")
    
    if state == 'installed':
        print(f"✓ Module already installed")
        return True
    
    if state == 'uninstalled' or state == 'to install':
        print(f"🔄 Installing module '{module_name}'...")
        try:
            # Trigger install
            models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'button_immediate_install',
                [[module_info['id']]])
            
            print(f"✓ Module '{module_name}' installation initiated")
            
            # Wait and check status
            time.sleep(2)
            for i in range(30):  # Wait up to 60 seconds
                module_info = get_module_info(models, uid, module_name)
                if module_info['state'] == 'installed':
                    print(f"✓ Module '{module_name}' successfully installed")
                    return True
                elif module_info['state'] == 'to install':
                    print(f"⏳ Waiting for installation to complete... ({i+1}/30)")
                    time.sleep(2)
                else:
                    print(f"⚠ Unexpected state: {module_info['state']}")
                    time.sleep(2)
            
            print(f"⚠ Installation timeout for '{module_name}'")
            return False
            
        except xmlrpc.client.Fault as e:
            print(f"❌ Installation failed with fault: {e.faultCode}")
            print(f"   {e.faultString}")
            return False
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    return False

def main():
    """Main installation process"""
    print(f"\n{'='*60}")
    print(f"OPS Matrix Modules Installation")
    print(f"{'='*60}")
    print(f"URL: {URL}")
    print(f"Database: {DB}")
    print(f"{'='*60}\n")
    
    # Connect
    common, models, uid = connect()
    if not uid:
        sys.exit(1)
    
    # Update module list
    if not update_module_list(models, uid):
        sys.exit(1)
    
    # Install modules in order
    results = {}
    for module_name in MODULES:
        success = install_module(models, uid, module_name)
        results[module_name] = "✓ INSTALLED" if success else "❌ FAILED"
        
        if not success:
            print(f"\n⚠ Installation stopped due to failure in '{module_name}'")
            break
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"INSTALLATION SUMMARY")
    print(f"{'='*60}")
    for module_name, status in results.items():
        print(f"{module_name:30} {status}")
    print(f"{'='*60}\n")
    
    # Exit with appropriate code
    if all("INSTALLED" in status for status in results.values()):
        print("✓ All modules installed successfully!")
        sys.exit(0)
    else:
        print("❌ Some modules failed to install")
        sys.exit(1)

if __name__ == "__main__":
    main()
