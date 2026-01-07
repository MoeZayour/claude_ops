# OPS FRAMEWORK - COMPLETE FIX & ENHANCEMENT
## Multi-Phase Systematic Implementation

**Objective**: Fix all critical bugs, reorganize menus, and unify UI styling in systematic phases.

**Working Directory**: `/opt/gemini_odoo19/addons/`

**Target Modules**:
- ops_matrix_core
- ops_matrix_accounting  
- ops_matrix_reporting
- ops_matrix_asset_management

---

## ⚠️ CRITICAL RULES

1. **Complete each phase before moving to next**
2. **Report after EVERY phase**
3. **Stop if ANY task fails - report immediately**
4. **Validate XML after each file modification**
5. **Commit after each phase completes**
6. **Never skip validation steps**

---

# 📊 PHASE 1: FIX CRITICAL BUGS (System Breaking)

**Goal**: Restore basic system functionality

## Task 1.1: Fix Field Visibility Permission Block

**Problem**: Sales users blocked from accessing any pages

**File**: `ops_matrix_core/models/field_visibility.py`

**Find the check_field_visibility method and replace entire method**:

```python
@api.model
def check_field_visibility(self, model_name, field_name):
    """Check if field should be visible for current user"""
    # System Admin bypass - ALWAYS has access
    if self.env.user.has_group('base.group_system'):
        return True
    
    # Find applicable visibility rules
    rules = self.search([
        ('model_name', '=', model_name),
        ('field_name', '=', field_name),
        ('active', '=', True)
    ])
    
    # No rules = field is visible
    if not rules:
        return True
    
    # Check if current user is in any restricted group
    user_groups = self.env.user.groups_id
    for rule in rules:
        restricted_groups = rule.restricted_group_ids
        if any(group in user_groups for group in restricted_groups):
            return False  # User is in a restricted group
    
    # User not in any restricted groups = visible
    return True
```

**Validate**:
```bash
cd /opt/gemini_odoo19
python3 -m py_compile addons/ops_matrix_core/models/field_visibility.py
echo "Exit code: $?"
```

---

## Task 1.2: Fix Missing Asset Fields

**File**: `ops_matrix_asset_management/models/ops_asset.py`

**Add these fields to the OpsAsset class**:

```python
# Add after existing fields
book_value = fields.Monetary(
    string='Book Value',
    compute='_compute_book_value',
    store=True,
    currency_field='currency_id',
    help="Current book value (Acquisition Value - Depreciated Value)"
)

@api.depends('acquisition_value', 'depreciated_value')
def _compute_book_value(self):
    for asset in self:
        asset.book_value = asset.acquisition_value - asset.depreciated_value
```

**File**: `ops_matrix_asset_management/models/ops_asset_depreciation.py`

**Add these fields to the OpsAssetDepreciation class**:

```python
# Add after existing fields
move_id = fields.Many2one(
    'account.move',
    string='Journal Entry',
    readonly=True,
    copy=False,
    help="Accounting entry for this depreciation"
)

move_posted = fields.Boolean(
    related='move_id.posted',
    string='Posted',
    store=True,
    help="Whether the journal entry has been posted"
)
```

**Validate**:
```bash
python3 -m py_compile addons/ops_matrix_asset_management/models/ops_asset.py
python3 -m py_compile addons/ops_matrix_asset_management/models/ops_asset_depreciation.py
echo "Exit codes: $? (should be 0)"
```

---

## Task 1.3: Fix Missing View Definitions

**File**: `ops_matrix_asset_management/views/ops_asset_views.xml`

**Add tree view BEFORE the existing form view**:

```xml
<!-- OPS Asset Tree View -->
<record id="view_ops_asset_tree" model="ir.ui.view">
    <field name="name">ops.asset.tree</field>
    <field name="model">ops.asset</field>
    <field name="arch" type="xml">
        <tree decoration-danger="state == 'cancelled'"
              decoration-warning="state == 'disposed'"
              decoration-success="state == 'closed'"
              decoration-muted="active == False">
            <field name="name"/>
            <field name="code"/>
            <field name="category_id"/>
            <field name="acquisition_date"/>
            <field name="acquisition_value" sum="Total Value"/>
            <field name="book_value" sum="Book Value"/>
            <field name="state" widget="badge"
                   decoration-success="state in ('running', 'closed')"
                   decoration-warning="state == 'disposed'"
                   decoration-danger="state == 'cancelled'"
                   decoration-info="state == 'draft'"/>
            <field name="active" column_invisible="1"/>
        </tree>
    </field>
</record>

<!-- Update action to reference tree view -->
<record id="action_ops_asset" model="ir.actions.act_window">
    <field name="name">Assets</field>
    <field name="res_model">ops.asset</field>
    <field name="view_mode">tree,form</field>
    <field name="view_id" ref="view_ops_asset_tree"/>
</record>
```

**File**: `ops_matrix_accounting/views/ops_three_way_match_views.xml`

**Add tree view**:

```xml
<!-- Three-Way Match Tree View -->
<record id="view_ops_three_way_match_tree" model="ir.ui.view">
    <field name="name">ops.three.way.match.tree</field>
    <field name="model">ops.three.way.match</field>
    <field name="arch" type="xml">
        <tree decoration-danger="match_status == 'mismatch'"
              decoration-success="match_status == 'matched'"
              decoration-warning="match_status == 'partial'">
            <field name="name"/>
            <field name="purchase_order_id"/>
            <field name="receipt_id"/>
            <field name="invoice_id"/>
            <field name="match_status" widget="badge"/>
            <field name="total_amount"/>
        </tree>
    </field>
</record>

<!-- Update action -->
<record id="action_ops_three_way_match" model="ir.actions.act_window">
    <field name="name">Three-Way Match Report</field>
    <field name="res_model">ops.three.way.match</field>
    <field name="view_mode">tree,form</field>
    <field name="view_id" ref="view_ops_three_way_match_tree"/>
</record>
```

**File**: `ops_matrix_core/views/ops_api_views.xml`

**Add tree view**:

```xml
<!-- API Key Tree View -->
<record id="view_ops_api_key_tree" model="ir.ui.view">
    <field name="name">ops.api.key.tree</field>
    <field name="model">ops.api.key</field>
    <field name="arch" type="xml">
        <tree decoration-muted="active == False">
            <field name="name"/>
            <field name="key"/>
            <field name="user_id"/>
            <field name="expiry_date"/>
            <field name="active"/>
        </tree>
    </field>
</record>

<!-- Update action -->
<record id="action_ops_api_key" model="ir.actions.act_window">
    <field name="name">API Keys</field>
    <field name="res_model">ops.api.key</field>
    <field name="view_mode">tree,form</field>
    <field name="view_id" ref="view_ops_api_key_tree"/>
</record>
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_asset_management/views/ops_asset_views.xml
xmllint --noout addons/ops_matrix_accounting/views/ops_three_way_match_views.xml
xmllint --noout addons/ops_matrix_core/views/ops_api_views.xml
echo "Exit codes: $? (should be 0)"
```

---

## Task 1.4: Fix Budget Line Account Field

**File**: `ops_matrix_accounting/models/ops_budget.py`

**Find _compute_committed_amount method and replace**:

```python
@api.depends('account_id', 'budget_id.date_from', 'budget_id.date_to')
def _compute_committed_amount(self):
    """Compute committed amount from purchase orders"""
    for line in self:
        if not line.account_id or not line.budget_id:
            line.committed_amount = 0.0
            continue
        
        # Get PO lines where product's expense account matches our account
        domain = [
            ('order_id.state', 'in', ['purchase', 'done']),
            ('date_planned', '>=', line.budget_id.date_from),
            ('date_planned', '<=', line.budget_id.date_to),
        ]
        
        # Find PO lines with matching expense account
        po_lines = self.env['purchase.order.line'].search(domain)
        
        # Filter by account matching
        matching_lines = po_lines.filtered(
            lambda l: l.product_id.categ_id.property_account_expense_categ_id == line.account_id
        )
        
        line.committed_amount = sum(matching_lines.mapped('price_subtotal'))
```

