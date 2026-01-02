import xmlrpc.client
import sys
import time

# Connection details
URL = 'http://localhost:8089'
DB = 'mz-db'
USER = 'admin'
PASSWORD = 'admin'
MODULE_NAME = 'ops_matrix_core'

print("Waiting for Odoo to start...")
time.sleep(10)

try:
    # 1. Authenticate and get user ID
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASSWORD, {})

    if not uid:
        raise Exception("Authentication failed. Please check your credentials.")

    # 2. Connect to the 'object' endpoint
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    # 3. Search for the module ID
    module_ids = models.execute_kw(
        DB, uid, PASSWORD,
        'ir.module.module', 'search',
        [[['name', '=', MODULE_NAME]]]
    )

    if not module_ids:
        raise Exception(f"Module '{MODULE_NAME}' not found.")

    module_id = module_ids[0]

    # 4. Execute the immediate upgrade
    print(f"Attempting to upgrade module `{MODULE_NAME}`...")
    models.execute_kw(
        DB, uid, PASSWORD,
        'ir.module.module', 'button_immediate_upgrade',
        [[module_id]]
    )

    print(f"`{MODULE_NAME}` upgraded successfully")

except xmlrpc.client.Fault as e:
    print(f"An XML-RPC error occurred: {e.faultString}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)
