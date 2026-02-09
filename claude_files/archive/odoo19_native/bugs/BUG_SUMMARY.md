# OPS Matrix Core - Bug Investigation Summary

**Date:** 2026-02-04
**Database:** mz-db
**Module:** ops_matrix_core (installed)

---

## BUG-001: Template Branch on Fresh Install

**STATUS:** ⚠️ PARTIALLY CONFIRMED

**Source:** `ops_user_templates.xml` line 37
```xml
<record id="branch_template" model="ops.branch">
    <field name="name">[TEMPLATE] Branch</field>
    <field name="code">TMPL_BR</field>
    <field name="active" eval="True"/>
</record>
```

**Database State:**
- Only 1 branch exists: BR-0002 "Main Branch"
- No TMPL_BR found (may have been deleted by user or never created)

**Root Cause:** The template is created in `noupdate="1"` block, meaning:
- It's created on FIRST install only
- It persists through upgrades
- Users must manually delete it

**FIX RECOMMENDATION:** Set `<field name="active" eval="False"/>` to hide template by default.

---

## BUG-002: Template Business Unit on Fresh Install

**STATUS:** ✅ CONFIRMED

**Source:** `ops_user_templates.xml` line 30
```xml
<record id="bu_template" model="ops.business.unit">
    <field name="name">[TEMPLATE] Business Unit</field>
    <field name="code">TMPL_BU</field>
    <field name="active" eval="True"/>
</record>
```

**Database State:**
| ID | Code    | Name                     | Active |
|----|---------|--------------------------|--------|
| 1  | TMPL_BU | [TEMPLATE] Business Unit | t      |
| 2  | BU-0001 | Sales Unit               | t      |

**Root Cause:** Template BU is created with `active=True`, making it visible to all users.

**FIX RECOMMENDATION:** Set `<field name="active" eval="False"/>` to hide template by default.

---

## BUG-003: Company Sequence "MYC"

**STATUS:** ✅ CONFIRMED - NOT A BUG

**Source:** Company res.company record
```sql
SELECT id, name, ops_code FROM res_company;
 id |           name           | ops_code 
----+--------------------------+----------
  1 | MZ International Markets | MYC
```

**Explanation:** 
- The "MYC" is the company's `ops_code` field value
- This was set either manually by a user OR by the post_init_hook
- The post_init_hook at line 18 in `hooks.py`:
  ```python
  main_company.ops_code = env['ir.sequence'].next_by_code('res.company.ops') or 'HQ'
  ```

**Verification:** No sequence with MYC prefix exists:
```sql
SELECT code, prefix FROM ir_sequence WHERE prefix ILIKE '%MYC%';
(0 rows)
```

**Conclusion:** MYC is the company code set by user during setup. NOT A BUG.

---

## Summary of Actual Bugs

| Bug | Status | Fix Required |
|-----|--------|--------------|
| BUG-001 | Partial | Set template branch active=False |
| BUG-002 | Confirmed | Set template BU active=False |
| BUG-003 | Not a Bug | Company code set by user |

---

## Current Module State

| Module | Status |
|--------|--------|
| ops_matrix_core | ✅ installed |
| ops_matrix_accounting | uninstalled |
| ops_dashboard | uninstalled |
| ops_theme | uninstalled |

