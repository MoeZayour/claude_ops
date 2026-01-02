# 📋 OPS MATRIX FRAMEWORK - IMPLEMENTATION PROMPTS (Level 1)

**Version**: 1.0  
**Date**: 2025-12-24  
**Target**: Odoo 19 Community Edition  
**Architecture**: Company → Branch → Business Unit  

---

## 🎯 ARCHITECTURE OVERVIEW

```
Legal Entity (Company)
├─ Corporate Office (CEO, COO, Finance)
├─ Branch 1 (Operational Office)
│  ├─ Manager
│  ├─ Employees
│  ├─ Business Unit 1 → Analytic Account
│  └─ Business Unit 2 → Analytic Account
├─ Branch 2
│  ├─ Business Unit 1 → Analytic Account
│  └─ Business Unit 3 → Analytic Account
└─ Branch 3
   └─ Business Unit 2 → Analytic Account

Cross-Branch BU Leader:
- Sits in Branch 1
- Manages BU1 across Branch 1, 2, 3
- Access spans multiple branches for ONE business unit
```

**Key Concepts:**
- **Company** = Legal Entity with Financial Books (e.g., ABC-Qatar, ABC-UAE)
- **Branch** = Operational Office (e.g., ABC-Doha, ABC-AlKhor, ABC-Dubai)
- **Business Unit** = Profit Center (e.g., Retail, Coffee, Services)
- **Analytic Account** = Auto-created tracking dimension for Branch & BU

---

## 📊 PROGRESS TRACKER

### Phase 1: Foundation ✓ Complete / ☐ Pending / ⚠ In Progress
- [ ] 1.1: Create Branch Model
- [ ] 1.2: Update Business Unit Model
- [ ] 1.3: Clean up Company Model
- [ ] 1.4: Update Model Imports
- [ ] 1.5: Create Company Form Extension (UI)

### Phase 2: Data Flow ☐
- [ ] 2.1: Create Matrix Mixin
- [ ] 2.2: Update Standard Extensions
- [ ] 2.5: Branch Selection Widget (UI)

### Phase 3: Analytic Accounting ☐
- [ ] 3.1: Analytic Plan Structure
- [ ] 3.2: Account Move Distribution

### Phase 4: Security Model ☐
- [ ] 4.1: User Matrix Access
- [ ] 4.2: Security Rules

### Phase 5: Reporting Framework ☐
- [ ] 5.1: Consolidated Reporting
- [ ] 5.2: GL Wizard Enhancement

### Phase 6: Dashboards ☐
- [ ] 6.1: Multi-Level Dashboards

### Phase 7: Governance ☐
- [ ] 7.1: Persona Enhancement
- [ ] 7.2: Governance Rules Update

### Phase 8: Data Migration ☐
- [ ] 8.1: Default Data Templates

### Phase 9: Testing ☐
- [ ] 9.1: Test Suite Creation

---

## 🔨 IMPLEMENTATION PROMPTS

### **PHASE 1: FOUNDATION - COMPANY/BRANCH/BU HIERARCHY**

#### **Prompt 1.1: Create the Branch Model** ☐

**File**: `ops_matrix_core/models/ops_branch.py`

```
Create a new model file: ops_matrix_core/models/ops_branch.py

This model represents operational branches under a company (legal entity). Requirements:

1. Model Definition:
   - Model name: ops.branch (NOT res.company!)
   - Inherits: mail.thread, mail.activity.mixin
   - Description: "Operational Branch (not a legal entity)"

2. Required Fields:
   - name (Char, required, tracking=True) - Branch name
   - code (Char, required, copy=False, readonly=True, default='New') - Auto-generated code
   - company_id (Many2one to res.company, required, ondelete='restrict') - Parent legal entity
   - manager_id (Many2one to res.users, string="Branch Manager") - Who manages this branch
   - analytic_account_id (Many2one to account.analytic.account, readonly=True, copy=False) - Auto-created
   - active (Boolean, default=True)

3. Optional Fields:
   - parent_id (Many2one to 'ops.branch') - For branch hierarchy (Regional → City → Outlet)
   - address (Text) - Physical address
   - phone (Char)
   - email (Char)
   - warehouse_id (Many2one to stock.warehouse) - Primary warehouse link
   - color (Integer, default=0) - For kanban view
   - sequence (Integer, default=10) - For ordering

4. Computed Fields:
   - child_ids (One2many 'ops.branch', 'parent_id') - Sub-branches
   - business_unit_count (Integer, compute='_compute_business_unit_count') - Count of BUs

5. Methods to Implement:
   
   @api.model_create_multi
   def create(self, vals_list):
       # Generate code if 'New'
       for vals in vals_list:
           if vals.get('code', 'New') == 'New':
               vals['code'] = self.env['ir.sequence'].next_by_code('ops.branch') or 'New'
       records = super().create(vals_list)
       records._create_analytic_accounts()
       return records
   
   def write(self, vals):
       result = super().write(vals)
       if 'name' in vals or 'code' in vals:
           self._sync_analytic_account_name()
       return result
   
   def _create_analytic_accounts(self):
       """Auto-create analytic account for each branch."""
       for branch in self:
           if not branch.analytic_account_id:
               analytic_plan = self._get_or_create_analytic_plan('Branch')
               analytic_account = self.env['account.analytic.account'].create({
                   'name': f"{branch.code} - {branch.name}",
                   'code': branch.code,
                   'plan_id': analytic_plan.id,
                   'company_id': branch.company_id.id,
               })
               branch.analytic_account_id = analytic_account.id
   
   def _sync_analytic_account_name(self):
       """Sync analytic account name when branch name/code changes."""
       for branch in self:
           if branch.analytic_account_id:
               branch.analytic_account_id.write({
                   'name': f"{branch.code} - {branch.name}",
                   'code': branch.code,
               })
   
   def _get_or_create_analytic_plan(self, plan_type):
       """Get or create analytic plan for Branch dimension."""
       plan_name = f"Matrix {plan_type}"
       plan = self.env['account.analytic.plan'].search([('name', '=', plan_name)], limit=1)
       if not plan:
           plan = self.env['account.analytic.plan'].create({
               'name': plan_name,
               'company_id': False,  # Global plan
           })
       return plan
   
   def _compute_business_unit_count(self):
       for branch in self:
           branch.business_unit_count = self.env['ops.business.unit'].search_count([
               ('branch_ids', 'in', branch.id)
           ])

6. Constraints:
   - SQL constraint: unique code per company
   - Python constraint: Prevent deletion if has transactions

7. Sequence Creation:
   Create in data/ir_sequence_data.xml:
   <record id="seq_ops_branch" model="ir.sequence">
       <field name="name">Branch Sequence</field>
       <field name="code">ops.branch</field>
       <field name="prefix">BR-</field>
       <field name="padding">4</field>
       <field name="company_id" eval="False"/>
   </record>

Make it compatible with Odoo 19 CE patterns and use self.env for all operations.
```

---

#### **Prompt 1.2: Update Business Unit Model to Link to Branch** ☐

**File**: `ops_matrix_core/models/ops_business_unit.py`

```
Update existing file: ops_matrix_core/models/ops_business_unit.py

Change the Business Unit model to link to branches (not companies directly):

1. Field Changes:
   
   REMOVE:
   - company_id as direct Many2one field
   
   ADD:
   - branch_ids (Many2many to ops.branch, string="Operating Branches")
     Domain: [('company_id', 'in', user's allowed companies)]
     Help: "This BU operates in these branches"
   
   - company_ids (Many2many, related='branch_ids.company_id', store=True, string="Companies")
     For filtering by legal entity
   
   - primary_branch_id (Many2one to ops.branch, string="Primary Branch")
     Help: "Main branch where BU leader sits"

2. Update Analytic Account Creation:
   
   def _create_analytic_accounts(self):
       """Create one analytic account per BU (not per branch)."""
       for bu in self:
           if not bu.analytic_account_id:
               # Use primary branch's company, or first company if no primary
               company_id = bu.primary_branch_id.company_id.id if bu.primary_branch_id else (
                   bu.company_ids[0].id if bu.company_ids else self.env.company.id
               )
               
               analytic_plan = self._get_or_create_analytic_plan('Business Unit')
               analytic_account = self.env['account.analytic.account'].create({
                   'name': f"{bu.code} - {bu.name}",
                   'code': bu.code,
                   'plan_id': analytic_plan.id,
                   'company_id': company_id,
               })
               bu.analytic_account_id = analytic_account.id

3. Update Methods:
   - Keep code auto-generation (sequence 'ops.business.unit')
   - Update _sync_analytic_account_name() if it exists
   - Add validation: At least one branch must be selected

4. Add Computed Field:
   - branch_count (Integer, compute='_compute_branch_count')
   
   def _compute_branch_count(self):
       for bu in self:
           bu.branch_count = len(bu.branch_ids)

5. Constraints:
   - Python: @api.constrains('branch_ids')
     def _check_branch_ids(self):
         for bu in self:
             if not bu.branch_ids:
                 raise ValidationError("Business Unit must operate in at least one branch.")

This allows BUs to span multiple branches (e.g., Retail BU in 5 branches across 2 countries).
```

---

#### **Prompt 1.3: Clean up Company Model Extension** ☐

**File**: `ops_matrix_core/models/res_company.py`

```
Update existing file: ops_matrix_core/models/res_company.py

Simplify res.company to ONLY handle legal entity identification (not operational):

1. Model Definition:
   class ResCompany(models.Model):
       _inherit = 'res.company'

2. Fields to KEEP:
   - ops_code (Char, required=True, readonly=True, copy=False, default='New')
     For legal entity identification (e.g., QAT-001, UAE-001)
   
   - ops_manager_id (Many2one to res.users, string="Country Manager")
     Company-level manager (CEO, Country Director)

3. Fields to ADD:
   - branch_ids (One2many 'ops.branch', 'company_id', string="Operational Branches")
   - branch_count (Integer, compute='_compute_branch_count', string="Number of Branches")

4. Fields to REMOVE:
   - ops_business_unit_ids (BUs now linked to branches)
   - ops_analytic_account_id (Analytic accounts now on branches)

5. Methods to UPDATE:
   
   @api.model_create_multi
   def create(self, vals_list):
       for vals in vals_list:
           if vals.get('ops_code', 'New') == 'New':
               vals['ops_code'] = self.env['ir.sequence'].next_by_code('res.company.ops') or 'New'
       return super().create(vals_list)
   
   def _compute_branch_count(self):
       for company in self:
           company.branch_count = len(company.branch_ids)

6. Constraints:
   - SQL: unique ops_code (across all companies)
   - Python: Validate ops_code format if needed

7. Remove analytic account auto-creation logic (now in ops.branch)

This makes res.company purely a legal entity container, with operational structure in branches.
```

---

#### **Prompt 1.4: Update Model Imports** ☐

**File**: `ops_matrix_core/models/__init__.py`

```
Update: ops_matrix_core/models/__init__.py

Ensure proper import order for model dependencies:

Current imports (example):
from . import res_company
from . import ops_business_unit
from . import ops_persona
# ... other imports

UPDATE TO:
from . import res_company          # First: base Odoo model
from . import ops_branch            # Second: NEW - Branch model (depends on company)
from . import ops_business_unit     # Third: BU model (now depends on branch)
from . import ops_persona           # Fourth: Persona (depends on branch/BU)
from . import ops_mixin             # Fifth: Mixin (depends on branch/BU)
# ... rest of imports in logical order

CRITICAL:
- ops_branch MUST come before ops_business_unit (BU references branch)
- ops_branch MUST come after res_company (branch references company)
- Check for any circular dependencies

Remove any duplicate or deprecated imports.
```

---

#### **Prompt 1.5: Create Company Form Extension with Branch Tab** ☐ **(NEW)**

**File**: `ops_matrix_core/views/res_company_views.xml`

