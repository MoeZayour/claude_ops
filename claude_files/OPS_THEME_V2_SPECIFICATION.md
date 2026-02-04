# OPS Theme v2.0 - Implementation Specification

**Document Type**: Technical Specification for Claude Code Agent  
**Version**: 2.0  
**Date**: January 30, 2026  
**Status**: READY FOR IMPLEMENTATION

---

## Executive Summary

Create an **original** OPS Theme for Odoo 19 CE inspired by modern SaaS UI/UX patterns (as analyzed from Gilded Admin reference). This is NOT a copy - we implement our own CSS, JS, and assets following Gilded's UX principles.

### Design Philosophy
- **Micro-interactions everywhere** - Every click, hover, transition feels alive
- **Depth through shadows** - Floating cards, layered UI
- **Smooth transitions** - Nothing snaps, everything flows
- **Dark mode first-class** - Not an afterthought
- **White-label ready** - Company branding from day one

---

## Module Structure

```
/opt/gemini_odoo19/addons/ops_theme/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_company.py          # Company theme settings
│   ├── res_users.py            # User preferences
│   └── res_config_settings.py  # Settings UI
├── controllers/
│   ├── __init__.py
│   └── theme_controller.py     # Dynamic CSS endpoint
├── static/
│   └── src/
│       ├── scss/
│       │   ├── _variables.scss         # CSS variables (light/dark)
│       │   ├── _base.scss              # Typography, reset
│       │   ├── _interactions.scss      # Ripples, hovers, transitions
│       │   ├── _animations.scss        # Keyframes, entrance effects
│       │   ├── _loader.scss            # Page loader
│       │   ├── _login.scss             # Split-screen login
│       │   ├── _navbar.scss            # Top navigation
│       │   ├── _sidebar.scss           # App drawer (if needed)
│       │   ├── _cards.scss             # Card components
│       │   ├── _forms.scss             # Form styling
│       │   ├── _buttons.scss           # Button variants
│       │   ├── _lists.scss             # List/tree views
│       │   ├── _kanban.scss            # Kanban view
│       │   ├── _chatter.scss           # Chatter position
│       │   ├── _dropdowns.scss         # Animated dropdowns
│       │   ├── _badges.scss            # Status badges
│       │   ├── _dark_mode.scss         # Dark mode overrides
│       │   ├── _debranding.scss        # Remove Odoo branding
│       │   └── theme.scss              # Main entry (imports all)
│       ├── js/
│       │   ├── theme_loader.js         # Initial theme application
│       │   ├── dark_mode_toggle.js     # Light/Dark/System toggle
│       │   ├── interactions.js         # Ripple effects, animations
│       │   ├── page_loader.js          # Loading spinner control
│       │   └── chatter_toggle.js       # Chatter position preference
│       ├── xml/
│       │   └── templates.xml           # OWL component templates
│       └── img/
│           ├── ops_logo_light.svg      # Logo for dark backgrounds
│           ├── ops_logo_dark.svg       # Logo for light backgrounds
│           ├── favicon.ico             # Neutral favicon
│           └── login_bg.svg            # Abstract login background
├── views/
│   ├── res_config_settings_views.xml   # Theme settings in General Settings
│   ├── res_company_views.xml           # Company theme tab
│   ├── res_users_views.xml             # User display preferences
│   ├── login_templates.xml             # Split-screen login override
│   ├── webclient_templates.xml         # Layout modifications
│   └── debranding_templates.xml        # Remove Odoo branding
├── security/
│   └── ir.model.access.csv
└── data/
    └── theme_presets.xml               # Default color presets
```

---

## Phase 1: Foundation & Variables

### 1.1 __manifest__.py

```python
{
    'name': 'OPS Theme',
    'version': '19.0.2.0.0',
    'category': 'Themes/Backend',
    'summary': 'Enterprise white-label theme with micro-interactions',
    'description': """
        OPS Theme - Modern Enterprise UI
        ================================
        * Split-screen login with company branding
        * Light/Dark/System color modes
        * Micro-interactions (ripples, transitions, animations)
        * Complete Odoo debranding
        * Company-configurable colors
        * Chatter position toggle
    """,
    'author': 'OPS Framework',
    'website': 'https://ops-framework.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/theme_presets.xml',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/res_users_views.xml',
        'views/login_templates.xml',
        'views/webclient_templates.xml',
        'views/debranding_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # SCSS files
            'ops_theme/static/src/scss/_variables.scss',
            'ops_theme/static/src/scss/_base.scss',
            'ops_theme/static/src/scss/_interactions.scss',
            'ops_theme/static/src/scss/_animations.scss',
            'ops_theme/static/src/scss/_loader.scss',
            'ops_theme/static/src/scss/_navbar.scss',
            'ops_theme/static/src/scss/_cards.scss',
            'ops_theme/static/src/scss/_forms.scss',
            'ops_theme/static/src/scss/_buttons.scss',
            'ops_theme/static/src/scss/_lists.scss',
            'ops_theme/static/src/scss/_kanban.scss',
            'ops_theme/static/src/scss/_chatter.scss',
            'ops_theme/static/src/scss/_dropdowns.scss',
            'ops_theme/static/src/scss/_badges.scss',
            'ops_theme/static/src/scss/_dark_mode.scss',
            'ops_theme/static/src/scss/_debranding.scss',
            # JS files
            'ops_theme/static/src/js/theme_loader.js',
            'ops_theme/static/src/js/dark_mode_toggle.js',
            'ops_theme/static/src/js/interactions.js',
            'ops_theme/static/src/js/page_loader.js',
        ],
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_variables.scss',
            'ops_theme/static/src/scss/_login.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### 1.2 _variables.scss - CSS Custom Properties

```scss
// =============================================================================
// OPS THEME - CSS VARIABLES
// =============================================================================
// Design System: Light mode default, dark mode via .dark-skin class
// All colors use CSS custom properties for runtime theming
// =============================================================================

