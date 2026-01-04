# Priority #9: Auto-List Accounts in Reports - Technical Specifications

**Priority**: #9 - HIGH  
**Estimated Effort**: 1 session (2-3 hours)  
**Status**: READY FOR DEVELOPMENT  
**Phase-Based Implementation**: Yes (Single phase, quick win)

---

## Overview

Automate the population of accounts in financial reports based on account type and report template. Eliminate manual account selection and ensure consistent, accurate report formatting across all branches and business units.

---

## Business Context

### Problem Statement

Without auto-list accounts:
- ❌ Users must manually select each account for reports
- ❌ Time-consuming (5-10 minutes per report)
- ❌ Prone to errors (missing accounts, wrong grouping)
- ❌ Inconsistent formatting across users
- ❌ No standard templates
- ❌ New accounts not automatically included

### Solution

**Auto-List Accounts System**:
1. **Template-Based**: Preloaded templates for common reports
2. **Account Type Mapping**: Auto-select by account type
3. **Intelligent Grouping**: Group by type, sort by code
4. **Branch/BU Filtering**: Filter accounts per branch/BU
5. **One-Click Apply**: Apply template instantly
6. **Custom Templates**: Save user configurations

### User Stories

**As a** Finance Manager  
**I want** reports to auto-populate with relevant accounts  
**So that** I don't waste time selecting accounts manually

**As an** Accountant  
**I want** standard templates for P&L and Balance Sheet  
**So that** reports are consistent across periods

**As a** CFO  
**I want** all branches to use same report format  
**So that** I can compare performance easily

---

## Core Concepts

### Report Types & Account Types

**Profit & Loss (P&L)**:
- Revenue Accounts (type: `income`)
- Expense Accounts (type: `expense`)
- Grouping: By account code
- Subtotals: Revenue total, Expense total, Net profit

**Balance Sheet**:
- Asset Accounts (type: `asset`)
- Liability Accounts (type: `liability`)
- Equity Accounts (type: `equity`)
- Grouping: Assets | Liabilities & Equity
- Subtotals: Total assets, Total liabilities, Total equity

**Cash Flow Statement**:
- Cash Accounts (type: `asset`, `account_type`: `liquidity`)
- Operating Activities
- Investing Activities
- Financing Activities

**Trial Balance**:
- All Accounts (all types)
- Grouping: By account type
- Show: Opening, Debit, Credit, Closing

### Template Structure

```
Template: "Standard P&L"
├── Section: "Revenue"
│   ├── Filter: account_type = 'income'
│   ├── Sort: account.code ASC
│   └── Subtotal: Yes
│
├── Section: "Cost of Goods Sold"
│   ├── Filter: account_type = 'expense' AND code LIKE '5%'
│   ├── Sort: account.code ASC
│   └── Subtotal: Yes
│
├── Section: "Gross Profit" (Calculated)
│   └── Formula: Revenue - COGS
│
├── Section: "Operating Expenses"
│   ├── Filter: account_type = 'expense' AND code LIKE '6%'
│   ├── Sort: account.code ASC
│   └── Subtotal: Yes
│
└── Section: "Net Profit" (Calculated)
    └── Formula: Revenue - Total Expenses
```

---

## PHASE 1: Auto-List Implementation (Single Session)

### Objectives

1. Create report template model
2. Create template line model (sections)
3. Implement auto-populate logic
4. Create preloaded templates (P&L, Balance Sheet, Trial Balance)
5. Add "Apply Template" button to reports
6. Add "Save as Template" functionality
7. Testing

### Files to Create

#### 1. `models/ops_report_template.py`

**Purpose**: Store report templates

