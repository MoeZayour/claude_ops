# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    budget_warning = fields.Text(
        string='Budget Warning',
        compute='_compute_budget_warning',
        store=False,
        help='Warning message if bill exceeds available budget'
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

    def action_post(self):
        """Check budget before posting vendor bills/expenses."""
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
