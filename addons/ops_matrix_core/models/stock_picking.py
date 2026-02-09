from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from typing import List, Dict, Any
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'ops.matrix.mixin', 'ops.approval.mixin']
    _name = 'stock.picking'

    # ==========================================================================
    # CREDIT ENFORCEMENT FIELDS
    # ==========================================================================
    ops_credit_blocked = fields.Boolean(
        string='Credit Blocked',
        default=False,
        copy=False,
        help='Indicates this delivery is blocked due to credit limit violation'
    )
    ops_credit_block_reason = fields.Text(
        string='Credit Block Reason',
        readonly=True,
        copy=False,
        help='Reason for credit block on this delivery'
    )
    ops_credit_approval_id = fields.Many2one(
        'ops.approval.request',
        string='Credit Approval',
        copy=False,
        help='Approval request for credit limit override'
    )

    # Note: branch fields now come from ops.matrix.mixin as ops_branch_id and ops_business_unit_id
    # Keeping legacy fields for backward compatibility
    branch_id = fields.Many2one(
        'res.company',
        string='Branch (Legacy)',
        compute='_compute_legacy_branch_id',
        store=True,
        readonly=False, # Allow direct write for legacy/import cases
        inverse='_inverse_legacy_branch_id'
    )

    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit (Legacy)',
        related='ops_business_unit_id',
        store=True
    )

    @api.depends('ops_branch_id')
    def _compute_legacy_branch_id(self):
        for picking in self:
            picking.branch_id = picking.ops_branch_id.company_id if picking.ops_branch_id else False

    def _inverse_legacy_branch_id(self):
        for picking in self:
            if picking.branch_id and not picking.ops_branch_id:
                # Find the first ops.branch for this company and assign it
                branch = self.env['ops.branch'].search([('company_id', '=', picking.branch_id.id)], limit=1)
                if branch:
                    picking.ops_branch_id = branch

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'StockPicking':
        """Override to set ops_branch_id from user context if not provided."""
        for vals in vals_list:
            # Set ops_branch_id from user's primary branch if not provided
            if not vals.get('ops_branch_id') and self.env.user.primary_branch_id:
                vals['ops_branch_id'] = self.env.user.primary_branch_id.id
        return super().create(vals_list)

    def _check_partner_credit_limit(self):
        """
        HARD BLOCK: Check partner credit limit before allowing delivery.

        This is the enforcement point for credit limits - SO confirmation only warns,
        but actual delivery (stock.picking validation) is blocked if over credit.

        Returns:
            tuple: (can_proceed: bool, message: str)
        """
        self.ensure_one()

        # Admin bypass
        if self.env.is_superuser() or self.env.user.has_group('base.group_system'):
            return True, 'Admin bypass'

        # Only check outgoing deliveries (customer deliveries)
        if self.picking_type_id.code != 'outgoing':
            return True, 'Not an outgoing delivery'

        partner = self.partner_id
        if not partner:
            return True, 'No partner on picking'

        # Check if there's an approved credit override
        if self.ops_credit_approval_id and self.ops_credit_approval_id.state == 'approved':
            return True, 'Credit override approved'

        # Calculate picking value from sale order if linked
        picking_value = 0.0
        if self.sale_id:
            picking_value = self.sale_id.amount_total
        else:
            # Estimate value from move lines
            for move in self.move_ids:
                if move.product_id and move.product_uom_qty:
                    picking_value += move.product_id.list_price * move.product_uom_qty

        # Check credit limit
        if hasattr(partner, 'ops_credit_limit') and hasattr(partner, 'ops_total_outstanding'):
            if partner.ops_credit_limit > 0:
                total_outstanding = partner.ops_total_outstanding
                potential_total = total_outstanding + picking_value

                if potential_total > partner.ops_credit_limit:
                    return False, (
                        f"CREDIT LIMIT EXCEEDED - Delivery Blocked!\n\n"
                        f"Partner: {partner.name}\n"
                        f"Credit Limit: {partner.ops_credit_limit:.2f}\n"
                        f"Current Outstanding: {total_outstanding:.2f}\n"
                        f"This Delivery Value: {picking_value:.2f}\n"
                        f"Total If Delivered: {potential_total:.2f}\n"
                        f"Over Limit By: {potential_total - partner.ops_credit_limit:.2f}\n\n"
                        f"Action Required: Collect payment or request credit override approval."
                    )

        # Also check partner state
        if hasattr(partner, 'ops_state'):
            if partner.ops_state == 'blocked':
                return False, f"Partner '{partner.name}' is blocked from transactions."
            if partner.ops_state == 'archived':
                return False, f"Partner '{partner.name}' is archived."

        return True, 'Credit check passed'

    def action_request_credit_override(self):
        """
        Request approval to override credit limit block on this delivery.
        Creates an approval request and links it to this picking.
        """
        self.ensure_one()

        if not self.ops_credit_blocked:
            raise UserError(_("This delivery is not credit blocked."))

        # Check for existing pending approval
        if self.ops_credit_approval_id and self.ops_credit_approval_id.state == 'pending':
            raise UserError(_(
                "An approval request is already pending for this delivery.\n"
                "Please wait for approval or cancel the existing request."
            ))

        # Find approvers (Finance Manager or CFO groups)
        approvers = self.env['res.users']

        # Try Finance Manager group first
        try:
            finance_group = self.env.ref('ops_matrix_core.group_ops_finance_manager', raise_if_not_found=False)
            if finance_group:
                group_data = finance_group.read(['users'])[0] if finance_group else {}
                user_ids = group_data.get('users', [])
                if user_ids:
                    approvers = self.env['res.users'].browse(user_ids).filtered(lambda u: u.active)[:5]
        except Exception:
            _logger.debug('Failed to resolve approvers from Finance Manager group', exc_info=True)

        # Fallback to CFO group
        if not approvers:
            try:
                cfo_group = self.env.ref('ops_matrix_core.group_ops_cfo', raise_if_not_found=False)
                if cfo_group:
                    group_data = cfo_group.read(['users'])[0] if cfo_group else {}
                    user_ids = group_data.get('users', [])
                    if user_ids:
                        approvers = self.env['res.users'].browse(user_ids).filtered(lambda u: u.active)[:5]
            except Exception:
                _logger.debug('Failed to resolve approvers from CFO group', exc_info=True)

        # Final fallback to admin
        if not approvers:
            admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
            if admin_user and admin_user.active:
                approvers = admin_user

        if not approvers:
            raise UserError(_("No approvers found for credit override. Please configure Finance Manager or CFO users."))

        # Create approval request
        approval = self.env['ops.approval.request'].create({
            'name': _("Credit Override: %s") % self.name,
            'model_name': 'stock.picking',
            'res_id': self.id,
            'notes': self.ops_credit_block_reason or _("Credit limit override requested for delivery"),
            'approver_ids': [(6, 0, approvers.ids)],
            'requested_by': self.env.user.id,
        })

        self.write({
            'ops_credit_approval_id': approval.id,
        })

        # Post to chatter
        if hasattr(self, 'message_post'):
            self.message_post(
                body=_(
                    "<strong>Credit Override Requested</strong><br/>"
                    "Approval request created: %s<br/>"
                    "Approvers: %s"
                ) % (approval.name, ', '.join(approvers.mapped('name'))),
                subject=_("Credit Override Request"),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

        _logger.info(
            "Credit override requested for picking %s by user %s",
            self.name, self.env.user.name
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Credit Override Requested'),
                'message': _('Approval request sent to: %s') % ', '.join(approvers.mapped('name')),
                'type': 'success',
                'sticky': False,
            }
        }

    def button_validate(self) -> bool:
        """
        Override button_validate to enforce:
        1. Credit limit check (HARD BLOCK for outgoing deliveries)
        2. Strict inventory check (prevent negative stock)
        """
        for picking in self:
            # =================================================================
            # CREDIT LIMIT ENFORCEMENT (HARD BLOCK)
            # =================================================================
            if picking.picking_type_id.code == 'outgoing':
                can_proceed, credit_message = picking._check_partner_credit_limit()

                if not can_proceed:
                    # Block the delivery and mark it
                    picking.write({
                        'ops_credit_blocked': True,
                        'ops_credit_block_reason': credit_message,
                    })

                    # Log the block
                    _logger.warning(
                        "Credit BLOCK on picking %s: %s",
                        picking.name, credit_message
                    )

                    # Post to chatter
                    if hasattr(picking, 'message_post'):
                        picking.message_post(
                            body=_(
                                "<strong>🚫 Delivery BLOCKED - Credit Limit Exceeded</strong><br/><br/>"
                                "%s<br/><br/>"
                                "<em>Use 'Request Credit Override' button to request approval.</em>"
                            ) % credit_message.replace('\n', '<br/>'),
                            subject=_("Delivery Blocked - Credit Limit"),
                            message_type='notification',
                            subtype_xmlid='mail.mt_note',
                        )

                    raise UserError(_(
                        "🚫 DELIVERY BLOCKED - CREDIT LIMIT EXCEEDED\n\n%s"
                    ) % credit_message)

                # Clear any previous block if credit is now OK
                if picking.ops_credit_blocked:
                    picking.write({
                        'ops_credit_blocked': False,
                        'ops_credit_block_reason': False,
                    })

            # =================================================================
            # STRICT INVENTORY ENFORCEMENT
            # =================================================================
            if picking.picking_type_id.code == 'outgoing':
                # Check each move for stock availability
                for move in picking.move_ids:
                    # Skip if product is consumable or service type
                    if move.product_id.type in ['consu', 'service']:
                        continue

                    # Get available quantity at source location
                    available_qty = move.product_id.with_context(
                        location=move.location_id.id
                    ).qty_available

                    # Check if move would cause negative stock
                    if available_qty < move.product_uom_qty:
                        raise ValidationError(
                            f"Cannot validate delivery. Product '{move.product_id.display_name}' "
                            f"has insufficient stock in '{move.location_id.display_name}'. "
                            f"Available: {available_qty:.2f}, Required: {move.product_uom_qty:.2f}. "
                            f"You cannot drive stock into negative."
                        )

        return super().button_validate()
