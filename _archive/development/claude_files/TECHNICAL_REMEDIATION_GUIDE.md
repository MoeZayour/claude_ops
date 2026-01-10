═══════════════════════════════════════════════════════════════════════════════
TECHNICAL REMEDIATION GUIDE: Missing UI Features
═══════════════════════════════════════════════════════════════════════════════

COMPLETE WALKTHROUGH WITH EXACT COMMANDS AND CODE

═══════════════════════════════════════════════════════════════════════════════
PART 1: MANIFEST FILE FIXES
═══════════════════════════════════════════════════════════════════════════════

FILE 1: ops_matrix_accounting/__manifest__.py
───────────────────────────────────────────────

CURRENT STATE:
  'data': [
      'data/ops_asset_data.xml',
      'report/ops_asset_report_templates.xml',
      'security/ir.model.access.csv',
      'security/ops_asset_security.xml',
      'views/accounting_menus.xml',
      'views/ops_asset_category_views.xml',
      'views/ops_asset_depreciation_views.xml',
      'views/ops_asset_views.xml',
      'views/ops_budget_views.xml',
      'views/ops_pdc_views.xml',
      'wizard/ops_asset_depreciation_wizard_views.xml',
  ],

REQUIRED CHANGES (Add 10 files):

Location: /opt/gemini_odoo19/addons/ops_matrix_accounting/__manifest__.py

Change the 'data' list to:
  'data': [
      # Existing files
      'data/ops_asset_data.xml',
      'report/ops_asset_report_templates.xml',
      'security/ir.model.access.csv',
      'security/ops_asset_security.xml',
      'views/accounting_menus.xml',
      'views/ops_asset_category_views.xml',
      'views/ops_asset_depreciation_views.xml',
      'views/ops_asset_views.xml',
      'views/ops_budget_views.xml',
      'views/ops_pdc_views.xml',
      'wizard/ops_asset_depreciation_wizard_views.xml',
      
      # NEW FILES TO ADD (below existing):
      'data/templates/ops_budget_templates.xml',
      'demo/ops_asset_demo.xml',
      'report/ops_consolidated_report_templates.xml',
      'report/ops_financial_report_template.xml',
      'report/ops_general_ledger_template.xml',
      'views/ops_financial_report_wizard_views.xml',
      'views/ops_general_ledger_wizard_enhanced_views.xml',
      'views/ops_general_ledger_wizard_views.xml',
      'wizard/ops_asset_disposal_wizard_views.xml',
      'wizard/ops_asset_report_wizard.xml',
  ],

File locations that MUST EXIST:
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/data/templates/ops_budget_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/demo/ops_asset_demo.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_consolidated_report_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_financial_report_template.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_general_ledger_template.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/views/ops_financial_report_wizard_views.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/views/ops_general_ledger_wizard_enhanced_views.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/views/ops_general_ledger_wizard_views.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_asset_disposal_wizard_views.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_asset_report_wizard.xml

───────────────────────────────────────────────────────────────────────────────

FILE 2: ops_matrix_core/__manifest__.py
────────────────────────────────────────

CURRENT STATE:
  'data': [
      'data/email_templates.xml',
      'data/ir_cron_archiver.xml',
      'data/ir_cron_data.xml',
      'data/ir_cron_escalation.xml',
      'data/ir_module_category.xml',
      'data/ir_sequence_data.xml',
      'data/ops_archive_templates.xml',
      'data/ops_governance_rule_three_way_match.xml',
      'data/ops_report_templates.xml',
      'data/res_groups.xml',
      'data/sale_order_actions.xml',
      'data/templates/ops_governance_rule_templates.xml',
      'data/templates/ops_persona_templates.xml',
      'data/templates/ops_sla_templates.xml',
      'reports/ops_products_availability_report.xml',
      'security/ir.model.access.csv',
      'security/ir_rule.xml',
      # ... view files ...
      'wizard/apply_report_template_wizard_views.xml',
      'wizard/ops_approval_recall_wizard_views.xml',
      'wizard/ops_approval_reject_wizard_views.xml',
      'wizard/sale_order_import_wizard_views.xml',
      'wizard/three_way_match_override_wizard_views.xml',
  ],

