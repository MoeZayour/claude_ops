# OPS Theme Comprehensive Enhancement Specification

## Overview

This specification outlines the implementation of 6 major features to enhance OPS Theme with advanced UI/UX capabilities while maintaining its superior branding and corporate identity strengths.

## Target Features

1. **Sidebar/AppsBar** — Collapsible navigation with app icons
2. **Applications Home Screen** — Enhanced grid layout for app selection
3. **Dialog Enhancements** — Fullscreen toggle for all dialogs
4. **Enhanced Chatter** — External/Internal buttons, recipients list
5. **Group Controls** — Expand/Collapse All in list/kanban views
6. **Auto-Refresh** — Configurable view refresh with countdown

## Architecture Principles

- **Single Module Approach**: Keep all features within `ops_theme` module
- **OPS Branding First**: Integrate with existing OPS color system and theme skins
- **Dark Mode Compatible**: All features must work in both light and dark modes
- **User Preferences**: Leverage existing OPS user preference system
- **Settings Integration**: Add controls to existing OPS Settings page

---

## Phase A: Sidebar/AppsBar Implementation

### A.1 Database Schema

**New Fields in `res.users`**:
```python
# In addons/ops_theme/models/res_users_preferences.py
ops_sidebar_type = fields.Selection([
    ('invisible', 'Hidden'),
    ('small', 'Small Icons'),
    ('large', 'Large Icons')
], string='Sidebar Type', default='large')

ops_sidebar_position = fields.Selection([
    ('left', 'Left Side'),
    ('right', 'Right Side')
], string='Sidebar Position', default='left')
```

**New Fields in `res.company`**:
```python
# In addons/ops_theme/models/res_company_branding.py
ops_sidebar_logo = fields.Binary(
    string='Sidebar Footer Logo',
    attachment=True,
    help='Logo displayed at the bottom of the sidebar (recommended: 120x40px)'
)
```

### A.2 JavaScript Components

**File**: `addons/ops_theme/static/src/js/ops_sidebar.js`
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class OpsSidebar extends Component {
    static template = "ops_theme.OpsSidebar";
    static props = {};

    setup() {
        this.menuService = useService("menu");
        this.user = useService("user");
        this.state = useState({
            sidebarType: this.user.context.ops_sidebar_type || 'large',
            collapsed: false
        });
    }

    get apps() {
        return this.menuService.getApps();
    }

    get currentApp() {
        return this.menuService.getCurrentApp();
    }

    toggleSidebar() {
        this.state.collapsed = !this.state.collapsed;
        // Save preference to localStorage
        localStorage.setItem('ops_sidebar_collapsed', this.state.collapsed);
    }

    selectApp(app) {
        this.menuService.selectMenu(app);
    }
}

registry.category("components").add("OpsSidebar", OpsSidebar);
```

**File**: `addons/ops_theme/static/src/js/ops_webclient_patch.js`
```javascript
/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        // Add sidebar to webclient components
    }
});
```

### A.3 Templates

**File**: `addons/ops_theme/static/src/xml/ops_sidebar.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ops_theme.OpsSidebar">
        <div class="ops-sidebar" 
             t-attf-class="ops-sidebar-{{ state.sidebarType }} {{ state.collapsed ? 'collapsed' : '' }}">
            
            <!-- Toggle Button -->
            <div class="ops-sidebar-toggle" t-on-click="toggleSidebar">
                <i class="fa fa-bars"/>
            </div>

            <!-- Apps List -->
            <div class="ops-sidebar-apps">
                <t t-foreach="apps" t-as="app" t-key="app.id">
                    <div class="ops-sidebar-app" 
                         t-attf-class="{{ app.id === currentApp?.id ? 'active' : '' }}"
                         t-on-click="() => this.selectApp(app)"
                         t-att-title="app.name">
                        <img t-if="app.webIconData" 
                             t-att-src="app.webIconData" 
                             class="ops-sidebar-app-icon"/>
                        <i t-else="" class="fa fa-th-large ops-sidebar-app-icon"/>
                        <span class="ops-sidebar-app-name" t-esc="app.name"/>
                    </div>
                </t>
            </div>

            <!-- Footer Logo -->
            <div class="ops-sidebar-footer" t-if="user.activeCompany.ops_sidebar_logo">
                <img t-att-src="'/web/image/res.company/' + user.activeCompany.id + '/ops_sidebar_logo'" 
                     class="ops-sidebar-footer-logo"/>
            </div>
        </div>
    </t>