```python
class OpsReportTemplate(models.Model):
    _name = 'ops.report.template'
    _description = 'Financial Report Template'
    _order = 'sequence, name'
    
    name = fields.Char('Template Name', required=True)
    report_type = fields.Selection([
        ('profit_loss', 'Profit & Loss'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow'),
        ('trial_balance', 'Trial Balance'),
        ('custom', 'Custom'),
    ], required=True, default='profit_loss')
    
    template_line_ids = fields.One2many(
        'ops.report.template.line',
        'template_id',
        'Template Lines'
    )
    
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', 'Company')
    is_system_template = fields.Boolean(
        'System Template',
        default=False,
        help='System templates cannot be modified by users'
    )
    
    def action_apply_to_report(self, report_id, date_from, date_to, branch_id=False, bu_id=False):
        """Apply template to a financial report."""
        self.ensure_one()
        
        Report = self.env['account.report']  # Or your report model
        report = Report.browse(report_id)
        
        # Clear existing lines
        report.line_ids.unlink()
        
        # Generate lines from template
        for template_line in self.template_line_ids.sorted('sequence'):
            accounts = template_line._get_accounts(
                date_from=date_from,
                date_to=date_to,
                branch_id=branch_id,
                bu_id=bu_id
            )
            
            if template_line.is_section_header:
                # Create section header
                report.line_ids.create({
                    'report_id': report.id,
                    'name': template_line.section_name,
                    'is_section': True,
                    'sequence': template_line.sequence,
                })
            
            # Create account lines
            for account in accounts:
                report.line_ids.create({
                    'report_id': report.id,
                    'account_id': account.id,
                    'name': f"{account.code} - {account.name}",
                    'sequence': template_line.sequence + account.code,
                })
            
            if template_line.show_subtotal and accounts:
                # Create subtotal line
                report.line_ids.create({
                    'report_id': report.id,
                    'name': f"Total {template_line.section_name}",
                    'is_subtotal': True,
                    'sequence': template_line.sequence + 999,
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Template "{self.name}" applied successfully',
                'type': 'success',
            }
        }
```

#### 2. `models/ops_report_template_line.py`

**Purpose**: Template sections/lines

```python
class OpsReportTemplateLine(models.Model):
    _name = 'ops.report.template.line'
    _description = 'Report Template Line'
    _order = 'sequence, id'
    
    template_id = fields.Many2one('ops.report.template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    
    section_name = fields.Char('Section Name', required=True)
    is_section_header = fields.Boolean('Show Section Header', default=True)
    show_subtotal = fields.Boolean('Show Subtotal', default=True)
    
    # Account Selection Criteria
    account_type = fields.Selection([
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ], 'Account Type')
    
    account_code_pattern = fields.Char(
        'Account Code Pattern',
        help='SQL LIKE pattern (e.g., "5%" for codes starting with 5)'
    )
    
    account_ids = fields.Many2many(
        'account.account',
        'report_template_line_account_rel',
        'line_id',
        'account_id',
        'Specific Accounts',
        help='If specified, use these accounts instead of filters'
    )
    
    sort_by = fields.Selection([
        ('code', 'Account Code'),
        ('name', 'Account Name'),
    ], default='code')
    
    def _get_accounts(self, date_from, date_to, branch_id=False, bu_id=False):
        """Get accounts matching this template line criteria."""
        self.ensure_one()
        
        # If specific accounts defined, use those
        if self.account_ids:
            return self.account_ids
        
        # Build domain
        domain = [('company_id', '=', self.template_id.company_id.id)]
        
        # Account type filter
        if self.account_type:
            domain.append(('account_type', '=', self.account_type))
        
        # Code pattern filter
        if self.account_code_pattern:
            domain.append(('code', 'like', self.account_code_pattern))
        
        # Branch filter (if accounts have branch field)
        if branch_id:
            domain.append(('ops_branch_id', '=', branch_id))
        
        # Search accounts
        accounts = self.env['account.account'].search(domain)
        
        # Sort
        if self.sort_by == 'code':
            accounts = accounts.sorted(lambda a: a.code)
        else:
            accounts = accounts.sorted(lambda a: a.name)
        
        return accounts
```

#### 3. Preloaded Templates

**File**: `data/ops_report_templates.xml`

