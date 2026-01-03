from odoo import models, fields, api
from odoo.exceptions import ValidationError
from typing import List, Dict, Any

class StockPicking(models.Model):
    _inherit = ['stock.picking', 'ops.matrix.mixin', 'ops.approval.mixin']
    _name = 'stock.picking'

    # Note: branch fields now come from ops.matrix.mixin as ops_branch_id and ops_business_unit_id
    # Keeping legacy fields for backward compatibility
    branch_id = fields.Many2one(
        'res.company',
        string='Branch (Legacy)',
        compute='_compute_legacy_branch_id',
        store=True,
        readonly=False, # Allow direct write for legacy/import cases
        inverse='_inverse_legacy_branch_id'
    )

    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit (Legacy)',
        related='ops_business_unit_id',
        store=True
    )

    @api.depends('ops_branch_id')
    def _compute_legacy_branch_id(self):
        for picking in self:
            picking.branch_id = picking.ops_branch_id.company_id if picking.ops_branch_id else False

    def _inverse_legacy_branch_id(self):
        for picking in self:
            if picking.branch_id and not picking.ops_branch_id:
                # Find the first ops.branch for this company and assign it
                branch = self.env['ops.branch'].search([('company_id', '=', picking.branch_id.id)], limit=1)
                if branch:
                    picking.ops_branch_id = branch

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'StockPicking':
        """Override to set ops_branch_id from user context if not provided."""
        for vals in vals_list:
            # Set ops_branch_id from user's primary branch if not provided
            if not vals.get('ops_branch_id') and self.env.user.primary_branch_id:
                vals['ops_branch_id'] = self.env.user.primary_branch_id.id
        return super().create(vals_list)

    def button_validate(self) -> bool:
        """
        Task 1: Enforce strict inventory at delivery.
        Prevent validation if it would cause negative stock (outgoing deliveries only).
        """
        # Only check for outgoing pickings (deliveries)
        for picking in self:
            if picking.picking_type_id.code == 'outgoing':
                # Check each move for stock availability
                for move in picking.move_ids:
                    # Skip if product is consumable or service type
                    if move.product_id.type in ['consu', 'service']:
                        continue
                    
                    # Get available quantity at source location
                    available_qty = move.product_id.with_context(
                        location=move.location_id.id
                    ).qty_available
                    
                    # Check if move would cause negative stock
                    if available_qty < move.product_uom_qty:
                        raise ValidationError(
                            f"Cannot validate delivery. Product '{move.product_id.display_name}' "
                            f"has insufficient stock in '{move.location_id.display_name}'. "
                            f"Available: {available_qty:.2f}, Required: {move.product_uom_qty:.2f}. "
                            f"You cannot drive stock into negative."
                        )
        
        return super().button_validate()
