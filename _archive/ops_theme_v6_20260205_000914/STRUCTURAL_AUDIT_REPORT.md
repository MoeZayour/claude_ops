# OPS THEME STRUCTURAL AUDIT REPORT

**Date:** 2026-02-04  
**Auditor:** Cline AI Senior Odoo Architect  
**Principle:** "OPS owns COLOR. Odoo 19 owns STRUCTURE."

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total SCSS Files | 27 |
| Files with Structural Rules | 19 (70%) |
| Files that are CLEAN | 8 (30%) |
| Total Structural Rule Count | ~310+ |
| Dark Mode Structural Rules | 46 |

---

## FILE-BY-FILE BREAKDOWN

### 🔴 CRITICAL (40+ rules) - REQUIRES MAJOR REWRITE

| File | Rules | Analysis |
|------|-------|----------|
| `_login.scss` | **61** | **WORST OFFENDER** - Complete login page layout override. Uses flex, absolute positioning, width/height throughout. Creates custom login UI that breaks Odoo 19 native login. |

### 🟠 HIGH (25-40 rules) - REQUIRES CLEANUP

| File | Rules | Analysis |
|------|-------|----------|
| `_form_controls.scss` | 38 | Custom checkbox/toggle sizing, absolute positioning for checkmarks. Some may be needed for custom styled controls. |
| `_utilities.scss` | 33 | **SAFE TO KEEP** - Utility classes (.ops-flex, .ops-grid, etc.) are intentional opt-in classes, not structural overrides. |
| `_debranding.scss` | 27 | **SAFE TO KEEP** - All `display: none !important` to hide Odoo branding elements. Intentional behavior. |
| `_kanban.scss` | 25 | Heavy structural overrides for kanban cards and columns (flex, grid, width/height, gap). |

### 🟡 MEDIUM (10-25 rules) - NEEDS REVIEW

| File | Rules | Analysis |
|------|-------|----------|
| `_control_panel.scss` | 17 | Control panel flex layouts, icon sizing, dropdown positioning. |
| `_wizard_sections.scss` | 17 | Grid layouts for wizard sections. May conflict with Odoo 19 wizard layouts. |
| `_user_menu.scss` | 16 | User dropdown menu flex layouts, avatar sizing, dropdown widths. |
| `_cards.scss` | 15 | Card layouts, icon sizing, flex displays. |
| `_tables.scss` | 14 | Table width, scrollbar sizing, row heights. |
| `_buttons_enhanced.scss` | 13 | Button gap, icon sizing, loading spinner positioning. |
| `_typography.scss` | 10 | Line-heights throughout - may cause layout shifts. |

### 🟢 LOW (1-10 rules) - MINOR CLEANUP

| File | Rules | Analysis |
|------|-------|----------|
| `_navbar.scss` | 7 | Navbar flex layouts, icon sizing. |
| `_badges_enhanced.scss` | 5 | Badge sizing and display properties. |
| `_appearance.scss` | 4 | Minor structural rules. |
| `_00_design_tokens.scss` | 3 | Contains some width/height values. |
| `_error_fields.scss` | 3 | Error field sizing. |
| `_list.scss` | 1 | **CLEANED IN PHASE 1** |
| `_modals.scss` | 1 | **CLEANED IN PHASE 1** |

### ✅ CLEAN FILES (No Structural Overrides)

| File | Status |
|------|--------|
| `_animations_minimal.scss` | ✅ CLEAN |
| `_chatter_fix.scss` | ✅ CLEAN |
| `_dark_mode.scss` | ✅ CLEAN (placeholder) |
| `_dashboard_kanban_fix.scss` | ✅ CLEAN |
| `_form_inputs_fix.scss` | ✅ CLEAN |
| `_primary_variables.scss` | ✅ CLEAN |
| `_settings_layout.scss` | ✅ CLEANED IN PHASE 1 |
| `_variables.scss` | ✅ CLEAN |

---

## DARK MODE FILE ANALYSIS

### Backup: `_dark_mode.scss.phase2_backup` (3,914 lines)

| Metric | Value |
|--------|-------|
| Total Lines | 3,914 |
| Structural Rules | 46 |
| `[data-color-mode="dark"]` Scopes | 56 |
| Rules Outside Scope | **POTENTIAL ISSUE** |

### Structural Rules Found (46 total):

