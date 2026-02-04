# OPS Theme Development Skill

**Skill Name**: `ops-theme`  
**Command**: `/ops-theme`  
**Description**: OPS Theme module development for white-label enterprise UI

---

## Skill Purpose

This skill guides Claude Code through OPS Theme module development, ensuring:
- White-label, company-brandable UI (no Odoo branding)
- Dynamic CSS generation from company settings
- Light/Dark/System color mode support
- Consistent design patterns across all views
- Mobile-responsive layouts
- Split-screen login with company branding
- Horizontal menu tabs with app grid home

---

## Context Files (Always Load)

When this skill is invoked, Claude Code should read:

```
/opt/gemini_odoo19/addons/ops_theme/__manifest__.py
/opt/gemini_odoo19/addons/ops_theme/static/src/scss/theme.scss
```

---

## Module Location

```
/opt/gemini_odoo19/addons/ops_theme/
```

---

## Code Patterns to Follow

### 1. Company Theme Fields Pattern
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Theme Preset
    ops_theme_preset = fields.Selection([
        ('corporate_blue', 'Corporate Blue'),
        ('modern_dark', 'Modern Dark'),
        ('clean_light', 'Clean Light'),
        ('enterprise_navy', 'Enterprise Navy'),
        ('custom', 'Custom'),
    ], string='Theme Preset', default='corporate_blue')

    # Brand Colors
    ops_primary_color = fields.Char(
        string='Primary Color',
        default='#1e293b',
        help='Main brand color for navbar and headers'
    )
    ops_secondary_color = fields.Char(
        string='Secondary Color', 
        default='#3b82f6',
        help='Accent color for buttons and links'
    )
    ops_success_color = fields.Char(string='Success Color', default='#10b981')
    ops_warning_color = fields.Char(string='Warning Color', default='#f59e0b')
    ops_danger_color = fields.Char(string='Danger Color', default='#ef4444')

    # Login Page
    ops_login_background = fields.Binary(string='Login Background Image')
    ops_login_tagline = fields.Char(
        string='Login Tagline',
        default='Enterprise Resource Planning'
    )
    ops_login_show_logo = fields.Boolean(string='Show Logo on Login', default=True)

    # Layout Options
    ops_navbar_style = fields.Selection([
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('primary', 'Primary Color'),
    ], string='Navbar Style', default='dark')
    ops_card_shadow = fields.Selection([
        ('none', 'None'),
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('heavy', 'Heavy'),
    ], string='Card Shadow', default='medium')
    ops_border_radius = fields.Selection([
        ('sharp', 'Sharp'),
        ('rounded', 'Rounded'),
        ('pill', 'Pill'),
    ], string='Border Radius', default='rounded')

    # Reports
    ops_report_header_bg = fields.Char(string='Report Header Color', default='#1e293b')
    ops_report_logo_position = fields.Selection([
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ], string='Logo Position', default='left')

    # Attribution
    ops_powered_by_visible = fields.Boolean(
        string='Show "Powered by OPS Framework"',
        default=True
    )

    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        presets = {
            'corporate_blue': ('#1e293b', '#3b82f6'),
            'modern_dark': ('#0f172a', '#6366f1'),
            'clean_light': ('#374151', '#059669'),
            'enterprise_navy': ('#1e3a5f', '#0ea5e9'),
        }
        if self.ops_theme_preset in presets:
            self.ops_primary_color, self.ops_secondary_color = presets[self.ops_theme_preset]
```

### 2. User Preferences Pattern
```python
class ResUsers(models.Model):
    _inherit = 'res.users'

    ops_chatter_position = fields.Selection([
        ('below', 'Below Form'),
        ('right', 'Right Side'),
    ], string='Chatter Position', default='below')
    
    ops_color_mode = fields.Selection([
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System (Auto)'),
    ], string='Color Mode', default='system',
       help='Light: Always light theme. Dark: Always dark theme. System: Follow browser/OS preference.')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['ops_chatter_position', 'ops_color_mode']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['ops_chatter_position', 'ops_color_mode']
```

### 3. Dynamic CSS Controller Pattern
```python
from odoo import http
from odoo.http import request


