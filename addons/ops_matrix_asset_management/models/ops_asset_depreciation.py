from odoo import models, fields, api

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
    
    # Add after existing fields
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
        help="Accounting entry for this depreciation"
    )
    
    move_posted = fields.Boolean(
        string='Posted',
        compute='_compute_move_posted',
        store=True,
        help="Whether the journal entry has been posted"
    )
    
    @api.depends('move_id.state')
    def _compute_move_posted(self):
        for line in self:
            line.move_posted = line.move_id.state == 'posted' if line.move_id else False
