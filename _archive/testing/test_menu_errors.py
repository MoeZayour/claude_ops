#!/usr/bin/env python3
"""
Test all OPS Framework menus for errors
"""
import xmlrpc.client
import sys

# Configuration
url = 'http://localhost:8082'
db = 'mz-db'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Failed to authenticate")
    sys.exit(1)

print(f"Authenticated as UID: {uid}")

# Get all OPS-related menus
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Test key models
test_models = [
    'ops.asset.category',
    'ops.asset.depreciation',
    'ops.asset',
    'ops.asset.model',
    'ops.asset.register.report',
    'ops.asset.depreciation.wizard',
    'ops.asset.disposal.wizard',
    'ops.financial.report.wizard',
    'ops.general.ledger.wizard',
    'ops.governance.rule',
    'ops.persona',
    'ops.segregation.of.duties',
    'ops.sla.template',
    'ops.approval.request',
]

print("\n" + "="*60)
print("TESTING MENUS/MODELS")
print("="*60)

errors = []
for model in test_models:
    try:
        # Try to search records (lightweight test)
        result = models.execute_kw(db, uid, password, model, 'search_count', [[]])
        print(f"✅ {model}: OK ({result} records)")
    except Exception as e:
        error_msg = str(e)
        if 'Missing' in error_msg or 'does not exist' in error_msg or 'AccessError' in error_msg:
            print(f"❌ {model}: {error_msg[:100]}")
            errors.append((model, error_msg))
        else:
            print(f"⚠️  {model}: {error_msg[:80]}")
            errors.append((model, error_msg))

print("\n" + "="*60)
print("ERROR SUMMARY")
print("="*60)
if errors:
    for model, err in errors:
        print(f"\n{model}:")
        print(f"  {err[:200]}")
else:
    print("No errors found!")

print(f"\nTotal models tested: {len(test_models)}")
print(f"Models with errors: {len(errors)}")
