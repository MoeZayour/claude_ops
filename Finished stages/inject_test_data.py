import xmlrpc.client
import time
import sys

# ==========================================
# CONFIGURATION
# ==========================================
# URL updated to use localhost since port is mapped
URL = "http://localhost:8089" 
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"

def wait_for_odoo():
    """Wait for Odoo to be ready"""
    print(f"🔄 Connecting to {URL}...")
    for i in range(10):
        try:
            common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
            uid = common.authenticate(DB, USERNAME, PASSWORD, {})
            if uid:
                return common, uid
        except Exception as e:
            print(f"   Waiting... ({e})")
            time.sleep(3)
    raise Exception("❌ Could not connect to Odoo.")

try:
    # 1. AUTHENTICATE
    common, uid = wait_for_odoo()
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    print(f"✅ Connected to {DB} (User ID: {uid})")

    # 2. HELPER: CREATE OR GET
    def ensure_record(model, domain, data):
        ids = models.execute_kw(DB, uid, PASSWORD, model, 'search', [domain])
        if ids:
            print(f"   -> [EXISTS] {model}: {data.get('name')}")
            return ids[0]
        id = models.execute_kw(DB, uid, PASSWORD, model, 'create', [data])
        print(f"   -> [CREATED] {model}: {data.get('name')} (ID: {id})")
        return id

    print("\n--- 1. MATRIX STRUCTURE ---")
    b_a = ensure_record('ops.branch', [('code', '=', 'BRA')], {'name': 'Branch A', 'code': 'BRA'})
    u_1 = ensure_record('ops.business.unit', [('code', '=', 'BU1')], {'name': 'Unit 1', 'code': 'BU1'})
    u_2 = ensure_record('ops.business.unit', [('code', '=', 'BU2')], {'name': 'Unit 2', 'code': 'BU2'})

    print("\n--- 2. USER CONFIGURATION ---")
    # Check if custom fields exist before writing to avoid crashes
    user_fields = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'fields_get', [], {'attributes': ['string']})
    
    user_vals = {
        'name': 'Ricky Restricted',
        'login': 'restricted',
        'password': 'restricted'
    }

    # Only add matrix fields if they exist in the schema
    if 'ops_default_branch_id' in user_fields:
        user_vals.update({
            'ops_default_branch_id': b_a,
            'ops_allowed_branch_ids': [(6, 0, [b_a])],
            'ops_default_business_unit_id': u_1,
            'ops_allowed_business_unit_ids': [(6, 0, [u_1])]
        })
        print("   -> Matrix fields detected and applied.")
    else:
        print("   ⚠️ WARNING: Matrix fields (ops_*) not found on res.users. Skipping assignment.")

    # Create/Update User
    user_search = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'search', [[('login', '=', 'restricted')]])
    if user_search:
        models.execute_kw(DB, uid, PASSWORD, 'res.users', 'write', [user_search, user_vals])
        print("   -> [UPDATED] User 'restricted'")
    else:
        models.execute_kw(DB, uid, PASSWORD, 'res.users', 'create', [user_vals])
        print("   -> [CREATED] User 'restricted'")

    print("\n--- 3. PRODUCTS ---")
    # Global Product
    ensure_record('product.template', [('name', '=', 'Global Service')], 
        {'name': 'Global Service', 'type': 'service', 'list_price': 100.0})
    
    # Siloed Product (Assigned to BU2)
    ensure_record('product.template', [('name', '=', 'Siloed Product')], 
        {'name': 'Siloed Product', 'type': 'service', 'business_unit_id': u_2, 'list_price': 200.0})

    print("\n✅ INJECTION COMPLETE")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
