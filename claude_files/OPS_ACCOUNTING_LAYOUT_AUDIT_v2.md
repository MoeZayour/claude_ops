# OPS Accounting - Layout Purity Audit Report v2.0

**Audit Date:** 2026-02-05
**Auditor:** Claude Code (Layout Mode)
**Governing Rule:** Odoo 19 owns the layout. OPS owns the colors.
**Module:** ops_matrix_accounting v19.0.18.0.0

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| Total View XML Files | 27 | Audited |
| Total Wizard XML Files | 8 | Audited |
| CSS/SCSS Files | 3 | Reviewed |
| **Critical Issues** | **0** | None |
| **Medium Issues** | **4** | Actionable |
| **Low Issues** | **5** | Cleanup |

**Overall Assessment:** The module demonstrates **strong layout discipline**. No inline styles or hardcoded colors were found in view XML. The CSS files appropriately handle colors/styling without layout contamination. The primary issues are **missing `name=` attributes** on groups/pages (affecting xpath inheritance) and **minor deviations** from native Odoo patterns.

---

## Audit Methodology

Every XML view file was checked against Odoo 19 native patterns:

### Form View Checklist
- [x] `<header>` -> `<sheet>` -> `oe_button_box` -> `oe_title` -> `<group>` -> `<notebook>` -> `</sheet>` -> `<chatter/>`
- [x] Two-column layout: nested `<group><group>...<group>` pattern
- [x] Hidden fields wrapped in `<group invisible="1">`
- [x] One2many fields OUTSIDE `<group>` (in page or sheet)
- [ ] `name=` attribute on every `<group>`, `<page>` (PARTIAL - many missing)
- [x] Amount totals use `oe_subtotal_footer oe_right` pattern
- [x] No inline CSS (`style=`)
- [x] No hardcoded colors

### Wizard Checklist
- [x] NO `<sheet>` wrapper
- [x] Buttons in `<footer>` (not `<header>`)
- [x] Primary action uses `class="btn-primary"`
- [x] Cancel uses `special="cancel"`
- [x] Compact two-column layout

### General Checklist
- [x] No deprecated `attrs=` usage
- [ ] No `<br/>` for spacing (2 violations found)
- [ ] No custom CSS classes in views (uses `ops_wizard_section` etc.)
- [x] All CSS/SCSS files loaded in manifest

---

## FINDINGS

### Critical - Breaks Layout

**None found.** All views maintain proper structural hierarchy.

---

### Medium - Non-Standard but Functional

#### M1. Bare Invisible Fields at Form Root (ops_general_ledger_wizard_enhanced_views.xml)

