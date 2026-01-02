# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'ops.governance.mixin']
    
    # Governance Fields (explicitly declared for proper column creation)
    approval_locked = fields.Boolean(
        string='Approval Locked',
        default=False,
        help='Record is locked pending approval',
        copy=False
    )
    
    # OPS Matrix Fields
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        tracking=True,
        help='Operational branch for this purchase order'
    )
    
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        tracking=True,
        help='Business unit for this purchase order'
    )
    
    @api.onchange('ops_branch_id')
    def _onchange_ops_branch_id(self):
        """Update company when branch changes."""
        if self.ops_branch_id:
            self.company_id = self.ops_branch_id.company_id
    
    def button_confirm(self):
        """
        Override button_confirm to enforce governance rules before confirmation.
        
        This ensures that governance rules are checked even if standard write()
        is bypassed, providing a hard gate for purchase order confirmation.
        """
        for order in self:
            _logger.info("OPS Governance: Checking PO %s for confirmation rules", order.name)
            
            # ADMIN BYPASS: Skip governance for administrators
            if self.env.su or self.env.user.has_group('base.group_system'):
                _logger.info("OPS Governance: Admin bypass for PO %s", order.name)
                # Log admin override for audit trail
                try:
                    self.env['ops.security.audit'].sudo().log_security_override(
                        model_name=order._name,
                        record_id=order.id,
                        reason='Admin bypass used to confirm Purchase Order without governance checks'
                    )
                except Exception as e:
                    _logger.warning("Failed to log admin override: %s", str(e))
                continue
            
            # Explicitly trigger Governance check for 'on_write' trigger
            # This catches rules like "Purchase orders over $10K require approval"
            order._enforce_governance_rules(order, trigger_type='on_write')
            
            _logger.info("OPS Governance: PO %s passed all governance checks", order.name)
        
        # If we reach here, all governance checks passed
        return super(PurchaseOrder, self).button_confirm()
    
    def action_rfq_send(self):
        """
        Override email sending to enforce governance rules.
        
        This prevents users from sending purchase orders/RFQs by email
        if they violate governance rules or have pending approvals.
        """
        # ADMIN BYPASS: Allow administrators to send anything
        if self.env.su or self.env.user.has_group('base.group_system'):
            # Log admin override for audit trail
            try:
                for order in self:
                    self.env['ops.security.audit'].sudo().log_security_override(
                        model_name=order._name,
                        record_id=order.id,
                        reason='Admin bypass used to send Purchase Order/RFQ without governance checks'
                    )
            except Exception as e:
                _logger.warning("Failed to log admin override: %s", str(e))
            return super().action_rfq_send()
        
        for order in self:
            _logger.info("OPS Governance: Checking PO %s for email commitment", order.name)
            
            # Check for pending approvals
            if hasattr(order, 'approval_request_ids'):
                pending_approvals = order.approval_request_ids.filtered(
                    lambda a: a.state == 'pending'
                )
                
                if pending_approvals:
                    rule_names = ', '.join(pending_approvals.mapped('rule_id.name'))
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s' "
                        "until it satisfies company Governance Rules.\n\n"
                        "⏳ Pending Approval: %s\n\n"
                        "This document is locked for external commitment (email or print) "
                        "until the required approvals are granted."
                    ) % (order.display_name, rule_names))
            
            # Enforce governance rules
            try:
                order._enforce_governance_rules(order, trigger_type='on_write')
                _logger.info("OPS Governance: PO %s passed all governance checks for email", order.name)
            except UserError as e:
                # Re-raise with enhanced message for email context
                error_message = str(e)
                if 'requires approval' in error_message.lower():
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n"
                        "%s\n\n"
                        "External commitment (email/print) is blocked until approval is granted."
                    ) % (order.display_name, error_message))
                else:
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n%s"
                    ) % (order.display_name, error_message))
        
        # If all checks pass, proceed with email wizard
        return super().action_rfq_send()


class PurchaseOrderLine(models.Model):
    """Extend purchase.order.line with Matrix Mixin for dimension propagation."""
    _inherit = ['purchase.order.line', 'ops.matrix.mixin']
    _name = 'purchase.order.line'
    
    # These fields are inherited from ops.matrix.mixin:
    # - ops_branch_id
    # - ops_business_unit_id
    # - ops_company_id
    # - ops_analytic_distribution
    
    def _get_default_ops_branch(self):
        """Get default branch from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['purchase.order'].browse(self._context['default_order_id'])
            if order.ops_branch_id:
                return order.ops_branch_id.id
        return super()._get_default_ops_branch()
    
    def _get_default_ops_business_unit(self):
        """Get default BU from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['purchase.order'].browse(self._context['default_order_id'])
            if order.ops_business_unit_id:
                return order.ops_business_unit_id.id
        return super()._get_default_ops_business_unit()
    
    @api.onchange('order_id')
    def _onchange_order_id_propagate_dimensions(self):
        """
        When order_id changes or is set, inherit the order's matrix dimensions.
        
        This ensures that when a line is added to an order with specific dimensions,
        it automatically gets the correct dimensions.
        """
        if self.order_id:
            # Inherit dimensions from parent order if not already set
            if not self.ops_branch_id and self.order_id.ops_branch_id:
                self.ops_branch_id = self.order_id.ops_branch_id
            if not self.ops_business_unit_id and self.order_id.ops_business_unit_id:
                self.ops_business_unit_id = self.order_id.ops_business_unit_id