**Validate**:
```bash
python3 -m py_compile addons/ops_matrix_accounting/models/ops_budget.py
echo "Exit code: $?"
```

---

## Task 1.5: Phase 1 Validation & Commit

```bash
cd /opt/gemini_odoo19

# Validate all Python files modified
echo "=== Validating Python Files ==="
python3 -m py_compile addons/ops_matrix_core/models/field_visibility.py
python3 -m py_compile addons/ops_matrix_asset_management/models/ops_asset.py
python3 -m py_compile addons/ops_matrix_asset_management/models/ops_asset_depreciation.py
python3 -m py_compile addons/ops_matrix_accounting/models/ops_budget.py

# Validate all XML files modified
echo "=== Validating XML Files ==="
xmllint --noout addons/ops_matrix_asset_management/views/ops_asset_views.xml
xmllint --noout addons/ops_matrix_accounting/views/ops_three_way_match_views.xml
xmllint --noout addons/ops_matrix_core/views/ops_api_views.xml

# Count modifications
echo "=== Files Modified ==="
git status --short | grep -E "\.py$|\.xml$" | wc -l

# Stage and commit
git add addons/ops_matrix_core/models/field_visibility.py
git add addons/ops_matrix_asset_management/models/ops_asset.py
git add addons/ops_matrix_asset_management/models/ops_asset_depreciation.py
git add addons/ops_matrix_accounting/models/ops_budget.py
git add addons/ops_matrix_asset_management/views/ops_asset_views.xml
git add addons/ops_matrix_accounting/views/ops_three_way_match_views.xml
git add addons/ops_matrix_core/views/ops_api_views.xml

git commit -m "fix: Phase 1 - Critical bugs fixed

FIXES APPLIED:
- Fixed field visibility permission blocking sales users (C1)
- Added missing book_value field to ops.asset (C2)
- Added missing move_id field to ops.asset.depreciation (C2)
- Fixed missing tree view definitions for Assets/API/3WM (C3)
- Fixed budget line account_id domain error (C2)

FILES MODIFIED:
- models/field_visibility.py
- models/ops_asset.py
- models/ops_asset_depreciation.py
- models/ops_budget.py
- views/ops_asset_views.xml
- views/ops_three_way_match_views.xml
- views/ops_api_views.xml

VALIDATION: All Python and XML files validated successfully

Refs: C1, C2, C3"

git push origin main

echo "=== Phase 1 Commit Info ==="
git log -1 --oneline
```

---

## 📋 PHASE 1 REPORT

Generate this report:

```bash
cat << 'REPORT_END'
================================================================================
PHASE 1 COMPLETE: Critical Bugs Fixed
================================================================================

Tasks Completed:
✅ 1.1: Field Visibility permission fix
✅ 1.2: Asset missing fields (book_value, move_id)
✅ 1.3: Missing view definitions (3 actions)
✅ 1.4: Budget line account field fix
✅ 1.5: Validation & commit

FILES MODIFIED:
Python Files: 4
- field_visibility.py
- ops_asset.py
- ops_asset_depreciation.py
- ops_budget.py

XML Files: 3
- ops_asset_views.xml
- ops_three_way_match_views.xml
- ops_api_views.xml

VALIDATION RESULTS:
Python Syntax: PASS (exit code 0)
XML Syntax: PASS (exit code 0)

GIT STATUS:
Branch: main
Commit: [SHOW HASH]
Pushed: YES

ISSUES ENCOUNTERED: [NONE or list any]

READY FOR PHASE 2: YES

TIME TAKEN: [ESTIMATE]

================================================================================
REPORT_END
```

**STOP HERE. Report above. Wait for confirmation before Phase 2.**

---

# 📊 PHASE 2: FIX HIGH PRIORITY BUGS

**Goal**: Restore core functionality

## Task 2.1: Make User Fields Optional

**File**: `ops_matrix_core/models/res_users.py`

**Find the field definitions and modify**:

```python
# In the res.users inheritance

default_branch_id = fields.Many2one(
    'ops.branch',
    string='Default Branch',
    required=False,  # Changed from True
    help="User's default branch for operations. Can be left empty for system users."
)

business_unit_id = fields.Many2one(
    'ops.business.unit',
    string='Business Unit',
    required=False,  # Changed from True
    compute='_compute_business_unit',
    store=True,
    help="Computed from default branch"
)

persona_ids = fields.Many2many(
    'ops.persona',
    'ops_persona_user_rel',
    'user_id',
    'persona_id',
    string='Personas',
    required=False,  # Changed from True
    help="User's assigned personas/roles"
)

@api.depends('default_branch_id')
def _compute_business_unit(self):
    """Compute BU from branch"""
    for user in self:
        if user.default_branch_id:
            user.business_unit_id = user.default_branch_id.business_unit_id
        else:
            user.business_unit_id = False
```

**Validate**:
```bash
python3 -m py_compile addons/ops_matrix_core/models/res_users.py
echo "Exit code: $?"
```

---

## Task 2.2: Unlock Product Category Fields

**File**: `ops_matrix_core/views/product_category_views.xml`

**Add or update this view**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Unlock Product Category Fields -->
    <record id="view_product_category_form_inherit_unlock" model="ir.ui.view">
        <field name="name">product.category.form.inherit.unlock</field>
        <field name="model">product.category</field>
        <field name="inherit_id" ref="stock_account.view_category_property_form"/>
        <field name="arch" type="xml">
            <!-- Remove readonly from cost method -->
            <xpath expr="//field[@name='property_cost_method']" position="attributes">
                <attribute name="readonly">0</attribute>
            </xpath>
            
            <!-- Remove readonly from valuation -->
            <xpath expr="//field[@name='property_valuation']" position="attributes">
                <attribute name="readonly">0</attribute>
            </xpath>
        </field>
    </record>
</odoo>
```

**Add to manifest if not already there**:
```python
'data': [
    # ...
    'views/product_category_views.xml',
],
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/product_category_views.xml
```

---

## Task 2.3: Fix Branch Field in Budget Form

**File**: `ops_matrix_accounting/models/ops_budget.py`

**Ensure these fields exist in OpsBudget model**:

```python
class OpsBudget(models.Model):
    _name = 'ops.budget'
    _description = 'OPS Budget'
    
    # Ensure these fields exist
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        domain="[('company_id', '=', company_id)]",
        help="Budget is specific to this branch"
    )
    
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        related='branch_id.business_unit_id',
        store=True,
        readonly=True
    )
```

**File**: `ops_matrix_accounting/views/ops_budget_views.xml`

**Find the branch_id field in form view and ensure it looks like this**:

```xml
<field name="branch_id" 
       domain="[('company_id', '=', company_id)]"
       context="{'default_company_id': company_id}"
       options="{'no_create': True, 'no_open': True}"/>
```

**Validate**:
```bash
python3 -m py_compile addons/ops_matrix_accounting/models/ops_budget.py
xmllint --noout addons/ops_matrix_accounting/views/ops_budget_views.xml
```

---

## Task 2.4: Add Financial Reports Menu

**File**: `ops_matrix_accounting/views/ops_report_menu.xml`

**Create this new file**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Financial Reports Wizard Action -->
    <record id="action_ops_financial_reports_wizard" model="ir.actions.act_window">
        <field name="name">Financial Reports</field>
        <field name="res_model">ops.report.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="context">{}</field>
    </record>
    
    <!-- Menu Item under Accounting > Reporting -->
    <menuitem id="menu_ops_financial_reports"
              name="Financial Reports"
              parent="account.menu_finance_reports"
              action="action_ops_financial_reports_wizard"
              sequence="5"
              groups="account.group_account_manager"/>
    
    <!-- Report Templates Menu -->
    <record id="action_ops_report_template" model="ir.actions.act_window">
        <field name="name">Report Templates</field>
        <field name="res_model">ops.report.template</field>
        <field name="view_mode">tree,form</field>
    </record>
    
    <menuitem id="menu_ops_report_templates"
              name="Report Templates"
              parent="account.menu_finance_reports"
              action="action_ops_report_template"
              sequence="90"
              groups="account.group_account_manager"/>
    
    <!-- Excel Export Wizard -->
    <record id="action_ops_excel_export" model="ir.actions.act_window">
        <field name="name">Excel Export</field>
        <field name="res_model">ops.excel.export.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
    
    <menuitem id="menu_ops_excel_export"
              name="Excel Export"
              parent="account.menu_finance_reports"
              action="action_ops_excel_export"
              sequence="95"
              groups="account.group_account_user"/>
</odoo>
```

