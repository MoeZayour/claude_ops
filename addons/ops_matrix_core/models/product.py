from odoo import models, fields, api
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.api import Environment

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Matrix Integration: Link to Business Unit for Product Silo
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        help="Business Unit this product belongs to for Matrix access control.",
        tracking=True
    )
    
    # The Cost Shield: Field-Level Security for Product Costs
    # These computed fields control visibility and editability of sensitive cost information
    can_user_access_cost_prices = fields.Boolean(
        string='Can Access Cost Prices',
        compute='_compute_can_user_access_cost_prices',
        store=False,
        help="Determines if the current user can view cost prices based on their Persona authority."
    )
    
    can_user_modify_product_master = fields.Boolean(
        string='Can Modify Product Master',
        compute='_compute_can_user_modify_product_master',
        store=False,
        help="Determines if the current user can edit product master data (costs, suppliers) based on their Persona authority."
    )
    
    @api.depends_context('uid')
    def _compute_can_user_access_cost_prices(self):
        """
        Check if user has authority to view cost prices.
        
        Security Logic:
        - System administrators (base.group_system) always have access
        - Other users must have 'can_access_cost_prices' authority flag in their active Persona
        - Users with no personas are denied access by default
        
        This implements "The Cost Shield" anti-fraud measure.
        """
        for record in self:
            # Administrators bypass all restrictions
            if self.env.user.has_group('base.group_system'):
                record.can_user_access_cost_prices = True
            else:
                # Check persona authority flag
                record.can_user_access_cost_prices = self.env.user.has_ops_authority('can_access_cost_prices')
    
    @api.depends_context('uid')
    def _compute_can_user_modify_product_master(self):
        """
        Check if user has authority to modify product master data.
        
        Security Logic:
        - System administrators (base.group_system) always have access
        - Other users must have 'can_modify_product_master' authority flag in their active Persona
        - Users with no personas cannot modify product master data
        - This controls editing of cost prices, supplier information, and other sensitive fields
        
        This implements "The Cost Shield" anti-fraud measure.
        """
        for record in self:
            # Administrators bypass all restrictions
            if self.env.user.has_group('base.group_system'):
                record.can_user_modify_product_master = True
            else:
                # Check persona authority flag
                record.can_user_modify_product_master = self.env.user.has_ops_authority('can_modify_product_master')
    
    @api.model
    def _search_default_business_unit(self):
        """Get default business unit from user's access"""
        user = self.env.user
        access = user.get_effective_matrix_access()
        business_units = access.get('business_units', self.env['ops.business.unit'])
        if business_units:
            return business_units[0]
        return None
    
    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """
        Override search to filter products by user's business unit access.
        
        PERFORMANCE NOTE: Uses pure SQL domain construction (not Python filtering).
        This ensures the ORM can optimize the query at DB level and the
        scheduler doesn't suffer from excessive Python processing.
        
        Logic:
        - Superusers bypass filtering entirely
        - Regular users see: (product in their BU) OR (product has no BU)
        - Uses domain syntax to let ORM handle DB-level filtering
        
        :param domain: Original domain filter
        :param offset: Record offset for pagination
        :param limit: Maximum records to return
        :param order: Order by clause
        :param count: If True, return count instead of records
        :return: Filtered RecordSet or count
        """
        # Get user's allowed business units using unified access method
        user = self.env.user
        access = user.get_effective_matrix_access()
        business_units = access.get('business_units', self.env['ops.business.unit'])
        
        # PURE SQL DOMAIN CONSTRUCTION (No Python filtering)
        # Build domain: products are visible if they belong to user's BU OR have no BU assigned
        if not self.env.is_superuser():
            if business_units:
                # Construct domain: (BU match) OR (no BU assigned)
                bu_domain = [
                    '|',
                    ('business_unit_id', 'in', business_units.ids),
                    ('business_unit_id', '=', False)
                ]
                # Merge with original domain using AND logic
                domain = bu_domain + domain
            else:
                # User has no business units, show only products with no BU
                domain = [('business_unit_id', '=', False)] + domain
        
        # Handle count parameter (removed in Odoo 19)
        if count:
            return super().search_count(domain)
        else:
            return super().search(domain, offset=offset, limit=limit, order=order)
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Auto-assign business unit from current user if not specified.
        
        Ensures new products are automatically scoped to the creating user's
        business unit (if applicable), simplifying the UI experience.
        """
        for vals in vals_list:
            if not vals.get('business_unit_id') and not self.env.is_superuser():
                default_bu = self._search_default_business_unit()
                if default_bu:
                    vals['business_unit_id'] = default_bu.id
        return super().create(vals_list)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """
        Override search to filter product variants by business unit access.
        
        PERFORMANCE NOTE: Filters through the product template's business_unit_id
        using pure SQL domain (not Python loops). Maintains consistency with
        ProductTemplate filtering.
        
        :param domain: Original domain filter
        :param offset: Record offset for pagination
        :param limit: Maximum records to return
        :param order: Order by clause
        :param count: If True, return count instead of records
        :return: Filtered RecordSet or count
        """
        # Get user's allowed business units
        user = self.env.user
        access = user.get_effective_matrix_access()
        business_units = access.get('business_units', self.env['ops.business.unit'])
        
        # PURE SQL DOMAIN CONSTRUCTION through product template
        # Filter product variants by their template's business unit
        if not self.env.is_superuser():
            if business_units:
                # Construct domain: (product's template BU matches) OR (no BU assigned)
                bu_domain = [
                    '|',
                    ('product_tmpl_id.business_unit_id', 'in', business_units.ids),
                    ('product_tmpl_id.business_unit_id', '=', False)
                ]
                domain = bu_domain + domain
            else:
                # User has no business units, show only products with no BU
                domain = [('product_tmpl_id.business_unit_id', '=', False)] + domain
        
        # Handle count parameter (removed in Odoo 19)
        if count:
            return super().search_count(domain)
        else:
            return super().search(domain, offset=offset, limit=limit, order=order)