</templates>
```

### A.4 SCSS Styling

**File**: `addons/ops_theme/static/src/scss/_ops_sidebar.scss`
```scss
// OPS Sidebar — Collapsible App Navigation
// =========================================================================

.ops-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    background: var(--ops-sidebar-bg, #{$ops_color_brand});
    color: var(--ops-sidebar-text, #ffffff);
    transition: width 0.3s ease;
    z-index: 1050;
    display: flex;
    flex-direction: column;

    // Size variants
    &.ops-sidebar-large {
        width: 200px;
        
        .ops-sidebar-app-name {
            display: block;
        }
    }

    &.ops-sidebar-small {
        width: 60px;
        
        .ops-sidebar-app-name {
            display: none;
        }
    }

    &.ops-sidebar-invisible {
        width: 0;
        overflow: hidden;
    }

    &.collapsed {
        width: 60px;
        
        .ops-sidebar-app-name {
            display: none;
        }
    }
}

.ops-sidebar-toggle {
    padding: 1rem;
    text-align: center;
    cursor: pointer;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    &:hover {
        background: rgba(255, 255, 255, 0.1);
    }
}

.ops-sidebar-apps {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 0;
}

.ops-sidebar-app {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: background 0.2s ease;

    &:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    &.active {
        background: rgba(255, 255, 255, 0.2);
        border-right: 3px solid var(--ops-accent, #60a5fa);
    }
}

.ops-sidebar-app-icon {
    width: 24px;
    height: 24px;
    margin-right: 0.75rem;
    flex-shrink: 0;
}

.ops-sidebar-app-name {
    font-size: 0.875rem;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ops-sidebar-footer {
    padding: 1rem;
    text-align: center;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.ops-sidebar-footer-logo {
    max-width: 100%;
    max-height: 40px;
    opacity: 0.8;
}

// Dark mode adjustments
.ops-sidebar.dark.scss {
    background: var(--ops-sidebar-bg-dark, #1e293b);
    
    .ops-sidebar-toggle,
    .ops-sidebar-app {
        &:hover {
            background: rgba(255, 255, 255, 0.05);
        }
    }
    
    .ops-sidebar-app.active {
        background: rgba(255, 255, 255, 0.1);
    }
}

// Responsive adjustments
@media (max-width: 768px) {
    .ops-sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        
        &.mobile-open {
            transform: translateX(0);
        }
    }
}

// Main content adjustment when sidebar is visible
.o_web_client {
    &.has-ops-sidebar-large {
        margin-left: 200px;
    }
    
    &.has-ops-sidebar-small {
        margin-left: 60px;
    }
}
```

---

## Phase B: Applications Home Screen Enhancement

### B.1 JavaScript Components

**File**: `addons/ops_theme/static/src/js/ops_home_menu.js`
```javascript
/** @odoo-module **/

import { HomeMenu } from "@web_enterprise/webclient/home_menu/home_menu";
import { patch } from "@web/core/utils/patch";

patch(HomeMenu.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            viewMode: 'grid', // grid, list, tiles
            searchTerm: '',
            categoryFilter: 'all'
        });
    },

    get filteredApps() {
        let apps = this.menuService.getApps();
        
        // Search filter
        if (this.state.searchTerm) {
            apps = apps.filter(app => 
                app.name.toLowerCase().includes(this.state.searchTerm.toLowerCase())
            );
        }
        
        // Category filter (if categories are defined)
        if (this.state.categoryFilter !== 'all') {
            apps = apps.filter(app => app.category === this.state.categoryFilter);
        }
        
        return apps;
    },

    get appCategories() {
        const categories = new Set();
        this.menuService.getApps().forEach(app => {
            if (app.category) categories.add(app.category);
        });
        return Array.from(categories);
    },

    setViewMode(mode) {
        this.state.viewMode = mode;
        localStorage.setItem('ops_home_view_mode', mode);
    },

    onSearchInput(ev) {
        this.state.searchTerm = ev.target.value;
    },

    onCategoryFilter(category) {
        this.state.categoryFilter = category;
    }
});
```

### B.2 Enhanced Home Menu Template

**File**: `addons/ops_theme/static/src/xml/ops_home_menu.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ops_theme.HomeMenuEnhanced" t-inherit="web_enterprise.HomeMenu" t-inherit-mode="extension">
        
        <!-- Add search and filter controls -->
        <xpath expr="//div[hasclass('o_home_menu')]" position="inside">
            <div class="ops-home-controls">
                
                <!-- Search Bar -->
                <div class="ops-home-search">
                    <input type="text" 
                           class="form-control" 
                           placeholder="Search applications..."
                           t-model="state.searchTerm"
                           t-on-input="onSearchInput"/>
                    <i class="fa fa-search ops-search-icon"/>
                </div>

                <!-- View Mode Toggle -->
                <div class="ops-home-view-toggle">
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ state.viewMode === 'grid' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setViewMode('grid')">
                        <i class="fa fa-th"/>
                    </button>
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ state.viewMode === 'list' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setViewMode('list')">
                        <i class="fa fa-list"/>
                    </button>
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ state.viewMode === 'tiles' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setViewMode('tiles')">
                        <i class="fa fa-th-large"/>
                    </button>
                </div>

                <!-- Category Filter -->
                <div class="ops-home-categories" t-if="appCategories.length">
                    <select class="form-select" t-model="state.categoryFilter" t-on-change="onCategoryFilter">
                        <option value="all">All Categories</option>
                        <t t-foreach="appCategories" t-as="category" t-key="category">
                            <option t-att-value="category" t-esc="category"/>
                        </t>
                    </select>
                </div>
            </div>
        </xpath>

        <!-- Replace app grid with enhanced layout -->
        <xpath expr="//div[hasclass('o_apps')]" position="replace">
            <div class="ops-apps-container" t-attf-class="ops-apps-{{ state.viewMode }}">
                <t t-foreach="filteredApps" t-as="app" t-key="app.id">
                    <div class="ops-app-item" t-on-click="() => this._onAppClick(app)">
                        
                        <!-- App Icon -->
                        <div class="ops-app-icon">
                            <img t-if="app.webIconData" 
                                 t-att-src="app.webIconData" 
                                 t-att-alt="app.name"/>
                            <i t-else="" class="fa fa-th-large"/>
                        </div>

                        <!-- App Info -->
                        <div class="ops-app-info">
                            <h3 class="ops-app-name" t-esc="app.name"/>
                            <p class="ops-app-description" t-if="app.description" t-esc="app.description"/>
                            <span class="ops-app-category" t-if="app.category" t-esc="app.category"/>
                        </div>

                        <!-- Quick Actions (for tiles/list view) -->
                        <div class="ops-app-actions" t-if="state.viewMode !== 'grid'">
                            <button class="btn btn-sm btn-outline-primary">
                                <i class="fa fa-external-link"/>
                            </button>
                        </div>
                    </div>
                </t>
            </div>
        </xpath>
    </t>