```
Update existing file: ops_matrix_core/views/res_company_views.xml

Extend the native Company form to manage branches from Settings → Companies:

1. Inherit Company Form View:
   <record id="view_company_form_ops_branches" model="ir.ui.view">
       <field name="name">res.company.form.ops.branches</field>
       <field name="model">res.company</field>
       <field name="inherit_id" ref="base.view_company_form"/>
       <field name="arch" type="xml">
           
           <!-- Add OPS Code field in header -->
           <xpath expr="//field[@name='name']" position="after">
               <field name="ops_code" readonly="1" class="oe_inline"/>
           </xpath>
           
           <!-- Add Country Manager field -->
           <xpath expr="//field[@name='partner_id']" position="after">
               <field name="ops_manager_id" string="Country Manager"/>
           </xpath>
           
           <!-- Add Operational Branches Tab -->
           <xpath expr="//notebook" position="inside">
               <page string="Operational Branches" name="ops_branches">
                   <div class="alert alert-info" role="alert">
                       <strong>Note:</strong> These are operational branches, not legal entities.
                       All branches share this company's financial books.
                       Analytic accounts are auto-created for reporting.
                   </div>
                   
                   <field name="branch_ids" mode="tree,kanban" context="{'default_company_id': active_id}">
                       <!-- Tree View for Branches -->
                       <tree string="Branches" editable="bottom">
                           <field name="sequence" widget="handle"/>
                           <field name="code" readonly="1"/>
                           <field name="name"/>
                           <field name="manager_id"/>
                           <field name="phone"/>
                           <field name="business_unit_count" string="BUs"/>
                           <field name="active" widget="boolean_button"/>
                       </tree>
                       
                       <!-- Kanban View for Visual Overview -->
                       <kanban>
                           <field name="id"/>
                           <field name="name"/>
                           <field name="code"/>
                           <field name="manager_id"/>
                           <field name="color"/>
                           <templates>
                               <t t-name="card">
                                   <div t-attf-class="oe_kanban_color_#{record.color.raw_value} oe_kanban_card">
                                       <div class="oe_kanban_content">
                                           <strong><field name="name"/></strong>
                                           <div><field name="code"/></div>
                                           <div><field name="manager_id" widget="many2one_avatar_user"/></div>
                                       </div>
                                   </div>
                               </t>
                           </templates>
                       </kanban>
                       
                       <!-- Form View for Quick Create -->
                       <form string="Branch">
                           <sheet>
                               <group>
                                   <group>
                                       <field name="name" placeholder="e.g., Doha Office"/>
                                       <field name="code" readonly="1"/>
                                       <field name="manager_id" placeholder="Select branch manager"/>
                                   </group>
                                   <group>
                                       <field name="phone"/>
                                       <field name="email"/>
                                       <field name="active"/>
                                   </group>
                               </group>
                               <group string="Address">
                                   <field name="address" placeholder="Physical location address"/>
                               </group>
                           </sheet>
                       </form>
                   </field>
               </page>
           </xpath>
           
       </field>
   </record>

2. Add Branch Count to Company Tree View:
   <record id="view_company_tree_ops" model="ir.ui.view">
       <field name="name">res.company.tree.ops</field>
       <field name="model">res.company</field>
       <field name="inherit_id" ref="base.view_company_tree"/>
       <field name="arch" type="xml">
           <xpath expr="//field[@name='name']" position="after">
               <field name="ops_code"/>
               <field name="branch_count" string="Branches"/>
           </xpath>
       </field>
   </record>

This allows users to manage their entire operational structure from Settings → Companies.
```

---

### **PHASE 2: DATA FLOW PROPAGATION**

#### **Prompt 2.1: Create Matrix Mixin for Dimension Propagation** ☐

**File**: `ops_matrix_core/models/ops_matrix_mixin.py`

```
Create: ops_matrix_core/models/ops_matrix_mixin.py

Create a reusable mixin for all transaction models to handle dimension propagation:

1. Abstract Model Definition:
   class OpsMatrixMixin(models.AbstractModel):
       _name = 'ops.matrix.mixin'
       _description = 'OPS Matrix Dimension Propagation Mixin'

2. Fields:
   # Matrix Dimensions
   ops_company_id = fields.Many2one('res.company', string='Legal Entity', 
                                     compute='_compute_ops_company', store=True)
   ops_branch_id = fields.Many2one('ops.branch', string='Branch', required=True, 
                                    default=lambda self: self._get_default_ops_branch())
   ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', required=True,
                                           default=lambda self: self._get_default_ops_business_unit())
   
   # Analytic Distribution (Odoo 19 format)
   ops_analytic_distribution = fields.Json(compute='_compute_analytic_distribution', store=True)

3. Computed Methods:
   
   @api.depends('ops_branch_id')
   def _compute_ops_company(self):
       for record in self:
           record.ops_company_id = record.ops_branch_id.company_id if record.ops_branch_id else False
   
   @api.depends('ops_branch_id', 'ops_business_unit_id')
   def _compute_analytic_distribution(self):
       """Compute analytic distribution for dual-dimension tracking."""
       for record in self:
           distribution = {}
           if record.ops_branch_id and record.ops_branch_id.analytic_account_id:
               distribution[str(record.ops_branch_id.analytic_account_id.id)] = 50
           if record.ops_business_unit_id and record.ops_business_unit_id.analytic_account_id:
               distribution[str(record.ops_business_unit_id.analytic_account_id.id)] = 50
           record.ops_analytic_distribution = distribution if distribution else False

4. Default Methods:
   
   def _get_default_ops_branch(self):
       """Get default branch from user's persona."""
       user = self.env.user
       if hasattr(user, 'default_branch_id') and user.default_branch_id:
           return user.default_branch_id.id
       # Fallback: First branch of user's company
       branch = self.env['ops.branch'].search([('company_id', '=', user.company_id.id)], limit=1)
       return branch.id if branch else False
   
   def _get_default_ops_business_unit(self):
       """Get default BU from user's persona."""
       user = self.env.user
       if hasattr(user, 'default_business_unit_id') and user.default_business_unit_id:
           return user.default_business_unit_id.id
       return False

5. Propagation Helper:
   
   def _propagate_matrix_to_lines(self, line_model, line_field='order_line'):
       """Propagate matrix dimensions to related lines."""
       for record in self:
           lines = record[line_field]
           lines.write({
               'ops_branch_id': record.ops_branch_id.id,
               'ops_business_unit_id': record.ops_business_unit_id.id,
           })

6. Models to Apply Mixin:
   - sale.order
   - purchase.order
   - stock.picking
   - account.move
   - stock.inventory (if applicable)

This ensures consistent dimension tracking across all transactions.
```

---

#### **Prompt 2.2: Update Standard Model Extensions for Propagation** ☐

**File**: `ops_matrix_accounting/models/ops_matrix_standard_extensions.py`

```
Create/Update: ops_matrix_accounting/models/ops_matrix_standard_extensions.py

Extend standard Odoo models to propagate dimensions through transaction lifecycle:

1. Sale Order → Invoice Propagation:
   
   class SaleOrder(models.Model):
       _inherit = ['sale.order', 'ops.matrix.mixin']
       _name = 'sale.order'
       
       def _prepare_invoice(self):
           """Propagate matrix dimensions to invoice."""
           invoice_vals = super()._prepare_invoice()
           invoice_vals.update({
               'ops_branch_id': self.ops_branch_id.id,
               'ops_business_unit_id': self.ops_business_unit_id.id,
           })
           return invoice_vals
       
       @api.onchange('ops_branch_id', 'ops_business_unit_id')
       def _onchange_matrix_dimensions(self):
           """Propagate to order lines when changed."""
           for line in self.order_line:
               line.ops_branch_id = self.ops_branch_id
               line.ops_business_unit_id = self.ops_business_unit_id

2. Sale Order Line:
   
   class SaleOrderLine(models.Model):
       _inherit = ['sale.order.line', 'ops.matrix.mixin']
       _name = 'sale.order.line'
       
       # Inherit dimension fields from mixin
       # No additional methods needed - mixin handles it

3. Purchase Order → Bill Propagation:
   
   class PurchaseOrder(models.Model):
       _inherit = ['purchase.order', 'ops.matrix.mixin']
       _name = 'purchase.order'
       
       def _prepare_invoice(self):
           invoice_vals = super()._prepare_invoice()
           invoice_vals.update({
               'ops_branch_id': self.ops_branch_id.id,
               'ops_business_unit_id': self.ops_business_unit_id.id,
           })
           return invoice_vals

4. Sale/Purchase → Stock Picking:
   
   class StockPicking(models.Model):
       _inherit = ['stock.picking', 'ops.matrix.mixin']
       _name = 'stock.picking'
       
       # Dimensions propagate from sale.order via _create_picking
       
       def _action_done(self):
           """Propagate to account moves when delivery is done."""
           result = super()._action_done()
           for picking in self:
               if picking.move_ids:
                   account_moves = picking.move_ids.mapped('account_move_ids')
                   account_moves.write({
                       'ops_branch_id': picking.ops_branch_id.id,
                       'ops_business_unit_id': picking.ops_business_unit_id.id,
                   })
           return result

5. Override Create Methods to Propagate:
   
   class SaleOrder(models.Model):
       _inherit = 'sale.order'
       
       @api.model_create_multi
       def create(self, vals_list):
           orders = super().create(vals_list)
           for order in orders:
               order._propagate_matrix_to_lines('order_line')
           return orders

Apply similar pattern to:
- purchase.order → purchase.order.line
- stock.picking → stock.move
- account.move → account.move.line

This ensures dimensions flow through: Sale → Invoice → Picking → Accounting Entry.
```

---

#### **Prompt 2.5: Branch/BU Selection Widget in Transaction Forms** ☐ **(NEW)**

**Files**: `ops_matrix_core/views/sale_order_views.xml`, `purchase_order_views.xml`, etc.

```
Create: ops_matrix_core/views/ops_matrix_transaction_views.xml

Add Branch and Business Unit selection prominently in all transaction forms:

1. Sale Order Form Enhancement:
   <record id="view_order_form_ops_matrix" model="ir.ui.view">
       <field name="name">sale.order.form.ops.matrix</field>
       <field name="model">sale.order</field>
       <field name="inherit_id" ref="sale.view_order_form"/>
       <field name="arch" type="xml">
           
           <!-- Add Matrix Fields at Top (before order lines) -->
           <xpath expr="//field[@name='pricelist_id']" position="after">
               <field name="ops_branch_id" 
                      options="{'no_create': True, 'no_open': True}"
                      domain="[('company_id', '=', company_id), ('active', '=', True)]"
                      required="1"
                      attrs="{'readonly': [('state', 'not in', ['draft', 'sent'])]}"/>
               
               <field name="ops_business_unit_id"
                      options="{'no_create': True, 'no_open': True}"
                      domain="[('branch_ids', 'in', [ops_branch_id]), ('active', '=', True)]"
                      required="1"
                      attrs="{'readonly': [('state', 'not in', ['draft', 'sent'])]}"/>
           </xpath>
           
           <!-- Add to tree view for visibility -->
           <xpath expr="//tree//field[@name='partner_id']" position="after">
               <field name="ops_branch_id" optional="show"/>
               <field name="ops_business_unit_id" optional="show"/>
           </xpath>
           
       </field>
   </record>

2. Purchase Order Form Enhancement:
   <record id="view_purchase_order_form_ops_matrix" model="ir.ui.view">
       <field name="name">purchase.order.form.ops.matrix</field>
       <field name="model">purchase.order</field>
       <field name="inherit_id" ref="purchase.view_purchase_order_form"/>
       <field name="arch" type="xml">
           
           <xpath expr="//field[@name='partner_id']" position="after">
               <field name="ops_branch_id" 
                      options="{'no_create': True}"
                      domain="[('company_id', '=', company_id)]"
                      required="1"/>
               <field name="ops_business_unit_id"
                      options="{'no_create': True}"
                      domain="[('branch_ids', 'in', [ops_branch_id])]"
                      required="1"/>
           </xpath>
           
       </field>
   </record>

3. Stock Picking Form Enhancement:
   <record id="view_picking_form_ops_matrix" model="ir.ui.view">
       <field name="name">stock.picking.form.ops.matrix</field>
       <field name="model">stock.picking</field>
       <field name="inherit_id" ref="stock.view_picking_form"/>
       <field name="arch" type="xml">
           
           <xpath expr="//field[@name='partner_id']" position="after">
               <field name="ops_branch_id" readonly="1"/>
               <field name="ops_business_unit_id" readonly="1"/>
           </xpath>
           
       </field>
   </record>

4. Invoice Form Enhancement:
   <record id="view_move_form_ops_matrix" model="ir.ui.view">
       <field name="name">account.move.form.ops.matrix</field>
       <field name="model">account.move</field>
       <field name="inherit_id" ref="account.view_move_form"/>
       <field name="arch" type="xml">
           
           <xpath expr="//field[@name='partner_id']" position="after">
               <field name="ops_branch_id" 
                      attrs="{'readonly': [('state', '!=', 'draft')]}"/>
               <field name="ops_business_unit_id"
                      attrs="{'readonly': [('state', '!=', 'draft')]}"/>
           </xpath>
           
       </field>
   </record>

Key Features:
- Required fields (can't create transaction without branch/BU)
- Domain filters (show only valid branches/BUs)
- Readonly after confirmation (prevent changes)
- Visible in tree views for filtering
- No create/edit from dropdown (force selection of existing)

This ensures users ALWAYS select operational dimensions before creating transactions.
```

