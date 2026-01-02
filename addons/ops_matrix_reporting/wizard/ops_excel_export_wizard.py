# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import io
import base64
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("xlsxwriter library not found. Excel export will not be available.")
    xlsxwriter = None


class OpsExcelExportWizard(models.TransientModel):
    _name = 'ops.excel.export.wizard'
    _description = 'OPS Excel Export Wizard'
    
    report_type = fields.Selection([
        ('sales', 'Sales Analysis'),
        ('financial', 'Financial Analysis'),
        ('inventory', 'Inventory Analysis'),
    ], string='Report Type', required=True, default='sales')
    
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    
    branch_ids = fields.Many2many(
        'res.company', 
        string='Branches',
        help='Leave empty to include all branches'
    )
    
    business_unit_ids = fields.Many2many(
        'ops.business.unit', 
        string='Business Units',
        help='Leave empty to include all business units'
    )
    
    filename = fields.Char(string='Filename', readonly=True)
    excel_file = fields.Binary(string='Excel File', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range."""
        for wizard in self:
            if wizard.date_from and wizard.date_to:
                if wizard.date_from > wizard.date_to:
                    raise ValidationError(
                        _('The start date must be earlier than the end date.')
                    )
    
    def action_generate_excel(self):
        """Generate Excel file based on report type."""
        self.ensure_one()
        
        # Check if xlsxwriter is available
        if xlsxwriter is None:
            raise UserError(
                _('Excel export functionality is not available. '
                  'Please install the xlsxwriter Python library:\n\n'
                  'pip install xlsxwriter')
            )
        
        try:
            # Generate Excel file
            if self.report_type == 'sales':
                excel_data = self._generate_sales_excel()
                filename = 'sales_analysis.xlsx'
            elif self.report_type == 'financial':
                excel_data = self._generate_financial_excel()
                filename = 'financial_analysis.xlsx'
            elif self.report_type == 'inventory':
                excel_data = self._generate_inventory_excel()
                filename = 'inventory_analysis.xlsx'
            else:
                raise ValidationError(_('Invalid report type selected.'))
            
            # Save file to wizard
            self.write({
                'excel_file': base64.b64encode(excel_data),
                'filename': filename,
                'state': 'done',
            })
            
            # Return action to download file
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ops.excel.export.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
            }
            
        except Exception as e:
            _logger.exception("Error generating Excel export")
            raise UserError(
                _('Failed to generate Excel file:\n\n%s') % str(e)
            )
    
    def _generate_sales_excel(self):
        """Generate Sales Analysis Excel report."""
        # Build domain
        domain = []
        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        
        # Fetch data
        sales_data = self.env['ops.sales.analysis'].search_read(
            domain,
            ['date_order', 'product_id', 'partner_id', 'ops_branch_id', 
             'ops_business_unit_id', 'product_uom_qty', 'price_subtotal', 
             'margin', 'margin_percent'],
            order='date_order desc, partner_id'
        )
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sales Analysis')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00%',
            'border': 1,
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
        })
        
        text_format = workbook.add_format({'border': 1})
        
        # Set column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 30)  # Product
        worksheet.set_column('C:C', 25)  # Customer
        worksheet.set_column('D:D', 20)  # Branch
        worksheet.set_column('E:E', 20)  # Business Unit
        worksheet.set_column('F:F', 12)  # Quantity
        worksheet.set_column('G:G', 15)  # Revenue
        worksheet.set_column('H:H', 15)  # Margin
        worksheet.set_column('I:I', 12)  # Margin %
        
        # Write headers
        headers = ['Date', 'Product', 'Customer', 'Branch', 'Business Unit', 
                   'Quantity', 'Revenue', 'Margin', 'Margin %']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        total_qty = 0
        total_revenue = 0
        total_margin = 0
        
        for record in sales_data:
            worksheet.write(row, 0, record['date_order'], text_format)
            worksheet.write(row, 1, record['product_id'][1] if record.get('product_id') else '', text_format)
            worksheet.write(row, 2, record['partner_id'][1] if record.get('partner_id') else '', text_format)
            worksheet.write(row, 3, record['ops_branch_id'][1] if record.get('ops_branch_id') else '', text_format)
            worksheet.write(row, 4, record['ops_business_unit_id'][1] if record.get('ops_business_unit_id') else '', text_format)
            worksheet.write(row, 5, record['product_uom_qty'], number_format)
            worksheet.write(row, 6, record['price_subtotal'], currency_format)
            worksheet.write(row, 7, record['margin'], currency_format)
            worksheet.write(row, 8, record['margin_percent'] / 100, percent_format)
            
            total_qty += record['product_uom_qty']
            total_revenue += record['price_subtotal']
            total_margin += record['margin']
            row += 1
        
        # Write totals
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E7E6E6',
            'border': 1,
            'num_format': '#,##0.00',
        })
        
        worksheet.write(row, 4, 'TOTAL:', total_format)
        worksheet.write(row, 5, total_qty, total_format)
        worksheet.write(row, 6, total_revenue, total_format)
        worksheet.write(row, 7, total_margin, total_format)
        avg_margin = (total_margin / total_revenue * 100) if total_revenue else 0
        worksheet.write(row, 8, f'{avg_margin:.2f}%', total_format)
        
        workbook.close()
        output.seek(0)
        return output.read()
    
    def _generate_financial_excel(self):
        """Generate Financial Analysis Excel report."""
        # Build domain
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        
        # Fetch data
        financial_data = self.env['ops.financial.analysis'].search_read(
            domain,
            ['date', 'account_id', 'ops_branch_id', 'ops_business_unit_id', 
             'move_type', 'partner_id', 'debit', 'credit', 'balance'],
            order='date desc, account_id'
        )
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Financial Analysis')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#70AD47',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
        })
        
        text_format = workbook.add_format({'border': 1})
        
        # Set column widths
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        
        # Write headers
        headers = ['Date', 'Account', 'Branch', 'Business Unit', 'Move Type', 
                   'Partner', 'Debit', 'Credit', 'Balance']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        total_debit = 0
        total_credit = 0
        total_balance = 0
        
        for record in financial_data:
            worksheet.write(row, 0, record['date'], text_format)
            worksheet.write(row, 1, record['account_id'][1] if record.get('account_id') else '', text_format)
            worksheet.write(row, 2, record['ops_branch_id'][1] if record.get('ops_branch_id') else '', text_format)
            worksheet.write(row, 3, record['ops_business_unit_id'][1] if record.get('ops_business_unit_id') else '', text_format)
            worksheet.write(row, 4, record.get('move_type', ''), text_format)
            worksheet.write(row, 5, record['partner_id'][1] if record.get('partner_id') else '', text_format)
            worksheet.write(row, 6, record['debit'], currency_format)
            worksheet.write(row, 7, record['credit'], currency_format)
            worksheet.write(row, 8, record['balance'], currency_format)
            
            total_debit += record['debit']
            total_credit += record['credit']
            total_balance += record['balance']
            row += 1
        
        # Write totals
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E7E6E6',
            'border': 1,
            'num_format': '#,##0.00',
        })
        
        worksheet.write(row, 5, 'TOTAL:', total_format)
        worksheet.write(row, 6, total_debit, total_format)
        worksheet.write(row, 7, total_credit, total_format)
        worksheet.write(row, 8, total_balance, total_format)
        
        workbook.close()
        output.seek(0)
        return output.read()
    
    def _generate_inventory_excel(self):
        """Generate Inventory Analysis Excel report."""
        # Build domain
        domain = []
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        
        # Fetch data
        inventory_data = self.env['ops.inventory.analysis'].search_read(
            domain,
            ['product_id', 'location_id', 'ops_business_unit_id', 'quantity', 
             'reserved_quantity', 'available_quantity', 'standard_price', 'stock_value'],
            order='product_id, location_id'
        )
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Inventory Analysis')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFC000',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1,
        })
        
        text_format = workbook.add_format({'border': 1})
        
        # Set column widths
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 12)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 15)
        
        # Write headers
        headers = ['Product', 'Location', 'Business Unit', 'On Hand', 'Reserved', 
                   'Available', 'Unit Price', 'Stock Value']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        total_on_hand = 0
        total_reserved = 0
        total_available = 0
        total_value = 0
        
        for record in inventory_data:
            worksheet.write(row, 0, record['product_id'][1] if record.get('product_id') else '', text_format)
            worksheet.write(row, 1, record['location_id'][1] if record.get('location_id') else '', text_format)
            worksheet.write(row, 2, record['ops_business_unit_id'][1] if record.get('ops_business_unit_id') else '', text_format)
            worksheet.write(row, 3, record['quantity'], number_format)
            worksheet.write(row, 4, record['reserved_quantity'], number_format)
            worksheet.write(row, 5, record['available_quantity'], number_format)
            worksheet.write(row, 6, record['standard_price'], currency_format)
            worksheet.write(row, 7, record['stock_value'], currency_format)
            
            total_on_hand += record['quantity']
            total_reserved += record['reserved_quantity']
            total_available += record['available_quantity']
            total_value += record['stock_value']
            row += 1
        
        # Write totals
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E7E6E6',
            'border': 1,
            'num_format': '#,##0.00',
        })
        
        worksheet.write(row, 2, 'TOTAL:', total_format)
        worksheet.write(row, 3, total_on_hand, total_format)
        worksheet.write(row, 4, total_reserved, total_format)
        worksheet.write(row, 5, total_available, total_format)
        worksheet.write(row, 6, '', total_format)
        worksheet.write(row, 7, total_value, total_format)
        
        workbook.close()
        output.seek(0)
        return output.read()
    
    def action_download(self):
        """Download the generated Excel file."""
        self.ensure_one()
        
        if not self.excel_file:
            raise UserError(_('No Excel file has been generated yet.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/ops.excel.export.wizard/{self.id}/excel_file/{self.filename}?download=true',
            'target': 'self',
        }