class OpsThemeController(http.Controller):

    @http.route('/ops_theme/variables.css', type='http', auth='public', cors='*')
    def theme_variables(self, **kwargs):
        company = request.env.company
        
        css = f"""
:root {{
    --ops-primary: {company.ops_primary_color or '#1e293b'};
    --ops-secondary: {company.ops_secondary_color or '#3b82f6'};
    --ops-success: {company.ops_success_color or '#10b981'};
    --ops-warning: {company.ops_warning_color or '#f59e0b'};
    --ops-danger: {company.ops_danger_color or '#ef4444'};
    
    --ops-bg-body: #f1f5f9;
    --ops-bg-card: #ffffff;
    --ops-text-primary: #1e293b;
    --ops-text-secondary: #64748b;
    --ops-border: #e2e8f0;
    
    --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    
    --ops-radius-sm: 0.375rem;
    --ops-radius-md: 0.5rem;
    --ops-radius-lg: 0.75rem;
}}
"""
        return request.make_response(css, headers=[
            ('Content-Type', 'text/css'),
            ('Cache-Control', 'public, max-age=3600'),
        ])
```

### 4. SCSS Pattern (Light/Dark Mode Support)
```scss
// =============================================================================
// OPS THEME - COMPONENT NAME
// =============================================================================
// ALWAYS use CSS custom properties, NEVER hardcode colors
// Variables automatically switch between light/dark mode
// =============================================================================

.ops-component {
    background-color: var(--ops-bg-card);
    color: var(--ops-text-primary);
    border: 1px solid var(--ops-border);
    border-radius: var(--ops-radius-md);
    box-shadow: var(--ops-shadow-sm);
    
    &:hover {
        border-color: var(--ops-secondary);
        box-shadow: var(--ops-shadow-md);
    }
    
    &__title {
        color: var(--ops-text-primary);
        font-weight: 600;
    }
    
    &__subtitle {
        color: var(--ops-text-secondary);
    }
    
    // Variants
    &--primary { background-color: var(--ops-primary); color: var(--ops-text-inverse); }
    &--success { background-color: var(--ops-success); color: var(--ops-text-inverse); }
    &--warning { background-color: var(--ops-warning); color: var(--ops-text-inverse); }
    &--danger { background-color: var(--ops-danger); color: var(--ops-text-inverse); }
}