:root {
    // -------------------------------------------------------------------------
    // BRAND COLORS (Company-configurable via Settings)
    // -------------------------------------------------------------------------
    --ops-primary: #1e293b;           // Deep slate - headers, navbar
    --ops-secondary: #3b82f6;         // Blue - buttons, links, accents
    --ops-secondary-hover: #2563eb;   // Blue darker - hover states
    --ops-secondary-rgb: 59, 130, 246; // For rgba() usage
    
    // -------------------------------------------------------------------------
    // SEMANTIC COLORS
    // -------------------------------------------------------------------------
    --ops-success: #10b981;           // Green - positive states
    --ops-warning: #f59e0b;           // Amber - warnings
    --ops-danger: #ef4444;            // Red - errors, destructive
    --ops-info: #06b6d4;              // Cyan - informational
    
    // -------------------------------------------------------------------------
    // LIGHT MODE SURFACES
    // -------------------------------------------------------------------------
    --ops-bg-body: #f1f5f9;           // Page background (slate-100)
    --ops-bg-card: #ffffff;           // Card/panel background
    --ops-bg-input: #ffffff;          // Input background
    --ops-bg-hover: #f8fafc;          // Hover state background
    --ops-bg-selected: #eff6ff;       // Selected row (blue tint)
    
    // -------------------------------------------------------------------------
    // LIGHT MODE TEXT
    // -------------------------------------------------------------------------
    --ops-text-primary: #1e293b;      // Primary text (slate-800)
    --ops-text-secondary: #64748b;    // Secondary text (slate-500)
    --ops-text-disabled: #94a3b8;     // Disabled text (slate-400)
    --ops-text-inverse: #ffffff;      // Text on dark backgrounds
    
    // -------------------------------------------------------------------------
    // BORDERS & DIVIDERS
    // -------------------------------------------------------------------------
    --ops-border: #e2e8f0;            // Default border (slate-200)
    --ops-border-focus: #3b82f6;      // Focus state border
    --ops-divider: #f1f5f9;           // Subtle divider
    
    // -------------------------------------------------------------------------
    // SHADOWS (Depth System)
    // -------------------------------------------------------------------------
    --ops-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                     0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
                     0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --ops-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
                     0 10px 10px -5px rgba(0, 0, 0, 0.04);
    
    // -------------------------------------------------------------------------
    // BORDER RADIUS
    // -------------------------------------------------------------------------
    --ops-radius-sm: 4px;
    --ops-radius-md: 8px;
    --ops-radius-lg: 12px;
    --ops-radius-xl: 16px;
    --ops-radius-full: 9999px;
    
    // -------------------------------------------------------------------------
    // TRANSITIONS (Smooth by default)
    // -------------------------------------------------------------------------
    --ops-transition-fast: 150ms ease;
    --ops-transition-base: 200ms ease;
    --ops-transition-slow: 300ms ease;
    
    // -------------------------------------------------------------------------
    // TYPOGRAPHY
    // -------------------------------------------------------------------------
    --ops-font-family: 'Inter', -apple-system, BlinkMacSystemFont, 
                       'Segoe UI', Roboto, sans-serif;
    --ops-font-size-xs: 0.75rem;      // 12px
    --ops-font-size-sm: 0.875rem;     // 14px
    --ops-font-size-base: 1rem;       // 16px
    --ops-font-size-lg: 1.125rem;     // 18px
    --ops-font-size-xl: 1.25rem;      // 20px
    
    // -------------------------------------------------------------------------
    // Z-INDEX SCALE
    // -------------------------------------------------------------------------
    --ops-z-dropdown: 1000;
    --ops-z-sticky: 1020;
    --ops-z-fixed: 1030;
    --ops-z-modal-backdrop: 1040;
    --ops-z-modal: 1050;
    --ops-z-popover: 1060;
    --ops-z-tooltip: 1070;
    --ops-z-loader: 9999;
}

// =============================================================================
// DARK MODE OVERRIDES
// =============================================================================
// Applied when body has .dark-skin class
// =============================================================================

.dark-skin {
    // Surfaces
    --ops-bg-body: #0f172a;           // Slate-900
    --ops-bg-card: #1e293b;           // Slate-800
    --ops-bg-input: #334155;          // Slate-700
    --ops-bg-hover: #334155;          // Slate-700
    --ops-bg-selected: #1e3a5f;       // Blue tint dark
    
    // Text
    --ops-text-primary: #f1f5f9;      // Slate-100
    --ops-text-secondary: #94a3b8;    // Slate-400
    --ops-text-disabled: #64748b;     // Slate-500
    
    // Borders
    --ops-border: #334155;            // Slate-700
    --ops-divider: #1e293b;           // Slate-800
    
    // Shadows (more pronounced in dark mode)
    --ops-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 
                     0 2px 4px -1px rgba(0, 0, 0, 0.2);
    --ops-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 
                     0 4px 6px -2px rgba(0, 0, 0, 0.2);
}
```

### 1.3 _base.scss - Typography & Reset

```scss
// =============================================================================
// OPS THEME - BASE STYLES
// =============================================================================

