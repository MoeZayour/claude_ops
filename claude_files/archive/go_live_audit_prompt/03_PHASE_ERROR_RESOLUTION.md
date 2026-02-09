# Phase 2: Error Resolution

**Duration:** 90 minutes (may vary based on errors)  
**Objective:** Identify and fix ALL errors in OPS Framework source code

---

## ERROR RESOLUTION PRINCIPLES

1. **Read the FULL error message** - Don't guess
2. **Fix in SOURCE CODE only** - No database hacks
3. **Test after each fix** - Don't batch fixes blindly
4. **Document every fix** - Future reference
5. **Commit major fixes individually** - Clean git history

---

## Task 2.1: Comprehensive Log Analysis

```bash
echo "========================================"
echo "PHASE 2: ERROR RESOLUTION"
echo "========================================"

echo "=== Collecting all Odoo logs ==="
docker logs gemini_odoo19 --tail 1000 > /tmp/odoo_full_log.txt 2>&1

echo "=== Filtering ERROR messages ==="
grep -n "ERROR" /tmp/odoo_full_log.txt > /tmp/errors_only.txt
cat /tmp/errors_only.txt

echo "=== Filtering Traceback messages ==="
grep -n -A 20 "Traceback" /tmp/odoo_full_log.txt > /tmp/tracebacks.txt
cat /tmp/tracebacks.txt

echo "=== Filtering Warning messages ==="
grep -n "WARNING" /tmp/odoo_full_log.txt | head -50

echo "✅ Log analysis complete"
```

---

## Task 2.2: Categorize Errors

Categorize each error into:

| Category | Priority | Example |
|----------|----------|---------|
| **Import Error** | CRITICAL | Missing module, wrong import path |
| **Syntax Error** | CRITICAL | Python syntax issues |
| **Field Error** | HIGH | Missing field, wrong field type |
| **View Error** | HIGH | Invalid XML, missing field in view |
| **Constraint Error** | MEDIUM | SQL constraint violation |
| **Data Error** | MEDIUM | Invalid data file reference |
| **Warning** | LOW | Deprecation, best practice |

---

## Task 2.3: Error Fix Template

For EACH error found, follow this process:

### Error Analysis Template

```markdown
## Error #[N]

**Error Message:**
```
[Full error message]
```

**Category:** [Import/Syntax/Field/View/Constraint/Data/Warning]
**Priority:** [CRITICAL/HIGH/MEDIUM/LOW]
**File:** [Full path to file]
**Line:** [Line number if applicable]

**Root Cause Analysis:**
[Why this error occurs]

**Fix Applied:**
[Exact code change made]

**Before:**
```python
[Original code]
```

**After:**
```python
[Fixed code]
```

**Verification:**
- [ ] Module reinstalls without this error
- [ ] No new errors introduced
- [ ] Feature works as expected
```

---

## Task 2.4: Common Error Fixes

### Import Errors

```bash
# Find missing imports
grep -rn "from odoo import" /opt/gemini_odoo19/addons/ops_*/models/
grep -rn "from odoo.exceptions import" /opt/gemini_odoo19/addons/ops_*/

# Fix pattern:
# Add missing import at top of file
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, UserError
```

### Field Definition Errors

```bash
# Find field definitions
grep -rn "fields\." /opt/gemini_odoo19/addons/ops_*/models/ | head -50

# Common fixes:
# - Add missing 'string' parameter
# - Fix comodel_name spelling
# - Add missing inverse_name for One2many
```

### View XML Errors

```bash
# Validate XML syntax
for f in /opt/gemini_odoo19/addons/ops_*/views/*.xml; do
  echo "Checking: $f"
  python3 -c "import xml.etree.ElementTree as ET; ET.parse('$f')" 2>&1 || echo "INVALID XML: $f"
done

# Common fixes:
# - Close unclosed tags
# - Fix field names that don't exist
# - Fix inherit_id references
```

### Security File Errors

```bash
# Check CSV syntax
for f in /opt/gemini_odoo19/addons/ops_*/security/ir.model.access.csv; do
  echo "Checking: $f"
  head -5 "$f"
  wc -l "$f"
done

# Common fixes:
# - Ensure header row exists
# - Fix model_id references (model_module_modelname)
# - Fix group_id references
```

### Manifest Errors

```bash
# Check manifest syntax
for f in /opt/gemini_odoo19/addons/ops_*/__manifest__.py; do
  echo "Checking: $f"
  python3 -c "exec(open('$f').read())" 2>&1 || echo "INVALID: $f"
done

# Common fixes:
# - Fix file paths in 'data' list
# - Fix dependency names
# - Remove non-existent files
```

