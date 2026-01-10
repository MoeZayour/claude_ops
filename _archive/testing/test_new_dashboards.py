#!/usr/bin/env python3
"""
PRIORITY #14: DASHBOARDS - VERIFICATION TEST
============================================
Tests the NEW dashboard implementation.
"""

import xmlrpc.client

# Odoo connection settings
ODOO_URL = 'http://localhost:8089'
ODOO_DB = 'mz-db'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

def test_dashboards():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Checking models...")
    for model in ['ops.dashboard', 'ops.dashboard.widget']:
        res = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.model', 'search_count', [[['model', '=', model]]])
        print(f"Model {model}: {'EXISTS' if res else 'MISSING'}")

    print("\nChecking Dashboards...")
    dashboards = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ops.dashboard', 'search_read', [[]], {'fields': ['name']})
    print(f"Found {len(dashboards)} dashboards:")
    for d in dashboards:
        widgets = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ops.dashboard.widget', 'search_count', [[['dashboard_id', '=', d['id']]]])
        print(f" - {d['name']}: {widgets} widgets")

    print("\nChecking Total Widgets...")
    total_widgets = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ops.dashboard.widget', 'search_count', [[]])
    print(f"Total widgets: {total_widgets}")

    if total_widgets >= 17:
        print("\n✅ SUCCESS: Dashboard system is fully implemented with 17+ widgets.")
    else:
        print(f"\n❌ FAILURE: Only {total_widgets} widgets found.")

if __name__ == '__main__':
    try:
        test_dashboards()
    except Exception as e:
        print(f"Error: {e}")
