#!/usr/bin/env python3
"""Install OPS modules via Odoo JSON-RPC"""
import subprocess
import json
import time

def run_curl(method, params):
    """Execute a JSON-RPC call via curl"""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "call",
        "params": params,
        "id": 1
    })
    
    cmd = [
        'docker', 'exec', 'gemini_odoo19', 'bash', '-c',
        f"curl -s -X POST http://localhost:8089/jsonrpc -H 'Content-Type: application/json' -H 'X-Odoo-Database: mz-db' -d '{payload}'"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

print("="*70)
print("OPS MODULE INSTALLATION VIA JSON-RPC")
print("="*70)

# 1. Authenticate
print("\n[1] Authenticating...")
auth_response = run_curl('authenticate', {
    'service': 'common',
    'method': 'authenticate',
    'args': ['mz-db', 'admin', 'admin', {}]
})

if 'result' not in auth_response:
    print(f"✗ Authentication failed: {auth_response}")
    exit(1)

uid = auth_response['result']
print(f"    ✓ UID: {uid}")

# 2. Install modules
modules = [
    'ops_matrix_core',
    'ops_matrix_accounting',
    'ops_matrix_reporting',
    'ops_matrix_asset_management'
]

print(f"\n[2] Installing {len(modules)} modules...")
for module_name in modules:
    print(f"\n    Module: {module_name}")
    
    # Search for module
    search_response = run_curl('search', {
        'service': 'object',
        'method': 'execute_kw',
        'args': ['mz-db', uid, 'admin', 'ir.module.module', 'search', [[['name', '=', module_name]]]]
    })
    
    if 'result' not in search_response or not search_response['result']:
        print(f"      ✗ Module not found")
        continue
    
    module_id = search_response['result'][0]
    print(f"      Module ID: {module_id}")
    
    # Install module
    install_response = run_curl('install', {
        'service': 'object',
        'method': 'execute_kw',
        'args': ['mz-db', uid, 'admin', 'ir.module.module', 'button_immediate_install', [[module_id]]]
    })
    
    if 'error' in install_response:
        print(f"      ✗ Error: {install_response['error']}")
    else:
        print(f"      ✓ Installation triggered")
    
    time.sleep(2)

print("\n[3] Waiting for installation to complete...")
time.sleep(15)

# 3. Verify installations
print("\n[4] Verifying installations...")
verify_response = run_curl('verify', {
    'service': 'object',
    'method': 'execute_kw',
    'args': ['mz-db', uid, 'admin', 'ir.module.module', 'search_read', [[['name', 'in', modules]]], ['name', 'state']]
})

if 'result' in verify_response:
    print("\nModule States:")
    for mod in verify_response['result']:
        status = "✓" if mod['state'] == 'installed' else "✗"
        print(f"  {status} {mod['name']}: {mod['state']}")

print("\n" + "="*70)
print("Installation complete!")
print("="*70)