```xml
<odoo>
    <data noupdate="1">
        <!-- P&L Template -->
        <record id="template_profit_loss_standard" model="ops.report.template">
            <field name="name">Standard Profit & Loss</field>
            <field name="report_type">profit_loss</field>
            <field name="is_system_template" eval="True"/>
            <field name="sequence">10</field>
        </record>
        
        <record id="template_pl_line_revenue" model="ops.report.template.line">
            <field name="template_id" ref="template_profit_loss_standard"/>
            <field name="sequence">10</field>
            <field name="section_name">REVENUE</field>
            <field name="account_type">income</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <record id="template_pl_line_cogs" model="ops.report.template.line">
            <field name="template_id" ref="template_profit_loss_standard"/>
            <field name="sequence">20</field>
            <field name="section_name">COST OF GOODS SOLD</field>
            <field name="account_type">expense</field>
            <field name="account_code_pattern">5%</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <record id="template_pl_line_opex" model="ops.report.template.line">
            <field name="template_id" ref="template_profit_loss_standard"/>
            <field name="sequence">30</field>
            <field name="section_name">OPERATING EXPENSES</field>
            <field name="account_type">expense</field>
            <field name="account_code_pattern">6%</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <!-- Balance Sheet Template -->
        <record id="template_balance_sheet_standard" model="ops.report.template">
            <field name="name">Standard Balance Sheet</field>
            <field name="report_type">balance_sheet</field>
            <field name="is_system_template" eval="True"/>
            <field name="sequence">20</field>
        </record>
        
        <record id="template_bs_line_assets" model="ops.report.template.line">
            <field name="template_id" ref="template_balance_sheet_standard"/>
            <field name="sequence">10</field>
            <field name="section_name">ASSETS</field>
            <field name="account_type">asset</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <record id="template_bs_line_liabilities" model="ops.report.template.line">
            <field name="template_id" ref="template_balance_sheet_standard"/>
            <field name="sequence">20</field>
            <field name="section_name">LIABILITIES</field>
            <field name="account_type">liability</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <record id="template_bs_line_equity" model="ops.report.template.line">
            <field name="template_id" ref="template_balance_sheet_standard"/>
            <field name="sequence">30</field>
            <field name="section_name">EQUITY</field>
            <field name="account_type">equity</field>
            <field name="show_subtotal" eval="True"/>
        </record>
        
        <!-- Trial Balance Template -->
        <record id="template_trial_balance" model="ops.report.template">
            <field name="name">Standard Trial Balance</field>
            <field name="report_type">trial_balance</field>
            <field name="is_system_template" eval="True"/>
            <field name="sequence">30</field>
        </record>
        
        <record id="template_tb_line_all" model="ops.report.template.line">
            <field name="template_id" ref="template_trial_balance"/>
            <field name="sequence">10</field>
            <field name="section_name">ALL ACCOUNTS</field>
            <field name="is_section_header" eval="False"/>
            <field name="show_subtotal" eval="False"/>
        </record>
    </data>
</odoo>
```

### Views to Create

#### 1. Template Management Views

**File**: `views/ops_report_template_views.xml`

```xml
<!-- Tree View -->
<record id="view_report_template_tree" model="ir.ui.view">
    <field name="name">ops.report.template.tree</field>
    <field name="model">ops.report.template</field>
    <field name="arch" type="xml">
        <tree>
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="report_type"/>
            <field name="is_system_template"/>
            <field name="active" widget="boolean_toggle"/>
        </tree>
    </field>
</record>

<!-- Form View -->
<record id="view_report_template_form" model="ir.ui.view">
    <field name="name">ops.report.template.form</field>
    <field name="model">ops.report.template</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="action_apply_to_report" type="object" 
                            class="oe_stat_button" icon="fa-magic" string="Apply to Report"/>
                </div>
                
                <group>
                    <group>
                        <field name="name"/>
                        <field name="report_type"/>
                        <field name="company_id" groups="base.group_multi_company"/>
                    </group>
                    <group>
                        <field name="active"/>
                        <field name="sequence"/>
                        <field name="is_system_template" readonly="1"/>
                    </group>
                </group>
                
                <notebook>
                    <page name="template_lines" string="Template Lines">
                        <field name="template_line_ids">
                            <tree editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="section_name"/>
                                <field name="account_type"/>
                                <field name="account_code_pattern"/>
                                <field name="sort_by"/>
                                <field name="is_section_header" widget="boolean_toggle"/>
                                <field name="show_subtotal" widget="boolean_toggle"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>

<!-- Action -->
<record id="action_report_template" model="ir.actions.act_window">
    <field name="name">Report Templates</field>
    <field name="res_model">ops.report.template</field>
    <field name="view_mode">tree,form</field>
</record>

<!-- Menu Item -->
<menuitem id="menu_report_template"
          name="Report Templates"
          parent="ops_matrix_core.menu_ops_reporting"
          action="action_report_template"
          sequence="90"/>
```

