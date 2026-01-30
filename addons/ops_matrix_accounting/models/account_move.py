# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ==================================================================
    # ASSET MANAGEMENT FIELDS
    # ==================================================================

    asset_id = fields.Many2one(
        'ops.asset',
        string='Related Asset',
        readonly=True,
        copy=False,
        help="Asset this journal entry is related to, created automatically by the asset module."
    )
    asset_depreciation_id = fields.Many2one(
        'ops.asset.depreciation',
        string='Asset Depreciation Line',
        readonly=True,
        copy=False,
        help="The depreciation line that created this entry."
    )

    # ==================================================================
    # BUDGET WARNING FIELDS
    # ==================================================================

    budget_warning = fields.Text(
        string='Budget Warning',
        compute='_compute_budget_warning',
        store=False,
        help='Warning message if bill exceeds available budget'
    )

    # ==================================================================
    # THREE-WAY MATCH FIELDS
    # ==================================================================

    three_way_match_status = fields.Selection([
        ('not_applicable', 'N/A'),
        ('no_po', 'No PO Reference'),
        ('pending_receipt', 'Pending Receipt'),
        ('partial_receipt', 'Partial Receipt'),
        ('partial_match', 'Partial Match'),
        ('fully_matched', 'Fully Matched'),
        ('over_billed', 'Over-Billed'),
        ('exception', 'Exception'),
    ], string='Match Status',
        compute='_compute_three_way_match',
        store=True,
        tracking=True,
        index=True,
        help='Three-way match status: PO ↔ Receipt ↔ Invoice'
    )

    three_way_match_details = fields.Text(
        string='Match Details',
        compute='_compute_three_way_match',
        store=True,
        help='Detailed breakdown of three-way match analysis'
    )

    # Related Documents
    matched_po_ids = fields.Many2many(
        'purchase.order',
        'ops_move_purchase_order_match_rel',
        'move_id',
        'po_id',
        string='Related POs',
        compute='_compute_matched_documents',
        store=True,
        help='Purchase orders linked to this bill'
    )
    matched_po_count = fields.Integer(
        string='PO Count',
        compute='_compute_matched_documents',
        store=True
    )

    matched_picking_ids = fields.Many2many(
        'stock.picking',
        'ops_move_stock_picking_match_rel',
        'move_id',
        'picking_id',
        string='Related Receipts',
        compute='_compute_matched_documents',
        store=True,
        help='Stock receipts (GRN) linked to this bill'
    )
    matched_picking_count = fields.Integer(
        string='Receipt Count',
        compute='_compute_matched_documents',
        store=True
    )

    # Control Settings
    three_way_match_required = fields.Boolean(
        string='3-Way Match Required',
        compute='_compute_three_way_match_required',
        store=True,
        help='Indicates if this bill requires three-way match validation'
    )
    three_way_match_override = fields.Boolean(
        string='Match Override',
        default=False,
        tracking=True,
        copy=False,
        help='Override three-way match requirement (requires approval)'
    )
    three_way_match_override_reason = fields.Text(
        string='Override Reason',
        tracking=True,
        copy=False,
        help='Justification for overriding three-way match requirement'
    )
    three_way_match_override_by = fields.Many2one(
        'res.users',
        string='Override By',
        readonly=True,
        copy=False,
        help='User who approved the match override'
    )
    three_way_match_override_date = fields.Datetime(
        string='Override Date',
        readonly=True,
        copy=False,
        help='Date/time when override was approved'
    )

    @api.depends('amount_total', 'ops_branch_id', 'ops_business_unit_id', 'move_type')
    def _compute_budget_warning(self):
        """Compute budget availability warning for vendor bills."""
        Budget = self.env['ops.budget']
        for move in self:
            move.budget_warning = ''

            # Only check vendor bills
            if move.move_type not in ('in_invoice', 'in_refund'):
                continue

            if not move.ops_branch_id or not move.ops_business_unit_id:
                continue

            if move.amount_total <= 0:
                continue

            result = Budget.check_budget_availability(
                branch_id=move.ops_branch_id.id,
                business_unit_id=move.ops_business_unit_id.id,
                amount=move.amount_total,
                date=move.invoice_date or move.date or fields.Date.today(),
            )

            if not result.get('available', True):
                move.budget_warning = _(
                    "Budget Warning: %(message)s\n"
                    "Budget: %(budget)s\n"
                    "Available: %(remaining).2f\n"
                    "Requested: %(amount).2f"
                ) % {
                    'message': result.get('message', ''),
                    'budget': result.get('budget_name', 'N/A'),
                    'remaining': result.get('remaining', 0),
                    'amount': move.amount_total,
                }

    # ==================================================================
    # THREE-WAY MATCH COMPUTE METHODS
    # ==================================================================

    @api.depends('move_type', 'company_id', 'company_id.three_way_match_required')
    def _compute_three_way_match_required(self):
        """Determine if three-way match is required based on company settings."""
        for move in self:
            if move.move_type != 'in_invoice':
                move.three_way_match_required = False
            else:
                # Check company setting
                move.three_way_match_required = (
                    move.company_id.three_way_match_required or False
                )

    @api.depends(
        'invoice_line_ids.purchase_line_id',
        'invoice_line_ids.purchase_line_id.product_qty',
        'invoice_line_ids.purchase_line_id.qty_received',
        'invoice_line_ids.quantity',
        'invoice_line_ids.display_type',
        'move_type',
        'state'
    )
    def _compute_three_way_match(self):
        """
        Compute three-way match status.

        Three-Way Match = PO ↔ Receipt ↔ Invoice
        - PO: purchase.order.line (product_qty)
        - Receipt: qty_received on PO line (from stock.picking)
        - Invoice: account.move.line quantity
        """
        for move in self:
            # Only for vendor bills
            if move.move_type != 'in_invoice':
                move.three_way_match_status = 'not_applicable'
                move.three_way_match_details = ''
                continue

            # Get invoice lines with PO reference
            lines_with_po = move.invoice_line_ids.filtered(
                lambda l: l.purchase_line_id and l.display_type == 'product'
            )
            product_lines = move.invoice_line_ids.filtered(
                lambda l: l.display_type == 'product'
            )

            # No product lines at all
            if not product_lines:
                move.three_way_match_status = 'not_applicable'
                move.three_way_match_details = _('No product lines on invoice')
                continue

            # No PO reference on any lines
            if not lines_with_po:
                move.three_way_match_status = 'no_po'
                move.three_way_match_details = _(
                    'No purchase order reference found on invoice lines.\n'
                    'This bill is not linked to any PO.'
                )
                continue

            # Analyze each line for match status
            details = []
            total_ordered = 0.0
            total_received = 0.0
            total_billed = 0.0
            has_pending = False
            has_over = False
            has_partial = False

            for line in lines_with_po:
                po_line = line.purchase_line_id
                ordered = po_line.product_qty
                received = po_line.qty_received
                billed = line.quantity

                total_ordered += ordered
                total_received += received
                total_billed += billed

                product_name = line.product_id.display_name or line.name or 'Unknown'

                # Check for over-billing
                if billed > ordered:
                    has_over = True
                    details.append(_(
                        "• %(product)s: OVER-BILLED - Billed %(billed)s > Ordered %(ordered)s"
                    ) % {'product': product_name, 'billed': billed, 'ordered': ordered})
                # Check for pending receipt
                elif received < billed:
                    has_pending = True
                    details.append(_(
                        "• %(product)s: Billed %(billed)s, Received %(received)s, Ordered %(ordered)s"
                    ) % {'product': product_name, 'billed': billed,
                         'received': received, 'ordered': ordered})
                # Check for partial receipt
                elif received < ordered:
                    has_partial = True

            # Determine final status
            if has_over:
                move.three_way_match_status = 'over_billed'
            elif total_received == 0:
                move.three_way_match_status = 'pending_receipt'
            elif has_pending or total_received < total_billed:
                move.three_way_match_status = 'partial_receipt'
            elif has_partial:
                move.three_way_match_status = 'partial_match'
            elif total_billed <= total_received and total_billed <= total_ordered:
                move.three_way_match_status = 'fully_matched'
            else:
                move.three_way_match_status = 'exception'

            # Build details text
            summary = _(
                "Summary: Ordered %(ordered).2f | Received %(received).2f | Billed %(billed).2f"
            ) % {'ordered': total_ordered, 'received': total_received, 'billed': total_billed}

            if details:
                move.three_way_match_details = summary + _('\n\nDiscrepancies:\n') + '\n'.join(details)
            else:
                move.three_way_match_details = summary + _('\n\n✓ All lines fully matched')

    @api.depends(
        'invoice_line_ids.purchase_line_id.order_id',
        'invoice_line_ids.purchase_line_id.move_ids.picking_id',
        'move_type'
    )
    def _compute_matched_documents(self):
        """Compute related POs and receipts (pickings)."""
        for move in self:
            if move.move_type != 'in_invoice':
                move.matched_po_ids = False
                move.matched_po_count = 0
                move.matched_picking_ids = False
                move.matched_picking_count = 0
                continue

            # Get PO lines from invoice lines
            po_lines = move.invoice_line_ids.mapped('purchase_line_id')

            # Get unique POs
            pos = po_lines.mapped('order_id')
            move.matched_po_ids = pos
            move.matched_po_count = len(pos)

            # Get Receipts (pickings) - only done pickings
            pickings = po_lines.mapped('move_ids.picking_id').filtered(
                lambda p: p.state == 'done'
            )
            move.matched_picking_ids = pickings
            move.matched_picking_count = len(pickings)

    # ==================================================================
    # THREE-WAY MATCH ACTION METHODS
    # ==================================================================

    def action_request_match_override(self):
        """Request three-way match override - creates activity for AP manager."""
        self.ensure_one()

        # Find AP manager group users
        manager_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
        if manager_group and manager_group.users:
            # Prefer a user from the same company
            target_user = manager_group.users.filtered(
                lambda u: self.company_id in u.company_ids
            )[:1] or manager_group.users[:1]
        else:
            target_user = self.env.user

        # Schedule activity
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Three-Way Match Override Request'),
            note=_(
                '<strong>Override requested for vendor bill:</strong> %(bill)s<br/><br/>'
                '<strong>Vendor:</strong> %(vendor)s<br/>'
                '<strong>Amount:</strong> %(amount)s %(currency)s<br/>'
                '<strong>Match Status:</strong> %(status)s<br/><br/>'
                '<strong>Details:</strong><br/><pre>%(details)s</pre>'
            ) % {
                'bill': self.name or _('Draft'),
                'vendor': self.partner_id.name or _('Unknown'),
                'amount': self.amount_total,
                'currency': self.currency_id.name,
                'status': dict(self._fields['three_way_match_status'].selection).get(
                    self.three_way_match_status, self.three_way_match_status
                ),
                'details': self.three_way_match_details or _('N/A'),
            },
            user_id=target_user.id,
        )

        # Log in chatter
        self.message_post(
            body=_(
                '📋 Three-way match override requested.<br/>'
                'Assigned to: %s<br/>'
                'Awaiting approval...'
            ) % target_user.name,
            message_type='notification'
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Override Requested'),
                'message': _('Approval activity created for %s.') % target_user.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_approve_match_override(self):
        """Open wizard to approve three-way match override."""
        self.ensure_one()
        return {
            'name': _('Approve Match Override'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.three.way.match.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
            }
        }

    def action_view_matched_pos(self):
        """View related purchase orders."""
        self.ensure_one()
        action = {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.matched_po_ids.ids)],
            'context': {'create': False},
        }
        if len(self.matched_po_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.matched_po_ids.id
        return action

    def action_view_matched_receipts(self):
        """View related receipts (stock pickings)."""
        self.ensure_one()
        action = {
            'name': _('Receipts'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.matched_picking_ids.ids)],
            'context': {'create': False},
        }
        if len(self.matched_picking_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.matched_picking_ids.id
        return action

    # ==================================================================
    # POSTING VALIDATION
    # ==================================================================

    def action_post(self):
        """Check period lock, three-way match, and budget before posting."""
        # 1. Check period locks first
        self._check_period_lock()

        # 2. Check three-way match for vendor bills
        self._check_three_way_match()

        # 3. Then check budgets
        Budget = self.env['ops.budget']

        for move in self:
            # Only check vendor bills
            if move.move_type not in ('in_invoice', 'in_refund'):
                continue

            if not move.ops_branch_id or not move.ops_business_unit_id:
                continue

            result = Budget.check_budget_availability(
                branch_id=move.ops_branch_id.id,
                business_unit_id=move.ops_business_unit_id.id,
                amount=move.amount_total,
                date=move.invoice_date or move.date or fields.Date.today(),
            )

            if not result.get('available', True):
                raise ValidationError(_(
                    "Cannot post: Budget exceeded for %(branch)s / %(bu)s.\n\n"
                    "Budget: %(budget)s\n"
                    "Available: %(available).2f\n"
                    "Required: %(amount).2f\n"
                    "Over by: %(over).2f\n\n"
                    "Please request a budget increase or split the expense."
                ) % {
                    'branch': move.ops_branch_id.name,
                    'bu': move.ops_business_unit_id.name,
                    'budget': result.get('budget_name', 'N/A'),
                    'available': result.get('remaining', 0),
                    'amount': move.amount_total,
                    'over': result.get('over_amount', 0),
                })

        return super().action_post()

    def _check_three_way_match(self):
        """Check three-way match validation before posting vendor bills.

        Raises:
            ValidationError: If three-way match is required and not satisfied
        """
        for move in self:
            # Only check vendor bills
            if move.move_type != 'in_invoice':
                continue

            # Skip if three-way match not required for this company
            if not move.three_way_match_required:
                continue

            # Check if override was approved
            if move.three_way_match_override:
                # Log override usage
                move.message_post(
                    body=_(
                        '⚠️ <strong>Three-way match override used</strong><br/>'
                        '<strong>Reason:</strong> %(reason)s<br/>'
                        '<strong>Approved by:</strong> %(approver)s<br/>'
                        '<strong>Approved on:</strong> %(date)s'
                    ) % {
                        'reason': move.three_way_match_override_reason or _('Not specified'),
                        'approver': move.three_way_match_override_by.name if move.three_way_match_override_by else _('Unknown'),
                        'date': move.three_way_match_override_date.strftime('%Y-%m-%d %H:%M') if move.three_way_match_override_date else _('N/A'),
                    },
                    message_type='notification'
                )
                continue

            # Block posting for problematic statuses
            blocking_statuses = ('no_po', 'pending_receipt', 'over_billed')
            if move.three_way_match_status in blocking_statuses:
                status_label = dict(move._fields['three_way_match_status'].selection).get(
                    move.three_way_match_status, move.three_way_match_status
                )
                raise ValidationError(_(
                    "Cannot post vendor bill - Three-Way Match validation failed.\n\n"
                    "Bill: %(bill)s\n"
                    "Status: %(status)s\n\n"
                    "Details:\n%(details)s\n\n"
                    "Options:\n"
                    "• Wait for goods receipt to be completed\n"
                    "• Request match override from AP manager\n"
                    "• Correct the invoice quantities to match received goods"
                ) % {
                    'bill': move.name or _('Draft'),
                    'status': status_label,
                    'details': move.three_way_match_details or _('N/A'),
                })

            # Log warning for partial matches (don't block)
            elif move.three_way_match_status in ('partial_receipt', 'partial_match'):
                _logger.warning(
                    'Posting vendor bill with partial three-way match: %s (status: %s)',
                    move.name, move.three_way_match_status
                )
                move.message_post(
                    body=_(
                        '⚠️ <strong>Partial receipt warning</strong> - not all ordered items '
                        'have been received.<br/><br/>%(details)s'
                    ) % {'details': (move.three_way_match_details or '').replace('\n', '<br/>')},
                    message_type='notification'
                )

    def _check_period_lock(self):
        """Check if posting is blocked by period lock.

        Raises:
            ValidationError: If period is hard-locked
        """
        Period = self.env['ops.fiscal.period']

        for move in self:
            # Find applicable period for this move's date
            period = Period.get_period_for_date(
                move.date,
                move.company_id.id
            )

            if not period:
                # No period defined - allow posting
                continue

            # Check company-level lock first
            if period.lock_state == 'hard_lock':
                lock_info = ""
                if period.locked_by and period.locked_date:
                    lock_info = _('\nLocked by: %s on %s') % (
                        period.locked_by.name,
                        period.locked_date.strftime('%Y-%m-%d %H:%M')
                    )
                raise ValidationError(_(
                    'Cannot post to period "%s" - it is hard locked.%s\n\n'
                    'Please contact your accounting manager to unlock the period.'
                ) % (period.name, lock_info))

            elif period.lock_state == 'soft_lock':
                # Log warning but allow posting
                _logger.warning(
                    'Posting to soft-locked period %s: %s (user: %s)',
                    period.name, move.name, self.env.user.name
                )
                move.message_post(
                    body=_(
                        '<strong>Warning:</strong> Posted to soft-locked period "%s".<br/>'
                        'This period is in soft-lock status. Please verify this posting is correct.'
                    ) % period.name,
                    message_type='notification'
                )

            # Check branch-level lock if applicable
            if hasattr(move, 'ops_branch_id') and move.ops_branch_id:
                branch_lock = period.branch_lock_ids.filtered(
                    lambda l: l.ops_branch_id == move.ops_branch_id
                )
                if branch_lock and branch_lock.lock_state == 'hard_lock':
                    lock_info = ""
                    if branch_lock.locked_by and branch_lock.locked_date:
                        lock_info = _('\nLocked by: %s on %s') % (
                            branch_lock.locked_by.name,
                            branch_lock.locked_date.strftime('%Y-%m-%d %H:%M')
                        )
                    raise ValidationError(_(
                        'Cannot post to period "%s" - branch "%s" is hard locked.%s'
                    ) % (period.name, move.ops_branch_id.name, lock_info))

                elif branch_lock and branch_lock.lock_state == 'soft_lock':
                    _logger.warning(
                        'Posting to soft-locked branch %s in period %s: %s',
                        move.ops_branch_id.name, period.name, move.name
                    )
                    move.message_post(
                        body=_(
                            '<strong>Warning:</strong> Posted to soft-locked branch "%s" '
                            'in period "%s".'
                        ) % (move.ops_branch_id.name, period.name),
                        message_type='notification'
                    )

    def button_cancel(self):
        # Override to prevent cancellation of asset-related moves
        for move in self:
            if move.asset_id and not self.env.context.get('force_cancel'):
                raise models.UserError(
                    "You cannot cancel a journal entry related to a fixed asset. "
                    "Please use the asset's functionality to reverse or manage it."
                )
        return super(AccountMove, self).button_cancel()

    def unlink(self):
        # Override to prevent deletion of asset-related moves
        for move in self:
            if move.asset_id and not self.env.context.get('force_delete'):
                 raise models.UserError(
                    "You cannot delete a journal entry related to a fixed asset. "
                    "Please use the asset's functionality to manage it."
                )
        return super(AccountMove, self).unlink()
