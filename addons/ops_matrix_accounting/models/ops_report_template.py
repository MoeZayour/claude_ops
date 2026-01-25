# -*- coding: utf-8 -*-
"""
OPS Matrix Smart Report Templates
=================================

Allows users to save and load preset configurations for all Matrix Reports.
Templates can be global (shared with all users) or private (user-specific).

Author: OPS Matrix Framework
Version: 1.0 (Phase 9 - Smart Reporting Templates)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class OpsReportTemplate(models.Model):
    """Report Template - Extends core template with smart configuration storage"""
    _inherit = 'ops.report.template'
    _description = 'Smart Report Template'
    _order = 'sequence, engine, name'
    _rec_name = 'display_name'

    # ============================================
    # CORE FIELDS
    # ============================================
    name = fields.Char(
        string='Template Name',
        required=True,
        help='Descriptive name for this report template'
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
        string='Display Name'
    )

    engine = fields.Selection([
        ('financial', 'Financial Intelligence'),
        ('treasury', 'Treasury (PDC)'),
        ('asset', 'Asset Management'),
        ('inventory', 'Inventory Intelligence'),
    ], string='Report Engine', required=False, index=True, default='financial',
       help='Which reporting engine this template applies to')

    description = fields.Text(
        string='Description',
        help='Detailed description of what this template reports on'
    )

    # ============================================
    # CONFIGURATION DATA
    # ============================================
    config_data = fields.Text(
        string='Configuration (JSON)',
        help='JSON-encoded wizard field values',
        default='{}'
    )

    # ============================================
    # ACCESS CONTROL
    # ============================================
    is_global = fields.Boolean(
        string='Global Template',
        default=False,
        help='If checked, this template is visible to all users. Otherwise, only the creator can see it.'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        help='User who created this template'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company this template belongs to'
    )

    # ============================================
    # CONTEXT FIELDS (Optional)
    # ============================================
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Default Branch',
        help='Optional: Link this template to a specific branch context'
    )

    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Default Business Unit',
        help='Optional: Link this template to a specific business unit'
    )

    # ============================================
    # METADATA
    # ============================================
    active = fields.Boolean(default=True)
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        help='Number of times this template has been used'
    )
    last_used = fields.Datetime(
        string='Last Used',
        help='When this template was last applied'
    )

    # ============================================
    # COMPUTED METHODS
    # ============================================

    @api.depends('name', 'engine', 'is_global')
    def _compute_display_name(self):
        """Generate display name with engine prefix and scope."""
        engine_labels = {
            'financial': 'FIN',
            'treasury': 'PDC',
            'asset': 'AST',
            'inventory': 'INV',
        }
        for template in self:
            prefix = engine_labels.get(template.engine, 'RPT')
            scope = '(Global)' if template.is_global else '(Private)'
            template.display_name = f"[{prefix}] {template.name} {scope}"

    # ============================================
    # CRUD METHODS
    # ============================================

    def write(self, vals):
        """Track usage when template is loaded."""
        res = super().write(vals)
        return res

    def increment_usage(self):
        """Increment usage counter when template is applied."""
        for template in self:
            template.sudo().write({
                'usage_count': template.usage_count + 1,
                'last_used': fields.Datetime.now(),
            })

    # ============================================
    # CONFIG METHODS
    # ============================================

    def get_config_dict(self):
        """Parse config_data JSON and return as dictionary."""
        self.ensure_one()
        try:
            return json.loads(self.config_data or '{}')
        except json.JSONDecodeError:
            _logger.warning(f"Invalid JSON in template {self.name}: {self.config_data}")
            return {}

    def set_config_dict(self, config):
        """Set config_data from dictionary."""
        self.ensure_one()
        # Clean up the config - remove non-serializable items
        clean_config = {}
        for key, value in config.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                clean_config[key] = value
            elif isinstance(value, (list, tuple)):
                # Handle Many2many field data
                clean_config[key] = list(value)
            elif isinstance(value, dict):
                clean_config[key] = value
        self.config_data = json.dumps(clean_config, default=str)

    # ============================================
    # DOMAIN FOR WIZARD ACCESS
    # ============================================

    @api.model
    def get_available_templates(self, engine):
        """Get templates available to current user for a specific engine."""
        domain = [
            ('engine', '=', engine),
            ('active', '=', True),
            '|',
            ('is_global', '=', True),
            ('user_id', '=', self.env.uid),
        ]
        return self.search(domain, order='is_global desc, usage_count desc, name')

    # ============================================
    # TEMPLATE CREATION FROM WIZARD
    # ============================================

    @api.model
    def create_from_wizard(self, wizard, name, engine, is_global=False, description=False):
        """Create a new template from wizard current state."""
        config = wizard._get_template_config()

        template = self.create({
            'name': name,
            'engine': engine,
            'description': description or f"Created from {wizard._description}",
            'config_data': json.dumps(config, default=str),
            'is_global': is_global,
            'user_id': self.env.uid,
            'company_id': self.env.company.id,
        })

        _logger.info(f"Created report template '{name}' for engine '{engine}' by user {self.env.user.name}")
        return template


class OpsReportTemplateSaveWizard(models.TransientModel):
    """Wizard to save current report settings as a new template"""
    _name = 'ops.report.template.save.wizard'
    _description = 'Save Report Template Wizard'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Enter a descriptive name for this template'
    )

    description = fields.Text(
        string='Description',
        help='Optional description of what this template reports'
    )

    is_global = fields.Boolean(
        string='Share with All Users',
        default=False,
        help='If checked, all users can use this template'
    )

    # Source wizard reference (set in context)
    source_wizard_model = fields.Char(string='Source Model')
    source_wizard_id = fields.Integer(string='Source ID')

    def action_save(self):
        """Save the template."""
        self.ensure_one()

        if not self.source_wizard_model or not self.source_wizard_id:
            raise UserError(_("Source wizard information is missing."))

        # Get the source wizard
        wizard = self.env[self.source_wizard_model].browse(self.source_wizard_id)
        if not wizard.exists():
            raise UserError(_("Source wizard no longer exists."))

        # Determine engine from wizard model
        engine_map = {
            'ops.general.ledger.wizard.enhanced': 'financial',
            'ops.treasury.report.wizard': 'treasury',
            'ops.asset.report.wizard': 'asset',
            'ops.inventory.report.wizard': 'inventory',
        }
        engine = engine_map.get(self.source_wizard_model)
        if not engine:
            raise UserError(_("Unknown wizard type: %s") % self.source_wizard_model)

        # Create the template
        template = self.env['ops.report.template'].create_from_wizard(
            wizard=wizard,
            name=self.name,
            engine=engine,
            is_global=self.is_global,
            description=self.description,
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Saved'),
                'message': _("Template '%s' has been saved successfully.") % self.name,
                'type': 'success',
                'sticky': False,
            }
        }
