# -*- coding: utf-8 -*-
"""
OPS Secure Data Export Wizard
Provides a secure, audited alternative to native exports with matrix filtering.
"""
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import json
import base64
import io
import logging

_logger = logging.getLogger(__name__)


class OpsSecureExportWizard(models.TransientModel):
    _name = 'ops.secure.export.wizard'
    _description = 'OPS Secure Data Export'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        domain=[('transient', '=', False)],
        help='Select the model/object to export data from'
    )

    model_name = fields.Char(
        related='model_id.model',
        string='Model Name',
        readonly=True
    )

    domain = fields.Char(
        string='Filter Domain',
        default='[]',
        help='JSON domain filter to apply. Leave as [] for all records.'
    )

    field_ids = fields.Many2many(
        'ir.model.fields',
        string='Fields to Export',
        help='Select which fields to include in the export'
    )

    format = fields.Selection([
        ('xlsx', 'Excel (XLSX)'),
        ('csv', 'CSV'),
    ], default='xlsx', required=True, string='Export Format')

    include_ids = fields.Boolean(
        string='Include Record IDs',
        default=False,
        help='Include internal database IDs in export'
    )

    record_count = fields.Integer(
        string='Records to Export',
        compute='_compute_record_count',
        help='Number of records that will be exported based on current filters'
    )

    context_source = fields.Char(
        string='Source',
        compute='_compute_context_source',
        help='Indicates if wizard was launched from list view'
    )

    @api.depends('model_id')
    def _compute_context_source(self):
        """Show helpful message when launched from list view."""
        for wizard in self:
            if wizard._context.get('active_model'):
                wizard.context_source = f"Pre-filled from {wizard.model_id.name} list view"
            else:
                wizard.context_source = False

    @api.model
    def default_get(self, fields_list):
        """Handle context from export button intercept."""
        res = super().default_get(fields_list)
        
        # If launched from list view export button, context will have these
        if self._context.get('default_model_id'):
            res['model_id'] = self._context.get('default_model_id')
        
        if self._context.get('default_domain'):
            res['domain'] = self._context.get('default_domain')
        
        if self._context.get('default_field_ids'):
            res['field_ids'] = self._context.get('default_field_ids')
        
        return res

    @api.depends('model_id', 'domain')
    def _compute_record_count(self):
        """Compute the number of records that match current filters."""
        for wizard in self:
            if not wizard.model_id:
                wizard.record_count = 0
                continue

            try:
                domain = json.loads(wizard.domain or '[]')
                Model = self.env[wizard.model_id.model]

                # Apply matrix filtering
                domain = wizard._apply_matrix_filtering(Model, domain)

                wizard.record_count = Model.search_count(domain)
            except Exception as e:
                _logger.warning("Error computing record count: %s", str(e))
                wizard.record_count = 0

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """Reset fields when model changes."""
        self.field_ids = False
        self.domain = '[]'

    def _check_export_permission(self):
        """Verify user has permission to export data."""
        if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
            raise AccessError(_(
                "You don't have permission to export data.\n\n"
                "This action requires the 'Can Export Data' permission.\n"
                "Please contact your administrator if you need this access."
            ))

    def _apply_matrix_filtering(self, Model, domain):
        """Apply branch/BU matrix filtering to the domain."""
        # Check if model has branch_id field
        if 'ops_branch_id' in Model._fields:
            allowed_branches = self.env.user.ops_allowed_branch_ids.ids
            if allowed_branches:
                domain.append(('ops_branch_id', 'in', allowed_branches))

        # Check if model has business_unit_id field
        if 'ops_business_unit_id' in Model._fields:
            allowed_bus = self.env.user.ops_allowed_business_unit_ids.ids
            if allowed_bus:
                domain.append(('ops_business_unit_id', 'in', allowed_bus))

        return domain

    def _get_allowed_fields(self):
        """Get fields user is allowed to export based on visibility rules."""
        self.ensure_one()

        if not self.field_ids:
            # Default to all readable fields
            Model = self.env[self.model_id.model]
            requested_fields = [
                f for f in Model._fields.keys()
                if not f.startswith('_') and f not in ('id', 'create_uid', 'write_uid')
            ]
        else:
            requested_fields = self.field_ids.mapped('name')

        hidden_fields = []

        # Check field visibility rules
        FieldVisibility = self.env.get('ops.field.visibility.rule')
        if FieldVisibility is not None:
            hidden_rules = FieldVisibility.search([
                ('model_id', '=', self.model_id.id),
                ('hidden', '=', True),
            ])
            hidden_fields.extend(hidden_rules.mapped('field_id.name'))

        # Check cost visibility
        if not self.env.user.has_group('ops_matrix_core.group_ops_see_cost'):
            hidden_fields.extend([
                'standard_price', 'cost', 'cost_price', 'purchase_price',
                'lst_price', 'list_price'
            ])

        # Check margin visibility
        if not self.env.user.has_group('ops_matrix_core.group_ops_see_margin'):
            hidden_fields.extend([
                'margin', 'profit_margin', 'markup', 'margin_percent'
            ])

        # Filter out hidden fields
        allowed = [f for f in requested_fields if f not in hidden_fields]

        return allowed

    def _log_export(self, records, fields_exported):
        """Log the export action for audit purposes."""
        self.ensure_one()

        try:
            domain = json.loads(self.domain or '[]')
        except (ValueError, TypeError):
            domain = []

        log_data = {
            'user_id': self.env.user.id,
            'action': 'data_export',
            'model': self.model_id.model,
            'details': json.dumps({
                'record_count': len(records),
                'record_ids': records.ids[:100],  # First 100 IDs only
                'fields': fields_exported,
                'domain': domain,
                'format': self.format,
                'export_time': fields.Datetime.now().isoformat(),
            }),
        }

        # Try ops.audit.log first, fall back to ops.security.audit
        AuditLog = self.env.get('ops.audit.log')
        if AuditLog is not None:
            try:
                AuditLog.sudo().create({
                    'timestamp': fields.Datetime.now(),
                    'endpoint': f'/secure-export/{self.model_id.model}',
                    'http_method': 'POST',
                    'status_code': 200,
                    'company_id': self.env.company.id,
                    'request_params': json.dumps({
                        'model': self.model_id.model,
                        'record_count': len(records),
                        'format': self.format,
                    }),
                })
            except Exception as e:
                _logger.debug("Failed to log to ops.audit.log: %s", str(e))

        # Also log to security audit
        SecurityAudit = self.env.get('ops.security.audit')
        if SecurityAudit is not None:
            try:
                SecurityAudit.sudo().create({
                    'user_id': self.env.user.id,
                    'event_type': 'matrix_change',  # Using existing event type
                    'model_name': self.model_id.model,
                    'details': f"Data export: {len(records)} records, fields: {fields_exported}",
                    'company_id': self.env.company.id,
                    'severity': 'info',
                })
            except Exception as e:
                _logger.debug("Failed to log to ops.security.audit: %s", str(e))

        _logger.info(
            "Secure export: User %s exported %d records from %s (format: %s)",
            self.env.user.name, len(records), self.model_id.model, self.format
        )

    def action_export(self):
        """Export data with security checks and audit logging."""
        self.ensure_one()

        # Check user has export permission
        self._check_export_permission()

        # Get model
        Model = self.env[self.model_id.model]

        # Parse domain
        try:
            domain = json.loads(self.domain or '[]')
        except json.JSONDecodeError:
            raise UserError(_("Invalid domain filter. Please enter valid JSON."))

        # Apply matrix filtering (branch/BU)
        domain = self._apply_matrix_filtering(Model, domain)

        # Filter fields based on visibility rules
        allowed_fields = self._get_allowed_fields()

        if not allowed_fields:
            raise UserError(_("No fields available for export based on your permissions."))

        # Fetch records
        records = Model.search(domain)

        if not records:
            raise UserError(_("No records found matching the specified criteria."))

        # Audit log BEFORE export
        self._log_export(records, allowed_fields)

        # Generate export
        if self.format == 'xlsx':
            return self._export_xlsx(records, allowed_fields)
        else:
            return self._export_csv(records, allowed_fields)

    def _get_field_value(self, record, field_name):
        """Get a formatted field value for export."""
        try:
            value = getattr(record, field_name, '')

            if value is False:
                return ''

            # Handle relational fields
            if hasattr(value, 'name'):
                return value.name
            elif hasattr(value, 'display_name'):
                return value.display_name
            elif hasattr(value, 'ids'):
                # Many2many or One2many
                return ', '.join(value.mapped('display_name') or value.mapped('name') or [])

            # Handle date/datetime
            if isinstance(value, (fields.Date, fields.Datetime)):
                return str(value)

            return str(value) if value else ''
        except Exception:
            _logger.debug('Failed to format field value for export', exc_info=True)
            return ''

    def _export_xlsx(self, records, field_list):
        """Generate Excel export."""
        self.ensure_one()

        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_(
                "Excel export requires the 'xlsxwriter' library.\n"
                "Please contact your administrator to install it."
            ))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.model_id.name[:31])  # Max 31 chars

        # Formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        cell_format = workbook.add_format({'border': 1})

        # Include ID column if requested
        col_offset = 0
        if self.include_ids:
            worksheet.write(0, 0, 'ID', header_format)
            worksheet.set_column(0, 0, 10)
            col_offset = 1

        # Header row
        for col, field in enumerate(field_list):
            worksheet.write(0, col + col_offset, field, header_format)
            worksheet.set_column(col + col_offset, col + col_offset, 15)

        # Data rows
        for row, record in enumerate(records, start=1):
            if self.include_ids:
                worksheet.write(row, 0, record.id, cell_format)

            for col, field in enumerate(field_list):
                value = self._get_field_value(record, field)
                worksheet.write(row, col + col_offset, value, cell_format)

        workbook.close()
        output.seek(0)

        # Create attachment
        filename = f'{self.model_id.model.replace(".", "_")}_export.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _export_csv(self, records, field_list):
        """Generate CSV export."""
        self.ensure_one()

        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        header = list(field_list)
        if self.include_ids:
            header.insert(0, 'ID')
        writer.writerow(header)

        # Data rows
        for record in records:
            row = []
            if self.include_ids:
                row.append(record.id)

            for field in field_list:
                value = self._get_field_value(record, field)
                row.append(value)
            writer.writerow(row)

        # Create attachment
        filename = f'{self.model_id.model.replace(".", "_")}_export.csv'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue().encode('utf-8')),
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
