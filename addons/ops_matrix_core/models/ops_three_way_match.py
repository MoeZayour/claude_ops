from odoo import api, fields, models

class OpsThreeWayMatch(models.Model):
    _name = 'ops.three.way.match'
    _description = 'Three-Way Match Engine'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', required=True, ondelete='cascade')
    ordered_qty = fields.Float('Ordered Quantity', related='purchase_line_id.product_qty', store=True)
    received_qty = fields.Float('Received Quantity', compute='_compute_received_qty', store=True)
    billed_qty = fields.Float('Billed Quantity', compute='_compute_billed_qty', store=True)
    match_state = fields.Selection([
        ('matched', 'Matched'),
        ('under_billed', 'Under Billed'),
        ('over_billed', 'Over Billed'),
        ('no_receipt', 'No Receipt'),
        ('partial_receipt', 'Partial Receipt'),
    ], string='Match Status', compute='_compute_match_state', store=True)
    is_blocked = fields.Boolean('Is Blocked', compute='_compute_match_state', store=True)
    blocking_reason = fields.Text('Blocking Reason', compute='_compute_match_state', store=True)
    qty_variance = fields.Float('Quantity Variance', compute='_compute_variance', store=True)
    qty_variance_percent = fields.Float('Quantity Variance (%)', compute='_compute_variance', store=True)

    @api.depends('purchase_line_id')
    def _compute_received_qty(self):
        """Calculate total received quantity from stock moves."""
        for record in self:
            moves = self.env['stock.move'].search([
                ('purchase_line_id', '=', record.purchase_line_id.id),
                ('state', '=', 'done')
            ])
            record.received_qty = sum(moves.mapped('product_uom_qty'))

    @api.depends('purchase_line_id')
    def _compute_billed_qty(self):
        """Calculate total billed quantity from invoice lines."""
        for record in self:
            invoice_lines = self.env['account.move.line'].search([
                ('purchase_line_id', '=', record.purchase_line_id.id),
                ('move_id.move_type', '=', 'in_invoice'),
                ('move_id.state', '!=', 'cancel')
            ])
            record.billed_qty = sum(invoice_lines.mapped('quantity'))

    @api.depends('ordered_qty', 'received_qty', 'billed_qty')
    def _compute_match_state(self):
        """Determine match state and blocking status."""
        for record in self:
            tolerance_pct = record.purchase_order_id.company_id.three_way_match_tolerance or 0.0
            tolerance = record.received_qty * (tolerance_pct / 100.0)

            if record.received_qty == 0:
                record.match_state = 'no_receipt'
                record.is_blocked = True
                record.blocking_reason = 'No goods have been received for this purchase order line.'
            elif record.billed_qty > (record.received_qty + tolerance):
                record.match_state = 'over_billed'
                record.is_blocked = True
                record.blocking_reason = f'Billed quantity ({record.billed_qty}) exceeds received quantity ({record.received_qty}) by more than tolerance ({tolerance_pct}%).'
            elif record.billed_qty < (record.received_qty - tolerance):
                record.match_state = 'under_billed'
                record.is_blocked = False
                record.blocking_reason = False
            elif record.received_qty < record.ordered_qty:
                record.match_state = 'partial_receipt'
                record.is_blocked = False
                record.blocking_reason = False
            else:
                record.match_state = 'matched'
                record.is_blocked = False
                record.blocking_reason = False

    @api.depends('received_qty', 'billed_qty')
    def _compute_variance(self):
        """Calculate quantity variance."""
        for record in self:
            record.qty_variance = record.billed_qty - record.received_qty
            if record.received_qty > 0:
                record.qty_variance_percent = (record.qty_variance / record.received_qty) * 100
            else:
                record.qty_variance_percent = 0.0
