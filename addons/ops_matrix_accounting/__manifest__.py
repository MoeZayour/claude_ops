{
    "name": "OPS Matrix - Accounting",
    "version": "19.0.20.0.0",  # Wave 8 — Report restructuring: single-generation architecture
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
    "author": "OPS Framework",
    "website": "https://github.com/MoeZayour",
    "license": "LGPL-3",
    "depends": [
        "account",
        "purchase",
        "stock",
        "ops_matrix_core",
        "analytic",
    ],
    # Note: report_xlsx dependency removed (module unavailable)
    # Excel export features will use xlsxwriter directly when needed
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/ops_accounting_rules.xml",
        "security/ops_asset_security.xml",

        # Data
        "data/ops_asset_data.xml",
        "data/pdc_sequence.xml",
        "data/cron_snapshot.xml",
        "data/cron_depreciation.xml",
        "data/cron_recurring.xml",
        "data/cron_followup.xml",
        "data/followup_data.xml",
        "data/sequences_advanced.xml",
        "data/templates/ops_budget_templates.xml",
        "data/report_templates.xml",
        "data/report_templates_extra.xml",
        "data/ops_paperformat.xml",
        "data/ops_sod_bank_rules.xml",

        # Views
        "views/ops_asset_category_views.xml",
        "views/ops_asset_views.xml",
        "views/ops_asset_depreciation_views.xml",
        "views/ops_budget_views.xml",
        "views/ops_pdc_views.xml",
        "views/ops_fiscal_period_views.xml",
        "views/account_move_views.xml",
        "views/ops_pdc_receivable_menus.xml",
        "views/ops_pdc_payable_menus.xml",
        "views/ops_pdc_reports_menus.xml",
        "views/res_config_settings_views.xml",
        # DEPRECATED: ops_financial_report_wizard_views.xml moved to deprecated/
        # DEPRECATED: ops_general_ledger_wizard_views.xml moved to deprecated/
        "views/res_company_report_colors_views.xml",
        "views/ops_general_ledger_wizard_enhanced_views.xml",
        "views/ops_matrix_snapshot_views.xml",
        "views/ops_trend_analysis_views.xml",
        # DISABLED: ops_report_menu.xml - references deprecated ops.financial.report.wizard model
        # "views/ops_report_menu.xml",
        "views/ops_report_template_views.xml",
        "views/ops_inventory_report_views.xml",
        "views/ops_report_audit_views.xml",
        "views/ops_dashboard_action.xml",
        "views/ops_recurring_views.xml",
        "views/ops_financial_report_config_views.xml",
        "views/ops_followup_views.xml",
        "views/ops_daily_reports_views.xml",
        "views/ops_interbranch_transfer_views.xml",
        "views/ops_bank_reconciliation_views.xml",
        "views/ops_lease_views.xml",
        "views/ops_fx_revaluation_views.xml",

        # Wizards
        "wizard/ops_asset_depreciation_wizard_views.xml",
        "wizard/ops_asset_disposal_wizard_views.xml",
        "wizard/ops_treasury_report_wizard_views.xml",
        "wizard/ops_period_close_wizard_views.xml",
        "wizard/ops_asset_report_wizard_views.xml",
        "wizard/ops_three_way_match_override_wizard_views.xml",
        "wizard/ops_consolidation_intelligence_wizard_views.xml",
        "wizard/ops_budget_vs_actual_wizard_views.xml",
        # "wizard/ops_asset_report_wizard.xml",  # Disabled - references AbstractModel

        # Menus - must load AFTER all views/wizards that define actions
        "views/accounting_menus.xml",

        # Reports - Shared Components
        "report/ops_corporate_report_layout.xml",  # Corporate PDF layout (footer + page numbers)
        "report/components/ops_corporate_report_components.xml",  # Corporate report components (16 official reports)
        "report/ops_asset_report_templates.xml",
        "report/ops_consolidated_report_templates.xml",
        "report/ops_financial_report_template.xml",
        "report/ops_general_ledger_template.xml",
        "report/ops_inventory_report_templates.xml",  # Inventory Intelligence Reports
        "report/ops_treasury_report_templates.xml",   # Treasury Intelligence Reports
        "report/ops_daily_report_templates.xml",        # Daily Cash/Bank/Day Book Reports
        "report/ops_partner_ledger_corporate.xml",       # Partner Ledger (Corporate)
        "report/ops_budget_vs_actual_corporate.xml",     # Budget vs Actual (Corporate)
        "report/ops_report_invoice.xml",                 # OPS Branded Invoice / Credit Note
        "report/ops_report_payment.xml",                 # OPS Branded Payment Receipt / Voucher


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
            "ops_matrix_accounting/static/src/scss/ops_corporate_reports.scss",
        ],
        "web.report_assets_common": [
            "ops_matrix_accounting/static/src/css/ops_internal_report.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
