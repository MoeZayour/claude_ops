# OPS Theme v3.0 - Complete Development Specification

**Document**: Full Development Guide for Claude Code  
**Version**: 3.0  
**Date**: January 30, 2026  
**Goal**: Enterprise-grade theme surpassing MuK Theme using Odoo 19 native patterns

---

## Executive Summary

Transform OPS Theme from CSS-only styling to a **fully integrated Odoo 19 theme** using native patterns:
- OWL component patches
- Session info integration
- Native dark mode bundle
- SCSS variable overrides
- Proper FormCompiler integration

---

## Current State (v2.0)

| Feature | Status | Issue |
|---------|--------|-------|
| Split-screen login | ✅ Working | None |
| Light mode default | ✅ Working | None |
| Navbar styling | ⚠️ Partial | Still some purple |
| Chatter position | ❌ Broken | CSS-only approach |
| Dark mode toggle | ❌ Broken | Not using native system |
| Settings tabs | ❌ Broken | Purple color |
| Dropdown positioning | ⚠️ Partial | Some menus mispositioned |

---

## Target State (v3.0)

| Feature | Target | Approach |
|---------|--------|----------|
| Chatter position | ✅ Working toggle | FormCompiler patch + session |
| Dark mode | ✅ Native Odoo | web.assets_web_dark bundle |
| Color system | ✅ Deep integration | SCSS $o-brand-* overrides |
| All purple killed | ✅ Complete | Bootstrap variable overrides |
| Theme presets | ✅ 5 presets | Dynamic SCSS generation |
| List refresh | ✅ Auto-refresh | ControlPanel patch |
| Group expand/collapse | ✅ Cog menu | Registry addition |

---

## PHASE 1: Foundation Fixes (2-3 hours)

### Objective
Fix remaining CSS issues before adding JS features.

### Task 1.1: Kill All Purple - Bootstrap Variable Override

Create `/static/src/scss/_bootstrap_overrides.scss`:

```scss
// =============================================================================
// OPS THEME - BOOTSTRAP VARIABLE OVERRIDES
// =============================================================================
// Override Bootstrap's primary color at the source
// =============================================================================

// Override Odoo's brand colors
$o-brand-odoo: #1e293b !default;
$o-brand-primary: #3b82f6 !default;
$o-community-color: #1e293b !default;
$o-enterprise-color: #1e293b !default;
$o-enterprise-action-color: #3b82f6 !default;

// Override Bootstrap primary
$primary: #3b82f6 !default;
$success: #10b981 !default;
$info: #06b6d4 !default;
$warning: #f59e0b !default;
$danger: #ef4444 !default;

// Theme color map
$theme-colors: (
    "primary": $primary,
    "secondary": #64748b,
    "success": $success,
    "info": $info,
    "warning": $warning,
    "danger": $danger,
    "light": #f8fafc,
    "dark": #1e293b,
) !default;
```

### Task 1.2: Register in Primary Variables Bundle

Update `__manifest__.py` assets:

```python
'assets': {
    'web._assets_primary_variables': [
        ('after', 'web/static/src/scss/primary_variables.scss',
         'ops_theme/static/src/scss/_bootstrap_overrides.scss'),
    ],
    # ... rest of assets
}
```

### Task 1.3: Fix Selected Tabs

Add to `_settings.scss`:

```scss
// Settings tabs - override text-bg-primary
.o_setting_container .settings_tab,
div.settings_tab {
    .tab {
        color: #64748b;
        background: transparent;
        padding: 12px 24px;
        border-radius: 6px 6px 0 0;
        transition: all 0.2s ease;
        
        &:hover:not(.selected) {
            background: #f1f5f9;
            color: #1e293b;
        }
        
        &.selected,
        &.selected.text-bg-primary {
            background: #3b82f6 !important;
            color: #ffffff !important;
        }
    }
}

// Override Bootstrap text-bg-primary globally
.text-bg-primary {
    background-color: #3b82f6 !important;
    color: #ffffff !important;
}
```

### Task 1.4: Fix Settings Card Backgrounds

Add to `_settings.scss`:

