from odoo import models
from odoo.exceptions import UserError
import io
import base64

class OpsGeneralLedgerXlsx(models.AbstractModel):
    """
    General Ledger XLSX Export.
    Uses in-memory generation to maintain "Zero DB Bloat" design.
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger_xlsx'
    _description = 'General Ledger XLSX Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        """
        Generate XLSX report using xlsxwriter.
        
        Args:
            workbook: xlsxwriter.Workbook instance
            data: Report data dict from wizard
            partners: Wizard recordset (docids)
        """
        try:
            # Get report data from the parser
            report_parser = self.env['report.ops_matrix_accounting.report_general_ledger']
            report_values = report_parser._get_report_values(partners.ids, data)
            
            # Create worksheet
            worksheet = workbook.add_worksheet('General Ledger')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
            })
            
            account_header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#E9ECEF',
                'border': 1,
            })
            
            total_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FFF3CD',
                'border': 1,
                'num_format': '#,##0.00',
            })
            
            currency_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
            })
            
            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1,
            })
            
            text_format = workbook.add_format({
                'border': 1,
            })
            
            # Set column widths
            worksheet.set_column('A:A', 12)  # Date
            worksheet.set_column('B:B', 15)  # Journal
            worksheet.set_column('C:C', 25)  # Partner
            worksheet.set_column('D:D', 35)  # Label
            worksheet.set_column('E:E', 15)  # Reference
            worksheet.set_column('F:F', 15)  # Debit
            worksheet.set_column('G:G', 15)  # Credit
            worksheet.set_column('H:H', 15)  # Balance
            
            # Write report header
            row = 0
            worksheet.merge_range(row, 0, row, 7, 'GENERAL LEDGER REPORT', header_format)
            row += 1
            
            # Write metadata
            company = report_values.get('company')
            worksheet.write(row, 0, 'Company:', text_format)
            worksheet.write(row, 1, company.name if company else '', text_format)
            row += 1
            
            worksheet.write(row, 0, 'Period:', text_format)
            period_text = f"{data.get('date_from', '')} to {data.get('date_to', '')}"
            worksheet.write(row, 1, period_text, text_format)
            row += 1
            
            worksheet.write(row, 0, 'Target Moves:', text_format)
            worksheet.write(row, 1, data.get('target_move', 'posted'), text_format)
            row += 2
            
            # Process accounts
            accounts = report_values.get('accounts', [])
            
            for account in accounts:
                # Account header
                account_title = f"{account['account_code']} - {account['account_name']}"
                worksheet.merge_range(row, 0, row, 7, account_title, account_header_format)
                row += 1
                
                # Column headers
                headers = ['Date', 'Journal', 'Partner', 'Label', 'Reference', 'Debit', 'Credit', 'Balance']
                for col, header in enumerate(headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Account lines
                for line in account.get('lines', []):
                    worksheet.write(row, 0, line['move_date'], date_format)
                    worksheet.write(row, 1, line['journal'], text_format)
                    worksheet.write(row, 2, line['partner'], text_format)
                    worksheet.write(row, 3, line['label'], text_format)
                    worksheet.write(row, 4, line['reference'], text_format)
                    worksheet.write(row, 5, line['debit'], currency_format)
                    worksheet.write(row, 6, line['credit'], currency_format)
                    worksheet.write(row, 7, line['balance'], currency_format)
                    row += 1
                
                # Account totals
                worksheet.write(row, 4, 'Account Total:', total_format)
                worksheet.write(row, 5, account['total_debit'], total_format)
                worksheet.write(row, 6, account['total_credit'], total_format)
                worksheet.write(row, 7, account['total_balance'], total_format)
                row += 2
            
            # Grand totals
            grand_total = report_values.get('grand_total', {})
            worksheet.merge_range(row, 0, row, 4, 'GRAND TOTAL', total_format)
            worksheet.write(row, 5, grand_total.get('debit', 0.0), total_format)
            worksheet.write(row, 6, grand_total.get('credit', 0.0), total_format)
            worksheet.write(row, 7, grand_total.get('balance', 0.0), total_format)
            
        except Exception as e:
            raise UserError(f"Error generating XLSX report: {str(e)}")

    def _get_objs_for_report(self, docids, data):
        """
        Override to provide wizard data to the report.
        This method is called by the abstract XLSX report class.
        """
        if data:
            return self.env['ops.general.ledger.wizard'].browse(docids)
        return self.env['ops.general.ledger.wizard']
