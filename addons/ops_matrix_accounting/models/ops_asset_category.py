# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class OpsAssetCategory(models.Model):
    _name = 'ops.asset.category'
    _description = 'Fixed Asset Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _parent_store = True
    _parent_name = 'parent_id'

    parent_id = fields.Many2one(
        'ops.asset.category',
        string='Parent Category',
        index=True,
        ondelete='restrict',
    )

    parent_path = fields.Char(index=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    name = fields.Char(string='Category Name', required=True, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the category without removing it.")

    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=False,
        ondelete='set null',
        domain="[('type', '=', 'general')]",
        help="Journal for posting depreciation entries. Optional until accounting is configured; cleared if removed during chart changes."
    )

    asset_account_id = fields.Many2one(
        'account.account', string='Asset Account',
        required=False, ondelete='set null',
        help="Account to book the value of new assets. Optional until accounting is configured; cleared if removed during chart changes."
    )

    depreciation_account_id = fields.Many2one(
        'account.account', string='Accumulated Depreciation Account',
        required=False, ondelete='set null',
        help="Account for accumulated depreciation. Optional until accounting is configured; cleared if removed during chart changes."
    )

    expense_account_id = fields.Many2one(
        'account.account', string='Depreciation Expense Account',
        required=False, ondelete='set null',
        help="Account for the periodic depreciation expense. Optional until accounting is configured; cleared if removed during chart changes."
    )

    depreciation_method = fields.Selection([
        ('straight_line', 'Straight-line'),
        ('declining_balance', 'Declining Balance')
    ], string='Depreciation Method', default='straight_line', required=True,
       help="Method used to calculate depreciation.")

    depreciation_duration = fields.Integer(
        string='Depreciation Duration (Years)', required=True,
        help="Duration over which the asset is depreciated."
    )

    asset_ids = fields.One2many('ops.asset', 'category_id', string='Assets')
    asset_count = fields.Integer(compute='_compute_asset_count', string='Asset Count')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Asset category name must be unique!')
    ]

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for category in self:
            category.asset_count = len(category.asset_ids)

    def open_assets(self):
        self.ensure_one()
        return {
            'name': _('Assets'),
            'view_mode': 'list,form',
            'res_model': 'ops.asset',
            'type': 'ir.actions.act_window',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id}
        }

    def unlink(self):
        for category in self:
            if category.asset_ids:
                raise UserError(_('You cannot delete a category that is being used by an asset.'))
        return super(OpsAssetCategory, self).unlink()