```scss
// Remove gradient backgrounds from settings cards
.o_setting_box,
div.o_setting_box,
.o_searchable_setting {
    background: #ffffff !important;
    background-image: none !important;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 16px;
}

.app_settings_block,
div.app_settings_block {
    background: transparent !important;
    background-image: none !important;
}

.o_settings_container {
    background: #f8fafc;
}
```

### Task 1.5: Fix Toggle/Radio Buttons

Add to `_forms.scss`:

```scss
// Toggle switches - green when checked
.form-check-input:checked,
.o_boolean_toggle input:checked + label,
input[type="checkbox"]:checked,
input[type="radio"]:checked {
    background-color: #10b981 !important;
    border-color: #10b981 !important;
}

.form-switch .form-check-input:checked {
    background-color: #10b981 !important;
    border-color: #10b981 !important;
}
```

### Verification Phase 1

```bash
# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init

# Check for errors
docker logs gemini_odoo19 --tail 50 | grep -i error

# Restart
docker restart gemini_odoo19
```

**Success Criteria:**
- [ ] No purple (#714B67) visible anywhere
- [ ] Selected tabs are blue (#3b82f6)
- [ ] Settings cards have white background
- [ ] Toggle buttons are green when checked
- [ ] No SCSS compilation errors

---

## PHASE 2: Chatter Position Toggle (3-4 hours)

### Objective
Implement working chatter position toggle using Odoo 19 native patterns.

### Task 2.1: Update res_users.py Model

File: `/models/res_users.py`

```python
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # -------------------------------------------------------------------------
    # SELF_READABLE/WRITEABLE for user preferences
    # -------------------------------------------------------------------------
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'ops_chatter_position',
            'ops_color_mode',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'ops_chatter_position',
            'ops_color_mode',
        ]
    
    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    
    ops_chatter_position = fields.Selection([
        ('side', 'Side'),
        ('bottom', 'Bottom'),
    ], string="Chatter Position", default='bottom', required=True,
       help="Position of the chatter/messaging area on form views")
    
    ops_color_mode = fields.Selection([
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ], string="Color Mode", default='light', required=True,
       help="Color theme preference")
```

### Task 2.2: Create ir_http.py for Session Info

File: `/models/ir_http.py`

```python
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"
    
    def session_info(self):
        """Pass user theme preferences to frontend session."""
        result = super().session_info()
        if self.env.user._is_internal():
            result['chatter_position'] = self.env.user.ops_chatter_position
            result['color_mode'] = self.env.user.ops_color_mode
        return result
```

### Task 2.3: Update models/__init__.py

```python
from . import res_company
from . import res_users
from . import res_config_settings
from . import ir_http
```

### Task 2.4: Create FormCompiler Patch

File: `/static/src/views/form/form_compiler.js`

```javascript
/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { append, setAttributes } from '@web/core/utils/xml';
import { FormCompiler } from '@web/views/form/form_compiler';

patch(FormCompiler.prototype, {
    /**
     * Override compile to handle chatter positioning based on user preference.
     * When chatter_position is 'bottom', move chatter inside the form sheet.
     */
    compile(node, params) {
        const res = super.compile(node, params);
        
        // Find chatter container
        const chatterContainerHookXml = res.querySelector(
            '.o_form_renderer > .o-mail-Form-chatter'
        );
        
        if (!chatterContainerHookXml) {
            return res;
        }
        
        // Set ref for potential JS access
        setAttributes(chatterContainerHookXml, {
            't-ref': 'chatterContainer',
        });
        
        // Handle bottom position
        if (session.chatter_position === 'bottom') {
            const formSheetBgXml = res.querySelector('.o_form_sheet_bg');
            
            if (!formSheetBgXml?.parentNode) {
                return res;
            }
            
            // Get the chatter component
            const chatterContainerXml = chatterContainerHookXml.querySelector(
                "t[t-component='__comp__.mailComponents.Chatter']"
            );
            
            // Clone and modify for bottom position
            const sheetBgChatterContainerHookXml = chatterContainerHookXml.cloneNode(true);
            const sheetBgChatterContainerXml = sheetBgChatterContainerHookXml.querySelector(
                "t[t-component='__comp__.mailComponents.Chatter']"
            );
            
            // Add classes for bottom positioning
            sheetBgChatterContainerHookXml.classList.add('o-isInFormSheetBg', 'w-auto', 'mt-4');
            
            // Append to form sheet
            append(formSheetBgXml, sheetBgChatterContainerHookXml);
            
            // Set attributes for bottom mode
            if (sheetBgChatterContainerXml) {
                setAttributes(sheetBgChatterContainerXml, {
                    isInFormSheetBg: 'true',
                    isChatterAside: 'false',
                });
            }
            
            if (chatterContainerXml) {
                setAttributes(chatterContainerXml, {
                    isInFormSheetBg: 'true',
                    isChatterAside: 'false',
                });
            }
            
            // Hide original chatter container
            setAttributes(chatterContainerHookXml, {
                't-if': 'false',
            });
            
            // Also hide attachment preview if present
            const webClientViewAttachmentViewHookXml = res.querySelector('.o_attachment_preview');
            if (webClientViewAttachmentViewHookXml) {
                setAttributes(webClientViewAttachmentViewHookXml, {
                    't-if': 'false',
                });
            }
        }
        
        return res;
    },
});
```

### Task 2.5: Create User Preferences View

File: `/views/res_users_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add OPS Theme preferences to user form -->
    <record id="res_users_view_form_ops_theme" model="ir.ui.view">
        <field name="name">res.users.form.ops.theme</field>
        <field name="model">res.users</field>
        <field name="inherit_id" ref="base.view_users_form_simple_modif"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='preferences']" position="inside">
                <group string="OPS Theme" name="ops_theme_preferences">
                    <field name="ops_chatter_position" widget="radio" 
                           options="{'horizontal': true}"/>
                    <field name="ops_color_mode" widget="radio"
                           options="{'horizontal': true}"/>
                </group>
            </xpath>
        </field>
    </record>
</odoo>
```

### Task 2.6: Add Chatter Bottom Styling

File: `/static/src/scss/_chatter.scss` (add to existing):

```scss
// =============================================================================
// CHATTER BOTTOM POSITION STYLING
// =============================================================================

// When chatter is in form sheet (bottom position)
.o-isInFormSheetBg {
    width: 100% !important;
    max-width: 100% !important;
    border-top: 1px solid var(--ops-border, #e2e8f0);
    padding-top: 24px;
    margin-top: 24px;
    
    .o-mail-Chatter {
        max-width: 100%;
    }
    
    .o-mail-Thread {
        max-height: 400px;
        overflow-y: auto;
    }
}

// Hide chatter when t-if="false"
.o-mail-Form-chatter[t-if="false"] {
    display: none !important;
}
```

### Task 2.7: Update Manifest Assets

Add to `__manifest__.py`:

```python
'assets': {
    'web.assets_backend': [
        # ... existing files ...
        'ops_theme/static/src/views/form/form_compiler.js',
    ],
},
```

### Verification Phase 2

```bash
# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init

# Check logs
docker logs gemini_odoo19 --tail 100 | grep -i "error\|chatter"

# Restart
docker restart gemini_odoo19
```

**Success Criteria:**
- [ ] User preferences show Chatter Position field
- [ ] Setting to "Bottom" moves chatter below form
- [ ] Setting to "Side" keeps chatter on right
- [ ] Preference persists after logout/login
- [ ] No JS console errors

---

## PHASE 3: Native Dark Mode Integration (2-3 hours)

### Objective
Use Odoo 19's native dark mode system instead of custom implementation.

### Task 3.1: Create Dark Mode SCSS Bundle

File: `/static/src/scss/_dark_mode_native.scss`

```scss
// =============================================================================
// OPS THEME - NATIVE DARK MODE
// =============================================================================
// This file is loaded via web.assets_web_dark bundle
// =============================================================================

// Override Odoo dark mode colors with OPS colors
$o-brand-odoo: #1e293b;
$o-brand-primary: #3b82f6;

// Dark mode specific overrides
:root {
    --ops-bg-body: #0f172a;
    --ops-bg-card: #1e293b;
    --ops-bg-input: #334155;
    --ops-bg-hover: #334155;
    --ops-text-primary: #f1f5f9;
    --ops-text-secondary: #94a3b8;
    --ops-border: #334155;
}

// Navbar in dark mode
.o_main_navbar {
    background: #0f172a !important;
}

// Forms in dark mode
.o_form_view,
.o_form_sheet {
    background: #1e293b !important;
    color: #f1f5f9 !important;
}

// Lists in dark mode
.o_list_view {
    background: #1e293b !important;
    
    th, td {
        color: #f1f5f9 !important;
        border-color: #334155 !important;
    }
}

// Settings in dark mode
.o_settings_container {
    background: #0f172a !important;
}

.o_setting_box {
    background: #1e293b !important;
    border-color: #334155 !important;
}

// Dropdowns in dark mode
.dropdown-menu,
.o-dropdown--menu {
    background: #1e293b !important;
    border-color: #334155 !important;
}

.dropdown-item {
    color: #f1f5f9 !important;
    
    &:hover {
        background: #334155 !important;
    }
}

// Chatter in dark mode
.o-mail-Chatter,
.o_Chatter {
    background: #1e293b !important;
    color: #f1f5f9 !important;
}

.o-mail-Message-body {
    color: #f1f5f9 !important;
}
```

### Task 3.2: Update Manifest for Dark Mode Bundle

```python
'assets': {
    'web._assets_primary_variables': [
        ('after', 'web/static/src/scss/primary_variables.scss',
         'ops_theme/static/src/scss/_bootstrap_overrides.scss'),
    ],
    'web.assets_web_dark': [
        'ops_theme/static/src/scss/_dark_mode_native.scss',
    ],
    'web.assets_backend': [
        # ... existing backend assets ...
    ],
},
```

### Task 3.3: Remove Custom Dark Mode JS

Remove or disable the custom dark mode toggle JS since Odoo handles it natively.

Update `/static/src/js/theme_loader.js`:

```javascript
/** @odoo-module **/

/**
 * OPS Theme Loader
 * 
 * Handles initial theme setup. Dark mode is handled natively by Odoo 19.
 * This file handles other OPS-specific initializations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Replace favicon
    const favicon = document.querySelector('link[rel="icon"]') || 
                    document.querySelector('link[rel="shortcut icon"]');
    if (favicon) {
        favicon.href = '/ops_theme/static/src/img/favicon.ico';
    }
    
    // Update page title (remove "Odoo")
    if (document.title.includes('Odoo')) {
        document.title = document.title.replace(/Odoo\s*[-–]\s*/gi, '');
    }
});
```

### Verification Phase 3

```bash
# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init
docker restart gemini_odoo19
```

**Success Criteria:**
- [ ] Odoo's native dark mode toggle works
- [ ] Dark mode applies OPS colors (not Odoo purple)
- [ ] All views render correctly in dark mode
- [ ] Light mode is default
- [ ] No flash of wrong theme on load

---

## PHASE 4: Enhanced Features (3-4 hours)

### Objective
Add productivity features that surpass MuK Theme.

### Task 4.1: List Auto-Refresh Feature

File: `/static/src/search/control_panel_refresh.js`

```javascript
/** @odoo-module **/

import { useState, useEffect, onWillStart } from '@odoo/owl';
import { browser } from '@web/core/browser/browser';
import { patch } from '@web/core/utils/patch';
import { session } from '@web/session';
import { ControlPanel } from '@web/search/control_panel/control_panel';

patch(ControlPanel.prototype, {
    setup() {
        super.setup(...arguments);
        
        this.autoRefreshState = useState({
            active: false,
            counter: 0,
            interval: 30, // seconds
        });
        
        onWillStart(() => {
            if (this._checkAutoRefreshAvailable() && this._getStoredAutoRefresh()) {
                this.autoRefreshState.active = true;
            }
        });
        
        useEffect(
            () => {
                if (!this.autoRefreshState.active) {
                    return;
                }
                
                this.autoRefreshState.counter = this.autoRefreshState.interval;
                
                const intervalId = browser.setInterval(() => {
                    this.autoRefreshState.counter--;
                    
                    if (this.autoRefreshState.counter <= 0) {
                        this.autoRefreshState.counter = this.autoRefreshState.interval;
                        this._triggerRefresh();
                    }
                }, 1000);
                
                return () => browser.clearInterval(intervalId);
            },
            () => [this.autoRefreshState.active]
        );
    },
    
    _checkAutoRefreshAvailable() {
        return ['kanban', 'list'].includes(this.env.config?.viewType);
    },
    
    _getStorageKey() {
        const keys = [
            this.env.config?.actionId ?? '',
            this.env.config?.viewType ?? '',
        ];
        return `ops_auto_refresh:${keys.join(',')}`;
    },
    
    _getStoredAutoRefresh() {
        return browser.localStorage.getItem(this._getStorageKey()) === 'true';
    },
    
    _setStoredAutoRefresh(value) {
        if (value) {
            browser.localStorage.setItem(this._getStorageKey(), 'true');
        } else {
            browser.localStorage.removeItem(this._getStorageKey());
        }
    },
    
    _triggerRefresh() {
        if (this.pagerProps?.onUpdate) {
            this.pagerProps.onUpdate({
                offset: this.pagerProps.offset,
                limit: this.pagerProps.limit,
            });
        } else if (this.env.searchModel?.search) {
            this.env.searchModel.search();
        }
    },
    
    toggleAutoRefresh() {
        this.autoRefreshState.active = !this.autoRefreshState.active;
        this._setStoredAutoRefresh(this.autoRefreshState.active);
    },
});
```

### Task 4.2: Expand/Collapse All Groups

File: `/static/src/search/group_actions.js`

```javascript
/** @odoo-module **/

import { Component } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { DropdownItem } from '@web/core/dropdown/dropdown_item';

const cogMenuRegistry = registry.category('cogMenu');

// Expand All Groups
export class ExpandAllGroups extends Component {
    static template = 'ops_theme.ExpandAllGroups';
    static components = { DropdownItem };
    static props = {};
    
    async onClick() {
        let groups = this.env.model.root.groups;
        
        while (groups && groups.length) {
            const foldedGroups = groups.filter(g => g._config?.isFolded);
            
            for (const group of foldedGroups) {
                await group.toggle();
            }
            
            const subGroups = foldedGroups
                .map(g => g.list?.groups || [])
                .flat();
            
            groups = subGroups;
        }
        
        await this.env.model.root.load();
        this.env.model.notify();
    }
}

cogMenuRegistry.add('ops-expand-all', {
    Component: ExpandAllGroups,
    groupNumber: 15,
    isDisplayed: (env) => (
        ['kanban', 'list'].includes(env.config?.viewType) &&
        env.model?.root?.isGrouped
    ),
}, { sequence: 1 });

// Collapse All Groups
export class CollapseAllGroups extends Component {
    static template = 'ops_theme.CollapseAllGroups';
    static components = { DropdownItem };
    static props = {};
    
    async onClick() {
        const groups = this.env.model.root.groups || [];
        
        for (const group of groups) {
            if (!group._config?.isFolded) {
                await group.toggle();
            }
        }
        
        this.env.model.notify();
    }
}

cogMenuRegistry.add('ops-collapse-all', {
    Component: CollapseAllGroups,
    groupNumber: 15,
    isDisplayed: (env) => (
        ['kanban', 'list'].includes(env.config?.viewType) &&
        env.model?.root?.isGrouped
    ),
}, { sequence: 2 });
```

### Task 4.3: OWL Templates for New Features

File: `/static/src/xml/control_panel.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    
    <!-- Auto-refresh toggle button -->
    <t t-name="ops_theme.AutoRefreshButton">
        <button t-if="_checkAutoRefreshAvailable()" 
                class="btn btn-secondary btn-sm ms-2"
                t-att-class="{'btn-success': autoRefreshState.active}"
                t-on-click="toggleAutoRefresh"
                title="Auto-refresh">
            <i class="fa fa-refresh"/>
            <t t-if="autoRefreshState.active">
                <span class="ms-1" t-esc="autoRefreshState.counter"/>s
            </t>
        </button>
    </t>
    
    <!-- Expand All menu item -->
    <t t-name="ops_theme.ExpandAllGroups">
        <DropdownItem onSelected.bind="onClick">
            <i class="fa fa-expand me-2"/>
            Expand All
        </DropdownItem>
    </t>
    
    <!-- Collapse All menu item -->
    <t t-name="ops_theme.CollapseAllGroups">
        <DropdownItem onSelected.bind="onClick">
            <i class="fa fa-compress me-2"/>
            Collapse All
        </DropdownItem>
    </t>
    
</templates>
```

### Verification Phase 4

```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init
docker restart gemini_odoo19
```

**Success Criteria:**
- [ ] Auto-refresh button visible in list/kanban views
- [ ] Clicking toggle starts/stops countdown
- [ ] List refreshes when counter reaches 0
- [ ] Expand All visible in cog menu when grouped
- [ ] Collapse All visible in cog menu when grouped
- [ ] Both expand/collapse work correctly

---

## PHASE 5: Theme Configuration UI (2-3 hours)

### Objective
Complete the Settings UI for theme configuration.

### Task 5.1: Update res_config_settings.py

File: `/models/res_config_settings.py`

```python
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # -------------------------------------------------------------------------
    # Theme Configuration
    # -------------------------------------------------------------------------
    
    ops_theme_preset = fields.Selection(
        related='company_id.ops_theme_preset',
        readonly=False,
    )
    
    ops_primary_color = fields.Char(
        related='company_id.ops_primary_color',
        readonly=False,
    )
    
    ops_secondary_color = fields.Char(
        related='company_id.ops_secondary_color',
        readonly=False,
    )
    
    ops_login_background = fields.Binary(
        related='company_id.ops_login_background',
        readonly=False,
    )
    
    ops_login_tagline = fields.Char(
        related='company_id.ops_login_tagline',
        readonly=False,
    )
    
    ops_powered_by_visible = fields.Boolean(
        related='company_id.ops_powered_by_visible',
        readonly=False,
    )
```

### Task 5.2: Update res_company.py

File: `/models/res_company.py`

```python
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # -------------------------------------------------------------------------
    # Theme Preset
    # -------------------------------------------------------------------------
    
    ops_theme_preset = fields.Selection([
        ('corporate_blue', 'Corporate Blue'),
        ('modern_dark', 'Modern Dark'),
        ('clean_light', 'Clean Light'),
        ('enterprise_navy', 'Enterprise Navy'),
        ('custom', 'Custom'),
    ], string='Theme Preset', default='corporate_blue')
    
    # -------------------------------------------------------------------------
    # Custom Colors
    # -------------------------------------------------------------------------
    
    ops_primary_color = fields.Char(
        string='Primary Color',
        default='#1e293b',
        help='Main brand color (navbar, headers)'
    )
    
    ops_secondary_color = fields.Char(
        string='Secondary Color',
        default='#3b82f6',
        help='Accent color (buttons, links)'
    )
    
    # -------------------------------------------------------------------------
    # Login Page
    # -------------------------------------------------------------------------
    
    ops_login_background = fields.Binary(
        string='Login Background Image',
        help='Custom background for the login page brand panel'
    )
    
    ops_login_tagline = fields.Char(
        string='Login Tagline',
        default='Enterprise Resource Planning',
        help='Tagline shown on the login page'
    )
    
    # -------------------------------------------------------------------------
    # Branding
    # -------------------------------------------------------------------------
    
    ops_powered_by_visible = fields.Boolean(
        string='Show "Powered by OPS Framework"',
        default=True,
    )
    
    # -------------------------------------------------------------------------
    # Computed/Logic
    # -------------------------------------------------------------------------
    
    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        """Apply preset colors when preset changes."""
        presets = {
            'corporate_blue': ('#1e293b', '#3b82f6'),
            'modern_dark': ('#0f172a', '#6366f1'),
            'clean_light': ('#374151', '#059669'),
            'enterprise_navy': ('#1e3a5f', '#0ea5e9'),
        }
        if self.ops_theme_preset in presets:
            self.ops_primary_color, self.ops_secondary_color = presets[self.ops_theme_preset]
```

### Task 5.3: Settings View XML

File: `/views/res_config_settings_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="res_config_settings_view_form_ops_theme" model="ir.ui.view">
        <field name="name">res.config.settings.view.form.ops.theme</field>
        <field name="model">res.config.settings</field>
        <field name="inherit_id" ref="base.res_config_settings_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//form" position="inside">
                <app data-string="Theme" string="Theme" name="ops_theme">
                    <block title="Theme Configuration" name="ops_theme_config">
                        <setting string="Theme Preset" 
                                 help="Select a predefined color scheme or choose Custom">
                            <field name="ops_theme_preset" widget="selection"/>
                        </setting>
                    </block>
                    
                    <block title="Brand Colors" name="ops_brand_colors"
                           attrs="{'invisible': [('ops_theme_preset', '!=', 'custom')]}">
                        <setting string="Primary Color"
                                 help="Main brand color for navbar and headers">
                            <field name="ops_primary_color" widget="color"/>
                        </setting>
                        <setting string="Secondary Color"
                                 help="Accent color for buttons and links">
                            <field name="ops_secondary_color" widget="color"/>
                        </setting>
                    </block>
                    
                    <block title="Login Page" name="ops_login_config">
                        <setting string="Login Tagline"
                                 help="Text shown below company name on login">
                            <field name="ops_login_tagline"/>
                        </setting>
                        <setting string="Login Background"
                                 help="Custom background image for login page">
                            <field name="ops_login_background" widget="image"/>
                        </setting>
                    </block>
                    
                    <block title="Branding" name="ops_branding">
                        <setting string="Show OPS Attribution"
                                 help="Show 'Powered by OPS Framework' in footer">
                            <field name="ops_powered_by_visible"/>
                        </setting>
                    </block>
                </app>
            </xpath>
        </field>
    </record>
</odoo>
```

### Verification Phase 5

```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init
docker restart gemini_odoo19
```

**Success Criteria:**
- [ ] Theme tab appears in Settings
- [ ] Theme preset dropdown works
- [ ] Custom colors visible when "Custom" selected
- [ ] Login tagline field saves
- [ ] Settings persist after save

---

## PHASE 6: Final Polish & Testing (2-3 hours)

### Objective
Complete testing, documentation, and final refinements.

### Task 6.1: Update Module Manifest

File: `__manifest__.py` (complete version)

```python
{
    'name': 'OPS Theme',
    'version': '19.0.3.0.0',
    'category': 'Themes/Backend',
    'summary': 'Enterprise white-label theme with advanced features',
    'description': '''
        OPS Theme v3.0 - Enterprise UI Framework
        =========================================
        
        Features:
        * Split-screen login with company branding
        * Light/Dark mode (native Odoo integration)
        * Chatter position toggle (side/bottom)
        * Complete Odoo debranding
        * Theme presets and custom colors
        * List auto-refresh
        * Expand/Collapse all groups
        * Bootstrap variable overrides
        
        Developed for OPS Matrix Framework.
    ''',
    'author': 'OPS Framework',
    'website': 'https://ops-framework.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/login_templates.xml',
        'views/webclient_templates.xml',
        'views/debranding_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss',
             'ops_theme/static/src/scss/_bootstrap_overrides.scss'),
        ],
        'web.assets_web_dark': [
            'ops_theme/static/src/scss/_dark_mode_native.scss',
        ],
        'web.assets_backend': [
            'ops_theme/static/src/scss/_variables.scss',
            'ops_theme/static/src/scss/_base.scss',
            'ops_theme/static/src/scss/_navbar.scss',
            'ops_theme/static/src/scss/_buttons.scss',
            'ops_theme/static/src/scss/_cards.scss',
            'ops_theme/static/src/scss/_forms.scss',
            'ops_theme/static/src/scss/_lists.scss',
            'ops_theme/static/src/scss/_kanban.scss',
            'ops_theme/static/src/scss/_chatter.scss',
            'ops_theme/static/src/scss/_dropdowns.scss',
            'ops_theme/static/src/scss/_badges.scss',
            'ops_theme/static/src/scss/_settings.scss',
            'ops_theme/static/src/scss/_control_panel.scss',
            'ops_theme/static/src/scss/_debranding.scss',
            'ops_theme/static/src/scss/_interactions.scss',
            'ops_theme/static/src/scss/_animations.scss',
            'ops_theme/static/src/js/theme_loader.js',
            'ops_theme/static/src/views/form/form_compiler.js',
            'ops_theme/static/src/search/control_panel_refresh.js',
            'ops_theme/static/src/search/group_actions.js',
            'ops_theme/static/src/xml/control_panel.xml',
        ],
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_variables.scss',
            'ops_theme/static/src/scss/_login.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### Task 6.2: Security File

File: `/security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

### Task 6.3: Full Test Checklist

Run all tests manually:

```bash
# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_theme --stop-after-init

# Check for Python errors
docker logs gemini_odoo19 --tail 100 | grep -i "error\|traceback"

# Check for JS errors (in browser console)
# Check for SCSS errors
docker logs gemini_odoo19 --tail 100 | grep -i "scss\|sass"

# Restart
docker restart gemini_odoo19
```

### Task 6.4: Git Commit

```bash
cd /opt/gemini_odoo19

git add addons/ops_theme/

git commit -m "[THEME-RELEASE] OPS Theme v3.0 - Enterprise UI Framework

Major Features:
- Chatter position toggle (side/bottom) via FormCompiler patch
- Native Odoo 19 dark mode integration
- Bootstrap variable overrides for complete debranding
- List auto-refresh feature
- Expand/Collapse all groups in cog menu
- Theme presets with custom color support
- Complete Settings UI

Technical Improvements:
- Uses Odoo 19 native patterns (patch, session, OWL)
- Proper web.assets_web_dark bundle
- web._assets_primary_variables override
- No layout-breaking CSS

Tested on Odoo 19 CE."

git push origin main
```

---

## Complete File Structure (v3.0)

```
ops_theme/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_company.py
│   ├── res_users.py
│   ├── res_config_settings.py
│   └── ir_http.py
├── views/
│   ├── res_config_settings_views.xml
│   ├── res_users_views.xml
│   ├── login_templates.xml
│   ├── webclient_templates.xml
│   └── debranding_templates.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── banner.png
│   └── src/
│       ├── scss/
│       │   ├── _bootstrap_overrides.scss  # NEW
│       │   ├── _variables.scss
│       │   ├── _base.scss
│       │   ├── _navbar.scss
│       │   ├── _buttons.scss
│       │   ├── _cards.scss
│       │   ├── _forms.scss
│       │   ├── _lists.scss
│       │   ├── _kanban.scss
│       │   ├── _chatter.scss
│       │   ├── _dropdowns.scss
│       │   ├── _badges.scss
│       │   ├── _settings.scss
│       │   ├── _control_panel.scss
│       │   ├── _debranding.scss
│       │   ├── _interactions.scss
│       │   ├── _animations.scss
│       │   ├── _login.scss
│       │   └── _dark_mode_native.scss  # NEW
│       ├── js/
│       │   └── theme_loader.js
│       ├── views/
│       │   └── form/
│       │       └── form_compiler.js  # NEW
│       ├── search/
│       │   ├── control_panel_refresh.js  # NEW
│       │   └── group_actions.js  # NEW
│       ├── xml/
│       │   └── control_panel.xml  # NEW
│       └── img/
│           ├── favicon.ico
│           └── ops_logo.svg
└── data/
    └── (optional theme presets)
```

---

## Success Criteria Summary

| Phase | Criteria |
|-------|----------|
| **Phase 1** | No purple visible, tabs blue, toggles green |
| **Phase 2** | Chatter position toggle works |
| **Phase 3** | Native dark mode works |
| **Phase 4** | Auto-refresh and group expand/collapse work |
| **Phase 5** | Settings UI complete and functional |
| **Phase 6** | All tests pass, committed to git |

---

## Timeline Estimate

| Phase | Duration |
|-------|----------|
| Phase 1: Foundation Fixes | 2-3 hours |
| Phase 2: Chatter Position | 3-4 hours |
| Phase 3: Native Dark Mode | 2-3 hours |
| Phase 4: Enhanced Features | 3-4 hours |
| Phase 5: Theme Config UI | 2-3 hours |
| Phase 6: Polish & Testing | 2-3 hours |
| **Total** | **14-20 hours** |

---

**Document Version**: 1.0  
**Last Updated**: January 30, 2026  
**Author**: OPS Framework Team
