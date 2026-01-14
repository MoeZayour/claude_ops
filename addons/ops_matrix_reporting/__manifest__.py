{
    'name': 'OPS Matrix Reporting',
    'version': '19.0.1.5.0',
    'category': 'Reporting',
    'summary': 'Branch/Business Unit Matrix Analytics and Reporting',
    'description': """
    High-performance SQL-based reporting and analytics for the OPS Matrix framework.
    
    Features:
    - Sales Analysis by Branch and Business Unit
    - Financial Analysis with dimension tracking
    - Inventory Health and BU segregation verification
    - Spreadsheet Dashboard integration
    - Strict record-level security enforcement
    """,
    'author': 'OPS Matrix Development Team',
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    'depends': [
        'ops_matrix_core',
        'sale',
        'account',
        'stock',
        # # 'spreadsheet_dashboard',  # Removed - Enterprise only  # Removed - Enterprise only
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Base Structure
        'views/base_menus.xml',
        # Views & Data
        'views/ops_export_log_views.xml',
        'views/ops_dashboard_views.xml',
        'data/ops_dashboard_data.xml',
        'views/ops_sales_analysis_views.xml',
        'views/ops_financial_analysis_views.xml',
        'views/ops_inventory_analysis_views.xml',
        'views/ops_excel_export_wizard_views.xml',
        'views/secure_excel_export_wizard_views.xml',
        'views/reporting_menu.xml',
        # 'data/dashboard_data.xml',  # Disabled - Enterprise spreadsheet.dashboard not available
    ],
    'assets': {
        'web.assets_backend': [
            'ops_matrix_reporting/static/src/css/reporting.css',
            'ops_matrix_reporting/static/src/js/ops_dashboard.js',
            'ops_matrix_reporting/static/src/xml/ops_dashboard_templates.xml',
        ],
    },
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'images': ['static/description/icon.png'],
}
