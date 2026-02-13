# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.21.0.0',
    'category': 'Themes/Backend',
    'summary': 'Minimal OPS Framework theme — Odoo owns the layout, OPS owns the colors',
    'description': """
OPS Theme v19.0 — Light-Only Skin System
==========================================

Clean, minimal theme following "Odoo 19 owns the layout, OPS owns the colors":

**What This Theme Does (5 Things):**
1. Debranding — Replace Odoo purple with OPS Navy at Bootstrap compile time
2. Login Screen — Split-screen branded login page
3. Skin System — 10-color palette presets compiled into CSS bundles
4. Chatter Position — Toggle between side/bottom via user preference
5. Clean UI — Remove odoo.com links and branding via CSS + registry cleanup
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
        'views/product_views.xml',
        'report/ops_report_css.xml',
        'report/ops_external_layout.xml',
        'data/ops_theme_skin_data.xml',
    ],
    'assets': {
        # =================================================================
        # PRIMARY VARIABLES — Loaded BEFORE Bootstrap compilation
        # Colors first (replaceable via ir.asset), then structural vars.
        # =================================================================
        'web._assets_primary_variables': [
            ('prepend', 'ops_theme/static/src/scss/_primary_variables.scss'),
            (
                'before',
                'ops_theme/static/src/scss/_primary_variables.scss',
                'ops_theme/static/src/scss/_colors_light.scss',
            ),
        ],

        # =================================================================
        # FRONTEND ASSETS (Login page)
        # =================================================================
        'web.assets_frontend': [
            'ops_theme/static/src/scss/_login.scss',
        ],

        # =================================================================
        # BACKEND ASSETS — Structural overrides (no color wiring)
        # =================================================================
        'web.assets_backend': [
            # SCSS - Light mode structural overrides
            'ops_theme/static/src/scss/_debranding.scss',
            'ops_theme/static/src/scss/_chatter_position.scss',
            'ops_theme/static/src/scss/_ops_chatter.scss',
            'ops_theme/static/src/scss/_ops_overrides.scss',
            'ops_theme/static/src/scss/_ops_dialog.scss',
            'ops_theme/static/src/scss/_ops_sidebar.scss',
            'ops_theme/static/src/scss/_settings_theme_page.scss',
            'ops_theme/static/src/scss/_ops_home_menu.scss',

            # SCSS - Global "Life" Injection (Phase 5)
            'ops_theme/static/src/scss/_global_life.scss',

            # SCSS - Rich Media Kanban (Phase 8)
            'ops_theme/static/src/scss/_ops_product_kanban.scss',

            # JavaScript
            'ops_theme/static/src/js/debranding.js',
            'ops_theme/static/src/js/ops_theme_toggles.js',
            'ops_theme/static/src/js/chatter_position_patch.js',
            'ops_theme/static/src/js/ops_chatter_patch.js',
            'ops_theme/static/src/js/ops_dialog_patch.js',
            'ops_theme/static/src/js/ops_sidebar.js',
            'ops_theme/static/src/js/ops_webclient_patch.js',
            'ops_theme/static/src/js/ops_skin_selector.js',
            'ops_theme/static/src/js/ops_home_menu.js',
            'ops_theme/static/src/xml/ops_skin_selector.xml',
            'ops_theme/static/src/xml/ops_home_menu.xml',

            # Group expand/collapse controls (cog menu)
            'ops_theme/static/src/js/ops_group_controls.js',
            'ops_theme/static/src/xml/ops_group_controls.xml',
            'ops_theme/static/src/scss/_ops_group_controls.scss',

            # Auto-Refresh systray component
            'ops_theme/static/src/js/ops_auto_refresh.js',
            'ops_theme/static/src/xml/ops_auto_refresh.xml',
            'ops_theme/static/src/scss/_ops_auto_refresh.scss',

            # XML templates
            'ops_theme/static/src/xml/user_menu.xml',
            'ops_theme/static/src/xml/ops_chatter.xml',
            'ops_theme/static/src/xml/ops_dialog.xml',
            'ops_theme/static/src/xml/ops_sidebar.xml',
            'ops_theme/static/src/xml/ops_webclient.xml',
        ],

        # Dark mode bundle removed — light-only skin system.
        # _colors_dark.scss and *.dark.scss files kept on disk for future reactivation.
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