REQUIRED CHANGES (Add 14 files):

Add these to the 'data' list (best: after existing data files, before security files):

      'data/ops_account_templates.xml',
      'data/ops_default_data.xml',
      'data/ops_default_data_clean.xml',
      'data/ops_governance_rule_templates.xml',
      'data/ops_governance_templates.xml',
      'data/ops_governance_templates_extended.xml',
      'data/ops_persona_templates.xml',
      'data/ops_product_templates.xml',
      'data/ops_sla_templates.xml',
      'data/product_rules.xml',
      'data/templates/ops_user_templates.xml',
      'demo/ops_demo_data.xml',
      'demo/ops_demo_data_clean.xml',
      'views/sale_order_import_wizard_views.xml',

NOTE: Some files appear duplicated - review carefully
      'data/templates/ops_governance_rule_templates.xml' (already declared once)
      'data/templates/ops_persona_templates.xml' (already declared once)
      'data/templates/ops_sla_templates.xml' (already declared once)

Action: If duplicates found, keep only ONE copy in the list!

File locations that MUST EXIST:
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_account_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_default_data.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_default_data_clean.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_rule_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_governance_templates_extended.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_persona_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_product_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/ops_sla_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/product_rules.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/data/templates/ops_user_templates.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/demo/ops_demo_data.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/demo/ops_demo_data_clean.xml
  ✓ /opt/gemini_odoo19/addons/ops_matrix_core/views/sale_order_import_wizard_views.xml

───────────────────────────────────────────────────────────────────────────────

FILE 3: ops_matrix_reporting/__manifest__.py
──────────────────────────────────────────────

CURRENT STATE:
  'data': [
      'security/ir.model.access.csv',
      'security/ir_rule.xml',
      'views/ops_excel_export_wizard_views.xml',
      'views/ops_financial_analysis_views.xml',
      'views/ops_inventory_analysis_views.xml',
      'views/ops_sales_analysis_views.xml',
      'views/reporting_menu.xml',
  ],

REQUIRED CHANGES (Add 1 file):

Add to the 'data' list:
      'data/dashboard_data.xml',

File location that MUST EXIST:
  ✓ /opt/gemini_odoo19/addons/ops_matrix_reporting/data/dashboard_data.xml

═════════════════════════════════════════════════════════════════════════════════

PART 2: MODULE UPGRADE
═════════════════════════════════════════════════════════════════════════════════

After updating manifest files, run module upgrade:

COMMAND:
docker exec gemini_odoo19 odoo -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init

EXPECTED OUTPUT:
  INFO mz-db [module_updates] Starting upgrade...
  INFO mz-db [ir.model] Synced model...
  INFO mz-db [ir.ui.view] Loaded views...
  INFO mz-db Modules installed successfully

VALIDATION AFTER UPGRADE:
Run this command to verify views were loaded:

docker exec gemini_odoo19_db psql -U odoo -d mz-db -c \
  "SELECT COUNT(*) as loaded_views FROM ir_ui_view WHERE model LIKE 'ops.%';"

EXPECTED: Should be HIGHER than before upgrade (currently 87)
Target: 100+ views

═════════════════════════════════════════════════════════════════════════════════

PART 3: CREATING MISSING ACTIONS & MENUS
═════════════════════════════════════════════════════════════════════════════════

After manifest fixes work, create new XML files for missing actions.

FILE 1: ops_matrix_core/views/ops_governance_configuration_menus.xml
─────────────────────────────────────────────────────────────────────

