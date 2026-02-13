# -*- coding: utf-8 -*-
"""
OPS Period Close Wizard

Guides users through the period close process with:
- Checklist progress overview
- Bulk mark done functionality
- Final lock action
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsPeriodCloseWizard(models.TransientModel):
    """Wizard to guide through period close process."""
    _name = 'ops.period.close.wizard'
    _description = 'Period Close Wizard'

    period_id = fields.Many2one(
        'ops.fiscal.period',
        string='Fiscal Period',
        required=True,
        readonly=True,
        help="The period being closed"
    )
    period_name = fields.Char(
        related='period_id.name',
        string='Period Name'
    )
    period_date_from = fields.Date(
        related='period_id.date_from'
    )
    period_date_to = fields.Date(
        related='period_id.date_to'
    )
    current_lock_state = fields.Selection(
        related='period_id.lock_state',
        string='Current Status'
    )

    # Checklist Info
    checklist_progress = fields.Float(
        related='period_id.checklist_progress',
        string='Checklist Progress'
    )
    checklist_count = fields.Integer(
        related='period_id.checklist_count'
    )
    checklist_done_count = fields.Integer(
        related='period_id.checklist_done_count'
    )
    pending_items = fields.Integer(
        string='Pending Items',
        compute='_compute_pending_items'
    )

    # Checklist lines for bulk action
    checklist_line_ids = fields.Many2many(
        'ops.period.close.checklist',
        string='Checklist Items',
        compute='_compute_checklist_lines'
    )

    # Wizard State
    state = fields.Selection([
        ('overview', 'Overview'),
        ('checklist', 'Complete Checklist'),
        ('confirm', 'Confirm Lock'),
    ], default='overview', string='Step')

    # Lock Options
    lock_action = fields.Selection([
        ('soft_lock', 'Soft Lock (Warning Only)'),
        ('hard_lock', 'Hard Lock (Block Posting)'),
    ], string='Lock Action', default='soft_lock',
       help="Soft Lock: Users can still post but see a warning.\n"
            "Hard Lock: No posting allowed until unlocked.")

    notes = fields.Text(
        string='Close Notes',
        help="Notes about this period close"
    )

    @api.depends('period_id')
    def _compute_pending_items(self):
        """Compute number of pending checklist items."""
        for wizard in self:
            wizard.pending_items = wizard.checklist_count - wizard.checklist_done_count

    @api.depends('period_id')
    def _compute_checklist_lines(self):
        """Get checklist lines for this period."""
        for wizard in self:
            wizard.checklist_line_ids = wizard.period_id.checklist_ids

    def action_next_overview(self):
        """Move from overview to checklist step."""
        self.ensure_one()
        if self.pending_items > 0:
            self.state = 'checklist'
        else:
            self.state = 'confirm'
        return self._reopen_wizard()

    def action_next_checklist(self):
        """Move from checklist to confirm step."""
        self.ensure_one()
        self.state = 'confirm'
        return self._reopen_wizard()

    def action_back_overview(self):
        """Go back to overview step."""
        self.ensure_one()
        self.state = 'overview'
        return self._reopen_wizard()

    def action_back_checklist(self):
        """Go back to checklist step."""
        self.ensure_one()
        self.state = 'checklist'
        return self._reopen_wizard()

    def action_mark_all_done(self):
        """Mark all pending checklist items as done."""
        self.ensure_one()
        pending = self.period_id.checklist_ids.filtered(lambda x: not x.is_done)
        pending.action_mark_done()
        return self._reopen_wizard()

    def action_close_period(self):
        """Apply the lock action to the period."""
        self.ensure_one()

        # Log the close action
        if self.notes:
            self.period_id.message_post(
                body=_('Period close notes: %s') % self.notes,
                message_type='notification'
            )

        # Apply lock
        if self.lock_action == 'soft_lock':
            self.period_id.action_soft_lock()
        elif self.lock_action == 'hard_lock':
            # Check if checklist is complete for hard lock
            if self.checklist_count > 0 and self.checklist_progress < 100:
                raise UserError(_(
                    'Cannot hard lock: Checklist is only %.0f%% complete.\n'
                    'Complete all checklist items or choose Soft Lock.'
                ) % self.checklist_progress)
            self.period_id.action_hard_lock()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Period Closed'),
                'message': _('Period "%s" has been %s.') % (
                    self.period_id.name,
                    'soft locked' if self.lock_action == 'soft_lock' else 'hard locked'
                ),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }

    def _reopen_wizard(self):
        """Reopen the wizard to refresh display."""
        return {
            'name': _('Close Period: %s') % self.period_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'ops.period.close.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
