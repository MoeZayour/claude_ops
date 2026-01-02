from odoo import models, fields

class OpsAssetModel(models.Model):
    _name = 'ops.asset.model'
    _description = 'Asset Model'
    _order = 'name'

    name = fields.Char(string='Model Name', required=True)
    category_id = fields.Many2one('ops.asset.category', string='Asset Category', required=True)
    product_id = fields.Many2one('product.product', string='Product')
