# -*- coding: utf-8 -*-
"""
Purchase Order Budget Control Integration
Enforces budget checks when creating or confirming purchase orders.
"""
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    budget_warning = fields.Text(
        string='Budget Warning',
        compute='_compute_budget_warning',
        store=False,
        help='Warning message if purchase exceeds available budget'
    )

    budget_available = fields.Boolean(
        string='Budget Available',
        compute='_compute_budget_warning',
        store=False,
        help='Whether sufficient budget is available for this purchase'
    )

    @api.depends('amount_total', 'ops_branch_id', 'ops_business_unit_id')
    def _compute_budget_warning(self):
        """Compute budget availability warning."""
        Budget = self.env['ops.budget']
        for order in self:
            order.budget_warning = ''
            order.budget_available = True

            if not order.ops_branch_id or not order.ops_business_unit_id:
                continue

            if order.amount_total <= 0:
                continue

            result = Budget.check_budget_availability(
                branch_id=order.ops_branch_id.id,
                business_unit_id=order.ops_business_unit_id.id,
                amount=order.amount_total,
                date=order.date_order.date() if order.date_order else fields.Date.today(),
            )

            if not result.get('available', True):
                order.budget_available = False
                order.budget_warning = _(
                    "Budget Warning: %(message)s\n"
                    "Budget: %(budget)s\n"
                    "Available: %(remaining).2f\n"
                    "Requested: %(amount).2f\n"
                    "Over by: %(over).2f"
                ) % {
                    'message': result.get('message', ''),
                    'budget': result.get('budget_name', 'N/A'),
                    'remaining': result.get('remaining', 0),
                    'amount': order.amount_total,
                    'over': result.get('over_amount', 0),
                }

    @api.model_create_multi
    def create(self, vals_list):
        """Create PO and check budget availability."""
        orders = super().create(vals_list)
        for order in orders:
            order._check_budget_availability(raise_error=False)
        return orders

    def write(self, vals):
        """Update PO and check budget if amount changed."""
        result = super().write(vals)
        if 'order_line' in vals or 'amount_total' in vals:
            for order in self:
                order._check_budget_availability(raise_error=False)
        return result

    def button_confirm(self):
        """Check budget before confirming PO."""
        for order in self:
            order._check_budget_availability(raise_error=True)
        return super().button_confirm()

    def _check_budget_availability(self, raise_error=False):
        """Check if PO amount is within budget.

        Args:
            raise_error: If True, raise ValidationError when over budget.
                        If False, just log a warning message.

        Returns:
            bool: True if budget is available, False otherwise.
        """
        self.ensure_one()

        if not self.ops_branch_id or not self.ops_business_unit_id:
            return True

        if self.amount_total <= 0:
            return True

        Budget = self.env['ops.budget']
        result = Budget.check_budget_availability(
            branch_id=self.ops_branch_id.id,
            business_unit_id=self.ops_business_unit_id.id,
            amount=self.amount_total,
            date=self.date_order.date() if self.date_order else fields.Date.today(),
        )

        if not result.get('available', True):
            msg = _(
                "Budget exceeded for %(branch)s / %(bu)s.\n"
                "Budget: %(budget)s\n"
                "Requested: %(amount).2f\n"
                "Available: %(available).2f\n"
                "Over by: %(over).2f"
            ) % {
                'branch': self.ops_branch_id.name,
                'bu': self.ops_business_unit_id.name,
                'budget': result.get('budget_name', 'N/A'),
                'amount': self.amount_total,
                'available': result.get('remaining', 0),
                'over': result.get('over_amount', 0),
            }

            if raise_error:
                raise ValidationError(msg)
            else:
                # Log warning in chatter
                self.message_post(
                    body=_("<strong>Budget Warning</strong><br/>%s") % msg.replace('\n', '<br/>'),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
                _logger.warning(
                    "Budget exceeded for PO %s: %s",
                    self.name or 'New',
                    msg.replace('\n', ' | ')
                )

        return result.get('available', True)
