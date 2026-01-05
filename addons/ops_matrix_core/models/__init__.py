# -*- coding: utf-8 -*-

# ==================================================================
# CRITICAL: Import Order Matters - Dependencies!
# ==================================================================
# 1. Core Structure (Company → Branch → BU → Config → Mixin)
from . import res_company          # First: base Odoo model
from . import ops_branch            # Second: Branch model (depends on company)
from . import ops_business_unit     # Third: BU model (depends on branch)
from . import ops_matrix_config     # Fourth: Configuration model
from . import ops_mixin             # Fifth: Mixin (depends on branch/BU)
from . import ops_matrix_mixin      # Sixth: Matrix dimension propagation mixin
from . import ops_approval_mixin    # Approval locking mixin
from . import ops_segregation_of_duties  # SoD rule management
from . import ops_segregation_of_duties_mixin  # SoD enforcement mixin
from . import field_visibility           # Field visibility rules and mixin
from . import ops_analytic_mixin    # Analytic Mixin for financial models
from . import ops_analytic_setup    # Analytic accounting setup wizard
from . import ops_performance_indexes  # Performance optimization indexes

# 2. Security Engine (depends on user model)
from . import ops_security_rules    # Security rule engine
from . import ops_security_audit    # Security audit logging

# 2a. API Authentication & Audit Logging
from . import ops_api_key           # API key management
from . import ops_audit_log         # API audit logging

# 3. Persona Engine (depends on branch/BU)
from . import ops_persona
from . import ops_persona_delegation
from . import res_users

# 3a. Inter-Branch Transfers
from . import ops_inter_branch_transfer

# 4. Governance & Approvals
from . import ops_governance_mixin
from . import ops_governance_rule
from . import ops_governance_limits      # NEW: Related limit models
from . import ops_approval_request
from . import ops_approval_dashboard
from . import ops_governance_violation_report
from . import ops_archive_policy
from . import ops_three_way_match

# 5. SLA Engine
from . import ops_sla_mixin
from . import ops_sla_template
from . import ops_sla_instance

# 6. Dashboard Configuration
from . import ops_dashboard_config
from . import ops_dashboard_widget

# 7. Standard Model Extensions
from . import ir_actions_report  # Governance enforcement on PDF generation
from . import product
from . import partner
from . import pricelist
from . import sale_order
from . import purchase_order
from . import account_move
from . import account_payment
from . import stock_warehouse
from . import stock_warehouse_orderpoint
from . import stock_picking
from . import stock_move
from . import stock_quant
from . import mail_message
from . import ops_report_template
from . import ops_report_template_line

# 7. Product Requests
from . import ops_product_request

# 8. Wizards (Located in models folder currently)
from . import sale_order_import_wizard
from . import account_report

# Core OPS models
from . import ops_business_unit
from . import ops_branch
from . import ops_persona

# Security models
from . import ops_segregation_of_duties
from . import ops_segregation_of_duties_mixin
from . import field_visibility

# Approval workflow
from . import ops_approval_mixin

# Extended models
from . import sale_order
from . import purchase_order
from . import account_move
from . import account_payment
from . import stock_picking
from . import product
from . import stock_move
from . import stock_quant
