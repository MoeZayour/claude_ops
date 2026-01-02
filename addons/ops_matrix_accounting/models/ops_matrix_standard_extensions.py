from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this sale"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        default=lambda self: self._get_default_business_unit(),
        help="Business unit this sale belongs to"
    )
    
    def _get_default_branch(self):
        """Get default branch from user or first available"""
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id:
            return self.env.user.branch_id
        return self.env['ops.branch'].search([], limit=1)
    
    def _get_default_business_unit(self):
        """Get default business unit or first available"""
        return self.env['ops.business.unit'].search([], limit=1)

    def _prepare_invoice(self):
        """Propagate matrix dimensions to created invoice."""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'ops_branch_id': self.ops_branch_id.id,
            'ops_business_unit_id': self.ops_business_unit_id.id,
        })
        return invoice_vals


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this purchase"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        default=lambda self: self._get_default_business_unit(),
        help="Business unit this purchase belongs to"
    )
    
    def _get_default_branch(self):
        """Get default branch from user or first available"""
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id:
            return self.env.user.branch_id
        return self.env['ops.branch'].search([], limit=1)
    
    def _get_default_business_unit(self):
        """Get default business unit or first available"""
        return self.env['ops.business.unit'].search([], limit=1)

    def _prepare_invoice(self):
        """Propagate matrix dimensions to created bill."""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'ops_branch_id': self.ops_branch_id.id,
            'ops_business_unit_id': self.ops_business_unit_id.id,
        })
        return invoice_vals


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this transfer"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        default=lambda self: self._get_default_business_unit(),
        help="Business unit this transfer belongs to"
    )
    
    def _get_default_branch(self):
        """Get default branch from user or first available"""
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id:
            return self.env.user.branch_id
        return self.env['ops.branch'].search([], limit=1)
    
    def _get_default_business_unit(self):
        """Get default business unit or first available"""
        return self.env['ops.business.unit'].search([], limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit matrix dimensions from source document."""
        for vals in vals_list:
            if vals.get('origin'):
                # Try to find source document
                sale_order = self.env['sale.order'].search([('name', '=', vals['origin'])], limit=1)
                if sale_order:
                    vals.update({
                        'ops_branch_id': sale_order.ops_branch_id.id,
                        'ops_business_unit_id': sale_order.ops_business_unit_id.id,
                    })
                    continue

                purchase_order = self.env['purchase.order'].search([('name', '=', vals['origin'])], limit=1)
                if purchase_order:
                    vals.update({
                        'ops_branch_id': purchase_order.ops_branch_id.id,
                        'ops_business_unit_id': purchase_order.ops_business_unit_id.id,
                    })
        
        return super().create(vals_list)


class AccountMove(models.Model):
    _inherit = 'account.move'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this entry"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        default=lambda self: self._get_default_business_unit(),
        help="Business unit this entry belongs to"
    )
    
    def _get_default_branch(self):
        """Get default branch from user or first available"""
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id:
            return self.env.user.branch_id
        return self.env['ops.branch'].search([], limit=1)
    
    def _get_default_business_unit(self):
        """Get default business unit or first available"""
        return self.env['ops.business.unit'].search([], limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure matrix dimensions are properly set."""
        moves = super().create(vals_list)
        for move in moves:
            # Propagate dimensions to lines if not already set
            for line in move.line_ids:
                if not line.ops_branch_id:
                    line.ops_branch_id = move.ops_branch_id
                if not line.ops_business_unit_id:
                    line.ops_business_unit_id = move.ops_business_unit_id
        return moves


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        default=lambda self: self._get_default_branch(),
        help="Branch for this journal item"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        default=lambda self: self._get_default_business_unit(),
        help="Business unit for this journal item"
    )
    
    def _get_default_branch(self):
        """Get default branch from move or user or first available"""
        if self.move_id and self.move_id.ops_branch_id:
            return self.move_id.ops_branch_id
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id:
            return self.env.user.branch_id
        return self.env['ops.branch'].search([], limit=1)
    
    def _get_default_business_unit(self):
        """Get default business unit from move or first available"""
        if self.move_id and self.move_id.ops_business_unit_id:
            return self.move_id.ops_business_unit_id
        return self.env['ops.business.unit'].search([], limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure matrix dimensions are inherited from parent move."""
        for vals in vals_list:
            if vals.get('move_id'):
                move = self.env['account.move'].browse(vals['move_id'])
                if not vals.get('ops_branch_id'):
                    vals['ops_branch_id'] = move.ops_branch_id.id
                if not vals.get('ops_business_unit_id'):
                    vals['ops_business_unit_id'] = move.ops_business_unit_id.id
        
        return super().create(vals_list)
