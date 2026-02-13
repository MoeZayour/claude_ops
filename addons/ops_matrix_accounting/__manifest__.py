{
    "name": "OPS Matrix - Accounting",
    "version": "19.0.21.0.0",  # Wave 9 — Report Engine v2 rewrite (Phase 0: archive)
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
        "data/ops_seed_fiscal.xml",

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
        "views/res_company_report_colors_views.xml",
        # ARCHIVED v1: "views/ops_general_ledger_wizard_enhanced_views.xml",
        "views/ops_matrix_snapshot_views.xml",
        "views/ops_trend_analysis_views.xml",
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
        "wizard/ops_financial_wizard_views.xml",

        # Menus - must load AFTER all views/wizards that define actions
        "views/accounting_menus.xml",

        # Report Engine v2 - Templates (base → shapes → actions → configs)
        "report/ops_report_base.xml",
        "report/ops_report_shape_lines.xml",
        "report/ops_report_shape_hierarchy.xml",
        "report/ops_report_shape_matrix.xml",
        "report/ops_report_actions.xml",
        "report/ops_report_configs.xml",

        # Reports - Kept
        "report/ops_corporate_report_layout.xml",
        # ARCHIVED v1: "report/components/ops_corporate_report_components.xml",
        # ARCHIVED v1: "report/ops_asset_report_templates.xml",
        # ARCHIVED v1: "report/ops_consolidated_report_templates.xml",
        # ARCHIVED v1: "report/ops_financial_report_template.xml",
        # ARCHIVED v1: "report/ops_general_ledger_template.xml",
        # ARCHIVED v1: "report/ops_inventory_report_templates.xml",
        # ARCHIVED v1: "report/ops_treasury_report_templates.xml",
        # ARCHIVED v1: "report/ops_daily_report_templates.xml",
        # ARCHIVED v1: "report/ops_partner_ledger_corporate.xml",
        # ARCHIVED v1: "report/ops_budget_vs_actual_corporate.xml",
        "report/ops_report_invoice.xml",
        "report/ops_report_payment.xml",
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