Create file with this content:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">

        <!-- GOVERNANCE LIMITS MENU -->
        <menuitem id="menu_ops_governance_limits"
                  name="Governance Limits"
                  parent="ops_matrix.menu_ops_governance"
                  sequence="30"/>

        <!-- Discount Limits Action -->
        <record id="action_ops_governance_discount_limit" model="ir.actions.act_window">
            <field name="name">Discount Limits</field>
            <field name="res_model">ops.governance.discount.limit</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Define discount limits for different customer segments or scenarios
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_discount_limits"
                  name="Discount Limits"
                  parent="menu_ops_governance_limits"
                  action="action_ops_governance_discount_limit"
                  sequence="10"/>

        <!-- Margin Rules Action -->
        <record id="action_ops_governance_margin_rule" model="ir.actions.act_window">
            <field name="name">Margin Rules</field>
            <field name="res_model">ops.governance.margin.rule</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Configure minimum margin requirements for different products or channels
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_margin_rules"
                  name="Margin Rules"
                  parent="menu_ops_governance_limits"
                  action="action_ops_governance_margin_rule"
                  sequence="20"/>

        <!-- Price Authorities Action -->
        <record id="action_ops_governance_price_authority" model="ir.actions.act_window">
            <field name="name">Price Authorities</field>
            <field name="res_model">ops.governance.price.authority</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Define who has authority to approve price changes
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_price_authority"
                  name="Price Authorities"
                  parent="menu_ops_governance_limits"
                  action="action_ops_governance_price_authority"
                  sequence="30"/>

        <!-- WORKFLOW CONFIGURATION MENU -->
        <menuitem id="menu_ops_workflow_management"
                  name="Workflow Configuration"
                  parent="ops_matrix.menu_ops_governance"
                  sequence="35"/>

        <!-- Approval Workflows Action -->
        <record id="action_ops_approval_workflow" model="ir.actions.act_window">
            <field name="name">Approval Workflows</field>
            <field name="res_model">ops.approval.workflow</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Create and manage approval workflows for different document types
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_approval_workflows"
                  name="Approval Workflows"
                  parent="menu_ops_workflow_management"
                  action="action_ops_approval_workflow"
                  sequence="10"/>

        <!-- Workflow Steps Action -->
        <record id="action_ops_approval_workflow_step" model="ir.actions.act_window">
            <field name="name">Workflow Steps</field>
            <field name="res_model">ops.approval.workflow.step</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Define the approval steps within workflows
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_workflow_steps"
                  name="Workflow Steps"
                  parent="menu_ops_workflow_management"
                  action="action_ops_approval_workflow_step"
                  sequence="20"/>

        <!-- MATRIX CONFIGURATION ACTION -->
        <record id="action_ops_matrix_config" model="ir.actions.act_window">
            <field name="name">Matrix Configuration</field>
            <field name="res_model">ops.matrix.config</field>
            <field name="view_mode">form</field>
            <field name="target">main</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Configure OPS Matrix dimensions and settings
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_matrix_config"
                  name="Matrix Configuration"
                  parent="ops_matrix.menu_ops_config"
                  action="action_ops_matrix_config"
                  sequence="40"/>

        <!-- SECURITY MANAGEMENT MENU -->
        <menuitem id="menu_ops_security_management"
                  name="Security Management"
                  parent="ops_matrix.menu_ops_governance"
                  sequence="40"/>

        <!-- Security Audit Action -->
        <record id="action_ops_security_audit" model="ir.actions.act_window">
            <field name="name">Security Audits</field>
            <field name="res_model">ops.security.audit</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Review security audit logs and compliance reports
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_security_audit"
                  name="Security Audit"
                  parent="menu_ops_security_management"
                  action="action_ops_security_audit"
                  sequence="10"/>

        <!-- Security Rules Action -->
        <record id="action_ops_security_rules" model="ir.actions.act_window">
            <field name="name">Security Rules</field>
            <field name="res_model">ops.security.rules</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Define and manage security rules
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_security_rules"
                  name="Security Rules"
                  parent="menu_ops_security_management"
                  action="action_ops_security_rules"
                  sequence="20"/>

        <!-- PERFORMANCE & ANALYSIS MENU -->
        <menuitem id="menu_ops_performance_analysis"
                  name="Performance & Analysis"
                  parent="ops_matrix.menu_ops_config"
                  sequence="30"/>

        <!-- Performance Indexes Action -->
        <record id="action_ops_performance_indexes" model="ir.actions.act_window">
            <field name="name">Performance KPIs</field>
            <field name="res_model">ops.performance.indexes</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Manage and track key performance indicators
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_performance_indexes"
                  name="Performance KPIs"
                  parent="menu_ops_performance_analysis"
                  action="action_ops_performance_indexes"
                  sequence="10"/>

    </data>