**File:** [views/ops_general_ledger_wizard_enhanced_views.xml](views/ops_general_ledger_wizard_enhanced_views.xml#L24-L25)
**Lines:** 24-25

```xml
<!-- BEFORE -->
<form string="Matrix Financial Intelligence">
    <!-- Hidden computed/related fields -->
    <field name="currency_id" invisible="1"/>
    <field name="report_title" invisible="1"/>
    ...
```

**Issue:** Fields placed directly inside `<form>` without a group wrapper. Should be wrapped.

```xml
<!-- AFTER -->
<form string="Matrix Financial Intelligence">
    <group invisible="1" name="hidden_fields">
        <field name="currency_id"/>
        <field name="report_title"/>
    </group>
    ...
```

---

#### M2. Bare Invisible Fields in Period Close Wizard (wizard/ops_period_close_wizard_views.xml)

**File:** [wizard/ops_period_close_wizard_views.xml](wizard/ops_period_close_wizard_views.xml#L15-L17)
**Lines:** 15-17

```xml
<!-- BEFORE -->
<form string="Close Fiscal Period">
    <field name="state" invisible="1"/>
    <field name="checklist_count" invisible="1"/>
    <field name="checklist_progress" invisible="1"/>
```

```xml
<!-- AFTER -->
<form string="Close Fiscal Period">
    <group invisible="1" name="hidden_fields">
        <field name="state"/>
        <field name="checklist_count"/>
        <field name="checklist_progress"/>
    </group>
```

---

#### M3. Custom CSS Classes in Wizard Views

**Files:** Multiple wizard views use non-standard CSS classes:
- `ops_wizard_section` (groups)
- `ops_wizard_notebook` (notebook)

**Affected Files:**
- ops_inventory_report_views.xml (lines 18, 32, 40, 58, 83, 160)
- ops_balance_sheet_wizard_views.xml (lines 18, 25, 44, 62, 79)
- ops_treasury_report_wizard_views.xml (lines 18, 32, 49, 72, 96, 129)

**Assessment:** These classes are only referenced in views but **not defined** in the CSS files. They have no effect unless styling is added. Either:
1. Remove them (if unused)
2. Define them in CSS with styling (if needed)

**Recommendation:** Remove unused classes to keep views clean.

---

#### M4. Emojis in Section Headers (ops_inventory_report_views.xml)

**File:** [views/ops_inventory_report_views.xml](views/ops_inventory_report_views.xml)
**Lines:** 18, 32, 40, 58, 86, 113, 127, 160

```xml
<!-- Examples with emojis -->
<group name="template_section" string="📁 Quick Start" ...>
<group name="report_type_section" string="📊 Report Selection" ...>
<page string="📈 Aging Settings" ...>
```

**Issue:** Emojis in UI strings are non-standard for professional enterprise modules.

**Recommendation:** Remove emojis from string attributes. Use icons via `icon=` attribute on pages if visual differentiation is needed.

---

### Low - Cleanup Opportunities

#### L1. Missing `name=` Attribute on Groups

Groups without `name=` cannot be targeted for xpath inheritance. This affects extendability.

**Affected Files (partial list - most files have this issue):**
| File | Unnamed Groups Count |
|------|---------------------|
| ops_pdc_views.xml | 16+ |
| ops_asset_views.xml | 8+ |
| ops_budget_views.xml | 4+ |
| ops_lease_views.xml | 12+ |
| ops_recurring_views.xml | 16+ |
| ops_followup_views.xml | 14+ |
| ops_fiscal_period_views.xml | 10+ |

**Example Fix (ops_pdc_views.xml:58-66):**
```xml
<!-- BEFORE -->
<group>
    <group string="Check Information">
        ...
    </group>
    <group string="Dates">
        ...
    </group>
</group>

<!-- AFTER -->
<group name="check_details_outer">
    <group name="check_info" string="Check Information">
        ...
    </group>
    <group name="check_dates" string="Dates">
        ...
    </group>
</group>
```

---

#### L2. Missing `name=` Attribute on Pages

Pages without `name=` cannot be extended via xpath.

**Affected Files:**
| File | Unnamed Pages |
|------|---------------|
| ops_inventory_report_views.xml | 2 (lines 86, 113) |
| ops_trend_analysis_views.xml | 2 (lines 63, 90) |
| ops_recurring_views.xml | 6 (lines 64, 77, 175, 187, 275, 290) |
| ops_financial_report_config_views.xml | 4 (lines 33, 39, 51, 62) |

**Note:** Some files DO have proper `name=` on pages (good pattern).

---

#### L3. `<br/>` Tags for Spacing (ops_asset_category_views.xml)

**File:** [views/ops_asset_category_views.xml](views/ops_asset_category_views.xml#L61)
**Lines:** 61, 101

```xml
<!-- BEFORE -->
<div class="alert alert-info" role="alert" ...>
    <strong>...</strong>
    Each period: Book Value × <field .../>
    <br/>
    The depreciation amount decreases...
</div>
```

**Issue:** `<br/>` used for line breaks inside alert divs. While functional, native patterns prefer separate elements.

**Assessment:** Minor. These are inside informational alerts, not layout-critical areas.

---

#### L4. Alert Banners Inside Sheet (ops_asset_views.xml)

**File:** [views/ops_asset_views.xml](views/ops_asset_views.xml#L38-L48)
**Lines:** 38-48, 58-64

Standard Odoo pattern places alert banners BEFORE `<sheet>`, not inside it after the opening tag.

**Current Pattern:**
```xml
<sheet>
    <div class="alert alert-warning mb-3" ...>...</div>  <!-- Inside sheet -->
    <div class="oe_button_box" name="button_box">...
```

**Native Pattern:**
```xml
<!-- Banners before sheet -->
<div class="alert alert-warning mb-3" ...>...</div>
<sheet>
    <div class="oe_button_box" name="button_box">...
```

**Assessment:** Functional but non-standard. The current placement works but differs from native Odoo patterns.

---

#### L5. One2many Inside Group in Notebook Page

**File:** [views/ops_pdc_views.xml](views/ops_pdc_views.xml#L93-L100)
**Lines:** 93-100

```xml
<page string="Journal Entries" name="journal_entries" ...>
    <group>
        <group>
            <field name="deposit_move_id" readonly="1"/>
            <field name="clearance_move_id" readonly="1"/>
            <field name="bounce_move_id" .../>
        </group>
    </group>
</page>
```

**Issue:** Journal entry fields (Many2one, not One2many) wrapped in nested groups. This is acceptable for standard fields. The actual One2many fields in this module (like `line_ids`) ARE correctly placed outside groups.

**Assessment:** False positive - pattern is correct for Many2one fields.

---

## CSS/SCSS File Review

### ops_accounting.css (204 lines)
- **Purpose:** Backend UI styling (forms, lists, kanban)
- **Assessment:** CLEAN - Only defines color classes (`ops-accounting__badge--success`, etc.)
- **Layout Impact:** None - uses BEM architecture for styling only

### ops_report.css (1685 lines)
- **Purpose:** PDF report styling for wkhtmltopdf
- **Assessment:** ACCEPTABLE - Defines report-specific layout for printed PDF output
- **Layout Impact:** PDF reports only, not backend views

### ops_corporate_reports.scss (652 lines)
- **Purpose:** Corporate report styling with SCSS variables
- **Assessment:** CLEAN - Report templates only
- **Layout Impact:** PDF reports only, not backend views

**Verdict:** CSS files adhere to "Odoo owns layout, OPS owns colors" for backend views. Report CSS contains layout rules but these are for PDF generation, not backend view manipulation.

---

## File-by-File Summary

| File | Type | Forms | Lists | Xpaths | Issues |
|------|------|-------|-------|--------|--------|
| account_move_views.xml | Inherited | 0 | 0 | 10 | None |
| res_config_settings_views.xml | Inherited | 0 | 0 | 2 | None |
| ops_pdc_views.xml | Native | 2 | 2 | 0 | L1 (groups) |
| ops_asset_views.xml | Native | 1 | 1 | 0 | L1, L4 |
| ops_asset_category_views.xml | Native | 1 | 1 | 0 | L1, L3 |
| ops_budget_views.xml | Native | 1 | 1 | 0 | L1 |
| ops_recurring_views.xml | Native | 3 | 3 | 0 | L1, L2 |
| ops_lease_views.xml | Native | 1 | 1 | 0 | L1 |
| ops_followup_views.xml | Native | 3 | 2 | 0 | L1 |
| ops_fiscal_period_views.xml | Native | 1 | 3 | 0 | L1 |
| ops_general_ledger_wizard_enhanced_views.xml | Wizard | 1 | 0 | 0 | M1 |
| ops_inventory_report_views.xml | Wizard | 1 | 0 | 0 | M3, M4 |
| ops_balance_sheet_wizard_views.xml | Wizard | 1 | 0 | 0 | M3 |
| ops_treasury_report_wizard_views.xml | Wizard | 1 | 0 | 0 | M3 |
| ops_period_close_wizard_views.xml | Wizard | 1 | 0 | 0 | M2 |

---

## Remediation Priority

### Priority 1: Quick Wins (30 min)
1. Remove emojis from ops_inventory_report_views.xml (M4)
2. Wrap bare invisible fields in groups (M1, M2)

### Priority 2: Systematic Cleanup (2-3 hours)
1. Add `name=` attributes to all groups (L1)
2. Add `name=` attributes to all pages (L2)
3. Remove unused `ops_wizard_section` class references (M3)

### Priority 3: Optional Refinement
1. Move alert banners before `<sheet>` in ops_asset_views.xml (L4)
2. Replace `<br/>` with proper structure in alerts (L3)

---

## Conclusion

The `ops_matrix_accounting` module demonstrates **excellent layout discipline**:

- **No inline styles** in any XML file
- **No hardcoded colors** in any XML file
- **Proper wizard structure** (footer buttons, no sheet wrapper)
- **Correct One2many placement** (outside groups, in pages)
- **Clean CSS separation** (colors only, no layout overrides for backend)

The identified issues are primarily **maintainability concerns** (missing `name=` attributes) rather than layout violations. The module successfully follows the governing rule: **Odoo 19 owns the layout, OPS owns the colors.**

---

**Report Generated:** 2026-02-05
**Next Audit:** After remediation of Medium priority items
