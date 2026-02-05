# OPS Dashboard — Layout Purity Audit Report

**Audit Date:** 2026-02-05
**Module:** ops_dashboard
**Auditor:** Claude Code (Opus 4.5)
**Governing Rule:** Odoo 19 owns the layout. OPS owns the colors.

---

## Executive Summary

The `ops_dashboard` module passed the layout purity audit with **24 medium-severity issues** identified and fixed. All issues were unnamed `<group>` elements in view XML files. No critical violations (inline styles, hardcoded colors, emojis) were found in view XML.

**Verdict:** COMPLIANT (after remediation)

---

## Inventory

| File Type | Count | Lines |
|-----------|-------|-------|
| View XML | 4 | 432 |
| Data XML | 2 | 1,968 |
| Security XML | 1 | 88 |
| OWL Template XML | 2 | 591 |
| SCSS | 2 | ~400 |
| JavaScript | 4 | - |
| **Total XML** | **9** | **3,079** |

---

## Scan Results

### Scan 1: Hardcoded Colors in View XML
**Result:** 0 violations

### Scan 2: Inline Styles in View XML
**Result:** 0 violations

(Note: OWL templates in `static/src/xml/` have 13 dynamic style bindings for dashboard visualization. This is acceptable for dashboard components that require runtime styling based on data.)

### Scan 3: Emojis
**Result:** 0 violations

### Scan 4: Unnamed Groups
**Result:** 24 violations (FIXED)

| File | Unnamed Groups |
|------|---------------|
| ops_dashboard_views.xml | 6 |
| ops_dashboard_widget_views.xml | 7 |
| ops_kpi_views.xml | 11 |
| **Total** | **24** |

### Scan 5: Unnamed Pages
**Result:** 0 violations

### Scan 6: CSS Hardcoded Colors
**Result:** ~30 instances in SCSS files

These are SCSS variable definitions and class-based color utilities, which is the correct approach. Colors are defined as variables (`$chart-primary`, etc.) and applied via CSS classes (`.color-green`, `.color-blue`, etc.).

**Assessment:** ACCEPTABLE - follows best practices for themeable dashboards.

### Scan 7: CSS Registration
**Result:** Both SCSS files registered in manifest

- `dashboard.scss` - Registered
- `charts.scss` - Registered

---

## Remediation Applied

### Fix 1: Add name= attributes to all groups (24 total)

**ops_dashboard_views.xml** (6 groups):
- Line 46: `<group name="main_info">`
- Line 47: `<group name="identification">`
- Line 53: `<group name="settings">`
- Line 77: `<group name="access_control">`
- Line 78: `<group name="target_personas">`
- Line 81: `<group name="access_groups">`

**ops_dashboard_widget_views.xml** (7 groups):
- Line 29: `<group name="main_info">`
- Line 30: `<group name="basic_info">`
- Line 37: `<group name="kpi_settings">`
- Line 43: `<group name="display_settings">`
- Line 44: `<group name="display">`
- Line 50: `<group name="position">`
- Line 57: `<group name="list_config">`

**ops_kpi_views.xml** (11 groups):
- Line 36: `<group name="main_info">`
- Line 37: `<group name="identification">`
- Line 43: `<group name="data_source">`
- Line 49: `<group name="filtering_display">`
- Line 50: `<group name="filtering">`
- Line 55: `<group name="display">`
- Line 61: `<group name="trend_security">`
- Line 62: `<group name="trend">`
- Line 66: `<group name="security">`
- Line 72: `<group name="target_personas">`
- Line 75: `<group name="description">`

---

## Verification

| Check | Status |
|-------|--------|
| XML validation (all 9 files) | PASS |
| Unnamed groups (re-scan) | 0 remaining |
| Module update | SUCCESS |
| Error logs | CLEAN |

---

## OWL Template Analysis

The `static/src/xml/` templates contain dynamic styles for dashboard components:

| File | Dynamic Styles | Purpose |
|------|---------------|---------|
| chart_templates.xml | 6 | KPI card colors, chart legends, progress bars |
| ops_dashboard_templates.xml | 4 | KPI cards, widget backgrounds |

**Assessment:** ACCEPTABLE

Dashboard components require runtime-computed colors based on KPI configuration (e.g., red/yellow/green status indicators, user-defined KPI colors). These use `t-att-style` bindings with data-driven values, which is the correct OWL pattern.

---

## SCSS Analysis

Both SCSS files follow best practices:

1. **Variable-based colors** - Colors defined as SCSS variables at file top
2. **Class-based application** - Colors applied via utility classes (`.color-green`, etc.)
3. **No inline styles in Python** - All styling via CSS classes
4. **Themeable structure** - Easy to override via CSS custom properties

**Recommendation:** Consider migrating to CSS custom properties (`--ops-chart-primary`) for runtime theming support. This is a future enhancement, not a compliance issue.

---

## Commit Details

**Commit:** `4d00e05`
**Message:** fix(dashboard): Layout purity remediation - Odoo 19 native compliance
**Files Changed:** 3
**Lines Changed:** 48 (24 insertions, 24 deletions)

---

## Conclusion

The `ops_dashboard` module is now **fully compliant** with the OPS Framework layout purity standard:

| Category | Status |
|----------|--------|
| View XML structure | COMPLIANT |
| Group naming | COMPLIANT |
| Page naming | COMPLIANT |
| Inline styles (views) | COMPLIANT |
| Emojis | COMPLIANT |
| CSS architecture | COMPLIANT |
| OWL templates | ACCEPTABLE (dashboard-specific) |

**Module Compliance Score:** 100%

---

*Report generated by Claude Code (Opus 4.5)*
*Audit methodology: OPS Framework Layout Purity Standard v1.0*
