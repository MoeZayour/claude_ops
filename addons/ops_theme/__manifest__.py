# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.2.0.0',
    'category': 'Themes/Backend',
    'summary': 'Enterprise white-label theme with micro-interactions',
    'description': """
OPS Theme v2.0 - Modern Enterprise UI
=====================================

Features:
- Split-screen login with company branding
- Light/Dark/System color modes
- Micro-interactions (ripples, transitions, animations)
- Complete Odoo debranding
- Company-configurable colors
- Chatter position toggle
- Theme configuration UI in Settings
- Color pickers for brand customization
- Theme presets (Corporate Blue, Modern Dark, etc.)
- Smooth hover effects on all interactive elements
- Loading spinners and progress indicators
- Animated dropdowns and modals
    """,
    'author': 'OPS Framework',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'ops_matrix_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/res_users_views.xml',
        'views/login_templates.xml',
        'views/webclient_templates.xml',
        'views/debranding_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # 1. Variables first (CSS custom properties)
            'ops_theme/static/src/scss/_variables.scss',
            # 2. Base styles
            'ops_theme/static/src/scss/_base.scss',
            # 3. Animations (needed for login)
            'ops_theme/static/src/scss/_animations.scss',
            # 4. Login page styling
            'ops_theme/static/src/scss/_login.scss',
            # 5. JavaScript (early load for color mode)
            'ops_theme/static/src/js/theme_loader.js',
        ],
        'web.assets_backend': [
            # 1. Variables first (CSS custom properties)
            'ops_theme/static/src/scss/_variables.scss',
            # 2. Base styles
            'ops_theme/static/src/scss/_base.scss',
            # 3. Animations and interactions
            'ops_theme/static/src/scss/_animations.scss',
            'ops_theme/static/src/scss/_interactions.scss',
            'ops_theme/static/src/scss/_loader.scss',
            # 4. Navigation
            'ops_theme/static/src/scss/_app_grid.scss',
            'ops_theme/static/src/scss/_navbar.scss',
            'ops_theme/static/src/scss/_menu_tabs.scss',
            'ops_theme/static/src/scss/_breadcrumb.scss',
            # 5. Views
            'ops_theme/static/src/scss/_control_panel.scss',
            'ops_theme/static/src/scss/_form.scss',
            'ops_theme/static/src/scss/_list.scss',
            'ops_theme/static/src/scss/_kanban.scss',
            # 6. Components
            'ops_theme/static/src/scss/_dropdowns.scss',
            'ops_theme/static/src/scss/_badges.scss',
            'ops_theme/static/src/scss/_chatter.scss',
            'ops_theme/static/src/scss/_user_menu.scss',
            'ops_theme/static/src/scss/_settings.scss',
            # 7. Debranding LAST (to override Odoo styles)
            'ops_theme/static/src/scss/_debranding.scss',
            # 8. JavaScript
            'ops_theme/static/src/js/theme_loader.js',
            'ops_theme/static/src/js/color_mode_toggle.js',
            'ops_theme/static/src/js/chatter_toggle.js',
            'ops_theme/static/src/js/interactions.js',
            'ops_theme/static/src/js/page_loader.js',
            # 9. XML templates
            'ops_theme/static/src/xml/user_menu.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