// Import Inter font (open source, similar to Gilded's Poppins)
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

// Global box-sizing
*, *::before, *::after {
    box-sizing: border-box;
}

// Body defaults
body {
    font-family: var(--ops-font-family);
    font-size: var(--ops-font-size-sm);
    color: var(--ops-text-primary);
    background-color: var(--ops-bg-body);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

// Universal transitions (makes everything smooth)
.o_web_client {
    * {
        transition: background-color var(--ops-transition-base),
                    color var(--ops-transition-base),
                    border-color var(--ops-transition-base),
                    box-shadow var(--ops-transition-base),
                    opacity var(--ops-transition-base);
    }
}

// Headings
h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6 {
    font-weight: 600;
    color: var(--ops-text-primary);
    margin-bottom: 0.5rem;
}

// Links
a {
    color: var(--ops-secondary);
    text-decoration: none;
    transition: color var(--ops-transition-fast);
    
    &:hover {
        color: var(--ops-secondary-hover);
    }
}

// Selection color
::selection {
    background-color: rgba(var(--ops-secondary-rgb), 0.2);
    color: var(--ops-text-primary);
}

// Scrollbar styling
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--ops-bg-body);
}

::-webkit-scrollbar-thumb {
    background: var(--ops-border);
    border-radius: var(--ops-radius-full);
    
    &:hover {
        background: var(--ops-text-disabled);
    }
}

// Focus visible (accessibility)
:focus-visible {
    outline: 2px solid var(--ops-secondary);
    outline-offset: 2px;
}
```

---

## Phase 2: Micro-Interactions

### 2.1 _interactions.scss - Ripple Effects & Hovers

```scss
// =============================================================================
// OPS THEME - MICRO-INTERACTIONS
// =============================================================================
// Makes the UI feel alive and responsive
// =============================================================================

// -----------------------------------------------------------------------------
// RIPPLE EFFECT (Material Design inspired)
// -----------------------------------------------------------------------------
// Usage: Add .ops-ripple class to any clickable element

.ops-ripple {
    position: relative;
    overflow: hidden;
    
    &::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10%);
        background-repeat: no-repeat;
        background-position: 50%;
        transform: scale(10, 10);
        opacity: 0;
        transition: transform 0.5s, opacity 1s;
    }
    
    &:active::after {
        transform: scale(0, 0);
        opacity: 0.3;
        transition: 0s;
    }
}

// Dark ripple variant (for light backgrounds)
.ops-ripple-dark {
    &::after {
        background-image: radial-gradient(circle, rgba(0, 0, 0, 0.15) 10%, transparent 10%);
    }
}

// -----------------------------------------------------------------------------
// APPLY RIPPLE TO ODOO BUTTONS
// -----------------------------------------------------------------------------

.btn,
.o_form_button_save,
.o_form_button_cancel,
.o_statusbar_buttons button,
.o_kanban_button,
.o_list_button {
    @extend .ops-ripple;
}

// -----------------------------------------------------------------------------
// HOVER LIFT EFFECT
// -----------------------------------------------------------------------------
// Subtle lift on hover for cards and buttons

.ops-hover-lift {
    transition: transform var(--ops-transition-base), 
                box-shadow var(--ops-transition-base);
    
    &:hover {
        transform: translateY(-2px);
        box-shadow: var(--ops-shadow-lg);
    }
    
    &:active {
        transform: translateY(0);
        box-shadow: var(--ops-shadow-md);
    }
}

// Apply to cards
.o_kanban_record,
.o_form_view,
.o_dashboard_graph {
    @extend .ops-hover-lift;
}

// -----------------------------------------------------------------------------
// ROW HOVER HIGHLIGHT
// -----------------------------------------------------------------------------

.o_list_view tbody tr {
    transition: background-color var(--ops-transition-fast);
    
    &:hover {
        background-color: var(--ops-bg-hover) !important;
    }
    
    &.o_data_row_selected {
        background-color: var(--ops-bg-selected) !important;
    }
}

// -----------------------------------------------------------------------------
// BUTTON HOVER STATES
// -----------------------------------------------------------------------------

.btn {
    transition: all var(--ops-transition-base);
    
    &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: var(--ops-shadow-md);
    }
    
    &:active:not(:disabled) {
        transform: translateY(0);
        box-shadow: var(--ops-shadow-sm);
    }
}

// Primary button glow on hover
.btn-primary {
    &:hover:not(:disabled) {
        box-shadow: 0 4px 14px rgba(var(--ops-secondary-rgb), 0.4);
    }
}

// -----------------------------------------------------------------------------
// ICON SPIN ON HOVER
// -----------------------------------------------------------------------------

.ops-icon-spin:hover {
    .fa, .oi, i {
        animation: ops-spin 0.5s ease;
    }
}

@keyframes ops-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