</templates>
```

### B.3 Home Menu SCSS

**File**: `addons/ops_theme/static/src/scss/_ops_home_menu.scss`
```scss
// OPS Enhanced Home Menu
// =========================================================================

.ops-home-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: var(--body-bg);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ops-home-search {
    position: relative;
    flex: 1;
    max-width: 400px;

    input {
        padding-right: 2.5rem;
    }

    .ops-search-icon {
        position: absolute;
        right: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-muted);
    }
}

.ops-home-view-toggle {
    display: flex;
    gap: 0.25rem;

    .btn {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
}

.ops-home-categories {
    min-width: 150px;
}

// App Container Layouts
.ops-apps-container {
    &.ops-apps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1.5rem;
        
        .ops-app-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 2rem 1rem;
            background: var(--body-bg);
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;

            &:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            }
        }

        .ops-app-icon {
            width: 64px;
            height: 64px;
            margin-bottom: 1rem;

            img, i {
                width: 100%;
                height: 100%;
                object-fit: contain;
                font-size: 3rem;
                color: var(--primary);
            }
        }

        .ops-app-name {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--headings-color);
        }

        .ops-app-description {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .ops-app-category {
            font-size: 0.75rem;
            color: var(--primary);
            background: rgba(var(--primary-rgb), 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
        }
    }

    &.ops-apps-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;

        .ops-app-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: var(--body-bg);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            cursor: pointer;

            &:hover {
                background: var(--hover-bg);
            }
        }

        .ops-app-icon {
            width: 40px;
            height: 40px;
            margin-right: 1rem;
            flex-shrink: 0;

            img, i {
                width: 100%;
                height: 100%;
                object-fit: contain;
                font-size: 1.5rem;
                color: var(--primary);
            }
        }

        .ops-app-info {
            flex: 1;
        }

        .ops-app-name {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: var(--headings-color);
        }

        .ops-app-description {
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .ops-app-actions {
            margin-left: 1rem;
        }
    }

    &.ops-apps-tiles {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;

        .ops-app-item {
            display: flex;
            align-items: center;
            padding: 1.5rem;
            background: var(--body-bg);
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            cursor: pointer;

            &:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            }
        }

        .ops-app-icon {
            width: 48px;
            height: 48px;
            margin-right: 1rem;
            flex-shrink: 0;

            img, i {
                width: 100%;
                height: 100%;
                object-fit: contain;
                font-size: 2rem;
                color: var(--primary);
            }
        }

        .ops-app-info {
            flex: 1;
        }

        .ops-app-name {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--headings-color);
        }

        .ops-app-description {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        .ops-app-category {
            font-size: 0.75rem;
            color: var(--primary);
            background: rgba(var(--primary-rgb), 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            display: inline-block;
        }
    }
}