Most are at lines 1030-2154 and 2978-3277, indicating:
1. **Lines 1030-1154**: Table/column width overrides
2. **Lines 1994-2078**: Chatter/form layout (flex, position, width)
3. **Lines 2089-2154**: More table width overrides
4. **Lines 2978-3277**: Kanban grid layout

### ⚠️ CONCERN: Many structural rules appear to be in "@media" queries or outside proper `[data-color-mode="dark"]` scoping, meaning they affect LIGHT mode too!

---

## CLASSIFICATION BY TYPE

### SAFE TO KEEP (Intentional Behavior)
- `_debranding.scss` - Hides Odoo branding (display: none)
- `_utilities.scss` - Utility classes are opt-in
- `_form_controls.scss` (partial) - Custom checkbox/toggle styling

### REMOVE/REFACTOR (Structural Overrides)
- `_login.scss` - **PRIORITY 1** - Full custom login layout
- `_kanban.scss` - Heavy grid/flex overrides
- `_control_panel.scss` - Layout overrides
- `_wizard_sections.scss` - Grid layouts
- `_user_menu.scss` - Dropdown layouts
- `_cards.scss` - Card layouts
- `_tables.scss` - Table layouts
- `_dark_mode.scss` (original) - Contains 46 structural rules

---

## RECOMMENDED REMEDIATION PLAN

### Phase 1: ✅ COMPLETED
- [x] Clean `_settings_layout.scss` (282 → 200 lines)
- [x] Clean `_modals.scss` (494 → 311 lines)
- [x] Clean `_list.scss` (420 → 282 lines)

### Phase 2: IN PROGRESS
- [x] Disable dark mode for testing
- [x] Full structural audit (THIS REPORT)

### Phase 3: DARK MODE RECONSTRUCTION
Priority order for cleaning:
1. **_login.scss** (61 rules) - Remove all structural, keep colors only
2. **_kanban.scss** (25 rules) - Remove grid/flex overrides
3. **_control_panel.scss** (17 rules) - Remove layout overrides
4. **_dark_mode.scss** (46 rules) - Strip structural, keep colors
5. **_cards.scss** (15 rules) - Remove layout overrides
6. **_tables.scss** (14 rules) - Remove width overrides

### Phase 4: VERIFICATION
- Re-enable dark mode
- Test light/dark toggle
- Verify no layout breakage

---

## STRUCTURAL KEYWORDS REFERENCE

### ❌ REMOVE (Structure)
```css
grid-template-columns, display:(grid|flex|block|none),
width, max-width, min-width, height, max-height, min-height,
flex-direction, flex-wrap, flex-basis, table-layout,
position:(absolute|fixed|relative), overflow, float, gap
```

### ✅ KEEP (Appearance)
```css
color, background-color, border-color, border-radius,
box-shadow, font-*, transition, cursor, accent-color,
opacity, text-shadow, outline-color, fill, stroke
```

---

## MANIFEST LOADING ORDER

```python
'web._assets_primary_variables': [
    'ops_theme/static/src/scss/_primary_variables.scss'  # ✅ CLEAN
]

'web.assets_frontend': [
    '_animations_minimal.scss'  # ✅ CLEAN
    '_login.scss'              # 🔴 61 structural rules
]

'web.assets_backend': [
    '_variables.scss'           # ✅ CLEAN
    '_00_design_tokens.scss'    # 🟢 3 rules
    '_typography.scss'          # 🟡 10 rules
    '_appearance.scss'          # 🟢 4 rules
    '_animations_minimal.scss'  # ✅ CLEAN
    '_form_controls.scss'       # 🟠 38 rules
    '_form_inputs_fix.scss'     # ✅ CLEAN
    '_cards.scss'               # 🟡 15 rules
    '_badges_enhanced.scss'     # 🟢 5 rules
    '_buttons_enhanced.scss'    # 🟡 13 rules
    '_tables.scss'              # 🟡 14 rules
    '_navbar.scss'              # 🟢 7 rules
    '_list.scss'                # 🟢 1 rule (cleaned)
    '_control_panel.scss'       # 🟡 17 rules
    '_kanban.scss'              # 🟠 25 rules
    ...and more
]
```

---

## NEXT STEPS

1. **Decision Point:** Should we proceed with Phase 3 (Clean dark mode file)?
2. **Alternative:** Replace `_login.scss` with color-only version first
3. **Testing:** After each cleanup, verify layout integrity in both light/dark modes

---

*Report generated by Cline AI - Phase 2 Structural Audit Complete*
