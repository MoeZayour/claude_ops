# OPS Theme Guidebook

**A Complete Handbook for Developers & Administrators**

**Version:** 19.0.6.6.3 | **Odoo:** 19.0 | **Last Updated:** February 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Architecture Overview](#3-architecture-overview)
4. [Color System](#4-color-system)
5. [Dark Mode Implementation](#5-dark-mode-implementation)
6. [User Preferences](#6-user-preferences)
7. [CSS Variables Reference](#7-css-variables-reference)
8. [SCSS File Guide](#8-scss-file-guide)
9. [JavaScript Components](#9-javascript-components)
10. [Customization Guide](#10-customization-guide)
11. [Troubleshooting](#11-troubleshooting)
12. [Best Practices](#12-best-practices)
13. [API Reference](#13-api-reference)

---

## 1. Introduction

### What is OPS Theme?

OPS Theme is a premium enterprise theme for Odoo 19 that provides:

- **Complete Debranding**: Removes all Odoo purple colors and branding
- **Dark Mode**: Full dark mode support with user toggle
- **Modern Design**: Clean slate/blue color scheme with Inter font
- **Enhanced Components**: Improved forms, cards, buttons, and tables
- **User Preferences**: Color mode and chatter position saved per user

### Design Philosophy

1. **Minimal Override**: Only override what's necessary
2. **CSS Variables First**: Use custom properties for theming
3. **Bootstrap Compatible**: Work with Odoo's Bootstrap foundation
4. **Performance**: Efficient CSS with targeted selectors
5. **Maintainability**: Organized file structure with clear naming

---

## 2. Installation

### Prerequisites

- Odoo 19.0
- Python 3.10+
- PostgreSQL 13+

### Installation Steps

1. **Copy module to addons directory:**
   ```bash
   cp -r ops_theme /path/to/odoo/addons/
   ```

2. **Update module list:**
   ```bash
   docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db --update=base --stop-after-init --no-http
   ```

3. **Install the module:**
   - Go to Apps
   - Search for "OPS Theme"
   - Click Install

4. **Restart container:**
   ```bash
   docker restart gemini_odoo19
   ```

### Post-Installation

After installation:
- Refresh browser (Ctrl+Shift+R to clear cache)
- The theme is automatically applied
- Use user menu to toggle dark mode

---

## 3. Architecture Overview

### Module Structure

```
ops_theme/
├── __manifest__.py          # Dependencies, assets, data files
├── models/                  # Python models
├── controllers/             # HTTP controllers
├── views/                   # XML views and templates
├── security/                # Access control
└── static/src/              # Frontend assets
    ├── scss/               # Stylesheets
    ├── js/                 # JavaScript
    └── xml/                # QWeb templates
```

### Asset Loading Pipeline

```
1. PRIMARY VARIABLES (web._assets_primary_variables)
   └── _primary_variables.scss → Overrides Bootstrap BEFORE compilation

2. FRONTEND (web.assets_frontend)
   └── Login page styles

3. BACKEND (web.assets_backend)
   ├── CSS Variables (_variables.scss)
   ├── Typography
   ├── Components (forms, cards, buttons, etc.)
   ├── Layout (navbar, list, control panel)
   ├── Dark Mode
   ├── Debranding
   └── JavaScript
```

### Why This Order Matters

- `_primary_variables.scss` loads BEFORE Bootstrap compiles
- This allows changing `$primary`, `$secondary`, etc. at the source
- Other SCSS files load AFTER and use CSS custom properties
- JavaScript loads last for DOM manipulation

---

## 4. Color System

### Brand Colors

| Name | Light Mode | Dark Mode | Usage |
|------|------------|-----------|-------|
| Primary | `#1e293b` | `#1e293b` | Navbar, headers, brand |
| Secondary | `#3b82f6` | `#3b82f6` | Buttons, links, accents |
| Success | `#10b981` | `#10b981` | Success states |
| Warning | `#f59e0b` | `#f59e0b` | Warning states |
| Danger | `#ef4444` | `#ef4444` | Error states |
| Info | `#06b6d4` | `#06b6d4` | Info states |

### Background Colors

| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Body | `#f1f5f9` | `#0f172a` |
| Cards/Panels | `#ffffff` | `#1e293b` |
| Hover | `#f8fafc` | `#334155` |
| Selected | `#eff6ff` | `rgba(59,130,246,0.2)` |
| Inputs | `#ffffff` | `#334155` |

### Text Colors

| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary | `#1e293b` | `#f1f5f9` |
| Secondary | `#64748b` | `#94a3b8` |
| Muted | `#94a3b8` | `#64748b` |
| Disabled | `#cbd5e1` | `#475569` |
| Links | `#3b82f6` | `#60a5fa` |

### Border Colors

| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Default | `#e2e8f0` | `#334155` |
| Focus | `#3b82f6` | `#3b82f6` |
| Divider | `#f1f5f9` | `#1e293b` |

---

## 5. Dark Mode Implementation

### How Dark Mode Works

1. **HTML Attribute**: `data-color-mode="dark"` on `<html>`
2. **CSS Class**: `ops-dark-mode` on `<html>` and `<body>`
3. **localStorage**: `ops_color_mode` key stores preference
4. **Database**: `res.users.ops_color_mode` field

### CSS Selector Pattern

```scss
// Light mode (default) - no selector needed
.my-component {
    background-color: #ffffff;
    color: #1e293b;
}

// Dark mode - use attribute selector
[data-color-mode="dark"] {
    .my-component {
        background-color: #1e293b;
        color: #f1f5f9;
    }
}
```

### JavaScript API

```javascript
// Get current mode
const mode = window.getOpsColorMode(); // 'light' or 'dark'

// Set mode
window.setOpsColorMode('dark');
window.setOpsColorMode('light');

// Toggle
const current = window.getOpsColorMode();
window.setOpsColorMode(current === 'light' ? 'dark' : 'light');
```

### Initialization Flow

```
1. Page Load
   ↓
2. theme_loader.js runs
   ↓
3. Check localStorage for saved preference
   ↓
4. Apply data-color-mode attribute
   ↓
5. CSS automatically applies correct colors
```

---

## 6. User Preferences

### Available Preferences

| Preference | Field | localStorage Key | Values |
|------------|-------|------------------|--------|
| Color Mode | `ops_color_mode` | `ops_color_mode` | `light`, `dark` |
| Chatter Position | `ops_chatter_position` | `ops_chatter_position` | `bottom`, `right` |

### User Menu Items

The user menu (avatar dropdown) contains:

1. **Switch to Dark/Light Mode** - Toggles color mode
2. **Chatter: Move to Bottom/Side** - Toggles chatter position

### Saving Preferences

Preferences are saved in two places:
1. **localStorage** - Immediate, works offline
2. **Database** - Persists across devices

```javascript
// Example: Save to both
localStorage.setItem('ops_color_mode', 'dark');

// Save to database via RPC
fetch('/web/dataset/call_kw/res.users/write', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
            model: 'res.users',
            method: 'write',
            args: [[userId], { ops_color_mode: 'dark' }],
            kwargs: {},
        },
    }),
});
```

---

## 7. CSS Variables Reference

### Complete Variable List

```scss
:root {
    // Brand
    --ops-primary: #1e293b;
    --ops-primary-rgb: 30, 41, 59;
    --ops-primary-hover: #0f172a;
    --ops-primary-light: rgba(30, 41, 59, 0.1);
    --ops-secondary: #3b82f6;
    --ops-secondary-rgb: 59, 130, 246;
    --ops-secondary-hover: #2563eb;
    --ops-secondary-light: rgba(59, 130, 246, 0.1);

    // Semantic
    --ops-success: #10b981;
    --ops-warning: #f59e0b;
    --ops-danger: #ef4444;
    --ops-info: #06b6d4;

    // Backgrounds
    --ops-bg-body: #f1f5f9;
    --ops-bg-card: #ffffff;
    --ops-bg-input: #ffffff;
    --ops-bg-hover: #f8fafc;
    --ops-bg-selected: #eff6ff;
    --ops-bg-navbar: var(--ops-primary);
    --ops-bg-dropdown: #ffffff;
    --ops-bg-modal: #ffffff;

    // Text
    --ops-text-primary: #1e293b;
    --ops-text-secondary: #64748b;
    --ops-text-muted: #94a3b8;
    --ops-text-disabled: #cbd5e1;
    --ops-text-inverse: #ffffff;
    --ops-text-link: var(--ops-secondary);

    // Borders
    --ops-border: #e2e8f0;
    --ops-border-focus: var(--ops-secondary);
    --ops-divider: #f1f5f9;

    // Shadows
    --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --ops-card-shadow: var(--ops-shadow-md);

    // Radius
    --ops-radius-sm: 4px;
    --ops-radius-md: 8px;
    --ops-radius-lg: 12px;
    --ops-radius-xl: 16px;
    --ops-radius-full: 9999px;

    // Transitions
    --ops-transition-fast: 150ms ease;
    --ops-transition-normal: 250ms ease;
    --ops-transition-slow: 300ms ease;

    // Typography
    --ops-font-family: 'Inter', -apple-system, sans-serif;
    --ops-font-size-xs: 0.75rem;
    --ops-font-size-sm: 0.875rem;
    --ops-font-size-md: 1rem;
    --ops-font-size-lg: 1.125rem;
    --ops-font-weight-normal: 400;
    --ops-font-weight-medium: 500;
    --ops-font-weight-semibold: 600;
    --ops-font-weight-bold: 700;
}
```

### Using Variables

```scss
// In your SCSS
.my-card {
    background-color: var(--ops-bg-card);
    color: var(--ops-text-primary);
    border: 1px solid var(--ops-border);
    border-radius: var(--ops-radius-md);
    box-shadow: var(--ops-card-shadow);
    transition: box-shadow var(--ops-transition-normal);

    &:hover {
        box-shadow: var(--ops-shadow-lg);
    }
}
```

---

## 8. SCSS File Guide

### Core Files

| File | Purpose | Lines |
|------|---------|-------|
| `_variables.scss` | CSS custom properties | ~200 |
| `_primary_variables.scss` | Bootstrap overrides | ~50 |
| `_dark_mode_comprehensive.scss` | All dark mode fixes | 3,823 |

### Component Files

| File | Components Styled |
|------|-------------------|
| `_typography.scss` | Fonts, headings, text |
| `_form_controls.scss` | Inputs, checkboxes, toggles |
| `_cards.scss` | Card containers, KPIs |
| `_badges_enhanced.scss` | Status badges |
| `_buttons_enhanced.scss` | Button variants |
| `_tables.scss` | Table styling |

### Layout Files

| File | Layout Elements |
|------|-----------------|
| `_navbar.scss` | Top navigation bar |
| `_list.scss` | List view styling |
| `_control_panel.scss` | Search, filters, buttons |
| `_kanban.scss` | Kanban view cards |

### Special Files

| File | Purpose |
|------|---------|
| `_login.scss` | Split-screen login page |
| `_debranding.scss` | Remove Odoo branding |
| `_chatter_fix.scss` | Chatter readability |
| `_settings_layout.scss` | Settings page layout |

### Comprehensive Fix File Structure

The `_dark_mode_comprehensive.scss` contains 22 fixes:

```scss
/* =============================================================================
   FIX 1: NOTEBOOK TABS
   ============================================================================= */
// Lines 735-777

/* =============================================================================
   FIX 2: CHATTER
   ============================================================================= */
// Lines 778-845

// ... continues through FIX 22
```

---

## 9. JavaScript Components

### theme_loader.js

**Purpose**: Initialize theme on page load

```javascript
// Key functions
window.getOpsColorMode()    // Get current mode
window.setOpsColorMode(m)   // Set mode ('light'/'dark')
window.initOpsTheme()       // Initialize theme
```

### user_menu_items.js

**Purpose**: Add color mode toggle to user menu

```javascript
// Registers menu item
registry.category("user_menuitems").add("ops_color_mode", colorModeToggleItem);
```

### chatter_toggle.js

**Purpose**: Add chatter position toggle to user menu

```javascript
// Functions
getCurrentChatterPosition()  // 'bottom' or 'right'
applyChatterPosition(pos)    // Apply CSS class
toggleChatterPosition()      // Toggle and save

// Registers menu item
registry.category("user_menuitems").add("ops_chatter_position", chatterPositionToggleItem);
```

### debranding.js

**Purpose**: Remove Odoo branding from UI

- Clears systray registry items
- Removes "Odoo" from title
- Hides enterprise features

### control_panel_refresh.js

**Purpose**: Add auto-refresh to list views

```javascript
// Adds refresh button to control panel
// Configurable interval
```

### group_actions.js

**Purpose**: Expand/collapse all groups

```javascript
// Adds buttons to grouped list views
// "Expand All" / "Collapse All"
```

---

## 10. Customization Guide

### Changing Brand Colors

Edit `_primary_variables.scss`:

```scss
// Change primary color
$primary: #your-color;
$o-brand-odoo: #your-color;
$o-brand-primary: #your-color;

// Change secondary color
$secondary: #your-accent;
```

Edit `_variables.scss`:

```scss
:root {
    --ops-primary: #your-color;
    --ops-secondary: #your-accent;
}
```

### Adding New Dark Mode Fixes

Follow this pattern in `_dark_mode_comprehensive.scss`:

```scss
/* =============================================================================
   FIX XX: COMPONENT NAME - Brief description
   ============================================================================= */

// Light mode (if needed)
.component-class {
    background-color: #ffffff !important;
    color: #1e293b !important;
}

// Dark mode
[data-color-mode="dark"] {
    .component-class {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
}
```

### Custom Component Styling

Create a new SCSS file:

```scss
// _my_component.scss

// Light mode (default)
.my-component {
    background-color: var(--ops-bg-card);
    color: var(--ops-text-primary);
    border: 1px solid var(--ops-border);
    border-radius: var(--ops-radius-md);
}

// Dark mode
[data-color-mode="dark"] {
    .my-component {
        background-color: #1e293b;
        color: #f1f5f9;
        border-color: #334155;
    }
}
```

Add to manifest:

```python
'assets': {
    'web.assets_backend': [
        # ... existing files
        'ops_theme/static/src/scss/_my_component.scss',
    ],
},
```

---

## 11. Troubleshooting

### Common Issues

#### Issue: Colors not updating after changes

**Solution:**
```bash
# Clear browser cache
Ctrl+Shift+R (hard refresh)

# Restart container
docker restart gemini_odoo19

# Or full module update
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init --no-http
```

#### Issue: Dark mode not applying to specific element

**Solution:**
1. Inspect element in DevTools
2. Find exact class names
3. Add fix to `_dark_mode_comprehensive.scss`:

```scss
[data-color-mode="dark"] {
    .exact-class-name {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
}
```

#### Issue: Purple color still visible somewhere

**Solution:**
The element is using Odoo's native `$primary` or `$o-brand-odoo`. Add override:

```scss
// In appropriate SCSS file
.element-class {
    background-color: #3b82f6 !important;  // Replace purple with blue
    border-color: #3b82f6 !important;
}
```

#### Issue: Module update fails

**Solution:**
Often caused by security group dependencies. Use restart instead:
```bash
docker restart gemini_odoo19
```

#### Issue: JavaScript error in user menu

**Solution:**
Check browser console. Ensure:
1. OWL component properly registered
2. Menu item format is correct:
```javascript
{
    type: "item",
    id: "unique_id",
    description: "Menu Label",
    callback: async () => { /* action */ },
    sequence: 10,
}
```

### Debug Mode

Enable developer mode to see more details:
1. Go to Settings
2. Scroll to bottom
3. Click "Activate developer mode"

### Checking Applied Styles

```javascript
// In browser console
// Get computed style
getComputedStyle(document.querySelector('.element')).backgroundColor

// Check color mode
document.documentElement.getAttribute('data-color-mode')

// Check localStorage
localStorage.getItem('ops_color_mode')
```

---

## 12. Best Practices

### CSS Guidelines

1. **Use !important sparingly but consistently**
   - Odoo uses high specificity; we need `!important` to override
   - Be consistent: if you use it, use it everywhere for that property

2. **Follow the selector pattern**
   ```scss
   // Light mode first (no selector)
   .component { ... }

   // Dark mode with attribute selector
   [data-color-mode="dark"] {
       .component { ... }
   }
   ```

3. **Use CSS variables for values that change**
   ```scss
   // Good
   color: var(--ops-text-primary);

   // Avoid hardcoding in light mode
   color: #1e293b;
   ```

4. **Group related fixes**
   - Keep component fixes together
   - Use clear section headers

### JavaScript Guidelines

1. **Check for global functions before calling**
   ```javascript
   if (typeof window.setOpsColorMode === 'function') {
       window.setOpsColorMode(newMode);
   }
   ```

2. **Use registry properly**
   ```javascript
   registry.category("user_menuitems").add("unique_id", itemFunction, { sequence: 10 });
   ```

3. **Handle errors gracefully**
   ```javascript
   try {
       // action
   } catch (err) {
       console.warn('[OPS Theme] Error:', err);
   }
   ```

### Maintenance Guidelines

1. **Document all fixes**
   - Use clear section headers
   - Explain what component is being fixed
   - Note which Odoo classes are targeted

2. **Version bump for every change**
   ```python
   'version': '19.0.6.6.X',  # Increment X
   ```

3. **Test in both modes**
   - Always test light mode AND dark mode
   - Check all major views: list, form, kanban, dashboard

4. **Backup before major changes**
   - The `_unused_backup` folder is for archived code

---

## 13. API Reference

### Python Models

#### res.users (Extended)

| Field | Type | Description |
|-------|------|-------------|
| `ops_color_mode` | Selection | `light` or `dark` |
| `ops_chatter_position` | Selection | `bottom` or `right` |

#### res.company (Extended)

| Field | Type | Description |
|-------|------|-------------|
| `ops_theme_enabled` | Boolean | Theme active for company |

### HTTP Controllers

#### /ops_theme/preferences (GET)

Returns current user's theme preferences.

Response:
```json
{
    "color_mode": "dark",
    "chatter_position": "bottom"
}
```

#### /ops_theme/preferences (POST)

Updates user's theme preferences.

Body:
```json
{
    "color_mode": "dark",
    "chatter_position": "right"
}
```

### JavaScript Global Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `window.getOpsColorMode()` | - | `'light'` or `'dark'` | Get current color mode |
| `window.setOpsColorMode()` | `mode: string` | - | Set color mode |
| `window.initOpsTheme()` | - | - | Initialize theme |

### OWL Registry Items

| Registry | Key | Type |
|----------|-----|------|
| `user_menuitems` | `ops_color_mode` | Menu item |
| `user_menuitems` | `ops_chatter_position` | Menu item |

---

## Appendix A: Color Palette Quick Reference

### Slate Scale (Primary)

```
#0f172a - Slate 900 (darkest bg)
#1e293b - Slate 800 (dark card bg)
#334155 - Slate 700 (dark hover)
#475569 - Slate 600 (dark border)
#64748b - Slate 500 (muted text)
#94a3b8 - Slate 400 (secondary text dark)
#cbd5e1 - Slate 300 (disabled)
#e2e8f0 - Slate 200 (light border)
#f1f5f9 - Slate 100 (light bg)
#f8fafc - Slate 50 (hover bg)
```

### Blue Scale (Secondary)

```
#1e3a5f - Blue 900 (dark card with blue)
#1e40af - Blue 800 (dark active)
#2563eb - Blue 700 (hover)
#3b82f6 - Blue 600 (primary blue)
#60a5fa - Blue 500 (light mode accent)
#93c5fd - Blue 400 (dark mode link)
#bfdbfe - Blue 300 (light card accent)
#dbeafe - Blue 200 (light selected)
#eff6ff - Blue 100 (lightest blue bg)
```

---

## Appendix B: File Size Reference

| File | Lines | Size |
|------|-------|------|
| `_dark_mode_comprehensive.scss` | 3,823 | ~120KB |
| `_variables.scss` | ~200 | ~6KB |
| `_form_controls.scss` | ~300 | ~10KB |
| `_login.scss` | ~200 | ~6KB |
| **Total SCSS** | ~5,500 | ~180KB |

---

## Appendix C: Changelog

### v19.0.6.6.3 (2026-02-01)
- FIX 22: Odoo app dashboards (Purchase, Sales, Inventory, CRM)
- Fixed `bg-view` class for all modes

### v19.0.6.6.2 (2026-02-01)
- FIX 21: OPS Dashboard custom components

### v19.0.6.6.1 (2026-02-01)
- FIX 20: Note editor and add links

### v19.0.6.6.0 (2026-02-01)
- FIX 19: Kanban view complete overhaul
- Replaced all 12 kanban color classes

### v19.0.6.5.9 (2026-02-01)
- FIX 18: Search panel sidebar

### v19.0.6.5.8 (2026-02-01)
- FIX 17: Status bar widget (purple → blue)

---

**End of Guidebook**

*For questions or contributions, see the GitHub repository.*
