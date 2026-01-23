# -*- coding: utf-8 -*-
"""
OPS Matrix Core - Stock Move Extensions
========================================

Enhanced stock move handling for multi-branch, multi-BU operations.
Provides automatic tagging of accounting entries for inter-branch transfers.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = ['stock.move', 'ops.field.visibility.mixin']

    # ==========================================================================
    # LEGACY RELATED FIELDS (for backward compatibility with picking)
    # ==========================================================================
    branch_id = fields.Many2one(
        'res.company',
        string='Branch (Legacy)',
        related='picking_id.branch_id',
        store=True,
        readonly=True,
        help="Branch related to this stock move (legacy field)"
    )

    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit (Legacy)',
        related='picking_id.business_unit_id',
        store=True,
        readonly=True,
        help="Business unit from the source document (legacy field)"
    )

    # ==========================================================================
    # OPS MATRIX FIELDS: Source and Destination Dimensions
    # ==========================================================================
    ops_source_branch_id = fields.Many2one(
        'ops.branch',
        string='Source Branch',
        compute='_compute_ops_branch_dimensions',
        store=True,
        readonly=True,
        help='Branch from which the stock is being moved (source location branch)'
    )

    ops_source_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Source Business Unit',
        compute='_compute_ops_branch_dimensions',
        store=True,
        readonly=True,
        help='Business Unit from which the stock is being moved'
    )

    ops_dest_branch_id = fields.Many2one(
        'ops.branch',
        string='Destination Branch',
        compute='_compute_ops_branch_dimensions',
        store=True,
        readonly=True,
        help='Branch to which the stock is being moved (destination location branch)'
    )

    ops_dest_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Destination Business Unit',
        compute='_compute_ops_branch_dimensions',
        store=True,
        readonly=True,
        help='Business Unit to which the stock is being moved'
    )

    ops_is_inter_branch = fields.Boolean(
        string='Inter-Branch Transfer',
        compute='_compute_ops_branch_dimensions',
        store=True,
        readonly=True,
        help='True if this move transfers stock between different branches'
    )

    @api.depends('location_id', 'location_dest_id', 'picking_id',
                 'picking_id.ops_branch_id', 'picking_id.ops_business_unit_id')
    def _compute_ops_branch_dimensions(self):
        """
        Compute source and destination branch/BU dimensions.

        Logic:
        1. For source, use location's warehouse branch, fall back to picking's branch
        2. For destination, use dest_location's warehouse branch, fall back to picking's branch
        3. Inter-branch flag is set when source != destination branch
        """
        for move in self:
            # Source dimensions from source location's warehouse
            source_branch = False
            source_bu = False
            if move.location_id and move.location_id.warehouse_id:
                warehouse = move.location_id.warehouse_id
                # Try to find ops.branch linked to warehouse
                branch = self.env['ops.branch'].search([
                    ('warehouse_id', '=', warehouse.id)
                ], limit=1)
                if branch:
                    source_branch = branch

            # Fall back to picking's branch if no warehouse branch
            if not source_branch and move.picking_id and move.picking_id.ops_branch_id:
                source_branch = move.picking_id.ops_branch_id

            # Source BU from picking
            if move.picking_id and move.picking_id.ops_business_unit_id:
                source_bu = move.picking_id.ops_business_unit_id

            # Destination dimensions from destination location's warehouse
            dest_branch = False
            dest_bu = False
            if move.location_dest_id and move.location_dest_id.warehouse_id:
                warehouse = move.location_dest_id.warehouse_id
                # Try to find ops.branch linked to warehouse
                branch = self.env['ops.branch'].search([
                    ('warehouse_id', '=', warehouse.id)
                ], limit=1)
                if branch:
                    dest_branch = branch

            # Fall back to picking's branch if no warehouse branch
            if not dest_branch and move.picking_id and move.picking_id.ops_branch_id:
                dest_branch = move.picking_id.ops_branch_id

            # Destination BU from picking (same as source for single-branch operations)
            if move.picking_id and move.picking_id.ops_business_unit_id:
                dest_bu = move.picking_id.ops_business_unit_id

            # Set computed fields
            move.ops_source_branch_id = source_branch.id if source_branch else False
            move.ops_source_business_unit_id = source_bu.id if source_bu else False
            move.ops_dest_branch_id = dest_branch.id if dest_branch else False
            move.ops_dest_business_unit_id = dest_bu.id if dest_bu else False

            # Determine if this is an inter-branch transfer
            move.ops_is_inter_branch = bool(
                source_branch and dest_branch and source_branch.id != dest_branch.id
            )

    def _prepare_account_move_vals(self):
        """
        Override to add comprehensive branch and business unit tagging to accounting entries.

        For inter-branch transfers:
        - DEBIT line (inventory increase): Tagged with DESTINATION branch/BU
        - CREDIT line (inventory decrease): Tagged with SOURCE branch/BU

        This enables proper financial reporting by branch/BU including inter-company transfers.
        """
        vals = super(StockMove, self)._prepare_account_move_vals()

        # Determine primary branch/BU for the account move header
        # Use destination branch for incoming, source branch for outgoing
        primary_branch = self.ops_dest_branch_id or self.ops_source_branch_id
        primary_bu = self.ops_dest_business_unit_id or self.ops_source_business_unit_id

        # Add matrix dimensions to account move header
        if primary_branch:
            vals['ops_branch_id'] = primary_branch.id
            # Also set legacy field if it exists
            if hasattr(self.env['account.move'], 'branch_id'):
                vals['branch_id'] = primary_branch.company_id.id if primary_branch.company_id else False
        if primary_bu:
            vals['ops_business_unit_id'] = primary_bu.id
            # Also set legacy field
            if hasattr(self.env['account.move'], 'business_unit_id'):
                vals['business_unit_id'] = primary_bu.id

        # Add dimensions to all move lines with inter-branch awareness
        if 'line_ids' in vals:
            for idx, line in enumerate(vals['line_ids']):
                if len(line) > 2 and isinstance(line[2], dict):
                    line_vals = line[2]

                    # Determine branch/BU for this line based on debit/credit
                    # DEBIT = inventory increase = destination
                    # CREDIT = inventory decrease = source
                    debit = line_vals.get('debit', 0)
                    credit = line_vals.get('credit', 0)

                    if self.ops_is_inter_branch:
                        if debit > 0:
                            # Debit line - tag with destination
                            line_branch = self.ops_dest_branch_id
                            line_bu = self.ops_dest_business_unit_id
                        else:
                            # Credit line - tag with source
                            line_branch = self.ops_source_branch_id
                            line_bu = self.ops_source_business_unit_id
                    else:
                        # Same branch - use primary
                        line_branch = primary_branch
                        line_bu = primary_bu

                    if line_branch:
                        line_vals['ops_branch_id'] = line_branch.id
                        if hasattr(self.env['account.move.line'], 'branch_id'):
                            line_vals['branch_id'] = line_branch.company_id.id if line_branch.company_id else False
                    if line_bu:
                        line_vals['ops_business_unit_id'] = line_bu.id
                        if hasattr(self.env['account.move.line'], 'business_unit_id'):
                            line_vals['business_unit_id'] = line_bu.id

        # Log inter-branch transfers for audit trail
        if self.ops_is_inter_branch:
            _logger.info(
                "Inter-Branch Transfer Accounting: Move %s - %s -> %s (Product: %s, Qty: %s)",
                self.id,
                self.ops_source_branch_id.display_name if self.ops_source_branch_id else 'N/A',
                self.ops_dest_branch_id.display_name if self.ops_dest_branch_id else 'N/A',
                self.product_id.display_name if self.product_id else 'N/A',
                self.product_uom_qty
            )

        return vals

    def _action_done(self, cancel_backorder=False):
        """
        Override _action_done to ensure inter-branch accounting is properly recorded.
        """
        res = super()._action_done(cancel_backorder=cancel_backorder)

        # Post-process inter-branch moves for additional tracking
        inter_branch_moves = self.filtered(lambda m: m.ops_is_inter_branch)
        if inter_branch_moves:
            for move in inter_branch_moves:
                _logger.info(
                    "Inter-Branch Stock Move Completed: %s -> %s, Product: %s, Qty: %s",
                    move.ops_source_branch_id.display_name if move.ops_source_branch_id else 'Source',
                    move.ops_dest_branch_id.display_name if move.ops_dest_branch_id else 'Destination',
                    move.product_id.display_name,
                    move.quantity
                )

        return res