**Add to manifest**:
```python
'data': [
    # ... existing files ...
    'views/ops_report_menu.xml',
],
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_accounting/views/ops_report_menu.xml
```

---

## Task 2.5: Phase 2 Validation & Commit

```bash
cd /opt/gemini_odoo19

# Validate all modifications
echo "=== Validating Python Files ==="
python3 -m py_compile addons/ops_matrix_core/models/res_users.py
python3 -m py_compile addons/ops_matrix_accounting/models/ops_budget.py

echo "=== Validating XML Files ==="
xmllint --noout addons/ops_matrix_core/views/product_category_views.xml
xmllint --noout addons/ops_matrix_accounting/views/ops_budget_views.xml
xmllint --noout addons/ops_matrix_accounting/views/ops_report_menu.xml

# Check manifest updates
grep -n "ops_report_menu.xml" addons/ops_matrix_accounting/__manifest__.py

# Stage and commit
git add addons/ops_matrix_core/models/res_users.py
git add addons/ops_matrix_core/views/product_category_views.xml
git add addons/ops_matrix_accounting/models/ops_budget.py
git add addons/ops_matrix_accounting/views/ops_budget_views.xml
git add addons/ops_matrix_accounting/views/ops_report_menu.xml
git add addons/ops_matrix_accounting/__manifest__.py

git commit -m "fix: Phase 2 - High priority bugs fixed

FIXES APPLIED:
- Made user BU/Branch/Persona fields optional (H1)
- Unlocked product category costing/valuation fields (H2)
- Fixed branch field in budget form showing companies (H3)
- Added Financial Reports menu under Accounting (H4)

FILES MODIFIED:
- models/res_users.py
- models/ops_budget.py
- views/product_category_views.xml (created)
- views/ops_budget_views.xml
- views/ops_report_menu.xml (created)
- __manifest__.py (accounting)

VALIDATION: All files validated successfully

Refs: H1, H2, H3, H4"

git push origin main

echo "=== Phase 2 Commit Info ==="
git log -1 --oneline
```

---

## 📋 PHASE 2 REPORT

```bash
cat << 'REPORT_END'
================================================================================
PHASE 2 COMPLETE: High Priority Bugs Fixed
================================================================================

Tasks Completed:
✅ 2.1: User fields optional (BU/Branch/Persona)
✅ 2.2: Product category fields unlocked
✅ 2.3: Branch field fixed in budget
✅ 2.4: Financial Reports menu added
✅ 2.5: Validation & commit

FILES MODIFIED:
Python Files: 2
- res_users.py
- ops_budget.py

XML Files: 3
- product_category_views.xml (created)
- ops_budget_views.xml
- ops_report_menu.xml (created)

Manifest Files: 1

VALIDATION RESULTS:
Python Syntax: PASS
XML Syntax: PASS

GIT STATUS:
Commit: [SHOW HASH]
Pushed: YES

ISSUES ENCOUNTERED: [NONE or list any]

READY FOR PHASE 3: YES

TIME TAKEN: [ESTIMATE]

================================================================================
REPORT_END
```

**STOP HERE. Report above. Wait for confirmation before Phase 3.**

---

# 📊 PHASE 3: MENU REORGANIZATION

**Goal**: Professional menu structure

## Task 3.1: Create Approvals Root Menu

**File**: `ops_matrix_core/views/ops_approvals_menu.xml`

**Create this new file**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Approvals Root Menu -->
    <menuitem id="menu_ops_approvals_root"
              name="Approvals"
              sequence="45"
              groups="ops_matrix_core.group_ops_manager,ops_matrix_core.group_ops_branch_manager"/>
    
    <!-- My Approvals Dashboard -->
    <menuitem id="menu_ops_my_approvals_dashboard"
              name="My Approvals"
              parent="menu_ops_approvals_root"
              action="action_ops_approval_dashboard"
              sequence="10"
              groups="ops_matrix_core.group_ops_manager"/>
    
    <!-- Pending Approvals List -->
    <record id="action_ops_pending_approvals" model="ir.actions.act_window">
        <field name="name">Pending Approvals</field>
        <field name="res_model">ops.approval.request</field>
        <field name="view_mode">tree,form</field>
        <field name="domain">[('state', '=', 'pending'), ('approver_id', '=', uid)]</field>
        <field name="context">{'default_state': 'pending'}</field>
    </record>
    
    <menuitem id="menu_ops_pending_approvals"
              name="Pending Approvals"
              parent="menu_ops_approvals_root"
              action="action_ops_pending_approvals"
              sequence="20"/>
    
    <!-- Approval History -->
    <menuitem id="menu_ops_approval_history"
              name="Approval History"
              parent="menu_ops_approvals_root"
              action="action_ops_approval_request"
              sequence="30"/>
    
    <!-- SLA Tracking -->
    <menuitem id="menu_ops_sla_tracking"
              name="SLA Tracking"
              parent="menu_ops_approvals_root"
              action="action_ops_sla_instance"
              sequence="40"
              groups="ops_matrix_core.group_ops_manager"/>
    
    <!-- Violations & Alerts -->
    <menuitem id="menu_ops_violations"
              name="Violations & Alerts"
              parent="menu_ops_approvals_root"
              action="action_ops_sod_violations"
              sequence="50"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
</odoo>
```

**Add to manifest**:
```python
'data': [
    # Load menus after actions
    'views/ops_approvals_menu.xml',
],
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/ops_approvals_menu.xml
```

---

## Task 3.2: Reorganize Settings Menu

**File**: `ops_matrix_core/views/ops_settings_menu.xml`

**Create this new file**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- OPS Framework Section in Settings -->
    <menuitem id="menu_ops_settings_root"
              name="OPS Framework"
              parent="base.menu_administration"
              sequence="100"
              groups="base.group_system"/>
    
    <!-- ========================================= -->
    <!-- COMPANY STRUCTURE                         -->
    <!-- ========================================= -->
    <menuitem id="menu_ops_company_structure"
              name="Company Structure"
              parent="menu_ops_settings_root"
              sequence="10"/>
    
    <menuitem id="menu_ops_business_unit"
              name="Business Units"
              parent="menu_ops_company_structure"
              action="action_ops_business_unit"
              sequence="10"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <menuitem id="menu_ops_branch"
              name="Branches"
              parent="menu_ops_company_structure"
              action="action_ops_branch"
              sequence="20"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <menuitem id="menu_ops_companies"
              name="Companies"
              parent="menu_ops_company_structure"
              action="base.action_res_company_form"
              sequence="30"
              groups="base.group_system"/>
    
    <!-- ========================================= -->
    <!-- SECURITY & GOVERNANCE                     -->
    <!-- ========================================= -->
    <menuitem id="menu_ops_security_governance"
              name="Security & Governance"
              parent="menu_ops_settings_root"
              sequence="20"/>
    
    <!-- Personas -->
    <menuitem id="menu_ops_persona"
              name="Personas"
              parent="menu_ops_security_governance"
              action="action_ops_persona"
              sequence="10"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <!-- Delegations -->
    <menuitem id="menu_ops_persona_delegation"
              name="Delegations"
              parent="menu_ops_security_governance"
              action="action_ops_persona_delegation"
              sequence="20"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <!-- SoD Rules -->
    <menuitem id="menu_ops_sod_root"
              name="SoD Rules"
              parent="menu_ops_security_governance"
              action="action_ops_sod_rules"
              sequence="30"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <!-- Field Visibility Rules -->
    <menuitem id="menu_ops_field_visibility_rules"
              name="Field Visibility Rules"
              parent="menu_ops_security_governance"
              action="action_ops_field_visibility_rule"
              sequence="40"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <!-- Governance Rules -->
    <menuitem id="menu_ops_governance_rules"
              name="Governance Rules"
              parent="menu_ops_security_governance"
              action="action_ops_governance_rule"
              sequence="50"
              groups="base.group_system,ops_matrix_core.group_ops_manager"/>
    
    <!-- Archive Policies -->
    <menuitem id="menu_ops_archive_policy"
              name="Archive Policies"
              parent="menu_ops_security_governance"
              action="action_ops_archive_policy"
              sequence="60"
              groups="base.group_system"/>
    
    <!-- ========================================= -->
    <!-- WORKFLOW CONFIGURATION                    -->
    <!-- ========================================= -->
    <menuitem id="menu_ops_workflow_config"
              name="Workflow Configuration"
              parent="menu_ops_settings_root"
              sequence="30"/>
    
    <!-- SLA Templates -->
    <menuitem id="menu_ops_sla_template"
              name="SLA Templates"
              parent="menu_ops_workflow_config"
              action="action_ops_sla_template"
              sequence="10"
              groups="base.group_system,ops_matrix_core.group_ops_admin"/>
    
    <!-- Dashboard Widgets -->
    <menuitem id="menu_ops_dashboard_widget"
              name="Dashboard Widgets"
              parent="menu_ops_workflow_config"
              action="action_ops_dashboard_widget_management"
              sequence="20"
              groups="base.group_system"/>
</odoo>
```

