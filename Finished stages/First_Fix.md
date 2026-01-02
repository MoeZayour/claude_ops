Role: Odoo 19 Senior Developer - OPS Matrix Core EnhancementContext: User testing revealed 7 critical issues and enhancement requirements for the OPS Matrix Core module. We need to fix bugs, improve UX for non-technical users, and add pre-configured data templates.CRITICAL FIXES AND ENHANCEMENTS - EXECUTE IN ORDER:

ISSUE 1: Admin Cannot Create Branch/BU - Access Rights ErrorProblem: Admin gets "doesn't have 'create' access" error when creating branches.Root Cause: Record rules are too restrictive for system administrators.Fix:

Open: addons/ops_matrix_core/security/ops_security.xml


Find the record rule ops_branch_visibility_rule and modify it to EXCLUDE system admins:

<record id="ops_branch_visibility_rule" model="ir.rule">
    <field name="name">Branch Visibility: Allowed Only</field>
    <field name="model_id" ref="model_ops_branch"/>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="domain_force">[
        '|',
            ('id', 'in', user.allowed_branch_ids.ids),
            ('id', '=', user.primary_branch_id.id)
    ]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>

<!-- NEW: System Admin Bypass Rule -->
<record id="ops_branch_admin_full_access" model="ir.rule">
    <field name="name">Branch: Admin Full Access</field>
    <field name="model_id" ref="model_ops_branch"/>
    <field name="groups" eval="[(4, ref('base.group_system'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
Do the same for Business Units (ops_business_unit_visibility_rule):

<record id="ops_business_unit_admin_full_access" model="ir.rule">
    <field name="name">Business Unit: Admin Full Access</field>
    <field name="model_id" ref="model_ops_business_unit"/>
    <field name="groups" eval="[(4, ref('base.group_system'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>



ISSUE 2: Auto-Generate Codes for All EntitiesProblem: Users can manually enter codes and mess things up.Solution: Make all code fields readonly and auto-generate using sequences.



Step 2A: Create Sequences Data FileCreate new file: addons/ops_matrix_core/data/ir_sequence_data.xml


<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Business Unit Code Sequence -->
        <record id="seq_ops_business_unit_code" model="ir.sequence">
            <field name="name">Business Unit Code</field>
            <field name="code">ops.business.unit.code</field>
            <field name="prefix">BU</field>
            <field name="padding">4</field>
            <field name="number_increment">1</field>
            <field name="number_next">1</field>
        </record>
        <!-- Branch Code Sequence -->
        <record id="seq_ops_branch_code" model="ir.sequence">
            <field name="name">Branch Code</field>
            <field name="code">ops.branch.code</field>
            <field name="prefix">BR</field>
            <field name="padding">4</field>
            <field name="number_increment">1</field>
            <field name="number_next">1</field>
        </record>

        <!-- Persona Code Sequence -->
        <record id="seq_ops_persona_code" model="ir.sequence">
            <field name="name">Persona Code</field>
            <field name="code">ops.persona.code</field>
            <field name="prefix">PRS</field>
            <field name="padding">4</field>
            <field name="number_increment">1</field>
            <field name="number_next">1</field>
        </record>

        <!-- Governance Rule Code Sequence -->
        <record id="seq_ops_governance_rule_code" model="ir.sequence">
            <field name="name">Governance Rule Code</field>
            <field name="code">ops.governance.rule.code</field>
            <field name="prefix">GR</field>
            <field name="padding">4</field>
            <field name="number_increment">1</field>
            <field name="number_next">1</field>
        </record>

    </data>
</odoo>



Step 2B: Update Models to Auto-Generate CodesFor ops_business_unit.py:
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('ops.business.unit.code') or 'BU0001'
    return super(OpsBusinessUnit, self).create(vals)For ops_branch.py:
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('ops.branch.code') or 'BR0001'
    return super(OpsBranch, self).create(vals)For ops_persona.py:
@api.model
def create(self, vals):
    if not vals.get('code'):
        vals['code'] = self.env['ir.sequence'].next_by_code('ops.persona.code') or 'PRS0001'
    return super(OpsPersona, self).create(vals)For ops_governance_rule.py:Add a code field first:
code = fields.Char(string='Code', required=True, readonly=True, copy=False, default='New')

@api.model
def create(self, vals):
    if vals.get('code', 'New') == 'New':
        vals['code'] = self.env['ir.sequence'].next_by_code('ops.governance.rule.code') or 'GR0001'
    return super(OpsGovernanceRule, self).create(vals)
    


Step 2C: Update Views to Make Code ReadonlyIn all form views (business_unit, branch, persona, governance_rule), change:<field name="code"/>To:<field name="code" readonly="1"/>

Step 2D: Update ManifestAdd to __manifest__.py data section:
'data': [
    'security/ops_security.xml',
    'security/ir.model.access.csv',
    'data/ir_sequence_data.xml',  # ADD THIS LINE
    'views/ops_business_unit_views.xml',
    # ... rest of views
],

