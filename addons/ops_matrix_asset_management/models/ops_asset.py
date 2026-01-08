from odoo import models, fields, api

class OpsAsset(models.Model):
    _name = 'ops.asset'
    _description = 'Matrix Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'ops.matrix.mixin']

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    code = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    model_id = fields.Many2one('ops.asset.model', string='Model', required=True)
    category_id = fields.Many2one('ops.asset.category', string='Category', related='model_id.category_id', store=True)
    asset_type = fields.Selection([
        ('tangible', 'Tangible'),
        ('intangible', 'Intangible'),
    ], string='Asset Type', default='tangible', required=True)
    purchase_date = fields.Date(string='Purchase Date', required=True, tracking=True)
    purchase_value = fields.Float(string='Purchase Value', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('close', 'Closed'),
        ('sold', 'Sold'),
    ], string='Status', default='draft', tracking=True)

    value = fields.Float(string='Gross Value', required=True, tracking=True)
    salvage_value = fields.Float(string='Salvage Value', tracking=True)
    value_residual = fields.Float(string='Residual Value', compute='_compute_value_residual', store=True)
    
    # Additional computed fields
    acquisition_value = fields.Float(string='Acquisition Value', related='value', store=True)
    depreciated_value = fields.Float(string='Depreciated Value', compute='_compute_depreciated_value', store=True)
    book_value = fields.Monetary(
        string='Book Value',
        compute='_compute_book_value',
        store=True,
        currency_field='currency_id',
        help="Current book value (Acquisition Value - Depreciated Value)"
    )
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                   default=lambda self: self.env.company.currency_id)

    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True)
    account_depreciation_id = fields.Many2one('account.account', string='Depreciation Account', required=True)
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Expense Account', required=True)

    method = fields.Selection([
        ('linear', 'Linear'),
        ('degressive', 'Degressive'),
    ], string='Method', default='linear', required=True)
    method_number = fields.Integer(string='Number of Depreciations', default=5, required=True)
    method_period = fields.Integer(string='Period Length (months)', default=12, required=True)
    depreciation_line_ids = fields.One2many('ops.asset.depreciation', 'asset_id', string='Depreciation Lines')

    @api.depends('value', 'salvage_value', 'depreciation_line_ids.amount')
    def _compute_value_residual(self):
        for asset in self:
            total_depreciation = sum(line.amount for line in asset.depreciation_line_ids if line.state == 'posted')
            asset.value_residual = asset.value - asset.salvage_value - total_depreciation
    
    @api.depends('depreciation_line_ids.amount', 'depreciation_line_ids.state')
    def _compute_depreciated_value(self):
        for asset in self:
            asset.depreciated_value = sum(line.amount for line in asset.depreciation_line_ids if line.state == 'posted')
    
    @api.depends('acquisition_value', 'depreciated_value')
    def _compute_book_value(self):
        for asset in self:
            asset.book_value = asset.acquisition_value - asset.depreciated_value
    
    fully_depreciated = fields.Boolean(
        string='Fully Depreciated',
        compute='_compute_fully_depreciated',
        store=True,
        help="Check if the asset is fully depreciated"
    )

    @api.depends('acquisition_value', 'depreciated_value', 'salvage_value')
    def _compute_fully_depreciated(self):
        for asset in self:
            depreciable = asset.acquisition_value - asset.salvage_value
            asset.fully_depreciated = asset.depreciated_value >= depreciable if depreciable > 0 else False
