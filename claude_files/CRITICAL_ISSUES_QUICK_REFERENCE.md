═══════════════════════════════════════════════════════════════════════════════
🔴 CRITICAL ISSUES SUMMARY - Quick Reference
═══════════════════════════════════════════════════════════════════════════════
Date: January 5, 2026

CRITICAL GAPS PREVENTING FEATURE USE:
═════════════════════════════════════════════════════════════════════════════════

🔴 EMERGENCY FIX #1: Financial Reporting Completely Broken
───────────────────────────────────────────────────────────
Issue: 6 financial report wizards are in code but:
  ❌ View XML files NOT loaded (not in manifest)
  ❌ No window actions created
  ❌ No menu items
  ❌ USERS CANNOT RUN FINANCIAL REPORTS

Models affected:
  - ops.financial.report.wizard
  - ops.general.ledger.wizard
  - ops.general.ledger.wizard.enhanced
  - ops.matrix.profitability.analysis
  - ops.company.consolidation
  - ops.consolidated.balance.sheet

Files to add to ops_matrix_accounting manifest:
  ✓ views/ops_financial_report_wizard_views.xml
  ✓ views/ops_general_ledger_wizard_views.xml
  ✓ views/ops_general_ledger_wizard_enhanced_views.xml
  ✓ report/ops_financial_report_template.xml
  ✓ report/ops_general_ledger_template.xml
  ✓ report/ops_consolidated_report_templates.xml

Actions to create:
  ✓ action_ops_financial_report_wizard
  ✓ action_ops_general_ledger_wizard
  ✓ action_ops_general_ledger_wizard_enhanced

Menu structure needed:
  OPS Matrix → Configuration → Reporting Tools → [Financial Reports]
    ├─ Generate Financial Report
    ├─ General Ledger Report
    └─ General Ledger (Enhanced)

───────────────────────────────────────────────────────────────────────────────

🔴 EMERGENCY FIX #2: Asset Disposal Not Accessible
───────────────────────────────────────────────────

Issue: Asset disposal wizard coded but completely inaccessible
  ❌ View XML NOT loaded
  ❌ No window action
  ❌ No menu entry
  ❌ USERS CANNOT DISPOSE OF ASSETS

Model: ops.asset.disposal.wizard

File to add to manifest:
  ✓ wizard/ops_asset_disposal_wizard_views.xml

Action to create:
  ✓ action_ops_asset_disposal_wizard

Menu item needed:
  OPS Matrix → Configuration → Asset Management → Asset Disposals

───────────────────────────────────────────────────────────────────────────────

🔴 EMERGENCY FIX #3: Approval Workflows Not Editable
─────────────────────────────────────────────────────

Issue: Approval workflow records exist but cannot be accessed
  ❌ No menu for ops.approval.workflow
  ❌ No menu for ops.approval.workflow.step
  ❌ APPROVAL CONFIGURATIONS IMMUTABLE

Models affected:
  - ops.approval.workflow (no menu)
  - ops.approval.workflow.step (no menu)

Actions needed:
  ✓ action_ops_approval_workflow
  ✓ action_ops_workflow_step

Menu structure needed:
  OPS Matrix → Governance → [Workflow Configuration]
    ├─ Approval Workflows
    └─ Workflow Steps

───────────────────────────────────────────────────────────────────────────────

🔴 CRITICAL FIX #4: Governance Configuration Inaccessible
──────────────────────────────────────────────────────────

Issue: 3 governance configuration models have no menus
  ❌ ops.governance.discount.limit (no menu)
  ❌ ops.governance.margin.rule (no menu)
  ❌ ops.governance.price.authority (no menu)
  ❌ ops.matrix.config (no menu)
  ❌ GOVERNANCE RULES CANNOT BE CONFIGURED

Actions needed:
  ✓ action_ops_discount_limit
  ✓ action_ops_margin_rule
  ✓ action_ops_price_authority
  ✓ action_ops_matrix_config

Menu structure needed:
  OPS Matrix → Governance → [Governance Limits]
    ├─ Discount Limits
    ├─ Margin Rules
    ├─ Price Authorities
    └─ Matrix Configuration

───────────────────────────────────────────────────────────────────────────────

🔴 CRITICAL FIX #5: Budget Line Items Not Manageable
────────────────────────────────────────────────────

Issue: Budget details exist but no way to edit them
  ❌ ops.budget.line model has no menu
  ❌ NO WAY TO MANAGE BUDGET DETAILS
  ❌ BUDGET FUNCTIONALITY INCOMPLETE

Model: ops.budget.line

Action needed:
  ✓ action_ops_budget_line

Menu item:
  OPS Matrix → Configuration → Budget Management → Budget Lines

───────────────────────────────────────────────────────────────────────────────

📊 COMPLETE LIST OF MISSING MODELS (No UI Access)
═════════════════════════════════════════════════════════════════════════════════