---

### **PHASE 3: ANALYTIC ACCOUNTING HIERARCHY**

#### **Prompt 3.1: Create Analytic Plan Structure** ☐

**File**: `ops_matrix_core/models/ops_analytic_setup.py`

```
Create: ops_matrix_core/models/ops_analytic_setup.py

Set up the dual-dimension analytic accounting hierarchy:

1. Model for Analytic Setup:
   class OpsAnalyticSetup(models.TransientModel):
       _name = 'ops.analytic.setup'
       _description = 'OPS Analytic Accounting Setup Helper'
       
       def setup_analytic_structure(self):
           """Ensure analytic plans and accounts are properly configured."""
           self._ensure_analytic_plans()
           self._sync_branch_analytic_accounts()
           self._sync_bu_analytic_accounts()
       
       def _ensure_analytic_plans(self):
           """Create Matrix Branch and Matrix BU analytic plans if not exist."""
           AnalyticPlan = self.env['account.analytic.plan']
           
           # Branch Plan
           if not AnalyticPlan.search([('name', '=', 'Matrix Branch')]):
               AnalyticPlan.create({
                   'name': 'Matrix Branch',
                   'company_id': False,  # Global plan
                   'description': 'Operational Branch tracking for Matrix reporting',
               })
           
           # Business Unit Plan
           if not AnalyticPlan.search([('name', '=', 'Matrix Business Unit')]):
               AnalyticPlan.create({
                   'name': 'Matrix Business Unit',
                   'company_id': False,
                   'description': 'Business Unit profit center tracking',
               })
       
       def _sync_branch_analytic_accounts(self):
           """Ensure all branches have analytic accounts."""
           branches = self.env['ops.branch'].search([('analytic_account_id', '=', False)])
           for branch in branches:
               branch._create_analytic_accounts()
       
       def _sync_bu_analytic_accounts(self):
           """Ensure all business units have analytic accounts."""
           bus = self.env['ops.business.unit'].search([('analytic_account_id', '=', False)])
           for bu in bus:
               bu._create_analytic_accounts()

2. Add Constraint to Prevent Deletion:
   
   class AccountAnalyticAccount(models.Model):
       _inherit = 'account.analytic.account'
       
       def unlink(self):
           """Prevent deletion if linked to active branch or BU."""
           Branch = self.env['ops.branch']
           BU = self.env['ops.business.unit']
           
           for account in self:
               # Check if linked to branch
               branch = Branch.search([('analytic_account_id', '=', account.id), ('active', '=', True)], limit=1)
               if branch:
                   raise UserError(
                       f"Cannot delete analytic account '{account.name}' because it is linked to "
                       f"active branch '{branch.name}'. Deactivate the branch first."
                   )
               
               # Check if linked to BU
               bu = BU.search([('analytic_account_id', '=', account.id), ('active', '=', True)], limit=1)
               if bu:
                   raise UserError(
                       f"Cannot delete analytic account '{account.name}' because it is linked to "
                       f"active business unit '{bu.name}'. Deactivate the BU first."
                   )
           
           return super().unlink()

3. Add Sync Functionality to Branch/BU Models:
   
   class OpsBranch(models.Model):
       _inherit = 'ops.branch'
       
       def write(self, vals):
           result = super().write(vals)
           if 'name' in vals or 'code' in vals:
               self._sync_analytic_account_name()
           return result
       
       def _sync_analytic_account_name(self):
           for branch in self:
               if branch.analytic_account_id:
                   branch.analytic_account_id.write({
                       'name': f"{branch.code} - {branch.name}",
                       'code': branch.code,
                   })

This ensures analytic tracking is automatically maintained and protected.
```

---

#### **Prompt 3.2: Update Account Move for Analytic Distribution** ☐

**File**: `ops_matrix_core/models/account_move.py`

```
Update: ops_matrix_core/models/account_move.py

Enhance account.move to automatically assign analytic dimensions (Odoo 19 analytic_distribution):

1. Inherit Account Move:
   class AccountMove(models.Model):
       _inherit = ['account.move', 'ops.matrix.mixin']
       _name = 'account.move'
       
       # Matrix fields inherited from mixin

2. Override Create for Auto-Distribution:
   
   @api.model_create_multi
   def create(self, vals_list):
       """Auto-assign analytic distribution from matrix dimensions."""
       for vals in vals_list:
           # If branch/BU provided, compute analytic distribution
           if vals.get('ops_branch_id') or vals.get('ops_business_unit_id'):
               distribution = {}
               
               if vals.get('ops_branch_id'):
                   branch = self.env['ops.branch'].browse(vals['ops_branch_id'])
                   if branch.analytic_account_id:
                       distribution[str(branch.analytic_account_id.id)] = 50
               
               if vals.get('ops_business_unit_id'):
                   bu = self.env['ops.business.unit'].browse(vals['ops_business_unit_id'])
                   if bu.analytic_account_id:
                       distribution[str(bu.analytic_account_id.id)] = 50
               
               if distribution:
                   vals['invoice_line_ids'] = vals.get('invoice_line_ids', [])
                   # Apply distribution to all lines
                   for line_vals in vals['invoice_line_ids']:
                       if isinstance(line_vals, (list, tuple)) and line_vals[0] == 0:
                           line_vals[2]['analytic_distribution'] = distribution
       
       return super().create(vals_list)

3. Update Account Move Line:
   
   class AccountMoveLine(models.Model):
       _inherit = ['account.move.line', 'ops.matrix.mixin']
       _name = 'account.move.line'
       
       @api.onchange('ops_branch_id', 'ops_business_unit_id')
       def _onchange_matrix_analytic(self):
           """Update analytic distribution when dimensions change."""
           distribution = {}
           
           if self.ops_branch_id and self.ops_branch_id.analytic_account_id:
               distribution[str(self.ops_branch_id.analytic_account_id.id)] = 50
           
           if self.ops_business_unit_id and self.ops_business_unit_id.analytic_account_id:
               distribution[str(self.ops_business_unit_id.analytic_account_id.id)] = 50
           
           self.analytic_distribution = distribution if distribution else False

4. Add Validation:
   
   @api.constrains('ops_branch_id', 'ops_business_unit_id')
   def _check_matrix_dimensions(self):
       """Ensure required dimensions are present."""
       for move in self:
           if move.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
               if not move.ops_branch_id:
                   raise ValidationError("Branch is required for invoices.")
               if not move.ops_business_unit_id:
                   raise ValidationError("Business Unit is required for invoices.")

5. Add Compute Method for Summary:
   
   ops_analytic_summary = fields.Char(compute='_compute_analytic_summary', string='Analytic Summary')
   
   @api.depends('ops_branch_id', 'ops_business_unit_id')
   def _compute_analytic_summary(self):
       for move in self:
           parts = []
           if move.ops_branch_id:
               parts.append(f"Branch: {move.ops_branch_id.code}")
           if move.ops_business_unit_id:
               parts.append(f"BU: {move.ops_business_unit_id.code}")
           move.ops_analytic_summary = " | ".join(parts) if parts else "No dimensions"

This ensures all journal entries carry proper analytic distribution for dual-dimension reporting.
```

---

### **PHASE 4: SECURITY MODEL**

#### **Prompt 4.1: Update User Model for Matrix Access** ☐

**File**: `ops_matrix_core/models/res_users.py`

```
Update: ops_matrix_core/models/res_users.py

Extend user model for matrix-based access control:

1. Add Access Control Fields:
   
   class ResUsers(models.Model):
       _inherit = 'res.users'
       
       # Multi-company access (standard Odoo)
       # company_ids already exists (Many2many to res.company)
       
       # Multi-branch access
       allowed_branch_ids = fields.Many2many(
           'ops.branch', 
           'user_branch_access_rel', 
           'user_id', 
           'branch_id',
           string='Allowed Branches',
           help='Branches this user can access'
       )
       
       # Multi-BU access  
       allowed_business_unit_ids = fields.Many2many(
           'ops.business.unit',
           'user_bu_access_rel',
           'user_id',
           'bu_id',
           string='Allowed Business Units',
           help='Business units this user can access'
       )
       
       # Defaults
       default_branch_id = fields.Many2one('ops.branch', string='Default Branch')
       default_business_unit_id = fields.Many2one('ops.business.unit', string='Default BU')
       
       # Role indicator
       is_cross_branch_bu_leader = fields.Boolean(
           string='Cross-Branch BU Leader',
           help='Can access same BU across multiple branches'
       )

2. Add Computed Access Methods:
   
   def get_effective_matrix_access(self):
       """Returns computed access based on user's persona and groups."""
       self.ensure_one()
       
       # If admin, grant all access
       if self.has_group('base.group_system'):
           return {
               'companies': self.env['res.company'].search([]),
               'branches': self.env['ops.branch'].search([]),
               'business_units': self.env['ops.business.unit'].search([]),
           }
       
       # Get from direct assignments
       companies = self.company_ids
       branches = self.allowed_branch_ids
       business_units = self.allowed_business_unit_ids
       
       # Get from persona (if persona module exists)
       if hasattr(self, 'persona_ids'):
           for persona in self.persona_ids:
               if hasattr(persona, 'allowed_branch_ids'):
                   branches |= persona.allowed_branch_ids
               if hasattr(persona, 'allowed_business_unit_ids'):
                   business_units |= persona.allowed_business_unit_ids
       
       return {
           'companies': companies,
           'branches': branches,
           'business_units': business_units,
       }
   
   def can_access_branch(self, branch_id):
       """Check if user can access specific branch."""
       self.ensure_one()
       if self.has_group('base.group_system'):
           return True
       return branch_id in self.allowed_branch_ids.ids
   
   def can_access_business_unit(self, bu_id):
       """Check if user can access specific business unit."""
       self.ensure_one()
       if self.has_group('base.group_system'):
           return True
       return bu_id in self.allowed_business_unit_ids.ids

3. Add Constraints:
   
   @api.constrains('default_branch_id', 'allowed_branch_ids')
   def _check_default_branch(self):
       for user in self:
           if user.default_branch_id and user.default_branch_id not in user.allowed_branch_ids:
               raise ValidationError(
                   f"Default branch must be in user's allowed branches."
               )

4. Override Write to Update Dependent Records:
   
   def write(self, vals):
       result = super().write(vals)
       # If allowed branches change, may need to update user's active transactions
       if 'allowed_branch_ids' in vals or 'allowed_business_unit_ids' in vals:
           # Log or notify for security audit
           _logger.info(f"User {self.name} (ID: {self.id}) access rights modified")
       return result

This provides flexible, role-based matrix access control.
```

