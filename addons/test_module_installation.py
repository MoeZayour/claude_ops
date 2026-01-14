#!/usr/bin/env python3
"""
Test installation of all OPS modules in sequence
Uses proper method for running Odoo instance
"""

import subprocess
import sys

def install_module(module_name, db_name='mz-db', container='gemini_odoo19'):
    """Attempt to install a module and return success/failure"""
    print(f"\n{'='*60}")
    print(f"INSTALLING: {module_name}")
    print(f"{'='*60}")
    
    # Use shell mode to install/upgrade module on running instance
    python_script = f"""
import sys
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-d', '{db_name}'])
with odoo.api.Environment.manage():
    with odoo.registry('{db_name}').cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {{}})
        
        # Find module
        module = env['ir.module.module'].search([('name', '=', '{module_name}')])
        
        if not module:
            print(f"ERROR: Module {module_name} not found in module list")
            sys.exit(1)
        
        # Check current state
        print(f"Module state: {{module.state}}")
        
        if module.state == 'installed':
            print(f"Module {module_name} is already installed, upgrading...")
            module.button_immediate_upgrade()
        elif module.state in ['uninstalled', 'to install']:
            print(f"Installing module {module_name}...")
            module.button_immediate_install()
        else:
            print(f"Module in state: {{module.state}}, attempting install...")
            module.button_immediate_install()
        
        cr.commit()
        print(f"SUCCESS: Module {module_name} processed successfully")
"""
    
    cmd = [
        'docker', 'exec', container,
        'python3', '-c', python_script
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        # Check output
        output = result.stdout + result.stderr
        
        if result.returncode == 0 and 'SUCCESS:' in output:
            print(f"✅ SUCCESS: {module_name}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED: {module_name}")
            print(f"Return code: {result.returncode}")
            print("\nOutput:")
            print(output[:3000])
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {module_name} installation timed out")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Main installation test"""
    print("="*60)
    print("OPS MODULES INSTALLATION TEST")
    print("="*60)
    
    modules = [
        ('ops_matrix_core', 'Core module (should already be installed)'),
        ('ops_matrix_reporting', 'Reporting module'),
        ('ops_matrix_accounting', 'Accounting module'),
        ('ops_matrix_asset_management', 'Asset Management module'),
    ]
    
    results = {}
    
    for module_name, description in modules:
        print(f"\n{description}")
        success = install_module(module_name)
        results[module_name] = success
        
        # If a module fails, still continue to test others
        if not success:
            print(f"⚠️  Continuing with next module despite failure...")
    
    # Print summary
    print(f"\n{'='*60}")
    print("INSTALLATION SUMMARY")
    print(f"{'='*60}")
    
    for module_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {module_name}")
    
    # Overall result
    all_success = all(results.values())
    print(f"\n{'='*60}")
    if all_success:
        print("🎉 ALL MODULES INSTALLED SUCCESSFULLY!")
        print(f"{'='*60}")
        return 0
    else:
        failed = [m for m, s in results.items() if not s]
        print(f"⚠️  {len(failed)} MODULE(S) FAILED:")
        for module in failed:
            print(f"  - {module}")
        print(f"{'='*60}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
