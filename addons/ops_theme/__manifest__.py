# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.1.0.0',
    'category': 'Themes/Backend',
    'summary': 'Company-brandable backend theme with light/dark mode support',
    'description': """
OPS Theme - Enterprise Backend Theme
=====================================

Features:
- Company-brandable UI with dynamic colors
- Light/Dark/System color mode support
- Split-screen login page with company branding
- App grid home menu with horizontal menu tabs
- Chatter position toggle (below/right)
- Complete Odoo debranding
- PDF report theming
- Theme configuration UI in Settings
- Color pickers for brand customization
- Theme presets (Corporate Blue, Modern Dark, etc.)
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
            'ops_theme/static/src/scss/_variables.scss',
            'ops_theme/static/src/scss/_login.scss',
            'ops_theme/static/src/js/theme_loader.js',
        ],
        'web.assets_backend': [
            'ops_theme/static/src/scss/theme.scss',
            'ops_theme/static/src/js/theme_loader.js',
            'ops_theme/static/src/js/color_mode_toggle.js',
            'ops_theme/static/src/js/chatter_toggle.js',
            'ops_theme/static/src/xml/user_menu.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
