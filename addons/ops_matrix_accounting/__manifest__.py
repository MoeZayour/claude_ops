{
    "name": "OPS Matrix - Accounting",
    "version": "19.0.2.1.0",
    "category": "Accounting/Accounting",
    "summary": "OPS Framework Accounting Extensions",
    "description": """
        OPS Matrix Accounting Module
        ============================

        Enterprise-grade accounting features:
        - Fixed Asset Management
        - Post-Dated Checks (PDC)
        - Budget Management
        - Enhanced Financial Reporting
        - Multi-branch Accounting
    """,
    "author": "OPS Matrix",
    "website": "https://github.com/MoeZayour",
    "license": "LGPL-3",
    "depends": [
        "account",
        "ops_matrix_core",
        "report_xlsx",
        "analytic",
    ],
    "external_dependencies": {
        "python": ["xlsxwriter"],
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/ops_asset_security.xml",

        # Data
        "data/ops_asset_data.xml",

        # Views
        "views/ops_asset_category_views.xml",
        "views/ops_asset_views.xml",
        "views/ops_asset_depreciation_views.xml",
        "views/ops_budget_views.xml",
        "views/ops_pdc_views.xml",

        # Wizards
        "wizard/ops_asset_depreciation_wizard_views.xml",

        # Reports
        "report/ops_asset_report_templates.xml",

        # Menus
        "views/accounting_menus.xml",
    ],
    "demo": [
        "demo/ops_asset_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ops_matrix_accounting/static/src/css/ops_accounting.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
