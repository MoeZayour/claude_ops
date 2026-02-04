from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import io
import base64
import logging
import warnings

_logger = logging.getLogger(__name__)


class OpsFinancialReportWizard(models.TransientModel):
    """
    ============================================================================
    DEPRECATED: This wizard is deprecated as of v19.0.2.2

    Please use 'ops.general.ledger.wizard.enhanced' (Matrix Financial Intelligence)
    which consolidates all 8 core financial reports with full Matrix dimension support.

    Menu: Accounting > Reporting > Matrix Financial Intelligence

    This wizard will be removed in a future version.
    ============================================================================
    """
    _name = 'ops.financial.report.wizard'
    _description = 'Financial Report Wizard (DEPRECATED - Use Matrix Financial Intelligence)'

    @api.model
    def _log_deprecation_warning(self):
        """Log deprecation warning when wizard is accessed."""
        _logger.warning(
            "DEPRECATED: ops.financial.report.wizard is deprecated. "
            "Please use 'ops.general.ledger.wizard.enhanced' (Matrix Financial Intelligence) instead. "
            "This wizard will be removed in a future version."
        )
        warnings.warn(
            "ops.financial.report.wizard is deprecated. Use ops.general.ledger.wizard.enhanced instead.",
            DeprecationWarning,
            stacklevel=3
        )

    report_type = fields.Selection([
        ('pl', 'P&L'),
        ('bs', 'Balance Sheet'),
        ('gl', 'General Ledger'),
        ('aged', 'Aged Partner'),
        ('tb', 'Trial Balance'),
        ('cf', 'Cash Flow')
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
        self._log_deprecation_warning()
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
        elif self.report_type == 'tb':
            # Trial Balance: Group by account
            context.update({
                'pivot_row_groupby': ['account_id'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        elif self.report_type == 'cf':
            # Cash Flow: Group by account (Liquidity)
            context.update({
                'pivot_row_groupby': ['account_id', 'date'],
                'pivot_column_groupby': [],
                'pivot_measures': ['debit', 'credit', 'balance'],
            })
        
        return context

    def action_view_data(self):
        """
        Open account.move.line in pivot/list view with filters applied.
        NO intermediate records created - Zero DB Bloat approach.
        """
        self.ensure_one()
        
        domain = self._get_domain()
        context = self._get_context_groupings()
        
        return {
            'name': _('%s - On-Screen Analysis') % dict(self._fields['report_type'].selection).get(self.report_type),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'pivot,list',
            'views': [(False, 'pivot'), (False, 'list')],
            'domain': domain,
            'context': context,
            'target': 'current',
        }

    def action_print_pdf(self):
        """Generate PDF report using AbstractModel parser (in-memory processing)."""
        self.ensure_one()
        return self.env.ref('ops_matrix_accounting.action_report_ops_financial').report_action(self)

    def action_export_pdf(self):
        """Alias for action_print_pdf to satisfy Priority #15 requirements."""
        return self.action_print_pdf()

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
            worksheet = workbook.add_worksheet(report_data['title'][:31]) # Excel sheet name limit
            
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
                # Ensure we only write values that exist in headers
                # For P&L and BS, lines are simple dicts with 'account' and 'amount'
                if self.report_type in ['pl', 'bs', 'tb']:
                    worksheet.write(row, 0, line.get('account', ''))
                    worksheet.write(row, 1, line.get('amount', line.get('debit', 0)))
                    if self.report_type == 'tb':
                        worksheet.write(row, 2, line.get('credit', 0))
                        worksheet.write(row, 3, line.get('balance', 0))
                elif self.report_type == 'gl':
                    worksheet.write(row, 0, str(line.get('date', '')))
                    worksheet.write(row, 1, line.get('move_name', ''))
                    worksheet.write(row, 2, line.get('account', ''))
                    worksheet.write(row, 3, line.get('partner', ''))
                    worksheet.write(row, 4, line.get('label', ''))
                    worksheet.write(row, 5, line.get('debit', 0))
                    worksheet.write(row, 6, line.get('credit', 0))
                    worksheet.write(row, 7, line.get('balance', 0))
                elif self.report_type == 'aged':
                    worksheet.write(row, 0, line.get('partner', ''))
                    worksheet.write(row, 1, line.get('debit', 0))
                    worksheet.write(row, 2, line.get('credit', 0))
                    worksheet.write(row, 3, line.get('balance', 0))
                elif self.report_type == 'cf':
                    worksheet.write(row, 0, line.get('account', ''))
                    worksheet.write(row, 1, line.get('inflow', 0))
                    worksheet.write(row, 2, line.get('outflow', 0))
                    worksheet.write(row, 3, line.get('net', 0))
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