---

#### **Prompt 4.2: Create Security Rules for Siloed Access** ☐

**File**: `ops_matrix_core/security/ir_rule.xml`

```
Update: ops_matrix_core/security/ir_rule.xml

Implement record rules for each model to enforce siloed access:

1. Company-Level Access Rule:
   <record id="rule_ops_company_access" model="ir.rule">
       <field name="name">OPS: User can only access allowed companies</field>
       <field name="model_id" ref="model_res_company"/>
       <field name="domain_force">[('id', 'in', user.company_ids.ids)]</field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>

2. Branch-Level Access Rule:
   <record id="rule_ops_branch_access" model="ir.rule">
       <field name="name">OPS: User can only access allowed branches</field>
       <field name="model_id" ref="model_ops_branch"/>
       <field name="domain_force">
           ['|', 
               ('id', 'in', user.allowed_branch_ids.ids),
               ('company_id', 'in', user.company_ids.ids)  # Company managers see all branches
           ]
       </field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>

3. Business Unit Access Rule:
   <record id="rule_ops_bu_access" model="ir.rule">
       <field name="name">OPS: User can only access allowed business units</field>
       <field name="model_id" ref="model_ops_business_unit"/>
       <field name="domain_force">
           ['|',
               ('id', 'in', user.allowed_business_unit_ids.ids),
               ('company_ids', 'in', user.company_ids.ids)  # Company managers see all BUs
           ]
       </field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>

4. Sale Order Access Rule:
   <record id="rule_ops_sale_order_access" model="ir.rule">
       <field name="name">OPS: User can only access sales from allowed branches/BUs</field>
       <field name="model_id" ref="sale.model_sale_order"/>
       <field name="domain_force">
           ['|', '|',
               ('ops_branch_id', 'in', user.allowed_branch_ids.ids),
               ('ops_business_unit_id', 'in', user.allowed_business_unit_ids.ids),
               ('company_id', 'in', user.company_ids.ids)
           ]
       </field>
       <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
   </record>

5. Purchase Order Access Rule:
   <record id="rule_ops_purchase_order_access" model="ir.rule">
       <field name="name">OPS: User can only access purchases from allowed branches/BUs</field>
       <field name="model_id" ref="purchase.model_purchase_order"/>
       <field name="domain_force">
           ['|', '|',
               ('ops_branch_id', 'in', user.allowed_branch_ids.ids),
               ('ops_business_unit_id', 'in', user.allowed_business_unit_ids.ids),
               ('company_id', 'in', user.company_ids.ids)
           ]
       </field>
       <field name="groups" eval="[(4, ref('purchase.group_purchase_user'))]"/>
   </record>

6. Invoice Access Rule:
   <record id="rule_ops_account_move_access" model="ir.rule">
       <field name="name">OPS: User can only access invoices from allowed branches/BUs</field>
       <field name="model_id" ref="account.model_account_move"/>
       <field name="domain_force">
           ['|', '|', '|',
               ('ops_branch_id', 'in', user.allowed_branch_ids.ids),
               ('ops_business_unit_id', 'in', user.allowed_business_unit_ids.ids),
               ('company_id', 'in', user.company_ids.ids),
               ('move_type', 'not in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'])  # Allow non-invoices
           ]
       </field>
       <field name="groups" eval="[(4, ref('account.group_account_user'))]"/>
   </record>

7. Stock Picking Access Rule:
   <record id="rule_ops_stock_picking_access" model="ir.rule">
       <field name="name">OPS: User can only access stock from allowed branches</field>
       <field name="model_id" ref="stock.model_stock_picking"/>
       <field name="domain_force">
           ['|',
               ('ops_branch_id', 'in', user.allowed_branch_ids.ids),
               ('company_id', 'in', user.company_ids.ids)
           ]
       </field>
       <field name="groups" eval="[(4, ref('stock.group_stock_user'))]"/>
   </record>

8. Cross-Branch BU Leader Override:
   <record id="rule_ops_cross_branch_bu_leader" model="ir.rule">
       <field name="name">OPS: Cross-branch BU leaders see their BU everywhere</field>
       <field name="model_id" ref="sale.model_sale_order"/>
       <field name="domain_force">
           [('ops_business_unit_id', 'in', user.allowed_business_unit_ids.ids)]
       </field>
       <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_bu_leader'))]"/>
   </record>

Key Features:
- OR operator allows access if ANY condition is met
- Company managers see all data in their companies
- Branch users see only their branch data
- Cross-branch BU leaders see their BU across all branches
- System admins bypass all rules (implicit in Odoo)
```

---

### **PHASE 5: REPORTING FRAMEWORK**

#### **Prompt 5.1: Create Consolidated Financial Reporting** ☐

**File**: `ops_matrix_accounting/models/ops_consolidated_reporting.py`

```
Create: ops_matrix_accounting/models/ops_consolidated_reporting.py

Build reporting engine for hierarchical financial reports:

1. Company Consolidation Report:
   
   class OpsCompanyConsolidation(models.TransientModel):
       _name = 'ops.company.consolidation'
       _description = 'Company-Level Consolidated Report'
       
       company_id = fields.Many2one('res.company', required=True)
       date_from = fields.Date(required=True)
       date_to = fields.Date(required=True)
       
       def get_company_pnl(self):
           """Get consolidated P&L for all branches in company."""
           self.ensure_one()
           
           # Get all branches in company
           branches = self.env['ops.branch'].search([('company_id', '=', self.company_id.id)])
           
           # Aggregate using _read_group for performance
           MoveLine = self.env['account.move.line']
           domain = [
               ('date', '>=', self.date_from),
               ('date', '<=', self.date_to),
               ('company_id', '=', self.company_id.id),
               ('move_id.state', '=', 'posted'),
           ]
           
           grouped_data = MoveLine._read_group(
               domain,
               ['account_id', 'ops_branch_id', 'debit', 'credit', 'balance'],
               ['account_id', 'ops_branch_id'],
           )
           
           # Process and structure data
           income_total = 0.0
           expense_total = 0.0
           
           for group in grouped_data:
               account = self.env['account.account'].browse(group['account_id'][0])
               if account.account_type in ['income', 'income_other']:
                   income_total += group['credit'] - group['debit']
               elif account.account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                   expense_total += group['debit'] - group['credit']
           
           return {
               'company': self.company_id.name,
               'period': f"{self.date_from} to {self.date_to}",
               'income_total': income_total,
               'expense_total': expense_total,
               'net_profit': income_total - expense_total,
               'branches': len(branches),
           }

2. Branch Report:
   
   class OpsBranchReport(models.TransientModel):
       _name = 'ops.branch.report'
       _description = 'Branch-Level P&L Report'
       
       branch_id = fields.Many2one('ops.branch', required=True)
       date_from = fields.Date(required=True)
       date_to = fields.Date(required=True)
       
       def get_branch_pnl(self):
           """Get P&L for specific branch."""
           self.ensure_one()
           
           MoveLine = self.env['account.move.line']
           domain = [
               ('date', '>=', self.date_from),
               ('date', '<=', self.date_to),
               ('ops_branch_id', '=', self.branch_id.id),
               ('move_id.state', '=', 'posted'),
           ]
           
           grouped_data = MoveLine._read_group(
               domain,
               ['account_id', 'ops_business_unit_id', 'debit', 'credit'],
               ['account_id', 'ops_business_unit_id'],
           )
           
           # Structure by BU
           bu_performance = {}
           for group in grouped_data:
               account = self.env['account.account'].browse(group['account_id'][0])
               bu_id = group['ops_business_unit_id'][0] if group.get('ops_business_unit_id') else False
               
               if bu_id not in bu_performance:
                   bu_performance[bu_id] = {'income': 0.0, 'expense': 0.0}
               
               if account.account_type in ['income', 'income_other']:
                   bu_performance[bu_id]['income'] += group['credit'] - group['debit']
               elif account.account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                   bu_performance[bu_id]['expense'] += group['debit'] - group['credit']
           
           return {
               'branch': self.branch_id.name,
               'period': f"{self.date_from} to {self.date_to}",
               'bu_performance': bu_performance,
           }

3. Business Unit Report (Cross-Branch):
   
   class OpsBusinessUnitReport(models.TransientModel):
       _name = 'ops.business.unit.report'
       _description = 'Business Unit Profitability Report'
       
       business_unit_id = fields.Many2one('ops.business.unit', required=True)
       date_from = fields.Date(required=True)
       date_to = fields.Date(required=True)
       branch_ids = fields.Many2many('ops.branch', string='Filter Branches')
       
       def get_bu_pnl(self):
           """Get BU P&L across branches (or filtered branches)."""
           self.ensure_one()
           
           MoveLine = self.env['account.move.line']
           domain = [
               ('date', '>=', self.date_from),
               ('date', '<=', self.date_to),
               ('ops_business_unit_id', '=', self.business_unit_id.id),
               ('move_id.state', '=', 'posted'),
           ]
           
           if self.branch_ids:
               domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
           
           grouped_data = MoveLine._read_group(
               domain,
               ['account_id', 'ops_branch_id', 'debit', 'credit'],
               ['account_id', 'ops_branch_id'],
           )
           
           # Structure by branch
           branch_performance = {}
           for group in grouped_data:
               account = self.env['account.account'].browse(group['account_id'][0])
               branch_id = group['ops_branch_id'][0] if group.get('ops_branch_id') else False
               
               if branch_id not in branch_performance:
                   branch_performance[branch_id] = {'income': 0.0, 'expense': 0.0}
               
               if account.account_type in ['income', 'income_other']:
                   branch_performance[branch_id]['income'] += group['credit'] - group['debit']
               elif account.account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                   branch_performance[branch_id]['expense'] += group['debit'] - group['credit']
           
           return {
               'business_unit': self.business_unit_id.name,
               'period': f"{self.date_from} to {self.date_to}",
               'branch_performance': branch_performance,
               'total_branches': len(branch_performance),
           }

4. Consolidated Balance Sheet:
   
   class OpsConsolidatedBalanceSheet(models.TransientModel):
       _name = 'ops.consolidated.balance.sheet'
       _description = 'Group-Level Balance Sheet'
       
       company_ids = fields.Many2many('res.company', string='Companies', required=True)
       date = fields.Date(required=True)
       
       def get_consolidated_balance_sheet(self):
           """Get balance sheet for multiple companies (group level)."""
           MoveLine = self.env['account.move.line']
           domain = [
               ('date', '<=', self.date),
               ('company_id', 'in', self.company_ids.ids),
               ('move_id.state', '=', 'posted'),
           ]
           
           grouped_data = MoveLine._read_group(
               domain,
               ['account_id', 'company_id', 'balance'],
               ['account_id', 'company_id'],
           )
           
           # Aggregate by account type
           assets = expenses = liabilities = equity = 0.0
           
           for group in grouped_data:
               account = self.env['account.account'].browse(group['account_id'][0])
               balance = group['balance']
               
               if account.account_type.startswith('asset'):
                   assets += balance
               elif account.account_type.startswith('liability'):
                   liabilities += balance
               elif account.account_type == 'equity':
                   equity += balance
           
           return {
               'companies': self.company_ids.mapped('name'),
               'date': self.date,
               'assets': assets,
               'liabilities': liabilities,
               'equity': equity,
           }

All reports use _read_group() for database-level aggregation (performance optimized).
```

---

#### **Prompt 5.2: Update General Ledger Wizard for Matrix Filtering** ☐

**File**: `ops_matrix_accounting/wizard/ops_general_ledger_wizard.py`

