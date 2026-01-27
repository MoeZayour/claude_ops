# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpsMatrixConfig(models.Model):
    """
    OPS Matrix Framework Configuration
    
    Centralized configuration for the matrix framework, including
    analytic distribution weights, default behaviors, and system-wide settings.
    """
    _name = 'ops.matrix.config'
    _description = 'OPS Matrix Configuration'
    _rec_name = 'company_id'
    
    # =========================================================================
    # Basic Fields
    # =========================================================================
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company this configuration applies to'
    )
    
    active = fields.Boolean(
        default=True,
        help='Set to False to disable this configuration'
    )
    
    # =========================================================================
    # Analytic Distribution Configuration
    # =========================================================================
    branch_weight = fields.Float(
        string='Branch Analytic Weight (%)',
        default=50.0,
        help='Percentage of analytic distribution allocated to Branch dimension (0-100)'
    )
    
    business_unit_weight = fields.Float(
        string='Business Unit Analytic Weight (%)',
        default=50.0,
        help='Percentage of analytic distribution allocated to Business Unit dimension (0-100)'
    )
    
    enforce_balanced_distribution = fields.Boolean(
        string='Enforce Balanced Distribution',
        default=True,
        help='If enabled, Branch + BU weights must equal 100%'
    )
    
    allow_single_dimension = fields.Boolean(
        string='Allow Single Dimension',
        default=True,
        help='Allow transactions with only Branch OR BU (not both)'
    )
    
    single_dimension_weight = fields.Float(
        string='Single Dimension Weight (%)',
        default=100.0,
        help='Weight to assign when only one dimension is present'
    )
    
    # =========================================================================
    # Matrix Behavior Configuration
    # =========================================================================
    require_branch_on_transactions = fields.Boolean(
        string='Require Branch on Transactions',
        default=True,
        help='Make Branch field required on sale orders, invoices, etc.'
    )
    
    require_bu_on_transactions = fields.Boolean(
        string='Require BU on Transactions',
        default=True,
        help='Make Business Unit field required on sale orders, invoices, etc.'
    )
    
    auto_propagate_dimensions = fields.Boolean(
        string='Auto-propagate Dimensions',
        default=True,
        help='Automatically copy Branch/BU from source document to related records'
    )
    
    validate_bu_branch_compatibility = fields.Boolean(
        string='Validate BU-Branch Compatibility',
        default=True,
        help='Ensure selected BU operates in selected Branch'
    )
    
    # =========================================================================
    # Reporting Configuration
    # =========================================================================
    default_reporting_dimension = fields.Selection([
        ('branch', 'Branch'),
        ('business_unit', 'Business Unit'),
        ('matrix', 'Matrix (Branch × BU)'),
    ], string='Default Reporting Dimension',
       default='matrix',
       help='Default dimension for reports and dashboards')
    
    enable_cross_branch_bu_access = fields.Boolean(
        string='Enable Cross-Branch BU Access',
        default=True,
        help='Allow BU leaders to see their BU data across all branches'
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
       help='Pre-configured settings for specific industries')
    
    # =========================================================================
    # Constraints
    # =========================================================================
    @api.constrains('branch_weight', 'business_unit_weight', 'enforce_balanced_distribution')
    def _check_analytic_weights(self):
        """Validate analytic weight distribution."""
        for config in self:
            # Check valid range
            if not (0 <= config.branch_weight <= 100):
                raise ValidationError(_(
                    'Branch weight must be between 0 and 100. Current value: %.2f'
                ) % config.branch_weight)
            
            if not (0 <= config.business_unit_weight <= 100):
                raise ValidationError(_(
                    'Business Unit weight must be between 0 and 100. Current value: %.2f'
                ) % config.business_unit_weight)
            
            # Check balanced distribution if enforced
            if config.enforce_balanced_distribution:
                total = config.branch_weight + config.business_unit_weight
                if abs(total - 100.0) > 0.01:  # Allow tiny floating point errors
                    raise ValidationError(_(
                        'Branch weight (%.2f%%) + Business Unit weight (%.2f%%) must equal 100%%. '
                        'Current total: %.2f%%'
                    ) % (config.branch_weight, config.business_unit_weight, total))
    
    @api.constrains('single_dimension_weight')
    def _check_single_dimension_weight(self):
        """Validate single dimension weight."""
        for config in self:
            if not (0 <= config.single_dimension_weight <= 100):
                raise ValidationError(_(
                    'Single dimension weight must be between 0 and 100. Current value: %.2f'
                ) % config.single_dimension_weight)
    
    # ORM Constraints (Odoo 19 syntax)
    _company_unique = models.Constraint(
        'UNIQUE(company_id)',
        'Only one configuration record per company is allowed!'
    )
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    @api.model
    def get_config(self, company_id=None):
        """
        Get configuration for the specified company (or current company).
        Creates default configuration if none exists.
        
        :param company_id: ID of the company (optional)
        :return: ops.matrix.config record
        """
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        
        if not config:
            config = self.create({
                'company_id': company_id,
                'branch_weight': 50.0,
                'business_unit_weight': 50.0,
            })
        
        return config
    
    def get_analytic_distribution(self, branch_id=None, bu_id=None):
        """
        Calculate analytic distribution based on configuration.
        
        :param branch_id: Branch analytic account ID
        :param bu_id: Business Unit analytic account ID
        :return: Dictionary {analytic_account_id: weight}
        """
        self.ensure_one()
        distribution = {}
        
        # Both dimensions present
        if branch_id and bu_id:
            if self.branch_weight > 0:
                distribution[str(branch_id)] = self.branch_weight
            if self.business_unit_weight > 0:
                distribution[str(bu_id)] = self.business_unit_weight
        
        # Only branch
        elif branch_id and self.allow_single_dimension:
            distribution[str(branch_id)] = self.single_dimension_weight
        
        # Only BU
        elif bu_id and self.allow_single_dimension:
            distribution[str(bu_id)] = self.single_dimension_weight
        
        return distribution if distribution else False
    
    # =========================================================================
    # Industry Template Application
    # =========================================================================
    def apply_industry_template(self):
        """Apply industry-specific configuration settings."""
        self.ensure_one()
        
        templates = {
            'retail': {
                'branch_weight': 60.0,
                'business_unit_weight': 40.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': True,
                'default_reporting_dimension': 'branch',
            },
            'manufacturing': {
                'branch_weight': 40.0,
                'business_unit_weight': 60.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': True,
                'default_reporting_dimension': 'business_unit',
            },
            'services': {
                'branch_weight': 50.0,
                'business_unit_weight': 50.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': True,
                'default_reporting_dimension': 'matrix',
            },
            'hospitality': {
                'branch_weight': 70.0,
                'business_unit_weight': 30.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': False,
                'default_reporting_dimension': 'branch',
            },
            'healthcare': {
                'branch_weight': 50.0,
                'business_unit_weight': 50.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': True,
                'default_reporting_dimension': 'matrix',
            },
            'construction': {
                'branch_weight': 30.0,
                'business_unit_weight': 70.0,
                'require_branch_on_transactions': True,
                'require_bu_on_transactions': True,
                'default_reporting_dimension': 'business_unit',
            },
        }
        
        if self.industry_template and self.industry_template in templates:
            template_values = templates[self.industry_template]
            self.write(template_values)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template Applied'),
                    'message': _('Industry template "%s" has been applied successfully.') % 
                              dict(self._fields['industry_template'].selection).get(self.industry_template),
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    # =========================================================================
    # Action Methods
    # =========================================================================
    def action_reset_to_defaults(self):
        """Reset configuration to default values."""
        self.ensure_one()
        self.write({
            'branch_weight': 50.0,
            'business_unit_weight': 50.0,
            'enforce_balanced_distribution': True,
            'allow_single_dimension': True,
            'single_dimension_weight': 100.0,
            'require_branch_on_transactions': True,
            'require_bu_on_transactions': True,
            'auto_propagate_dimensions': True,
            'validate_bu_branch_compatibility': True,
            'default_reporting_dimension': 'matrix',
            'enable_cross_branch_bu_access': True,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Reset'),
                'message': _('Configuration has been reset to default values.'),
                'type': 'info',
                'sticky': False,
            }
        }
