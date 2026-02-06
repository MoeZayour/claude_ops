# -*- coding: utf-8 -*-
"""
OPS Matrix Core - Sale Order Line Extensions
===============================================

Extends sale.order.line with matrix mixin integration, price protection,
cost shield, margin calculations, and branch activation governance.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    """Extend sale.order.line with Matrix Mixin for dimension propagation."""
    _inherit = ['sale.order.line', 'ops.matrix.mixin', 'ops.field.visibility.mixin']
    _name = 'sale.order.line'

    # These fields are inherited from ops.matrix.mixin:
    # - ops_branch_id
    # - ops_business_unit_id
    # - ops_company_id
    # - ops_analytic_distribution

    # ==========================================================================
    # PRICE PROTECTION: Field to control price_unit editability
    # ==========================================================================
    can_edit_unit_price = fields.Boolean(
        string='Can Edit Unit Price',
        compute='_compute_can_edit_unit_price',
        store=False,
        help="Determines if the current user can edit unit prices. Only Managers and Admins can edit."
    )

    # The Cost Shield: Field-Level Security for Sale Order Line Costs
    can_user_access_cost_prices = fields.Boolean(
        string='Can Access Cost Prices',
        compute='_compute_can_user_access_cost_prices',
        store=False,
        help="Determines if the current user can view cost prices on sale order lines."
    )

    # Cost Shield Protected Fields - ISS-002 Hardening
    purchase_price = fields.Float(
        string='Cost',
        compute='_compute_purchase_price',
        digits='Product Price',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Unit cost price from product (protected field - Admin/OPS Manager only)"
    )

    margin = fields.Float(
        string='Margin',
        compute='_compute_margin',
        digits='Product Price',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Gross margin amount (Sale Price - Cost) x Quantity (protected field - Admin/OPS Manager only)"
    )

    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Gross margin percentage (protected field - Admin/OPS Manager only)"
    )

    @api.depends_context('uid')
    def _compute_can_edit_unit_price(self):
        """
        PRICE PROTECTION: Determine if user can edit unit prices.

        Only OPS Managers and System Administrators can edit unit prices.
        """
        is_manager = self.env.user.has_group('ops_matrix_core.group_ops_manager')
        is_admin = self.env.user.has_group('base.group_system')
        can_edit = is_manager or is_admin

        for record in self:
            record.can_edit_unit_price = can_edit

    @api.depends_context('uid')
    def _compute_can_user_access_cost_prices(self):
        """
        Check if user has authority to view cost prices on sale order lines.
        Implements "The Cost Shield" anti-fraud measure.
        """
        for record in self:
            # Administrators bypass all restrictions
            if self.env.user.has_group('base.group_system'):
                record.can_user_access_cost_prices = True
            else:
                # Check persona authority flag
                record.can_user_access_cost_prices = self.env.user.has_ops_authority('can_access_cost_prices')

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_purchase_price(self):
        """Compute the unit cost (purchase price) from product standard_price."""
        for line in self:
            if line.product_id:
                line.purchase_price = line.product_id.standard_price
            else:
                line.purchase_price = 0.0

    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
    def _compute_margin(self):
        """Compute margin and margin percentage for sale order lines."""
        for line in self:
            if line.product_id:
                total_cost = line.purchase_price * line.product_uom_qty
                line.margin = line.price_subtotal - total_cost

                if line.price_subtotal:
                    line.margin_percent = (line.margin / line.price_subtotal) * 100.0
                else:
                    line.margin_percent = 0.0
            else:
                line.margin = 0.0
                line.margin_percent = 0.0

    def _get_default_ops_branch(self):
        """Get default branch from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['sale.order'].browse(self._context['default_order_id'])
            if order.ops_branch_id:
                return order.ops_branch_id.id
        return super()._get_default_ops_branch()

    def _get_default_ops_business_unit(self):
        """Get default BU from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['sale.order'].browse(self._context['default_order_id'])
            if order.ops_business_unit_id:
                return order.ops_business_unit_id.id
        return super()._get_default_ops_business_unit()

    def write(self, vals):
        """
        Override write to enforce PRICE PROTECTION.

        Only OPS Managers and System Administrators can modify price_unit.
        """
        # Check if price_unit is being modified
        if 'price_unit' in vals:
            # Skip check for superuser/admin
            if not (self.env.su or self.env.user.has_group('base.group_system')):
                # Check if user is OPS Manager
                if not self.env.user.has_group('ops_matrix_core.group_ops_manager'):
                    raise UserError(_(
                        "PRICE PROTECTION: You are not authorized to change unit prices.\n\n"
                        "Only Managers and Administrators can modify the Unit Price field.\n"
                        "Please contact your manager if a price adjustment is required."
                    ))

        return super().write(vals)

    @api.onchange('order_id')
    def _onchange_order_id_propagate_dimensions(self):
        """When order_id changes, inherit the order's matrix dimensions."""
        if self.order_id:
            if not self.ops_branch_id and self.order_id.ops_branch_id:
                self.ops_branch_id = self.order_id.ops_branch_id
            if not self.ops_business_unit_id and self.order_id.ops_business_unit_id:
                self.ops_business_unit_id = self.order_id.ops_business_unit_id

    @api.constrains('product_id', 'order_id')
    def _check_product_branch_activation(self):
        """
        BRANCH ACTIVATION GOVERNANCE: Ensure products are activated for the order's branch.
        """
        for line in self:
            # Skip validation for superuser/admin
            if self.env.is_superuser() or self.env.user.has_group('base.group_system'):
                continue

            if not line.product_id or not line.order_id:
                continue

            product_tmpl = line.product_id.product_tmpl_id
            order_branch = line.order_id.ops_branch_id

            # Check if product is a Global Master
            if product_tmpl.ops_is_global_master:
                # Check if product is activated for this branch
                if order_branch and order_branch not in product_tmpl.ops_branch_activation_ids:
                    raise ValidationError(_(
                        "BRANCH ACTIVATION BLOCK: Product '%(product)s' is a Global Master "
                        "and is NOT activated for branch '%(branch)s'.\n\n"
                        "Global Master products must be explicitly activated for each branch "
                        "before they can be sold in that branch.\n\n"
                        "Contact Master Data Management to request activation."
                    ) % {
                        'product': product_tmpl.name,
                        'branch': order_branch.display_name,
                    })
