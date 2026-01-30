{
    'name': 'OPS Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Dashboards',
    'summary': 'Executive and Operational Dashboards for OPS Matrix',
    'description': """
OPS Dashboard - Enterprise Analytics
====================================
* Executive Dashboard (CEO/CFO view)
* Branch Performance Dashboard
* Sales Dashboard
* KPI Cards with real-time data
* Security-compliant data filtering
* Trading company focused metrics
    """,
    'author': 'OPS Framework',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'sale',
        'purchase',
        'account',
        'stock',
        'ops_matrix_core',
        'ops_matrix_accounting',
    ],
    'data': [
        'security/ops_dashboard_security.xml',
        'security/ir.model.access.csv',
        'data/ops_kpi_data.xml',
        'data/ops_dashboard_data.xml',
        'views/ops_dashboard_views.xml',
        'views/ops_dashboard_widget_views.xml',
        'views/ops_kpi_views.xml',
        'views/ops_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_dashboard/static/src/scss/dashboard.scss',
            'ops_dashboard/static/src/js/ops_dashboard_action.js',
            'ops_dashboard/static/src/xml/ops_dashboard_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
