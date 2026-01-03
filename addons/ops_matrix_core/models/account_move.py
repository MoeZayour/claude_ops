from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = ['account.move', 'ops.matrix.mixin', 'ops.approval.mixin']
    _name = 'account.move'
    
    # The following fields are inherited from ops.matrix.mixin:
    # - ops_branch_id (Many2one to ops.branch)
    # - ops_business_unit_id (Many2one to ops.business.unit)
    # - ops_persona_id (Many2one to ops.persona)
    # - ops_company_id (computed Many2one to res.company)
    # - ops_analytic_distribution (computed Json field)
    
    # ========================================================================
    # ADDITIONAL FIELDS
    # ========================================================================
    
    ops_source_order_id = fields.Reference(
        [('sale.order', 'Sale Order'), ('purchase.order', 'Purchase Order')],
        string='Source Order',
        help='Original order that generated this invoice/bill',
        readonly=True
    )
    
    ops_analytic_summary = fields.Char(
        compute='_compute_analytic_summary',
        string='Analytic Summary',
        store=True,
        help='Summary of Branch and Business Unit dimensions'
    )
    
    # Anti-Fraud Security: Button-level authority for invoice posting
    can_user_validate_invoices = fields.Boolean(
        compute='_compute_can_user_validate_invoices',
        string='Can Validate Invoices',
        help='Technical field: User has authority to post/validate invoices'
    )
    
    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================
    
    @api.depends_context('uid')
    def _compute_can_user_validate_invoices(self):
        """
        Check if current user has authority to validate invoices.
        
        ADMIN BYPASS: System administrators always have access.
        PERSONA LOGIC: Uses additive authority - if ANY persona grants the right, access is granted.
        """
        for record in self:
            # Admin bypass
            if self.env.su or self.env.user.has_group('base.group_system'):
                record.can_user_validate_invoices = True
            else:
                # Check persona authority using the helper method
                record.can_user_validate_invoices = self.env.user.has_ops_authority('can_validate_invoices')
    
    @api.depends('ops_branch_id', 'ops_business_unit_id')
    def _compute_analytic_summary(self):
        """Compute human-readable summary of matrix dimensions."""
        for move in self:
            parts = []
            if move.ops_branch_id:
                branch_code = move.ops_branch_id.code if hasattr(move.ops_branch_id, 'code') else move.ops_branch_id.name
                parts.append(_("Branch: %s") % branch_code)
            if move.ops_business_unit_id:
                bu_code = move.ops_business_unit_id.code if hasattr(move.ops_business_unit_id, 'code') else move.ops_business_unit_id.name
                parts.append(_("BU: %s") % bu_code)
            
            move.ops_analytic_summary = " | ".join(parts) if parts else _("No dimensions")
    
    # ========================================================================
    # CRUD METHODS
    # ========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign analytic distribution from matrix dimensions when creating moves."""
        # First, propagate dimensions from source orders
        for vals in vals_list:
            self._propagate_matrix_dimensions(vals)
        
        # Create the records
        moves = super().create(vals_list)
        
        # Then update analytic distribution for each move
        for move in moves:
            # Only update if we have branch or BU (may have been set via defaults)
            if move.ops_branch_id or move.ops_business_unit_id:
                # Compute distribution based on current values
                distribution = move._compute_analytic_distribution_values()
                
                # Apply to all move lines
                if distribution and move.line_ids:
                    for line in move.line_ids:
                        # Only update if line doesn't already have analytic distribution
                        if not line.analytic_distribution:
                            line.analytic_distribution = distribution
        
        return moves
    
    def write(self, vals):
        """Update analytic distribution when matrix dimensions change."""
        # Capture old values for branch and BU before write
        old_branch_values = {move.id: move.ops_branch_id for move in self}
        old_bu_values = {move.id: move.ops_business_unit_id for move in self}
        
        # Perform the write
        result = super().write(vals)
        
        # Check if we need to update analytic distribution
        update_moves = self.filtered(lambda m: (
            (m.id in old_branch_values and m.ops_branch_id != old_branch_values[m.id]) or
            (m.id in old_bu_values and m.ops_business_unit_id != old_bu_values[m.id])
        ))
        
        if update_moves:
            for move in update_moves:
                # Only update draft or posted moves (based on business rules)
                if move.state in ('draft', 'posted'):
                    distribution = move._compute_analytic_distribution_values()
                    
                    if distribution:
                        # Update lines that don't have manual analytic assignments
                        for line in move.line_ids.filtered(lambda l: not l.analytic_distribution):
                            line.analytic_distribution = distribution
                    
                    # Log the change for audit trail
                    move.message_post(
                        body=_('Matrix dimensions updated: Branch=%s, BU=%s') % (
                            move.ops_branch_id.name if move.ops_branch_id else 'None',
                            move.ops_business_unit_id.name if move.ops_business_unit_id else 'None'
                        )
                    )
        
        return result
    
    # ========================================================================
    # ONCHANGE METHODS
    # ========================================================================
    
    @api.onchange('ops_branch_id')
    def _onchange_ops_branch_id(self):
        """Filter available BUs when branch changes and update analytic distribution."""
        if self.ops_branch_id:
            # Filter available BUs
            available_bus = self.env['ops.business.unit'].search([
                ('branch_ids', 'in', self.ops_branch_id.id),
                ('active', '=', True)
            ])
            
            # Reset BU if incompatible
            if self.ops_business_unit_id and self.ops_business_unit_id not in available_bus:
                self.ops_business_unit_id = False
            
            # Update analytic distribution on lines
            if self.line_ids:
                distribution = self._compute_analytic_distribution_values()
                for line in self.line_ids.filtered(lambda l: not l.analytic_distribution):
                    line.analytic_distribution = distribution
            
            return {
                'domain': {
                    'ops_business_unit_id': [('id', 'in', available_bus.ids)]
                }
            }
        return {}
    
    @api.onchange('ops_business_unit_id')
    def _onchange_ops_business_unit_id(self):
        """Update analytic distribution when BU changes."""
        if self.line_ids:
            distribution = self._compute_analytic_distribution_values()
            for line in self.line_ids.filtered(lambda l: not l.analytic_distribution):
                line.analytic_distribution = distribution
    
    # ========================================================================
    # VALIDATION CONSTRAINTS
    # ========================================================================
    
    @api.constrains('ops_branch_id', 'ops_business_unit_id')
    def _check_matrix_dimensions(self):
        """Ensure required dimensions are present for invoices."""
        for move in self:
            # Only validate for invoice types
            if move.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                if not move.ops_branch_id:
                    raise ValidationError(_(
                        "Branch is required for %s '%s'. Please select a branch before confirming."
                    ) % (move.move_type, move.name))
                
                if not move.ops_business_unit_id:
                    raise ValidationError(_(
                        "Business Unit is required for %s '%s'. Please select a business unit before confirming."
                    ) % (move.move_type, move.name))
                
                # Also validate that BU operates in the selected branch (only when model matches)
                bu_branches = move.ops_business_unit_id.branch_ids
                if (move.ops_branch_id and move.ops_business_unit_id and bu_branches and
                        bu_branches._name == move.ops_branch_id._name and
                        move.ops_branch_id not in bu_branches):
                    raise ValidationError(_(
                        "Business Unit '%(bu_name)s' does not operate in Branch '%(branch_name)s'. "
                        "Please select a compatible combination."
                    ) % {
                        'bu_name': move.ops_business_unit_id.name,
                        'branch_name': move.ops_branch_id.name
                    })
    
    # ========================================================================
    # ACTION METHODS
    # ========================================================================
    
    def action_post(self):
        """Override post action to validate matrix dimensions before posting."""
        # Validate dimensions for invoices
        invoice_moves = self.filtered(lambda m: m.is_invoice(include_receipts=True))
        for move in invoice_moves:
            if not move.ops_branch_id:
                raise ValidationError(_(
                    "Cannot post invoice %s without a Branch. Please select a branch."
                ) % move.name)
            
            if not move.ops_business_unit_id:
                raise ValidationError(_(
                    "Cannot post invoice %s without a Business Unit. Please select a business unit."
                ) % move.name)
        
        # Ensure analytic distribution is set on lines
        for move in self:
            if move.ops_branch_id or move.ops_business_unit_id:
                distribution = move._compute_analytic_distribution_values()
                if distribution:
                    for line in move.line_ids.filtered(lambda l: not l.analytic_distribution):
                        line.analytic_distribution = distribution
        
        return super().action_post()
    
    def action_recompute_analytic_distribution(self):
        """Manual action to recompute analytic distribution for selected moves."""
        for move in self:
            distribution = move._compute_analytic_distribution_values()
            if distribution:
                for line in move.line_ids:
                    line.analytic_distribution = distribution
                
                move.message_post(
                    body=_('Analytic distribution recomputed for all lines.')
                )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Analytic Distribution Updated'),
                'message': _('Analytic distribution has been recomputed for %d moves.') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _compute_analytic_distribution_values(self):
        """
        Compute analytic distribution values for this move using dynamic configuration.
        Weights are retrieved from ops.matrix.config instead of hardcoded values.
        """
        self.ensure_one()
        
        # Get configuration
        config = self.env['ops.matrix.config'].get_config(
            company_id=self.company_id.id if self.company_id else None
        )
        
        # Extract analytic account IDs
        branch_account_id = None
        bu_account_id = None
        
        if self.ops_branch_id:
            if hasattr(self.ops_branch_id, 'analytic_account_id') and self.ops_branch_id.analytic_account_id:
                branch_account_id = self.ops_branch_id.analytic_account_id.id
            elif hasattr(self.ops_branch_id, 'ops_analytic_account_id') and self.ops_branch_id.ops_analytic_account_id:
                branch_account_id = self.ops_branch_id.ops_analytic_account_id.id
        
        if self.ops_business_unit_id and self.ops_business_unit_id.analytic_account_id:
            bu_account_id = self.ops_business_unit_id.analytic_account_id.id
        
        # Use config to calculate distribution
        return config.get_analytic_distribution(
            branch_id=branch_account_id,
            bu_id=bu_account_id
        )
    
    def _propagate_matrix_dimensions(self, vals):
        """
        Propagate matrix dimensions from source order to invoice/bill.
        
        This method examines the context or related orders to extract
        ops_branch_id and ops_business_unit_id and populate them in vals.
        
        :param vals: Dictionary of values being created
        """
        # Check if dimensions already explicitly set
        if vals.get('ops_branch_id') or vals.get('ops_business_unit_id'):
            return
        
        # Try to find source order from invoice_origin or context
        invoice_origin = vals.get('invoice_origin')
        source_order = None
        
        if invoice_origin:
            # Parse invoice_origin (e.g., "SO0001234" or "PO0001234")
            source_order = self._find_source_order(invoice_origin)
        
        # If source order found, extract dimensions
        if source_order:
            if hasattr(source_order, 'ops_branch_id') and source_order.ops_branch_id:
                vals['ops_branch_id'] = source_order.ops_branch_id.id
            if hasattr(source_order, 'ops_business_unit_id') and source_order.ops_business_unit_id:
                vals['ops_business_unit_id'] = source_order.ops_business_unit_id.id
            vals['ops_source_order_id'] = f"{source_order._name},{source_order.id}"
    
    def _find_source_order(self, origin_reference):
        """
        Find the source order (SaleOrder or PurchaseOrder) by origin reference.
        
        :param origin_reference: String like "SO0001234" or "PO0001234"
        :return: RecordSet of order or None
        """
        if not origin_reference:
            return None
        
        # Try to find sale order
        sale_order = self.env['sale.order'].search([
            '|',
            ('name', '=', origin_reference),
            ('name', '=', origin_reference.replace('SO', '').lstrip('0') or origin_reference)
        ], limit=1)
        
        if sale_order:
            return sale_order
        
        # Try to find purchase order
        purchase_order = self.env['purchase.order'].search([
            '|',
            ('name', '=', origin_reference),
            ('name', '=', origin_reference.replace('PO', '').lstrip('0') or origin_reference)
        ], limit=1)
        
        return purchase_order if purchase_order else None
    
    def action_invoice_sent(self):
        """
        Override email sending to enforce governance rules.
        
        This prevents users from sending invoices by email
        if they violate governance rules or have pending approvals.
        """
        # ADMIN BYPASS: Allow administrators to send anything
        if self.env.su or self.env.user.has_group('base.group_system'):
            # Log admin override for audit trail
            try:
                for move in self:
                    if move.is_invoice(include_receipts=True):
                        self.env['ops.security.audit'].sudo().log_security_override(
                            model_name=move._name,
                            record_id=move.id,
                            reason='Admin bypass used to send Invoice/Bill without governance checks'
                        )
            except Exception as e:
                _logger.warning("Failed to log admin override: %s", str(e))
            return super().action_invoice_sent()
        
        for move in self:
            # Only enforce for invoices and bills
            if move.is_invoice(include_receipts=True):
                _logger.info("OPS Governance: Checking invoice %s for email commitment", move.name)
                
                # Check for pending approvals (if governance mixin is applied)
                if hasattr(move, 'approval_request_ids'):
                    pending_approvals = move.approval_request_ids.filtered(
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
                        ) % (move.display_name, rule_names))
                
                # Enforce governance rules (if mixin is applied)
                if hasattr(move, '_enforce_governance_rules'):
                    try:
                        move._enforce_governance_rules(move, trigger_type='on_write')
                        _logger.info("OPS Governance: Invoice %s passed all governance checks for email", move.name)
                    except UserError as e:
                        # Re-raise with enhanced message for email context
                        error_message = str(e)
                        if 'requires approval' in error_message.lower():
                            raise UserError(_(
                                "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n"
                                "%s\n\n"
                                "External commitment (email/print) is blocked until approval is granted."
                            ) % (move.display_name, error_message))
                        else:
                            raise UserError(_(
                                "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n%s"
                            ) % (move.display_name, error_message))
        
        # If all checks pass, proceed with email wizard
        return super().action_invoice_sent()


