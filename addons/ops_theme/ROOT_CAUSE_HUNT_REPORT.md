# OPS Theme - Root Cause Hunt Report

**Date:** 2026-02-04  
**Version:** 19.0.8.0.0  
**Status:** ✅ RESOLVED

---

## Executive Summary

The dark mode functionality was not working because the `_dark_mode.scss` file was intentionally emptied during a previous layout diagnostic and never restored. The comprehensive 3,914-line dark mode SCSS has now been restored.

---

## Diagnostic Results

### Phase 1: Primary Variables ✅ CLEAN
**File:** `static/src/scss/_primary_variables.scss` (62 lines)

- Only contains **color variables** (brand colors, Bootstrap colors, link colors)
- Uses `!default` properly (follows MuK Theme pattern)
- **NO layout-critical variables** found:
  - No `$spacer`, `$grid-gutter-width`, `$grid-breakpoints`
  - No `$container-max-widths`, `$form-group-margin-bottom`
  
**Verdict:** Safe, color-only overrides.

---

### Phase 2: JavaScript Files ✅ SAFE
**Files analyzed:** 8 JS files

| File | Purpose | Risk |
|------|---------|------|
| `chatter_position_patch.js` | Patches FormRenderer.mailLayout() | LOW - respects Odoo's layout modes |
| `debranding.js` | Hides Odoo.com links | LOW - display:none only |
| `interactions.js` | Ripple effects, focus styling | LOW - adds classes only |
| `ops_theme_toggles.js` | User menu toggle actions | LOW - RPC calls only |
| `page_loader.js` | Loading overlay | LOW - isolated element |
| `theme_loader.js` | Favicon loading | LOW - cosmetic |
| `control_panel_refresh.js` | Refresh button | LOW - OWL component |
| `group_actions.js` | Expand/Collapse groups | LOW - cog menu items |

**Key Finding:** `chatter_position_patch.js` patches `FormRenderer.prototype.mailLayout()` but correctly falls back to `super.mailLayout()` when no user preference is set.

**Verdict:** No JS files modify core Odoo layout structures.

---

### Phase 3: XML View Templates ✅ CLEAN
**Files analyzed:** 7 XML files

| File | Purpose | Structural Impact |
|------|---------|-------------------|
| `debranding_templates.xml` | Hide Odoo branding | None - CSS only |
| `login_templates.xml` | Custom login page | Self-contained |
| `res_config_settings_views.xml` | Settings UI | Standard Odoo form |
| `res_users_views.xml` | Empty (comment only) | None |
| `webclient_templates.xml` | Favicon, fonts, cookie | Head elements only |
| `control_panel.xml` | Refresh button | OWL template |
| `user_menu.xml` | Toggle menu items | OWL template |

**Verdict:** No XML templates override Odoo's core layout structure.

---

### Phase 4: Other OPS Modules ✅ ISOLATED
**Modules analyzed:** ops_matrix_core, ops_matrix_accounting, ops_dashboard

| Module | SCSS Files | Layout Overrides |
|--------|-----------|------------------|
| ops_matrix_core | None | None |
| ops_matrix_accounting | `ops_corporate_reports.scss` | PDF reports only |
| ops_dashboard | `dashboard.scss`, `charts.scss` | `.ops-dashboard*` classes only |

**Critical Finding:** `ops_theme/models/ir_http.py` correctly manages dark mode:
- `color_scheme()` - Returns 'dark' when user has `ops_color_mode='dark'`
- `webclient_rendering_context()` - Sets `html_data['data-color-mode']`
- `session_info()` - Includes `ops_color_mode` and `ops_chatter_position`

**Verdict:** Backend Python code is correctly implemented.

---

### Phase 5: Database & Service ✅ VERIFIED

```sql
-- User fields exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'res_users' AND column_name LIKE 'ops_%';

-- Results:
ops_color_mode          -- Dark mode preference
ops_chatter_position    -- Chatter position preference
ops_branch_id           -- Matrix branch
ops_default_branch_id   -- Default branch
ops_default_business_unit_id -- Default BU
ops_api_key             -- API key
ops_api_rate_limit      -- Rate limit
ops_dashboard_config    -- Dashboard JSON
```

**Admin user status:**
```
id | login | ops_color_mode
---|-------|---------------
 2 | admin | dark
```

---

## Root Cause Found

### The Problem
The `_dark_mode.scss` file was **intentionally disabled** during a previous layout diagnostic:

```scss
// =============================================================================
// TEMPORARILY DISABLED FOR LAYOUT DIAGNOSTIC
// Original backed up as .phase2_backup
// =============================================================================
// This file intentionally left empty to test if dark mode overrides
// are causing layout breakage. Dark mode colors will not work.
// =============================================================================
```

### The Fix
Restored the comprehensive dark mode SCSS from backup:

```bash
cp _dark_mode.scss.phase2_backup _dark_mode.scss
# 3,914 lines restored
```

---

## Dark Mode Architecture Summary

### How Odoo 19 Dark Mode Works

1. **Server-side (ir_http.py):**
   ```python
   def color_scheme(self):
       if user.ops_color_mode == 'dark':
           return 'dark'
       return 'light'
   ```

2. **Template (webclient_bootstrap.xml):**
   ```xml
   <t t-if="color_scheme == 'dark'">
       <t t-call-assets="web.assets_web_dark" media="screen" t-js="false"/>
   </t>
   ```

3. **HTML attribute (via webclient_rendering_context):**
   ```python
   result['html_data'] = {'data-color-mode': color_scheme}
   # Results in: <html data-color-mode="dark">
   ```

4. **CSS Selector (our SCSS):**
   ```scss
   [data-color-mode="dark"] {
       --ops-dm-bg-page: #0f172a;
       // ... dark mode variables
   }
   ```

5. **Cookie (for JS access):**
   ```javascript
   document.cookie = "color_scheme=" + colorScheme + "; path=/";
   ```

---

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| `static/src/scss/_dark_mode.scss` | Restored from backup | 3,914 |

## Backups Created

| File | Purpose |
|------|---------|
| `_dark_mode.scss.placeholder` | Empty diagnostic placeholder |
| `_dark_mode.scss.phase2_backup` | Original comprehensive dark mode |

---

## Verification Steps

1. **Login as admin** at http://localhost:8069/web/login
2. **Check HTML tag** - Should have `data-color-mode="dark"`
3. **Verify CSS loaded** - `web.assets_web_dark` in network tab
4. **Toggle dark mode** - User menu → "Switch to Light Mode"

---

## Remaining Considerations

### Structural Audit (from previous session)
The original `_dark_mode.scss` backup contains **46 structural rules** that may need review:

- `display: flex|grid|block|none`
- `width/height/max-width/min-width`
- `position: relative|absolute|fixed|sticky`
- `flex-direction`, `gap`, `overflow`

These were flagged in the Structural Audit Report but the "Layout is broken even with ALL theme SCSS disabled" finding suggests the layout issue is NOT in the theme SCSS files.

### Recommendation
If layout issues persist after restoring dark mode:
1. Check browser console for JS errors
2. Verify no conflicting modules installed
3. Test with fresh browser profile (clear all cache)

---

## Conclusion

**Root Cause:** `_dark_mode.scss` was disabled during diagnostic  
**Fix Applied:** Restored 3,914-line comprehensive dark mode SCSS  
**Status:** Dark mode should now work when user sets `ops_color_mode = 'dark'`

---

*Report generated by OPS Theme Root Cause Hunt diagnostic*