**Add to manifest**:
```python
'data': [
    # ...
    'views/ops_settings_menu.xml',
],
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/ops_settings_menu.xml
```

---

## Task 3.3: Move Dashboards to Native App

**File**: `ops_matrix_core/views/ops_dashboards_menu.xml`

**Create this new file**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Move OPS Dashboards under native Dashboards app -->
    
    <!-- Executive Dashboard -->
    <menuitem id="menu_ops_executive_dashboard"
              name="Executive Dashboard"
              parent="board.menu_board_root"
              action="action_ops_executive_dashboard"
              sequence="10"
              groups="ops_matrix_core.group_ops_executive,ops_matrix_core.group_ops_cfo,base.group_system"/>
    
    <!-- Branch Performance Dashboard -->
    <menuitem id="menu_ops_branch_dashboard"
              name="Branch Performance"
              parent="board.menu_board_root"
              action="action_ops_branch_manager_dashboard"
              sequence="20"
              groups="ops_matrix_core.group_ops_branch_manager,ops_matrix_core.group_ops_bu_leader,base.group_system"/>
    
    <!-- BU Performance Dashboard -->
    <menuitem id="menu_ops_bu_dashboard"
              name="BU Performance"
              parent="board.menu_board_root"
              action="action_ops_bu_leader_dashboard"
              sequence="30"
              groups="ops_matrix_core.group_ops_bu_leader,ops_matrix_core.group_ops_executive,base.group_system"/>
    
    <!-- Sales Performance Dashboard -->
    <menuitem id="menu_ops_sales_dashboard"
              name="Sales Performance"
              parent="board.menu_board_root"
              action="action_ops_sales_dashboard"
              sequence="40"
              groups="sales_team.group_sale_manager,base.group_system"/>
</odoo>
```

**Add to manifest**:
```python
'data': [
    # ...
    'views/ops_dashboards_menu.xml',
],
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/ops_dashboards_menu.xml
```

---

## Task 3.4: Disable API Integration Menus

**File**: `ops_matrix_core/views/ops_api_menu.xml`

**Find existing API menu items and add active="False"**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Disable API Integration menus (not priority) -->
    
    <record id="menu_ops_api_root" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>
    
    <record id="menu_ops_api_keys" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>
    
    <record id="menu_ops_audit_logs" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>
    
    <record id="menu_ops_api_analytics" model="ir.ui.menu">
        <field name="active" eval="False"/>
    </record>
</odoo>
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/ops_api_menu.xml
```

---

## Task 3.5: Disable OPS Matrix Root Menu

**File**: `ops_matrix_core/views/ops_dashboard_menu.xml`

**Find the OPS Matrix root menu and disable it**:

```xml
<!-- Disable old OPS Matrix root menu -->
<record id="menu_ops_matrix_root" model="ir.ui.menu">
    <field name="active" eval="False"/>
</record>
```

**Or if it's a menuitem, change to**:

```xml
<menuitem id="menu_ops_matrix_root"
          name="OPS Matrix"
          active="False"/>
```

**Validate**:
```bash
xmllint --noout addons/ops_matrix_core/views/ops_dashboard_menu.xml
```

---

## Task 3.6: Update Manifest Load Order

**File**: `ops_matrix_core/__manifest__.py`

**Ensure menus load in correct order**:

```python
'data': [
    # Security first
    'security/ir.model.access.csv',
    'security/ir_rule.xml',
    'data/res_groups.xml',
    
    # Actions before menus
    'views/ops_persona_views.xml',
    'views/ops_approval_views.xml',
    'views/ops_sla_views.xml',
    'views/ops_sod_views.xml',
    'views/field_visibility_views.xml',
    'views/ops_governance_views.xml',
    'views/ops_business_unit_views.xml',
    'views/ops_branch_views.xml',
    'views/ops_dashboard_views.xml',
    
    # Menus last
    'views/ops_settings_menu.xml',
    'views/ops_approvals_menu.xml',
    'views/ops_dashboards_menu.xml',
    'views/ops_dashboard_menu.xml',  # Contains root disable
    'views/ops_api_menu.xml',  # Contains API disable
],
```

---

## Task 3.7: Phase 3 Validation & Commit

```bash
cd /opt/gemini_odoo19

# Validate all menu XML files
echo "=== Validating Menu Files ==="
xmllint --noout addons/ops_matrix_core/views/ops_approvals_menu.xml
xmllint --noout addons/ops_matrix_core/views/ops_settings_menu.xml
xmllint --noout addons/ops_matrix_core/views/ops_dashboards_menu.xml
xmllint --noout addons/ops_matrix_core/views/ops_api_menu.xml
xmllint --noout addons/ops_matrix_core/views/ops_dashboard_menu.xml

# Count menu changes
echo "=== Menu Changes ==="
echo "New menu files created: 3"
echo "Modified menu files: 2"

# Stage and commit
git add addons/ops_matrix_core/views/ops_approvals_menu.xml
git add addons/ops_matrix_core/views/ops_settings_menu.xml
git add addons/ops_matrix_core/views/ops_dashboards_menu.xml
git add addons/ops_matrix_core/views/ops_api_menu.xml
git add addons/ops_matrix_core/views/ops_dashboard_menu.xml
git add addons/ops_matrix_core/__manifest__.py

git commit -m "refactor: Phase 3 - Menu reorganization complete

CHANGES APPLIED:
- Created Approvals root menu with 5 items (M7)
- Reorganized Settings with OPS Framework section
  - Company Structure (3 menus)
  - Security & Governance (6 menus)
  - Workflow Configuration (2 menus)
- Moved 4 dashboards to native Dashboards app
- Disabled API Integration menus (4 menus)
- Disabled OPS Matrix root menu

FILES CREATED:
- views/ops_approvals_menu.xml
- views/ops_settings_menu.xml
- views/ops_dashboards_menu.xml

FILES MODIFIED:
- views/ops_api_menu.xml (disabled menus)
- views/ops_dashboard_menu.xml (disabled root)
- __manifest__.py (load order)

MENU STRUCTURE:
New Menus: 11
Reorganized Menus: 15
Disabled Menus: 5

VALIDATION: All XML files validated

Refs: M7"

git push origin main

echo "=== Phase 3 Commit Info ==="
git log -1 --oneline
```

---

## 📋 PHASE 3 REPORT

