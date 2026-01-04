# -*- coding: utf-8 -*-
{
    'name': 'OPS Matrix Core',
    'version': '19.0.1.3',
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
        'purchase',
        'stock',
        'hr',  # Required for ops.persona employee_id field
    ],
    'data': [
        # Load in exact order
        # Data & Config (Groups must load first)
        'data/ir_module_category.xml',
        'data/res_groups.xml',
        
        # Security (depends on groups)
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        
        # Sequences and core data
        'data/ir_sequence_data.xml',
        
        # Template Data Files (Active templates for reference)
        'data/templates/ops_persona_templates.xml',
        'data/templates/ops_governance_rule_templates.xml',
        'data/ops_governance_rule_three_way_match.xml',
        'data/templates/ops_sla_templates.xml',
        
        # Views - Main Structure (load Business Unit before Branch, as Branch references BU action)
        'views/ops_business_unit_views.xml',
        'views/ops_branch_views.xml',
        'views/res_company_views.xml',
        'views/ops_inter_branch_transfer_views.xml',
        
        # Views - Persona Engine
        'views/ops_persona_views.xml',
        'views/ops_persona_delegation_views.xml',
        'views/res_users_views.xml',
        
        # Views - Governance & Approvals
        'views/ops_approval_request_views.xml',
        'views/ops_governance_rule_views.xml',
        'views/ops_approval_dashboard_views.xml',
        'views/ops_governance_violation_report_views.xml',
        'views/ops_three_way_match_views.xml',
        'views/ops_archive_policy_views.xml',
        'views/ops_analytic_views.xml',
        'views/ops_report_template_views.xml',
        
        # Views - SLA
        'views/ops_sla_template_views.xml',
        'views/ops_sla_instance_views.xml',
        
        # Views - Dashboards (CE compatible)
        'views/ops_executive_dashboard_views.xml',
        'views/ops_branch_dashboard_views.xml',
        'views/ops_bu_dashboard_views.xml',
        'views/ops_sales_dashboard_views.xml',
        
        'views/ops_dashboard_config_views.xml',
        
        # Views - Standard Model Extensions
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_warehouse_orderpoint_views.xml',
        'views/ops_product_request_views.xml',
        'views/product_silo_views.xml',
        'views/account_report_views.xml',
        
        # Views - API Integration & Security
        'views/ops_api_key_views.xml',
        'views/ops_audit_log_views.xml',
        
        # Menus (must be loaded after all views with actions)
        'views/ops_dashboard_menu.xml',
        
        # Additional data
        'data/ir_cron_data.xml',
        'data/ir_cron_archiver.xml',
        'data/sale_order_actions.xml',
        'data/ir_cron_escalation.xml',
        'data/email_templates.xml',
        'data/ops_report_templates.xml',
        
        # Archive policy templates (inactive by default)
        'data/ops_archive_templates.xml',
        
        # Reports
        'reports/ops_products_availability_report.xml',
        'wizard/ops_approval_recall_wizard_views.xml',
        'wizard/ops_approval_reject_wizard_views.xml',
        'wizard/three_way_match_override_wizard_views.xml',
        'wizard/sale_order_import_wizard_views.xml',
        'wizard/apply_report_template_wizard_views.xml',
    ],
    'demo': [
        'demo/ops_demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_matrix_core/static/src/css/ops_theme.css',
            'ops_matrix_core/static/src/js/storage_guard.js',  # Load first for safety
            'ops_matrix_core/static/src/js/report_action_override.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}