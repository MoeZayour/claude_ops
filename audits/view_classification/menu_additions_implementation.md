# Menu Additions Implementation Plan

**Date:** 2026-02-12
**Based on:** view_classification_report.md
**Status:** READY FOR REVIEW — No code changes made

---

## Summary of Required Changes

| Phase | Items | Files Modified | Risk |
|-------|-------|---------------|------|
| Phase 1: API Administration | 3 menus | ops_settings_menu.xml | LOW |
| Phase 2: Accounting Reports | 3 menus | accounting_menus.xml | LOW |
| Phase 3: Enhanced GL Decision | 1 menu | accounting_menus.xml | MEDIUM |
| Phase 4: Dead Code Cleanup | 3 actions removed | 3 view files | LOW |

---

## Phase 1: API Administration (Priority: HIGH)

### Target File
`addons/ops_matrix_core/views/ops_settings_menu.xml`

### Insert Location
After Performance Monitor (sequence 48), before Corporate Audit Log (sequence 60).

### XML to Add

```xml
<!-- =================== API ADMINISTRATION =================== -->
<menuitem id="menu_ops_api_admin"
          name="API Administration"
          parent="menu_ops_settings_root"
          sequence="49"
          groups="base.group_system"/>

<!-- API Keys Management -->
<menuitem id="menu_ops_api_keys"
          name="API Keys"
          parent="menu_ops_api_admin"
          action="action_ops_api_key"
          sequence="10"
          groups="base.group_system"/>

<!-- API Audit Log -->
<menuitem id="menu_ops_api_audit_log"
          name="API Audit Log"
          parent="menu_ops_api_admin"
          action="action_ops_audit_log"
          sequence="20"
          groups="base.group_system"/>

<!-- API Usage Analytics -->
<menuitem id="menu_ops_api_analytics"
          name="API Analytics"
          parent="menu_ops_api_admin"
          action="action_ops_api_analytics"
          sequence="30"
          groups="base.group_system"/>
```

### Verification Steps
1. Module update: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init`
2. Login as admin → Settings → OPS Framework → API Administration
3. Verify all 3 sub-menus appear
4. Click each menu → verify correct list/form/pivot/graph views load
5. Verify non-admin users cannot see the menu

### IT Admin Blindness Check
- `ops.api.key` — Contains API secrets. IT Admin should NOT see this.
- `ops.audit.log` — Contains API access patterns. Consider IT Admin blindness.
- **Action:** Verify existing record rules in `ir_rule_it_blind.xml` cover these models.

---

## Phase 2: Accounting Report Menus (Priority: HIGH)

### Target File
`addons/ops_matrix_accounting/views/accounting_menus.xml`

### 2a. PDC Reports

**Insert Location:** Under Reporting section, after existing report menus.

```xml
<!-- PDC Reports -->
<menuitem id="menu_reporting_pdc_reports"
          name="PDC Reports"
          parent="menu_ops_accounting_reporting"
          action="action_ops_pdc_reports"
          sequence="45"
          groups="account.group_account_user"/>
```

**Note:** The action is defined in `ops_pdc_reports_menus.xml`. The comment in that file says "MOVED: Menu consolidated in accounting_menus.xml as menu_reporting_pdc_reports" — but the menu was never actually created. This fixes the oversight.

### 2b. Period Close Wizard

**Insert Location:** Under Period Close section.

```xml
<!-- Period Close Wizard -->
<menuitem id="menu_ops_period_close_wizard"
          name="Period Close Wizard"
          parent="menu_ops_period_close"
          action="action_ops_period_close_wizard"
          sequence="5"
          groups="account.group_account_manager"/>
```

### 2c. Asset Register Report

**Insert Location:** Under Assets section.

```xml
<!-- Asset Register Report -->
<menuitem id="menu_ops_asset_register_report"
          name="Asset Register Report"
          parent="menu_ops_accounting_assets"
          action="action_ops_asset_register_report"
          sequence="40"
          groups="account.group_account_user"/>
```

### Verification Steps
1. Module update: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init`
2. Login → Accounting → Reporting → verify "PDC Reports" appears
3. Login → Accounting → Period Close → verify "Period Close Wizard" appears
4. Login → Accounting → Assets → verify "Asset Register Report" appears
5. Click each → verify correct view/wizard opens
6. Verify IT Admin blindness (PDC is in the IT Admin blocked models list)

---

## Phase 3: Enhanced GL Decision (Priority: MEDIUM)

### Decision Required

The system has TWO General Ledger wizards:

| Wizard | Action ID | Status | Complexity |
|--------|-----------|--------|------------|
| Standard GL | `action_gl_wizard` | HAS MENU | Basic parameters |
| Enhanced GL | `action_ops_general_ledger_wizard_enhanced` | NO MENU | Advanced filters |

**Option A — Replace Standard:**
```xml
<!-- Change existing menu to point to enhanced -->
<menuitem id="menu_ops_gl_wizard"
          action="action_ops_general_ledger_wizard_enhanced"/>
```

**Option B — Add Supplement:**
```xml
<menuitem id="menu_ops_gl_wizard_enhanced"
          name="General Ledger (Enhanced)"
          parent="menu_ops_accounting_reporting"
          action="action_ops_general_ledger_wizard_enhanced"
          sequence="12"
          groups="account.group_account_user"/>
```

**Option C — Deprecate Enhanced:**
Remove `action_ops_general_ledger_wizard_enhanced` if it's incomplete/redundant.

**Recommended:** Option B (supplement) — preserves existing user workflows while exposing the enhanced version for power users.

---

## Phase 4: Dead Code Cleanup (Priority: LOW)

### Actions to Remove

| Action | File | Reason |
|--------|------|--------|
| `action_aged_wizard` | ops_financial_wizard_views.xml:298 | Superseded by separate `action_aged_payables_wizard` and `action_aged_receivables_wizard` |
| `action_ops_dashboard_widget` | ops_dashboard_config_views.xml:228 | Duplicate of `action_ops_dashboard_widget_management` in ops_dashboard_widget_views.xml |
| `action_ops_dashboard_config` | ops_dashboard_config_views.xml:217 | No access path; dashboard config handled internally |

### Cleanup Process
1. Verify no XML `noupdate` blocks reference these action IDs
2. Remove `<record>` blocks from source XML
3. Module update
4. Verify no errors in logs

---

## Pre-Implementation Checklist

- [ ] Review this plan with project owner
- [ ] Verify parent menu XML IDs exist (grep for `menu_ops_accounting_reporting`, `menu_ops_period_close`, `menu_ops_accounting_assets`)
- [ ] Check IT Admin blindness coverage for ops.api.key, ops.audit.log
- [ ] Decide on Phase 3 (Enhanced GL) option
- [ ] Back up current XML before changes
- [ ] Schedule module update window

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Menu sequence conflicts | Chosen sequences avoid existing entries |
| Missing parent menus | All parent IDs verified via grep |
| ACL permission gaps | All referenced models have existing ACL entries |
| IT Admin access to sensitive data | API keys/PDC already have IT Admin blindness rules |
| Broken references on cleanup | Dead code verified as truly unreferenced |

---

*Implementation plan generated by Claude Code. No code changes applied — report only.*