```bash
cat << 'REPORT_END'
================================================================================
PHASE 3 COMPLETE: Menu Reorganization
================================================================================

Tasks Completed:
✅ 3.1: Approvals root menu created (5 items)
✅ 3.2: Settings menu reorganized (11 items)
✅ 3.3: Dashboards moved to native app (4 items)
✅ 3.4: API menus disabled (4 menus)
✅ 3.5: OPS Matrix root menu disabled
✅ 3.6: Manifest load order updated
✅ 3.7: Validation & commit

FILES CREATED:
- ops_approvals_menu.xml
- ops_settings_menu.xml
- ops_dashboards_menu.xml

FILES MODIFIED:
- ops_api_menu.xml
- ops_dashboard_menu.xml
- __manifest__.py

MENU SUMMARY:
New Structure:
  - Approvals: 5 menus
  - Settings > OPS Framework: 11 menus
  - Dashboards: 4 menus
Disabled:
  - OPS Matrix root
  - API Integration section

VALIDATION RESULTS:
XML Syntax: PASS

GIT STATUS:
Commit: [SHOW HASH]
Pushed: YES

ISSUES ENCOUNTERED: [NONE or list any]

READY FOR PHASE 4: YES

TIME TAKEN: [ESTIMATE]

================================================================================
REPORT_END
```

**STOP HERE. Report above. Wait for confirmation before Phase 4.**

---

# 📊 PHASE 4: UI STYLING UNIFICATION

**Goal**: Professional, consistent UI across all forms

## Task 4.1: Create CSS Theme File

**Create directory**:
```bash
mkdir -p addons/ops_matrix_core/static/src/css
```

**File**: `ops_matrix_core/static/src/css/ops_theme.css`

**Create this file**:

```css
/*
 * OPS Matrix Framework - UI Theme
 * Version: 1.0
 * Odoo 19 CE Compatible
 */

/* ============================================
   STATUS BAR COLORS
   ============================================ */

/* Draft State - Gray */
.o_statusbar_status .o_arrow_button[data-value="draft"],
.o_statusbar_status .o_arrow_button[data-value="new"] {
    --StatusBar-arrow-bg: #6c757d !important;
}

/* Confirmed/Validated State - Blue */
.o_statusbar_status .o_arrow_button[data-value="confirmed"],
.o_statusbar_status .o_arrow_button[data-value="validated"],
.o_statusbar_status .o_arrow_button[data-value="open"] {
    --StatusBar-arrow-bg: #007bff !important;
}

/* Approved State - Teal */
.o_statusbar_status .o_arrow_button[data-value="approved"],
.o_statusbar_status .o_arrow_button[data-value="running"] {
    --StatusBar-arrow-bg: #17a2b8 !important;
}

/* Posted/Done State - Green */
.o_statusbar_status .o_arrow_button[data-value="posted"],
.o_statusbar_status .o_arrow_button[data-value="done"],
.o_statusbar_status .o_arrow_button[data-value="collected"],
.o_statusbar_status .o_arrow_button[data-value="completed"],
.o_statusbar_status .o_arrow_button[data-value="closed"] {
    --StatusBar-arrow-bg: #28a745 !important;
}

/* Cancelled/Rejected State - Red */
.o_statusbar_status .o_arrow_button[data-value="cancelled"],
.o_statusbar_status .o_arrow_button[data-value="rejected"],
.o_statusbar_status .o_arrow_button[data-value="bounced"] {
    --StatusBar-arrow-bg: #dc3545 !important;
}

/* Pending/Hold State - Yellow */
.o_statusbar_status .o_arrow_button[data-value="pending"],
.o_statusbar_status .o_arrow_button[data-value="hold"],
.o_statusbar_status .o_arrow_button[data-value="deposited"] {
    --StatusBar-arrow-bg: #ffc107 !important;
}

/* ============================================
   BUTTON ENHANCEMENTS
   ============================================ */

/* Primary button subtle shadow */
.o_form_view .o_form_statusbar .btn-primary {
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.25);
}

/* Danger button confirmation highlight */
.o_form_view .o_form_statusbar .btn-danger {
    box-shadow: 0 2px 4px rgba(220, 53, 69, 0.25);
}

/* ============================================
   NOTEBOOK TAB ICONS
   ============================================ */

.o_notebook .nav-link .fa {
    margin-right: 6px;
    opacity: 0.8;
}

/* ============================================
   MONETARY FIELD COLORS
   ============================================ */

.o_field_monetary.text-danger,
.o_list_table .text-danger {
    color: #dc3545 !important;
}

.o_field_monetary.text-success,
.o_list_table .text-success {
    color: #28a745 !important;
}

/* ============================================
   KANBAN CARD STATES
   ============================================ */

.o_kanban_record.oe_kanban_color_0 { 
    border-left: 3px solid #6c757d; 
}  /* Draft */

.o_kanban_record.oe_kanban_color_1 { 
    border-left: 3px solid #007bff; 
}  /* Confirmed */

.o_kanban_record.oe_kanban_color_2 { 
    border-left: 3px solid #28a745; 
}  /* Done */

.o_kanban_record.oe_kanban_color_3 { 
    border-left: 3px solid #dc3545; 
}  /* Cancelled */

.o_kanban_record.oe_kanban_color_4 { 
    border-left: 3px solid #ffc107; 
}  /* Warning */
```

**Update Manifest**:

**File**: `ops_matrix_core/__manifest__.py`

```python
# Add assets section if not exists
'assets': {
    'web.assets_backend': [
        'ops_matrix_core/static/src/css/ops_theme.css',
    ],
},
```

**Validate**:
```bash
ls -la addons/ops_matrix_core/static/src/css/ops_theme.css
```

---

## Task 4.2: Add Chatter to Forms

**Add mail.thread inheritance to models**:

For each model that doesn't have it, add:

```python
class ModelName(models.Model):
    _name = 'model.name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Model Description'
```

**Apply to these models**:
1. `ops_matrix_core/models/ops_inter_branch_transfer.py`
2. `ops_matrix_core/models/ops_product_request.py`
3. `ops_matrix_accounting/models/ops_budget.py`
4. `ops_matrix_accounting/models/ops_pdc.py`
5. `ops_matrix_asset_management/models/ops_asset.py`

**Add chatter to form views** (add after `</sheet>` closing tag):

```xml
<!-- Chatter -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

**Apply to these view files**:
1. `ops_matrix_core/views/ops_inter_branch_transfer_views.xml`
2. `ops_matrix_core/views/ops_product_request_views.xml`
3. `ops_matrix_accounting/views/ops_budget_views.xml`
4. `ops_matrix_accounting/views/ops_pdc_views.xml`
5. `ops_matrix_asset_management/views/ops_asset_views.xml`

**Validate**:
```bash
# Validate Python
find addons/ops_matrix_*/models -name "*.py" -exec python3 -m py_compile {} \;

# Validate XML
find addons/ops_matrix_*/views -name "*_views.xml" -exec xmllint --noout {} \;
```

---

## Task 4.3: Standardize Form Button Headers

**Apply this button pattern to ALL form headers**:

```xml
<header>
    <!-- Status bar - ALWAYS first -->
    <field name="state" widget="statusbar" 
           statusbar_visible="draft,confirmed,done"/>
    
    <!-- ONE primary button only -->
    <button name="action_confirm" 
            type="object" 
            string="Confirm"
            class="btn-primary" 
            icon="fa-check"
            invisible="state != 'draft'"
            data-hotkey="v"/>
    
    <!-- Secondary actions -->
    <button name="action_compute" 
            type="object" 
            string="Calculate"
            class="btn-secondary" 
            icon="fa-calculator"
            invisible="state != 'draft'"/>
    
    <!-- Success actions (green) -->
    <button name="action_approve" 
            type="object" 
            string="Approve"
            class="btn-success" 
            icon="fa-thumbs-up"
            invisible="state != 'confirmed'"
            groups="ops_matrix_core.group_ops_manager"/>
    
    <!-- Danger actions (red) with confirm -->
    <button name="action_cancel" 
            type="object" 
            string="Cancel"
            class="btn-danger" 
            icon="fa-times"
            invisible="state in ('done', 'cancelled')"
            confirm="Are you sure you want to cancel this record?"/>
    
    <!-- Warning actions (yellow) -->
    <button name="action_draft" 
            type="object" 
            string="Reset to Draft"
            class="btn-warning" 
            icon="fa-undo"
            invisible="state != 'cancelled'"
            groups="base.group_system"/>