</odoo>
```

Then add to manifest:
  'views/ops_governance_configuration_menus.xml',

───────────────────────────────────────────────────────────────────────────────

FILE 2: ops_matrix_accounting/views/ops_financial_wizard_menus.xml
──────────────────────────────────────────────────────────────────

Create file with this content:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">

        <!-- REPORTING TOOLS SUBMENU (if not already defined) -->
        <menuitem id="menu_ops_reporting_tools"
                  name="Reporting Tools"
                  parent="ops_matrix.menu_ops_config"
                  sequence="35"/>

        <!-- Financial Reports Submenu -->
        <menuitem id="menu_ops_financial_reports"
                  name="Financial Reports"
                  parent="menu_ops_reporting_tools"
                  sequence="10"/>

        <!-- Financial Report Wizard Action -->
        <record id="action_ops_financial_report_wizard" model="ir.actions.act_window">
            <field name="name">Generate Financial Report</field>
            <field name="res_model">ops.financial.report.wizard</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Generate comprehensive financial reports with customizable parameters
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_financial_report_wizard"
                  name="Financial Report"
                  parent="menu_ops_financial_reports"
                  action="action_ops_financial_report_wizard"
                  sequence="10"/>

        <!-- General Ledger Wizard Action -->
        <record id="action_ops_general_ledger_wizard" model="ir.actions.act_window">
            <field name="name">General Ledger Report</field>
            <field name="res_model">ops.general.ledger.wizard</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Generate standard general ledger reports
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_general_ledger_wizard"
                  name="General Ledger"
                  parent="menu_ops_financial_reports"
                  action="action_ops_general_ledger_wizard"
                  sequence="20"/>

        <!-- General Ledger Enhanced Wizard Action -->
        <record id="action_ops_general_ledger_wizard_enhanced" model="ir.actions.act_window">
            <field name="name">General Ledger (Enhanced)</field>
            <field name="res_model">ops.general.ledger.wizard.enhanced</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Generate general ledger reports with matrix dimensions
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_general_ledger_wizard_enhanced"
                  name="General Ledger (Enhanced)"
                  parent="menu_ops_financial_reports"
                  action="action_ops_general_ledger_wizard_enhanced"
                  sequence="30"/>

        <!-- Consolidation Reports Submenu -->
        <menuitem id="menu_ops_consolidation_reports"
                  name="Consolidation Reports"
                  parent="menu_ops_reporting_tools"
                  sequence="20"/>

        <!-- Profitability Analysis Wizard Action -->
        <record id="action_ops_matrix_profitability_analysis" model="ir.actions.act_window">
            <field name="name">Matrix Profitability Analysis</field>
            <field name="res_model">ops.matrix.profitability.analysis</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Analyze profitability by branch and business unit
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_matrix_profitability_analysis"
                  name="Profitability Analysis"
                  parent="menu_ops_consolidation_reports"
                  action="action_ops_matrix_profitability_analysis"
                  sequence="10"/>

        <!-- Company Consolidation Wizard Action -->
        <record id="action_ops_company_consolidation" model="ir.actions.act_window">
            <field name="name">Financial Consolidation</field>
            <field name="res_model">ops.company.consolidation</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Consolidate financials across multiple companies
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_company_consolidation"
                  name="Company Consolidation"
                  parent="menu_ops_consolidation_reports"
                  action="action_ops_company_consolidation"
                  sequence="20"/>

        <!-- Consolidated Balance Sheet Wizard Action -->
        <record id="action_ops_consolidated_balance_sheet" model="ir.actions.act_window">
            <field name="name">Consolidated Balance Sheet</field>
            <field name="res_model">ops.consolidated.balance.sheet</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Generate consolidated balance sheet reports
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_consolidated_balance_sheet"
                  name="Balance Sheet"
                  parent="menu_ops_consolidation_reports"
                  action="action_ops_consolidated_balance_sheet"
                  sequence="30"/>

        <!-- Asset Disposal Menu -->
        <menuitem id="menu_ops_asset_disposal"
                  name="Asset Disposals"
                  parent="menu_ops_reporting_tools"
                  sequence="30"/>

        <!-- Asset Disposal Wizard Action -->
        <record id="action_ops_asset_disposal_wizard" model="ir.actions.act_window">
            <field name="name">Dispose Asset</field>
            <field name="res_model">ops.asset.disposal.wizard</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Process asset disposals and removals
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_asset_disposal_wizard"
                  name="Dispose Asset"
                  parent="menu_ops_asset_disposal"
                  action="action_ops_asset_disposal_wizard"
                  sequence="10"/>

    </data>
</odoo>
```