```
Update: ops_matrix_accounting/wizard/ops_general_ledger_wizard.py

Enhance GL wizard to include matrix dimension filtering:

1. Add Matrix Filter Fields:
   
   class OpsGeneralLedgerWizard(models.TransientModel):
       _name = 'ops.general.ledger.wizard'
       _description = 'General Ledger Report Wizard with Matrix Dimensions'
       
       # Existing fields
       date_from = fields.Date(required=True)
       date_to = fields.Date(required=True)
       company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
       target_move = fields.Selection([('posted', 'Posted'), ('all', 'All')], default='posted')
       journal_ids = fields.Many2many('account.journal')
       account_ids = fields.Many2many('account.account')
       
       # NEW: Matrix dimension filters
       branch_ids = fields.Many2many(
           'ops.branch',
           string='Branches',
           help='Filter by specific branches. Leave empty for all branches.',
           domain="[('company_id', '=', company_id)]"
       )
       business_unit_ids = fields.Many2many(
           'ops.business.unit',
           string='Business Units',
           help='Filter by specific business units. Leave empty for all BUs.'
       )
       
       # NEW: Consolidation options
       consolidate_by_branch = fields.Boolean(
           string='Group by Branch',
           help='Show totals grouped by branch'
       )
       consolidate_by_bu = fields.Boolean(
           string='Group by Business Unit',
           help='Show totals grouped by business unit'
       )

2. Update Domain Building:
   
   def _get_domain(self):
       """Build domain with matrix dimension filters."""
       domain = [
           ('date', '>=', self.date_from),
           ('date', '<=', self.date_to),
           ('company_id', '=', self.company_id.id),
       ]
       
       if self.target_move == 'posted':
           domain.append(('move_id.state', '=', 'posted'))
       
       if self.journal_ids:
           domain.append(('journal_id', 'in', self.journal_ids.ids))
       
       if self.account_ids:
           domain.append(('account_id', 'in', self.account_ids.ids))
       
       # NEW: Matrix filters
       if self.branch_ids:
           domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
       
       if self.business_unit_ids:
           domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
       
       return domain

3. Update Report Generation:
   
   def action_print_pdf(self):
       """Generate PDF with matrix dimension grouping."""
       self.ensure_one()
       
       MoveLine = self.env['account.move.line']
       domain = self._get_domain()
       
       # Determine grouping fields
       groupby_fields = ['account_id']
       if self.consolidate_by_branch:
           groupby_fields.append('ops_branch_id')
       if self.consolidate_by_bu:
           groupby_fields.append('ops_business_unit_id')
       
       # Use search_read for detail or _read_group for consolidation
       if self.consolidate_by_branch or self.consolidate_by_bu:
           # Consolidated report
           grouped_data = MoveLine._read_group(
               domain,
               groupby_fields + ['debit', 'credit', 'balance'],
               groupby_fields,
           )
           
           report_data = {
               'grouped': True,
               'data': grouped_data,
               'groupby': groupby_fields,
           }
       else:
           # Detailed report
           lines_data = MoveLine.search_read(
               domain,
               ['date', 'account_id', 'ops_branch_id', 'ops_business_unit_id', 
                'partner_id', 'move_id', 'debit', 'credit', 'balance', 'name'],
               limit=10000,
               order='date, move_id, id'
           )
           
           report_data = {
               'grouped': False,
               'data': lines_data,
           }
       
       return self.env.ref('ops_matrix_accounting.report_general_ledger').report_action(
           self, data=report_data
       )
   
   def action_print_xlsx(self):
       """Generate XLSX export with matrix dimensions."""
       self.ensure_one()
       return {
           'type': 'ir.actions.report',
           'report_type': 'xlsx',
           'report_name': 'ops_matrix_accounting.report_general_ledger_xlsx',
           'data': {
               'wizard_id': self.id,
               'consolidate_by_branch': self.consolidate_by_branch,
               'consolidate_by_bu': self.consolidate_by_bu,
           },
       }

4. Add Drill-Down Actions:
   
   def action_view_moves(self):
       """Open filtered journal entries."""
       self.ensure_one()
       domain = self._get_domain()
       
       return {
           'name': 'Journal Entries',
           'type': 'ir.actions.act_window',
           'res_model': 'account.move',
           'view_mode': 'tree,form',
           'domain': [('line_ids', 'any', domain)],
           'context': {
               'search_default_group_by_date': 1,
               'search_default_group_by_branch': 1 if self.consolidate_by_branch else 0,
           },
       }

This allows users to filter GL reports by Branch, BU, or both, and view consolidated or detailed output.
```

---

### **PHASE 6: DASHBOARDS**

#### **Prompt 6.1: Create Multi-Level Role-Based Dashboards** ☐

**Files**: `ops_matrix_core/views/ops_dashboard_*.xml`

```
Create dashboard views for different user roles (CE-compatible using pivot/graph views):

IMPORTANT: Odoo CE does not have spreadsheet_dashboard module (Enterprise only).
Use native pivot views + graph views + custom actions for CE compatibility.

1. Executive Dashboard (Company Level):
   
   File: ops_matrix_core/views/ops_executive_dashboard_views.xml
   
   <record id="view_ops_executive_dashboard" model="ir.ui.view">
       <field name="name">ops.executive.dashboard</field>
       <field name="model">account.move.line</field>
       <field name="arch" type="xml">
           <pivot string="Executive Dashboard - Company Performance">
               <field name="company_id" type="row"/>
               <field name="ops_branch_id" type="row"/>
               <field name="date" interval="month" type="col"/>
               <field name="balance" type="measure"/>
           </pivot>
       </field>
   </record>
   
   <record id="action_ops_executive_dashboard" model="ir.actions.act_window">
       <field name="name">Executive Dashboard</field>
       <field name="res_model">account.move.line</field>
       <field name="view_mode">pivot,graph</field>
       <field name="view_id" ref="view_ops_executive_dashboard"/>
       <field name="domain">[('move_id.state', '=', 'posted')]</field>
       <field name="context">{
           'search_default_group_by_company': 1,
           'group_by': ['company_id', 'ops_branch_id']
       }</field>
   </record>

2. Branch Manager Dashboard:
   
   File: ops_matrix_core/views/ops_branch_dashboard_views.xml
   
   <record id="view_ops_branch_dashboard" model="ir.ui.view">
       <field name="name">ops.branch.dashboard</field>
       <field name="model">account.move.line</field>
       <field name="arch" type="xml">
           <pivot string="Branch Performance Dashboard">
               <field name="ops_business_unit_id" type="row"/>
               <field name="account_id" type="row"/>
               <field name="date" interval="week" type="col"/>
               <field name="debit" type="measure"/>
               <field name="credit" type="measure"/>
               <field name="balance" type="measure"/>
           </pivot>
       </field>
   </record>
   
   <record id="action_ops_branch_dashboard" model="ir.actions.act_window">
       <field name="name">Branch Performance</field>
       <field name="res_model">account.move.line</field>
       <field name="view_mode">pivot,graph</field>
       <field name="view_id" ref="view_ops_branch_dashboard"/>
       <field name="domain">[
           ('move_id.state', '=', 'posted'),
           ('ops_branch_id', '=', user.default_branch_id.id)
       ]</field>
       <field name="context">{
           'search_default_group_by_bu': 1
       }</field>
   </record>

3. BU Leader Dashboard (Cross-Branch):
   
   File: ops_matrix_core/views/ops_bu_dashboard_views.xml
   
   <record id="view_ops_bu_leader_dashboard" model="ir.ui.view">
       <field name="name">ops.bu.leader.dashboard</field>
       <field name="model">account.move.line</field>
       <field name="arch" type="xml">
           <pivot string="Business Unit Performance Across Branches">
               <field name="ops_branch_id" type="row"/>
               <field name="account_id" type="row"/>
               <field name="date" interval="month" type="col"/>
               <field name="balance" type="measure"/>
           </pivot>
       </field>
   </record>
   
   <record id="action_ops_bu_leader_dashboard" model="ir.actions.act_window">
       <field name="name">My Business Unit Performance</field>
       <field name="res_model">account.move.line</field>
       <field name="view_mode">pivot,graph</field>
       <field name="view_id" ref="view_ops_bu_leader_dashboard"/>
       <field name="domain">[
           ('move_id.state', '=', 'posted'),
           ('ops_business_unit_id', '=', user.default_business_unit_id.id)
       ]</field>
       <field name="context">{
           'search_default_group_by_branch': 1,
           'search_default_current_year': 1
       }</field>
   </record>

4. Sales Dashboard by Matrix:
   
   File: ops_matrix_core/views/ops_sales_dashboard_views.xml
   
   <record id="view_ops_sales_dashboard" model="ir.ui.view">
       <field name="name">ops.sales.dashboard</field>
       <field name="model">sale.order</field>
       <field name="arch" type="xml">
           <pivot string="Sales by Branch and BU">
               <field name="ops_branch_id" type="row"/>
               <field name="ops_business_unit_id" type="row"/>
               <field name="date_order" interval="month" type="col"/>
               <field name="amount_total" type="measure"/>
           </pivot>
       </field>
   </record>
   
   <record id="action_ops_sales_dashboard" model="ir.actions.act_window">
       <field name="name">Sales Performance Matrix</field>
       <field name="res_model">sale.order</field>
       <field name="view_mode">pivot,graph,tree,form</field>
       <field name="view_id" ref="view_ops_sales_dashboard"/>
       <field name="domain">[('state', 'in', ['sale', 'done'])]</field>
   </record>

5. Menu Structure:
   
   <menuitem id="menu_ops_dashboards" 
             name="OPS Dashboards" 
             parent="account.menu_finance"
             sequence="1"/>
   
   <menuitem id="menu_ops_executive_dashboard"
             name="Executive View"
             parent="menu_ops_dashboards"
             action="action_ops_executive_dashboard"
             groups="ops_matrix_core.group_ops_executive"
             sequence="10"/>
   
   <menuitem id="menu_ops_branch_dashboard"
             name="Branch Performance"
             parent="menu_ops_dashboards"
             action="action_ops_branch_dashboard"
             groups="ops_matrix_core.group_ops_branch_manager"
             sequence="20"/>
   
   <menuitem id="menu_ops_bu_leader_dashboard"
             name="Business Unit View"
             parent="menu_ops_dashboards"
             action="action_ops_bu_leader_dashboard"
             groups="ops_matrix_core.group_ops_bu_leader"
             sequence="30"/>

ALTERNATIVE for Enterprise Edition:
If using Odoo Enterprise, replace pivot views with spreadsheet_dashboard for interactive reporting.

This provides role-specific views without requiring Enterprise Edition modules.
```

---

### **PHASE 7: GOVERNANCE LAYER**

#### **Prompt 7.1: Update Persona Model for Branch/BU Assignment** ☐

**File**: `ops_matrix_core/models/ops_persona.py`

