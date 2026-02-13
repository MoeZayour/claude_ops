# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OpsAssetDisposalWizard(models.TransientModel):
    _name = 'ops.asset.disposal.wizard'
    _description = 'Asset Disposal Wizard'

    disposal_date = fields.Date(
        string='Disposal Date',
        required=True,
        default=fields.Date.context_today,
        help="Date of asset disposal."
    )
    asset_id = fields.Many2one(
        'ops.asset',
        string='Asset to Dispose',
        required=True,
        domain="[('state', '=', 'in_use')]",
        help="Select the asset you wish to dispose of."
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Disposal Journal',
        required=True,
        domain="[ ('type', '=', 'general')]",
        help="Journal for recording the disposal entry."
    )
    gain_account_id = fields.Many2one(
        'account.account',
        string='Gain on Disposal Account',
        help="Account to record any gain from the disposal."
    )
    loss_account_id = fields.Many2one(
        'account.account',
        string='Loss on Disposal Account',
        help="Account to record any loss from the disposal."
    )
    reason = fields.Text(
        string='Reason for Disposal',
        help="Explain why this asset is being disposed."
    )

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        """When an asset is selected, automatically populate the gain/loss accounts."""
        if self.asset_id and self.asset_id.category_id:
            self.gain_account_id = self.asset_id.category_id.account_gain_id
            self.loss_account_id = self.asset_id.category_id.account_loss_id
            self.journal_id = self.asset_id.category_id.journal_id

    def _create_disposal_move(self):
        """Creates the journal entry for the asset disposal."""
        self.ensure_one()
        asset = self.asset_id

        if not self.loss_account_id or not self.gain_account_id:
            raise UserError(_("Please configure the Gain and Loss accounts on the asset category."))

        move_lines = []

        # 1. Debit: Accumulated Depreciation
        if asset.accumulated_depreciation > 0:
            move_lines.append((0, 0, {
                'account_id': asset.category_id.account_depreciation_id.id,
                'debit': asset.accumulated_depreciation,
                'credit': 0,
                'name': _('Disposal: Accumulated Depreciation for %s') % asset.name,
            }))

        # 2. Credit: Asset Account (at original cost)
        move_lines.append((0, 0, {
            'account_id': asset.category_id.account_asset_id.id,
            'debit': 0,
            'credit': asset.purchase_value,
            'name': _('Disposal: Original Cost of %s') % asset.name,
        }))

        # 3. Calculate Gain or Loss
        book_value = asset.purchase_value - asset.accumulated_depreciation
        disposal_proceeds = 0

        if disposal_proceeds > book_value:  # Gain
            gain = disposal_proceeds - book_value
            account_id = self.gain_account_id.id
            debit = 0
            credit = gain
        else:  # Loss
            loss = book_value - disposal_proceeds
            account_id = self.loss_account_id.id
            debit = loss
            credit = 0

        if book_value != 0:
            move_lines.append((0, 0, {
                'account_id': account_id,
                'debit': debit,
                'credit': credit,
                'name': _('Disposal: Gain/Loss for %s') % asset.name,
            }))

        move_vals = {
            'ref': _('Disposal of %s') % asset.name,
            'date': self.disposal_date,
            'journal_id': self.journal_id.id,
            'line_ids': move_lines,
        }

        return self.env['account.move'].create(move_vals)

    def action_dispose_asset(self):
        """Creates the journal entry and updates the asset state."""
        self.ensure_one()

        move = self._create_disposal_move()
        move.action_post()

        self.asset_id.write({
            'state': 'disposed',
            'disposal_date': self.disposal_date,
            'disposal_move_id': move.id,
        })

        return {
            'name': _('Disposal Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }
