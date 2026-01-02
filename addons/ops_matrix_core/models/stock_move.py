from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        related='picking_id.branch_id',
        store=True,
        readonly=True,
        help="Branch related to this stock move"
    )

    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        related='picking_id.business_unit_id',
        store=True,
        readonly=True,
        help="Business unit from the source document (Sale/Purchase Order)"
    )

    def _prepare_account_move_vals(self):
        """Override to add branch and business unit to accounting entries."""
        vals = super(StockMove, self)._prepare_account_move_vals()
        
        # Add matrix dimensions to account move
        vals.update({
            'branch_id': self.branch_id.id,
            'business_unit_id': self.business_unit_id.id,
        })

        # Add dimensions to all move lines
        if 'line_ids' in vals:
            for line in vals['line_ids']:
                if len(line) > 2 and isinstance(line[2], dict):
                    line[2].update({
                        'branch_id': self.branch_id.id,
                        'business_unit_id': self.business_unit_id.id,
                    })
        
        return vals