```
Update existing file: ops_matrix_core/models/ops_persona.py

Enhance persona model to work with new branch/BU structure:

1. Update Fields:
   
   class OpsPersona(models.Model):
       _name = 'ops.persona'
       _inherit = ['mail.thread', 'mail.activity.mixin']
       _description = 'OPS Persona - Role Assignment'
       
       # Existing fields
       name = fields.Char(required=True, tracking=True)
       code = fields.Char(required=True, copy=False, default='New')
       user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
       active = fields.Boolean(default=True)
       
       # UPDATE: Matrix assignment
       company_id = fields.Many2one('res.company', required=True)
       
       # CHANGE from branch_id (single) to branch_ids (multi)
       branch_ids = fields.Many2many(
           'ops.branch',
           'persona_branch_rel',
           'persona_id',
           'branch_id',
           string='Assigned Branches',
           domain="[('company_id', '=', company_id)]",
           help='Branches this persona can access'
       )
       
       # CHANGE from business_unit_id (single) to business_unit_ids (multi)
       business_unit_ids = fields.Many2many(
           'ops.business.unit',
           'persona_bu_rel',
           'persona_id',
           'bu_id',
           string='Assigned Business Units',
           help='Business units this persona manages'
       )
       
       # Default selections
       default_branch_id = fields.Many2one(
           'ops.branch',
           string='Default Branch',
           domain="[('id', 'in', branch_ids)]"
       )
       default_business_unit_id = fields.Many2one(
           'ops.business.unit',
           string='Default Business Unit',
           domain="[('id', 'in', business_unit_ids)]"
       )
       
       # Role indicators
       is_branch_manager = fields.Boolean(string='Branch Manager')
       is_bu_leader = fields.Boolean(string='Business Unit Leader')
       is_cross_branch = fields.Boolean(
           string='Cross-Branch Authority',
           help='Can access same BU across multiple branches'
       )

2. Add Sync Method:
   
   @api.model_create_multi
   def create(self, vals_list):
       """Auto-sync persona access to user."""
       personas = super().create(vals_list)
       personas._sync_user_access()
       return personas
   
   def write(self, vals):
       """Auto-sync when access changes."""
       result = super().write(vals)
       if any(field in vals for field in ['branch_ids', 'business_unit_ids', 'default_branch_id']):
           self._sync_user_access()
       return result
   
   def _sync_user_access(self):
       """Sync persona access to res.users."""
       for persona in self:
           if persona.user_id:
               # Update user's allowed branches and BUs
               persona.user_id.write({
                   'allowed_branch_ids': [(6, 0, persona.branch_ids.ids)],
                   'allowed_business_unit_ids': [(6, 0, persona.business_unit_ids.ids)],
                   'default_branch_id': persona.default_branch_id.id if persona.default_branch_id else False,
                   'default_business_unit_id': persona.default_business_unit_id.id if persona.default_business_unit_id else False,
                   'is_cross_branch_bu_leader': persona.is_cross_branch,
               })

3. Add Validation:
   
   @api.constrains('branch_ids', 'company_id')
   def _check_branch_company(self):
       """Ensure all branches belong to persona's company."""
       for persona in self:
           invalid_branches = persona.branch_ids.filtered(
               lambda b: b.company_id != persona.company_id
           )
           if invalid_branches:
               raise ValidationError(
                   f"Branches {invalid_branches.mapped('name')} do not belong to company {persona.company_id.name}"
               )
   
   @api.constrains('default_branch_id', 'branch_ids')
   def _check_default_branch(self):
       """Ensure default branch is in assigned branches."""
       for persona in self:
           if persona.default_branch_id and persona.default_branch_id not in persona.branch_ids:
               raise ValidationError("Default branch must be in assigned branches.")

4. Add Computed Fields:
   
   branch_count = fields.Integer(compute='_compute_branch_count', string='Branch Count')
   bu_count = fields.Integer(compute='_compute_bu_count', string='BU Count')
   
   @api.depends('branch_ids')
   def _compute_branch_count(self):
       for persona in self:
           persona.branch_count = len(persona.branch_ids)
   
   @api.depends('business_unit_ids')
   def _compute_bu_count(self):
       for persona in self:
           persona.bu_count = len(persona.business_unit_ids)

This allows one user to have multiple personas with different matrix access patterns.
```

---

#### **Prompt 7.2: Update Governance Rules for Matrix, Discount & Margin Enforcement** ☐

**File**: `ops_matrix_core/models/ops_governance_rule.py`

```
Update existing file: ops_matrix_core/models/ops_governance_rule.py

Enhance governance rules to validate branch/BU requirements AND enforce discount/margin/pricing controls:

1. Add Matrix and Pricing Validation Rules:
   
   class OpsGovernanceRule(models.Model):
       _name = 'ops.governance.rule'
       _inherit = ['mail.thread']
       _description = 'OPS Governance Rule'
       
       # Existing fields
       name = fields.Char(required=True)
       model_id = fields.Many2one('ir.model', required=True)
       rule_type = fields.Selection([
           ('approval', 'Approval Required'),
           ('validation', 'Validation'),
           ('notification', 'Notification'),
           ('discount_limit', 'Discount Limit'),
           ('margin_protection', 'Margin Protection'),
           ('price_override', 'Price Override Control'),
       ], required=True)
       
       # Matrix enforcement
       enforce_branch_bu = fields.Boolean(
           string='Enforce Branch/BU Selection',
           help='Require branch and business unit on transactions'
       )
       allowed_branch_ids = fields.Many2many(
           'ops.branch',
           'rule_branch_rel',
           string='Allowed Branches',
           help='Restrict to specific branches. Empty = all branches.'
       )
       allowed_business_unit_ids = fields.Many2many(
           'ops.business.unit',
           'rule_bu_rel',
           string='Allowed Business Units',
           help='Restrict to specific BUs. Empty = all BUs.'
       )
       
       # NEW: Discount Control
       enforce_discount_limit = fields.Boolean(
           string='Enforce Discount Limit',
           help='Require approval when discount exceeds limit'
       )
       discount_limit_percent = fields.Float(
           string='Max Discount %',
           help='Maximum discount percentage without approval'
       )
       discount_limit_by_role = fields.One2many(
           'ops.governance.discount.limit',
           'rule_id',
           string='Role-Based Discount Limits'
       )
       
       # NEW: Margin Protection
       enforce_margin_protection = fields.Boolean(
           string='Enforce Margin Protection',
           help='Require approval when margin falls below threshold'
       )
       minimum_margin_percent = fields.Float(
           string='Minimum Margin %',
           help='Minimum acceptable margin percentage'
       )
       margin_by_category = fields.One2many(
           'ops.governance.margin.rule',
           'rule_id',
           string='Category-Specific Margins'
       )
       
       # NEW: Pricing Authority
       enforce_price_override = fields.Boolean(
           string='Enforce Price Override Control',
           help='Require approval for manual price changes'
       )
       max_price_variance_percent = fields.Float(
           string='Max Price Variance %',
           help='Maximum price variance from pricelist without approval'
       )
       price_authority_by_role = fields.One2many(
           'ops.governance.price.authority',
           'rule_id',
           string='Role-Based Price Authority'
       )

2. Add Related Models for Role-Based Controls:
   
   class OpsGovernanceDiscountLimit(models.Model):
       _name = 'ops.governance.discount.limit'
       _description = 'Role-Based Discount Limits'
       
       rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade')
       persona_id = fields.Many2one('ops.persona', string='Persona/Role')
       user_group_id = fields.Many2one('res.groups', string='User Group')
       max_discount_percent = fields.Float(string='Max Discount %', required=True)
       approval_required_above = fields.Float(string='Approval Required Above %')
       approver_persona_ids = fields.Many2many('ops.persona', string='Approvers')
   
   class OpsGovernanceMarginRule(models.Model):
       _name = 'ops.governance.margin.rule'
       _description = 'Category-Specific Margin Rules'
       
       rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade')
       product_category_id = fields.Many2one('product.category', string='Product Category')
       business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')
       minimum_margin_percent = fields.Float(string='Minimum Margin %', required=True)
       warning_margin_percent = fields.Float(string='Warning Threshold %')
       escalation_required_below = fields.Float(string='Escalation Required Below %')
       approver_persona_ids = fields.Many2many('ops.persona', string='Approvers')
   
   class OpsGovernancePriceAuthority(models.Model):
       _name = 'ops.governance.price.authority'
       _description = 'Role-Based Pricing Authority'
       
       rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade')
       persona_id = fields.Many2one('ops.persona', string='Persona/Role')
       user_group_id = fields.Many2one('res.groups', string='User Group')
       max_price_increase_percent = fields.Float(string='Max Price Increase %')
       max_price_decrease_percent = fields.Float(string='Max Price Decrease %')
       can_override_without_approval = fields.Boolean(string='Can Override w/o Approval')
       approver_persona_ids = fields.Many2many('ops.persona', string='Approvers')

3. Enhanced Validation Method:
   
   def validate_record(self, record):
       """Validate record against ALL governance rules."""
       self.ensure_one()
       errors = []
       warnings = []
       
       # A. Matrix dimension validation
       if self.enforce_branch_bu:
           if hasattr(record, 'ops_branch_id'):
               if not record.ops_branch_id:
                   errors.append(f"Branch is required by governance rule '{self.name}'")
               elif self.allowed_branch_ids and record.ops_branch_id not in self.allowed_branch_ids:
                   errors.append(
                       f"Branch '{record.ops_branch_id.name}' is not allowed. "
                       f"Allowed: {', '.join(self.allowed_branch_ids.mapped('name'))}"
                   )
           
           if hasattr(record, 'ops_business_unit_id'):
               if not record.ops_business_unit_id:
                   errors.append(f"Business Unit is required by governance rule '{self.name}'")
               elif self.allowed_business_unit_ids and record.ops_business_unit_id not in self.allowed_business_unit_ids:
                   errors.append(
                       f"Business Unit '{record.ops_business_unit_id.name}' is not allowed. "
                       f"Allowed: {', '.join(self.allowed_business_unit_ids.mapped('name'))}"
                   )
       
       # B. Discount limit validation (for sale.order.line)
       if self.enforce_discount_limit and record._name == 'sale.order.line':
           line_discount = record.discount
           user_max_discount = self._get_user_discount_limit(record.env.user)
           
           if line_discount > user_max_discount:
               errors.append(
                   f"Discount {line_discount}% exceeds your limit of {user_max_discount}%. "
                   f"Approval required from: {self._get_discount_approvers(user_max_discount)}"
               )
       
       # C. Margin protection validation (for sale.order and sale.order.line)
       if self.enforce_margin_protection:
           if record._name == 'sale.order.line':
               margin_percent = self._calculate_margin_percent(record)
               min_margin = self._get_category_min_margin(
                   record.product_id.categ_id,
                   record.order_id.ops_business_unit_id
               )
               
               if margin_percent < min_margin:
                   errors.append(
                       f"Product '{record.product_id.name}' margin {margin_percent:.2f}% "
                       f"is below minimum {min_margin:.2f}%. Approval required."
                   )
               elif margin_percent < (min_margin + 5):  # Warning threshold
                   warnings.append(
                       f"Product '{record.product_id.name}' margin {margin_percent:.2f}% "
                       f"is near minimum threshold."
                   )
       
       # D. Price override validation
       if self.enforce_price_override and record._name == 'sale.order.line':
           if record.price_unit != record.product_id.lst_price:
               variance_percent = abs(
                   (record.price_unit - record.product_id.lst_price) / record.product_id.lst_price * 100
               )
               user_authority = self._get_user_price_authority(record.env.user)
               
               if variance_percent > user_authority.get('max_variance', 0):
                   errors.append(
                       f"Price variance {variance_percent:.2f}% exceeds your authority. "
                       f"Approval required for manual pricing."
                   )
       
       return {'errors': errors, 'warnings': warnings}
   
   def action_validate(self, record):
       """Validate and raise errors if any."""
       result = self.validate_record(record)
       if result['errors']:
           raise ValidationError('\n'.join(result['errors']))
       if result['warnings']:
           # Log warnings or create activities
           for warning in result['warnings']:
               _logger.warning(f"[GOVERNANCE] {warning}")
       return True

4. Helper Methods for Calculations:
   
   def _calculate_margin_percent(self, order_line):
       """Calculate margin percentage for a sale order line."""
       if order_line.price_subtotal == 0:
           return 0.0
       
       # Get product cost
       cost = order_line.product_id.standard_price * order_line.product_uom_qty
       revenue = order_line.price_subtotal
       margin = revenue - cost
       margin_percent = (margin / revenue) * 100 if revenue else 0.0
       
       return margin_percent
   
   def _get_user_discount_limit(self, user):
       """Get maximum discount percentage for user based on role/persona."""
       max_discount = 0.0
       
       # Check persona-based limits
       persona = user.persona_id if hasattr(user, 'persona_id') else False
       if persona:
           limit_rule = self.discount_limit_by_role.filtered(
               lambda r: r.persona_id == persona
           )
           if limit_rule:
               max_discount = max(max_discount, limit_rule[0].max_discount_percent)
       
       # Check group-based limits
       for limit_rule in self.discount_limit_by_role.filtered(lambda r: r.user_group_id):
           if user.has_group(limit_rule.user_group_id.xml_id):
               max_discount = max(max_discount, limit_rule.max_discount_percent)
       
       # Fallback to rule default
       if max_discount == 0.0:
           max_discount = self.discount_limit_percent
       
       return max_discount
   
   def _get_category_min_margin(self, category, business_unit):
       """Get minimum margin for product category and business unit."""
       margin_rule = self.margin_by_category.filtered(
           lambda r: r.product_category_id == category and
                    (not r.business_unit_id or r.business_unit_id == business_unit)
       )
       
       if margin_rule:
           return margin_rule[0].minimum_margin_percent
       
       return self.minimum_margin_percent
   
   def _get_user_price_authority(self, user):
       """Get user's pricing authority."""
       authority = {'max_variance': 0.0, 'can_override': False}
       
       persona = user.persona_id if hasattr(user, 'persona_id') else False
       if persona:
           auth_rule = self.price_authority_by_role.filtered(
               lambda r: r.persona_id == persona
           )
           if auth_rule:
               authority['max_variance'] = max(
                   auth_rule.mapped('max_price_increase_percent') +
                   auth_rule.mapped('max_price_decrease_percent')
               )
               authority['can_override'] = any(auth_rule.mapped('can_override_without_approval'))
       
       return authority
   
   def _get_discount_approvers(self, exceeded_limit):
       """Get list of approvers for discount exceeding limit."""
       approvers = self.env['res.users']
       
       for limit_rule in self.discount_limit_by_role:
           if limit_rule.approval_required_above and exceeded_limit > limit_rule.approval_required_above:
               approvers |= limit_rule.approver_persona_ids.mapped('user_id')
       
       return ', '.join(approvers.mapped('name')) if approvers else 'Manager'

5. Auto-Trigger on Sale Order Line Changes:
   
   class SaleOrderLine(models.Model):
       _inherit = 'sale.order.line'
       
       @api.constrains('discount', 'price_unit')
       def _check_governance_rules(self):
           """Auto-check governance rules on discount/price changes."""
           for line in self:
               # Find applicable governance rules
               rules = self.env['ops.governance.rule'].search([
                   '|', '|',
                   ('enforce_discount_limit', '=', True),
                   ('enforce_margin_protection', '=', True),
                   ('enforce_price_override', '=', True),
                   ('model_id.model', '=', 'sale.order.line'),
               ])
               
               for rule in rules:
                   rule.action_validate(line)
       
       @api.onchange('discount')
       def _onchange_discount_check(self):
           """Real-time validation when discount changes."""
           if self.discount:
               rules = self.env['ops.governance.rule'].search([
                   ('enforce_discount_limit', '=', True),
                   ('model_id.model', '=', 'sale.order.line'),
               ])
               
               for rule in rules:
                   result = rule.validate_record(self)
                   if result['errors']:
                       return {'warning': {
                           'title': 'Discount Limit Exceeded',
                           'message': '\n'.join(result['errors'])
                       }}
                   if result['warnings']:
                       return {'warning': {
                           'title': 'Discount Warning',
                           'message': '\n'.join(result['warnings'])
                       }}
       
       @api.onchange('price_unit')
       def _onchange_price_check(self):
           """Real-time validation when price changes."""
           if self.price_unit and self.product_id:
               rules = self.env['ops.governance.rule'].search([
                   '|',
                   ('enforce_price_override', '=', True),
                   ('enforce_margin_protection', '=', True),
                   ('model_id.model', '=', 'sale.order.line'),
               ])
               
               for rule in rules:
                   result = rule.validate_record(self)
                   if result['errors']:
                       return {'warning': {
                           'title': 'Price Override Violation',
                           'message': '\n'.join(result['errors'])
                       }}

6. Add Approval Rules by Matrix:
   
   class OpsApprovalRequest(models.Model):
       _inherit = 'ops.approval.request'
       
       # Add matrix and pricing fields
       ops_branch_id = fields.Many2one('ops.branch', related='record_ref.ops_branch_id', store=True)
       ops_business_unit_id = fields.Many2one('ops.business.unit', related='record_ref.ops_business_unit_id', store=True)
       discount_percent = fields.Float(string='Discount %')
       margin_percent = fields.Float(string='Margin %')
       price_variance_percent = fields.Float(string='Price Variance %')
       
       def _find_approvers(self):
           """Find approvers based on matrix dimensions and violation type."""
           self.ensure_one()
           
           approvers = self.env['res.users']
           
           # Get personas that can approve for this branch/BU
           Persona = self.env['ops.persona']
           domain = [('active', '=', True)]
           
           if self.ops_branch_id:
               domain.append(('branch_ids', 'in', self.ops_branch_id.id))
           
           if self.ops_business_unit_id:
               domain.append(('business_unit_ids', 'in', self.ops_business_unit_id.id))
           
           # Add specific approvers based on violation type
           if self.discount_percent:
               domain.append(('can_approve_discounts', '=', True))
           
           personas = Persona.search(domain)
           approvers |= personas.mapped('user_id')
           
           return approvers

7. Create Dashboard/Report for Governance Violations:
   
   class OpsGovernanceViolationReport(models.TransientModel):
       _name = 'ops.governance.violation.report'
       _description = 'Governance Violations Dashboard'
       
       date_from = fields.Date(required=True)
       date_to = fields.Date(required=True)
       branch_id = fields.Many2one('ops.branch')
       business_unit_id = fields.Many2one('ops.business.unit')
       violation_type = fields.Selection([
           ('discount', 'Discount Violations'),
           ('margin', 'Margin Violations'),
           ('price', 'Price Override Violations'),
       ])
       
       def get_violations(self):
           """Generate report of governance violations."""
           domain = [
               ('create_date', '>=', self.date_from),
               ('create_date', '<=', self.date_to),
           ]
           
           if self.branch_id:
               domain.append(('ops_branch_id', '=', self.branch_id.id))
           
           if self.business_unit_id:
               domain.append(('ops_business_unit_id', '=', self.business_unit_id.id))
           
           # Query approval requests for violations
           approvals = self.env['ops.approval.request'].search(domain)
           
           violations = []
           for approval in approvals:
               if self.violation_type == 'discount' and approval.discount_percent:
                   violations.append({
                       'date': approval.create_date,
                       'user': approval.create_uid.name,
                       'branch': approval.ops_branch_id.name,
                       'bu': approval.ops_business_unit_id.name,
                       'discount': approval.discount_percent,
                       'status': approval.state,
                   })
           
           return violations

This comprehensive governance system ensures:
- Matrix-based access control
- Role-based discount limits with automatic approval routing
- Margin protection with category/BU-specific thresholds
- Price override control with variance monitoring
- Real-time validation and warnings
- Audit trail of all violations and approvals
```

