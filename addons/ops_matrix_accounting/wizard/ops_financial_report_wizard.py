from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import io
import base64

class OpsFinancialReportWizard(models.TransientModel):
    """
    Lightweight Financial Reporting Wizard for Zero DB Bloat.
    Uses native Odoo views for on-screen analysis and in-memory generation for exports.
    """
    _name = 'ops.financial.report.wizard'
    _description = 'Financial Report Wizard'

    report_type = fields.Selection([
        ('pl', 'P&L'),
        ('bs', 'Balance Sheet'),
        ('gl', 'General Ledger'),
        ('aged', 'Aged Partner')
    ], string='Report Type', required=True, default='gl')
    
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        help="Filter by branch (via analytic account)"
    )
    
    target_move = fields.Selection([
        ('posted', 'Posted Only'),
        ('all', 'All')
    ], string='Target Moves', default='posted', required=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        help='Leave empty to include all journals'
    )

    @api.model
    def default_get(self, fields_list):
        """Set default date range to current month."""
        res = super().default_get(fields_list)
        
        today = fields.Date.context_today(self)
        first_day = today.replace(day=1)
        last_day = (first_day + relativedelta(months=1, days=-1))
        
        if 'date_from' in fields_list:
            res['date_from'] = first_day
        if 'date_to' in fields_list:
            res['date_to'] = last_day
        
        return res

    def _get_domain(self):
        """Build domain for account.move.line based on wizard filters."""
        self.ensure_one()
        
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        
        # Filter by move state
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        
        # Filter by branch (via ops_branch_id field)
        # Note: In Odoo 19, analytic_account_id is not available on account.move.line
        # We use ops_branch_id field added by ops_matrix_core module
        if self.branch_id:
            domain.append(('ops_branch_id', '=', self.branch_id.id))
        
        # Filter by journals if specified
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        
        return domain

    def _get_context_groupings(self):
        """Return default groupings based on report type."""
        self.ensure_one()
        
        context = {}
        
        if self.report_type == 'pl':
            # P&L: Group by account type (Income/Expense)
            context.update({
                'pivot_row_groupby': ['account_id'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        elif self.report_type == 'bs':
            # Balance Sheet: Group by account type (Asset/Liability)
            context.update({
                'pivot_row_groupby': ['account_id'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        elif self.report_type == 'gl':
            # General Ledger: Group by account and date
            context.update({
                'pivot_row_groupby': ['account_id', 'date'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        elif self.report_type == 'aged':
            # Aged Partner: Group by partner
            context.update({
                'pivot_row_groupby': ['partner_id'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        
        return context

    def action_view_data(self):
        """
        Open account.move.line in pivot/tree view with filters applied.
        NO intermediate records created - Zero DB Bloat approach.
        """
        self.ensure_one()
        
        domain = self._get_domain()
        context = self._get_context_groupings()
        
        return {
            'name': _('%s - On-Screen Analysis') % dict(self._fields['report_type'].selection).get(self.report_type),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'pivot,tree',
            'views': [(False, 'pivot'), (False, 'tree')],
            'domain': domain,
            'context': context,
            'target': 'current',
        }

    def action_print_pdf(self):
        """Generate PDF report using AbstractModel parser (in-memory processing)."""
        self.ensure_one()
        return self.env.ref('ops_matrix_accounting.action_report_ops_financial').report_action(self)

    def action_export_xlsx(self):
        """Export to Excel using in-memory generation."""
        self.ensure_one()
        
        # Get the report parser (must match parser _name)
        report_parser = self.env['report.ops_matrix_accounting.report_ops_financial_document']
        report_data = report_parser._get_report_data(self)
        
        # Generate XLSX file
        try:
            import xlsxwriter
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet(report_data['title'])
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            # Write headers
            col = 0
            for header in report_data['headers']:
                worksheet.write(0, col, header, header_format)
                col += 1
            
            # Write data
            row = 1
            for line in report_data['lines']:
                col = 0
                for value in line.values():
                    worksheet.write(row, col, value)
                    col += 1
                row += 1
            
            workbook.close()
            output.seek(0)
            
            # Create attachment
            filename = f"{report_data['title']}_{self.date_from}_{self.date_to}.xlsx"
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
            
        except ImportError:
            raise UserError(_('xlsxwriter library is not installed. Please install it to export to Excel.'))
