# -*- coding: utf-8 -*-
"""
Three-Way Match Override Wizard
Allows AP managers to approve override of three-way match validation.
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsThreeWayMatchOverrideWizard(models.TransientModel):
    _name = 'ops.three.way.match.override.wizard'
    _description = 'Three-Way Match Override Wizard'

    # ==================================================================
    # FIELDS
    # ==================================================================

    move_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        required=True,
        readonly=True,
        ondelete='cascade',
    )

    # Display fields (related)
    move_name = fields.Char(
        related='move_id.name',
        string='Bill Reference',
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='move_id.partner_id',
        string='Vendor',
        readonly=True,
    )
    amount_total = fields.Monetary(
        related='move_id.amount_total',
        string='Total Amount',
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='move_id.currency_id',
        readonly=True,
    )
    match_status = fields.Selection(
        related='move_id.three_way_match_status',
        string='Match Status',
        readonly=True,
    )
    match_details = fields.Text(
        related='move_id.three_way_match_details',
        string='Match Details',
        readonly=True,
    )

    # PO and Receipt info
    matched_po_count = fields.Integer(
        related='move_id.matched_po_count',
        string='PO Count',
        readonly=True,
    )
    matched_picking_count = fields.Integer(
        related='move_id.matched_picking_count',
        string='Receipt Count',
        readonly=True,
    )

    # Override fields
    override_reason = fields.Text(
        string='Override Reason',
        required=True,
        help='Provide a detailed justification for approving this override. '
             'This will be logged in the bill\'s chatter for audit purposes.'
    )

    # Confirmation checkbox
    confirm_override = fields.Boolean(
        string='I confirm this override',
        default=False,
        help='Check this box to confirm you have reviewed the match details '
             'and approve the override.'
    )

    # ==================================================================
    # ACTIONS
    # ==================================================================

    def action_approve_override(self):
        """Approve the three-way match override."""
        self.ensure_one()

        # Validation: reason must be meaningful
        if not self.override_reason or len(self.override_reason.strip()) < 10:
            raise UserError(_(
                'Please provide a detailed reason for the override '
                '(minimum 10 characters).'
            ))

        # Validation: confirmation checkbox
        if not self.confirm_override:
            raise UserError(_(
                'Please check the confirmation box to approve the override.'
            ))

        # Apply override to the move
        self.move_id.write({
            'three_way_match_override': True,
            'three_way_match_override_reason': self.override_reason.strip(),
            'three_way_match_override_by': self.env.uid,
            'three_way_match_override_date': fields.Datetime.now(),
        })

        # Post message in chatter
        self.move_id.message_post(
            body=_(
                '✓ <strong>Three-way match override approved</strong><br/><br/>'
                '<strong>Reason:</strong> %(reason)s<br/>'
                '<strong>Approved by:</strong> %(user)s<br/>'
                '<strong>Match Status:</strong> %(status)s<br/>'
                '<strong>POs:</strong> %(pos)d | <strong>Receipts:</strong> %(receipts)d'
            ) % {
                'reason': self.override_reason.strip(),
                'user': self.env.user.name,
                'status': dict(self.move_id._fields['three_way_match_status'].selection).get(
                    self.move_id.three_way_match_status, self.move_id.three_way_match_status
                ),
                'pos': self.matched_po_count,
                'receipts': self.matched_picking_count,
            },
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        # Mark related activities as done
        activities = self.move_id.activity_ids.filtered(
            lambda a: a.summary and 'Override' in a.summary
        )
        if activities:
            activities.action_done()

        _logger.info(
            'Three-way match override approved for %s by %s. Reason: %s',
            self.move_id.name,
            self.env.user.name,
            self.override_reason.strip()[:100]
        )

        # Return notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Override Approved'),
                'message': _('Three-way match override has been approved. '
                           'The bill can now be posted.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_reject_override(self):
        """Reject the override request and notify the requester."""
        self.ensure_one()

        # Post rejection message
        self.move_id.message_post(
            body=_(
                '✗ <strong>Three-way match override rejected</strong><br/><br/>'
                'The override request has been rejected by %(user)s.<br/>'
                'Please ensure goods are received before attempting to post this bill, '
                'or contact your AP manager for further assistance.'
            ) % {'user': self.env.user.name},
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        # Mark related activities as done
        activities = self.move_id.activity_ids.filtered(
            lambda a: a.summary and 'Override' in a.summary
        )
        if activities:
            activities.action_done()

        return {'type': 'ir.actions.act_window_close'}
