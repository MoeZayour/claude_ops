# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class OpsPersona(models.Model):
    _name = 'ops.persona'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'OPS Persona - Role Assignment with Matrix Dimensions'
    _order = 'sequence, name'
    
    # ============================================
    # BASIC IDENTIFICATION FIELDS
    # ============================================
    name = fields.Char(
        string='Persona Name',
        required=True,
        tracking=True,
        help='Display name for this persona/role assignment. '
             'Format: "[Location] [Role]" or "[Role] - [BusinessUnit]". '
             'Examples: "Seattle Store Manager", "Retail Director - Electronics", "Regional VP - North". '
             'This name appears in: approval requests, delegation records, user dashboards, reports. '
             'Best Practice: Use clear, descriptive names that immediately identify the role and scope. '
             'A persona combines a user with specific matrix access (branches + business units).'
    )
    
    code = fields.Char(
        string='Persona Code',
        required=True,
        copy=False,
        default='New',
        help='Unique identifier for this persona across all companies. '
             'Auto-generated on save (format: PRS-XXXX). '
             'Cannot be changed after creation. '
             'Used in: Audit logs, approval workflows, reporting, API integrations. '
             'Example: PRS-001, PRS-MGR-SEA, PRS-DIR-RETAIL.'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of this persona\'s role, responsibilities, and scope of authority. '
             'Include: Key responsibilities, decision-making authority, reporting structure, coverage areas. '
             'Example: "Manages all retail operations for Seattle branch including sales, inventory, and staff. '
             'Approval authority up to $50K. Reports to Regional Director. Covers Electronics and Appliances BUs." '
             'Use Cases: Onboarding new users, defining role boundaries, documenting approval limits. '
             'Best Practice: Update when responsibilities change.'
    )
    
    # ============================================
    # USER ASSIGNMENT
    # ============================================
    user_id = fields.Many2one(
        'res.users',
        string='Assigned User',
        required=False,  # Can be empty for draft personas
        ondelete='cascade',
        tracking=True,
        help='The Odoo user who is assigned to this persona/role. '
             'This user inherits all matrix access (branches, business units) defined in this persona. '
             'A user can have multiple personas (e.g., Store Manager + Regional Backup). '
             'Can be empty for template personas or during setup. '
             'When assigned: User automatically gains access to the specified branches and BUs. '
             'Important: Changing the user immediately updates their system access. '
             'Related: User can delegate this persona to another user temporarily.'
    )
    
    # Multi-user support (optional - for future use)
    secondary_user_ids = fields.Many2many(
        'res.users',
        'persona_secondary_users_rel',
        'persona_id',
        'user_id',
        string='Secondary Users',
        help='Additional backup users who can act under this persona when the primary user is unavailable. '
             'Use Cases: Vacation coverage, peak period support, cross-training, emergency backup. '
             'Secondary users have the same access as the primary user for this persona. '
             'Example: Primary = Store Manager, Secondary = Assistant Manager (can cover during manager absence). '
             'Note: For temporary coverage, use the Delegation system instead.'
    )
    
    # Legacy HR integration
    employee_id = fields.Many2one(
        'hr.employee',
        string='Related Employee',
        tracking=True,
        help="The HR Employee record (for hierarchy and department logic)"
    )
    
    # ============================================
    # MATRIX DIMENSION ASSIGNMENTS
    # ============================================
    
    # Company assignment
    company_id = fields.Many2one(
        'res.company',
        string='Primary Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
        help='The legal entity (company) this persona belongs to. Required. '
             'All assigned branches must belong to this company. '
             'Used for: Financial reporting, legal compliance, multi-company access control. '
             'Important: Cannot be changed if persona has historical transactions. '
             'Multi-Company Note: A user can have different personas in different companies.'
    )
    
    # Branch assignments (multi-branch support) - NEW OPS.BRANCH MODEL
    branch_ids = fields.Many2many(
        'ops.branch',
        'persona_branch_rel',
        'persona_id',
        'branch_id',
        string='Assigned Branches',
        domain="[('company_id', '=', company_id)]",
        help='Branches (locations) where this persona can operate and access data. '
             'The user assigned to this persona will see transactions only from these branches. '
             'Examples: '
             '- Single-branch persona: Manager of Seattle Store → [Seattle] '
             '- Multi-branch persona: Regional Director → [Seattle, Portland, Vancouver] '
             '- Nationwide persona: VP Sales → [All retail branches]. '
             'Access Control: User can view/create transactions only in assigned branches. '
             'Reporting: Reports can be filtered by these branches. '
             'Must be from the same company as the persona.'
    )
    
    # Business Unit assignments (multi-BU support)
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'persona_business_unit_rel',
        'persona_id',
        'unit_id',
        string='Assigned Business Units',
        help='Business Units (product lines/divisions) this persona can access and manage. '
             'Combined with branch access, this defines the complete matrix scope. '
             'Examples: '
             '- "Seattle Store Manager" → Branches:[Seattle], BUs:[Retail Electronics, Retail Appliances] '
             '- "Wholesale Director" → Branches:[All], BUs:[Wholesale] '
             '- "Electronics VP" → Branches:[All retail], BUs:[Electronics only]. '
             'Access Control: User sees only products and transactions for these BUs in their branches. '
             'Matrix Rule: User access = Intersection of (Assigned Branches) × (Assigned BUs). '
             'Validation: Selected BUs must operate in at least one assigned branch.'
    )
    
    # ============================================
    # DEFAULT SELECTIONS FOR TRANSACTIONS
    # ============================================
    default_branch_id = fields.Many2one(
        'ops.branch',
        string='Default Branch',
        domain="[('id', 'in', branch_ids)]",
        help='The branch that is automatically pre-selected when user creates new transactions. '
             'Must be one of the assigned branches above. '
             'Used when creating: Sales orders, purchase orders, invoices, stock transfers. '
             'User can change to other assigned branches if needed. '
             'Example: Regional manager has 10 branches but defaults to headquarters branch. '
             'Best Practice: Set to the user\'s primary work location. '
             'Leave empty for multi-branch users without a primary location.'
    )
    
    default_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Default Business Unit',
        domain="[('id', 'in', business_unit_ids)]",
        help='The Business Unit that is automatically pre-selected when user creates new transactions. '
             'Must be one of the assigned BUs above. '
             'Used when creating: Sales orders, products, quotations, reports. '
             'User can change to other assigned BUs if needed. '
             'Example: Manager handles Retail and Wholesale but defaults to Retail (higher volume). '
             'Best Practice: Set to the BU the user works with most frequently. '
             'Leave empty for users without a primary BU focus.'
    )
    
    # ============================================
    # ROLE INDICATORS AND AUTHORITIES
    # ============================================
    is_branch_manager = fields.Boolean(
        string='Branch Manager',
        default=False,
        help='This persona has branch management authority'
    )
    
    is_bu_leader = fields.Boolean(
        string='Business Unit Leader',
        default=False,
        help='This persona has BU leadership authority'
    )
    
    is_cross_branch = fields.Boolean(
        string='Cross-Branch Authority',
        default=False,
        help='Can access same BU across multiple branches'
    )
    
    is_matrix_administrator = fields.Boolean(
        string='Matrix Administrator',
        default=False,
        help='Can configure matrix structure and rules'
    )

    # Legacy approval and limit fields (compatibility with test seed)
    max_discount_percent = fields.Float(
        string='Max Discount %',
        default=0.0,
        help='Maximum discount percentage this persona can apply (legacy compatibility)'
    )
    max_sale_amount = fields.Float(
        string='Max Sale Amount',
        default=0.0,
        help='Maximum sale amount this persona can approve (legacy compatibility)'
    )
    max_payment_amount = fields.Float(
        string='Max Payment Amount',
        default=0.0,
        help='Maximum payment amount this persona can approve (legacy compatibility)'
    )
    can_approve_sales = fields.Boolean(
        string='Can Approve Sales',
        default=False,
        help='Allow this persona to approve sales documents (legacy compatibility)'
    )
    can_approve_payments = fields.Boolean(
        string='Can Approve Payments',
        default=False,
        help='Allow this persona to approve payments (legacy compatibility)'
    )
    
    is_approver = fields.Boolean(
        string='Approver Role',
        default=False,
        help='Can approve transactions and requests'
    )
    
    # Approval limits
    approval_limit = fields.Monetary(
        string='Approval Limit Amount',
        currency_field='currency_id',
        help='Maximum amount this persona can approve'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True
    )
    
    # Legacy approval flags
    can_approve_orders = fields.Boolean(
        string='Can Approve Orders',
        default=False,
        help='Computed from is_approver for backward compatibility'
    )
    
    can_approve_expenses = fields.Boolean(
        string='Can Approve Expenses',
        default=False,
        help='Computed from is_approver for backward compatibility'
    )
    
    can_approve_leave = fields.Boolean(
        string='Can Approve Leave',
        default=False,
        help='Computed from is_approver for backward compatibility'
    )
    
    can_manage_team = fields.Boolean(
        string='Can Manage Team',
        default=False,
        help='Computed from is_branch_manager or is_bu_leader'
    )
    
    # ============================================
    # SEGREGATION OF DUTIES (SoD) AUTHORITY FLAGS
    # ============================================
    can_modify_product_master = fields.Boolean(
        string='Can Modify Product Master',
        default=False,
        help='Authority to modify product cost and supplier information. '
             'Restricted to Procurement and Finance roles to prevent cost manipulation.'
    )
    
    can_access_cost_prices = fields.Boolean(
        string='Can Access Cost Prices',
        default=False,
        help='Authority to view product cost prices. '
             'Restricted from Sales to maintain margin confidentiality.'
    )
    
    can_validate_invoices = fields.Boolean(
        string='Can Validate Invoices',
        default=False,
        help='Authority to validate and post customer/vendor invoices. '
             'Restricted to Accountant level and above.'
    )
    
    can_post_journal_entries = fields.Boolean(
        string='Can Post Journal Entries',
        default=False,
        help='Authority to post accounting journal entries. '
             'Restricted to Accountant/CFO only to prevent financial manipulation.'
    )
    
    can_execute_payments = fields.Boolean(
        string='Can Execute Payments',
        default=False,
        help='Authority to execute vendor payments and transfers. '
             'Restricted to Treasury role only for financial control.'
    )
    
    can_adjust_inventory = fields.Boolean(
        string='Can Adjust Inventory',
        default=False,
        help='Authority to post inventory adjustments (write-offs, corrections). '
             'Restricted to Inventory Manager to prevent stock manipulation.'
    )
    
    can_manage_pdc = fields.Boolean(
        string='Can Manage PDC',
        default=False,
        help='Authority to post and deposit Post Dated Checks. '
             'Restricted to authorized Treasury/Finance personnel.'
    )
    
    # ============================================
    # DELEGATION SYSTEM INTEGRATION
    # ============================================
    can_be_delegated = fields.Boolean(
        string='Allow Delegation',
        default=True,
        help='Whether this persona can be delegated'
    )
    
    # Delegation Records
    delegation_ids = fields.One2many(
        'ops.persona.delegation',
        'persona_id',
        string='Delegations',
        help='All delegation records for this persona'
    )
    
    active_delegation_id = fields.Many2one(
        'ops.persona.delegation',
        string='Active Delegation',
        compute='_compute_active_delegation',
        store=False,
        compute_sudo=True,
        help='Currently active delegation record, if any'
    )
    
    # Legacy delegation fields (computed from delegation records)
    delegate_id = fields.Many2one(
        'res.users',
        string='Current Delegate',
        compute='_compute_active_delegation',
        store=False,
        compute_sudo=True,
        help='User temporarily acting as this persona'
    )
    
    delegation_start = fields.Datetime(
        string='Delegation Start',
        compute='_compute_active_delegation',
        store=False,
        compute_sudo=True
    )
    
    delegation_end = fields.Datetime(
        string='Delegation End',
        compute='_compute_active_delegation',
        store=False,
        compute_sudo=True
    )
    
    is_delegated = fields.Boolean(
        string='Is Delegated',
        compute='_compute_active_delegation',
        store=False,
        compute_sudo=True,
        help='Active delegation is in effect'
    )
    
    effective_user_id = fields.Many2one(
        'res.users',
        string='Effective User',
        compute='_compute_effective_user',
        store=True,
        help='User who currently holds this persona\'s power'
    )
    
    # Delegation history
    delegation_history_ids = fields.One2many(
        'ops.persona.delegation',
        'persona_id',
        string='Delegation History',
        help='Historical record of delegations'
    )
    
    # ============================================
    # COMPUTED FIELDS FOR UI DISPLAY
    # ============================================
    branch_count = fields.Integer(
        compute='_compute_counts',
        string='Branch Count',
        store=True
    )
    
    bu_count = fields.Integer(
        compute='_compute_counts',
        string='Business Unit Count',
        store=True
    )
    
    matrix_access_summary = fields.Char(
        compute='_compute_matrix_access_summary',
        string='Matrix Access Summary',
        store=True,
        help='Summary of matrix access rights'
    )
    
    # ============================================
    # HIERARCHY & JOB FUNCTION
    # ============================================
    parent_id = fields.Many2one(
        'ops.persona',
        string='Parent Persona',
        help='Reporting line'
    )
    
    child_ids = fields.One2many(
        'ops.persona',
        'parent_id',
        string='Direct Reports'
    )
    
    job_level = fields.Selection([
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
        ('lead', 'Team Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('executive', 'Executive'),
    ], string='Job Level', default='mid', tracking=True)
    
    # ============================================
    # SECURITY GROUPS
    # ============================================
    access_group_ids = fields.Many2many(
        'res.groups',
        'ops_persona_groups_rel',
        'persona_id',
        'group_id',
        string='Odoo Security Groups'
    )

    # Generated System Group (from activation)
    group_id = fields.Many2one(
        'res.groups',
        string='System Group',
        readonly=True,
        ondelete='set null',
        help='The Odoo Security Group generated when this persona was activated. '
             'This group can be assigned to users to grant them the persona\'s permissions.'
    )
    
    # ============================================
    # STATUS AND VALIDITY
    # ============================================
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help='Active personas are available for assignment'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Controls the display order of personas in lists and selection menus. '
             'Lower numbers appear first. Default is 10. '
             'Use Cases: Prioritize frequently-used personas, group by hierarchy, order by importance. '
             'Example: CEO = 1, Directors = 5, Managers = 10, Staff = 20. '
             'Tip: Use increments of 5 to allow easy reordering without affecting other personas.'
    )
    
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.today,
        help='The date when this persona assignment becomes effective and user gains access. '
             'Use Cases: '
             '- Future assignments: Create persona in advance, starts on employee join date '
             '- Promotions: Schedule new role to start on promotion date '
             '- Reorganizations: Coordinate role changes with org structure changes. '
             'Default: Today\'s date (immediate effect). '
             'Important: User will not have access until this date arrives. '
             'System checks this date when determining active personas.'
    )
    
    end_date = fields.Date(
        string='End Date',
        help='Optional date when this persona assignment expires and access is automatically revoked. '
             'Leave empty for permanent assignments. '
             'Use Cases: '
             '- Temporary assignments: Project managers, interim coverage, seasonal roles '
             '- Contract employees: Set to contract end date '
             '- Planned departures: Set when resignation notice is received. '
             'Auto-Deactivation: System automatically deactivates persona after this date (via scheduled job). '
             'User loses access on the day after the end date. '
             'Example: Temporary holiday season manager from Nov 1 to Jan 15.'
    )
    
    is_active_today = fields.Boolean(
        compute='_compute_is_active_today',
        string='Currently Active',
        store=True,
        help='Persona is active today based on start/end dates'
    )
    
    # Audit fields
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True,
        help='When persona was last synced to user access'
    )
    
    # Legacy user count
    user_count = fields.Integer(
        compute='_compute_user_count',
        string='User Count'
    )
    
    user_ids = fields.One2many(
        'res.users',
        'persona_id',
        string='Assigned Users'
    )
    
    # ============================================
    # COMPUTED METHODS
    # ============================================
    
    @api.depends('branch_ids', 'business_unit_ids')
    def _compute_counts(self):
        """Compute counts of branches and business units."""
        for persona in self:
            persona.branch_count = len(persona.branch_ids)
            persona.bu_count = len(persona.business_unit_ids)
    
    @api.depends('delegation_ids', 'delegation_ids.active', 
                 'delegation_ids.start_date', 'delegation_ids.end_date')
    def _compute_active_delegation(self):
        """Compute currently active delegation and related fields."""
        now = fields.Datetime.now()
        for persona in self:
            # Find active delegation
            active_delegation = self.env['ops.persona.delegation'].search([
                ('persona_id', '=', persona.id),
                ('active', '=', True),
                ('start_date', '<=', now),
                ('end_date', '>=', now)
            ], limit=1, order='start_date desc')
            
            # Set computed fields
            persona.active_delegation_id = active_delegation
            persona.is_delegated = bool(active_delegation)
            persona.delegate_id = active_delegation.delegate_id if active_delegation else False
            persona.delegation_start = active_delegation.start_date if active_delegation else False
            persona.delegation_end = active_delegation.end_date if active_delegation else False
    
    @api.depends('user_id', 'delegation_ids', 'delegation_ids.active',
                 'delegation_ids.start_date', 'delegation_ids.end_date')
    def _compute_effective_user(self):
        """Determine who holds the power right now."""
        now = fields.Datetime.now()
        for persona in self:
            # Check for active delegation
            active_delegation = self.env['ops.persona.delegation'].search([
                ('persona_id', '=', persona.id),
                ('active', '=', True),
                ('start_date', '<=', now),
                ('end_date', '>=', now)
            ], limit=1)
            
            if active_delegation:
                persona.effective_user_id = active_delegation.delegate_id
            else:
                persona.effective_user_id = persona.user_id
    
    @api.depends('branch_ids', 'business_unit_ids', 'is_branch_manager', 
                 'is_bu_leader', 'is_cross_branch', 'is_matrix_administrator')
    def _compute_matrix_access_summary(self):
        """Compute human-readable summary of matrix access."""
        for persona in self:
            parts = []
            
            # Branch access summary
            if persona.branch_ids:
                if persona.branch_count <= 3:
                    branch_names = persona.branch_ids.mapped('code')
                    parts.append(f"Branches: {', '.join(branch_names)}")
                else:
                    parts.append(f"Branches: {persona.branch_count}")
            
            # BU access summary
            if persona.business_unit_ids:
                if persona.bu_count <= 3:
                    bu_names = persona.business_unit_ids.mapped('code')
                    parts.append(f"BUs: {', '.join(bu_names)}")
                else:
                    parts.append(f"BUs: {persona.bu_count}")
            
            # Role indicators
            if persona.is_branch_manager:
                parts.append("Branch Manager")
            if persona.is_bu_leader:
                parts.append("BU Leader")
            if persona.is_cross_branch:
                parts.append("Cross-Branch")
            if persona.is_matrix_administrator:
                parts.append("Matrix Admin")
            if persona.is_approver:
                parts.append("Approver")
            
            persona.matrix_access_summary = " | ".join(parts) if parts else "No matrix access"
    
    @api.depends('active', 'start_date', 'end_date')
    def _compute_is_active_today(self):
        """Determine if persona is active today based on dates."""
        today = fields.Date.today()
        for persona in self:
            active_by_date = True
            if persona.start_date and persona.start_date > today:
                active_by_date = False
            if persona.end_date and persona.end_date < today:
                active_by_date = False
            
            persona.is_active_today = persona.active and active_by_date
    
    def _compute_user_count(self):
        """Compute count of users assigned to this persona."""
        if not self:
            return
        user_data = self.env['res.users'].read_group(
            [('persona_id', 'in', self.ids)],
            ['persona_id'],
            ['persona_id']
        )
        mapped_data = {d['persona_id'][0]: d['persona_id_count'] for d in user_data if d['persona_id']}
        for record in self:
            record.user_count = mapped_data.get(record.id, 0)
    
    # ============================================
    # CONSTRAINT METHODS
    # ============================================
    
    @api.constrains('branch_ids', 'company_id')
    def _check_branch_company(self):
        """Ensure all branches belong to persona's company."""
        for persona in self:
            invalid_branches = persona.branch_ids.filtered(
                lambda b: b.company_id != persona.company_id
            )
            if invalid_branches:
                raise ValidationError(_(
                    "Branches %(branch_names)s do not belong to company %(company_name)s. "
                    "Please select branches from the correct company."
                ) % {
                    'branch_names': ', '.join(invalid_branches.mapped('name')),
                    'company_name': persona.company_id.name
                })
    
    @api.constrains('business_unit_ids', 'branch_ids')
    def _check_bu_branch_compatibility(self):
        """Ensure BUs operate in assigned branches."""
        for persona in self:
            for bu in persona.business_unit_ids:
                # Check if BU operates in at least one of persona's branches
                compatible_branches = bu.branch_ids & persona.branch_ids
                if not compatible_branches:
                    raise ValidationError(_(
                        "Business Unit '%(bu_name)s' does not operate in any of "
                        "persona's assigned branches. Please assign compatible branches."
                    ) % {'bu_name': bu.name})
    
    @api.constrains('default_branch_id', 'branch_ids')
    def _check_default_branch(self):
        """Ensure default branch is in assigned branches."""
        for persona in self:
            if (persona.default_branch_id and 
                persona.default_branch_id not in persona.branch_ids):
                raise ValidationError(_(
                    "Default branch '%(branch_name)s' must be in persona's assigned branches."
                ) % {'branch_name': persona.default_branch_id.name})
    
    @api.constrains('default_business_unit_id', 'business_unit_ids')
    def _check_default_bu(self):
        """Ensure default BU is in assigned BUs."""
        for persona in self:
            if (persona.default_business_unit_id and 
                persona.default_business_unit_id not in persona.business_unit_ids):
                raise ValidationError(_(
                    "Default business unit '%(bu_name)s' must be in persona's assigned business units."
                ) % {'bu_name': persona.default_business_unit_id.name})
    
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        """Prevent circular parent relationships."""
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive persona hierarchies.'))
    
    # ============================================
    # CRUD METHODS
    # ============================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate code and sync with user."""
        # Generate codes
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.persona.code') or 'PRS0001'
        
        personas = super().create(vals_list)
        
        # Sync to user access
        personas._sync_user_access()
        
        # Log creation
        for persona in personas:
            _logger.info(f"Persona created: {persona.name} (ID: {persona.id}) for user {persona.user_id.name if persona.user_id else 'N/A'}")
            persona.message_post(
                body=_('Persona created with access to %d branches and %d business units.') % (
                    persona.branch_count, persona.bu_count
                )
            )
        
        return personas
    
    def write(self, vals):
        """Override write to sync changes to user access."""
        # Track changes for logging
        changes = {}
        matrix_fields = ['branch_ids', 'business_unit_ids', 'default_branch_id', 
                        'default_business_unit_id', 'user_id', 'active',
                        'is_branch_manager', 'is_bu_leader', 'is_cross_branch']
        
        for field in matrix_fields:
            if field in vals:
                changes[field] = {
                    'old': str(self.mapped(field)),
                    'new': str(vals[field])
                }
        
        # Perform write
        result = super().write(vals)
        
        # Sync to user if matrix fields changed
        sync_fields = ['branch_ids', 'business_unit_ids', 'default_branch_id', 
                      'default_business_unit_id', 'user_id', 'active',
                      'is_branch_manager', 'is_bu_leader', 'is_cross_branch',
                      'is_matrix_administrator']
        
        if any(field in vals for field in sync_fields):
            self._sync_user_access()
            self.last_sync_date = fields.Datetime.now()
        
        # Log changes
        for field, change in changes.items():
            if change['old'] != change['new']:
                for persona in self:
                    persona.message_post(
                        body=_('Persona field updated: %(field)s changed.') % {
                            'field': field
                        }
                    )
        
        return result
    
    def unlink(self):
        """Override unlink to remove user access before deletion."""
        # Store user references for cleanup
        user_persona_map = {}
        for persona in self:
            if persona.user_id:
                user_id = persona.user_id.id
                if user_id not in user_persona_map:
                    user_persona_map[user_id] = []
                user_persona_map[user_id].append(persona.id)
        
        # Remove access before deletion
        for persona in self:
            persona._remove_user_access()
        
        # Perform deletion
        result = super().unlink()
        
        # Log deletion
        for user_id, persona_ids in user_persona_map.items():
            _logger.info(f"Personas {persona_ids} deleted for user {user_id}")
        
        return result
    
    # ============================================
    # SYNC METHODS FOR USER ACCESS
    # ============================================
    
    def _sync_user_access(self):
        """Sync persona access to the assigned user."""
        for persona in self.filtered(lambda p: p.is_active_today and p.user_id):
            user = persona.user_id
            
            # Get all active personas for this user
            active_personas = self.search([
                ('user_id', '=', user.id),
                ('is_active_today', '=', True),
            ])
            
            # Collect all access from all active personas
            all_branches = self.env['ops.branch']
            all_bus = self.env['ops.business.unit']
            all_companies = self.env['res.company']
            
            has_branch_manager = False
            has_bu_leader = False
            has_cross_branch = False
            has_matrix_admin = False
            
            for active_persona in active_personas:
                all_branches |= active_persona.branch_ids
                all_bus |= active_persona.business_unit_ids
                all_companies |= active_persona.branch_ids.mapped('company_id')
                
                if active_persona.is_branch_manager:
                    has_branch_manager = True
                if active_persona.is_bu_leader:
                    has_bu_leader = True
                if active_persona.is_cross_branch:
                    has_cross_branch = True
                if active_persona.is_matrix_administrator:
                    has_matrix_admin = True
            
            # Determine defaults (prefer this persona's defaults)
            default_branch_obj = persona.default_branch_id or (all_branches[0] if all_branches else False)
            default_company = default_branch_obj.company_id if default_branch_obj else (all_companies[0] if all_companies else False)
            default_bu = persona.default_business_unit_id or (all_bus[0] if all_bus else False)
            
            # Update user access (if user has matrix fields)
            user_vals = {}
            if hasattr(user, 'allowed_branch_ids'):
                user_vals['allowed_branch_ids'] = [(6, 0, all_companies.ids)]
            if hasattr(user, 'allowed_business_unit_ids'):
                user_vals['allowed_business_unit_ids'] = [(6, 0, all_bus.ids)]
            if hasattr(user, 'default_branch_id'):
                user_vals['default_branch_id'] = default_company.id if default_company else False
            if hasattr(user, 'default_business_unit_id'):
                user_vals['default_business_unit_id'] = default_bu.id if default_bu else False
            if hasattr(user, 'is_cross_branch_bu_leader'):
                user_vals['is_cross_branch_bu_leader'] = has_cross_branch
            
            if user_vals:
                user.write(user_vals)
            
            # Update group membership for roles
            self._sync_user_groups(user, {
                'is_branch_manager': has_branch_manager,
                'is_bu_leader': has_bu_leader,
                'is_matrix_administrator': has_matrix_admin,
            })
            
            _logger.debug(f"Synced persona {persona.name} access to user {user.name}")
    
    def _remove_user_access(self):
        """Remove persona access from user."""
        for persona in self:
            if not persona.user_id:
                continue
                
            user = persona.user_id
            
            # Check if user has other active personas
            other_active_personas = self.search([
                ('id', '!=', persona.id),
                ('user_id', '=', user.id),
                ('is_active_today', '=', True),
            ])
            
            if other_active_personas:
                # User has other personas, resync based on remaining personas
                other_active_personas._sync_user_access()
            else:
                # No other active personas, clear matrix access
                user_vals = {}
                if hasattr(user, 'allowed_branch_ids'):
                    user_vals['allowed_branch_ids'] = [(5, 0, 0)]
                if hasattr(user, 'allowed_business_unit_ids'):
                    user_vals['allowed_business_unit_ids'] = [(5, 0, 0)]
                if hasattr(user, 'default_branch_id'):
                    user_vals['default_branch_id'] = False
                if hasattr(user, 'default_business_unit_id'):
                    user_vals['default_business_unit_id'] = False
                if hasattr(user, 'is_cross_branch_bu_leader'):
                    user_vals['is_cross_branch_bu_leader'] = False
                
                if user_vals:
                    user.write(user_vals)
                
                # Clear role groups
                self._sync_user_groups(user, {
                    'is_branch_manager': False,
                    'is_bu_leader': False,
                    'is_matrix_administrator': False,
                })
    
    def _sync_user_groups(self, user, role_flags):
        """Sync user group membership based on role flags."""
        group_refs = {
            'is_branch_manager': 'ops_matrix_core.group_ops_branch_manager',
            'is_bu_leader': 'ops_matrix_core.group_ops_bu_leader',
            'is_matrix_administrator': 'ops_matrix_core.group_ops_matrix_administrator',
        }
        
        for role_field, group_ref in group_refs.items():
            try:
                group = self.env.ref(group_ref, False)
                if group:
                    if role_flags.get(role_field, False):
                        # Add to group if not already member
                        if group not in user.group_ids:
                            user.group_ids = [(4, group.id)]
                    else:
                        # Remove from group if member
                        if group in user.group_ids:
                            user.group_ids = [(3, group.id)]
            except Exception as e:
                _logger.warning(f"Failed to sync group {group_ref}: {e}")
    
    # ============================================
    # DELEGATION METHODS
    # ============================================
    
    def action_delegate_persona(self):
        """Open wizard to create a new delegation."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Delegation'),
            'res_model': 'ops.persona.delegation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_persona_id': self.id,
                'default_delegator_id': self.user_id.id if self.user_id else False,
            }
        }
    
    def action_revoke_delegation(self):
        """Revoke active delegation."""
        self.ensure_one()
        
        active_delegation = self.env['ops.persona.delegation'].get_active_delegation_for_persona(self.id)
        
        if not active_delegation:
            raise UserError(_("No active delegation to revoke."))
        
        # Deactivate delegation
        active_delegation.write({'active': False})
        
        # Resync user access
        self._sync_user_access()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Delegation Revoked'),
                'message': _('Delegation for persona %s has been revoked.') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }
    
    def action_view_delegations(self):
        """View all delegations for this persona."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delegations'),
            'res_model': 'ops.persona.delegation',
            'view_mode': 'list,form',
            'domain': [('persona_id', '=', self.id)],
            'context': {
                'default_persona_id': self.id,
            }
        }
    
    def get_effective_user(self):
        """Helper method to get the effective user (considering delegation)."""
        self.ensure_one()
        now = fields.Datetime.now()
        
        # Check for active delegation
        active_delegation = self.env['ops.persona.delegation'].search([
            ('persona_id', '=', self.id),
            ('active', '=', True),
            ('start_date', '<=', now),
            ('end_date', '>=', now)
        ], limit=1)
        
        if active_delegation:
            return active_delegation.delegate_id
        
        return self.user_id
    
    def _get_active_user(self):
        """Legacy method - kept for backward compatibility."""
        return self.get_effective_user()
    
    @api.model
    def get_active_persona_for_user(self, user_id):
        """Find which Persona a specific User ID is currently acting as."""
        if isinstance(user_id, int):
            user_id = self.env['res.users'].browse(user_id)
        
        now = fields.Datetime.now()
        
        # 1. Check if user is a delegate for any persona
        active_delegations = self.env['ops.persona.delegation'].search([
            ('delegate_id', '=', user_id.id),
            ('active', '=', True),
            ('start_date', '<=', now),
            ('end_date', '>=', now)
        ], order='start_date desc', limit=1)
        
        if active_delegations:
            return active_delegations.persona_id
        
        # 2. Check user's own persona
        owned_personas = self.search([
            ('user_id', '=', user_id.id),
            ('active', '=', True),
            ('is_active_today', '=', True)
        ], limit=1)
        
        return owned_personas if owned_personas else self.browse()
    
    def get_active_delegation(self):
        """Get the currently active delegation for this persona, if any."""
        self.ensure_one()
        return self.env['ops.persona.delegation'].get_active_delegation_for_persona(self.id)
    
    def has_active_delegation(self):
        """Check if this persona has an active delegation."""
        self.ensure_one()
        return bool(self.get_active_delegation())
    
    # ============================================
    # BUSINESS METHODS
    # ============================================

    # ---------------------------------------------------------
    # ACTIVATION LOGIC (Template -> Real Group)
    # ---------------------------------------------------------
    def action_activate_persona(self):
        """
        Converts this Persona Template into a real Odoo Security Group.

        This creates an `res.groups` record linked to this persona, enabling
        the persona to be assigned to users via Odoo's standard group mechanism.
        """
        for persona in self:
            if persona.group_id:
                # Already linked to a group - skip
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Already Activated'),
                        'message': _("Persona '%s' is already linked to group '%s'.") % (
                            persona.name, persona.group_id.name
                        ),
                        'type': 'warning',
                        'sticky': False,
                    }
                }

            # 1. Create the Group Name (e.g., "OPS / Financial Controller")
            group_name = f"OPS / {persona.name}"

            # 2. Find or Create the "OPS Personas" Category
            category = self.env['ir.module.category'].search(
                [('name', '=', 'OPS Personas')], limit=1
            )
            if not category:
                category = self.env['ir.module.category'].create({
                    'name': 'OPS Personas',
                    'description': 'Security groups generated from OPS Persona templates',
                    'sequence': 100,
                })

            # 3. Create the Real Odoo Group
            group = self.env['res.groups'].create({
                'name': group_name,
                'category_id': category.id,
                'comment': f"Generated from OPS Persona: {persona.description or persona.name}",
            })

            # 4. Link it back to the persona
            persona.write({
                'group_id': group.id,
                'active': True,
            })

            # 5. Add the new group to the persona's access_group_ids
            persona.access_group_ids = [(4, group.id)]

            # 6. Log the activation
            persona.message_post(
                body=_("Persona activated. Security Group '%s' created (ID: %s).") % (
                    group_name, group.id
                ),
                subject=_('Persona Activated')
            )
            _logger.info(
                "Persona %s (ID: %s) activated - created group '%s' (ID: %s)",
                persona.name, persona.id, group_name, group.id
            )

            # 7. Notify User
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Persona Activated'),
                    'message': _("Security Group '%s' created successfully.") % group_name,
                    'type': 'success',
                    'sticky': False,
                }
            }

        return True

    def action_view_user_access(self):
        """Open view of user's current access."""
        self.ensure_one()
        return {
            'name': _('User Access Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'form',
            'res_id': self.user_id.id if self.user_id else False,
            'views': [(False, 'form')],
            'target': 'current',
        }
    
    def action_view_branches(self):
        """Open view of assigned branches."""
        self.ensure_one()
        return {
            'name': _('Assigned Branches'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.branch',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.branch_ids.ids)],
            'context': {
                'search_default_active': 1,
                'default_company_id': self.company_id.id,
            }
        }
    
    def action_view_business_units(self):
        """Open view of assigned business units."""
        self.ensure_one()
        return {
            'name': _('Assigned Business Units'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.business.unit',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.business_unit_ids.ids)],
            'context': {
                'search_default_active': 1,
                'default_company_id': self.company_id.id,
            }
        }
    
    def action_force_sync(self):
        """Force sync of persona access to user."""
        self.ensure_one()
        self._sync_user_access()
        self.last_sync_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _('Persona access synced to user %s.') % (self.user_id.name if self.user_id else 'N/A'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_check_access_compliance(self):
        """Check if persona access complies with security rules."""
        self.ensure_one()
        
        issues = []
        
        # Check branch assignments
        if not self.branch_ids:
            issues.append(_("No branches assigned."))
        
        # Check BU assignments
        if not self.business_unit_ids:
            issues.append(_("No business units assigned."))
        
        # Check compatibility
        for bu in self.business_unit_ids:
            compatible_branches = bu.branch_ids & self.branch_ids
            if not compatible_branches:
                issues.append(_(
                    "Business Unit '%(bu_name)s' is not compatible with assigned branches."
                ) % {'bu_name': bu.name})
        
        # Check role assignments
        if self.is_branch_manager and len(self.branch_ids) > 1:
            issues.append(_(
                "Branch manager role assigned to multiple branches. "
                "Typically a branch manager manages only one branch."
            ))
        
        if self.is_cross_branch and not self.is_bu_leader:
            issues.append(_(
                "Cross-branch authority requires BU leader role."
            ))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Access Compliance Check'),
                'message': '\n'.join(issues) if issues else _('No compliance issues found.'),
                'type': 'warning' if issues else 'success',
                'sticky': True,
            }
        }
    
    # ============================================
    # CRON/SCHEDULED ACTIONS
    # ============================================
    
    @api.model
    def cron_sync_all_personas(self):
        """Scheduled job to sync all active personas."""
        active_personas = self.search([('is_active_today', '=', True)])
        
        synced_count = 0
        for persona in active_personas:
            try:
                persona._sync_user_access()
                persona.last_sync_date = fields.Datetime.now()
                synced_count += 1
            except Exception as e:
                _logger.error(f"Failed to sync persona {persona.id}: {e}")
                persona.message_post(
                    body=_('Auto-sync failed: %s') % str(e),
                    subject=_('Sync Error')
                )
        
        _logger.info(f"Auto-synced {synced_count} personas out of {len(active_personas)}")
    
    @api.model
    def cron_check_delegation_expiry(self):
        """Check for expired delegations and revoke them."""
        now = fields.Datetime.now()
        
        # Find expired delegations
        expired_delegations = self.env['ops.persona.delegation'].search([
            ('active', '=', True),
            ('end_date', '!=', False),
            ('end_date', '<=', now),
        ])
        
        for delegation in expired_delegations:
            try:
                delegation.write({'active': False})
                delegation.persona_id._sync_user_access()
                _logger.info(f"Auto-revoked expired delegation {delegation.id} for persona {delegation.persona_id.id}")
            except Exception as e:
                _logger.error(f"Failed to auto-revoke delegation {delegation.id}: {e}")
