from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _valid_field_parameter(cls, field, name):
        # Add 'tracking' to valid parameters
        return name == 'tracking' or models.BaseModel._valid_field_parameter(cls, field, name)

    # ============================================
    # PERSONA FIELDS (Many2many Primary)
    # ============================================
    ops_persona_ids = fields.Many2many(
        'ops.persona',
        'res_users_ops_persona_rel',
        'user_id',
        'persona_id',
        string='OPS Personas',
        help='Multiple organizational personas/roles assigned to this user. '
             'User inherits ALL authorities from ALL assigned personas.',
        tracking=True
    )
    
    # Legacy Many2one field (computed for backward compatibility)
    persona_id = fields.Many2one(
        'ops.persona',
        string='Primary Persona',
        compute='_compute_persona_id',
        inverse='_inverse_persona_id',
        store=True,
        help='[DEPRECATED] Primary persona (first from ops_persona_ids). Use ops_persona_ids instead.',
        tracking=True
    )
    
    # Legacy alias for backward compatibility
    persona_ids = fields.Many2many(
        'ops.persona',
        'res_users_legacy_persona_rel',
        'user_id',
        'persona_id',
        string='Personas (Legacy)',
        compute='_compute_persona_ids',
        inverse='_inverse_persona_ids',
        store=True,
        help='[DEPRECATED ALIAS] Use ops_persona_ids instead'
    )
    
    delegated_persona_ids = fields.Many2many(
        'ops.persona',
        'res_users_ops_delegated_persona_rel',
        'user_id',
        'persona_id',
        string='Delegated Personas'
    )
    
    primary_branch_id = fields.Many2one(
        'ops.branch',
        string='Primary Branch',
        help='Primary branch this user belongs to',
        tracking=True
    )
    
    # ============================================
    # MATRIX ACCESS CONTROL FIELDS
    # ============================================
    
    # Multi-branch access
    ops_allowed_branch_ids = fields.Many2many(
        'ops.branch',
        'res_users_ops_allowed_branch_rel',
        'user_id',
        'branch_id',
        string='Allowed Branches',
        help='Operational branches this user can access',
        tracking=True
    )
    
    # Multi-business unit access
    ops_allowed_business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'res_users_ops_allowed_business_unit_rel',
        'user_id',
        'business_unit_id',
        string='Allowed Business Units',
        help='Business units this user can access',
        tracking=True
    )
    
    # Default selections for quick transactions
    ops_default_branch_id = fields.Many2one(
        'ops.branch',
        string='Default Branch',
        help='Default branch for new transactions',
        domain="[('id', 'in', ops_allowed_branch_ids)]",
        tracking=True
    )

    # Compatibility alias for legacy consumers (e.g., governance tests)
    # Mirrors ops_default_branch_id
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Primary Branch (Alias)',
        compute='_compute_ops_branch_alias',
        inverse='_inverse_ops_branch_alias',
        store=True,
        readonly=False,
        help='Alias of ops_default_branch_id for backward compatibility'
    )
    
    ops_default_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Default Business Unit',
        help='Default business unit for new transactions',
        domain="[('id', 'in', ops_allowed_business_unit_ids)]",
        tracking=True
    )
    
    # Role indicators
    is_cross_branch_bu_leader = fields.Boolean(
        string='Cross-Branch BU Leader',
        help='Can access the same business unit across multiple branches',
        tracking=True
    )
    
    is_matrix_administrator = fields.Boolean(
        string='Matrix Administrator',
        help='Can configure and manage matrix structure (not data)',
        tracking=True
    )
    
    # ============================================
    # COMPUTED FIELDS
    # ============================================
    
    # Access summary for UI display
    matrix_access_summary = fields.Char(
        compute='_compute_matrix_access_summary',
        string='Matrix Access',
        help='Summary of user\'s matrix access rights'
    )
    
    # Count fields for quick reference
    allowed_branch_count = fields.Integer(
        compute='_compute_allowed_counts',
        string='Branch Count'
    )
    
    allowed_bu_count = fields.Integer(
        compute='_compute_allowed_counts',
        string='BU Count'
    )
    
    # Effective companies from allowed branches
    effective_company_ids = fields.Many2many(
        'res.company',
        compute='_compute_effective_companies',
        string='Effective Companies',
        help='Companies derived from allowed branches',
        store=False
    )
    
    # ========================================================================
    # LEGACY FIELDS (Computed for Backward Compatibility - DB Stored)
    # ========================================================================
    allowed_branch_ids = fields.Many2many(
        'ops.branch',
        'res_users_legacy_branch_rel',
        'user_id',
        'branch_id',
        string='Allowed Branches (Legacy)',
        compute='_compute_allowed_branch_ids',
        inverse='_inverse_allowed_branch_ids',
        store=True,
        help='[DEPRECATED] Use ops_allowed_branch_ids instead'
    )
    
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'res_users_legacy_business_unit_rel',
        'user_id',
        'business_unit_id',
        string='Business Units (Legacy)',
        compute='_compute_business_unit_ids',
        inverse='_inverse_business_unit_ids',
        store=True,
        help='[DEPRECATED] Use ops_allowed_business_unit_ids instead'
    )
    
    allowed_business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'res_users_allowed_business_unit_alias_rel',
        'user_id',
        'business_unit_id',
        string='Allowed Business Units (Alias)',
        compute='_compute_allowed_business_unit_ids',
        inverse='_inverse_allowed_business_unit_ids',
        store=True,
        help='[DEPRECATED ALIAS] Use ops_allowed_business_unit_ids instead'
    )
    
    default_branch_id = fields.Many2one(
        'ops.branch',
        string='Default Branch (Alias)',
        compute='_compute_default_branch_id',
        inverse='_inverse_default_branch_id',
        store=True,
        help='[DEPRECATED ALIAS] Use ops_default_branch_id instead'
    )
    
    default_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Default BU (Alias)',
        compute='_compute_default_business_unit_id',
        inverse='_inverse_default_business_unit_id',
        store=True,
        help='[DEPRECATED ALIAS] Use ops_default_business_unit_id instead'
    )
    
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch (Legacy)',
        compute='_compute_branch_id',
        inverse='_inverse_branch_id',
        store=True,
        help='[DEPRECATED] Use primary_branch_id instead'
    )
    
    # ========================================================================
    # COMPUTED METHODS - Synchronization
    # ========================================================================
    
    @api.depends('ops_allowed_branch_ids')
    def _compute_allowed_branch_ids(self):
        """Compute legacy field from OPS matrix field."""
        for user in self:
            user.allowed_branch_ids = user.ops_allowed_branch_ids
    
    def _inverse_allowed_branch_ids(self):
        """Inverse synchronization: Writing to legacy field updates OPS field."""
        for user in self:
            user.ops_allowed_branch_ids = user.allowed_branch_ids
    
    @api.depends('ops_allowed_business_unit_ids')
    def _compute_business_unit_ids(self):
        """Compute legacy field from OPS matrix field."""
        for user in self:
            user.business_unit_ids = user.ops_allowed_business_unit_ids
    
    def _inverse_business_unit_ids(self):
        """Inverse synchronization: Writing to legacy field updates OPS field."""
        for user in self:
            user.ops_allowed_business_unit_ids = user.business_unit_ids
    
    @api.depends('ops_allowed_business_unit_ids')
    def _compute_allowed_business_unit_ids(self):
        """Compute alias field from OPS matrix field."""
        for user in self:
            user.allowed_business_unit_ids = user.ops_allowed_business_unit_ids
    
    def _inverse_allowed_business_unit_ids(self):
        """Inverse synchronization: Writing to alias field updates OPS field."""
        for user in self:
            user.ops_allowed_business_unit_ids = user.allowed_business_unit_ids
    
    @api.depends('ops_default_branch_id')
    def _compute_default_branch_id(self):
        """Compute alias field from OPS matrix field."""
        for user in self:
            user.default_branch_id = user.ops_default_branch_id
    
    def _inverse_default_branch_id(self):
        """Inverse synchronization: Writing to alias field updates OPS field."""
        for user in self:
            user.ops_default_branch_id = user.default_branch_id

    @api.depends('ops_default_branch_id')
    def _compute_ops_branch_alias(self):
        """Keep ops_branch_id in sync with ops_default_branch_id."""
        for user in self:
            user.ops_branch_id = user.ops_default_branch_id

    def _inverse_ops_branch_alias(self):
        """Writing legacy alias updates ops_default_branch_id."""
        for user in self:
            user.ops_default_branch_id = user.ops_branch_id
    
    @api.depends('ops_default_business_unit_id')
    def _compute_default_business_unit_id(self):
        """Compute alias field from OPS matrix field."""
        for user in self:
            user.default_business_unit_id = user.ops_default_business_unit_id
    
    def _inverse_default_business_unit_id(self):
        """Inverse synchronization: Writing to alias field updates OPS field."""
        for user in self:
            user.ops_default_business_unit_id = user.default_business_unit_id
    
    @api.depends('primary_branch_id')
    def _compute_branch_id(self):
        """Compute legacy field from primary_branch_id."""
        for user in self:
            user.branch_id = user.primary_branch_id
    
    def _inverse_branch_id(self):
        """Inverse synchronization: Writing to legacy field updates primary_branch_id."""
        for user in self:
            user.primary_branch_id = user.branch_id
    
    @api.depends('ops_persona_ids')
    def _compute_persona_id(self):
        """Compute primary persona from ops_persona_ids (first active persona)."""
        for user in self:
            active_personas = user.ops_persona_ids.filtered(lambda p: p.active and p.is_active_today)
            user.persona_id = active_personas[0] if active_personas else False
    
    def _inverse_persona_id(self):
        """Inverse synchronization: Writing to persona_id updates ops_persona_ids."""
        for user in self:
            if user.persona_id:
                # Add to ops_persona_ids if not already there
                if user.persona_id not in user.ops_persona_ids:
                    user.ops_persona_ids = [(4, user.persona_id.id)]
            else:
                # Clear all personas
                user.ops_persona_ids = [(5, 0, 0)]
    
    @api.depends('ops_persona_ids')
    def _compute_persona_ids(self):
        """Compute legacy persona_ids from ops_persona_ids."""
        for user in self:
            user.persona_ids = user.ops_persona_ids
    
    def _inverse_persona_ids(self):
        """Inverse synchronization: Writing to legacy field updates ops_persona_ids."""
        for user in self:
            user.ops_persona_ids = user.persona_ids
    
    # ========================================================================
    # COMPUTED METHODS - New Matrix Fields
    # ========================================================================
    
    @api.depends('ops_allowed_branch_ids', 'ops_allowed_business_unit_ids', 
                 'is_cross_branch_bu_leader', 'is_matrix_administrator')
    def _compute_matrix_access_summary(self):
        """Compute human-readable summary of matrix access."""
        for user in self:
            parts = []
            
            # Branch access summary
            if user.ops_allowed_branch_ids:
                if len(user.ops_allowed_branch_ids) <= 3:
                    branch_codes = [b.code if hasattr(b, 'code') else b.name 
                                   for b in user.ops_allowed_branch_ids]
                    parts.append(f"Branches: {', '.join(branch_codes)}")
                else:
                    parts.append(f"Branches: {len(user.ops_allowed_branch_ids)} branches")
            
            # BU access summary
            if user.ops_allowed_business_unit_ids:
                if len(user.ops_allowed_business_unit_ids) <= 3:
                    bu_codes = [bu.code if hasattr(bu, 'code') else bu.name 
                               for bu in user.ops_allowed_business_unit_ids]
                    parts.append(f"BUs: {', '.join(bu_codes)}")
                else:
                    parts.append(f"BUs: {len(user.ops_allowed_business_unit_ids)} units")
            
            # Role indicators
            if user.is_cross_branch_bu_leader:
                parts.append("Cross-Branch Leader")
            if user.is_matrix_administrator:
                parts.append("Matrix Admin")
            
            user.matrix_access_summary = " | ".join(parts) if parts else "No matrix access"
    
    @api.depends('ops_allowed_branch_ids', 'ops_allowed_business_unit_ids')
    def _compute_allowed_counts(self):
        """Compute count of allowed branches and BUs."""
        for user in self:
            user.allowed_branch_count = len(user.ops_allowed_branch_ids)
            user.allowed_bu_count = len(user.ops_allowed_business_unit_ids)
    
    @api.depends('ops_allowed_branch_ids')
    def _compute_effective_companies(self):
        """Compute companies from allowed branches."""
        for user in self:
            # Get companies from allowed branches (ops.branch has company_id field)
            companies = user.ops_allowed_branch_ids.mapped('company_id')
            user.effective_company_ids = [(6, 0, companies.ids)]
    
    # ========================================================================
    # ACCESS CONTROL METHODS
    # ========================================================================
    
    def get_effective_matrix_access(self):
        """
        Returns computed access based on user's direct assignments and personas.
        Consolidated view of all access rights.
        """
        self.ensure_one()
        
        # If system administrator, grant all access
        if self.has_group('base.group_system'):
            return {
                'companies': self.env['res.company'].search([]),
                'branches': self.env['ops.branch'].search([]),
                'business_units': self.env['ops.business.unit'].search([]),
            }
        
        # Start with direct assignments
        companies = self.company_ids
        branches = self.ops_allowed_branch_ids
        business_units = self.ops_allowed_business_unit_ids
        
        # Add access from personas (if persona module exists and is installed)
        if hasattr(self, 'persona_ids'):
            for persona in self.persona_ids.filtered(lambda p: p.active):
                # Add persona's allowed branches
                if hasattr(persona, 'branch_ids'):
                    branches |= persona.branch_ids
                
                # Add persona's allowed business units
                if hasattr(persona, 'business_unit_ids'):
                    business_units |= persona.business_unit_ids
        
        # For cross-branch BU leaders, get all branches where their BUs operate
        if self.is_cross_branch_bu_leader and business_units:
            # Get all branches where allowed BUs operate
            bu_branches = business_units.mapped('branch_ids')
            branches |= bu_branches
        
        # Derive companies from branches (if not already set)
        if branches and not companies:
            companies = branches.mapped('company_id')
        
        return {
            'companies': companies,
            'branches': branches,
            'business_units': business_units,
        }
    
    def can_access_branch(self, branch_id):
        """Check if user can access specific branch."""
        self.ensure_one()
        
        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True
        
        # Get effective access
        effective_access = self.get_effective_matrix_access()
        
        # Check if branch is in allowed branches
        branch = self.env['ops.branch'].browse(branch_id)
        if not branch.exists():
            return False
        
        # Company-level access: if user has company access, they can see all branches in that company
        if branch.company_id.id in effective_access['companies'].ids:
            return True
        
        # Branch-level access
        return branch_id in effective_access['branches'].ids
    
    def can_access_business_unit(self, bu_id):
        """Check if user can access specific business unit."""
        self.ensure_one()
        
        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True
        
        # Get effective access
        effective_access = self.get_effective_matrix_access()
        
        # Check if BU is in allowed BUs
        bu = self.env['ops.business.unit'].browse(bu_id)
        if not bu.exists():
            return False
        
        # Company-level access: if user has company access, they can see all BUs in that company
        bu_companies = bu.branch_ids.mapped('company_id')
        if any(company.id in effective_access['companies'].ids for company in bu_companies):
            return True
        
        # BU-level access
        return bu_id in effective_access['business_units'].ids
    
    def can_access_matrix_combination(self, branch_id, bu_id):
        """
        Check if user can access specific branch-BU combination.
        Useful for transaction validation.
        """
        self.ensure_one()
        
        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True
        
        # Check individual access
        if not self.can_access_branch(branch_id):
            return False
        
        if not self.can_access_business_unit(bu_id):
            return False
        
        # For cross-branch BU leaders: special handling
        if self.is_cross_branch_bu_leader:
            # Cross-branch BU leaders can access their BUs in any branch
            allowed_bus = self.get_effective_matrix_access()['business_units']
            return bu_id in allowed_bus.ids
        
        # Regular users: BU must operate in the branch
        bu = self.env['ops.business.unit'].browse(bu_id)
        branch = self.env['ops.branch'].browse(branch_id)
        
        return branch in bu.branch_ids
    
    # ========================================================================
    # SEGREGATION OF DUTIES (SoD) AUTHORITY CHECKING
    # ========================================================================
    
    def has_authority(self, authority_field):
        """
        Check if user has specific authority based on ANY of their assigned personas.
        Returns True if ANY active persona has the authority flag set to True.
        
        :param authority_field: Name of the authority field (e.g., 'can_validate_invoices')
        :return: Boolean
        """
        self.ensure_one()
        
        # System administrators bypass all checks
        if self.has_group('base.group_system'):
            return True
        
        # Check all active personas
        active_personas = self.ops_persona_ids.filtered(lambda p: p.active and p.is_active_today)
        
        for persona in active_personas:
            if hasattr(persona, authority_field) and getattr(persona, authority_field):
                return True
        
        return False
    
    def has_ops_authority(self, field_name):
        """
        Cumulative Authority Logic Helper: Check if ANY of the user's assigned personas
        grants a specific authority.
        
        This method implements the OPS Framework anti-fraud pattern where users can have
        multiple personas, and we check if ANY persona grants the requested authority.
        
        Usage Example:
            if self.env.user.has_ops_authority('can_validate_invoices'):
                # Show validate button
                pass
        
        :param field_name: Name of the boolean authority field on ops.persona model
                          (e.g., 'can_validate_invoices', 'can_post_journal_entries')
        :return: Boolean - True if ANY active persona has the authority, False otherwise
        
        Edge Cases Handled:
        - Returns True for system administrators (bypass all checks)
        - Returns False if user has no personas assigned
        - Returns False if the field doesn't exist on the persona model
        - Returns False if all personas lack the authority
        - Considers only active personas with valid date ranges
        """
        self.ensure_one()
        
        # System administrators bypass all authority checks
        if self.has_group('base.group_system'):
            return True
        
        # Handle case: No personas assigned to user
        if not self.ops_persona_ids:
            _logger.debug(
                f"User {self.name} (ID: {self.id}) has no personas assigned. "
                f"Authority check for '{field_name}' returns False."
            )
            return False
        
        # Filter to only active personas with valid date ranges
        active_personas = self.ops_persona_ids.filtered(
            lambda p: p.active and p.is_active_today
        )
        
        # Handle case: No active personas
        if not active_personas:
            _logger.debug(
                f"User {self.name} (ID: {self.id}) has no active personas. "
                f"Authority check for '{field_name}' returns False."
            )
            return False
        
        # Defensive check: Verify field exists on persona model
        persona_model = self.env['ops.persona']
        if field_name not in persona_model._fields:
            _logger.warning(
                f"Authority field '{field_name}' does not exist on ops.persona model. "
                f"Authority check for user {self.name} (ID: {self.id}) returns False."
            )
            return False
        
        # Use any() for efficient cumulative authority check
        # Returns True if ANY persona has the authority field set to True
        try:
            has_authority = any(
                getattr(persona, field_name, False)
                for persona in active_personas
            )
            
            if has_authority:
                _logger.debug(
                    f"User {self.name} (ID: {self.id}) has authority '{field_name}' "
                    f"via one or more active personas."
                )
            
            return has_authority
            
        except Exception as e:
            _logger.error(
                f"Error checking authority '{field_name}' for user {self.name} (ID: {self.id}): {e}"
            )
            return False
    
    def can_modify_product_master(self):
        """Check if user can modify product master data (cost, suppliers)."""
        return self.has_authority('can_modify_product_master')
    
    def can_access_cost_prices(self):
        """Check if user can access/view product cost prices."""
        return self.has_authority('can_access_cost_prices')
    
    def can_validate_invoices(self):
        """Check if user can validate and post invoices."""
        return self.has_authority('can_validate_invoices')
    
    def can_post_journal_entries(self):
        """Check if user can post accounting journal entries."""
        return self.has_authority('can_post_journal_entries')
    
    def can_execute_payments(self):
        """Check if user can execute vendor payments."""
        return self.has_authority('can_execute_payments')
    
    def can_adjust_inventory(self):
        """Check if user can post inventory adjustments."""
        return self.has_authority('can_adjust_inventory')
    
    def can_manage_pdc(self):
        """Check if user can manage Post Dated Checks."""
        return self.has_authority('can_manage_pdc')
    
    # ========================================================================
    # VALIDATION CONSTRAINTS
    # ========================================================================
    
    @api.onchange('ops_allowed_branch_ids', 'ops_default_branch_id')
    def _onchange_auto_populate_primary_branch(self):
        """Auto-populate Primary Branch when allowed branches are selected."""
        for user in self:
            # Only auto-populate if primary_branch_id is not yet set
            if not user.primary_branch_id:
                # First try to use default branch if set
                if user.ops_default_branch_id and user.ops_default_branch_id in user.ops_allowed_branch_ids:
                    user.primary_branch_id = user.ops_default_branch_id
                # Otherwise use first allowed branch
                elif user.ops_allowed_branch_ids:
                    user.primary_branch_id = user.ops_allowed_branch_ids[0]
    
    @api.constrains('ops_default_branch_id', 'ops_allowed_branch_ids')
    def _check_default_branch_in_allowed(self):
        """Ensure default branch is in user's allowed branches."""
        for user in self:
            if (user.ops_default_branch_id and
                user.ops_default_branch_id not in user.ops_allowed_branch_ids):
                raise ValidationError(_(
                    "Default branch '%(branch_name)s' must be in user's allowed branches."
                ) % {
                    'branch_name': user.ops_default_branch_id.name
                })
    
    @api.constrains('ops_default_business_unit_id', 'ops_allowed_business_unit_ids')
    def _check_default_bu_in_allowed(self):
        """Ensure default BU is in user's allowed business units."""
        for user in self:
            if (user.ops_default_business_unit_id and 
                user.ops_default_business_unit_id not in user.ops_allowed_business_unit_ids):
                raise ValidationError(_(
                    "Default business unit '%(bu_name)s' must be in user's allowed business units."
                ) % {
                    'bu_name': user.ops_default_business_unit_id.name
                })
    
    @api.constrains('ops_allowed_branch_ids')
    def _check_branch_company_consistency(self):
        """Ensure all allowed branches belong to user's companies."""
        for user in self:
            if user.ops_allowed_branch_ids and user.company_ids:
                # ops.branch has company_id field linking to res.company
                invalid_branches = user.ops_allowed_branch_ids.filtered(
                    lambda b: b.company_id not in user.company_ids
                )
                if invalid_branches:
                    raise ValidationError(_(
                        "Branches %(branch_names)s do not belong to any of user's companies %(company_names)s."
                    ) % {
                        'branch_names': ', '.join(invalid_branches.mapped('name')),
                        'company_names': ', '.join(user.company_ids.mapped('name'))
                    })
    
    # @api.constrains('primary_branch_id', 'ops_allowed_business_unit_ids', 'persona_id')
    # def _check_user_matrix_requirements(self):
    #     """
    #     Ensure user has Primary Branch, at least one Business Unit, and a Persona assigned.
    #     Exception: Admin (ID 1) and Settings Managers are exempt from this check.
    #     
    #     Note: Setting a Persona is the first step - it will trigger auto-population of
    #     Primary Branch and Business Units if they are empty.
    #     """
    #     if self.env.context.get('install_mode'):
    #         return

    #     for user in self:
    #         # Skip admin user
    #         if user.id == 1:
    #             continue
    #         
    #         # Skip Settings Managers
    #         if user.has_group('base.group_system'):
    #             continue
    #         
    #         # Skip if user is being created (not yet saved)
    #         if not user.id:
    #             continue
    #         
    #         # Skip portal/public users
    #         if user.share:
    #             continue
    #         
    #         # If persona is assigned, allow save even if other fields are empty
    #         # The onchange will auto-populate them
    #         if user.persona_id:
    #             # Persona is set - this satisfies the first requirement
    #             # The system will auto-populate Primary Branch and BU
    #             continue
    #         
    #         # Validation: Persona required as first step
    #         if not user.persona_id:
    #             raise ValidationError(_(
    #                 "User '%(user_name)s' cannot be saved without an OPS Persona.\n\n"
    #                 "Please go to the 'OPS Matrix Access' tab and select a Persona first.\n"
    #                 "The system will then automatically populate Primary Branch and Business Units."
    #             ) % {'user_name': user.name}))
    
    # ========================================================================
    # CRUD OVERRIDE
    # ========================================================================
    
    def write(self, vals):
        """
        Override write to handle matrix access changes and persona assignment.
        Important: Update dependent records and log changes for security audit.
        """
        # Track changes for audit
        matrix_fields = [
            'ops_allowed_branch_ids', 'ops_allowed_business_unit_ids',
            'ops_default_branch_id', 'ops_default_business_unit_id',
            'is_cross_branch_bu_leader', 'is_matrix_administrator', 'persona_id'
        ]
        
        matrix_changes = any(field in vals for field in matrix_fields)
        persona_changed = 'persona_id' in vals
        
        # Perform the write
        result = super().write(vals)
        
        # AUTO-SYNC: If persona changed, auto-populate and map groups
        if persona_changed:
            for user in self:
                # Auto-populate Primary Branch if empty
                if not user.primary_branch_id and user.persona_id:
                    main_branch = self.env['ops.branch'].search([
                        ('company_id', '=', user.company_id.id),
                        ('active', '=', True)
                    ], limit=1, order='sequence, id')
                    
                    if main_branch:
                        # Direct write to avoid recursion
                        super(ResUsers, user).write({'primary_branch_id': main_branch.id})
                        _logger.info(f"Auto-populated Primary Branch for user {user.name}: {main_branch.name}")
                
                # Auto-map security groups
                user._map_persona_to_groups()
        
        # Log matrix access changes for security audit
        if matrix_changes:
            for user in self:
                _logger.info(
                    f"User {user.name} (ID: {user.id}) matrix access rights modified. "
                    f"Changes: {', '.join([k for k in vals.keys() if k in matrix_fields])}"
                )
                
                # Post message for audit trail on partner (users don't have message_post)
                if user.partner_id:
                    user.partner_id.message_post(
                        body=_('Matrix access rights updated by %s') % self.env.user.name,
                        subject=_('Security Configuration Change')
                    )
        
        return result
    
    # ========================================================================
    # CONTEXT METHODS FOR DEFAULTS
    # ========================================================================
    
    @api.model
    def _get_default_branch_context(self):
        """Get default branch for context based on user's settings."""
        user = self.env.user
        if user.ops_default_branch_id:
            return {'default_ops_branch_id': user.ops_default_branch_id.id}
        return {}
    
    @api.model
    def _get_default_bu_context(self):
        """Get default BU for context based on user's settings."""
        user = self.env.user
        if user.ops_default_business_unit_id:
            return {'default_ops_business_unit_id': user.ops_default_business_unit_id.id}
        return {}
    
    def get_context_with_matrix_defaults(self):
        """Return context dictionary with matrix defaults."""
        context = self._context.copy()
        context.update(self._get_default_branch_context())
        context.update(self._get_default_bu_context())
        return context
    
    # ========================================================================
    # ACTION METHODS FOR UI
    # ========================================================================
    
    def action_view_allowed_branches(self):
        """Open view of user's allowed branches."""
        self.ensure_one()
        return {
            'name': _('Allowed Branches'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.branch',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.ops_allowed_branch_ids.ids)],
            'context': {
                'search_default_active': 1,
            }
        }
    
    def action_view_allowed_business_units(self):
        """Open view of user's allowed business units."""
        self.ensure_one()
        return {
            'name': _('Allowed Business Units'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.business.unit',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.ops_allowed_business_unit_ids.ids)],
            'context': {
                'search_default_active': 1,
            }
        }
    
    def action_reset_matrix_access(self):
        """Reset matrix access to defaults (company-level)."""
        self.ensure_one()
        
        # Get all branches in user's companies
        company_branches = self.env['ops.branch'].search([
            ('company_id', 'in', self.company_ids.ids),
            ('active', '=', True)
        ])
        
        # Get all BUs in those branches
        company_bus = self.env['ops.business.unit'].search([
            ('branch_ids', 'in', company_branches.ids),
            ('active', '=', True)
        ])
        
        # Update user
        self.write({
            'ops_allowed_branch_ids': [(6, 0, company_branches.ids)],
            'ops_allowed_business_unit_ids': [(6, 0, company_bus.ids)],
            'ops_default_branch_id': company_branches[0].id if company_branches else False,
            'ops_default_business_unit_id': company_bus[0].id if company_bus else False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Matrix Access Reset'),
                'message': _('Matrix access has been reset to company defaults.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    # ========================================================================
    # GROUP SYNCHRONIZATION
    # ========================================================================
    
    @api.depends('group_ids')
    def _compute_matrix_roles_from_groups(self):
        """Sync group membership with role boolean fields."""
        matrix_admin_group = self.env.ref('ops_matrix_core.group_ops_matrix_administrator', False)
        cross_branch_group = self.env.ref('ops_matrix_core.group_ops_cross_branch_bu_leader', False)
        
        for user in self:
            if matrix_admin_group:
                user.is_matrix_administrator = matrix_admin_group in user.group_ids
            if cross_branch_group:
                user.is_cross_branch_bu_leader = cross_branch_group in user.group_ids
    
    @api.onchange('is_matrix_administrator')
    def _onchange_is_matrix_administrator(self):
        """Update group membership when role changes."""
        # Skip if record not yet created (group_ids not available on new records in onchange)
        if not self.id:
            return
        matrix_admin_group = self.env.ref('ops_matrix_core.group_ops_matrix_administrator', False)
        if matrix_admin_group:
            if self.is_matrix_administrator:
                self.group_ids = [(4, matrix_admin_group.id)]
            else:
                self.group_ids = [(3, matrix_admin_group.id)]
    
    @api.onchange('is_cross_branch_bu_leader')
    def _onchange_is_cross_branch_bu_leader(self):
        """Update group membership when role changes."""
        # Skip if record not yet created (group_ids not available on new records in onchange)
        if not self.id:
            return
        cross_branch_group = self.env.ref('ops_matrix_core.group_ops_cross_branch_bu_leader', False)
        if cross_branch_group:
            if self.is_cross_branch_bu_leader:
                self.group_ids = [(4, cross_branch_group.id)]
            else:
                self.group_ids = [(3, cross_branch_group.id)]
    
    # ========================================================================
    # PERSONA AUTO-SYNC: ZERO-FRICTION SETUP
    # ========================================================================
    
    @api.onchange('persona_id')
    def _onchange_persona_id(self):
        """
        AUTO-SYNC LOGIC: When a persona is assigned:
        1. Auto-populate Primary Branch (use company's first branch)
        2. Auto-map Odoo 19 security groups based on persona
        3. Prevent "Primary Branch is missing" error
        """
        for user in self:
            if not user.persona_id:
                continue
            
            # Step 1: Auto-populate Primary Branch if empty
            if not user.primary_branch_id:
                # Find the first branch in the user's company
                main_branch = self.env['ops.branch'].search([
                    ('company_id', '=', user.company_id.id),
                    ('active', '=', True)
                ], limit=1, order='sequence, id')
                
                if main_branch:
                    user.primary_branch_id = main_branch
                    _logger.info(f"Auto-populated Primary Branch for user {user.name}: {main_branch.name}")
            
            # Step 2: Auto-map security groups based on persona code
            user._map_persona_to_groups()
    
    def _map_persona_to_groups(self):
        """
        Map persona to Odoo 19 security groups automatically.
        This is the "Zero-Friction" setup logic.
        """
        self.ensure_one()
        
        if not self.persona_id:
            return
        
        persona_code = self.persona_id.code
        groups_to_add = []
        
        # Persona → Group Mapping
        persona_group_map = {
            'CEO': [
                'base.group_erp_manager',  # Access Rights
                'sales_team.group_sale_manager',  # Sales Manager
                'account.group_account_manager',  # Billing Manager
                'stock.group_stock_manager',  # Inventory Manager
                'ops_matrix_core.group_ops_executive',  # OPS Executive
                'ops_matrix_core.group_ops_matrix_administrator',  # Matrix Admin
            ],
            'CFO': [
                'account.group_account_manager',  # Billing Manager
                'account.group_account_user',  # Billing
                'ops_matrix_core.group_ops_executive',  # OPS Executive
                'ops_matrix_core.group_ops_cost_controller',  # Cost Controller
            ],
            'SALES_LEADER': [
                'sales_team.group_sale_manager',  # Sales Manager
                'sale.group_sale_manager',  # Administrator
                'ops_matrix_core.group_ops_bu_leader',  # BU Leader
            ],
            'SALES_MGR': [
                'sales_team.group_sale_manager',  # Sales Manager
                'sale.group_sale_salesman_all_leads',  # See All Leads
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'SALES_REP': [
                'sales_team.group_sale_salesman',  # User: Own Documents Only
                'sale.group_sale_salesman',  # User: Own Documents Only
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'HR_MGR': [
                'hr.group_hr_manager',  # Officer (if HR installed)
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'CHIEF_ACCT': [
                'account.group_account_manager',  # Billing Manager
                'account.group_account_user',  # Billing
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'FIN_MGR': [
                'account.group_account_manager',  # Accounting Manager (full invoicing)
                'account.group_account_invoice',  # Invoicing access
                'account.group_account_user',  # Accounting features
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'ACCOUNTANT': [
                'account.group_account_user',  # Billing
                'account.group_account_invoice',  # Billing
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'LOG_MGR': [
                'stock.group_stock_manager',  # Inventory Manager
                'ops_matrix_core.group_ops_branch_manager',  # Branch Manager
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'LOG_CLERK': [
                'stock.group_stock_user',  # User
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'TECH_SUPPORT': [
                'base.group_user',  # Internal User
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'SYS_ADMIN': [
                'base.group_system',  # Settings
                'ops_matrix_core.group_ops_matrix_administrator',  # Matrix Admin
            ],
        }
        
        # Get groups for this persona
        group_xmlids = persona_group_map.get(persona_code, [])
        
        for xmlid in group_xmlids:
            try:
                group = self.env.ref(xmlid, raise_if_not_found=False)
                if group:
                    groups_to_add.append(group.id)
            except Exception as e:
                _logger.warning(f"Could not find group {xmlid}: {e}")
        
        # Add groups to user
        if groups_to_add:
            self.group_ids = [(4, gid) for gid in groups_to_add]
            _logger.info(f"Auto-mapped {len(groups_to_add)} groups to user {self.name} based on persona {persona_code}")
    
    # ========================================================================
    # PERSONA INTEGRATION
    # ========================================================================
    
    def _get_effective_persona(self):
        """Get the effective persona considering delegations."""
        self.ensure_one()
        
        # Check if there's an active delegation TO this user
        delegation = self.env['ops.persona.delegation'].search([
            ('delegate_id', '=', self.id),
            ('active', '=', True),
            ('start_date', '<=', fields.Date.today()),
            '|',
            ('end_date', '=', False),
            ('end_date', '>=', fields.Date.today()),
        ], limit=1)
        
        if delegation:
            return delegation.delegator_id.persona_id
        
        # Return user's own persona
        return self.persona_id
    
    # ========================================================================
    # REST API AUTHENTICATION FIELDS
    # ========================================================================
    
    ops_api_key = fields.Char(
        string='API Key',
        copy=False,
        groups='base.group_system',
        help='API key for REST API authentication. Keep this secret! '
             'Used in X-API-Key header for API requests.'
    )
    
    ops_api_key_created = fields.Datetime(
        string='API Key Created',
        copy=False,
        readonly=True,
        groups='base.group_system',
        help='Timestamp when the current API key was generated'
    )
    
    ops_api_rate_limit = fields.Integer(
        string='API Rate Limit (per hour)',
        default=1000,
        groups='base.group_system',
        help='Maximum number of API calls this user can make per hour. '
             'Default: 1000 calls/hour'
    )
    
    # ========================================================================
    # DASHBOARD CONFIGURATION FIELDS
    # ========================================================================
    
    # Dashboard Configuration
    ops_dashboard_config = fields.Json(
        string='Dashboard Configuration',
        help='User-specific dashboard configuration'
    )
    
    # Favorite Dashboards
    favorite_dashboard_ids = fields.Many2many(
        'ir.actions.act_window',
        'user_favorite_dashboard_rel',
        'user_id',
        'action_id',
        string='Favorite Dashboards',
        help='User\'s favorite dashboard actions'
    )
    
    # Dashboard Last Accessed
    last_dashboard_access = fields.Datetime(
        string='Last Dashboard Access',
        help='Timestamp of last dashboard access'
    )
    
    def get_dashboard_config(self):
        """Get user's dashboard configuration with defaults."""
        self.ensure_one()
        
        default_config = {
            'dashboard_layout': 'standard',
            'default_date_range': 'month',
            'show_branch_first': True,
            'include_inactive_dimensions': False,
            'color_scheme': 'corporate',
            'primary_color': '#1f77b4',
            'secondary_color': '#ff7f0e',
            'success_color': '#2ca02c',
            'warning_color': '#d62728',
            'cache_duration': 15,
            'auto_refresh': True,
            'refresh_interval': 300,
        }
        
        user_config = self.ops_dashboard_config or {}
        return {**default_config, **user_config}
    
    def action_open_dashboard_config(self):
        """Open dashboard configuration wizard."""
        self.ensure_one()
        
        return {
            'name': _('Dashboard Configuration'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.dashboard.config',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
            }
        }
    
    # ========================================================================
    # REST API KEY MANAGEMENT ACTIONS
    # ========================================================================
    
    def action_generate_api_key(self):
        """Generate a new secure API key for the user."""
        self.ensure_one()
        
        import secrets
        
        # Generate secure random key (32 bytes = 256 bits)
        new_key = secrets.token_urlsafe(32)
        
        self.write({
            'ops_api_key': new_key,
            'ops_api_key_created': fields.Datetime.now()
        })
        
        _logger.info(f"API key generated for user {self.name} (ID: {self.id})")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Generated'),
                'message': _('New API key: %s\n\nSave this key securely. It will not be shown again.') % new_key,
                'type': 'success',
                'sticky': True,
            }
        }
    
    def action_revoke_api_key(self):
        """Revoke the user's API key."""
        self.ensure_one()
        
        self.write({
            'ops_api_key': False,
            'ops_api_key_created': False
        })
        
        _logger.warning(f"API key revoked for user {self.name} (ID: {self.id})")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Revoked'),
                'message': _('API key has been revoked. Generate a new key to continue using the API.'),
                'type': 'warning',
            }
        }
