from odoo import models, fields


class OpsAssetCategory(models.Model):
    _inherit = 'ops.asset.category'
    _description = 'Asset Category'

    child_ids = fields.One2many('ops.asset.category', 'parent_id', string='Child Categories')