ISSUE 3: Approval Workflow for Governance RulesProblem: Rules should trigger approval workflows, not just block/warn.Solution: Add new action types and approval mechanism.

Step 3A: Update ops_governance_rule.pyAdd new fields and action types:
action_type = fields.Selection([
    ('warning', 'Warning'),
    ('block', 'Block'),
    ('require_approval', 'Require Approval'),  # NEW
], string='Action Type', required=True, default='warning')

approval_user_ids = fields.Many2many(
    'res.users',
    string='Approval Users',
    help='Users who can approve when this rule is triggered'
)

approval_persona_ids = fields.Many2many(
    'ops.persona',
    string='Approval Personas',
    help='Personas who can approve when this rule is triggered'
)

lock_on_approval_request = fields.Boolean(
    string='Lock During Approval',
    default=True,
    help='Lock record while approval is pending'
)

Step 3B: Create Approval Request ModelCreate new file: addons/ops_matrix_core/models/ops_approval_request.py




from odoo import models, fields, api
from odoo.exceptions import UserError

class OpsApprovalRequest(models.Model):
    _name = 'ops.approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True, readonly=True, default='New')
    rule_id = fields.Many2one('ops.governance.rule', string='Governance Rule', required=True, readonly=True)
    model_name = fields.Char(string='Model', required=True, readonly=True)
    res_id = fields.Integer(string='Record ID', required=True, readonly=True)
    res_name = fields.Char(string='Record Name', compute='_compute_res_name', store=True)
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', required=True, tracking=True)
    
    requested_by = fields.Many2one('res.users', string='Requested By', required=True, readonly=True, default=lambda self: self.env.user)
    requested_date = fields.Datetime(string='Request Date', required=True, readonly=True, default=fields.Datetime.now)
    
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, tracking=True)
    approved_date = fields.Datetime(string='Approval Date', readonly=True)
    
    approver_ids = fields.Many2many('res.users', string='Allowed Approvers', compute='_compute_approver_ids')
    
    notes = fields.Text(string='Request Notes')
    response_notes = fields.Text(string='Response Notes')
    
    @api.depends('model_name', 'res_id')
    def _compute_res_name(self):
        for record in self:
            if record.model_name and record.res_id:
                target_record = self.env[record.model_name].browse(record.res_id)
                record.res_name = target_record.display_name if target_record.exists() else 'Deleted Record'
            else:
                record.res_name = ''
    
    @api.depends('rule_id')
    def _compute_approver_ids(self):
        for record in self:
            approvers = record.rule_id.approval_user_ids
            # Add users with matching personas
            if record.rule_id.approval_persona_ids:
                persona_users = self.env['res.users'].search([
                    ('persona_id', 'in', record.rule_id.approval_persona_ids.ids)
                ])
                approvers |= persona_users
            record.approver_ids = approvers
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('ops.approval.request') or 'APR0001'
        return super(OpsApprovalRequest, self).create(vals)
    
    def action_approve(self):
        self.ensure_one()
        if self.env.user not in self.approver_ids:
            raise UserError('You are not authorized to approve this request.')
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        
        # Unlock the record
        target_record = self.env[self.model_name].browse(self.res_id)
        if target_record.exists() and hasattr(target_record, 'approval_locked'):
            target_record.write({'approval_locked': False})
        
        # Post message
        self.message_post(body=f'Approved by {self.env.user.name}')
        
        return True
    
    def action_reject(self):
        self.ensure_one()
        if self.env.user not in self.approver_ids:
            raise UserError('You are not authorized to reject this request.')
        
        self.write({
            'state': 'rejected',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        
        # Unlock the record
        target_record = self.env[self.model_name].browse(self.res_id)
        if target_record.exists() and hasattr(target_record, 'approval_locked'):
            target_record.write({'approval_locked': False})
        
        # Post message
        self.message_post(body=f'Rejected by {self.env.user.name}')
        
        return True
    
    def action_cancel(self):
        self.ensure_one()
        if self.env.user != self.requested_by and not self.env.user.has_group('base.group_system'):
            raise UserError('Only the requester or admin can cancel this request.')
        
        self.write({'state': 'cancelled'})
        
        # Unlock the record
        target_record = self.env[self.model_name].browse(self.res_id)
        if target_record.exists() and hasattr(target_record, 'approval_locked'):
            target_record.write({'approval_locked': False})
        
        return True

Step 3C: Add Approval SequenceAdd to data/ir_sequence_data.xml:

<!-- Approval Request Sequence -->
<record id="seq_ops_approval_request" model="ir.sequence">
    <field name="name">Approval Request</field>
    <field name="code">ops.approval.request</field>
    <field name="prefix">APR</field>
    <field name="padding">5</field>
    <field name="number_increment">1</field>
    <field name="number_next">1</field>
</record>

Step 3D: Update Governance MixinIn models/ops_governance_mixin.py, update the _apply_governance_rule method:
def _apply_governance_rule(self, rule, trigger_type):
    """Apply a governance rule and handle different action types."""
    context = self._get_governance_context()
    
    # Evaluate condition
    try:
        if rule.condition_code:
            exec(rule.condition_code, context)
            result = context.get('result', False)
        else:
            result = True
    except Exception as e:
        raise UserError(f"Error evaluating rule condition: {str(e)}")
    
    if result:
        # Rule triggered - take action based on action_type
        if rule.action_type == 'block':
            raise UserError(rule.error_message or f"Operation blocked by rule: {rule.name}")
        
        elif rule.action_type == 'warning':
            return {
                'warning': {
                    'title': 'Governance Rule Warning',
                    'message': rule.error_message or f"Warning from rule: {rule.name}",
                }
            }
        
        elif rule.action_type == 'require_approval':
            # Check if already has pending approval
            existing_approval = self.env['ops.approval.request'].search([
                ('model_name', '=', self._name),
                ('res_id', '=', self.id),
                ('rule_id', '=', rule.id),
                ('state', '=', 'pending'),
            ], limit=1)
            
            if not existing_approval:
                # Create approval request
                approval = self.env['ops.approval.request'].create({
                    'rule_id': rule.id,
                    'model_name': self._name,
                    'res_id': self.id,
                    'notes': rule.error_message or f"Approval required by rule: {rule.name}",
                })
                
                # Lock record if configured
                if rule.lock_on_approval_request and hasattr(self, 'approval_locked'):
                    self.write({'approval_locked': True})
                
                # Notify approvers
                approval.message_subscribe(partner_ids=approval.approver_ids.mapped('partner_id').ids)
                approval.message_post(
                    body=f"Approval requested by {self.env.user.name} for {self.display_name}",
                    subject="New Approval Request"
                )
            
            return {
                'warning': {
                    'title': 'Approval Required',
                    'message': f"This action requires approval. Request has been submitted to authorized approvers.",
                }
            }
    
    return {}

Step 3E: Add Approval Fields to MixinIn models/ops_governance_mixin.py, add these fields to the mixin:
approval_locked = fields.Boolean(
    string='Approval Locked',
    default=False,
    help='Record is locked pending approval',
    copy=False
)

approval_request_ids = fields.One2many(
    'ops.approval.request',
    compute='_compute_approval_requests',
    string='Approval Requests'
)

approval_request_count = fields.Integer(
    compute='_compute_approval_requests',
    string='Approval Requests'
)

@api.depends('id')
def _compute_approval_requests(self):
    for record in self:
        if record.id:
            approvals = self.env['ops.approval.request'].search([
                ('model_name', '=', record._name),
                ('res_id', '=', record.id),
            ])
            record.approval_request_ids = approvals
            record.approval_request_count = len(approvals)
        else:
            record.approval_request_ids = False
            record.approval_request_count = 0

def action_view_approvals(self):
    """Open approval requests for this record."""
    self.ensure_one()
    return {
        'name': 'Approval Requests',
        'type': 'ir.actions.act_window',
        'res_model': 'ops.approval.request',
        'view_mode': 'tree,form',
        'domain': [('model_name', '=', self._name), ('res_id', '=', self.id)],
        'context': {'default_model_name': self._name, 'default_res_id': self.id},
    }

def action_request_approval(self):
    """Manually request approval."""
    self.ensure_one()
    # Find applicable rules that require approval
    rules = self.env['ops.governance.rule'].search([
        ('model_id.model', '=', self._name),
        ('action_type', '=', 'require_approval'),
        ('active', '=', True),
    ])
    
    if not rules:
        raise UserError('No approval rules configured for this model.')
    
    # Apply first matching rule
    for rule in rules:
        self._apply_governance_rule(rule, 'manual')
        break
    
    return True

Step 3F: Override write() to Prevent Changes When LockedIn models/ops_governance_mixin.py, add this to the write method:
def write(self, vals):
    # Check if record is approval locked
    for record in self:
        if hasattr(record, 'approval_locked') and record.approval_locked:
            # Check if user is trying to change fields other than approval_locked
            if set(vals.keys()) - {'approval_locked'}:
                # Cancel pending approvals if data changed
                pending_approvals = self.env['ops.approval.request'].search([
                    ('model_name', '=', record._name),
                    ('res_id', '=', record.id),
                    ('state', '=', 'pending'),
                ])
                pending_approvals.write({'state': 'cancelled'})
                
                # Unlock and allow change
                vals['approval_locked'] = False
    
    result = super(OpsGovernanceMixin, self).write(vals)
    
    # Apply governance rules on write
    # ... existing code ...
    
    return result

Step 3G: Create Approval Request ViewsCreate new file: addons/ops_matrix_core/views/ops_approval_request_views.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Approval Request Tree View -->
    <record id="view_ops_approval_request_tree" model="ir.ui.view">
        <field name="name">ops.approval.request.tree</field>
        <field name="model">ops.approval.request</field>
        <field name="arch" type="xml">
            <tree string="Approval Requests" decoration-info="state=='pending'" decoration-success="state=='approved'" decoration-danger="state=='rejected'">
                <field name="name"/>
                <field name="rule_id"/>
                <field name="res_name"/>
                <field name="requested_by"/>
                <field name="requested_date"/>
                <field name="state" widget="badge" decoration-info="state=='pending'" decoration-success="state=='approved'" decoration-danger="state=='rejected'"/>
            </tree>
        </field>
    </record>

    <!-- Approval Request Form View -->
    <record id="view_ops_approval_request_form" model="ir.ui.view">
        <field name="name">ops.approval.request.form</field>
        <field name="model">ops.approval.request</field>
        <field name="arch" type="xml">
            <form string="Approval Request">
                <header>
                    <button name="action_approve" string="Approve" type="object" class="oe_highlight" attrs="{'invisible': [('state', '!=', 'pending')]}"/>
                    <button name="action_reject" string="Reject" type="object" attrs="{'invisible': [('state', '!=', 'pending')]}"/>
                    <button name="action_cancel" string="Cancel" type="object" attrs="{'invisible': [('state', '!=', 'pending')]}"/>
                    <field name="state" widget="statusbar" statusbar_visible="pending,approved,rejected"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" readonly="1"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="rule_id" readonly="1"/>
                            <field name="res_name" readonly="1"/>
                            <field name="requested_by" readonly="1"/>
                            <field name="requested_date" readonly="1"/>
                        </group>
                        <group>
                            <field name="approved_by" readonly="1" attrs="{'invisible': [('approved_by', '=', False)]}"/>
                            <field name="approved_date" readonly="1" attrs="{'invisible': [('approved_date', '=', False)]}"/>
                            <field name="approver_ids" widget="many2many_tags" readonly="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Request Details">
                            <group>
                                <field name="notes" readonly="1"/>
                                <field name="response_notes" attrs="{'readonly': [('state', '!=', 'pending')]}"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Approval Request Action -->
    <record id="action_ops_approval_request" model="ir.actions.act_window">
        <field name="name">Approval Requests</field>
        <field name="res_model">ops.approval.request</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                No approval requests yet
            </p>
        </field>
    </record>

    <!-- Menu Item -->
    <menuitem id="menu_ops_approval_request"
              name="Approval Requests"
              parent="menu_ops_governance_root"
              action="action_ops_approval_request"
              sequence="40"/>

</odoo>

Step 3H: Update Governance Rule Form ViewIn views/ops_governance_rule_views.xml, add approval fields:
<page string="Approval Settings" attrs="{'invisible': [('action_type', '!=', 'require_approval')]}">
    <group>
        <field name="approval_user_ids" widget="many2many_tags"/>
        <field name="approval_persona_ids" widget="many2many_tags"/>
        <field name="lock_on_approval_request"/>
    </group>
</page>

Step 3I: Add Smart Button to Models with GovernanceFor sale.order form view (as example), add inheritance to show approval button:Create: addons/ops_matrix_core/views/sale_order_views.xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <record id="view_order_form_governance" model="ir.ui.view">
        <field name="name">sale.order.form.governance</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@name='button_box']" position="inside">
                <button name="action_view_approvals" 
                        type="object" 
                        class="oe_stat_button" 
                        icon="fa-check-circle"
                        attrs="{'invisible': [('approval_request_count', '=', 0)]}">
                    <field name="approval_request_count" widget="statinfo" string="Approvals"/>
                </button>
                <button name="action_request_approval" 
                        type="object" 
                        class="oe_stat_button" 
                        icon="fa-paper-plane"
                        string="Request Approval"
                        attrs="{'invisible': ['|', ('approval_locked', '=', True), ('state', 'not in', ['draft', 'sent'])]}"/>
            </xpath>
            <xpath expr="//sheet" position="before">
                <div class="alert alert-warning" role="alert" attrs="{'invisible': [('approval_locked', '=', False)]}">
                    <strong>Approval Required:</strong> This document is locked pending approval. No changes can be made until approved or rejected.
                </div>
            </xpath>
        </field>
    </record>

</odoo>

Step 3J: Update init.py FilesIn models/__init__.py, add:
from . import ops_approval_requestIn __manifest__.py, add to data section:
'views/ops_approval_request_views.xml',
'views/sale_order_views.xml',

ISSUE 4: Fix Domain Syntax ErrorProblem: Validation error with invalid domain syntax when creating sales order without branch.Fix: Update the governance rule evaluation to handle empty/invalid domains gracefully.In models/ops_governance_mixin.py, update condition evaluation:
def _apply_governance_rule(self, rule, trigger_type):
    """Apply a governance rule and handle different action types."""
    context = self._get_governance_context()
    
    # Evaluate condition
    try:
        if rule.condition_code:
            # Clean and validate the code
            code = rule.condition_code.strip()
            if not code:
                return {}
            
            # Execute in safe context
            exec(code, context)
            result = context.get('result', False)
        else:
            result = True
    except SyntaxError as e:
        # Log syntax errors but don't crash
        _logger.error(f"Syntax error in rule {rule.name}: {str(e)}")
        return {}
    except Exception as e:
        # For other errors, show user-friendly message
        raise UserError(f"Error evaluating rule '{rule.name}': {str(e)}")
    
    # ... rest of methodAlso add import at top:
import logging
_logger = logging.getLogger(__name__)

ISSUE 5: Enhance Persona ModelProblem: Persona form needs more fields to act as a proper role template.Solution: Add comprehensive fields to persona model.In models/ops_persona.py, add these fields:
# Add after existing fields:

description = fields.Text(string='Description', help='Detailed description of this persona role')

# Hierarchical structure
parent_id = fields.Many2one('ops.persona', string='Parent Persona', help='Parent role in hierarchy')
child_ids = fields.One2many('ops.persona', 'parent_id', string='Child Personas')

# Access control
access_group_ids = fields.Many2many(
    'res.groups',
    'ops_persona_groups_rel',
    'persona_id',
    'group_id',
    string='Access Groups',
    help='Odoo security groups assigned to this persona'
)

# Department and job function
department_id = fields.Many2one('hr.department', string='Department')
job_level = fields.Selection([
    ('entry', 'Entry Level'),
    ('junior', 'Junior'),
    ('mid', 'Mid-Level'),
    ('senior', 'Senior'),
    ('lead', 'Team Lead'),
    ('manager', 'Manager'),
    ('director', 'Director'),
    ('executive', 'Executive'),
], string='Job Level')

# Approval authority
approval_limit = fields.Monetary(
    string='Approval Limit',
    currency_field='currency_id',
    help='Maximum amount this persona can approve'
)
currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

# Responsibilities
can_approve_orders = fields.Boolean(string='Can Approve Orders', default=False)
can_approve_expenses = fields.Boolean(string='Can Approve Expenses', default=False)
can_approve_leave = fields.Boolean(string='Can Approve Leave', default=False)
can_manage_team = fields.Boolean(string='Can Manage Team', default=False)

# Usage tracking
user_count = fields.Integer(string='Users', compute='_compute_user_count')

@api.depends('id')
def _compute_user_count(self):
    for record in self:
        record.user_count = self.env['res.users'].search_count([('persona_id', '=', record.id)])Update the form view in views/ops_persona_views.xml:
    <record id="view_ops_persona_form" model="ir.ui.view">
    <field name="name">ops.persona.form</field>
    <field name="model">ops.persona</field>
    <field name="arch" type="xml">
        <form string="Persona">
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="toggle_active" type="object" class="oe_stat_button" icon="fa-archive">
                        <field name="active" widget="boolean_button" options="{'terminology': 'archive'}"/>
                    </button>
                </div>
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Persona Name"/>
                    </h1>
                    <h3>
                        <field name="code" readonly="1"/>
                    </h3>
                </div>
                <group>
                    <group string="Basic Information">
                        <field name="parent_id"/>
                        <field name="department_id"/>
                        <field name="job_level"/>
                        <field name="user_count"/>
                    </group>
                    <group string="Approval Authority">
                        <field name="approval_limit"/>
                        <field name="currency_id" invisible="1"/>
                        <field name="can_approve_orders"/>
                        <field name="can_approve_expenses"/>
                        <field name="can_approve_leave"/>
                        <field name="can_manage_team"/>
                    </group>
                </group>
                <group>
                    <field name="description" placeholder="Describe the role and responsibilities..."/>
                </group>
                <notebook>
                    <page string="Access Rights">
                        <field name="access_group_ids" widget="many2many_tags"/>
                    </page>
                    <page string="Branch Access">
                        <field name="primary_branch_id"/>
                        <field name="allowed_branch_ids" widget="many2many_tags"/>
                    </page>
                    <page string="Business Unit Access">
                        <field name="allowed_business_unit_ids" widget="many2many_tags"/>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>

ISSUE 6 & 7: Pre-Configure Standard Personas and Governance RulesSolution: Create data files with deactivated templates that users can activate.

Step 6A: Create Persona TemplatesCreate file: addons/ops_matrix_core/data/ops_persona_templates.xml

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <!-- Executive Level -->
        <record id="persona_ceo" model="ops.persona">
            <field name="name">Chief Executive Officer (CEO)</field>
            <field name="code">CEO</field>
            <field name="description">Highest executive responsible for overall company operations and strategy</field>
            <field name="job_level">executive</field>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_approve_leave" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_cfo" model="ops.persona">
            <field name="name">Chief Financial Officer (CFO)</field>
            <field name="code">CFO</field>
            <field name="description">Executive responsible for financial planning, management, and reporting</field>
            <field name="job_level">executive</field>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_coo" model="ops.persona">
            <field name="name">Chief Operating Officer (COO)</field>
            <field name="code">COO</field>
            <field name="description">Executive responsible for daily operations and operational efficiency</field>
            <field name="job_level">executive</field>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Director Level -->
        <record id="persona_sales_director" model="ops.persona">
            <field name="name">Sales Director</field>
            <field name="code">SALES_DIR</field>
            <field name="description">Director overseeing sales operations and strategy</field>
            <field name="job_level">director</field>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_finance_director" model="ops.persona">
            <field name="name">Finance Director</field>
            <field name="code">FIN_DIR</field>
            <field name="description">Director managing financial operations and accounting</field>
            <field name="job_level">director</field>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_operations_director" model="ops.persona">
            <field name="name">Operations Director</field>
            <field name="code">OPS_DIR</field>
            <field name="description">Director managing operational processes and efficiency</field>
            <field name="job_level">director</field>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Manager Level -->
        <record id="persona_sales_manager" model="ops.persona">
            <field name="name">Sales Manager</field>
            <field name="code">SALES_MGR</field>
            <field name="description">Manager responsible for sales team and targets</field>
            <field name="job_level">manager</field>
            <field name="parent_id" ref="persona_sales_director"/>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_account_manager" model="ops.persona">
            <field name="name">Account Manager</field>
            <field name="code">ACCT_MGR</field>
            <field name="description">Manager handling key customer accounts</field>
            <field name="job_level">manager</field>
            <field name="parent_id" ref="persona_sales_director"/>
            <field name="can_approve_orders" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_finance_manager" model="ops.persona">
            <field name="name">Finance Manager</field>
            <field name="code">FIN_MGR</field>
            <field name="description">Manager overseeing accounting and financial operations</field>
            <field name="job_level">manager</field>
            <field name="parent_id" ref="persona_finance_director"/>
            <field name="can_approve_expenses" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_warehouse_manager" model="ops.persona">
            <field name="name">Warehouse Manager</field>
            <field name="code">WH_MGR</field>
            <field name="description">Manager responsible for warehouse operations and inventory</field>
            <field name="job_level">manager</field>
            <field name="parent_id" ref="persona_operations_director"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_purchasing_manager" model="ops.persona">
            <field name="name">Purchasing Manager</field>
            <field name="code">PURCH_MGR</field>
            <field name="description">Manager handling procurement and vendor relationships</field>
            <field name="job_level">manager</field>
            <field name="parent_id" ref="persona_operations_director"/>
            <field name="can_approve_orders" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_hr_manager" model="ops.persona">
            <field name="name">HR Manager</field>
            <field name="code">HR_MGR</field>
            <field name="description">Manager responsible for human resources and recruitment</field>
            <field name="job_level">manager</field>
            <field name="can_approve_leave" eval="True"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Team Lead Level -->
        <record id="persona_sales_team_lead" model="ops.persona">
            <field name="name">Sales Team Lead</field>
            <field name="code">SALES_LEAD</field>
            <field name="description">Team lead coordinating sales activities</field>
            <field name="job_level">lead</field>
            <field name="parent_id" ref="persona_sales_manager"/>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_support_team_lead" model="ops.persona">
            <field name="name">Customer Support Team Lead</field>
            <field name="code">SUPP_LEAD</field>
            <field name="description">Team lead managing customer support operations</field>
            <field name="job_level">lead</field>
            <field name="can_manage_team" eval="True"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Senior Level -->
        <record id="persona_senior_sales" model="ops.persona">
            <field name="name">Senior Sales Executive</field>
            <field name="code">SR_SALES</field>
            <field name="description">Experienced sales professional handling major accounts</field>
            <field name="job_level">senior</field>
            <field name="parent_id" ref="persona_sales_team_lead"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_senior_accountant" model="ops.persona">
            <field name="name">Senior Accountant</field>
            <field name="code">SR_ACCT</field>
            <field name="description">Senior accounting professional handling complex transactions</field>
            <field name="job_level">senior</field>
            <field name="parent_id" ref="persona_finance_manager"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Mid Level -->
        <record id="persona_sales_executive" model="ops.persona">
            <field name="name">Sales Executive</field>
            <field name="code">SALES_EXEC</field>
            <field name="description">Sales professional managing customer relationships and deals</field>
            <field name="job_level">mid</field>
            <field name="parent_id" ref="persona_sales_team_lead"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_accountant" model="ops.persona">
            <field name="name">Accountant</field>
            <field name="code">ACCOUNTANT</field>
            <field name="description">Accounting professional handling financial transactions</field>
            <field name="job_level">mid</field>
            <field name="parent_id" ref="persona_finance_manager"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_warehouse_operator" model="ops.persona">
            <field name="name">Warehouse Operator</field>
            <field name="code">WH_OPR</field>
            <field name="description">Warehouse staff handling inventory and logistics</field>
            <field name="job_level">mid</field>
            <field name="parent_id" ref="persona_warehouse_manager"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_purchasing_officer" model="ops.persona">
            <field name="name">Purchasing Officer</field>
            <field name="code">PURCH_OFF</field>
            <field name="description">Procurement professional handling purchase orders</field>
            <field name="job_level">mid</field>
            <field name="parent_id" ref="persona_purchasing_manager"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_support_specialist" model="ops.persona">
            <field name="name">Customer Support Specialist</field>
            <field name="code">SUPP_SPEC</field>
            <field name="description">Support staff assisting customers</field>
            <field name="job_level">mid</field>
            <field name="parent_id" ref="persona_support_team_lead"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Junior Level -->
        <record id="persona_junior_sales" model="ops.persona">
            <field name="name">Junior Sales Executive</field>
            <field name="code">JR_SALES</field>
            <field name="description">Entry-level sales role learning the business</field>
            <field name="job_level">junior</field>
            <field name="parent_id" ref="persona_sales_executive"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_junior_accountant" model="ops.persona">
            <field name="name">Junior Accountant</field>
            <field name="code">JR_ACCT</field>
            <field name="description">Entry-level accounting role</field>
            <field name="job_level">junior</field>
            <field name="parent_id" ref="persona_accountant"/>
            <field name="active" eval="False"/>
        </record>

        <record id="persona_data_entry" model="ops.persona">
            <field name="name">Data Entry Clerk</field>
            <field name="code">DATA_ENTRY</field>
            <field name="description">Staff responsible for data input and maintenance</field>
            <field name="job_level">entry</field>
            <field name="active" eval="False"/>
        </record>

    </data>
</odoo>

Step 6B: Create Governance Rule TemplatesCreate file: addons/ops_matrix_core/data/ops_governance_rule_templates.xml

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <!-- Sales Order Rules -->
        <record id="rule_high_value_order_approval" model="ops.governance.rule">
            <field name="name">High Value Order Approval</field>
            <field name="code">GR_SO_001</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Orders over $50,000 require manager approval</field>
            <field name="condition_code">result = record.amount_total > 50000</field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_sales_manager'))]"/>
            <field name="active" eval="False"/>
        </record>

        <record id="rule_large_discount_approval" model="ops.governance.rule">
            <field name="name">Large Discount Approval Required</field>
            <field name="code">GR_SO_002</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="trigger_type">on_write</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Discounts over 20% require director approval</field>
            <field name="condition_code">
# Check if any order line has discount > 20%
result = False
for line in record.order_line:
    if line.discount > 20:
        result = True
        break
            </field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_sales_director'))]"/>
            <field name="active" eval="False"/>
        </record>

        <record id="rule_credit_limit_warning" model="ops.governance.rule">
            <field name="name">Customer Credit Limit Warning</field>
            <field name="code">GR_SO_003</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">warning</field>
            <field name="error_message">Warning: Customer is approaching credit limit</field>
            <field name="condition_code">
# Check if customer has credit limit set
if record.partner_id.credit_limit > 0:
    total_due = record.partner_id.credit + record.amount_total
    result = total_due > (record.partner_id.credit_limit * 0.9)
else:
    result = False
            </field>
            <field name="active" eval="False"/>
        </record>

        <record id="rule_junior_sales_limit" model="ops.persona">
            <field name="name">Junior Sales Order Limit</field>
            <field name="code">GR_SO_004</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">block</field>
            <field name="error_message">Junior sales staff cannot create orders over $10,000</field>
            <field name="condition_code">
result = record.amount_total > 10000 and persona.code in ['JR_SALES', 'SALES_EXEC']
            </field>
            <field name="active" eval="False"/>
        </record>

        <!-- Purchase Order Rules -->
        <record id="rule_purchase_approval_50k" model="ops.governance.rule">
            <field name="name">Purchase Order Approval - Over 50K</field>
            <field name="code">GR_PO_001</field>
            <field name="model_id" ref="purchase.model_purchase_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Purchase orders over $50,000 require manager approval</field>
            <field name="condition_code">result = record.amount_total > 50000</field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_purchasing_manager'))]"/>
            <field name="active" eval="False"/>
        </record>

        <record id="rule_purchase_approval_100k" model="ops.governance.rule">
            <field name="name">Purchase Order Approval - Over 100K</field>
            <field name="code">GR_PO_002</field>
            <field name="model_id" ref="purchase.model_purchase_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Purchase orders over $100,000 require director approval</field>
            <field name="condition_code">result = record.amount_total > 100000</field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_operations_director'))]"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Expense Rules -->
        <record id="rule_expense_approval_1k" model="ops.governance.rule">
            <field name="name">Expense Approval - Over 1K</field>
            <field name="code">GR_EXP_001</field>
            <field name="model_id" ref="hr_expense.model_hr_expense"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Expenses over $1,000 require manager approval</field>
            <field name="condition_code">result = record.total_amount > 1000</field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_finance_manager'))]"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Invoice Rules -->
        <record id="rule_invoice_approval_payment_terms" model="ops.governance.rule">
            <field name="name">Custom Payment Terms Approval</field>
            <field name="code">GR_INV_001</field>
            <field name="model_id" ref="account.model_account_move"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Custom payment terms require finance manager approval</field>
            <field name="condition_code">
# Check if payment term is not standard (e.g., not 30 days)
result = record.move_type == 'out_invoice' and record.invoice_payment_term_id.name not in ['Immediate Payment', '30 Days']
            </field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_finance_manager'))]"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Inventory Rules -->
        <record id="rule_stock_adjustment_approval" model="ops.governance.rule">
            <field name="name">Large Stock Adjustment Approval</field>
            <field name="code">GR_INV_002</field>
            <field name="model_id" ref="stock.model_stock_quant"/>
            <field name="trigger_type">on_write</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Stock adjustments over 100 units require warehouse manager approval</field>
            <field name="condition_code">
# Check if quantity change is significant
result = abs(record.quantity - record._origin.quantity) > 100
            </field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_warehouse_manager'))]"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Customer/Vendor Rules -->
        <record id="rule_customer_credit_limit_approval" model="ops.governance.rule">
            <field name="name">Customer Credit Limit Change Approval</field>
            <field name="code">GR_CUS_001</field>
            <field name="model_id" ref="base.model_res_partner"/>
            <field name="trigger_type">on_write</field>
            <field name="action_type">require_approval</field>
            <field name="error_message">Credit limit changes over $50,000 require finance director approval</field>
            <field name="condition_code">
# Check if credit limit was increased significantly
if 'credit_limit' in record._fields and record._origin.credit_limit:
    increase = record.credit_limit - record._origin.credit_limit
    result = increase > 50000
else:
    result = False
            </field>
            <field name="approval_persona_ids" eval="[(4, ref('persona_finance_director'))]"/>
            <field name="active" eval="False"/>
        </record>

        <!-- Cross-Branch Rules -->
        <record id="rule_cross_branch_order" model="ops.governance.rule">
            <field name="name">Cross-Branch Order Warning</field>
            <field name="code">GR_BR_001</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="trigger_type">on_create</field>
            <field name="action_type">warning</field>
            <field name="error_message">This order is for a customer from a different branch</field>
            <field name="condition_code">
# Check if customer's branch differs from user's branch
user_branch = env.user.primary_branch_id
customer_branch = record.partner_id.primary_branch_id
result = user_branch and customer_branch and user_branch != customer_branch
            </field>
            <field name="active" eval="False"/>
        </record>

    </data>
</odoo>

Step 6C: Update ManifestIn __manifest__.py, add to data section (order matters):

'data': [
    'security/ops_security.xml',
    'security/ir.model.access.csv',
    'data/ir_sequence_data.xml',
    'data/ops_persona_templates.xml',  # ADD THIS
    'data/ops_governance_rule_templates.xml',  # ADD THIS
    'views/ops_business_unit_views.xml',
    # ... rest of views
],

FINAL STEPS: Update Module and Test

Step 1: Update init.py in models/Ensure all new models are imported:

from . import ops_business_unit
from . import ops_branch
from . import ops_persona
from . import ops_persona_delegation
from . import ops_governance_rule
from . import ops_governance_mixin
from . import ops_approval_request  # ADD THIS
from . import res_users
from . import sale_order  # If you created separate file

Step 2: Update Module

Run: 

docker exec -it gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init

docker restart gemini_odoo19

Step 3: Verify All FixesAfter restart, log in as admin and verify:
✅ Can create Business Units and Branches without access errors
✅ All codes are auto-generated and readonly
✅ Approval workflow available in Governance Rules
✅ No syntax errors when creating sales orders
✅ Persona form has comprehensive fields
✅ Pre-configured personas visible (deactivated) in Settings → OPS Governance → Personas
✅ Pre-configured governance rules visible (deactivated) in Settings → OPS Governance → Governance Rules
Step 4: Test Approval Workflow
Activate persona: Sales Manager
Activate rule: High Value Order Approval
Assign Sales Manager persona to an approver user
Create sales order > $50,000
Should see "Request Approval" button
Submit for approval
Log in as approver and approve
REPORT BACK WITH:
Did all module updates complete without errors? (Yes/No)
Can you now create Branches/BUs as admin? (Yes/No)
Are codes auto-generated for all entities? (Yes/No)
Does the approval workflow work? (Yes/No)
Can you see and activate pre-configured personas? (Yes/No)
Can you see and activate pre-configured governance rules? (Yes/No)
Any errors in logs? (paste them)
Screenshots of: Persona list, Governance Rules list, Approval request