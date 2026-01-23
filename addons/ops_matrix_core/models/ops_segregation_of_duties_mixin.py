# -*- coding: utf-8 -*-
"""
Segregation of Duties (SoD) Mixin
Applied to critical transaction models to enforce SoD rules
"""

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsSoDMixin(models.AbstractModel):
    """
    Segregation of Duties Enforcement Mixin
    
    Provides enforcement of SoD rules on models.
    Mix in with: sale.order, purchase.order, account.move, account.payment
    
    Usage:
        _inherit = ['model.name', 'ops.segregation.of.duties.mixin']
    
    Then call _check_sod_violation('action') before state-changing methods.
    """
    _name = 'ops.segregation.of.duties.mixin'
    _description = 'Segregation of Duties Enforcement'
    
    def _check_sod_violation(self, action):
        """
        Check if current action violates SoD rules.
        
        Args:
            action (str): The action being performed (confirm, post, validate, etc.)
        
        Raises:
            UserError: If SoD violation is detected and block_violation=True
        
        Returns:
            None
        """
        self.ensure_one()
        
        # Skip checks for superuser/admin
        if self.env.su or self.env.user.has_group('base.group_system'):
            return
        
        _logger.info(
            'SoD Check: %s [%s] action=%s user=%s',
            self._name, self.id, action, self.env.user.name
        )
        
        # Get applicable SoD rules
        SoDRule = self.env['ops.segregation.of.duties']
        
        rules = SoDRule.search([
            ('model_name', '=', self._name),
            ('action_2', '=', action),
            ('active', '=', True),
            '|',
                ('company_id', '=', False),
                ('company_id', '=', self.company_id.id)
        ])
        
        if not rules:
            return
        
        _logger.debug('Found %d applicable SoD rules for %s', len(rules), self._name)
        
        for rule in rules:
            # CATALOG MODE: Skip rules that are not enabled
            # This allows rules to be visible (active=True) but not enforced (enabled=False)
            if not rule.enabled:
                _logger.debug(
                    'Rule %s: Not enabled (Catalog Mode), skipping enforcement',
                    rule.name
                )
                continue

            # Check if threshold applies
            if rule.threshold_amount > 0:
                if hasattr(self, 'amount_total'):
                    if self.amount_total < rule.threshold_amount:
                        _logger.debug(
                            'Rule %s: Amount %.2f below threshold %.2f, skipping',
                            rule.name, self.amount_total, rule.threshold_amount
                        )
                        continue
            
            # Get user who performed action_1
            action_1_user = rule._get_action_1_user(self)
            
            if not action_1_user:
                _logger.debug('Rule %s: Could not determine action_1 user, skipping', rule.name)
                continue
            
            # Check if same user is trying to perform action_2
            if action_1_user.id == self.env.user.id:
                # SoD violation detected!
                _logger.warning(
                    'SoD Violation: User %s attempted to perform %s after %s on %s/%s',
                    self.env.user.name, action, rule.action_1, self._name, self.id
                )
                
                self._log_sod_violation(rule, action, action_1_user)
                
                if rule.block_violation:
                    raise UserError(_(
                        "🚫 SEGREGATION OF DUTIES VIOLATION!\n\n"
                        "Rule: %(rule_name)s\n\n"
                        "You cannot %(action)s this document because you already %(action1)s it.\n"
                        "Another user must perform this action to maintain proper controls.\n\n"
                        "This restriction is in place to prevent fraud and ensure proper "
                        "authorization workflow."
                    ) % {
                        'rule_name': rule.name,
                        'action': action,
                        'action1': rule.action_1,
                    })
    
    def _log_sod_violation(self, rule, action, action_1_user):
        """
        Log SoD violation for audit trail.
        
        Args:
            rule: ops.segregation.of.duties record
            action: The action that was blocked
            action_1_user: res.users who performed first action
        """
        self.ensure_one()
        
        log_vals = {
            'rule_id': rule.id,
            'model_name': self._name,
            'res_id': self.id,
            'user_id': self.env.user.id,
            'action_1_user_id': action_1_user.id,
            'action_attempted': action,
            'blocked': rule.block_violation,
            'document_reference': self.name if hasattr(self, 'name') else str(self.id),
            'company_id': self.company_id.id if hasattr(self, 'company_id') else self.env.company.id,
            'notes': f"Violation of rule '{rule.name}': {self.env.user.name} attempted to {action} "
                     f"document {self.name} after {action_1_user.name} performed {rule.action_1}",
        }
        
        try:
            self.env['ops.segregation.of.duties.log'].create(log_vals)
            _logger.info('SoD violation logged: rule=%s user=%s action=%s', 
                         rule.id, self.env.user.id, action)
        except Exception as e:
            _logger.error('Failed to log SoD violation: %s', str(e))
            # Don't raise - logging failure shouldn't block the enforcement
    
    def _notify_sod_violation(self, rule, action_1_user):
        """
        Send notification about SoD violation to chatter.
        
        Args:
            rule: ops.segregation.of.duties record
            action_1_user: res.users who performed first action
        """
        self.ensure_one()
        
        if not hasattr(self, 'message_post'):
            return
        
        message = _(
            "⚠️ <b>Segregation of Duties Violation Detected</b><br/><br/>"
            "Rule: %(rule_name)s<br/>"
            "Attempted action: %(action)s<br/>"
            "Original actor: %(user)s<br/>"
            "Violating user: %(violator)s<br/><br/>"
            "This violation has been logged for compliance audit."
        ) % {
            'rule_name': rule.name,
            'action': rule.action_2,
            'user': action_1_user.name,
            'violator': self.env.user.name,
        }
        
        try:
            self.message_post(
                body=message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
        except Exception as e:
            _logger.debug('Failed to post SoD violation to chatter: %s', str(e))
