# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class OpsWelcomeWizard(models.TransientModel):
    """
    OPS Matrix Framework - Welcome & Setup Wizard
    
    Guides users through the initial setup of the OPS Matrix Framework:
    1. Welcome & Overview
    2. Company Configuration
    3. Branch Creation
    4. Business Unit Setup
    5. Industry Template Selection
    6. Configuration Summary & Finalization
    """
    _name = 'ops.welcome.wizard'
    _description = 'OPS Matrix Setup Wizard'
    
    # =========================================================================
    # Wizard State Management
    # =========================================================================
    state = fields.Selection([
        ('welcome', 'Welcome'),
        ('company', 'Company Setup'),
        ('branches', 'Branch Configuration'),
        ('business_units', 'Business Units'),
        ('industry', 'Industry Template'),
        ('configuration', 'Matrix Configuration'),
        ('summary', 'Summary & Confirmation'),
        ('complete', 'Setup Complete'),
    ], string='Wizard Step', default='welcome', required=True)
    
    # =========================================================================
    # Company Information
    # =========================================================================
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        help='Select the legal entity to configure'
    )
    
    company_setup_complete = fields.Boolean(
        string='Company Already Configured',
        compute='_compute_company_setup_complete',
        help='Indicates if the company has basic information'
    )
    
    @api.depends('company_id')
    def _compute_company_setup_complete(self):
        """Check if company has minimum required information."""
        for wizard in self:
            if wizard.company_id:
                wizard.company_setup_complete = bool(
                    wizard.company_id.name and
                    wizard.company_id.currency_id and
                    wizard.company_id.country_id
                )
            else:
                wizard.company_setup_complete = False
    
    # =========================================================================
    # Branch Configuration
    # =========================================================================
    branch_count = fields.Integer(
        string='Number of Branches',
        default=1,
        help='How many geographic locations does your organization operate?'
    )
    
    branch_ids = fields.One2many(
        'ops.welcome.wizard.branch',
        'wizard_id',
        string='Branches'
    )
    
    create_sample_branches = fields.Boolean(
        string='Create Sample Branches',
        default=False,
        help='Create example branches for testing'
    )
    
    # =========================================================================
    # Business Unit Configuration
    # =========================================================================
    business_unit_count = fields.Integer(
        string='Number of Business Units',
        default=1,
        help='How many strategic business units/divisions do you have?'
    )
    
    business_unit_ids = fields.One2many(
        'ops.welcome.wizard.business.unit',
        'wizard_id',
        string='Business Units'
    )
    
    create_sample_business_units = fields.Boolean(
        string='Create Sample Business Units',
        default=False,
        help='Create example business units for testing'
    )
    
    # =========================================================================
    # Industry Template
    # =========================================================================
    industry_template = fields.Selection([
        ('retail', 'Retail & Distribution'),
        ('manufacturing', 'Manufacturing'),
        ('services', 'Professional Services'),
        ('hospitality', 'Hospitality & F&B'),
        ('healthcare', 'Healthcare'),
        ('construction', 'Construction & Real Estate'),
        ('custom', 'Custom Configuration'),
    ], string='Industry Template',
       default='custom',
       help='Choose a template optimized for your industry')
    
    # =========================================================================
    # Configuration Settings
    # =========================================================================
    branch_weight = fields.Float(
        string='Branch Weight (%)',
        default=50.0,
        help='Analytic distribution weight for Branch dimension'
    )
    
    business_unit_weight = fields.Float(
        string='Business Unit Weight (%)',
        default=50.0,
        help='Analytic distribution weight for Business Unit dimension'
    )
    
    require_branch_on_transactions = fields.Boolean(
        string='Require Branch on Transactions',
        default=True
    )
    
    require_bu_on_transactions = fields.Boolean(
        string='Require Business Unit on Transactions',
        default=True
    )
    
    # =========================================================================
    # Setup Progress
    # =========================================================================
    setup_log = fields.Text(
        string='Setup Log',
        readonly=True,
        help='Log of setup actions performed'
    )
    
    # =========================================================================
    # Navigation Methods
    # =========================================================================
    def action_next(self):
        """Move to the next step in the wizard."""
        self.ensure_one()
        
        state_sequence = [
            'welcome', 'company', 'branches', 'business_units',
            'industry', 'configuration', 'summary', 'complete'
        ]
        
        current_index = state_sequence.index(self.state)
        
        # Validate current step before proceeding
        self._validate_current_step()
        
        if current_index < len(state_sequence) - 1:
            self.state = state_sequence[current_index + 1]
            
            # Auto-execute certain steps
            if self.state == 'complete':
                self._execute_setup()
        
        return self._reopen_wizard()
    
    def action_back(self):
        """Move to the previous step in the wizard."""
        self.ensure_one()
        
        state_sequence = [
            'welcome', 'company', 'branches', 'business_units',
            'industry', 'configuration', 'summary', 'complete'
        ]
        
        current_index = state_sequence.index(self.state)
        
        if current_index > 0:
            self.state = state_sequence[current_index - 1]
        
        return self._reopen_wizard()
    
    def action_skip(self):
        """Skip the current optional step."""
        self.ensure_one()
        return self.action_next()
    
    def _reopen_wizard(self):
        """Reopen the wizard at the current state."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ops.welcome.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
    
    # =========================================================================
    # Validation Methods
    # =========================================================================
    def _validate_current_step(self):
        """Validate the current wizard step before proceeding."""
        self.ensure_one()
        
        if self.state == 'company':
            if not self.company_id:
                raise ValidationError(_('Please select a company to continue.'))
        
        elif self.state == 'branches':
            if not self.create_sample_branches and not self.branch_ids:
                raise ValidationError(_(
                    'Please create at least one branch or enable sample branch creation.'
                ))
        
        elif self.state == 'business_units':
            if not self.create_sample_business_units and not self.business_unit_ids:
                raise ValidationError(_(
                    'Please create at least one business unit or enable sample BU creation.'
                ))
        
        elif self.state == 'configuration':
            total = self.branch_weight + self.business_unit_weight
            if abs(total - 100.0) > 0.01:
                raise ValidationError(_(
                    'Branch weight (%.2f%%) + Business Unit weight (%.2f%%) must equal 100%%.'
                ) % (self.branch_weight, self.business_unit_weight))
    
    # =========================================================================
    # Setup Execution
    # =========================================================================
    def _execute_setup(self):
        """Execute the complete setup based on wizard configuration."""
        self.ensure_one()
        
        log_lines = []
        log_lines.append(_('=== OPS Matrix Setup Started ==='))
        log_lines.append(_('Company: %s') % self.company_id.name)
        
        try:
            # 1. Create configuration
            config = self._create_matrix_configuration()
            log_lines.append(_('✓ Matrix configuration created'))
            
            # 2. Create branches
            branches = self._create_branches()
            log_lines.append(_('✓ Created %d branches') % len(branches))
            
            # 3. Create business units
            business_units = self._create_business_units(branches)
            log_lines.append(_('✓ Created %d business units') % len(business_units))
            
            # 4. Apply industry template
            if self.industry_template != 'custom':
                config.industry_template = self.industry_template
                config.apply_industry_template()
                log_lines.append(_('✓ Applied %s industry template') % self.industry_template)
            
            # 5. Configure admin user
            self._configure_admin_user(branches, business_units)
            log_lines.append(_('✓ Configured admin user access'))
            
            log_lines.append(_('=== Setup Complete ==='))
            
            self.setup_log = '\n'.join(log_lines)
            
        except Exception as e:
            log_lines.append(_('✗ ERROR: %s') % str(e))
            self.setup_log = '\n'.join(log_lines)
            raise UserError(_(
                'Setup failed with error: %s\n\nPlease contact support or try again.'
            ) % str(e))
    
    def _create_matrix_configuration(self):
        """Create or update matrix configuration."""
        self.ensure_one()
        
        config = self.env['ops.matrix.config'].search([
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not config:
            config = self.env['ops.matrix.config'].create({
                'company_id': self.company_id.id,
                'branch_weight': self.branch_weight,
                'business_unit_weight': self.business_unit_weight,
                'require_branch_on_transactions': self.require_branch_on_transactions,
                'require_bu_on_transactions': self.require_bu_on_transactions,
                'industry_template': self.industry_template,
            })
        else:
            config.write({
                'branch_weight': self.branch_weight,
                'business_unit_weight': self.business_unit_weight,
                'require_branch_on_transactions': self.require_branch_on_transactions,
                'require_bu_on_transactions': self.require_bu_on_transactions,
                'industry_template': self.industry_template,
            })
        
        return config
    
    def _create_branches(self):
        """Create branches based on wizard configuration."""
        self.ensure_one()
        
        if self.create_sample_branches:
            return self._create_sample_branches()
        
        branches = self.env['ops.branch']
        for branch_line in self.branch_ids:
            branch = self.env['ops.branch'].create({
                'name': branch_line.name,
                'code': branch_line.code or 'BR-' + branch_line.name[:3].upper(),
                'company_id': self.company_id.id,
                'address': branch_line.address,
                'phone': branch_line.phone,
                'email': branch_line.email,
            })
            branches |= branch
        
        return branches
    
    def _create_sample_branches(self):
        """Create sample branches for testing."""
        self.ensure_one()
        
        sample_data = [
            {'name': 'Head Office', 'code': 'BR-HQ'},
            {'name': 'Branch A', 'code': 'BR-A'},
            {'name': 'Branch B', 'code': 'BR-B'},
        ]
        
        branches = self.env['ops.branch']
        for data in sample_data[:self.branch_count]:
            branch = self.env['ops.branch'].create({
                'name': data['name'],
                'code': data['code'],
                'company_id': self.company_id.id,
            })
            branches |= branch
        
        return branches
    
    def _create_business_units(self, branches):
        """Create business units based on wizard configuration."""
        self.ensure_one()
        
        if self.create_sample_business_units:
            return self._create_sample_business_units(branches)
        
        business_units = self.env['ops.business.unit']
        for bu_line in self.business_unit_ids:
            # Get branch IDs from wizard line
            branch_ids = bu_line.branch_ids.ids if bu_line.branch_ids else branches.ids
            
            bu = self.env['ops.business.unit'].create({
                'name': bu_line.name,
                'code': bu_line.code or 'BU-' + bu_line.name[:3].upper(),
                'description': bu_line.description,
                'branch_ids': [(6, 0, branch_ids)],
                'primary_branch_id': branch_ids[0] if branch_ids else False,
            })
            business_units |= bu
        
        return business_units
    
    def _create_sample_business_units(self, branches):
        """Create sample business units for testing."""
        self.ensure_one()
        
        sample_data = [
            {'name': 'Sales Division', 'code': 'BU-SALES'},
            {'name': 'Operations', 'code': 'BU-OPS'},
            {'name': 'Services', 'code': 'BU-SVC'},
        ]
        
        business_units = self.env['ops.business.unit']
        for data in sample_data[:self.business_unit_count]:
            bu = self.env['ops.business.unit'].create({
                'name': data['name'],
                'code': data['code'],
                'branch_ids': [(6, 0, branches.ids)],
                'primary_branch_id': branches[0].id if branches else False,
            })
            business_units |= bu
        
        return business_units
    
    def _configure_admin_user(self, branches, business_units):
        """Configure the admin user with matrix access."""
        self.ensure_one()
        
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        if admin_user:
            admin_user.write({
                'ops_allowed_branch_ids': [(6, 0, branches.ids)],
                'ops_allowed_business_unit_ids': [(6, 0, business_units.ids)],
                'ops_default_branch_id': branches[0].id if branches else False,
                'ops_default_business_unit_id': business_units[0].id if business_units else False,
            })
    
    # =========================================================================
    # Action Methods
    # =========================================================================
    def action_finish(self):
        """Complete the wizard and close."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Setup Complete!'),
                'message': _('OPS Matrix Framework has been configured successfully. '
                           'You can now start using branches and business units in your transactions.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    def action_open_configuration(self):
        """Open the matrix configuration form."""
        self.ensure_one()
        
        config = self.env['ops.matrix.config'].search([
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ops.matrix.config',
            'res_id': config.id if config else False,
            'view_mode': 'form',
            'target': 'current',
        }


class OpsWelcomeWizardBranch(models.TransientModel):
    """Wizard line for branch creation."""
    _name = 'ops.welcome.wizard.branch'
    _description = 'Welcome Wizard - Branch Line'
    
    wizard_id = fields.Many2one(
        'ops.welcome.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string='Branch Name', required=True)
    code = fields.Char(string='Branch Code')
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')


class OpsWelcomeWizardBusinessUnit(models.TransientModel):
    """Wizard line for business unit creation."""
    _name = 'ops.welcome.wizard.business.unit'
    _description = 'Welcome Wizard - Business Unit Line'
    
    wizard_id = fields.Many2one(
        'ops.welcome.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string='Business Unit Name', required=True)
    code = fields.Char(string='BU Code')
    description = fields.Text(string='Description')
    branch_ids = fields.Many2many(
        'ops.branch',
        string='Operating Branches',
        help='Leave empty to include all branches'
    )
