from odoo import models, fields, api

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        compute='_compute_branch_id',
        store=True,
        help="Branch from the warehouse"
    )

    @api.depends('warehouse_id', 'warehouse_id.branch_id')
    def _compute_branch_id(self):
        """Compute branch from warehouse."""
        for orderpoint in self:
            orderpoint.branch_id = orderpoint.warehouse_id.branch_id if orderpoint.warehouse_id else False
