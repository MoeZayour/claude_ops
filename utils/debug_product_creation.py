#!/usr/bin/env python3
"""Debug product creation"""

import xmlrpc.client

URL = "http://localhost:8089"
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def execute(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)

print("Testing product creation...")

# Try minimal product first
try:
    product_id = execute('product.product', 'create', {
        'name': 'Test Laptop',
        'type': 'product',
    })
    print(f"✅ Created product with minimal fields: ID {product_id}")
except Exception as e:
    print(f"❌ Error: {str(e)[:200]}")

# Try with more fields
try:
    product_id2 = execute('product.product', 'create', {
        'name': 'Test Mouse',
        'type': 'consu',
        'list_price': 25.0,
        'standard_price': 10.0,
    })
    print(f"✅ Created product with pricing: ID {product_id2}")
except Exception as e:
    print(f"❌ Error with pricing: {str(e)[:200]}")
