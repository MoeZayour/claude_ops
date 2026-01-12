# -*- coding: utf-8 -*-
"""
OPS Export Audit Log Model
Comprehensive audit trail for data exports to track who exported what data and when.
Critical for compliance, security audits, and data leak investigation.
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpsExportLog(models.Model):
    """
    Audit trail for data exports to track who exported what data and when.
    Critical for compliance, security audits, and data leak investigation.
    """
    _name = 'ops.export.log'
    _description = 'Data Export Audit Log'
    _order = 'export_date desc'
    _rec_name = 'export_date'

    # Who exported
    user_id = fields.Many2one(
        'res.users',
        string='Exported By',
        required=True,
        readonly=True,
        index=True,
        default=lambda self: self.env.user,
        help='User who performed the export'
    )

    # What was exported
    model_id = fields.Many2one(
        'ir.model',
        string='Data Model',
        required=True,
        readonly=True,
        index=True,
        ondelete='cascade',
        help='Type of data exported (e.g., Invoices, Sales Orders)'
    )
    model_name = fields.Char(
        string='Model Technical Name',
        related='model_id.model',
        store=True,
        readonly=True,
        index=True
    )

    # How much data
    record_count = fields.Integer(
        string='Records Exported',
        readonly=True,
        help='Number of records included in the export'
    )

    # When exported
    export_date = fields.Datetime(
        string='Export Date',
        required=True,
        readonly=True,
        index=True,
        default=fields.Datetime.now,
        help='Timestamp when export was performed'
    )

    # Matrix dimensions accessed
    branch_ids = fields.Many2many(
        'ops.branch',
        'ops_export_log_branch_rel',
        'log_id',
        'branch_id',
        string='Branches Accessed',
        readonly=True,
        help='Branches included in the exported data'
    )
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'ops_export_log_business_unit_rel',
        'log_id',
        'business_unit_id',
        string='Business Units Accessed',
        readonly=True,
        help='Business units included in the exported data'
    )

    # Technical details
    domain_filter = fields.Text(
        string='Applied Filters',
        readonly=True,
        help='Domain filter used for the export'
    )
    export_format = fields.Selection([
        ('xlsx', 'Excel (XLSX)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ], string='Format', readonly=True, default='xlsx')

    # Security context
    ip_address = fields.Char(
        string='IP Address',
        readonly=True,
        help='IP address from which export was performed'
    )
    session_id = fields.Char(
        string='Session ID',
        readonly=True,
        help='User session identifier'
    )

    # Data classification
    data_classification = fields.Selection([
        ('public', 'Public'),
        ('internal', 'Internal Use Only'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ], string='Data Classification',
       default='internal',
       readonly=True,
       help='Classification level of exported data')

    # Additional context
    notes = fields.Text(
        string='Export Notes',
        readonly=True,
        help='Additional context or reason for export'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.company,
        index=True
    )

    # Computed fields for reporting
    export_day = fields.Date(
        string='Export Day',
        compute='_compute_export_day',
        store=True,
        index=True
    )

    @api.depends('export_date')
    def _compute_export_day(self):
        """Extract date from datetime for daily reporting"""
        for log in self:
            log.export_day = log.export_date.date() if log.export_date else False

    def name_get(self):
        """Display format: [Date] User exported Model (X records)"""
        result = []
        for log in self:
            date_str = fields.Datetime.to_string(log.export_date) if log.export_date else 'Unknown'
            model_name = log.model_id.name if log.model_id else 'Unknown Model'
            user_name = log.user_id.name if log.user_id else 'Unknown User'
            name = _('[%s] %s exported %s (%s records)') % (
                date_str,
                user_name,
                model_name,
                log.record_count or 0
            )
            result.append((log.id, name))
        return result

    @api.model
    def log_export(self, model_name, records, domain=None, export_format='xlsx', notes=None):
        """
        Helper method to create export log entry.

        Usage:
            self.env['ops.export.log'].log_export(
                model_name='account.move',
                records=move_recordset,
                domain=[('state', '=', 'posted')],
                export_format='xlsx',
                notes='Monthly financial report'
            )

        Args:
            model_name (str): Technical name of the model being exported
            records (recordset): Recordset of records being exported
            domain (list, optional): Domain filter applied to the export
            export_format (str, optional): Export format (xlsx, csv, pdf)
            notes (str, optional): Additional notes about the export

        Returns:
            ops.export.log: Created log record
        """
        model_id = self.env['ir.model'].search([('model', '=', model_name)], limit=1)

        # Extract branches and BUs from records
        branch_ids = []
        bu_ids = []
        if hasattr(records, 'mapped'):
            if 'ops_branch_id' in records._fields:
                branch_ids = records.mapped('ops_branch_id').ids
            if 'ops_business_unit_id' in records._fields:
                bu_ids = records.mapped('ops_business_unit_id').ids

        # Get IP address and session ID
        ip_address = self._get_ip_address()
        session_id = self._get_session_id()

        # Determine data classification based on model
        classification = self._determine_classification(model_name)

        # Create log entry
        log = self.create({
            'user_id': self.env.user.id,
            'model_id': model_id.id if model_id else False,
            'record_count': len(records) if records else 0,
            'export_date': fields.Datetime.now(),
            'branch_ids': [(6, 0, branch_ids)] if branch_ids else False,
            'business_unit_ids': [(6, 0, bu_ids)] if bu_ids else False,
            'domain_filter': str(domain) if domain else False,
            'export_format': export_format,
            'ip_address': ip_address,
            'session_id': session_id,
            'data_classification': classification,
            'notes': notes,
        })

        _logger.info(
            'Export logged: User %s exported %d %s records (format: %s, classification: %s)',
            self.env.user.login,
            len(records) if records else 0,
            model_name,
            export_format,
            classification
        )

        return log

    def _get_ip_address(self):
        """Get client IP address from request context"""
        try:
            from odoo.http import request
            if request and hasattr(request, 'httprequest'):
                return request.httprequest.environ.get('REMOTE_ADDR', 'Unknown')
        except (ImportError, RuntimeError, AttributeError):
            # Not in HTTP request context (CLI, cron, etc.)
            return 'System'
        return 'Unknown'

    def _get_session_id(self):
        """Get user session ID from request context"""
        try:
            from odoo.http import request
            if request and hasattr(request, 'session'):
                return request.session.sid
        except (ImportError, RuntimeError, AttributeError):
            # Not in HTTP request context
            return 'CLI'
        return 'Unknown'

    def _determine_classification(self, model_name):
        """Determine data classification based on model type"""
        # Financial data = Confidential
        if model_name in ['account.move', 'account.move.line', 'account.payment',
                          'account.bank.statement', 'account.journal']:
            return 'confidential'
        # HR/payroll = Restricted
        elif model_name in ['hr.employee', 'hr.payslip', 'hr.contract',
                            'hr.expense', 'hr.leave']:
            return 'restricted'
        # Sales/Purchase = Internal
        elif model_name in ['sale.order', 'purchase.order', 'stock.picking',
                            'crm.lead', 'project.task']:
            return 'internal'
        # Partners/Contacts = Internal
        elif model_name in ['res.partner', 'res.users']:
            return 'internal'
        # Default = Internal
        else:
            return 'internal'