🔴 MUST FIX (Core functionality blocked):
├── ops.approval.workflow             → Menu: Governance → Workflow Configuration
├── ops.approval.workflow.step        → Menu: Governance → Workflow Configuration
├── ops.budget.line                   → Menu: Configuration → Budget Management
├── ops.governance.discount.limit     → Menu: Governance → Governance Limits
├── ops.governance.margin.rule        → Menu: Governance → Governance Limits
├── ops.governance.price.authority    → Menu: Governance → Governance Limits
├── ops.matrix.config                 → Menu: Configuration → Matrix Configuration
└── ops.security.audit                → Menu: Governance → Security → Security Audit

⚠️  SHOULD FIX (Reduced functionality):
├── ops.performance.indexes           → Menu: Configuration → Performance KPIs
├── ops.persona.delegation            → Menu: Governance → Active Delegations
├── ops.report.template.line          → Menu: Configuration → Report Templates
├── ops.security.rules                → Menu: Governance → Security → Security Rules
└── [Mixins - architecture only]

═════════════════════════════════════════════════════════════════════════════════

📋 MANIFEST FIXES NEEDED (25 Files Not Being Loaded)
═════════════════════════════════════════════════════════════════════════════════

FILE: /opt/gemini_odoo19/addons/ops_matrix_accounting/__manifest__.py
ADD TO 'data' LIST:
  ├── 'data/templates/ops_budget_templates.xml'
  ├── 'demo/ops_asset_demo.xml'
  ├── 'report/ops_consolidated_report_templates.xml'
  ├── 'report/ops_financial_report_template.xml'
  ├── 'report/ops_general_ledger_template.xml'
  ├── 'views/ops_financial_report_wizard_views.xml'
  ├── 'views/ops_general_ledger_wizard_enhanced_views.xml'
  ├── 'views/ops_general_ledger_wizard_views.xml'
  ├── 'wizard/ops_asset_disposal_wizard_views.xml'
  └── 'wizard/ops_asset_report_wizard.xml'

FILE: /opt/gemini_odoo19/addons/ops_matrix_core/__manifest__.py
ADD TO 'data' LIST:
  ├── 'data/ops_account_templates.xml'
  ├── 'data/ops_default_data.xml'
  ├── 'data/ops_default_data_clean.xml'
  ├── 'data/ops_governance_rule_templates.xml'
  ├── 'data/ops_governance_templates.xml'
  ├── 'data/ops_governance_templates_extended.xml'
  ├── 'data/ops_persona_templates.xml'
  ├── 'data/ops_product_templates.xml'
  ├── 'data/ops_sla_templates.xml'
  ├── 'data/product_rules.xml'
  ├── 'data/templates/ops_user_templates.xml'
  ├── 'demo/ops_demo_data.xml'
  ├── 'demo/ops_demo_data_clean.xml'
  └── 'views/sale_order_import_wizard_views.xml'

FILE: /opt/gemini_odoo19/addons/ops_matrix_reporting/__manifest__.py
ADD TO 'data' LIST:
  └── 'data/dashboard_data.xml'

═════════════════════════════════════════════════════════════════════════════════

🚀 IMPLEMENTATION CHECKLIST
═════════════════════════════════════════════════════════════════════════════════

Phase 1 - CRITICAL (Before any other changes):
  □ Update ops_matrix_core/__manifest__.py - add 14 missing files
  □ Update ops_matrix_accounting/__manifest__.py - add 10 missing files
  □ Update ops_matrix_reporting/__manifest__.py - add 1 missing file
  □ Run module upgrade: odoo -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting
  □ Test: Check database for new views loaded (SELECT COUNT(*) FROM ir_ui_view WHERE model LIKE 'ops.%')

Phase 2 - Create Missing Actions & Menus:
  □ Create views/ops_governance_config_menus.xml with all missing actions
  □ Create views/ops_financial_report_menus.xml with wizard menus
  □ Create views/ops_approval_workflow_menus.xml with workflow menus
  □ Update views/ops_dashboard_menu.xml to reorganize and add missing items
  □ Run module upgrade again
  □ Test: All menus appear in OPS Matrix menu

Phase 3 - Verification:
  □ Test financial report wizard opens
  □ Test asset disposal wizard opens
  □ Test approval workflow management opens
  □ Test governance limit configuration
  □ Test budget line editing
  □ Verify all actions resolve correctly

═════════════════════════════════════════════════════════════════════════════════

STATS BEFORE/AFTER FIX
═════════════════════════════════════════════════════════════════════════════════

BEFORE:
  Models in code:        66
  Models in DB:          59
  Models with menu:      28 (42% coverage) 🔴
  Wizards in code:       13
  Wizards with action:   1 (8% coverage) 🔴
  View files in code:    53
  View files loaded:     TBD (many not in manifest)
  XML files in manifest: 79
  XML files not loaded:  25 (24% waste!) 🔴

AFTER (Target):
  Models in code:        66
  Models in DB:          66 (100%)
  Models with menu:      35+ (53% coverage) ✓
  Wizards in code:       13
  Wizards with action:   13 (100%) ✓
  View files in code:    53
  View files loaded:     53 (100%) ✓
  XML files in manifest: 104
  XML files not loaded:  0 (0% waste!) ✓

═════════════════════════════════════════════════════════════════════════════════
