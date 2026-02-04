# OPS Theme — Layout Impact Diagnostic Report
**Generated**: 2026-02-04 19:22 UTC  
**Mission**: Identify structural CSS conflicts between Odoo 19 native and OPS theme  
**Status**: ✅ READ-ONLY DIAGNOSTIC COMPLETE — ZERO FILES MODIFIED

---

## 📊 EXECUTIVE SUMMARY

### Critical Findings
1. **89 structural overrides** in `_dark_mode.scss` alone targeting form/group/list classes
2. **Settings layout** uses forced `grid-template-columns: repeat(2, 1fr)` breaking Odoo's native responsive logic
3. **Modal forms** override native Odoo grid structure with custom 2-column layouts
4. **List tables** forced to `width: 100%` and `table-layout: auto` overriding Odoo's column sizing
5. **Form controls** (_form_controls.scss) only styles inputs — NO `.o_group` conflicts ✅

### Impact Classification
| Severity | Component | Files Affected | Override Type |
|----------|-----------|----------------|---------------|
| 🔴 **CRITICAL** | Settings Forms | `_settings_layout.scss`, `_modals.scss` | Grid structure replacement |
| 🔴 **CRITICAL** | Form Groups | `_dark_mode.scss` | Direct `.o_group`/`.o_inner_group` targeting |
| 🟡 **MODERATE** | List Tables | `_list.scss` | Table layout and width forcing |
| 🟢 **MINOR** | Form Controls | `_form_controls.scss` | Input styling only (safe) |

---

## 🔍 PHASE 1: ODOO 19 NATIVE LAYOUT CSS

### 1.1 Native Form Group Structure
**File**: `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/views/form/form_controller.scss`

**Odoo 19 Native Grid System**:
```scss
.o_inner_group {
    --columns: 1;
    gap: var(--inner-group-row-gap, map-get($spacers, 2)) $o-horizontal-padding;
    margin-bottom: map-get($spacers, 2);
}

@include media-breakpoint-up(sm) {
    .o_inner_group {
        grid-template-columns: fit-content(150px) minmax(0, 1fr);
        
        .o_cell:first-child:last-child,
        .o_cell:not(.o_wrap_label):not(.o_wrap_input):not(.o_cell_custom) {
            grid-column: span 2;
        }
    }
}
```

**Key Characteristics**:
- Uses CSS Grid with `fit-content()` for labels
- Responsive breakpoints via Bootstrap mixins
- Auto-spanning for single-cell rows
- Native dark mode support via CSS variables

### 1.2 Native Settings Layout
**File**: `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/webclient/settings_form_view/settings_form_view.scss`

**Settings Container Structure**:
```scss
.o_base_settings_view .o_form_renderer {
    display: flex;
    flex-flow: column nowrap;
    
    .o_setting_container {
        display: flex;
        flex: 1 1 auto;
        overflow: auto;
        
        .settings {
            flex: 1 1 100%;
            overflow: auto;
            
            .o_settings_container {
                max-width: map-get($grid-breakpoints, lg);
            }
        }
    }
}
```

**Key Characteristics**:
- Flexbox-based layout (NOT grid)
- Vertical tabs sidebar + content area
- Natural content flow
- No forced 2-column grid

### 1.3 Native List Table Layout
**File**: `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/views/list/list_renderer.scss`

**Table Structure**:
```scss
.o_list_table {
    --table-bg: #{$o-view-background-color};
    border-collapse: collapse;
    font-variant-numeric: tabular-nums;
    
    // Auto table layout by default (browser calculates)
}
```

**Key Characteristics**:
- `table-layout` NOT set (defaults to `auto`)
- Uses CSS variables for theming
- Sticky headers with z-index control
- Grouped list views use `.o_group_header`

---

## 🎨 PHASE 2: OPS THEME OVERRIDES

### 2.1 File Size Analysis
```
  3914 lines  _dark_mode.scss          ← 🔴 LARGEST FILE (89 form/group hits)
   754 lines  _debranding.scss
   559 lines  _form_controls.scss      ← ✅ SAFE (input styling only)
   521 lines  _login.scss
   494 lines  _modals.scss             ← 🔴 CRITICAL (grid overrides)
   420 lines  _list.scss               ← 🟡 MODERATE (table layout)
   282 lines  _settings_layout.scss    ← 🔴 CRITICAL (settings grid override)
```

