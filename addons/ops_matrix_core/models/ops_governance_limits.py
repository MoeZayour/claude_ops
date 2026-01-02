# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsGovernanceDiscountLimit(models.Model):
    """Role-Based Discount Limits integrated with Persona Model"""
    _name = 'ops.governance.discount.limit'
    _description = 'Role-Based Discount Limits'
    _order = 'max_discount_percent desc'
    
    rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade', string='Governance Rule')
    
    # Target definition (either persona or group)
    persona_id = fields.Many2one('ops.persona', string='Persona/Role',
                                 help='Apply limit to users with this persona')
    user_group_id = fields.Many2one('res.groups', string='User Group',
                                    help='Alternative to persona: apply to all users in group')
    
    # Limit configuration
    max_discount_percent = fields.Float(
        string='Maximum Discount %', 
        required=True,
        digits=(5, 2), 
        default=0.0,
        help='Maximum discount percentage without approval'
    )
    
    approval_required_above = fields.Float(
        string='Approval Required Above %',
        digits=(5, 2),
        help='Discount percentage that triggers approval requirement'
    )
    
    # Approval configuration
    approver_persona_ids = fields.Many2many(
        'ops.persona', 
        'discount_limit_approver_rel',
        'limit_id',
        'persona_id',
        string='Approver Personas',
        help='Personas that can approve discount exceptions'
    )
    
    approver_group_ids = fields.Many2many(
        'res.groups', 
        'discount_limit_group_approver_rel',
        'limit_id',
        'group_id',
        string='Approver Groups',
        help='User groups that can approve discount exceptions'
    )
    
    # Scope restrictions
    branch_ids = fields.Many2many(
        'ops.branch', 
        'discount_limit_branch_rel',
        'limit_id',
        'branch_id',
        string='Applicable Branches',
        help='Limit applies only to these branches (empty = all)'
    )
    
    business_unit_ids = fields.Many2many(
        'ops.business.unit', 
        'discount_limit_bu_rel',
        'limit_id',
        'bu_id',
        string='Applicable Business Units',
        help='Limit applies only to these BUs (empty = all)'
    )
    
    product_category_ids = fields.Many2many(
        'product.category', 
        'discount_limit_category_rel',
        'limit_id',
        'category_id',
        string='Applicable Categories',
        help='Limit applies only to these categories (empty = all)'
    )
    
    # Validation
    @api.constrains('persona_id', 'user_group_id')
    def _check_target(self):
        """Ensure either persona or group is specified, but not both."""
        for limit in self:
            if not limit.persona_id and not limit.user_group_id:
                raise ValidationError(_("Either Persona or User Group must be specified"))
            if limit.persona_id and limit.user_group_id:
                raise ValidationError(_("Specify either Persona OR User Group, not both"))
    
    @api.constrains('max_discount_percent', 'approval_required_above')
    def _check_percentages(self):
        """Validate percentage values."""
        for limit in self:
            if limit.max_discount_percent < 0 or limit.max_discount_percent > 100:
                raise ValidationError(_("Maximum discount must be between 0 and 100"))
            if limit.approval_required_above and (limit.approval_required_above < 0 or limit.approval_required_above > 100):
                raise ValidationError(_("Approval threshold must be between 0 and 100"))
    
    def get_applicable_limit(self, user, branch_id=False, bu_id=False, category_id=False):
        """Get applicable discount limit for user in context."""
        self.ensure_one()
        
        # Check persona match
        user_personas = user.persona_ids if hasattr(user, 'persona_ids') else self.env['ops.persona']
        
        for persona in user_personas:
            if self.persona_id == persona:
                # Check scope restrictions
                if self._check_scope(branch_id, bu_id, category_id):
                    return self.max_discount_percent
        
        # Check group match
        if self.user_group_id and user.has_group(self.user_group_id.xml_id or 'base.group_user'):
            if self._check_scope(branch_id, bu_id, category_id):
                return self.max_discount_percent
        
        return 0.0
    
    def _check_scope(self, branch_id, bu_id, category_id):
        """Check if limit applies to given scope."""
        # Check branch scope
        if self.branch_ids and branch_id not in self.branch_ids.ids:
            return False
        
        # Check BU scope
        if self.business_unit_ids and bu_id not in self.business_unit_ids.ids:
            return False
        
        # Check category scope
        if self.product_category_ids and category_id not in self.product_category_ids.ids:
            return False
        
        return True


