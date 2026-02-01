# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.6.3.0',
    'category': 'Themes/Backend',
    'summary': 'Premium enterprise theme with modern styling',
    'description': """
OPS Theme v5.0 - Premium Enterprise Theme
==========================================

Modern, premium theme following minimal-override philosophy:
- Inter font family with proper typography hierarchy
- Custom-styled form controls (radio, checkbox, toggle, inputs)
- Card and KPI dashboard styling with hover effects
- Status badges with soft colored backgrounds
- Enhanced buttons with hover animations
- Clean table styling
- Full dark mode support with system preference detection

Features:
- Bootstrap variable overrides for complete debranding
- Clean slate/blue color scheme
- Dark/Light/System mode toggle
- Chatter position toggle via FormCompiler patch
- List auto-refresh feature
- Expand/Collapse all groups
- Split-screen login page
    """,
    'author': 'OPS Framework',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/login_templates.xml',
        'views/webclient_templates.xml',
        'views/debranding_templates.xml',
    ],
    'assets': {
        # =================================================================
        # PRIMARY VARIABLES - Loaded BEFORE Bootstrap compilation
        # =================================================================
        # This is the key to proper debranding - override colors at source
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss',
             'ops_theme/static/src/scss/_primary_variables.scss'),
        ],

        # =================================================================
        # FRONTEND ASSETS (Login page)
        # =================================================================
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_animations_minimal.scss',
            'ops_theme/static/src/scss/_login.scss',
            'ops_theme/static/src/js/theme_loader.js',
        ],

        # =================================================================
        # BACKEND ASSETS - Complete theme styling
        # =================================================================
        'web.assets_backend': [
            # 0. CSS Variables (single source of truth - load FIRST)
            'ops_theme/static/src/scss/_variables.scss',

            # 1. Typography (loads Inter font)
            'ops_theme/static/src/scss/_typography.scss',

            # 2. Core appearance styling
            'ops_theme/static/src/scss/_appearance.scss',
            'ops_theme/static/src/scss/_animations_minimal.scss',

            # 3. Enhanced component styling
            'ops_theme/static/src/scss/_form_controls.scss',
            'ops_theme/static/src/scss/_form_inputs_fix.scss',
            'ops_theme/static/src/scss/_cards.scss',
            'ops_theme/static/src/scss/_badges_enhanced.scss',
            'ops_theme/static/src/scss/_buttons_enhanced.scss',
            'ops_theme/static/src/scss/_tables.scss',

            # 4. Layout components (navbar, list, control panel, kanban)
            'ops_theme/static/src/scss/_navbar.scss',
            'ops_theme/static/src/scss/_list.scss',
            'ops_theme/static/src/scss/_control_panel.scss',
            'ops_theme/static/src/scss/_kanban.scss',

            # 5. Dark mode
            'ops_theme/static/src/scss/_dark_mode.scss',

            # 5.5. Chatter readability fix
            'ops_theme/static/src/scss/_chatter_fix.scss',

            # 5.6. Settings layout and error fields
            'ops_theme/static/src/scss/_settings_layout.scss',
            'ops_theme/static/src/scss/_error_fields.scss',

            # 5.7. Comprehensive dark mode fixes
            'ops_theme/static/src/scss/_dark_mode_comprehensive.scss',

            # 6. Complete debranding (enterprise hiding + color overrides)
            'ops_theme/static/src/scss/_debranding.scss',

            # 7. Color mode toggle styling
            'ops_theme/static/src/scss/_user_menu.scss',

            # 8. JavaScript - Theme utilities
            'ops_theme/static/src/js/theme_loader.js',

            # 9. JavaScript - Debranding (registry cleanup)
            'ops_theme/static/src/js/debranding.js',

            # 10. Color mode toggle component
            'ops_theme/static/src/js/color_mode_toggle.js',

            # 11. OWL Component Patches (behavior via JS, not CSS)
            'ops_theme/static/src/views/form/form_compiler.js',

            # 12. Feature extensions
            'ops_theme/static/src/search/control_panel_refresh.js',
            'ops_theme/static/src/search/group_actions.js',

            # 13. XML templates
            'ops_theme/static/src/xml/user_menu.xml',
            'ops_theme/static/src/xml/control_panel.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