// -----------------------------------------------------------------------------
// SCALE ON HOVER (for icons, avatars)
// -----------------------------------------------------------------------------

.ops-hover-scale {
    transition: transform var(--ops-transition-fast);
    
    &:hover {
        transform: scale(1.1);
    }
}
```

### 2.2 _animations.scss - Keyframes & Entrance Effects

```scss
// =============================================================================
// OPS THEME - ANIMATIONS
// =============================================================================

// -----------------------------------------------------------------------------
// ENTRANCE ANIMATIONS
// -----------------------------------------------------------------------------

// Fade In
@keyframes ops-fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

// Fade In Up
@keyframes ops-fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

// Fade In Down
@keyframes ops-fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

// Scale In (Bounce effect)
@keyframes ops-scaleIn {
    0% {
        opacity: 0;
        transform: scale(0.9);
    }
    50% {
        transform: scale(1.02);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

// Slide In Right
@keyframes ops-slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

// -----------------------------------------------------------------------------
// ATTENTION ANIMATIONS
// -----------------------------------------------------------------------------

// Pulse (for notifications)
@keyframes ops-pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

// Pulse Ring (notification badge)
@keyframes ops-pulseRing {
    0% {
        box-shadow: 0 0 0 0 rgba(var(--ops-secondary-rgb), 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(var(--ops-secondary-rgb), 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(var(--ops-secondary-rgb), 0);
    }
}

// Shake (error/attention)
@keyframes ops-shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

// -----------------------------------------------------------------------------
// UTILITY CLASSES
// -----------------------------------------------------------------------------

.ops-animate-fadeIn { animation: ops-fadeIn 0.3s ease; }
.ops-animate-fadeInUp { animation: ops-fadeInUp 0.3s ease; }
.ops-animate-fadeInDown { animation: ops-fadeInDown 0.3s ease; }
.ops-animate-scaleIn { animation: ops-scaleIn 0.3s ease; }
.ops-animate-slideInRight { animation: ops-slideInRight 0.3s ease; }
.ops-animate-pulse { animation: ops-pulse 2s infinite; }
.ops-animate-pulseRing { animation: ops-pulseRing 2s infinite; }
.ops-animate-shake { animation: ops-shake 0.5s ease; }

// -----------------------------------------------------------------------------
// APPLY TO ODOO COMPONENTS
// -----------------------------------------------------------------------------

// Dropdowns animate in
.dropdown-menu.show {
    animation: ops-scaleIn 0.2s ease;
    transform-origin: top;
}

// Modals
.modal.show .modal-dialog {
    animation: ops-fadeInUp 0.3s ease;
}

// Notifications
.o_notification {
    animation: ops-slideInRight 0.3s ease;
}

// Form views entrance
.o_form_view {
    animation: ops-fadeIn 0.2s ease;
}

// Kanban cards stagger (if supported)
.o_kanban_record {
    animation: ops-fadeInUp 0.3s ease;
}
```

### 2.3 _loader.scss - Page Loading Spinner

```scss
// =============================================================================
// OPS THEME - PAGE LOADER
// =============================================================================

#ops-loader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--ops-bg-body);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: var(--ops-z-loader);
    transition: opacity 0.3s ease, visibility 0.3s ease;
    
    &.ops-loader-hidden {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
    }
}

// Spinner
.ops-spinner {
    width: 48px;
    height: 48px;
    border: 3px solid var(--ops-border);
    border-top-color: var(--ops-secondary);
    border-radius: 50%;
    animation: ops-spin-loader 0.8s linear infinite;
}

@keyframes ops-spin-loader {
    to { transform: rotate(360deg); }
}

// Loading text
.ops-loader-text {
    margin-top: 16px;
    color: var(--ops-text-secondary);
    font-size: var(--ops-font-size-sm);
    font-weight: 500;
}

// Progress bar variant
.ops-loader-progress {
    width: 200px;
    height: 4px;
    background: var(--ops-border);
    border-radius: var(--ops-radius-full);
    overflow: hidden;
    margin-top: 16px;
    
    &::after {
        content: '';
        display: block;
        width: 30%;
        height: 100%;
        background: var(--ops-secondary);
        border-radius: var(--ops-radius-full);
        animation: ops-progress 1.5s ease-in-out infinite;
    }
}

@keyframes ops-progress {
    0% { transform: translateX(-100%); }
    50% { transform: translateX(250%); }
    100% { transform: translateX(-100%); }
}
```

---

## Phase 3: Login Page (Split-Screen)

### 3.1 _login.scss - Complete Login Styling

```scss
// =============================================================================
// OPS THEME - LOGIN PAGE
// =============================================================================
// Split-screen layout: Brand left, Form right
// =============================================================================

// Full-height login container
.ops-login-wrapper {
    min-height: 100vh;
    display: flex;
    background: var(--ops-bg-body);
}

// -----------------------------------------------------------------------------
// LEFT PANEL - Brand Section
// -----------------------------------------------------------------------------

.ops-login-brand {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 48px;
    background: linear-gradient(135deg, var(--ops-primary) 0%, #0f172a 100%);
    position: relative;
    overflow: hidden;
    
    // Abstract background pattern
    &::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    // Hide on mobile
    @media (max-width: 991px) {
        display: none;
    }
}

.ops-login-logo {
    margin-bottom: 32px;
    
    img {
        max-width: 180px;
        height: auto;
    }
}

.ops-login-welcome {
    text-align: center;
    color: var(--ops-text-inverse);
    z-index: 1;
    
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 16px;
        color: var(--ops-text-inverse);
    }
    
    p {
        font-size: 1.125rem;
        opacity: 0.9;
        max-width: 400px;
        line-height: 1.6;
    }
}

// Decorative element
.ops-login-decoration {
    margin-top: 48px;
    display: flex;
    gap: 8px;
    
    span {
        display: block;
        height: 4px;
        border-radius: var(--ops-radius-full);
        background: var(--ops-secondary);
        
        &:nth-child(1) { width: 60px; opacity: 0.9; }
        &:nth-child(2) { width: 40px; opacity: 0.6; }
        &:nth-child(3) { width: 24px; opacity: 0.3; }
    }
}

// -----------------------------------------------------------------------------
// RIGHT PANEL - Form Section
// -----------------------------------------------------------------------------

.ops-login-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 48px 24px;
    background: var(--ops-bg-card);
    
    @media (max-width: 991px) {
        padding: 24px 16px;
    }
}

.ops-login-form-container {
    width: 100%;
    max-width: 400px;
}

// Mobile logo (shown only on small screens)
.ops-login-mobile-logo {
    display: none;
    text-align: center;
    margin-bottom: 32px;
    
    @media (max-width: 991px) {
        display: block;
    }
    
    img {
        max-width: 120px;
        height: auto;
    }
}

// Form header
.ops-login-header {
    margin-bottom: 32px;
    
    h2 {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--ops-text-primary);
        margin-bottom: 8px;
    }
    
    p {
        color: var(--ops-text-secondary);
        font-size: var(--ops-font-size-sm);
    }
}

// -----------------------------------------------------------------------------
// FORM INPUTS STYLING
// -----------------------------------------------------------------------------

.ops-login-form {
    .field-login,
    .field-password,
    .form-group {
        margin-bottom: 20px;
    }
    
    label {
        display: block;
        font-weight: 500;
        color: var(--ops-text-primary);
        margin-bottom: 8px;
        font-size: var(--ops-font-size-sm);
    }
    
    input[type="text"],
    input[type="password"],
    input[type="email"],
    .form-control {
        width: 100%;
        padding: 12px 16px;
        font-size: var(--ops-font-size-base);
        color: var(--ops-text-primary);
        background: var(--ops-bg-input);
        border: 1px solid var(--ops-border);
        border-radius: var(--ops-radius-md);
        transition: all var(--ops-transition-base);
        
        &::placeholder {
            color: var(--ops-text-disabled);
        }
        
        &:focus {
            outline: none;
            border-color: var(--ops-secondary);
            box-shadow: 0 0 0 3px rgba(var(--ops-secondary-rgb), 0.15);
        }
        
        &:hover:not(:focus) {
            border-color: var(--ops-text-disabled);
        }
    }
    
    // Login button
    button[type="submit"],
    .btn-primary {
        width: 100%;
        padding: 14px 24px;
        font-size: var(--ops-font-size-base);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--ops-text-inverse);
        background: var(--ops-secondary) !important;
        border: none !important;
        border-radius: var(--ops-radius-md);
        cursor: pointer;
        transition: all var(--ops-transition-base);
        
        &:hover:not(:disabled) {
            background: var(--ops-secondary-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(var(--ops-secondary-rgb), 0.4);
        }
        
        &:active:not(:disabled) {
            transform: translateY(0);
        }
        
        &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    }
    
    // Links
    a {
        color: var(--ops-secondary);
        font-size: var(--ops-font-size-sm);
        
        &:hover {
            color: var(--ops-secondary-hover);
            text-decoration: underline;
        }
    }
}

// Footer
.ops-login-footer {
    margin-top: 32px;
    text-align: center;
    
    small {
        color: var(--ops-text-disabled);
        font-size: var(--ops-font-size-xs);
    }
}
```

### 3.2 login_templates.xml - Template Override

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- =====================================================================
         OPS THEME - SPLIT-SCREEN LOGIN
         ===================================================================== -->
    
    <!-- Override the login layout -->
    <template id="login_layout" inherit_id="web.login_layout" name="OPS Login Layout" priority="100">
        <!-- Add body class -->
        <xpath expr="//body" position="attributes">
            <attribute name="class" add="ops-login-body" separator=" "/>
        </xpath>
        
        <!-- Replace main container with split-screen layout -->
        <xpath expr="//main" position="replace">
            <main class="ops-login-wrapper">
                <!-- LEFT: Brand Panel -->
                <div class="ops-login-brand">
                    <div class="ops-login-logo">
                        <t t-if="company and company.logo">
                            <img t-attf-src="/web/binary/company_logo?company={{company.id}}&amp;colorize=white" 
                                 alt="Company Logo"/>
                        </t>
                        <t t-else="">
                            <img src="/ops_theme/static/src/img/ops_logo_light.svg" 
                                 alt="OPS Framework"/>
                        </t>
                    </div>
                    <div class="ops-login-welcome">
                        <h1>Welcome</h1>
                        <p t-if="company and company.name" t-esc="company.name"/>
                        <p t-else="">Enterprise Resource Planning</p>
                    </div>
                    <div class="ops-login-decoration">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                
                <!-- RIGHT: Form Panel -->
                <div class="ops-login-form">
                    <div class="ops-login-form-container">
                        <!-- Mobile logo -->
                        <div class="ops-login-mobile-logo">
                            <t t-if="company and company.logo">
                                <img t-attf-src="/web/binary/company_logo?company={{company.id}}" 
                                     alt="Company Logo"/>
                            </t>
                            <t t-else="">
                                <img src="/ops_theme/static/src/img/ops_logo_dark.svg" 
                                     alt="OPS Framework"/>
                            </t>
                        </div>
                        
                        <!-- Form header -->
                        <div class="ops-login-header">
                            <h2>Sign In</h2>
                            <p>Enter your credentials to access your account</p>
                        </div>
                        
                        <!-- Odoo's form content injected here -->
                        <t t-out="0"/>
                        
                        <!-- Footer -->
                        <div class="ops-login-footer">
                            <small>Powered by OPS Framework</small>
                        </div>
                    </div>
                </div>
            </main>
        </xpath>
    </template>
    
    <!-- Remove default Odoo branding from login -->
    <template id="login_debranding" inherit_id="web.login" name="OPS Login Debranding" priority="100">
        <!-- Remove "Powered by Odoo" -->
        <xpath expr="//div[hasclass('text-center')]/small[contains(text(), 'Odoo')]" position="replace"/>
        <xpath expr="//a[contains(@href, 'odoo.com')]" position="replace"/>
    </template>
</odoo>
```

---

## Phase 4: Backend Components

### 4.1 _navbar.scss - Top Navigation

```scss
// =============================================================================
// OPS THEME - NAVBAR
// =============================================================================

.o_main_navbar {
    background: var(--ops-primary) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: var(--ops-shadow-md);
    height: 50px;
    
    // All text/icons white
    .o_menu_brand,
    .o_menu_sections a,
    .o_menu_systray a,
    .dropdown-toggle,
    .nav-link {
        color: rgba(255, 255, 255, 0.85) !important;
        transition: color var(--ops-transition-fast);
        
        &:hover {
            color: rgba(255, 255, 255, 1) !important;
        }
    }
    
    // App menu button
    .o_navbar_apps_menu .dropdown-toggle {
        padding: 8px 12px;
        border-radius: var(--ops-radius-md);
        
        &:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    }
    
    // Search
    .o_menu_search {
        .o_searchview {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: var(--ops-radius-md);
            
            input {
                color: white;
                
                &::placeholder {
                    color: rgba(255, 255, 255, 0.5);
                }
            }
            
            &:focus-within {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
        }
    }
    
    // Notification badge pulse
    .o_notification_counter {
        animation: ops-pulseRing 2s infinite;
    }
}

// Dark mode toggle button (custom component)
.ops-dark-toggle {
    padding: 8px;
    border-radius: var(--ops-radius-md);
    cursor: pointer;
    transition: all var(--ops-transition-fast);
    
    &:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    i {
        transition: transform var(--ops-transition-base);
    }
    
    &.rotating i {
        transform: rotate(180deg);
    }
}
```

### 4.2 _cards.scss - Card Components

```scss
// =============================================================================
// OPS THEME - CARDS
// =============================================================================

// Base card style for all Odoo views
.o_form_view,
.o_list_view,
.o_kanban_view {
    background: var(--ops-bg-card);
    border-radius: var(--ops-radius-lg);
    box-shadow: var(--ops-shadow-md);
    margin: 16px;
    overflow: hidden;
}

// Form view specifics
.o_form_view {
    padding: 24px;
    
    .o_form_sheet_bg {
        background: transparent !important;
    }
    
    .o_form_sheet {
        background: transparent !important;
        border: none;
        box-shadow: none;
        max-width: none;
        padding: 0;
    }
}

// List view specifics
.o_list_view {
    padding: 0;
    
    .o_list_table {
        margin: 0;
        
        thead {
            background: var(--ops-bg-hover);
            
            th {
                color: var(--ops-text-secondary);
                font-weight: 600;
                font-size: var(--ops-font-size-xs);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 12px 16px;
                border-bottom: 1px solid var(--ops-border);
            }
        }
        
        tbody td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--ops-divider);
            color: var(--ops-text-primary);
        }
    }
}

// Kanban view
.o_kanban_view {
    padding: 16px;
    background: var(--ops-bg-body) !important;
    box-shadow: none;
    
    .o_kanban_group {
        background: var(--ops-bg-card);
        border-radius: var(--ops-radius-lg);
        padding: 12px;
    }
    
    .o_kanban_record {
        background: var(--ops-bg-card);
        border: 1px solid var(--ops-border);
        border-radius: var(--ops-radius-md);
        margin-bottom: 8px;
        padding: 12px;
        transition: all var(--ops-transition-base);
        
        &:hover {
            border-color: var(--ops-secondary);
            box-shadow: var(--ops-shadow-md);
        }
    }
}
```

### 4.3 _buttons.scss - Button Variants

```scss
// =============================================================================
// OPS THEME - BUTTONS
// =============================================================================

// Reset all Odoo button styles
.btn {
    font-family: var(--ops-font-family);
    font-weight: 500;
    border-radius: var(--ops-radius-md);
    padding: 8px 16px;
    transition: all var(--ops-transition-base);
    
    &:focus {
        box-shadow: 0 0 0 3px rgba(var(--ops-secondary-rgb), 0.2);
    }
}

// Primary button
.btn-primary {
    background: var(--ops-secondary) !important;
    border-color: var(--ops-secondary) !important;
    color: white !important;
    
    &:hover:not(:disabled) {
        background: var(--ops-secondary-hover) !important;
        border-color: var(--ops-secondary-hover) !important;
        box-shadow: 0 4px 12px rgba(var(--ops-secondary-rgb), 0.4);
    }
}

// Secondary button
.btn-secondary {
    background: var(--ops-bg-card);
    border: 1px solid var(--ops-border);
    color: var(--ops-text-primary);
    
    &:hover:not(:disabled) {
        background: var(--ops-bg-hover);
        border-color: var(--ops-text-disabled);
    }
}

// Success button
.btn-success {
    background: var(--ops-success) !important;
    border-color: var(--ops-success) !important;
}

// Danger button
.btn-danger {
    background: var(--ops-danger) !important;
    border-color: var(--ops-danger) !important;
}

// Link button
.btn-link {
    color: var(--ops-secondary);
    
    &:hover {
        color: var(--ops-secondary-hover);
    }
}

// Icon-only buttons
.btn-icon {
    padding: 8px;
    line-height: 1;
}
```

### 4.4 _badges.scss - Status Badges

```scss
// =============================================================================
// OPS THEME - BADGES
// =============================================================================

.badge {
    font-family: var(--ops-font-family);
    font-weight: 500;
    font-size: var(--ops-font-size-xs);
    padding: 4px 8px;
    border-radius: var(--ops-radius-sm);
}

// Light badge variants (Gilded-inspired)
.badge-primary-light,
.ops-badge-primary {
    background: rgba(var(--ops-secondary-rgb), 0.15);
    color: var(--ops-secondary);
}

.badge-success-light,
.ops-badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: var(--ops-success);
}

.badge-warning-light,
.ops-badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: var(--ops-warning);
}

.badge-danger-light,
.ops-badge-danger {
    background: rgba(239, 68, 68, 0.15);
    color: var(--ops-danger);
}

.badge-info-light,
.ops-badge-info {
    background: rgba(6, 182, 212, 0.15);
    color: var(--ops-info);
}

// Odoo state badges
.o_field_badge {
    border-radius: var(--ops-radius-sm);
    padding: 4px 10px;
    font-weight: 500;
}
```

### 4.5 _debranding.scss - Remove Odoo Branding

```scss
// =============================================================================
// OPS THEME - DEBRANDING
// =============================================================================
// Remove all Odoo branding elements and colors
// =============================================================================

// Override Odoo's brand purple (#714B67)
:root {
    --o-brand-odoo: var(--ops-primary) !important;
    --o-brand-primary: var(--ops-secondary) !important;
}

// Hide Odoo logos and brand text
.o_main_navbar .o_menu_brand img[src*="odoo"],
img[src*="odoo-icon"],
img[src*="odoo_icon"],
img[src*="logo2"],
[src*="odoo.com"] {
    opacity: 0 !important;
    pointer-events: none;
}

// Remove "Powered by Odoo" and Odoo links
a[href*="odoo.com"],
.o_footer_powered,
[class*="powered_by"] {
    display: none !important;
}

// Kill Odoo purple everywhere
.text-odoo,
.bg-odoo,
.btn-odoo {
    color: var(--ops-secondary) !important;
    background-color: var(--ops-secondary) !important;
}

// Override primary color usage
.bg-primary {
    background-color: var(--ops-secondary) !important;
}

.text-primary {
    color: var(--ops-secondary) !important;
}

.border-primary {
    border-color: var(--ops-secondary) !important;
}

// Facet tags in search
.o_searchview_facet {
    background: var(--ops-secondary) !important;
    
    .o_facet_value {
        color: white;
    }
}

// Active tabs
.nav-tabs .nav-link.active,
.o_notebook .nav-link.active {
    color: var(--ops-secondary) !important;
    border-bottom-color: var(--ops-secondary) !important;
}

// Selection highlight
.o_list_view tr.o_data_row.o_row_selected {
    background: rgba(var(--ops-secondary-rgb), 0.1) !important;
}

// Replace favicon via JS (in theme_loader.js)
```

---

## Phase 5: JavaScript Interactions

### 5.1 theme_loader.js

```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";

// Apply theme on load
document.addEventListener('DOMContentLoaded', () => {
    // Check saved dark mode preference
    const darkMode = localStorage.getItem('ops-dark-mode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (darkMode === 'true' || (darkMode === null && prefersDark)) {
        document.body.classList.add('dark-skin');
    }
    
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

// Watch for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const userPref = localStorage.getItem('ops-dark-mode');
    if (userPref === null) { // Only if user hasn't set preference
        document.body.classList.toggle('dark-skin', e.matches);
    }
});
```

### 5.2 dark_mode_toggle.js

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class DarkModeToggle extends Component {
    setup() {
        this.state = useState({
            isDark: document.body.classList.contains('dark-skin'),
            rotating: false
        });
    }
    
    toggle() {
        this.state.rotating = true;
        
        setTimeout(() => {
            this.state.isDark = !this.state.isDark;
            document.body.classList.toggle('dark-skin', this.state.isDark);
            localStorage.setItem('ops-dark-mode', this.state.isDark);
            
            setTimeout(() => {
                this.state.rotating = false;
            }, 200);
        }, 150);
    }
}

DarkModeToggle.template = "ops_theme.DarkModeToggle";

registry.category("systray").add("ops_theme.DarkModeToggle", {
    Component: DarkModeToggle,
}, { sequence: 1 });
```

### 5.3 interactions.js - Ripple Effect

```javascript
/** @odoo-module **/

// Add ripple effect to buttons on click
document.addEventListener('click', (e) => {
    const target = e.target.closest('.btn, button[type="submit"]');
    if (!target) return;
    
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ops-ripple-effect');
    
    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    `;
    
    target.style.position = 'relative';
    target.style.overflow = 'hidden';
    target.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
});

// Add ripple animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
```

---

## Phase 6: Company Settings Model

### 6.1 res_company.py

```python
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Theme Settings
    ops_theme_preset = fields.Selection([
        ('corporate_blue', 'Corporate Blue'),
        ('modern_dark', 'Modern Dark'),
        ('clean_light', 'Clean Light'),
        ('enterprise_navy', 'Enterprise Navy'),
        ('custom', 'Custom'),
    ], string='Theme Preset', default='corporate_blue')
    
    # Custom Colors
    ops_primary_color = fields.Char(
        string='Primary Color',
        default='#1e293b',
        help='Main brand color (headers, navbar)'
    )
    ops_secondary_color = fields.Char(
        string='Secondary Color',
        default='#3b82f6',
        help='Accent color (buttons, links)'
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
    
    # Branding
    ops_powered_by_visible = fields.Boolean(
        string='Show "Powered by OPS"',
        default=True
    )
    
    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        """Apply preset colors when preset changes"""
        presets = {
            'corporate_blue': ('#1e293b', '#3b82f6'),
            'modern_dark': ('#0f172a', '#6366f1'),
            'clean_light': ('#374151', '#059669'),
            'enterprise_navy': ('#1e3a5f', '#0ea5e9'),
        }
        if self.ops_theme_preset in presets:
            self.ops_primary_color, self.ops_secondary_color = presets[self.ops_theme_preset]
```

### 6.2 res_users.py

```python
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    ops_color_mode = fields.Selection([
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ], string='Color Mode', default='system')
    
    ops_chatter_position = fields.Selection([
        ('below', 'Below Form'),
        ('right', 'Right Side'),
    ], string='Chatter Position', default='below')
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['ops_color_mode', 'ops_chatter_position']
    
    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['ops_color_mode', 'ops_chatter_position']
```

---

## Implementation Checklist

### Priority 1: Core Styling (Day 1)
- [ ] Create module structure
- [ ] Implement _variables.scss with CSS custom properties
- [ ] Implement _base.scss with typography
- [ ] Implement _navbar.scss
- [ ] Implement _cards.scss for floating views
- [ ] Implement _debranding.scss
- [ ] Test module installation

### Priority 2: Login Page (Day 1-2)
- [ ] Create login_templates.xml with split-screen
- [ ] Implement _login.scss
- [ ] Create OPS logo SVGs (light/dark variants)
- [ ] Test login page rendering
- [ ] Verify mobile responsiveness

### Priority 3: Micro-Interactions (Day 2)
- [ ] Implement _interactions.scss (ripples, hovers)
- [ ] Implement _animations.scss (entrances)
- [ ] Implement interactions.js (JS ripple)
- [ ] Test button effects
- [ ] Test dropdown animations

### Priority 4: Dark Mode (Day 2-3)
- [ ] Complete _dark_mode.scss
- [ ] Implement dark_mode_toggle.js
- [ ] Create OWL template for toggle
- [ ] Add toggle to systray
- [ ] Test mode switching

### Priority 5: Settings UI (Day 3)
- [ ] Create res_company.py model
- [ ] Create res_users.py model
- [ ] Create res_config_settings.py
- [ ] Create settings view XML
- [ ] Test color customization

### Priority 6: Polish (Day 3-4)
- [ ] Implement _loader.scss
- [ ] Implement page_loader.js
- [ ] Complete _forms.scss
- [ ] Complete _lists.scss
- [ ] Complete _badges.scss
- [ ] Full QA testing

---

## Testing Checklist

- [ ] Module installs without errors
- [ ] No SCSS compilation errors
- [ ] No JS console errors
- [ ] Login page displays split-screen
- [ ] Login form is styled (not purple)
- [ ] Dark mode toggle works
- [ ] Ripple effects on buttons
- [ ] Smooth hover transitions
- [ ] Dropdown animations
- [ ] No Odoo branding visible
- [ ] Company colors apply
- [ ] Mobile responsive
- [ ] Chrome, Firefox, Safari compatible

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Page load perception | < 1s (with loader) |
| Button response | Immediate ripple |
| Hover transitions | 200ms smooth |
| Dark mode switch | < 300ms |
| Purple (#714B67) instances | Zero |
| "Odoo" text visible | Zero |
| Customer "ownership" feeling | High |

---

**Document Status**: READY FOR CLAUDE CODE IMPLEMENTATION  
**Estimated Effort**: 3-4 days  
**Priority**: P0 - Critical for product launch
