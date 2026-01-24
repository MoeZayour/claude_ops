# -*- coding: utf-8 -*-
{
    'name': 'OPS Matrix Core',
    'version': '19.0.1.11.0',
    'category': 'Operations',
    'summary': 'Core module for OPS Matrix Framework',
    'description': """
        OPS Matrix Framework - Core Module
        ==================================
        This module provides the foundation for the OPS Matrix Framework.
        It includes Company, Branch, Business Unit models and the security framework.
    """,
    'author': 'Gemini Agent',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'analytic',
        'account',
        'sale',
        'sale_management',
        'purchase',
        'stock',
        'stock_account',
        'hr',
    ],
    'data': [
        # 1. Base Framework
        'data/ir_module_category.xml',
        'data/res_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/ops_menus.xml',
        'data/ir_sequence_data.xml',
        'data/product_request_sequence.xml',
        'data/ops_account_templates.xml',

        # 2. ACTORS (Core Personas - REQUIRED)
        'data/ops_persona_templates.xml',
        'data/ops_user_templates.xml',

        # 3. DEFINITIONS
        'data/ops_sla_templates.xml',
        'data/ops_product_templates.xml',
        'data/ops_sod_default_rules.xml',
        'data/field_visibility_rules.xml',
        'data/product_rules.xml',

        # 4. MATRIX STRUCTURE (Base Only)
        'data/ops_governance_templates.xml',
        # REMOVED: 'data/ops_governance_templates_extended.xml' - Contains broken demo data with invalid references

        # 5. RULES (Base Only)
        'data/ops_governance_rule_templates.xml',

        # 6. Default Data
        'data/ops_default_data_clean.xml',

        # 7. Views & Actions (Standard Load)
        'data/sale_order_actions.xml',
        'views/ops_business_unit_views.xml',
        'views/ops_branch_views.xml',
        'views/res_company_views.xml',
        'views/ops_inter_branch_transfer_views.xml',
        'views/ops_persona_views.xml',
        'views/ops_persona_delegation_views.xml',
        'views/res_users_views.xml',
        'views/ops_approval_request_views.xml',
        'views/ops_approval_rule_views.xml',
        'views/ops_governance_rule_views.xml',
        'views/ops_approval_dashboard_views.xml',
        'views/ops_governance_violation_report_views.xml',
        'views/ops_three_way_match_views.xml',
        'views/ops_archive_policy_views.xml',
        'views/ops_analytic_views.xml',
        'views/ops_report_template_views.xml',
        'views/ops_sla_template_views.xml',
        'views/ops_sla_instance_views.xml',
        'views/ops_executive_dashboard_views.xml',
        'views/ops_branch_dashboard_views.xml',
        'views/ops_bu_dashboard_views.xml',
        'views/ops_sales_dashboard_views.xml',
        'views/ops_dashboard_config_views.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_warehouse_orderpoint_views.xml',
        'views/ops_product_request_views.xml',
        'views/product_silo_views.xml',
        'views/account_report_views.xml',
        'views/ops_api_key_views.xml',
        'views/ops_audit_log_views.xml',
        'views/ops_sod_views.xml',
        'views/field_visibility_views.xml',
        'views/ops_dashboard_widget_views.xml',

        # STUB VIEWS (Intentionally Excluded - Schema Only, No UI):
        # 'views/ops_session_manager_views.xml',
        # 'views/ops_ip_whitelist_views.xml',
        # 'views/ops_security_audit_enhanced_views.xml',
        # 'views/ops_performance_monitor_views.xml',

        # 8. Final Config
        'views/ops_settings_menu.xml',
        'views/ops_approvals_menu.xml',
        'views/ops_dashboards_menu.xml',
        'views/ops_dashboard_menu.xml',
        'data/ir_cron_data.xml',
        'data/ir_cron_archiver.xml',
        'data/ir_cron_escalation.xml',
        'data/email_templates.xml',
        'data/ops_report_templates.xml',
        'data/ops_archive_templates.xml',
        'reports/ops_products_availability_report.xml',
        'reports/sale_order_documentation_report.xml',
        'reports/sale_order_availability_report.xml',
        'wizard/ops_approval_recall_wizard_views.xml',
        'wizard/ops_approval_reject_wizard_views.xml',
        'wizard/three_way_match_override_wizard_views.xml',
        'wizard/apply_report_template_wizard_views.xml',
        'wizard/ops_sale_order_import_wizard_views.xml',
        'wizard/ops_purchase_order_import_wizard_views.xml',
        'views/sale_order_import_wizard_views.xml',

        # Phase 13: UAT Fixes
        'data/hide_duplicate_reports.xml',
    ],
    'demo': [
        'demo/ops_demo_data.xml',
        'demo/ops_demo_data_clean.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_matrix_core/static/src/css/ops_theme.css',
            'ops_matrix_core/static/src/js/storage_guard.js',
            'ops_matrix_core/static/src/js/report_action_override.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}