// Responsive
@media (max-width: 991.98px) {
    .ops-component {
        // Mobile adjustments
    }
}
```

### 5. CSS Variables Pattern (Light/Dark/System)
```scss
// =============================================================================
// LIGHT MODE (Default)
// =============================================================================
:root,
[data-color-mode="light"] {
    // Brand (from company settings via dynamic CSS)
    --ops-primary: #1e293b;
    --ops-secondary: #3b82f6;
    
    // Semantic (consistent in both modes)
    --ops-success: #10b981;
    --ops-warning: #f59e0b;
    --ops-danger: #ef4444;
    --ops-info: #06b6d4;
    
    // Backgrounds - LIGHT
    --ops-bg-body: #f1f5f9;
    --ops-bg-card: #ffffff;
    --ops-bg-input: #ffffff;
    --ops-bg-hover: #f8fafc;
    
    // Text - LIGHT
    --ops-text-primary: #1e293b;
    --ops-text-secondary: #64748b;
    --ops-text-disabled: #94a3b8;
    --ops-text-inverse: #ffffff;
    
    // Borders - LIGHT
    --ops-border: #e2e8f0;
    --ops-border-focus: var(--ops-secondary);
    
    // Shadows - LIGHT
    --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

// =============================================================================
// DARK MODE
// =============================================================================
[data-color-mode="dark"] {
    // Brand - auto-adjusted for dark backgrounds
    --ops-primary: #475569;
    --ops-secondary: #60a5fa;
    
    // Backgrounds - DARK
    --ops-bg-body: #0f172a;
    --ops-bg-card: #1e293b;
    --ops-bg-input: #334155;
    --ops-bg-hover: #334155;
    
    // Text - DARK (inverted)
    --ops-text-primary: #f1f5f9;
    --ops-text-secondary: #94a3b8;
    --ops-text-disabled: #64748b;
    --ops-text-inverse: #0f172a;
    
    // Borders - DARK
    --ops-border: #334155;
    --ops-border-focus: var(--ops-secondary);
    
    // Shadows - DARK (stronger)
    --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}

// =============================================================================
// SYSTEM PREFERENCE (Auto-detect from OS/Browser)
// =============================================================================
@media (prefers-color-scheme: dark) {
    [data-color-mode="system"] {
        --ops-primary: #475569;
        --ops-secondary: #60a5fa;
        --ops-bg-body: #0f172a;
        --ops-bg-card: #1e293b;
        --ops-bg-input: #334155;
        --ops-bg-hover: #334155;
        --ops-text-primary: #f1f5f9;
        --ops-text-secondary: #94a3b8;
        --ops-text-disabled: #64748b;
        --ops-text-inverse: #0f172a;
        --ops-border: #334155;
        --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
        --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
}
```

### 6. Login Template Pattern (Company-Branded + Dark Mode)
```xml
<!-- Login page respects system color preference before user logs in -->
<template id="login_layout" inherit_id="web.login_layout" name="OPS Login">
    <xpath expr="//html" position="attributes">
        <!-- Default to system preference for login page (user not logged in yet) -->
        <attribute name="data-color-mode">system</attribute>
    </xpath>
    <xpath expr="//div[hasclass('container')]" position="replace">
        <div class="ops-login-container">
            <!-- Left: Company Branding (always uses company primary color) -->
            <div class="ops-login-brand"
                 t-attf-style="background-color: #{request.env.company.ops_primary_color or '#1e293b'}">
                <t t-if="request.env.company.ops_login_show_logo">
                    <img t-att-src="'/web/binary/company_logo?company=%s' % request.env.company.id"
                         class="ops-login-logo" alt="Company Logo"/>
                </t>
                <h1 class="ops-login-tagline"
                    t-esc="request.env.company.ops_login_tagline or 'Welcome'"/>
            </div>
            <!-- Right: Login Form (follows light/dark mode) -->
            <div class="ops-login-form">
                <t t-out="0"/>
            </div>
        </div>
    </xpath>
</template>
```

### 7. Debranding Template Pattern
```xml
<!-- Remove Odoo branding from footer -->
<template id="brand_promotion" inherit_id="web.brand_promotion" name="OPS Debranding">
    <xpath expr="//t[@t-call='web.brand_promotion_message']" position="replace">
        <t t-if="request.env.company.ops_powered_by_visible">
            <span class="ops-powered-by">Powered by OPS Framework</span>
        </t>
    </xpath>
</template>

<!-- Remove Odoo logo from login -->
<template id="login" inherit_id="web.login" name="OPS Login Debrand">
    <xpath expr="//img[contains(@src, 'logo')]" position="replace"/>
</template>
```

### 8. OWL Component Pattern
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OpsChatterToggle extends Component {
    static template = "ops_theme.ChatterToggle";
    
    setup() {
        this.user = useService("user");
        this.rpc = useService("rpc");
        this.state = useState({
            position: 'below',
        });
    }
    
    async togglePosition() {
        const newPosition = this.state.position === 'below' ? 'right' : 'below';
        await this.rpc('/web/dataset/call_kw', {
            model: 'res.users',
            method: 'write',
            args: [[this.user.userId], { ops_chatter_position: newPosition }],
            kwargs: {},
        });
        this.state.position = newPosition;
        window.location.reload();
    }
}

registry.category("user_menuitems").add("ops_chatter_toggle", OpsChatterToggle);
```

### 9. Color Mode Toggle Pattern
```javascript
/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OpsColorModeToggle extends Component {
    static template = "ops_theme.ColorModeToggle";
    
    setup() {
        this.user = useService("user");
        this.rpc = useService("rpc");
        this.state = useState({
            mode: 'system', // light, dark, system
        });
        
        onMounted(() => {
            this.loadUserPreference();
        });
    }
    
    async loadUserPreference() {
        const result = await this.rpc('/web/dataset/call_kw', {
            model: 'res.users',
            method: 'read',
            args: [[this.user.userId], ['ops_color_mode']],
            kwargs: {},
        });
        this.state.mode = result[0]?.ops_color_mode || 'system';
        this.applyMode();
    }
    
    applyMode() {
        document.documentElement.setAttribute('data-color-mode', this.state.mode);
        localStorage.setItem('ops_color_mode', this.state.mode);
    }
    
    async setMode(mode) {
        this.state.mode = mode;
        this.applyMode();
        
        await this.rpc('/web/dataset/call_kw', {
            model: 'res.users',
            method: 'write',
            args: [[this.user.userId], { ops_color_mode: mode }],
            kwargs: {},
        });
    }
    
    get modeIcon() {
        const icons = { light: 'fa-sun-o', dark: 'fa-moon-o', system: 'fa-adjust' };
        return icons[this.state.mode];
    }
}

registry.category("user_menuitems").add("ops_color_mode", OpsColorModeToggle);
```

### 10. Theme Loader (Apply Mode on Page Load)
```javascript
/** @odoo-module **/

// Apply color mode immediately on page load (before render)
// This prevents flash of wrong theme
(function() {
    const savedMode = localStorage.getItem('ops_color_mode') || 'system';
    document.documentElement.setAttribute('data-color-mode', savedMode);
})();
```

---

## File Structure

```
ops_theme/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_company_theme.py      # Company theme settings
│   └── res_users_preferences.py  # User preferences
├── controllers/
│   ├── __init__.py
│   └── theme_controller.py       # Dynamic CSS endpoint
├── static/src/
│   ├── scss/
│   │   ├── _variables.scss       # CSS variable definitions (light/dark)
│   │   ├── _base.scss            # Base styling
│   │   ├── _login.scss           # Split-screen login
│   │   ├── _app_grid.scss        # Home menu grid
│   │   ├── _navbar.scss          # Top navigation
│   │   ├── _menu_tabs.scss       # Horizontal menus
│   │   ├── _breadcrumb.scss      # Enhanced breadcrumb
│   │   ├── _control_panel.scss   # Search/filter bar
│   │   ├── _form.scss            # Form views
│   │   ├── _list.scss            # List views
│   │   ├── _kanban.scss          # Kanban views
│   │   ├── _chatter.scss         # Chatter positioning
│   │   ├── _components.scss      # UI components
│   │   └── theme.scss            # Main entry point
│   ├── js/
│   │   ├── theme_loader.js       # Apply color mode on page load
│   │   ├── color_mode_toggle.js  # Light/Dark/System toggle
│   │   ├── chatter_toggle.js     # Toggle chatter position
│   │   └── app_grid.js           # App grid enhancements
│   └── xml/
│       └── templates.xml         # OWL templates
├── views/
│   ├── res_company_views.xml     # Theme config UI
│   ├── res_users_views.xml       # User preferences
│   ├── login_templates.xml       # Login page
│   └── webclient_templates.xml   # Debranding + assets
├── data/
│   ├── theme_presets.xml         # Preset data
│   └── ir_config_parameter.xml   # System params
└── security/
    └── ir.model.access.csv       # Access rights
```

---

## UI Layout Specifications

### Login Page (Split Screen)
```
┌─────────────────────────────────┬─────────────────────────────────┐
│         LEFT (50%)              │          RIGHT (50%)            │
│     Company Branding            │         Login Form              │
│                                 │                                 │
│     [COMPANY LOGO]              │     Sign In                     │
│                                 │     ┌───────────────────┐       │
│     "Company Tagline"           │     │ Email             │       │
│                                 │     └───────────────────┘       │
│     (Primary color bg           │     ┌───────────────────┐       │
│      or custom image)           │     │ Password          │       │
│                                 │     └───────────────────┘       │
│                                 │     [    Sign In    ]           │
└─────────────────────────────────┴─────────────────────────────────┘
Mobile: Right panel only (left hidden)
```

### App Grid (Home Menu)
```
┌─────────────────────────────────────────────────────────────────┐
│                      🔍 Search Apps...                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  📊     │  │  🛒     │  │  📦     │  │  💰     │           │
│  │ Sales   │  │Purchase │  │Inventory│  │Invoicing│           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│  Cards with shadow, hover lift effect                          │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation Structure
```
┌─────────────────────────────────────────────────────────────────┐
│ ⊞ Grid │ APP NAME │ 🏠 › Section › Record               🔔 👤 ⚙️│
├─────────────────────────────────────────────────────────────────┤
│ Menu Tab 1 │ Menu Tab 2 ▼ │ Menu Tab 3 │       🔍 Search       │
├─────────────────────────────────────────────────────────────────┤
│                         CONTENT                                 │
└─────────────────────────────────────────────────────────────────┘
- Grid button (⊞) returns to app grid
- Menus are horizontal tabs (click to open dropdown)
- Breadcrumb: 🏠 › App › Section › Record (enhanced styling)
```

### Chatter Position (User Toggle)
```
Default (Below):                    Optional (Right):
┌────────────────────────┐          ┌──────────────────┬───────┐
│        FORM            │          │      FORM        │CHATTER│
├────────────────────────┤          │                  │       │
│       CHATTER          │          │                  │       │
└────────────────────────┘          └──────────────────┴───────┘
Toggle in user menu dropdown. Mobile: always below.
```

### User Menu (Top Right)
```
┌─────────────────────────────┐
│  👤 John Doe                │
│  john@company.com           │
├─────────────────────────────┤
│  ☀️ Light    ○ ● ○          │  ← Color Mode: Light/Dark/System
│  💬 Chatter  [Below ▼]      │  ← Chatter Position
├─────────────────────────────┤
│  ⚙️ Preferences             │
│  🚪 Log Out                 │
└─────────────────────────────┘

Color Mode Options:
- Light (☀️): Always light theme
- Dark (🌙): Always dark theme  
- System (◐): Follow OS/browser preference
```

---

## Color Mode Behavior

| Context | Behavior |
|---------|----------|
| **Login Page** | Respects system preference (`prefers-color-scheme`) |
| **After Login** | Uses user's saved preference |
| **Default** | `system` (auto-detect) |
| **Storage** | User DB field + localStorage (for instant load) |

### Color Mode Rules
1. Users always have choice (no company override)
2. Login page respects `prefers-color-scheme` before login
3. Dark mode colors auto-calculated from light colors
4. Brand colors (company primary/secondary) adjust for contrast

---

## Theme Presets

| Preset ID | Name | Primary | Secondary |
|-----------|------|---------|-----------|
| `corporate_blue` | Corporate Blue | `#1e293b` | `#3b82f6` |
| `modern_dark` | Modern Dark | `#0f172a` | `#6366f1` |
| `clean_light` | Clean Light | `#374151` | `#059669` |
| `enterprise_navy` | Enterprise Navy | `#1e3a5f` | `#0ea5e9` |
| `custom` | Custom | (user defined) | (user defined) |

---

## Debranding Checklist

All Odoo branding must be removed:

- [ ] Login page - No Odoo logo
- [ ] Login page - No "Powered by Odoo"
- [ ] Footer - No Odoo references
- [ ] About dialog - Hidden or customized
- [ ] Database manager - Debranded
- [ ] Favicon - Neutral or company
- [ ] Error pages - No Odoo branding
- [ ] No Odoo purple (#714B67) in CSS
- [ ] No odoo.com links

---

## Testing Commands

After making changes:

```bash
# Clear asset cache
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "DELETE FROM ir_attachment WHERE name LIKE '%assets%';"

# Restart Odoo
/odoo-restart

# Update the module
/odoo-update ops_theme

# Check logs for SCSS errors
/odoo-logs --tail 100 | grep -i scss

# Hard refresh browser: Ctrl+Shift+R
```

---

## Git Commit Convention

Use `/ops-commit` with these prefixes:

- `[THEME-FIX]` - Bug fixes
- `[THEME-FEAT]` - New features
- `[THEME-STYLE]` - Pure styling changes
- `[THEME-DEBRAND]` - Debranding changes
- `[THEME-REFACTOR]` - Code refactoring

Example:
```
[THEME-FEAT] Login: Implement split-screen company-branded layout

- Added ops_login_background, ops_login_tagline to res.company
- Created split-screen login template
- Added responsive mobile layout (form only)
- Removed Odoo logo and branding

Closes: Phase 2 Login Page
```

---

## Checklist Before Committing

- [ ] No hardcoded colors (use CSS variables)
- [ ] No Odoo branding text or colors (#714B67)
- [ ] Responsive breakpoints defined
- [ ] Dark mode compatible (variables work in both modes)
- [ ] Company logo uses dynamic path
- [ ] Login tagline is dynamic
- [ ] SCSS imports added to theme.scss
- [ ] Assets registered in __manifest__.py
- [ ] Views registered in __manifest__.py

---

## Quick Reference: CSS Variables

### Light Mode (Default)
```css
/* Brand Colors - from company settings */
--ops-primary: #1e293b;
--ops-secondary: #3b82f6;
--ops-success: #10b981;
--ops-warning: #f59e0b;
--ops-danger: #ef4444;

/* Backgrounds */
--ops-bg-body: #f1f5f9;
--ops-bg-card: #ffffff;

/* Text */
--ops-text-primary: #1e293b;
--ops-text-secondary: #64748b;
--ops-text-inverse: #ffffff;

/* Borders & Shadows */
--ops-border: #e2e8f0;
--ops-shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--ops-shadow-md: 0 4px 6px rgba(0,0,0,0.1);

/* Radius */
--ops-radius-sm: 0.375rem;
--ops-radius-md: 0.5rem;
--ops-radius-lg: 0.75rem;
```

### Dark Mode (Auto-calculated)
```css
/* Brand Colors - adjusted for dark backgrounds */
--ops-primary: #475569;      /* Lighter for visibility */
--ops-secondary: #60a5fa;    /* Brighter for contrast */

/* Backgrounds - inverted */
--ops-bg-body: #0f172a;
--ops-bg-card: #1e293b;

/* Text - inverted */
--ops-text-primary: #f1f5f9;
--ops-text-secondary: #94a3b8;
--ops-text-inverse: #0f172a;

/* Borders & Shadows - adjusted */
--ops-border: #334155;
--ops-shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
--ops-shadow-md: 0 4px 6px rgba(0,0,0,0.4);
```

### Usage (Same Code, Auto-Switches)
```scss
.my-component {
    background: var(--ops-bg-card);     /* White in light, dark slate in dark */
    color: var(--ops-text-primary);      /* Dark in light, light in dark */
    border: 1px solid var(--ops-border); /* Auto-adjusts */
}
```

---

## Subcommands

### `/ops-theme status`
Show current implementation status by phase

### `/ops-theme preview`
Clear asset cache and provide preview instructions

### `/ops-theme lint`
Check SCSS for:
- Hardcoded colors (must use CSS variables)
- Odoo branding references
- Nesting depth (max 4)

### `/ops-theme colors`
Display color palette and variable mapping

### `/ops-theme debrand`
Scan for remaining Odoo branding

### `/ops-theme component <name>`
Scaffold new component:
- `/ops-theme component kpi-card`
- `/ops-theme component status-badge`

---

## Example Usage

```
User: /ops-theme status

Claude Code: Loading OPS Theme context...

OPS Theme Implementation Status
═══════════════════════════════

Phase 1: Foundation
  ▢ Module manifest
  ▢ Company theme fields
  ▢ User preferences
  ▢ Dynamic CSS controller

Phase 2: Login & Navigation  
  ▢ Split-screen login
  ▢ App grid (home menu)
  ▢ Navbar styling
  ▢ Menu tabs
  ▢ Breadcrumb

Phase 3: Views
  ▢ Form views
  ▢ List views
  ▢ Kanban views
  ▢ Chatter toggle

Phase 4: Debranding
  ▢ Remove Odoo branding
  ▢ Replace favicon

Progress: 0/15 (0%)

Which phase would you like to work on?
```

```
User: Let's start with Phase 1

Claude Code: Starting Phase 1: Foundation

I'll create these files:
1. __manifest__.py - Module definition
2. models/res_company_theme.py - Theme settings
3. models/res_users_preferences.py - User prefs
4. controllers/theme_controller.py - Dynamic CSS

Shall I proceed?
```