class OpsGovernanceMarginRule(models.Model):
    """Category-Specific Margin Rules with BU/Branch dimensions"""
    _name = 'ops.governance.margin.rule'
    _description = 'Category-Specific Margin Rules'
    _order = 'minimum_margin_percent desc'
    
    rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade', string='Governance Rule')
    
    # Scope definition
    product_category_id = fields.Many2one(
        'product.category', 
        string='Product Category',
        required=True,
        help='Product category this margin rule applies to'
    )
    
    business_unit_id = fields.Many2one(
        'ops.business.unit', 
        string='Business Unit',
        help='Optional: restrict to specific BU'
    )
    
    branch_id = fields.Many2one(
        'ops.branch', 
        string='Branch',
        help='Optional: restrict to specific branch'
    )
    
    # Margin thresholds
    minimum_margin_percent = fields.Float(
        string='Minimum Margin %', 
        required=True,
        digits=(5, 2), 
        default=0.0,
        help='Minimum acceptable margin percentage'
    )
    
    warning_margin_percent = fields.Float(
        string='Warning Threshold %',
        digits=(5, 2),
        help='Margin percentage that triggers warning (above minimum)'
    )
    
    critical_margin_percent = fields.Float(
        string='Critical Threshold %',
        digits=(5, 2),
        help='Margin percentage that requires immediate attention'
    )
    
    # Approval configuration
    approver_persona_ids = fields.Many2many(
        'ops.persona', 
        'margin_rule_approver_rel',
        'rule_id',
        'persona_id',
        string='Approver Personas',
        help='Personas that can approve margin exceptions'
    )
    
    auto_escalate_below = fields.Float(
        string='Auto-Escalate Below %',
        digits=(5, 2),
        help='Auto-create approval request when margin falls below this'
    )
    
    # Special handling
    allow_negative_margin = fields.Boolean(
        string='Allow Negative Margin',
        default=False,
        help='Allow margin below zero with approval'
    )
    
    exclude_from_reports = fields.Boolean(
        string='Exclude from Margin Reports',
        default=False,
        help='Hide this category from standard margin reports'
    )
    
    @api.constrains('minimum_margin_percent', 'warning_margin_percent', 'critical_margin_percent')
    def _check_margin_thresholds(self):
        """Validate margin threshold relationships."""
        for rule in self:
            if rule.warning_margin_percent and rule.warning_margin_percent < rule.minimum_margin_percent:
                raise ValidationError(_("Warning threshold must be greater than minimum margin"))
            if rule.critical_margin_percent and rule.critical_margin_percent < rule.minimum_margin_percent:
                raise ValidationError(_("Critical threshold must be greater than minimum margin"))
    
    def get_applicable_margin(self, category_id, bu_id=False, branch_id=False):
        """Get applicable minimum margin for given context."""
        # Try exact match (category + BU + branch)
        if bu_id and branch_id:
            rule = self.search([
                ('product_category_id', '=', category_id),
                ('business_unit_id', '=', bu_id),
                ('branch_id', '=', branch_id),
                ('rule_id', '=', self.rule_id.id),
            ], limit=1)
            if rule:
                return rule.minimum_margin_percent
        
        # Try category + BU
        if bu_id:
            rule = self.search([
                ('product_category_id', '=', category_id),
                ('business_unit_id', '=', bu_id),
                ('branch_id', '=', False),
                ('rule_id', '=', self.rule_id.id),
            ], limit=1)
            if rule:
                return rule.minimum_margin_percent
        
        # Try category + branch
        if branch_id:
            rule = self.search([
                ('product_category_id', '=', category_id),
                ('business_unit_id', '=', False),
                ('branch_id', '=', branch_id),
                ('rule_id', '=', self.rule_id.id),
            ], limit=1)
            if rule:
                return rule.minimum_margin_percent
        
        # Try category only
        rule = self.search([
            ('product_category_id', '=', category_id),
            ('business_unit_id', '=', False),
            ('branch_id', '=', False),
            ('rule_id', '=', self.rule_id.id),
        ], limit=1)
        if rule:
            return rule.minimum_margin_percent
        
        return 0.0