Then add to manifest:
  'views/ops_financial_wizard_menus.xml',

───────────────────────────────────────────────────────────────────────────────

FILE 3: ops_matrix_core/views/ops_budget_menus.xml
──────────────────────────────────────────────────

Create file with this content:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">

        <!-- BUDGET MANAGEMENT MENU -->
        <menuitem id="menu_ops_budget_management"
                  name="Budget Management"
                  parent="ops_matrix.menu_ops_config"
                  sequence="28"/>

        <!-- Budget Lines Action -->
        <record id="action_ops_budget_line" model="ir.actions.act_window">
            <field name="name">Budget Lines</field>
            <field name="res_model">ops.budget.line</field>
            <field name="view_mode">tree,form</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Manage individual budget line items
                </p>
            </field>
        </record>

        <menuitem id="menu_ops_budget_line"
                  name="Budget Lines"
                  parent="menu_ops_budget_management"
                  action="action_ops_budget_line"
                  sequence="10"/>

    </data>
</odoo>
```

Then add to manifest:
  'views/ops_budget_menus.xml',

═════════════════════════════════════════════════════════════════════════════════

PART 4: FINAL MODULE UPGRADE
═════════════════════════════════════════════════════════════════════════════════

After adding all new XML files and updating manifests:

STEP 1: Add all new menu files to manifests:

ops_matrix_core/__manifest__.py - add to 'data':
  'views/ops_governance_configuration_menus.xml',
  'views/ops_budget_menus.xml',

ops_matrix_accounting/__manifest__.py - add to 'data':
  'views/ops_financial_wizard_menus.xml',

STEP 2: Run final module upgrade:

docker exec gemini_odoo19 odoo -d mz-db -u ops_matrix_core,ops_matrix_accounting --stop-after-init

STEP 3: Validate results:

# Check actions created:
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c \
  "SELECT name, res_model FROM ir_act_window WHERE res_model LIKE 'ops.%' ORDER BY res_model;"

# Check models with menus:
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c \
  "SELECT DISTINCT w.res_model FROM ir_act_window w 
   JOIN ir_ui_menu m ON m.action = CONCAT('ir.actions.act_window,', w.id) 
   WHERE w.res_model LIKE 'ops.%' ORDER BY w.res_model;"

# Check menu structure:
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c \
  "SELECT REPEAT('  ', (SELECT COUNT(*) FROM ir_ui_menu m2 
                        WHERE m2.id IN (SELECT parent_id FROM ir_ui_menu 
                                       WHERE parent_id IS NOT NULL) 
                        AND m2.parent_id = ir_ui_menu.parent_id)) || name 
   FROM ir_ui_menu WHERE parent_id IN (SELECT id FROM ir_ui_menu WHERE name LIKE '%OPS%') 
   ORDER BY sequence, name;"

═════════════════════════════════════════════════════════════════════════════════
