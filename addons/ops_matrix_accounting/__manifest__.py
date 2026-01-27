{
    "name": "OPS Matrix - Accounting",
    "version": "19.0.9.0.0",
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
        "stock",
        "ops_matrix_core",
        "analytic",
    ],
    # Note: report_xlsx dependency removed (module unavailable)
    # Excel export features will use xlsxwriter directly when needed
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/ops_asset_security.xml",

        # Data
        "data/ops_asset_data.xml",
        "data/pdc_sequence.xml",
        "data/cron_snapshot.xml",
        "data/templates/ops_budget_templates.xml",
        "data/report_templates.xml",
        "data/report_templates_extra.xml",
        "data/ops_paperformat.xml",

        # Views
        "views/ops_asset_category_views.xml",
        "views/ops_asset_views.xml",
        "views/ops_asset_depreciation_views.xml",
        "views/ops_budget_views.xml",
        "views/ops_pdc_views.xml",
        "views/ops_pdc_receivable_menus.xml",
        "views/ops_pdc_payable_menus.xml",
        "views/ops_pdc_reports_menus.xml",
        "views/accounting_menus.xml",
        "views/ops_financial_report_wizard_views.xml",
        "views/ops_general_ledger_wizard_enhanced_views.xml",
        "views/ops_general_ledger_wizard_views.xml",
        "views/ops_matrix_snapshot_views.xml",
        "views/ops_trend_analysis_views.xml",
        "views/ops_report_menu.xml",
        "views/ops_report_template_views.xml",
        "views/ops_inventory_report_views.xml",
        "views/ops_report_audit_views.xml",
        "views/ops_dashboard_action.xml",

        # Wizards
        "wizard/ops_asset_depreciation_wizard_views.xml",
        "wizard/ops_asset_disposal_wizard_views.xml",
        "wizard/ops_treasury_report_wizard_views.xml",
        "wizard/ops_asset_report_wizard_views.xml",
        # "wizard/ops_asset_report_wizard.xml",  # Disabled - references AbstractModel

        # Reports
        "report/ops_report_layout.xml",  # Corporate branding & shared styles
        "report/ops_asset_report_templates.xml",
        "report/ops_consolidated_report_templates.xml",
        "report/ops_financial_report_template.xml",
        "report/ops_general_ledger_template.xml",
        "report/ops_inventory_report_templates.xml",  # Inventory Intelligence Reports
        "report/ops_treasury_report_templates.xml",   # Treasury Intelligence Reports

        # Menus
        # "views/ops_report_menu.xml",  # Disabled - references missing model
    ],
    "demo": [
        "demo/ops_asset_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ops_matrix_accounting/static/src/css/ops_accounting.css",
            "ops_matrix_accounting/static/src/css/ops_report.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
