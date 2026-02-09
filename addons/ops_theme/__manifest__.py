# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.12.0.0',
    'category': 'Themes/Backend',
    'summary': 'Minimal OPS Framework theme — Odoo owns the layout, OPS owns the colors',
    'description': """
OPS Theme v12.0 — Complete Architectural Rebuild
=================================================

Clean, minimal theme following "Odoo 19 owns the layout, OPS owns the colors":

**What This Theme Does (6 Things):**
1. Debranding — Replace Odoo purple with OPS Navy at Bootstrap compile time
2. Login Screen — Split-screen branded login page
3. Dark/Light Mode — Toggle using native Odoo data-bs-theme + CSS bundle switching
4. Chatter Position — Toggle between side/bottom via user preference
5. Clean UI — Remove odoo.com links and branding via CSS + registry cleanup
6. User Preferences — Save theme settings per user

**Architecture:**
- Layer 1 (compile-time): _primary_variables.scss overrides $o-community-color
- Layer 2 (runtime): /variables.css serves CSS custom properties from Settings
- Dark mode: Rides Odoo's native 62+ .dark.scss files, OPS adds essential overrides only
- Debranding: CSS patterns + OWL registry cleanup (no MutationObserver)
- Dark presets auto-enable dark mode via write() and onchange

**SCSS:** ~550 lines theme (components moved to ops_matrix_core)
    """,
    'author': 'OPS Framework',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/debranding_templates.xml',
        'views/login_templates.xml',
        'views/webclient_templates.xml',
        'views/res_config_settings_views.xml',
        'report/ops_report_css.xml',
        'report/ops_document_extras.xml',
        'report/ops_external_layout.xml',
    ],
    'assets': {
        # =================================================================
        # PRIMARY VARIABLES — Loaded BEFORE Bootstrap compilation
        # =================================================================
        'web._assets_primary_variables': [
            ('prepend', 'ops_theme/static/src/scss/_primary_variables.scss'),
        ],

        # =================================================================
        # FRONTEND ASSETS (Login page)
        # =================================================================
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_login.scss',
        ],

        # =================================================================
        # BACKEND ASSETS — Theme overrides
        # =================================================================
        'web.assets_backend': [
            # SCSS
            'ops_theme/static/src/scss/_debranding.scss',
            'ops_theme/static/src/scss/_chatter_position.scss',
            'ops_theme/static/src/scss/_ops_overrides.scss',
            'ops_theme/static/src/scss/_settings_theme_page.scss',

            # JavaScript
            'ops_theme/static/src/js/debranding.js',
            'ops_theme/static/src/js/ops_theme_toggles.js',
            'ops_theme/static/src/js/chatter_position_patch.js',
            'ops_theme/static/src/js/ops_theme_selector.js',
            'ops_theme/static/src/xml/ops_theme_selector.xml',
            'ops_theme/static/src/js/theme_preview.js',

            # XML templates
            'ops_theme/static/src/xml/user_menu.xml',
        ],

        # =================================================================
        # DARK MODE — Essential OPS overrides only
        # =================================================================
        # Odoo's 62+ native .dark.scss files handle standard components.
        # This file adds design tokens + OPS-specific dark fixes.
        'web.assets_web_dark': [
            'ops_theme/static/src/scss/_ops_dark.dark.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
