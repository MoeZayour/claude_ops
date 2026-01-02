from odoo import models, fields

class OpsAssetDepreciation(models.Model):
    _name = 'ops.asset.depreciation'
    _description = 'Asset Depreciation Line'
    _order = 'depreciation_date desc'

    name = fields.Char(string='Name', required=True)
    asset_id = fields.Many2one('ops.asset', string='Asset', required=True, ondelete='cascade')
    amount = fields.Float(string='Amount', required=True)
    depreciation_date = fields.Date(string='Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
