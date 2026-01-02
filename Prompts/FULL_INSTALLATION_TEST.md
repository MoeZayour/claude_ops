
# OPS Framework - Full Installation Validation Protocol

## Configuration
- **Database**: mz-db
- **Admin User**: admin
- **Admin Password**: admin
- **Max Retries Per Error**: 5
- **Odoo URL**: http://localhost:8069

## Objective
Perform complete installation and web-based validation of OPS Framework modules to catch ALL errors before user testing.

## CRITICAL: Use the SAME database the user will use
Database name: [mz-db]

---

## PHASE 1: Clean Environment Setup

```bash
# Stop any running Odoo instance
pkill -f odoo-bin || true
sleep 2

# Clear all Python cache
find /opt/gemini_odoo19 -name "*.pyc" -delete
find /opt/gemini_odoo19 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Clear Odoo asset cache (IMPORTANT!)
rm -rf /opt/gemini_odoo19/addons/web/static/lib/.cache 2>/dev/null || true
```

## PHASE 2: Syntax Validation (Before Installation)

```bash
# Validate all Python files
for module in ops_matrix_core ops_matrix_accounting ops_matrix_reporting; do
    echo "=== Checking $module ==="
    find /opt/gemini_odoo19/addons/$module -name "*.py" -exec python3 -m py_compile {} \;
    echo "Python syntax: OK"
done

# Validate all XML files
for module in ops_matrix_core ops_matrix_accounting ops_matrix_reporting; do
    find /opt/gemini_odoo19/addons/$module -name "*.xml" -exec xmllint --noout {} \;
    echo "XML syntax for $module: OK"
done
```

## PHASE 3: Database Installation (Full Mode)

```bash
cd /opt/gemini_odoo19

# Install modules with FULL logging (not --stop-after-init)
./odoo-bin -c odoo.conf -d mz-db \
    -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting \
    --log-level=info \
    --stop-after-init 2>&1 | tee /tmp/odoo_install.log

# Check for errors
echo "=== Checking for installation errors ==="
grep -i "error\|exception\|failed\|traceback" /tmp/odoo_install.log
```

## PHASE 4: Start Server and Test Web Access

```bash
# Start Odoo in background
cd /opt/gemini_odoo19
./odoo-bin -c odoo.conf -d mz-db --log-level=debug &
ODOO_PID=$!
sleep 10

# Test if server is responding
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login
echo " <- Should be 200"

# Test module assets load
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/assets/debug/web.assets_backend.js
echo " <- Should be 200"
```

## PHASE 5: Validate All Views via API

Create and run this Python script:

```python
#!/usr/bin/env python3
"""
OPS Framework View Validation Script
Tests all views render without errors
"""

import xmlrpc.client

# Configuration
URL = 'http://localhost:8069'
DB = 'mz-db'
USERNAME = 'admin'
PASSWORD = 'admin'  # Change if different

# Connect
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

print(f"Connected as UID: {uid}")

# Models to test
OPS_MODELS = [
    'ops.branch',
    'ops.business.unit', 
    'ops.governance.structure',
    'ops.asset',
    'ops.asset.category',
    'ops.budget',
    'ops.pdc',
]

errors = []

for model in OPS_MODELS:
    try:
        # Test search (validates model exists)
        result = models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [[]])
        print(f"✓ {model}: {result} records")
        
        # Test fields_get (validates field definitions)
        fields = models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], {'attributes': ['string', 'type']})
        print(f"  └─ {len(fields)} fields defined")
        
    except Exception as e:
        print(f"✗ {model}: ERROR - {e}")
        errors.append((model, str(e)))

print("\n" + "="*50)
if errors:
    print("VALIDATION FAILED - Errors found:")
    for model, error in errors:
        print(f"  - {model}: {error}")
else:
    print("ALL MODELS VALIDATED SUCCESSFULLY")
```

Save as `/tmp/validate_ops.py` and run:

```bash
python3 /tmp/validate_ops.py
```

## PHASE 6: Browser Simulation Test

```bash
# Test actual view rendering (catches XML view errors)
curl -s -X POST http://localhost:8069/web/dataset/call_kw \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.ui.view",
            "method": "search_read",
            "args": [[["model", "like", "ops.%"]]],
            "kwargs": {"fields": ["name", "model", "type"]}
        },
        "id": 1
    }' | python3 -m json.tool
```

## PHASE 7: Menu Access Test

```bash
# Verify all OPS menus are accessible
psql -d mz-db -c "
SELECT 
    m.name, 
    m.complete_name,
    CASE WHEN m.action IS NOT NULL THEN 'Has Action' ELSE 'No Action' END as status
FROM ir_ui_menu m
WHERE m.name ILIKE '%ops%' OR m.complete_name ILIKE '%ops%'
ORDER BY m.complete_name;
"
```

## PHASE 8: Security Access Verification

```bash
# Check all OPS models have access rules
psql -d mz-db -c "
SELECT 
    model_id.model,
    access.name,
    access.perm_read,
    access.perm_write,
    access.perm_create,
    access.perm_unlink
FROM ir_model_access access
JOIN ir_model model_id ON access.model_id = model_id.id
WHERE model_id.model LIKE 'ops.%'
ORDER BY model_id.model;
"
```

## PHASE 9: Final Web Validation Checklist

After all tests pass, manually verify OR use browser automation:

1. [ ] Login to http://localhost:8069
2. [ ] Navigate to each OPS menu item
3. [ ] Open list view for each model
4. [ ] Open form view (create new record)
5. [ ] Check all buttons render with proper icons/colors
6. [ ] Verify no JavaScript console errors (F12)

---

## Error Reporting Format

If ANY phase fails, report:

```
PHASE [X] FAILED
Error Type: [Python/XML/View/Security/Asset]
Error Message: [Full error text]
File: [Path to problematic file]
Line: [Line number if available]

Proposed Fix: [What needs to change]
```

---

## SUCCESS CRITERIA

All phases must pass:
- [ ] Phase 1: Clean environment
- [ ] Phase 2: Syntax validation
- [ ] Phase 3: CLI installation
- [ ] Phase 4: Web server responds
- [ ] Phase 5: All models accessible via API
- [ ] Phase 6: Views render correctly
- [ ] Phase 7: Menus accessible
- [ ] Phase 8: Security rules defined
- [ ] Phase 9: Manual/browser verification

Only report "Installation Successful" when ALL criteria pass.
```