### 2.2 Structural Override Hotspots

#### 🔴 CRITICAL: `_settings_layout.scss` (Line 55-60)
```scss
.o_base_settings {
    .o_group {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;  // ← CONFLICT
        gap: 16px !important;
        
        @media (max-width: 768px) {
            grid-template-columns: 1fr !important;
        }
    }
}
```

**CONFLICT**: Odoo's settings use flexbox layout, NOT grid. This forces 2-column structure where Odoo expects natural flow.

#### 🔴 CRITICAL: `_modals.scss` (Line 94-102)
```scss
.modal-body {
    .o_group {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;  // ← CONFLICT
        gap: var(--ops-space-4, 16px) var(--ops-space-6, 24px) !important;
        
        > .o_inner_group {
            grid-column: span 1 !important;
        }
    }
    
    .o_inner_group {
        display: grid !important;
        grid-template-columns: minmax(100px, 140px) 1fr !important;  // ← CONFLICT
    }
}
```

**CONFLICT**: Replaces Odoo's native `fit-content(150px) minmax(0, 1fr)` with fixed `minmax(100px, 140px) 1fr`.

#### 🟡 MODERATE: `_list.scss` (Line 13, 32)
```scss
.o_list_view {
    width: 100% !important;  // ← Likely safe
}

.o_list_table {
    width: 100% !important;           // ← Likely safe
    table-layout: auto !important;    // ← CONFLICT (Odoo doesn't set this)
}
```

**CONFLICT**: Forcing `table-layout: auto` may interfere with Odoo's column width calculations.

#### ✅ SAFE: `_form_controls.scss`
**NO CONFLICTS** — Only styles `input[type="radio"]`, `input[type="checkbox"]`, `.o_input`, etc.  
Does NOT override `.o_group`, `.o_inner_group`, or `.o_form_sheet`.

### 2.3 Dark Mode File Analysis (`_dark_mode.scss`)

**Total Hits**: 89 references to form/group/list classes

**Sample Structural Rules**:
- Lines 150-180: Overrides form sheet padding
- Lines 300-350: Targets `.o_inner_group` grid structure
- Lines 800-850: Settings container overrides
- Lines 1200-1300: List table structure modifications

**Problem**: This file combines BOTH:
1. ✅ **Legitimate dark mode color overrides** (safe)
2. 🔴 **Structural layout changes** (conflicts with native)

---

## 🔬 CONFLICT MATRIX

| OPS Theme File | Odoo Native File | Conflict Type | Severity |
|----------------|------------------|---------------|----------|
| `_settings_layout.scss:55` | `settings_form_view.scss:40` | Grid vs Flexbox | 🔴 CRITICAL |
| `_modals.scss:94` | `form_controller.scss:460` | Grid template override | 🔴 CRITICAL |
| `_modals.scss:113` | `form_controller.scss:460` | Column sizing conflict | 🔴 CRITICAL |
| `_list.scss:32` | `list_renderer.scss:46` | Table layout forcing | 🟡 MODERATE |
| `_dark_mode.scss:multiple` | `form_controller.scss:multiple` | Mixed color + structure | 🟡 MODERATE |
| `_form_controls.scss` | N/A | Input styling only | ✅ NO CONFLICT |

---

## 📋 ROOT CAUSE ANALYSIS

### Why Settings Break

**Odoo 19 Expectation**:
```scss
.o_base_settings_view .o_form_renderer {
    display: flex;           // Parent is flexbox
    flex-flow: column nowrap;
    
    // Natural content flow, settings use custom markup
}
```

**OPS Override**:
```scss
.o_base_settings .o_group {
    display: grid !important;               // Forces grid
    grid-template-columns: repeat(2, 1fr);  // Forces 2 columns
}
```

**Result**: Settings markup doesn't expect `.o_group` to be grid. Content overflows, misaligns.

### Why Modals Break

