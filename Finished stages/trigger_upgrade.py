#!/usr/bin/env python3
"""
Script to trigger module upgrade via Odoo RPC (JSON-RPC).
This allows us to upgrade the module through the running instance without touching DB directly.
"""
import requests
import json
import sys

# Configuration
ODOO_URL = 'http://localhost:8089'
DB_NAME = 'mz-db'
ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'admin'
MODULE_NAME = 'ops_matrix_core'

def call_rpc(method, params):
    """Call Odoo RPC endpoint."""
    payload = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': 1,
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            f'{ODOO_URL}/jsonrpc',
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            print(f"RPC Error: {result['error']}")
            return None
        return result.get('result')
    except Exception as e:
        print(f"RPC Call failed: {e}")
        return None

def authenticate():
    """Authenticate and get session."""
    # Try login
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'common',
            'method': 'authenticate',
            'args': [DB_NAME, ADMIN_LOGIN, ADMIN_PASSWORD, {}]
        },
        'id': 1,
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            f'{ODOO_URL}/jsonrpc',
            json=payload,
            headers=headers,
            timeout=30
        )
        result = response.json()
        if 'result' in result and result['result']:
            print(f"✓ Authenticated as user ID: {result['result']}")
            return True
        else:
            print(f"✗ Authentication failed: {result}")
            return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def upgrade_module():
    """Upgrade the module."""
    print(f"\nUpgrading module: {MODULE_NAME}")
    
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'object',
            'method': 'execute',
            'args': [
                DB_NAME,
                1,  # uid (admin is 1)
                'admin',  # password
                'ir.module.module',
                'button_upgrade',
                [
                    # Find the module and upgrade it
                    ('name', '=', MODULE_NAME)
                ]
            ]
        },
        'id': 1,
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            f'{ODOO_URL}/jsonrpc',
            json=payload,
            headers=headers,
            timeout=120
        )
        result = response.json()
        if 'result' in result:
            print(f"✓ Module upgrade initiated")
            return True
        else:
            print(f"✗ Upgrade failed: {result}")
            return False
    except Exception as e:
        print(f"Upgrade error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("OPS Matrix Core Module Upgrade Trigger")
    print("=" * 60)
    
    print(f"\nTarget: {ODOO_URL}")
    print(f"Database: {DB_NAME}")
    print(f"Module: {MODULE_NAME}")
    
    if authenticate():
        if upgrade_module():
            print("\n" + "=" * 60)
            print("✓ Upgrade completed successfully!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n✗ Upgrade failed")
            sys.exit(1)
    else:
        print("\n✗ Could not authenticate")
        sys.exit(1)
