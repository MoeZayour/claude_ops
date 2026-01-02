# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OpsMatrixMixin(models.AbstractModel):
    """
    OPS Matrix Dimension Propagation Mixin
    
    This mixin provides matrix dimension tracking (Branch + Business Unit) for all transaction models.
    It automatically:
    - Tracks which branch and business unit a transaction belongs to
    - Computes the legal entity (company) from the branch
    - Generates analytic distribution for dual-dimension reporting
    - Provides default values from user's persona
    - Propagates dimensions to related records
    
    Usage:
        class SaleOrder(models.Model):
            _inherit = ['sale.order', 'ops.matrix.mixin']
            _name = 'sale.order'
    """
    _name = 'ops.matrix.mixin'
    _description = 'OPS Matrix Dimension Propagation Mixin'

    # =========================================================================
    # Matrix Dimension Fields
    # =========================================================================
    
    ops_company_id = fields.Many2one(
        'res.company',
        string='Legal Entity',
        compute='_compute_ops_company',
        store=True,
        help="Legal entity computed from branch"
    )
    
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', ondelete='set null', index=True)
    
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', ondelete='set null', index=True)

    ops_persona_id = fields.Many2one('ops.persona', string='Persona', ondelete='set null', index=True)
    
    ops_analytic_distribution = fields.Json(
        string='Matrix Analytic Distribution',
        compute='_compute_analytic_distribution',
        store=True,
        help="Analytic distribution for dual-dimension tracking (Branch + BU)"
    )

    # =========================================================================
    # Computed Methods
    # =========================================================================
    
    @api.depends('ops_branch_id')
    def _compute_ops_company(self):
        """
        Compute the legal entity (company) from the selected branch.
        """
        for record in self:
            if record.ops_branch_id and hasattr(record.ops_branch_id, 'company_id'):
                record.ops_company_id = record.ops_branch_id.company_id
            else:
                record.ops_company_id = False
    
    @api.depends('ops_branch_id', 'ops_business_unit_id')
    def _compute_analytic_distribution(self):
        """
        Compute analytic distribution for dual-dimension tracking using configurable weights.
        
        Format for Odoo 19: {'analytic_account_id': percentage}
        Example: {'123': 60, '456': 40} means 60% to Branch analytic account,
                                              40% to BU analytic account
        
        Weights are retrieved from ops.matrix.config for flexibility.
        """
        # Get configuration for weight calculation
        config = self.env['ops.matrix.config'].get_config()
        
        for record in self:
            # Get analytic account IDs
            branch_analytic_id = None
            bu_analytic_id = None
            
            # Extract branch analytic account
            if record.ops_branch_id:
                if hasattr(record.ops_branch_id, 'ops_analytic_account_id') and record.ops_branch_id.ops_analytic_account_id:
                    branch_analytic_id = record.ops_branch_id.ops_analytic_account_id.id
                elif hasattr(record.ops_branch_id, 'analytic_account_id') and record.ops_branch_id.analytic_account_id:
                    branch_analytic_id = record.ops_branch_id.analytic_account_id.id
            
            # Extract BU analytic account
            if record.ops_business_unit_id and record.ops_business_unit_id.analytic_account_id:
                bu_analytic_id = record.ops_business_unit_id.analytic_account_id.id
            
            # Use config to calculate distribution
            distribution = config.get_analytic_distribution(
                branch_id=branch_analytic_id,
                bu_id=bu_analytic_id
            )
            
            record.ops_analytic_distribution = distribution

    # =========================================================================
    # Default Value Methods
    # =========================================================================
    
    def _get_default_ops_branch(self):
        """
        Get default branch from user's persona or company.
        
        Priority:
        1. User's persona default branch
        2. User's default branch (if field exists)
        3. First branch of user's current company
        4. User's current company (fallback)
        """
        user = self.env.user
        
        # Try to get from persona, check if field exists on model first
        if 'persona_id' in self.env['res.users']._fields and hasattr(user, 'persona_id') and user.persona_id:
            if hasattr(user.persona_id, 'default_branch_id') and user.persona_id.default_branch_id:
                return user.persona_id.default_branch_id.id
        
        # Try to get from user's default branch
        if 'default_branch_id' in self.env['res.users']._fields and hasattr(user, 'default_branch_id') and user.default_branch_id:
            return user.default_branch_id.id
        
        # Fallback: Try to get first branch of user's company
        # When ops.branch is implemented:
        # branch = self.env['ops.branch'].search([('company_id', '=', user.company_id.id)], limit=1)
        # For now, return current company
        return user.company_id.id if user.company_id else False
    
    def _get_default_ops_business_unit(self):
        """
        Get default business unit from user's persona.
        
        Priority:
        1. User's persona default business unit
        2. User's default business unit (if field exists)
        3. False (no default)
        """
        user = self.env.user
        
        # Try to get from persona, check if field exists on model first
        if 'persona_id' in self.env['res.users']._fields and hasattr(user, 'persona_id') and user.persona_id:
            if hasattr(user.persona_id, 'default_business_unit_id') and user.persona_id.default_business_unit_id:
                return user.persona_id.default_business_unit_id.id
        
        # Try to get from user's default BU
        if 'default_business_unit_id' in self.env['res.users']._fields and hasattr(user, 'default_business_unit_id') and user.default_business_unit_id:
            return user.default_business_unit_id.id
        
        return False

    # =========================================================================
    # Propagation Helper Methods
    # =========================================================================
    
    def _propagate_matrix_to_lines(self, line_field='order_line'):
        """
        Propagate matrix dimensions to related line items.
        
        Args:
            line_field: Name of the One2many field containing lines (default: 'order_line')
        
        Usage:
            order._propagate_matrix_to_lines('order_line')
            invoice._propagate_matrix_to_lines('invoice_line_ids')
        """
        for record in self:
            if hasattr(record, line_field):
                lines = record[line_field]
                if lines:
                    lines.write({
                        'ops_branch_id': record.ops_branch_id.id if record.ops_branch_id else False,
                        'ops_business_unit_id': record.ops_business_unit_id.id if record.ops_business_unit_id else False,
                    })
    
    def _prepare_invoice_vals(self, **kwargs):
        """
        Helper to prepare invoice values with matrix dimensions.
        Override this in models that create invoices.
        
        Returns:
            dict: Invoice values including matrix dimensions
        """
        vals = {}
        if hasattr(self, 'ops_branch_id') and self.ops_branch_id:
            vals['ops_branch_id'] = self.ops_branch_id.id
        if hasattr(self, 'ops_business_unit_id') and self.ops_business_unit_id:
            vals['ops_business_unit_id'] = self.ops_business_unit_id.id
        vals.update(kwargs)
        return vals
    
    def _prepare_picking_vals(self, **kwargs):
        """
        Helper to prepare stock picking values with matrix dimensions.
        Override this in models that create pickings.
        
        Returns:
            dict: Picking values including matrix dimensions
        """
        vals = {}
        if hasattr(self, 'ops_branch_id') and self.ops_branch_id:
            vals['ops_branch_id'] = self.ops_branch_id.id
        if hasattr(self, 'ops_business_unit_id') and self.ops_business_unit_id:
            vals['ops_business_unit_id'] = self.ops_business_unit_id.id
        vals.update(kwargs)
        return vals
    
    def get_matrix_domain(self):
        """
        Get domain filter for matrix dimensions.
        Useful for filtering related records.
        
        Returns:
            list: Domain for searching records with same matrix dimensions
        """
        self.ensure_one()
        domain = []
        if self.ops_branch_id:
            domain.append(('ops_branch_id', '=', self.ops_branch_id.id))
        if self.ops_business_unit_id:
            domain.append(('ops_business_unit_id', '=', self.ops_business_unit_id.id))
        return domain
    
    def validate_matrix_dimensions(self):
        """
        Validate that required matrix dimensions are set.
        Override this in specific models to enforce requirements.
        
        Returns:
            bool: True if valid
        
        Raises:
            ValidationError: If required dimensions are missing
        """
        for record in self:
            # Basic validation - can be overridden
            if not record.ops_branch_id:
                # Warning only, not blocking for compatibility
                pass
            if not record.ops_business_unit_id:
                # Warning only, not blocking for compatibility
                pass
        return True

    # =========================================================================
    # Onchange Methods for UI
    # =========================================================================
    
    @api.onchange('ops_branch_id')
    def _onchange_branch_id(self):
        """
        Clear business unit when branch changes to ensure valid combinations.
        Also applies domain filter to BU selection based on selected branch.
        """
        for record in self:
            if record.ops_branch_id:
                # If BU is set and doesn't belong to new branch, clear it
                if record.ops_business_unit_id:
                    if record.ops_branch_id not in record.ops_business_unit_id.branch_ids:
                        record.ops_business_unit_id = False
                
                # Return domain to filter BU selection
                return {
                    'domain': {
                        'ops_business_unit_id': [
                            ('branch_ids', '=', record.ops_branch_id.id),
                            ('active', '=', True)
                        ]
                    }
                }
            else:
                # No branch selected, clear BU
                record.ops_business_unit_id = False
    
    @api.onchange('ops_branch_id', 'ops_business_unit_id')
    def _onchange_matrix_dimensions(self):
        """
        Trigger when matrix dimensions change in the UI.
        Can be overridden to add model-specific behavior.
        """
        # This is a hook for subclasses to implement
        pass
    
    # =========================================================================
    # Branch Access Control Methods
    # =========================================================================
    
    def _get_branch_domain(self):
        """
        Get domain filter for user's allowed branches.
        
        Returns domain that limits records to branches the current user can access.
        System administrators (base.group_system) bypass all restrictions.
        Cross-branch BU leaders get special handling.
        
        Returns:
            list: Odoo domain for branch filtering
        
        Usage:
            domain = self._get_branch_domain()
            records = self.env['sale.order'].search(domain)
        """
        user = self.env.user
        
        # Admin bypass: System administrators can access all branches
        if user.has_group('base.group_system'):
            return []
        
        # Get user's allowed branches from res.users
        allowed_branch_ids = []
        
        # Direct branch assignments
        if hasattr(user, 'ops_allowed_branch_ids') and user.ops_allowed_branch_ids:
            allowed_branch_ids = user.ops_allowed_branch_ids.ids
        
        # Legacy field support
        elif hasattr(user, 'allowed_branch_ids') and user.allowed_branch_ids:
            allowed_branch_ids = user.allowed_branch_ids.ids
        
        # Cross-branch BU leader: Get branches where their BUs operate
        if user.has_group('ops_matrix_core.group_ops_cross_branch_bu_leader'):
            allowed_bus = user.ops_allowed_business_unit_ids if hasattr(user, 'ops_allowed_business_unit_ids') else self.env['ops.business.unit']
            if allowed_bus:
                bu_branch_ids = allowed_bus.mapped('branch_ids').ids
                allowed_branch_ids = list(set(allowed_branch_ids + bu_branch_ids))
        
        # If no branches defined, return domain that matches nothing
        if not allowed_branch_ids:
            return [('id', '=', False)]
        
        return [('ops_branch_id', 'in', allowed_branch_ids)]
    
    def _apply_branch_filter(self, domain):
        """
        Apply branch access filter to an existing domain.
        
        Combines the provided domain with branch access restrictions.
        Useful for extending search domains with security filters.
        
        Args:
            domain (list): Existing Odoo domain to enhance
        
        Returns:
            list: Combined domain with branch filter applied
        
        Usage:
            base_domain = [('state', '=', 'draft')]
            filtered_domain = self._apply_branch_filter(base_domain)
            records = self.env['sale.order'].search(filtered_domain)
        """
        branch_domain = self._get_branch_domain()
        
        if not branch_domain:
            # No filter needed (admin bypass)
            return domain
        
        # Combine domains with AND logic
        if domain:
            return ['&'] + branch_domain + domain
        else:
            return branch_domain
    
    def _check_branch_access(self):
        """
        Verify that current user has access to this record's branch.
        
        Validates user permissions against the record's ops_branch_id.
        System administrators always have access.
        Raises ValidationError if user lacks access rights.
        
        Returns:
            bool: True if user has access
        
        Raises:
            ValidationError: If user cannot access the branch
        
        Usage:
            # In a model method
            self._check_branch_access()
            # Proceed with operation...
        """
        from odoo.exceptions import ValidationError
        
        for record in self:
            user = self.env.user
            
            # Admin bypass: System administrators can access all branches
            if user.has_group('base.group_system'):
                continue
            
            # If no branch set on record, allow (for backward compatibility)
            if not record.ops_branch_id:
                continue
            
            # Get user's allowed branches
            allowed_branch_ids = []
            
            if hasattr(user, 'ops_allowed_branch_ids') and user.ops_allowed_branch_ids:
                allowed_branch_ids = user.ops_allowed_branch_ids.ids
            elif hasattr(user, 'allowed_branch_ids') and user.allowed_branch_ids:
                allowed_branch_ids = user.allowed_branch_ids.ids
            
            # Cross-branch BU leader special handling
            if user.has_group('ops_matrix_core.group_ops_cross_branch_bu_leader'):
                allowed_bus = user.ops_allowed_business_unit_ids if hasattr(user, 'ops_allowed_business_unit_ids') else self.env['ops.business.unit']
                if allowed_bus:
                    bu_branch_ids = allowed_bus.mapped('branch_ids').ids
                    allowed_branch_ids = list(set(allowed_branch_ids + bu_branch_ids))
            
            # Check access
            if record.ops_branch_id.id not in allowed_branch_ids:
                raise ValidationError(
                    f"Access Denied: You do not have access to branch '{record.ops_branch_id.name}'. "
                    f"Contact your system administrator to request access."
                )
        
        return True
    
    def _get_allowed_branches(self):
        """
        Get recordset of branches that current user can access.
        
        Returns:
            recordset: ops.branch records the user can access
        
        Usage:
            allowed_branches = self._get_allowed_branches()
            for branch in allowed_branches:
                print(branch.name)
        """
        user = self.env.user
        
        # Admin bypass: return all branches
        if user.has_group('base.group_system'):
            return self.env['ops.branch'].search([('active', '=', True)])
        
        # Get user's allowed branches
        allowed_branches = self.env['ops.branch']
        
        if hasattr(user, 'ops_allowed_branch_ids') and user.ops_allowed_branch_ids:
            allowed_branches = user.ops_allowed_branch_ids
        elif hasattr(user, 'allowed_branch_ids') and user.allowed_branch_ids:
            allowed_branches = user.allowed_branch_ids
        
        # Add branches for cross-branch BU leaders
        if user.has_group('ops_matrix_core.group_ops_cross_branch_bu_leader'):
            allowed_bus = user.ops_allowed_business_unit_ids if hasattr(user, 'ops_allowed_business_unit_ids') else self.env['ops.business.unit']
            if allowed_bus:
                bu_branches = allowed_bus.mapped('branch_ids')
                allowed_branches |= bu_branches
        
        return allowed_branches
