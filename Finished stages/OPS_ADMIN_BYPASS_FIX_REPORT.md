# OPS Admin Bypass - Critical Fix Applied
## Fix Report

**Date:** December 26, 2025  
**Issue:** Governance rules still applied to administrators after initial fix  
**Root Cause:** `ops.governance.mixin` was enforcing rules without admin bypass check

---

## 🔴 Problem Identified

After initial implementation, the admin bypass was not working because:

1. ✅ `ops_governance_rule.py` had bypass - **BUT** it was never called
2. ❌ `ops.governance.mixin` was directly enforcing rules without bypass check
3. ❌ The mixin's `create()`, `write()`, and `unlink()` methods called `_enforce_governance_rules()` without admin detection

### Call Flow (Before Fix):
```
sale.order.create()
  ↓
ops.governance.mixin.create()  ← Inherits from this
  ↓
_enforce_governance_rules()  ← NO ADMIN CHECK HERE!
  ↓
_apply_governance_rule()  ← Rules enforced for everyone
```

---

## ✅ Solution Applied

### Critical Fix #1: `ops_governance_mixin.py`

**Method:** `_enforce_governance_rules` (Line 140)

**Added admin bypass at the beginning:**

```python
def _enforce_governance_rules(self, records, trigger_type: str) -> None:
    """
    Find and enforce all active governance rules for this model and trigger type.
    """
    if not records:
        return

    # ADMIN BYPASS: Skip governance rule enforcement for Administrator and System Managers
    if self.env.su or self.env.user.has_group('base.group_system'):
        return  # ← CRITICAL FIX: Exit early for admins

    # Get the model name
    model_name = self._name
    # ... rest of enforcement logic
```

### Call Flow (After Fix):
```
sale.order.create()
  ↓
ops.governance.mixin.create()
  ↓
_enforce_governance_rules()
  ↓
Admin Check: if env.su or has_group('base.group_system')
  ↓
  YES → RETURN (skip all rules) ← Admin gets bypass
  ↓
  NO → Continue with rule enforcement ← Regular users still validated
```

### Critical Fix #2: `res_users_views.xml`

**Problem:** The user form view had `required="1"` attributes on matrix fields, enforcing UI-level validation that blocked administrators **before** the Python constraint could run.

**Fields Affected:**
- `persona_id` (Line 27) - Had `required="1"`
- `primary_branch_id` (Line 32) - Had `required="1"`
- `ops_allowed_business_unit_ids` (Line 69) - Had `required="1"`

**Solution:** Removed `required="1"` attributes from all three fields

**Result:**
- UI no longer enforces mandatory validation
- Python constraint in [`res_users.py:524`](addons/ops_matrix_core/models/res_users.py:524) now handles validation
- Admin bypass logic in Python constraint works correctly (already had `if user.has_group('base.group_system'): continue`)

**Updated Help Text:**
```xml
<!-- Before -->
help="User's organizational role (REQUIRED - Set this first...)"

<!-- After -->
help="User's organizational role (REQUIRED for non-admin users - Set this first...)"
```

---

## 📊 Complete Fix Summary

### All Admin Bypass Points:

| Location | Method | Line | Status |
|----------|--------|------|--------|
| `res_users.py` | `_check_user_matrix_requirements` | 524 | ✅ Existing |
| `res_users.py` | `get_effective_matrix_access` | 335 | ✅ Existing |
| `res_users.py` | `can_access_*` methods | 379+ | ✅ Existing |
| `ops_governance_rule.py` | `validate_record` | 188 | ✅ Added |
| `ops_governance_rule.py` | `evaluate_rules_for_record` | 787 | ✅ Added |
| **`ops_governance_mixin.py`** | **`_enforce_governance_rules`** | **144** | ✅ **FIXED** |
| **`res_users_views.xml`** | **`persona_id` field** | **24** | ✅ **FIXED** |
| **`res_users_views.xml`** | **`primary_branch_id` field** | **29** | ✅ **FIXED** |
| **`res_users_views.xml`** | **`ops_allowed_business_unit_ids` field** | **64** | ✅ **FIXED** |
| `ir_rule.xml` | Branch admin bypass rule | 36 | ✅ Added |

---

## 🚀 Deployment Instructions

### Step 1: Restart Odoo
```bash
docker restart gemini_odoo19
```

### Step 2: Wait for Container to Start (30 seconds)
```bash
sleep 30
```

### Step 3: Upgrade Module
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf \
    -d postgres -u ops_matrix_core --stop-after-init
