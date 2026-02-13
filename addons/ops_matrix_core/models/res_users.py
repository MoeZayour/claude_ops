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
        tracking=True,
        required=False
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
    # SOD CONFLICT DETECTION FIELDS
    # ========================================================================

    sod_conflicts = fields.Text(
        string='SoD Conflicts',
        compute='_compute_sod_conflicts',
        help='Conflicting group memberships that violate Segregation of Duties policies',
    )

    has_sod_conflict = fields.Boolean(
        string='Has SoD Conflict',
        compute='_compute_sod_conflicts',
        help='Indicates if user has conflicting security group memberships',
    )

    sod_conflict_count = fields.Integer(
        string='SoD Conflict Count',
        compute='_compute_sod_conflicts',
        help='Number of SoD conflicts detected for this user',
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
        """Alias compute: Sync ops_persona_ids -> persona_ids."""
        for user in self:
            user.persona_ids = user.ops_persona_ids

    def _inverse_persona_ids(self):
        """Alias inverse: Writing persona_ids updates ops_persona_ids."""
        for user in self:
            user.ops_persona_ids = user.persona_ids

    # ========================================================================
    # COMPUTED METHODS - Access Summary
    # ========================================================================

    @api.depends('ops_allowed_branch_ids', 'ops_allowed_business_unit_ids')
    def _compute_matrix_access_summary(self):
        """Generate human-readable summary of user's matrix access."""
        for user in self:
            parts = []

            if user.ops_allowed_branch_ids:
                branch_count = len(user.ops_allowed_branch_ids)
                parts.append(_('%d branch(es)') % branch_count)

            if user.ops_allowed_business_unit_ids:
                bu_count = len(user.ops_allowed_business_unit_ids)
                parts.append(_('%d BU(s)') % bu_count)

            if user.is_cross_branch_bu_leader:
                parts.append(_('Cross-Branch BU Leader'))

            if user.is_matrix_administrator:
                parts.append(_('Matrix Admin'))

            user.matrix_access_summary = ', '.join(parts) if parts else _('No matrix access')

    @api.depends('ops_allowed_branch_ids', 'ops_allowed_business_unit_ids')
    def _compute_allowed_counts(self):
        """Compute count of allowed branches and BUs."""
        for user in self:
            user.allowed_branch_count = len(user.ops_allowed_branch_ids)
            user.allowed_bu_count = len(user.ops_allowed_business_unit_ids)

    @api.depends('ops_allowed_branch_ids')
    def _compute_effective_companies(self):
        """Compute effective companies from allowed branches."""
        for user in self:
            # Get unique companies from allowed branches
            company_ids = user.ops_allowed_branch_ids.mapped('company_id').ids
            user.effective_company_ids = [(6, 0, company_ids)]

    # ========================================================================
    # SOD CONFLICT DETECTION
    # ========================================================================

    @api.depends('group_ids')
    def _compute_sod_conflicts(self):
        """
        Detect Segregation of Duties (SoD) violations based on group memberships.
        Uses ops.sod.policy records to identify conflicting groups.
        """
        SodPolicy = self.env['ops.sod.policy'].sudo()

        for user in self:
            conflicts = []
            user_groups = user.group_ids

            # Search all active SoD policies
            policies = SodPolicy.search([('active', '=', True)])

            for policy in policies:
                # Check if user has BOTH conflicting groups
                has_group_a = policy.group_a_id in user_groups
                has_group_b = policy.group_b_id in user_groups

                if has_group_a and has_group_b:
                    conflicts.append(
                        _('Policy "%(policy)s": %(group_a)s + %(group_b)s') % {
                            'policy': policy.name,
                            'group_a': policy.group_a_id.name,
                            'group_b': policy.group_b_id.name
                        }
                    )

            # Set computed fields
            user.sod_conflicts = '\n'.join(conflicts) if conflicts else False
            user.has_sod_conflict = bool(conflicts)
            user.sod_conflict_count = len(conflicts)

    # ========================================================================
    # CONSTRAINT VALIDATION
    # ========================================================================

    @api.constrains('ops_default_branch_id', 'ops_allowed_branch_ids')
    def _check_default_branch_allowed(self):
        """Ensure default branch is in user's allowed branches."""
        for user in self:
            if user.ops_default_branch_id and user.ops_allowed_branch_ids:
                if user.ops_default_branch_id not in user.ops_allowed_branch_ids:
                    raise ValidationError(_(
                        "Default branch %(branch_name)s must be one of the user's allowed branches."
                    ) % {
                        'branch_name': user.ops_default_branch_id.name
                    })

    @api.constrains('ops_default_business_unit_id', 'ops_allowed_business_unit_ids')
    def _check_default_bu_allowed(self):
        """Ensure default BU is in user's allowed BUs."""
        for user in self:
            if user.ops_default_business_unit_id and user.ops_allowed_business_unit_ids:
                if user.ops_default_business_unit_id not in user.ops_allowed_business_unit_ids:
                    raise ValidationError(_(
                        "Default business unit %(bu_name)s must be one of the user's allowed business units."
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

    @api.constrains('primary_branch_id', 'ops_allowed_business_unit_ids', 'ops_persona_ids', 'persona_id')
    def _check_user_matrix_requirements(self):
        """
        ✅ HARD VALIDATION: Ensure non-admin internal users have:
        1. At least one OPS Persona assigned
        2. A Primary Branch assigned (now required=True)
        3. At least one Business Unit assigned
        """
        # Skip during module installation/upgrade
        if self.env.context.get('install_mode'):
            return

        # Skip during data import
        if self.env.context.get('import_file'):
            return

        # Skip if explicitly bypassed (e.g., during testing or migration)
        if self.env.context.get('skip_ops_validation'):
            return

        # Get system admin group for checks
        system_group = self.env.ref('base.group_system', raise_if_not_found=False)

        for user in self:
            # Skip XMLID-based system users (admin, public, etc.)
            if isinstance(user.id, int) and user.id <= 2:
                continue

            # Skip portal/public users (external users)
            if user.share:
                continue

            # Skip users without login (template users, etc.)
            if not user.login:
                continue

            # Skip Settings Managers / System Administrators
            if system_group and hasattr(user, 'group_ids') and user.group_ids and system_group in user.group_ids:
                continue

            # === GOVERNANCE VALIDATION (HARD) ===
            errors = []

            # Check 1: At least one Persona assigned
            has_persona = bool(user.ops_persona_ids) or bool(user.persona_id)
            if not has_persona:
                errors.append(
                    _("• OPS Persona: At least one persona must be assigned.")
                )

            # Check 2: Primary Branch assigned (redundant with required=True, but kept for clarity)
            if not user.primary_branch_id:
                errors.append(
                    _("• Primary Branch: A primary branch must be assigned.")
                )

            # Check 3: At least one Business Unit assigned
            if not user.ops_allowed_business_unit_ids:
                errors.append(
                    _("• Business Units: At least one business unit must be assigned.")
                )

            # ✅ RAISE ERROR if validation fails
            if errors:
                raise ValidationError(_(
                    "User '%(name)s' is missing required OPS Matrix configuration:\n%(errors)s\n\n"
                    "All internal users must have:\n"
                    "- At least one OPS Persona\n"
                    "- A Primary Branch\n"
                    "- At least one Business Unit"
                ) % {
                    'name': user.name,
                    'errors': '\n'.join(errors)
                })

    # ========================================================================
    # CRUD OVERRIDE
    # ========================================================================


    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to handle OPS Matrix governance on user creation.
        Auto-populates missing values where possible, then enforces
        hard validation: every internal user MUST have persona, branch, and BU.
        """
        # Skip during module installation/upgrade
        if self.env.context.get('install_mode'):
            return super().create(vals_list)

        for vals in vals_list:
            # Check if user is share/portal user - skip all processing
            if vals.get('share'):
                continue

            # AUTO-SYNC: If persona_id is set but ops_persona_ids is not, sync them
            persona_id = vals.get('persona_id')
            ops_persona_ids = vals.get('ops_persona_ids', [])
            has_ops_persona = False

            for cmd in ops_persona_ids:
                if isinstance(cmd, (list, tuple)):
                    if cmd[0] in (4, 6) and (cmd[1] if cmd[0] == 4 else cmd[2]):
                        has_ops_persona = True
                        break

            if not has_ops_persona and persona_id:
                vals['ops_persona_ids'] = [(4, persona_id)]

            # AUTO-POPULATE: If primary_branch_id is missing, try to find a default
            if not vals.get('primary_branch_id'):
                ops_allowed_branch_ids = vals.get('ops_allowed_branch_ids', [])
                for cmd in ops_allowed_branch_ids:
                    if isinstance(cmd, (list, tuple)):
                        if cmd[0] == 4:
                            vals['primary_branch_id'] = cmd[1]
                            break
                        elif cmd[0] == 6 and cmd[2]:
                            vals['primary_branch_id'] = cmd[2][0]
                            break

                if not vals.get('primary_branch_id'):
                    company_id = vals.get('company_id') or self.env.company.id
                    default_branch = self.env['ops.branch'].search([
                        ('company_id', '=', company_id),
                        ('active', '=', True)
                    ], limit=1, order='sequence, id')
                    if default_branch:
                        vals['primary_branch_id'] = default_branch.id
                        if not ops_allowed_branch_ids:
                            vals['ops_allowed_branch_ids'] = [(4, default_branch.id)]

            # HARD VALIDATION — persona, branch, BU required
            # @api.constrains only fires when watched fields are IN vals.
            # If none are set, the constraint never triggers.
            errors = []
            user_name = vals.get('name', vals.get('login', 'New User'))

            if not vals.get('persona_id'):
                errors.append(_("• OPS Persona: A persona must be assigned."))

            if not vals.get('primary_branch_id'):
                errors.append(_("• Primary Branch: A primary branch must be assigned."))

            if not self._vals_has_m2m_data(vals.get('ops_allowed_business_unit_ids', [])):
                errors.append(_("• Business Unit: At least one business unit must be assigned."))

            if errors:
                raise ValidationError(_(
                    "Cannot create user '%(name)s' — missing required OPS Matrix configuration:\n%(errors)s\n\n"
                    "All internal users must have:\n"
                    "- An OPS Persona\n"
                    "- A Primary Branch\n"
                    "- At least one Business Unit"
                ) % {
                    'name': user_name,
                    'errors': '\n'.join(errors)
                })

        # Create the user
        users = super().create(vals_list)

        # Map persona to security groups for each created user
        for user in users:
            if user.persona_id and not user.share:
                user._map_persona_to_groups()
                _logger.info(
                    "Auto-mapped security groups for new user %s with persona %s",
                    user.name, user.persona_id.code
                )

        return users

    @staticmethod
    def _vals_has_m2m_data(commands):
        """Check if M2M ORM commands actually contain data.
        Returns True if commands would result in at least one linked record.
        """
        if not commands:
            return False
        for cmd in commands:
            if isinstance(cmd, (list, tuple)):
                if cmd[0] == 4 and cmd[1]:        # (4, id) link
                    return True
                if cmd[0] == 6 and cmd[2]:         # (6, 0, [ids]) replace
                    return True
                if cmd[0] == 0 and cmd[2]:         # (0, 0, {vals}) create+link
                    return True
        return False

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

                # Auto-map security groups (method from res_users_group_mapper.py)
                user._map_persona_to_groups()

        # Log matrix access changes (server log only — all matrix fields
        # have tracking=True so Odoo chatter records changes natively.
        # Manual message_post removed: caused cascading side-effects
        # during user creation, corrupting the save response.)
        if matrix_changes:
            changed = [k for k in vals if k in matrix_fields]
            for user in self:
                _logger.info(
                    "User %s (ID: %s) matrix access modified: %s",
                    user.name, user.id, ', '.join(changed)
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
