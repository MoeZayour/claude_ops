from odoo import models, fields, api
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.api import Environment

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # Matrix Integration: Branch and Business Unit for Pricing Matrix
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        help="Branch this pricelist applies to for Matrix pricing.",
        tracking=True,
        ondelete='set null',
        index=True,
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        help="Business Unit this pricelist applies to for Matrix pricing.",
        tracking=True
    )
    
    ops_is_matrix_pricelist = fields.Boolean(
        string='Matrix Pricelist',
        default=False,
        help='If checked, this pricelist is managed by the Matrix pricing engine'
    )
    
    ops_priority = fields.Integer(
        string='Matrix Priority',
        default=10,
        help='Priority for auto-selection (lower = higher priority)'
    )
    
    @api.model
    def _get_applicable_pricelist(self, partner_id=None, branch_id=None, business_unit_id=None, company_id=None):
        """
        Get the most appropriate pricelist based on matrix dimensions.
        
        Selection priority:
        1. Branch + Business Unit exact match
        2. Business Unit only match
        3. Branch only match
        4. Partner-specific pricelist
        5. Default company pricelist
        """
        domain = [('active', '=', True)]
        
        if company_id:
            domain.append(('company_id', '=', company_id))
        
        candidates = []
        
        # Priority 1: Branch + Business Unit exact match
        if branch_id and business_unit_id:
            exact_match = self.search([
                *domain,
                ('ops_branch_id', '=', branch_id),
                ('ops_business_unit_id', '=', business_unit_id),
                ('ops_is_matrix_pricelist', '=', True)
            ], order='ops_priority ASC', limit=1)
            if exact_match:
                return exact_match
        
        # Priority 2: Business Unit only
        if business_unit_id:
            bu_match = self.search([
                *domain,
                ('ops_business_unit_id', '=', business_unit_id),
                ('ops_branch_id', '=', False),
                ('ops_is_matrix_pricelist', '=', True)
            ], order='ops_priority ASC', limit=1)
            if bu_match:
                return bu_match
        
        # Priority 3: Branch only
        if branch_id:
            branch_match = self.search([
                *domain,
                ('ops_branch_id', '=', branch_id),
                ('ops_business_unit_id', '=', False),
                ('ops_is_matrix_pricelist', '=', True)
            ], order='ops_priority ASC', limit=1)
            if branch_match:
                return branch_match
        
        # Priority 4: Partner-specific pricelist
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.property_product_pricelist:
                return partner.property_product_pricelist
        
        # Priority 5: Default company pricelist
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company
        if company.sale_pricelist_id:
            return company.sale_pricelist_id
        
        # Fallback: First active pricelist
        return self.search(domain, limit=1)
    
    def _compute_price_from_matrix_context(self, product_id, quantity=1, partner_id=None):
        """
        Compute product price considering matrix context.
        Called during sale order line price calculation.
        """
        self.ensure_one()
        
        # Get base pricelist pricing
        pricelist_item = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', self.id),
            ('product_id', '=', product_id)
        ], limit=1)
        
        if pricelist_item:
            return pricelist_item.compute_price(product_id, quantity)
        
        # Return product list price as fallback
        product = self.env['product.product'].browse(product_id)
        return product.list_price
    
    @api.model
    def _get_pricelist_for_sale_order(self, partner_id, branch_id=None, business_unit_id=None):
        """
        Determine the pricelist for a sale order based on matrix dimensions.
        This is called during SO creation to auto-select the appropriate pricelist.
        """
        # Get user's current matrix context if not provided
        if not branch_id or not business_unit_id:
            user_context = self.env.user.get_effective_matrix_access()
            if not branch_id and user_context['branch_ids']:
                branch_id = user_context['branch_ids'][0].id
            if not business_unit_id and user_context['business_unit_ids']:
                business_unit_id = user_context['business_unit_ids'][0].id
        
        # Find appropriate pricelist
        company_id = self.env.company.id
        pricelist = self._get_applicable_pricelist(
            partner_id=partner_id,
            branch_id=branch_id,
            business_unit_id=business_unit_id,
            company_id=company_id
        )
        
        return pricelist if pricelist else self.env.company.sale_pricelist_id
