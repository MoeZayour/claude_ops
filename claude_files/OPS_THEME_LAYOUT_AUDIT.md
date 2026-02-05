# OPS Theme — Layout Contamination Audit Report

**Audit Date:** 2026-02-05
**Auditor:** Claude Code (Layout Mode)
**Governing Rule:** Odoo 19 owns the layout. OPS owns the colors.
**Module:** ops_theme v19.0.7.0.0

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| SCSS Files | 5 | Audited |
| JS Files | 4 | Audited |
| XML Templates | 4 | Audited |
| **Layout Contaminations** | **0** | CLEAN |
| **Debranding (Allowed)** | 3 | Expected |
| **Custom Login (Allowed)** | 1 | Expected |

**Overall Assessment:** **EXCELLENT.** The theme demonstrates **exemplary adherence** to the "Odoo 19 owns layout, OPS owns colors" philosophy. No layout contamination detected in backend views. All CSS/JS modifications are appropriately scoped to:
1. Bootstrap variable overrides (colors only)
2. Custom login page layout (OPS-owned page)
3. Debranding (hiding Odoo.com links)
4. Chatter position toggle (works WITH Odoo's native system)

---

## Theme Architecture

### Manifest Philosophy (Stated in `__manifest__.py`)

```
"Color + Enhance, Never Fight OWL"

What This Theme Does (6 Things):
1. Debranding - Replace Odoo purple with OPS Navy at Bootstrap compile time
2. Login Screen - Split-screen branded login page
3. Dark/Light Mode - Toggle using native Odoo data-color-mode
4. Chatter Position - Toggle between side/bottom via user preference
5. Clean UI - Remove odoo.com links and branding
6. User Preferences - Save theme settings per user

What This Theme Does NOT Do:
- Override form view layouts (rides Odoo native)
- Rewrite list view renderers (rides Odoo native)
- Modify wizard/modal structure (rides Odoo native)
- Fight OWL component rendering (uses Odoo's dark mode)
- Inject CSS that breaks two-column forms (minimal overrides only)
```

**Verdict:** The theme's stated philosophy is **fully implemented** in the code.

---

## SCSS File Analysis

### 1. _primary_variables.scss (40 lines)
**Purpose:** Bootstrap variable overrides loaded BEFORE compilation

| Property | Value | Classification |
|----------|-------|----------------|
| `$o-community-color` | `#1e293b` | ✅ COLOR |
| `$o-enterprise-color` | `#1e293b` | ✅ COLOR |
| `$o-brand-odoo` | `#1e293b` | ✅ COLOR |
| `$o-brand-primary` | `#1e293b` | ✅ COLOR |
| `$o-action` | `#3b82f6` | ✅ COLOR |
| `$o-success` | `#10b981` | ✅ COLOR |
| `$o-info` | `#06b6d4` | ✅ COLOR |
| `$o-warning` | `#f59e0b` | ✅ COLOR |
| `$o-danger` | `#ef4444` | ✅ COLOR |
| `$o-main-link-color` | `#3b82f6` | ✅ COLOR |

**Verdict:** ✅ CLEAN. **Colors only.** No layout properties.

---

### 2. _debranding.scss (33 lines)
**Purpose:** Hide Odoo.com links and branding

| Rule | Classification |
|------|----------------|
| `a[href*="odoo.com"] { display: none }` | ✅ DEBRANDING |
| `.o_menu_brand { display: none }` | ✅ DEBRANDING |
| `.o_debug_manager a[href*="odoo.com"]` | ✅ DEBRANDING |

**Verdict:** ✅ ALLOWED. Debranding is an explicit allowed use case.

---

### 3. _chatter_position.scss (21 lines)
**Purpose:** Support for chatter position toggle

| Rule | Content | Classification |
|------|---------|----------------|
| `.o_form_view.o_xxl_form_view .o_form_sheet_bg` | **Empty rule block** | ✅ CLEAN |

**Verdict:** ✅ CLEAN. File contains only placeholder/comment. No actual overrides.

---

### 4. _login.scss (522 lines)
**Purpose:** Custom split-screen login page

**Scope:** ALL rules target `.ops-login-*` classes only.

| Pattern | Examples |
|---------|----------|
| Custom containers | `.ops-login-wrapper`, `.ops-login-container` |
| Brand panel | `.ops-login-brand`, `.ops-login-logo` |
| Form panel | `.ops-login-form-panel`, `.ops-login-header` |
| Mobile support | `@media (max-width: 767.98px)` |

**Native Odoo classes touched:**
- `.card`, `.card-body` - Set to `transparent/none` to reset default styling **on login page only**
- **Does NOT affect backend `.o_form_*` views**

**Verdict:** ✅ ALLOWED. Login page is OPS-custom territory. Not a backend view.

---

### 5. _ops_dark_mode.scss (82 lines)
**Purpose:** Dark mode colors for OPS-custom components

**Scope:** ALL rules scoped to `[data-color-mode="dark"] .ops-*` selectors.

**Explicit comment in file (lines 71-81):**
```scss
// DO NOT ADD OVERRIDES FOR NATIVE ODOO COMPONENTS:
// - .o_form_view
// - .o_list_view
// - .modal, .modal-content
// - .o_settings_container
// - .o_kanban_view
// - .o_control_panel
// - Any other native Odoo class
//
// Odoo 19 handles its own dark mode for these components!
```

**Verdict:** ✅ CLEAN. Only styles OPS-custom components. Explicitly avoids Odoo native.

---

## JavaScript File Analysis

### 1. theme_loader.js (31 lines)
**Purpose:** Initialize color mode, favicon, page title

| Action | Classification |
|--------|----------------|
| Set `data-color-mode` on `<html>` | ✅ COLOR |
| Replace favicon | ✅ DEBRANDING |
| Update page title (remove "Odoo") | ✅ DEBRANDING |

**Verdict:** ✅ CLEAN. No DOM structure manipulation.

---

### 2. debranding.js (131 lines)
**Purpose:** Remove enterprise/odoo.com elements

| Action | Classification |
|--------|----------------|
| Remove user menu items (`odoo_account`, etc.) | ✅ DEBRANDING |
| Remove systray items (`upgrade`, etc.) | ✅ DEBRANDING |
| Hide elements with `style.display = 'none'` | ✅ DEBRANDING |

**DOM Changes:** Sets `display: none` on branding elements only. **Does NOT modify backend view structure.**

**Verdict:** ✅ ALLOWED. Debranding is permitted.

---

### 3. ops_theme_toggles.js (89 lines)
**Purpose:** Add color mode and chatter position toggles to user menu

| Action | Classification |
|--------|----------------|
| Register user menu items | ✅ ENHANCEMENT |
| RPC to server for preference save | ✅ ENHANCEMENT |
| Reload page on toggle | ✅ SAFE |

**Verdict:** ✅ CLEAN. Adds menu items, does not modify view rendering.

---

### 4. chatter_position_patch.js (71 lines)
**Purpose:** Allow user to toggle chatter position

**Patch Target:** `FormRenderer.prototype.mailLayout()`

**How it works:**
1. Checks `session.ops_chatter_position` (user preference)
2. If preference exists, returns appropriate layout mode
3. If no preference, **falls back to Odoo's native logic**

```javascript
// Falls back to Odoo's automatic logic
return super.mailLayout(hasAttachmentContainer);
```

**Verdict:** ✅ ALLOWED. This is an **enhancement** that works WITH Odoo's architecture:
- Uses Odoo's native layout modes (`SIDE_CHATTER`, `BOTTOM_CHATTER`, etc.)
- Does not fight OWL rendering
- Respects screen size constraints
- Provides graceful fallback

---

## XML Template Analysis

### 1. login_templates.xml (157 lines)
**Purpose:** Override login page with split-screen design

**Target:** `web.login_layout` (frontend template, not backend views)

**Verdict:** ✅ ALLOWED. Login page is OPS-custom territory.

---

### 2. webclient_templates.xml (12 lines)
**Content:** Empty (just a note about JS handling)

**Verdict:** ✅ CLEAN. No overrides.

---

### 3. user_menu.xml (7 lines)
**Content:** Empty placeholder

**Verdict:** ✅ CLEAN. No overrides.

---

## Layout Contamination Scan Results

| Scan | Result |
|------|--------|
| Layout overrides on `.o_form_*`, `.o_group`, etc. | **NONE** |
| `display: none` on backend views | **NONE** (only debranding/login) |
| `!important` on layout properties | **NONE** (only `.ops-login-*`) |
| Hardcoded pixel sizes on Odoo classes | **NONE** (only `.ops-login-*`) |
| DOM manipulation in JS | **NONE** |
| Renderer patches modifying layout | **NONE** (chatter position is allowed) |

---

## Classification Summary

| Category | Files | Verdict |
|----------|-------|---------|
| **COLOR OVERRIDES** | `_primary_variables.scss` | ✅ ALLOWED |
| **DEBRANDING** | `_debranding.scss`, `debranding.js` | ✅ ALLOWED |
| **CUSTOM LOGIN** | `_login.scss`, `login_templates.xml` | ✅ ALLOWED |
| **OPS DARK MODE** | `_ops_dark_mode.scss` | ✅ ALLOWED |
| **CHATTER POSITION** | `chatter_position_patch.js` | ✅ ALLOWED |
| **THEME TOGGLES** | `ops_theme_toggles.js`, `theme_loader.js` | ✅ ALLOWED |

---

## Remediation Plan

### No Remediation Needed

The theme is **100% compliant** with the governing rule.

---

## Conclusion

The `ops_theme` module is a **model implementation** of the "Odoo 19 owns layout, OPS owns colors" philosophy:

- **Zero layout contamination** in backend views
- **All CSS** targets either Bootstrap variables or OPS-custom classes
- **All JS** works with Odoo's native systems, not against them
- **Explicit documentation** in code about what NOT to override
- **Graceful fallbacks** to Odoo native behavior

**Recommendation:** Use this theme as a **reference implementation** for any future theme development.

---

**Report Generated:** 2026-02-05
**Auditor:** Claude Code (Layout Mode)

