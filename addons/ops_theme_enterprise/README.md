# 🎨 OPS Enterprise Theme

**Version:** 1.0  
**Category:** Theme/Backend  
**License:** LGPL-3  
**Odoo Version:** 19.0 (Community Edition)

---

## 📋 Overview

The **OPS Enterprise Theme** is a purely visual module designed to transform the Odoo 19 backend interface with a modern, professional "Gilded Admin" aesthetic. This theme features:

- ✨ **Card-Based Layout** – Floating white containers with soft shadows
- 🎨 **Modern Color Palette** – Deep Navy primary with Vibrant Blue accents
- 📐 **Bootstrap 5 Native** – Fully integrated with Odoo 19's BS5 framework
- 🌙 **Dark Mode Compatible** – Uses CSS variables with fallbacks
- 🚀 **Zero Python Logic** – Pure SCSS/CSS implementation for easy maintenance

---

## 🎨 Color Palette Reference

Use these exact hex codes when extending or customizing the theme:

| Color Name         | Hex Code  | Usage                                    | CSS Variable                    |
|--------------------|-----------|------------------------------------------|---------------------------------|
| **Primary**        | `#0f172a` | Navbar, Dark Elements, Branding          | `var(--o-brand-odoo)`          |
| **Secondary**      | `#3b82f6` | Buttons, Links, Active States            | `var(--o-brand-primary)`       |
| **Background**     | `#f1f5f9` | Body Background (Light Grey)             | `var(--o-view-background-color)` |
| **Surface**        | `#ffffff` | Cards, Form Views, Modal Backgrounds     | `--`                           |
| **Text Primary**   | `#1e293b` | Headings, Labels, Primary Text           | `var(--o-main-text-color)`     |
| **Text Secondary** | `#64748b` | Muted Text, Descriptions, Placeholders   | `var(--o-main-text-color-muted)` |
| **Success**        | `#10b981` | Success Messages, Positive Actions       | `--`                           |
| **Warning**        | `#f59e0b` | Warning Messages, Alerts                 | `--`                           |
| **Danger**         | `#ef4444` | Error Messages, Delete Actions           | `--`                           |
| **Border**         | `#e2e8f0` | Borders, Dividers, Input Outlines        | `var(--o-border-color)`        |

### 🎨 Tailwind CSS Equivalents
For designers familiar with Tailwind CSS:
- Primary = `slate-900`
- Secondary = `blue-500`
- Background = `slate-100`
- Text Primary = `slate-800`
- Text Secondary = `slate-500`
- Border = `slate-200`

---

## 📁 File Structure & Purpose

```
addons/ops_theme_enterprise/
│
├── __init__.py                          # Python module initializer (minimal)
├── __manifest__.py                      # Module metadata & asset declarations
│
├── static/src/scss/
│   ├── primary_variables.scss           # 🔧 Bootstrap 5 variable overrides
│   └── layout_overrides.scss            # 🎨 Visual styling & component CSS
│
└── views/
    └── web_asset_backend_template.xml   # Asset bundle registration (empty)
```

### 🔧 `primary_variables.scss`
**Purpose:** Defines the design system foundation  
**Contains:**
- Color palette definitions (`$ops-primary`, `$ops-secondary`, etc.)
- Bootstrap 5 variable overrides (`$primary`, `$secondary`, etc.)
- Odoo-specific brand variables (`$o-brand-odoo`, `$o-brand-primary`)
- Typography system (font families, sizes, weights)
- Border radius & shadow definitions
- Component-specific variable overrides (cards, buttons, forms)

**When to Edit:**
- Changing brand colors across the entire theme
- Adjusting global spacing, shadows, or border radius
- Modifying default font families or sizes
- Tweaking button or input styling globally

### 🎨 `layout_overrides.scss`
**Purpose:** Applies visual styles to Odoo UI components  
**Contains:**
- Global body & web client background styling
- Navbar (top bar) styling with deep navy background
- View container styles (form, list, kanban, calendar, etc.)
- "Floating card" design with margins and shadows
- Control panel (search bar & buttons) styling
- Form elements (inputs, labels, groups)
- Modal dialog styling
- Chatter (sidebar) styling
- Search panel (left sidebar) styling

**When to Edit:**
- Adjusting specific view layouts (e.g., form view padding)
- Changing hover effects or transitions
- Modifying table row styling
- Tweaking card shadows or spacing
- Customizing specific UI components

---

## 🛠️ Installation & Activation

### Prerequisites
- Odoo 19 Community Edition
- `ops_matrix_core` module installed
- Docker environment: `gemini_odoo19` container

### Installation Steps

1. **Ensure the module is in the addons path:**
   ```bash
   ls /opt/gemini_odoo19/addons/ops_theme_enterprise/
   ```

2. **Install the module:**
   ```bash
   docker exec gemini_odoo19 odoo-bin -d mz-db -u ops_theme_enterprise --stop-after-init
   ```

3. **Restart Odoo container:**
   ```bash
   docker restart gemini_odoo19
   ```

4. **Clear browser cache** and refresh the Odoo interface.

### Verification
After installation, you should see:
- Deep navy navbar at the top
- Light grey background (`#f1f5f9`)
- White floating cards for form/list views with soft shadows
- Vibrant blue (`#3b82f6`) for primary buttons

---

## 🎨 Customization Guide

### 🔹 Changing the Brand Color (Primary)

