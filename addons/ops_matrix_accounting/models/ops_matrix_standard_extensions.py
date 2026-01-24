import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        index=True,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this sale"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        index=True,
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
        index=True,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this purchase"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        index=True,
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
        index=True,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this transfer"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        index=True,
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
        index=True,
        default=lambda self: self._get_default_branch(),
        help="Branch responsible for this entry"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        index=True,
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

    # =========================================================================
    # ZERO-TRUST SECURITY: Matrix Dimension Validation
    # =========================================================================

    def _validate_matrix_dimensions(self):
        """
        Validate that required matrix dimensions are set before posting.
        This enforces Zero-Trust Governance - no financial transaction
        can be posted without proper Branch/BU classification.
        """
        for move in self:
            # Only validate for actual financial transactions (not misc entries)
            if move.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                if not move.ops_branch_id:
                    raise UserError(
                        f"SECURITY BLOCK: Cannot post {move.name or 'invoice'}.\n\n"
                        f"Matrix Governance requires a Branch to be assigned.\n"
                        f"Please select a Branch before posting this transaction."
                    )
                if not move.ops_business_unit_id:
                    raise UserError(
                        f"SECURITY BLOCK: Cannot post {move.name or 'invoice'}.\n\n"
                        f"Matrix Governance requires a Business Unit to be assigned.\n"
                        f"Please select a Business Unit before posting this transaction."
                    )

    def action_post(self):
        """Override to enforce Zero-Trust Matrix validation before posting."""
        self._validate_matrix_dimensions()
        return super().action_post()

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

        # Invalidate report caches on new financial entries
        if any(move.state == 'posted' for move in moves):
            self._invalidate_consolidated_report_cache()

        return moves

    def write(self, vals):
        """Invalidate report caches when financial data changes."""
        result = super().write(vals)

        # Invalidate if critical fields changed
        cache_invalidation_fields = [
            'state',  # Posted/cancelled
            'amount_total',  # Amount changed
            'ops_branch_id',  # Dimension changed
            'ops_business_unit_id',  # Dimension changed
            'date',  # Period changed
        ]

        if any(field in vals for field in cache_invalidation_fields):
            self._invalidate_consolidated_report_cache()

        return result

    def _invalidate_consolidated_report_cache(self):
        """
        Clear cached consolidated reports for affected companies.

        Note: Since OpsCompanyConsolidation is a TransientModel, records
        auto-expire naturally. This method logs the invalidation event
        and could clear specific caches if persistent caching is added later.
        """
        companies = self.mapped('company_id')
        if companies:
            _logger.info(
                f"🧹 Report caches invalidated for companies: {companies.mapped('name')} "
                f"due to financial data change"
            )

            # Clear wizard caches for affected companies
            wizards = self.env['ops.company.consolidation'].search([
                ('company_id', 'in', companies.ids),
                ('cached_data', '!=', False)
            ])

            if wizards:
                wizards.write({
                    'cached_data': False,
                    'cache_timestamp': False
                })
                _logger.info(f"   Cleared {len(wizards)} cached report(s)")

            # Also clear matrix wizard caches (if model exists)
            if 'ops.profitability.matrix.wizard' in self.env:
                matrix_wizards = self.env['ops.profitability.matrix.wizard'].search([
                    ('company_id', 'in', companies.ids),
                    ('cached_data', '!=', False)
                ])
                if matrix_wizards:
                    matrix_wizards.write({
                        'cached_data': False,
                        'cache_timestamp': False
                    })
                    _logger.info(f"   Cleared {len(matrix_wizards)} cached matrix report(s)")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        index=True,
        default=lambda self: self._get_default_branch(),
        help="Branch for this journal item"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=False,
        index=True,
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

    # =========================================================================
    # ZERO-TRUST SECURITY: Line-level Matrix Validation
    # =========================================================================

    @api.constrains('ops_business_unit_id', 'account_id')
    def _check_revenue_expense_bu(self):
        """
        Validate that revenue/expense lines have Business Unit assigned.
        This ensures proper profit center tracking for P&L items.
        """
        for line in self:
            # Skip if no account (happens during creation)
            if not line.account_id:
                continue

            # Check if this is a revenue or expense account (P&L accounts)
            account_type = line.account_id.account_type
            pnl_types = (
                'income', 'income_other',
                'expense', 'expense_depreciation', 'expense_direct_cost'
            )

            if account_type in pnl_types:
                # Only enforce on posted moves to allow draft editing
                if line.move_id.state == 'posted' and not line.ops_business_unit_id:
                    raise ValidationError(
                        f"SECURITY BLOCK: Revenue/Expense line requires Business Unit.\n\n"
                        f"Account: {line.account_id.display_name}\n"
                        f"Matrix Governance requires all P&L items to be assigned to a Business Unit "
                        f"for proper profit center tracking."
                    )