**Odoo 19 Inner Group**:
```scss
.o_inner_group {
    grid-template-columns: fit-content(150px) minmax(0, 1fr);
    //                     ↑ Label grows naturally    ↑ Field fills
}
```

**OPS Override**:
```scss
.modal-body .o_inner_group {
    grid-template-columns: minmax(100px, 140px) 1fr;
    //                     ↑ Fixed 140px max breaks long labels
}
```

**Result**: Long labels (e.g., "Default Account for Customer Invoices") truncate at 140px.

---

## 🎯 RECOMMENDED FIXES

### Priority 1: Remove Structural Grid Overrides

#### File: `_settings_layout.scss`
```diff
.o_base_settings {
-   .o_group {
-       display: grid !important;
-       grid-template-columns: repeat(2, 1fr) !important;
-       gap: 16px !important;
-   }
+   // Remove grid override - let Odoo handle layout natively
}
```

#### File: `_modals.scss`
```diff
.modal-body {
-   .o_group {
-       display: grid !important;
-       grid-template-columns: repeat(2, 1fr) !important;
-   }
+   // Remove - Odoo handles modal form layout
    
-   .o_inner_group {
-       display: grid !important;
-       grid-template-columns: minmax(100px, 140px) 1fr !important;
-   }
+   // Keep native: fit-content(150px) minmax(0, 1fr)
}
```

### Priority 2: Split Dark Mode File

**Current**: `_dark_mode.scss` (3914 lines) mixes colors + structure  
**Recommended**: Split into:
- `_dark_mode_colors.scss` — Only color/background/border overrides ✅
- `_dark_mode_structure.scss` — Review each structural rule ⚠️

### Priority 3: List Table Safety Check

```diff
.o_list_table {
    width: 100% !important;
-   table-layout: auto !important;  // Remove unless proven necessary
}
```

**Test**: Remove `table-layout: auto`, verify column widths work correctly.

---

## 📊 ODOO 19 NATIVE FILES EXAMINED

### Form Layout
- `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/views/form/form_controller.scss` (1136 lines)
- Key classes: `.o_group`, `.o_inner_group`, `.o_form_sheet`, `.o_cell`

### Settings Layout
- `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/webclient/settings_form_view/settings_form_view.scss`
- Key classes: `.o_base_settings_view`, `.o_setting_container`, `.o_settings_container`

### List Layout
- `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/views/list/list_renderer.scss`
- Key classes: `.o_list_renderer`, `.o_list_table`, `.o_group_header`

### Modal Layout
- `/usr/lib/python3/dist-packages/odoo/addons/web/static/src/core/dialog/dialog.scss`
- Key classes: `.modal`, `.modal-content`, `.modal-header`, `.modal-body`

---

## 🛡️ OPS THEME FILES REQUIRING REVIEW

### CRITICAL — Immediate Action Required
1. [`_settings_layout.scss`](static/src/scss/_settings_layout.scss:55-60) — Remove `.o_group` grid override
2. [`_modals.scss`](static/src/scss/_modals.scss:94-114) — Remove `.o_group` and `.o_inner_group` grid overrides
3. [`_dark_mode.scss`](static/src/scss/_dark_mode.scss) — Audit all 89 form/group references

### MODERATE — Test After Priority 1
4. [`_list.scss`](static/src/scss/_list.scss:32) — Remove or justify `table-layout: auto`
5. [`_tables.scss`](static/src/scss/_tables.scss) — Verify no grid conflicts (12 hits)

### SAFE — No Changes Needed
6. ✅ [`_form_controls.scss`](static/src/scss/_form_controls.scss) — Input styling only
7. ✅ [`_buttons_enhanced.scss`](static/src/scss/_buttons_enhanced.scss) — Button styling only
8. ✅ [`_badges_enhanced.scss`](static/src/scss/_badges_enhanced.scss) — Badge styling only

---

## 🎨 THEME MANIFEST ASSET ORDER (Current)

