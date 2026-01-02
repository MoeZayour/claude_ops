{
    'name': 'OPS Matrix Reporting',
    'version': '19.0.1.0',
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
        'account',
        'stock',
        'spreadsheet_dashboard',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Views
        'views/ops_sales_analysis_views.xml',
        'views/ops_financial_analysis_views.xml',
        'views/ops_inventory_analysis_views.xml',
        'views/ops_excel_export_wizard_views.xml',
        'views/reporting_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_matrix_reporting/static/src/css/reporting.css',
        ],
    },
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'images': ['static/description/icon.png'],
}