class OpsGovernancePriceAuthority(models.Model):
    """Role-Based Pricing Authority for price override control"""
    _name = 'ops.governance.price.authority'
    _description = 'Role-Based Pricing Authority'
    _order = 'max_price_variance_percent desc'
    
    rule_id = fields.Many2one('ops.governance.rule', required=True, ondelete='cascade', string='Governance Rule')
    
    # Authority definition
    persona_id = fields.Many2one(
        'ops.persona', 
        string='Persona/Role',
        help='Apply authority to users with this persona'
    )
    
    user_group_id = fields.Many2one(
        'res.groups', 
        string='User Group',
        help='Alternative to persona: apply to all users in group'
    )
    
    # Price variance limits
    max_price_variance_percent = fields.Float(
        string='Maximum Price Variance %',
        digits=(5, 2), 
        default=0.0,
        help='Maximum allowed variance from list price (%)'
    )
    
    max_price_increase_percent = fields.Float(
        string='Maximum Price Increase %',
        digits=(5, 2),
        help='Maximum allowed price increase (%)'
    )
    
    max_price_decrease_percent = fields.Float(
        string='Maximum Price Decrease %',
        digits=(5, 2),
        help='Maximum allowed price decrease (%)'
    )
    
    # Override permissions
    can_override_without_approval = fields.Boolean(
        string='Can Override Without Approval',
        default=False,
        help='User can override price without approval'
    )
    
    approval_required_above = fields.Float(
        string='Approval Required Above %',
        digits=(5, 2),
        help='Price variance that triggers approval requirement'
    )
    
    # Scope restrictions
    branch_ids = fields.Many2many(
        'ops.branch', 
        'price_authority_branch_rel',
        'authority_id',
        'branch_id',
        string='Applicable Branches',
        help='Authority applies only to these branches (empty = all)'
    )
    
    business_unit_ids = fields.Many2many(
        'ops.business.unit', 
        'price_authority_bu_rel',
        'authority_id',
        'bu_id',
        string='Applicable Business Units',
        help='Authority applies only to these BUs (empty = all)'
    )
    
    product_category_ids = fields.Many2many(
        'product.category', 
        'price_authority_category_rel',
        'authority_id',
        'category_id',
        string='Applicable Categories',
        help='Authority applies only to these categories (empty = all)'
    )
    
    # Approval configuration
    approver_persona_ids = fields.Many2many(
        'ops.persona', 
        'price_authority_approver_rel',
        'authority_id',
        'persona_id',
        string='Approver Personas',
        help='Personas that can approve price overrides'
    )
    
    # Validation
    @api.constrains('persona_id', 'user_group_id')
    def _check_target(self):
        """Ensure either persona or group is specified, but not both."""
        for auth in self:
            if not auth.persona_id and not auth.user_group_id:
                raise ValidationError(_("Either Persona or User Group must be specified"))
            if auth.persona_id and auth.user_group_id:
                raise ValidationError(_("Specify either Persona OR User Group, not both"))
    
    @api.constrains('max_price_variance_percent', 'max_price_increase_percent', 'max_price_decrease_percent')
    def _check_percentages(self):
        """Validate percentage values."""
        for auth in self:
            if auth.max_price_variance_percent < 0 or auth.max_price_variance_percent > 100:
                raise ValidationError(_("Price variance must be between 0 and 100"))
            if auth.max_price_increase_percent and (auth.max_price_increase_percent < 0 or auth.max_price_increase_percent > 100):
                raise ValidationError(_("Price increase must be between 0 and 100"))
            if auth.max_price_decrease_percent and (auth.max_price_decrease_percent < 0 or auth.max_price_decrease_percent > 100):
                raise ValidationError(_("Price decrease must be between 0 and 100"))
    
    def get_applicable_authority(self, user, branch_id=False, bu_id=False, category_id=False):
        """Get applicable price authority for user in context."""
        self.ensure_one()
        
        # Check persona match
        user_personas = user.persona_ids if hasattr(user, 'persona_ids') else self.env['ops.persona']
        
        for persona in user_personas:
            if self.persona_id == persona:
                # Check scope restrictions
                if self._check_scope(branch_id, bu_id, category_id):
                    return {
                        'max_variance': self.max_price_variance_percent,
                        'can_override': self.can_override_without_approval,
                        'requires_approval_above': self.approval_required_above,
                    }
        
        # Check group match
        if self.user_group_id and user.has_group(self.user_group_id.xml_id or 'base.group_user'):
            if self._check_scope(branch_id, bu_id, category_id):
                return {
                    'max_variance': self.max_price_variance_percent,
                    'can_override': self.can_override_without_approval,
                    'requires_approval_above': self.approval_required_above,
                }
        
        # Default: no authority
        return {'max_variance': 0.0, 'can_override': False, 'requires_approval_above': 0.0}
    
    def _check_scope(self, branch_id, bu_id, category_id):
        """Check if authority applies to given scope."""
        # Check branch scope
        if self.branch_ids and branch_id not in self.branch_ids.ids:
            return False
        
        # Check BU scope
        if self.business_unit_ids and bu_id not in self.business_unit_ids.ids:
            return False
        
        # Check category scope
        if self.product_category_ids and category_id not in self.product_category_ids.ids:
            return False
        
        return True