If you need to change the primary brand color from Navy to another color:

1. **Edit `static/src/scss/primary_variables.scss`:**
   ```scss
   // Find this line:
   $ops-primary: #0f172a;  // Current: Deep Navy
   
   // Change to your brand color:
   $ops-primary: #1a365d;  // Example: Darker Blue
   ```

2. **Update dependent variables:**
   ```scss
   $dark: $ops-primary !default;
   $o-brand-odoo: $ops-primary !default;
   ```

3. **Save and upgrade the module:**
   ```bash
   docker exec gemini_odoo19 odoo-bin -d mz-db -u ops_theme_enterprise --stop-after-init
   ```

4. **Hard refresh your browser** (Ctrl+Shift+R or Cmd+Shift+R).

### 🔹 Changing the Accent Color (Secondary)

To change the secondary accent color (buttons, links):

1. **Edit `static/src/scss/primary_variables.scss`:**
   ```scss
   // Find this line:
   $ops-secondary: #3b82f6;  // Current: Vibrant Blue
   
   // Change to your accent color:
   $ops-secondary: #8b5cf6;  // Example: Purple
   ```

2. **Update Bootstrap primary:**
   ```scss
   $primary: $ops-secondary !default;
   $o-brand-primary: $ops-secondary !default;
   ```

3. **Save and upgrade** (same command as above).

### 🔹 Adjusting Card Shadows

To make shadows more or less prominent:

1. **Edit `static/src/scss/primary_variables.scss`:**
   ```scss
   // Find the shadow system:
   $box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !default;
   
   // Options:
   // Lighter shadow:
   $box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !default;
   
   // Heavier shadow:
   $box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !default;
   ```

2. **Save and upgrade the module.**

### 🔹 Modifying Border Radius

To change the "roundness" of cards and buttons:

1. **Edit `static/src/scss/primary_variables.scss`:**
   ```scss
   // Find these lines:
   $border-radius: 0.75rem !default;       // 12px - Default
   $border-radius-sm: 0.5rem !default;     // 8px
   $border-radius-lg: 1rem !default;       // 16px
   
   // Options:
   // More rounded:
   $border-radius: 1rem !default;          // 16px
   
   // Less rounded (sharper):
   $border-radius: 0.5rem !default;        // 8px
   
   // Square (no rounding):
   $border-radius: 0 !default;             // 0px
   ```

2. **Save and upgrade the module.**

---

## 🌙 Dark Mode Compatibility

This theme is designed to be **dark mode compatible** through the use of CSS variables with fallbacks:

```scss
// Example from layout_overrides.scss:
.o_form_view {
    background-color: var(--o-view-background-color, #ffffff) !important;
    color: var(--o-main-text-color, #1e293b);
}
```

**How it works:**
1. In **light mode**, Odoo's CSS variables are undefined, so the fallback values (our custom colors) are used.
2. In **dark mode**, Odoo automatically sets its own dark mode variables, overriding our fallbacks.
3. Result: The theme adapts automatically to the user's mode preference.

**Testing Dark Mode:**
1. In Odoo, go to **User Menu → Preferences**
2. Enable **Dark Mode**
3. Refresh the page
4. The theme should adapt with darker backgrounds and lighter text

---

## 🚫 What NOT to Do

### ❌ Do NOT Use Hardcoded Colors in Dark Mode
```scss
/* BAD - Breaks dark mode: */
.o_form_view {
    background-color: #ffffff !important;
    color: #000000;
}
```

```scss
/* GOOD - Dark mode compatible: */
.o_form_view {
    background-color: var(--o-view-background-color, #ffffff) !important;
    color: var(--o-main-text-color, #000000);
}
```

### ❌ Do NOT Add Python Logic to This Module
This is a **purely visual theme**. All business logic belongs in `ops_matrix_core` or other functional modules. Keep this module lightweight for easy upgrades.

### ❌ Do NOT Modify Core Odoo Files
Always use inheritance and overrides in this module. Never edit:
- `/usr/lib/python3/dist-packages/odoo/` (Core Odoo)
- Standard Odoo addons directly (`sale`, `account`, etc.)

---

## 📝 Maintenance Notes

### After SCSS Changes
```bash
# Always upgrade the module after editing SCSS:
docker exec gemini_odoo19 odoo-bin -d mz-db -u ops_theme_enterprise --stop-after-init

# Then perform a hard browser refresh
```

### Debugging CSS Issues
1. **Open browser DevTools** (F12)
2. **Inspect the element** to see computed styles
3. **Check if CSS variables are loading** in the Styles panel
4. **Look for overriding rules** that might be conflicting

### Common Issues
| Issue | Solution |
|-------|----------|
| "Styles not applying" | Upgrade module + hard refresh browser |
| "Dark mode broken" | Check for hardcoded colors without CSS variables |
| "Buttons wrong color" | Verify `$o-brand-primary` in `primary_variables.scss` |
| "Cards not floating" | Check `.o_form_view` margin in `layout_overrides.scss` |

---

## 📞 Support & Contribution

**Project:** OPS Framework (Enterprise ERP on Odoo CE)  
**Module Maintainer:** Frontend Team  
**Dependencies:** `base`, `web`, `ops_matrix_core`

For issues or customization requests, consult the project's main documentation in `/docs/technical/`.

---

## 📄 License

LGPL-3 – This module is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

---

**Last Updated:** January 2026  
**Odoo Version:** 19.0 Community Edition