</header>
```

**Apply to these forms**:
- ops_asset_views.xml
- ops_pdc_views.xml  
- ops_budget_views.xml
- ops_inter_branch_transfer_views.xml
- ops_product_request_views.xml

---

## Task 4.4: Add Notebook Tab Icons

**Add icons to all notebook pages**:

```xml
<notebook>
    <page string="General Information" name="general" icon="fa-info-circle">
        <!-- content -->
    </page>
    <page string="Lines/Items" name="lines" icon="fa-list">
        <!-- content -->
    </page>
    <page string="Accounting" name="accounting" icon="fa-book">
        <!-- content -->
    </page>
    <page string="Depreciation" name="depreciation" icon="fa-line-chart">
        <!-- content -->
    </page>
    <page string="Notes" name="notes" icon="fa-sticky-note">
        <!-- content -->
    </page>
    <page string="Documents" name="documents" icon="fa-paperclip">
        <!-- content -->
    </page>
</notebook>
```

**Apply to all forms with notebooks**

---

## Task 4.5: Add Tree View Decorations

**Apply this decoration pattern to ALL tree views**:

```xml
<tree decoration-danger="state in ('cancelled', 'bounced', 'rejected')"
      decoration-warning="state in ('pending', 'hold')"
      decoration-success="state in ('done', 'posted', 'collected')"
      decoration-muted="active == False">
    
    <field name="name"/>
    <!-- other fields -->
    
    <!-- State field with badge -->
    <field name="state" 
           widget="badge"
           decoration-success="state == 'done'"
           decoration-warning="state == 'pending'"
           decoration-danger="state == 'cancelled'"
           decoration-info="state == 'draft'"/>
    
    <!-- Hidden fields for decorations -->
    <field name="active" column_invisible="1"/>
</tree>
```

**Apply to all tree views in**:
- ops_asset_views.xml
- ops_pdc_views.xml
- ops_budget_views.xml
- ops_inter_branch_transfer_views.xml
- ops_product_request_views.xml

---

## Task 4.6: Phase 4 Validation & Commit

```bash
cd /opt/gemini_odoo19

# Validate CSS exists
echo "=== Checking CSS File ==="
ls -lh addons/ops_matrix_core/static/src/css/ops_theme.css

# Validate all Python (mail.thread inheritance)
echo "=== Validating Python Files ==="
find addons/ops_matrix_*/models -name "*.py" -exec python3 -m py_compile {} \;

# Validate all XML
echo "=== Validating XML Files ==="
find addons/ops_matrix_*/views -name "*.xml" -exec xmllint --noout {} \;

