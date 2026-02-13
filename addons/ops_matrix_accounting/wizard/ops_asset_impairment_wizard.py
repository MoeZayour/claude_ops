# -*- coding: utf-8 -*-
"""
OPS Asset Impairment Wizard
Records impairment losses for fixed assets per IAS 36.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsAssetImpairmentWizard(models.TransientModel):
    """Wizard to record asset impairment."""
    _name = 'ops.asset.impairment.wizard'
    _description = 'Asset Impairment Wizard'

    asset_id = fields.Many2one('ops.asset', required=True, string='Asset')
    impairment_date = fields.Date(string='Impairment Date', required=True, default=fields.Date.today)
    currency_id = fields.Many2one(related='asset_id.company_id.currency_id')
    current_carrying_amount = fields.Monetary(string='Current Carrying Amount', readonly=True)
    recoverable_amount = fields.Monetary(string='Recoverable Amount', required=True,
                                          help="Higher of fair value less costs to sell and value in use")
    impairment_loss = fields.Monetary(string='Impairment Loss', compute='_compute_loss')
    reason = fields.Text(string='Impairment Reason', required=True,
                          help="Document the indicators of impairment and basis for recoverable amount")
    regenerate_schedule = fields.Boolean(string='Regenerate Depreciation Schedule', default=True,
                                          help="Regenerate future depreciation based on new carrying amount")
    impairment_loss_account_id = fields.Many2one(
        'account.account', string='Impairment Loss Account',
        help="Account to record the impairment loss expense"
    )

    @api.depends('current_carrying_amount', 'recoverable_amount')
    def _compute_loss(self):
        for wizard in self:
            if wizard.recoverable_amount and wizard.current_carrying_amount > wizard.recoverable_amount:
                wizard.impairment_loss = wizard.current_carrying_amount - wizard.recoverable_amount
            else:
                wizard.impairment_loss = 0

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        if self.asset_id:
            self.current_carrying_amount = self.asset_id.book_value
            if self.asset_id.impairment_loss_account_id:
                self.impairment_loss_account_id = self.asset_id.impairment_loss_account_id

    def action_record_impairment(self):
        """Record the impairment."""
        self.ensure_one()
        if self.impairment_loss <= 0:
            raise UserError(_('No impairment loss to record. Recoverable amount exceeds or equals carrying amount.'))

        asset = self.asset_id
        if not self.impairment_loss_account_id:
            raise UserError(_('Please select an impairment loss account.'))

        if not asset.category_id.account_depreciation_id:
            raise UserError(_('Asset category does not have an accumulated depreciation account configured.'))

        # Create impairment journal entry
        # Debit: Impairment Loss (expense)
        # Credit: Accumulated Depreciation (or asset directly)
        move_vals = {
            'date': self.impairment_date,
            'journal_id': asset.category_id.journal_id.id,
            'ref': f'Asset Impairment: {asset.name}',
            'ops_branch_id': asset.ops_branch_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.impairment_loss_account_id.id,
                    'name': f'Impairment Loss: {asset.name}',
                    'debit': self.impairment_loss,
                    'credit': 0,
                    'ops_branch_id': asset.ops_branch_id.id,
                }),
                (0, 0, {
                    'account_id': asset.category_id.account_depreciation_id.id,
                    'name': f'Impairment: {asset.name}',
                    'debit': 0,
                    'credit': self.impairment_loss,
                    'ops_branch_id': asset.ops_branch_id.id,
                }),
            ],
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        # Update asset with impairment information
        new_depreciable_value = self.recoverable_amount - asset.salvage_value
        if new_depreciable_value < 0:
            new_depreciable_value = 0

        asset.write({
            'impaired': True,
            'impairment_date': self.impairment_date,
            'original_value': asset.purchase_value if not asset.original_value else asset.original_value,
            'recoverable_amount': self.recoverable_amount,
            'impairment_move_id': move.id,
            'impairment_loss_account_id': self.impairment_loss_account_id.id,
        })

        asset.message_post(body=_(
            'Asset impaired on %s.\n'
            'Previous Carrying Amount: %s\n'
            'Recoverable Amount: %s\n'
            'Impairment Loss: %s\n'
            'Reason: %s\n'
            'Journal Entry: %s'
        ) % (
            self.impairment_date,
            self.current_carrying_amount,
            self.recoverable_amount,
            self.impairment_loss,
            self.reason,
            move.name
        ))

        # Regenerate depreciation schedule if requested
        if self.regenerate_schedule:
            # Remove future draft depreciation lines
            future_lines = asset.depreciation_ids.filtered(
                lambda l: l.state == 'draft' and l.depreciation_date > self.impairment_date
            )
            future_lines.unlink()

            # Trigger schedule regeneration if method exists
            if hasattr(asset, 'generate_depreciation_schedule'):
                asset.generate_depreciation_schedule()
                asset.message_post(body=_('Depreciation schedule regenerated based on new carrying amount.'))

        return {'type': 'ir.actions.act_window_close'}