class AccountMoveLine(models.Model):
    _inherit = ['account.move.line', 'ops.matrix.mixin']
    _name = 'account.move.line'
    
    # These fields are inherited from ops.matrix.mixin:
    # - ops_branch_id
    # - ops_business_unit_id
    # - ops_company_id
    # - ops_analytic_distribution
    
    # ========================================================================
    # DEFAULT METHODS
    # ========================================================================
    
    def _get_default_ops_branch(self):
        """Get default branch from parent move if available."""
        if self._context.get('default_move_id'):
            move = self.env['account.move'].browse(self._context['default_move_id'])
            if move.ops_branch_id:
                return move.ops_branch_id.id
        return super()._get_default_ops_branch()
    
    def _get_default_ops_business_unit(self):
        """Get default BU from parent move if available."""
        if self._context.get('default_move_id'):
            move = self.env['account.move'].browse(self._context['default_move_id'])
            if move.ops_business_unit_id:
                return move.ops_business_unit_id.id
        return super()._get_default_ops_business_unit()
    
    # ========================================================================
    # ONCHANGE METHODS
    # ========================================================================
    
    @api.onchange('ops_branch_id', 'ops_business_unit_id')
    def _onchange_matrix_dimensions(self):
        """Update analytic distribution when matrix dimensions change on line."""
        distribution = self._compute_analytic_distribution_values()
        if distribution:
            self.analytic_distribution = distribution
        elif self.analytic_distribution:
            # Clear if no dimensions
            self.analytic_distribution = False
    
    @api.onchange('move_id')
    def _onchange_move_id_propagate_dimensions(self):
        """
        When move_id changes or is set, inherit the move's matrix dimensions.
        
        This ensures that when a line is added to a move with specific dimensions,
        it automatically gets the correct dimensions.
        """
        if self.move_id:
            # Inherit dimensions from parent move if not already set
            if not self.ops_branch_id and self.move_id.ops_branch_id:
                self.ops_branch_id = self.move_id.ops_branch_id
            if not self.ops_business_unit_id and self.move_id.ops_business_unit_id:
                self.ops_business_unit_id = self.move_id.ops_business_unit_id
            
            # Update analytic distribution
            distribution = self._compute_analytic_distribution_values()
            if distribution:
                self.analytic_distribution = distribution
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _compute_analytic_distribution_values(self):
        """
        Compute analytic distribution for this line using dynamic configuration.
        Weights are retrieved from ops.matrix.config instead of hardcoded values.
        """
        self.ensure_one()
        
        # Get configuration
        company_id = self.company_id.id if self.company_id else (
            self.move_id.company_id.id if self.move_id and self.move_id.company_id else None
        )
        config = self.env['ops.matrix.config'].get_config(company_id=company_id)
        
        # Check if line has its own dimensions, otherwise use move's dimensions
        branch = self.ops_branch_id or (self.move_id.ops_branch_id if self.move_id else False)
        bu = self.ops_business_unit_id or (self.move_id.ops_business_unit_id if self.move_id else False)
        
        # Extract analytic account IDs
        branch_account_id = None
        bu_account_id = None
        
        if branch:
            if hasattr(branch, 'analytic_account_id') and branch.analytic_account_id:
                branch_account_id = branch.analytic_account_id.id
            elif hasattr(branch, 'ops_analytic_account_id') and branch.ops_analytic_account_id:
                branch_account_id = branch.ops_analytic_account_id.id
        
        if bu and bu.analytic_account_id:
            bu_account_id = bu.analytic_account_id.id
        
        # Use config to calculate distribution
        return config.get_analytic_distribution(
            branch_id=branch_account_id,
            bu_id=bu_account_id
        )