---

### **PHASE 8: DATA MIGRATION & TEMPLATES**

#### **Prompt 8.1: Create Default Company/Branch/BU Templates** ☐

**File**: `ops_matrix_core/data/ops_default_data.xml`

```
Create: ops_matrix_core/data/ops_default_data.xml

Provide demo/template data for testing the matrix structure:

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- Demo Companies (Legal Entities) -->
        <record id="company_qatar" model="res.company">
            <field name="name">ABC Qatar</field>
            <field name="ops_code">QAT-001</field>
            <field name="currency_id" ref="base.QAR"/>
            <field name="country_id" ref="base.qa"/>
        </record>
        
        <record id="company_uae" model="res.company">
            <field name="name">ABC UAE</field>
            <field name="ops_code">UAE-001</field>
            <field name="currency_id" ref="base.AED"/>
            <field name="country_id" ref="base.ae"/>
        </record>
        
        <!-- Demo Branches (Operational Offices) -->
        <record id="branch_doha" model="ops.branch">
            <field name="name">Doha Office</field>
            <field name="code">BR-DOHA</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="address">Al Corniche Street, Doha, Qatar</field>
            <field name="active">True</field>
        </record>
        
        <record id="branch_alkhor" model="ops.branch">
            <field name="name">Al Khor Branch</field>
            <field name="code">BR-ALKHOR</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="address">Al Khor Industrial Area, Qatar</field>
            <field name="active">True</field>
        </record>
        
        <record id="branch_dukhan" model="ops.branch">
            <field name="name">Dukhan Branch</field>
            <field name="code">BR-DUKHAN</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="address">Dukhan City, Qatar</field>
            <field name="active">True</field>
        </record>
        
        <record id="branch_dubai" model="ops.branch">
            <field name="name">Dubai Office</field>
            <field name="code">BR-DUBAI</field>
            <field name="company_id" ref="company_uae"/>
            <field name="address">Dubai Marina, Dubai, UAE</field>
            <field name="active">True</field>
        </record>
        
        <record id="branch_abudhabi" model="ops.branch">
            <field name="name">Abu Dhabi Branch</field>
            <field name="code">BR-ABUDHABI</field>
            <field name="company_id" ref="company_uae"/>
            <field name="address">Corniche Road, Abu Dhabi, UAE</field>
            <field name="active">True</field>
        </record>
        
        <!-- Demo Business Units (Profit Centers) -->
        <record id="bu_retail" model="ops.business.unit">
            <field name="name">Retail Sales</field>
            <field name="code">BU-RETAIL</field>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_doha'), ref('branch_alkhor'), ref('branch_dubai')])]"/>
            <field name="primary_branch_id" ref="branch_doha"/>
            <field name="active">True</field>
        </record>
        
        <record id="bu_coffee" model="ops.business.unit">
            <field name="name">Coffee Division</field>
            <field name="code">BU-COFFEE</field>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_doha'), ref('branch_dukhan')])]"/>
            <field name="primary_branch_id" ref="branch_doha"/>
            <field name="active">True</field>
        </record>
        
        <record id="bu_services" model="ops.business.unit">
            <field name="name">Professional Services</field>
            <field name="code">BU-SERVICES</field>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_dubai'), ref('branch_abudhabi')])]"/>
            <field name="primary_branch_id" ref="branch_dubai"/>
            <field name="active">True</field>
        </record>
        
        <record id="bu_wholesale" model="ops.business.unit">
            <field name="name">Wholesale Distribution</field>
            <field name="code">BU-WHOLESALE</field>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_alkhor'), ref('branch_dukhan')])]"/>
            <field name="primary_branch_id" ref="branch_alkhor"/>
            <field name="active">True</field>
        </record>
        
        <!-- Demo Users with Matrix Access -->
        <record id="user_ceo_qatar" model="res.users">
            <field name="name">Ahmed Al-Khalifa (CEO Qatar)</field>
            <field name="login">ceo.qatar@abc.com</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="company_ids" eval="[(6, 0, [ref('company_qatar')])]"/>
            <field name="allowed_branch_ids" eval="[(6, 0, [ref('branch_doha'), ref('branch_alkhor'), ref('branch_dukhan')])]"/>
            <field name="default_branch_id" ref="branch_doha"/>
            <field name="groups_id" eval="[(6, 0, [ref('base.group_system')])]"/>
        </record>
        
        <record id="user_retail_leader" model="res.users">
            <field name="name">Fatima Hassan (Retail Leader)</field>
            <field name="login">retail.leader@abc.com</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="company_ids" eval="[(6, 0, [ref('company_qatar'), ref('company_uae')])]"/>
            <field name="allowed_branch_ids" eval="[(6, 0, [ref('branch_doha'), ref('branch_alkhor'), ref('branch_dubai')])]"/>
            <field name="allowed_business_unit_ids" eval="[(6, 0, [ref('bu_retail')])]"/>
            <field name="default_branch_id" ref="branch_doha"/>
            <field name="default_business_unit_id" ref="bu_retail"/>
            <field name="is_cross_branch_bu_leader" eval="True"/>
            <field name="groups_id" eval="[(6, 0, [ref('sales_team.group_sale_manager')])]"/>
        </record>
        
        <record id="user_doha_manager" model="res.users">
            <field name="name">Mohammed Al-Mansoori (Doha Manager)</field>
            <field name="login">doha.manager@abc.com</field>
            <field name="company_id" ref="company_qatar"/>
            <field name="company_ids" eval="[(6, 0, [ref('company_qatar')])]"/>
            <field name="allowed_branch_ids" eval="[(6, 0, [ref('branch_doha')])]"/>
            <field name="allowed_business_unit_ids" eval="[(6, 0, [ref('bu_retail'), ref('bu_coffee')])]"/>
            <field name="default_branch_id" ref="branch_doha"/>
            <field name="groups_id" eval="[(6, 0, [ref('sales_team.group_sale_manager'), ref('stock.group_stock_manager')])]"/>
        </record>
        
        <!-- Demo Personas -->
        <record id="persona_retail_leader" model="ops.persona">
            <field name="name">Retail Division Leader</field>
            <field name="code">PERSONA-RETAIL</field>
            <field name="user_id" ref="user_retail_leader"/>
            <field name="company_id" ref="company_qatar"/>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_doha'), ref('branch_alkhor'), ref('branch_dubai')])]"/>
            <field name="business_unit_ids" eval="[(6, 0, [ref('bu_retail')])]"/>
            <field name="default_branch_id" ref="branch_doha"/>
            <field name="default_business_unit_id" ref="bu_retail"/>
            <field name="is_bu_leader" eval="True"/>
            <field name="is_cross_branch" eval="True"/>
        </record>
        
        <record id="persona_doha_manager" model="ops.persona">
            <field name="name">Doha Branch Manager</field>
            <field name="code">PERSONA-DOHA-MGR</field>
            <field name="user_id" ref="user_doha_manager"/>
            <field name="company_id" ref="company_qatar"/>
            <field name="branch_ids" eval="[(6, 0, [ref('branch_doha')])]"/>
            <field name="business_unit_ids" eval="[(6, 0, [ref('bu_retail'), ref('bu_coffee')])]"/>
            <field name="default_branch_id" ref="branch_doha"/>
            <field name="is_branch_manager" eval="True"/>
        </record>
        
    </data>
</odoo>

Add this file to __manifest__.py under 'data' section.

This provides ready-to-test hierarchical structure matching real-world use case.
```