// Dark mode adjustments
.ops-apps-container.dark.scss {
    .ops-app-item {
        background: var(--surface-color);
        
        &:hover {
            background: var(--hover-bg);
        }
    }
}

// Responsive adjustments
@media (max-width: 768px) {
    .ops-home-controls {
        flex-direction: column;
        gap: 0.75rem;
        
        .ops-home-search {
            max-width: none;
        }
    }

    .ops-apps-container {
        &.ops-apps-grid {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
        }

        &.ops-apps-tiles {
            grid-template-columns: 1fr;
        }
    }
}
```

---

## Phase C: Dialog Enhancements

### C.1 JavaScript Implementation

**File**: `addons/ops_theme/static/src/js/ops_dialog_patch.js`
```javascript
/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(Dialog.prototype, {
    setup() {
        super.setup();
        this.dialogState = useState({
            isFullscreen: false,
            userPreference: this.env.services.user.context.ops_dialog_size || 'normal'
        });
        
        // Apply user preference on mount
        if (this.dialogState.userPreference === 'fullscreen') {
            this.dialogState.isFullscreen = true;
        }
    },

    toggleFullscreen() {
        this.dialogState.isFullscreen = !this.dialogState.isFullscreen;
        
        // Save preference
        this.env.services.rpc('/web/dataset/call_kw', {
            model: 'res.users',
            method: 'write',
            args: [[this.env.services.user.userId], {
                ops_dialog_size: this.dialogState.isFullscreen ? 'fullscreen' : 'normal'
            }],
            kwargs: {}
        });
    },

    get dialogClass() {
        let classes = super.dialogClass || '';
        if (this.dialogState.isFullscreen) {
            classes += ' ops-dialog-fullscreen';
        }
        return classes;
    }
});
```

### C.2 Dialog Template Extension

**File**: `addons/ops_theme/static/src/xml/ops_dialog.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ops_theme.DialogEnhanced" t-inherit="web.Dialog" t-inherit-mode="extension">
        
        <!-- Add fullscreen toggle button to header -->
        <xpath expr="//header//button[hasclass('btn-close')]" position="before">
            <button type="button" 
                    class="btn btn-sm btn-outline-secondary ops-dialog-fullscreen-btn"
                    t-on-click="toggleFullscreen"
                    t-att-title="dialogState.isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'">
                <i t-attf-class="fa fa-{{ dialogState.isFullscreen ? 'compress' : 'expand' }}"/>
            </button>
        </xpath>
    </t>
