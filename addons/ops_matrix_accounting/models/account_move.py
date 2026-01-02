# -*- coding: utf-8 -*-
from odoo import fields, models, api

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