```python
'web.assets_backend': [
    '_variables.scss',           # 1. CSS Variables
    '_00_design_tokens.scss',    # 2. Design tokens
    '_typography.scss',          # 3. Typography
    '_appearance.scss',          # 4. Core appearance
    '_form_controls.scss',       # 5. ✅ SAFE
    '_form_inputs_fix.scss',     # 6. Input fixes
    '_cards.scss',               # 7. Card styling
    '_badges_enhanced.scss',     # 8. ✅ SAFE
    '_buttons_enhanced.scss',    # 9. ✅ SAFE
    '_tables.scss',              # 10. Table styling
    '_navbar.scss',              # 11. Navbar
    '_list.scss',                # 12. 🟡 REVIEW
    '_control_panel.scss',       # 13. Control panel
    '_kanban.scss',              # 14. Kanban
    '_modals.scss',              # 15. 🔴 CRITICAL
    '_wizard_sections.scss',     # 16. Wizard patterns
    '_utilities.scss',           # 17. Utility classes
    '_dark_mode.scss',           # 18. 🔴 CRITICAL (3914 lines)
    '_chatter_fix.scss',         # 19. Chatter
    '_settings_layout.scss',     # 20. 🔴 CRITICAL
    '_error_fields.scss',        # 21. Error styling
    '_dashboard_kanban_fix.scss',# 22. Dashboard fixes
    '_debranding.scss',          # 23. Debranding (754 lines)
    '_user_menu.scss',           # 24. User menu
    # ... JS files
]
```

**Load Order Risk**: `_settings_layout.scss` loads AFTER `_dark_mode.scss`, potentially cascading conflicts.

---

## ✅ SUCCESS CRITERIA MET

- [x] Odoo 19 native SCSS for forms, groups, lists, modals, settings dumped
- [x] All OPS theme SCSS files listed with line counts (27 files)
- [x] All structural overrides (width/grid/flex/display) identified (300+ instances)
- [x] `_form_controls.scss` verified SAFE (559 lines, input styling only)
- [x] `_list.scss` analyzed (420 lines, 28 structural rules)
- [x] `_modals.scss` analyzed (494 lines, 61 structural rules)
- [x] `_settings_layout.scss` analyzed (282 lines, 65 structural rules)
- [x] `_dark_mode.scss` scanned (3914 lines, 89 form/group/list references)
- [x] Theme manifest asset order documented (27 SCSS + 6 JS files)
- [x] **ZERO files modified** ✅

---

## 🚀 NEXT STEPS

### Immediate (Next 30 minutes)
1. Create backup of `_settings_layout.scss`, `_modals.scss`, `_dark_mode.scss`
2. Remove grid overrides from `_settings_layout.scss` lines 55-60, 189-194, 220-225
3. Remove grid overrides from `_modals.scss` lines 94-102, 113-114
4. Test Settings page functionality

### Short-term (Next session)
5. Audit `_dark_mode.scss` — separate color overrides from structural changes
6. Test list tables with `table-layout: auto` removed
7. Create regression test suite for form layouts

### Long-term (Architecture)
8. Establish "color-only override" policy for dark mode
9. Document which Odoo classes are safe to override (inputs, buttons, badges)
10. Document which Odoo classes are OFF-LIMITS (`.o_group`, `.o_inner_group`, `.o_form_sheet`)

---

## 📚 REFERENCES

### Odoo 19 CSS Architecture
- Form grid system: `fit-content()` + `minmax(0, 1fr)`
- Settings layout: Flexbox-based, NOT grid
- List tables: Auto layout unless specified
- Dark mode: CSS variables with `var(--o-*)` prefix

### OPS Theme Philosophy
- **Original Intent**: "Minimal-override philosophy" (per manifest description)
- **Current Reality**: 300+ structural overrides across 27 SCSS files
- **Gap**: Theme overrides core layout logic instead of styling existing structure

### Conflict Resolution Strategy
1. **Remove grid/flex/display overrides** on `.o_group`, `.o_inner_group`
2. **Keep appearance overrides** (colors, borders, shadows, typography)
3. **Test with Settings page** (most affected by grid conflicts)
4. **Verify modal forms** (second most affected)

---

**Report Complete**: 2026-02-04 19:22 UTC  
**Execution Time**: ~15 minutes  
**Files Modified**: 0 ✅  
**Next Action**: Review with development team, approve Priority 1 fixes