# Count modifications
echo "=== Forms Modified ==="
grep -r "oe_chatter" addons/ops_matrix_*/views/*.xml | wc -l

# Stage and commit
git add addons/ops_matrix_core/static/src/css/ops_theme.css
git add addons/ops_matrix_core/__manifest__.py
git add addons/ops_matrix_*/models/*.py
git add addons/ops_matrix_*/views/*.xml

git commit -m "style: Phase 4 - UI styling unification

STYLING APPLIED:
- Created ops_theme.css with professional color scheme (M8)
- Added status bar colors (6 states)
- Enhanced button styling with shadows
- Added chatter to 5 forms with mail.thread
- Standardized button headers (8 forms)
  - One primary button per form
  - Danger buttons with confirm dialogs
  - Consistent icons (fa-check, fa-times, etc.)
- Added notebook tab icons
- Applied tree view decorations
  - Color coding by state
  - Badge widgets for status fields

FILES MODIFIED:
CSS Files: 1 (created)
Python Files: 5 (mail.thread inheritance)
XML View Files: 8+
Manifest Files: 1

FORMS WITH CHATTER:
- Inter-Branch Transfers
- Product Requests
- Budget Control
- PDC Receivable/Payable
- Assets

STYLING ELEMENTS:
- Status bar colors: 6 states
- Button classes: 5 types
- Tree decorations: 4 states
- Notebook icons: 6 common icons

VALIDATION: All files validated

Refs: M8"

git push origin main

echo "=== Phase 4 Commit Info ==="
git log -1 --oneline
```

---

## 📋 PHASE 4 REPORT

```bash
cat << 'REPORT_END'
================================================================================
PHASE 4 COMPLETE: UI Styling Unification
================================================================================

Tasks Completed:
✅ 4.1: CSS theme file created (ops_theme.css)
✅ 4.2: Chatter added to 5 forms
✅ 4.3: Button headers standardized (8 forms)
✅ 4.4: Notebook icons added to all tabs
✅ 4.5: Tree decorations applied
✅ 4.6: Validation & commit

FILES CREATED:
- static/src/css/ops_theme.css

FILES MODIFIED:
Python Models: 5
- Added mail.thread inheritance

XML Views: 8+
- Added chatter
- Standardized headers
- Added icons
- Added decorations

STYLING SUMMARY:
Forms with Chatter: 5
Standardized Headers: 8
Notebooks with Icons: 6+
Trees with Decorations: 8+

CSS FEATURES:
- 6 status bar colors
- Button shadows
- Tab icon spacing
- Monetary field colors
- Kanban card borders

VALIDATION RESULTS:
Python Syntax: PASS
XML Syntax: PASS
CSS Created: YES

GIT STATUS:
Commit: [SHOW HASH]
Pushed: YES

ISSUES ENCOUNTERED: [NONE or list any]

READY FOR PHASE 5: YES

TIME TAKEN: [ESTIMATE]

================================================================================
REPORT_END
```

**STOP HERE. Report above. Wait for confirmation before Phase 5.**

---

# 📊 PHASE 5: MODULE UPGRADE & DEPLOYMENT

**Goal**: Deploy all changes and verify system

## Task 5.1: Backup Database

```bash
cd /opt/gemini_odoo19

# Create backup with timestamp
BACKUP_FILE="/tmp/mz-db_backup_$(date +%Y%m%d_%H%M%S).sql"

docker exec gemini_odoo19_db pg_dump -U odoo -d mz-db > "$BACKUP_FILE"

# Verify backup created
echo "=== Backup Created ==="
ls -lh "$BACKUP_FILE"
du -h "$BACKUP_FILE"

# Show backup info
echo "Backup file: $BACKUP_FILE"
echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
```

---

## Task 5.2: Upgrade All OPS Modules

```bash
cd /opt/gemini_odoo19

# Stop Odoo cleanly
echo "=== Stopping Odoo ==="
docker stop gemini_odoo19
sleep 5

# Start and upgrade modules
echo "=== Starting Odoo and Upgrading Modules ==="
docker start gemini_odoo19
sleep 10

# Upgrade all OPS modules
docker exec gemini_odoo19 odoo \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management \
  --stop-after-init \
  --log-level=info \
  2>&1 | tee /tmp/ops_upgrade_$(date +%Y%m%d_%H%M%S).log

# Check for errors in upgrade log
echo "=== Checking for Errors ==="
grep -E "ERROR|CRITICAL|ParseError|Traceback" /tmp/ops_upgrade_*.log | tail -20

# Count errors
ERROR_COUNT=$(grep -c "ERROR" /tmp/ops_upgrade_*.log || echo "0")
echo "Total errors found: $ERROR_COUNT"

# Restart Odoo
echo "=== Restarting Odoo ==="
docker restart gemini_odoo19
sleep 25

# Verify Odoo is running
docker ps | grep gemini_odoo19

# Test HTTP endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8089)
echo "HTTP Status: $HTTP_CODE"
```

---

## Task 5.3: Verify Security Rules

```bash
echo "=== Verifying Security Rules ==="

# Count System Admin bypass rules
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT COUNT(*) as admin_bypass_rules
FROM ir_rule 
WHERE name LIKE '%System Admin%' 
  AND active = true;
"

# List all active OPS security rules
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT name, active, model_id
FROM ir_rule 
WHERE (name LIKE '%OPS%' OR name LIKE '%System Admin%')
  AND active = true
ORDER BY name
LIMIT 20;
"

# Should show 18+ System Admin bypass rules
```

---

## Task 5.4: Verify Menu Structure

```bash
echo "=== Verifying Menu Structure ==="

# Check new root menus exist
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT id, name, parent_id, sequence, active
FROM ir_ui_menu 
WHERE name IN ('Approvals', 'OPS Framework', 'Executive Dashboard', 'OPS Matrix')
ORDER BY name;
"

# Count menus under Approvals
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT COUNT(*) as approval_menus
FROM ir_ui_menu 
WHERE parent_id = (SELECT id FROM ir_ui_menu WHERE name = 'Approvals' LIMIT 1);
"

# Count menus under OPS Framework
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT COUNT(*) as ops_framework_menus
FROM ir_ui_menu 
WHERE parent_id = (SELECT id FROM ir_ui_menu WHERE name = 'OPS Framework' LIMIT 1);
"
```

---

## Task 5.5: Verify Data Integrity

```bash
echo "=== Verifying Data Integrity ==="

# Check test data still exists
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT 
    'Business Units' as item, COUNT(*)::text as count 
FROM ops_business_unit
UNION ALL 
SELECT 'Branches', COUNT(*)::text FROM ops_branch
UNION ALL 
SELECT 'Products', COUNT(*)::text FROM product_product 
    WHERE default_code LIKE 'LAP-%' OR default_code LIKE 'MSE-%'
UNION ALL 
SELECT 'Sales Orders', COUNT(*)::text FROM sale_order
UNION ALL 
SELECT 'Customers', COUNT(*)::text FROM res_partner 
    WHERE customer_rank > 0;
"

# All counts should match pre-upgrade values
```

---

## Task 5.6: Test Critical Functionality

```bash
echo "=== Manual Testing Required ==="

cat << 'TEST_CHECKLIST'
================================================================================
MANUAL TEST CHECKLIST
================================================================================

Please perform these tests in the web interface:

1. LOGIN AS ADMIN
   ☐ Navigate to http://localhost:8089
   ☐ Login as admin/admin
   ☐ Clear browser cache (Ctrl+Shift+Delete)

2. VERIFY MENUS
   ☐ Approvals menu exists (top navigation)
   ☐ Settings → OPS Framework exists
   ☐ Dashboards app shows OPS dashboards
   ☐ OPS Matrix menu is NOT visible

3. TEST USER CREATION
   ☐ Settings → Users → Create
   ☐ Create user WITHOUT BU/Branch/Persona
   ☐ Should save successfully (H1 fix)

4. TEST SALES USER ACCESS
   ☐ Logout, login as salestest user
   ☐ Sales → Products
   ☐ Should open without error (C1 fix)
   ☐ Cost field should be hidden

5. TEST ASSETS
   ☐ Login as admin
   ☐ Navigate to Assets menu
   ☐ Should show tree view (C3 fix)
   ☐ Open an asset
   ☐ Should show book_value field (C2 fix)

6. TEST BUDGET
   ☐ Open Budget Control
   ☐ Create new budget
   ☐ Branch field should show branches not companies (H3 fix)

7. TEST FINANCIAL REPORTS
   ☐ Accounting → Reporting → Financial Reports
   ☐ Menu should exist (H4 fix)

8. TEST UI STYLING
   ☐ Open any form (Asset, Budget, PDC)
   ☐ Should have chatter at bottom (M8)
   ☐ Buttons should have colors and icons (M8)
   ☐ Status bar should have colors (M8)

================================================================================
TEST_CHECKLIST
```

---

## Task 5.7: Check System Logs

```bash
echo "=== Checking System Logs ==="

# Show last 100 lines of Odoo logs
docker logs gemini_odoo19 --tail 100 | tail -50

# Look for warnings/errors
docker logs gemini_odoo19 --tail 200 | grep -E "WARNING|ERROR|CRITICAL" | tail -20

# Check for XML/Python errors
docker logs gemini_odoo19 --tail 500 | grep -E "ParseError|SyntaxError|ImportError" | tail -10
```

---

## Task 5.8: Generate Final System Status

```bash
echo "=== Generating System Status Report ==="

cat << 'STATUS_REPORT'
================================================================================
SYSTEM STATUS REPORT
================================================================================

DOCKER CONTAINERS:
DOCKER_STATUS

DATABASE STATUS:
DB_STATUS

HTTP ENDPOINT:
HTTP_STATUS

MODULE STATUS:
MODULE_STATUS

SECURITY RULES:
SECURITY_STATUS

MENU STRUCTURE:
MENU_STATUS

DATA INTEGRITY:
DATA_STATUS

RECENT LOGS (Last 20 lines):
LOGS

================================================================================
STATUS_REPORT

# Replace placeholders with actual data
docker ps | grep gemini_odoo19
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT version();"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8089
docker logs gemini_odoo19 --tail 20
```

---

## 📋 PHASE 5 REPORT

```bash
cat << 'REPORT_END'
================================================================================
PHASE 5 COMPLETE: Module Upgrade & Deployment
================================================================================

Tasks Completed:
✅ 5.1: Database backup created
✅ 5.2: All modules upgraded
✅ 5.3: Security rules verified
✅ 5.4: Menu structure verified
✅ 5.5: Data integrity verified
✅ 5.6: Manual test checklist provided
✅ 5.7: System logs checked
✅ 5.8: Final status report generated

BACKUP DETAILS:
File: [PATH]
Size: [SIZE]
Created: [TIMESTAMP]

MODULE UPGRADE:
Modules Upgraded: 4
- ops_matrix_core
- ops_matrix_accounting
- ops_matrix_reporting
- ops_matrix_asset_management

Upgrade Errors: [COUNT]
Upgrade Warnings: [COUNT]
Upgrade Duration: [TIME]

VERIFICATION RESULTS:
Security Rules Active: [COUNT] (expect 18+)
Menu Structure: [PASS/FAIL]
  - Approvals menu: [EXISTS/MISSING]
  - OPS Framework menu: [EXISTS/MISSING]
  - OPS Matrix disabled: [YES/NO]
Data Integrity: [PASS/FAIL]
  - Business Units: [COUNT]
  - Branches: [COUNT]
  - Products: [COUNT]

SYSTEM STATUS:
Docker Container: [RUNNING/DOWN]
Database: [CONNECTED/DOWN]
HTTP Endpoint: [STATUS CODE]
Critical Errors: [COUNT]

MANUAL TESTING:
Checklist Provided: YES
Tests Required: 8
Estimated Test Time: 15 minutes

ISSUES ENCOUNTERED: [NONE or list any]

SYSTEM READY FOR UAT: [YES/NO]

TIME TAKEN: [ESTIMATE]

================================================================================
REPORT_END
```

**STOP HERE. Report above. Proceed to Final Report.**

---

# 📋 FINAL COMPREHENSIVE REPORT

```bash
cat << 'FINAL_REPORT'
================================================================================
================================================================================
           OPS FRAMEWORK COMPLETE FIX - FINAL COMPREHENSIVE REPORT
================================================================================
================================================================================

EXECUTION DATE: [INSERT DATE]
AGENT: [CLINE/ROO]
TOTAL DURATION: [HOURS]

================================================================================
OVERALL STATUS: [SUCCESS / PARTIAL SUCCESS / FAILED]
================================================================================

PHASES COMPLETED: [X/5]

Phase 1: Critical Bugs ................ [✅/❌]
Phase 2: High Priority Bugs ........... [✅/❌]
Phase 3: Menu Reorganization .......... [✅/❌]
Phase 4: UI Styling Unification ....... [✅/❌]
Phase 5: Deployment & Testing ......... [✅/❌]

================================================================================
PHASE 1: CRITICAL BUGS FIXED
================================================================================

Status: [COMPLETE/INCOMPLETE]

Tasks Completed:
✅/❌ 1.1: Field Visibility permission fix
✅/❌ 1.2: Asset missing fields (book_value, move_id)
✅/❌ 1.3: Missing view definitions (Assets, 3WM, API)
✅/❌ 1.4: Budget line account field fix
✅/❌ 1.5: Validation & commit

Files Modified:
- Python: 4 files
- XML: 3 files

Git Commit: [HASH]
Issues: [NONE or LIST]

================================================================================
PHASE 2: HIGH PRIORITY BUGS FIXED
================================================================================

Status: [COMPLETE/INCOMPLETE]

Tasks Completed:
✅/❌ 2.1: User fields made optional
✅/❌ 2.2: Product category fields unlocked
✅/❌ 2.3: Branch field fixed in budget
✅/❌ 2.4: Financial Reports menu added
✅/❌ 2.5: Validation & commit

Files Created:
- product_category_views.xml
- ops_report_menu.xml

Files Modified:
- Python: 2 files
- XML: 2 files

Git Commit: [HASH]
Issues: [NONE or LIST]

================================================================================
PHASE 3: MENU REORGANIZATION
================================================================================

Status: [COMPLETE/INCOMPLETE]

Tasks Completed:
✅/❌ 3.1: Approvals menu created (5 items)
✅/❌ 3.2: Settings reorganized (11 items)
✅/❌ 3.3: Dashboards moved (4 items)
✅/❌ 3.4: API menus disabled (4 menus)
✅/❌ 3.5: OPS Matrix disabled
✅/❌ 3.6: Manifest updated
✅/❌ 3.7: Validation & commit

Files Created:
- ops_approvals_menu.xml
- ops_settings_menu.xml
- ops_dashboards_menu.xml

Menu Summary:
New Menus: 11
Reorganized: 15
Disabled: 5

Git Commit: [HASH]
Issues: [NONE or LIST]

================================================================================
PHASE 4: UI STYLING UNIFICATION
================================================================================

Status: [COMPLETE/INCOMPLETE]

Tasks Completed:
✅/❌ 4.1: CSS theme created
✅/❌ 4.2: Chatter added (5 forms)
✅/❌ 4.3: Headers standardized (8 forms)
✅/❌ 4.4: Notebook icons added
✅/❌ 4.5: Tree decorations applied
✅/❌ 4.6: Validation & commit

Files Created:
- ops_theme.css

Forms with Chatter: 5
Standardized Headers: 8
Notebooks with Icons: 6+
Trees with Decorations: 8+

Git Commit: [HASH]
Issues: [NONE or LIST]

================================================================================
PHASE 5: DEPLOYMENT & TESTING
================================================================================

Status: [COMPLETE/INCOMPLETE]

Tasks Completed:
✅/❌ 5.1: Database backup
✅/❌ 5.2: Module upgrade
✅/❌ 5.3: Security verification
✅/❌ 5.4: Menu verification
✅/❌ 5.5: Data verification
✅/❌ 5.6: Test checklist
✅/❌ 5.7: Log check
✅/❌ 5.8: Status report

Backup: [PATH] ([SIZE])
Upgrade Errors: [COUNT]
System Status: [RUNNING/DOWN]
HTTP Status: [CODE]

Issues: [NONE or LIST]

================================================================================
SUMMARY STATISTICS
================================================================================

Files Modified:
- Python Files: [COUNT]
- XML Files: [COUNT]
- CSS Files: 1
- Total: [COUNT]

Lines Changed:
- Additions: [+COUNT]
- Deletions: [-COUNT]
- Net Change: [±COUNT]

Git Activity:
- Total Commits: 5
- Branch: main
- Remote: origin/main

Time Investment:
- Estimated: 6-8 hours
- Actual: [HOURS]

================================================================================
BUGS FIXED BY PRIORITY
================================================================================

CRITICAL (System Breaking):
✅ C1: Field Visibility blocking users
✅ C2: Missing Asset fields
✅ C3: Missing view definitions

HIGH PRIORITY:
✅ H1: User creation blocked
✅ H2: Product category locked
✅ H3: Branch field wrong data
✅ H4: Missing Financial Reports menu

MEDIUM PRIORITY:
⏳ M7: Menu reorganization (COMPLETE)
⏳ M8: UI styling (COMPLETE)
☐ M1-M6: Not in scope

================================================================================
NEW FEATURES IMPLEMENTED
================================================================================

✅ Approvals Menu Structure
   - My Approvals dashboard
   - Pending Approvals list
   - Approval History
   - SLA Tracking
   - Violations & Alerts

✅ Professional UI Theme
   - Status bar colors (6 states)
   - Button styling with icons
   - Tree view decorations
   - Notebook tab icons
   - Chatter integration

✅ Reorganized Settings
   - Company Structure section
   - Security & Governance section
   - Workflow Configuration section

✅ Moved Dashboards
   - All dashboards in native Dashboards app
   - Proper access controls

================================================================================
KNOWN ISSUES / LIMITATIONS
================================================================================

Issues Remaining:
[LIST ANY UNRESOLVED ISSUES FROM PHASES]

Out of Scope (Medium Priority):
- M1: Asset Categories redirect
- M2: PDC currency hard-coded
- M3: Fiscal localization missing CoA
- M4: Active Delegations wrong form
- M5: Approval Requests unclear purpose
- M6: Security Groups field unlabeled

Design Review Needed:
- D1: Inter-Branch Transfers form
- D2: Product Requests form
- D3: API Features (frozen)

================================================================================
TESTING STATUS
================================================================================

Automated Validation:
✅ Python syntax: PASS
✅ XML syntax: PASS
✅ Module installation: PASS

Manual Testing Required:
☐ Login as admin
☐ Verify menu structure
☐ Create user without BU/Branch
☐ Test sales user access
☐ Test Assets module
☐ Test Budget branch field
☐ Test Financial Reports
☐ Verify UI styling

Estimated Test Time: 15-20 minutes

================================================================================
DEPLOYMENT CHECKLIST
================================================================================

Pre-UAT:
✅ Database backup created
✅ All modules upgraded
✅ System running (HTTP 200)
☐ Browser cache cleared
☐ Admin can access all menus
☐ Test users created

Ready for UAT:
☐ All critical fixes tested
☐ All high priority fixes tested
☐ Menu navigation verified
☐ UI styling verified
☐ Security rules working

Production Readiness:
☐ UAT sign-off received
☐ Known issues documented
☐ User training completed
☐ Rollback plan prepared

================================================================================
NEXT STEPS
================================================================================

Immediate (Today):
1. Clear browser cache
2. Perform manual testing
3. Create test users for each persona
4. Verify security isolation works

Short Term (This Week):
5. Fix remaining medium priority bugs
6. Design review for Inter-Branch/Product Request forms
7. Complete UAT testing

Medium Term (Next Week):
8. Address design review findings
9. Fix any issues found in UAT
10. Plan production deployment

================================================================================
SIGN-OFF
================================================================================

Technical Implementation: [COMPLETE/INCOMPLETE]

Critical Bugs Fixed: [YES/NO]
High Priority Fixed: [YES/NO]
Menus Reorganized: [YES/NO]
UI Unified: [YES/NO]
System Operational: [YES/NO]

Ready for UAT: [YES/NO]
Ready for Production: [NO - UAT Required]

Prepared By: [AGENT NAME]
Date: [DATE]
Time: [TIME]

================================================================================
END OF COMPREHENSIVE REPORT
================================================================================
FINAL_REPORT
```

---

## 🎯 MISSION COMPLETE CRITERIA

Report **MISSION COMPLETE** when:

✅ All 5 phases show completed status
✅ All validation tests passed
✅ 5 git commits successfully made
✅ Module upgrade completed without critical errors
✅ System running (HTTP 200)
✅ No blocking issues in final report

If ANY phase has failures, report **MISSION INCOMPLETE** with details.

---

## 🚨 FINAL ERROR HANDLING

If mission cannot complete:

1. **Document the failure point**
2. **List what was completed**
3. **Provide detailed error logs**
4. **Suggest recovery steps**
5. **Estimate effort to complete**

---

**END OF COMPREHENSIVE PROMPT**

Execute Phase 1 and report. Proceed systematically through all phases.
Good luck! 🚀
