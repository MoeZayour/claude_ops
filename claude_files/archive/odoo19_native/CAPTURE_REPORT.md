# Odoo 19 CE Native Source Capture Report

**Date:** 2026-02-04  
**Purpose:** Reference material for OPS Theme refactoring  
**Target:** Odoo 19.0-20251208

---

## Executive Summary

This archive contains extracted Odoo 19 CE source code for reference during theme development. The capture includes:
- Core SCSS architecture and Bootstrap overrides
- Webclient OWL components (navbar, user menu, burger menu, settings)
- View renderers (form, list, kanban)
- Account module views for xpath targeting
- Login templates and color management

---

## File Inventory

| Category | Count | Location |
|----------|-------|----------|
| SCSS Variables | 76 files | `scss/` |
| Webclient Components | 65 files | `webclient/` |
| View Renderers | 31 files | `views/` |
| Account Reference | 5 files | `account/` |
| Dashboard Reference | 1 files | `dashboard/` |
| Templates | 4 files | `templates/` |
| Bug Evidence | 5 files | `bugs/` |

---

## Bug Investigation Results

### BUG-001: Template Branch on Fresh Install

**Status:** ⚠️ DESIGN ISSUE (not a bug)

**Source:** `ops_user_templates.xml` line 37
- Creates `[TEMPLATE] Branch` with code `TMPL_BR`
- Set to `active=True` in `noupdate="1"` block
- This is intentional for user cloning but should be hidden

**Recommendation:** Change to `active=False` to hide from normal users.

---

### BUG-002: Template Business Unit on Fresh Install

**Status:** ✅ CONFIRMED

**Source:** `ops_user_templates.xml` line 30
- Creates `[TEMPLATE] Business Unit` with code `TMPL_BU`
- Visible to all users with `active=True`

**Current Database:**
```
 id |  code   |           name           | active 
----+---------+--------------------------+--------
  1 | TMPL_BU | [TEMPLATE] Business Unit | t
  2 | BU-0001 | Sales Unit               | t
```

**Recommendation:** Change to `active=False` to hide from normal users.

---

### BUG-003: Company Sequence "MYC"

**Status:** ❌ NOT A BUG

**Finding:** The "MYC" is the company's `ops_code` field value, set by the user during company setup.

**Current Database:**
```
 id |           name           | ops_code 
----+--------------------------+----------
  1 | MZ International Markets | MYC
```

**Explanation:** This is working as designed. The company code is user-configurable.

---

## Key SCSS Files for Theming

### Primary Variables (Load BEFORE Bootstrap)
- `scss/primary_variables.scss` - Brand colors, o-brand variables
- `scss/pre_variables.scss` - Pre-Bootstrap setup
- `scss/bootstrap_overridden.scss` - Bootstrap customizations

### Component SCSS
- `scss/core/dialog/dialog.scss` - Modal/dialog styles
- `views/form/form_controller.scss` - Form view styles
- `views/list/list_renderer.scss` - List view styles
- `views/kanban/kanban_record.scss` - Kanban card styles

### Webclient SCSS
- `webclient/navbar/navbar.scss` - Main navigation bar
- `webclient/settings_form_view/settings_form_view.scss` - Settings page
- `webclient/user_menu/user_menu.scss` - User dropdown

---

## Asset Bundle Structure

### `web._assets_primary_variables` (2 entries)
These load BEFORE Bootstrap - ideal for brand color overrides:
```
web/static/src/scss/primary_variables.scss
web/static/src/**/*.variables.scss
```

### `web.assets_frontend` (67 entries)
Public-facing pages (login, portal).

### `web.assets_backend` (66 entries)
Internal application (after login).

---

## Color Mode / Dark Mode

Key files for dark mode implementation:
- `webclient/core/colors/colors.js` - Color utilities
- `scss/bootstrap_overridden.scss` - Contains `[data-color-mode="dark"]` scopes

Odoo 19 uses `data-color-mode` attribute on `<html>` element:
- `data-color-mode="light"` - Light mode
- `data-color-mode="dark"` - Dark mode

---

## Next Steps

1. **Fix BUG-001 & BUG-002:** Update `ops_user_templates.xml` to set `active=False`
2. **Theme Refactoring:** Use `scss/primary_variables.scss` as reference for color overrides
3. **Dark Mode:** Ensure all OPS theme styles use `[data-color-mode="dark"]` scopes
4. **HomeMenu:** CE uses burger menu - Enterprise-style full-page grid requires custom OWL component

---

## Archive Structure

```
odoo19_native/
├── scss/                    # SCSS variables and Bootstrap overrides
│   ├── primary_variables.scss
│   ├── bootstrap_overridden.scss
│   ├── core/               # Core component styles
│   └── views/              # View-specific styles
├── webclient/              # OWL components
│   ├── navbar/             # Main navbar
│   ├── user_menu/          # User dropdown
│   ├── burger_menu/        # CE home menu
│   ├── settings_form_view/ # Settings page
│   └── core/               # Core utilities
├── views/                  # View renderers
│   ├── form/               # Form view
│   ├── list/               # List view
│   └── kanban/             # Kanban view
├── account/                # Account module references
├── dashboard/              # Dashboard framework
├── templates/              # XML templates
├── bugs/                   # Bug investigation evidence
├── ASSET_BUNDLES.txt       # Asset bundle analysis
├── OPS_THEME_CURRENT_FILES.txt
└── OPS_THEME_MANIFEST.py
```

---

*Generated by Claude Code - Odoo 19 CE Native Capture Mission*
