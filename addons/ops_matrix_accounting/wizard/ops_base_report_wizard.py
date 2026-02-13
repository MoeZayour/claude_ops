# -*- coding: utf-8 -*-
"""
OPS Matrix Base Report Wizard
=============================

Abstract base class for all OPS Matrix report wizards.
Provides shared functionality for template management, validation,
and common computed fields.

This reduces code duplication across Financial, Treasury, Asset,
and Inventory report wizards.

Author: OPS Matrix Framework
Version: 1.0 (Phase 11 - Code Refactoring)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import date_utils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsBaseReportWizard(models.AbstractModel):
    """
    Abstract Base Report Wizard for OPS Matrix Reporting Engines.

    Provides:
    - Template loading/saving functionality
    - Common computed fields (report_title, filter_summary, currency_id)
    - Shared validation logic
    - Action dispatch pattern
    - IT Admin Blindness via security mixin
    - Branch isolation via security mixin

    Subclasses MUST implement:
    - _get_engine_name() -> str
    - _get_report_titles() -> dict
    - _get_scalar_fields_for_template() -> list
    - _get_m2m_fields_for_template() -> list
    - _get_report_data() -> dict
    - _return_report_action(data) -> dict

    Subclasses MAY override:
    - _apply_template_date_modes(config) -> None
    - _add_filter_summary_parts(parts) -> None
    - _validate_filters_extra() -> bool|dict
    - _estimate_record_count() -> int
    """
    _name = 'ops.base.report.wizard'
    _inherit = 'ops.intelligence.security.mixin'
    _description = 'Base Report Wizard (Abstract)'

    # ============================================
    # COMMON FIELDS
    # ============================================
    report_template_id = fields.Many2one(
        'ops.report.template',
        string='Load Template',
        help='Select a saved report template to load its configuration'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency'
    )

    report_title = fields.Char(
        compute='_compute_report_title',
        string='Report Title'
    )

    filter_summary = fields.Char(
        compute='_compute_filter_summary',
        string='Filter Summary',
        help='Summary of active filters'
    )

    record_count = fields.Integer(
        compute='_compute_record_count',
        string='Estimated Records',
        help='Estimated number of records matching filters'
    )

    # ============================================
    # COMMON REPORT FIELDS (v2 contract base)
    # ============================================
    output_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Export'),
        ('html', 'View in Browser'),
    ], string='Output Format', default='pdf')

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    as_of_date = fields.Date(string='As of Date')

    branch_ids = fields.Many2many('ops.branch', string='Branches')
    business_unit_ids = fields.Many2many('ops.business.unit', string='Business Units')

    target_move = fields.Selection([
        ('posted', 'Posted Only'),
        ('all', 'All Entries'),
    ], default='posted', string='Target Moves')

    matrix_filter_mode = fields.Selection([
        ('any', 'Any'),
        ('exact', 'Exact'),
    ], default='any', string='Matrix Filter Mode')

    # ============================================
    # ABSTRACT METHODS - MUST OVERRIDE
    # ============================================

    def _get_engine_name(self):
        """
        Return the engine name for template filtering.

        Returns:
            str: Engine name ('financial', 'treasury', 'asset', 'inventory')
        """
        raise NotImplementedError("Subclasses must implement _get_engine_name()")

    def _get_report_titles(self):
        """
        Return mapping of report_type to human-readable title.

        Returns:
            dict: {'type_key': 'Human Title', ...}
        """
        raise NotImplementedError("Subclasses must implement _get_report_titles()")

    def _get_scalar_fields_for_template(self):
        """
        Return list of scalar field names to save/load from templates.

        Returns:
            list: ['field_name', ...]
        """
        raise NotImplementedError("Subclasses must implement _get_scalar_fields_for_template()")

    def _get_m2m_fields_for_template(self):
        """
        Return list of Many2many field names to save/load from templates.

        Returns:
            list: ['field_name_ids', ...]
        """
        raise NotImplementedError("Subclasses must implement _get_m2m_fields_for_template()")

    def _get_report_data(self):
        """
        Dispatch to appropriate report data method based on report_type.

        Returns:
            dict: Report data structure
        """
        raise NotImplementedError("Subclasses must implement _get_report_data()")

    def _return_report_action(self, data):
        """
        Return appropriate action for displaying the report.

        Args:
            data: Report data dict from _get_report_data()

        Returns:
            dict: Action dictionary
        """
        raise NotImplementedError("Subclasses must implement _return_report_action()")

    def _get_report_shape(self):
        """Return report shape: 'lines', 'hierarchy', or 'matrix'.

        Subclasses MUST implement this for the v2 data contract system.
        """
        raise NotImplementedError("Subclasses must implement _get_report_shape()")

    # ============================================
    # OPTIONAL HOOKS - MAY OVERRIDE
    # ============================================

    def _apply_template_date_modes(self, config):
        """
        Handle dynamic date mode calculations when loading templates.
        Override to handle engine-specific date modes like 'next_30_days'.

        Args:
            config: Template configuration dict
        """
        # Default implementation handles common date modes
        today = fields.Date.today()
        date_mode = config.get('date_mode')

        if date_mode == 'last_month':
            if hasattr(self, 'date_from'):
                self.date_from = date_utils.start_of(today - relativedelta(months=1), 'month')
            if hasattr(self, 'date_to'):
                self.date_to = date_utils.end_of(today - relativedelta(months=1), 'month')
        elif date_mode == 'current_month':
            if hasattr(self, 'date_from'):
                self.date_from = date_utils.start_of(today, 'month')
            if hasattr(self, 'date_to'):
                self.date_to = date_utils.end_of(today, 'month')
        elif date_mode == 'ytd':
            if hasattr(self, 'date_from'):
                self.date_from = date_utils.start_of(today, 'year')
            if hasattr(self, 'date_to'):
                self.date_to = today
        elif date_mode == 'next_30_days':
            if hasattr(self, 'date_from'):
                self.date_from = today
            if hasattr(self, 'date_to'):
                self.date_to = today + timedelta(days=30)
        elif date_mode == 'next_60_days':
            if hasattr(self, 'date_from'):
                self.date_from = today
            if hasattr(self, 'date_to'):
                self.date_to = today + timedelta(days=60)
        elif date_mode == 'next_90_days':
            if hasattr(self, 'date_from'):
                self.date_from = today
            if hasattr(self, 'date_to'):
                self.date_to = today + timedelta(days=90)
        else:
            # Static dates from config
            if config.get('date_from') and hasattr(self, 'date_from'):
                self.date_from = fields.Date.from_string(config['date_from'])
            if config.get('date_to') and hasattr(self, 'date_to'):
                self.date_to = fields.Date.from_string(config['date_to'])

        # Handle as_of_date if present
        if config.get('as_of_date') and hasattr(self, 'as_of_date'):
            self.as_of_date = fields.Date.from_string(config['as_of_date'])

    def _add_filter_summary_parts(self, parts):
        """
        Add engine-specific filter descriptions to summary.
        Override to add wizard-specific filter info.

        Args:
            parts: List of summary parts (mutate in place)
        """
        pass  # Default: no additional parts

    def _validate_filters_extra(self):
        """
        Perform engine-specific validation beyond base date checks.
        Override to add custom validation.

        Returns:
            True, or dict with 'warning' key, or raises ValidationError
        """
        return True

    def _estimate_record_count(self):
        """
        Estimate number of records matching current filters.
        Override to provide accurate counts.

        Returns:
            int: Estimated record count
        """
        return 0

    # ============================================
    # COMPUTED METHODS
    # ============================================

    @api.depends('report_type' if 'report_type' in dir() else 'company_id')
    def _compute_report_title(self):
        """Get human-readable report title."""
        titles = self._get_report_titles() if callable(getattr(self, '_get_report_titles', None)) else {}
        for wizard in self:
            report_type = getattr(wizard, 'report_type', None)
            wizard.report_title = titles.get(report_type, 'Report')

    @api.depends('company_id')
    def _compute_filter_summary(self):
        """Compute human-readable summary of active filters."""
        for wizard in self:
            parts = [wizard.report_title or 'Report']

            # Date range (common to most wizards)
            date_from = getattr(wizard, 'date_from', None)
            date_to = getattr(wizard, 'date_to', None)
            as_of_date = getattr(wizard, 'as_of_date', None)

            if date_from and date_to:
                parts.append(f"Period: {date_from} to {date_to}")
            elif as_of_date:
                parts.append(f"As of: {as_of_date}")

            # Call hook for wizard-specific parts
            wizard._add_filter_summary_parts(parts)

            wizard.filter_summary = " | ".join(parts) if parts else "No filters applied"

    @api.depends('company_id')
    def _compute_record_count(self):
        """Estimate number of records matching current filters."""
        for wizard in self:
            try:
                wizard.record_count = wizard._estimate_record_count()
            except Exception as e:
                _logger.error(f"Error counting records: {e}")
                wizard.record_count = 0

    # ============================================
    # VALIDATION
    # ============================================

    def _validate_filters(self):
        """
        Validate wizard filters before generating report.

        Performs base date validation and calls _validate_filters_extra() hook.

        Returns:
            True, or dict with 'warning' key

        Raises:
            ValidationError: If validation fails
        """
        self.ensure_one()

        # Base date validation
        date_from = getattr(self, 'date_from', None)
        date_to = getattr(self, 'date_to', None)

        if date_from and date_to and date_from > date_to:
            raise ValidationError(_("From date cannot be after To date."))

        # Call hook for engine-specific validation
        return self._validate_filters_extra()

    # ============================================
    # REPORT GENERATION
    # ============================================

    def action_generate_report(self):
        """Main action: Validate filters and generate report.

        Dispatches to PDF, Excel, or HTML based on ``output_format``.
        Security checks (IT Admin Blindness, branch isolation) run first,
        regardless of output format.
        """
        self.ensure_one()

        # =====================================================================
        # SECURITY CHECK - MUST BE FIRST
        # Enforces IT Admin Blindness and role-based access
        # =====================================================================
        pillar_name = self._get_pillar_name()
        self._check_intelligence_access(pillar_name)

        # Validate branch access if user selected specific branches
        branch_field = getattr(self, 'branch_ids', None) or getattr(self, 'ops_branch_ids', None)
        if branch_field:
            self._validate_branch_access(branch_field)

        # Validate
        validation_result = self._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            pass  # Allow to proceed with warning

        # Dispatch based on output format
        output_fmt = getattr(self, 'output_format', 'pdf') or 'pdf'
        if output_fmt == 'excel':
            return self.action_export_to_excel()
        elif output_fmt == 'html':
            return self.action_view_in_browser()

        # Default: PDF
        report_data = self._get_report_data()

        # Log to audit trail (The Black Box)
        self._log_report_audit(report_data)

        # Return report action
        return self._return_report_action(report_data)

    def _get_pillar_name(self):
        """
        Get the pillar name for security checks.
        Override in subclass if engine name doesn't match pillar name.
        """
        engine = 'Report'
        if callable(getattr(self, '_get_engine_name', None)):
            engine = self._get_engine_name()
        # Map engine names to pillar names
        pillar_map = {
            'financial': 'Financial',
            'treasury': 'Treasury',
            'asset': 'Asset',
            'inventory': 'Inventory',
        }
        return pillar_map.get(engine, engine.capitalize())

    def _log_report_audit(self, report_data=None):
        """
        Create an audit log entry for this report generation.

        This is "The Black Box" - silent compliance logging that
        tracks all reporting activity without blocking execution.

        Args:
            report_data: Report data dict (optional, for record count)
        """
        try:
            # Get engine name
            engine = 'financial'  # Default
            if callable(getattr(self, '_get_engine_name', None)):
                engine = self._get_engine_name()

            # Get report title
            report_name = getattr(self, 'report_title', 'Unknown Report')
            if not report_name or report_name == 'Report':
                titles = {}
                if callable(getattr(self, '_get_report_titles', None)):
                    titles = self._get_report_titles()
                report_type = getattr(self, 'report_type', None)
                report_name = titles.get(report_type, 'Report')

            # Get report type code
            report_type = getattr(self, 'report_type', None)

            # Capture parameters
            try:
                parameters = self.read()[0] if self else {}
            except Exception:
                _logger.debug('Failed to read wizard parameters for audit', exc_info=True)
                parameters = {}

            # Determine export format from context or defaults
            export_format = 'screen'
            ctx = self.env.context
            if ctx.get('xlsx_export') or ctx.get('excel_export'):
                export_format = 'excel'
            elif ctx.get('pdf_export'):
                export_format = 'pdf'

            # Estimate record count from report data
            record_count = 0
            if report_data:
                if isinstance(report_data, dict):
                    # Try common patterns for record count
                    if 'lines' in report_data:
                        record_count = len(report_data.get('lines', []))
                    elif 'records' in report_data:
                        record_count = len(report_data.get('records', []))
                    elif 'data' in report_data:
                        data = report_data.get('data', [])
                        record_count = len(data) if isinstance(data, list) else 0

            # Create audit log
            self.env['ops.report.audit'].log_report(
                engine=engine,
                report_name=report_name,
                report_type=report_type,
                parameters=parameters,
                export_format=export_format,
                wizard_model=self._name,
                record_count=record_count,
            )

        except Exception as e:
            # CRITICAL: Never block report generation due to audit failure
            _logger.error(f"Audit logging failed (non-blocking): {e}")

    # ============================================
    # EXCEL / HTML OUTPUT
    # ============================================

    def action_generate_pdf(self):
        """Generate PDF report directly (button action)."""
        self.ensure_one()
        self.output_format = 'pdf'
        return self.action_generate_report()

    def action_export_to_excel(self):
        """Excel export using generic renderer.

        Only users in ``group_ops_can_export`` may use this.
        Generates an XLSX file via ``ops.excel.renderer`` and returns
        a download action for the resulting attachment.
        """
        if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
            raise AccessError(_("You do not have permission to export data. Contact your administrator."))

        import base64
        report_data = self._get_report_data()
        self._log_report_audit(report_data)

        renderer = self.env['ops.excel.renderer']
        xlsx_content = renderer.render(report_data)

        title = report_data.get('meta', {}).get('report_title', 'Report')
        filename = '%s_%s.xlsx' % (title.replace(' ', '_'), fields.Date.today())
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xlsx_content),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': '%s/web/content/%s?download=true' % (base_url, attachment.id),
            'target': 'self',
        }

    def action_view_in_browser(self):
        """Open report in browser HTML view (Phase 5 controller)."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = '%s/ops/report/html/%s/%s' % (base_url, self._name, self.id)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    # ============================================
    # TEMPLATE METHODS
    # ============================================

    @api.onchange('report_template_id')
    def _onchange_report_template_id(self):
        """Load configuration from selected template."""
        if not self.report_template_id:
            return

        template = self.report_template_id
        config = template.get_config_dict()

        if not config:
            return

        # Apply scalar fields
        scalar_fields = self._get_scalar_fields_for_template()
        for field in scalar_fields:
            if field in config and hasattr(self, field):
                setattr(self, field, config[field])

        # Apply date modes (handles dynamic dates like 'last_month')
        self._apply_template_date_modes(config)

        # Apply Many2many fields
        m2m_fields = self._get_m2m_fields_for_template()
        for field in m2m_fields:
            if config.get(field) and hasattr(self, field):
                setattr(self, field, [(6, 0, config[field])])

        # Increment template usage
        template.increment_usage()

        _logger.info(f"Loaded {self._get_engine_name()} report template: {template.name}")

    def _get_template_config(self):
        """
        Get current wizard configuration for template saving.

        Returns:
            dict: Configuration that can be stored in template
        """
        self.ensure_one()
        config = {}

        # Get scalar fields
        scalar_fields = self._get_scalar_fields_for_template()
        for field in scalar_fields:
            if hasattr(self, field):
                config[field] = getattr(self, field)

        # Get Many2many fields as ID lists
        m2m_fields = self._get_m2m_fields_for_template()
        for field in m2m_fields:
            if hasattr(self, field):
                field_value = getattr(self, field)
                config[field] = field_value.ids if field_value else []

        return config

    def action_save_template(self):
        """Open wizard to save current settings as a template."""
        self.ensure_one()
        return {
            'name': _('Save as Report Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.report.template.save.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_wizard_model': self._name,
                'default_source_wizard_id': self.id,
            },
        }

    # ============================================
    # HELPER - Template Domain
    # ============================================

    @api.model
    def _get_template_domain(self):
        """
        Get domain for report_template_id field.

        Returns:
            list: Domain for filtering templates by engine
        """
        engine = self._get_engine_name() if callable(getattr(self, '_get_engine_name', None)) else 'financial'
        return [
            ('engine', '=', engine),
            '|',
            ('is_global', '=', True),
            ('user_id', '=', self.env.uid)
        ]

    # ============================================
    # NUMBER FORMATTING HELPERS
    # ============================================

    @staticmethod
    def _format_amount(value):
        """
        Format amount with proper negative handling for minimal report styling.

        Args:
            value: Numeric value to format

        Returns:
            dict: {
                'value': Formatted string,
                'class': CSS class ('ops-zero', 'ops-negative', or 'ops-positive')
            }
        """
        if value == 0:
            return {'value': '0.00', 'class': 'ops-zero'}
        elif value < 0:
            return {'value': f"({abs(value):,.2f})", 'class': 'ops-negative'}
        else:
            return {'value': f"{value:,.2f}", 'class': 'ops-positive'}

    @staticmethod
    def _format_amount_no_decimals(value):
        """
        Format amount without decimals for minimal report styling.

        Args:
            value: Numeric value to format

        Returns:
            dict: {
                'value': Formatted string (no decimals),
                'class': CSS class ('ops-zero', 'ops-negative', or 'ops-positive')
            }
        """
        if value == 0:
            return {'value': '0', 'class': 'ops-zero'}
        elif value < 0:
            return {'value': f"({abs(value):,.0f})", 'class': 'ops-negative'}
        else:
            return {'value': f"{value:,.0f}", 'class': 'ops-positive'}

    @staticmethod
    def _format_percentage(value, decimals=1):
        """
        Format percentage with proper styling.

        Args:
            value: Numeric value (0.15 = 15%)
            decimals: Number of decimal places (default 1)

        Returns:
            dict: {
                'value': Formatted percentage string,
                'class': CSS class
            }
        """
        pct = value * 100
        format_str = f"{{:,.{decimals}f}}%"
        if pct == 0:
            return {'value': format_str.format(0), 'class': 'ops-zero'}
        elif pct < 0:
            return {'value': f"({format_str.format(abs(pct))})", 'class': 'ops-negative'}
        else:
            return {'value': format_str.format(pct), 'class': 'ops-positive'}

    def _get_company_primary_color(self):
        """
        Get company's primary color for report accent.

        Returns:
            str: Hex color code (defaults to #C9A962 gold)
        """
        company = getattr(self, 'company_id', None) or self.env.company
        return getattr(company, 'primary_color', None) or '#C9A962'

    @staticmethod
    def _get_primary_light(primary_hex):
        """
        Generate light background from primary color (15% opacity with white).

        Args:
            primary_hex: Hex color code (e.g., '#5B6BBB')

        Returns:
            str: Light hex color code for backgrounds
        """
        if not primary_hex:
            primary_hex = '#5B6BBB'

        # Remove # if present
        hex_color = primary_hex.lstrip('#')

        # Convert to RGB
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            # Invalid hex, return default light color
            return '#E8EAF6'

        # Blend with white at 15% opacity
        opacity = 0.15
        light_r = int(r * opacity + 255 * (1 - opacity))
        light_g = int(g * opacity + 255 * (1 - opacity))
        light_b = int(b * opacity + 255 * (1 - opacity))

        return '#{:02x}{:02x}{:02x}'.format(light_r, light_g, light_b)

    @staticmethod
    def _get_primary_dark(primary_hex):
        """
        Generate darker shade of primary color.

        Args:
            primary_hex: Hex color code (e.g., '#5B6BBB')

        Returns:
            str: Darker hex color code
        """
        if not primary_hex:
            primary_hex = '#5B6BBB'

        hex_color = primary_hex.lstrip('#')

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            # Invalid hex, return default dark color
            return '#3D4A8A'

        factor = 0.7  # Darken by 30%
        dark_r = int(r * factor)
        dark_g = int(g * factor)
        dark_b = int(b * factor)

        return '#{:02x}{:02x}{:02x}'.format(dark_r, dark_g, dark_b)

    def get_color_scheme(self):
        """
        Get complete color scheme for reports based on company primary color.

        Returns:
            dict: {
                'primary': Primary hex color,
                'primary_light': Light background color,
                'primary_dark': Dark shade,
                'navy': Standard navy for text,
                'success': Success/positive green,
                'danger': Danger/negative red,
                'warning': Warning orange,
                'gold': Meridian gold accent
            }
        """
        primary = self._get_company_primary_color()
        return {
            'primary': primary,
            'primary_light': self._get_primary_light(primary),
            'primary_dark': self._get_primary_dark(primary),
            'navy': '#1e293b',
            'success': '#16a34a',
            'danger': '#dc2626',
            'warning': '#d97706',
            'gold': '#C9A962',
        }

    # =========================================================================
    # UI VIEW FEATURE
    # =========================================================================

    def action_view_report(self):
        """
        Open report in UI View mode (browser preview with toolbar).

        Returns:
            dict: Action to open report HTML in new tab
        """
        self.ensure_one()

        # Run validation
        validation_result = self._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            return validation_result

        # Security check
        engine_name = self._get_engine_name()
        if engine_name:
            self._check_intelligence_access(engine_name)

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """
        Get the XML ID of the report template for this wizard.
        Must be overridden by child classes.

        Returns:
            str: XML ID of report template (e.g., 'ops_matrix_accounting.report_general_ledger')
        """
        raise NotImplementedError(
            "Wizards must implement _get_report_template_xmlid() to use UI View feature"
        )
