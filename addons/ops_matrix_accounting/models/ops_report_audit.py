# -*- coding: utf-8 -*-
"""
OPS Report Audit Model
======================

Silent audit trail for all OPS Matrix reporting activities.
Tracks every report generation with user, parameters, and metadata.

This is "The Black Box" - a compliance-grade audit log that cannot
be tampered with by regular users.

Author: OPS Matrix Framework
Version: 1.0 (Phase 12 - Compliance & Audit Logging)
"""

import json
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class OpsReportAudit(models.Model):
    """
    Audit log for report generation activities.

    Records every report generated through OPS Matrix reporting engines,
    capturing who, when, what, and how for compliance purposes.
    """
    _name = 'ops.report.audit'
    _description = 'Report Audit Log'
    _order = 'action_date desc, id desc'
    _rec_name = 'display_name'

    # ============================================
    # FIELDS
    # ============================================

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
        help='User who generated the report'
    )

    action_date = fields.Datetime(
        string='Date/Time',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
        index=True,
        help='Exact timestamp of report generation'
    )

    report_engine = fields.Selection(
        selection=[
            ('financial', 'Financial Reports'),
            ('treasury', 'Treasury Reports'),
            ('asset', 'Asset Reports'),
            ('inventory', 'Inventory Reports'),
        ],
        string='Report Engine',
        required=True,
        readonly=True,
        index=True,
        help='Which reporting engine was used'
    )

    report_name = fields.Char(
        string='Report Name',
        required=True,
        readonly=True,
        help='Human-readable report title (e.g., "Profit and Loss")'
    )

    report_type = fields.Char(
        string='Report Type Code',
        readonly=True,
        help='Internal report type code (e.g., "pl", "bs", "aging")'
    )

    parameters = fields.Text(
        string='Parameters (JSON)',
        readonly=True,
        help='JSON dump of all filters and parameters used'
    )

    export_format = fields.Selection(
        selection=[
            ('screen', 'Screen View'),
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('html', 'HTML'),
        ],
        string='Export Format',
        default='screen',
        readonly=True,
        help='Output format of the report'
    )

    ip_address = fields.Char(
        string='IP Address',
        readonly=True,
        help='Client IP address if available from request context'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.company,
        help='Company context for the report'
    )

    wizard_model = fields.Char(
        string='Wizard Model',
        readonly=True,
        help='Technical name of the wizard model used'
    )

    record_count = fields.Integer(
        string='Records',
        readonly=True,
        help='Number of records returned in the report'
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True
    )

    # ============================================
    # COMPUTED METHODS
    # ============================================

    @api.depends('report_engine', 'report_name', 'action_date')
    def _compute_display_name(self):
        """Generate a descriptive display name."""
        for record in self:
            engine = dict(self._fields['report_engine'].selection).get(
                record.report_engine, 'Unknown'
            )
            date_str = record.action_date.strftime('%Y-%m-%d %H:%M') if record.action_date else ''
            record.display_name = f"{engine}: {record.report_name} ({date_str})"

    # ============================================
    # API METHODS
    # ============================================

    @api.model
    def log_report(self, engine, report_name, report_type=None, parameters=None,
                   export_format='screen', wizard_model=None, record_count=0):
        """
        Create an audit log entry for a report generation.

        This method is called silently from report wizards and should
        never block report generation even if logging fails.

        Args:
            engine (str): Report engine ('financial', 'treasury', 'asset', 'inventory')
            report_name (str): Human-readable report name
            report_type (str): Internal report type code
            parameters (dict): Filter parameters (will be JSON serialized)
            export_format (str): Output format ('screen', 'pdf', 'excel', 'html')
            wizard_model (str): Technical model name of the wizard
            record_count (int): Number of records in report

        Returns:
            ops.report.audit record or False on failure
        """
        try:
            # Get IP address from request context if available
            ip_address = False
            try:
                from odoo.http import request
                if request and hasattr(request, 'httprequest'):
                    ip_address = request.httprequest.environ.get(
                        'HTTP_X_FORWARDED_FOR',
                        request.httprequest.environ.get('REMOTE_ADDR', False)
                    )
                    # Take first IP if multiple (proxy chain)
                    if ip_address and ',' in ip_address:
                        ip_address = ip_address.split(',')[0].strip()
            except Exception:
                _logger.debug('Failed to resolve client IP address', exc_info=True)
                # Request context not available (cron, shell, etc.)

            # Serialize parameters safely
            params_json = False
            if parameters:
                try:
                    # Clean parameters for JSON serialization
                    clean_params = self._clean_params_for_json(parameters)
                    params_json = json.dumps(clean_params, indent=2, default=str)
                except Exception as e:
                    _logger.warning(f"Could not serialize report parameters: {e}")
                    params_json = json.dumps({'error': 'Could not serialize parameters'})

            # Create audit record using sudo to ensure it always works
            audit = self.sudo().create({
                'user_id': self.env.user.id,
                'report_engine': engine,
                'report_name': report_name,
                'report_type': report_type or '',
                'parameters': params_json,
                'export_format': export_format,
                'ip_address': ip_address,
                'wizard_model': wizard_model,
                'record_count': record_count,
                'company_id': self.env.company.id,
            })

            _logger.debug(
                f"Audit log created: {audit.display_name} by {self.env.user.name}"
            )
            return audit

        except Exception as e:
            # CRITICAL: Never block report generation due to audit failure
            _logger.error(f"Failed to create audit log: {e}", exc_info=True)
            return False

    def _clean_params_for_json(self, params):
        """
        Clean parameter dict for JSON serialization.

        Handles Odoo recordsets and other non-serializable objects.

        Args:
            params (dict): Raw parameters

        Returns:
            dict: Cleaned parameters safe for JSON
        """
        cleaned = {}
        for key, value in params.items():
            # Skip internal fields
            if key.startswith('_') or key in ('id', 'create_uid', 'create_date',
                                                'write_uid', 'write_date', '__last_update'):
                continue

            # Handle recordsets
            if hasattr(value, 'ids'):
                cleaned[key] = value.ids if value else []
            # Handle dates
            elif hasattr(value, 'isoformat'):
                cleaned[key] = value.isoformat()
            # Handle basic types
            elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                cleaned[key] = value
            else:
                # Convert other types to string
                cleaned[key] = str(value)

        return cleaned

    # ============================================
    # SECURITY: No unlink for regular users
    # ============================================

    def unlink(self):
        """
        Prevent deletion of audit records except by admin.

        Audit records are permanent for compliance purposes.
        """
        if not self.env.user._is_admin():
            _logger.warning(
                f"User {self.env.user.name} attempted to delete audit records: {self.ids}"
            )
            raise models.UserError(
                "Audit records cannot be deleted. They are permanent for compliance."
            )
        return super().unlink()

    def write(self, vals):
        """
        Prevent modification of audit records.

        Audit records are immutable once created.
        """
        # Allow only display_name updates (computed field storage)
        allowed_fields = {'display_name'}
        if set(vals.keys()) - allowed_fields:
            if not self.env.user._is_admin():
                _logger.warning(
                    f"User {self.env.user.name} attempted to modify audit records: {self.ids}"
                )
                raise models.UserError(
                    "Audit records cannot be modified. They are immutable for compliance."
                )
        return super().write(vals)
