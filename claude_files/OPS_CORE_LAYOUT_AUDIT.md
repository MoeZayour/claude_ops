# OPS Core — Layout Purity Audit Report

**Audit Date:** 2026-02-05
**Auditor:** Claude Code (Layout Mode)
**Governing Rule:** Odoo 19 owns the layout. OPS owns the colors.
**Module:** ops_matrix_core

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| Total View XML Files | 50 | Audited |
| Total Wizard XML Files | 8 | Audited |
| CSS Files | 2 | Reviewed |
| **Critical Issues** | **0** | None |
| **Medium Issues** | **8** | Actionable |
| **Low Issues** | **340+** | Cleanup |

**Overall Assessment:** The module follows Odoo 19 patterns reasonably well. No hardcoded colors in XML views. Primary issues are **inline styles** (margin/font-size), **bare invisible fields**, **emojis**, and **missing name= attributes** on groups/pages.

---

## Audit Methodology

Every XML view file was checked against Odoo 19 native patterns:

### Form View Checklist
- [x] Proper header → sheet → oe_button_box → oe_title → group → notebook → chatter
- [x] Two-column layout: nested `<group><group>...<group>` pattern
- [~] Hidden fields wrapped in `<group invisible="1">` (PARTIAL - some bare fields)
- [x] One2many fields OUTSIDE `<group>` (in page or sheet)
- [ ] `name=` attribute on every `<group>`, `<page>` (320 groups, 19 pages missing)
- [x] No hardcoded colors
- [~] No inline CSS (PARTIAL - some style= attributes found)

### Wizard Checklist
- [x] NO `<sheet>` wrapper
- [x] Buttons in `<footer>` (not `<header>`)
- [x] Primary action uses `class="btn-primary"`
- [x] Cancel uses `special="cancel"`
- [x] Compact two-column layout

### General Checklist
- [x] No deprecated `attrs=` usage
- [~] No `<br/>` for spacing (some violations found)
- [x] No custom OPS CSS classes in views
- [~] All CSS files loaded in manifest (1 missing)

---

## FINDINGS

### Critical - Breaks Layout

**None found.** All views maintain proper structural hierarchy.

---

### Medium - Non-Standard but Functional

#### M1. Bare Invisible Fields at Form Root

**Files affected:**
- `wizard/ops_sale_order_import_wizard_views.xml:9-11`
- `wizard/ops_purchase_order_import_wizard_views.xml:8-10`
- `views/ops_security_compliance_views.xml:332, 389`

```xml
<!-- BEFORE (ops_sale_order_import_wizard_views.xml) -->
<form string="Import Sale Order Lines from Excel">
    <field name="state" invisible="1"/>
    <field name="template_file" invisible="1"/>
    <field name="template_filename" invisible="1"/>
```

```xml
<!-- AFTER -->
<form string="Import Sale Order Lines from Excel">
    <group invisible="1" name="hidden_fields">
        <field name="state"/>
        <field name="template_file"/>
        <field name="template_filename"/>
    </group>
```

---

#### M2. Inline Styles in Views

**Files affected:**

| File | Lines | Style |
|------|-------|-------|
| views/ops_persona_views.xml | 393 | `style="font-size: 0.9em;"` |
| wizard/ops_sale_order_import_wizard_views.xml | 38, 46, 57-60 | margin, font-size styles |
| wizard/ops_purchase_order_import_wizard_views.xml | 38 | `style="margin: 20px;"` |
| views/ops_dashboard_config_views.xml | 158 | Dynamic `t-att-style` (acceptable) |

**Recommendation:** Replace inline styles with Bootstrap utility classes:
- `font-size: 0.9em` → `class="small"`
- `margin: 20px` → `class="m-3"`
- `margin-left: 20px` → `class="ms-3"`
- `margin-top: 10px` → `class="mt-2"`

---

#### M3. Emojis in String Attributes

**Files affected:**

| File | Emojis Found |
|------|--------------|
| views/ops_sod_views.xml:139, 143 | ⚠️, ℹ️ |
| views/partner_views.xml:50, 56, 62 | ⚠️, ✅, ✓ |
| wizard/sale_order_import_wizard_views.xml:88 | ⚠️ |

**Recommendation:** Remove emojis from string attributes. Use Font Awesome icons via `<i class="fa fa-warning"/>` for visual indicators.

---

#### M4. CSS File Not in Manifest

**File:** `static/src/components/matrix_availability_tab/matrix_availability_tab.css`

**Status:** NOT loaded in manifest assets.

**Recommendation:** Either add to manifest or remove if unused.

---

### Low - Cleanup Opportunities

#### L1. Missing `name=` Attribute on Groups

**Count:** 320 unnamed groups across all view files.

Groups without `name=` cannot be targeted for xpath inheritance.

**Affected files (high count):**
| File | Unnamed Groups |
|------|----------------|
| ops_persona_views.xml | 28+ |
| ops_security_compliance_views.xml | 24+ |
| ops_branch_views.xml | 16+ |
| ops_business_unit_views.xml | 14+ |
| ops_governance_rule_views.xml | 12+ |
| (... all 50 view files affected) | |

---

#### L2. Missing `name=` Attribute on Pages

**Count:** 19 unnamed pages.

**Affected files:**
| File | Unnamed Pages |
|------|---------------|
| ops_persona_views.xml | 4 |
| ops_security_compliance_views.xml | 3 |
| ops_branch_views.xml | 2 |
| ops_governance_rule_views.xml | 2 |
| (... others) | |

---

#### L3. `<br/>` Tags for Spacing

**Files affected:**
- `views/res_users_views.xml:17`
- `views/partner_views.xml:50, 56`
- `views/ops_governance_rule_views.xml:89-97, 239-241`

**Assessment:** Mostly inside alert info blocks for readability. Low priority.

---

## CSS File Review

### ops_theme.css (in manifest)
- **Purpose:** Backend UI styling
- **Assessment:** CLEAN - Standard CSS classes
- **Layout Impact:** None

### matrix_availability_tab.css (NOT in manifest)
- **Purpose:** Component-specific styling
- **Assessment:** NOT LOADED - Either add to manifest or verify unused

---

## Remediation Priority

### Priority 1: Quick Wins (30 min)
1. ✅ Wrap bare invisible fields in groups (M1)
2. ✅ Remove emojis from string attributes (M3)
3. ✅ Remove inline styles, use Bootstrap classes (M2)

### Priority 2: Systematic Cleanup (2-3 hours)
1. ✅ Add `name=` attributes to all groups (L1)
2. ✅ Add `name=` attributes to all pages (L2)

### Priority 3: Optional
1. Verify/add matrix_availability_tab.css to manifest (M4)
2. Replace `<br/>` tags with structured markup (L3)

---

## Conclusion

The `ops_matrix_core` module demonstrates **good layout discipline**:

- **No hardcoded colors** in any XML file
- **Proper wizard structure** (footer buttons, no sheet wrapper)
- **Correct One2many placement** (outside groups, in pages)
- **No deprecated attrs= usage**

The identified issues are primarily **maintainability concerns** (missing `name=` attributes) and **minor style violations** (inline styles, emojis). The module successfully follows the governing rule: **Odoo 19 owns the layout, OPS owns the colors.**

---

**Report Generated:** 2026-02-05
**Next Audit:** After remediation

