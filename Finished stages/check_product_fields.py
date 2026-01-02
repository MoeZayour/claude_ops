import xmlrpc.client

url = "http://localhost:8089"
db = "mz-db"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

fields_info = models.execute_kw(db, uid, password, 'product.template', 'fields_get', [])
print("Fields containing 'business' or 'unit' on product.template:")
for field_name, field_info in fields_info.items():
    if any(word in field_name.lower() for word in ['business', 'unit']):
        print(f"  - {field_name}: {field_info.get('string', 'No label')}")
