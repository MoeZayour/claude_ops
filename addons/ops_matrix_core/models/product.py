from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.api import Environment


# ==========================================================================
# PRODUCT CATEGORY - INVENTORY VALUATION STANDARDS ENFORCEMENT
# ==========================================================================
class ProductCategory(models.Model):
    """
    Extend product.category to enforce OPS Framework inventory standards.

    CRITICAL: Forces FIFO costing and real-time valuation for all categories.
    This ensures consistent inventory valuation across all branches and prevents
    accounting discrepancies from manual valuation method changes.
    """
    _inherit = 'product.category'

    # Override property fields with strict defaults and readonly
    property_cost_method = fields.Selection(
        selection_add=[],
        default='fifo',
        readonly=True,
        help='Costing method is enforced to FIFO by OPS Framework governance. '
             'This ensures consistent inventory valuation across all branches.'
    )

    property_valuation = fields.Selection(
        selection_add=[],
        default='real_time',
        readonly=True,
        help='Valuation type is enforced to Real-Time (Automated) by OPS Framework governance. '
             'This ensures inventory movements create immediate accounting entries.'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Force FIFO and real-time valuation on category creation."""
        for vals in vals_list:
            # Always enforce FIFO costing method
            vals['property_cost_method'] = 'fifo'
            # Always enforce real-time valuation
            vals['property_valuation'] = 'real_time'
        return super().create(vals_list)

    def write(self, vals):
        """Prevent changes to costing method and valuation type."""
        # Block any attempt to change cost method or valuation
        if 'property_cost_method' in vals and vals['property_cost_method'] != 'fifo':
            raise ValidationError(_(
                "OPS Framework Governance: Costing method must remain FIFO. "
                "This is enforced to ensure consistent inventory valuation across all branches."
            ))
        if 'property_valuation' in vals and vals['property_valuation'] != 'real_time':
            raise ValidationError(_(
                "OPS Framework Governance: Valuation type must remain Real-Time (Automated). "
                "This is enforced to ensure inventory movements create immediate accounting entries."
            ))
        # Force correct values even if passed
        vals['property_cost_method'] = 'fifo'
        vals['property_valuation'] = 'real_time'
        return super().write(vals)


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'ops.field.visibility.mixin']

    # Override default_code - unique constraint enforced via SQL
    # NOTE: required=False to not break existing data, enforced via view/onchange
    default_code = fields.Char(
        string='Internal Reference',
        index=True,
        copy=False,
        help='Unique product SKU/code used for inventory tracking. '
             'This field must be unique across all products.'
    )

    @api.constrains('default_code')
    def _check_default_code_unique(self):
        """Validate SKU uniqueness with detailed error message."""
        for product in self:
            if product.default_code:
                # Check for duplicates (excluding self)
                duplicate = self.search([
                    ('default_code', '=', product.default_code),
                    ('id', '!=', product.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        "SKU '%(sku)s' is already used by product '%(product)s'. "
                        "Each product must have a unique Internal Reference."
                    ) % {
                        'sku': product.default_code,
                        'product': duplicate.name
                    })

    # Matrix Integration: Link to Business Unit for Product Silo (THE MASTER)
    # NOTE: Required=False at model level to not break existing data,
    # but enforced via view attributes and onchange validation
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        index=True,
        tracking=True,
        help="Business Unit this product belongs to. "
             "This is the primary matrix dimension for product ownership and access control. "
             "Products can only be accessed by users with permission to this Business Unit."
    )

    # Alias for consistency with OPS naming conventions
    ops_business_unit_id = fields.Many2one(
        related='business_unit_id',
        string='OPS Business Unit',
        store=True,
        readonly=True,
        help="Alias of business_unit_id for OPS Framework consistency."
    )

    # ==========================================================================
    # MASTER DATA GOVERNANCE: Global Master & Branch Activation
    # ==========================================================================
    ops_is_global_master = fields.Boolean(
        string='Global Master Product',
        default=False,
        tracking=True,
        help='Mark this product as a Global Master product. '
             'Global Master products are managed centrally and require branch activation. '
             'When enabled, this product must be explicitly activated for each branch '
             'before it can be used in Sales Orders for that branch.'
    )

    ops_branch_activation_ids = fields.Many2many(
        'ops.branch',
        'product_template_branch_activation_rel',
        'product_id',
        'branch_id',
        string='Activated Branches',
        tracking=True,
        help='Branches where this product is activated and can be sold. '
             'If empty and product is a Global Master, it cannot be sold anywhere. '
             'Products must be activated for a branch to appear in that branch\'s Sales Orders. '
             'This enables central product management with regional deployment control.'
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
    def default_get(self, fields_list):
        """
        Override default_get to pre-fill OPS Matrix fields from current user context.

        Auto-populates:
        - business_unit_id: User's default business unit
        - ops_branch_activation_ids: User's primary branch (pre-selected)
        """
        defaults = super().default_get(fields_list)
        user = self.env.user

        # Pre-fill Business Unit from user's default
        if 'business_unit_id' in fields_list and not defaults.get('business_unit_id'):
            default_bu = self._search_default_business_unit()
            if default_bu:
                defaults['business_unit_id'] = default_bu.id

        # Pre-fill Branch Activation with user's primary branch
        if 'ops_branch_activation_ids' in fields_list and not defaults.get('ops_branch_activation_ids'):
            if user.primary_branch_id:
                # Use (6, 0, [ids]) format to set Many2many default
                defaults['ops_branch_activation_ids'] = [(6, 0, [user.primary_branch_id.id])]
            elif user.ops_allowed_branch_ids:
                # Fallback: use first allowed branch
                defaults['ops_branch_activation_ids'] = [(6, 0, [user.ops_allowed_branch_ids[0].id])]

        return defaults
    
    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """
        Override search to filter products by user's business unit AND branch access.

        PERFORMANCE NOTE: Uses pure SQL domain construction (not Python filtering).
        This ensures the ORM can optimize the query at DB level and the
        scheduler doesn't suffer from excessive Python processing.

        Logic:
        - Superusers bypass filtering entirely
        - Regular users see products based on:
          1. Business Unit filter: (product in their BU) OR (product has no BU)
          2. Branch Activation filter: For Global Master products, only show if
             activated for user's branch OR product is not a global master

        :param domain: Original domain filter
        :param offset: Record offset for pagination
        :param limit: Maximum records to return
        :param order: Order by clause
        :param count: If True, return count instead of records
        :return: Filtered RecordSet or count
        """
        # Get user's allowed access using unified access method
        user = self.env.user
        access = user.get_effective_matrix_access()
        business_units = access.get('business_units', self.env['ops.business.unit'])
        user_branches = access.get('branches', self.env['ops.branch'])

        # PURE SQL DOMAIN CONSTRUCTION (No Python filtering)
        if not self.env.is_superuser():
            # 1. Business Unit filtering
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

            # 2. Branch Activation filtering for Global Master products
            # Products visible if: (NOT a global master) OR (activated for user's branch)
            if user_branches:
                branch_domain = [
                    '|',
                    ('ops_is_global_master', '=', False),
                    ('ops_branch_activation_ids', 'in', user_branches.ids)
                ]
                domain = branch_domain + domain
            else:
                # User has no branches - only show non-global-master products
                domain = [('ops_is_global_master', '=', False)] + domain

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
    _name = 'product.product'
    _inherit = ['product.product', 'ops.field.visibility.mixin']

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """
        Override search to filter product variants by business unit AND branch access.

        PERFORMANCE NOTE: Filters through the product template's fields
        using pure SQL domain (not Python loops). Maintains consistency with
        ProductTemplate filtering.

        :param domain: Original domain filter
        :param offset: Record offset for pagination
        :param limit: Maximum records to return
        :param order: Order by clause
        :param count: If True, return count instead of records
        :return: Filtered RecordSet or count
        """
        # Get user's allowed access
        user = self.env.user
        access = user.get_effective_matrix_access()
        business_units = access.get('business_units', self.env['ops.business.unit'])
        user_branches = access.get('branches', self.env['ops.branch'])

        # PURE SQL DOMAIN CONSTRUCTION through product template
        if not self.env.is_superuser():
            # 1. Business Unit filtering
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

            # 2. Branch Activation filtering for Global Master products
            if user_branches:
                branch_domain = [
                    '|',
                    ('product_tmpl_id.ops_is_global_master', '=', False),
                    ('product_tmpl_id.ops_branch_activation_ids', 'in', user_branches.ids)
                ]
                domain = branch_domain + domain
            else:
                # User has no branches - only show non-global-master products
                domain = [('product_tmpl_id.ops_is_global_master', '=', False)] + domain

        # Handle count parameter (removed in Odoo 19)
        if count:
            return super().search_count(domain)
        else:
            return super().search(domain, offset=offset, limit=limit, order=order)
