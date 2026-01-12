# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import base64
import io
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

class SecureExcelExportWizard(models.TransientModel):
    _name = 'secure.excel.export.wizard'
    _description = 'Secure Excel Export Wizard'
    
    model_id = fields.Many2one('ir.model', 'Model to Export', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', readonly=True)
    
    field_ids = fields.Many2many('ir.model.fields', 'export_wizard_field_rel',
                                  'wizard_id', 'field_id',
                                  'Fields to Export',
                                  domain="[('model_id', '=', model_id), ('store', '=', True)]")
    
    domain = fields.Text('Domain Filter', default='[]',
                         help='Python domain to filter records')
    
    limit = fields.Integer('Record Limit', default=1000,
                          help='Maximum records to export (max 10000)')
    
    file_data = fields.Binary('Excel File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Configure'),
        ('done', 'Done')
    ], default='draft')
    
    @api.constrains('limit')
    def _check_limit(self):
        for wizard in self:
            if wizard.limit > 10000:
                raise ValidationError(_('Export limit cannot exceed 10,000 records.'))
    
    def action_export(self):
        """Generate secure Excel export"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise ValidationError(_('xlsxwriter library is not installed.'))
        
        if not self.field_ids:
            raise ValidationError(_('Please select at least one field to export.'))
        
        # Get records with security filtering
        Model = self.env[self.model_name]

        # Parse domain safely - CRITICAL: Use safe_eval to prevent code injection
        try:
            domain = safe_eval(self.domain) if self.domain else []
            # Validate domain is a list
            if not isinstance(domain, list):
                raise ValueError("Domain must be a list")
        except (ValueError, SyntaxError, NameError, TypeError) as e:
            raise ValidationError(_(
                'Invalid domain filter. Please use Python list format.\n'
                'Example: [("state", "=", "draft"), ("amount", ">", 100)]\n'
                'Error: %s'
            ) % str(e))
        
        # Apply automatic branch filtering if model has branch_id
        # Check for ops_branch_id or branch_id
        branch_field = None
        if 'ops_branch_id' in Model._fields:
            branch_field = 'ops_branch_id'
        elif 'branch_id' in Model._fields:
            branch_field = 'branch_id'
            
        if branch_field and not self.env.user.has_group('ops_matrix_core.group_ops_ceo'):
            # In Odoo 19, check for user's branch access
            if hasattr(self.env.user, 'ops_allowed_branch_ids'):
                user_branches = self.env.user.ops_allowed_branch_ids
                if user_branches:
                    domain += [(branch_field, 'in', user_branches.ids)]
        
        records = Model.search(domain, limit=self.limit)
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Export')
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # Write headers
        visible_fields = []
        for col, field in enumerate(self.field_ids):
            # Check field visibility
            if self._is_field_visible(field):
                worksheet.write(0, len(visible_fields), field.field_description, header_format)
                visible_fields.append(field)
        
        # Write data
        for row, record in enumerate(records, start=1):
            for col, field in enumerate(visible_fields):
                value = self._get_field_value(record, field)
                worksheet.write(row, col, value)
        
        workbook.close()
        
        # Save file
        self.write({
            'file_data': base64.b64encode(output.getvalue()),
            'file_name': f'{self.model_id.name}_export.xlsx',
            'state': 'done'
        })
        
        # Log export activity
        self.env['ops.export.log'].create({
            'user_id': self.env.user.id,
            'model_id': self.model_id.id,
            'record_count': len(records),
            'export_date': fields.Datetime.now()
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'secure.excel.export.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new'
        }
    
    def _is_field_visible(self, field):
        """Check if user can see this field"""
        # Hide cost/margin fields unless user is authorized
        sensitive_fields = ['standard_price', 'purchase_price', 'cost', 'margin', 'margin_percent']
        if field.name in sensitive_fields:
            return self.env.user.has_group('ops_matrix_core.group_ops_manager') or \
                   self.env.user.has_group('base.group_system')
        return True
    
    def _get_field_value(self, record, field):
        """Get field value with proper formatting"""
        try:
            value = getattr(record, field.name)
            
            if field.ttype in ('many2one',):
                return value.display_name if value else ''
            elif field.ttype in ('one2many', 'many2many'):
                return ', '.join(value.mapped('display_name'))
            elif field.ttype == 'boolean':
                return 'Yes' if value else 'No'
            elif field.ttype in ('date', 'datetime'):
                return str(value) if value else ''
            else:
                return value or ''
        except:
            return ''

# Export log model
class OpsExportLog(models.Model):
    _name = 'ops.export.log'
    _description = 'Export Activity Log'
    _order = 'export_date desc'
    
    user_id = fields.Many2one('res.users', 'User', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, ondelete='cascade')
    record_count = fields.Integer('Records Exported')
    export_date = fields.Datetime('Export Date', required=True)
