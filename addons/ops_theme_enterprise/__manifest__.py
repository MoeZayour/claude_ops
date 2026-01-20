{
    'name': 'OPS Enterprise Theme',
    'version': '1.0',
    'category': 'Theme/Backend',
    'summary': 'Modern Enterprise UI for Odoo 19',
    'description': """
        High-end visual theme for OPS Framework.
        - Card-based Layout (White Surface / Soft Shadows)
        - Modern Typography
        - Deep Navy Primary / Vibrant Blue Secondary
        - Clean Interface Overrides
    """,
    'depends': ['base', 'web', 'ops_matrix_core'],
    'data': [
        'views/web_asset_backend_template.xml',
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_theme_enterprise/static/src/scss/primary_variables.scss',
            'ops_theme_enterprise/static/src/scss/layout_overrides.scss',
            'ops_theme_enterprise/static/src/scss/home_menu_grid.scss',
        ],
        'web.assets_frontend': [
            'ops_theme_enterprise/static/src/scss/login_styles.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}