#### 2. Apply Template Wizard

**File**: `wizard/apply_report_template_wizard.py`

```python
class ApplyReportTemplateWizard(models.TransientModel):
    _name = 'apply.report.template.wizard'
    _description = 'Apply Report Template Wizard'
    
    template_id = fields.Many2one('ops.report.template', 'Template', required=True)
    date_from = fields.Date('From Date', required=True)
    date_to = fields.Date('To Date', required=True)
    branch_id = fields.Many2one('ops.branch', 'Branch')
    business_unit_id = fields.Many2one('ops.business.unit', 'Business Unit')
    
    def action_apply_template(self):
        """Apply selected template to current report."""
        self.ensure_one()
        report_id = self.env.context.get('active_id')
        
        return self.template_id.action_apply_to_report(
            report_id=report_id,
            date_from=self.date_from,
            date_to=self.date_to,
            branch_id=self.branch_id.id if self.branch_id else False,
            bu_id=self.business_unit_id.id if self.business_unit_id else False
        )
```

**File**: `wizard/apply_report_template_wizard_views.xml`

```xml
<record id="view_apply_report_template_wizard" model="ir.ui.view">
    <field name="name">apply.report.template.wizard.form</field>
    <field name="model">apply.report.template.wizard</field>
    <field name="arch" type="xml">
        <form string="Apply Report Template">
            <group>
                <field name="template_id"/>
                <field name="date_from"/>
                <field name="date_to"/>
                <field name="branch_id"/>
                <field name="business_unit_id"/>
            </group>
            <footer>
                <button name="action_apply_template" type="object" 
                        string="Apply Template" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

### Integration with Existing Reports

**Add "Apply Template" Button to Report Views**:

```xml
<!-- Example for account.financial.report or your report model -->
<xpath expr="//form/header" position="inside">
    <button name="%(action_apply_report_template_wizard)d"
            type="action"
            string="Apply Template"
            icon="fa-magic"
            class="btn-primary"/>
</xpath>
```

### Testing Checklist

**Template Creation**:
- [ ] Create custom template
- [ ] Add template lines
- [ ] Configure filters (account type, code pattern)
- [ ] Save and verify

**Template Application**:
- [ ] Open financial report
- [ ] Click "Apply Template"
- [ ] Select template
- [ ] Set date range
- [ ] Apply and verify accounts populated

**Preloaded Templates**:
- [ ] P&L template loads revenue accounts
- [ ] P&L template separates COGS from OPEX
- [ ] Balance Sheet shows Assets/Liabilities/Equity
- [ ] Trial Balance shows all accounts

**Filtering**:
- [ ] Branch filter works
- [ ] BU filter works
- [ ] Account code pattern works (e.g., "5%")
- [ ] Account type filter works

**Grouping & Sorting**:
- [ ] Accounts sorted by code
- [ ] Section headers display
- [ ] Subtotals appear
- [ ] Order matches template sequence

---

## Success Metrics

**Feature Success If**:
- ✅ Report setup time reduced from 10 min to <30 sec
- ✅ 100% of users use templates (vs manual)
- ✅ Zero missing accounts in reports
- ✅ Consistent formatting across all branches
- ✅ New accounts auto-included in reports

---

## Future Enhancements (Out of Scope)

1. **Calculated Lines**
   - Gross profit = Revenue - COGS
   - Net profit = Revenue - Total expenses
   - Formulas in template

2. **Conditional Formatting**
   - Highlight negative numbers in red
   - Bold section headers
   - Indent sub-accounts

3. **Multi-Period Comparison**
   - Side-by-side columns
   - Variance columns
   - Trend analysis

4. **Export Templates**
   - Export to Excel with formatting
   - Import templates from Excel
   - Share templates between companies

---

## READY FOR DEVELOPMENT

**Phases**: Single phase (quick win)  
**Effort**: 2-3 hours (1 session)  
**Impact**: 95% time savings on report setup  

**All requirements defined. Ready for RooCode!** 🚀
