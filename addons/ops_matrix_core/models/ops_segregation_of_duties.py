# -*- coding: utf-8 -*-
"""
Segregation of Duties (SoD) Security Implementation
Prevents same user from creating AND confirming/posting critical transactions
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class OpsSoDRule(models.Model):
    """
    Segregation of Duties Rules
    
    Defines rules that prevent a single user from performing multiple
    critical actions on the same document (e.g., creating and confirming).
    """
    _name = 'ops.segregation.of.duties'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Segregation of Duties Rules'
    _order = 'name'
    
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Descriptive name for this SoD rule'
    )
    
    model_name = fields.Selection(
        selection=[
            ('sale.order', 'Sales Order'),
            ('purchase.order', 'Purchase Order'),
            ('account.move', 'Invoice/Bill'),
            ('account.payment', 'Payment'),
            ('stock.picking', 'Stock Picking'),
        ],
        string='Document Type',
        required=True,
        help='Which document type this rule applies to'
    )
    
    action_1 = fields.Selection(
        selection=[
            ('create', 'Create'),
            ('confirm', 'Confirm'),
            ('approve', 'Approve'),
            ('post', 'Post'),
            ('validate', 'Validate'),
        ],
        string='First Action',
        required=True,
        help='The first action that triggers the rule'
    )
    
    action_2 = fields.Selection(
        selection=[
            ('create', 'Create'),
            ('confirm', 'Confirm'),
            ('approve', 'Approve'),
            ('post', 'Post'),
            ('validate', 'Validate'),
        ],
        string='Blocked Action',
        required=True,
        help='The second action that will be blocked if same user performed action_1'
    )
    
    threshold_amount = fields.Float(
        string='Threshold Amount',
        default=0.0,
        help='Rule only applies to documents with amount >= threshold. 0 = always enforce'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Controls visibility in menus. Uncheck to archive/hide the rule.'
    )
    enabled = fields.Boolean(
        string='Enabled',
        default=False,
        copy=False,
        help='If checked, this SoD rule is enforced. '
             'CATALOG MODE: Rules can be visible (active=True) but not enforced (enabled=False). '
             'This allows administrators to review available SoD rules without activating them.'
    )

    block_violation = fields.Boolean(
        string='Block Violation',
        default=True,
        help='If True, block the action. If False, only log the violation'
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        help='Leave empty to apply to all companies'
    )
    
    is_system_rule = fields.Boolean(
        string='System Rule',
        default=False,
        readonly=True,
        help='System rules are created during module installation'
    )
    
    violation_count = fields.Integer(
        string='Violation Count',
        compute='_compute_violation_count',
        store=False,
        help='Number of violations detected by this rule'
    )
    
    description = fields.Text(
        string='Description',
        help='Additional details about why this rule exists'
    )
    
    created_date = fields.Datetime(
        string='Created Date',
        readonly=True,
        default=lambda self: fields.Datetime.now()
    )
    
    def _compute_violation_count(self):
        """Count violations associated with this rule."""
        for rule in self:
            rule.violation_count = self.env['ops.segregation.of.duties.log'].search_count(
                [('rule_id', '=', rule.id)]
            )
    
    def _check_rule_applies(self, record, action):
        """
        Check if this rule applies to the given record and action.

        Returns: Boolean - True if rule should be enforced
        """
        self.ensure_one()

        # CATALOG MODE: Rule must be enabled to be enforced
        if not self.enabled:
            return False
        
        # Document type must match
        if record._name != self.model_name:
            return False
        
        # Action must match
        if action != self.action_2:
            return False
        
        # Company check (if rule is company-specific)
        if self.company_id and record.company_id != self.company_id:
            return False
        
        # Threshold check
        if self.threshold_amount > 0:
            if hasattr(record, 'amount_total'):
                if record.amount_total < self.threshold_amount:
                    return False
        
        return True
    
    def _get_action_1_user(self, record):
        """
        Get the user who performed action_1 on the record.
        
        Returns: res.users or None
        """
        self.ensure_one()
        
        action_1 = self.action_1
        
        if action_1 == 'create':
            # Get the user who created the record
            return record.create_uid if hasattr(record, 'create_uid') else None
        
        elif action_1 == 'confirm':
            # Check for state change fields or workflows
            # For sale.order and purchase.order
            if hasattr(record, 'state') and record.state == 'sale':
                # Get from create_uid as fallback (cannot reliably determine who confirmed)
                return record.create_uid
        
        elif action_1 == 'post':
            # For account.move
            if hasattr(record, 'state') and record.state == 'posted':
                return record.create_uid
        
        elif action_1 == 'approve':
            # Get from approval workflow if available
            if hasattr(record, 'approval_request_ids'):
                approved_requests = record.approval_request_ids.filtered(
                    lambda r: r.state == 'approved'
                )
                if approved_requests:
                    return approved_requests[0].approver_id
        
        return None
    
    def action_enable_rule(self):
            """Enable SoD rule - called from list view button"""
            for rule in self:
                rule.write({'active': True})
            return True
        
    def action_disable_rule(self):
        """Disable SoD rule - called from list view button"""
        for rule in self:
            rule.write({'active': False})
        return True

class OpsSoDLog(models.Model):
    """
    Segregation of Duties Violation Log
    
    Audit trail for all SoD violations detected, whether blocked or allowed.
    Used for compliance reporting and violation analysis.
    """
    _name = 'ops.segregation.of.duties.log'
    _description = 'SoD Violation Log'
    _order = 'timestamp desc'
    
    rule_id = fields.Many2one(
        comodel_name='ops.segregation.of.duties',
        string='Rule',
        required=True,
        ondelete='cascade'
    )
    
    model_name = fields.Char(
        string='Document Model',
        required=True,
        help='The model name of the document (e.g., sale.order)'
    )
    
    res_id = fields.Integer(
        string='Document ID',
        required=True,
        help='The database ID of the document'
    )
    
    document_reference = fields.Char(
        string='Document Reference',
        help='Human-readable reference (e.g., SO-001)'
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Violating User',
        required=True,
        ondelete='cascade',
        help='User who attempted the blocked action'
    )
    
    action_1_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Action 1 User',
        ondelete='set null',
        help='User who performed the first action'
    )
    
    action_attempted = fields.Char(
        string='Attempted Action',
        required=True,
        help='The action that was blocked'
    )
    
    blocked = fields.Boolean(
        string='Blocked',
        default=True,
        help='Whether the action was blocked or only logged'
    )
    
    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=lambda self: fields.Datetime.now()
    )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional context about the violation'
    )
    
    @api.model
    def create(self, vals):
        """Log when violations are created."""
        result = super().create(vals)
        
        # Log to system logger for compliance audit
        _logger.warning(
            'SoD Violation Detected [Rule: %s] [User: %s] [Document: %s/%s] [Blocked: %s]',
            vals.get('rule_id'),
            vals.get('user_id'),
            vals.get('model_name'),
            vals.get('res_id'),
            vals.get('blocked', True)
        )
        
        return result
    
    def get_violation_summary(self):
        """Get summary statistics for reporting."""
        self.ensure_one()
        
        return {
            'rule_name': self.rule_id.name,
            'rule_id': self.rule_id.id,
            'user_name': self.user_id.name,
            'action_1_user': self.action_1_user_id.name if self.action_1_user_id else 'Unknown',
            'document': f"{self.model_name}/{self.res_id}",
            'document_ref': self.document_reference,
            'timestamp': self.timestamp,
            'blocked': self.blocked,
        }
    
    @api.model
    def get_violations_report(self, start_date=None, end_date=None, rule_id=None, user_id=None):
        """
        Generate a compliance report of SoD violations.
        
        Args:
            start_date: Filter violations after this date
            end_date: Filter violations before this date
            rule_id: Filter by specific rule
            user_id: Filter by specific user
        
        Returns: List of violation summaries
        """
        domain = []
        
        if start_date:
            domain.append(('timestamp', '>=', start_date))
        if end_date:
            domain.append(('timestamp', '<=', end_date))
        if rule_id:
            domain.append(('rule_id', '=', rule_id))
        if user_id:
            domain.append(('user_id', '=', user_id))
        
        violations = self.search(domain)
        return [v.get_violation_summary() for v in violations]
