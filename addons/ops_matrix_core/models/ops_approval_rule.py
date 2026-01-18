# -*- coding: utf-8 -*-
"""
OPS Approval Rule - Lightweight wrapper for ops.governance.rule

This model provides a simpler interface for approval-specific rules,
delegating to the full ops.governance.rule engine for enforcement.

The model is required by governance workflows that reference 'ops.approval.rule'.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsApprovalRule(models.Model):
    """
    Approval Rule model for simple approval workflow configuration.

    This is a lightweight model that works alongside ops.governance.rule
    for scenarios where a simple approval rule definition is needed.
    """
    _name = 'ops.approval.rule'
    _description = 'OPS Approval Rule'
    _order = 'sequence, name'
    _inherit = ['mail.thread']

    # Core Fields
    name = fields.Char(
        string='Rule Name',
        required=True,
        tracking=True,
        help='Descriptive name for this approval rule.'
    )

    code = fields.Char(
        string='Rule Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in which rules are evaluated. Lower = higher priority.'
    )

    # Model Targeting
    model_id = fields.Many2one(
        'ir.model',
        string='Applies To',
        required=True,
        ondelete='cascade',
        help='The model this rule applies to (e.g., sale.order, purchase.order).'
    )

    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
        readonly=True
    )

    # Condition
    condition_code = fields.Text(
        string='Condition (Python)',
        help='Python expression that returns True when approval is required.\n'
             'Available variables: record, user, env.\n'
             'Example: record.amount_total > 10000'
    )

    condition_domain = fields.Char(
        string='Condition (Domain)',
        help='Domain filter to match records requiring approval.\n'
             'Example: [(\'amount_total\', \'>\', 10000)]'
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Approvers
    approver_user_ids = fields.Many2many(
        'res.users',
        'ops_approval_rule_user_rel',
        'rule_id',
        'user_id',
        string='Approver Users',
        help='Specific users who can approve this rule.'
    )

    approver_persona_ids = fields.Many2many(
        'ops.persona',
        'ops_approval_rule_persona_rel',
        'rule_id',
        'persona_id',
        string='Approver Personas',
        help='Personas (roles) that can approve this rule.'
    )

    approver_group_ids = fields.Many2many(
        'res.groups',
        'ops_approval_rule_group_rel',
        'rule_id',
        'group_id',
        string='Approver Groups',
        help='Security groups that can approve this rule.'
    )

    # Linked Governance Rule (optional)
    governance_rule_id = fields.Many2one(
        'ops.governance.rule',
        string='Linked Governance Rule',
        help='Link to full governance rule for advanced enforcement.'
    )

    # Statistics
    approval_count = fields.Integer(
        string='Approval Count',
        compute='_compute_approval_count'
    )

    # ============================================
    # COMPUTED METHODS
    # ============================================

    def _compute_approval_count(self):
        """Count approval requests using this rule."""
        ApprovalRequest = self.env['ops.approval.request']
        for rule in self:
            # Count by rule_id if governance rule linked, otherwise by approval_rule_id
            if rule.governance_rule_id:
                rule.approval_count = ApprovalRequest.search_count([
                    ('rule_id', '=', rule.governance_rule_id.id)
                ])
            else:
                rule.approval_count = ApprovalRequest.search_count([
                    ('approval_rule_id', '=', rule.id)
                ])

    # ============================================
    # BUSINESS METHODS
    # ============================================

    def check_requires_approval(self, record):
        """
        Check if a record requires approval based on this rule.

        Args:
            record: The record to check

        Returns:
            bool: True if approval is required
        """
        self.ensure_one()

        if not self.active:
            return False

        # Check model match
        if record._name != self.model_name:
            return False

        # Check domain condition
        if self.condition_domain:
            try:
                from odoo.tools.safe_eval import safe_eval
                domain = safe_eval(self.condition_domain)
                if not record.filtered_domain(domain):
                    return False
            except Exception as e:
                _logger.warning(f"Error evaluating domain for rule {self.name}: {e}")
                return False

        # Check Python condition
        if self.condition_code:
            try:
                from odoo.tools.safe_eval import safe_eval
                local_vars = {
                    'record': record,
                    'user': self.env.user,
                    'env': self.env,
                }
                result = safe_eval(self.condition_code, local_vars)
                if not result:
                    return False
            except Exception as e:
                _logger.warning(f"Error evaluating condition for rule {self.name}: {e}")
                return False

        return True

    def get_approvers(self, record=None):
        """
        Get the approvers for this rule.

        Args:
            record: Optional record for context-aware approver selection

        Returns:
            res.users recordset
        """
        self.ensure_one()
        approvers = self.env['res.users']

        # Direct user approvers
        approvers |= self.approver_user_ids

        # Persona-based approvers
        if self.approver_persona_ids:
            persona_users = self.env['res.users'].search([
                ('ops_persona_ids', 'in', self.approver_persona_ids.ids),
                ('active', '=', True)
            ])
            approvers |= persona_users

        # Group-based approvers
        if self.approver_group_ids:
            group_users = self.env['res.users'].search([
                ('groups_id', 'in', self.approver_group_ids.ids),
                ('active', '=', True)
            ])
            approvers |= group_users

        return approvers

    def create_approval_request(self, record, notes=''):
        """
        Create an approval request for this rule.

        Args:
            record: The record requiring approval
            notes: Optional notes/reason

        Returns:
            ops.approval.request record
        """
        self.ensure_one()

        approvers = self.get_approvers(record)
        if not approvers:
            raise ValidationError(_(
                "No approvers configured for rule '%s'. "
                "Please configure approver users, personas, or groups."
            ) % self.name)

        # Create the approval request
        vals = {
            'name': _("Approval: %s - %s") % (self.name, record.display_name),
            'approval_rule_id': self.id,
            'rule_id': self.governance_rule_id.id if self.governance_rule_id else False,
            'model_name': record._name,
            'res_id': record.id,
            'notes': notes or _("Approval required by rule: %s") % self.name,
            'approver_ids': [(6, 0, approvers.ids)],
            'requested_by': self.env.user.id,
        }

        return self.env['ops.approval.request'].create(vals)

    # ============================================
    # CRUD OVERRIDES
    # ============================================

    @api.model_create_multi
    def create(self, vals_list):
        """Generate code if not provided."""
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.approval.rule') or 'APR0001'
        return super().create(vals_list)

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_approvals(self):
        """View approval requests for this rule."""
        self.ensure_one()

        domain = []
        if self.governance_rule_id:
            domain = [('rule_id', '=', self.governance_rule_id.id)]
        else:
            domain = [('approval_rule_id', '=', self.id)]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Requests'),
            'res_model': 'ops.approval.request',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'default_approval_rule_id': self.id},
        }