```

### Step 4: Restart Again (to load new code)
```bash
docker restart gemini_odoo19
```

### Step 5: Clear Browser Cache
```
Press F12 → Application → Clear Storage → Clear site data
OR
Ctrl+Shift+Delete → Clear browsing data
```

---

## ✅ Testing Checklist

### Test as Administrator:

1. **Login as admin** (must have `base.group_system` group)

2. **Test Governance Rule Bypass:**
   - Navigate to: **Sales → Orders → Create**
   - Create an order with:
     - Any discount % (should not trigger discount rules)
     - Low margin products (should not trigger margin rules)
     - Any price variance (should not trigger price rules)
   - **Expected:** No governance errors, order saves successfully

3. **Test Matrix Validation Bypass:**
   - Try creating order without Branch/BU selection
   - **Expected:** No "Branch/BU Required" errors

4. **Test Configuration Access:**
   - Navigate to: **Settings → Accounting → Configuration**
   - **Expected:** Full access without persona/matrix assignment

### Test as Regular User:

1. **Create a test user** (NOT in `base.group_system`)

2. **Test Governance Rules Still Work:**
   - Login as test user
   - Create sale order with high discount
   - **Expected:** Should receive governance validation error

3. **Test Matrix Requirements Still Work:**
   - Try to save user without Branch/BU/Persona
   - **Expected:** Should receive validation error

---

## 🎯 Why This Fix Works

### 1. Early Exit Pattern
The bypass check is at the **very beginning** of `_enforce_governance_rules()`, before any rule search or evaluation.

### 2. Affects All Triggers
Since `create()`, `write()`, and `unlink()` all call `_enforce_governance_rules()`, the single bypass point covers all operations.

### 3. Preserved for Regular Users
The bypass is conditional - only admins skip validation. Regular users still go through all enforcement logic.

### 4. Multiple Detection Methods
Uses both `env.su` (superuser mode) and `has_group('base.group_system')` for maximum reliability.

---

## 📝 Files Modified in This Fix

1. ✅ `addons/ops_matrix_core/models/ops_governance_mixin.py` - **CRITICAL FIX #1** (Governance rule bypass)
2. ✅ `addons/ops_matrix_core/views/res_users_views.xml` - **CRITICAL FIX #2** (UI validation bypass)
3. ✅ `addons/ops_matrix_core/models/ops_governance_rule.py` - Previous fix
4. ✅ `addons/ops_matrix_core/security/ir_rule.xml` - Previous fix

---

## 🔍 Verification Commands

### Check if admin has correct group:
```sql
-- Connect to postgres
SELECT u.login, g.name 
FROM res_users u
JOIN res_groups_users_rel r ON r.uid = u.id
JOIN res_groups g ON g.id = r.gid
WHERE u.login = 'admin' AND g.full_name LIKE '%Administration / Settings%';
```

### Expected output:
```
login | name
------+---------
admin | Settings
```

### If not in group, add via UI:
```
Settings → Users & Companies → Users → admin
→ Access Rights tab → Check "Administration / Settings"
→ Save
```

---

## ⚠️ Important Notes

### 1. Module Must Be Upgraded
The Python code changes require a module upgrade, not just a restart:
```bash
# This is REQUIRED:
odoo -u ops_matrix_core

# This alone is NOT enough:
docker restart gemini_odoo19
```

### 2. Browser Cache Must Be Cleared
JavaScript and cached responses can interfere with testing

### 3. User Must Be in base.group_system
The bypass only works for users in the "Settings" group

### 4. Test Both Admin and Regular Users
Verify bypass works for admin AND enforcement still works for regular users

---

## 🎉 Expected Results

### Administrator Experience:
```
✅ Can create/modify any record without governance errors
✅ Can skip Branch/BU/Persona requirements
✅ Can access all configuration menus
✅ No "rule blocked" messages
✅ Full system access
```

### Regular User Experience:
```
❌ Still receives governance rule errors
❌ Still must assign Branch/BU/Persona
❌ Still has matrix-restricted access
❌ Governance rules still enforced
✅ System security maintained
```

---

## 📚 Related Documentation

- **Full Implementation:** [`OPS_ADMIN_BYPASS_COMPLETION_REPORT.md`](OPS_ADMIN_BYPASS_COMPLETION_REPORT.md)
- **Menu Fixes:** [`OPS_IDENTITY_MENU_RESTORATION_REPORT.md`](OPS_IDENTITY_MENU_RESTORATION_REPORT.md)
- **Cleanup Report:** [`OPS_GOVERNANCE_FINAL_CLEANUP_REPORT.md`](OPS_GOVERNANCE_FINAL_CLEANUP_REPORT.md)

---

## ✅ Status: FIXED

**Both critical fixes have been applied:**
1. ✅ `ops.governance.mixin` - Governance rule bypass at runtime
2. ✅ `res_users_views.xml` - UI validation bypass for admin user settings

Administrator bypass should now work correctly for:
- ✅ All governance rule enforcement (create/write/unlink operations)
- ✅ User form editing (can save without Branch/BU/Persona)

**Action Required:**
1. ✅ Restart Odoo container
2. ✅ Upgrade ops_matrix_core module
3. ✅ Clear browser cache
4. ✅ Test as administrator
5. ✅ Verify regular users still have validation

---

*Fix Applied: December 26, 2025*  
*Framework Version: 19.0.1.1*  
*Critical File: ops_governance_mixin.py:144*
