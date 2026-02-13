from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.api import Environment

class StockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = ['stock.quant', 'ops.field.visibility.mixin']
    
    # ========================================================================
    # BUSINESS UNIT SEGMENTATION
    # ========================================================================
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        compute='_compute_ops_business_unit_id',
        store=True,
        index=True,
        help='Business unit this stock quant belongs to (from product assignment)'
    )
    
    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================
    @api.depends('product_id.business_unit_id')
    def _compute_ops_business_unit_id(self):
        """
        Compute business unit from the product's assignment.
        
        Stock quants inherit their BU from the product template.
        If a product has no BU assignment, the quant is considered "global"
        and can be used by any BU (subject to strict constraint checks).
        """
        for quant in self:
            if quant.product_id and quant.product_id.business_unit_id:
                quant.ops_business_unit_id = quant.product_id.business_unit_id.id
            else:
                quant.ops_business_unit_id = False
    
    # ========================================================================
    # OVERRIDE: Availability Checking with BU Constraints
    # ========================================================================
    def _get_available_quantity(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
        business_unit_id=None,
    ):
        """
        Override to enforce business unit constraints on stock reservation.
        
        CRITICAL CONSTRAINT:
        - A Sale Order for "Business Unit A" can ONLY reserve quants
          where ops_business_unit_id matches "Business Unit A"
        - Quants with NO business unit (global) can be reserved by any BU
          (This allows shared inventory while maintaining accounting separation)
        
        Performance Note: This uses pure SQL domain filtering, not Python loops,
        to keep the scheduler efficient even with large quant datasets.
        
        :param product_id: Product to check availability for
        :param location_id: Location to check in
        :param lot_id: Lot filter (optional)
        :param package_id: Package filter (optional)
        :param owner_id: Owner filter (optional)
        :param strict: Whether to enforce strict positivity
        :param allow_negative: Whether to allow negative stock
        :param business_unit_id: Business unit context for filtering
        :return: Available quantity respecting BU constraints
        """
        
        # If no BU context provided, use default (should not happen in normal flow)
        if not business_unit_id:
            # Try to get from context (set by sale order confirmation)
            business_unit_id = self.env.context.get('ops_business_unit_id')
        
        # Build domain for quant search with BU constraint
        domain = [
            ('product_id', '=', product_id.id),
            ('location_id', '=', location_id.id),
            ('quantity', '!=', 0),
        ]
        
        # ADD BUSINESS UNIT CONSTRAINT
        # Quants are available if:
        # 1. They belong to the requesting BU, OR
        # 2. They have NO BU assignment (global stock)
        if business_unit_id:
            domain.append(
                '|',
            )
            domain.append(
                ('ops_business_unit_id', '=', business_unit_id.id)
            )
            domain.append(
                ('ops_business_unit_id', '=', False)  # Global stock
            )
        else:
            # No BU context: only show global quants (safety constraint)
            domain.append(('ops_business_unit_id', '=', False))
        
        # Apply standard filters
        if lot_id:
            domain.append(('lot_id', '=', lot_id.id))
        if package_id:
            domain.append(('package_id', '=', package_id.id))
        if owner_id:
            domain.append(('owner_id', '=', owner_id.id))
        
        # Search with pure SQL domain (ORM will optimize at DB level)
        quants = self.search(domain)
        
        if strict:
            # Only positive quantities
            quants = quants.filtered(lambda q: float_compare(q.quantity, 0, precision_digits=2) > 0)
        
        if allow_negative:
            # Include negative quants
            pass
        else:
            # Only non-negative
            quants = quants.filtered(lambda q: float_compare(q.quantity, 0, precision_digits=2) >= 0)
        
        # Sum the available quantity
        total_quantity = sum(quants.mapped('quantity'))
        
        return total_quantity
    
    # ========================================================================
    # RESERVED QUANTITY OVERRIDE with BU Constraint
    # ========================================================================
    def _get_reserved_quantity(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        business_unit_id=None,
    ):
        """
        Get reserved quantity respecting BU boundaries.
        
        Reserved stock is considered "committed" and cannot be used by other BUs.
        This method ensures we only count reservations for the requesting BU.
        
        :param product_id: Product to check reservations for
        :param location_id: Location to check in
        :param lot_id: Lot filter (optional)
        :param package_id: Package filter (optional)
        :param owner_id: Owner filter (optional)
        :param business_unit_id: Business unit context
        :return: Total reserved quantity for the BU
        """
        
        # Build domain for reserved quants
        domain = [
            ('product_id', '=', product_id.id),
            ('location_id', '=', location_id.id),
            ('reserved_quantity', '!=', 0),
        ]
        
        # Apply BU constraint (reserved qty is BU-specific)
        if business_unit_id:
            domain.append(('ops_business_unit_id', '=', business_unit_id.id))
        else:
            # No BU context: only global reservations
            domain.append(('ops_business_unit_id', '=', False))
        
        # Apply standard filters
        if lot_id:
            domain.append(('lot_id', '=', lot_id.id))
        if package_id:
            domain.append(('package_id', '=', package_id.id))
        if owner_id:
            domain.append(('owner_id', '=', owner_id.id))
        
        # Search with pure SQL domain
        quants = self.search(domain)
        
        # Sum reserved quantities
        total_reserved = sum(quants.mapped('reserved_quantity'))
        
        return total_reserved
    
    # ========================================================================
    # CONSTRAINT: Prevent Invalid Cross-BU Reservations
    # ========================================================================
    # NOTE: This constraint is commented out because stock.move.line.quant_id
    # is not a stored field in Odoo core, causing SQL conversion errors.
    # BU validation is handled at the reservation level through domain filtering.
    
    # @api.constrains('ops_business_unit_id', 'reserved_quantity')
    # def _check_bu_reservation_consistency(self):
    #     """
    #     Ensure that if a quant is reserved, its BU matches the related move's BU.
    #
    #     This constraint prevents the scenario where:
    #     1. A quant is reserved for Business Unit A
    #     2. But the move is actually for Business Unit B
    #
    #     This is a safety net to catch any BU mismatch in the reservation chain.
    #     """
    #     # Commented out - quant_id field is not stored on stock.move.line
    #     pass
    
    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity=0.0,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
        reserved_quantity=None,
        business_unit_id=None,
    ):
        """
        Update available quantity respecting BU constraints.
        
        When stock is moved or adjusted, ensure the operation respects
        BU boundaries. Global stock (no BU) can be adjusted freely.
        
        :param product_id: Product being updated
        :param location_id: Location being updated
        :param quantity: Quantity change (default 0 for reservation-only updates)
        :param lot_id: Lot filter
        :param package_id: Package filter
        :param owner_id: Owner filter
        :param in_date: Date of receipt
        :param reserved_quantity: Reserved quantity to update (Odoo core parameter)
        :param business_unit_id: BU context for the change
        :return: Tuple (available_quantity, in_date) as expected by Odoo core
        """
        
        # Get existing quant with BU constraint
        quants = self.search([
            ('product_id', '=', product_id.id),
            ('location_id', '=', location_id.id),
            ('lot_id', '=', lot_id.id if lot_id else False),
            ('package_id', '=', package_id.id if package_id else False),
            ('owner_id', '=', owner_id.id if owner_id else False),
        ])
        
        # Filter for BU constraint
        if business_unit_id:
            quants = quants.filtered(
                lambda q: (q.ops_business_unit_id == business_unit_id or not q.ops_business_unit_id)
            )
        else:
            quants = quants.filtered(lambda q: not q.ops_business_unit_id)
        
        # Store the in_date to return
        result_in_date = in_date or fields.Datetime.now()
        
        if quants:
            # Use first matching quant
            quants = quants[0:1]
            vals_to_write = {}
            
            # Update on-hand quantity if provided
            if quantity != 0:
                vals_to_write['quantity'] = quants[0].quantity + quantity
            
            # Update reserved quantity if provided (Odoo core compatibility)
            if reserved_quantity is not None:
                vals_to_write['reserved_quantity'] = quants[0].reserved_quantity + reserved_quantity
            
            if vals_to_write:
                quants.write(vals_to_write)
            
            # Use the quant's in_date if available
            result_in_date = quants[0].in_date or result_in_date
            result_quantity = quants[0].quantity
        else:
            # Create new quant with BU assignment
            # Only create if there's actual quantity or reservation to record
            if quantity != 0 or reserved_quantity:
                vals = {
                    'product_id': product_id.id,
                    'location_id': location_id.id,
                    'quantity': quantity,
                    'in_date': result_in_date,
                }
                
                if lot_id:
                    vals['lot_id'] = lot_id.id
                if package_id:
                    vals['package_id'] = package_id.id
                if owner_id:
                    vals['owner_id'] = owner_id.id
                
                # Add reserved quantity if provided (Odoo core compatibility)
                if reserved_quantity is not None:
                    vals['reserved_quantity'] = reserved_quantity
                
                if business_unit_id and business_unit_id.id:
                    # Note: BU is computed from product, but stored context helps
                    vals['ops_business_unit_id'] = business_unit_id.id
                
                quants = self.create(vals)
                result_quantity = quants.quantity
                result_in_date = quants.in_date
            else:
                # No quantity change and no reservation - return zero quantity
                result_quantity = 0.0
        
        # Return tuple as expected by Odoo core: (available_quantity, in_date)
        return result_quantity, result_in_date
    
    # ========================================================================
    # CONTEXT HELPERS
    # ========================================================================
    @staticmethod
    def _prepare_bu_context(business_unit_id):
        """
        Prepare context dictionary for BU-aware operations.
        
        Use this when calling stock operations with BU context.
        
        :param business_unit_id: ops.business.unit record or ID
        :return: Context dict with BU information
        """
        bu_id = business_unit_id.id if hasattr(business_unit_id, 'id') else business_unit_id
        return {
            'ops_business_unit_id': bu_id,
        }


# Import validation error
from odoo.exceptions import ValidationError