class OpsApprovalWorkflow(models.Model):
    """Approval Workflow Definition for multi-step approvals"""
    _name = 'ops.approval.workflow'
    _description = 'Approval Workflow Definition'
    _order = 'name'
    
    name = fields.Char(string='Workflow Name', required=True)
    code = fields.Char(string='Code', required=True, readonly=True, copy=False, default='New')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    
    # Steps configuration
    step_ids = fields.One2many(
        'ops.approval.workflow.step', 
        'workflow_id',
        string='Approval Steps',
        help='Define the sequence of approval steps'
    )
    
    # Settings
    allow_parallel_approval = fields.Boolean(
        string='Allow Parallel Approval',
        default=False,
        help='Multiple approvers can approve simultaneously'
    )
    
    require_unanimous = fields.Boolean(
        string='Require Unanimous Approval',
        default=True,
        help='All approvers must approve'
    )
    
    auto_approve_after_days = fields.Integer(
        string='Auto-Approve After Days',
        default=0,
        help='Automatically approve if no action after X days (0 = disabled)'
    )
    
    # Notifications
    notify_on_submission = fields.Boolean(string='Notify on Submission', default=True)
    notify_on_approval = fields.Boolean(string='Notify on Approval', default=True)
    notify_on_rejection = fields.Boolean(string='Notify on Rejection', default=True)
    
    # Methods
    def get_next_approvers(self, current_step=0):
        """Get approvers for next step in workflow."""
        self.ensure_one()
        steps = self.step_ids.sorted('sequence')
        if current_step >= len(steps):
            return self.env['res.users']
        
        step = steps[current_step]
        return step.get_approvers()
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate code if not provided."""
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.approval.workflow') or 'WF001'
        return super().create(vals_list)


class OpsApprovalWorkflowStep(models.Model):
    """Approval Workflow Step for defining approval sequences"""
    _name = 'ops.approval.workflow.step'
    _description = 'Approval Workflow Step'
    _order = 'sequence, id'
    
    workflow_id = fields.Many2one('ops.approval.workflow', required=True, ondelete='cascade', string='Workflow')
    sequence = fields.Integer(string='Sequence', required=True, default=10)
    name = fields.Char(string='Step Name', required=True)
    
    # Approver definition
    approver_persona_ids = fields.Many2many(
        'ops.persona', 
        'step_persona_approver_rel',
        'step_id',
        'persona_id',
        string='Approver Personas',
        help='Users with these personas can approve'
    )
    
    approver_group_ids = fields.Many2many(
        'res.groups', 
        'step_group_approver_rel',
        'step_id',
        'group_id',
        string='Approver Groups',
        help='Users in these groups can approve'
    )
    
    specific_approver_ids = fields.Many2many(
        'res.users', 
        'step_specific_approver_rel',
        'step_id',
        'user_id',
        string='Specific Approvers',
        help='Specific users who can approve'
    )
    
    # Conditions
    minimum_approvers_required = fields.Integer(
        string='Minimum Approvers Required', 
        default=1,
        help='Minimum number of approvers required to proceed'
    )
    
    approval_threshold_percent = fields.Integer(
        string='Approval Threshold %', 
        default=100,
        help='Percentage of approvers required to approve'
    )
    
    # Actions
    auto_approve_if_no_action = fields.Boolean(
        string='Auto-Approve If No Action',
        default=False
    )
    
    days_for_auto_approve = fields.Integer(
        string='Days for Auto-Approval',
        default=0
    )
    
    # Methods
    def get_approvers(self):
        """Get all approvers for this step."""
        self.ensure_one()
        approvers = self.env['res.users']
        
        # Get users from personas
        if self.approver_persona_ids:
            approvers |= self.approver_persona_ids.mapped('user_id')
        
        # Get users from groups
        for group in self.approver_group_ids:
            approvers |= self.env['res.users'].search([('group_ids', 'in', group.id)])
        
        # Add specific approvers
        approvers |= self.specific_approver_ids
        
        return approvers