</templates>
```

### C.3 Dialog SCSS

**File**: `addons/ops_theme/static/src/scss/_ops_dialog.scss`
```scss
// OPS Dialog Enhancements
// =========================================================================

.ops-dialog-fullscreen-btn {
    margin-right: 0.5rem;
    
    &:hover {
        background: var(--hover-bg);
    }
}

.modal.ops-dialog-fullscreen {
    .modal-dialog {
        max-width: 100vw;
        width: 100vw;
        height: 100vh;
        margin: 0;
        
        .modal-content {
            height: 100vh;
            border-radius: 0;
            
            .modal-body {
                flex: 1;
                overflow: auto;
            }
        }
    }
}

// Smooth transitions
.modal-dialog {
    transition: all 0.3s ease;
}

// Dark mode adjustments
.ops-dialog-fullscreen-btn.dark.scss {
    &:hover {
        background: rgba(255, 255, 255, 0.1);
    }
}
```

---

## Phase D: Enhanced Chatter

### D.1 JavaScript Implementation

**File**: `addons/ops_theme/static/src/js/ops_chatter_patch.js`
```javascript
/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.chatterState = useState({
            showRecipients: false,
            messageType: 'note', // note, comment, email
            isResizable: true,
            width: parseInt(localStorage.getItem('ops_chatter_width')) || 300
        });
    },

    toggleRecipients() {
        this.chatterState.showRecipients = !this.chatterState.showRecipients;
    },

    setMessageType(type) {
        this.chatterState.messageType = type;
    },

    onResizeStart(ev) {
        if (!this.chatterState.isResizable) return;
        
        const startX = ev.clientX;
        const startWidth = this.chatterState.width;
        
        const onMouseMove = (e) => {
            const newWidth = startWidth + (startX - e.clientX);
            this.chatterState.width = Math.max(250, Math.min(600, newWidth));
        };
        
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            localStorage.setItem('ops_chatter_width', this.chatterState.width);
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    },

    get chatterStyle() {
        if (this.props.position === 'side') {
            return `width: ${this.chatterState.width}px;`;
        }
        return '';
    }
});
```

### D.2 Enhanced Chatter Template

**File**: `addons/ops_theme/static/src/xml/ops_chatter.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ops_theme.ChatterEnhanced" t-inherit="mail.Chatter" t-inherit-mode="extension">
        
        <!-- Add message type selector -->
        <xpath expr="//div[hasclass('o-mail-Chatter')]" position="inside">
            <div class="ops-chatter-controls">
                
                <!-- Message Type Buttons -->
                <div class="ops-message-type-selector">
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ chatterState.messageType === 'note' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setMessageType('note')"
                            title="Internal Note">
                        <i class="fa fa-sticky-note"/> Note
                    </button>
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ chatterState.messageType === 'comment' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setMessageType('comment')"
                            title="Internal Comment">
                        <i class="fa fa-comment"/> Comment
                    </button>
                    <button class="btn btn-sm" 
                            t-attf-class="btn-{{ chatterState.messageType === 'email' ? 'primary' : 'outline-secondary' }}"
                            t-on-click="() => this.setMessageType('email')"
                            title="Send Email">
                        <i class="fa fa-envelope"/> Email
                    </button>
                </div>

                <!-- Recipients Toggle -->
                <button class="btn btn-sm btn-outline-secondary ops-recipients-toggle"
                        t-on-click="toggleRecipients"
                        t-if="chatterState.messageType === 'email'">
                    <i class="fa fa-users"/> Recipients
                    <i t-attf-class="fa fa-chevron-{{ chatterState.showRecipients ? 'up' : 'down' }}"/>
                </button>
            </div>

            <!-- Recipients Panel -->
            <div class="ops-recipients-panel" t-if="