---

### **PHASE 9: TESTING & VALIDATION**

#### **Prompt 9.1: Create Comprehensive Test Suite** ☐

**File**: `ops_matrix_core/tests/test_matrix_framework.py`

```
Create: ops_matrix_core/tests/test_matrix_framework.py

Build comprehensive test suite for matrix framework:

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError

class TestMatrixFramework(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test company
        self.company_test = self.env['res.company'].create({
            'name': 'Test Company',
            'ops_code': 'TST-001',
        })
        
        # Create test branches
        self.branch_a = self.env['ops.branch'].create({
            'name': 'Branch A',
            'code': 'BR-A',
            'company_id': self.company_test.id,
        })
        
        self.branch_b = self.env['ops.branch'].create({
            'name': 'Branch B',
            'code': 'BR-B',
            'company_id': self.company_test.id,
        })
        
        # Create test business units
        self.bu_sales = self.env['ops.business.unit'].create({
            'name': 'Sales BU',
            'code': 'BU-SALES',
            'branch_ids': [(6, 0, [self.branch_a.id, self.branch_b.id])],
            'primary_branch_id': self.branch_a.id,
        })
        
        self.bu_ops = self.env['ops.business.unit'].create({
            'name': 'Operations BU',
            'code': 'BU-OPS',
            'branch_ids': [(6, 0, [self.branch_a.id])],
            'primary_branch_id': self.branch_a.id,
        })
    
    def test_01_branch_creation(self):
        """Test branch creation and analytic account auto-creation."""
        self.assertTrue(self.branch_a.analytic_account_id, 
                       "Analytic account should be auto-created for branch")
        self.assertEqual(self.branch_a.analytic_account_id.code, 'BR-A',
                        "Analytic account code should match branch code")
        self.assertEqual(self.branch_a.analytic_account_id.company_id, self.company_test,
                        "Analytic account should belong to branch's company")
    
    def test_02_bu_creation(self):
        """Test business unit creation and multi-branch assignment."""
        self.assertTrue(self.bu_sales.analytic_account_id,
                       "Analytic account should be auto-created for BU")
        self.assertEqual(len(self.bu_sales.branch_ids), 2,
                        "BU should be assigned to 2 branches")
        self.assertIn(self.branch_a, self.bu_sales.branch_ids,
                     "Branch A should be in BU's branches")
    
    def test_03_sale_order_propagation(self):
        """Test dimension propagation from sale order to invoice."""
        partner = self.env['res.partner'].create({'name': 'Test Customer'})
        product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })
        
        # Create sale order with matrix dimensions
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'company_id': self.company_test.id,
            'ops_branch_id': self.branch_a.id,
            'ops_business_unit_id': self.bu_sales.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })
        
        # Check line propagation
        self.assertEqual(sale_order.order_line[0].ops_branch_id, self.branch_a,
                        "Branch should propagate to order lines")
        self.assertEqual(sale_order.order_line[0].ops_business_unit_id, self.bu_sales,
                        "BU should propagate to order lines")
        
        # Confirm and create invoice
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        
        # Check invoice propagation
        self.assertEqual(invoice.ops_branch_id, self.branch_a,
                        "Branch should propagate to invoice")
        self.assertEqual(invoice.ops_business_unit_id, self.bu_sales,
                        "BU should propagate to invoice")
        
        # Check analytic distribution
        self.assertTrue(invoice.invoice_line_ids[0].analytic_distribution,
                       "Analytic distribution should be set on invoice lines")
    
    def test_04_user_access_control(self):
        """Test user access restrictions based on matrix."""
        # Create test user with limited access
        user_limited = self.env['res.users'].create({
            'name': 'Limited User',
            'login': 'limited@test.com',
            'company_id': self.company_test.id,
            'company_ids': [(6, 0, [self.company_test.id])],
            'allowed_branch_ids': [(6, 0, [self.branch_a.id])],
            'allowed_business_unit_ids': [(6, 0, [self.bu_sales.id])],
        })
        
        # Test branch access
        self.assertTrue(user_limited.can_access_branch(self.branch_a.id),
                       "User should access Branch A")
        self.assertFalse(user_limited.can_access_branch(self.branch_b.id),
                        "User should not access Branch B")
        
        # Test BU access
        self.assertTrue(user_limited.can_access_business_unit(self.bu_sales.id),
                       "User should access Sales BU")
        self.assertFalse(user_limited.can_access_business_unit(self.bu_ops.id),
                        "User should not access Operations BU")
    
    def test_05_analytic_account_deletion_protection(self):
        """Test that active branch/BU analytic accounts cannot be deleted."""
        with self.assertRaises(UserError,
                              msg="Should prevent deletion of branch analytic account"):
            self.branch_a.analytic_account_id.unlink()
        
        # Deactivate branch and try again
        self.branch_a.active = False
        # Should now be able to delete (or still protected - depends on business logic)
    
    def test_06_cross_branch_bu_reporting(self):
        """Test reporting for BU across multiple branches."""
        # Create journal entries for same BU in different branches
        # (Simplified - in reality would create through transactions)
        
        # Check that BU report aggregates across branches
        bu_report = self.env['ops.business.unit.report'].create({
            'business_unit_id': self.bu_sales.id,
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
        })
        
        result = bu_report.get_bu_pnl()
        self.assertIn('branch_performance', result,
                     "Report should include branch-level breakdown")
    
    def test_07_persona_access_sync(self):
        """Test persona access syncs to user."""
        user = self.env['res.users'].create({
            'name': 'Persona Test User',
            'login': 'persona@test.com',
            'company_id': self.company_test.id,
        })
        
        persona = self.env['ops.persona'].create({
            'name': 'Test Persona',
            'code': 'PERS-TEST',
            'user_id': user.id,
            'company_id': self.company_test.id,
            'branch_ids': [(6, 0, [self.branch_a.id, self.branch_b.id])],
            'business_unit_ids': [(6, 0, [self.bu_sales.id])],
            'default_branch_id': self.branch_a.id,
        })
        
        # Check sync
        self.assertEqual(len(user.allowed_branch_ids), 2,
                        "User should have 2 allowed branches from persona")
        self.assertEqual(user.default_branch_id, self.branch_a,
                        "User default branch should match persona")
    
    def test_08_validation_constraints(self):
        """Test data validation constraints."""
        # Test BU must have at least one branch
        with self.assertRaises(ValidationError,
                              msg="BU must have at least one branch"):
            self.env['ops.business.unit'].create({
                'name': 'Invalid BU',
                'code': 'BU-INVALID',
                'branch_ids': [(6, 0, [])],  # Empty branches
            })
        
        # Test default branch must be in allowed branches
        user = self.env['res.users'].create({
            'name': 'Validation Test',
            'login': 'validation@test.com',
            'company_id': self.company_test.id,
            'allowed_branch_ids': [(6, 0, [self.branch_a.id])],
        })
        
        with self.assertRaises(ValidationError,
                              msg="Default branch must be in allowed branches"):
            user.default_branch_id = self.branch_b.id
    
    def test_09_hierarchy_integrity(self):
        """Test company → branch → BU hierarchy integrity."""
        # Branch must belong to company
        self.assertEqual(self.branch_a.company_id, self.company_test,
                        "Branch company should be set")
        
        # BU branches must exist and be active
        for branch in self.bu_sales.branch_ids:
            self.assertTrue(branch.exists(), "BU branch must exist")
        
        # Company should show branch count
        branch_count = len(self.company_test.branch_ids)
        self.assertEqual(branch_count, 2,
                        "Company should have 2 branches")

Run with: python3 odoo-bin -c config/odoo.conf -d test_db -i ops_matrix_core --test-enable --stop-after-init
```

---

## 🎯 EXECUTION CHECKLIST

### Pre-Implementation
- [ ] Backup current database (if exists)
- [ ] Review all 9 phases and understand dependencies
- [ ] Ensure Odoo 19 CE is installed and working

### Implementation Order
1. **Phase 1**: Foundation (1.1 → 1.2 → 1.3 → 1.4 → 1.5)
   - ⚠️ **CRITICAL**: ops_branch must be created before ops_business_unit
2. **Phase 2**: Data Flow (2.1 → 2.2 → 2.5)
3. **Phase 3**: Analytic (3.1 → 3.2)
4. **Phase 4**: Security (4.1 → 4.2)
5. **Phase 5**: Reporting (5.1 → 5.2)
6. **Phase 6**: Dashboards (6.1)
7. **Phase 7**: Governance (7.1 → 7.2)
8. **Phase 8**: Data (8.1)
9. **Phase 9**: Testing (9.1)

### Post-Implementation
- [ ] Run test suite (Phase 9.1)
- [ ] Load demo data (Phase 8.1)
- [ ] Verify dashboards display correctly
- [ ] Test user access with different roles
- [ ] Create sample transactions and verify propagation
- [ ] Generate sample reports at each level

---

## 📝 NOTES & WARNINGS

### ⚠️ Breaking Changes from Previous Implementation
1. **ops_branch is restored** as separate model (was merged into res.company)
2. **All field references** ops_company_id → ops_branch_id (except computed company field)
3. **Security rules** now multi-level (Company → Branch → BU)
4. **Analytic structure** changed to dual-dimension (Branch + BU, not just Branch)

### 🔧 Technical Considerations
- **Odoo 19 API**: Use `_read_group()` not `read_group()`
- **Hook Signature**: Use `post_init_hook(env)` not `post_init_hook(cr, registry)`
- **Analytic Distribution**: JSON field format `{'account_id': percentage}`
- **Performance**: Always use database-level aggregation for reports (>10K records)

### 🎯 Success Criteria
- ✅ Company can have multiple branches
- ✅ BU can operate in multiple branches
- ✅ Cross-branch BU leader sees their BU across all branches
- ✅ All transactions carry branch + BU dimensions
- ✅ Reports consolidate at Company, Branch, and BU levels
- ✅ Security rules enforce siloed access
- ✅ Analytic accounts auto-created and protected

---

## 🚀 READY TO START

**Current Status**: Prompts complete, ready for Phase 1 implementation.

**First Action**: Execute Prompt 1.1 (Create Branch Model)

**Estimated Total Time**: 8-10 development days

Good luck! 🎉
