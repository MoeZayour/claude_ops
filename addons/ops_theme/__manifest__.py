# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.10.0.0',
    'category': 'Themes/Backend',
    'summary': 'Minimal OPS Framework theme with clean debranding',
    'description': """
OPS Theme v7.0 - Minimal Override Philosophy
============================================

Clean, minimal theme following the "Color + Enhance, Never Fight OWL" philosophy:

**What This Theme Does (6 Things):**
1. Debranding - Replace Odoo purple with OPS Navy at Bootstrap compile time
2. Login Screen - Split-screen branded login page
3. Dark/Light Mode - Toggle using native Odoo data-bs-theme + CSS bundle switching
4. Chatter Position - Toggle between side/bottom via user preference
5. Clean UI - Remove odoo.com links and branding
6. User Preferences - Save theme settings per user

**What This Theme Does NOT Do:**
- Override form view layouts (rides Odoo native)
- Rewrite list view renderers (rides Odoo native)
- Modify wizard/modal structure (rides Odoo native)
- Fight OWL component rendering (uses Odoo's dark mode)
- Inject CSS that breaks two-column forms (minimal overrides only)

**Total SCSS**: ~400 lines (vs 3800+ in v6)
**Philosophy**: Let Odoo handle component styling, we just brand the colors
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
        # PRIMARY VARIABLES - Loaded BEFORE Bootstrap compilation
        # =================================================================
        # This is the KEY to proper debranding - override colors at source
        'web._assets_primary_variables': [
            ('prepend', 'ops_theme/static/src/scss/_primary_variables.scss'),
        ],

        # =================================================================
        # FRONTEND ASSETS (Login page)
        # =================================================================
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_login.scss',
            'ops_theme/static/src/js/theme_loader.js',
        ],

        # =================================================================
        # BACKEND ASSETS - Minimal theme styling
        # =================================================================
        'web.assets_backend': [
            # 1. Core styling (debranding, chatter)
            'ops_theme/static/src/scss/_debranding.scss',
            'ops_theme/static/src/scss/_chatter_position.scss',
            'ops_theme/static/src/scss/_dynamic_overrides.scss',
            'ops_theme/static/src/scss/_settings_theme_page.scss',

            # 2. JavaScript - Theme initialization and toggles
            'ops_theme/static/src/js/theme_loader.js',
            'ops_theme/static/src/js/debranding.js',
            'ops_theme/static/src/js/ops_theme_toggles.js',
            'ops_theme/static/src/js/chatter_position_patch.js',
            'ops_theme/static/src/js/ops_theme_selector.js',
            'ops_theme/static/src/xml/ops_theme_selector.xml',
            'ops_theme/static/src/js/theme_preview.js',

            # 3. XML templates - User menu with theme toggles
            'ops_theme/static/src/xml/user_menu.xml',
        ],

        # =================================================================
        # DARK MODE OVERRIDES - Only loaded when dark mode is active
        # =================================================================
        # web.assets_web_dark = include(web.assets_web) + *.dark.scss files
        # Our file loads AFTER all native dark.scss, giving highest cascade priority
        'web.assets_web_dark': [
            'ops_theme/static/src/scss/_ops_dark_mode.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
