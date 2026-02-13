# -*- coding: utf-8 -*-
"""
OPS Inter-Branch Transfer Accounting
Handles transfers of inventory, assets, or funds between branches
with automatic mirror journal entry creation.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsInterbranchTransfer(models.Model):
    """Inter-Branch Transfer Document."""
    _name = 'ops.interbranch.transfer'
    _description = 'Inter-Branch Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    transfer_type = fields.Selection([
        ('inventory', 'Inventory Transfer'),
        ('asset', 'Asset Transfer'),
        ('funds', 'Funds Transfer'),
        ('expense', 'Expense Allocation'),
    ], string='Transfer Type', required=True, default='inventory', tracking=True)

    date = fields.Date(
        string='Transfer Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )

    source_branch_id = fields.Many2one(
        'ops.branch', string='Source Branch',
        required=True, tracking=True,
        domain="[('company_id', '=', company_id)]"
    )

    dest_branch_id = fields.Many2one(
        'ops.branch', string='Destination Branch',
        required=True, tracking=True,
        domain="[('company_id', '=', company_id), ('id', '!=', source_branch_id)]"
    )

    currency_id = fields.Many2one(related='company_id.currency_id')
    amount = fields.Monetary(string='Transfer Amount', required=True, tracking=True)

    transit_account_id = fields.Many2one(
        'account.account', string='Transit Account', required=True
    )

    source_account_id = fields.Many2one(
        'account.account', string='Source Account', required=True
    )

    dest_account_id = fields.Many2one(
        'account.account', string='Destination Account', required=True
    )

    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=True,
        domain="[('type', '=', 'general')]"
    )

    inventory_transfer_id = fields.Many2one('stock.picking', string='Inventory Transfer')
    asset_id = fields.Many2one('ops.asset', string='Asset')

    source_move_id = fields.Many2one('account.move', string='Source Entry', readonly=True, copy=False)
    dest_move_id = fields.Many2one('account.move', string='Destination Entry', readonly=True, copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Receipt'),
        ('received', 'Received'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    sent_by = fields.Many2one('res.users', string='Sent By', readonly=True)
    sent_date = fields.Datetime(string='Sent Date', readonly=True)
    received_by = fields.Many2one('res.users', string='Received By', readonly=True)
    received_date = fields.Datetime(string='Received Date', readonly=True)
    description = fields.Text(string='Description')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.interbranch.transfer') or _('New')
        return super().create(vals_list)

    @api.constrains('source_branch_id', 'dest_branch_id')
    def _check_branches(self):
        for transfer in self:
            if transfer.source_branch_id == transfer.dest_branch_id:
                raise ValidationError(_('Source and destination branches must be different.'))

    @api.constrains('amount')
    def _check_amount(self):
        for transfer in self:
            if transfer.amount <= 0:
                raise ValidationError(_('Transfer amount must be positive.'))

    def action_send(self):
        """Send the transfer - creates source branch journal entry."""
        for transfer in self:
            if transfer.state != 'draft':
                raise UserError(_('Can only send draft transfers.'))

            move_vals = {
                'date': transfer.date,
                'journal_id': transfer.journal_id.id,
                'ref': f'IBT Send: {transfer.name}',
                'ops_branch_id': transfer.source_branch_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': transfer.transit_account_id.id,
                        'name': f'Inter-branch transfer to {transfer.dest_branch_id.name}',
                        'debit': transfer.amount,
                        'credit': 0,
                        'ops_branch_id': transfer.source_branch_id.id,
                    }),
                    (0, 0, {
                        'account_id': transfer.source_account_id.id,
                        'name': f'Inter-branch transfer to {transfer.dest_branch_id.name}',
                        'debit': 0,
                        'credit': transfer.amount,
                        'ops_branch_id': transfer.source_branch_id.id,
                    }),
                ],
            }

            move = self.env['account.move'].create(move_vals)
            move.action_post()

            transfer.write({
                'source_move_id': move.id,
                'state': 'pending',
                'sent_by': self.env.uid,
                'sent_date': fields.Datetime.now(),
            })

            transfer.message_post(body=_(
                'Transfer sent to %s. Amount: %s'
            ) % (transfer.dest_branch_id.name, transfer.amount))

    def action_receive(self):
        """Receive the transfer - creates destination branch journal entry."""
        for transfer in self:
            if transfer.state != 'pending':
                raise UserError(_('Can only receive pending transfers.'))

            move_vals = {
                'date': fields.Date.today(),
                'journal_id': transfer.journal_id.id,
                'ref': f'IBT Receive: {transfer.name}',
                'ops_branch_id': transfer.dest_branch_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': transfer.dest_account_id.id,
                        'name': f'Inter-branch transfer from {transfer.source_branch_id.name}',
                        'debit': transfer.amount,
                        'credit': 0,
                        'ops_branch_id': transfer.dest_branch_id.id,
                    }),
                    (0, 0, {
                        'account_id': transfer.transit_account_id.id,
                        'name': f'Inter-branch transfer from {transfer.source_branch_id.name}',
                        'debit': 0,
                        'credit': transfer.amount,
                        'ops_branch_id': transfer.dest_branch_id.id,
                    }),
                ],
            }

            move = self.env['account.move'].create(move_vals)
            move.action_post()

            transfer.write({
                'dest_move_id': move.id,
                'state': 'received',
                'received_by': self.env.uid,
                'received_date': fields.Datetime.now(),
            })

            transfer.message_post(body=_(
                'Transfer received from %s. Amount: %s'
            ) % (transfer.source_branch_id.name, transfer.amount))

    def action_reconcile(self):
        """Mark transfer as reconciled after verification."""
        for transfer in self:
            if transfer.state != 'received':
                raise UserError(_('Can only reconcile received transfers.'))

            if not transfer.source_move_id or not transfer.dest_move_id:
                raise UserError(_('Both journal entries must exist.'))

            if transfer.source_move_id.state != 'posted' or transfer.dest_move_id.state != 'posted':
                raise UserError(_('Both journal entries must be posted.'))

            transfer.write({'state': 'reconciled'})
            transfer.message_post(body=_('Transfer reconciled.'))

    def action_cancel(self):
        """Cancel the transfer and reverse entries if needed."""
        for transfer in self:
            if transfer.state == 'reconciled':
                raise UserError(_('Cannot cancel reconciled transfers.'))

            if transfer.dest_move_id and transfer.dest_move_id.state == 'posted':
                transfer.dest_move_id.button_draft()
                transfer.dest_move_id.button_cancel()

            if transfer.source_move_id and transfer.source_move_id.state == 'posted':
                transfer.source_move_id.button_draft()
                transfer.source_move_id.button_cancel()

            transfer.write({'state': 'cancelled'})
            transfer.message_post(body=_('Transfer cancelled.'))

    def action_view_journal_entries(self):
        """View related journal entries."""
        self.ensure_one()
        move_ids = []
        if self.source_move_id:
            move_ids.append(self.source_move_id.id)
        if self.dest_move_id:
            move_ids.append(self.dest_move_id.id)

        return {
            'name': _('Journal Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', move_ids)],
        }


class ResCompanyInterbranchExtension(models.Model):
    _inherit = 'res.company'

    interbranch_transit_account_id = fields.Many2one(
        'account.account', string='Inter-Branch Transit Account',
        domain="[('company_id', '=', id)]"
    )

    interbranch_journal_id = fields.Many2one(
        'account.journal', string='Inter-Branch Journal',
        domain="[('company_id', '=', id), ('type', '=', 'general')]"
    )