---

## Task 2.5: Fix and Retest Loop

```bash
# After each fix:

echo "=== Attempting module update ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_theme,ops_dashboard --stop-after-init 2>&1 | tee /tmp/update_test.log

echo "=== Checking for remaining errors ==="
grep -E "(ERROR|Traceback)" /tmp/update_test.log

echo "=== Restarting container ==="
docker restart gemini_odoo19
sleep 10

echo "=== Verifying Odoo responds ==="
docker logs gemini_odoo19 --tail 30
```

---

## Task 2.6: Refactoring Check

Check for code that needs refactoring:

```bash
echo "=== Checking for deprecated patterns ==="

# Check for sudo() usage (should be documented)
grep -rn "\.sudo()" /opt/gemini_odoo19/addons/ops_*/models/ | head -20

# Check for direct SQL (should be avoided)
grep -rn "self\.env\.cr\.execute" /opt/gemini_odoo19/addons/ops_*/models/ | head -20

# Check for hardcoded values (should be configurable)
grep -rn "hardcode\|TODO\|FIXME\|XXX" /opt/gemini_odoo19/addons/ops_*/ | head -20

# Check for proper tracking
grep -rn "tracking=True" /opt/gemini_odoo19/addons/ops_*/models/ | wc -l

echo "✅ Refactoring check complete"
```

---

## Task 2.7: Template Deactivation Verification

Ensure templates are set up for user cloning:

```bash
echo "=== Checking SLA Templates ==="
grep -rn "active.*=.*True" /opt/gemini_odoo19/addons/ops_*/data/*sla*.xml
grep -rn "enabled.*=.*False" /opt/gemini_odoo19/addons/ops_*/data/*sla*.xml

echo "=== Checking Governance Rule Templates ==="
grep -rn "active" /opt/gemini_odoo19/addons/ops_*/data/*governance*.xml

echo "=== Checking Persona Templates ==="
grep -rn "active" /opt/gemini_odoo19/addons/ops_*/data/*persona*.xml

echo "✅ Template configuration verified"
```

**Expected Pattern:**
- `active = True` (visible in UI for cloning)
- `enabled = False` or similar (not auto-applied)

---

## Task 2.8: Generate Error Fix Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/02_ERROR_FIX_REPORT.md`:

```markdown
# Error Fix Report

**Date:** [DATE]
**Executor:** Claude Code
**Total Errors Found:** [X]
**Total Errors Fixed:** [X]
**Errors Deferred:** [X]

## Error Summary

| # | Category | File | Line | Status | Commit |
|---|----------|------|------|--------|--------|
| 1 | Import | models/x.py | 15 | FIXED | abc123 |
| 2 | View | views/x.xml | 42 | FIXED | abc123 |
| ... | ... | ... | ... | ... | ... |

## Detailed Fixes

### Fix #1: [Description]
[Full details using template from Task 2.3]

### Fix #2: [Description]
[Full details]

...

## Refactoring Notes

| Issue | Location | Recommendation | Priority |
|-------|----------|----------------|----------|
| sudo() usage | models/x.py:50 | Document reason | LOW |
| ... | ... | ... | ... |

## Template Configuration Status

| Template Type | File | active | enabled | Ready for Clone |
|---------------|------|--------|---------|-----------------|
| SLA Templates | sla_templates.xml | True | False | ✅ |
| Governance Rules | governance_rules.xml | True | False | ✅ |
| Personas | persona_templates.xml | False | N/A | ✅ |

## Verification

- [ ] All modules update without errors
- [ ] No Traceback in logs
- [ ] Odoo web interface loads
- [ ] All menus accessible
```

---

## Phase 2 Completion Checklist

- [ ] All ERROR messages resolved
- [ ] All Traceback issues fixed
- [ ] Modules update cleanly
- [ ] No new errors introduced
- [ ] Templates configured for cloning
- [ ] Error fix report created

---

## Git Commits (after major fixes)

```bash
cd /opt/gemini_odoo19
git add -A

git commit -m "[GO-LIVE] Phase 2: Error fixes applied

Fixed:
- [Error 1 description]
- [Error 2 description]
- [Error 3 description]

Files modified:
- [file1.py]
- [file2.xml]

Tested: Module update successful
Errors Fixed: [X]"

git push origin main
```

---

## PROCEED TO PHASE 3
